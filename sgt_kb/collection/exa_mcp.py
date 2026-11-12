"""Minimal Streamable HTTP client for the configured Exa MCP server."""
from __future__ import annotations

import json
import os

import requests


DEFAULT_EXA_MCP_URL = (
    "https://mcp.exa.ai/mcp?tools=web_search_advanced_exa,web_fetch_exa"
)
MAX_RESPONSE_BYTES = 20 * 1024 * 1024


def decode_mcp_response(response: requests.Response) -> dict:
    response.raise_for_status()
    if len(response.content) > MAX_RESPONSE_BYTES:
        raise RuntimeError("Exa MCP response exceeded 20 MiB")
    if "text/event-stream" not in response.headers.get("content-type", ""):
        payload = response.json()
        if not isinstance(payload, dict):
            raise TypeError("Exa MCP returned a non-object response")
        return payload
    for event in response.text.split("\n\n"):
        data = "\n".join(
            line[6:] for line in event.split("\n") if line.startswith("data: ")
        )
        if data:
            payload = json.loads(data)
            if not isinstance(payload, dict):
                raise TypeError("Exa MCP returned a non-object SSE event")
            return payload
    raise RuntimeError("Exa MCP response contained no data event")


class ExaMcpClient:
    def __init__(self, url: str | None = None) -> None:
        self.url = url or os.environ.get("EXA_MCP_URL") or DEFAULT_EXA_MCP_URL
        self.session = requests.Session()
        self.session.trust_env = False
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        self._request_id = 0
        self._initialize()

    def _post(self, payload: dict, timeout: int = 60) -> requests.Response:
        return self.session.post(
            self.url, headers=self.headers, json=payload, timeout=timeout
        )

    def _initialize(self) -> None:
        self._request_id += 1
        response = self._post({
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "sgt-kb", "version": "1.0"},
            },
        }, timeout=30)
        payload = decode_mcp_response(response)
        if payload.get("error"):
            raise RuntimeError(f"Exa MCP initialize failed: {payload['error']}")
        session_id = response.headers.get("mcp-session-id", "")
        if not session_id:
            raise RuntimeError("Exa MCP did not return a session id")
        self.headers["Mcp-Session-Id"] = session_id
        self._post({
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        }, timeout=30).raise_for_status()

    def call_tool(self, name: str, arguments: dict) -> dict:
        self._request_id += 1
        payload = decode_mcp_response(self._post({
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        }))
        if payload.get("error"):
            raise RuntimeError(f"Exa MCP tool failed: {payload['error']}")
        content = payload.get("result", {}).get("content", [])
        text = next(
            (item.get("text", "") for item in content if item.get("type") == "text"),
            "",
        )
        result = json.loads(text)
        if not isinstance(result, dict):
            raise TypeError("Exa MCP tool returned non-object JSON")
        return result

    def search(self, query: str, num_results: int, since: str) -> list[dict]:
        result = self.call_tool("web_search_advanced_exa", {
            "query": query,
            "numResults": num_results,
            "type": "auto",
            "startPublishedDate": since,
            "moderation": True,
            "enableHighlights": True,
            "highlightsMaxCharacters": 800,
            "textMaxCharacters": 1200,
        })
        rows = result.get("results", [])
        if not isinstance(rows, list):
            raise TypeError("Exa MCP search results were not a list")
        return [row for row in rows if isinstance(row, dict)]
