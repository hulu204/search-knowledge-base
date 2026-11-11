import hashlib
import importlib.util
import base64
import os
import struct
import sys
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE))

from build_index import enrich_figures
from crawl import extract_publish_date
from ingestion_queue import enqueue, get_job, run_once
from ingest_url import normalize_url
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def load_webhook():
    spec = importlib.util.spec_from_file_location(
        "wechat_webhook", BASE / "wechat_webhook.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MultimodalIndexTest(unittest.TestCase):
    def test_figure_replaces_image_with_searchable_text(self):
        body = "# 干预系统\n\n![x](../images/doc/figure-001.png)"
        figures = [{
            "figure_id": "doc-fig-001",
            "image_path": "images/doc/figure-001.png",
            "source_url": "https://example.test/a.png",
            "section": "干预系统",
            "description": "Query 直接改写与 DOCID 强制过滤",
            "ocr_text": "黑名单过滤",
            "relations": [{
                "source": "通用干预规则",
                "relation": "包含",
                "target": "Query直接改写",
            }],
            "status": "ready",
        }]
        text = enrich_figures(body, figures)
        self.assertIn("doc-fig-001", text)
        self.assertIn("Query 直接改写", text)
        self.assertIn("黑名单过滤", text)
        self.assertNotIn("![", text)


class IngestionTest(unittest.TestCase):
    def test_wechat_url_normalization(self):
        self.assertEqual(
            normalize_url(
                "http://mp.weixin.qq.com/s/abc?utm_source=test#fragment"
            ),
            "https://mp.weixin.qq.com/s/abc",
        )
        self.assertEqual(
            normalize_url(
                "http://mp.weixin.qq.com/s?__biz=biz&mid=1&idx=2"
                "&sn=abc&scene=27#wechat_redirect"
            ),
            "https://mp.weixin.qq.com/s?__biz=biz&mid=1&idx=2&sn=abc",
        )

    def test_publish_time_extraction(self):
        self.assertEqual(
            extract_publish_date("<script>var ct = '1767225600';</script>"),
            "2026-01-01",
        )

    def test_queue_is_idempotent_and_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "jobs.sqlite"
            first = enqueue(
                "https://mp.weixin.qq.com/s/example",
                "test",
                "msg-1",
                db,
            )
            second = enqueue(
                "https://mp.weixin.qq.com/s/example",
                "test",
                "msg-1",
                db,
            )
            self.assertTrue(first["created"])
            self.assertFalse(second["created"])
            self.assertEqual(first["job_id"], second["job_id"])

            result = run_once(
                db,
                ingest_func=lambda url, origin: {
                    "status": "existing_url",
                    "url": url,
                    "origin": origin,
                },
            )
            self.assertEqual(result["status"], "succeeded")
            self.assertEqual(get_job(first["job_id"], db)["attempts"], 1)


class WeChatWebhookTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.webhook = load_webhook()

    def test_signature(self):
        expected = hashlib.sha1(
            "".join(sorted(["token", "1700000000", "nonce"])).encode()
        ).hexdigest()
        self.assertEqual(
            self.webhook.signature("token", "1700000000", "nonce"), expected
        )

    def test_link_and_text_messages(self):
        link = self.webhook.parse_xml(
            b"<xml><MsgType>link</MsgType><Url>"
            b"https://mp.weixin.qq.com/s/abc</Url><MsgId>1</MsgId></xml>"
        )
        self.assertEqual(
            self.webhook.extract_urls(link),
            ["https://mp.weixin.qq.com/s/abc"],
        )
        text = {
            "MsgType": "text",
            "Content": (
                "看看 https://mp.weixin.qq.com/s/one "
                "忽略 https://example.com/no"
            ),
        }
        self.assertEqual(
            self.webhook.extract_urls(text),
            ["https://mp.weixin.qq.com/s/one"],
        )

    def test_rejects_unsafe_xml(self):
        with self.assertRaises(ValueError):
            self.webhook.parse_xml(
                b'<!DOCTYPE x [<!ENTITY y SYSTEM "file:///etc/passwd">]>'
                b"<xml><Content>&y;</Content></xml>"
            )

    def test_safe_mode_decryption(self):
        key = bytes(range(32))
        encoding_key = base64.b64encode(key).decode().rstrip("=")
        message = b"<xml><MsgType>text</MsgType></xml>"
        plain = (
            os.urandom(16)
            + struct.pack("!I", len(message))
            + message
            + b"wx-app-id"
        )
        padding = 32 - len(plain) % 32
        plain += bytes([padding]) * padding
        encryptor = Cipher(
            algorithms.AES(key), modes.CBC(key[:16])
        ).encryptor()
        ciphertext = base64.b64encode(
            encryptor.update(plain) + encryptor.finalize()
        ).decode()
        self.assertEqual(
            self.webhook.decrypt_wechat(
                ciphertext, encoding_key, "wx-app-id"
            ),
            message,
        )


if __name__ == "__main__":
    unittest.main()
