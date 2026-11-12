# /// script
# requires-python = ">=3.10"
# dependencies = ["requests", "beautifulsoup4", "lxml", "markdownify"]
# ///
"""Manage the human-review queue for English source candidates.

The queue is a CSV so it stays easy to inspect and edit.  This module adds the
missing lifecycle around it: URL-level deduplication, explicit decisions, and
ingestion of approved rows.
"""
from __future__ import annotations

import argparse
import csv
import fcntl
import hashlib
import json
import os
import shutil
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Callable
from urllib.parse import urlsplit, urlunsplit

from sgt_kb.collection.english_sources import host_is_curated, title_is_relevant

from sgt_kb.paths import ROOT

BASE = ROOT
QUEUE = BASE / "ingestion" / "review_queue.csv"
FIELDS = [
    "id", "company", "title", "date", "url", "margin", "added_at",
    "status", "reviewed_at", "error",
    "claim_id", "claimed_at",
]
VALID_STATUSES = {"pending", "approved", "processing", "rejected", "ingested", "failed"}
STATUS_PRIORITY = {
    "pending": 0, "failed": 1, "processing": 2,
    "approved": 3, "rejected": 4, "ingested": 5,
}
PROCESSING_LEASE_SECONDS = 7200


def normalize_candidate_url(url: str) -> str:
    parts = urlsplit(url.strip())
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        raise ValueError(f"invalid candidate URL: {url!r}")
    path = "/".join(part for part in parts.path.split("/") if part)
    path = f"/{path}" if path else "/"
    return urlunsplit(("https", parts.netloc.lower(), path, parts.query, ""))


def candidate_id(url: str) -> str:
    return hashlib.sha256(normalize_candidate_url(url).encode()).hexdigest()[:12]


def _canonical_record(row: dict[str, str]) -> dict[str, str]:
    raw_status = (row.get("status") or "").strip()
    if raw_status and raw_status not in VALID_STATUSES:
        raise ValueError(f"invalid status: {raw_status!r}")
    status = raw_status or "pending"
    url = normalize_candidate_url(row.get("url", ""))
    return {
        "id": row.get("id") or candidate_id(url),
        "company": row.get("company", "").strip(),
        "title": row.get("title", "").strip(),
        "date": row.get("date", "").strip(),
        "url": url,
        "margin": row.get("margin", "").strip(),
        "added_at": row.get("added_at", "").strip(),
        "status": status,
        "reviewed_at": row.get("reviewed_at", "").strip(),
        "error": row.get("error", "").strip(),
        "claim_id": row.get("claim_id", "").strip(),
        "claimed_at": row.get("claimed_at", "").strip(),
    }


def _load_queue_report(path: Path) -> tuple[list[dict[str, str]], int, int]:
    if not path.exists():
        return [], 0, 0
    records: dict[str, dict[str, str]] = {}
    duplicates = 0
    invalid = 0
    with path.open(encoding="utf-8", newline="") as handle:
        for raw in csv.DictReader(handle):
            try:
                record = _canonical_record(raw)
            except ValueError:
                invalid += 1
                continue
            key = record["url"]
            if key in records:
                duplicates += 1
                current = records[key]
                for field in ("company", "title", "date", "margin"):
                    if not current[field] and record[field]:
                        current[field] = record[field]
                if record["added_at"] and (
                    not current["added_at"] or record["added_at"] < current["added_at"]
                ):
                    current["added_at"] = record["added_at"]
                if STATUS_PRIORITY[record["status"]] > STATUS_PRIORITY[current["status"]]:
                    for field in ("status", "reviewed_at", "error", "claim_id", "claimed_at"):
                        current[field] = record[field]
                continue
            records[key] = record
    return list(records.values()), duplicates, invalid


def load_queue(path: Path = QUEUE) -> tuple[list[dict[str, str]], int]:
    records, duplicates, invalid = _load_queue_report(path)
    if invalid:
        raise ValueError(f"queue contains {invalid} invalid row(s)")
    return records, duplicates


def save_queue(records: list[dict[str, str]], path: Path = QUEUE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in FIELDS} for row in records)
        temp_path = Path(handle.name)
    os.replace(temp_path, path)


