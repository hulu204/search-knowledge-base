# sgt-kb

本地知识库：把公开的搜索 / 推荐 / RAG 技术文章，走完「爬取 → 解析切块 → 混合索引 → 带引用检索」。

在线演示：[hulu204.github.io/sgt-kb](https://hulu204.github.io/sgt-kb/)（用仓库内公开样例做**标题和摘要的关键词检索**，不是本地 bge-m3 的 dense / sparse 混合检索）。

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
    → 结果带标题、来源、doc_id 和原文链接
```

本地 Web 工作台只绑定 loopback，语料默认留在本机。上面这条流水线描述的是本地完整系统；GitHub Pages 演示页只检索标题和摘要关键词。

## 仓库里有什么

- 采集、切块、索引、MCP 和服务端代码
- 2421 篇公开技术文章正文（微信公众号、Elastic、LanceDB、个人技术博客等），目录见上
- 配图 OCR / 说明 sidecar（`figures/`）
- 可点开的 GitHub Pages 演示（标题和摘要关键词检索）

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
