import importlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

from sgt_kb.paths import ROOT


GROUPS = {
    "collection": (
        "crawl", "daily_update", "en_poll", "english_sources", "exa_discover",
        "exa_mcp", "figure_pipeline", "ingest_url", "ingestion_queue",
        "oneapi_wechat", "review_queue", "rss_poll", "video_ingest",
        "wayback_catchup", "wayback_wechat", "wechat_auth_update",
        "wechat_catchup", "wechat_identity", "wechat_mp",
        "wechat_public_registry", "wechat_webhook", "weread_mp",
    ),
    "indexing": ("build_index", "export_pages", "kb_gate"),
    "service": ("kb_server", "start_workbench", "workbench_api"),
}


class ModuleStructureTest(unittest.TestCase):
    def test_legacy_imports_share_canonical_modules_and_checkout_paths(self):
        self.assertEqual(Path(__file__).resolve().parents[1], ROOT)
        for group, names in GROUPS.items():
            for name in names:
                with self.subTest(module=name):
                    legacy = importlib.import_module(name)
                    canonical = importlib.import_module(f"sgt_kb.{group}.{name}")
                    self.assertIs(legacy, canonical)
                    self.assertEqual(ROOT / "sgt_kb" / group / f"{name}.py", Path(legacy.__file__))
                    if hasattr(canonical, "BASE"):
                        self.assertEqual(ROOT, canonical.BASE)

    def test_legacy_monkeypatch_changes_canonical_function_globals(self):
        import crawl
        from sgt_kb.collection import crawl as canonical

        with mock.patch.object(crawl, "BASE", Path("/temporary-test-base")):
            self.assertEqual(Path("/temporary-test-base"), canonical.BASE)
            self.assertIs(crawl.write_article.__globals__, canonical.__dict__)

    def test_spec_loaded_legacy_webhook_forwards_to_implementation(self):
        from sgt_kb.collection import wechat_webhook

        spec = importlib.util.spec_from_file_location(
            "legacy_webhook_test", ROOT / "wechat_webhook.py",
        )
        wrapper = importlib.util.module_from_spec(spec)
        self.addCleanup(sys.modules.pop, "legacy_webhook_test", None)
        spec.loader.exec_module(wrapper)
        self.assertIs(wrapper.signature, wechat_webhook.signature)
        self.assertIs(sys.modules["legacy_webhook_test"], wechat_webhook)

    def test_recency_helpers_are_reexported_by_legacy_server(self):
        import kb_server
        from sgt_kb.retrieval import recency

        self.assertIs(recency._apply_recency, kb_server._apply_recency)
        self.assertIs(recency._freshness_factor, kb_server._freshness_factor)
        self.assertEqual(recency.RECENCY_FLOOR, kb_server.RECENCY_FLOOR)

    def test_mcp_attribute_remains_lazy_through_legacy_import(self):
        import kb_server
        from sgt_kb.service import kb_server as canonical

        sentinel = object()
        with mock.patch.object(canonical, "_get_mcp", return_value=sentinel):
            self.assertIs(sentinel, kb_server.mcp)

    def test_root_commands_and_package_commands_keep_help(self):
        for name, module in (
            ("build_index", "sgt_kb.indexing.build_index"),
            ("export_pages", "sgt_kb.indexing.export_pages"),
            ("ingest_url", "sgt_kb.collection.ingest_url"),
            ("wechat_webhook", "sgt_kb.collection.wechat_webhook"),
        ):
            with self.subTest(command=name):
                for args in ([str(ROOT / f"{name}.py")], ["-m", module]):
                    result = subprocess.run(
                        [sys.executable, *args, "--help"],
                        cwd=ROOT, capture_output=True, text=True, timeout=10,
                    )
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertIn("usage:", result.stdout)

    def test_legacy_scripts_keep_inline_dependency_metadata(self):
        for group, names in GROUPS.items():
            for name in names:
                source = (ROOT / "sgt_kb" / group / f"{name}.py").read_text(encoding="utf-8")
                if "# /// script\n" in source:
                    with self.subTest(script=name):
                        metadata = source[source.index("# /// script\n"):].split("# ///\n", 1)[0]
                        self.assertIn(metadata, (ROOT / f"{name}.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
