# /// script
# requires-python = ">=3.10"
# dependencies = ["requests", "beautifulsoup4", "lxml", "markdownify"]
# ///
"""Refresh WeChat MP auth from a Chrome "Copy as cURL" request.

The cURL text is read from stdin. Secrets are never printed or passed through
process arguments. The new auth is verified before atomically replacing the
local mode-0600 auth file.
"""
from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from wechat_mp import (
    AUTH_FILE,
    AuthExpired,
    FreqControl,
    WechatApiError,
    api_get,
    make_session,
)


def extract_auth(curl_text: str) -> dict[str, str]:
    try:
        tokens = shlex.split(curl_text.replace("\\\n", " "))
    except ValueError as exc:
        raise ValueError(f"无法解析 cURL: {exc}") from exc

    cookie = ""
    urls: list[str] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token in {"-H", "--header"} and index + 1 < len(tokens):
            header = tokens[index + 1]
            name, separator, value = header.partition(":")
            if separator and name.strip().lower() == "cookie":
                cookie = value.strip()
            index += 2
            continue
        if token.startswith("https://mp.weixin.qq.com/"):
            urls.append(token)
        index += 1

    auth_token = ""
    for url in urls:
        values = parse_qs(urlsplit(url).query).get("token") or []
        if values and values[0]:
            auth_token = values[0]
            break
    if not cookie:
        raise ValueError("cURL 中没有 Cookie 请求头")
    if not auth_token:
        raise ValueError("cURL URL 中没有 token 参数")
    return {"cookie": cookie, "token": auth_token}


def verify_auth(auth: dict[str, str]) -> None:
    session = make_session(auth)
    try:
        api_get(
            session,
            auth,
            "https://mp.weixin.qq.com/cgi-bin/searchbiz",
            {"action": "search_biz", "begin": 0, "count": 1, "query": "腾讯技术工程"},
        )
    except FreqControl:
        # ret=200013 proves the session was authenticated even though rate-limited.
        return
    except AuthExpired as exc:
        raise ValueError("复制的登录态已失效，请重新扫码登录后再复制") from exc
    finally:
        session.close()


def save_auth(auth: dict[str, str], path: Path = AUTH_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        json.dump(auth, handle, ensure_ascii=False)
        handle.write("\n")
        temp_path = Path(handle.name)
    try:
        os.chmod(temp_path, 0o600)
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def kickstart_catchup() -> None:
    subprocess.run(
        [
            "launchctl", "kickstart",
            f"gui/{os.getuid()}/com.lcy.sgt-kb-wechat-catchup",
        ],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main() -> int:
    curl_text = sys.stdin.read()
    if not curl_text.strip():
        print("剪贴板为空：请先在 Chrome Network 中复制任意 mp.weixin.qq.com 请求为 cURL")
        return 2
    try:
        auth = extract_auth(curl_text)
        verify_auth(auth)
        save_auth(auth)
    except ValueError as exc:
        print(f"续期失败：{exc}")
        return 1
    except WechatApiError:
        print("续期失败：公众号接口暂时不可用，旧授权未修改")
        return 1
    except Exception:
        print("续期失败：验证或写入失败，旧授权未修改")
        return 1
    print("登录态已验证并安全更新，正在恢复公众号补抓任务。")
    kickstart_catchup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
