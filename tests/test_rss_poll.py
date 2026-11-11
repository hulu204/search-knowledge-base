import sys
import unittest
from unittest import mock

import ingest_url
import rss_poll


class RssPollTest(unittest.TestCase):
    def test_feed_date_parses_rfc822(self) -> None:
        self.assertEqual(
            "2026-08-20",
            rss_poll._feed_date("Thu, 20 Aug 2026 08:30:00 +0800"),
        )

    def test_full_feed_content_is_used_and_one_failure_does_not_stop_feed(self) -> None:
        content = "<p>RAG 检索正文</p>" * 80
        xml = f"""<rss xmlns:content="http://purl.org/rss/1.0/modules/content/"><channel>
        <item><title>RAG 检索失败样例</title><link>https://mp.weixin.qq.com/s/first</link>
        <pubDate>Thu, 20 Aug 2026 08:30:00 +0800</pubDate><content:encoded><![CDATA[{content}]]></content:encoded></item>
        <item><title>向量检索成功样例</title><link>https://mp.weixin.qq.com/s/second</link>
        <pubDate>Thu, 20 Aug 2026 09:30:00 +0800</pubDate><content:encoded><![CDATA[{content}]]></content:encoded></item>
        </channel></rss>""".encode()
        response = mock.Mock(content=xml)
        response.raise_for_status.return_value = None
        success = {
            "status": "ingested",
            "title": "向量检索成功样例",
        }
        with (
            mock.patch.object(rss_poll, "FEEDS", {"测试号": ("测试", "feed")}),
            mock.patch.object(rss_poll.requests, "get", return_value=response),
            mock.patch.object(rss_poll.time, "sleep"),
            mock.patch.object(rss_poll, "_finish") as finish,
            mock.patch.object(
                ingest_url,
                "ingest_html_content",
                side_effect=[RuntimeError("first failed"), success],
            ) as from_feed,
            mock.patch.object(sys, "argv", ["rss_poll.py", "--defer-index"]),
        ):
            rss_poll.main()

        self.assertEqual(2, from_feed.call_count)
        finish.assert_called_once_with(["向量检索成功样例"], True)
        self.assertEqual("2026-08-20", from_feed.call_args.kwargs["date"])
        self.assertEqual("wechat-rss-feedbody", from_feed.call_args.kwargs["origin"])


if __name__ == "__main__":
    unittest.main()
