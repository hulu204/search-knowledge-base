import argparse
import json
import stat
from pathlib import Path
from unittest import mock

import pytest

import weread_mp
from weread_mp import (
    MAX_RESPONSE_BYTES,
    WeReadAuth,
    WeReadClient,
    flatten_groups,
    load_auth,
    parse_content_page,
    parse_curl,
    save_auth,
    select_candidates,
    update_state,
    write_candidates,
)


def test_parse_curl_requires_cookie_and_proof():
    text = """curl 'https://weread.qq.com/web/book/read' \\
      -b 'a=b' \\
      -H 'x-wrpa-0: proof' \\
      -H 'User-Agent: Test Agent' \\
      --data-raw '{}'
    """
    auth = parse_curl(text)
    assert auth.cookie == "a=b"
    assert auth.x_wrpa_0 == "proof"
    assert auth.user_agent == "Test Agent"


def test_parse_curl_rejects_other_host():
    with pytest.raises(ValueError):
        parse_curl("curl 'https://example.com/web/book/read' -b 'a=b' -H 'x-wrpa-0: proof'")


def test_save_auth_is_private(tmp_path):
    path = tmp_path / ".weread_auth.json"
    save_auth(WeReadAuth("a=b", "ua", "proof"), path)
    assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_load_auth_rejects_group_or_world_permissions(tmp_path):
    path = tmp_path / ".weread_auth.json"
    path.write_text(json.dumps({"cookie": "a=b", "x_wrpa_0": "proof"}))
    path.chmod(0o640)
    with pytest.raises(RuntimeError, match="0600"):
        load_auth(path)


class FakeStreamingResponse:
    def __init__(self, chunks, content_length=None):
        self.headers = {}
        if content_length is not None:
            self.headers["Content-Length"] = str(content_length)
        self.chunks = chunks
        self.close = mock.Mock()
        self.raise_for_status = mock.Mock()

    def iter_content(self, chunk_size):
        assert chunk_size == 64 * 1024
        yield from self.chunks


def test_client_rejects_declared_oversize_before_streaming():
    client = WeReadClient(WeReadAuth("a=b", "ua", "proof"), "info")
    response = FakeStreamingResponse([], MAX_RESPONSE_BYTES + 1)
    client.session.get = mock.Mock(return_value=response)

    with pytest.raises(RuntimeError, match="响应过大"):
        client.get("/web/mp/articles", {"offset": 0})

    assert client.session.get.call_args.kwargs["stream"] is True
    response.close.assert_called_once()


def test_client_stops_stream_as_soon_as_body_exceeds_limit(monkeypatch):
    monkeypatch.setattr(weread_mp, "MAX_RESPONSE_BYTES", 5)
    client = WeReadClient(WeReadAuth("a=b", "ua", "proof"), "info")
    response = FakeStreamingResponse([b"123", b"456", pytest.fail])
    client.session.get = mock.Mock(return_value=response)

    with pytest.raises(RuntimeError, match="响应过大"):
        client.get("/web/mp/content", {"reviewId": "r1"})

    response.close.assert_called_once()


def test_flatten_and_select_candidates():
    groups = [{
        "createTime": 1711929600,
        "subReviews": [{
            "reviewId": "r1",
            "review": {"mpInfo": {"title": "向量检索实践", "mp_name": "技术号"}},
        }],
    }]
    articles = flatten_groups(groups)
    selected = select_candidates(articles, "2024-01-01", ("向量",))
    assert len(selected) == 1
    assert selected[0]["review_id"] == "r1"


def test_english_keywords_do_not_match_inside_unrelated_words():
    articles = [
        {"date": "2025-01-01", "title": "Seed Research 最新成果"},
        {"date": "2025-01-01", "title": "Storage Agent Family"},
        {"date": "2025-01-01", "title": "OpenSearch 技术实践"},
        {"date": "2025-01-01", "title": "RAG 检索增强生成"},
    ]

    selected = select_candidates(
        articles,
        "2024-01-01",
        ("search", "rag", "opensearch"),
    )

    assert [item["title"] for item in selected] == [
        "OpenSearch 技术实践",
        "RAG 检索增强生成",
    ]


