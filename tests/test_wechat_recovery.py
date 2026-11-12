import argparse
import json
import os
import io
import tempfile
import sys
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

from sgt_kb.collection import wechat_catchup
from sgt_kb.collection import wechat_auth_update
from sgt_kb.collection import wechat_mp
from sgt_kb.collection import ingest_url


class WechatRecoveryTest(unittest.TestCase):
    def test_extract_auth_from_copy_as_curl(self) -> None:
        value = wechat_auth_update.extract_auth(
            "curl 'https://mp.weixin.qq.com/cgi-bin/appmsg?token=123456&lang=zh_CN' "
            "-H 'Cookie: session=fake; other=value'"
        )
        self.assertEqual("123456", value["token"])
        self.assertEqual("session=fake; other=value", value["cookie"])

    def test_auth_is_saved_atomically_with_private_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / ".wechat_mp_auth.json"
            wechat_auth_update.save_auth(
                {"cookie": "session=fake", "token": "123456"}, path
            )
            stored = json.loads(path.read_text())
            mode = os.stat(path).st_mode & 0o777

        self.assertEqual("123456", stored["token"])
        self.assertEqual(0o600, mode)

    def test_failed_replace_preserves_old_auth_and_cleans_temp(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / ".wechat_mp_auth.json"
            path.write_text('{"cookie":"old","token":"old"}\n')
            with mock.patch.object(
                wechat_auth_update.os, "replace", side_effect=OSError("replace failed")
            ):
                with self.assertRaises(OSError):
                    wechat_auth_update.save_auth(
                        {"cookie": "new", "token": "new"}, path
                    )

            self.assertIn('"old"', path.read_text())
            self.assertEqual([path], list(Path(temp_dir).iterdir()))

    def test_http_error_never_exposes_token_or_cookie(self) -> None:
        import requests

        response = requests.Response()
        response.status_code = 500
        response.url = "https://mp.weixin.qq.com/cgi-bin/appmsg?token=SECRET_TOKEN"
        session = mock.Mock()
        session.get.return_value = response
        with self.assertRaisesRegex(wechat_mp.WechatApiError, "status=500") as error:
            wechat_mp.api_get(
                session,
                {"cookie": "SECRET_COOKIE", "token": "SECRET_TOKEN"},
                "https://mp.weixin.qq.com/cgi-bin/appmsg",
                {"action": "list_ex"},
            )

        rendered = str(error.exception)
        self.assertNotIn("SECRET_TOKEN", rendered)
        self.assertNotIn("SECRET_COOKIE", rendered)

    def test_refresh_main_redacts_unexpected_api_error(self) -> None:
        output = io.StringIO()
        with (
            mock.patch.object(
                wechat_auth_update.sys, "stdin",
                io.StringIO(
                    "curl 'https://mp.weixin.qq.com/x?token=SECRET_TOKEN' "
                    "-H 'Cookie: SECRET_COOKIE'"
                ),
            ),
            mock.patch.object(
                wechat_auth_update, "verify_auth",
                side_effect=wechat_mp.WechatApiError(
                    "failed https://example/?token=SECRET_TOKEN"
                ),
            ),
            redirect_stdout(output),
        ):
            code = wechat_auth_update.main()

        self.assertEqual(1, code)
        self.assertNotIn("SECRET_TOKEN", output.getvalue())
        self.assertNotIn("SECRET_COOKIE", output.getvalue())

    def test_auth_expiry_has_distinct_exit_code(self) -> None:
        import sys

        with (
            mock.patch.object(
                wechat_mp, "cmd_backfill",
                side_effect=wechat_mp.AuthExpired("expired"),
            ),
            mock.patch.object(
                sys, "argv", ["sgt-kb wechat-mp", "backfill", "--max-pages", "1"]
            ),
        ):
            code = wechat_mp.main()

        self.assertEqual(wechat_mp.AUTH_EXPIRED_EXIT, code)

    def test_auth_expiry_notification_is_debounced_within_two_hours(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            auth_file = base / ".auth.json"
            notice_file = base / "notice.json"
            auth_file.write_text("{}")
            with (
                mock.patch.object(wechat_catchup, "AUTH_FILE", auth_file),
                mock.patch.object(wechat_catchup, "AUTH_NOTICE_FILE", notice_file),
                mock.patch.object(wechat_catchup.time, "time", return_value=1_000_000),
                mock.patch.object(wechat_catchup.subprocess, "run") as notify,
            ):
                wechat_catchup.notify_auth_expired()
                os.utime(auth_file, None)
                wechat_catchup.notify_auth_expired()

            self.assertEqual(2, notify.call_count)
            notify.assert_any_call(
                ["open", "https://mp.weixin.qq.com/"],
                check=False,
                stdout=wechat_catchup.subprocess.DEVNULL,
                stderr=wechat_catchup.subprocess.DEVNULL,
            )

    def test_same_expired_auth_notifies_again_after_two_hours(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            auth_file = base / ".auth.json"
            notice_file = base / "notice.json"
            auth_file.write_text('{"token":"same"}')
            with (
                mock.patch.object(wechat_catchup, "AUTH_FILE", auth_file),
                mock.patch.object(wechat_catchup, "AUTH_NOTICE_FILE", notice_file),
                mock.patch.object(
                    wechat_catchup.time, "time",
                    side_effect=[1_000_000, 1_000_000 + 2 * 60 * 60],
                ),
                mock.patch.object(wechat_catchup.subprocess, "run") as notify,
            ):
                wechat_catchup.notify_auth_expired()
                wechat_catchup.notify_auth_expired()

            self.assertEqual(4, notify.call_count)

    def test_changed_auth_content_can_notify_again(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            auth_file = base / ".auth.json"
            notice_file = base / "notice.json"
            auth_file.write_text('{"token":"first"}')
            with (
                mock.patch.object(wechat_catchup, "AUTH_FILE", auth_file),
                mock.patch.object(wechat_catchup, "AUTH_NOTICE_FILE", notice_file),
                mock.patch.object(
                    wechat_catchup.time, "time",
                    side_effect=[1_000_000, 1_000_001],
                ),
                mock.patch.object(wechat_catchup.subprocess, "run") as notify,
            ):
                wechat_catchup.notify_auth_expired()
                auth_file.write_text('{"token":"second"}')
                wechat_catchup.notify_auth_expired()

            self.assertEqual(4, notify.call_count)

    def test_title_filter_avoids_substring_and_domain_false_positives(self) -> None:
        false_titles = [
            "Storage Agent Family: Agent 时代重构云存储",
            "视频生成：基于全局时间索引的 3D 位置编码优化",
            "当理解成为瓶颈：AI 编程时代的意图债",
            "相关性不等于因果性：因果推断实践",
            "前端如何实现业务解耦：酒店查询首页升级",
        ]
        true_titles = [
            "RAG 复合检索 Agent 的系统设计实践",
            "火山引擎 MySQL 向量索引实践",
            "搜索排序相关性优化实践",
        ]
        self.assertTrue(all(not wechat_mp.title_matches(title) for title in false_titles))
        self.assertTrue(all(wechat_mp.title_matches(title) for title in true_titles))

    def test_rate_limit_state_has_bounded_cooldown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = Path(temp_dir) / "state.json"
            state = {}
            with mock.patch.object(wechat_mp, "STATE_FILE", state_file):
                wechat_mp.record_rate_limit(
                    state, command="backfill", account="字节跳动技术团队",
                    query="检索", begin=9,
                )

            stored = json.loads(state_file.read_text())
            remaining = wechat_mp.rate_limit_remaining(stored)
            self.assertGreater(remaining, 60 * 60)
            self.assertLessEqual(remaining, 2 * 60 * 60)

    def test_backfill_skips_network_during_cooldown(self) -> None:
        state = {
            "rate_limit": {
                "retry_after": (
                    datetime.now(wechat_mp.SHANGHAI) + timedelta(hours=1)
                ).isoformat(timespec="seconds")
            }
        }
        args = argparse.Namespace(account=None, max_pages=2, tag_default="待分类")
        with (
            mock.patch.object(wechat_mp, "load_auth", return_value={"cookie": "x", "token": "y"}),
            mock.patch.object(wechat_mp, "load_state", return_value=state),
            mock.patch.object(wechat_mp, "make_session") as make_session,
        ):
            code = wechat_mp.cmd_backfill(args)

        self.assertEqual(wechat_mp.RATE_LIMIT_EXIT, code)
        make_session.assert_not_called()

    def test_catchup_crawls_and_indexes_only_when_manifest_grows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            state_file = base / "state.json"
            manifest = base / "manifest.csv"
            lock = base / "daily.lock"
            state_file.write_text(json.dumps({
                "accounts": {"测试号": {"queries": {"搜索": {"done": False}}}}
            }))
            manifest.write_text("header\n")
            calls = []

            def run(args, timeout):
                calls.append((args, timeout))
                if "backfill" in args:
                    manifest.write_text("header\nnew-row\n")
                return 0

            with (
                mock.patch.object(wechat_catchup, "STATE_FILE", state_file),
                mock.patch.object(wechat_catchup, "MANIFEST", manifest),
                mock.patch.object(wechat_catchup, "LOCK_FILE", lock),
                mock.patch.object(wechat_catchup, "run_command", side_effect=run),
            ):
                code = wechat_catchup.main()

        self.assertEqual(0, code)
        self.assertIn("--max-pages", calls[0][0])
        self.assertEqual("2", calls[0][0][-1])
        self.assertTrue(any("crawl" in call[0] for call in calls))
        self.assertTrue(any("build-index" in call[0] for call in calls))
        self.assertTrue(all(call[0][:3] == [sys.executable, "-m", "sgt_kb"] for call in calls))

    def test_poll_continues_after_single_article_failure(self) -> None:
        state = {
            "accounts": {
                "测试号": {"fakeid": "fake", "company": "测试", "mode": "filter"}
            }
        }
        data = {
            "app_msg_list": [
                {"title": "RAG 第一篇", "link": "https://mp.weixin.qq.com/s/first"},
                {"title": "向量检索第二篇", "link": "https://mp.weixin.qq.com/s/second"},
            ]
        }
        args = argparse.Namespace(tag_default="待分类")
        success = {"status": "ingested", "title": "向量检索第二篇"}
        with (
            mock.patch.object(wechat_mp, "load_auth", return_value={"cookie": "x", "token": "y"}),
            mock.patch.object(wechat_mp, "load_state", return_value=state),
            mock.patch.object(wechat_mp, "make_session", return_value=mock.Mock()),
            mock.patch.object(wechat_mp, "load_targets", return_value=[{
                "name": "测试号", "company": "测试", "mode": "filter",
            }]),
            mock.patch.object(wechat_mp, "api_get", return_value=data),
            mock.patch.object(wechat_mp, "clear_rate_limit"),
            mock.patch.object(wechat_mp.time, "sleep"),
            mock.patch.object(
                ingest_url, "ingest",
                side_effect=[RuntimeError("first failed"), success],
            ) as ingest,
            mock.patch("subprocess.run") as build,
        ):
            code = wechat_mp.cmd_poll(args)

        self.assertEqual(0, code)
        self.assertEqual(2, ingest.call_count)
        build.assert_called_once()

    def test_catchup_does_not_crawl_when_manifest_does_not_grow(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            state_file = base / "state.json"
            manifest = base / "manifest.csv"
            lock = base / "daily.lock"
            state_file.write_text(json.dumps({
                "accounts": {"测试号": {"queries": {"搜索": {"done": False}}}}
            }))
            manifest.write_text("header\n")
            with (
                mock.patch.object(wechat_catchup, "STATE_FILE", state_file),
                mock.patch.object(wechat_catchup, "MANIFEST", manifest),
                mock.patch.object(wechat_catchup, "LOCK_FILE", lock),
                mock.patch.object(wechat_catchup, "run_command", return_value=0) as run,
            ):
                code = wechat_catchup.main()

        self.assertEqual(0, code)
        self.assertEqual(1, run.call_count)

    def test_catchup_propagates_temporary_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            state_file = base / "state.json"
            manifest = base / "manifest.csv"
            lock = base / "daily.lock"
            state_file.write_text(json.dumps({
                "accounts": {"测试号": {"queries": {"搜索": {"done": False}}}}
            }))
            manifest.write_text("header\n")
            with (
                mock.patch.object(wechat_catchup, "STATE_FILE", state_file),
                mock.patch.object(wechat_catchup, "MANIFEST", manifest),
                mock.patch.object(wechat_catchup, "LOCK_FILE", lock),
                mock.patch.object(wechat_catchup, "run_command", return_value=75),
            ):
                code = wechat_catchup.main()

        self.assertEqual(75, code)


if __name__ == "__main__":
    unittest.main()
