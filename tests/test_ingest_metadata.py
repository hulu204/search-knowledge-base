import csv
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import ingest_url


class IngestMetadataTest(unittest.TestCase):
    def test_feed_title_and_date_override_generic_page_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            articles = base / "articles"
            articles.mkdir()
            manifest = base / "crawl_manifest.csv"
            with manifest.open("w", encoding="utf-8", newline="") as handle:
                csv.DictWriter(handle, fieldnames=ingest_url.FIELDS).writeheader()

            with (
                mock.patch.object(ingest_url, "OUT", articles),
                mock.patch.object(ingest_url, "MANIFEST", manifest),
                mock.patch.object(
                    ingest_url, "fetch",
                    return_value=({"title": "", "date": "", "account": "", "body": "正文" * 120}, None),
                ),
            ):
                result = ingest_url.ingest(
                    "https://lancedb.com/blog/agent-memory",
                    company="LanceDB", tag="问答/RAG", skip_images=True,
                    skip_index=True, title="Agent memory", date="2026-08-03",
                )

            article = Path(result["article_path"]).read_text(encoding="utf-8")
            with manifest.open(encoding="utf-8") as handle:
                row = list(csv.DictReader(handle))[0]
            self.assertIn("title: 'Agent memory'", article)
            self.assertEqual("Agent memory", row["title"])
            self.assertEqual("2026-08-03", row["date"])


if __name__ == "__main__":
    unittest.main()
