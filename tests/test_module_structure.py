import importlib
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

from sgt_kb.__main__ import COMMANDS, main
from sgt_kb.paths import ROOT


HELPERS = {
    "english_sources": "sgt_kb.collection.english_sources",
    "exa_mcp": "sgt_kb.collection.exa_mcp",
    "wechat_public_registry": "sgt_kb.collection.wechat_public_registry",
}


class ModuleStructureTest(unittest.TestCase):
    def test_implementations_live_in_package_and_root_wrappers_are_removed(self):
        self.assertEqual(Path(__file__).resolve().parents[1], ROOT)
        modules = {*COMMANDS.values(), *HELPERS.values()}
        self.assertEqual(28, len(modules))
        for name in sorted(modules):
            with self.subTest(module=name):
                module = importlib.import_module(name)
                expected = ROOT / (name.replace(".", "/") + ".py")
                self.assertEqual(expected, Path(module.__file__))
                self.assertFalse((ROOT / expected.name).exists())
                if hasattr(module, "BASE"):
                    self.assertEqual(ROOT, module.BASE)

    def test_recency_helpers_are_shared_by_package_server(self):
        from sgt_kb.service import kb_server
        from sgt_kb.retrieval import recency

        self.assertIs(recency._apply_recency, kb_server._apply_recency)
        self.assertIs(recency._freshness_factor, kb_server._freshness_factor)
        self.assertEqual(recency.RECENCY_FLOOR, kb_server.RECENCY_FLOOR)

    def test_mcp_transport_remains_lazy(self):
        from sgt_kb.service import kb_server

        sentinel = object()
        with mock.patch.object(kb_server, "_get_mcp", return_value=sentinel):
            self.assertIs(sentinel, kb_server.mcp)

    def test_unified_cli_dispatches_arguments_and_restores_process_argv(self):
        module = mock.Mock()
        original = sys.argv

        def invoke():
            self.assertEqual(
                ["python -m sgt_kb ingest-url", "https://example.test/article", "--skip-images"],
                sys.argv,
            )
            return 7

        module.main.side_effect = invoke
        with mock.patch("sgt_kb.__main__.importlib.import_module", return_value=module) as load:
            self.assertEqual(7, main(["ingest-url", "https://example.test/article", "--skip-images"]))
            load.assert_called_once_with("sgt_kb.collection.ingest_url")
        self.assertIs(original, sys.argv)

    def test_unified_cli_help_and_commands(self):
        for command in (None, *sorted(COMMANDS)):
            with self.subTest(command=command):
                result = subprocess.run(
                    [sys.executable, "-m", "sgt_kb", *([command] if command else []), "--help"],
                    cwd=ROOT, capture_output=True, text=True, timeout=10,
                )
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertIn("usage:", result.stdout)


if __name__ == "__main__":
    unittest.main()
