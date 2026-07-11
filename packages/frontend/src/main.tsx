import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider, useMutation, useQuery } from "@tanstack/react-query";
import { Bookmark, Copy, ExternalLink, GitBranch, History, Library, Search, Sparkles, Zap } from "lucide-react";
import { answer, collections, defaultFilters, Filters, history, normalizeDomain, quota, search, similar, SearchResult } from "./lib/api";
import "./styles.css";

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Meridian />
    </QueryClientProvider>
  );
}

function Meridian() {
  const [query, setQuery] = useState("semantic search evaluation benchmarks");
  const [filters, setFilters] = useState<Filters>(defaultFilters);
  const [tab, setTab] = useState<"search" | "answer">("search");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [selectedSimilar, setSelectedSimilar] = useState<SearchResult | null>(null);
  const quotaQuery = useQuery({ queryKey: ["quota"], queryFn: quota });
  const historyQuery = useQuery({ queryKey: ["history"], queryFn: history });
  const collectionsQuery = useQuery({ queryKey: ["collections"], queryFn: collections });
  const searchMutation = useMutation({
    mutationFn: () => search(query, filters),
    onSuccess: (payload) => setResults(payload.results)
  });
  const answerMutation = useMutation({ mutationFn: () => answer(query, filters) });
  const similarMutation = useMutation({ mutationFn: (url: string) => similar(url, filters), onSuccess: () => null });

  const run = () => {
    if (tab === "answer") answerMutation.mutate();
    else searchMutation.mutate();
  };

  const shareUrl = useMemo(() => {
    const state = btoa(JSON.stringify({ query, filters }));
    return `${location.origin}${location.pathname}?saved=${state}`;
  }, [query, filters]);

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand"><span>M</span><strong>Meridian</strong></div>
        <nav>
          <a className="active"><Search size={17} /> Search</a>
          <a><Sparkles size={17} /> Answer</a>
          <a><Library size={17} /> Collections</a>
          <a><History size={17} /> History</a>
          <a><Zap size={17} /> Quota</a>
        </nav>
      </aside>
      <main>
        <header className="topbar">
          <div className="searchbox">
            <Search size={20} />
            <input value={query} onChange={(event) => setQuery(event.target.value)} onKeyDown={(event) => event.key === "Enter" && run()} aria-label="Search query" />
            <button onClick={run}>{searchMutation.isPending || answerMutation.isPending ? "Searching" : "Run"}</button>
          </div>
          <div className="modes">
            {(["neural", "keyword", "auto"] as const).map((mode) => (
              <button key={mode} className={filters.type === mode ? "selected" : ""} onClick={() => setFilters({ ...filters, type: mode })}>{mode}</button>
            ))}
            <label><input type="checkbox" checked={filters.use_autoprompt} onChange={(event) => setFilters({ ...filters, use_autoprompt: event.target.checked })} /> Autoprompt</label>
          </div>
        </header>
        <div className="tabs">
          <button className={tab === "search" ? "active" : ""} onClick={() => setTab("search")}>Results</button>
          <button className={tab === "answer" ? "active" : ""} onClick={() => setTab("answer")}>Cited answer</button>
          <button onClick={() => navigator.clipboard.writeText(shareUrl)}>Copy saved-search link</button>
        </div>
        <section className="workspace">
          <FiltersPanel filters={filters} setFilters={setFilters} />
          <section className="results">
            {(searchMutation.error || answerMutation.error) && <div className="error">{String((searchMutation.error || answerMutation.error)?.message)}</div>}
            {tab === "answer" ? (
              <AnswerView payload={answerMutation.data} loading={answerMutation.isPending} />
            ) : (
              <ResultList results={results} loading={searchMutation.isPending} onSimilar={(result) => { setSelectedSimilar(result); similarMutation.mutate(result.url); }} />
            )}
          </section>
          <aside className="inspector">
            <QuotaPanel quota={quotaQuery.data} />
            {selectedSimilar && <SimilarityPanel result={selectedSimilar} results={similarMutation.data?.results || []} loading={similarMutation.isPending} />}
            <MiniPanel title="Collections" items={(collectionsQuery.data?.items || []).map((item: any) => `${item.name} (${item.count})`)} />
            <MiniPanel title="History" items={(historyQuery.data?.items || []).slice(0, 5).map((item: any) => `${item.query} - ${item.result_count}`)} />
          </aside>
        </section>
      </main>
    </div>
  );
}

