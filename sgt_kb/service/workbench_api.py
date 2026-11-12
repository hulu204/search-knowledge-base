# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.0", "FlagEmbedding>=1.3", "torch", "numpy", "scipy"]
# ///
"""Local HTTP adapter for the SGT knowledge-base workbench.

The browser only receives explicitly requested local knowledge-base results.
The service binds to loopback and does not send corpus content to a third party.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


from sgt_kb.paths import ROOT

BASE = ROOT
DB = BASE / "index" / "kb.sqlite"
CONTEXT_FILE = BASE / "extra-docs" / "local-context.md"
HOST = "127.0.0.1"
PORT = 8766
MAX_BODY_BYTES = 1_000_000
SEARCH_LOCK = threading.Lock()


def _db() -> sqlite3.Connection:
    if not DB.exists():
        raise FileNotFoundError(f"知识库索引不存在: {DB}")
    return sqlite3.connect(DB)


def _stats() -> dict[str, object]:
    with _db() as conn:
        docs, chunks = conn.execute(
            "SELECT (SELECT COUNT(*) FROM docs), (SELECT COUNT(*) FROM chunks)"
        ).fetchone()
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        figures = (
            conn.execute("SELECT COUNT(*) FROM figures").fetchone()[0]
            if "figures" in tables
            else 0
        )
        companies = conn.execute(
            """
            SELECT company, COUNT(*) AS count
            FROM docs
            WHERE TRIM(COALESCE(company, '')) != ''
            GROUP BY company
            ORDER BY count DESC, company
            LIMIT 16
            """
        ).fetchall()
        tags = conn.execute(
            """
            SELECT tag, COUNT(*) AS count
            FROM docs
            WHERE TRIM(COALESCE(tag, '')) != ''
            GROUP BY tag
            ORDER BY count DESC, tag
            LIMIT 16
            """
        ).fetchall()
        company_count = conn.execute(
            "SELECT COUNT(DISTINCT company) FROM docs WHERE TRIM(COALESCE(company, '')) != ''"
        ).fetchone()[0]
        tag_count = conn.execute(
            "SELECT COUNT(DISTINCT tag) FROM docs WHERE TRIM(COALESCE(tag, '')) != ''"
        ).fetchone()[0]
    return {
        "docs": int(docs),
        "chunks": int(chunks),
        "figures": int(figures),
        "company_count": int(company_count),
        "tag_count": int(tag_count),
        "companies": [{"name": name, "count": count} for name, count in companies],
        "tags": [{"name": name, "count": count} for name, count in tags],
    }


def _get_doc(doc_id: str) -> dict[str, str]:
    with _db() as conn:
        row = conn.execute(
            """
            SELECT path, title, company, tag, date, url
            FROM docs
            WHERE doc_id = ?
            """,
            (doc_id,),
        ).fetchone()
    if not row:
        raise ValueError(f"doc_id 不存在: {doc_id}")
    path = (BASE / row[0]).resolve()
    if BASE not in path.parents:
        raise ValueError("文档路径越界")
    if not path.exists():
        raise FileNotFoundError(f"文档文件缺失: {row[0]}")
    return {
        "doc_id": doc_id,
        "title": row[1] or "",
        "company": row[2] or "",
        "tag": row[3] or "",
        "date": row[4] or "",
        "url": row[5] or "",
        "markdown": path.read_text(encoding="utf-8"),
    }


class WorkbenchHandler(BaseHTTPRequestHandler):
    server_version = "SGTKBWorkbench/1.0"

    def log_message(self, format: str, *args: object) -> None:
        print(f"[workbench] {self.address_string()} - {format % args}")

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict[str, object]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValueError("Content-Length 非法") from exc
        if length > MAX_BODY_BYTES:
            raise ValueError("请求体过大")
        if length == 0:
            return {}
        payload = json.loads(self.rfile.read(length))
        if not isinstance(payload, dict):
            raise ValueError("请求体必须是 JSON object")
        return payload

    def _handle(self, action) -> None:
        try:
            action()
        except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
            self._json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        except Exception as exc:
            print(f"[workbench] error: {type(exc).__name__}: {exc}")
            self._json(
                {"error": f"本地服务异常: {type(exc).__name__}: {exc}"},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:
        self._handle(self._get)

    def _get(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self._json({"status": "ok"})
        elif parsed.path == "/api/stats":
            self._json(_stats())
        elif parsed.path == "/api/context":
            text = (
                CONTEXT_FILE.read_text(encoding="utf-8")
                if CONTEXT_FILE.exists()
                else "本地上下文尚未创建。"
            )
            self._json({"markdown": text})
        elif parsed.path == "/api/doc":
            doc_id = parse_qs(parsed.query).get("doc_id", [""])[0].strip()
            if not doc_id:
                raise ValueError("缺少 doc_id")
            self._json(_get_doc(doc_id))
        else:
            self._json({"error": "接口不存在"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        self._handle(self._post)

    def _post(self) -> None:
        path = urlparse(self.path).path
        payload = self._body()

        if path == "/api/search":
            query = str(payload.get("query", "")).strip()
            if not query:
                raise ValueError("query 不能为空")
            top_k = max(1, min(int(payload.get("top_k", 6)), 20))
            from sgt_kb.service.kb_server import search_knowledge_base

            with SEARCH_LOCK:
                results = search_knowledge_base(
                    query=query,
                    top_k=top_k,
                    company=str(payload.get("company", "")),
                    tag=str(payload.get("tag", "")),
                )
            self._json({"query": query, "results": results})
        else:
            self._json({"error": "接口不存在"}, HTTPStatus.NOT_FOUND)


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), WorkbenchHandler)
    print(f"SGT KB workbench API: http://{HOST}:{PORT}")
    print("知识库内容只在本机 loopback 接口中流转。")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
