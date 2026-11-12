# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.0,<2", "FlagEmbedding>=1.3", "torch", "numpy", "scipy"]
# ///
"""搜广推知识库 MCP server (stdio).

Hybrid retrieval: bge-m3 dense (brute-force cosine) + sparse (lexical) with RRF fusion.
"""
import json
import sqlite3
from pathlib import Path

import numpy as np

from sgt_kb.retrieval.recency import (
    RECENCY_HALF_LIFE_DAYS, RECENCY_FLOOR, UNDATED_FACTOR,
    _apply_recency, _freshness_factor,
)

from sgt_kb.paths import ROOT

BASE = ROOT
INDEX = BASE / "index"
MODEL_DIR = BASE / "models" / "bge-m3"
CONTEXT_FILE = BASE / "extra-docs" / "local-context.md"
RRF_K = 60
CAND = 50

_model = None
_dense = None
_sparse = None
_conn = None
_index_signature = None
_mcp = None


def _load():
    from scipy import sparse as sp

    global _model, _dense, _sparse, _conn, _index_signature
    index_files = (INDEX / "kb.sqlite", INDEX / "dense.npy", INDEX / "sparse.npz")
    signature = tuple((path.stat().st_mtime_ns, path.stat().st_size)
                      for path in index_files)
    if _conn is None or signature != _index_signature:
        conn = sqlite3.connect(index_files[0], check_same_thread=False)
        dense = np.load(index_files[1]).astype(np.float32)
        sparse = sp.load_npz(index_files[2]).tocsr()
        chunk_count = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        if dense.shape[0] != chunk_count or sparse.shape[0] != chunk_count:
            conn.close()
            raise RuntimeError(
                "索引文件不一致，请等待 python3 -m sgt_kb build-index 完成后重试。"
            )
        if _conn is not None:
            _conn.close()
        _conn, _dense, _sparse = conn, dense, sparse
        _index_signature = signature
    if _model is None:
        import torch
        from FlagEmbedding import BGEM3FlagModel
        dev = "mps" if torch.backends.mps.is_available() else "cpu"
        _model = BGEM3FlagModel(str(MODEL_DIR), use_fp16=(dev != "cpu"), devices=dev)


def _doc_meta(doc_id):
    r = _conn.execute(
        "SELECT title, company, tag, date, url, path FROM docs WHERE doc_id=?",
        (doc_id,)).fetchone()
    return dict(zip(("title", "company", "tag", "date", "url", "path"), r)) if r else {}


def search_knowledge_base(
    query: str,
    top_k: int = 6,
    company: str = "",
    tag: str = "",
) -> list[dict[str, object]]:
    """执行混合检索，返回工作台和 MCP 共用的结构化结果。"""
    _load()
    out = _model.encode([query], max_length=512,
                        return_dense=True, return_sparse=True,
                        return_colbert_vecs=False)
    qd = np.asarray(out["dense_vecs"][0], dtype=np.float32)
    qd /= (np.linalg.norm(qd) or 1.0)
    lw = out["lexical_weights"][0]

    dense_scores = _dense @ qd
    qs = np.zeros(_sparse.shape[1], dtype=np.float32)
    for tok, w in lw.items():
        qs[int(tok)] = float(w)
    sparse_scores = _sparse @ qs

    # optional metadata filter -> allowed chunk mask
    allowed = None
    if company or tag:
        sql = "SELECT chunk_id FROM chunks c JOIN docs d ON c.doc_id=d.doc_id WHERE 1=1"
        args = []
        if company:
            sql += " AND d.company LIKE ?"
            args.append(f"%{company}%")
        if tag:
            sql += " AND d.tag LIKE ?"
            args.append(f"%{tag}%")
        allowed = np.array([r[0] for r in _conn.execute(sql, args)], dtype=int)
        if allowed.size == 0:
            return []
        mask = np.full(len(dense_scores), -np.inf, dtype=np.float32)
        mask[allowed] = 0.0
        dense_scores = dense_scores + mask
        sparse_scores = sparse_scores + mask

    candidate_count = min(CAND, allowed.size) if allowed is not None else CAND
    d_rank = np.argsort(-dense_scores)[:candidate_count]
    s_rank = np.argsort(-sparse_scores)[:candidate_count]
    rrf = {}
    for rank, cid in enumerate(d_rank):
        rrf[int(cid)] = rrf.get(int(cid), 0.0) + 1.0 / (RRF_K + rank + 1)
    for rank, cid in enumerate(s_rank):
        rrf[int(cid)] = rrf.get(int(cid), 0.0) + 1.0 / (RRF_K + rank + 1)
    chunk_docs, chunk_dates = {}, {}
    candidate_ids = list(rrf)
    if not candidate_ids:
        return []
    placeholders = ",".join("?" for _ in candidate_ids)
    for cid, doc_id, doc_date in _conn.execute(
        f"""
        SELECT c.chunk_id, c.doc_id, d.date
        FROM chunks c JOIN docs d ON c.doc_id=d.doc_id
        WHERE c.chunk_id IN ({placeholders})
        """,
        candidate_ids,
    ):
        chunk_docs[cid] = doc_id
        chunk_dates[cid] = doc_date or ""
    rerank_scores = _apply_recency(rrf, chunk_dates)
    ranked = sorted(rerank_scores, key=rerank_scores.get, reverse=True)
    # diversity: 每篇文档最多取 1 个最优 chunk
    top, seen_docs = [], set()
    for cid in ranked:
        doc_id = chunk_docs[cid]
        if doc_id in seen_docs:
            continue
        seen_docs.add(doc_id)
        top.append(cid)
        if len(top) >= top_k:
            break

    results = []
    for cid in top:
        doc_id, seq, txt = _conn.execute(
            "SELECT doc_id, seq, text FROM chunks WHERE chunk_id=?", (cid,)).fetchone()
        m = _doc_meta(doc_id)
        results.append(
            {
                "doc_id": doc_id,
                "chunk_id": cid,
                "seq": seq,
                "title": m.get("title", ""),
                "company": m.get("company", ""),
                "tag": m.get("tag", ""),
                "date": m.get("date", ""),
                "url": m.get("url", ""),
                "path": m.get("path", ""),
                "text": txt,
                "score": rerank_scores.get(cid, 0.0),
            }
        )
    return results


