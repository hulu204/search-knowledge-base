# Stored production chunks for Pages

The Pages interface is **offline static lexical retrieval**. It does not run
bge-m3, dense/sparse RRF, an LLM, ingestion, or query-time chunking. Results show
the complete original `chunks.text`, HTML-escaped with safe highlighting, with
the source title, URL, `doc_id`, and `chunk_id`. Only HTTP(S) source URLs become
links. Lexical normalization is used for search copies and index metadata; it
never changes the text stored in a text shard or displayed in a result.

The committed Pages corpus is a dual-filtered export of **unmodified production
stored chunks**: **2402 documents / 25838 chunks**, `status: stored-chunks`,
`chunk_boundaries: unmodified-stored-chunks`. The document ID SHA-256 is
`0cb203aa14438799f4bfd4d61861817dab28c3873255a2f4dacf4da3566231eb`. The first-load
bootstrap `search-index.json` is **1,637,633 bytes raw / 446,207 bytes gzip**.
Text is split into 302 shards (max 131,071 bytes); lexical postings are 256
on-demand files. The previous 44 MB `demo-index.json` (`utf8-bytes-v1` fallback
cuts) is not the default corpus and is not in the tree. Fixture tests still
cover the exporter and browser without requiring a private database checkout.

## Export directly from production SQLite

Run from a public checkout with the `articles/` directory present. The exporter
uses only Python's standard library, reads SQLite with URI `mode=ro`, and needs
only the production `docs` and `chunks` tables. It does not require
`ingestion_metadata` or read `figures`.

```sh
python3 -m sgt_kb export-pages \
  --db /path/to/production/kb.sqlite \
  --output-dir /tmp/sgt-pages-production \
  --require-production-counts \
  --write-intermediate /tmp/public-chunks.jsonl
```

`--require-production-counts` requires **2402 documents / 25838 chunks** and
the coordinator-verified document ID SHA-256:
`0cb203aa14438799f4bfd4d61861817dab28c3873255a2f4dacf4da3566231eb`.
The digest is `sha256("\n".join(sorted(doc_ids)).encode("utf-8"))`, with no
trailing newline. These checks identify the expected article subset; they do
not independently prove which tokenizer originally created its chunks.

The allowlist comes from the **2421** public `articles/*.md` stems. A source must
both have an allowed `doc_id` and the exact safe path
`articles/<doc_id>.md`. Expected nonpublic production documents, including safe
nested `extra-docs/` paths, are excluded. Unexpected paths, a private path
attached to a public ID, traversal, malformed rows, orphan chunks, duplicate
chunk IDs, and duplicate `(doc_id, seq)` pairs cause refusal. All emitted text
comes directly from the selected stored rows, preserving chunk IDs, sequence
numbers, text and boundaries. No chunks are combined, split, truncated, or
summarized. An individual chunk larger than the shard target stays whole.

The exporter selects only these metadata fields from `docs`:
`doc_id`, `path`, `title`, `company`, `tag`, `date`, `url`. It selects only
`chunk_id`, `doc_id`, `seq`, `text` from `chunks`. It omits hashes, OCR, figure
blobs, and all other columns. Public article company/source clues are preserved.
Databases identified as `utf8-bytes` fallback ingestion are refused rather than
relabelled as production chunks.

The command never copies a database. A Pages output must be a separate
directory, cannot contain the input database/export, and cannot use a SQLite
or JSON filename. A JSONL output cannot overwrite or alias the input, point
through a symlink, or be written inside an input export directory. Intermediate
files are written with an atomic replacement. The exporter replaces only its
marked `search-chunks/` and `search-postings/` directories; an existing unmarked
directory is refused.

## Integrate an already exported intermediate

An intermediate is either flat JSONL or a JSON object with exactly `docs` and
`chunks` arrays. A flat JSONL row has exactly these fields:

```json
{"doc_id":"public-article-id","path":"articles/public-article-id.md","title":"Source title","company":"Public source clue","tag":"搜索","date":"2026-01-01","url":"https://example.org/article","chunk_id":123,"seq":5,"text":"Complete, unchanged stored chunk text.\n"}
```