def _locked_update(update: Callable[[list[dict[str, str]]], bool], path: Path = QUEUE) -> bool:
    lock_path = path.with_suffix(path.suffix + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+") as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        records, duplicates, invalid = _load_queue_report(path)
        if invalid:
            raise ValueError(f"queue contains {invalid} invalid row(s); update aborted")
        changed = update(records)
        if changed or duplicates:
            save_queue(records, path)
        return changed


def enqueue_candidate(
    company: str,
    title: str,
    date: str,
    url: str,
    margin: float | None,
    path: Path = QUEUE,
    status: str = "pending",
    error: str = "",
) -> bool:
    if status not in {"pending", "rejected", "ingested", "failed"}:
        raise ValueError(f"unsupported initial status: {status}")
    normalized = normalize_candidate_url(url)

    def append_if_missing(records: list[dict[str, str]]) -> bool:
        if any(row["url"] == normalized for row in records):
            return False
        records.append({
            "id": candidate_id(normalized),
            "company": company,
            "title": title,
            "date": date,
            "url": normalized,
            "margin": "" if margin is None else str(margin),
            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": status,
            "reviewed_at": (
                datetime.now().strftime("%Y-%m-%d %H:%M")
                if status != "pending" else ""
            ),
            "error": error,
            "claim_id": "",
            "claimed_at": "",
        })
        return True

    return _locked_update(append_if_missing, path)


def set_decision(
    ids: set[str], status: str, path: Path = QUEUE, require_all: bool = False
) -> int:
    if status not in {"approved", "rejected"}:
        raise ValueError(f"unsupported decision: {status}")
    changed_count = 0

    def update(records: list[dict[str, str]]) -> bool:
        nonlocal changed_count
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        by_id = {row["id"]: row for row in records}
        missing = ids - by_id.keys()
        allowed = (
            {"pending", "failed", "rejected"}
            if status == "approved"
            else {"pending", "failed", "approved"}
        )
        blocked = {
            candidate for candidate in ids
            if candidate in by_id and by_id[candidate]["status"] not in allowed
        }
        if require_all and (missing or blocked):
            raise ValueError(
                f"decision rejected; missing={sorted(missing)} blocked={sorted(blocked)}"
            )
        for row in records:
            if row["id"] in ids and row["status"] in allowed:
                row["status"] = status
                row["reviewed_at"] = now
                row["error"] = ""
                row["claim_id"] = ""
                row["claimed_at"] = ""
                changed_count += 1
        return changed_count > 0

    _locked_update(update, path)
    return changed_count


def _parse_timestamp(value: str) -> datetime | None:
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def claim_next_approved(path: Path = QUEUE) -> dict[str, str] | None:
    claimed: dict[str, str] | None = None

    def claim(records: list[dict[str, str]]) -> bool:
        nonlocal claimed
        now = datetime.now()
        changed = False
        for row in records:
            if row["status"] != "processing":
                continue
            started = _parse_timestamp(row["claimed_at"])
            if started is None or (now - started).total_seconds() >= PROCESSING_LEASE_SECONDS:
                row["status"] = "approved"
                row["claim_id"] = ""
                row["claimed_at"] = ""
                row["error"] = "recovered expired processing lease"
                changed = True
        for row in records:
            if row["status"] != "approved":
                continue
            row["status"] = "processing"
            row["claim_id"] = uuid.uuid4().hex
            row["claimed_at"] = now.strftime("%Y-%m-%d %H:%M:%S")
            claimed = row.copy()
            return True
        return changed

    _locked_update(claim, path)
    return claimed


def complete_claim(
    candidate: dict[str, str], status: str, error: str, path: Path = QUEUE
) -> bool:
    if status not in {"ingested", "failed"}:
        raise ValueError(f"invalid claim outcome: {status}")

    def complete(records: list[dict[str, str]]) -> bool:
        for row in records:
            if (
                row["id"] == candidate["id"]
                and row["status"] == "processing"
                and row["claim_id"] == candidate["claim_id"]
            ):
                row["status"] = status
                row["error"] = error
                row["claim_id"] = ""
                row["claimed_at"] = ""
                return True
        return False

    return _locked_update(complete, path)


def ingest_approved(
    path: Path = QUEUE,
    ingest_fn: Callable[..., dict] | None = None,
) -> dict[str, int]:
    if ingest_fn is None:
        from sgt_kb.collection.en_poll import classify_tag
        from sgt_kb.collection.ingest_url import ingest

        def ingest_fn(**record):
            host = urlsplit(record["url"]).hostname or ""
            allowed_hosts = {host, host.removeprefix("www."), f"www.{host.removeprefix('www.')}"}
            return ingest(
                record["url"], company=record["company"],
                tag=classify_tag(record["title"]), origin="en-rss-review",
                skip_index=True, allowed_hosts=allowed_hosts,
                title=record["title"], date=record["date"],
            )

    counts = {"ingested": 0, "existing": 0, "failed": 0}
    while True:
        row = claim_next_approved(path)
        if row is None:
            break
        try:
            result = ingest_fn(**row)
            result_status = result.get("status", "")
            if result_status == "ingested":
                count_key = "ingested"
            elif result_status in {"existing_url", "existing_content"}:
                count_key = "existing"
            else:
                raise RuntimeError(f"unexpected ingest status: {result_status!r}")
            if not complete_claim(row, "ingested", "", path):
                raise RuntimeError("claim lost before completion")
            counts[count_key] += 1
        except BaseException as exc:
            counts["failed"] += 1
            complete_claim(row, "failed", f"{type(exc).__name__}: {exc}", path)
            if not isinstance(exc, Exception):
                raise
    return counts


def migrate_queue(path: Path = QUEUE) -> dict[str, object]:
    result: dict[str, object] = {}

    def migrate(_records: list[dict[str, str]]) -> bool:
        records, duplicates, invalid = _load_queue_report(path)
        if invalid:
            raise ValueError(f"queue contains {invalid} invalid URL row(s); migration aborted")
        if any(row["status"] == "processing" for row in records):
            raise ValueError("queue has active processing rows; migration aborted")
        backup = ""
        if path.exists():
            backup_path = path.with_suffix(path.suffix + f".bak-{datetime.now():%Y%m%d%H%M%S%f}")
            shutil.copy2(path, backup_path)
            backup = str(backup_path)
        save_queue(records, path)
        result.update(rows=len(records), duplicates_removed=duplicates, backup=backup)
        return False

    _locked_update(migrate, path)
    return result


def select_rows(
    records: list[dict[str, str]], status: str, since: str, limit: int
) -> list[dict[str, str]]:
    selected = [
        row for row in records
        if (status == "all" or row["status"] == status)
        and (not since or row["date"] >= since)
    ]
    selected.sort(key=lambda row: (row["date"], row["added_at"]), reverse=True)
    return selected[:limit]


def auto_triage_pending(path: Path = QUEUE, dry_run: bool = False) -> dict[str, int]:
    counts = {"approved": 0, "rejected": 0, "deferred_host": 0}

    def triage(records: list[dict[str, str]]) -> bool:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        for row in records:
            if row["status"] != "pending":
                continue
            if not host_is_curated(row["url"]):
                counts["deferred_host"] += 1
                continue
            relevant = title_is_relevant(row["title"])
            target = "approved" if relevant else "rejected"
            counts[target] += 1
            if dry_run:
                continue
            row["status"] = target
            row["reviewed_at"] = now
            row["error"] = f"auto-title:{'relevant' if relevant else 'irrelevant'}"
            row["claim_id"] = ""
            row["claimed_at"] = ""
        return not dry_run and (counts["approved"] + counts["rejected"] > 0)

    _locked_update(triage, path)
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("migrate")
    listing = sub.add_parser("list")
    listing.add_argument("--status", choices=["all", *sorted(VALID_STATUSES)], default="pending")
    listing.add_argument("--since", default="")
    listing.add_argument("--limit", type=int, default=50)
    for command in ("approve", "reject"):
        decision = sub.add_parser(command)
        decision.add_argument("ids", nargs="+")
    sub.add_parser("ingest-approved")
    triage = sub.add_parser("auto-triage")
    triage.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.command == "migrate":
        print(json.dumps(migrate_queue(), ensure_ascii=False))
        return 0
    if args.command == "list":
        records, _ = load_queue()
        print(json.dumps(select_rows(records, args.status, args.since, args.limit), ensure_ascii=False, indent=2))
        return 0
    if args.command in {"approve", "reject"}:
        requested = set(args.ids)
        target = "approved" if args.command == "approve" else "rejected"
        try:
            changed = set_decision(requested, target, require_all=True)
        except ValueError as exc:
            print(json.dumps({"error": str(exc)}, ensure_ascii=False))
            return 2
        print(json.dumps({"updated": changed}, ensure_ascii=False))
        return 0
    if args.command == "auto-triage":
        print(json.dumps(auto_triage_pending(dry_run=args.dry_run), ensure_ascii=False))
        return 0
    result = ingest_approved()
    print(json.dumps(result, ensure_ascii=False))
    return 1 if result["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
