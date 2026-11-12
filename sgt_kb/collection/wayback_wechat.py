# /// script
# requires-python = ">=3.10"
# dependencies = ["requests", "beautifulsoup4", "lxml", "markdownify"]
# ///
"""Discover and restore archived WeChat articles from the Wayback Machine."""
from __future__ import annotations

import argparse
import csv
import fcntl
import html
import json
import re
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests

from sgt_kb.collection.crawl import parse_weixin_html, safe_get
from sgt_kb.collection.ingest_url import ingest_body, normalize_url
from sgt_kb.collection.en_poll import classify_tag
from sgt_kb.collection.wechat_identity import (
    IdentityResolutionError,
    extract_identity_from_html,
    read_snapshot_html,
    resolve_article_identity,
)
from sgt_kb.collection.wechat_mp import title_matches
from sgt_kb.collection.wechat_public_registry import (
    PublicRegistryError,
    PublicRegistryNotFound,
    lookup_public_registry_biz,
)

from sgt_kb.paths import ROOT

BASE = ROOT
TARGETS_FILE = BASE / "wayback_targets.csv"
CANDIDATES_FILE = BASE / "ingestion" / "wayback_candidates.csv"
LOCK_FILE = BASE / "ingestion" / "wayback_candidates.lock"
MANIFEST = BASE / "crawl_manifest.csv"
INDEX_DB = BASE / "index" / "kb.sqlite"
INDEX_DIRTY_FILE = BASE / "ingestion" / "wayback_index_dirty"
DISCOVERY_STATE_FILE = BASE / "ingestion" / "wayback_discovery_state.json"
CDX_API = "https://web.archive.org/cdx/search/cdx"
ARCHIVE_HOSTS = {"web.archive.org"}
ALLOWED_QUERY_FIELDS = {"__biz", "mid", "idx", "sn"}
ARCHIVE_QUERY_FIELDS = ALLOWED_QUERY_FIELDS | {"chksm", "scene", "mpshare", "srcid"}
FIELDS = [
    "account", "company", "biz_info", "url", "timestamps", "captures_json",
    "status", "error", "attempt_cursor", "failure_rounds",
    "last_attempt_at", "next_attempt_at",
]
MAX_URL_LENGTH = 64 * 1024
MAX_UNESCAPE_DEPTH = 32
MAX_CDX_BYTES = 16 * 1024 * 1024
DISCOVERY_OK_INTERVAL = timedelta(days=7)
DISCOVERY_RETRY_INTERVAL = timedelta(days=1)
TARGET_FIELDS = [
    "account", "company", "biz_info", "ghid", "seed_url",
    "candidate_biz", "candidate_verified_at",
]


class WaybackCdxError(RuntimeError):
    pass


class IdentityApprovalError(RuntimeError):
    pass


@dataclass(frozen=True)
class Capture:
    timestamp: str
    url: str
    archive_url: str


def decode_html_url(value: str) -> str:
    if len(value) > MAX_URL_LENGTH:
        raise ValueError("archived URL is too long")
    previous = value
    for _ in range(MAX_UNESCAPE_DEPTH):
        current = html.unescape(previous)
        if current == previous:
            return current
        previous = current
    raise ValueError("archived URL exceeded HTML unescape depth")


def sanitize_archive_locator(value: str) -> str:
    decoded = decode_html_url(value)
    parts = urlsplit(decoded)
    if parts.hostname != "mp.weixin.qq.com":
        raise ValueError("not a WeChat article URL")
    if parts.path != "/s" and not parts.path.startswith("/s/"):
        raise ValueError("not a WeChat article path")
    if parts.path.startswith("/s/"):
        return urlunsplit(("https", "mp.weixin.qq.com", parts.path, "", ""))
    query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=False)
        if key in ARCHIVE_QUERY_FIELDS
    ]
    values = dict(query)
    if not values.get("__biz") or not values.get("mid"):
        raise ValueError("missing stable WeChat article identifiers")
    return urlunsplit((
        "https", "mp.weixin.qq.com", "/s", urlencode(query), "",
    ))


def normalize_archived_url(value: str) -> str:
    return normalize_url(sanitize_archive_locator(value))


