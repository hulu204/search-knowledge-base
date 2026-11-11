# /// script
# requires-python = ">=3.10"
# dependencies = ["FlagEmbedding>=1.3", "torch", "numpy", "scipy", "tqdm", "tokenizers"]
# ///
"""Build hybrid index (bge-m3 dense + sparse) from sgt-kb/articles/*.md.

Incremental: unchanged docs (by content hash) reuse cached embeddings.
Outputs under sgt-kb/index/:
  kb.sqlite    - docs & chunks metadata + chunk text
  dense.npy    - float16 [n_chunks, 1024], L2-normalized
  sparse.npz   - CSR [n_chunks, vocab_size] lexical weights
"""
import hashlib
import json
import re
import sqlite3
import sys
from pathlib import Path

import numpy as np
from scipy import sparse as sp

BASE = Path(__file__).parent
ARTICLES = BASE / "articles"
EXTRA = BASE / "extra-docs"          # 手工补充的文档也一并索引
FIGURES = BASE / "figures"
INDEX = BASE / "index"
INDEX.mkdir(exist_ok=True)
DB = INDEX / "kb.sqlite"
MODEL_DIR = BASE / "models" / "bge-m3"
VOCAB_SIZE = 250002                  # bge-m3 (xlm-roberta) vocab
# 标题树自顶向下递归切块：按 tokenizer 计数，优先在标题和段落边界切开，无 overlap。
SECTION_CAPACITY = 1800              # 容量是合并额度,不是填充目标
PARAGRAPH_CAPACITY = 200             # 低于此的节点不构成独立主题,向兄弟合并
EMBED_WINDOW = 8192                  # bge-m3 硬窗口


def parse_frontmatter(text: str):
    meta = {}
    body = text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip("'\"")
            body = text[end + 4:]
    return meta, body


_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


def _figure_text(record: dict) -> str:
    if record.get("status") != "ready":
        return ""
    lines = [f"[图像 {record.get('figure_id', '')}]"]
    if record.get("section"):
        lines.append(f"所属章节：{record['section']}")
    if record.get("description"):
        lines.append(f"图像说明：{record['description']}")
    if record.get("ocr_text"):
        lines.append(f"图中文字：{record['ocr_text']}")
    entities = record.get("entities") or []
    if entities:
        lines.append("图中实体：" + "；".join(map(str, entities)))
    relations = record.get("relations") or []
    if relations:
        relation_text = []
        for relation in relations:
            if isinstance(relation, dict):
                relation_text.append(
                    f"{relation.get('source', '')} "
                    f"{relation.get('relation', '')} "
                    f"{relation.get('target', '')}".strip()
                )
            else:
                relation_text.append(str(relation))
        lines.append("图中关系：" + "；".join(filter(None, relation_text)))
    if record.get("source_url"):
        lines.append(f"图片来源：{record['source_url']}")
    return "\n".join(lines)


def enrich_figures(body: str, figures: list[dict]) -> str:
    by_source = {record.get("source_url"): record for record in figures}
    by_path = {record.get("image_path"): record for record in figures}

    def replace(match):
        target = match.group(2)
        record = by_source.get(target)
        if record is None:
            normalized = target.removeprefix("../").removeprefix("./")
            record = by_path.get(normalized)
        return _figure_text(record) if record else ""

    return _IMAGE_RE.sub(replace, body)


def clean_body(body: str, figures: list[dict] | None = None) -> str:
    body = enrich_figures(body, figures or [])
    body = _IMAGE_RE.sub("", body)                              # unprocessed images
    body = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", body)      # links -> text
    body = re.sub(r"\*{2,4}", "", body)
    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip()


_SENTENCE_RE = re.compile(r"[^.!?。！？;；]+(?:[.!?。！？;；]+|$)")
_PUNCT_SPLIT_RE = re.compile(r"[,，:：、\s]+")

_tokenizer = None


def _tok(text: str) -> int:
    global _tokenizer
    if _tokenizer is None:
        from tokenizers import Tokenizer
        _tokenizer = Tokenizer.from_file(str(MODEL_DIR / "tokenizer.json"))
    return max(1, len(_tokenizer.encode(text).ids)) if text else 0


