# sgt-kb

本地知识库：把公开的搜索 / 推荐 / RAG 技术文章，走完「爬取 → 解析切块 → 混合索引 → 带引用检索」。

在线演示：[hulu204.github.io/sgt-kb](https://hulu204.github.io/sgt-kb/)（**离线静态词法检索**）。Pages 架构使用小型索引和按需加载的原始 chunk 分片；生产 SQLite 导出尚未集成时，页面会明确显示“等待生产导出”，不使用旧 UTF-8 字节分块作为默认语料。本地 bge-m3 dense / sparse + RRF 检索需另行运行。

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
- GitHub Pages 静态词法检索界面、受控导出器和分片加载器

语料起点是 [Doragd/Algorithm-Practice-in-Industry](https://github.com/Doragd/Algorithm-Practice-in-Industry)，后续又补充了公开网页和公众号技术文。版权归原作者，这里只做检索演示，请通过每篇文章的 `url` 访问原文。

实现代码按职责放在 `sgt_kb/` 中：`collection/` 负责采集、解析与队列，`indexing/` 负责入库、切块与静态导出，`retrieval/` 放检索评分辅助逻辑，`service/` 提供 MCP 和本地 HTTP 服务。前端保留在 `workbench/` 和 `docs/`（Pages）。根目录的 28 个 Python 兼容文件已删除。统一入口为 `python3 -m sgt_kb COMMAND`，安装后也可用 `sgt-kb COMMAND`；Python 导入使用完整包名。旧命令和导入的对照见[迁移说明](docs/CLI-MIGRATION.md)。

## 仓库里没有什么

- embedding 模型（约 2GB，需自行下载）
- 配图原文件（约 881MB，不放入 git）
- SQLite / 向量索引（克隆后用 `python3 -m sgt_kb build-index` 生成；Pages 静态导出除外）
- 微信 / 微信读书等登录态，以及任何密钥
- 公司内部文档、未授权网盘文件或提取码

## 本地快速开始

```bash
# 1. 安装本地运行依赖，准备模型
python3 -m pip install -e '.[collection,indexing,service]'
# 将 BAAI/bge-m3 放到 models/bge-m3/

# 2. 用仓库内的公开文章构建索引
python3 -m sgt_kb build-index

# 3. 启动本地工作台（http://localhost:3917）
cd workbench && npm ci && cd ..
python3 -m sgt_kb start-workbench
```

也可以单条入库公开链接：

```bash
python3 -m sgt_kb ingest-url 'https://www.elastic.co/search-labs/blog/hybrid-search-elasticsearch'
python3 -m sgt_kb build-index
```

可选的持续采集还有公开 RSS（`python3 -m sgt_kb rss-poll`）和 Wayback 历史页（`python3 -m sgt_kb wayback-wechat`）。微信公众号后台登录态是可选的本机能力，凭据只应写在被 gitignore 的 `.wechat_mp_auth.json`，不要提交到仓库。

## 导出 Pages 原始 chunks

导出命令只需 Python 标准库，不需模型或网络。它以只读方式打开已经入库的 SQLite，以公开 checkout 中 `articles/*.md` 文件名建立 allowlist，并同时要求记录路径属于 `articles/`。默认省略 figures；不会复制数据库，不会重新切块或生成摘要。

```bash
# 在保存生产 SQLite 的机器上直接导出；输出仅含 allowlist 公开字段
python3 -m sgt_kb export-pages --db /path/to/production/kb.sqlite --output-dir docs --require-production-counts

# 或从协调者已经导出的 JSONL / JSON / JSONL 目录构建分片
python3 -m sgt_kb export-pages --input /path/to/prod-export/ --output-dir docs --require-production-counts
python3 -m http.server 8000 --directory docs
```

当前 Pages 已接入生产库中按公开白名单导出的原始存储 chunks：**2402 篇 / 25838 块**，文档 ID SHA-256 为 `0cb203aa14438799f4bfd4d61861817dab28c3873255a2f4dacf4da3566231eb`，与先前核对一致。导出使用公开仓库 2421 个 `articles/*.md` stem 作为白名单，并要求 `path` 恰好为 `articles/<doc_id>.md`。生产库里 20 篇 `extra-docs/`（709 块）以及 1 篇未进入公开仓库的 `articles/` 文档被排除，未写入静态站点。仓库仍保留全部 2421 篇公开文章和目录。如需重建空的等待态索引，可执行 `python3 -m sgt_kb export-pages --pending --output-dir docs`。

旧 `demo-index.json`（68833 个 `utf8-bytes-v1` chunks）不再作为默认 Pages 语料。这些边界来自 UTF-8 字节预算，不能称为生产 token 预算的原始 chunks。`build-index --lexical-only` 仅供本地独立测试；Pages 生产导出会拒绝已知字节预算索引。

浏览器先加载小型检索目录，再按查询加载词项 postings，最后只加载核验候选及展示结果所需的原文分片。广泛查询会显示已核验候选数，并提供继续检索按钮。结果显示完整存储文本，展示层只做 HTML 转义和 Unicode 安全高亮，保留标题、原文 URL、`doc_id` 与 `chunk_id`。中文连续词组不拆成单字；`查询理解`、`Query理解` 与 `Query Understanding` 采用明确词组别名。实现和格式见 [STORED-EXPORT.md](docs/STORED-EXPORT.md)。Pages 是离线静态词法检索，不代表本地 bge-m3 混合检索。

验证命令（现有 Python 运行依赖需已安装；静态导出和 Node 测试只用标准库）：

```bash
python3 -m unittest discover -s tests -v
node --test tests/*.test.mjs
```

## MCP

将 MCP 启动命令设置为 `python3 -m sgt_kb kb-server`（工作目录为本仓库）后，可用 `kb_search`、`kb_get_doc`、`kb_get_figures`、`kb_stats`。需要本地上下文时，复制 `extra-docs/local-context.example.md` 为 `local-context.md`。

## License

代码为 MIT。`articles/` 与 `figures/` 中的内容版权归原作者，仅供检索演示。
