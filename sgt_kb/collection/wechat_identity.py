# /// script
# requires-python = ">=3.10"
# dependencies = ["requests", "beautifulsoup4", "lxml", "markdownify"]
# ///
"""Resolve a WeChat account identity from a public article and Wayback snapshots."""
from __future__ import annotations

import argparse
import html
import json
import re
import time
from dataclasses import asdict, dataclass
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup

from sgt_kb.collection.crawl import safe_get

CDX_API = "https://web.archive.org/cdx/search/cdx"
ARCHIVE_HOSTS = {"web.archive.org"}
STABLE_QUERY_FIELDS = {"__biz", "mid", "idx", "sn"}
MAX_HTML_BYTES = 5 * 1024 * 1024
MAX_CDX_BYTES = 16 * 1024 * 1024
MAX_SNAPSHOTS = 8
BIZ_PATTERN = re.compile(r"^[A-Za-z0-9+/]{8,}={0,2}$")


class IdentityResolutionError(RuntimeError):
    pass


@dataclass(frozen=True)
class WechatIdentity:
    account: str
    biz_info: str
    seed_url: str
    timestamp: str


def normalize_seed_url(value: str) -> str:
    parts = urlsplit(html.unescape(value.strip()))
    if parts.scheme not in {"http", "https"} or parts.hostname != "mp.weixin.qq.com":
        raise ValueError("只支持公开的 mp.weixin.qq.com 文章链接")
    if parts.path != "/s" and not parts.path.startswith("/s/"):
        raise ValueError("不是微信公众号文章路径")
    if parts.path.startswith("/s/"):
        if not parts.path.removeprefix("/s/") or "/" in parts.path.removeprefix("/s/"):
            raise ValueError("公众号文章短链接格式错误")
        return urlunsplit(("https", "mp.weixin.qq.com", parts.path, "", ""))
    query = [
        (key, item)
        for key, item in parse_qsl(parts.query, keep_blank_values=False)
        if key in STABLE_QUERY_FIELDS
    ]
    values = dict(query)
    if not values.get("__biz") or not values.get("mid"):
        raise ValueError("长链接缺少稳定的 __biz/mid 参数")
    return urlunsplit(("https", "mp.weixin.qq.com", "/s", urlencode(query), ""))


def extract_identity_from_html(source: str, seed_url: str, timestamp: str) -> WechatIdentity:
    decoded = html.unescape(source)
    biz = ""
    for pattern in (
        r"\bvar\s+biz\s*=\s*(?:[\"']{2}\s*\|\|\s*)?[\"']([^\"']+)",
        r"\bvar\s+appuin\s*=\s*[\"']([^\"']+)",
        r"(?:[?&]|&amp;)__biz=([A-Za-z0-9+/=]+)",
    ):
        match = re.search(pattern, decoded)
        if match and BIZ_PATTERN.fullmatch(match.group(1)):
            biz = match.group(1)
            break
    if not biz:
        raise IdentityResolutionError("归档页面缺少有效 biz")

    account = ""
    for pattern in (
        r"\bvar\s+nickname\s*=\s*[\"']([^\"']+)",
        r"\bnickname\s*=\s*htmlDecode\(\s*[\"']([^\"']+)",
    ):
        match = re.search(pattern, decoded)
        if match:
            account = html.unescape(match.group(1)).strip()
            break
    if not account:
        node = BeautifulSoup(source, "lxml").select_one("#js_name")
        account = node.get_text(strip=True) if node else ""
    if not account:
        raise IdentityResolutionError("归档页面缺少公众号名称")
    return WechatIdentity(account=account, biz_info=biz, seed_url=seed_url, timestamp=timestamp)


