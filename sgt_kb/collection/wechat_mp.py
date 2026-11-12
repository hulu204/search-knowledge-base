# /// script
# requires-python = ">=3.10"
# dependencies = ["requests", "beautifulsoup4", "lxml", "markdownify"]
# ///
"""公众号历史文章采集:走公众平台后台「引用文章」接口(searchbiz/appmsg)。

需要你自己的公众号登录态(mp.weixin.qq.com 后台的 cookie + token),写入
.wechat_mp_auth.json(见 README「公众号批量采集」)。三个子命令:

  resolve   把 wechat_targets.csv 里的公众号名解析成 fakeid(缓存进 state)
  backfill  翻历史文章列表,断点续跑,命中主题过滤的追加进 crawl_manifest.csv
  poll      每个号只看第一页,新文章直接调 ingest_url 入库(增量)

频控说明:该接口官方限速,连续翻页约几十页后返回 ret=200013(freq control),
脚本会保存断点退出,过 1-2 小时再跑即可继续。默认单次最多 --max-pages 页、
每页间隔 15-25s,请不要调得更激进。
"""
import argparse
import csv
import json
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

from sgt_kb.paths import ROOT

BASE = ROOT
AUTH_FILE = BASE / ".wechat_mp_auth.json"
TARGETS_FILE = BASE / "wechat_targets.csv"
STATE_FILE = BASE / "ingestion" / "wechat_mp_state.json"
DISCOVERED_FILE = BASE / "ingestion" / "wechat_discovered.csv"
MANIFEST = BASE / "crawl_manifest.csv"
SHANGHAI = ZoneInfo("Asia/Shanghai")
RATE_LIMIT_EXIT = 75
AUTH_EXPIRED_EXIT = 76

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

# 只收「搜索相关」:核心词直接命中;次级词(召回/排序等)在不含推荐/广告语境时命中
CORE_KEYWORDS = [
    "搜索", "检索", "查询", "query", "Query", "搜一搜", "search", "Search",
    "索引", "倒排", "BM25", "爬虫", "抓取", "spider", "Spider", "收录",
    "时效性", "新鲜度", "相关性", "RAG", "rag", "问答", "意图", "DeepSearch",
]
SECONDARY_KEYWORDS = [
    "召回", "排序", "rerank", "Rerank", "向量", "embedding", "Embedding", "ANN", "语义",
]
RECAD_WORDS = ["推荐", "广告", "营销", "用增", "增长", "投放"]
NEG_WORDS = ["招聘", "招募", "议题", "峰会", "大会", "报名", "直播", "日程",
             "专场", "志愿者", "征稿", "门票", "抽奖"]
FALSE_POSITIVE_PATTERNS = [
    "时间索引", "位置索引", "意图债", "查询首页", "查询页面",
]

# backfill 按这些词在每个号内搜标题(接口 query 参数),不做全量翻页
SEARCH_QUERIES = ["搜索", "检索", "召回", "排序", "相关性", "索引",
                  "爬虫", "时效性", "query", "RAG", "向量", "问答"]


class AuthExpired(Exception):
    pass


class WechatApiError(Exception):
    pass


class FreqControl(Exception):
    pass


def load_auth() -> dict:
    if not AUTH_FILE.exists():
        raise AuthExpired(
            f"缺少 {AUTH_FILE.name}:登录 https://mp.weixin.qq.com 后台,"
            "从任意后台请求里复制 Cookie 和 URL 上的 token 参数,写成\n"
            '  {"cookie": "...", "token": "..."}'
        )
    auth = json.loads(AUTH_FILE.read_text())
    if not auth.get("cookie") or not auth.get("token"):
        raise AuthExpired("auth 文件需要 cookie 和 token 两个字段")
    return auth


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"accounts": {}}


def save_state(state: dict):
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2))


