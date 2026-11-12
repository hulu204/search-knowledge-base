#!/usr/bin/env python3
"""Export exact public SQLite ingestion chunks for offline Pages retrieval.

No article text is cut, summarized or re-chunked here. Build the public database:
  python3 build_index.py --lexical-only --public-only
Then export it:
  python3 export_pages.py
"""
import argparse
import json
import sqlite3
from contextlib import closing
from pathlib import Path

from sgt_kb.paths import ROOT

BASE = ROOT


def export_index(db: Path, output: Path, *, base: Path = BASE):
    # Read-only also prevents silently creating a missing database.
    with closing(sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True)) as conn:
        conn.row_factory = sqlite3.Row
        ingestion = dict(conn.execute("SELECT key, value FROM ingestion_metadata"))
        if ingestion.get("public_only") != "true":
            raise ValueError("Pages export requires a --public-only ingested index")
        docs = [dict(row) for row in conn.execute("SELECT * FROM docs ORDER BY doc_id")]
        public_ids = {path.stem for path in (base / "articles").glob("*.md")}
        for doc in docs:
            path = Path(doc["path"])
            if (doc["doc_id"] not in public_ids or path.parts != ("articles", doc["doc_id"] + ".md")):
                raise ValueError("Refusing to export a document outside the public articles corpus")
        chunks = [dict(row) for row in conn.execute(
            "SELECT chunk_id, doc_id, seq, text FROM chunks ORDER BY chunk_id"
        )]
        doc_ids = {doc["doc_id"] for doc in docs}
        if any(chunk["doc_id"] not in doc_ids for chunk in chunks):
            raise ValueError("Orphan chunk in ingestion index")
    data = {
        "format_version": 2,
        "retrieval": "offline-static-lexical",
        "ingestion": ingestion,
        "docs": docs,
        "chunks": chunks,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=BASE / "index/public-static/kb.sqlite")
    parser.add_argument("--output", type=Path, default=BASE / "docs/demo-index.json")
    args = parser.parse_args()
    data = export_index(args.db, args.output)
    print(f"Exported {len(data['docs'])} public docs and {len(data['chunks'])} exact stored chunks")


if __name__ == "__main__":
    main()
