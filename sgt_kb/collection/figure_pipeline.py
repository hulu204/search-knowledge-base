# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///
"""Download article figures and create OCR/VLM sidecars for indexing."""
import argparse
import hashlib
import json
import mimetypes
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests
from sgt_kb.collection.crawl import safe_get

from sgt_kb.paths import ROOT

BASE = ROOT
ARTICLES = BASE / "articles"
IMAGES = BASE / "images"
FIGURES = BASE / "figures"
OVERRIDES = BASE / "figure-overrides"
OCR_SOURCE = BASE / "scripts" / "vision_ocr.swift"
OCR_BIN = BASE / "cache" / "bin" / "vision_ocr"
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\((https?://[^)\s]+)\)")
HEADING_RE = re.compile(r"^\s*#{1,6}\s+(.+?)\s*$")
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
MAX_IMAGE_BYTES = 20 * 1024 * 1024


def _frontmatter(raw: str):
    meta, body = {}, raw
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end >= 0:
            for line in raw[3:end].strip().splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    meta[key.strip()] = value.strip().strip("'\"")
            body = raw[end + 4 :]
    return meta, body


def _section_before(body: str, offset: int) -> str:
    for line in reversed(body[:offset].splitlines()):
        match = HEADING_RE.match(line)
        if match:
            return match.group(1).strip()
    return ""


def _extension(url: str, content_type: str) -> str:
    normalized = content_type.split(";", 1)[0].strip().lower()
    by_type = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/webp": ".webp",
        "image/bmp": ".bmp",
    }
    if normalized in by_type:
        return by_type[normalized]
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}:
        return ".jpg" if suffix == ".jpeg" else suffix
    return mimetypes.guess_extension(normalized) or ".img"


def _ensure_ocr_binary():
    if OCR_BIN.exists() and OCR_BIN.stat().st_mtime_ns >= OCR_SOURCE.stat().st_mtime_ns:
        return
    OCR_BIN.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["swiftc", "-O", str(OCR_SOURCE), "-o", str(OCR_BIN)],
        check=True,
    )


def _ocr(image_path: Path):
    _ensure_ocr_binary()
    result = subprocess.run(
        [str(OCR_BIN), str(image_path)],
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )
    lines = json.loads(result.stdout)
    return lines, "\n".join(
        line["text"] for line in lines if line.get("text", "").strip()
    )


def _vlm(image_path: Path, section: str, ocr_text: str):
    command = os.environ.get("SGT_KB_VLM_COMMAND", "").strip()
    if not command:
        return {}
    prompt = {
        "task": "将图片转换为可检索的结构化知识，不补充图片中没有的信息。",
        "section": section,
        "ocr_text": ocr_text,
        "output_schema": {
            "description": "图片的一段事实性说明",
            "entities": ["图中实体"],
            "relations": [{"source": "", "relation": "", "target": ""}],
        },
    }
    result = subprocess.run(
        [*shlex.split(command), str(image_path)],
        input=json.dumps(prompt, ensure_ascii=False),
        check=True,
        capture_output=True,
        text=True,
        timeout=180,
    )
    value = json.loads(result.stdout)
    if not isinstance(value, dict):
        raise ValueError("SGT_KB_VLM_COMMAND must return a JSON object")
    return value


def _overrides(doc_id: str):
    path = OVERRIDES / f"{doc_id}.json"
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def _download(session: requests.Session, url: str, referer: str):
    response = safe_get(
        url, timeout=30, session=session, stream=True,
        headers={"Referer": referer},
    )
    try:
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")
        if not content_type.lower().startswith("image/"):
            raise ValueError(f"not an image: {content_type or 'unknown content type'}")
        content_length = response.headers.get("Content-Length", "")
        if content_length.isdigit() and int(content_length) > MAX_IMAGE_BYTES:
            raise ValueError(f"image exceeds {MAX_IMAGE_BYTES} byte limit")
        content = bytearray()
        for chunk in response.iter_content(chunk_size=64 * 1024):
            if not chunk:
                continue
            content.extend(chunk)
            if len(content) > MAX_IMAGE_BYTES:
                raise ValueError(f"image exceeds {MAX_IMAGE_BYTES} byte limit")
        return bytes(content), _extension(url, content_type)
    finally:
        response.close()