def kb_search(query: str, top_k: int = 6, company: str = "", tag: str = "") -> str:
    """检索搜广推工业实践知识库(阿里/美团/腾讯/快手/百度等的搜索、推荐、
    广告、召回、排序、冷启动等实践)。

    Args:
        query: 中文自然语言查询,例如 "多路召回如何做融合排序"
        top_k: 返回的片段数量
        company: 可选,按公司过滤,如 "美团"
        tag: 可选,按标签过滤,如 "召回"/"排序"/"广告"
    """
    results = search_knowledge_base(query, top_k, company, tag)
    blocks = [
        f"### [{item['company']}] {item['title']} ({item['date']}, {item['tag']})\n"
        f"doc_id: {item['doc_id']} | chunk_id: {item['chunk_id']} | "
        f"seq: {item['seq']} | path: {item['path']} | {item['url']}\n\n{item['text']}"
        for item in results
    ]
    return "\n\n---\n\n".join(blocks) if blocks else "无结果。"


def kb_get_doc(doc_id: str) -> str:
    """按 doc_id 获取整篇文章全文(kb_search 结果里带 doc_id)。"""
    _load()
    r = _conn.execute("SELECT path FROM docs WHERE doc_id=?", (doc_id,)).fetchone()
    if not r:
        return f"doc_id 不存在: {doc_id}"
    p = BASE / r[0]
    return p.read_text(encoding="utf-8") if p.exists() else f"文件缺失: {r[0]}"


def kb_get_figures(doc_id: str) -> str:
    """获取文章配图的本地路径、OCR、结构化说明与图中关系。

    Args:
        doc_id: kb_search 结果中的 doc_id
    """
    _load()
    rows = _conn.execute(
        """
        SELECT figure_id, seq, image_path, source_url, section, ocr_text,
               description, entities_json, relations_json, status
        FROM figures WHERE doc_id=? ORDER BY seq
        """,
        (doc_id,),
    ).fetchall()
    if not rows:
        return f"该文章没有已处理的配图: {doc_id}"
    keys = (
        "figure_id", "seq", "image_path", "source_url", "section", "ocr_text",
        "description", "entities", "relations", "status",
    )
    figures = []
    for row in rows:
        value = dict(zip(keys, row))
        value["entities"] = json.loads(value["entities"] or "[]")
        value["relations"] = json.loads(value["relations"] or "[]")
        if value["image_path"]:
            value["image_path"] = str(BASE / value["image_path"])
        figures.append(value)
    return json.dumps(figures, ensure_ascii=False, indent=2)


def kb_context() -> str:
    """获取可选的本地上下文(用户是谁、业务目标、系统现状)。做任何方案评估前先读这个,
    再用 kb_search 找业界对标实践。"""
    if CONTEXT_FILE.exists():
        return CONTEXT_FILE.read_text(encoding="utf-8")
    return "本地上下文文档尚未创建（可复制 extra-docs/local-context.example.md 为 local-context.md）。"


def kb_stats() -> str:
    """知识库统计:文档数、公司分布、标签分布(用于确定过滤条件的可用取值)。"""
    _load()
    n_docs, n_chunks = _conn.execute(
        "SELECT (SELECT COUNT(*) FROM docs), (SELECT COUNT(*) FROM chunks)").fetchone()
    comp = _conn.execute(
        "SELECT company, COUNT(*) FROM docs GROUP BY company ORDER BY 2 DESC LIMIT 20").fetchall()
    tags = _conn.execute(
        "SELECT tag, COUNT(*) FROM docs GROUP BY tag ORDER BY 2 DESC LIMIT 20").fetchall()
    return (f"docs={n_docs} chunks={n_chunks}\n\n公司: "
            + ", ".join(f"{c}({n})" for c, n in comp)
            + "\n标签: " + ", ".join(f"{t}({n})" for t, n in tags))


def _get_mcp():
    """Load the optional MCP transport only when starting the MCP service."""
    global _mcp
    if _mcp is None:
        from mcp.server.fastmcp import FastMCP

        _mcp = FastMCP("sgt-kb")
        for tool in (kb_search, kb_get_doc, kb_get_figures, kb_context, kb_stats):
            _mcp.tool()(tool)
    return _mcp


def __getattr__(name):
    # Preserve `from sgt_kb.service.kb_server import mcp` without requiring MCP for API/helpers.
    if name == "mcp":
        return _get_mcp()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def main() -> None:
    import argparse

    argparse.ArgumentParser(description="Run the local SGT KB MCP service.").parse_args()
    _get_mcp().run()


if __name__ == "__main__":
    main()
