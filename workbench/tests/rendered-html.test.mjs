import assert from "node:assert/strict";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request("http://localhost/", {
      headers: { accept: "text/html" },
    }),
    {
      ASSETS: {
        fetch: async () => new Response("Not found", { status: 404 }),
      },
    },
    {
      waitUntil() {},
      passThroughOnException() {},
    },
  );
}

test("server-renders the knowledge base workbench", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /SGT KB/);
  assert.match(html, /工业实践知识库/);
  assert.match(html, /知识检索/);
  assert.match(html, /检索知识库/);
  assert.match(html, /内容仅在本机流转/);
  assert.doesNotMatch(html, /边干边学/);
  assert.doesNotMatch(html, /最小知识/);
  assert.doesNotMatch(html, /汇报质检/);
  assert.doesNotMatch(html, /sgt-kb-mentor/);
  assert.doesNotMatch(html, /codex-preview/);
  assert.doesNotMatch(html, /react-loading-skeleton/);
});