def test_select_candidates_ignores_blank_keywords():
    articles = [
        {"date": "2025-01-01", "title": "Unrelated article"},
        {"date": "2025-01-01", "title": "RAG 检索增强生成"},
    ]

    selected = select_candidates(articles, "2024-01-01", ("", "  ", " RAG "))

    assert [item["title"] for item in selected] == ["RAG 检索增强生成"]


def test_select_candidates_rejects_all_blank_keywords():
    with pytest.raises(ValueError, match="关键词不能为空"):
        select_candidates([], "2024-01-01", ("", " \t "))


def test_parse_content_page():
    raw = """
    <!doctype html><html><head>
      <meta property="og:url" content="https://mp.weixin.qq.com/s?__biz=x&amp;mid=1&amp;idx=1&amp;sn=y">
    </head><body><h1 id="activity-name">测试文章</h1><div id="js_content"><p>正文</p></div></body></html>
    """
    url, title, content = parse_content_page(raw)
    assert url == "https://mp.weixin.qq.com/s?__biz=x&mid=1&idx=1&sn=y"
    assert title == "测试文章"
    assert "正文" in content


def test_state_and_candidates_are_atomically_published(tmp_path):
    state_path = tmp_path / "state" / "weread_state.json"
    candidate_path = tmp_path / "candidates" / "weread_candidates.csv"
    real_replace = weread_mp.os.replace
    replacements = []

    def record_replace(source, destination):
        replacements.append((source, destination))
        real_replace(source, destination)

    with (
        mock.patch.object(weread_mp, "STATE_FILE", state_path),
        mock.patch.object(weread_mp.os, "replace", side_effect=record_replace),
        mock.patch.object(weread_mp.os, "fsync", wraps=weread_mp.os.fsync) as fsync,
    ):
        update_state({"index_dirty": True})
        write_candidates([], candidate_path)

    assert json.loads(state_path.read_text()) == {"index_dirty": True}
    assert candidate_path.read_text().startswith("account,title,date")
    assert fsync.call_count == 2
    assert len(replacements) == 2
    for source, destination in replacements:
        assert Path(source).parent == Path(destination).parent


def test_dirty_state_retries_index_after_failed_build(tmp_path):
    state_path = tmp_path / "weread_state.json"
    article = {
        "account": "技术号",
        "title": "向量检索实践",
        "date": "2024-04-01",
        "timestamp": 1711929600,
        "review_id": "r1",
        "original_id": "o1",
        "read_num": 1,
        "like_num": 1,
    }
    page = """<!doctype html><html><head>
      <meta property="og:url" content="https://mp.weixin.qq.com/s?x=1">
      </head><body><h1>title</h1><div id="js_content">body</div></body></html>"""
    client = mock.Mock()
    client.enumerate_articles.return_value = [article]
    client.fetch_content.return_value = page
    args = argparse.Namespace(
        account="技术号",
        info_id="info",
        book_id="book",
        since="2024-01-01",
        tag="搜索/RAG",
        keyword=["向量"],
        delay=0,
        dry_run=False,
        skip_images=True,
        skip_index=False,
    )

    with (
        mock.patch.object(weread_mp, "STATE_FILE", state_path),
        mock.patch.object(weread_mp, "load_auth", return_value=WeReadAuth("a", "ua", "p")),
        mock.patch.object(weread_mp, "WeReadClient", return_value=client),
        mock.patch.object(weread_mp, "write_candidates"),
        mock.patch.object(weread_mp.time, "sleep"),
        mock.patch.object(
            weread_mp,
            "ingest_html_content",
            side_effect=[{"status": "ingested"}, {"status": "existing"}],
        ),
        mock.patch.object(
            weread_mp.subprocess,
            "run",
            side_effect=[RuntimeError("build failed"), mock.DEFAULT],
        ) as build_index,
    ):
        with pytest.raises(RuntimeError, match="build failed"):
            weread_mp.sync(args)
        assert json.loads(state_path.read_text())["index_dirty"] is True

        result = weread_mp.sync(args)

    assert result["existing"] == 1
    assert build_index.call_count == 2
    assert json.loads(state_path.read_text())["index_dirty"] is False