def process_article(article_path: Path, run_ocr: bool = True):
    raw = article_path.read_text(encoding="utf-8")
    meta, body = _frontmatter(raw)
    doc_id = article_path.stem
    source_page = meta.get("url", "")
    matches = list(IMAGE_RE.finditer(body))
    sidecar_path = FIGURES / f"{doc_id}.json"
    if not matches:
        existing = (
            json.loads(sidecar_path.read_text(encoding="utf-8"))
            if sidecar_path.exists()
            else []
        )
        return {"doc_id": doc_id, "figures": len(existing), "changed": False}

    session = requests.Session()
    session.headers.update({"User-Agent": UA, "Accept": "image/avif,image/webp,image/*"})
    image_dir = IMAGES / doc_id
    image_dir.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    overrides = _overrides(doc_id)
    records, replacements = [], []

    for seq, match in enumerate(matches, 1):
        alt, source_url = match.group(1), match.group(2)
        figure_id = f"{doc_id}-fig-{seq:03d}"
        print(
            f"[figure {seq}/{len(matches)}] {figure_id}",
            file=sys.stderr,
            flush=True,
        )
        section = _section_before(body, match.start())
        record = {
            "figure_id": figure_id,
            "doc_id": doc_id,
            "seq": seq,
            "source_url": source_url,
            "image_path": "",
            "section": section,
            "alt": alt,
            "ocr_lines": [],
            "ocr_text": "",
            "description": "",
            "entities": [],
            "relations": [],
            "analysis_backend": "apple-vision-ocr",
            "status": "pending",
            "error": "",
        }
        try:
            content, extension = _download(session, source_url, source_page)
            image_path = image_dir / f"figure-{seq:03d}{extension}"
            image_path.write_bytes(content)
            record["image_path"] = str(image_path.relative_to(BASE))
            record["content_hash"] = hashlib.sha256(content).hexdigest()
            if run_ocr:
                record["ocr_lines"], record["ocr_text"] = _ocr(image_path)
            vlm = _vlm(image_path, section, record["ocr_text"])
            record.update({key: value for key, value in vlm.items()
                           if key in {"description", "entities", "relations"}})
            if not record["description"]:
                visible = [line["text"] for line in record["ocr_lines"]
                           if line.get("text", "").strip()]
                record["description"] = (
                    f"{section or '文章'}中的配图，包含文字："
                    + "；".join(visible[:30])
                    if visible
                    else f"{section or '文章'}中的配图，未识别出文字。"
                )
            if not record["entities"]:
                record["entities"] = list(dict.fromkeys(
                    line["text"].strip() for line in record["ocr_lines"]
                    if line.get("text", "").strip()
                ))
            if figure_id in overrides:
                record.update(overrides[figure_id])
                record["analysis_backend"] = (
                    f"{record['analysis_backend']}+curated-override"
                )
            record["status"] = "ready"
            local_url = f"../{record['image_path']}"
            replacements.append((match.start(), match.end(), f"![{figure_id}]({local_url})"))
        except Exception as exc:
            record["status"] = "failed"
            record["error"] = f"{type(exc).__name__}: {exc}"
            print(f"  failed: {record['error']}", file=sys.stderr, flush=True)
        records.append(record)

    new_body = body
    for start, end, replacement in reversed(replacements):
        new_body = new_body[:start] + replacement + new_body[end:]
    prefix_length = len(raw) - len(body)
    new_raw = raw[:prefix_length] + new_body
    article_path.write_text(new_raw, encoding="utf-8")
    sidecar_path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "doc_id": doc_id,
        "figures": len(records),
        "ready": sum(record["status"] == "ready" for record in records),
        "failed": sum(record["status"] == "failed" for record in records),
        "changed": new_raw != raw,
        "sidecar": str(sidecar_path),
    }


def main():
    parser = argparse.ArgumentParser()
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--article", type=Path)
    target.add_argument("--doc-id")
    parser.add_argument("--no-ocr", action="store_true")
    args = parser.parse_args()
    article_path = args.article or ARTICLES / f"{args.doc_id}.md"
    if not article_path.is_absolute():
        article_path = BASE / article_path
    if not article_path.exists():
        print(f"article not found: {article_path}", file=sys.stderr)
        return 2
    result = process_article(article_path, run_ocr=not args.no_ocr)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not result.get("failed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
