# /// script
# requires-python = ">=3.10"
# dependencies = ["requests", "beautifulsoup4", "lxml", "markdownify"]
# ///
"""Crawl articles from crawl_manifest.csv into markdown files with frontmatter."""
from __future__ import annotations

import argparse, csv, re, sys, time, random, hashlib, ipaddress, socket
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

BASE = Path(__file__).parent
OUT = BASE / "articles"
OUT.mkdir(exist_ok=True)
FAIL_LOG = BASE / "crawl_failures.csv"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
S = requests.Session()
S.headers.update({"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"})

DELETED_MARKERS = [
    "该内容已被发布者删除", "此内容因违规无法查看", "此内容被投诉且经审核涉嫌侵权",
    "该公众号已迁移", "此帐号已被屏蔽", "参数错误", "链接已过期",
]
SHANGHAI = ZoneInfo("Asia/Shanghai")


def validate_public_url(url: str, allowed_hosts: set[str] | None = None) -> None:
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    if parts.scheme not in {"http", "https"} or not host:
        raise ValueError("只支持公开 http/https URL")
    if allowed_hosts is not None and host not in allowed_hosts:
        raise ValueError(f"重定向到了未授权域名: {host}")
    if host == "localhost" or host.endswith(".local"):
        raise ValueError("拒绝访问本机或局域网地址")
    default_port = 443 if parts.scheme == "https" else 80
    try:
        addresses = {
            item[4][0]
            for item in socket.getaddrinfo(host, parts.port or default_port)
        }
    except OSError as exc:
        raise ValueError("公网地址 DNS 解析失败") from exc
    if not addresses or any(not ipaddress.ip_address(address).is_global for address in addresses):
        raise ValueError("拒绝访问非公网地址")


def safe_get(
    url: str,
    timeout: int = 30,
    allowed_hosts: set[str] | None = None,
    session: requests.Session | None = None,
    stream: bool = False,
    headers: dict[str, str] | None = None,
):
    current = url
    client = session or S
    for _ in range(6):
        validate_public_url(current, allowed_hosts)
        response = client.get(
            current, timeout=timeout, allow_redirects=False,
            stream=stream, headers=headers,
        )
        if response.is_redirect or response.is_permanent_redirect:
            location = response.headers.get("Location")
            if not location:
                response.close()
                raise ValueError("重定向响应缺少 Location")
            current = urljoin(current, location)
            response.close()
            continue
        return response
    raise ValueError("重定向次数过多")


def slug(title: str, url: str) -> str:
    t = re.sub(r"[^\w一-鿿]+", "-", title)[:48].strip("-")
    h = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"{t}-{h}"


