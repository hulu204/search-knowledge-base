# /// script
# requires-python = ">=3.10"
# dependencies = ["requests", "beautifulsoup4", "lxml", "markdownify"]
# ///
"""Enumerate and ingest WeChat public-account articles through WeRead."""
from __future__ import annotations

import argparse
import csv
import html
import json
import os
import re
import shlex
import stat
import subprocess
import sys
import tempfile
import time
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from sgt_kb.collection.ingest_url import ingest_html_content

from sgt_kb.paths import ROOT

BASE = ROOT
AUTH_FILE = BASE / ".weread_auth.json"
STATE_FILE = BASE / "ingestion" / "weread_state.json"
CANDIDATE_FILE = BASE / "ingestion" / "weread_candidates.csv"
DEFAULT_KEYWORDS = (
    "搜索", "检索", "召回", "排序", "向量", "知识库", "rag", "embedding",
    "vector", "vectors", "vectordbbench", "retrieval", "search", "searchcli",
    "opensearch", "diskann", "rank", "recommend", "推荐系统",
)
MAX_RESPONSE_BYTES = 10 * 1024 * 1024


@dataclass(frozen=True)
class WeReadAuth:
    cookie: str
    user_agent: str
    x_wrpa_0: str


def parse_curl(text: str) -> WeReadAuth:
    tokens = shlex.split(text.replace("\\\n", " "))
    cookie = ""
    headers: dict[str, str] = {}
    url = ""
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token in {"-b", "--cookie"} and i + 1 < len(tokens):
            cookie = tokens[i + 1]
            i += 2
            continue
        if token.startswith("--cookie="):
            cookie = token.split("=", 1)[1]
        if token in {"-H", "--header"} and i + 1 < len(tokens):
            name, sep, value = tokens[i + 1].partition(":")
            if sep:
                headers[name.strip().lower()] = value.strip()
            i += 2
            continue
        if token.startswith("https://"):
            url = token
        i += 1
    parts = urlsplit(url)
    if parts.hostname != "weread.qq.com" or parts.path != "/web/book/read":
        raise ValueError("只接受微信读书 /web/book/read cURL")
    proof = headers.get("x-wrpa-0", "")
    if not cookie or not proof:
        raise ValueError("cURL 缺少 Cookie 或 x-wrpa-0")
    return WeReadAuth(
        cookie=cookie,
        user_agent=headers.get("user-agent", "Mozilla/5.0")[:500],
        x_wrpa_0=proof,
    )


def save_auth(auth: WeReadAuth, path: Path = AUTH_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "cookie": auth.cookie,
        "user_agent": auth.user_agent,
        "x_wrpa_0": auth.x_wrpa_0,
        "captured_at": int(time.time()),
    }
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False)
            handle.write("\n")
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_auth(path: Path = AUTH_FILE) -> WeReadAuth:
    mode = path.stat().st_mode
    if not stat.S_ISREG(mode):
        raise RuntimeError("微信读书认证路径不是普通文件")
    if stat.S_IMODE(mode) & 0o077:
        raise RuntimeError("微信读书认证文件权限过宽，请设为 0600")
    data = json.loads(path.read_text(encoding="utf-8"))
    auth = WeReadAuth(
        cookie=str(data.get("cookie") or ""),
        user_agent=str(data.get("user_agent") or "Mozilla/5.0")[:500],
        x_wrpa_0=str(data.get("x_wrpa_0") or ""),
    )
    if not auth.cookie or not auth.x_wrpa_0:
        raise RuntimeError("微信读书认证文件缺少 Cookie 或 x_wrpa_0")
    return auth


