# SGT KB Workbench

搜广推工业实践知识库的本地 Web 前端，只提供知识检索和文档追溯：

- 自然语言混合检索；
- 来源和主题过滤；
- 结构化结果、`doc_id` 与原文链接；
- 本地全文阅读；
- 文档、片段、配图、来源与主题统计。

数据和检索能力由 `sgt-kb` MCP / 本地 API 提供，语料内容只在本机流转。

## 启动

在仓库根目录运行：

```bash
python3 -m sgt_kb start-workbench
```

首次使用若提示缺少前端依赖：

```bash
cd workbench
npm ci
cd ..
python3 -m sgt_kb start-workbench
```

工作台固定监听 `http://localhost:3917`，API 固定监听 `http://127.0.0.1:8766`。两者都只绑定本机 loopback。

## 开发与验证

```bash
npm run dev
npm run build
npm test
```
