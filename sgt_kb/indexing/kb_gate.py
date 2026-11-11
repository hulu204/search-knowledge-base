# /// script
# requires-python = ">=3.10"
# dependencies = ["FlagEmbedding>=1.3", "torch", "numpy"]
# ///
"""入库门控:判断一篇候选文章是否属于「搜索工程」主题,拦住 GEO/营销污染。

三层判定,输出 accept / reject / review:
1. 规则黑名单(融资/招聘/GEO营销/listicle 等模式)→ 直接 reject
2. bge-m3 双质心打分:与「搜索工程」正向种子质心、「GEO/营销」负向种子
   质心分别算余弦,margin = sim_pos - sim_neg
3. margin >= ACCEPT_MARGIN 且 sim_pos >= MIN_POS → accept;
   margin <= REJECT_MARGIN → reject;中间 → review(落 review 队列人工看)

用法:
  import 用法:from kb_gate import gate_texts; gate_texts(["title. summary", ...])
  CLI 用法:uv run kb_gate.py --csv harvest.csv   # 读 title 列,追加 verdict 列
设计上是纯函数节点:任何编排器(cron 脚本、将来的 LangGraph graph)都可直接调用。
"""
import argparse
import csv
import re
import sys
from pathlib import Path

from sgt_kb.paths import ROOT

BASE = ROOT
MODEL_DIR = BASE / "models" / "bge-m3"

# ---- 层 1:规则黑名单(命中即 reject,大小写不敏感) ----
RULE_REJECT = [
    r"generative engine optimi", r"\bAI SEO\b",
    r"rank(ing)? (your|in|on) (brand|AI search|LLM|ChatGPT|Perplexity)",
    r"optimi[sz]e .* for (AI search|LLM|ChatGPT|citations)",
    r"\btop \d+ (tools|apps|platforms)", r"\b\d+ best\b",
    r"series [A-F]\b", r"we('| a)re hiring", r"join (us|our team)",
    r"funding|raised \$|webinar|customer (story|case study)|press release",
    r"\bnewsletter\b", r"crawl archive now available",
    r"^host- and domain-level web graphs", r"general assembly|hackathon",
    r"招聘|融资|直播预告|议题|大会报名|志愿者|早鸟|门票|获奖|喜报|征稿",
]

# ---- 层 2:双质心种子(中英混合;改完种子删 cache 让它重算) ----
POS_SEEDS = [
    "Optimizing BM25 inverted index memory layout for billion-document retrieval",
    "Crawl scheduling and recrawl frequency estimation for web-scale crawlers",
    "URL frontier prioritization and link discovery via anchor text and PageRank",
    "Approximate nearest neighbor search: HNSW graph tuning and quantization tradeoffs",
    "Query understanding: intent classification, spelling correction and query rewriting",
    "Hybrid retrieval with dense embeddings and sparse BM25, fused by reciprocal rank",
    "Learning to rank with click models and relevance judgments for search evaluation",
    "Index compression techniques: delta encoding, posting list layout, zstd",
    "Search relevance evaluation: building golden sets, offline metrics, A/B tests",
    "Freshness-aware indexing pipeline for real-time news and time-sensitive queries",
    "RAG retrieval quality: chunking strategy, reranking and context selection",
    "搜索引擎爬虫抓取调度与网页库更新机制",
    "查询理解链路:意图识别、实体链接与查询改写",
    "倒排索引构建与向量召回的混合检索架构",
    "搜索相关性模型与排序特征工程实践",
    "NDCG, MRR and offline evaluation metrics for search ranking quality",
    "Building judgment lists and golden sets for relevance testing",
    "LambdaMART and learning-to-rank models for product search",
    "ColBERT late interaction and multi-vector retrieval",
    "Open-domain question answering with retrieval augmentation",
    "Generative retrieval: end-to-end search framework replacing cascade ranking",
    "Agentic RAG: multi-step retrieval planning and tool-augmented search pipeline",
    "How search engine crawlers render JavaScript and manage crawl budget",
    "端到端生成式搜索/推荐框架的工业落地",
]
NEG_SEEDS = [
    "How to rank your brand in AI search results: the complete GEO guide",
    "Generative engine optimization is the new SEO: get cited by ChatGPT",
    "10 best AI search tools for marketers in 2026",
    "Announcing our Series B funding to build the future of search",
    "How our customer increased conversions 300% with our search product",
    "Join our webinar: unlock the power of AI for your business",
    "We are hiring: come build the next generation of AI agents",
    "AI 搜索时代品牌如何被大模型引用:GEO 优化完全指南",
    "如何让你的内容出现在 AI 搜索结果里:面向 ChatGPT 的内容优化",
    "峰会议程公布:60 个 Agent 案例等你来听,早鸟票开售",
]

