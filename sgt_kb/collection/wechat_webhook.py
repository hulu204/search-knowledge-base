# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "cryptography",
#   "requests",
#   "beautifulsoup4",
#   "lxml",
#   "markdownify",
# ]
# ///
"""WeChat Official Account callback: verify, extract URLs, enqueue, respond fast."""
import argparse
import base64
import hashlib
import hmac
import os
import re
import struct
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit
from xml.etree import ElementTree

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from sgt_kb.collection.ingestion_queue import enqueue

URL_RE = re.compile(r"https?://[^\s<>'\"]+")
MAX_BODY = 1024 * 1024
ALLOWED_HOSTS = {"mp.weixin.qq.com"}


def signature(token: str, timestamp: str, nonce: str, encrypted: str = "") -> str:
    pieces = [token, timestamp, nonce]
    if encrypted:
        pieces.append(encrypted)
    return hashlib.sha1("".join(sorted(pieces)).encode()).hexdigest()


def valid_signature(
    expected: str,
    token: str,
    timestamp: str,
    nonce: str,
    encrypted: str = "",
) -> bool:
    return bool(expected) and hmac.compare_digest(
        expected, signature(token, timestamp, nonce, encrypted)
    )


def parse_xml(raw: bytes) -> dict[str, str]:
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("unsafe XML")
    root = ElementTree.fromstring(raw)
    return {child.tag: child.text or "" for child in root}


def extract_urls(message: dict[str, str]) -> list[str]:
    candidates = []
    if message.get("MsgType") == "link":
        candidates.extend(URL_RE.findall(message.get("Url", "")))
    elif message.get("MsgType") == "text":
        candidates.extend(URL_RE.findall(message.get("Content", "")))
    output = []
    for value in candidates:
        value = value.rstrip(".,;:!?，。；：！？、)]}")
        if urlsplit(value).hostname in ALLOWED_HOSTS and value not in output:
            output.append(value)
    return output


def _pkcs7_unpad(value: bytes) -> bytes:
    size = value[-1]
    if size < 1 or size > 32 or value[-size:] != bytes([size]) * size:
        raise ValueError("invalid PKCS#7 padding")
    return value[:-size]


def decrypt_wechat(ciphertext: str, encoding_aes_key: str, app_id: str) -> bytes:
    key = base64.b64decode(encoding_aes_key + "=")
    if len(key) != 32:
        raise ValueError("WECHAT_ENCODING_AES_KEY 长度错误")
    encrypted = base64.b64decode(ciphertext)
    decryptor = Cipher(algorithms.AES(key), modes.CBC(key[:16])).decryptor()
    plain = _pkcs7_unpad(decryptor.update(encrypted) + decryptor.finalize())
    if len(plain) < 20:
        raise ValueError("encrypted payload too short")
    message_length = struct.unpack("!I", plain[16:20])[0]
    message = plain[20 : 20 + message_length]
    received_app_id = plain[20 + message_length :].decode()
    if app_id and not hmac.compare_digest(received_app_id, app_id):
        raise ValueError("AppID 不匹配")
    return message


class WeChatHandler(BaseHTTPRequestHandler):
    server_version = "sgt-kb-wechat/1.0"

    def _query(self):
        return parse_qs(urlsplit(self.path).query)

    def _send(self, status: int, body: str):
        payload = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _credentials(self):
        return (
            os.environ.get("WECHAT_TOKEN", ""),
            os.environ.get("WECHAT_ENCODING_AES_KEY", ""),
            os.environ.get("WECHAT_APP_ID", ""),
        )

    def do_GET(self):
        if urlsplit(self.path).path == "/health":
            self._send(200, "ok")
            return
        if urlsplit(self.path).path != "/wechat":
            self._send(404, "not found")
            return
        token, aes_key, app_id = self._credentials()
        query = self._query()
        timestamp = query.get("timestamp", [""])[0]
        nonce = query.get("nonce", [""])[0]
        echostr = query.get("echostr", [""])[0]
        msg_sig = query.get("msg_signature", [""])[0]
        expected = msg_sig or query.get("signature", [""])[0]
        encrypted = echostr if msg_sig else ""
        if not token or not valid_signature(
            expected, token, timestamp, nonce, encrypted
        ):
            self._send(403, "invalid signature")
            return
        if msg_sig:
            if not aes_key:
                self._send(500, "WECHAT_ENCODING_AES_KEY is required")
                return
            try:
                echostr = decrypt_wechat(echostr, aes_key, app_id).decode()
            except Exception:
                self._send(400, "invalid encrypted echo")
                return
        self._send(200, echostr)

    def do_POST(self):
        if urlsplit(self.path).path != "/wechat":
            self._send(404, "not found")
            return
        token, aes_key, app_id = self._credentials()
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > MAX_BODY:
            self._send(413, "invalid body size")
            return
        raw = self.rfile.read(length)
        query = self._query()
        timestamp = query.get("timestamp", [""])[0]
        nonce = query.get("nonce", [""])[0]
        try:
            outer = parse_xml(raw)
            encrypted = outer.get("Encrypt", "")
            expected = (
                query.get("msg_signature", [""])[0]
                if encrypted
                else query.get("signature", [""])[0]
            )
            if not token or not valid_signature(
                expected, token, timestamp, nonce, encrypted
            ):
                self._send(403, "invalid signature")
                return
            if encrypted:
                if not aes_key:
                    raise ValueError("WECHAT_ENCODING_AES_KEY is required")
                raw = decrypt_wechat(encrypted, aes_key, app_id)
            message = parse_xml(raw)
            urls = extract_urls(message)
            message_id = message.get("MsgId", "")
            for index, url in enumerate(urls):
                dedup_id = f"{message_id}:{index}" if message_id else ""
                enqueue(url, source="wechat-official-account", source_message_id=dedup_id)
        except Exception:
            self._send(400, "invalid request")
            return
        self._send(200, "success")

    def log_message(self, fmt, *args):
        print(f"{self.client_address[0]} {fmt % args}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    if not os.environ.get("WECHAT_TOKEN"):
        raise SystemExit("请先设置 WECHAT_TOKEN")
    server = ThreadingHTTPServer((args.host, args.port), WeChatHandler)
    print(f"WeChat callback listening on http://{args.host}:{args.port}/wechat")
    server.serve_forever()


if __name__ == "__main__":
    main()
