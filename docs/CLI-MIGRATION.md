# Python 入口迁移

28 个根目录 Python 兼容文件已经删除，实现在 `sgt_kb/` 中保留一份。在仓库根目录运行 `python3 -m sgt_kb --help`；安装 `python3 -m pip install -e '.[collection,indexing,service]'` 后，也可将下表中的 `python3 -m sgt_kb` 换成 `sgt-kb`。静态导出只用标准库，不需要安装可选依赖。

旧脚本的参数原样接在新命令后；定时任务、MCP 配置和外部调用也应更新。工作目录仍为本仓库。视频转写另装 `.[video]`。包内的 inline dependency metadata 只是依赖说明；统一入口不自动安装它们。

| 旧根目录入口 | 新命令或包导入 |
| --- | --- |
| `build_index.py` | `python3 -m sgt_kb build-index` |
| `crawl.py` | `python3 -m sgt_kb crawl` |
| `daily_update.py` | `python3 -m sgt_kb daily-update` |
| `en_poll.py` | `python3 -m sgt_kb en-poll` |
| `english_sources.py` | `sgt_kb.collection.english_sources`（导入辅助模块） |
| `exa_discover.py` | `python3 -m sgt_kb exa-discover` |
| `exa_mcp.py` | `sgt_kb.collection.exa_mcp`（导入辅助模块） |
| `export_pages.py` | `python3 -m sgt_kb export-pages` |
| `figure_pipeline.py` | `python3 -m sgt_kb figure-pipeline` |
| `ingest_url.py` | `python3 -m sgt_kb ingest-url` |
| `ingestion_queue.py` | `python3 -m sgt_kb ingestion-queue` |
| `kb_gate.py` | `python3 -m sgt_kb kb-gate` |
| `kb_server.py` | `python3 -m sgt_kb kb-server` |
| `oneapi_wechat.py` | `python3 -m sgt_kb oneapi-wechat` |
| `review_queue.py` | `python3 -m sgt_kb review-queue` |
| `rss_poll.py` | `python3 -m sgt_kb rss-poll` |
| `start_workbench.py` | `python3 -m sgt_kb start-workbench` |
| `video_ingest.py` | `python3 -m sgt_kb video-ingest` |
| `wayback_catchup.py` | `python3 -m sgt_kb wayback-catchup` |
| `wayback_wechat.py` | `python3 -m sgt_kb wayback-wechat` |
| `wechat_auth_update.py` | `python3 -m sgt_kb wechat-auth-update`（仍从 stdin 读 cURL） |
| `wechat_catchup.py` | `python3 -m sgt_kb wechat-catchup` |
| `wechat_identity.py` | `python3 -m sgt_kb wechat-identity` |
| `wechat_mp.py` | `python3 -m sgt_kb wechat-mp` |
| `wechat_public_registry.py` | `sgt_kb.collection.wechat_public_registry`（导入辅助模块） |
| `wechat_webhook.py` | `python3 -m sgt_kb wechat-webhook` |
| `weread_mp.py` | `python3 -m sgt_kb weread-mp` |
| `workbench_api.py` | `python3 -m sgt_kb workbench-api` |

Python 导入也需要改成包名，例如 `from sgt_kb.collection import crawl`、`from sgt_kb.indexing.build_index import chunk_text`、`from sgt_kb.service import kb_server`。检索时效评分辅助函数位于 `sgt_kb.retrieval.recency`。

Pages 导出不再先用 `build-index --lexical-only` 重建语料。应从生产 SQLite 的原始 chunks 或受控中间文件导出；具体命令、公开字段过滤和分片格式见 [STORED-EXPORT.md](STORED-EXPORT.md)。