ACCEPT_MARGIN = 0.03
REJECT_MARGIN = -0.05
MIN_POS = 0.30

_model = None
_pos_c = None
_neg_c = None


def _load():
    global _model, _pos_c, _neg_c
    if _model is not None:
        return
    import numpy as np
    import torch
    from FlagEmbedding import BGEM3FlagModel
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    _model = BGEM3FlagModel(str(MODEL_DIR), use_fp16=(dev != "cpu"), devices=dev)

    def centroid(texts):
        out = _model.encode(texts, max_length=512, return_dense=True,
                            return_sparse=False, return_colbert_vecs=False)
        v = np.asarray(out["dense_vecs"], dtype=np.float32)
        v /= np.linalg.norm(v, axis=1, keepdims=True)
        c = v.mean(axis=0)
        return c / np.linalg.norm(c)

    _pos_c = centroid(POS_SEEDS)
    _neg_c = centroid(NEG_SEEDS)


def rule_hit(text: str):
    for pat in RULE_REJECT:
        if re.search(pat, text, re.IGNORECASE):
            return pat
    # GEO 作为营销缩写只认全大写,避免误伤 geospatial/geo field
    if re.search(r"\bGEO\b", text) and not re.search(r"geo[ _-]?(field|spatial|point|shape|distance)", text, re.IGNORECASE):
        return "rule:GEO-acronym"
    return None


def gate_texts(texts: list[str]) -> list[dict]:
    """texts: 每篇文章的 title(可拼上摘要)。返回 verdict 列表。"""
    import numpy as np
    results = []
    pending_idx = []
    for i, t in enumerate(texts):
        pat = rule_hit(t)
        if pat:
            results.append({"verdict": "reject", "reason": f"rule:{pat}",
                            "sim_pos": None, "sim_neg": None, "margin": None})
        else:
            results.append(None)
            pending_idx.append(i)
    if pending_idx:
        _load()
        out = _model.encode([texts[i] for i in pending_idx], max_length=512,
                            return_dense=True, return_sparse=False,
                            return_colbert_vecs=False)
        v = np.asarray(out["dense_vecs"], dtype=np.float32)
        v /= np.linalg.norm(v, axis=1, keepdims=True)
        sp = v @ _pos_c
        sn = v @ _neg_c
        for k, i in enumerate(pending_idx):
            margin = float(sp[k] - sn[k])
            if margin >= ACCEPT_MARGIN and sp[k] >= MIN_POS:
                verdict = "accept"
            elif margin <= REJECT_MARGIN:
                verdict = "reject"
            else:
                verdict = "review"
            results[i] = {"verdict": verdict, "reason": "centroid",
                          "sim_pos": round(float(sp[k]), 3),
                          "sim_neg": round(float(sn[k]), 3),
                          "margin": round(margin, 3)}
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="含 title 列的 CSV,原地追加 verdict/margin 列")
    args = ap.parse_args()
    rows = list(csv.DictReader(open(args.csv, encoding="utf-8")))
    if not rows:
        sys.exit("empty csv")
    verdicts = gate_texts([r["title"] for r in rows])
    fields = list(rows[0].keys()) + ["verdict", "margin", "reason"]
    with open(args.csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r, v in zip(rows, verdicts):
            r.update({"verdict": v["verdict"], "margin": v["margin"], "reason": v["reason"]})
            w.writerow(r)
    from collections import Counter
    print(Counter(v["verdict"] for v in verdicts))


if __name__ == "__main__":
    main()
