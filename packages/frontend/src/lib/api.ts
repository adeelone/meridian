import { z } from "zod";

export const resultSchema = z.object({
  id: z.string(),
  title: z.string(),
  url: z.string(),
  domain: z.string().optional(),
  author: z.string().nullable().optional(),
  published_date: z.string().nullable().optional(),
  score: z.number().nullable().optional(),
  text: z.string().nullable().optional(),
  highlights: z.array(z.string()).default([]),
  summary: z.string().nullable().optional()
});

export type SearchResult = z.infer<typeof resultSchema>;

export type QuotaSnapshot = {
  limit: number;
  used_today: number;
  remaining: number;
  cache_hits_today: number;
  warning?: string;
};

export type HistoryItem = {
  id: number;
  query: string;
  result_count: number;
};

export type CollectionSummary = {
  name: string;
  count: number;
};

export type Filters = {
  num_results: number;
  type: "neural" | "keyword" | "auto";
  use_autoprompt: boolean;
  category?: string;
  include_domains: string[];
  exclude_domains: string[];
  start_published_date?: string;
  end_published_date?: string;
  start_crawl_date?: string;
  end_crawl_date?: string;
  include_text: string[];
  exclude_text: string[];
};

export const defaultFilters: Filters = {
  num_results: 10,
  type: "auto",
  use_autoprompt: true,
  include_domains: [],
  exclude_domains: [],
  include_text: [],
  exclude_text: []
};

async function post<T>(url: string, body: unknown): Promise<T> {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(payload.detail || "Request failed.");
  }
  return response.json();
}

export function normalizeDomain(value: string): string {
  const withProtocol = value.includes("://") ? value : `https://${value}`;
  const parsed = new URL(withProtocol);
  return parsed.hostname.replace(/^www\./, "").toLowerCase();
}

export async function search(query: string, filters: Filters) {
  return post<{ results: SearchResult[]; autoprompt?: string }>("/api/search", { query, filters });
}

export async function answer(query: string, filters: Filters) {
  return post<{ answer: string; sources: Array<{ index: number; title: string; url: string; snippet: string }>; warning?: string }>("/api/answer", { query, filters });
}

export async function similar(url: string, filters: Filters) {
  return post<{ results: SearchResult[] }>("/api/similar", { url, filters });
}

export async function quota() {
  return fetch("/api/quota").then((response) => response.json() as Promise<QuotaSnapshot>);
}

export async function history() {
  return fetch("/api/history").then((response) => response.json() as Promise<{ items: HistoryItem[] }>);
}

export async function collections() {
  return fetch("/api/collections").then((response) => response.json() as Promise<{ items: CollectionSummary[] }>);
}

export async function saveToCollection(collection: string, result: SearchResult, note = "") {
  return post<{ ok: boolean }>("/api/collections", { collection, result, note });
}

export async function exportResults(query: string, filters: Filters, fmt = "markdown") {
  return post<{ content: string }>(`/api/export/results/${fmt}`, { query, filters });
}

export async function exportAnswer(query: string, filters: Filters, fmt = "markdown") {
  return post<{ content: string }>(`/api/export/answer/${fmt}`, { query, filters });
}
