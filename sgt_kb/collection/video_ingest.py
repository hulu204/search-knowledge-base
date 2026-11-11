# /// script
# requires-python = ">=3.10"
# dependencies = ["yt-dlp", "faster-whisper", "requests", "FlagEmbedding>=1.3", "torch", "numpy"]
# ///
"""视频转文本入库:B站/YouTube 链接 → 字幕(有则优先)/whisper 转写 → 文章落库。

策略:
- YouTube:先 yt-dlp 拉人工/自动字幕(零计算);拿不到再下音频跑 ASR
- B站:字幕接口大多需登录(可选 env BILI_SESSDATA);默认下音频跑 ASR
- ASR:faster-whisper(默认 large-v3-turbo,int8,本地 CPU;HF_ENDPOINT 默认走 hf-mirror)
- 落库:如果 manifest 里已有该 URL 的行且文章文件是 metadata-only 占位,原地替换正文;
  否则新增 manifest 行(origin=video)。之后跑 build_index.py 即可入索引。

用法:
  uv run video_ingest.py <url> [--title T --company C --tag TAG --date D]
  uv run video_ingest.py --backlog        # 处理 manifest 里所有 bilibili 占位行
  uv run video_ingest.py <url> --model small   # 快速低精度测试
"""
import argparse
import csv
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# hf-mirror 已失效(302 回源站);实测 HF 直连 ~900KB/s 可用

from sgt_kb.paths import ROOT

BASE = ROOT
OUT = BASE / "articles"
MANIFEST = BASE / "crawl_manifest.csv"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def is_bilibili(url): return "bilibili.com" in url
def is_youtube(url): return "youtube.com" in url or "youtu.be" in url


# ---------- 字幕优先 ----------

def youtube_subs(url: str, workdir: Path) -> str | None:
    """尝试拉 YouTube 人工/自动字幕,成功返回纯文本。"""
    cmd = ["yt-dlp", "--skip-download", "--write-sub", "--write-auto-sub",
           "--sub-langs", "zh-Hans,zh,en", "--sub-format", "vtt",
           "-o", str(workdir / "sub"), url]
    r = subprocess.run(cmd, capture_output=True, text=True)
    vtts = list(workdir.glob("sub*.vtt"))
    if not vtts:
        return None
    return vtt_to_text(vtts[0].read_text(encoding="utf-8"))


def vtt_to_text(vtt: str) -> str:
    lines, seen = [], set()
    for ln in vtt.splitlines():
        ln = ln.strip()
        if not ln or "-->" in ln or ln.isdigit() or ln.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
            continue
        ln = re.sub(r"<[^>]+>", "", ln)
        if ln and ln not in seen:      # 自动字幕滚动窗口去重
            seen.add(ln)
            lines.append(ln)
    return "\n".join(lines)


def bilibili_subs(url: str) -> str | None:
    """B站 CC 字幕(多数需登录,SESSDATA 可选)。"""
    import requests
    m = re.search(r"(BV[0-9A-Za-z]+)", url)
    if not m:
        return None
    bvid = m.group(1)
    headers = {"User-Agent": UA, "Referer": "https://www.bilibili.com"}
    if os.environ.get("BILI_SESSDATA"):
        headers["Cookie"] = f"SESSDATA={os.environ['BILI_SESSDATA']}"
    try:
        view = requests.get(f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}",
                            headers=headers, timeout=20).json()
        cid = view["data"]["cid"]
        player = requests.get(f"https://api.bilibili.com/x/player/wbi/v2?bvid={bvid}&cid={cid}",
                              headers=headers, timeout=20).json()
        subs = player.get("data", {}).get("subtitle", {}).get("subtitles", [])
        if not subs:
            return None
        sub_url = subs[0]["subtitle_url"]
        if sub_url.startswith("//"):
            sub_url = "https:" + sub_url
        body = requests.get(sub_url, headers=headers, timeout=20).json()
        return "\n".join(seg["content"] for seg in body.get("body", []))
    except Exception:
        return None


# ---------- ASR 兜底 ----------

