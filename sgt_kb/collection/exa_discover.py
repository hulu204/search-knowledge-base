# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///
"""Discover authoritative search/RAG sources through Exa MCP, one query per run."""
from __future__ import annotations

import argparse
import csv
import json
import os
import tempfile
import time
from datetime import datetime
from pathlib import Path

from sgt_kb.collection.english_sources import CURATED_HOSTS, normalize_host, title_is_relevant
from sgt_kb.collection.exa_mcp import ExaMcpClient
from sgt_kb.collection.review_queue import QUEUE, enqueue_candidate


from sgt_kb.paths import ROOT

BASE = ROOT
HOSTS_FILE = BASE / "ingestion" / "exa_source_hosts.csv"
STATE_FILE = BASE / "ingestion" / "exa_discovery_state.json"
HOST_FIELDS = [
    "host", "status", "discoveries", "relevant_titles", "first_seen",
    "last_seen", "last_title", "last_url",
]
QUERIES = (
    "search retrieval ranking relevance engineering architecture",
    "RAG retrieval reranking evaluation production engineering",
    "vector search ANN HNSW indexing benchmark engineering",
    "query understanding recommendation advertising ranking engineering",
    "web crawling indexing search engine architecture engineering",
    "hybrid retrieval BM25 embeddings reciprocal rank fusion",
)


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_hosts(path: Path = HOSTS_FILE) -> dict[str, dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return {row["host"]: row for row in csv.DictReader(handle)}
    except FileNotFoundError:
        return {}


def save_hosts(hosts: dict[str, dict[str, str]], path: Path = HOSTS_FILE) -> None:
    from io import StringIO

    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=HOST_FIELDS)
    writer.writeheader()
    writer.writerows(hosts[host] for host in sorted(hosts))
    atomic_text(path, buffer.getvalue())


def load_state(path: Path = STATE_FILE) -> dict:
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    return state if isinstance(state, dict) else {}


def discover(
    results: list[dict], query: str, queue: Path = QUEUE,
    hosts_path: Path = HOSTS_FILE, dry_run: bool = False,
) -> dict[str, int]:
    hosts = load_hosts(hosts_path)
    counts = {"results": 0, "relevant": 0, "queued": 0, "new_hosts": 0}
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    for result in results:
        title = str(result.get("title") or "").strip()
        url = str(result.get("url") or "").strip()
        host = normalize_host(url)
        if not title or not host or not url.startswith(("http://", "https://")):
            continue
        counts["results"] += 1
        relevant = title_is_relevant(title)
        counts["relevant"] += int(relevant)
        row = hosts.get(host)
        if row is None:
            counts["new_hosts"] += 1
            row = {
                "host": host,
                "status": "curated" if host in CURATED_HOSTS else "candidate",
                "discoveries": "0",
                "relevant_titles": "0",
                "first_seen": now,
                "last_seen": now,
                "last_title": "",
                "last_url": "",
            }
            hosts[host] = row
        row["discoveries"] = str(int(row.get("discoveries") or 0) + 1)
        row["relevant_titles"] = str(
            int(row.get("relevant_titles") or 0) + int(relevant)
        )
        row["last_seen"] = now
        row["last_title"] = title
        row["last_url"] = url
        if not relevant or row["status"] == "blocked" or dry_run:
            continue
        published = str(result.get("publishedDate") or "")[:10]
        if enqueue_candidate(host, title, published, url, None, queue):
            counts["queued"] += 1
    if not dry_run:
        save_hosts(hosts, hosts_path)
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query")
    parser.add_argument("--num-results", type=int, default=20)
    parser.add_argument("--since", default="2024-01-01")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.num_results <= 100:
        parser.error("--num-results must be between 1 and 100")
    state = load_state()
    cursor = int(state.get("query_cursor") or 0) % len(QUERIES)
    query = args.query or QUERIES[cursor]
    results = ExaMcpClient().search(query, args.num_results, args.since)
    counts = discover(results, query, dry_run=args.dry_run)
    if not args.dry_run:
        state.update({
            "updated_at": int(time.time()),
            "query_cursor": (cursor + 1) % len(QUERIES),
            "last_query": query,
            "last_counts": counts,
        })
        atomic_text(STATE_FILE, json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"query": query, **counts}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
