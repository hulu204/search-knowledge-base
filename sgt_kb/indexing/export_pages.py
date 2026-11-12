"""Export allowlisted, unchanged stored chunks into an offline Pages corpus.

This command reads existing chunks. It never runs an ingestion chunker, a model,
or a query-time snippet generator. See docs/STORED-EXPORT.md for the format.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import closing
import gzip
import hashlib
import json
from pathlib import Path
import re
import shutil
import sqlite3
import tempfile
import unicodedata

from sgt_kb.paths import ROOT

FORMAT_VERSION = 3
RETRIEVAL = "offline-static-lexical"
DOC_FIELDS = ("doc_id", "path", "title", "company", "tag", "date", "url")
CHUNK_FIELDS = ("chunk_id", "doc_id", "seq", "text")
FLAT_FIELDS = set(DOC_FIELDS) | set(CHUNK_FIELDS)
PRODUCTION_DOCS = 2402
PRODUCTION_CHUNKS = 25838
PRODUCTION_DOC_IDS_SHA256 = "0cb203aa14438799f4bfd4d61861817dab28c3873255a2f4dacf4da3566231eb"
POSTING_SHARDS = 256
TEXT_SHARD_BYTES = 128 * 1024
OWNED_MARKER = ".sgt-pages-export"


def _json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def normalize(value):
    """Match the browser's NFKC/lowercase/whitespace lexical normalization."""
    # ECMAScript's \s differs from Python's str.split()/re \s, and leading or
    # trailing whitespace is significant to the browser's normalized length.
    return re.sub(r"[ \t\n\r\v\f\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000\ufeff]+", " ",
                  unicodedata.normalize("NFKC", value).lower())


def _cjk(char):
    code = ord(char)
    return (0x3400 <= code <= 0x4DBF or 0x4E00 <= code <= 0x9FFF
            or 0xF900 <= code <= 0xFAFF or 0x20000 <= code <= 0x323AF
            or 0x3040 <= code <= 0x30FF or 0x31F0 <= code <= 0x31FF)


def lexical_tokens(value):
    """Body-only CJK bigrams and Unicode words; deliberately no CJK unigrams."""
    tokens = []
    run = ""
    kind = None

    def flush():
        if kind == "c":
            tokens.extend("c:" + run[i:i + 2] for i in range(len(run) - 1))
        elif run:
            tokens.append("w:" + run)

    for char in normalize(value):
        next_kind = "c" if _cjk(char) else "w" if (char.isalnum() or unicodedata.category(char).startswith("M") or char == "_") else None
        if next_kind != kind or next_kind is None:
            flush()
            run = ""
        if next_kind:
            run += char
        kind = next_kind
    flush()
    return tokens


def posting_bucket(token):
    value = 2166136261
    for byte in token.encode("utf-8"):
        value = ((value ^ byte) * 16777619) & 0xFFFFFFFF
    return f"{value % POSTING_SHARDS:02x}"


def public_allowlist(base):
    articles = Path(base) / "articles"
    if not articles.is_dir():
        raise ValueError("A public checkout with articles/*.md is required")
    result = {path.stem for path in articles.glob("*.md") if path.is_file()}
    if not result:
        raise ValueError("The public article allowlist must not be empty")
    return result


def _source_doc(row, allowlist, *, strict):
    if not isinstance(row, dict) or set(row) - set(DOC_FIELDS):
        raise ValueError("Source metadata contains unsupported fields")
    doc_id, path = row.get("doc_id"), row.get("path")
    if not isinstance(doc_id, str) or not doc_id or "/" in doc_id or "\\" in doc_id or doc_id in {".", ".."}:
        raise ValueError("Refused document identifier")
    if not isinstance(path, str):
        raise ValueError("Refused source path")
    expected = f"articles/{doc_id}.md"
    if doc_id not in allowlist or path != expected:
        # A mixed production database is expected to contain private extra-docs.
        # They are excluded before any chunk text is emitted. An intermediate,
        # unlike the production DB, must already be entirely public.
        private_parts = path.split("/")
        safe_private = (len(private_parts) > 1 and private_parts[0] == "extra-docs"
                        and all(part not in {"", ".", ".."} for part in private_parts)
                        and "\\" not in path and "\x00" not in path)
        if not strict and doc_id not in allowlist and (path == expected or safe_private):
            return None
        raise ValueError("Refused document outside the public articles allowlist or safe articles/<doc_id>.md path")
    result = {}
    for key in DOC_FIELDS:
        value = row.get(key, "")
        if value is None and key not in {"doc_id", "path", "title"}:
            value = ""
        if not isinstance(value, str):
            raise ValueError(f"Source field {key} must be text")
        result[key] = value
    return result