In structured JSON, each `docs` item has the seven source fields above and each
`chunks` item has `chunk_id`, `doc_id`, `seq`, `text`. A directory input reads
sorted `*.jsonl` files. Every intermediate row must already be public and
allowlisted; private rows and extra fields are refused. Files containing raw
SQLite data are refused even if renamed to `.json`.

After the coordinator supplies that intermediate:

```sh
python3 -m sgt_kb export-pages \
  --input /workspace/sgt-kb-codex-run2/prod-export/ \
  --output-dir docs \
  --require-production-counts
node --test tests/pages_search.test.mjs
python3 -m unittest discover -s tests
```

To intentionally restore the empty default while waiting for production:

```sh
python3 -m sgt_kb export-pages --pending --output-dir docs
```

## Static format version 3 and request sizes

The homepage fetches `search-index.json`, containing source metadata, compact
chunk locators, available posting buckets, and text shard descriptors. It does
not include chunk text or the full lexical postings. Each chunk locator is:

```text
[chunk_id, source_doc_array_index, seq, text_shard_array_index, normalized_codepoint_length]
```

The lexical index is split into up to 256
`search-postings/00.json`–`search-postings/ff.json` files. A token maps to
`[[chunk_array_index, frequency], ...]`. Its bucket is FNV-1a 32-bit over the
token's UTF-8 bytes modulo 256. CJK runs yield overlapping bigrams prefixed
`c:`; Unicode words yield `w:` tokens. **CJK unigrams are never indexed.**
For lexical copies only, normalization is NFKC, lowercase, and ECMAScript
whitespace collapse to one space, without trimming. Python and browser tests
cover edge whitespace, supplementary Han, emoji, combining accents, fullwidth
characters, and Kana.

Query terms fetch only needed posting buckets. Intersections nominate candidate
chunks; original text is loaded from needed `search-chunks/0000.json` files and
the full phrase is verified before a hit is shown. Bilingual query-understanding
aliases apply equally to all sources. `查询理解` is not reduced to separate
characters, preventing unrelated TuGraph results. Stored deep-body chunks are
preferred over leads and tables of contents.

Text shards target **128 KiB raw**, with whole original chunks. Their shape is
`{"format_version":3,"chunks":[{"chunk_id":123,"doc_id":"...","seq":5,"text":"..."}]}`.
The manifest and bootstrap record exact raw/gzip sizes and SHA-256 values for
integrity and review. Actual production bootstrap and shard sizes remain
unknown until its export is integrated. With no integrated corpus, there are
no posting or text JSON shard downloads.

With the production export integrated, the homepage first load is HTML +
`search.js` + `search-index.json`: bootstrap **1,637,633 bytes raw / 446,207
bytes gzip**. Posting files total 53,639,777 bytes (256 shards, fetched only for
query terms; typical shard about 120–267 KiB, max 454,098). Text shards total
39,133,933 bytes (302 files, max 131,071 bytes) and are fetched only for
displayed hits. No synthetic corpus is shipped. The earlier empty pending
payload (26,377 bytes raw first load) remains available via `--pending` for
local experiments.

For broad queries, the browser initially examines 48 candidates and all nominated
chunks of selected documents. It continues until it has 12 exact document hits
or has exhausted the candidates. When more candidates remain, the UI shows
checked/total counts and a Continue button that increases the budget. This is
an incremental lexical ranking; the first batch is not a guarantee of globally
complete top-12 results. A no-match response requires exhausting and checking
all candidates. Tests can request `exhaustive: true`.

`search-manifest.json` records source kind, excluded-document count, expected
production counts/ID hash, actual counts, public allowlist count, payload sizes,
and hashes. The source database location is not published. Source URLs and
article text can themselves contain public third-party references; the allowlist
is a provenance boundary, not a claim that arbitrary article text is free of
sensitive strings. Review the exported text/URLs before publication. Never add
private company documents, models, or figure binaries to this corpus.
