# /// script
# requires-python = ">=3.10"
# dependencies = ["requests", "beautifulsoup4", "lxml", "markdownify"]
# ///
"""轮询 wechat2rss 托管 RSS(免登录),新文章入库。

作为 wechat-mp poll 的兜底通道:不依赖公众平台 cookie,但只覆盖
wechat2rss.xlab.app 免费收录的号(https://wechat2rss.xlab.app/list/all/)。
标题命中 wechat_mp.KEYWORDS 才入库。优先使用 RSS 自带完整正文，避免再次
访问微信原文触发反爬；链接仍保留微信原文用于追溯。
"""
import argparse
import re
import sys
import time
import random
from email.utils import parsedate_to_datetime
from pathlib import Path
from xml.etree import ElementTree

import requests

from sgt_kb.paths import ROOT

BASE = ROOT
from sgt_kb.collection.wechat_mp import title_matches
from sgt_kb.collection.en_poll import classify_tag

# 公众号 -> (company, wechat2rss feed id)
FEEDS = {
    "腾讯技术工程": ("腾讯", "9685937b45fe9c7a526dbc32e4f24ba879a65b9a"),
    "美团技术团队": ("美团", "eb4d04149424a874693a51c6fdda0dba8673f5e4"),
    "字节跳动技术团队": ("字节跳动", "4025ea55575daf8bfd8227e68b28d9638b073267"),
    "哔哩哔哩技术": ("B站", "434235d4815fdb8447ff3127fc053ceb8b3aada6"),
    "得物技术": ("得物", "f3a42bd249ec6e8834ae761d8d0f85a949950944"),
    "阿里技术": ("阿里", "6e1f9b775f7a5841ac1a94310f0478b45a02ec01"),
    "爱奇艺技术产品团队": ("爱奇艺", "16a4ec12a83a52e1f6e941bce030a4d64ee26c47"),
}


CONTENT_TAG = "{http://purl.org/rss/1.0/modules/content/}encoded"


def _feed_date(value: str) -> str:
    try:
        return parsedate_to_datetime(value).strftime("%Y-%m-%d")
    except (TypeError, ValueError, OverflowError):
        match = re.search(r"\d{4}-\d{2}-\d{2}", value or "")
        return match.group(0) if match else ""


def _finish(ingested: list, defer_index: bool):
    if ingested and not defer_index:
        import subprocess
        subprocess.run([sys.executable, "-m", "sgt_kb", "build-index"], cwd=BASE, check=True)
        print(f"本次新入库 {len(ingested)} 篇,索引已更新")
    elif ingested:
        print(f"本次新入库 {len(ingested)} 篇,等待统一建索引")
    else:
        print("无新文章")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--defer-index", action="store_true")
    args = parser.parse_args()
    from sgt_kb.collection.ingest_url import ingest, ingest_html_content
    ingested = []
    for name, (company, feed_id) in FEEDS.items():
        url = f"https://wechat2rss.xlab.app/feed/{feed_id}.xml"
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
            r.raise_for_status()
            root = ElementTree.fromstring(r.content)
        except Exception as e:
            print(f"!! {name} feed 拉取失败: {e}")
            continue
        for item in root.iter("item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            if not link or not title_matches(title):
                continue
            content_html = item.findtext(CONTENT_TAG) or ""
            date = _feed_date(item.findtext("pubDate") or "")
            try:
                if len(re.sub(r"<[^>]+>", "", content_html).strip()) >= 200:
                    result = ingest_html_content(
                        link,
                        content_html,
                        company=company,
                        title=title,
                        tag=classify_tag(title),
                        date=date,
                        origin="wechat-rss-feedbody",
                        skip_index=True,
                    )
                else:
                    result = ingest(
                        link,
                        company=company,
                        tag=classify_tag(title),
                        origin="wechat-rss",
                        skip_index=True,
                        title=title,
                        date=date,
                    )
            except Exception as e:
                print(f"!! {name}: {title[:40]} 入库失败: {e}")
                continue
            if result["status"] == "ingested":
                ingested.append(result["title"])
                print(f"+ {name}: {title[:50]}")
                time.sleep(1 + random.random())
        time.sleep(2 + random.random() * 2)
    _finish(ingested, args.defer_index)


if __name__ == "__main__":
    main()
