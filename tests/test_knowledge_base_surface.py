import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from sgt_kb.service import workbench_api


class KnowledgeBaseSurfaceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base = Path(self.temp_dir.name).resolve()
        self.db = self.base / "index" / "kb.sqlite"
        self.db.parent.mkdir()
        article = self.base / "articles" / "demo.md"
        article.parent.mkdir()
        article.write_text("# Demo\n\nKnowledge base content.", encoding="utf-8")

        with sqlite3.connect(self.db) as conn:
            conn.executescript(
                """
                CREATE TABLE docs (
                    doc_id TEXT PRIMARY KEY,
                    path TEXT,
                    title TEXT,
                    company TEXT,
                    tag TEXT,
                    date TEXT,
                    url TEXT
                );
                CREATE TABLE chunks (chunk_id INTEGER PRIMARY KEY, doc_id TEXT, text TEXT);
                CREATE TABLE figures (figure_id TEXT PRIMARY KEY, doc_id TEXT);
                """
            )
            conn.execute(
                "INSERT INTO docs VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    "demo",
                    "articles/demo.md",
                    "Demo article",
                    "Example",
                    "搜索",
                    "2026-08-02",
                    "https://example.com/demo",
                ),
            )
            conn.execute("INSERT INTO chunks VALUES (1, 'demo', 'chunk')")
            conn.execute("INSERT INTO figures VALUES ('figure-1', 'demo')")

        self.patches = (
            mock.patch.object(workbench_api, "BASE", self.base),
            mock.patch.object(workbench_api, "DB", self.db),
        )
        for patcher in self.patches:
            patcher.start()

    def tearDown(self) -> None:
        for patcher in reversed(self.patches):
            patcher.stop()
        self.temp_dir.cleanup()

    def test_stats_returns_knowledge_base_facets(self) -> None:
        stats = workbench_api._stats()

        self.assertEqual(1, stats["docs"])
        self.assertEqual(1, stats["chunks"])
        self.assertEqual(1, stats["figures"])
        self.assertEqual([{"name": "Example", "count": 1}], stats["companies"])
        self.assertEqual([{"name": "搜索", "count": 1}], stats["tags"])

    def test_document_response_is_traceable(self) -> None:
        document = workbench_api._get_doc("demo")

        self.assertEqual("Demo article", document["title"])
        self.assertEqual("https://example.com/demo", document["url"])
        self.assertIn("Knowledge base content", document["markdown"])

    def test_mentoring_routes_are_removed(self) -> None:
        source = Path(workbench_api.__file__).read_text(encoding="utf-8")
        for route in (
            "/api/learning-path",
            "/api/delivery-guide",
            "/api/report-review",
            "/api/review-guide",
            "/api/progress",
            "/api/domain-map",
            "/api/profile",
        ):
            self.assertNotIn(route, source)


if __name__ == "__main__":
    unittest.main()
