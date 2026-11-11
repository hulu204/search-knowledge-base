import socket
import unittest
from unittest import mock

import crawl
import figure_pipeline


class UrlSafetyTest(unittest.TestCase):
    def test_dns_resolution_failure_is_converted_to_safe_url_error(self) -> None:
        with mock.patch(
            "crawl.socket.getaddrinfo", side_effect=socket.gaierror("dns failed"),
        ):
            with self.assertRaisesRegex(ValueError, "DNS 解析失败"):
                crawl.validate_public_url("https://web.archive.org/example")

    def test_loopback_address_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "非公网地址"):
            crawl.validate_public_url("http://127.0.0.1/private")

    def test_unapproved_redirect_host_is_rejected_before_request(self) -> None:
        response = mock.Mock()
        response.is_redirect = True
        response.is_permanent_redirect = False
        response.headers = {"Location": "https://other.example/private"}
        with mock.patch.object(crawl, "validate_public_url") as validate:
            with mock.patch.object(crawl.S, "get", return_value=response) as get:
                validate.side_effect = [None, ValueError("未授权域名")]
                with self.assertRaisesRegex(ValueError, "未授权域名"):
                    crawl.safe_get(
                        "https://allowed.example/post",
                        allowed_hosts={"allowed.example"},
                    )
        self.assertEqual(1, get.call_count)
        response.close.assert_called_once()

    def test_figure_loopback_is_rejected_before_download(self) -> None:
        session = mock.Mock()
        with self.assertRaisesRegex(ValueError, "非公网地址"):
            figure_pipeline._download(session, "http://127.0.0.1/private.png", "https://source.example")
        session.get.assert_not_called()

    def test_figure_public_redirect_to_private_is_rejected(self) -> None:
        redirect = mock.Mock()
        redirect.is_redirect = True
        redirect.is_permanent_redirect = False
        redirect.headers = {"Location": "http://169.254.169.254/latest/meta-data"}
        session = mock.Mock()
        session.get.return_value = redirect
        with mock.patch.object(crawl, "validate_public_url") as validate:
            validate.side_effect = [None, ValueError("非公网地址")]
            with self.assertRaisesRegex(ValueError, "非公网地址"):
                crawl.safe_get("https://images.example/a.png", session=session)
        self.assertEqual(1, session.get.call_count)
        redirect.close.assert_called_once()

    def test_figure_content_length_limit_is_enforced(self) -> None:
        response = mock.Mock()
        response.headers = {
            "Content-Type": "image/png",
            "Content-Length": str(figure_pipeline.MAX_IMAGE_BYTES + 1),
        }
        with mock.patch.object(figure_pipeline, "safe_get", return_value=response):
            with self.assertRaisesRegex(ValueError, "exceeds"):
                figure_pipeline._download(mock.Mock(), "https://images.example/a.png", "")

    def test_figure_stream_limit_is_enforced_without_content_length(self) -> None:
        response = mock.Mock()
        response.headers = {"Content-Type": "image/png"}
        response.iter_content.return_value = [
            b"x" * figure_pipeline.MAX_IMAGE_BYTES,
            b"y",
        ]
        with mock.patch.object(figure_pipeline, "safe_get", return_value=response):
            with self.assertRaisesRegex(ValueError, "exceeds"):
                figure_pipeline._download(mock.Mock(), "https://images.example/a.png", "")


if __name__ == "__main__":
    unittest.main()
