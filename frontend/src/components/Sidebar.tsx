"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Server,
  Upload,
  Sliders,
  Database,
  Trash2,
  Key,
  Globe,
  Bot,
  Sparkles,
  CheckCircle,
  AlertCircle,
  FileText,
  Radio,
} from "lucide-react";
import { uploadFiles, resetVectorStore, StatsResponse } from "@/lib/api";

interface SidebarProps {
  stats: StatsResponse | null;
  onStatsRefresh: () => void;
  selectedProvider: string;
  setSelectedProvider: (prov: string) => void;
  selectedModel: string;
  setSelectedModel: (m: string) => void;
  topK: number;
  setTopK: (k: number) => void;
  similarityThreshold: number;
  setSimilarityThreshold: (th: number) => void;
  searchStrategy: string;
  setSearchStrategy: (st: string) => void;
  selectedDocFilter: string;
  setSelectedDocFilter: (doc: string) => void;
  indexedFiles: string[];
  onNavigateSettings?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  stats,
  onStatsRefresh,
  selectedProvider,
  setSelectedProvider,
  selectedModel,
  setSelectedModel,
  topK,
  setTopK,
  similarityThreshold,
  setSimilarityThreshold,
  searchStrategy,
  setSearchStrategy,
  selectedDocFilter,
  setSelectedDocFilter,
  indexedFiles,
  onNavigateSettings,
}) => {
  // Provider API Keys & Config (Stored in localStorage)
  const [openaiKey, setOpenaiKey] = useState("");
  const [groqKey, setGroqKey] = useState("");
  const [customGroqModel, setCustomGroqModel] = useState("");
  const [customOpenaiModel, setCustomOpenaiModel] = useState("");
  const [customUrl, setCustomUrl] = useState("http://localhost:11434/v1");
  const [customKey, setCustomKey] = useState("");
  const [customModel, setCustomModel] = useState("llama3");

  // File Upload State
  const [filesToUpload, setFilesToUpload] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load saved credentials from localStorage
  useEffect(() => {
    if (typeof window !== "undefined") {
      setOpenaiKey(localStorage.getItem("openai_api_key") || "");
      setGroqKey(localStorage.getItem("groq_api_key") || "");
      setCustomUrl(localStorage.getItem("custom_base_url") || "http://localhost:11434/v1");
      setCustomKey(localStorage.getItem("custom_api_key") || "");
      setCustomModel(localStorage.getItem("custom_model_name") || "llama3");
    }
  }, []);

  const handleSaveKey = (type: "openai" | "groq" | "custom") => {
    if (type === "openai") {
      localStorage.setItem("openai_api_key", openaiKey);
      setUploadStatus("✅ OpenAI API Key Saved");
    } else if (type === "groq") {
      localStorage.setItem("groq_api_key", groqKey);
      setUploadStatus("✅ Groq API Key Saved");
    } else {
      localStorage.setItem("custom_base_url", customUrl);
      localStorage.setItem("custom_api_key", customKey);
      localStorage.setItem("custom_model_name", customModel);
      setUploadStatus("✅ Custom Provider Saved");
    }
    setTimeout(() => setUploadStatus(null), 3000);
  };

  const handleClearKey = (type: "openai" | "groq" | "custom") => {
    if (type === "openai") {
      setOpenaiKey("");
      localStorage.removeItem("openai_api_key");
    } else if (type === "groq") {
      setGroqKey("");
      localStorage.removeItem("groq_api_key");
    } else {
      setCustomUrl("");
      setCustomKey("");
      setCustomModel("");
      localStorage.removeItem("custom_base_url");
      localStorage.removeItem("custom_api_key");
      localStorage.removeItem("custom_model_name");
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFilesToUpload(Array.from(e.target.files));
    }
  };

  const handleIngest = async () => {
    if (filesToUpload.length === 0) return;
    setIsUploading(true);
    setUploadStatus("Processing and indexing documents...");

    try {
      const res = await uploadFiles(filesToUpload);
      setUploadStatus(`✅ Successfully indexed ${res.total_chunks_indexed} chunk(s) from ${res.total_files_processed} file(s).`);
      setFilesToUpload([]);
      if (fileInputRef.current) fileInputRef.current.value = "";
      onStatsRefresh();
    } catch (err: any) {
      setUploadStatus(`❌ Ingestion failed: ${err.message}`);
    } finally {
      setIsUploading(false);
      setTimeout(() => setUploadStatus(null), 5000);
    }
  };

  const handleResetDb = async () => {
    if (confirm("Are you sure you want to clear the entire vector database collection?")) {
      try {
        await resetVectorStore();
        onStatsRefresh();
        alert("Vector database successfully cleared.");
      } catch (err: any) {
        alert(`Failed to reset: ${err.message}`);
      }
    }
  };

  return (
    <aside className="w-80 border-r border-white/10 bg-slate-950/80 backdrop-blur-xl p-5 flex flex-col gap-6 overflow-y-auto h-screen sticky top-0">
      {/* Platform Branding */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-sky-400 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/20">
          ⚡
        </div>
        <div>
          <h2 className="font-extrabold text-sm tracking-tight text-white">Enterprise RAG</h2>
          <p className="text-xs text-slate-400">Document Intelligence</p>
        </div>
      </div>

      {/* SECTION 1: LLM Provider Configuration */}
      <div className="glass-card p-4 flex flex-col gap-3">
        <div className="flex items-center gap-2 text-xs font-bold text-indigo-400 uppercase tracking-wider">
          <Bot className="w-4 h-4" />
          <span>LLM Provider</span>
        </div>

        <select
          value={selectedProvider}
          onChange={(e) => {
            setSelectedProvider(e.target.value);
            if (e.target.value === "OpenAI") setSelectedModel(customOpenaiModel.trim() || "gpt-4o-mini");
            else if (e.target.value === "Groq") setSelectedModel(customGroqModel.trim() || "llama-3.3-70b-versatile");
            else if (e.target.value === "Local") setSelectedModel("local-grounded-context");
          }}
          className="glass-input p-2 text-sm w-full bg-slate-900"
        >
          <option value="Groq">Groq (Llama 3.3 / Fast)</option>
          <option value="OpenAI">OpenAI (GPT-4o / Mini)</option>
          <option value="Custom">Custom / OpenRouter / Ollama</option>
          <option value="Local">Offline Local Extraction</option>
        </select>

        {/* OpenAI Options */}
        {selectedProvider === "OpenAI" && (
          <div className="flex flex-col gap-2 mt-1">
            <select
              value={
                [
                  "gpt-4o-mini",
                  "gpt-4o",
                  "o3-mini",
                  "o1-mini",
                  "o1-preview",
                  "gpt-4-turbo",
                  "gpt-3.5-turbo",
                ].includes(selectedModel)
                  ? selectedModel
                  : "custom"
              }
              onChange={(e) => {
                if (e.target.value !== "custom") {
                  setSelectedModel(e.target.value);
                  setCustomOpenaiModel("");
                } else {
                  setSelectedModel(customOpenaiModel.trim() || "gpt-4o-mini");
                }
              }}
              className="glass-input p-2 text-xs w-full bg-slate-900"
            >
              <option value="gpt-4o-mini">gpt-4o-mini (Recommended)</option>
              <option value="gpt-4o">gpt-4o (High Accuracy)</option>
              <option value="o3-mini">o3-mini (Reasoning)</option>
              <option value="o1-mini">o1-mini (Reasoning)</option>
              <option value="gpt-4-turbo">gpt-4-turbo</option>
              <option value="gpt-3.5-turbo">gpt-3.5-turbo</option>
              <option value="custom">✍️ Custom Model (Enter Name Below)</option>
            </select>
            <input
              type="text"
              placeholder="✍️ Custom OpenAI Model (e.g. o1, gpt-4-turbo)"
              value={customOpenaiModel}
              onChange={(e) => {
                setCustomOpenaiModel(e.target.value);
                if (e.target.value.trim()) {
                  setSelectedModel(e.target.value.trim());
                }
              }}
              className="glass-input p-2 text-xs w-full"
            />
            <input
              type="password"
              placeholder="OpenAI API Key (sk-...)"
              value={openaiKey}
              onChange={(e) => setOpenaiKey(e.target.value)}
              className="glass-input p-2 text-xs w-full"
            />
            <div className="flex gap-2">
              <button
                onClick={() => handleSaveKey("openai")}
                className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold py-1.5 px-3 rounded-lg flex-1 transition"
              >
                Save Key
              </button>
              <button
                onClick={() => handleClearKey("openai")}
                className="bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs py-1.5 px-3 rounded-lg transition"
              >
                Clear
              </button>
            </div>
          </div>
        )}

        {/* Groq Options */}
        {selectedProvider === "Groq" && (
          <div className="flex flex-col gap-2 mt-1">
            <select
              value={
                [
                  "llama-3.3-70b-versatile",
                  "openai/gpt-oss-120b",
                  "openai/gpt-oss-20b",
                  "qwen/qwen3.6-27b",
                  "deepseek-r1-distill-llama-70b",
                  "llama-3.1-8b-instant",
                  "mixtral-8x7b-32768",
                  "gemma2-9b-it",
                ].includes(selectedModel)
                  ? selectedModel
                  : "custom"
              }
              onChange={(e) => {
                if (e.target.value !== "custom") {
                  setSelectedModel(e.target.value);
                  setCustomGroqModel("");
                } else {
                  setSelectedModel(customGroqModel.trim() || "llama-3.3-70b-versatile");
                }
              }}
              className="glass-input p-2 text-xs w-full bg-slate-900"
            >
              <option value="llama-3.3-70b-versatile">llama-3.3-70b-versatile (Recommended)</option>
              <option value="openai/gpt-oss-120b">openai/gpt-oss-120b (High Quality)</option>
              <option value="openai/gpt-oss-20b">openai/gpt-oss-20b</option>
              <option value="qwen/qwen3.6-27b">qwen/qwen3.6-27b</option>
              <option value="deepseek-r1-distill-llama-70b">deepseek-r1-distill-llama-70b (Reasoning)</option>
              <option value="llama-3.1-8b-instant">llama-3.1-8b-instant (Fastest)</option>
              <option value="mixtral-8x7b-32768">mixtral-8x7b-32768</option>
              <option value="gemma2-9b-it">gemma2-9b-it</option>
              <option value="custom">✍️ Custom Groq Model (Enter Below)</option>
            </select>
            <input
              type="text"
              placeholder="✍️ Custom Groq Model Name (Optional Override)"
              value={customGroqModel}
              onChange={(e) => {
                setCustomGroqModel(e.target.value);
                if (e.target.value.trim()) {
                  setSelectedModel(e.target.value.trim());
                }
              }}
              className="glass-input p-2 text-xs w-full"
            />
            <input
              type="password"
              placeholder="Groq API Key (gsk_...)"
              value={groqKey}
              onChange={(e) => setGroqKey(e.target.value)}
              className="glass-input p-2 text-xs w-full"
            />
            <div className="flex gap-2">
              <button
                onClick={() => handleSaveKey("groq")}
                className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold py-1.5 px-3 rounded-lg flex-1 transition"
              >
                Save Key
              </button>
              <button
                onClick={() => handleClearKey("groq")}
                className="bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs py-1.5 px-3 rounded-lg transition"
              >
                Clear
              </button>
            </div>
          </div>
        )}

        {/* Custom Provider Options */}
        {selectedProvider === "Custom" && (
          <div className="flex flex-col gap-2 mt-1">
            <input
              type="text"
              placeholder="Base URL (e.g. http://localhost:11434/v1)"
              value={customUrl}
              onChange={(e) => setCustomUrl(e.target.value)}
              className="glass-input p-2 text-xs w-full"
            />
            <input
              type="password"
              placeholder="API Key (or 'ollama')"
              value={customKey}
              onChange={(e) => setCustomKey(e.target.value)}
              className="glass-input p-2 text-xs w-full"
            />
            <input
              type="text"
              placeholder="Model Name (e.g. llama3)"
              value={customModel}
              onChange={(e) => {
                setCustomModel(e.target.value);
                setSelectedModel(e.target.value);
              }}
              className="glass-input p-2 text-xs w-full"
            />
            <div className="flex gap-2">
              <button
                onClick={() => handleSaveKey("custom")}
                className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold py-1.5 px-3 rounded-lg flex-1 transition"
              >
                Save Provider
              </button>
              <button
                onClick={() => handleClearKey("custom")}
                className="bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs py-1.5 px-3 rounded-lg transition"
              >
                Clear
              </button>
            </div>
          </div>
        )}

        {selectedProvider === "Local" && (
          <div className="text-xs text-amber-300 bg-amber-950/40 p-2 rounded-lg border border-amber-500/20">
            Offline sentence-level extraction engine (Requires zero API keys).
          </div>
        )}
      </div>

      {/* SECTION 2: Document Ingestion */}
      <div className="glass-card p-4 flex flex-col gap-3">
        <div className="flex items-center gap-2 text-xs font-bold text-sky-400 uppercase tracking-wider">
          <Upload className="w-4 h-4" />
          <span>Upload Documents</span>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.txt,.md"
          onChange={handleFileChange}
          className="hidden"
          id="file-upload-input"
        />
        <label
          htmlFor="file-upload-input"
          className="border-2 border-dashed border-slate-700 hover:border-indigo-500/50 rounded-xl p-4 flex flex-col items-center justify-center cursor-pointer transition text-center bg-slate-900/50"
        >
          <FileText className="w-6 h-6 text-slate-400 mb-1" />
          <span className="text-xs font-medium text-slate-300">
            {filesToUpload.length > 0
              ? `${filesToUpload.length} file(s) selected`
              : "Click to select PDF, DOCX, TXT, MD"}
          </span>
        </label>

        {filesToUpload.length > 0 && (
          <button
            onClick={handleIngest}
            disabled={isUploading}
            className="w-full bg-gradient-to-r from-indigo-600 to-sky-500 hover:from-indigo-500 hover:to-sky-400 text-white text-xs font-bold py-2.5 px-4 rounded-xl shadow-lg shadow-indigo-500/20 transition disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {isUploading ? (
              <span>Indexing...</span>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Ingest & Index Files</span>
              </>
            )}
          </button>
        )}

        {uploadStatus && (
          <div className="text-xs p-2 rounded-lg bg-slate-900 border border-white/10 text-slate-200">
            {uploadStatus}
          </div>
        )}
      </div>

      {/* SECTION 3: Search Strategy & Filters */}
      <div className="glass-card p-4 flex flex-col gap-3">
        <div className="flex items-center gap-2 text-xs font-bold text-indigo-400 uppercase tracking-wider">
          <Sliders className="w-4 h-4" />
          <span>Search Strategy</span>
        </div>

        <div className="flex flex-col gap-1.5 text-xs">
          {[
            { id: "cross-encoder", label: "🎯 2-Stage Cross-Encoder" },
            { id: "hybrid", label: "🔍 Hybrid (Vector + BM25)" },
            { id: "vector", label: "⚡ Dense Vector Search" },
          ].map((mode) => (
            <label
              key={mode.id}
              className={`flex items-center gap-2 p-2 rounded-lg cursor-pointer transition ${
                searchStrategy === mode.id
                  ? "bg-indigo-600/20 text-indigo-300 border border-indigo-500/30"
                  : "text-slate-400 hover:bg-slate-900"
              }`}
            >
              <input
                type="radio"
                name="search_mode"
                checked={searchStrategy === mode.id}
                onChange={() => setSearchStrategy(mode.id)}
                className="hidden"
              />
              <span>{mode.label}</span>
            </label>
          ))}
        </div>

        <div className="pt-2 border-t border-white/5 flex flex-col gap-2">
          <div className="flex justify-between text-xs text-slate-400">
            <span>Top-K Chunks</span>
            <span className="text-indigo-400 font-bold">{topK}</span>
          </div>
          <input
            type="range"
            min="1"
            max="10"
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
            className="w-full accent-indigo-500"
          />

          <div className="flex justify-between text-xs text-slate-400 mt-1">
            <span>Min Similarity</span>
            <span className="text-indigo-400 font-bold">{similarityThreshold.toFixed(2)}</span>
          </div>
          <input
            type="range"
            min="0.0"
            max="1.0"
            step="0.05"
            value={similarityThreshold}
            onChange={(e) => setSimilarityThreshold(Number(e.target.value))}
            className="w-full accent-indigo-500"
          />
        </div>
      </div>

      {/* SECTION 4: External Integrations */}
      <div className="glass-card p-4 flex flex-col gap-2.5">
        <div className="flex items-center justify-between text-xs font-bold text-slate-400 uppercase tracking-wider">
          <div className="flex items-center gap-1.5">
            <Server className="w-4 h-4 text-indigo-400" />
            <span>ARTSA & API Hub</span>
          </div>
          <span className="text-emerald-400 text-[10px] bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20 font-semibold">Active</span>
        </div>
        <p className="text-[11px] text-slate-400">
          Configure ARTSA API endpoints, diagnostics, and Webhooks.
        </p>
        {onNavigateSettings && (
          <button
            onClick={onNavigateSettings}
            className="w-full mt-1 bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-200 border border-indigo-500/40 text-xs py-1.5 px-3 rounded-lg transition flex items-center justify-center gap-1.5 cursor-pointer font-semibold"
          >
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>Open Settings Hub</span>
          </button>
        )}
      </div>

      {/* SECTION 5: Database Management */}
      <div className="glass-card p-4 flex flex-col gap-2.5">
        <div className="flex items-center justify-between text-xs font-bold text-slate-400 uppercase tracking-wider">
          <div className="flex items-center gap-1.5">
            <Database className="w-4 h-4 text-emerald-400" />
            <span>ChromaDB Store</span>
          </div>
          <span className="text-emerald-400">Online</span>
        </div>

        <div className="text-xs text-slate-400 space-y-1">
          <div className="flex justify-between">
            <span>Indexed Chunks:</span>
            <span className="text-slate-200 font-bold">{stats?.total_chunks ?? 0}</span>
          </div>
          <div className="flex justify-between">
            <span>Unique Docs:</span>
            <span className="text-slate-200 font-bold">{stats?.unique_documents ?? 0}</span>
          </div>
        </div>

        <button
          onClick={handleResetDb}
          className="mt-1 flex items-center justify-center gap-2 bg-rose-950/40 hover:bg-rose-900/60 text-rose-300 border border-rose-500/20 text-xs py-2 px-3 rounded-lg transition"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span>Reset Vector Database</span>
        </button>
      </div>
    </aside>
  );
};