def parse_cdx_page(rows: list) -> tuple[list[Capture], str]:
    if not rows or not isinstance(rows[0], list):
        return [], ""
    header = rows[0]
    has_resume = (
        len(rows) >= 3 and rows[-2] == []
        and isinstance(rows[-1], list) and len(rows[-1]) == 1
    )
    data_rows = rows[1:-2] if has_resume else rows[1:]
    resume_key = rows[-1][0] if has_resume else ""
    positions = {name: index for index, name in enumerate(header)}
    captures = []
    for row in data_rows:
        try:
            archive_url = sanitize_archive_locator(row[positions["original"]])
            normalized = normalize_url(archive_url)
            timestamp = row[positions["timestamp"]]
        except (KeyError, IndexError, TypeError, ValueError):
            continue
        if re.fullmatch(r"\d{14}", timestamp):
            captures.append(Capture(
                timestamp=timestamp, url=normalized, archive_url=archive_url,
            ))
    return captures, resume_key


def discover_biz(
    biz_info: str,
    session: requests.Session | None = None,
    page_limit: int = 500,
) -> list[Capture]:
    owns_client = session is None
    client = session or requests.Session()
    resume_key = ""
    seen_resume_keys = set()
    captures: list[Capture] = []
    try:
        while True:
            params = [
                ("url", f"mp.weixin.qq.com/s?__biz={biz_info}*"),
                ("output", "json"),
                ("fl", "timestamp,original"),
                ("filter", "statuscode:200"),
                ("filter", "mimetype:text/html"),
                ("limit", str(page_limit)),
                ("showResumeKey", "true"),
            ]
            if resume_key:
                params.append(("resumeKey", resume_key))
            prepared_url = requests.Request("GET", CDX_API, params=params).prepare().url
            if not prepared_url:
                raise WaybackCdxError("CDX request URL preparation failed")
            rows = None
            for attempt in range(3):
                response = None
                try:
                    response = safe_get(
                        prepared_url, timeout=90, allowed_hosts=ARCHIVE_HOSTS,
                        session=client, stream=True,
                    )
                except ValueError as exc:
                    raise WaybackCdxError("CDX request rejected by URL safety policy") from exc
                except requests.RequestException as exc:
                    if attempt == 2:
                        raise WaybackCdxError("CDX request retries exhausted") from exc
                    time.sleep(2 ** attempt)
                    continue
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
                        raise WaybackCdxError("CDX response exceeded size limit")
                    chunks: list[bytes] = []
                    total = 0
                    for chunk in response.iter_content(chunk_size=64 * 1024):
                        if not chunk:
                            continue
                        total += len(chunk)
                        if total > MAX_CDX_BYTES:
                            raise WaybackCdxError("CDX response exceeded size limit")
                        chunks.append(chunk)
                    rows = json.loads(b"".join(chunks).decode("utf-8-sig"))
                    break
                except WaybackCdxError:
                    raise
                except (requests.RequestException, ValueError, UnicodeError) as exc:
                    raise WaybackCdxError("CDX response was invalid") from exc
                finally:
                    if response is not None:
                        response.close()
            if rows is None:
                raise WaybackCdxError("CDX request retries exhausted")
            if isinstance(rows, dict):
                raise WaybackCdxError("CDX returned an error object")
            page, resume_key = parse_cdx_page(rows)
            captures.extend(page)
            if not resume_key:
                break
            if resume_key in seen_resume_keys:
                raise WaybackCdxError("CDX returned a repeated resume key")
            seen_resume_keys.add(resume_key)
            time.sleep(0.5)
    finally:
        if owns_client:
            client.close()
    unique = {
        (capture.url, capture.timestamp, capture.archive_url): capture
        for capture in captures
    }
    return sorted(unique.values(), key=lambda item: (item.url, item.timestamp))


def registry_biz_matches_account(
    account: str,
    biz_info: str,
    captures: list[Capture],
    session: requests.Session,
) -> bool:
    for capture in sorted(
        captures, key=lambda item: item.timestamp, reverse=True,
    )[:8]:
        archive_url = (
            f"https://web.archive.org/web/{capture.timestamp}id_/"
            f"{capture.archive_url}"
        )
        try:
            identity = extract_identity_from_html(
                read_snapshot_html(archive_url, session),
                capture.archive_url,
                capture.timestamp,
            )
        except IdentityResolutionError:
            continue
        if identity.account == account and identity.biz_info == biz_info:
            return True
    return False


