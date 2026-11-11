# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Lightweight WeChat catch-up runner for launchd.

Runs at a low cadence, advances at most two history pages per invocation, and
only crawls/rebuilds when the manifest actually grows.  It shares daily.lock
with daily_update.py so the two orchestrators cannot overlap.
"""
from __future__ import annotations
import shutil

import fcntl
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

from sgt_kb.paths import ROOT

BASE = ROOT
LOCK_FILE = BASE / "ingestion" / "daily.lock"
STATE_FILE = BASE / "ingestion" / "wechat_mp_state.json"
MANIFEST = BASE / "crawl_manifest.csv"
AUTH_FILE = BASE / ".wechat_mp_auth.json"
AUTH_NOTICE_FILE = BASE / "ingestion" / "wechat_auth_notice.json"
UV = shutil.which("uv") or "uv"
AUTH_EXPIRED_EXIT = 76
AUTH_NOTICE_INTERVAL_SECONDS = 2 * 60 * 60


def backfill_pending() -> bool:
    if not STATE_FILE.exists():
        return False
    state = json.loads(STATE_FILE.read_text())
    for account in state.get("accounts", {}).values():
        queries = account.get("queries") or {}
        if not queries or not all(query.get("done") for query in queries.values()):
            return True
    return False


def run_command(args: list[str], timeout: int) -> int:
    result = subprocess.run(args, cwd=BASE, timeout=timeout, check=False)
    return result.returncode


def auth_fingerprint() -> str:
    if not AUTH_FILE.exists():
        return "missing"
    return hashlib.sha256(AUTH_FILE.read_bytes()).hexdigest()


def notify_auth_expired() -> None:
    fingerprint = auth_fingerprint()
    now = int(time.time())
    if AUTH_NOTICE_FILE.exists():
        try:
            previous = json.loads(AUTH_NOTICE_FILE.read_text())
        except (OSError, ValueError):
            previous = {}
        same_auth = previous.get("auth_fingerprint") == fingerprint
        last_notified_at = int(previous.get("last_notified_at") or 0)
        if same_auth and now - last_notified_at < AUTH_NOTICE_INTERVAL_SECONDS:
            return
    AUTH_NOTICE_FILE.parent.mkdir(exist_ok=True)
    AUTH_NOTICE_FILE.write_text(json.dumps({
        "auth_fingerprint": fingerprint,
        "last_notified_at": now,
    }) + "\n")
    message = "已打开公众号登录页；扫码后运行桌面续期工具"
    subprocess.run(
        [
            "osascript", "-e",
            f'display notification "{message}" with title "知识库公众号登录已失效"',
        ],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        ["open", "https://mp.weixin.qq.com/"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print("公众号登录态失效：请运行 scripts/refresh_wechat_auth.command")


def handle_command_result(code: int) -> int:
    if code == AUTH_EXPIRED_EXIT:
        notify_auth_expired()
    return code


def main() -> int:
    LOCK_FILE.parent.mkdir(exist_ok=True)
    with LOCK_FILE.open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("daily update 正在运行,本轮补抓跳过")
            return 0

        if backfill_pending():
            before = MANIFEST.stat().st_size if MANIFEST.exists() else 0
            code = run_command(
                [UV, "run", "wechat_mp.py", "backfill", "--max-pages", "2"],
                timeout=900,
            )
            if code != 0:
                return handle_command_result(code)
            after = MANIFEST.stat().st_size if MANIFEST.exists() else 0
            if after > before:
                code = run_command([UV, "run", "crawl.py"], timeout=3600)
                if code != 0:
                    return code
                return run_command([UV, "run", "build_index.py"], timeout=3600)
            return 0

        return handle_command_result(
            run_command([UV, "run", "wechat_mp.py", "poll"], timeout=1800)
        )


if __name__ == "__main__":
    raise SystemExit(main())
