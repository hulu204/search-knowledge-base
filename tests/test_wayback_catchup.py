import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

import wayback_catchup


class WaybackCatchupTest(unittest.TestCase):
    def test_discovery_due_after_seven_days(self) -> None:
        now = datetime(2026, 8, 24, 12, 0, 0)
        state = {"last_discover_at": (now - timedelta(days=7)).isoformat()}
        self.assertTrue(wayback_catchup.discovery_due(state, now))
        state = {"last_discover_at": (now - timedelta(days=1)).isoformat()}
        self.assertFalse(wayback_catchup.discovery_due(state, now))

    def test_main_discovers_then_runs_bounded_backfill(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            calls = []

            def run(args, timeout):
                calls.append((args, timeout))
                return 0

            with (
                mock.patch.object(wayback_catchup, "LOCK_FILE", base / "daily.lock"),
                mock.patch.object(wayback_catchup, "SCHEDULE_STATE", base / "state.json"),
                mock.patch.object(wayback_catchup, "run_command", side_effect=run),
            ):
                code = wayback_catchup.main()

        self.assertEqual(0, code)
        self.assertIn("discover", calls[0][0])
        self.assertIn("backfill", calls[1][0])
        self.assertIn("--max-attempts", calls[1][0])
        self.assertIn("40", calls[1][0])

    def test_partial_discovery_does_not_delay_retry_but_runs_backfill(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            calls = []
            with (
                mock.patch.object(wayback_catchup, "LOCK_FILE", base / "daily.lock"),
                mock.patch.object(wayback_catchup, "SCHEDULE_STATE", base / "state.json"),
                mock.patch.object(
                    wayback_catchup, "run_command", side_effect=[2, 0]
                ) as run,
            ):
                code = wayback_catchup.main()
            self.assertEqual(0, code)
            self.assertEqual(2, run.call_count)
            state = __import__("json").loads((base / "state.json").read_text())
            self.assertEqual("partial", state["last_discover_status"])


if __name__ == "__main__":
    unittest.main()
