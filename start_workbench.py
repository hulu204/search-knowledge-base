#!/usr/bin/env python3
"""Start the local SGT KB API and browser workbench together."""

from __future__ import annotations

import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path


BASE = Path(__file__).resolve().parent
WEB = BASE / "workbench"
URL = "http://localhost:3917"


def main() -> int:
    if not (WEB / "node_modules" / ".bin" / "vinext").exists():
        print("首次使用请先执行：")
        print(f"  cd '{WEB}' && npm install")
        return 1

    processes: list[subprocess.Popen[bytes]] = []

    def stop(*_: object) -> None:
        for process in processes:
            if process.poll() is None:
                process.terminate()
        for process in processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    try:
        processes.append(
            subprocess.Popen(
                ["uv", "run", "--script", str(BASE / "workbench_api.py")],
                cwd=BASE,
            )
        )
        processes.append(
            subprocess.Popen(["npm", "run", "dev"], cwd=WEB)
        )
        for _ in range(240):
            exited = next(
                (process for process in processes if process.poll() is not None),
                None,
            )
            if exited is not None:
                print(f"启动失败，子进程退出码：{exited.returncode}")
                return exited.returncode or 1
            try:
                with urllib.request.urlopen(URL, timeout=0.5) as response:
                    if response.status == 200:
                        break
            except (urllib.error.URLError, TimeoutError):
                time.sleep(0.25)
        else:
            print(f"启动超时，工作台未能访问：{URL}")
            return 1

        webbrowser.open(URL)
        print(f"工作台已启动：{URL}")
        print("按 Ctrl-C 同时停止 API 和前端。")

        while all(process.poll() is None for process in processes):
            time.sleep(0.5)
        return next(
            (process.returncode or 1 for process in processes if process.poll() is not None),
            0,
        )
    finally:
        stop()


if __name__ == "__main__":
    sys.exit(main())