def _validate_chunk(row, docs):
    if not isinstance(row, dict) or set(row) != set(CHUNK_FIELDS):
        raise ValueError("Each chunk must contain only chunk_id, doc_id, seq, text")
    if (type(row["chunk_id"]) is not int or row["chunk_id"] < 0
            or type(row["seq"]) is not int or row["seq"] < 0
            or not isinstance(row["text"], str)
            or not isinstance(row["doc_id"], str)
            or row["doc_id"] not in docs):
        raise ValueError("Invalid or orphan stored chunk")
    return dict(row)


def _finish_rows(docs, rows):
    chunks = []
    identifiers, sequences = set(), set()
    for row in rows:
        chunk = _validate_chunk(row, docs)
        if chunk["chunk_id"] in identifiers or (chunk["doc_id"], chunk["seq"]) in sequences:
            raise ValueError("Duplicate stored chunk identifier or document sequence")
        identifiers.add(chunk["chunk_id"])
        sequences.add((chunk["doc_id"], chunk["seq"]))
        chunks.append(chunk)
    return sorted(docs.values(), key=lambda doc: doc["doc_id"]), sorted(chunks, key=lambda chunk: chunk["chunk_id"])


def read_sqlite(db, allowlist):
    """Read the production docs/chunks schema using SQLite URI mode=ro."""
    db = Path(db).resolve()
    docs, all_ids, excluded = {}, set(), 0
    with closing(sqlite3.connect(db.as_uri() + "?mode=ro", uri=True)) as conn:
        conn.row_factory = sqlite3.Row
        # Old demo databases advertise byte cuts. Do not relabel their stored
        # fallback boundaries as production token-budget chunks.
        if conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='ingestion_metadata'").fetchone():
            metadata = dict(conn.execute("SELECT key, value FROM ingestion_metadata"))
            if "utf8-bytes" in str(metadata.get("token_budget", "")):
                raise ValueError("Refused utf8-bytes fallback chunks; export the production stored chunks")
        for row in conn.execute("SELECT " + ",".join(DOC_FIELDS) + " FROM docs ORDER BY doc_id"):
            raw = dict(row)
            if raw["doc_id"] in all_ids:
                raise ValueError("Duplicate source document")
            all_ids.add(raw["doc_id"])
            doc = _source_doc(raw, allowlist, strict=False)
            if doc is None:
                excluded += 1
            else:
                docs[doc["doc_id"]] = doc
        rows = []
        for row in conn.execute("SELECT chunk_id,doc_id,seq,text FROM chunks ORDER BY chunk_id"):
            if row["doc_id"] not in all_ids:
                raise ValueError("Orphan stored chunk in SQLite")
            if row["doc_id"] in docs:
                rows.append(dict(row))
    source_docs, chunks = _finish_rows(docs, rows)
    return source_docs, chunks, {"kind": "sqlite-read-only", "excluded_docs": excluded}


def _load_json(path):
    with path.open("rb") as stream:
        if stream.read(16).startswith(b"SQLite format 3"):
            raise ValueError("Raw SQLite files are not an intermediate export")
    if path.suffix.lower() not in {".json", ".jsonl"}:
        raise ValueError("Intermediate exports must be .json or .jsonl files")
    if path.suffix.lower() == ".jsonl":
        with path.open(encoding="utf-8") as stream:
            return [json.loads(line) for line in stream if line.strip()]
    return json.loads(path.read_text(encoding="utf-8"))


