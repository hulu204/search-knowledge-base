"""Read-only, allowlisted stored-chunk export; no ingestion or models required."""
from collections import Counter
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from sgt_kb.indexing.export_pages import (
    CHUNK_FIELDS, DOC_FIELDS, export_pages, lexical_tokens, normalize,
    posting_bucket, read_intermediate,
)


class PublicChunkExportTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.base = Path(self.directory.name)
        (self.base / "articles").mkdir()
        for doc_id in ("meituan-query", "tugraph", "other", "not-ingested"):
            (self.base / "articles" / f"{doc_id}.md").write_text("Allowlist only; this body is never read.", encoding="utf-8")
        self.db, self.output = self.base / "production.sqlite", self.base / "pages"
        self.docs = [self.doc("meituan-query", title="Query理解在美团搜索中的应用", company="美团"),
                     self.doc("other", title="Unicode与安全"),
                     self.doc("tugraph", title="蚂蚁 TuGraph-DB 查询图数据库", company="蚂蚁")]
        self.deep = "\n\t正文：查询理解与 Query理解改善搜索。😀 Ｑｕｅｒｙ understanding <script>alert('x')</script> & 实体。\n" * 6
        self.chunks = [
            dict(chunk_id=7, doc_id="meituan-query", seq=0, text="标题与背景，目录：一、系统简介；二、Query理解。"),
            dict(chunk_id=9, doc_id="meituan-query", seq=5, text=self.deep),
            dict(chunk_id=11, doc_id="tugraph", seq=3, text="理解图数据库的查询语言。蚂蚁 TuGraph-DB 深入图查询。"),
            dict(chunk_id=13, doc_id="other", seq=2, text="\n\t😀 cafe\u0301，ＣＡＦÉ 与𠮷野家。\ufeff "),
        ]
        with closing(sqlite3.connect(self.db)) as conn, conn:
            conn.executescript("""
                CREATE TABLE docs(doc_id TEXT PRIMARY KEY,path TEXT,title TEXT,company TEXT,tag TEXT,date TEXT,url TEXT,hash TEXT);
                CREATE TABLE chunks(chunk_id INTEGER PRIMARY KEY,doc_id TEXT,seq INTEGER,text TEXT);
                CREATE TABLE figures(figure_id TEXT,doc_id TEXT,ocr_text TEXT);
            """)
            for doc in self.docs + [self.doc("private-company", path="extra-docs/company-context.md"), self.doc("private-book", path="extra-docs/books/a-book.md"), self.doc("not-public", path="articles/not-public.md")]:
                conn.execute("INSERT INTO docs VALUES(?,?,?,?,?,?,?,?)", [doc[key] for key in DOC_FIELDS] + ["PRIVATE_HASH_SHOULD_NOT_EXPORT"])
            for chunk in self.chunks + [dict(chunk_id=99, doc_id="private-company", seq=0, text="PRIVATE_COMPANY_CONTEXT"), dict(chunk_id=100, doc_id="private-book", seq=0, text="PRIVATE_BOOK_CONTENT")]:
                conn.execute("INSERT INTO chunks VALUES(?,?,?,?)", [chunk[key] for key in CHUNK_FIELDS])
            conn.execute("INSERT INTO figures VALUES('secret','meituan-query','PRIVATE_FIGURE_OCR')")

    @staticmethod
    def doc(doc_id, *, path=None, title="公共来源", company=""):
        return dict(zip(DOC_FIELDS, (doc_id, path or f"articles/{doc_id}.md", title, company, "搜索", "2026-01-01", "https://example.test/?a=1&b=2")))

    def export(self, **kwargs):
        return export_pages(db=self.db, output_dir=self.output, base=self.base, **kwargs)

    def json(self, file):
        return json.loads((self.output / file).read_text(encoding="utf-8"))

    def emitted_chunks(self):
        return [chunk for shard in self.json("search-index.json")["text_shards"] for chunk in self.json(shard["file"])["chunks"]]

    def test_exact_stored_chunks_readonly_schema_and_private_exclusion(self):
        before = self.db.read_bytes()
        manifest = self.export(text_shard_bytes=400)
        self.assertEqual(before, self.db.read_bytes())
        self.assertEqual((3, 4, 4), (manifest["doc_count"], manifest["chunk_count"], manifest["public_article_files"]))
        self.assertEqual(3, manifest["source"]["excluded_docs"])
        self.assertEqual("sqlite-read-only", manifest["source"]["kind"])
        self.assertEqual("unmodified-stored-chunks", manifest["chunk_boundaries"])
        self.assertEqual(self.chunks, self.emitted_chunks())
        self.assertEqual(self.deep, self.emitted_chunks()[1]["text"])
        self.assertGreater(manifest["max_text_shard_bytes"], 400, "Oversized stored chunks must remain whole")
        payload = b"".join(path.read_bytes() for path in self.output.rglob("*.json"))
        for forbidden in (b"extra-docs", b"company-context", b"PRIVATE_", b"ocr_text", b'"hash"'):
            self.assertNotIn(forbidden, payload)
        self.assertIn("美团".encode(), payload, "Public company clues are preserved")
        self.assertEqual(self.docs, self.json("search-index.json")["docs"])

    def test_index_locator_posting_and_shard_integrity(self):
        manifest = self.export(text_shard_bytes=400)
        index = self.json("search-index.json")
        self.assertEqual(3, index["format_version"])
        self.assertLess(manifest["first_load_index"]["bytes"], 50_000)
        self.assertEqual(hashlib.sha256((self.output / "search-index.json").read_bytes()).hexdigest(), manifest["first_load_index"]["sha256"])
        for row, original in zip(index["chunks"], self.chunks):
            chunk_id, source, seq, shard, length = row
            self.assertEqual((original["chunk_id"], original["doc_id"], original["seq"], len(normalize(original["text"]))),
                             (chunk_id, index["docs"][source]["doc_id"], seq, length))
            self.assertIn(original, self.json(index["text_shards"][shard]["file"])["chunks"])
        for shard in index["text_shards"]:
            raw = (self.output / shard["file"]).read_bytes()
            self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()), (shard["bytes"], shard["sha256"]))
        postings = {}
        for bucket in index["posting_buckets"]:
            for token, rows in self.json(f"search-postings/{bucket}.json").items():
                self.assertEqual(bucket, posting_bucket(token))
                postings[token] = rows
        expected = {}
        for row, chunk in enumerate(self.chunks):
            for token, frequency in Counter(lexical_tokens(chunk["text"])).items():
                expected.setdefault(token, []).append([row, frequency])
        self.assertEqual(expected, postings)
        self.assertNotIn("c:查", postings)
        query_rows = set(row for row, _ in postings["c:查询"]) & set(row for row, _ in postings["c:询理"]) & set(row for row, _ in postings["c:理解"])
        self.assertEqual({1}, query_rows, "查询理解 must not nominate TuGraph via unigrams")

    def test_unicode_normalization_and_no_cjk_unigrams(self):
        self.assertEqual(" 😀 café,café 与𠮷野家。 ", normalize(self.chunks[3]["text"]))
        self.assertEqual(["c:查询", "c:询理", "c:理解", "w:query", "w:café", "c:𠮷野", "c:野家"], lexical_tokens("查询理解 Ｑｕｅｒｙ cafe\u0301 😀 𠮷野家"))
        self.assertEqual([], lexical_tokens("查 理 😀"))

    def test_intermediate_jsonl_and_json_roundtrip(self):
        intermediate = self.base / "public.jsonl"
        self.export(write_intermediate=intermediate, text_shard_bytes=400)
        expected = {p.relative_to(self.output): p.read_bytes() for p in self.output.rglob("*.json") if p.name != "search-manifest.json"}
        second = self.base / "from-jsonl"
        export_pages(intermediate=intermediate, output_dir=second, base=self.base, text_shard_bytes=400)
        self.assertEqual(expected, {p.relative_to(second): p.read_bytes() for p in second.rglob("*.json") if p.name != "search-manifest.json"})
        structured = self.base / "public.json"
        structured.write_text(json.dumps({"docs": self.docs, "chunks": self.chunks}, ensure_ascii=False), encoding="utf-8")
        docs, chunks, provenance = read_intermediate(structured, {doc["doc_id"] for doc in self.docs})
        self.assertEqual((self.docs, self.chunks), (docs, chunks))
        self.assertEqual("allowlisted-intermediate", provenance["kind"])

    def test_intermediate_refuses_private_fields_rows_raw_sqlite_and_duplicates(self):
        source = self.base / "input.json"
        for docs, chunks in [([self.doc("private", path="extra-docs/private.md")], []),
                             ([{**self.docs[0], "hash": "private"}], []),
                             ([self.docs[0]], [{**self.chunks[0], "ocr_text": "private"}]),
                             ([self.docs[0]], [{**self.chunks[0], "doc_id": "missing"}]),
                             ([self.docs[0]], [self.chunks[0], self.chunks[0]])]:
            with self.subTest(docs=docs, chunks=chunks):
                source.write_text(json.dumps({"docs": docs, "chunks": chunks}), encoding="utf-8")
                with self.assertRaises(ValueError):
                    export_pages(intermediate=source, output_dir=self.output, base=self.base)
        source.write_bytes(self.db.read_bytes())
        with self.assertRaisesRegex(ValueError, "Raw SQLite"):
            export_pages(intermediate=source, output_dir=self.output, base=self.base)
        self.assertFalse(self.output.exists())

    def test_refuses_malformed_or_private_paths_for_public_identifiers(self):
        for path in ("extra-docs/meituan-query.md", "articles/../meituan-query.md", "/articles/meituan-query.md", "articles/meituan-query.md/secret", "articles\\meituan-query.md"):
            with self.subTest(path=path):
                with closing(sqlite3.connect(self.db)) as conn, conn:
                    conn.execute("UPDATE docs SET path=? WHERE doc_id='meituan-query'", (path,))
                with self.assertRaisesRegex(ValueError, "Refused document"):
                    self.export()
        self.assertFalse(self.output.exists())

    def test_refuses_unsafe_nonpublic_path_and_orphan_chunks(self):
        with closing(sqlite3.connect(self.db)) as conn, conn:
            conn.execute("UPDATE docs SET path='extra-docs/../secret.md' WHERE doc_id='private-book'")
        with self.assertRaisesRegex(ValueError, "Refused document"):
            self.export()
        with closing(sqlite3.connect(self.db)) as conn, conn:
            conn.execute("UPDATE docs SET path='extra-docs/books/a-book.md' WHERE doc_id='private-book'")
            conn.execute("INSERT INTO chunks VALUES(123,'missing',0,'Orphan')")
        with self.assertRaisesRegex(ValueError, "Orphan"):
            self.export()

    def test_refuses_byte_fallback_and_wrong_production_counts(self):
        with self.assertRaisesRegex(ValueError, "Production counts required"):
            self.export(require_production_counts=True)
        self.assertFalse(self.output.exists())
        with closing(sqlite3.connect(self.db)) as conn, conn:
            conn.executescript("CREATE TABLE ingestion_metadata(key TEXT,value TEXT); INSERT INTO ingestion_metadata VALUES('token_budget','utf8-bytes-v1');")
        with self.assertRaisesRegex(ValueError, "utf8-bytes fallback"):
            self.export()

    def test_production_guard_verifies_document_identity_after_counts_match(self):
        with mock.patch.multiple("sgt_kb.indexing.export_pages", PRODUCTION_DOCS=3, PRODUCTION_CHUNKS=4):
            with self.assertRaisesRegex(ValueError, "identifiers do not match"):
                self.export(require_production_counts=True)
        self.assertFalse(self.output.exists())

    def test_output_guards_prevent_raw_copy_source_replacement_and_unowned_deletion(self):
        before = self.db.read_bytes()
        for output in (self.db, self.base, self.base / "copy.sqlite", self.base / "raw.json"):
            with self.subTest(output=output), self.assertRaises(ValueError):
                export_pages(db=self.db, output_dir=output, base=self.base)
        with self.assertRaisesRegex(ValueError, "separate .jsonl"):
            self.export(write_intermediate=self.db)
        owned = self.output / "search-chunks"
        owned.mkdir(parents=True)
        (owned / "keep.txt").write_text("Keep existing user files")
        with self.assertRaisesRegex(ValueError, "unowned"):
            self.export()
        self.assertTrue((owned / "keep.txt").exists())
        self.assertEqual(before, self.db.read_bytes())

    def test_intermediate_symlink_and_input_directory_destination_are_refused(self):
        incoming = self.base / "incoming"
        incoming.mkdir()
        source = incoming / "one.jsonl"
        source.write_text(json.dumps({**self.docs[0], **self.chunks[0]}) + "\n", encoding="utf-8")
        link = self.base / "linked.jsonl"
        link.symlink_to(source)
        for destination in (source, incoming / "two.jsonl", link):
            with self.subTest(destination=destination), self.assertRaises(ValueError):
                export_pages(intermediate=incoming, output_dir=self.output, base=self.base, write_intermediate=destination)
        self.assertEqual(1, len(list(incoming.iterdir())))
        self.assertFalse(self.output.exists())

    def test_intermediate_hardlink_cannot_truncate_production_database(self):
        before = self.db.read_bytes()
        alias = self.base / "hardlinked.jsonl"
        alias.hardlink_to(self.db)
        with self.assertRaisesRegex(ValueError, "alias a source"):
            self.export(write_intermediate=alias)
        self.assertEqual(before, self.db.read_bytes())
        self.assertFalse(self.output.exists())

    def test_missing_index_not_created_and_reexport_deterministic(self):
        missing = self.base / "missing.sqlite"
        with self.assertRaises(sqlite3.OperationalError):
            export_pages(db=missing, output_dir=self.output, base=self.base)
        self.assertFalse(missing.exists())
        self.export()
        before = {p.relative_to(self.output): p.read_bytes() for p in self.output.rglob("*") if p.is_file()}
        self.export()
        self.assertEqual(before, {p.relative_to(self.output): p.read_bytes() for p in self.output.rglob("*") if p.is_file()})

    def test_package_cli_explicit_pending_corpus(self):
        result = subprocess.run([sys.executable, "-m", "sgt_kb", "export-pages", "--pending", "--output-dir", str(self.output)], cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("pending-production-export", result.stdout)
        manifest = self.json("search-manifest.json")
        self.assertEqual((0, 0, 2421), (manifest["doc_count"], manifest["chunk_count"], manifest["public_article_files"]))
        self.assertLess(manifest["first_load_index"]["bytes"], 1000)


if __name__ == "__main__":
    unittest.main()
