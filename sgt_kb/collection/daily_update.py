# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""知识库每日更新:回填续跑(未完成时) → 抓正文 → RSS 轮询 → 公众号 poll → 建索引。

由 launchd 每天调用(com.lcy.sgt-kb-daily),也可手动跑。fcntl 文件锁防止
与上一次未结束的运行重叠。所有步骤失败不互相阻塞,日志见 logs/daily_update.log。
"""
import fcntl
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from sgt_kb.paths import ROOT

BASE = ROOT
LOG_DIR = BASE / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOCK_FILE = BASE / "ingestion" / "daily.lock"


def log(msg: str):
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line, flush=True)


def run_step(name: str, args: list[str], timeout: int = 3600) -> bool:
    log(f"--- {name} ---")
    try:
        r = subprocess.run(args, cwd=BASE, timeout=timeout,
                           capture_output=True, text=True)
        tail = "\n".join((r.stdout + r.stderr).strip().splitlines()[-8:])
        log(tail if tail else "(无输出)")
        if r.returncode != 0:
            log(f"!! {name} 退出码 {r.returncode}")
        return r.returncode == 0
    except subprocess.TimeoutExpired:
        log(f"!! {name} 超时({timeout}s),跳过")
        return False
    except Exception as e:
        log(f"!! {name} 异常: {e}")
        return False


def backfill_pending() -> bool:
    state_file = BASE / "ingestion" / "wechat_mp_state.json"
    if not state_file.exists():
        return False
    st = json.loads(state_file.read_text())
    for acc in st.get("accounts", {}).values():
        queries = acc.get("queries") or {}
        if not queries or not all(q.get("done") for q in queries.values()):
            return True
    return False


def main():
    LOCK_FILE.parent.mkdir(exist_ok=True)
    lock = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        log("上一次运行尚未结束,跳过本次")
        return

    log("===== daily update start =====")
    if backfill_pending():
        run_step("公众号回填续跑", [sys.executable, "-m", "sgt_kb", "wechat-mp", "backfill", "--max-pages", "2"],
                 timeout=3600)
    run_step("抓取清单中未落地的正文", [sys.executable, "-m", "sgt_kb", "crawl"], timeout=7200)
    run_step("RSS 轮询", [sys.executable, "-m", "sgt_kb", "rss-poll", "--defer-index"], timeout=3600)
    run_step("英文权威源轮询(门控)", [sys.executable, "-m", "sgt_kb", "en-poll"], timeout=3600)
    run_step("Exa MCP 补充 host 候选", [sys.executable, "-m", "sgt_kb", "exa-discover"], timeout=900)
    run_step("英文候选标题自动分流", [sys.executable, "-m", "sgt_kb", "review-queue", "auto-triage"],
             timeout=900)
    run_step("入库已批准英文候选", [sys.executable, "-m", "sgt_kb", "review-queue", "ingest-approved"], timeout=3600)
    run_step("公众号增量 poll", [sys.executable, "-m", "sgt_kb", "wechat-mp", "poll"], timeout=3600)
    run_step("增量建索引", [sys.executable, "-m", "sgt_kb", "build-index"], timeout=3600)
    log("===== daily update end =====")


if __name__ == "__main__":
    main()