def read_intermediate(source, allowlist):
    """Read strict flat JSONL rows or a JSON {docs: [...], chunks: [...]} export."""
    source = Path(source)
    files = sorted(source.glob("*.jsonl")) if source.is_dir() else [source]
    if not files:
        raise ValueError("An intermediate directory must contain JSONL chunk rows")
    docs, chunks = {}, []

    def add_doc(row):
        doc = _source_doc(row, allowlist, strict=True)
        previous = docs.get(doc["doc_id"])
        if previous is not None and previous != doc:
            raise ValueError("Conflicting source metadata in intermediate export")
        docs[doc["doc_id"]] = doc

    for path in files:
        value = _load_json(path)
        if isinstance(value, dict):
            if set(value) != {"docs", "chunks"} or not isinstance(value["docs"], list) or not isinstance(value["chunks"], list):
                raise ValueError("JSON intermediate must contain only docs and chunks arrays")
            for row in value["docs"]:
                add_doc(row)
            chunks.extend(value["chunks"])
        elif isinstance(value, list):
            for row in value:
                if not isinstance(row, dict) or set(row) != FLAT_FIELDS:
                    raise ValueError("Flat intermediate rows must contain only the documented public source and chunk fields")
                add_doc({key: row[key] for key in DOC_FIELDS})
                chunks.append({key: row[key] for key in CHUNK_FIELDS})
        else:
            raise ValueError("Invalid intermediate export")
    source_docs, chunks = _finish_rows(docs, chunks)
    return source_docs, chunks, {"kind": "allowlisted-intermediate", "excluded_docs": 0}


def _assert_output(output_dir, sources):
    output_dir = Path(output_dir).resolve()
    if output_dir.suffix.lower() in {".sqlite", ".sqlite3", ".db", ".json", ".jsonl"}:
        raise ValueError("Pages output must be a directory, never a SQLite or raw export file")
    for source in sources:
        if source is not None and Path(source).resolve().is_relative_to(output_dir):
            raise ValueError("Pages output must not contain or overwrite the source database/export")
    for name in ("search-chunks", "search-postings"):
        directory = output_dir / name
        if directory.is_symlink() or (directory.exists() and (not directory.is_dir() or not (directory / OWNED_MARKER).is_file())):
            raise ValueError(f"Refusing to replace an unowned output directory: {name}")
    for name in ("search-index.json", "search-manifest.json"):
        if (output_dir / name).is_symlink():
            raise ValueError("Refusing a symlink at an output file")
    return output_dir


def _write(path, value):
    content = _json_bytes(value)
    path.write_bytes(content)
    return {"file": str(path.name), "bytes": len(content), "gzip_bytes": len(gzip.compress(content, mtime=0)), "sha256": hashlib.sha256(content).hexdigest()}


