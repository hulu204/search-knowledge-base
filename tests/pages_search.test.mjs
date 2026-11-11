import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import test from "node:test";
import Search from "../docs/search.js";

const { createSearchIndex, queryTerms, highlight, renderResult, safeUrl } = Search;

function fixture(docs, chunks) {
  return { format_version: 2, retrieval: "offline-static-lexical", docs, chunks };
}

test("a deep body hit returns the entire unchanged stored chunk and source identifiers", () => {
  const deepText = "保留段落开头。\n" + "正文中的前文内容。".repeat(80) + "\n后文介绍查询理解模块和召回。\n保留段落结尾。";
  const doc = { doc_id: "source-1", title: "搜索实践", path: "articles/example.md", company: "公开来源", url: "https://example.org/source?a=1&b=2" };
  const index = createSearchIndex(fixture([doc], [
    { chunk_id: 11, doc_id: doc.doc_id, seq: 0, text: "文章简介与目录，不含检索词。" },
    { chunk_id: 19, doc_id: doc.doc_id, seq: 8, text: deepText },
  ]));
  const [hit] = index.search("查询理解");
  assert.equal(hit.chunk_id, 19);
  assert.equal(hit.doc_id, doc.doc_id);
  assert.equal(hit.seq, 8);
  assert.equal(hit.path, doc.path);
  assert.equal(hit.url, doc.url);
  assert.equal(hit.text, deepText);
  assert.equal(hit.snippet, deepText);
  const html = renderResult(hit, "查询理解");
  assert.ok(html.includes("保留段落开头。"));
  assert.ok(html.includes("保留段落结尾。"));
  assert.ok(html.includes("<mark>查询理解</mark>"));
  assert.ok(!html.includes("…"));
  assert.ok(html.includes("chunk_id: 19"));
});

test("no match and empty queries return no decorative or title-only snippets", () => {
  const index = createSearchIndex(fixture([{ doc_id: "a", title: "查询理解" }], [{ chunk_id: 1, doc_id: "a", seq: 0, text: "完全无关的正文。" }]));
  assert.deepEqual(index.search("不存在的词组"), []);
  assert.deepEqual(index.search("查询理解"), []);
  assert.deepEqual(index.search(""), []);
  assert.deepEqual(index.search(" < > !!! "), []);
});

test("Chinese phrases do not degrade into single-character matches", () => {
  const docs = [{ doc_id: "weak", title: "蚂蚁 TuGraph-DB 数据库查询引擎技术" }, { doc_id: "relevant", title: "Query理解在美团搜索中的应用" }];
  const index = createSearchIndex(fixture(docs, [
    { chunk_id: 1, doc_id: "weak", seq: 0, text: "查询引擎、数据治理、理解执行计划。" },
    { chunk_id: 2, doc_id: "relevant", seq: 9, text: "查询理解系统通过实体识别和意图识别提供基础信号。" },
  ]));
  assert.deepEqual(index.search("查询理解").map((hit) => hit.doc_id), ["relevant"]);
  assert.equal(highlight("查询引擎、理解执行计划", "查询理解"), "查询引擎、理解执行计划");
  assert.ok(queryTerms("查询理解").flat().every((term) => term.length > 1));
});

test("mixed Chinese-English queries use whole terms and generic bilingual phrase aliases", () => {
  const docs = [{ doc_id: "a", title: "Query理解在搜索中的应用" }, { doc_id: "b", title: "查询引擎" }];
  const index = createSearchIndex(fixture(docs, [
    { chunk_id: 1, doc_id: "a", seq: 4, text: "Query Understanding 在查询理解模块中结合 BERT 模型。" },
    { chunk_id: 2, doc_id: "b", seq: 0, text: "查询引擎的理解与 BERT 模型。" },
  ]));
  for (const query of ["查询理解 BERT", "QUERY理解 bert", "Query Understanding BERT"]) {
    assert.equal(index.search(query)[0].doc_id, "a");
  }
  assert.deepEqual(index.search("BERTing"), []);
  assert.deepEqual(queryTerms("BERT召回 RRF融合"), [["bert"], ["召回"], ["rrf"], ["融合"]]);
  assert.equal(highlight("Query理解 和 QUERY Understanding", "查询理解"), "<mark>Query理解</mark> 和 <mark>QUERY Understanding</mark>");
});

test("bilingual alias extraction never introduces isolated Chinese remainder terms", () => {
  for (const query of ["查询理解的", "Query理解与 BERT"]) {
    assert.ok(queryTerms(query).flat().every((term) => Array.from(term).length > 1));
  }
  assert.deepEqual(queryTerms("的"), []);
  assert.deepEqual(queryTerms("あ"), []);
  const index = createSearchIndex(fixture([
    { doc_id: "weak", title: "无关正文" },
    { doc_id: "relevant", title: "查询理解" },
  ], [
    { chunk_id: 1, doc_id: "weak", seq: 0, text: "的 与 的 与，只包含无关的单字。" },
    { chunk_id: 2, doc_id: "relevant", seq: 0, text: "查询理解模块使用 BERT 模型。" },
  ]));
  for (const query of ["查询理解的", "Query理解与 BERT"]) {
    assert.deepEqual(index.search(query).map((hit) => hit.doc_id), ["relevant"]);
  }
  assert.equal(highlight("的 与", "Query理解与 BERT"), "的 与");
});

