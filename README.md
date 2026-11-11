# sgt-kb

本地知识库：把公开的搜索 / 推荐 / RAG 技术文章，走完「爬取 → 解析切块 → 混合索引 → 带引用检索」。

在线演示：[hulu204.github.io/sgt-kb](https://hulu204.github.io/sgt-kb/)（**离线静态词法检索**：搜索公开文章入库时存储的全部 chunks，显示命中的完整 chunk 和引用）。Pages 的检索在浏览器内完成；本地 bge-m3 dense / sparse + RRF 检索需另行运行。

完整的 dense + sparse 混合检索、全文阅读和工作台需要在本地运行，并自行下载 [bge-m3](https://huggingface.co/BAAI/bge-m3) 到 `models/bge-m3/`。

## 文档目录

`articles/` 现有 **2421** 篇公开技术文章（按仓库内实际文件统计，已排除网盘元数据占位）。按主题和来源浏览：

- [目录总览](catalog.md)（主题、来源机构、原文站点）
- [按主题完整清单](catalog/by-topic.md)
- [按来源机构完整清单](catalog/by-source.md)

主题（frontmatter `tag`，未合并近义项）：

[搜索（565）](catalog/by-topic.md#搜索565) · [召回（318）](catalog/by-topic.md#召回318) · [工程相关（239）](catalog/by-topic.md#工程相关239) · [推荐（172）](catalog/by-topic.md#推荐172) · [问答/RAG（139）](catalog/by-topic.md#问答rag139) · [索引构建（136）](catalog/by-topic.md#索引构建136) · [排序（127）](catalog/by-topic.md#排序127) · [搜索/RAG（127）](catalog/by-topic.md#搜索rag127) · [广告（96）](catalog/by-topic.md#广告96) · [爬虫抓取（93）](catalog/by-topic.md#爬虫抓取93) · [评测（80）](catalog/by-topic.md#评测80) · [查询理解（75）](catalog/by-topic.md#查询理解75) · [搜索相关性（48）](catalog/by-topic.md#搜索相关性48) · [RAG（34）](catalog/by-topic.md#rag34) · [精排&CXR预估（27）](catalog/by-topic.md#精排cxr预估27) · [冷启动（15）](catalog/by-topic.md#冷启动15) · [多目标&多任务（15）](catalog/by-topic.md#多目标多任务15) · [时效性（15）](catalog/by-topic.md#时效性15) · [因果推断（13）](catalog/by-topic.md#因果推断13) · [粗排（10）](catalog/by-topic.md#粗排10) · [生成式（9）](catalog/by-topic.md#生成式9) · [重排（8）](catalog/by-topic.md#重排8) · [内容理解（7）](catalog/by-topic.md#内容理解7) · [推荐&图网络（7）](catalog/by-topic.md#推荐图网络7) · [知识图谱（6）](catalog/by-topic.md#知识图谱6) · [其他（5）](catalog/by-topic.md#其他5) · [问答（4）](catalog/by-topic.md#问答4) · [推荐&特征工程（3）](catalog/by-topic.md#推荐特征工程3) · [用增（3）](catalog/by-topic.md#用增3) · [用户增长（3）](catalog/by-topic.md#用户增长3) · [搜素（2）](catalog/by-topic.md#搜素2) · [数据科学（2）](catalog/by-topic.md#数据科学2) · [热点挖掘（2）](catalog/by-topic.md#热点挖掘2) · [粗排&精排（2）](catalog/by-topic.md#粗排精排2) · [偏好挖掘（1）](catalog/by-topic.md#偏好挖掘1) · [图推荐（1）](catalog/by-topic.md#图推荐1) · [多任务学习（1）](catalog/by-topic.md#多任务学习1) · [多场景排序（1）](catalog/by-topic.md#多场景排序1) · [大模型（1）](catalog/by-topic.md#大模型1) · [广告&混排（1）](catalog/by-topic.md#广告混排1) · [推荐&CXR预估（1）](catalog/by-topic.md#推荐cxr预估1) · [推荐&增量学习（1）](catalog/by-topic.md#推荐增量学习1) · [推荐&跨域（1）](catalog/by-topic.md#推荐跨域1) · [搜索生态（1）](catalog/by-topic.md#搜索生态1) · [文案挖掘（1）](catalog/by-topic.md#文案挖掘1) · [用户挖掘（1）](catalog/by-topic.md#用户挖掘1) · [粗排相关性（1）](catalog/by-topic.md#粗排相关性1) · [自动发现（1）](catalog/by-topic.md#自动发现1)

主要来源机构（frontmatter `company`，未合并同一公司的不同署名；其余 102 个见[完整来源清单](catalog/by-source.md)）：

[DataFun（234）](catalog/by-source.md#datafun234) · [Elastic（221）](catalog/by-source.md#elastic221) · [Sease（131）](catalog/by-source.md#sease131) · [Marginalia（121）](catalog/by-source.md#marginalia121) · [eugeneyan（121）](catalog/by-source.md#eugeneyan121) · [百度（102）](catalog/by-source.md#百度102) · [LanceDB（99）](catalog/by-source.md#lancedb99) · [阿里妈妈（96）](catalog/by-source.md#阿里妈妈96) · [阿里淘系（96）](catalog/by-source.md#阿里淘系96) · [Tunkelang（93）](catalog/by-source.md#tunkelang93) · [京东（82）](catalog/by-source.md#京东82) · [CommonCrawl（80）](catalog/by-source.md#commoncrawl80) · [腾讯（68）](catalog/by-source.md#腾讯68) · [快手（59）](catalog/by-source.md#快手59) · [美团（52）](catalog/by-source.md#美团52) · [softwaredoug（45）](catalog/by-source.md#softwaredoug45) · [Vespa（44）](catalog/by-source.md#vespa44) · [得物（43）](catalog/by-source.md#得物43)

每条目录项链到仓库内正文，并附原文链接。版权归原作者，请通过原文链接访问。

## 流水线

```text
公开文章 / URL / RSS
    → 清洗与切块（标题树递归，按 token 预算在标题和段落边界切开，无 overlap）
    → 本地 bge-m3：dense 向量 + sparse 词权重
    → 应用层 RRF 融合
    → 返回索引内命中 chunk 原文，带标题、来源、doc_id、chunk_id 和原文链接
```

本地 Web 工作台只绑定 loopback，语料默认留在本机。上面这条流水线描述的是本地完整系统；GitHub Pages 使用入库 chunks 的静态导出做词法检索。两种界面均直接显示存储的命中 chunk；展示层只转义 HTML 或高亮匹配，不在查询时切片或生成摘要。

## 仓库里有什么

- 采集、切块、索引、MCP 和服务端代码
- 2421 篇公开技术文章正文（微信公众号、Elastic、LanceDB、个人技术博客等），目录见上
- 配图 OCR / 说明 sidecar（`figures/`）
- 可点开的 GitHub Pages 演示（完整入库 chunks 的离线静态词法检索）

语料起点是 [Doragd/Algorithm-Practice-in-Industry](https://github.com/Doragd/Algorithm-Practice-in-Industry)，后续又补充了公开网页和公众号技术文。版权归原作者，这里只做检索演示，请通过每篇文章的 `url` 访问原文。

实现代码按职责放在 `sgt_kb/` 中：`collection/` 负责采集、解析与队列，`indexing/` 负责入库、切块与静态导出，`retrieval/` 放检索评分辅助逻辑，`service/` 提供 MCP 和本地 HTTP 服务。前端保留在 `workbench/` 和 `docs/`（Pages）。根目录同名 Python 文件是兼容入口，原有命令和 imports 可继续使用。

## 仓库里没有什么

- embedding 模型（约 2GB，需自行下载）
- 配图原文件（约 881MB，不放入 git）
- SQLite / 向量索引（克隆后用 `build_index.py` 生成；Pages 静态 JSON 导出除外）
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

## 重建 Pages 静态数据

无需模型、网络或新增依赖，只读取本仓库 `articles/` 和已有的 `figures/` 文本 sidecar：

```bash
python3 build_index.py --lexical-only --public-only
python3 export_pages.py
python3 -m http.server 8000 --directory docs
```

第一步复用同一个 `load_docs` 清洗和标题树 `chunk_text` 入库流程，将 chunks 写入独立的 `index/public-static/kb.sqlite`。由于公开 checkout 不含 bge-m3 tokenizer，离线入库显式使用 `utf8-bytes-v1` 容量计数（UTF-8 字节数）；这会与 bge-m3 token 计数产生不同的分块边界，不代表生产索引。默认混合索引仍使用原来的 bge-m3 tokenizer，二者禁止写入同一索引目录。

第二步仅从 SQLite 原样导出 `docs` 元数据和 `chunks.text` / `chunk_id` / `doc_id` / `seq` 到 `docs/demo-index.json`，不重新读取文章制作摘要。导出器拒绝包含 `extra-docs/` 的索引。也可将公开语料的混合索引原样导出：`uv run build_index.py --public-only` 后执行 `python3 export_pages.py --db index/kb.sqlite`。

当前静态数据含 2,402 篇符合既有入库条件的文档、68,833 个 chunks；全部 2,421 篇文章和目录保持完整，原流程会跳过 metadata-only 或清洗后不足 200 字符的正文。Pages 搜索全部 chunks，并选每篇文章得分最高的命中块展示。中文连续词串按完整词串匹配，不拆成单字；中英混合词支持 Unicode 归一化，`查询理解` / `Query理解` / `Query Understanding` 使用通用双语同义词组。排序综合命中词组覆盖、标题匹配和有限的词频，不使用 embedding 或云服务。

验证命令（现有 Python 运行依赖需已安装；静态导出和 Node 测试只用标准库）：

```bash
python3 -m unittest discover -s tests -v
node --test tests/*.test.mjs
```

## MCP

把 `kb_server.py` 加到 Claude Code 或 Codex 后，可用 `kb_search`、`kb_get_doc`、`kb_get_figures`、`kb_stats`。需要本地上下文时，复制 `extra-docs/local-context.example.md` 为 `local-context.md`。

## License

代码为 MIT。`articles/` 与 `figures/` 中的内容版权归原作者，仅供检索演示。
