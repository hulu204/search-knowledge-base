# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Low-rate scheduled Wayback discovery and historical article recovery."""
from __future__ import annotations

import fcntl
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

from sgt_kb.paths import ROOT

BASE = ROOT
LOCK_FILE = BASE / "ingestion" / "daily.lock"
SCHEDULE_STATE = BASE / "ingestion" / "wayback_schedule_state.json"
DISCOVER_INTERVAL = timedelta(days=7)


def load_state() -> dict:
    if not SCHEDULE_STATE.exists():
        return {}
    try:
        return json.loads(SCHEDULE_STATE.read_text())
    except (OSError, ValueError):
        return {}


def save_state(state: dict) -> None:
    SCHEDULE_STATE.parent.mkdir(exist_ok=True)
    temp = SCHEDULE_STATE.with_suffix(".json.tmp")
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    temp.replace(SCHEDULE_STATE)


def discovery_due(state: dict, now: datetime | None = None) -> bool:
    now = now or datetime.now()
    value = state.get("last_discover_at", "")
    try:
        previous = datetime.fromisoformat(value)
    except ValueError:
        return True
    return now - previous >= DISCOVER_INTERVAL


def run_command(args: list[str], timeout: int) -> int:
    return subprocess.run(args, cwd=BASE, timeout=timeout, check=False).returncode


def main() -> int:
    LOCK_FILE.parent.mkdir(exist_ok=True)
    with LOCK_FILE.open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("其他知识库更新任务正在运行,本轮 Wayback 跳过")
            return 0

        state = load_state()
        code = run_command(
            [sys.executable, "-m", "sgt_kb", "wayback-wechat", "discover", "--due-only"],
            timeout=3600,
        )
        if code not in {0, 2}:
            return code
        state["last_discover_attempt_at"] = datetime.now().isoformat(timespec="seconds")
        state["last_discover_status"] = "ok" if code == 0 else "partial"
        save_state(state)

        return run_command([
            sys.executable, "-m", "sgt_kb", "wayback-wechat", "backfill",
            "--max-articles", "5", "--max-attempts", "40",
            "--max-snapshots", "2",
        ], timeout=3600)


if __name__ == "__main__":
    raise SystemExit(main())
