"use client";

import { FormEvent, useEffect, useState } from "react";

type ApiState = "checking" | "online" | "offline";

type Facet = {
  name: string;
  count: number;
};

type Stats = {
  docs: number;
  chunks: number;
  figures: number;
  company_count: number;
  tag_count: number;
  companies: Facet[];
  tags: Facet[];
};

type SearchResult = {
  doc_id: string;
  chunk_id: number;
  seq: number;
  path: string;
  title: string;
  company: string;
  tag: string;
  date: string;
  url: string;
  text: string;
  score: number;
};

type DocumentDetail = Omit<SearchResult, "text" | "score" | "chunk_id" | "seq" | "path"> & {
  markdown: string;
};

const API_BASE = "http://127.0.0.1:8766";

const emptyStats: Stats = {
  docs: 0,
  chunks: 0,
  figures: 0,
  company_count: 0,
  tag_count: 0,
  companies: [],
  tags: [],
};

const suggestions = [
  "多路召回如何做融合与去重",
  "搜索冷启动的工程实践",
  "向量检索如何控制延迟和成本",
  "RAG 评测指标与 badcase 分析",
];

async function request(path: string, init?: RequestInit) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || `请求失败：${response.status}`);
  return data;
}

function compactNumber(value: number) {
  return new Intl.NumberFormat("zh-CN", { notation: "compact" }).format(value);
}

function ResultCard({
  item,
  index,
  onOpen,
}: {
  item: SearchResult;
  index: number;
  onOpen: (docId: string) => void;
}) {
  return (
    <article className="result-card">
      <div className="result-rank">{String(index + 1).padStart(2, "0")}</div>
      <div className="result-body">
        <div className="result-meta">
          {item.company && <span className="company-pill">{item.company}</span>}
          {item.tag && <span>{item.tag}</span>}
          {item.date && <span>{item.date}</span>}
        </div>
        <h3>{item.title || "未命名文档"}</h3>
        <p>{item.text}</p>
        <div className="result-actions">
          <button className="text-button" onClick={() => onOpen(item.doc_id)}>
            阅读全文
          </button>
          <span className="doc-id">
            doc_id: {item.doc_id} · chunk_id: {item.chunk_id} · seq: {item.seq}
          </span>
          {item.url && (
            <a href={item.url} target="_blank" rel="noreferrer">
              查看原文 ↗
            </a>
          )}
        </div>
      </div>
    </article>
  );
}