def build_pages(docs, chunks, output_dir, *, allowlist, source, require_production_counts=False, pending=False, text_shard_bytes=TEXT_SHARD_BYTES):
    """Write lexical postings and exact chunk text shards, without segmentation."""
    counts_match = len(docs) == PRODUCTION_DOCS and len(chunks) == PRODUCTION_CHUNKS
    doc_ids_sha256 = hashlib.sha256("\n".join(doc["doc_id"] for doc in docs).encode("utf-8")).hexdigest()
    if require_production_counts and not counts_match:
        raise ValueError(f"Production counts required: expected {PRODUCTION_DOCS} docs / {PRODUCTION_CHUNKS} chunks; got {len(docs)} / {len(chunks)}")
    if require_production_counts and doc_ids_sha256 != PRODUCTION_DOC_IDS_SHA256:
        raise ValueError("Production document identifiers do not match the coordinator-verified allowlisted doc_id SHA256")
    if text_shard_bytes <= 0:
        raise ValueError("The text shard byte target must be positive")
    output_dir = Path(output_dir)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".sgt-pages-", dir=output_dir.parent) as temporary:
        stage = Path(temporary)
        text_dir, posting_dir = stage / "search-chunks", stage / "search-postings"
        for directory in (text_dir, posting_dir):
            directory.mkdir()
            (directory / OWNED_MARKER).write_text("sgt-kb Pages format 3\n", encoding="utf-8")
        docs_by_id = {doc["doc_id"]: index for index, doc in enumerate(docs)}
        chunk_rows, text_shards, pending_chunks = [], [], []
        shard_size = len(_json_bytes({"format_version": FORMAT_VERSION, "chunks": []}))

        def finish_text_shard():
            if pending_chunks:
                filename = f"{len(text_shards):04d}.json"
                info = _write(text_dir / filename, {"format_version": FORMAT_VERSION, "chunks": pending_chunks})
                info.update(file="search-chunks/" + filename, chunks=len(pending_chunks))
                text_shards.append(info)
                pending_chunks.clear()

        postings = [{} for _ in range(POSTING_SHARDS)]
        for index, chunk in enumerate(chunks):
            chunk_size = len(_json_bytes(chunk))
            if pending_chunks and shard_size + chunk_size > text_shard_bytes:
                finish_text_shard()
                shard_size = len(_json_bytes({"format_version": FORMAT_VERSION, "chunks": []}))
            chunk_rows.append([chunk["chunk_id"], docs_by_id[chunk["doc_id"]], chunk["seq"], len(text_shards), len(normalize(chunk["text"]))])
            pending_chunks.append(chunk)
            shard_size += chunk_size
            for token, frequency in sorted(Counter(lexical_tokens(chunk["text"])).items()):
                postings[int(posting_bucket(token), 16)].setdefault(token, []).append([index, frequency])
        finish_text_shard()
        posting_files = []
        for bucket, entries in enumerate(postings):
            if entries:
                filename = f"{bucket:02x}.json"
                info = _write(posting_dir / filename, dict(sorted(entries.items())))
                info.update(file="search-postings/" + filename, bucket=f"{bucket:02x}")
                posting_files.append(info)
        status = "pending-production-export" if pending else "stored-chunks"
        bootstrap = {
            "format_version": FORMAT_VERSION, "retrieval": RETRIEVAL, "status": status,
            "docs": docs, "chunks": chunk_rows, "posting_shards": POSTING_SHARDS,
            "posting_buckets": [item["bucket"] for item in posting_files],
            "posting_path": "search-postings/{bucket}.json", "text_shards": text_shards,
            "manifest": "search-manifest.json",
        }
        index_info = _write(stage / "search-index.json", bootstrap)
        manifest = {
            "format_version": FORMAT_VERSION, "retrieval": RETRIEVAL, "status": status,
            "chunk_boundaries": "unmodified-stored-chunks" if not pending else "no-corpus-integrated",
            "public_article_files": len(allowlist), "doc_count": len(docs), "chunk_count": len(chunks),
            "source": source,
            "expected_production": {"doc_count": PRODUCTION_DOCS, "chunk_count": PRODUCTION_CHUNKS, "counts_match": counts_match,
                                    "doc_ids_sha256": PRODUCTION_DOC_IDS_SHA256, "doc_ids_match": doc_ids_sha256 == PRODUCTION_DOC_IDS_SHA256},
            "doc_ids_sha256_newline": doc_ids_sha256,
            "first_load_index": index_info,
            "posting_bytes": sum(item["bytes"] for item in posting_files),
            "text_bytes": sum(item["bytes"] for item in text_shards),
            "max_text_shard_bytes": max((item["bytes"] for item in text_shards), default=0),
            "posting_files": posting_files, "text_shards": text_shards,
        }
        _write(stage / "search-manifest.json", manifest)
        output_dir.mkdir(parents=True, exist_ok=True)
        # Only replace the two explicitly marked exporter-owned directories.
        for name in ("search-chunks", "search-postings"):
            target = output_dir / name
            if target.exists():
                shutil.rmtree(target)
            (stage / name).replace(target)
        for name in ("search-index.json", "search-manifest.json"):
            (stage / name).replace(output_dir / name)
    return manifest