def discover_seed_timestamps(
    seed_url: str, session: requests.Session, max_snapshots: int = MAX_SNAPSHOTS,
) -> list[str]:
    params = [
        ("url", f"{seed_url}*"),
        ("output", "json"),
        ("fl", "timestamp"),
        ("filter", "statuscode:200"),
        ("filter", "mimetype:text/html"),
        ("collapse", "digest"),
        ("limit", str(max_snapshots)),
    ]
    prepared_url = requests.Request("GET", CDX_API, params=params).prepare().url
    if not prepared_url:
        raise IdentityResolutionError("Wayback CDX 查询地址构造失败")
    payload = None
    for attempt in range(3):
        response = None
        try:
            response = safe_get(
                prepared_url, timeout=90, allowed_hosts=ARCHIVE_HOSTS,
                session=session, stream=True,
            )
        except requests.RequestException as exc:
            if attempt == 2:
                raise IdentityResolutionError("Wayback CDX 查询失败") from exc
            time.sleep(2 ** attempt)
            continue
        except ValueError as exc:
            raise IdentityResolutionError("Wayback CDX 查询被安全策略拒绝") from exc
        if response.status_code in {429, 503}:
            retry_after = response.headers.get("Retry-After", "")
            delay = int(retry_after) if retry_after.isdigit() else 2 ** attempt
            response.close()
            response = None
            time.sleep(min(delay, 30))
            continue
        try:
            response.raise_for_status()
            length = response.headers.get("Content-Length", "").strip()
            if length.isdigit() and int(length) > MAX_CDX_BYTES:
                raise IdentityResolutionError("Wayback CDX 响应超过大小限制")
            chunks: list[bytes] = []
            total = 0
            for chunk in response.iter_content(chunk_size=64 * 1024):
                if not chunk:
                    continue
                total += len(chunk)
                if total > MAX_CDX_BYTES:
                    raise IdentityResolutionError("Wayback CDX 响应超过大小限制")
                chunks.append(chunk)
            payload = json.loads(b"".join(chunks).decode("utf-8-sig"))
            break
        except IdentityResolutionError:
            raise
        except (requests.RequestException, ValueError, UnicodeError) as exc:
            raise IdentityResolutionError("Wayback CDX 查询失败") from exc
        finally:
            if response is not None:
                response.close()
    if payload is None:
        raise IdentityResolutionError("Wayback CDX 查询重试耗尽")
    if isinstance(payload, dict):
        raise IdentityResolutionError("Wayback CDX 返回错误对象")
    if not payload or not isinstance(payload[0], list) or "timestamp" not in payload[0]:
        return []
    position = payload[0].index("timestamp")
    timestamps = {
        str(row[position]) for row in payload[1:]
        if isinstance(row, list) and len(row) > position
        and re.fullmatch(r"\d{14}", str(row[position]))
    }
    return sorted(timestamps, reverse=True)[:max_snapshots]


def read_snapshot_html(url: str, session: requests.Session) -> str:
    response = None
    try:
        response = safe_get(
            url, timeout=60, allowed_hosts=ARCHIVE_HOSTS,
            session=session, stream=True,
        )
        response.raise_for_status()
        length = response.headers.get("Content-Length", "")
        if length.isdigit() and int(length) > MAX_HTML_BYTES:
            raise IdentityResolutionError("归档页面超过大小限制")
        chunks: list[bytes] = []
        total = 0
        for chunk in response.iter_content(chunk_size=64 * 1024):
            if not chunk:
                continue
            total += len(chunk)
            if total > MAX_HTML_BYTES:
                raise IdentityResolutionError("归档页面超过大小限制")
            chunks.append(chunk)
        return b"".join(chunks).decode(response.encoding or "utf-8", errors="replace")
    except (requests.RequestException, ValueError) as exc:
        raise IdentityResolutionError("Wayback 快照读取失败") from exc
    finally:
        if response is not None:
            response.close()


def resolve_article_identity(
    value: str,
    expected_account: str = "",
    session: requests.Session | None = None,
) -> WechatIdentity:
    seed_url = normalize_seed_url(value)
    owns_session = session is None
    client = session or requests.Session()
    client.headers.update({"User-Agent": "sgt-kb-wechat-identity/1.0"})
    try:
        timestamps = discover_seed_timestamps(seed_url, client)
        if not timestamps:
            raise IdentityResolutionError("Wayback 没有该文章的归档快照")
        last_error: IdentityResolutionError | None = None
        for timestamp in timestamps:
            archive_url = f"https://web.archive.org/web/{timestamp}id_/{seed_url}"
            try:
                identity = extract_identity_from_html(
                    read_snapshot_html(archive_url, client), seed_url, timestamp,
                )
            except IdentityResolutionError as exc:
                last_error = exc
                continue
            if expected_account and identity.account != expected_account:
                last_error = IdentityResolutionError("归档公众号名称与目标不一致")
                continue
            return identity
        raise last_error or IdentityResolutionError("归档快照无法解析公众号身份")
    finally:
        if owns_session:
            client.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--account", default="")
    args = parser.parse_args()
    try:
        identity = resolve_article_identity(args.url, args.account)
    except (ValueError, IdentityResolutionError) as exc:
        print(json.dumps({"status": "unresolved", "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"status": "resolved", **asdict(identity)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