def _md_blocks(text: str):
    """markdown -> [(type, level, text)] blocks; code fences kept whole."""
    blocks, para, in_code = [], [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
            para.append(line)
            continue
        if in_code:
            para.append(line)
            continue
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            if para:
                blocks.append(("paragraph", 0, "\n".join(para).strip())); para = []
            blocks.append(("heading", len(m.group(1)), line.strip()))
        elif not line.strip():
            if para:
                blocks.append(("paragraph", 0, "\n".join(para).strip())); para = []
        else:
            para.append(line)
    if para:
        blocks.append(("paragraph", 0, "\n".join(para).strip()))
    return [(t, lv, tx) for t, lv, tx in blocks if tx]


def _decompose(text: str):
    """Oversized block -> pieces: paragraph -> line -> sentence -> punct-seg."""
    pieces = []
    for para in filter(None, (p.strip() for p in re.split(r"\n{2,}", text))):
        if _tok(para) <= SECTION_CAPACITY:
            pieces.append(para)
            continue
        lines = [ln.strip() for ln in para.splitlines() if ln.strip()]
        targets = lines if len(lines) > 1 else [para]
        for t in targets:
            if _tok(t) <= SECTION_CAPACITY:
                pieces.append(t)
                continue
            for s in (m.group().strip() for m in _SENTENCE_RE.finditer(t)):
                if not s:
                    continue
                if _tok(s) <= EMBED_WINDOW:
                    pieces.append(s)
                else:                     # 上游是 drop-doc;语料库场景改为标点切+截断
                    pieces.extend(seg for seg in _PUNCT_SPLIT_RE.split(s)
                                  if seg and _tok(seg) <= EMBED_WINDOW)
    return pieces


def _build_forest(blocks):
    """[(type, level, units)] -> section forest, immune to skipped levels."""
    def parse(i, parent_level):
        nodes = []
        while i < len(blocks):
            typ, lv, units = blocks[i]
            if typ != "heading":
                nodes.append({"units": units, "children": [], "section": False})
                i += 1
                continue
            if lv <= parent_level:
                break
            heading = {"units": units, "children": [], "section": False}
            body, i = parse(i + 1, lv)
            children = [heading] + body
            nodes.append({
                "units": [u for c in children for u in c["units"]],
                "children": children, "section": True})
        return nodes, i
    forest, _ = parse(0, 0)
    # 单个顶层 section = 文章自己的标题包裹,解包一层
    if len(forest) == 1 and forest[0]["section"]:
        forest = forest[0]["children"]
    return forest


def _units_tok(units):
    return _tok("\n\n".join(units))


def _holds_heading(nodes):
    return any(c["section"] for n in nodes for c in n["children"])


def _merge_siblings(children, root):
    groups = []
    for node in children:
        can_merge = (groups
                     and _units_tok([u for n in groups[-1] for u in n["units"]])
                     < PARAGRAPH_CAPACITY
                     and not (root and node["section"]
                              and any(n["section"] for n in groups[-1])))
        if can_merge:
            groups[-1].append(node)
        else:
            groups.append([node])
    if len(groups) > 1:
        tail_units = [u for n in groups[-1] for u in n["units"]]
        if _units_tok(tail_units) < PARAGRAPH_CAPACITY:
            merged = groups[-2] + groups[-1]
            merged_units = [u for n in merged for u in n["units"]]
            root_block = (root and groups[-1][0]["section"]
                          and any(n["section"] for n in groups[-2]))
            if _units_tok(merged_units) <= SECTION_CAPACITY and not root_block:
                groups[-2] = merged
                groups.pop()
    return groups


def _pack(units):
    chunks = [[]]
    for u in units:
        if chunks[-1] and _units_tok(chunks[-1] + [u]) > SECTION_CAPACITY:
            chunks.append([])
        chunks[-1].append(u)
    return chunks


def _split_node(node, prefix, root):
    units = prefix + node["units"]
    if _units_tok(units) <= SECTION_CAPACITY and not _holds_heading([node]):
        return [units]
    if node["children"]:
        return _split_children(node["children"], prefix, root=False)
    return _pack(units)


def _split_children(children, prefix, root):
    chunks = []
    for i, group in enumerate(_merge_siblings(children, root)):
        gp = prefix if i == 0 else []
        units = gp + [u for n in group for u in n["units"]]
        if _units_tok(units) <= SECTION_CAPACITY and not _holds_heading(group):
            chunks.append(units)
            continue
        lead = gp + [u for n in group[:-1] for u in n["units"]]
        chunks.extend(_split_node(group[-1], lead, root))
    return chunks


def chunk_text(text: str):
    """按标题树递归切块，优先保留语义边界。"""
    blocks = []
    for typ, lv, tx in _md_blocks(text):
        units = [tx] if _tok(tx) <= SECTION_CAPACITY else _decompose(tx)
        blocks.append((typ, lv, units))
    if not blocks:
        return []
    forest = _build_forest(blocks)
    chunks = _split_children(forest, [], root=True)
    return [c for c in ("\n\n".join(u) for u in chunks) if len(c) >= 80]


def load_docs():
    docs = []
    for d in (ARTICLES, EXTRA):
        if not d.exists():
            continue
        for p in sorted(d.glob("*.md")):
            raw = p.read_text(encoding="utf-8")
            meta, body = parse_frontmatter(raw)
            if meta.get("note", "").startswith("metadata-only"):
                continue
            figure_path = FIGURES / f"{p.stem}.json"
            figure_raw = (
                figure_path.read_text(encoding="utf-8")
                if figure_path.exists()
                else ""
            )
            figures = json.loads(figure_raw) if figure_raw else []
            body = clean_body(body, figures)
            if len(body) < 200:
                continue
            docs.append({
                "doc_id": p.stem,
                "path": str(p.relative_to(BASE)),
                "title": meta.get("title", p.stem),
                "company": meta.get("company", ""),
                "tag": meta.get("tag", ""),
                "date": meta.get("date", ""),
                "url": meta.get("url", ""),
                "hash": hashlib.md5(
                    (
                        raw
                        + "\nFIGURES\n"
                        + figure_raw
                        + ("\nFIGURE_INDEX_FORMAT=1" if figure_raw else "")
                    ).encode()
                ).hexdigest(),
                "body": body,
                "figures": figures,
            })
    return docs


def embed(texts):
    import torch
    from FlagEmbedding import BGEM3FlagModel
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    model = BGEM3FlagModel(str(MODEL_DIR), use_fp16=(dev != "cpu"), devices=dev)
    out = model.encode(
        texts, batch_size=4, max_length=2048,
        return_dense=True, return_sparse=True, return_colbert_vecs=False,
    )
    dense = np.asarray(out["dense_vecs"], dtype=np.float32)
    rows, cols, vals = [], [], []
    for i, lw in enumerate(out["lexical_weights"]):
        for tok, w in lw.items():
            rows.append(i); cols.append(int(tok)); vals.append(float(w))
    sparse = sp.csr_matrix(
        (vals, (rows, cols)), shape=(len(texts), VOCAB_SIZE), dtype=np.float32)
    return dense, sparse


def main():
    conn = sqlite3.connect(DB)
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS docs(
        doc_id TEXT PRIMARY KEY, path TEXT, title TEXT, company TEXT,
        tag TEXT, date TEXT, url TEXT, hash TEXT);
    CREATE TABLE IF NOT EXISTS chunks(
        chunk_id INTEGER PRIMARY KEY, doc_id TEXT, seq INTEGER, text TEXT);
    CREATE TABLE IF NOT EXISTS figures(
        figure_id TEXT PRIMARY KEY, doc_id TEXT, seq INTEGER,
        image_path TEXT, source_url TEXT, section TEXT, ocr_text TEXT,
        description TEXT, entities_json TEXT, relations_json TEXT,
        hash TEXT, status TEXT);
    """)
    docs = load_docs()
    print(f"docs loaded: {len(docs)}")

    # ---- snapshot old state (before any table rewrite) ----
    old_hash = dict(conn.execute("SELECT doc_id, hash FROM docs"))
    old_chunks = {}                                   # doc_id -> [(chunk_id, seq, text)]
    for cid, doc_id, seq, txt in conn.execute(
            "SELECT chunk_id, doc_id, seq, text FROM chunks ORDER BY doc_id, seq"):
        old_chunks.setdefault(doc_id, []).append((cid, seq, txt))
    have_matrices = (INDEX / "dense.npy").exists() and (INDEX / "sparse.npz").exists()
    if have_matrices:
        dense_old = np.load(INDEX / "dense.npy").astype(np.float32)
        sparse_old = sp.load_npz(INDEX / "sparse.npz").tocsr()

    def cached(d):
        return (have_matrices and old_hash.get(d["doc_id"]) == d["hash"]
                and d["doc_id"] in old_chunks)

    todo = [d for d in docs if not cached(d)]
    print(f"unchanged: {len(docs) - len(todo)}, to embed: {len(todo)}")

    doc_new_chunks = {}
    new_texts, new_owner = [], []
    for d in todo:
        cks = chunk_text(d["body"])
        doc_new_chunks[d["doc_id"]] = cks
        header = f"《{d['title']}》 {d['company']} {d['tag']} {d['date']}\n"
        for c in cks:
            new_texts.append(header + c)
            new_owner.append(d["doc_id"])
    print(f"new chunks to embed: {len(new_texts)}")

    if new_texts:
        dense_new, sparse_new = embed(new_texts)
        owner_rows = {}
        for i, o in enumerate(new_owner):
            owner_rows.setdefault(o, []).append(i)

    # ---- rebuild tables + matrices in doc order ----
    conn.execute("DELETE FROM docs")
    conn.execute("DELETE FROM chunks")
    conn.execute("DELETE FROM figures")
    dense_parts, sparse_parts = [], []
    next_id = 0
    for d in docs:
        conn.execute("INSERT INTO docs VALUES(?,?,?,?,?,?,?,?)",
                     (d["doc_id"], d["path"], d["title"], d["company"],
                      d["tag"], d["date"], d["url"], d["hash"]))
        for figure in d["figures"]:
            conn.execute(
                "INSERT INTO figures VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    figure.get("figure_id", ""),
                    d["doc_id"],
                    figure.get("seq", 0),
                    figure.get("image_path", ""),
                    figure.get("source_url", ""),
                    figure.get("section", ""),
                    figure.get("ocr_text", ""),
                    figure.get("description", ""),
                    json.dumps(figure.get("entities", []), ensure_ascii=False),
                    json.dumps(figure.get("relations", []), ensure_ascii=False),
                    figure.get("content_hash", ""),
                    figure.get("status", ""),
                ),
            )
        if d["doc_id"] in doc_new_chunks:
            texts = doc_new_chunks[d["doc_id"]]
            idxs = owner_rows[d["doc_id"]]
            dense_parts.append(dense_new[idxs])
            sparse_parts.append(sparse_new[idxs])
        else:
            rows = old_chunks[d["doc_id"]]
            texts = [t for _, _, t in rows]
            cids = [c for c, _, _ in rows]
            dense_parts.append(dense_old[cids])
            sparse_parts.append(sparse_old[cids])
        for seq, t in enumerate(texts):
            conn.execute("INSERT INTO chunks VALUES(?,?,?,?)",
                         (next_id, d["doc_id"], seq, t))
            next_id += 1

    dense_all = np.vstack(dense_parts) if dense_parts else np.zeros((0, 1024), np.float32)
    norms = np.linalg.norm(dense_all, axis=1, keepdims=True)
    norms[norms == 0] = 1
    dense_all = (dense_all / norms).astype(np.float16)
    sparse_all = (sp.vstack(sparse_parts).tocsr() if sparse_parts
                  else sp.csr_matrix((0, VOCAB_SIZE), dtype=np.float32))

    np.save(INDEX / "dense.npy", dense_all)
    sp.save_npz(INDEX / "sparse.npz", sparse_all)
    conn.commit()
    print(f"index built: {len(docs)} docs, {next_id} chunks, "
          f"dense {dense_all.shape}, sparse nnz={sparse_all.nnz}")


if __name__ == "__main__":
    sys.exit(main())