def export_pages(*, db=None, intermediate=None, output_dir=ROOT / "docs", base=ROOT, require_production_counts=False, write_intermediate=None, pending=False, text_shard_bytes=TEXT_SHARD_BYTES):
    if sum((db is not None, intermediate is not None, bool(pending))) != 1:
        raise ValueError("Choose exactly one of db, intermediate, or pending")
    output_dir = _assert_output(output_dir, (db, intermediate))
    allowlist = public_allowlist(base)
    if pending:
        docs, chunks, source = [], [], {"kind": "pending-coordinator-production-export", "excluded_docs": 0}
    elif db is not None:
        docs, chunks, source = read_sqlite(db, allowlist)
    else:
        docs, chunks, source = read_intermediate(intermediate, allowlist)
    if write_intermediate is not None:
        if Path(write_intermediate).is_symlink():
            raise ValueError("Refusing an intermediate output symlink")
        destination = Path(write_intermediate).resolve()
        if destination.suffix.lower() != ".jsonl" or any(item is not None and destination == Path(item).resolve() for item in (db, intermediate)):
            raise ValueError("Intermediate output must be a separate .jsonl file; never a raw SQLite copy")
        if intermediate is not None and Path(intermediate).is_dir() and destination.is_relative_to(Path(intermediate).resolve()):
            raise ValueError("Intermediate output must not overwrite any source export directory")
        inputs = ([Path(db)] if db is not None else
                  list(Path(intermediate).glob("*.jsonl")) if intermediate is not None and Path(intermediate).is_dir() else
                  [Path(intermediate)] if intermediate is not None else [])
        if destination.exists() and any(destination.samefile(item) for item in inputs):
            raise ValueError("Intermediate output must not alias a source database/export inode")
        if destination.is_relative_to(output_dir / "search-chunks") or destination.is_relative_to(output_dir / "search-postings"):
            raise ValueError("Intermediate output must not overlap generated shards")
    manifest = build_pages(docs, chunks, output_dir, allowlist=allowlist, source=source,
                           require_production_counts=require_production_counts,
                           pending=pending, text_shard_bytes=text_shard_bytes)
    if write_intermediate is not None:
        by_id = {doc["doc_id"]: doc for doc in docs}
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(prefix=".sgt-public-", suffix=".jsonl", dir=destination.parent, delete=False) as stream:
                temporary_path = Path(stream.name)
                for chunk in chunks:
                    stream.write(_json_bytes({**by_id[chunk["doc_id"]], **chunk}))
            temporary_path.replace(destination)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sources = parser.add_mutually_exclusive_group(required=True)
    sources.add_argument("--db", type=Path, help="Production SQLite, opened using mode=ro")
    sources.add_argument("--input", type=Path, help="Allowlisted JSON/JSONL intermediate, or directory of JSONL files")
    sources.add_argument("--pending", action="store_true", help="Write an empty Pages corpus explicitly awaiting production export")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "docs")
    parser.add_argument("--require-production-counts", action="store_true", help="Require 2402 docs, 25838 stored chunks, and the coordinator-verified doc_id SHA256")
    parser.add_argument("--write-intermediate", type=Path, help="Optionally write allowlisted flat public rows to a separate .jsonl")
    args = parser.parse_args(argv)
    try:
        manifest = export_pages(db=args.db, intermediate=args.input, output_dir=args.output_dir,
                                require_production_counts=args.require_production_counts,
                                write_intermediate=args.write_intermediate, pending=args.pending)
    except (ValueError, OSError, sqlite3.Error) as error:
        parser.error(str(error))
    print(f"{manifest['status']}: {manifest['doc_count']} public docs / {manifest['chunk_count']} unchanged stored chunks; "
          f"first-load index {manifest['first_load_index']['bytes']} bytes")


if __name__ == "__main__":
    main()