def rate_limit_remaining(state: dict) -> int:
    value = (state.get("rate_limit") or {}).get("retry_after", "")
    if not value:
        return 0
    try:
        retry_after = datetime.fromisoformat(value)
    except ValueError:
        return 0
    return max(0, int((retry_after - datetime.now(SHANGHAI)).total_seconds()))


def record_rate_limit(state: dict, **context) -> None:
    from datetime import timedelta

    now = datetime.now(SHANGHAI)
    state["rate_limit"] = {
        **context,
        "detected_at": now.isoformat(timespec="seconds"),
        "retry_after": (now + timedelta(hours=2)).isoformat(timespec="seconds"),
    }
    save_state(state)


def clear_rate_limit(state: dict) -> None:
    if state.pop("rate_limit", None) is not None:
        save_state(state)


def load_targets() -> list[dict]:
    if not TARGETS_FILE.exists():
        sys.exit(f"缺少 {TARGETS_FILE.name}")
    return list(csv.DictReader(TARGETS_FILE.open(encoding="utf-8")))


def api_get(session: requests.Session, auth: dict, url: str, params: dict) -> dict:
    params = {**params, "token": auth["token"], "lang": "zh_CN", "f": "json", "ajax": "1"}
    try:
        r = session.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as exc:
        status = exc.response.status_code if exc.response is not None else "network"
        raise WechatApiError(f"公众号接口请求失败(status={status})") from None
    except ValueError:
        raise WechatApiError("公众号接口返回了无效 JSON") from None
    ret = (data.get("base_resp") or {}).get("ret", 0)
    if ret == 200013:
        raise FreqControl()
    if ret in (200003, -6):  # session 失效
        raise AuthExpired(f"登录态失效(ret={ret})")
    if ret != 0:
        raise WechatApiError(f"公众号接口返回 ret={ret}")
    return data


def make_session(auth: dict) -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": UA,
        "Cookie": auth["cookie"],
        "Referer": "https://mp.weixin.qq.com/",
    })
    return s


def norm_title(s: str) -> str:
    return re.sub(r"[\s\|｜\-—【】\[\]()（）!！?？:：，,。.'\"“”‘’]+", "", s).lower()