class WeReadClient:
    def __init__(self, auth: WeReadAuth, info_id: str):
        self.info_id = info_id
        self.session = requests.Session()
        self.session.trust_env = False
        self.headers = {
            "Cookie": auth.cookie,
            "x-wrpa-0": auth.x_wrpa_0,
            "User-Agent": auth.user_agent,
            "Referer": f"https://weread.qq.com/web/mp/reader/{info_id}",
            "Accept": "application/json, text/plain, */*",
        }

    def get(self, path: str, params: Mapping[str, str | int]) -> requests.Response:
        response = self.session.get(
            "https://weread.qq.com" + path,
            params=params,
            headers=self.headers,
            timeout=30,
            allow_redirects=False,
            stream=True,
        )
        try:
            response.raise_for_status()
            content_length = response.headers.get("Content-Length")
            if content_length is not None:
                try:
                    declared_size = int(content_length)
                except ValueError as exc:
                    raise RuntimeError(f"微信读书响应 Content-Length 无效: {path}") from exc
                if declared_size > MAX_RESPONSE_BYTES:
                    raise RuntimeError(f"微信读书响应过大: {path}")

            body = bytearray()
            for chunk in response.iter_content(chunk_size=64 * 1024):
                if not chunk:
                    continue
                body.extend(chunk)
                if len(body) > MAX_RESPONSE_BYTES:
                    raise RuntimeError(f"微信读书响应过大: {path}")
            response._content = bytes(body)
            return response
        finally:
            response.close()

    def enumerate_articles(self, book_id: str, delay: float = 0.55) -> list[dict]:
        groups: list[dict] = []
        offset = 0
        for _ in range(100):
            data = None
            for attempt in range(4):
                data = self.get(
                    "/web/mp/articles", {"bookId": book_id, "offset": offset}
                ).json()
                if not isinstance(data, dict) or not data.get("errCode"):
                    break
                if int(data.get("errCode") or 0) != -10100 or attempt == 3:
                    raise RuntimeError(
                        f"微信读书目录接口错误 offset={offset} errCode={data.get('errCode')}"
                    )
                time.sleep(2 ** attempt)
            page = data.get("reviews", []) if isinstance(data, dict) else []
            if not page:
                break
            groups.extend(page)
            offset += len(page)
            time.sleep(delay)
        else:
            raise RuntimeError("微信读书目录分页超过安全上限")
        return flatten_groups(groups)

    def fetch_content(self, review_id: str) -> str:
        response = self.get("/web/mp/content", {"reviewId": review_id})
        if not response.text.lstrip().lower().startswith("<!doctype html"):
            raise RuntimeError("微信读书正文不是 HTML")
        return response.text


def flatten_groups(groups: list[dict]) -> list[dict]:
    articles: list[dict] = []
    seen: set[str] = set()
    for group in groups:
        for sub in group.get("subReviews", []) or []:
            review = sub.get("review", {}) or {}
            mp_info = review.get("mpInfo", {}) or {}
            review_id = sub.get("reviewId") or review.get("reviewId") or ""
            if not review_id or review_id in seen:
                continue
            seen.add(review_id)
            timestamp = int(
                mp_info.get("time")
                or review.get("createTime")
                or group.get("createTime")
                or 0
            )
            date = (
                datetime.fromtimestamp(timestamp, tz=timezone.utc).date().isoformat()
                if timestamp else ""
            )
            articles.append({
                "account": str(mp_info.get("mp_name") or ""),
                "title": html.unescape(str(mp_info.get("title") or "")).strip(),
                "date": date,
                "timestamp": timestamp,
                "review_id": str(review_id),
                "original_id": str(mp_info.get("originalId") or ""),
                "read_num": int(mp_info.get("readNum") or 0),
                "like_num": int(mp_info.get("likeNum") or 0),
            })
    return articles


def select_candidates(
    articles: list[dict], since: str, keywords: tuple[str, ...]
) -> list[dict]:
    lowered = tuple(
        stripped.lower()
        for keyword in keywords
        if (stripped := keyword.strip())
    )
    if not lowered:
        raise ValueError("关键词不能为空")

    def matches(title: str) -> bool:
        normalized = title.lower()
        for keyword in lowered:
            if keyword.isascii():
                pattern = rf"(?<![a-z0-9]){re.escape(keyword)}(?![a-z0-9])"
                if re.search(pattern, normalized):
                    return True
            elif keyword in normalized:
                return True
        return False

    return [
        article for article in articles
        if article["date"] >= since
        and matches(article["title"])
    ]


def parse_content_page(raw_html: str) -> tuple[str, str, str]:
    soup = BeautifulSoup(raw_html, "lxml")
    content = soup.select_one("#js_content")
    if content is None:
        raise RuntimeError("正文缺少 #js_content")
    meta = soup.find("meta", attrs={"property": "og:url"})
    url = html.unescape(str(meta.get("content") if isinstance(meta, Tag) else "")).strip()
    parts = urlsplit(url)
    if parts.scheme != "https" or parts.hostname != "mp.weixin.qq.com":
        raise RuntimeError("正文缺少可信公众号原文 URL")
    title_node = soup.select_one("#activity-name") or soup.find("h1")
    title = title_node.get_text(" ", strip=True) if title_node else ""
    return url, title, str(content)


