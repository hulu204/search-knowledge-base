# /// script
# requires-python = ">=3.10"
# dependencies = ["requests", "beautifulsoup4", "lxml", "markdownify", "FlagEmbedding>=1.3", "torch", "numpy"]
# ///
"""英文权威源增量轮询:RSS → kb_gate 门控 → 入库。

- accept:直接入库(Medium 类站点从 feed 的 content:encoded 取全文,其余走 ingest_url 抓页面)
- review:落 ingestion/review_queue.csv 等人工确认,不入库
- reject:只记日志
新文章判定靠 ingest_url 的 URL/内容幂等去重 + manifest 标题去重。
"""
import csv
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree

import requests

from sgt_kb.paths import ROOT

BASE = ROOT
sys.path.insert(0, str(BASE))
from sgt_kb.indexing.kb_gate import gate_texts  # noqa: E402
from sgt_kb.collection.review_queue import candidate_id, enqueue_candidate, load_queue  # noqa: E402

MANIFEST = BASE / "crawl_manifest.csv"
UA = {"User-Agent": "Mozilla/5.0"}

# (company, feed_url, options)
FEEDS_EN = [
    ("Vespa", "https://blog.vespa.ai/feed.xml", {}),
    ("Elastic", "https://www.elastic.co/search-labs/blog/feed", {"path_filter": "/search-labs/"}),
    ("turbopuffer", "https://turbopuffer.com/blog/rss.xml", {}),
    ("LanceDB", "https://lancedb.com/blog/rss.xml", {}),
    ("softwaredoug", "https://softwaredoug.com/feed.xml", {}),
    ("Tunkelang", "https://medium.com/feed/@dtunkelang", {"content_from_feed": True}),
    ("eugeneyan", "https://eugeneyan.com/rss/", {}),
    ("Sease", "https://sease.io/feed", {}),
    ("Marginalia", "https://www.marginalia.nu/log/index.xml", {}),
    ("CommonCrawl", "https://commoncrawl.org/blog/rss.xml", {}),
]

TAG_RULES = [
    ("爬虫抓取", ["crawl", "Crawl", "spider", "bot ", "frontier", "爬虫", "抓取"]),
    ("索引构建", ["index", "Index", "inverted", "posting", "compression", "BM25", "索引"]),
    ("召回", ["retrieval", "Retrieval", "recall", "ANN", "HNSW", "vector", "embedding", "Embedding", "召回", "向量"]),
    ("排序", ["rank", "Rank", "rerank", "LTR", "relevance model", "排序"]),
    ("搜索相关性", ["relevance", "Relevance", "相关性"]),
    ("查询理解", ["query understanding", "Query Understanding", "intent", "query rewriting", "查询理解"]),
    ("评测", ["eval", "Eval", "benchmark", "Benchmark", "metric", "评测"]),
    ("问答/RAG", ["RAG", "DeepSearch", "DeepResearch", "question answering", "agentic", "Agentic"]),
]


def classify_tag(title: str) -> str:
    for tag, kws in TAG_RULES:
        if any(k in title for k in kws):
            return tag
    return "搜索"


def norm_title(s: str) -> str:
    return re.sub(r"[\s\|｜\-—【】\[\]()（）!！?？:：，,。.'\"“”‘’]+", "", s).lower()


def manifest_titles() -> set:
    return {norm_title(r["title"]) for r in csv.DictReader(MANIFEST.open(encoding="utf-8"))}


def manifest_candidate_ids() -> set[str]:
    ids = set()
    for row in csv.DictReader(MANIFEST.open(encoding="utf-8")):
        if not row.get("url"):
            continue
        try:
            ids.add(candidate_id(row["url"]))
        except ValueError:
            continue
    return ids


def source_allowed_hosts(url: str) -> set[str]:
    from urllib.parse import urlsplit
    host = urlsplit(url).hostname or ""
    bare = host.removeprefix("www.")
    return {host, bare, f"www.{bare}"}


def strip_html(s: str) -> str:
    return re.sub(r"<[^>]+>", " ", s or "")[:400]


def feed_items(xml_bytes):
    root = ElementTree.fromstring(xml_bytes)
    ns = {"content": "http://purl.org/rss/1.0/modules/content/",
          "atom": "http://www.w3.org/2005/Atom"}
    # RSS 2.0
    for item in root.iter("item"):
        yield {
            "title": (item.findtext("title") or "").strip(),
            "link": (item.findtext("link") or "").strip(),
            "summary": strip_html(item.findtext("description") or ""),
            "content": item.findtext("content:encoded", namespaces=ns) or "",
            "date": (item.findtext("pubDate") or "").strip(),
        }
    # Atom
    for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
        link_el = entry.find("{http://www.w3.org/2005/Atom}link")
        yield {
            "title": (entry.findtext("{http://www.w3.org/2005/Atom}title") or "").strip(),
            "link": (link_el.get("href") if link_el is not None else "").strip(),
            "summary": strip_html(entry.findtext("{http://www.w3.org/2005/Atom}summary") or
                                  entry.findtext("{http://www.w3.org/2005/Atom}content") or ""),
            "content": "",
            "date": (entry.findtext("{http://www.w3.org/2005/Atom}updated") or "").strip(),
        }


