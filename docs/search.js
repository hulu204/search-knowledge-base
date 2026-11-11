/* Offline lexical retrieval over exported ingestion chunks; no snippet generation.
 * The bilingual query-understanding aliases apply to every document equally.
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
  const cjk = /[\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}]/u;

  function queryTerms(query) {
    const text = normalize(query);
    const groups = [];
    let previous = 0;
    // Keep Chinese runs intact. In particular 查询理解 never becomes 查/询/理/解.
    const addWords = (part) => {
      let word = "";
      let kind;
      const addWord = () => {
        // Single Han/Kana queries and alias remainders (的/与, etc.) are ignored;
        // multi-character queries must never introduce accidental unigram hits.
        if (word && (kind !== "cjk" || Array.from(word).length > 1)) groups.push([word]);
        word = "";
      };
      for (const char of part) {
        const next = cjk.test(char) ? "cjk" : /[\p{L}\p{M}\p{N}_]/u.test(char) ? "word" : undefined;
        if (next !== kind || !next) {
          addWord();
        }
        if (next) word += char;
        kind = next;
      }
      addWord();
    };
    for (const match of text.matchAll(concept)) {
      addWords(text.slice(previous, match.index));
      groups.push([...new Set([match[0], ...aliases])]);
      previous = match.index + match[0].length;
    }
    addWords(text.slice(previous));
    return [...new Map(groups.map((group) => [group.slice().sort().join("|"), group])).values()];
  }

  function wordCharacter(char) {
    return !!char && /[\p{L}\p{M}\p{N}_]/u.test(char) && !cjk.test(char);
  }

  function occurrences(text, term) {
    const ranges = [];
    let start = 0;
    while ((start = text.indexOf(term, start)) !== -1) {
      const end = start + term.length;
      const first = Array.from(term)[0];
      const last = Array.from(term).at(-1);
      const before = Array.from(text.slice(Math.max(0, start - 2), start)).at(-1);
      const after = Array.from(text.slice(end, end + 2))[0];
      if ((!wordCharacter(first) || !wordCharacter(before)) && (!wordCharacter(last) || !wordCharacter(after))) {
        ranges.push([start, end]);
      }
      start = end;
    }
    return ranges;
  }

  function groupMatches(text, groups) {
    return groups.map((group) => group.flatMap((term) => occurrences(text, term)));
  }

  function createSearchIndex(data) {
    if (data.format_version !== 2 || data.retrieval !== "offline-static-lexical" || !Array.isArray(data.chunks) || !Array.isArray(data.docs)) {
      throw new Error("Expected a format_version 2 export of ingested chunks");
    }
    const docs = new Map();
    for (const doc of data.docs) {
      if (typeof doc.doc_id !== "string" || typeof doc.title !== "string" || docs.has(doc.doc_id)) {
        throw new Error("Each source must have a unique doc_id and a title");
      }
      docs.set(doc.doc_id, { doc, title: normalize(doc.title) });
    }
    const chunkIds = new Set();
    const chunks = data.chunks.map((chunk) => {
      if (!Number.isInteger(chunk.chunk_id) || chunkIds.has(chunk.chunk_id) || !Number.isInteger(chunk.seq) || chunk.seq < 0 || typeof chunk.text !== "string" || !docs.has(chunk.doc_id)) {
        throw new Error("Each stored chunk must have a unique integer chunk_id, seq, text and source doc_id");
      }
      chunkIds.add(chunk.chunk_id);
      return { chunk, text: normalize(chunk.text), source: docs.get(chunk.doc_id) };
    });
    return {
      docCount: docs.size,
      chunkCount: chunks.length,
      search(query, { limit = 12 } = {}) {
        const terms = queryTerms(query);
        if (!terms.length || limit <= 0) return [];
        const titleHits = new Map([...docs].map(([id, source]) => [id, groupMatches(source.title, terms).filter((hits) => hits.length).length]));
        const best = new Map();
        for (const row of chunks) {
          if (!row.source) continue;
          const matches = groupMatches(row.text, terms);
          const covered = matches.filter((hits) => hits.length).length;
          // A source/title match alone cannot attach an unrelated chunk as its snippet.
          if (!covered) continue;
          const frequency = matches.reduce((total, hits) => total + Math.min(hits.length, 6), 0);
          // Prefer the typed phrase slightly over its bilingual equivalents.
          const exactFrequency = terms.reduce((total, group) => total + Math.min(occurrences(row.text, group[0]).length, 6), 0);
          const score = covered * 32 + (covered === terms.length ? 32 : 0) + titleHits.get(row.chunk.doc_id) * 24 + frequency * 2 + exactFrequency * 2;
          const old = best.get(row.chunk.doc_id);
          if (!old || score > old.score || (score === old.score && row.chunk.seq < old.seq)) {
            best.set(row.chunk.doc_id, {
              ...row.source.doc,
              ...row.chunk,
              // The snippet is the complete, unchanged stored chunk, also returned as text.
              snippet: row.chunk.text,
              score,
            });
          }
        }
        return [...best.values()].sort((a, b) => b.score - a.score || String(a.doc_id).localeCompare(String(b.doc_id))).slice(0, limit);
      },
    };
  }

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
  }

  function normalizedOffsets(raw) {
    const segments = typeof Intl.Segmenter === "function"
      ? new Intl.Segmenter(undefined, { granularity: "grapheme" }).segment(raw)
      : Array.from(raw, (segment) => ({ segment }));
    let text = "";
    const offsets = [];
    let cursor = 0;
    for (const { segment } of segments) {
      const start = cursor;
      cursor += segment.length;
      for (const char of normalize(segment)) {
        if (char === " " && text.endsWith(" ")) {
          offsets[offsets.length - 1][1] = cursor;
          continue;
        }
        text += char;
        // Indices from String.indexOf use UTF-16 code units.
        for (let i = 0; i < char.length; i++) offsets.push([start, cursor]);
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
    let cursor = 0;
    let html = "";
    for (const [start, end] of merged) {
      // Match raw text first, then escape each piece. Never highlight inside entities.
      html += escapeHtml(raw.slice(cursor, start)) + "<mark>" + escapeHtml(raw.slice(start, end)) + "</mark>";
      cursor = end;
    }
    return html + escapeHtml(raw.slice(cursor));
  }

  function safeUrl(value) {
    try {
      const url = new URL(String(value));
      return ["https:", "http:"].includes(url.protocol) ? url.href : "";
    } catch (_) {
      return "";
    }
  }

  function renderResult(result, query) {
    const href = safeUrl(result.url);
    const title = highlight(result.title, query);
    const link = href ? `<a href="${escapeHtml(href)}" target="_blank" rel="noopener noreferrer">${title}</a>` : title;
    const chips = [["company", ""], ["tag", " tag"], ["date", " tag"]].map(([key, cls]) => result[key] ? `<span class="chip${cls}">${highlight(result[key], query)}</span>` : "").join("");
    return `<article class="result"><h2>${link}</h2><div class="chips">${chips}</div><p class="snippet">${highlight(result.text, query)}</p><div class="cite">doc_id: ${escapeHtml(result.doc_id)} · chunk_id: ${escapeHtml(result.chunk_id)}</div></article>`;
  }

  return { createSearchIndex, queryTerms, escapeHtml, highlight, safeUrl, renderResult };
});