def write_candidates(rows: list[dict], path: Path = CANDIDATE_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "account", "title", "date", "timestamp", "review_id", "original_id",
        "read_num", "like_num",
    ]
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def update_state(payload: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=STATE_FILE.name + ".", dir=STATE_FILE.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, STATE_FILE)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_state() -> dict:
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    if not isinstance(data, dict):
        raise TypeError("微信读书同步状态格式无效")
    return data


def sync(args: argparse.Namespace) -> dict:
    index_dirty = bool(load_state().get("index_dirty", False))
    client = WeReadClient(load_auth(), args.info_id)
    articles = client.enumerate_articles(args.book_id, delay=args.delay)
    keywords = tuple(args.keyword or DEFAULT_KEYWORDS)
    candidates = select_candidates(articles, args.since, keywords)
    write_candidates(candidates)
    result = {
        "account": args.account,
        "articles": len(articles),
        "since": args.since,
        "candidates": len(candidates),
        "ingested": 0,
        "existing": 0,
        "failed": 0,
    }
    if args.dry_run:
        update_state({
            **result,
            "updated_at": int(time.time()),
            "dry_run": True,
            "index_dirty": index_dirty,
        })
        return result

    for candidate in candidates:
        try:
            raw_html = client.fetch_content(candidate["review_id"])
            url, page_title, content_html = parse_content_page(raw_html)
            dirty_before_attempt = index_dirty
            index_dirty = True
            update_state({
                **result,
                "updated_at": int(time.time()),
                "dry_run": False,
                "index_dirty": True,
            })
            ingest_result = ingest_html_content(
                url=url,
                content_html=content_html,
                company=args.account,
                title=page_title or candidate["title"],
                tag=args.tag,
                date=candidate["date"],
                origin="weread-mp",
                skip_images=args.skip_images,
                skip_index=True,
            )
            if ingest_result["status"] == "ingested":
                result["ingested"] += 1
                update_state({
                    **result,
                    "updated_at": int(time.time()),
                    "dry_run": False,
                    "index_dirty": True,
                })
            else:
                result["existing"] += 1
                index_dirty = dirty_before_attempt
        # 单篇失败不得中断整批；记录最小上下文后继续处理下一篇。
        except Exception as exc:  # noqa: BLE001
            result["failed"] += 1
            print(json.dumps({
                "status": "failed",
                "review_id": candidate["review_id"],
                "title": candidate["title"],
                "error": f"{type(exc).__name__}: {exc}",
            }, ensure_ascii=False), file=sys.stderr)
        time.sleep(args.delay)
    if index_dirty and not args.skip_index:
        subprocess.run([sys.executable, "-m", "sgt_kb", "build-index"], cwd=BASE, check=True)
        index_dirty = False
    update_state({
        **result,
        "updated_at": int(time.time()),
        "dry_run": False,
        "index_dirty": index_dirty,
    })
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    auth_parser = subparsers.add_parser("auth-update")
    auth_parser.add_argument("curl_file", type=Path)

    sync_parser = subparsers.add_parser("sync")
    sync_parser.add_argument("--account", required=True)
    sync_parser.add_argument("--info-id", required=True)
    sync_parser.add_argument("--book-id", required=True)
    sync_parser.add_argument("--since", default="2024-01-01")
    sync_parser.add_argument("--tag", default="搜索/RAG")
    sync_parser.add_argument("--keyword", action="append")
    sync_parser.add_argument("--delay", type=float, default=0.7)
    sync_parser.add_argument("--dry-run", action="store_true")
    sync_parser.add_argument("--skip-images", action="store_true")
    sync_parser.add_argument("--skip-index", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "auth-update":
        save_auth(parse_curl(args.curl_file.read_text(encoding="utf-8")))
        print(json.dumps({"status": "updated", "path": str(AUTH_FILE)}, ensure_ascii=False))
        return 0
    print(json.dumps(sync(args), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