def download_audio(url: str, workdir: Path) -> Path | None:
    out = workdir / "audio.m4a"
    cmd = ["yt-dlp", "-f", "ba/b", "-x", "--audio-format", "m4a",
           "-o", str(workdir / "audio.%(ext)s"), url]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-400:], file=sys.stderr)
    cands = list(workdir.glob("audio.*"))
    return cands[0] if cands else None


_whisper = None

# 领域术语引导:whisper 的 initial_prompt 只保留末尾 ~224 token(约 200 汉字),
# 因此按视频动态拼装(基础 + tag + 公司),关键术语放末尾(截断保尾不保头)。
BASE_TERMS = ("pipeline、two-stage、baseline、badcase、benchmark、SOTA、A/B实验、"
              "AUC、GAUC、NDCG、embedding、transformer、attention、LLM、RAG、agent、"
              "scaling law、fine-tune、token、DSSM、双塔模型、i2i、u2i、swing、"
              "faiss、ANN、HNSW、BM25、倒排索引、向量检索、语义召回、多路召回")
TAG_TERMS = {
    "召回": "召回、粗排、truncation、召回率、负采样、hard negative、曝光未点击、内容冷启动",
    "排序": "精排、重排、listwise、pairwise、LTR、learning to rank、position bias、多目标融合",
    "搜索": "query理解、意图识别、查询改写、纠错、相关性、点击模型、session、长尾query",
    "推荐": "CTR、CVR、点击率预估、冷启动、兴趣建模、行为序列、多样性、E&E、探索利用",
    "广告": "出价、竞价、oCPC、oCPM、ROI、eCPM、计费、预算平滑、拍卖机制、DPA",
    "搜索相关性": "相关性、语义匹配、query-doc、BERT交互式、表示式、人工标注、档位",
    "问答/RAG": "RAG、检索增强、chunk、rerank、上下文、知识库、幻觉、引用",
}
COMPANY_TERMS = {
    "小红书": "小红书、REDtech、种草、笔记、社区、UGC",
    "阿里淘系": "淘宝、天猫、主搜、猜你喜欢、有好货、手淘、GMV",
    "美团": "美团、外卖、到店、LBS、商家、交易",
    "快手": "快手、老铁、直播、短视频、单双列",
    "B站": "B站、哔哩哔哩、弹幕、UP主、番剧",
    "京东": "京东、零售、SKU、自营、品类",
    "百度": "百度、大搜、凤巢、贴吧",
}


def build_prompt(meta: dict) -> str:
    parts = ["这是一场搜索推荐广告系统的技术分享,注意专业术语:", BASE_TERMS]
    tag_extra = TAG_TERMS.get(meta.get("tag", ""))
    if tag_extra:
        parts.append(tag_extra)
    comp_extra = COMPANY_TERMS.get(meta.get("company", ""))
    if comp_extra:
        parts.append(comp_extra)
    title = meta.get("title", "")
    if title:
        parts.append(f"本场主题:{title}")
    return "。".join(parts) + "。"


def transcribe(audio: Path, model_name: str, meta: dict | None = None):
    """返回 (text, quality) — quality 含置信度/幻觉/复读指标,供门控用。"""
    global _whisper
    from faster_whisper import WhisperModel
    if _whisper is None:
        _whisper = WhisperModel(model_name, device="cpu", compute_type="int8")
    prompt = build_prompt(meta or {})
    segments, info = _whisper.transcribe(
        str(audio), vad_filter=True, beam_size=5, initial_prompt=prompt)
    paras, cur, last_end = [], [], 0.0
    logprobs, hallu, repeats, total = [], 0, 0, 0
    prev_text, prev_count = None, 0
    for seg in segments:
        total += 1
        logprobs.append(seg.avg_logprob)
        if seg.compression_ratio > 2.4 or seg.no_speech_prob > 0.6:
            hallu += 1
        if seg.text.strip() == prev_text:
            prev_count += 1
            if prev_count >= 2:
                repeats += 1
                continue                    # 连续复读段(whisper 幻觉)直接丢弃
        else:
            prev_text, prev_count = seg.text.strip(), 0
        if cur and (seg.start - last_end > 2.0 or sum(len(s) for s in cur) > 800):
            paras.append("".join(cur)); cur = []
        cur.append(seg.text.strip())
        last_end = seg.end
    if cur:
        paras.append("".join(cur))
    text = "\n\n".join(paras)
    import statistics
    quality = {
        "mean_logprob": round(statistics.mean(logprobs), 3) if logprobs else -9,
        "low_conf_ratio": round(sum(1 for l in logprobs if l < -1.0) / max(total, 1), 3),
        "hallu_ratio": round(hallu / max(total, 1), 3),
        "repeat_ratio": round(repeats / max(total, 1), 3),
        "coverage": round(len(text) / max(info.duration, 1), 2),  # 字符/秒,中文演讲正常 3-6
    }
    print(f"  ASR done: lang={info.language} dur={info.duration:.0f}s paras={len(paras)} quality={quality}")
    return text, quality


