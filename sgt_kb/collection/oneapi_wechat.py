# /// script
# requires-python = ">=3.10"
# dependencies = ["requests", "beautifulsoup4", "lxml", "markdownify"]
# ///
"""Enumerate WeChat account articles since 2020 through a metered OneAPI feed."""
from __future__ import annotations

import argparse
import csv
import fcntl
import json
import math
import re
import sqlite3
import stat
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

import requests

from sgt_kb.collection.crawl import validate_public_url
from sgt_kb.collection.ingest_url import ingest, normalize_url
from sgt_kb.collection.wechat_mp import title_matches

from sgt_kb.paths import ROOT

BASE = ROOT
TARGETS_FILE = BASE / "wayback_targets.csv"
STATE_DB = BASE / "ingestion" / "oneapi_wechat.sqlite"
LOCK_FILE = BASE / "ingestion" / "oneapi_wechat.lock"
KEY_FILE = BASE / ".oneapi_key"
INDEX_DIRTY_FILE = BASE / "ingestion" / "oneapi_index_dirty"
INDEX_DB = BASE / "index" / "kb.sqlite"
MANIFEST = BASE / "crawl_manifest.csv"
ENDPOINT = "https://api.getoneapi.com/api/wechat-mp-v2/fetch_mp_article_list"
ALLOWED_HOSTS = {"api.getoneapi.com"}
SHANGHAI = ZoneInfo("Asia/Shanghai")
CUTOFF_TIMESTAMP = int(datetime(2020, 1, 1, tzinfo=SHANGHAI).timestamp())
PAGE_PRICE_YUAN = 0.15
MAX_RESPONSE_BYTES = 5 * 1024 * 1024
MAX_OFFSET_LENGTH = 4096
GHID_PATTERN = re.compile(r"^gh_[0-9a-f]{12}$")
OFFSET_PATTERN = re.compile(r"^[A-Za-z0-9_+/=-]+$")


class OneApiError(RuntimeError):
    pass


class OneApiKeyError(OneApiError):
    pass


class OneApiBalanceExhausted(OneApiError):
    pass


@dataclass(frozen=True)
class Target:
    account: str
    company: str
    ghid: str


@dataclass(frozen=True)
class Article:
    url: str
    title: str
    digest: str
    create_time: int


@dataclass(frozen=True)
class Page:
    articles: tuple[Article, ...]
    next_offset: str
    is_end: bool


def read_api_key(path: Path = KEY_FILE) -> str:
    try:
        info = path.stat()
        if stat.S_IMODE(info.st_mode) & 0o077:
            raise OneApiKeyError("OneAPI Key 文件权限必须为 0600")
        raw = path.read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise OneApiKeyError("缺少 OneAPI Key 文件") from exc
    except OSError as exc:
        raise OneApiKeyError("无法读取 OneAPI Key 文件") from exc
    if raw.startswith("{"):
        try:
            payload = json.loads(raw)
        except ValueError as exc:
            raise OneApiKeyError("OneAPI Key 文件格式无效") from exc
        raw = next((
            str(payload[name]).strip()
            for name in ("api_key", "apikey", "key", "token")
            if payload.get(name)
        ), "")
    if not 10 <= len(raw) <= 512 or any(char.isspace() for char in raw):
        raise OneApiKeyError("OneAPI Key 文件格式无效")
    return raw


def load_targets(path: Path = TARGETS_FILE) -> list[Target]:
    try:
        with path.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    except OSError as exc:
        raise OneApiError("无法读取公众号目标清单") from exc
    targets: list[Target] = []
    seen_accounts = set()
    seen_ghids = set()
    for row in rows:
        account = (row.get("account") or "").strip()
        company = (row.get("company") or "").strip()
        ghid = (row.get("ghid") or "").strip()
        if not account or not company or not GHID_PATTERN.fullmatch(ghid):
            raise OneApiError(f"目标清单身份字段无效: {account or 'unknown'}")
        if account in seen_accounts or ghid in seen_ghids:
            raise OneApiError("目标清单存在重复 account 或 ghid")
        seen_accounts.add(account)
        seen_ghids.add(ghid)
        targets.append(Target(account, company, ghid))
    if not targets:
        raise OneApiError("公众号目标清单为空")
    return targets