def clean_md(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_publish_date(html: str) -> str:
    now_year = datetime.now(SHANGHAI).year
    patterns = (
        r"\bvar\s+ct\s*=\s*['\"]([0-9]{10})['\"]",
        r"['\"]publish_time['\"]\s*:\s*['\"]?([0-9]{10})",
        r"['\"]create_time['\"]\s*:\s*['\"]?([0-9]{10})",
    )
    for pattern in patterns:
        for value in re.findall(pattern, html):
            date = datetime.fromtimestamp(int(value), SHANGHAI)
            if 2009 <= date.year <= now_year + 1:
                return date.strftime("%Y-%m-%d")
    return ""


def parse_weixin_html(html: str):
    for m in DELETED_MARKERS:
        if m in html and "js_content" not in html:
            return None, f"deleted: {m}"
    if "环境异常" in html and "完成验证" in html:
        return None, "captcha"
    soup = BeautifulSoup(html, "lxml")
    content = soup.select_one("#js_content")
    if content is None:
        return None, "no js_content"
    # weixin lazy-loads images via data-src
    for img in content.find_all("img"):
        src = img.get("data-src") or img.get("src") or ""
        img["src"] = src
    title_el = soup.select_one("#activity-name") or soup.select_one('meta[property="og:title"]')
    title = (title_el.get_text(strip=True) if title_el and title_el.name != "meta"
             else (title_el.get("content", "") if title_el else ""))
    account_el = soup.select_one("#js_name")
    account = account_el.get_text(strip=True) if account_el else ""
    body = clean_md(md(str(content), heading_style="ATX"))
    if len(body) < 200:
        return None, f"too short ({len(body)} chars)"
    return {
        "title": title,
        "account": account,
        "date": extract_publish_date(html),
        "body": body,
    }, None


def fetch_weixin(url: str):
    r = safe_get(url, timeout=30, allowed_hosts={"mp.weixin.qq.com"})
    try:
        r.raise_for_status()
        return parse_weixin_html(r.text)
    finally:
        r.close()


def fetch_generic(url: str, allowed_hosts: set[str] | None = None):
    r = safe_get(url, timeout=30, allowed_hosts=allowed_hosts)
    if r.status_code != 200:
        return None, f"http {r.status_code}"
    soup = BeautifulSoup(r.text, "lxml")
    node = None
    for sel in ("article", ".post-content", ".Post-RichTextContainer",
                ".elementor-widget-theme-post-content", "main", "body"):
        nodes = soup.select(sel)
        if not nodes:
            continue
        best = max(nodes, key=lambda n: len(n.get_text()))
        # 命中的节点太短(如相关文章卡片)则降级尝试下一个选择器
        if len(best.get_text(strip=True)) >= 500:
            node = best
            break
        node = node or best
    if node is None:
        return None, "no content node"
    for tag in node.select("script, style, nav, footer"):
        tag.decompose()
    body = clean_md(md(str(node), heading_style="ATX"))
    if len(body) < 200:
        return None, f"too short ({len(body)} chars)"
    return {"title": "", "account": "", "body": body}, None


def write_article(path: Path, row: dict, extra: dict, note: str = ""):
    fm = [
        "---",
        f"title: {row['title']!r}",
        f"company: {row['company']}",
        f"tag: {row['tag']}",
        f"date: {row['date']}",
        f"url: {row['url']}",
        f"account: {extra.get('account', '')}",
        f"origin: {row['origin']}",
    ]
    if note:
        fm.append(f"note: {note}")
    fm.append("---\n")
    path.write_text("\n".join(fm) + extra.get("body", ""), encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        action="append",
        dest="urls",
        help="only crawl this manifest URL (repeatable)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    rows = list(csv.DictReader(open(BASE / "crawl_manifest.csv")))
    selected_urls = set(args.urls or [])
    if selected_urls:
        manifest_urls = {row["url"] for row in rows}
        missing = sorted(selected_urls - manifest_urls)
        if missing:
            print(f"URLs not found in crawl_manifest.csv: {missing}", file=sys.stderr)
            return 2
    fails = []
    done = skipped = 0
    for i, row in enumerate(rows):
        url = row["url"]
        if selected_urls and url not in selected_urls:
            continue
        stem = slug(row["title"], url)
        name = f"{i:03d}-{stem}.md"
        path = OUT / name
        # slug 尾部是 URL md5 前 8 位,后缀匹配即视为已抓(manifest 行号可能因增删位移)
        if path.exists() or next(OUT.glob(f"*-{stem[-8:]}.md"), None):
            skipped += 1
            continue
        host = re.sub(r"https?://([^/]+).*", r"\1", url)
        try:
            if "pan.baidu.com" in host or "bilibili.com" in host:
                kind = "netdisk" if "pan" in host else "video"
                write_article(path, row, {"body": f"(仅元数据：{kind} 链接，无正文)"}, note=f"metadata-only:{kind}")
                done += 1
                continue
            if "mp.weixin.qq.com" in host:
                data, err = fetch_weixin(url)
                time.sleep(2.0 + random.random() * 1.5)
            else:
                data, err = fetch_generic(url)
                time.sleep(1.0)
            if data is None:
                fails.append({**row, "error": err})
                print(f"[{i+1}/{len(rows)}] FAIL {err}: {row['title'][:40]}", flush=True)
                continue
            write_article(path, row, data)
            done += 1
            if (done + skipped) % 10 == 0:
                print(f"[{i+1}/{len(rows)}] ok={done} skip={skipped} fail={len(fails)}", flush=True)
        except Exception as e:
            fails.append({**row, "error": repr(e)})
            print(f"[{i+1}/{len(rows)}] EXC {e!r}: {row['title'][:40]}", flush=True)
            time.sleep(3)
    if selected_urls and FAIL_LOG.exists():
        previous = list(csv.DictReader(open(FAIL_LOG)))
        fails = [row for row in previous if row["url"] not in selected_urls] + fails
    with open(FAIL_LOG, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["company", "title", "tag", "date", "url", "origin", "error"])
        w.writeheader()
        w.writerows(fails)
    print(f"DONE ok={done} skip={skipped} fail={len(fails)} -> {FAIL_LOG}", flush=True)
    return 0


if __name__ == "__main__":
    main()