def asr_verdict(quality: dict) -> tuple[str, str]:
    """转写质量门控:任何一项过差 → review(落人工队列,不入库)。"""
    problems = []
    if quality["mean_logprob"] < -0.8: problems.append(f"低置信 mean_logprob={quality['mean_logprob']}")
    if quality["low_conf_ratio"] > 0.3: problems.append(f"低置信段占比 {quality['low_conf_ratio']}")
    if quality["hallu_ratio"] > 0.15: problems.append(f"疑似幻觉段占比 {quality['hallu_ratio']}")
    if quality["repeat_ratio"] > 0.1: problems.append(f"复读段占比 {quality['repeat_ratio']}")
    if not 1.5 <= quality["coverage"] <= 12: problems.append(f"字符密度异常 {quality['coverage']}/s")
    return ("review" if problems else "accept"), "; ".join(problems)


# ---------- 落库 ----------

def norm_title(s): return re.sub(r"[\s\|｜\-—【】\[\]()（）!！?？:：，,。.'\"“”‘’]+", "", s).lower()


def find_article_by_url(url: str) -> Path | None:
    key = re.search(r"(BV[0-9A-Za-z]+|v=[\w-]+|youtu\.be/[\w-]+)", url)
    for p in OUT.glob("*.md"):
        head = p.read_text(encoding="utf-8")[:600]
        m = re.search(r"^url:\s*(.+)$", head, re.M)
        if m and (m.group(1).strip() == url or (key and key.group(1) in m.group(1))):
            return p
    return None