def manifest_titles() -> set:
    titles = set()
    if MANIFEST.exists():
        with MANIFEST.open(encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                titles.add(norm_title(row["title"]))
    return titles


def clean_title(title: str) -> str:
    return re.sub(r"</?em>", "", title).strip()


def keyword_matches(title: str, keyword: str) -> bool:
    if re.fullmatch(r"[A-Za-z0-9]+", keyword):
        return bool(re.search(
            rf"(?<![A-Za-z0-9]){re.escape(keyword)}(?![A-Za-z0-9])",
            title,
            re.IGNORECASE,
        ))
    return keyword in title


def title_matches(title: str) -> bool:
    title = clean_title(title)
    if any(k in title for k in NEG_WORDS + FALSE_POSITIVE_PATTERNS):
        return False
    if "相关性" in title and "因果" in title and not any(
        keyword in title for keyword in ("搜索", "检索", "排序", "召回", "推荐")
    ):
        return False
    if any(keyword_matches(title, keyword) for keyword in CORE_KEYWORDS):
        return True
    return (any(keyword_matches(title, keyword) for keyword in SECONDARY_KEYWORDS)
            and not any(k in title for k in RECAD_WORDS))


def cmd_resolve(args):
    auth = load_auth()
    state = load_state()
    session = make_session(auth)
    for t in load_targets():
        name = t["name"].strip()
        acc = state["accounts"].setdefault(name, {})
        acc.update({"company": t["company"], "mode": t["mode"]})
        if acc.get("fakeid"):
            print(f"已缓存 {name} -> {acc['fakeid']}")
            continue
        data = api_get(session, auth, "https://mp.weixin.qq.com/cgi-bin/searchbiz",
                       {"action": "search_biz", "begin": 0, "count": 5, "query": name})
        cands = data.get("list", [])
        hit = next((c for c in cands if c.get("nickname") == name), cands[0] if cands else None)
        if not hit:
            print(f"!! 未找到公众号: {name}")
            continue
        acc["fakeid"] = hit["fakeid"]
        acc["nickname"] = hit.get("nickname", name)
        print(f"{name} -> {hit['fakeid']} ({hit.get('nickname')})")
        save_state(state)
        time.sleep(3 + random.random() * 2)
    save_state(state)
    return 0


def _parse_items(data: dict) -> tuple[list[dict], int]:
    """兼容 app_msg_list 直出与 publish_page 两种返回形态。"""
    items, total = [], 0
    if data.get("app_msg_list"):
        items = data["app_msg_list"]
        total = data.get("app_msg_cnt", 0)
    elif data.get("publish_page"):
        page = json.loads(data["publish_page"])
        total = page.get("total_count", 0)
        for pub in page.get("publish_list", []):
            info = json.loads(pub["publish_info"]) if isinstance(pub.get("publish_info"), str) else pub.get("publish_info", {})
            for msg in info.get("appmsgex", []):
                items.append(msg)
    return items, total


def _discovered_writer():
    exists = DISCOVERED_FILE.exists()
    DISCOVERED_FILE.parent.mkdir(exist_ok=True)
    fh = DISCOVERED_FILE.open("a", newline="", encoding="utf-8")
    w = csv.writer(fh)
    if not exists:
        w.writerow(["account", "company", "title", "date", "url", "matched"])
    return fh, w


def cmd_backfill(args):
    auth = load_auth()
    state = load_state()
    remaining = rate_limit_remaining(state)
    if remaining:
        print(f"!! 微信接口冷却中,约 {remaining // 60 + 1} 分钟后重试")
        return RATE_LIMIT_EXIT
    session = make_session(auth)
    existing = manifest_titles()
    if DISCOVERED_FILE.exists():
        for row in csv.DictReader(DISCOVERED_FILE.open(encoding="utf-8")):
            existing.add(norm_title(row["title"]))
    names = [args.account] if args.account else [t["name"] for t in load_targets()]
    fh, w = _discovered_writer()
    manifest_fh = MANIFEST.open("a", newline="", encoding="utf-8")
    manifest_w = csv.writer(manifest_fh)
    pages_done = 0
    try:
        for name in names:
            acc = state["accounts"].get(name) or {}
            if not acc.get("fakeid"):
                print(f"跳过 {name}(先跑 resolve)")
                continue
            qstate = acc.setdefault("queries", {})
            for query in SEARCH_QUERIES:
                qs = qstate.setdefault(query, {"begin": 0, "done": False})
                if qs["done"]:
                    continue
                while pages_done < args.max_pages:
                    try:
                        data = api_get(session, auth, "https://mp.weixin.qq.com/cgi-bin/appmsg",
                                       {"action": "list_ex", "begin": qs["begin"], "count": 5,
                                        "fakeid": acc["fakeid"], "type": 9, "query": query})
                    except FreqControl:
                        print(f"!! 频控(ret=200013),断点已存({name}/{query} begin={qs['begin']}),1-2 小时后再跑")
                        record_rate_limit(
                            state, command="backfill", account=name,
                            query=query, begin=qs["begin"],
                        )
                        return RATE_LIMIT_EXIT
                    clear_rate_limit(state)
                    items, total = _parse_items(data)
                    if not items:
                        qs["done"] = True
                        save_state(state)
                        break
                    for it in items:
                        title = clean_title(it.get("title") or "")
                        link = it.get("link", "")
                        ts = it.get("create_time") or it.get("update_time") or 0
                        date = datetime.fromtimestamp(int(ts), SHANGHAI).strftime("%Y-%m-%d") if ts else ""
                        matched = title_matches(title)
                        if norm_title(title) not in existing:
                            existing.add(norm_title(title))
                            w.writerow([name, acc["company"], title, date, link, int(matched)])
                            if matched:
                                manifest_w.writerow([acc["company"], title, args.tag_default, date, link, "wechat-mp"])
                    qs["begin"] += len(items)
                    pages_done += 1
                    save_state(state)
                    print(f"{name}/{query}: {qs['begin']}/{total}", flush=True)
                    time.sleep(15 + random.random() * 10)
                if pages_done >= args.max_pages:
                    print(f"达到本次页数上限 {args.max_pages},断点已存,再跑继续")
                    return 0
            print(f"{name} 全部查询词完成")
    finally:
        fh.close()
        manifest_fh.close()
    print("提示:回填的新条目已进 crawl_manifest.csv(origin=wechat-mp),"
          "接着跑 `uv run crawl.py` 抓正文、`uv run build_index.py` 建索引")
    return 0


def cmd_poll(args):
    auth = load_auth()
    state = load_state()
    remaining = rate_limit_remaining(state)
    if remaining:
        print(f"!! 微信接口冷却中,约 {remaining // 60 + 1} 分钟后重试")
        return RATE_LIMIT_EXIT
    session = make_session(auth)
    sys.path.insert(0, str(BASE))
    from sgt_kb.collection.ingest_url import ingest
    ingested = []
    failures = []
    rate_limited = False
    for t in load_targets():
        name = t["name"].strip()
        acc = state["accounts"].get(name) or {}
        if not acc.get("fakeid"):
            print(f"跳过 {name}(先跑 resolve)")
            continue
        try:
            data = api_get(session, auth, "https://mp.weixin.qq.com/cgi-bin/appmsg",
                           {"action": "list_ex", "begin": 0, "count": 5,
                            "fakeid": acc["fakeid"], "type": 9, "query": ""})
        except FreqControl:
            print("!! 频控,poll 中止,稍后再试")
            record_rate_limit(
                state, command="poll", account=name, query="", begin=0,
            )
            rate_limited = True
            break
        clear_rate_limit(state)
        items, _ = _parse_items(data)
        for it in items:
            title = (it.get("title") or "").strip()
            link = it.get("link", "")
            if not link:
                continue
            if acc.get("mode") != "all" and not title_matches(title):
                continue
            try:
                result = ingest(
                    link, company=acc["company"], tag=args.tag_default,
                    origin="wechat-poll", skip_index=True,
                    title=title,
                )
            except Exception as exc:
                failures.append((name, title, f"{type(exc).__name__}: {exc}"))
                print(f"!! {name}: {title[:40]} 入库失败: {exc}")
                continue
            if result["status"] == "ingested":
                ingested.append(result["title"])
                print(f"+ {name}: {title[:50]}")
        time.sleep(5 + random.random() * 3)
    if ingested:
        import subprocess
        subprocess.run(["uv", "run", str(BASE / "build_index.py")], cwd=BASE, check=True)
        print(f"本次新入库 {len(ingested)} 篇,索引已更新")
    else:
        print("无新文章")
    if failures:
        print(f"本轮单篇失败 {len(failures)} 篇,其余文章已继续处理")
    return RATE_LIMIT_EXIT if rate_limited else 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("resolve")
    b = sub.add_parser("backfill")
    b.add_argument("--account", help="只回填这个号")
    b.add_argument("--max-pages", type=int, default=30, help="本次最多翻多少页(每页 5 篇)")
    b.add_argument("--tag-default", default="待分类")
    o = sub.add_parser("poll")
    o.add_argument("--tag-default", default="待分类")
    args = p.parse_args()
    try:
        return {"resolve": cmd_resolve, "backfill": cmd_backfill, "poll": cmd_poll}[args.cmd](args)
    except AuthExpired as exc:
        print(f"!! {exc}:请重新登录 mp.weixin.qq.com 并运行本地授权续期工具")
        return AUTH_EXPIRED_EXIT
    except WechatApiError as exc:
        print(f"!! {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
