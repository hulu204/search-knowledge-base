/* Offline static lexical retrieval over original stored chunks.
 * Bootstrap and postings contain no chunk text. Original text is loaded by shard,
 * verified against the locator, and only escaped/highlighted for display.
 */
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.SgtSearch = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const normalize = (value) => String(value ?? "").normalize("NFKC").toLowerCase().replace(/\s+/gu, " ");
  const aliases = ["查询理解", "query理解", "query 理解", "query understanding"];
  const concept = /查询理解|query\s*理解|query\s+understanding/gu;
  const cjk = /[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\u{20000}-\u{323AF}\u3040-\u30FF\u31F0-\u31FF]/u;
  const word = /[\p{L}\p{M}\p{N}_]/u;

  function runs(text) {
    const result = [];
    let value = "", kind;
    const flush = () => { if (value) result.push([kind, value]); value = ""; };
    for (const char of normalize(text)) {
      const next = cjk.test(char) ? "c" : word.test(char) ? "w" : undefined;
      if (next !== kind || !next) flush();
      if (next) value += char;
      kind = next;
    }
    flush();
    return result;
  }

  function indexTokens(text) {
    const tokens = [];
    for (const [kind, value] of runs(text)) {
      if (kind === "w") tokens.push(`w:${value}`);
      else {
        const chars = Array.from(value);
        for (let i = 0; i + 1 < chars.length; i++) tokens.push(`c:${chars[i]}${chars[i + 1]}`);
      }
    }
    return tokens;
  }

  function queryTerms(query) {
    const text = normalize(query);
    const groups = [];
    let previous = 0;
    const addWords = (part) => {
      for (const [kind, value] of runs(part)) {
        if (kind !== "c" || Array.from(value).length > 1) groups.push([value]);
      }
    };
    for (const match of text.matchAll(concept)) {
      addWords(text.slice(previous, match.index));
      groups.push([...new Set([match[0], ...aliases])]);
      previous = match.index + match[0].length;
    }
    addWords(text.slice(previous));
    return [...new Map(groups.map((group) => [group.slice().sort().join("|"), group])).values()];
  }

  function postingBucket(token) {
    let hash = 0x811c9dc5;
    for (const byte of new TextEncoder().encode(token)) hash = Math.imul(hash ^ byte, 0x01000193) >>> 0;
    return (hash % 256).toString(16).padStart(2, "0");
  }

  function wordCharacter(char) { return !!char && word.test(char) && !cjk.test(char); }

  function occurrences(text, term) {
    const ranges = [];
    let start = 0;
    while ((start = text.indexOf(term, start)) !== -1) {
      const end = start + term.length;
      const first = Array.from(term)[0];
      const last = Array.from(term).at(-1);
      const before = Array.from(text.slice(Math.max(0, start - 2), start)).at(-1);
      const after = Array.from(text.slice(end, end + 2))[0];
      if ((!wordCharacter(first) || !wordCharacter(before)) && (!wordCharacter(last) || !wordCharacter(after))) ranges.push([start, end]);
      start = end;
    }
    return ranges;
  }

  function groupMatches(text, groups) { return groups.map((group) => group.flatMap((term) => occurrences(text, term))); }

  function bodyQuality(text, seq) {
    // Rank substantive paragraphs ahead of navigation and introductory material.
    // The original stored text is never changed, cut or turned into a snippet.
    const lines = text.split(/\r?\n/u).map((line) => line.trim()).filter(Boolean);
    const prose = lines.filter((line) => !/^(?:[-*+]\s|#{1,6}\s|!\[|\[.*\]\(#)/u.test(line) && Array.from(line).length >= 60).length;
    const navigation = lines.filter((line) => /^(?:[-*+]\s|#{1,6}\s|\[.*\]\(#)/u.test(line)).length;
    return (seq > 0 ? 8 : -16) + Math.min(prose, 3) * 12
      - (navigation > lines.length / 2 && prose === 0 ? 32 : 0)
      - (/导读|主要围绕以下|分享嘉宾|编辑整理|出品社区|table of contents/iu.test(text) ? 24 : 0);
  }

  function createSearchIndex(data, { fetchJson } = {}) {
    if (data.format_version !== 3 || data.retrieval !== "offline-static-lexical" || !Array.isArray(data.docs) || !Array.isArray(data.chunks)
      || data.posting_shards !== 256 || data.posting_path !== "search-postings/{bucket}.json" || !Array.isArray(data.posting_buckets) || !Array.isArray(data.text_shards)
      || !["stored-chunks", "pending-production-export"].includes(data.status)) throw new Error("Expected a format_version 3 sharded stored-chunk index");
    if (typeof fetchJson !== "function") throw new Error("A shard fetchJson function is required");
    const docs = data.docs.map((doc) => {
      if (typeof doc.doc_id !== "string" || typeof doc.title !== "string" || doc.path !== `articles/${doc.doc_id}.md` || /[/\\]/u.test(doc.doc_id)) throw new Error("Invalid public article source");
      return { doc, title: normalize(doc.title) };
    });
    if (new Set(docs.map(({ doc }) => doc.doc_id)).size !== docs.length) throw new Error("Duplicate source doc_id");
    const buckets = new Set(data.posting_buckets);
    if (data.posting_buckets.some((bucket) => !/^[0-9a-f]{2}$/u.test(bucket))) throw new Error("Invalid posting bucket");
    for (const shard of data.text_shards) {
      if (!/^search-chunks\/[0-9]{4,}\.json$/u.test(shard.file || "")) throw new Error("Invalid stored-text shard path");
    }
    const chunkIds = new Set();
    const chunks = data.chunks.map((row) => {
      if (!Array.isArray(row) || row.length < 5 || row.some((value) => !Number.isSafeInteger(value)) || row[0] < 0 || chunkIds.has(row[0])
        || row[1] < 0 || row[1] >= docs.length || row[2] < 0 || row[3] < 0 || row[3] >= data.text_shards.length || row[4] < 0) throw new Error("Invalid stored-chunk locator");
      chunkIds.add(row[0]);
      return row;
    });
    if (data.status === "pending-production-export" && (docs.length || chunks.length)) throw new Error("Pending corpus must be empty");
    const chunkLocations = new Map(chunks.map((row) => [row[0], row]));
    const postingCache = new Map(), textCache = new Map();
    // Cache promises as well as results: concurrent candidates share one request.
    const cached = (cache, key, loader) => {
      if (!cache.has(key)) cache.set(key, Promise.resolve().then(loader).catch((error) => { cache.delete(key); throw error; }));
      return cache.get(key);
    };
    const loadPosting = (bucket) => !buckets.has(bucket) ? Promise.resolve({}) : cached(postingCache, bucket, async () => {
      const postings = await fetchJson(data.posting_path.replace("{bucket}", bucket));
      if (!postings || typeof postings !== "object" || Array.isArray(postings)) throw new Error("Invalid lexical posting shard");
      for (const [token, rows] of Object.entries(postings)) {
        if (postingBucket(token) !== bucket || !Array.isArray(rows)) throw new Error("Mismatched lexical posting shard");
        let previous = -1;
        for (const row of rows) {
          if (!Array.isArray(row) || row.length !== 2 || !Number.isInteger(row[0]) || row[0] <= previous || row[0] >= chunks.length || !Number.isInteger(row[1]) || row[1] < 1) throw new Error("Invalid lexical posting locator");
          previous = row[0];
        }
      }
      return postings;
    });
    const loadText = (shardIndex) => cached(textCache, shardIndex, async () => {
      const shard = await fetchJson(data.text_shards[shardIndex].file);
      if (shard.format_version !== 3 || !Array.isArray(shard.chunks)) throw new Error("Invalid stored-text shard");
      const rows = new Map();
      for (const chunk of shard.chunks) {
        const locator = chunkLocations.get(chunk.chunk_id);
        if (!locator || rows.has(chunk.chunk_id) || locator[3] !== shardIndex || chunk.doc_id !== docs[locator[1]].doc.doc_id || chunk.seq !== locator[2]
          || typeof chunk.text !== "string" || Array.from(normalize(chunk.text)).length !== locator[4]) throw new Error("Stored-text shard does not match index");
        rows.set(chunk.chunk_id, chunk);
      }
      if (chunks.filter((row) => row[3] === shardIndex).some((row) => !rows.has(row[0]))) throw new Error("Stored-text shard is missing indexed chunks");
      return rows;
    });

    const api = {
      docCount: docs.length, chunkCount: chunks.length, status: data.status,
      lastSearchStats: { candidateCount: 0, checkedCandidates: 0, hasMoreCandidates: false },
      async search(query, { limit = 12, candidateBudget = Math.max(48, limit * 4), exhaustive = false } = {}) {
        const groups = queryTerms(query);
        api.lastSearchStats = { candidateCount: 0, checkedCandidates: 0, hasMoreCandidates: false };
        if (!groups.length || limit <= 0 || !chunks.length) return [];
        const tokens = [...new Set(groups.flat(2).flatMap(indexTokens))];
        const postingData = new Map(await Promise.all([...new Set(tokens.map(postingBucket))].map(async (bucket) => [bucket, await loadPosting(bucket)])));
        const posting = (token) => new Map(postingData.get(postingBucket(token))?.[token] || []);
        const candidates = new Map();
        groups.forEach((group, groupIndex) => {
          const matches = new Map();
          for (const term of group) {
            const termTokens = [...new Set(indexTokens(term))];
            if (!termTokens.length) continue;
            const lists = termTokens.map(posting).sort((a, b) => a.size - b.size);
            for (const [chunkIndex, frequency] of lists[0]) {
              if (lists.every((list) => list.has(chunkIndex))) matches.set(chunkIndex, Math.max(matches.get(chunkIndex) || 0, Math.min(frequency, ...lists.slice(1).map((list) => list.get(chunkIndex)))));
            }
          }
          for (const [chunkIndex, frequency] of matches) {
            if (!candidates.has(chunkIndex)) candidates.set(chunkIndex, { chunkIndex, groups: new Set(), frequency: 0 });
            const row = candidates.get(chunkIndex);
            row.groups.add(groupIndex);
            row.frequency += Math.min(frequency, 6);
          }
        });
        const titleHits = docs.map((source) => groupMatches(source.title, groups).filter((hits) => hits.length).length);
        const ranked = [...candidates.values()].map((row) => {
          const locator = chunks[row.chunkIndex];
          return { ...row, priority: row.groups.size * 64 + (row.groups.size === groups.length ? 64 : 0) + titleHits[locator[1]] * 32 + row.frequency * 4 + (locator[2] > 0 ? 8 : -16) + Math.min(locator[4], 1000) / 1000 };
        }).sort((a, b) => b.priority - a.priority || chunks[a.chunkIndex][0] - chunks[b.chunkIndex][0]);
        const checked = new Set(), best = new Map();
        const inspect = async (rows) => {
          await Promise.all([...new Set(rows.map((row) => chunks[row.chunkIndex][3]))].map(loadText));
          for (const row of rows) {
            if (checked.has(row.chunkIndex)) continue;
            checked.add(row.chunkIndex);
            const locator = chunks[row.chunkIndex];
            const chunk = (await loadText(locator[3])).get(locator[0]);
            const text = normalize(chunk.text);
            const matches = groupMatches(text, groups);
            const covered = matches.filter((hits) => hits.length).length;
            // A title match or separated bigram match can never become a result.
            if (!covered) continue;
            const frequency = matches.reduce((total, hits) => total + Math.min(hits.length, 6), 0);
            const exactFrequency = groups.reduce((total, group) => total + Math.min(occurrences(text, group[0]).length, 6), 0);
            const score = covered * 64 + (covered === groups.length ? 64 : 0) + titleHits[locator[1]] * 32 + frequency * 2 + exactFrequency * 2 + bodyQuality(chunk.text, chunk.seq);
            const old = best.get(chunk.doc_id);
            if (!old || score > old.score || (score === old.score && chunk.seq < old.seq)) best.set(chunk.doc_id, { ...docs[locator[1]].doc, ...chunk, score });
          }
        };
        let cursor = 0;
        // If exact verification has not found a page of results, continue rather
        // than allowing bigram false positives to consume a hidden hard cap.
        while (cursor < ranked.length && (exhaustive || cursor < candidateBudget || best.size < limit)) {
          await inspect(ranked.slice(cursor, cursor + 8));
          cursor += 8;
        }
        const results = () => [...best.values()].sort((a, b) => b.score - a.score || String(a.doc_id).localeCompare(String(b.doc_id))).slice(0, limit);
        const selectedDocs = new Set(results().map((hit) => hit.doc_id));
        // Choose each returned source's best full chunk across all its nominated
        // chunks, including deep paragraphs beyond the first candidate page.
        for (let start = 0; start < ranked.length; start += 8) {
          const remaining = ranked.slice(start, start + 8).filter((row) => !checked.has(row.chunkIndex) && selectedDocs.has(docs[chunks[row.chunkIndex][1]].doc.doc_id));
          if (remaining.length) await inspect(remaining);
        }
        api.lastSearchStats = { candidateCount: ranked.length, checkedCandidates: checked.size, hasMoreCandidates: checked.size < ranked.length };
        return results();
      },
    };
    return api;
  }

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
  }

  function normalizedOffsets(raw) {
    const segments = typeof Intl.Segmenter === "function"
      ? new Intl.Segmenter(undefined, { granularity: "grapheme" }).segment(raw)
      : Array.from(raw, (segment) => ({ segment }));
    let compatible = "", cursor = 0;
    const compatibilityOffsets = [];
    for (const { segment } of segments) {
      const start = cursor;
      cursor += segment.length;
      const normalized = segment.normalize("NFKC");
      compatible += normalized;
      for (let i = 0; i < normalized.length; i++) compatibilityOffsets.push([start, cursor]);
    }
    // Lowercase the complete string so contextual Unicode casing (Greek final
    // sigma, for example) agrees with normalization used by the lexical index.
    const lowered = compatible.toLowerCase();
    const lowerOffsets = [];
    cursor = 0;
    for (const char of compatible) {
      for (let i = 0; i < char.toLowerCase().length; i++) lowerOffsets.push(compatibilityOffsets[cursor]);
      cursor += char.length;
    }
    let text = "";
    const offsets = [];
    cursor = 0;
    for (const char of lowered) {
      const range = lowerOffsets[cursor];
      cursor += char.length;
      if (/\s/u.test(char)) {
        if (text.endsWith(" ")) offsets[offsets.length - 1][1] = range[1];
        else { text += " "; offsets.push(range.slice()); }
      } else {
        text += char;
        for (let i = 0; i < char.length; i++) offsets.push(range.slice());
      }
    }
    return { text, offsets };
  }

  function highlight(value, query) {
    const raw = String(value ?? "");
    const groups = queryTerms(query);
    if (!groups.length) return escapeHtml(raw);
    const { text, offsets } = normalizedOffsets(raw);
    const ranges = groupMatches(text, groups).flat().map(([start, end]) => [offsets[start][0], offsets[end - 1][1]]).sort((a, b) => a[0] - b[0] || a[1] - b[1]);
    const merged = [];
    for (const range of ranges) {
      const last = merged.at(-1);
      if (last && range[0] <= last[1]) last[1] = Math.max(last[1], range[1]);
      else merged.push(range.slice());
    }
    let cursor = 0, html = "";
    for (const [start, end] of merged) {
      html += escapeHtml(raw.slice(cursor, start)) + "<mark>" + escapeHtml(raw.slice(start, end)) + "</mark>";
      cursor = end;
    }
    return html + escapeHtml(raw.slice(cursor));
  }

  function safeUrl(value) {
    try { const url = new URL(String(value)); return ["https:", "http:"].includes(url.protocol) && !url.username && !url.password ? url.href : ""; }
    catch (_) { return ""; }
  }

  function renderResult(result, query) {
    const href = safeUrl(result.url);
    const title = highlight(result.title, query);
    const link = href ? `<a href="${escapeHtml(href)}" target="_blank" rel="noopener noreferrer">${title}</a>` : title;
    const chips = [["company", ""], ["tag", " tag"], ["date", " tag"]].map(([key, cls]) => result[key] ? `<span class="chip${cls}">${highlight(result[key], query)}</span>` : "").join("");
    return `<article class="result"><h2>${link}</h2><div class="chips">${chips}</div><p class="snippet">${highlight(result.text, query)}</p><div class="cite">doc_id: ${escapeHtml(result.doc_id)} · chunk_id: ${escapeHtml(result.chunk_id)}</div></article>`;
  }

  return { createSearchIndex, indexTokens, postingBucket, queryTerms, escapeHtml, highlight, safeUrl, renderResult };
});