def load_targets() -> list[dict[str, str]]:
    with TARGETS_FILE.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def save_targets(rows: list[dict[str, str]]) -> None:
    fieldnames = list(TARGET_FIELDS)
    for row in rows:
        for field in row:
            if field not in fieldnames:
                fieldnames.append(field)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=TARGETS_FILE.parent, delete=False,
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        temp = Path(handle.name)
    temp.replace(TARGETS_FILE)


def existing_urls() -> set[str]:
    result = set()
    with MANIFEST.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            try:
                result.add(normalize_url(row.get("url", "")))
            except ValueError:
                continue
    return result


def load_candidates() -> list[dict[str, str]]:
    if not CANDIDATES_FILE.exists():
        return []
    return list(csv.DictReader(CANDIDATES_FILE.open(encoding="utf-8")))


def load_discovery_state() -> dict:
    if not DISCOVERY_STATE_FILE.exists():
        return {"accounts": {}}
    try:
        return json.loads(DISCOVERY_STATE_FILE.read_text())
    except (OSError, ValueError):
        return {"accounts": {}}


def save_discovery_state(state: dict) -> None:
    DISCOVERY_STATE_FILE.parent.mkdir(exist_ok=True)
    temp = DISCOVERY_STATE_FILE.with_suffix(".json.tmp")
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    temp.replace(DISCOVERY_STATE_FILE)


def account_discovery_due(record: dict, now: datetime | None = None) -> bool:
    now = now or datetime.now()
    previous = parse_datetime(record.get("updated_at", ""))
    if previous is None:
        return True
    interval = (
        DISCOVERY_OK_INTERVAL if record.get("status") == "ok"
        else DISCOVERY_RETRY_INTERVAL
    )
    return now - previous >= interval


def capture_identity_set(value: str) -> set[tuple[str, str]]:
    try:
        items = json.loads(value or "[]")
    except ValueError:
        return set()
    return {
        (str(item.get("timestamp", "")), str(item.get("archive_url", "")))
        for item in items if isinstance(item, dict)
    }


def save_candidates(rows: list[dict[str, str]]) -> None:
    CANDIDATES_FILE.parent.mkdir(exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=CANDIDATES_FILE.parent,
        delete=False,
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in FIELDS} for row in rows)
        temp = Path(handle.name)
    temp.replace(CANDIDATES_FILE)


class candidate_lock:
    def __enter__(self):
        LOCK_FILE.parent.mkdir(exist_ok=True)
        self.handle = LOCK_FILE.open("a+")
        fcntl.flock(self.handle, fcntl.LOCK_EX)
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.handle.close()


def _approve_identity_locked(account: str, expected_biz: str = "") -> dict[str, str]:
    targets = load_targets()
    for target in targets:
        if target.get("account", "").strip() != account.strip():
            continue
        candidate_biz = target.get("candidate_biz", "").strip()
        if not candidate_biz:
            raise IdentityApprovalError("该公众号没有待审批的身份候选")
        if expected_biz and candidate_biz != expected_biz.strip():
            raise IdentityApprovalError("待审批 biz 与指定值不一致")
        target["biz_info"] = candidate_biz
        target["candidate_biz"] = ""
        target["candidate_verified_at"] = ""
        save_targets(targets)
        state = load_discovery_state()
        state.setdefault("accounts", {}).pop(target["account"], None)
        save_discovery_state(state)
        return {"account": target["account"], "biz_info": candidate_biz}
    raise IdentityApprovalError("未找到指定公众号")


def approve_identity(account: str, expected_biz: str = "") -> dict[str, str]:
    if not account.strip():
        raise IdentityApprovalError("公众号名称不能为空")
    with candidate_lock():
        return _approve_identity_locked(account, expected_biz)