def _read_response_json(response: requests.Response, key: str) -> dict:
    length = response.headers.get("Content-Length", "").strip()
    if length.isdigit() and int(length) > MAX_RESPONSE_BYTES:
        raise OneApiError("OneAPI 响应超过大小限制")
    chunks: list[bytes] = []
    total = 0
    for chunk in response.iter_content(chunk_size=64 * 1024):
        if not chunk:
            continue
        total += len(chunk)
        if total > MAX_RESPONSE_BYTES:
            raise OneApiError("OneAPI 响应超过大小限制")
        chunks.append(chunk)
    try:
        payload = json.loads(b"".join(chunks).decode("utf-8-sig"))
    except (UnicodeError, ValueError) as exc:
        raise OneApiError("OneAPI 返回了无效 JSON") from exc
    if not isinstance(payload, dict):
        raise OneApiError("OneAPI 返回结构无效")
    if key in json.dumps(payload, ensure_ascii=False):
        raise OneApiError("OneAPI 响应意外包含访问凭据")
    return payload


def parse_page(payload: dict) -> Page:
    code = payload.get("code")
    message = str(payload.get("message") or "")[:200]
    if code == 301 and "insufficient balance" in message.lower():
        raise OneApiBalanceExhausted("OneAPI 余额不足")
    if code != 200:
        raise OneApiError(f"OneAPI 业务失败: code={code}")
    data = payload.get("data")
    if not isinstance(data, dict) or not isinstance(data.get("articles"), list):
        raise OneApiError("OneAPI 文章列表结构无效")
    if len(data["articles"]) > 100:
        raise OneApiError("OneAPI 单页文章数异常")
    articles = []
    for item in data["articles"]:
        if not isinstance(item, dict):
            continue
        raw_url = str(item.get("url") or "")
        parts = urlsplit(raw_url)
        if parts.hostname != "mp.weixin.qq.com" or (
            parts.path != "/s" and not parts.path.startswith("/s/")
        ):
            continue
        try:
            url = normalize_url(raw_url)
            created = int(item.get("create_time") or 0)
        except (TypeError, ValueError):
            continue
        if created <= 0:
            continue
        articles.append(Article(
            url=url,
            title=str(item.get("title") or "")[:500].strip(),
            digest=str(item.get("digest") or "")[:2000].strip(),
            create_time=created,
        ))
    offset = str(data.get("next_offset") or "")
    is_end = bool(int(data.get("is_end") or 0))
    if not is_end and (
        not offset or len(offset) > MAX_OFFSET_LENGTH
        or not OFFSET_PATTERN.fullmatch(offset)
    ):
        raise OneApiError("OneAPI 分页游标无效")
    return Page(tuple(articles), offset, is_end)


class OneApiClient:
    def __init__(self, key: str, session: requests.Session | None = None):
        self.key = key
        self.session = session or requests.Session()
        self.owns_session = session is None

    def close(self) -> None:
        if self.owns_session:
            self.session.close()

    def fetch_page(self, ghid: str, offset: str = "") -> Page:
        if not GHID_PATTERN.fullmatch(ghid):
            raise OneApiError("ghid 格式无效")
        if offset and (
            len(offset) > MAX_OFFSET_LENGTH or not OFFSET_PATTERN.fullmatch(offset)
        ):
            raise OneApiError("分页游标格式无效")
        validate_public_url(ENDPOINT, ALLOWED_HOSTS)
        response = None
        try:
            response = self.session.post(
                ENDPOINT,
                headers={
                    "Authorization": f"Bearer {self.key}",
                    "Content-Type": "application/json",
                },
                json={
                    "username": ghid,
                    "page_size": 20,
                    "offset": offset,
                    "item_show_type": 0,
                    "raw": False,
                },
                timeout=60,
                allow_redirects=False,
                stream=True,
            )
            if response.is_redirect or response.is_permanent_redirect:
                raise OneApiError("OneAPI 不应返回重定向")
            response.raise_for_status()
            return parse_page(_read_response_json(response, self.key))
        except OneApiError:
            raise
        except (requests.RequestException, ValueError) as exc:
            raise OneApiError("OneAPI 网络请求失败") from exc
        finally:
            if response is not None:
                response.close()


