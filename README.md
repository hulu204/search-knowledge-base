# sgt-kb

本地知识库：把公开的搜索 / 推荐 / RAG 技术文章，走完「爬取 → 解析切块 → 混合索引 → 带引用检索」。

在线演示（用仓库内公开样例做标题和摘要检索）：[hulu204.github.io/sgt-kb](https://hulu204.github.io/sgt-kb/)

完整的 dense + sparse 混合检索、全文阅读和工作台需要在本地运行，并自行下载 [bge-m3](https://huggingface.co/BAAI/bge-m3) 到 `models/bge-m3/`。

## 流水线

```text
公开文章 / URL / RSS
    → 清洗与切块（标题树递归，按 token 预算在标题和段落边界切开，无 overlap）
    → 本地 bge-m3：dense 向量 + sparse 词权重
    → 应用层 RRF 融合
    → 结果带标题、来源、doc_id 和原文链接
```

本地 Web 工作台只绑定 loopback，语料默认留在本机。

## 仓库里有什么

- 采集、切块、索引、MCP 和服务端代码
- 约 2400 篇公开技术文章正文（微信公众号、Elastic、LanceDB、个人技术博客等）
- 配图 OCR / 说明 sidecar（`figures/`）
- 可点开的 GitHub Pages 演示

语料起点是 [Doragd/Algorithm-Practice-in-Industry](https://github.com/Doragd/Algorithm-Practice-in-Industry)，后续又补充了公开网页和公众号技术文。版权归原作者，这里只做检索演示，请通过每篇文章的 `url` 访问原文。

## 仓库里没有什么

- embedding 模型（约 2GB，需自行下载）
- 配图原文件（约 881MB，不放入 git）
- 已构建的本地索引（克隆后用 `build_index.py` 生成）
- 微信 / 微信读书等登录态，以及任何密钥
- 公司内部文档、未授权网盘文件或提取码

## 本地快速开始

```bash
# 1. 准备模型
# 将 BAAI/bge-m3 放到 models/bge-m3/

# 2. 用仓库内的公开文章构建索引
uv run build_index.py

# 3. 启动本地工作台（http://localhost:3917）
cd workbench && npm install && cd ..
python3 start_workbench.py
```

也可以单条入库公开链接：

```bash
uv run ingest_url.py 'https://www.elastic.co/search-labs/blog/hybrid-search-elasticsearch'
uv run build_index.py
```

可选的持续采集还有公开 RSS（`rss_poll.py`）和 Wayback 历史页（`wayback_wechat.py`）。微信公众号后台登录态是可选的本机能力，凭据只应写在被 gitignore 的 `.wechat_mp_auth.json`，不要提交到仓库。

## MCP

把 `kb_server.py` 加到 Claude Code 或 Codex 后，可用 `kb_search`、`kb_get_doc`、`kb_get_figures`、`kb_stats`。需要本地上下文时，复制 `extra-docs/local-context.example.md` 为 `local-context.md`。

## License

代码为 MIT。`articles/` 与 `figures/` 中的内容版权归原作者，仅供检索演示。
