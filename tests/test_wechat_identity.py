import json
import socket
import unittest
from unittest import mock

from sgt_kb.collection import wechat_identity


class WechatIdentityTest(unittest.TestCase):
    def test_seed_normalization_drops_session_parameters(self) -> None:
        source = (
            "http://mp.weixin.qq.com/s?__biz=ABCDEF1234%3D%3D&mid=123&idx=1&sn=x"
            "&key=SECRET&pass_ticket=SECRET2&uin=SECRET3"
        )
        normalized = wechat_identity.normalize_seed_url(source)
        self.assertTrue(normalized.startswith("https://mp.weixin.qq.com/s?"))
        self.assertIn("__biz=ABCDEF1234%3D%3D", normalized)
        self.assertNotIn("SECRET", normalized)
        self.assertNotIn("pass_ticket", normalized)

    def test_seed_rejects_non_wechat_host(self) -> None:
        with self.assertRaises(ValueError):
            wechat_identity.normalize_seed_url("https://example.com/s/article")

    def test_identity_is_extracted_from_archived_html(self) -> None:
        source = '''
            <script>
            var biz = ""||"MzI4NjY4MTU5Nw==";
            var nickname = "vivo互联网技术";
            </script>
        '''
        identity = wechat_identity.extract_identity_from_html(
            source, "https://mp.weixin.qq.com/s/example", "20241007222537",
        )
        self.assertEqual("vivo互联网技术", identity.account)
        self.assertEqual("MzI4NjY4MTU5Nw==", identity.biz_info)

    def test_resolver_uses_wayback_snapshot_and_checks_account(self) -> None:
        source = 'var biz = "MzI4NjY4MTU5Nw=="; var nickname = "vivo互联网技术";'
        session = mock.Mock()
        with (
            mock.patch.object(
                wechat_identity, "discover_seed_timestamps",
                return_value=["20241007222537"],
            ),
            mock.patch.object(wechat_identity, "read_snapshot_html", return_value=source),
        ):
            identity = wechat_identity.resolve_article_identity(
                "https://mp.weixin.qq.com/s/MwG9GpnTVbma69PiOHHvgw",
                expected_account="vivo互联网技术",
                session=session,
            )
        self.assertEqual("MzI4NjY4MTU5Nw==", identity.biz_info)

    def test_resolver_rejects_wrong_account(self) -> None:
        source = 'var biz = "MzI4NjY4MTU5Nw=="; var nickname = "其他账号";'
        with (
            mock.patch.object(
                wechat_identity, "discover_seed_timestamps",
                return_value=["20241007222537"],
            ),
            mock.patch.object(wechat_identity, "read_snapshot_html", return_value=source),
        ):
            with self.assertRaisesRegex(
                wechat_identity.IdentityResolutionError, "名称与目标不一致",
            ):
                wechat_identity.resolve_article_identity(
                    "https://mp.weixin.qq.com/s/MwG9GpnTVbma69PiOHHvgw",
                    expected_account="vivo互联网技术",
                    session=mock.Mock(),
                )

    def test_snapshot_body_limit_is_enforced_and_response_closed(self) -> None:
        response = mock.Mock()
        response.headers = {"Content-Length": str(wechat_identity.MAX_HTML_BYTES + 1)}
        response.raise_for_status.return_value = None
        with mock.patch.object(wechat_identity, "safe_get", return_value=response):
            with self.assertRaisesRegex(
                wechat_identity.IdentityResolutionError, "超过大小限制",
            ):
                wechat_identity.read_snapshot_html(
                    "https://web.archive.org/web/20200101000000id_/https://mp.weixin.qq.com/s/x",
                    mock.Mock(),
                )
        response.close.assert_called_once()

    def test_resolver_tries_next_snapshot_after_first_connection_failure(self) -> None:
        source = (
            'var biz = "MzI4NjY4MTU5Nw=="; '
            'var nickname = "vivo互联网技术";'
        ).encode()
        response = mock.Mock(
            headers={}, encoding="utf-8",
            is_redirect=False, is_permanent_redirect=False,
        )
        response.raise_for_status.return_value = None
        response.iter_content.return_value = [source]
        session = mock.Mock()
        with (
            mock.patch.object(
                wechat_identity, "discover_seed_timestamps",
                return_value=["20241007222537", "20231007222537"],
            ),
            mock.patch.object(
                wechat_identity, "safe_get",
                side_effect=[
                    wechat_identity.requests.ConnectionError("offline"),
                    response,
                ],
            ) as safe_get,
        ):
            identity = wechat_identity.resolve_article_identity(
                "https://mp.weixin.qq.com/s/MwG9GpnTVbma69PiOHHvgw",
                expected_account="vivo互联网技术",
                session=session,
            )
        self.assertEqual("20231007222537", identity.timestamp)
        self.assertEqual(2, safe_get.call_count)
        response.close.assert_called_once()

    def test_resolver_tries_next_snapshot_after_first_dns_failure(self) -> None:
        source = (
            'var biz = "MzI4NjY4MTU5Nw=="; '
            'var nickname = "vivo互联网技术";'
        ).encode()
        response = mock.Mock(
            headers={}, encoding="utf-8",
            is_redirect=False, is_permanent_redirect=False,
        )
        response.raise_for_status.return_value = None
        response.iter_content.return_value = [source]
        session = mock.Mock()
        session.get.return_value = response
        with (
            mock.patch.object(
                wechat_identity, "discover_seed_timestamps",
                return_value=["20241007222537", "20231007222537"],
            ),
            mock.patch(
                "sgt_kb.collection.crawl.socket.getaddrinfo",
                side_effect=[
                    socket.gaierror("dns failed"),
                    [(2, 1, 6, "", ("8.8.8.8", 443))],
                ],
            ),
        ):
            identity = wechat_identity.resolve_article_identity(
                "https://mp.weixin.qq.com/s/MwG9GpnTVbma69PiOHHvgw",
                expected_account="vivo互联网技术",
                session=session,
            )
        self.assertEqual("20231007222537", identity.timestamp)
        self.assertEqual(1, session.get.call_count)
        response.close.assert_called_once()

    def test_cdx_rate_limit_is_retried_and_responses_are_closed(self) -> None:
        limited = mock.Mock(status_code=429, headers={"Retry-After": "0"})
        success = mock.Mock(status_code=200, headers={})
        success.raise_for_status.return_value = None
        success.iter_content.return_value = [
            json.dumps([["timestamp"], ["20241007222537"]]).encode(),
        ]
        session = mock.Mock()
        with (
            mock.patch.object(
                wechat_identity, "safe_get", side_effect=[limited, success],
            ) as safe_get,
            mock.patch.object(wechat_identity.time, "sleep"),
        ):
            timestamps = wechat_identity.discover_seed_timestamps(
                "https://mp.weixin.qq.com/s/example", session,
            )
        self.assertEqual(["20241007222537"], timestamps)
        self.assertEqual(2, safe_get.call_count)
        self.assertTrue(safe_get.call_args.kwargs["stream"])
        self.assertEqual({"web.archive.org"}, safe_get.call_args.kwargs["allowed_hosts"])
        limited.close.assert_called_once()
        success.close.assert_called_once()

    def test_cdx_cross_domain_redirect_is_rejected_before_second_request(self) -> None:
        redirect = mock.Mock(
            status_code=302,
            headers={"Location": "https://evil.example/collect"},
            is_redirect=True,
            is_permanent_redirect=False,
        )
        session = mock.Mock()
        session.get.return_value = redirect
        with mock.patch(
            "sgt_kb.collection.crawl.socket.getaddrinfo",
            return_value=[(2, 1, 6, "", ("8.8.8.8", 443))],
        ):
            with self.assertRaisesRegex(
                wechat_identity.IdentityResolutionError, "安全策略拒绝",
            ):
                wechat_identity.discover_seed_timestamps(
                    "https://mp.weixin.qq.com/s/example", session,
                )
        self.assertEqual(1, session.get.call_count)
        redirect.close.assert_called_once()

    def test_cdx_content_length_limit_fails_closed_and_closes(self) -> None:
        response = mock.Mock(
            status_code=200,
            headers={"Content-Length": str(wechat_identity.MAX_CDX_BYTES + 1)},
        )
        response.raise_for_status.return_value = None
        with mock.patch.object(wechat_identity, "safe_get", return_value=response):
            with self.assertRaisesRegex(
                wechat_identity.IdentityResolutionError, "超过大小限制",
            ):
                wechat_identity.discover_seed_timestamps(
                    "https://mp.weixin.qq.com/s/example", mock.Mock(),
                )
        response.iter_content.assert_not_called()
        response.close.assert_called_once()

    def test_cdx_streamed_body_limit_without_length_fails_closed_and_closes(self) -> None:
        response = mock.Mock(status_code=200, headers={})
        response.raise_for_status.return_value = None
        response.iter_content.return_value = [
            b"x" * wechat_identity.MAX_CDX_BYTES,
            b"x",
        ]
        with mock.patch.object(wechat_identity, "safe_get", return_value=response):
            with self.assertRaisesRegex(
                wechat_identity.IdentityResolutionError, "超过大小限制",
            ):
                wechat_identity.discover_seed_timestamps(
                    "https://mp.weixin.qq.com/s/example", mock.Mock(),
                )
        response.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
