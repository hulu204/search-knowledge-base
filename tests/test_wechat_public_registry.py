import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from sgt_kb.collection import wechat_public_registry


SAMPLE = (
    "\ufeffname,bizid,description\n"
    "vivo互联网技术,MzI4NjY4MTU5Nw==,技术分享\n"
    "冲突号,MzI1NjEwMTM4OA==,旧号\n"
    "冲突号,MzU1NTMyOTI4Mw==,新号\n"
).encode()


class WechatPublicRegistryTest(unittest.TestCase):
    def test_registry_url_is_pinned_to_immutable_commit(self) -> None:
        self.assertRegex(wechat_public_registry.REGISTRY_COMMIT, r"^[0-9a-f]{40}$")
        self.assertIn(
            f"/{wechat_public_registry.REGISTRY_COMMIT}/list.csv",
            wechat_public_registry.REGISTRY_URL,
        )
        self.assertNotIn("/main/", wechat_public_registry.REGISTRY_URL)

    def test_parser_keeps_exact_unique_name_and_drops_conflict(self) -> None:
        records = wechat_public_registry.parse_registry_bytes(SAMPLE)
        self.assertEqual("MzI4NjY4MTU5Nw==", records["vivo互联网技术"])
        self.assertNotIn("冲突号", records)

    def test_fresh_cache_lookup_does_not_use_network(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory) / "registry.csv"
            cache.write_bytes(SAMPLE)
            now = cache.stat().st_mtime + 60
            with (
                mock.patch.object(
                    wechat_public_registry, "download_registry",
                ) as download,
                mock.patch.object(
                    wechat_public_registry, "MIN_REGISTRY_RECORDS", 1,
                ),
            ):
                records = wechat_public_registry.load_public_registry(
                    mock.Mock(), cache_file=cache, now=now,
                )
            self.assertEqual("MzI4NjY4MTU5Nw==", records["vivo互联网技术"])
            download.assert_not_called()

    def test_download_uses_safe_host_limit_and_closes_response(self) -> None:
        response = mock.Mock(status_code=200, headers={})
        response.raise_for_status.return_value = None
        response.iter_content.return_value = [SAMPLE]
        with (
            mock.patch.object(
                wechat_public_registry, "safe_get", return_value=response,
            ) as safe_get,
            mock.patch.object(wechat_public_registry, "MIN_REGISTRY_RECORDS", 1),
        ):
            data = wechat_public_registry.download_registry(mock.Mock())
        self.assertEqual(SAMPLE, data)
        self.assertEqual(
            {"raw.githubusercontent.com"}, safe_get.call_args.kwargs["allowed_hosts"],
        )
        self.assertTrue(safe_get.call_args.kwargs["stream"])
        response.close.assert_called_once()

    def test_download_stream_limit_fails_closed_and_closes(self) -> None:
        response = mock.Mock(status_code=200, headers={})
        response.raise_for_status.return_value = None
        response.iter_content.return_value = [
            b"x" * wechat_public_registry.MAX_REGISTRY_BYTES, b"x",
        ]
        with mock.patch.object(
            wechat_public_registry, "safe_get", return_value=response,
        ):
            with self.assertRaisesRegex(
                wechat_public_registry.PublicRegistryError, "大小限制",
            ):
                wechat_public_registry.download_registry(mock.Mock())
        response.close.assert_called_once()

    def test_empty_registry_download_fails_minimum_record_gate(self) -> None:
        response = mock.Mock(status_code=200, headers={})
        response.raise_for_status.return_value = None
        response.iter_content.return_value = [b"name,bizid,description\n"]
        with (
            mock.patch.object(
                wechat_public_registry, "safe_get", return_value=response,
            ),
            mock.patch.object(wechat_public_registry, "MIN_REGISTRY_RECORDS", 1),
            self.assertRaisesRegex(
                wechat_public_registry.PublicRegistryError, "记录数异常",
            ),
        ):
            wechat_public_registry.download_registry(mock.Mock())
        response.close.assert_called_once()

    def test_stale_cache_is_used_when_refresh_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory) / "registry.csv"
            cache.write_bytes(SAMPLE)
            os.utime(cache, (1, 1))
            with (
                mock.patch.object(
                    wechat_public_registry, "download_registry",
                    side_effect=wechat_public_registry.PublicRegistryError("offline"),
                ),
                mock.patch.object(
                    wechat_public_registry, "MIN_REGISTRY_RECORDS", 1,
                ),
            ):
                records = wechat_public_registry.load_public_registry(
                    mock.Mock(), cache_file=cache, now=10**9,
                )
        self.assertEqual("MzI4NjY4MTU5Nw==", records["vivo互联网技术"])

    def test_corrupt_fresh_cache_is_replaced_from_network(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory) / "registry.csv"
            cache.write_bytes(b"not,a,registry\n")
            with (
                mock.patch.object(
                    wechat_public_registry, "download_registry", return_value=SAMPLE,
                ) as download,
                mock.patch.object(
                    wechat_public_registry, "MIN_REGISTRY_RECORDS", 1,
                ),
            ):
                records = wechat_public_registry.load_public_registry(
                    mock.Mock(), cache_file=cache,
                    now=cache.stat().st_mtime + 60,
                )
        self.assertEqual("MzI4NjY4MTU5Nw==", records["vivo互联网技术"])
        download.assert_called_once()

    def test_abnormally_shrunken_download_never_overwrites_good_cache(self) -> None:
        old = (
            "name,bizid\n" + "".join(
                f"账号{i},MzI4NjY4MTU5N{i:02d}==\n" for i in range(10)
            )
        ).encode()
        new = b"name,bizid\nonly,MzI4NjY4MTU5Nw==\n"
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory) / "registry.csv"
            cache.write_bytes(old)
            os.utime(cache, (1, 1))
            with (
                mock.patch.object(
                    wechat_public_registry, "download_registry", return_value=new,
                ),
                mock.patch.object(
                    wechat_public_registry, "MIN_REGISTRY_RECORDS", 1,
                ),
            ):
                records = wechat_public_registry.load_public_registry(
                    mock.Mock(), cache_file=cache, now=10**9,
                )
            self.assertEqual(10, len(records))
            self.assertEqual(old, cache.read_bytes())

    def test_cache_stat_and_read_oserrors_are_domain_errors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory) / "registry.csv"
            cache.write_bytes(SAMPLE)
            with (
                mock.patch.object(Path, "stat", side_effect=OSError("stat failed")),
                self.assertRaises(wechat_public_registry.PublicRegistryError),
            ):
                wechat_public_registry.load_public_registry(
                    mock.Mock(), cache_file=cache,
                )
            with (
                mock.patch.object(Path, "read_bytes", side_effect=OSError("read failed")),
                self.assertRaises(wechat_public_registry.PublicRegistryError),
            ):
                wechat_public_registry.load_public_registry(
                    mock.Mock(), cache_file=cache,
                )

    def test_replace_oserror_preserves_old_cache_and_cleans_temp(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory) / "registry.csv"
            cache.write_bytes(b"old-cache")
            with (
                mock.patch.object(Path, "replace", side_effect=OSError("replace failed")),
                self.assertRaises(wechat_public_registry.PublicRegistryError),
            ):
                wechat_public_registry.save_registry_cache(SAMPLE, cache)
            self.assertEqual(b"old-cache", cache.read_bytes())
            self.assertEqual([cache], list(cache.parent.iterdir()))


if __name__ == "__main__":
    unittest.main()
