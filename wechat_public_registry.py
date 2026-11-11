# /// script
# requires-python = ">=3.10"
# dependencies = ["requests", "beautifulsoup4", "lxml", "markdownify"]
# ///
"""Exact-name lookup in a cached, public WeChat account registry."""
from __future__ import annotations

import csv
import io
import math
import re
import tempfile
import time
from pathlib import Path

import requests

from crawl import safe_get

BASE = Path(__file__).parent
CACHE_FILE = BASE / "ingestion" / "wechat_public_registry.csv"
REGISTRY_COMMIT = "7c4913e5308780ecc39f3468ff7885e8eafb1626"
REGISTRY_URL = (
    "https://raw.githubusercontent.com/hellodword/wechat-feeds/"
    f"{REGISTRY_COMMIT}/list.csv"
)
REGISTRY_HOSTS = {"raw.githubusercontent.com"}
MAX_REGISTRY_BYTES = 2 * 1024 * 1024
MIN_REGISTRY_RECORDS = 1_000
MIN_CACHE_RETENTION_RATIO = 0.8
CACHE_TTL_SECONDS = 30 * 24 * 60 * 60
BIZ_PATTERN = re.compile(r"^[A-Za-z0-9+/]{8,}={0,2}$")


class PublicRegistryError(RuntimeError):
    pass


class PublicRegistryNotFound(PublicRegistryError):
    pass


def parse_registry_bytes(data: bytes) -> dict[str, str]:
    try:
        reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig")))
    except UnicodeError as exc:
        raise PublicRegistryError("公开公众号注册表编码无效") from exc
    if not reader.fieldnames or not {"name", "bizid"}.issubset(reader.fieldnames):
        raise PublicRegistryError("公开公众号注册表字段无效")
    candidates: dict[str, set[str]] = {}
    for row in reader:
        name = (row.get("name") or "").strip()
        biz_info = (row.get("bizid") or "").strip()
        if name and len(name) <= 200 and BIZ_PATTERN.fullmatch(biz_info):
            candidates.setdefault(name, set()).add(biz_info)
    return {
        name: next(iter(values))
        for name, values in candidates.items() if len(values) == 1
    }


def validate_registry_bytes(
    data: bytes, minimum_records: int | None = None,
) -> dict[str, str]:
    records = parse_registry_bytes(data)
    minimum = MIN_REGISTRY_RECORDS if minimum_records is None else minimum_records
    if len(records) < minimum:
        raise PublicRegistryError(
            f"公开公众号注册表记录数异常: {len(records)} < {minimum}"
        )
    return records


def read_registry_response(response: requests.Response) -> bytes:
    length = response.headers.get("Content-Length", "").strip()
    if length.isdigit() and int(length) > MAX_REGISTRY_BYTES:
        raise PublicRegistryError("公开公众号注册表超过大小限制")
    chunks: list[bytes] = []
    total = 0
    for chunk in response.iter_content(chunk_size=64 * 1024):
        if not chunk:
            continue
        total += len(chunk)
        if total > MAX_REGISTRY_BYTES:
            raise PublicRegistryError("公开公众号注册表超过大小限制")
        chunks.append(chunk)
    return b"".join(chunks)


def download_registry(session: requests.Session) -> bytes:
    response = None
    try:
        response = safe_get(
            REGISTRY_URL, timeout=60, allowed_hosts=REGISTRY_HOSTS,
            session=session, stream=True,
        )
        response.raise_for_status()
        data = read_registry_response(response)
        validate_registry_bytes(data)
        return data
    except PublicRegistryError:
        raise
    except (requests.RequestException, ValueError) as exc:
        raise PublicRegistryError("公开公众号注册表下载失败") from exc
    finally:
        if response is not None:
            response.close()


def save_registry_cache(data: bytes, cache_file: Path = CACHE_FILE) -> None:
    temp: Path | None = None
    try:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            "wb", dir=cache_file.parent, delete=False,
        ) as handle:
            handle.write(data)
            temp = Path(handle.name)
        temp.replace(cache_file)
    except OSError as exc:
        if temp is not None:
            try:
                temp.unlink(missing_ok=True)
            except OSError:
                pass
        raise PublicRegistryError("公开公众号注册表缓存写入失败") from exc
    if temp is not None:
        try:
            temp.unlink(missing_ok=True)
        except OSError as exc:
            raise PublicRegistryError("公开公众号注册表临时文件清理失败") from exc


def read_registry_cache(
    cache_file: Path, now: float,
) -> tuple[dict[str, str] | None, bool]:
    try:
        stat = cache_file.stat()
    except FileNotFoundError:
        return None, False
    except OSError as exc:
        raise PublicRegistryError("公开公众号注册表缓存状态读取失败") from exc
    if stat.st_size > MAX_REGISTRY_BYTES:
        return None, False
    try:
        cached_data = cache_file.read_bytes()
    except OSError as exc:
        raise PublicRegistryError("公开公众号注册表缓存读取失败") from exc
    try:
        records = validate_registry_bytes(cached_data)
    except PublicRegistryError:
        return None, False
    return records, now - stat.st_mtime < CACHE_TTL_SECONDS


def load_public_registry(
    session: requests.Session,
    cache_file: Path = CACHE_FILE,
    now: float | None = None,
) -> dict[str, str]:
    now = time.time() if now is None else now
    cached_records, fresh = read_registry_cache(cache_file, now)
    if cached_records is not None and fresh:
        return cached_records
    try:
        data = download_registry(session)
        records = validate_registry_bytes(data)
        if cached_records is not None:
            retained_minimum = math.ceil(
                len(cached_records) * MIN_CACHE_RETENTION_RATIO
            )
            if len(records) < retained_minimum:
                raise PublicRegistryError(
                    "公开公众号注册表相对已有缓存异常缩水"
                )
    except PublicRegistryError:
        if cached_records is not None:
            return cached_records
        raise
    save_registry_cache(data, cache_file)
    return records


def lookup_public_registry_biz(
    account: str,
    session: requests.Session,
    cache_file: Path = CACHE_FILE,
) -> str:
    name = account.strip()
    if not name or len(name) > 200:
        raise PublicRegistryNotFound("公众号名称不在公开注册表中")
    biz_info = load_public_registry(session, cache_file).get(name, "")
    if not biz_info:
        raise PublicRegistryNotFound("公众号名称不在公开注册表中")
    return biz_info
