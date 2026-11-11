"""Reproducible model-free ingestion and exact SQLite-to-Pages chunk export."""
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest import mock

import build_index
from export_pages import export_index


class PublicChunkExportTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.base = Path(self.directory.name)
        (self.base / "articles").mkdir()
        (self.base / "extra-docs").mkdir()
        self.body = (
            "# Background\n\n" + "无关的开头背景介绍。" * 160
            + "\n\n## 深入正文\n\n"
            + "查询理解 Query understanding 😀 <script>alert('x')</script> & 实体。" * 30
            + "\n\n## 后续内容\n\n" + "后续正文必须保持原样。" * 100
        )
        public = "---\ntitle: '公共文章'\nurl: 'https://example.test/?a=1&b=2'\ncompany: '美团'\ntag: '搜索'\n---\n" + self.body
        (self.base / "articles/public.md").write_text(public, encoding="utf-8")
        (self.base / "extra-docs/private.md").write_text(public, encoding="utf-8")
        for key, value in {"BASE": self.base, "ARTICLES": self.base / "articles", "EXTRA": self.base / "extra-docs", "FIGURES": self.base / "figures"}.items():
            patch = mock.patch.object(build_index, key, value)
            patch.start()
            self.addCleanup(patch.stop)
        self.db = self.base / "index/public-static/kb.sqlite"
        self.output = self.base / "demo-index.json"

    def test_export_is_exact_stored_chunks_not_article_lead(self):
        docs, chunks = build_index.build_lexical_index(self.db, public_only=True)
        self.assertEqual(1, docs)
        self.assertGreater(chunks, 2)
        data = export_index(self.db, self.output, base=self.base)
        with closing(sqlite3.connect(self.db)) as conn:
            stored = [dict(zip(("chunk_id", "doc_id", "seq", "text"), row)) for row in conn.execute("SELECT * FROM chunks ORDER BY chunk_id")]
        self.assertEqual(stored, data["chunks"])
        expected = build_index.chunk_text(build_index.clean_body(self.body), "utf8-bytes-v1")
        self.assertEqual(expected, [chunk["text"] for chunk in data["chunks"]])
        deep = next(chunk for chunk in stored if "查询理解" in chunk["text"])
        self.assertGreater(deep["seq"], 0)
        self.assertIn("<script>", deep["text"])
        self.assertIn("😀", deep["text"])
        self.assertEqual("offline-static-lexical", data["retrieval"])
        self.assertEqual("utf8-bytes-v1", data["ingestion"]["token_budget"])
        self.assertEqual("https://example.test/?a=1&b=2", data["docs"][0]["url"])
        before = self.output.read_bytes()
        build_index.build_lexical_index(self.db, public_only=True)
        export_index(self.db, self.output, base=self.base)
        self.assertEqual(before, self.output.read_bytes())
        self.assertEqual(data, json.loads(before))

    def test_public_only_never_loads_extra_docs(self):
        self.assertEqual(["public"], [doc["doc_id"] for doc in build_index.load_docs(public_only=True)])
        self.assertEqual(2, len(build_index.load_docs()))

    def test_export_rejects_non_public_index(self):
        build_index.build_lexical_index(self.db, public_only=False)
        with self.assertRaisesRegex(ValueError, "public-only"):
            export_index(self.db, self.output, base=self.base)
        self.assertFalse(self.output.exists())

    def test_export_rejects_private_rows_even_if_metadata_claims_public(self):
        build_index.build_lexical_index(self.db)
        with closing(sqlite3.connect(self.db)) as conn, conn:
            conn.execute("UPDATE docs SET path='extra-docs/private.md'")
        with self.assertRaisesRegex(ValueError, "outside the public"):
            export_index(self.db, self.output, base=self.base)

    def test_lexical_build_refuses_to_overwrite_hybrid_index(self):
        build_index.build_lexical_index(self.db)
        with closing(sqlite3.connect(self.db)) as conn, conn:
            conn.execute("DELETE FROM ingestion_metadata")
        with self.assertRaisesRegex(ValueError, "separate directory"):
            build_index.build_lexical_index(self.db)

    def test_missing_index_is_not_created_by_export(self):
        missing = self.base / "missing.sqlite"
        with self.assertRaises(sqlite3.OperationalError):
            export_index(missing, self.output, base=self.base)
        self.assertFalse(missing.exists())


if __name__ == "__main__":
    unittest.main()
