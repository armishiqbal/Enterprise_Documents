/**
 * Typed API Client for the Enterprise Document Intelligence RAG Platform.
 * Supports direct REST API calls, local proxying, and Vercel serverless functions.
 */

export interface StatsResponse {
  collection_name: string;
  total_chunks: number;
  unique_documents: number;
  persist_directory: string;
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

const API_BASE_URL = typeof window !== "undefined"
  ? (process.env.NEXT_PUBLIC_API_URL || "")
  : (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000");

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        ...(options.headers || {}),
      },
    });

    if (!res.ok) {
      const errorBody = await res.text();
      let errorMsg = `HTTP ${res.status}: ${res.statusText}`;
      try {
        const parsed = JSON.parse(errorBody);
        if (parsed.detail) errorMsg = parsed.detail;
      } catch {
        if (errorBody) errorMsg = errorBody;
      }
      throw new Error(errorMsg);
    }

    return await res.json();
  } catch (err: any) {
    console.error(`API Error [${endpoint}]:`, err);
    throw err;
  }
}

export async function fetchStats(): Promise<StatsResponse> {
  return request<StatsResponse>("/api/v1/stats");
}

export async function uploadFiles(files: File[]): Promise<IngestBatchResponse> {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }

  const url = `${API_BASE_URL}/api/v1/ingest`;
  const res = await fetch(url, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(errText || "Failed to upload files");
  }

  return await res.json();
}

export async function queryRAG(
  query: string,
  k: number = 4,
  score_threshold: number = 0.0
): Promise<QueryResponse> {
  return request<QueryResponse>("/api/v1/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, k, score_threshold }),
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
