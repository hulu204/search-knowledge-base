import csv
import tempfile
import unittest
from pathlib import Path

from sgt_kb.collection import exa_discover


class ExaDiscoverTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.queue = root / "queue.csv"
        self.hosts = root / "hosts.csv"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_unknown_relevant_host_is_queued_and_registered(self) -> None:
        counts = exa_discover.discover([{
            "title": "Hybrid retrieval with BM25 and vector reranking",
            "url": "https://engineering.example/search/hybrid",
            "publishedDate": "2026-08-01T00:00:00.000Z",
        }], "hybrid retrieval", self.queue, self.hosts)

        self.assertEqual(1, counts["queued"])
        queued = list(csv.DictReader(self.queue.open(encoding="utf-8")))
        hosts = list(csv.DictReader(self.hosts.open(encoding="utf-8")))
        self.assertEqual("pending", queued[0]["status"])
        self.assertEqual("candidate", hosts[0]["status"])
        self.assertEqual("1", hosts[0]["relevant_titles"])

    def test_irrelevant_result_only_updates_host_registry(self) -> None:
        counts = exa_discover.discover([{
            "title": "Company leadership year in review",
            "url": "https://example.org/review",
            "publishedDate": "2026-08-01T00:00:00.000Z",
        }], "search", self.queue, self.hosts)

        self.assertEqual(0, counts["queued"])
        self.assertFalse(self.queue.exists())
        self.assertTrue(self.hosts.exists())


if __name__ == "__main__":
    unittest.main()