def write_doc(url, text, meta, source_note):
    from datetime import datetime
    existing = find_article_by_url(url)
    row = {"company": meta.get("company", "待分类"), "title": meta["title"],
           "tag": meta.get("tag", "搜索"), "date": meta.get("date", ""),
           "url": url, "origin": "video"}
    fm = (f"---\ntitle: {row['title']!r}\ncompany: {row['company']}\ntag: {row['tag']}\n"
          f"date: {row['date']}\nurl: {row['url']}\naccount: \norigin: video\n"
          f"note: transcript:{source_note}\n---\n")
    if existing:
        # 占位文件原地替换,沿用文件名;manifest 行已存在
        existing.write_text(fm + text, encoding="utf-8")
        return existing
    rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8")))
    import hashlib
    t = re.sub(r"[^\w一-鿿]+", "-", row["title"])[:48].strip("-")
    h = hashlib.md5(url.encode()).hexdigest()[:8]
    path = OUT / f"{len(rows):03d}-{t}-{h}.md"
    path.write_text(fm + text, encoding="utf-8")
    with MANIFEST.open("a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=["company", "title", "tag", "date", "url", "origin"]).writerow(row)
    return path


def content_relevance(text: str, title: str) -> str:
    """转写正文抽 3 段过 kb_gate 双质心:多数段相关才放行。"""
    sys.path.insert(0, str(BASE))
    from sgt_kb.indexing.kb_gate import gate_texts
    paras = [p for p in text.split("\n\n") if len(p) > 200]
    if not paras:
        return "review"
    idx = [0, len(paras) // 2, len(paras) - 1]
    samples = [f"{title}。{paras[i][:400]}" for i in dict.fromkeys(idx)]
    verdicts = [v["verdict"] for v in gate_texts(samples)]
    if verdicts.count("reject") >= 2:
        return "reject"
    return "accept" if verdicts.count("accept") >= len(verdicts) / 2 else "review"


def queue_review(url, meta, text, note, reason):
    from datetime import datetime
    d = BASE / "ingestion" / "video_review"
    d.mkdir(parents=True, exist_ok=True)
    import hashlib
    p = d / f"{hashlib.md5(url.encode()).hexdigest()[:8]}.md"
    p.write_text(f"# {meta['title']}\n\nurl: {url}\nnote: {note}\nreason: {reason}\n\n---\n\n{text}",
                 encoding="utf-8")
    rq = BASE / "ingestion" / "review_queue.csv"
    new = not rq.exists()
    with rq.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["company", "title", "date", "url", "margin", "added_at"])
        w.writerow([meta.get("company", ""), meta["title"], meta.get("date", ""),
                    url, f"video:{reason[:60]}", datetime.now().strftime("%Y-%m-%d %H:%M")])
    print(f"  ?? 进人工队列: {reason[:80]} -> {p}")


def process(url, meta, model_name):
    print(f"== {meta.get('title', url)[:60]}")
    with tempfile.TemporaryDirectory() as td:
        workdir = Path(td)
        text, note, quality = None, "", None
        if is_youtube(url):
            text = youtube_subs(url, workdir)
            note = "youtube-subs"
        elif is_bilibili(url):
            text = bilibili_subs(url)
            note = "bilibili-cc"
        if not text or len(text) < 500:
            audio = download_audio(url, workdir)
            if not audio:
                print("  !! 音频下载失败"); return None
            text, quality = transcribe(audio, model_name, meta)
            note = f"whisper-{model_name}"
        if not text or len(text) < 500:
            print("  !! 转写文本过短,放弃"); return None
        # 门控层 1:ASR 置信度/幻觉指标(仅 ASR 路径)
        if quality is not None:
            verdict, reason = asr_verdict(quality)
            if verdict != "accept":
                queue_review(url, meta, text, note, f"ASR质量: {reason}")
                return None
            note += f" logprob={quality['mean_logprob']}"
        # 门控层 2:内容相关性(双质心,抽 3 段)
        rel = content_relevance(text, meta["title"])
        if rel == "reject":
            print("  !! 内容相关性不过关,拒绝"); return None
        if rel == "review":
            queue_review(url, meta, text, note, "内容相关性边界")
            return None
        path = write_doc(url, text, meta, note)
        print(f"  -> {path.name} ({len(text)} chars, {note})")
        return path


def backlog_rows():
    rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8")))
    todo = []
    for r in rows:
        if "bilibili.com" not in r["url"]:
            continue
        p = find_article_by_url(r["url"])
        if p is None or "metadata-only" in p.read_text(encoding="utf-8")[:600]:
            todo.append(r)
    return todo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url", nargs="?")
    ap.add_argument("--backlog", action="store_true", help="处理 manifest 里的 bilibili 占位行")
    ap.add_argument("--model", default="large-v3-turbo")
    ap.add_argument("--title"); ap.add_argument("--company", default="待分类")
    ap.add_argument("--tag", default="搜索"); ap.add_argument("--date", default="")
    args = ap.parse_args()
    if args.backlog:
        todo = backlog_rows()
        print(f"backlog: {len(todo)} 条")
        done = 0
        for r in todo:
            if process(r["url"], r, args.model):
                done += 1
        print(f"完成 {done}/{len(todo)};记得跑 uv run build_index.py")
    elif args.url:
        meta = {"title": args.title or args.url, "company": args.company,
                "tag": args.tag, "date": args.date}
        process(args.url, meta, args.model)
        print("记得跑 uv run build_index.py")
    else:
        ap.error("需要 url 或 --backlog")


if __name__ == "__main__":
    main()
