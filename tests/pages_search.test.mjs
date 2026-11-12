import assert from "node:assert/strict";
import { existsSync, mkdtempSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import Search from "../docs/search.js";

const { createSearchIndex, indexTokens, postingBucket, queryTerms, highlight, renderResult, safeUrl } = Search;
const normalize = (value) => value.normalize("NFKC").toLowerCase().replace(/\s+/gu, " ");

function fixture(docs, chunks) {
  const files = new Map();
  const postings = new Map();
  docs = docs.map((doc) => ({ path: `articles/${doc.doc_id}.md`, ...doc }));
  const data = { format_version: 3, retrieval: "offline-static-lexical", status: "stored-chunks", docs, chunks: [], posting_shards: 256, posting_path: "search-postings/{bucket}.json", posting_buckets: [], text_shards: [] };
  chunks.forEach((chunk, index) => {
    const file = `search-chunks/${String(index).padStart(4, "0")}.json`;
    files.set(file, { format_version: 3, chunks: [chunk] });
    data.text_shards.push({ file, chunks: 1 });
    data.chunks.push([chunk.chunk_id, docs.findIndex((doc) => doc.doc_id === chunk.doc_id), chunk.seq, index, Array.from(normalize(chunk.text)).length]);
    const frequencies = new Map();
    for (const token of indexTokens(chunk.text)) frequencies.set(token, (frequencies.get(token) || 0) + 1);
    for (const [token, frequency] of frequencies) {
      const bucket = postingBucket(token);
      if (!postings.has(bucket)) postings.set(bucket, {});
      const entries = postings.get(bucket);
      if (!entries[token]) entries[token] = [];
      entries[token].push([index, frequency]);
    }
  });
  data.posting_buckets = [...postings.keys()].sort();
  for (const [bucket, entries] of postings) files.set(`search-postings/${bucket}.json`, entries);
  const requests = [];
  const fetchJson = async (file) => {
    requests.push(file);
    assert.ok(files.has(file), `Unexpected shard ${file}`);
    return structuredClone(files.get(file));
  };
  return { data, files, requests, fetchJson, index: createSearchIndex(data, { fetchJson }) };
}

const source = { doc_id: "source-1", title: "搜索实践", company: "公开来源", url: "https://example.org/source?a=1&b=2" };

test("a deep-body hit returns the entire unchanged stored chunk and source identifiers", async () => {
  const deepText = "保留段落开头。\n" + "正文中的前文内容。".repeat(80) + "\n后文介绍查询理解模块和召回。\n保留段落结尾。";
  const { index } = fixture([source], [
    { chunk_id: 11, doc_id: source.doc_id, seq: 0, text: "文章简介与目录，不含检索词。" },
    { chunk_id: 19, doc_id: source.doc_id, seq: 8, text: deepText },
  ]);
  const [hit] = await index.search("查询理解");
  assert.equal(hit.chunk_id, 19);
  assert.equal(hit.doc_id, source.doc_id);
  assert.equal(hit.seq, 8);
  assert.equal(hit.path, "articles/source-1.md");
  assert.equal(hit.url, source.url);
  assert.equal(hit.text, deepText);
  const html = renderResult(hit, "查询理解");
  assert.ok(html.includes("保留段落开头。"));
  assert.ok(html.includes("保留段落结尾。"));
  assert.ok(html.includes("<mark>查询理解</mark>"));
  assert.ok(!html.includes("…"));
  assert.ok(html.includes("chunk_id: 19"));
});

test("no match and empty queries return no decorative or title-only chunks", async () => {
  const { index, requests } = fixture([{ doc_id: "a", title: "查询理解" }], [{ chunk_id: 1, doc_id: "a", seq: 0, text: "完全无关的正文。" }]);
  assert.deepEqual(await index.search("不存在的词组"), []);
  assert.deepEqual(await index.search("查询理解"), []);
  assert.deepEqual(await index.search(""), []);
  assert.deepEqual(await index.search(" < > !!! "), []);
  assert.ok(requests.every((file) => file.startsWith("search-postings/")));
});

test("Chinese phrases exclude TuGraph and prefer Meituan deep-body text over lead/TOC", async () => {
  const docs = [{ doc_id: "weak", title: "蚂蚁 TuGraph-DB 数据库查询引擎技术" }, { doc_id: "relevant", title: "Query理解在美团搜索中的应用" }];
  const body = "下面介绍查询理解系统。QU (Query Understanding)主要利用基础NLP能力，对用户输入进行分析，产生一系列基础信号，然后应用到整个搜索链路的召回和排序。";
  const { index } = fixture(docs, [
    { chunk_id: 1, doc_id: "weak", seq: 4, text: "查询引擎、数据治理、理解执行计划。" },
    { chunk_id: 2, doc_id: "relevant", seq: 0, text: "导读：查询理解。主要围绕以下几点展开：\n* Query理解简介\n* 查询理解\n* Query Understanding\n* 实体识别" },
    { chunk_id: 3, doc_id: "relevant", seq: 9, text: body },
  ]);
  const hits = await index.search("查询理解");
  assert.deepEqual(hits.map((hit) => hit.doc_id), ["relevant"]);
  assert.equal(hits[0].chunk_id, 3);
  assert.equal(hits[0].text, body);
  assert.equal(highlight("查询引擎、理解执行计划", "查询理解"), "查询引擎、理解执行计划");
  assert.ok(queryTerms("查询理解").flat().every((term) => term.length > 1));
});

test("separated bigrams are verified as a complete phrase before returning a chunk", async () => {
  const { index } = fixture([{ doc_id: "a", title: "查询理解" }], [
    { chunk_id: 1, doc_id: "a", seq: 3, text: "查询引擎、询理并非词语、理解执行计划。" },
  ]);
  assert.deepEqual(await index.search("查询理解"), []);
  assert.deepEqual(index.lastSearchStats, { candidateCount: 1, checkedCandidates: 1, hasMoreCandidates: false });
});

test("mixed queries use whole terms and generic bilingual aliases", async () => {
  const { index } = fixture([{ doc_id: "a", title: "Query理解在搜索中的应用" }, { doc_id: "b", title: "查询引擎" }], [
    { chunk_id: 1, doc_id: "a", seq: 4, text: "Query Understanding 在查询理解模块中结合 BERT 模型。" },
    { chunk_id: 2, doc_id: "b", seq: 0, text: "查询引擎的理解与 BERT 模型。" },
  ]);
  for (const query of ["查询理解 BERT", "QUERY理解 bert", "Query Understanding BERT"]) assert.equal((await index.search(query))[0].doc_id, "a");
  assert.deepEqual(await index.search("BERTing"), []);
  assert.deepEqual(queryTerms("BERT召回 RRF融合"), [["bert"], ["召回"], ["rrf"], ["融合"]]);
  assert.equal(highlight("Query理解 和 QUERY Understanding", "查询理解"), "<mark>Query理解</mark> 和 <mark>QUERY Understanding</mark>");
});

test("alias extraction never introduces isolated Chinese remainder terms", async () => {
  for (const query of ["查询理解的", "Query理解与 BERT"]) assert.ok(queryTerms(query).flat().every((term) => Array.from(term).length > 1));
  assert.deepEqual(queryTerms("的"), []);
  assert.deepEqual(queryTerms("あ"), []);
  const { index } = fixture([{ doc_id: "weak", title: "无关正文" }, { doc_id: "relevant", title: "查询理解" }], [
    { chunk_id: 1, doc_id: "weak", seq: 0, text: "的 与 的 与，只包含无关的单字。" },
    { chunk_id: 2, doc_id: "relevant", seq: 0, text: "查询理解模块使用 BERT 模型。" },
  ]);
  for (const query of ["查询理解的", "Query理解与 BERT"]) assert.deepEqual((await index.search(query)).map((hit) => hit.doc_id), ["relevant"]);
  assert.equal(highlight("的 与", "Query理解与 BERT"), "的 与");
});

test("Unicode normalization preserves stored whitespace, graphemes, emoji and contextual casing", async () => {
  const text = "\n\tＣＡＦÉ cafe\u0301 𠮷野家 ﬃ ΟΣ 😀\n";
  const { index } = fixture([{ doc_id: "unicode", title: "Unicode" }], [{ chunk_id: 1, doc_id: "unicode", seq: 0, text }]);
  assert.equal((await index.search("café 𠮷野家"))[0].text, text);
  assert.equal(highlight(text, "café 𠮷野家 ffi ος"), "\n\t<mark>ＣＡＦÉ</mark> <mark>cafe\u0301</mark> <mark>𠮷野家</mark> <mark>ﬃ</mark> <mark>ΟΣ</mark> 😀\n");
  assert.equal(highlight("query\n\t understanding", "查询理解"), "<mark>query\n\t understanding</mark>");
});

test("HTML is escaped after matching and only credential-free http(s) source URLs are linked", () => {
  assert.equal(highlight("& <script> ' \"", "amp"), "&amp; &lt;script&gt; &#39; &quot;");
  assert.equal(highlight("& <script>", "script"), "&amp; &lt;<mark>script</mark>&gt;");
  const html = renderResult({
    title: '<script>"bad"</script>', text: "查询理解 & <svg onload=alert(1)>",
    company: '<img src=x>', tag: '" onmouseover="bad', date: "<script>",
    url: "javascript:alert(1)", doc_id: '<a onclick="bad">', chunk_id: '<script>',
  }, "查询理解");
  for (const forbidden of ["<script>", "<img", "<svg", "href="]) assert.ok(!html.includes(forbidden));
  assert.ok(html.includes("&lt;script&gt;"));
  assert.ok(html.includes("<mark>查询理解</mark> &amp;"));
  const linked = renderResult({ title: "source", text: "text", url: 'https://example.org/?a=1&b="quoted"', doc_id: "a", chunk_id: 1 }, "");
  assert.ok(linked.includes("&amp;b="));
  for (const url of ["data:text/html,bad", "javascript:bad", "file:///etc/passwd", "//example.org/path", "https://user:pass@example.org/", "bad"]) assert.equal(safeUrl(url), "");
});

test("first load fetches no shards; a search fetches needed shards once and caches them", async () => {
  const { index, requests } = fixture([{ doc_id: "a", title: "召回" }, { doc_id: "b", title: "其他内容" }], [
    { chunk_id: 1, doc_id: "a", seq: 8, text: "查询理解结合 BERT。" },
    { chunk_id: 2, doc_id: "b", seq: 0, text: "无关原文完整保留。" },
  ]);
  assert.deepEqual(requests, []);
  await index.search("查询理解");
  assert.deepEqual(requests.filter((file) => file.startsWith("search-chunks/")), ["search-chunks/0000.json"]);
  const loaded = requests.length;
  await index.search("查询理解");
  assert.equal(requests.length, loaded);
});

test("candidate paging is explicit and still checks every candidate of returned sources", async () => {
  const docs = Array.from({ length: 30 }, (_, index) => ({ doc_id: `doc${index}`, title: "查询理解" }));
  const chunks = docs.map((doc, index) => ({ chunk_id: index + 1, doc_id: doc.doc_id, seq: 4, text: "查询理解正文。" }));
  chunks.push({ chunk_id: 90, doc_id: "doc0", seq: 20, text: "查询理解结合实体识别、实体链接和意图识别提供基础信号。".repeat(5) });
  const { index } = fixture(docs, chunks);
  assert.equal((await index.search("查询理解", { limit: 2, candidateBudget: 8 }))[0].chunk_id, 90);
  assert.equal(index.lastSearchStats.hasMoreCandidates, true);
  assert.ok(index.lastSearchStats.checkedCandidates < index.lastSearchStats.candidateCount);
  await index.search("查询理解", { limit: 30, exhaustive: true });
  assert.equal(index.lastSearchStats.hasMoreCandidates, false);
  assert.equal(index.lastSearchStats.checkedCandidates, chunks.length);
});

test("a budget of false bigram candidates cannot hide a later complete phrase", async () => {
  const docs = Array.from({ length: 30 }, (_, index) => ({ doc_id: `doc${index}`, title: "查询理解" }));
  const chunks = docs.map((doc, index) => ({ chunk_id: index + 1, doc_id: doc.doc_id, seq: 4, text: "查询、询理、理解。".repeat(6) }));
  chunks.push({ chunk_id: 90, doc_id: "doc0", seq: 20, text: "查询理解系统。" });
  const { index } = fixture(docs, chunks);
  assert.equal((await index.search("查询理解", { limit: 1, candidateBudget: 1 }))[0].chunk_id, 90);
  assert.equal(index.lastSearchStats.hasMoreCandidates, false);
});

test("legacy payloads, private paths and mismatched or missing text shards are refused", async () => {
  assert.throws(() => createSearchIndex({ format_version: 2, docs: [], chunks: [] }), /sharded stored-chunk/);
  const build = () => fixture([{ doc_id: "a", title: "source" }], [{ chunk_id: 1, doc_id: "a", seq: 0, text: "查询理解。" }]);
  const privateData = build();
  privateData.data.docs[0].path = "extra-docs/a.md";
  assert.throws(() => createSearchIndex(privateData.data, { fetchJson: privateData.fetchJson }), /public article/);
  for (const modify of [(chunk) => { chunk.doc_id = "other"; }, (chunk) => { chunk.seq = 3; }, (chunk) => { chunk.text += "replaced"; }]) {
    const { index, files } = build();
    modify(files.get("search-chunks/0000.json").chunks[0]);
    await assert.rejects(index.search("查询理解"), /does not match index/);
  }
  const missing = build();
  missing.files.get("search-chunks/0000.json").chunks = [];
  await assert.rejects(missing.index.search("查询理解"), /missing indexed chunks/);
});

test("Python exporter and browser agree on Unicode token buckets, locators and unchanged shard text", async () => {
  const base = mkdtempSync(join(tmpdir(), "sgt-pages-node-"));
  try {
    mkdirSync(join(base, "articles"));
    writeFileSync(join(base, "articles/a.md"), "public allowlist fixture");
    const text = "\n\t查询理解 Query Understanding ＣＡＦÉ cafe\u0301 𠮷野家 ﬃ ΟΣ 😀 カーネル・検索\ufeff \n";
    writeFileSync(join(base, "input.json"), JSON.stringify({ docs: [{ doc_id: "a", title: "source", path: "articles/a.md" }], chunks: [{ chunk_id: 79, doc_id: "a", seq: 8, text }] }));
    const script = "import sys\nfrom sgt_kb.indexing.export_pages import export_pages\nfrom pathlib import Path\nb=Path(sys.argv[1])\nexport_pages(intermediate=b/'input.json',output_dir=b/'out',base=b)\n";
    const python = spawnSync("python3", ["-c", script, base], { encoding: "utf8", cwd: new URL("..", import.meta.url) });
    assert.equal(python.status, 0, python.stderr);
    const data = JSON.parse(readFileSync(join(base, "out/search-index.json"), "utf8"));
    const index = createSearchIndex(data, { fetchJson: async (file) => JSON.parse(readFileSync(join(base, "out", file), "utf8")) });
    for (const query of ["查询理解", "query understanding", "café", "𠮷野家", "ffi", "ος", "カーネル・検索"]) assert.equal((await index.search(query))[0].text, text);
  } finally { rmSync(base, { recursive: true, force: true }); }
});

test("default Pages payload is small, sharded and candid about production integration", async () => {
  const root = new URL("../", import.meta.url);
  const data = JSON.parse(readFileSync(new URL("docs/search-index.json", root), "utf8"));
  const manifest = JSON.parse(readFileSync(new URL("docs/search-manifest.json", root), "utf8"));
  assert.equal(data.format_version, 3);
  assert.equal(data.retrieval, "offline-static-lexical");
  assert.equal(readdirSync(new URL("articles/", root)).filter((path) => path.endsWith(".md")).length, 2421);
  assert.ok(readFileSync(new URL("docs/search-index.json", root)).length < 3 * 1024 * 1024, "Bootstrap should remain under 3 MiB");
  assert.ok(!existsSync(new URL("docs/demo-index.json", root)));
  assert.equal(manifest.doc_count, data.docs.length);
  assert.equal(manifest.chunk_count, data.chunks.length);
  if (data.status === "pending-production-export") {
    assert.equal(data.docs.length, 0);
    assert.equal(data.chunks.length, 0);
    assert.equal(manifest.chunk_boundaries, "no-corpus-integrated");
  } else {
    assert.equal(data.docs.length, 2402);
    assert.equal(data.chunks.length, 25838);
    const index = createSearchIndex(data, { fetchJson: async (file) => JSON.parse(readFileSync(new URL(`docs/${file}`, root), "utf8")) });
    const hits = await index.search("查询理解", { exhaustive: true, limit: data.docs.length });
    const hit = hits.find((row) => row.title === "Query理解在美团搜索中的应用");
    assert.ok(hit, "Meituan article should be found");
    assert.ok(hit.seq > 0, "Meituan hit must be a deep stored chunk");
    assert.ok(!/导读|主要围绕以下|分享嘉宾|编辑整理|出品社区/u.test(hit.text), "Meituan hit should be substantive body text");
    assert.ok(!hits.some((row) => /TuGraph-DB/u.test(row.title)), "TuGraph must not match 查询理解");
  }
});