def _discover_locked(
    account_filter: str = "", due_only: bool = False,
    now: datetime | None = None,
) -> dict[str, int]:
    existing = {row["url"]: row for row in load_candidates()}
    indexed = existing_urls()
    state = load_discovery_state()
    counts = {
        "accounts_ok": 0, "accounts_failed": 0,
        "accounts_skipped": 0,
        "identities_resolved": 0,
        "identities_pending": 0,
        "captures": 0, "candidates": 0,
        "already_indexed": 0, "missing_biz": 0,
    }
    session = requests.Session()
    session.headers.update({"User-Agent": "sgt-kb-wayback/1.0"})
    try:
        targets = load_targets()
        for target in targets:
            if account_filter and target["account"] != account_filter:
                continue
            biz_info = target.get("biz_info", "").strip()
            seed_url = target.get("seed_url", "").strip()
            candidate_biz = target.get("candidate_biz", "").strip()
            account_captures: list[Capture] | None = None
            previous_state = state["accounts"].get(target["account"], {})
            if (
                due_only
                and not account_discovery_due(previous_state, now)
            ):
                counts["accounts_skipped"] += 1
                continue
            if not biz_info and seed_url:
                try:
                    identity = resolve_article_identity(
                        seed_url, expected_account=target["account"], session=session,
                    )
                except (IdentityResolutionError, ValueError) as exc:
                    counts["accounts_failed"] += 1
                    state["accounts"][target["account"]] = {
                        "status": "identity_failed", "error": type(exc).__name__,
                        "updated_at": datetime.now().isoformat(timespec="seconds"),
                    }
                    save_discovery_state(state)
                    continue
                biz_info = identity.biz_info
                target["biz_info"] = biz_info
                save_targets(targets)
                counts["identities_resolved"] += 1
            if not biz_info:
                if candidate_biz:
                    counts["identities_pending"] += 1
                    state["accounts"][target["account"]] = {
                        "status": "identity_pending", "error": "",
                        "candidate_biz": candidate_biz,
                        "updated_at": datetime.now().isoformat(timespec="seconds"),
                    }
                    save_discovery_state(state)
                    continue
                try:
                    biz_info = lookup_public_registry_biz(
                        target["account"], session=session,
                    )
                except PublicRegistryNotFound:
                    counts["missing_biz"] += 1
                    state["accounts"][target["account"]] = {
                        "status": "missing_biz", "error": "",
                        "updated_at": datetime.now().isoformat(timespec="seconds"),
                    }
                    save_discovery_state(state)
                    continue
                except PublicRegistryError as exc:
                    counts["accounts_failed"] += 1
                    state["accounts"][target["account"]] = {
                        "status": "identity_failed", "error": type(exc).__name__,
                        "updated_at": datetime.now().isoformat(timespec="seconds"),
                    }
                    save_discovery_state(state)
                    continue
                try:
                    account_captures = discover_biz(biz_info, session=session)
                except Exception as exc:
                    counts["accounts_failed"] += 1
                    state["accounts"][target["account"]] = {
                        "status": "identity_failed", "error": type(exc).__name__,
                        "updated_at": datetime.now().isoformat(timespec="seconds"),
                    }
                    save_discovery_state(state)
                    continue
                if not registry_biz_matches_account(
                    target["account"], biz_info, account_captures, session,
                ):
                    counts["accounts_failed"] += 1
                    state["accounts"][target["account"]] = {
                        "status": "identity_failed",
                        "error": "RegistryIdentityMismatch",
                        "updated_at": datetime.now().isoformat(timespec="seconds"),
                    }
                    save_discovery_state(state)
                    continue
                target["candidate_biz"] = biz_info
                target["candidate_verified_at"] = datetime.now().isoformat(
                    timespec="seconds"
                )
                save_targets(targets)
                counts["identities_pending"] += 1
                state["accounts"][target["account"]] = {
                    "status": "identity_pending", "error": "",
                    "candidate_biz": biz_info,
                    "updated_at": datetime.now().isoformat(timespec="seconds"),
                }
                save_discovery_state(state)
                continue
            grouped: dict[str, list[Capture]] = defaultdict(list)
            try:
                if account_captures is None:
                    account_captures = discover_biz(biz_info, session=session)
            except Exception as exc:
                counts["accounts_failed"] += 1
                state["accounts"][target["account"]] = {
                    "status": "failed", "error": type(exc).__name__,
                    "updated_at": datetime.now().isoformat(timespec="seconds"),
                }
                save_candidates(sorted(
                    existing.values(), key=lambda row: (row["account"], row["url"])
                ))
                save_discovery_state(state)
                continue
            for capture in account_captures:
                grouped[capture.url].append(capture)
                counts["captures"] += 1
            for url, url_captures in grouped.items():
                if url in indexed:
                    counts["already_indexed"] += 1
                    continue
                row = existing.get(url, {})
                old_capture_ids = capture_identity_set(row.get("captures_json", ""))
                new_capture_items = [
                    {"timestamp": capture.timestamp, "archive_url": capture.archive_url}
                    for capture in sorted(
                        url_captures, key=lambda item: item.timestamp, reverse=True
                    )
                ]
                new_capture_ids = {
                    (item["timestamp"], item["archive_url"])
                    for item in new_capture_items
                }
                revive = (
                    row.get("status") == "exhausted"
                    and bool(new_capture_ids - old_capture_ids)
                )
                row.update({
                    "account": target["account"],
                    "company": target["company"],
                    "biz_info": biz_info,
                    "url": url,
                    "timestamps": "|".join(sorted(
                        {capture.timestamp for capture in url_captures}, reverse=True
                    )),
                    "captures_json": json.dumps(
                        new_capture_items, ensure_ascii=False, separators=(",", ":")
                    ),
                    "status": "pending" if revive else row.get("status", "pending"),
                    "error": "" if revive else row.get("error", ""),
                    "attempt_cursor": "0" if revive else row.get("attempt_cursor", "0"),
                    "failure_rounds": "0" if revive else row.get("failure_rounds", "0"),
                    "last_attempt_at": "" if revive else row.get("last_attempt_at", ""),
                    "next_attempt_at": "" if revive else row.get("next_attempt_at", ""),
                })
                existing[url] = row
                counts["candidates"] += 1
            counts["accounts_ok"] += 1
            state["accounts"][target["account"]] = {
                "status": "ok", "error": "", "captures": len(account_captures),
                "unique_urls": len(grouped),
                "updated_at": datetime.now().isoformat(timespec="seconds"),
            }
            save_candidates(sorted(
                existing.values(), key=lambda row: (row["account"], row["url"])
            ))
            save_discovery_state(state)
    finally:
        session.close()
    save_candidates(sorted(existing.values(), key=lambda row: (row["account"], row["url"])))
    save_discovery_state(state)
    return counts


