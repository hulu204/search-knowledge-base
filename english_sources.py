"""Deterministic title and host policy for English knowledge sources."""
from __future__ import annotations

import re
from urllib.parse import urlsplit


CURATED_HOSTS = {
    "blog.vespa.ai",
    "bilibili.com",
    "commoncrawl.org",
    "dtunkelang.medium.com",
    "elastic.co",
    "eugeneyan.com",
    "lancedb.com",
    "marginalia.nu",
    "queryunderstanding.com",
    "sease.io",
    "softwaredoug.com",
    "turbopuffer.com",
}

REJECT_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\b(hiring|job|career|intern(ship)?|join our team)\b",
        r"\b(webinar|meetup|conference|summit|sponsorship|partner(ship)?)\b",
        r"\b(funding|series [a-f]|press release|newsletter|year in review)\b",
        r"\b(encryption|security distinction|multifactor authentication)\b",
        r"\b(best books?|reading club|writing process|macbook setup)\b",
        r"招聘|内推|实习|校招|议程|报名|峰会|书单|领电子书",
    )
)

ASCII_TERMS = (
    "ad ranking",
    "advertising",
    "ann",
    "bm25",
    "colbert",
    "crawl",
    "crawler",
    "embedding",
    "embeddings",
    "elasticsearch",
    "evaluation",
    "hnsw",
    "index",
    "indexing",
    "lambdamart",
    "learning to rank",
    "ltr",
    "ndcg",
    "opensearch",
    "personalization",
    "query",
    "rag",
    "rank",
    "ranking",
    "recall",
    "recommendation",
    "recommender",
    "relevance",
    "rerank",
    "retrieval",
    "search",
    "solr",
    "vector",
    "vespa",
)
ZH_TERMS = (
    "搜索", "检索", "召回", "排序", "推荐", "广告", "向量", "知识库",
    "查询理解", "索引", "爬虫", "相关性", "评测",
)


def normalize_host(url: str) -> str:
    host = (urlsplit(url).hostname or "").lower()
    return host.removeprefix("www.")


def title_is_relevant(title: str) -> bool:
    text = title.strip()
    if not text or any(pattern.search(text) for pattern in REJECT_PATTERNS):
        return False
    lowered = text.lower()
    if any(term in lowered for term in ZH_TERMS):
        return True
    return any(
        re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", lowered)
        for term in ASCII_TERMS
    )


def host_is_curated(url: str, additional_hosts: set[str] | None = None) -> bool:
    hosts = CURATED_HOSTS | (additional_hosts or set())
    return normalize_host(url) in hosts