def parse_date(s: str) -> str:
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(s.strip()[:31], fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s)
    return m.group(0) if m else ""


def ingest_from_feed_content(company, title, tag, date, url, content_html):
    """Medium 等 curl 403 的站:直接用 feed 里的全文落库。"""
    from markdownify import markdownify as md
    from sgt_kb.collection.crawl import write_article, slug, clean_md
    body = clean_md(md(content_html, heading_style="ATX"))
    if len(body) < 500:
        return False
    rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8")))
    row = {"company": company, "title": title, "tag": tag, "date": date,
           "url": url, "origin": "en-rss-feedbody"}
    path = BASE / "articles" / f"{len(rows):03d}-{slug(title, url)}.md"
    write_article(path, row, {"body": body, "account": company})
    with MANIFEST.open("a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=["company", "title", "tag", "date", "url", "origin"]).writerow(row)
    return True


def main():
    from sgt_kb.collection.ingest_url import ingest
    existing = manifest_titles()
    queued_ids = {row["id"] for row in load_queue()[0]} | manifest_candidate_ids()
    ingested, reviewed = [], 0
    for company, feed_url, opts in FEEDS_EN:
        try:
            r = requests.get(feed_url, headers=UA, timeout=30)
            r.raise_for_status()
            items = [it for it in feed_items(r.content) if it["title"] and it["link"]]
        except Exception as e:
            print(f"!! {company} feed 拉取失败: {e}")
            continue
        if opts.get("path_filter"):
            items = [it for it in items if opts["path_filter"] in it["link"]]
        fresh_items = []
        for item in items:
            try:
                item_id = candidate_id(item["link"])
            except ValueError as exc:
                print(f"!! {company}: 跳过非法 RSS URL: {exc}")
                continue
            if norm_title(item["title"]) not in existing and item_id not in queued_ids:
                fresh_items.append(item)
        items = fresh_items
        if not items:
            continue
        verdicts = gate_texts([f"{it['title']}. {it['summary']}" for it in items])
        for it, v in zip(items, verdicts):
            date = parse_date(it["date"])
            if v["verdict"] == "reject":
                enqueue_candidate(
                    company, it["title"], date, it["link"], v.get("margin"),
                    status="rejected", error=v.get("reason", "gate reject"),
                )
                queued_ids.add(candidate_id(it["link"]))
                print(f"- {company}: [reject {v['reason'][:20]}] {it['title'][:50]}")
                continue
            if v["verdict"] == "review":
                added = enqueue_candidate(
                    company, it["title"], date, it["link"], v.get("margin")
                )
                if added:
                    reviewed += 1
                    queued_ids.add(candidate_id(it["link"]))
                    print(f"? {company}: [review m={v['margin']}] {it['title'][:50]}")
                continue
            tag = classify_tag(it["title"])
            try:
                if opts.get("content_from_feed"):
                    ok = ingest_from_feed_content(company, it["title"], tag, date, it["link"], it["content"])
                    if ok:
                        ingested.append(it["title"])
                        existing.add(norm_title(it["title"]))
                        enqueue_candidate(
                            company, it["title"], date, it["link"], v.get("margin"),
                            status="ingested",
                        )
                        queued_ids.add(candidate_id(it["link"]))
                        print(f"+ {company}: {it['title'][:50]}")
                    else:
                        enqueue_candidate(
                            company, it["title"], date, it["link"], v.get("margin"),
                            status="failed", error="feed content too short",
                        )
                        queued_ids.add(candidate_id(it["link"]))
                else:
                    result = ingest(it["link"], company=company, tag=tag,
                                    origin="en-rss", skip_index=True,
                                    allowed_hosts=source_allowed_hosts(it["link"]),
                                    title=it["title"], date=date)
                    if result["status"] not in {"ingested", "existing_url", "existing_content"}:
                        raise RuntimeError(f"unexpected ingest status: {result['status']!r}")
                    enqueue_candidate(
                        company, it["title"], date, it["link"], v.get("margin"),
                        status="ingested",
                    )
                    queued_ids.add(candidate_id(it["link"]))
                    if result["status"] == "ingested":
                        ingested.append(it["title"])
                        existing.add(norm_title(it["title"]))
                        print(f"+ {company}: {it['title'][:50]}")
                    time.sleep(2 + random.random() * 2)
            except Exception as e:
                enqueue_candidate(
                    company, it["title"], date, it["link"], v.get("margin"),
                    status="failed", error=f"{type(e).__name__}: {e}",
                )
                queued_ids.add(candidate_id(it["link"]))
                print(f"!! {company}: {it['title'][:40]} 入库失败: {e}")
        time.sleep(1 + random.random())
    print(f"入库 {len(ingested)} 篇,review 队列 +{reviewed}")


if __name__ == "__main__":
    main()
