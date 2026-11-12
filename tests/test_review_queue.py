import csv
import tempfile
import threading
import unittest
from pathlib import Path

from sgt_kb.collection import review_queue


class ReviewQueueTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.queue = Path(self.temp_dir.name) / "review.csv"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_legacy_rows(self) -> None:
        with self.queue.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["company", "title", "date", "url", "margin", "added_at"],
            )
            writer.writeheader()
            writer.writerow({
                "company": "Elastic", "title": "Vector search", "date": "2026-08-01",
                "url": "http://EXAMPLE.com/post#section", "margin": "0.01",
                "added_at": "2026-08-02 12:00",
            })
            writer.writerow({
                "company": "Elastic", "title": "Vector search", "date": "2026-08-01",
                "url": "https://example.com/post", "margin": "0.01",
                "added_at": "2026-08-03 12:00",
            })

    def test_load_queue_migrates_and_deduplicates_legacy_rows(self) -> None:
        self.write_legacy_rows()

        records, duplicates = review_queue.load_queue(self.queue)

        self.assertEqual(1, duplicates)
        self.assertEqual(1, len(records))
        self.assertEqual("pending", records[0]["status"])
        self.assertEqual("https://example.com/post", records[0]["url"])

    def test_enqueue_candidate_is_idempotent(self) -> None:
        added = review_queue.enqueue_candidate(
            "LanceDB", "Agent memory", "2026-08-03",
            "https://example.com/agent", 0.01, self.queue,
        )
        repeated = review_queue.enqueue_candidate(
            "LanceDB", "Agent memory", "2026-08-03",
            "https://example.com/agent#top", 0.01, self.queue,
        )

        self.assertTrue(added)
        self.assertFalse(repeated)
        records = review_queue.load_queue(self.queue)[0]
        self.assertEqual(1, len(records))
        self.assertEqual(review_queue.candidate_id("https://example.com/agent"), records[0]["id"])

    def test_approved_candidate_is_ingested_and_marked(self) -> None:
        review_queue.enqueue_candidate(
            "LanceDB", "Agent memory", "2026-08-03",
            "https://example.com/agent", 0.01, self.queue,
        )
        record = review_queue.load_queue(self.queue)[0][0]
        review_queue.set_decision({record["id"]}, "approved", self.queue)

        calls = []

        def fake_ingest(**row):
            calls.append(row["url"])
            self.assertEqual("Agent memory", row["title"])
            self.assertEqual("2026-08-03", row["date"])
            return {"status": "ingested"}

        result = review_queue.ingest_approved(self.queue, fake_ingest)
        updated = review_queue.load_queue(self.queue)[0][0]

        self.assertEqual({"ingested": 1, "existing": 0, "failed": 0}, result)
        self.assertEqual(["https://example.com/agent"], calls)
        self.assertEqual("ingested", updated["status"])

    def test_gate_rejection_is_recorded_once(self) -> None:
        added = review_queue.enqueue_candidate(
            "Example", "Marketing event", "2026-08-03",
            "https://example.com/event", None, self.queue,
            status="rejected", error="rule:webinar",
        )
        repeated = review_queue.enqueue_candidate(
            "Example", "Marketing event", "2026-08-03",
            "https://example.com/event", None, self.queue,
            status="rejected", error="rule:webinar",
        )

        record = review_queue.load_queue(self.queue)[0][0]
        self.assertTrue(added)
        self.assertFalse(repeated)
        self.assertEqual("rejected", record["status"])
        self.assertEqual("rule:webinar", record["error"])

    def test_failed_candidate_can_be_reapproved(self) -> None:
        review_queue.enqueue_candidate(
            "Elastic", "Retrieval architecture", "2026-08-18",
            "https://example.com/retrieval", 0.01, self.queue,
        )
        record = review_queue.load_queue(self.queue)[0][0]
        review_queue.set_decision({record["id"]}, "approved", self.queue)

        def failing_ingest(**_row):
            raise RuntimeError("temporary 404")

        result = review_queue.ingest_approved(self.queue, failing_ingest)
        failed = review_queue.load_queue(self.queue)[0][0]
        changed = review_queue.set_decision({record["id"]}, "approved", self.queue)
        retried = review_queue.load_queue(self.queue)[0][0]

        self.assertEqual(1, result["failed"])
        self.assertEqual("failed", failed["status"])
        self.assertEqual(1, changed)
        self.assertEqual("approved", retried["status"])
        self.assertEqual("", retried["error"])

    def test_daily_update_consumes_approved_candidates(self) -> None:
        from sgt_kb.collection import daily_update

        source = Path(daily_update.__file__).read_text(encoding="utf-8")
        self.assertIn('"sgt_kb", "review-queue", "ingest-approved"', source)

    def test_auto_triage_uses_title_filter_for_curated_hosts(self) -> None:
        review_queue.enqueue_candidate(
            "Elastic", "Hybrid retrieval with BM25 and vectors", "2026-08-03",
            "https://elastic.co/search-labs/hybrid", 0.01, self.queue,
        )
        review_queue.enqueue_candidate(
            "Elastic", "Elastic achieves a security distinction", "2026-08-03",
            "https://elastic.co/security-award", 0.01, self.queue,
        )

        result = review_queue.auto_triage_pending(self.queue)
        statuses = {row["title"]: row["status"] for row in review_queue.load_queue(self.queue)[0]}

        self.assertEqual({"approved": 1, "rejected": 1, "deferred_host": 0}, result)
        self.assertEqual("approved", statuses["Hybrid retrieval with BM25 and vectors"])
        self.assertEqual("rejected", statuses["Elastic achieves a security distinction"])

    def test_auto_triage_defers_unknown_exa_host(self) -> None:
        review_queue.enqueue_candidate(
            "unknown.example", "Vector retrieval", "2026-08-03",
            "https://unknown.example/vector", 0.01, self.queue,
        )

        result = review_queue.auto_triage_pending(self.queue)

        self.assertEqual({"approved": 0, "rejected": 0, "deferred_host": 1}, result)
        self.assertEqual("pending", review_queue.load_queue(self.queue)[0][0]["status"])

    def test_only_one_concurrent_consumer_claims_candidate(self) -> None:
        review_queue.enqueue_candidate(
            "LanceDB", "Agent memory", "2026-08-03",
            "https://lancedb.com/blog/agent", 0.01, self.queue,
        )
        record = review_queue.load_queue(self.queue)[0][0]
        review_queue.set_decision({record["id"]}, "approved", self.queue)
        started = threading.Event()
        release = threading.Event()
        calls = []

        def slow_ingest(**row):
            calls.append(row["url"])
            started.set()
            release.wait(2)
            return {"status": "ingested"}

        first = threading.Thread(
            target=review_queue.ingest_approved, args=(self.queue, slow_ingest)
        )
        first.start()
        self.assertTrue(started.wait(2))
        second_result = review_queue.ingest_approved(self.queue, slow_ingest)
        release.set()
        first.join(2)

        self.assertEqual(1, len(calls))
        self.assertEqual({"ingested": 0, "existing": 0, "failed": 0}, second_result)

    def test_migration_preserves_terminal_status_and_creates_backup(self) -> None:
        with self.queue.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=review_queue.FIELDS)
            writer.writeheader()
            base = {
                "id": "", "company": "Elastic", "title": "Vector search",
                "date": "2026-08-01", "url": "https://elastic.co/post",
                "margin": "0.01", "added_at": "2026-08-01 12:00",
                "reviewed_at": "", "error": "",
            }
            writer.writerow({**base, "status": "pending"})
            writer.writerow({**base, "url": "http://elastic.co/post#top", "status": "ingested"})

        result = review_queue.migrate_queue(self.queue)
        record = review_queue.load_queue(self.queue)[0][0]

        self.assertEqual(1, result["duplicates_removed"])
        self.assertTrue(Path(result["backup"]).exists())
        self.assertEqual("ingested", record["status"])

    def test_migration_aborts_without_deleting_invalid_row(self) -> None:
        self.queue.write_text(
            "company,title,date,url,margin,added_at\nBad,Bad,,,0,2026-08-01 12:00\n",
            encoding="utf-8",
        )
        before = self.queue.read_text(encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "invalid row"):
            review_queue.migrate_queue(self.queue)

        self.assertEqual(before, self.queue.read_text(encoding="utf-8"))

    def test_unexpected_ingest_status_is_failed(self) -> None:
        review_queue.enqueue_candidate(
            "LanceDB", "Agent memory", "2026-08-03",
            "https://lancedb.com/blog/agent", 0.01, self.queue,
        )
        record = review_queue.load_queue(self.queue)[0][0]
        review_queue.set_decision({record["id"]}, "approved", self.queue)

        result = review_queue.ingest_approved(
            self.queue, lambda **_row: {"status": "partial"}
        )

        updated = review_queue.load_queue(self.queue)[0][0]
        self.assertEqual(1, result["failed"])
        self.assertEqual("failed", updated["status"])
        self.assertIn("unexpected ingest status", updated["error"])

    def test_processing_cannot_be_changed_by_normal_decision(self) -> None:
        review_queue.enqueue_candidate(
            "LanceDB", "Agent memory", "2026-08-03",
            "https://lancedb.com/blog/agent", 0.01, self.queue,
        )
        record = review_queue.load_queue(self.queue)[0][0]
        review_queue.set_decision({record["id"]}, "approved", self.queue)
        claimed = review_queue.claim_next_approved(self.queue)

        approved = review_queue.set_decision({record["id"]}, "approved", self.queue)
        rejected = review_queue.set_decision({record["id"]}, "rejected", self.queue)

        self.assertIsNotNone(claimed)
        self.assertEqual(0, approved)
        self.assertEqual(0, rejected)
        self.assertEqual("processing", review_queue.load_queue(self.queue)[0][0]["status"])

    def test_expired_processing_lease_is_recovered(self) -> None:
        review_queue.enqueue_candidate(
            "LanceDB", "First", "2026-08-03",
            "https://lancedb.com/blog/first", 0.01, self.queue,
        )
        first = review_queue.load_queue(self.queue)[0][0]
        review_queue.set_decision({first["id"]}, "approved", self.queue)
        claimed = review_queue.claim_next_approved(self.queue)

        records = review_queue.load_queue(self.queue)[0]
        records[0]["claimed_at"] = "2000-01-01 00:00:00"
        review_queue.save_queue(records, self.queue)
        recovered = review_queue.claim_next_approved(self.queue)

        self.assertNotEqual(claimed["claim_id"], recovered["claim_id"])
        self.assertEqual("processing", recovered["status"])

    def test_claim_completion_requires_matching_token(self) -> None:
        review_queue.enqueue_candidate(
            "LanceDB", "Agent memory", "2026-08-03",
            "https://lancedb.com/blog/agent", 0.01, self.queue,
        )
        record = review_queue.load_queue(self.queue)[0][0]
        review_queue.set_decision({record["id"]}, "approved", self.queue)
        claimed = review_queue.claim_next_approved(self.queue)
        stale = {**claimed, "claim_id": "wrong-token"}

        self.assertFalse(review_queue.complete_claim(stale, "ingested", "", self.queue))
        self.assertTrue(review_queue.complete_claim(claimed, "ingested", "", self.queue))

    def test_system_exit_marks_claim_failed_before_propagating(self) -> None:
        review_queue.enqueue_candidate(
            "LanceDB", "Agent memory", "2026-08-03",
            "https://lancedb.com/blog/agent", 0.01, self.queue,
        )
        record = review_queue.load_queue(self.queue)[0][0]
        review_queue.set_decision({record["id"]}, "approved", self.queue)

        with self.assertRaises(SystemExit):
            review_queue.ingest_approved(
                self.queue, lambda **_row: (_ for _ in ()).throw(SystemExit(1))
            )

        self.assertEqual("failed", review_queue.load_queue(self.queue)[0][0]["status"])

    def test_write_aborts_without_dropping_invalid_row(self) -> None:
        self.queue.write_text(
            "company,title,date,url,margin,added_at,status\n"
            "Good,Good,2026-08-01,https://lancedb.com/good,0,2026-08-01 12:00,pending\n"
            "Bad,Bad,2026-08-01,https://lancedb.com/bad,0,2026-08-01 12:00,ingestd\n",
            encoding="utf-8",
        )
        before = self.queue.read_text(encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "invalid row"):
            review_queue.enqueue_candidate(
                "New", "New", "2026-08-02", "https://lancedb.com/new", 0, self.queue
            )

        self.assertEqual(before, self.queue.read_text(encoding="utf-8"))

    def test_require_all_decision_is_atomic(self) -> None:
        review_queue.enqueue_candidate(
            "LanceDB", "Agent memory", "2026-08-03",
            "https://lancedb.com/blog/agent", 0.01, self.queue,
        )
        record = review_queue.load_queue(self.queue)[0][0]
        review_queue.set_decision({record["id"]}, "approved", self.queue)
        claimed = review_queue.claim_next_approved(self.queue)

        with self.assertRaisesRegex(ValueError, "blocked"):
            review_queue.set_decision(
                {record["id"]}, "rejected", self.queue, require_all=True
            )

        self.assertEqual(claimed["claim_id"], review_queue.load_queue(self.queue)[0][0]["claim_id"])


if __name__ == "__main__":
    unittest.main()