export default function Home() {
  const [apiState, setApiState] = useState<ApiState>("checking");
  const [stats, setStats] = useState<Stats>(emptyStats);
  const [query, setQuery] = useState("");
  const [company, setCompany] = useState("");
  const [tag, setTag] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searchedQuery, setSearchedQuery] = useState("");
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState("");
  const [document, setDocument] = useState<DocumentDetail | null>(null);
  const [loadingDocument, setLoadingDocument] = useState(false);

  useEffect(() => {
    request("/api/stats")
      .then((data) => {
        setStats(data);
        setApiState("online");
      })
      .catch(() => setApiState("offline"));
  }, []);

  useEffect(() => {
    if (!document) return;
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setDocument(null);
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [document]);

  async function runSearch(term = query, nextCompany = company, nextTag = tag) {
    const normalized = term.trim();
    if (!normalized) return;
    setQuery(normalized);
    setSearching(true);
    setError("");
    setResults([]);
    try {
      const data = await request("/api/search", {
        method: "POST",
        body: JSON.stringify({
          query: normalized,
          company: nextCompany,
          tag: nextTag,
          top_k: 10,
        }),
      });
      setResults(data.results || []);
      setSearchedQuery(normalized);
      setApiState("online");
    } catch (searchError) {
      setError(searchError instanceof Error ? searchError.message : "检索失败");
      setApiState("offline");
    } finally {
      setSearching(false);
    }
  }

  async function openDocument(docId: string) {
    setLoadingDocument(true);
    setError("");
    try {
      const data = await request(`/api/doc?doc_id=${encodeURIComponent(docId)}`);
      setDocument(data);
    } catch (documentError) {
      setError(documentError instanceof Error ? documentError.message : "文档读取失败");
    } finally {
      setLoadingDocument(false);
    }
  }

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    runSearch();
  }

  function clearFilters() {
    setCompany("");
    setTag("");
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">K</span>
          <div>
            <strong>SGT KB</strong>
            <small>工业实践知识库</small>
          </div>
        </div>

        <div className="sidebar-section">
          <span className="sidebar-label">知识范围</span>
          <p>搜索 · 推荐 · 广告 · RAG</p>
          <p>索引 · 召回 · 排序 · 评测</p>
        </div>

        <div className="sidebar-section facets">
          <span className="sidebar-label">主要来源</span>
          {stats.companies.slice(0, 6).map((item) => (
            <button key={item.name} onClick={() => setCompany(item.name)}>
              <span>{item.name}</span>
              <small>{item.count}</small>
            </button>
          ))}
        </div>

        <div className="sidebar-status">
          <div className="status-title">
            <span className={`status-dot ${apiState}`} />
            {apiState === "online"
              ? "本地索引已连接"
              : apiState === "checking"
                ? "正在连接索引"
                : "本地服务未启动"}
          </div>
          <p>
            {apiState === "online"
              ? `${stats.docs.toLocaleString()} 篇文档可检索`
              : "启动工作台后自动恢复"}
          </p>
        </div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <span className="eyebrow">LOCAL HYBRID RETRIEVAL</span>
            <h1>知识检索</h1>
          </div>
          <span className="privacy-chip">内容仅在本机流转</span>
        </header>

        <section className="search-hero">
          <div className="hero-copy">
            <span className="eyebrow">SGT KNOWLEDGE BASE</span>
            <h2>从真实工程实践里，<br />找到可以追溯的答案。</h2>
            <p>
              使用 dense + sparse 双路检索与 RRF 融合，定位行业案例、工程取舍和原始文档。
            </p>
          </div>

          <form className="search-panel" onSubmit={submitSearch}>
            <label htmlFor="kb-query">描述你要查的问题</label>
            <div className="search-row">
              <input
                id="kb-query"
                autoFocus
                placeholder="例如：多路召回如何做融合与去重"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
              />
              <button className="primary-button" disabled={!query.trim() || searching}>
                {searching ? "检索中…" : "检索知识库"}
              </button>
            </div>

            <div className="filter-row">
              <label>
                来源
                <input
                  list="company-options"
                  placeholder="全部来源"
                  value={company}
                  onChange={(event) => setCompany(event.target.value)}
                />
              </label>
              <label>
                主题
                <input
                  list="tag-options"
                  placeholder="全部主题"
                  value={tag}
                  onChange={(event) => setTag(event.target.value)}
                />
              </label>
              {(company || tag) && (
                <button type="button" className="clear-button" onClick={clearFilters}>
                  清除筛选
                </button>
              )}
            </div>

            <datalist id="company-options">
              {stats.companies.map((item) => <option key={item.name} value={item.name} />)}
            </datalist>
            <datalist id="tag-options">
              {stats.tags.map((item) => <option key={item.name} value={item.name} />)}
            </datalist>

            <div className="suggestions" aria-label="示例查询">
              {suggestions.map((item) => (
                <button key={item} type="button" onClick={() => runSearch(item)}>
                  {item}
                </button>
              ))}
            </div>
          </form>
        </section>

        <section className="stats-grid" aria-label="知识库统计">
          <div><strong>{stats.docs.toLocaleString()}</strong><span>文档</span></div>
          <div><strong>{compactNumber(stats.chunks)}</strong><span>知识片段</span></div>
          <div><strong>{stats.figures.toLocaleString()}</strong><span>已解析配图</span></div>
          <div><strong>{stats.company_count}</strong><span>内容来源</span></div>
          <div><strong>{stats.tag_count}</strong><span>主题标签</span></div>
        </section>

        {error && <div className="error-banner">{error}</div>}

        <section className="content-grid">
          <div className="results-section">
            <div className="section-heading">
              <div>
                <span className="eyebrow">SEARCH RESULTS</span>
                <h2>{searchedQuery ? `“${searchedQuery}”` : "开始一次知识检索"}</h2>
              </div>
              {searchedQuery && (
                <span className="result-count">
                  {searching ? "正在召回" : `${results.length} 条结果`}
                </span>
              )}
            </div>

            {!searchedQuery && !searching && (
              <div className="empty-state">
                <span>⌕</span>
                <strong>输入自然语言问题</strong>
                <p>结果会保留来源、主题、doc_id 和原文链接，便于继续追溯。</p>
              </div>
            )}

            {searchedQuery && !searching && results.length === 0 && (
              <div className="empty-state">
                <span>○</span>
                <strong>没有找到匹配内容</strong>
                <p>试试减少筛选条件，或改用更具体的场景、问题和方法名。</p>
              </div>
            )}

            <div className="result-list">
              {results.map((item, index) => (
                <ResultCard
                  key={`${item.doc_id}-${index}`}
                  item={item}
                  index={index}
                  onOpen={openDocument}
                />
              ))}
            </div>
          </div>

          <aside className="topics-card">
            <span className="eyebrow">TOP TOPICS</span>
            <h2>主要主题</h2>
            <div className="topic-list">
              {stats.tags.slice(0, 10).map((item) => (
                <button key={item.name} onClick={() => setTag(item.name)}>
                  <span>{item.name}</span>
                  <small>{item.count}</small>
                </button>
              ))}
            </div>
            <div className="retrieval-note">
              <strong>检索方式</strong>
              <p>本地 bge-m3 dense + sparse 双路召回，RRF 融合后按文档去重。</p>
            </div>
          </aside>
        </section>
      </section>

      {(document || loadingDocument) && (
        <div className="reader-backdrop" onClick={() => setDocument(null)}>
          <aside
            className="reader-drawer"
            role="dialog"
            aria-modal="true"
            aria-label="文档全文"
            onClick={(event) => event.stopPropagation()}
          >
            {loadingDocument && !document ? (
              <div className="reader-loading">正在读取文档…</div>
            ) : document ? (
              <>
                <header className="reader-header">
                  <div>
                    <div className="result-meta">
                      {document.company && <span className="company-pill">{document.company}</span>}
                      {document.tag && <span>{document.tag}</span>}
                      {document.date && <span>{document.date}</span>}
                    </div>
                    <h2>{document.title}</h2>
                    <span className="doc-id">doc_id: {document.doc_id}</span>
                  </div>
                  <button aria-label="关闭文档" onClick={() => setDocument(null)}>×</button>
                </header>
                <div className="reader-actions">
                  {document.url && (
                    <a href={document.url} target="_blank" rel="noreferrer">查看原文 ↗</a>
                  )}
                </div>
                <pre className="document-content">{document.markdown}</pre>
              </>
            ) : null}
          </aside>
        </div>
      )}
    </main>
  );
}