test("Unicode normalization preserves original stored text and highlights original graphemes", () => {
  const text = "ＣＡＦÉ cafe\u0301 𠮷野家 ﬃ";
  const index = createSearchIndex(fixture([{ doc_id: "unicode", title: "Unicode" }], [{ chunk_id: 1, doc_id: "unicode", seq: 0, text }]));
  assert.equal(index.search("café 𠮷野家")[0].text, text);
  assert.equal(highlight(text, "café 𠮷野家 ffi"), "<mark>ＣＡＦÉ</mark> <mark>cafe\u0301</mark> <mark>𠮷野家</mark> <mark>ﬃ</mark>");
});

test("HTML is escaped after matching so highlights cannot corrupt entities", () => {
  assert.equal(highlight("& <script> ' \"", "amp"), "&amp; &lt;script&gt; &#39; &quot;");
  assert.equal(highlight("& <script>", "script"), "&amp; &lt;<mark>script</mark>&gt;");
  assert.equal(highlight("查询理解 <img src=x onerror=alert(1)>", "查询理解"), "<mark>查询理解</mark> &lt;img src=x onerror=alert(1)&gt;");
  const html = renderResult({
    title: '<script>"bad"</script>', text: "查询理解 & <svg onload=alert(1)>",
    company: '<img src=x>', tag: '" onmouseover="bad', date: "<script>",
    url: "javascript:alert(1)", doc_id: '<a onclick="bad">', chunk_id: '<script>',
  }, "查询理解");
  assert.ok(!html.includes("<script>"));
  assert.ok(!html.includes("<img"));
  assert.ok(!html.includes("<svg"));
  assert.ok(!html.includes("href="));
  assert.ok(html.includes("&lt;script&gt;"));
  assert.ok(html.includes("<mark>查询理解</mark> &amp;"));
  const linked = renderResult({ title: "source", text: "text", url: 'https://example.org/?a=1&b="quoted"', doc_id: "a", chunk_id: 1 }, "");
  assert.ok(linked.includes("&amp;b="));
  assert.ok(!linked.includes('b="quoted"'));
  for (const url of ["data:text/html,bad", "javascript:bad", "file:///etc/passwd", "//example.org/path", "bad"]) assert.equal(safeUrl(url), "");
});

test("one best matching stored chunk is returned per document", () => {
  const index = createSearchIndex(fixture([{ doc_id: "a", title: "召回搜索" }], [
    { chunk_id: 1, doc_id: "a", seq: 0, text: "查询理解。" },
    { chunk_id: 2, doc_id: "a", seq: 7, text: "查询理解模块结合 BERT，使用 BERT 训练。" },
  ]));
  const hits = index.search("查询理解 BERT");
  assert.equal(hits.length, 1);
  assert.equal(hits[0].chunk_id, 2);
});

test("the frontend refuses legacy fabricated snippets and malformed stored-chunk exports", () => {
  assert.throws(() => createSearchIndex({ docs: [{ id: "old", snippet: "intro" }] }), /ingested chunks/);
  assert.throws(() => createSearchIndex(fixture([{ doc_id: "a", title: "source" }], [{ chunk_id: 1, doc_id: "missing", seq: 0, text: "text" }])), /source doc_id/);
  assert.throws(() => createSearchIndex(fixture([{ doc_id: "a", title: "source" }], [{ chunk_id: 1, doc_id: "a", seq: 0, snippet: "invented" }])), /text/);
});

test("the public corpus export ranks Meituan query understanding above weak TuGraph hits", () => {
  const data = JSON.parse(readFileSync(new URL("../docs/demo-index.json", import.meta.url), "utf8"));
  assert.equal(data.format_version, 2);
  assert.equal(data.retrieval, "offline-static-lexical");
  assert.equal(readdirSync(new URL("../articles/", import.meta.url)).filter((path) => path.endsWith(".md")).length, 2421);
  // The unchanged ingestion loader excludes 19 empty/too-short public articles.
  assert.equal(data.docs.length, 2402);
  assert.equal(data.chunks.length, 68833);
  assert.equal(data.ingestion.mode, "lexical-only");
  assert.equal(data.ingestion.public_only, "true");
  for (const doc of data.docs) {
    for (const field of ["doc_id", "path", "title", "company", "tag", "date", "url", "hash"]) assert.equal(typeof doc[field], "string", `Missing source field: ${field}`);
    assert.ok(doc.path.startsWith("articles/"));
  }
  const meituan = data.docs.find((doc) => doc.title === "Query理解在美团搜索中的应用");
  const tugraph = data.docs.find((doc) => /TuGraph-DB.*数据库查询引擎技术/.test(doc.title));
  assert.ok(meituan);
  assert.ok(tugraph);
  const index = createSearchIndex(data);
  const hits = index.search("查询理解", { limit: data.docs.length });
  const relevantRank = hits.findIndex((hit) => hit.doc_id === meituan.doc_id);
  const weakRank = hits.findIndex((hit) => hit.doc_id === tugraph.doc_id);
  assert.ok(relevantRank >= 0 && relevantRank < 12, `Meituan article rank: ${relevantRank + 1}`);
  assert.ok(weakRank === -1 || relevantRank < weakRank, `Meituan ${relevantRank + 1}, TuGraph ${weakRank + 1}`);
  for (const hit of hits) {
    const stored = data.chunks.find((chunk) => chunk.chunk_id === hit.chunk_id);
    assert.equal(hit.text, stored.text);
    assert.equal(hit.snippet, stored.text);
    assert.equal(hit.doc_id, stored.doc_id);
  }
  const mixedHits = index.search("Query理解 BERT", { limit: data.docs.length });
  const mixedRelevant = mixedHits.find((hit) => hit.doc_id === meituan.doc_id);
  assert.ok(mixedRelevant);
  assert.match(mixedRelevant.text, /Query理解|查询理解|BERT/iu);
  assert.deepEqual(index.search("zzzz-unmatchable-8e8a9e66"), []);
});
