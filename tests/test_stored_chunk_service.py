"""Stored chunk provenance across hybrid retrieval, HTTP and MCP responses."""
import sqlite3
import unittest
from unittest import mock

import numpy as np

import kb_server
import workbench_api


class StoredChunkServiceTest(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.addCleanup(self.conn.close)
        self.conn.executescript(
            """
            CREATE TABLE docs (
                doc_id TEXT PRIMARY KEY, path TEXT, title TEXT, company TEXT,
                tag TEXT, date TEXT, url TEXT
            );
            CREATE TABLE chunks (
                chunk_id INTEGER PRIMARY KEY, doc_id TEXT, seq INTEGER, text TEXT
            );
            INSERT INTO docs VALUES (
                'deep-doc', 'articles/deep-doc.md', 'Unicode 查询理解 😀', '美团',
                '搜索', '2021-05-07', 'https://example.test/source?x=1&y=2'
            );
            """
        )
        self.intro = "文章开头，介绍业务背景。" * 100
        self.stored = (
            "## 深入正文\n\n查询理解 combines Query understanding 与 Unicode 😀。\n"
            "<script>alert('stored text')</script> & HTML stays literal.\n"
            + "后续正文保留原样，不截断。" * 200
        )
        self.conn.executemany(
            "INSERT INTO chunks VALUES (?, ?, ?, ?)",
            [(0, "deep-doc", 0, self.intro), (1, "deep-doc", 7, self.stored)],
        )
        model = mock.Mock()
        model.encode.return_value = {
            "dense_vecs": [[1.0, 0.0]],
            "lexical_weights": [{"0": 1.0}],
        }
        patches = [
            mock.patch.object(kb_server, "_load"),
            mock.patch.object(kb_server, "_conn", self.conn),
            mock.patch.object(kb_server, "_model", model),
            mock.patch.object(kb_server, "_dense", np.array([[0.0, 1.0], [1.0, 0.0]])),
            mock.patch.object(kb_server, "_sparse", np.array([[0.0], [1.0]])),
        ]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)

    def test_deep_hit_returns_exact_stored_text_and_source(self):
        results = kb_server.search_knowledge_base("查询理解 Query understanding", top_k=1)
        self.assertEqual(1, len(results))
        hit = results[0]
        self.assertEqual(self.stored, hit["text"])
        self.assertNotEqual(self.intro, hit["text"])
        self.assertEqual("deep-doc", hit["doc_id"])
        self.assertEqual(1, hit["chunk_id"])
        self.assertEqual(7, hit["seq"])
        self.assertEqual("articles/deep-doc.md", hit["path"])
        self.assertEqual("Unicode 查询理解 😀", hit["title"])
        self.assertEqual("https://example.test/source?x=1&y=2", hit["url"])

    def test_http_response_keeps_stored_chunk_and_citation(self):
        # Run the actual route without opening sockets or loading a model.
        handler = object.__new__(workbench_api.WorkbenchHandler)
        handler.path = "/api/search"
        with mock.patch.object(handler, "_body", return_value={"query": "查询理解"}):
            with mock.patch.object(handler, "_json") as respond:
                handler._post()
        response = respond.call_args.args[0]
        hit = response["results"][0]
        self.assertEqual("查询理解", response["query"])
        self.assertEqual(self.stored, hit["text"])
        self.assertEqual(("deep-doc", 1, 7), (hit["doc_id"], hit["chunk_id"], hit["seq"]))
        self.assertEqual("articles/deep-doc.md", hit["path"])

    def test_mcp_citation_identifies_stored_chunk(self):
        response = kb_server.kb_search("查询理解", top_k=1)
        self.assertIn("doc_id: deep-doc | chunk_id: 1 | seq: 7", response)
        self.assertIn("path: articles/deep-doc.md", response)
        self.assertIn("https://example.test/source?x=1&y=2", response)
        self.assertTrue(response.endswith(self.stored))

    def test_metadata_filter_with_no_match_returns_no_results(self):
        self.assertEqual([], kb_server.search_knowledge_base("查询理解", company="不存在"))


if __name__ == "__main__":
    unittest.main()
