# /// script
# requires-python = ">=3.10"
# dependencies = ["requests", "beautifulsoup4", "lxml", "markdownify"]
# ///
"""Persistent, idempotent ingestion queue for shared URLs."""
import argparse
import json
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from sgt_kb.collection.ingest_url import ingest, normalize_url

from sgt_kb.paths import ROOT

BASE = ROOT
QUEUE_DIR = BASE / "ingestion"
DB = QUEUE_DIR / "jobs.sqlite"
SHANGHAI = ZoneInfo("Asia/Shanghai")


def now() -> str:
    return datetime.now(SHANGHAI).isoformat(timespec="seconds")


def connect(path: Path = DB) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS jobs(
            job_id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            source TEXT NOT NULL,
            source_message_id TEXT UNIQUE,
            status TEXT NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0,
            error TEXT NOT NULL DEFAULT '',
            result_json TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_jobs_status_id
            ON jobs(status, job_id);
        """
    )
    return conn


def enqueue(
    url: str,
    source: str = "manual",
    source_message_id: str = "",
    db_path: Path = DB,
) -> dict:
    normalized = normalize_url(url)
    stamp = now()
    with connect(db_path) as conn:
        try:
            cursor = conn.execute(
                """
                INSERT INTO jobs(
                    url, source, source_message_id, status, created_at, updated_at
                ) VALUES(?, ?, NULLIF(?, ''), 'queued', ?, ?)
                """,
                (normalized, source, source_message_id, stamp, stamp),
            )
            job_id = cursor.lastrowid
            created = True
        except sqlite3.IntegrityError:
            row = conn.execute(
                """
                SELECT * FROM jobs
                WHERE url=? OR (source_message_id IS NOT NULL AND source_message_id=?)
                ORDER BY job_id LIMIT 1
                """,
                (normalized, source_message_id),
            ).fetchone()
            if row is None:
                raise
            job_id = row["job_id"]
            created = False
        row = conn.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
    result = dict(row)
    result["created"] = created
    return result


def get_job(job_id: int, db_path: Path = DB) -> dict | None:
    with connect(db_path) as conn:
        row = conn.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
    return dict(row) if row else None


def _claim(db_path: Path = DB, max_attempts: int = 3) -> dict | None:
    with connect(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            """
            SELECT * FROM jobs
            WHERE status='queued'
               OR (status='failed' AND attempts < ?)
            ORDER BY job_id LIMIT 1
            """,
            (max_attempts,),
        ).fetchone()
        if row is None:
            conn.commit()
            return None
        updated = conn.execute(
            """
            UPDATE jobs
            SET status='running', attempts=attempts+1, error='', updated_at=?
            WHERE job_id=? AND status IN ('queued', 'failed')
            """,
            (now(), row["job_id"]),
        )
        conn.commit()
        if updated.rowcount != 1:
            return None
        return dict(
            conn.execute(
                "SELECT * FROM jobs WHERE job_id=?", (row["job_id"],)
            ).fetchone()
        )


def run_once(db_path: Path = DB, ingest_func=ingest) -> dict | None:
    job = _claim(db_path)
    if job is None:
        return None
    try:
        result = ingest_func(job["url"], origin=job["source"])
        status, error = "succeeded", ""
        result_json = json.dumps(result, ensure_ascii=False)
    except Exception as exc:
        status = "failed"
        error = f"{type(exc).__name__}: {exc}"
        result_json = ""
    with connect(db_path) as conn:
        conn.execute(
            """
            UPDATE jobs
            SET status=?, error=?, result_json=?, updated_at=?
            WHERE job_id=?
            """,
            (status, error, result_json, now(), job["job_id"]),
        )
    return get_job(job["job_id"], db_path)


def work(db_path: Path = DB, poll_seconds: float = 2.0):
    while True:
        job = run_once(db_path)
        if job:
            print(json.dumps(job, ensure_ascii=False), flush=True)
        else:
            time.sleep(poll_seconds)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=DB)
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("enqueue")
    add.add_argument("url")
    add.add_argument("--source", default="manual")
    add.add_argument("--message-id", default="")
    worker = sub.add_parser("work")
    worker.add_argument("--once", action="store_true")
    worker.add_argument("--poll-seconds", type=float, default=2.0)
    args = parser.parse_args()

    if args.command == "enqueue":
        result = enqueue(args.url, args.source, args.message_id, args.db)
    elif args.once:
        result = run_once(args.db) or {"status": "idle"}
    else:
        work(args.db, args.poll_seconds)
        return 0
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
