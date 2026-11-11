# /// script
# requires-python = ">=3.10"
# dependencies = ["requests", "beautifulsoup4", "lxml", "markdownify"]
# ///
"""Idempotently ingest one public URL into sgt-kb."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from markdownify import markdownify as markdown_to_text

from sgt_kb.collection.crawl import BASE, OUT, clean_md, fetch_generic, fetch_weixin, slug, write_article
from sgt_kb.collection.figure_pipeline import process_article

MANIFEST = BASE / "crawl_manifest.csv"
FIELDS = ["company", "title", "tag", "date", "url", "origin"]


def normalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        raise ValueError("只支持 http/https URL")
    host = parts.netloc.lower()
    scheme = "https"
    query = parts.query
    if host == "mp.weixin.qq.com":
        if parts.path.startswith("/s/"):
            query = ""
        elif parts.path == "/s":
            allowed = {"__biz", "mid", "idx", "sn"}
            query = urlencode(
                [
                    (key, value)
                    for key, value in parse_qsl(parts.query)
                    if key in allowed
                ]
            )
    return urlunsplit((scheme, host, parts.path, query, ""))


def _body_only(raw: str) -> str:
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end >= 0:
            raw = raw[end + 4 :]
    raw = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", raw)
    return re.sub(r"\s+", "", raw)


def _content_hash(body: str) -> str:
    return hashlib.sha256(_body_only(body).encode()).hexdigest()


def find_duplicate(body: str):
    target = _content_hash(body)
    for path in OUT.glob("*.md"):
        if _content_hash(path.read_text(encoding="utf-8")) == target:
            return path
    return None


def find_existing_url(url: str):
    normalized = normalize_url(url)
    for path in OUT.glob("*.md"):
        raw = path.read_text(encoding="utf-8")
        match = re.search(r"^url:\s*(.+?)\s*$", raw, re.MULTILINE)
        if match:
            try:
                if normalize_url(match.group(1)) == normalized:
                    return path
            except ValueError:
                pass
    return None


def fetch(url: str, allowed_hosts: set[str] | None = None):
    host = urlsplit(url).netloc.lower()
    return fetch_weixin(url) if host == "mp.weixin.qq.com" else fetch_generic(url, allowed_hosts)


def append_manifest(row: dict):
    with MANIFEST.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writerow({field: row.get(field, "") for field in FIELDS})


def ingest_body(
    url: str,
    body: str,
    company: str,
    title: str,
    tag: str,
    date: str,
    origin: str,
    account: str = "",
    skip_images: bool = False,
    skip_index: bool = False,
):
    url = normalize_url(url)
    existing = find_existing_url(url)
    if existing:
        return {
            "status": "existing_url",
            "url": url,
            "article_path": str(existing),
            "doc_id": existing.stem,
        }
    if len(re.sub(r"\s+", "", body)) < 200:
        raise RuntimeError("正文过短，拒绝入库")
    duplicate = find_duplicate(body)
    if duplicate:
        return {
            "status": "existing_content",
            "url": url,
            "article_path": str(duplicate),
            "doc_id": duplicate.stem,
        }

    with MANIFEST.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    row = {
        "company": company or account or "待分类",
        "title": title or url,
        "tag": tag or "待分类",
        "date": date,
        "url": url,
        "origin": origin,
    }
    article_path = OUT / f"{len(rows):03d}-{slug(row['title'], url)}.md"
    write_article(article_path, row, {"body": body, "account": account})
    append_manifest(row)

    figure_result = {"figures": 0, "changed": False}
    if not skip_images:
        figure_result = process_article(article_path)
    if not skip_index:
        subprocess.run(
            ["uv", "run", str(BASE / "build_index.py")],
            cwd=BASE,
            check=True,
        )
    return {
        "status": "ingested",
        "url": url,
        "article_path": str(article_path),
        "doc_id": article_path.stem,
        "title": row["title"],
        "company": row["company"],
        "tag": row["tag"],
        "date": row["date"],
        "figures": figure_result,
        "indexed": not skip_index,
    }


def ingest_html_content(
    url: str,
    content_html: str,
    company: str,
    title: str,
    tag: str,
    date: str,
    origin: str,
    skip_images: bool = False,
    skip_index: bool = False,
):
    body = clean_md(markdown_to_text(content_html, heading_style="ATX"))
    return ingest_body(
        url=url,
        body=body,
        company=company,
        title=title,
        tag=tag,
        date=date,
        origin=origin,
        account=company,
        skip_images=skip_images,
        skip_index=skip_index,
    )


def ingest(
    url: str,
    company: str = "",
    tag: str = "",
    origin: str = "auto-ingest",
    skip_images: bool = False,
    skip_index: bool = False,
    allowed_hosts: set[str] | None = None,
    title: str = "",
    date: str = "",
):
    url = normalize_url(url)
    existing = find_existing_url(url)
    if existing:
        return {
            "status": "existing_url",
            "url": url,
            "article_path": str(existing),
            "doc_id": existing.stem,
        }
    data, error = fetch(url, allowed_hosts)
    if data is None:
        raise RuntimeError(f"抓取失败: {error}")
    return ingest_body(
        url=url,
        body=data["body"],
        company=company or data.get("account") or "待分类",
        title=title or data.get("title") or url,
        tag=tag or "待分类",
        date=date or data.get("date", ""),
        origin=origin,
        account=data.get("account", ""),
        skip_images=skip_images,
        skip_index=skip_index,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--company", default="")
    parser.add_argument("--tag", default="")
    parser.add_argument("--origin", default="auto-ingest")
    parser.add_argument("--skip-images", action="store_true")
    parser.add_argument("--skip-index", action="store_true")
    parser.add_argument("--title", default="")
    parser.add_argument("--date", default="")
    args = parser.parse_args()
    try:
        result = ingest(
            args.url,
            company=args.company,
            tag=args.tag,
            origin=args.origin,
            skip_images=args.skip_images,
            skip_index=args.skip_index,
            title=args.title,
            date=args.date,
        )
    except Exception as exc:
        print(
            json.dumps(
                {"status": "failed", "error": f"{type(exc).__name__}: {exc}"},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
