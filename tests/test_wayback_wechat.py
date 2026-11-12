import unittest
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

from sgt_kb.collection import wayback_wechat
from sgt_kb.collection.crawl import extract_publish_date


class WaybackWechatTest(unittest.TestCase):
    def test_wechat_ct_has_priority_over_unrelated_create_time(self) -> None:
        source = (
            'window.noise={"create_time":"1430000000"};'
            'var ct = "1594295940";'
        )
        self.assertEqual("2020-07-09", extract_publish_date(source))

    def test_normalization_removes_all_session_parameters(self) -> None:
        url = (
            "https://mp.weixin.qq.com/s?__biz=ABC%3D%3D&amp;amp;mid=123&amp;idx=1"
            "&amp;sn=stable&amp;key=SECRET&amp;pass_ticket=SECRET2&amp;uin=SECRET3"
        )
        normalized = wayback_wechat.normalize_archived_url(url)
        self.assertIn("__biz=ABC%3D%3D", normalized)
        self.assertIn("mid=123", normalized)
        self.assertNotIn("key=", normalized)
        self.assertNotIn("pass_ticket", normalized)
        self.assertNotIn("uin", normalized)

    def test_deep_html_escaping_is_fully_decoded(self) -> None:
        value = "https://mp.weixin.qq.com/s?__biz=ABC%3D%3D&mid=123&idx=1&sn=x"
        for _ in range(8):
            value = value.replace("&", "&amp;")
        normalized = wayback_wechat.normalize_archived_url(value)
        self.assertIn("mid=123", normalized)

    def test_cdx_resume_key_is_parsed(self) -> None:
        rows = [
            ["timestamp", "original"],
            ["20200101000000", "https://mp.weixin.qq.com/s?__biz=ABC%3D%3D&mid=1&idx=1&sn=x"],
            [],
            ["resume-key"],
        ]
        captures, resume = wayback_wechat.parse_cdx_page(rows)
        self.assertEqual("resume-key", resume)
        self.assertEqual(1, len(captures))

    def test_discovery_never_persists_raw_sensitive_url(self) -> None:
        response = mock.Mock()
        response.status_code = 200
        response.headers = {}
        response.iter_content.return_value = [json.dumps([
            ["timestamp", "original"],
            [
                "20200101000000",
                "https://mp.weixin.qq.com/s?__biz=ABC%3D%3D&mid=1&idx=1&sn=x&key=SECRET",
            ],
        ]).encode()]
        response.raise_for_status.return_value = None
        session = mock.Mock()
        with mock.patch.object(wayback_wechat, "safe_get", return_value=response):
            captures = wayback_wechat.discover_biz("ABC==", session=session)
        self.assertEqual(1, len(captures))
        self.assertNotIn("SECRET", captures[0].url)
        self.assertNotIn("SECRET", captures[0].archive_url)
        response.close.assert_called_once()

    def test_duplicate_resume_key_fails_explicitly(self) -> None:
        response = mock.Mock(status_code=200, headers={})
        response.iter_content.return_value = [json.dumps([
            ["timestamp", "original"], [], ["same-key"],
        ]).encode()]
        response.raise_for_status.return_value = None
        session = mock.Mock()
        with mock.patch.object(wayback_wechat, "safe_get", return_value=response):
            with self.assertRaisesRegex(wayback_wechat.WaybackCdxError, "repeated"):
                wayback_wechat.discover_biz("ABC==", session=session)

    def test_resume_key_fetches_second_page_and_terminates(self) -> None:
        first = mock.Mock(status_code=200)
        first.headers = {}
        first.iter_content.return_value = [json.dumps([
            ["timestamp", "original"],
            ["20200101000000", "https://mp.weixin.qq.com/s?__biz=ABC%3D%3D&mid=1&idx=1&sn=x"],
            [], ["next-key"],
        ]).encode()]
        first.raise_for_status.return_value = None
        second = mock.Mock(status_code=200)
        second.headers = {}
        second.iter_content.return_value = [json.dumps([
            ["timestamp", "original"],
            ["20210101000000", "https://mp.weixin.qq.com/s?__biz=ABC%3D%3D&mid=2&idx=1&sn=y"],
        ]).encode()]
        second.raise_for_status.return_value = None
        session = mock.Mock()
        with (
            mock.patch.object(
                wayback_wechat, "safe_get", side_effect=[first, second],
            ) as safe_get,
            mock.patch.object(wayback_wechat.time, "sleep"),
        ):
            captures = wayback_wechat.discover_biz("ABC==", session=session)
        self.assertEqual(2, len(captures))
        self.assertIn("resumeKey=next-key", safe_get.call_args_list[1].args[0])
        first.close.assert_called_once()
        second.close.assert_called_once()

    def test_cdx_rate_limit_is_retried_and_responses_are_closed(self) -> None:
        limited = mock.Mock(status_code=503, headers={"Retry-After": "0"})
        success = mock.Mock(status_code=200, headers={})
        success.raise_for_status.return_value = None
        success.iter_content.return_value = [
            json.dumps([["timestamp", "original"]]).encode(),
        ]
        with (
            mock.patch.object(
                wayback_wechat, "safe_get", side_effect=[limited, success],
            ) as safe_get,
            mock.patch.object(wayback_wechat.time, "sleep"),
        ):
            captures = wayback_wechat.discover_biz("ABC==", session=mock.Mock())
        self.assertEqual([], captures)
        self.assertEqual(2, safe_get.call_count)
        self.assertTrue(safe_get.call_args.kwargs["stream"])
        self.assertEqual({"web.archive.org"}, safe_get.call_args.kwargs["allowed_hosts"])
        limited.close.assert_called_once()
        success.close.assert_called_once()

    def test_cdx_private_redirect_is_rejected_before_second_request(self) -> None:
        redirect = mock.Mock(
            status_code=302,
            headers={"Location": "/private-hop"},
            is_redirect=True,
            is_permanent_redirect=False,
        )
        session = mock.Mock()
        session.get.return_value = redirect
        addresses = [
            [(2, 1, 6, "", ("8.8.8.8", 443))],
            [(2, 1, 6, "", ("127.0.0.1", 443))],
        ]
        with mock.patch("sgt_kb.collection.crawl.socket.getaddrinfo", side_effect=addresses):
            with self.assertRaisesRegex(
                wayback_wechat.WaybackCdxError, "safety policy",
            ):
                wayback_wechat.discover_biz("ABC==", session=session)
        self.assertEqual(1, session.get.call_count)
        redirect.close.assert_called_once()

    def test_cdx_content_length_limit_fails_closed_and_closes(self) -> None:
        response = mock.Mock(
            status_code=200,
            headers={"Content-Length": str(wayback_wechat.MAX_CDX_BYTES + 1)},
        )
        response.raise_for_status.return_value = None
        with mock.patch.object(wayback_wechat, "safe_get", return_value=response):
            with self.assertRaisesRegex(wayback_wechat.WaybackCdxError, "size limit"):
                wayback_wechat.discover_biz("ABC==", session=mock.Mock())
        response.iter_content.assert_not_called()
        response.close.assert_called_once()

    def test_cdx_streamed_body_limit_without_length_fails_closed_and_closes(self) -> None:
        response = mock.Mock(status_code=200, headers={})
        response.raise_for_status.return_value = None
        response.iter_content.return_value = [
            b"x" * wayback_wechat.MAX_CDX_BYTES,
            b"x",
        ]
        with mock.patch.object(wayback_wechat, "safe_get", return_value=response):
            with self.assertRaisesRegex(wayback_wechat.WaybackCdxError, "size limit"):
                wayback_wechat.discover_biz("ABC==", session=mock.Mock())
        response.close.assert_called_once()

    def test_backfill_attempt_budget_limits_irrelevant_candidates(self) -> None:
        rows = [
            {
                "account": "测试", "company": "测试", "biz_info": "ABC==",
                "url": f"https://mp.weixin.qq.com/s?__biz=ABC%3D%3D&mid={i}&idx=1&sn=x",
                "timestamps": "20200101000000", "captures_json": "", "status": "pending",
                "error": "", "attempt_cursor": "0", "failure_rounds": "0",
                "last_attempt_at": "", "next_attempt_at": "",
            }
            for i in range(10)
        ]
        with (
            mock.patch.object(wayback_wechat, "load_candidates", return_value=rows),
            mock.patch.object(wayback_wechat, "save_candidates"),
            mock.patch.object(
                wayback_wechat, "fetch_capture",
                return_value={"title": "生活随笔", "body": "正文" * 200, "date": "2020-01-01"},
            ) as fetch,
        ):
            result = wayback_wechat._backfill_locked(max_attempts=3)
        self.assertEqual(3, result["attempted"])
        self.assertEqual(3, fetch.call_count)

    def test_discovery_checkpoints_success_before_next_account_failure(self) -> None:
        targets = [
            {"account": "成功号", "company": "成功", "biz_info": "GOOD=="},
            {"account": "失败号", "company": "失败", "biz_info": "BAD=="},
        ]
        capture = wayback_wechat.Capture(
            timestamp="20200101000000",
            url="https://mp.weixin.qq.com/s?__biz=GOOD%3D%3D&mid=1&idx=1&sn=x",
            archive_url="https://mp.weixin.qq.com/s?__biz=GOOD%3D%3D&mid=1&idx=1&sn=x",
        )
        with (
            mock.patch.object(wayback_wechat, "load_targets", return_value=targets),
            mock.patch.object(wayback_wechat, "load_candidates", return_value=[]),
            mock.patch.object(wayback_wechat, "existing_urls", return_value=set()),
            mock.patch.object(wayback_wechat, "load_discovery_state", return_value={"accounts": {}}),
            mock.patch.object(
                wayback_wechat, "discover_biz",
                side_effect=[[capture], wayback_wechat.WaybackCdxError("limited")],
            ),
            mock.patch.object(wayback_wechat, "save_candidates") as save_candidates,
            mock.patch.object(wayback_wechat, "save_discovery_state"),
        ):
            result = wayback_wechat._discover_locked()

        self.assertEqual(1, result["accounts_ok"])
        self.assertEqual(1, result["accounts_failed"])
        self.assertGreaterEqual(save_candidates.call_count, 2)
        first_checkpoint = save_candidates.call_args_list[0].args[0]
        self.assertEqual("成功号", first_checkpoint[0]["account"])

    def test_discovery_resolves_seed_identity_and_persists_biz(self) -> None:
        targets = [{
            "account": "测试技术", "company": "测试", "biz_info": "",
            "seed_url": "https://mp.weixin.qq.com/s/example",
        }]
        identity = mock.Mock(biz_info="ABCDEF1234==")
        with (
            mock.patch.object(wayback_wechat, "load_targets", return_value=targets),
            mock.patch.object(wayback_wechat, "load_candidates", return_value=[]),
            mock.patch.object(wayback_wechat, "existing_urls", return_value=set()),
            mock.patch.object(wayback_wechat, "load_discovery_state", return_value={"accounts": {}}),
            mock.patch.object(
                wayback_wechat, "resolve_article_identity", return_value=identity,
            ) as resolve,
            mock.patch.object(wayback_wechat, "save_targets") as save_targets,
            mock.patch.object(wayback_wechat, "discover_biz", return_value=[]),
            mock.patch.object(wayback_wechat, "save_candidates"),
            mock.patch.object(wayback_wechat, "save_discovery_state"),
        ):
            result = wayback_wechat._discover_locked()
        self.assertEqual(1, result["identities_resolved"])
        self.assertEqual("ABCDEF1234==", targets[0]["biz_info"])
        resolve.assert_called_once_with(
            targets[0]["seed_url"], expected_account="测试技术", session=mock.ANY,
        )
        save_targets.assert_called_once_with(targets)

    def test_verified_registry_identity_remains_pending_until_approved(self) -> None:
        targets = [{
            "account": "测试技术", "company": "测试", "biz_info": "",
            "seed_url": "",
        }]
        capture = wayback_wechat.Capture(
            timestamp="20200101000000",
            url="https://mp.weixin.qq.com/s?__biz=ABCDEF1234%3D%3D&mid=1&idx=1&sn=x",
            archive_url="https://mp.weixin.qq.com/s?__biz=ABCDEF1234%3D%3D&mid=1&idx=1&sn=x",
        )
        with (
            mock.patch.object(wayback_wechat, "load_targets", return_value=targets),
            mock.patch.object(wayback_wechat, "load_candidates", return_value=[]),
            mock.patch.object(wayback_wechat, "existing_urls", return_value=set()),
            mock.patch.object(wayback_wechat, "load_discovery_state", return_value={"accounts": {}}),
            mock.patch.object(
                wayback_wechat, "lookup_public_registry_biz",
                return_value="ABCDEF1234==",
            ) as lookup,
            mock.patch.object(
                wayback_wechat, "discover_biz", return_value=[capture],
            ) as discover,
            mock.patch.object(
                wayback_wechat, "registry_biz_matches_account", return_value=True,
            ) as verify,
            mock.patch.object(wayback_wechat, "save_targets") as save_targets,
            mock.patch.object(wayback_wechat, "save_candidates"),
            mock.patch.object(wayback_wechat, "save_discovery_state") as save_state,
        ):
            result = wayback_wechat._discover_locked()
        self.assertEqual(0, result["identities_resolved"])
        self.assertEqual(1, result["identities_pending"])
        self.assertEqual(0, result["accounts_ok"])
        self.assertEqual("", targets[0]["biz_info"])
        self.assertEqual("ABCDEF1234==", targets[0]["candidate_biz"])
        self.assertTrue(targets[0]["candidate_verified_at"])
        lookup.assert_called_once_with("测试技术", session=mock.ANY)
        discover.assert_called_once_with("ABCDEF1234==", session=mock.ANY)
        verify.assert_called_once()
        save_targets.assert_called_once_with(targets)
        self.assertEqual(
            "identity_pending",
            save_state.call_args.args[0]["accounts"]["测试技术"]["status"],
        )

    def test_approve_identity_moves_candidate_to_biz_under_lock(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            targets_file = base / "targets.csv"
            targets_file.write_text(
                "account,company,biz_info,seed_url,candidate_biz,candidate_verified_at\n"
                "测试技术,测试,,,ABCDEF1234==,2026-08-24T12:00:00\n",
                encoding="utf-8",
            )
            with (
                mock.patch.object(wayback_wechat, "TARGETS_FILE", targets_file),
                mock.patch.object(wayback_wechat, "LOCK_FILE", base / "identity.lock"),
                mock.patch.object(
                    wayback_wechat, "DISCOVERY_STATE_FILE", base / "state.json",
                ),
            ):
                result = wayback_wechat.approve_identity(
                    "测试技术", "ABCDEF1234==",
                )
                rows = wayback_wechat.load_targets()
        self.assertEqual("ABCDEF1234==", result["biz_info"])
        self.assertEqual("ABCDEF1234==", rows[0]["biz_info"])
        self.assertEqual("", rows[0]["candidate_biz"])
        self.assertEqual("", rows[0]["candidate_verified_at"])

    def test_registry_cache_oserror_does_not_stop_later_account(self) -> None:
        targets = [
            {"account": "失败号", "company": "失败", "biz_info": "", "seed_url": ""},
            {"account": "候选号", "company": "成功", "biz_info": "", "seed_url": ""},
        ]
        capture = wayback_wechat.Capture(
            timestamp="20200101000000",
            url="https://mp.weixin.qq.com/s?__biz=SUCCESS1234%3D%3D&mid=1&idx=1&sn=x",
            archive_url="https://mp.weixin.qq.com/s?__biz=SUCCESS1234%3D%3D&mid=1&idx=1&sn=x",
        )
        with (
            mock.patch.object(wayback_wechat, "load_targets", return_value=targets),
            mock.patch.object(wayback_wechat, "load_candidates", return_value=[]),
            mock.patch.object(wayback_wechat, "existing_urls", return_value=set()),
            mock.patch.object(
                wayback_wechat, "load_discovery_state", return_value={"accounts": {}},
            ),
            mock.patch.object(
                wayback_wechat, "lookup_public_registry_biz",
                side_effect=[
                    wayback_wechat.PublicRegistryError("cache stat failed"),
                    "SUCCESS1234==",
                ],
            ) as lookup,
            mock.patch.object(wayback_wechat, "discover_biz", return_value=[capture]),
            mock.patch.object(
                wayback_wechat, "registry_biz_matches_account", return_value=True,
            ),
            mock.patch.object(wayback_wechat, "save_targets"),
            mock.patch.object(wayback_wechat, "save_candidates"),
            mock.patch.object(wayback_wechat, "save_discovery_state"),
        ):
            result = wayback_wechat._discover_locked()
        self.assertEqual(2, lookup.call_count)
        self.assertEqual(1, result["accounts_failed"])
        self.assertEqual(1, result["identities_pending"])
        self.assertEqual(0, result["accounts_ok"])
        self.assertEqual("", targets[1]["biz_info"])
        self.assertEqual("SUCCESS1234==", targets[1]["candidate_biz"])

    def test_registry_identity_mismatch_never_persists_biz(self) -> None:
        targets = [{
            "account": "测试技术", "company": "测试", "biz_info": "",
            "seed_url": "",
        }]
        with (
            mock.patch.object(wayback_wechat, "load_targets", return_value=targets),
            mock.patch.object(wayback_wechat, "load_candidates", return_value=[]),
            mock.patch.object(wayback_wechat, "existing_urls", return_value=set()),
            mock.patch.object(wayback_wechat, "load_discovery_state", return_value={"accounts": {}}),
            mock.patch.object(
                wayback_wechat, "lookup_public_registry_biz",
                return_value="ABCDEF1234==",
            ),
            mock.patch.object(wayback_wechat, "discover_biz", return_value=[]),
            mock.patch.object(
                wayback_wechat, "registry_biz_matches_account", return_value=False,
            ),
            mock.patch.object(wayback_wechat, "save_targets") as save_targets,
            mock.patch.object(wayback_wechat, "save_candidates"),
            mock.patch.object(wayback_wechat, "save_discovery_state"),
        ):
            result = wayback_wechat._discover_locked()
        self.assertEqual(1, result["accounts_failed"])
        self.assertEqual("", targets[0]["biz_info"])
        save_targets.assert_not_called()

    def test_seed_connection_failure_checkpoints_and_continues_next_account(self) -> None:
        targets = [
            {
                "account": "失败号", "company": "失败", "biz_info": "",
                "seed_url": "https://mp.weixin.qq.com/s/failed",
            },
            {
                "account": "成功号", "company": "成功", "biz_info": "",
                "seed_url": "https://mp.weixin.qq.com/s/success",
            },
        ]
        identity = mock.Mock(biz_info="SUCCESS1234==")
        checkpoints = []

        def checkpoint(state):
            checkpoints.append(json.loads(json.dumps(state)))

        with (
            mock.patch.object(wayback_wechat, "load_targets", return_value=targets),
            mock.patch.object(wayback_wechat, "load_candidates", return_value=[]),
            mock.patch.object(wayback_wechat, "existing_urls", return_value=set()),
            mock.patch.object(
                wayback_wechat, "load_discovery_state", return_value={"accounts": {}},
            ),
            mock.patch.object(
                wayback_wechat, "resolve_article_identity",
                side_effect=[
                    wayback_wechat.IdentityResolutionError("连接失败"),
                    identity,
                ],
            ) as resolve,
            mock.patch.object(wayback_wechat, "save_targets"),
            mock.patch.object(wayback_wechat, "discover_biz", return_value=[]),
            mock.patch.object(wayback_wechat, "save_candidates"),
            mock.patch.object(
                wayback_wechat, "save_discovery_state", side_effect=checkpoint,
            ),
        ):
            result = wayback_wechat._discover_locked()

        self.assertEqual(2, resolve.call_count)
        self.assertEqual(1, result["accounts_failed"])
        self.assertEqual(1, result["accounts_ok"])
        self.assertEqual(1, result["identities_resolved"])
        self.assertEqual("identity_failed", checkpoints[0]["accounts"]["失败号"]["status"])
        self.assertNotIn("成功号", checkpoints[0]["accounts"])
        self.assertEqual("ok", checkpoints[-1]["accounts"]["成功号"]["status"])

    def test_pending_is_attempted_before_earlier_failed_rows(self) -> None:
        failed = [
            {
                "account": "测试", "company": "测试", "biz_info": "ABC==",
                "url": f"https://mp.weixin.qq.com/s?__biz=ABC%3D%3D&mid={i}&idx=1&sn=x",
                "timestamps": "20200101000000", "captures_json": "",
                "status": "failed", "error": "", "attempt_cursor": "0",
                "failure_rounds": "0", "last_attempt_at": "",
                "next_attempt_at": "",
            }
            for i in range(40)
        ]
        pending = {
            "account": "测试", "company": "测试", "biz_info": "ABC==",
            "url": "https://mp.weixin.qq.com/s?__biz=ABC%3D%3D&mid=999&idx=1&sn=x",
            "timestamps": "20200101000000", "captures_json": "",
            "status": "pending", "error": "", "attempt_cursor": "0",
            "failure_rounds": "0", "last_attempt_at": "", "next_attempt_at": "",
        }
        with (
            mock.patch.object(wayback_wechat, "load_candidates", return_value=[*failed, pending]),
            mock.patch.object(wayback_wechat, "save_candidates"),
            mock.patch.object(
                wayback_wechat, "fetch_capture",
                return_value={"title": "生活随笔", "body": "正文" * 200, "date": "2020-01-01"},
            ) as fetch,
        ):
            wayback_wechat._backfill_locked(max_attempts=1)
        self.assertEqual(pending["url"], fetch.call_args.args[1])

    def test_build_failure_keeps_dirty_state_for_next_run(self) -> None:
        with (
            mock.patch.object(
                sys, "argv", ["sgt-kb wayback-wechat", "backfill", "--max-attempts", "1"]
            ),
            mock.patch.object(
                wayback_wechat, "backfill",
                return_value={
                    "attempted": 0, "ingested": 0, "irrelevant": 0,
                    "failed": 0, "existing": 0,
                },
            ),
            mock.patch.object(wayback_wechat, "index_needs_rebuild", return_value=True),
            mock.patch.object(
                wayback_wechat.subprocess, "run",
                side_effect=subprocess.CalledProcessError(1, "build"),
            ),
            mock.patch.object(wayback_wechat, "clear_index_dirty") as clear,
        ):
            with self.assertRaises(subprocess.CalledProcessError):
                wayback_wechat.main()
        clear.assert_not_called()

    def test_due_only_retries_failed_account_without_requerying_recent_ok(self) -> None:
        now = wayback_wechat.datetime(2026, 8, 24, 12, 0, 0)
        targets = [
            {"account": "成功号", "company": "成功", "biz_info": "GOOD=="},
            {"account": "失败号", "company": "失败", "biz_info": "BAD=="},
        ]
        state = {"accounts": {
            "成功号": {"status": "ok", "updated_at": "2026-08-23T12:00:00"},
            "失败号": {"status": "failed", "updated_at": "2026-08-22T12:00:00"},
        }}
        with (
            mock.patch.object(wayback_wechat, "load_targets", return_value=targets),
            mock.patch.object(wayback_wechat, "load_candidates", return_value=[]),
            mock.patch.object(wayback_wechat, "existing_urls", return_value=set()),
            mock.patch.object(wayback_wechat, "load_discovery_state", return_value=state),
            mock.patch.object(wayback_wechat, "discover_biz", return_value=[]) as discover,
            mock.patch.object(wayback_wechat, "save_candidates"),
            mock.patch.object(wayback_wechat, "save_discovery_state"),
        ):
            result = wayback_wechat._discover_locked(due_only=True, now=now)
        self.assertEqual(1, discover.call_count)
        self.assertEqual("BAD==", discover.call_args.args[0])
        self.assertEqual(1, result["accounts_skipped"])

    def test_exhausted_candidate_revives_when_new_capture_appears(self) -> None:
        url = "https://mp.weixin.qq.com/s?__biz=ABC%3D%3D&mid=1&idx=1&sn=x"
        old_capture = {"timestamp": "20200101000000", "archive_url": url}
        row = {
            "account": "测试号", "company": "测试", "biz_info": "ABC==",
            "url": url, "timestamps": old_capture["timestamp"],
            "captures_json": __import__("json").dumps([old_capture]),
            "status": "exhausted", "error": "HTTPError", "attempt_cursor": "0",
            "failure_rounds": "3", "last_attempt_at": "2026-08-20T00:00:00",
            "next_attempt_at": "",
        }
        captures = [
            wayback_wechat.Capture(old_capture["timestamp"], url, url),
            wayback_wechat.Capture("20210101000000", url, url + "&scene=21"),
        ]
        with (
            mock.patch.object(wayback_wechat, "load_targets", return_value=[{
                "account": "测试号", "company": "测试", "biz_info": "ABC==",
            }]),
            mock.patch.object(wayback_wechat, "load_candidates", return_value=[row]),
            mock.patch.object(wayback_wechat, "existing_urls", return_value=set()),
            mock.patch.object(wayback_wechat, "load_discovery_state", return_value={"accounts": {}}),
            mock.patch.object(wayback_wechat, "discover_biz", return_value=captures),
            mock.patch.object(wayback_wechat, "save_candidates") as save,
            mock.patch.object(wayback_wechat, "save_discovery_state"),
        ):
            wayback_wechat._discover_locked()
        saved = save.call_args_list[-1].args[0][0]
        self.assertEqual("pending", saved["status"])
        self.assertEqual("0", saved["failure_rounds"])


if __name__ == "__main__":
    unittest.main()
