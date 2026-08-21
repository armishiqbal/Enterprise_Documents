/**
 * Typed API Client for the Enterprise Document Intelligence RAG Platform.
 * Supports direct REST API calls, local proxying, and Vercel serverless functions.
 */

export interface StatsResponse {
  collection_name: string;
  total_chunks: number;
  unique_documents: number;
  persist_directory: string;
  indexed_files?: string[];
}

export interface CitationItem {
  chunk_id: string;
  filename: string;
  page_number?: number | null;
  score: number;
  score_percent: string;
  source_path: string;
  snippet: string;
}

export interface GroundingInfo {
  groundedness_score: number;
  score_percent: string;
  confidence_label: string;
  is_verified: boolean;
  badge_color: string;
}

export interface QueryResponse {
  query: string;
  answer: string;
  citations: CitationItem[];
  model: string;
  retrieved_count: number;
  grounding?: GroundingInfo;
}

export interface IngestFileResponse {
  filename: string;
  file_type: string;
  doc_id: string;
  chunks_generated: number;
  status: string;
}

export interface IngestBatchResponse {
  total_files_processed: number;
  total_chunks_indexed: number;
  results: IngestFileResponse[];
}

export interface WebhookResponse {
  success: boolean;
  event: string;
  event_id: string;
  message: string;
  timestamp: string;
  data?: any;
}

export function getApiBaseUrl(): string {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  if (typeof window !== "undefined") {
    const hostname = window.location.hostname || "localhost";
    return `http://${hostname}:8080`;
  }
  return "http://127.0.0.1:8080";
}

async function parseJsonResponse<T>(res: Response): Promise<T> {
  const text = await res.text();
  if (!text.trim()) {
    throw new Error(`Empty response body (HTTP ${res.status})`);
  }
  try {
    return JSON.parse(text) as T;
  } catch {
    throw new Error(`Invalid JSON response (HTTP ${res.status})`);
  }
}

function extractErrorMessage(status: number, statusText: string, bodyText: string): string {
  let errorMsg = `HTTP ${status}: ${statusText}`;
  if (!bodyText) return errorMsg;

  try {
    const parsed = JSON.parse(bodyText);
    if (parsed.detail) {
      return typeof parsed.detail === "string" ? parsed.detail : JSON.stringify(parsed.detail);
    }
    if (parsed.message) return parsed.message;
  } catch {
    if (bodyText.trim().startsWith("<")) {
      const titleMatch = bodyText.match(/<title>(.*?)<\/title>/i);
      if (titleMatch && titleMatch[1]) {
        return `HTTP ${status} - ${titleMatch[1]}`;
      }
      return `HTTP ${status}: Backend service unavailable or route not found.`;
    }
    return bodyText;
  }
  return errorMsg;
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const baseUrls = typeof window !== "undefined"
    ? ["", getApiBaseUrl(), "http://127.0.0.1:8080", "http://localhost:8080"]
    : [getApiBaseUrl(), "http://127.0.0.1:8080", "http://localhost:8080"];

  // Deduplicate
  const uniqueBaseUrls = Array.from(new Set(baseUrls.filter((b) => b !== undefined)));

  let lastError: any = null;

  for (const base of uniqueBaseUrls) {
    const url = `${base}${endpoint}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 25000);

    try {
      const res = await fetch(url, {
        ...options,
        signal: options.signal || controller.signal,
        headers: {
          ...(options.headers || {}),
        },
      });

      clearTimeout(timeoutId);

      if (!res.ok) {
        const errorBody = await res.text();
        const errorMsg = extractErrorMessage(res.status, res.statusText, errorBody);
        throw new Error(errorMsg);
      }

      return await parseJsonResponse<T>(res);
    } catch (err: any) {
      clearTimeout(timeoutId);
      lastError = err;
      if (err.message && (err.message.startsWith("HTTP") || err.message.startsWith("Invalid JSON") || err.message.startsWith("Empty response"))) {
        throw err;
      }
    }
  }

  const msg = lastError?.name === "AbortError"
    ? "Request timed out after 25s. Please check if the FastAPI backend is running on port 8080."
    : (lastError?.message || "Failed to connect to backend server on port 8080.");
  throw new Error(msg);
}

export async function fetchStats(): Promise<StatsResponse> {
  try {
    return await request<StatsResponse>("/api/v1/stats");
  } catch {
    return {
      collection_name: "document_chunks",
      total_chunks: 0,
      unique_documents: 0,
      persist_directory: "data/vectorstore",
      indexed_files: [],
    };
  }
}

export async function uploadFiles(files: File[]): Promise<IngestBatchResponse> {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }

  const baseUrls = typeof window !== "undefined"
    ? ["", getApiBaseUrl(), "http://127.0.0.1:8080", "http://localhost:8080"]
    : [getApiBaseUrl(), "http://127.0.0.1:8080", "http://localhost:8080"];
  const uniqueBaseUrls = Array.from(new Set(baseUrls));

  let lastError: any = null;

  for (const base of uniqueBaseUrls) {
    try {
      const url = `${base}/api/v1/ingest`;
      const res = await fetch(url, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errText = await res.text();
        const errorMsg = extractErrorMessage(res.status, res.statusText, errText);
        throw new Error(errorMsg || "Failed to upload files");
      }

      return await parseJsonResponse<IngestBatchResponse>(res);
    } catch (err: any) {
      lastError = err;
      if (err.message && (err.message.startsWith("HTTP") || err.message.startsWith("Invalid JSON") || err.message.startsWith("Empty response"))) {
        throw err;
      }
    }
  }

  throw new Error(lastError?.message || "Failed to upload files to backend server.");
}

export async function queryRAG(
  query: string,
  k: number = 4,
  score_threshold: number = 0.0,
  provider?: string,
  model?: string,
  apiKey?: string,
  baseUrl?: string,
  searchStrategy?: string
): Promise<QueryResponse> {
  return request<QueryResponse>("/api/v1/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      k,
      score_threshold,
      provider: provider?.toLowerCase(),
      model,
      api_key: apiKey,
      base_url: baseUrl,
      search_strategy: searchStrategy,
    }),
  });
}

export async function deleteDocument(docId: string): Promise<{ message: string; doc_id: string }> {
  return request<{ message: string; doc_id: string }>(`/api/v1/documents/${encodeURIComponent(docId)}`, {
    method: "DELETE",
  });
}

export async function resetVectorStore(): Promise<{ message: string }> {
  return request<{ message: string }>("/api/v1/reset", {
    method: "DELETE",
  });
}

export async function sendWebhook(
  event: string,
  data: any,
  sender: string = "web_app",
  secret?: string
): Promise<WebhookResponse> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (secret) {
    headers["X-Webhook-Secret"] = secret;
  }

  return request<WebhookResponse>("/api/v1/webhook", {
    method: "POST",
    headers,
    body: JSON.stringify({
      event,
      sender,
      data,
      timestamp: new Date().toISOString(),
    }),
  });
}