def discover(account_filter: str = "", due_only: bool = False) -> dict[str, int]:
    with candidate_lock():
        return _discover_locked(account_filter, due_only)


def fetch_capture(timestamp: str, locator_url: str, session: requests.Session) -> dict:
    archive_url = f"https://web.archive.org/web/{timestamp}id_/{locator_url}"
    response = safe_get(
        archive_url,
        timeout=60,
        allowed_hosts=ARCHIVE_HOSTS,
        session=session,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    try:
        response.raise_for_status()
        data, error = parse_weixin_html(response.text)
    finally:
        response.close()
    if data is None:
        raise RuntimeError(error or "archived article parsing failed")
    return data


def parse_datetime(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def mark_index_dirty() -> None:
    INDEX_DIRTY_FILE.parent.mkdir(exist_ok=True)
    INDEX_DIRTY_FILE.write_text(datetime.now().isoformat(timespec="seconds") + "\n")


def index_needs_rebuild() -> bool:
    if INDEX_DIRTY_FILE.exists() or not INDEX_DB.exists():
        return True
    return MANIFEST.exists() and MANIFEST.stat().st_mtime_ns > INDEX_DB.stat().st_mtime_ns


def clear_index_dirty() -> None:
    INDEX_DIRTY_FILE.unlink(missing_ok=True)


def _backfill_locked(
    account_filter: str = "",
    max_articles: int = 20,
    max_attempts: int = 20,
    max_snapshots: int = 5,
) -> dict[str, int]:
    rows = load_candidates()
    counts = {
        "attempted": 0, "ingested": 0, "irrelevant": 0,
        "failed": 0, "existing": 0,
    }
    session = requests.Session()
    try:
        now = datetime.now()
        pending = [row for row in rows if row["status"] == "pending"]
        retryable = [
            row for row in rows
            if row["status"] == "failed"
            and (
                parse_datetime(row.get("next_attempt_at", "")) is None
                or parse_datetime(row.get("next_attempt_at", "")) <= now
            )
        ]
        retryable.sort(key=lambda row: (
            row.get("next_attempt_at", ""), row.get("last_attempt_at", ""), row["url"]
        ))
        for row in [*pending, *retryable]:
            if counts["ingested"] >= max_articles or counts["attempted"] >= max_attempts:
                break
            if account_filter and row["account"] != account_filter:
                continue
            if row["status"] not in {"pending", "failed"}:
                continue
            counts["attempted"] += 1
            row["last_attempt_at"] = now.isoformat(timespec="seconds")
            errors = []
            data = None
            try:
                capture_items = json.loads(row.get("captures_json") or "[]")
            except ValueError:
                capture_items = []
            if not capture_items:
                capture_items = [
                    {"timestamp": timestamp, "archive_url": row["url"]}
                    for timestamp in filter(None, row["timestamps"].split("|"))
                ]
            cursor = min(int(row.get("attempt_cursor") or 0), len(capture_items))
            selected = capture_items[cursor:cursor + max_snapshots]
            for capture_item in selected:
                try:
                    data = fetch_capture(
                        capture_item["timestamp"], capture_item["archive_url"], session
                    )
                    break
                except Exception as exc:
                    errors.append(type(exc).__name__)
            if data is None:
                row["error"] = ",".join(errors[-5:]) or "no usable capture"
                wrapped = cursor + len(selected) >= len(capture_items)
                row["attempt_cursor"] = str(0 if wrapped else cursor + len(selected))
                rounds = int(row.get("failure_rounds") or 0) + (1 if wrapped else 0)
                row["failure_rounds"] = str(rounds)
                if rounds >= 3:
                    row["status"] = "exhausted"
                    row["next_attempt_at"] = ""
                else:
                    row["status"] = "failed"
                    delay_days = min(2 ** max(rounds, 0), 14)
                    row["next_attempt_at"] = (
                        now + timedelta(days=delay_days)
                    ).isoformat(timespec="seconds")
                counts["failed"] += 1
                continue
            row["attempt_cursor"] = "0"
            row["failure_rounds"] = "0"
            row["next_attempt_at"] = ""
            if not title_matches(data.get("title", "")):
                row["status"] = "irrelevant"
                row["error"] = ""
                counts["irrelevant"] += 1
                continue
            try:
                mark_index_dirty()
                result = ingest_body(
                    url=row["url"], body=data["body"],
                    company=row["company"], title=data.get("title", ""),
                    tag=classify_tag(data.get("title", "")), date=data.get("date", ""),
                    origin="wayback-wechat", account=row["account"],
                    skip_index=True,
                )
                row["status"] = "ingested"
                row["error"] = ""
                key = "ingested" if result["status"] == "ingested" else "existing"
                counts[key] += 1
            except Exception as exc:
                row["status"] = "failed"
                row["error"] = type(exc).__name__
                row["next_attempt_at"] = (
                    now + timedelta(days=1)
                ).isoformat(timespec="seconds")
                counts["failed"] += 1
            time.sleep(1)
    finally:
        session.close()
        save_candidates(rows)
    return counts


def backfill(
    account_filter: str = "",
    max_articles: int = 20,
    max_attempts: int = 20,
    max_snapshots: int = 5,
) -> dict[str, int]:
    with candidate_lock():
        return _backfill_locked(
            account_filter, max_articles, max_attempts, max_snapshots
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    discover_parser = sub.add_parser("discover")
    discover_parser.add_argument("--account", default="")
    discover_parser.add_argument("--due-only", action="store_true")
    backfill_parser = sub.add_parser("backfill")
    backfill_parser.add_argument("--account", default="")
    backfill_parser.add_argument("--max-articles", type=int, default=20)
    backfill_parser.add_argument("--max-attempts", type=int, default=20)
    backfill_parser.add_argument("--max-snapshots", type=int, default=5)
    backfill_parser.add_argument("--defer-index", action="store_true")
    approve_parser = sub.add_parser("approve-identity")
    approve_parser.add_argument("--account", required=True)
    approve_parser.add_argument("--biz", default="")
    args = parser.parse_args()
    if args.command == "discover":
        result = discover(args.account, args.due_only)
    elif args.command == "approve-identity":
        result = approve_identity(args.account, args.biz)
    else:
        result = backfill(
            args.account, args.max_articles, args.max_attempts, args.max_snapshots
        )
        if not args.defer_index and index_needs_rebuild():
            subprocess.run(
                [sys.executable, "-m", "sgt_kb", "build-index"], cwd=BASE, check=True
            )
            clear_index_dirty()
    print(json.dumps(result, ensure_ascii=False))
    if args.command == "discover" and result["accounts_failed"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
