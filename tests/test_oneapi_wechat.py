import csv
import json
import os
import sqlite3
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

import oneapi_wechat


def write_targets(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "account", "company", "biz_info", "ghid", "seed_url",
            "candidate_biz", "candidate_verified_at",
        ])
        writer.writeheader()
        writer.writerows(rows)


def response_for(payload: dict, status: int = 200):
    body = json.dumps(payload).encode()
    response = mock.Mock(
        status_code=status,
        headers={},
        is_redirect=False,
        is_permanent_redirect=False,
    )
    response.raise_for_status.return_value = None
    response.iter_content.return_value = [body]
    return response


class OneApiWechatTest(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.base = Path(directory.name)
        patcher = mock.patch.object(
            oneapi_wechat, "INDEX_DIRTY_FILE", self.base / "oneapi_index_dirty",
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_api_key_requires_private_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "key"
            path.write_text("valid-secret-key")
            os.chmod(path, 0o644)
            with self.assertRaisesRegex(oneapi_wechat.OneApiKeyError, "0600"):
                oneapi_wechat.read_api_key(path)
            os.chmod(path, 0o600)
            self.assertEqual("valid-secret-key", oneapi_wechat.read_api_key(path))

    def test_load_targets_accepts_unique_valid_fixture_identities(self) -> None:
        # The public checkout does not include the machine-local target list.
        path = self.base / "targets.csv"
        rows = [
            {"account": " 测试号 ", "company": " 测试 ", "ghid": " gh_123456789abc "},
            {"account": "另一个测试号", "company": "示例", "ghid": "gh_0123456789ab"},
        ]
        write_targets(path, rows)

        targets = oneapi_wechat.load_targets(path)

        self.assertEqual([
            oneapi_wechat.Target("测试号", "测试", "gh_123456789abc"),
            oneapi_wechat.Target("另一个测试号", "示例", "gh_0123456789ab"),
        ], targets)

    def test_load_targets_rejects_duplicate_or_invalid_identities(self) -> None:
        path = self.base / "targets.csv"
        valid = {"account": "测试号", "company": "测试", "ghid": "gh_123456789abc"}
        cases = [
            ([valid, {**valid, "account": "另一个测试号"}], "重复"),
            ([valid, {**valid, "ghid": "gh_0123456789ab"}], "重复"),
            ([{**valid, "ghid": "invalid"}], "身份字段无效"),
            ([{**valid, "account": ""}], "身份字段无效"),
            ([{**valid, "company": ""}], "身份字段无效"),
            ([], "为空"),
        ]
        for rows, message in cases:
            with self.subTest(rows=rows):
                write_targets(path, rows)
                with self.assertRaisesRegex(oneapi_wechat.OneApiError, message):
                    oneapi_wechat.load_targets(path)

    def test_parse_page_normalizes_urls_and_detects_balance(self) -> None:
        payload = {
            "code": 200,
            "message": "success",
            "data": {
                "is_end": 0,
                "next_offset": "YWJjZA==",
                "articles": [{
                    "title": "向量检索实践",
                    "digest": "摘要",
                    "url": "http://mp.weixin.qq.com/s/abc?utm_source=x#fragment",
                    "create_time": 1700000000,
                }],
            },
        }
        page = oneapi_wechat.parse_page(payload)
        self.assertEqual("https://mp.weixin.qq.com/s/abc", page.articles[0].url)
        with self.assertRaises(oneapi_wechat.OneApiBalanceExhausted):
            oneapi_wechat.parse_page({
                "code": 301, "message": "Insufficient balance", "data": None,
            })

    def test_client_does_not_follow_redirect_and_closes_response(self) -> None:
        response = mock.Mock(
            status_code=302,
            headers={"Location": "http://127.0.0.1/private"},
            is_redirect=True,
            is_permanent_redirect=False,
        )
        session = mock.Mock()
        session.post.return_value = response
        client = oneapi_wechat.OneApiClient("secret-value", session=session)
        with mock.patch.object(oneapi_wechat, "validate_public_url"):
            with self.assertRaisesRegex(oneapi_wechat.OneApiError, "重定向"):
                client.fetch_page("gh_123456789abc")
        self.assertFalse(session.post.call_args.kwargs["allow_redirects"])
        response.close.assert_called_once()

    def test_client_streams_bounded_response_and_never_persists_key(self) -> None:
        payload = {
            "code": 200, "message": "success",
            "data": {"is_end": 1, "next_offset": "", "articles": []},
        }
        response = response_for(payload)
        session = mock.Mock()
        session.post.return_value = response
        client = oneapi_wechat.OneApiClient("secret-value", session=session)
        with mock.patch.object(oneapi_wechat, "validate_public_url"):
            page = client.fetch_page("gh_123456789abc")
        self.assertTrue(page.is_end)
        self.assertTrue(session.post.call_args.kwargs["stream"])
        self.assertNotIn("secret-value", json.dumps(payload))
        response.close.assert_called_once()

    def test_declared_response_limit_fails_before_reading_body(self) -> None:
        response = mock.Mock(headers={
            "Content-Length": str(oneapi_wechat.MAX_RESPONSE_BYTES + 1),
        })
        with self.assertRaisesRegex(oneapi_wechat.OneApiError, "大小限制"):
            oneapi_wechat._read_response_json(response, "secret")
        response.iter_content.assert_not_called()

    def test_checkpoint_filters_before_2020_and_commits_cursor(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "state.sqlite"
            connection = oneapi_wechat.connect_state(database)
            target = oneapi_wechat.Target("测试号", "测试", "gh_123456789abc")
            oneapi_wechat.sync_targets(connection, [target])
            page = oneapi_wechat.Page((
                oneapi_wechat.Article(
                    "https://mp.weixin.qq.com/s/new", "向量检索实践", "", 1700000000,
                ),
                oneapi_wechat.Article(
                    "https://mp.weixin.qq.com/s/old", "向量检索旧文", "", 1500000000,
                ),
            ), "next123", False)
            outcome = oneapi_wechat.checkpoint_page(connection, target, page)
            account = connection.execute(
                "SELECT offset, calls, done FROM accounts WHERE account='测试号'"
            ).fetchone()
            articles = connection.execute(
                "SELECT url, status FROM articles ORDER BY url"
            ).fetchall()
            connection.close()
        self.assertEqual(("next123", 1, 0), account)
        self.assertEqual(
            [("https://mp.weixin.qq.com/s/new", "pending")], articles,
        )
        self.assertEqual(1, outcome["stored"])

    def test_page_entirely_before_cutoff_marks_account_done(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            connection = oneapi_wechat.connect_state(Path(directory) / "state.sqlite")
            target = oneapi_wechat.Target("测试号", "测试", "gh_123456789abc")
            oneapi_wechat.sync_targets(connection, [target])
            page = oneapi_wechat.Page((oneapi_wechat.Article(
                "https://mp.weixin.qq.com/s/old", "旧文", "", 1500000000,
            ),), "next", False)
            outcome = oneapi_wechat.checkpoint_page(connection, target, page)
            done = connection.execute(
                "SELECT done FROM accounts WHERE account='测试号'"
            ).fetchone()[0]
            connection.close()
        self.assertTrue(outcome["done"])
        self.assertEqual(1, done)

    def test_balance_failure_does_not_advance_cursor(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            key = root / "key"
            key.write_text("valid-secret-key")
            os.chmod(key, 0o600)
            targets = root / "targets.csv"
            write_targets(targets, [{
                "account": "测试号", "company": "测试", "biz_info": "ABC==",
                "ghid": "gh_123456789abc", "seed_url": "",
                "candidate_biz": "", "candidate_verified_at": "",
            }])
            database = root / "state.sqlite"
            with mock.patch.object(
                oneapi_wechat.OneApiClient, "fetch_page",
                side_effect=oneapi_wechat.OneApiBalanceExhausted("empty"),
            ):
                result = oneapi_wechat.backfill(
                    5, 1.0, key_file=key, state_db=database,
                    targets_file=targets,
                )
            connection = sqlite3.connect(database)
            row = connection.execute(
                "SELECT offset, calls, last_error FROM accounts"
            ).fetchone()
            connection.close()
        self.assertTrue(result["balance_exhausted"])
        self.assertEqual(("", 0, "balance_exhausted"), row)

    def test_ingest_failure_retries_then_becomes_body_missing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "state.sqlite"
            connection = oneapi_wechat.connect_state(database)
            connection.execute("""
                INSERT INTO articles(
                    url, account, company, title, digest, create_time,
                    status, discovered_at
                ) VALUES (?, ?, ?, ?, '', ?, 'pending', ?)
            """, (
                "https://mp.weixin.qq.com/s/test", "测试号", "测试",
                "向量检索实践", 1700000000, datetime.now().isoformat(),
            ))
            connection.commit()
            connection.close()
            with mock.patch.object(oneapi_wechat, "ingest", side_effect=RuntimeError("captcha")):
                first = oneapi_wechat.ingest_pending(1, database, defer_index=True)
            connection = sqlite3.connect(database)
            connection.execute(
                "UPDATE articles SET next_attempt_at='' WHERE url=?",
                ("https://mp.weixin.qq.com/s/test",),
            )
            connection.commit()
            connection.close()
            with mock.patch.object(oneapi_wechat, "ingest", side_effect=RuntimeError("captcha")):
                oneapi_wechat.ingest_pending(1, database, defer_index=True)
            connection = sqlite3.connect(database)
            connection.execute(
                "UPDATE articles SET next_attempt_at='' WHERE url=?",
                ("https://mp.weixin.qq.com/s/test",),
            )
            connection.commit()
            connection.close()
            with mock.patch.object(oneapi_wechat, "ingest", side_effect=RuntimeError("captcha")):
                last = oneapi_wechat.ingest_pending(1, database, defer_index=True)
            connection = sqlite3.connect(database)
            row = connection.execute(
                "SELECT status, attempts, error FROM articles"
            ).fetchone()
            connection.close()
        self.assertEqual(1, first["failed"])
        self.assertEqual(1, last["body_missing"])
        self.assertEqual(("body_missing", 3, "RuntimeError"), row)


if __name__ == "__main__":
    unittest.main()