def connect_state(path: Path = STATE_DB) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            account TEXT PRIMARY KEY,
            company TEXT NOT NULL,
            ghid TEXT NOT NULL UNIQUE,
            offset TEXT NOT NULL DEFAULT '',
            done INTEGER NOT NULL DEFAULT 0,
            oldest_seen INTEGER NOT NULL DEFAULT 0,
            calls INTEGER NOT NULL DEFAULT 0,
            last_page_at TEXT NOT NULL DEFAULT '',
            last_poll_at TEXT NOT NULL DEFAULT '',
            last_error TEXT NOT NULL DEFAULT ''
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            url TEXT PRIMARY KEY,
            account TEXT NOT NULL,
            company TEXT NOT NULL,
            title TEXT NOT NULL,
            digest TEXT NOT NULL,
            create_time INTEGER NOT NULL,
            status TEXT NOT NULL,
            error TEXT NOT NULL DEFAULT '',
            attempts INTEGER NOT NULL DEFAULT 0,
            next_attempt_at TEXT NOT NULL DEFAULT '',
            discovered_at TEXT NOT NULL
        )
    """)
    connection.commit()
    return connection


def sync_targets(connection: sqlite3.Connection, targets: list[Target]) -> None:
    with connection:
        for target in targets:
            connection.execute("""
                INSERT INTO accounts(account, company, ghid)
                VALUES (?, ?, ?)
                ON CONFLICT(account) DO UPDATE SET
                    company=excluded.company,
                    ghid=excluded.ghid
            """, (target.account, target.company, target.ghid))


def _page_done(page: Page, cutoff: int) -> bool:
    timestamps = [article.create_time for article in page.articles]
    return page.is_end or bool(timestamps and max(timestamps) < cutoff)


def checkpoint_page(
    connection: sqlite3.Connection,
    target: Target,
    page: Page,
    cutoff: int = CUTOFF_TIMESTAMP,
    mode: str = "backfill",
) -> dict[str, int | bool]:
    now = datetime.now(SHANGHAI).isoformat(timespec="seconds")
    eligible = [article for article in page.articles if article.create_time >= cutoff]
    done = _page_done(page, cutoff)
    with connection:
        for article in eligible:
            status = "pending" if title_matches(article.title) else "irrelevant"
            connection.execute("""
                INSERT INTO articles(
                    url, account, company, title, digest, create_time,
                    status, discovered_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    title=excluded.title,
                    digest=excluded.digest,
                    create_time=excluded.create_time
            """, (
                article.url, target.account, target.company,
                article.title, article.digest, article.create_time, status, now,
            ))
        if mode == "backfill":
            oldest = min((article.create_time for article in page.articles), default=0)
            connection.execute("""
                UPDATE accounts SET
                    offset=?, done=?,
                    oldest_seen=CASE
                        WHEN oldest_seen=0 THEN ?
                        WHEN ?=0 THEN oldest_seen
                        ELSE MIN(oldest_seen, ?)
                    END,
                    calls=calls+1, last_page_at=?, last_error=''
                WHERE account=?
            """, (
                page.next_offset, int(done), oldest, oldest, oldest,
                now, target.account,
            ))
        else:
            connection.execute("""
                UPDATE accounts SET
                    calls=calls+1, last_poll_at=?, last_error=''
                WHERE account=?
            """, (now, target.account))
    return {"stored": len(eligible), "done": done}


def record_account_error(
    connection: sqlite3.Connection, account: str, error: str,
) -> None:
    now = datetime.now(SHANGHAI).isoformat(timespec="seconds")
    with connection:
        connection.execute(
            "UPDATE accounts SET last_error=?, last_page_at=? WHERE account=?",
            (error[:100], now, account),
        )


def _page_budget(max_pages: int, max_cost_yuan: float) -> int:
    if not 1 <= max_pages <= 500 or max_cost_yuan < PAGE_PRICE_YUAN:
        raise OneApiError("页数或成本上限无效")
    return min(max_pages, math.floor((max_cost_yuan + 1e-9) / PAGE_PRICE_YUAN))


def backfill(
    max_pages: int,
    max_cost_yuan: float,
    account_filter: str = "",
    key_file: Path = KEY_FILE,
    state_db: Path = STATE_DB,
    targets_file: Path = TARGETS_FILE,
) -> dict[str, int | float | bool]:
    budget = _page_budget(max_pages, max_cost_yuan)
    targets = load_targets(targets_file)
    by_account = {target.account: target for target in targets}
    if account_filter and account_filter not in by_account:
        raise OneApiError("未找到指定公众号")
    connection = connect_state(state_db)
    sync_targets(connection, targets)
    client = OneApiClient(read_api_key(key_file))
    requests_made = successful_calls = stored = completed = 0
    balance_exhausted = False
    failed_accounts: set[str] = set()
    try:
        while requests_made < budget:
            params: list[object] = []
            query = """
                SELECT account, offset FROM accounts
                WHERE done=0
            """
            if account_filter:
                query += " AND account=?"
                params.append(account_filter)
            query += " ORDER BY last_page_at, account"
            rows = connection.execute(query, params).fetchall()
            row = next((item for item in rows if item[0] not in failed_accounts), None)
            if row is None:
                break
            account, offset = row
            target = by_account[account]
            requests_made += 1
            try:
                page = client.fetch_page(target.ghid, offset)
            except OneApiBalanceExhausted:
                record_account_error(connection, account, "balance_exhausted")
                balance_exhausted = True
                break
            except OneApiError as exc:
                record_account_error(connection, account, type(exc).__name__)
                failed_accounts.add(account)
                continue
            outcome = checkpoint_page(connection, target, page)
            successful_calls += 1
            stored += int(outcome["stored"])
            completed += int(bool(outcome["done"]))
    finally:
        client.close()
        connection.close()
    return {
        "requests": requests_made,
        "successful_calls": successful_calls,
        "stored": stored,
        "accounts_completed": completed,
        "balance_exhausted": balance_exhausted,
        "estimated_cost_upper_bound_yuan": round(
            requests_made * PAGE_PRICE_YUAN, 2
        ),
    }


def poll_latest(
    max_cost_yuan: float,
    key_file: Path = KEY_FILE,
    state_db: Path = STATE_DB,
    targets_file: Path = TARGETS_FILE,
) -> dict[str, int | float | bool]:
    targets = load_targets(targets_file)
    from sgt_kb.collection.rss_poll import FEEDS
    targets = [target for target in targets if target.account not in FEEDS]
    budget = _page_budget(len(targets), max_cost_yuan)
    connection = connect_state(state_db)
    sync_targets(connection, targets)
    client = OneApiClient(read_api_key(key_file))
    requests_made = successful_calls = stored = 0
    balance_exhausted = False
    try:
        for target in targets[:budget]:
            requests_made += 1
            try:
                page = client.fetch_page(target.ghid)
            except OneApiBalanceExhausted:
                record_account_error(connection, target.account, "balance_exhausted")
                balance_exhausted = True
                break
            except OneApiError as exc:
                record_account_error(connection, target.account, type(exc).__name__)
                continue
            outcome = checkpoint_page(connection, target, page, mode="poll")
            successful_calls += 1
            stored += int(outcome["stored"])
    finally:
        client.close()
        connection.close()
    return {
        "requests": requests_made,
        "successful_calls": successful_calls,
        "stored": stored,
        "balance_exhausted": balance_exhausted,
        "estimated_cost_upper_bound_yuan": round(
            requests_made * PAGE_PRICE_YUAN, 2
        ),
    }


def mark_index_dirty() -> None:
    INDEX_DIRTY_FILE.parent.mkdir(parents=True, exist_ok=True)
    INDEX_DIRTY_FILE.write_text(
        datetime.now(SHANGHAI).isoformat(timespec="seconds") + "\n"
    )


def index_needs_rebuild() -> bool:
    if INDEX_DIRTY_FILE.exists() or not INDEX_DB.exists():
        return True
    return MANIFEST.exists() and MANIFEST.stat().st_mtime_ns > INDEX_DB.stat().st_mtime_ns


def clear_index_dirty() -> None:
    INDEX_DIRTY_FILE.unlink(missing_ok=True)


def ingest_pending(
    max_articles: int = 20,
    state_db: Path = STATE_DB,
    defer_index: bool = False,
) -> dict[str, int]:
    if not 1 <= max_articles <= 200:
        raise OneApiError("入库数量上限无效")
    connection = connect_state(state_db)
    now = datetime.now(SHANGHAI)
    rows = connection.execute("""
        SELECT url, company, title, create_time, attempts
        FROM articles
        WHERE status='pending'
           OR (status='failed' AND attempts < 3 AND next_attempt_at <= ?)
        ORDER BY create_time DESC
        LIMIT ?
    """, (now.isoformat(timespec="seconds"), max_articles)).fetchall()
    counts = {"ingested": 0, "existing": 0, "failed": 0, "body_missing": 0}
    for url, company, title, created, attempts in rows:
        date = datetime.fromtimestamp(created, SHANGHAI).strftime("%Y-%m-%d")
        try:
            mark_index_dirty()
            result = ingest(
                url,
                company=company,
                title=title,
                date=date,
                origin="oneapi-wechat-list",
                skip_index=True,
            )
            ingest_status = result.get("status")
            if ingest_status not in {
                "ingested", "existing_url", "existing_content",
            }:
                raise OneApiError("入库器返回未知状态")
        except Exception as exc:
            attempts += 1
            terminal = attempts >= 3
            status = "body_missing" if terminal else "failed"
            next_attempt = (now + timedelta(days=1)).isoformat(timespec="seconds")
            with connection:
                connection.execute("""
                    UPDATE articles SET
                        status=?, error=?, attempts=?, next_attempt_at=?
                    WHERE url=?
                """, (status, type(exc).__name__, attempts, next_attempt, url))
            counts[status] += 1
            continue
        status = "ingested" if ingest_status == "ingested" else "existing"
        with connection:
            connection.execute(
                "UPDATE articles SET status=?, error='' WHERE url=?",
                (status, url),
            )
        counts[status] += 1
    connection.close()
    if not defer_index and index_needs_rebuild():
        subprocess.run(
            [sys.executable, "-m", "sgt_kb", "build-index"], cwd=BASE, check=True,
        )
        clear_index_dirty()
    return counts


def status(state_db: Path = STATE_DB) -> dict:
    connection = connect_state(state_db)
    accounts = {
        "total": connection.execute("SELECT COUNT(*) FROM accounts").fetchone()[0],
        "done": connection.execute("SELECT COUNT(*) FROM accounts WHERE done=1").fetchone()[0],
        "calls": connection.execute("SELECT COALESCE(SUM(calls),0) FROM accounts").fetchone()[0],
    }
    articles = dict(connection.execute(
        "SELECT status, COUNT(*) FROM articles GROUP BY status"
    ).fetchall())
    connection.close()
    return {"accounts": accounts, "articles": articles}


class oneapi_lock:
    def __enter__(self):
        LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.handle = LOCK_FILE.open("a+")
        fcntl.flock(self.handle, fcntl.LOCK_EX)
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.handle.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    backfill_parser = sub.add_parser("backfill")
    backfill_parser.add_argument("--max-pages", type=int, default=20)
    backfill_parser.add_argument("--max-cost-yuan", type=float, default=3.0)
    backfill_parser.add_argument("--account", default="")
    poll_parser = sub.add_parser("poll")
    poll_parser.add_argument("--max-cost-yuan", type=float, default=2.0)
    ingest_parser = sub.add_parser("ingest")
    ingest_parser.add_argument("--max-articles", type=int, default=20)
    ingest_parser.add_argument("--defer-index", action="store_true")
    sub.add_parser("status")
    args = parser.parse_args()
    try:
        with oneapi_lock():
            if args.command == "backfill":
                result = backfill(
                    args.max_pages, args.max_cost_yuan, args.account,
                )
            elif args.command == "poll":
                result = poll_latest(args.max_cost_yuan)
            elif args.command == "ingest":
                result = ingest_pending(args.max_articles, defer_index=args.defer_index)
            else:
                result = status()
    except OneApiKeyError as exc:
        print(json.dumps({"status": "key_error", "message": str(exc)}, ensure_ascii=False))
        return 76
    except OneApiError as exc:
        print(json.dumps({"status": "failed", "message": str(exc)}, ensure_ascii=False))
        return 1
    except (OSError, sqlite3.Error):
        print(json.dumps({
            "status": "failed", "message": "OneAPI 本地状态读写失败",
        }, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False))
    if isinstance(result, dict) and result.get("balance_exhausted"):
        return 75
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