function FiltersPanel({ filters, setFilters }: { filters: Filters; setFilters: (filters: Filters) => void }) {
  const [domain, setDomain] = useState("");
  const addDomain = () => {
    if (!domain.trim()) return;
    setFilters({ ...filters, include_domains: Array.from(new Set([...filters.include_domains, normalizeDomain(domain)])) });
    setDomain("");
  };
  return (
    <aside className="filters">
      <h2>Filters</h2>
      <label>Category<select value={filters.category || ""} onChange={(event) => setFilters({ ...filters, category: event.target.value || undefined })}>
        <option value="">Any category</option><option>news</option><option>company</option><option>pdf</option><option>papers</option><option>github</option><option>tweet</option>
      </select></label>
      <label>Include domains<div className="chip-input"><input value={domain} onChange={(event) => setDomain(event.target.value)} onKeyDown={(event) => event.key === "Enter" && addDomain()} placeholder="https://www.tiktok.com" /><button onClick={addDomain}>Add</button></div></label>
      <div className="chips">{filters.include_domains.map((item) => <button key={item} onClick={() => setFilters({ ...filters, include_domains: filters.include_domains.filter((domain) => domain !== item) })}>{item}</button>)}</div>
      <label>Published after<input type="date" onChange={(event) => setFilters({ ...filters, start_published_date: event.target.value })} /></label>
      <label>Published before<input type="date" onChange={(event) => setFilters({ ...filters, end_published_date: event.target.value })} /></label>
      <label>Result count <strong>{filters.num_results}</strong><input type="range" min="1" max="50" value={filters.num_results} onChange={(event) => setFilters({ ...filters, num_results: Number(event.target.value) })} /></label>
      <label>Include text<input placeholder="exact phrase" onBlur={(event) => setFilters({ ...filters, include_text: event.target.value ? [event.target.value] : [] })} /></label>
      <label>Exclude text<input placeholder="noise words" onBlur={(event) => setFilters({ ...filters, exclude_text: event.target.value ? [event.target.value] : [] })} /></label>
    </aside>
  );
}

function ResultList({ results, loading, onSimilar }: { results: SearchResult[]; loading: boolean; onSimilar: (result: SearchResult) => void }) {
  if (loading) return <div className="skeleton"><span /><span /><span /></div>;
  if (!results.length) return <div className="empty">No results yet. Run a search, or broaden domain/date filters if results come back empty.</div>;
  return <>{results.map((result) => <ResultCard key={result.id} result={result} onSimilar={() => onSimilar(result)} />)}</>;
}

function ResultCard({ result, onSimilar }: { result: SearchResult; onSimilar: () => void }) {
  const author = result.author || "Unknown author";
  return (
    <article className="result-card" id={result.id}>
      <div className="favicon">{(result.domain || "m").slice(0, 1).toUpperCase()}</div>
      <div>
        <div className="meta">{result.domain || "Unknown domain"} · {result.published_date || "No date"} · {author}</div>
        <h3>{result.title}</h3>
        <p>{result.text || result.summary || result.highlights?.[0] || "No snippet was returned for this result."}</p>
        <div className="score"><span style={{ width: `${Math.round((result.score || 0.68) * 100)}%` }} /></div>
        <div className="actions">
          <a href={result.url} target="_blank" rel="noreferrer"><ExternalLink size={15} /> Open</a>
          <button onClick={onSimilar}><GitBranch size={15} /> Similar</button>
          <button><Bookmark size={15} /> Save</button>
          <button onClick={() => navigator.clipboard.writeText(`${result.title} - ${result.url}`)}><Copy size={15} /> Copy citation</button>
        </div>
      </div>
    </article>
  );
}

function AnswerView({ payload, loading }: { payload?: { answer: string; sources: Array<{ index: number; title: string; url: string; snippet: string }>; warning?: string }; loading: boolean }) {
  if (loading) return <div className="skeleton"><span /><span /><span /></div>;
  if (!payload) return <div className="empty">Run answer mode to synthesize a cited response from retrieved source text.</div>;
  return <div className="answer"><p>{payload.answer}</p>{payload.warning && <div className="warning">{payload.warning}</div>}<h3>Sources</h3>{payload.sources.map((source) => <article key={source.index} id={`source-${source.index}`}><strong>[{source.index}] {source.title}</strong><a href={source.url}>{source.url}</a><p>{source.snippet}</p></article>)}</div>;
}

function QuotaPanel({ quota }: { quota?: any }) {
  const percent = quota ? Math.round((quota.remaining / quota.limit) * 100) : 100;
  return <section className="panel"><h2>Quota</h2><strong>{quota?.remaining ?? "..."}</strong><span>requests remaining</span><div className="meter"><i style={{ width: `${percent}%` }} /></div><small>{quota?.used_today ?? 0} used today · {quota?.cache_hits_today ?? 0} cache hits</small>{quota?.warning && <div className="warning">{quota.warning}</div>}</section>;
}

function SimilarityPanel({ result, results, loading }: { result: SearchResult; results: SearchResult[]; loading: boolean }) {
  return <section className="panel"><h2>Similar to</h2><p>{result.title}</p>{loading ? <small>Loading related pages...</small> : results.map((item) => <a key={item.id} href={item.url}>{item.title}</a>)}</section>;
}

function MiniPanel({ title, items }: { title: string; items: string[] }) {
  return <section className="panel"><h2>{title}</h2>{items.length ? items.map((item) => <p key={item}>{item}</p>) : <small>No local entries yet.</small>}</section>;
}

createRoot(document.getElementById("root")!).render(<App />);
