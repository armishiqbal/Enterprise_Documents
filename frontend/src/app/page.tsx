"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  MessageSquare,
  Scale,
  Activity,
  FileText,
  Layers,
  DollarSign,
  Cpu,
  Sparkles,
} from "lucide-react";
import { Sidebar } from "@/components/Sidebar";
import { ChatPanel } from "@/components/ChatPanel";
import { ComparePanel } from "@/components/ComparePanel";
import { TokenDashboard } from "@/components/TokenDashboard";
import { SettingsPanel } from "@/components/SettingsPanel";
import { MetricCard } from "@/components/MetricCard";
import { fetchStats, StatsResponse } from "@/lib/api";

export default function Home() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [activeTab, setActiveTab] = useState<"chat" | "compare" | "tokens" | "settings">("chat");

  // RAG Configuration States
  const [selectedProvider, setSelectedProvider] = useState<string>("Groq");
  const [selectedModel, setSelectedModel] = useState<string>("llama-3.3-70b-versatile");
  const [topK, setTopK] = useState<number>(4);
  const [similarityThreshold, setSimilarityThreshold] = useState<number>(0.0);
  const [searchStrategy, setSearchStrategy] = useState<string>("cross-encoder");
  const [selectedDocFilter, setSelectedDocFilter] = useState<string>("All Documents");
  const [indexedFiles, setIndexedFiles] = useState<string[]>(["All Documents"]);

  // Token Tracking State
  const [totalQueries, setTotalQueries] = useState<number>(0);
  const [totalPromptTokens, setTotalPromptTokens] = useState<number>(0);
  const [totalCompletionTokens, setTotalCompletionTokens] = useState<number>(0);
  const [totalCostUsd, setTotalCostUsd] = useState<number>(0.0);

  const loadStats = useCallback(async () => {
    try {
      const data = await fetchStats();
      setStats(data);
      if (data.indexed_files && data.indexed_files.length > 0) {
        setIndexedFiles(["All Documents", ...data.indexed_files]);
      }
    } catch {
      setStats({
        collection_name: "document_chunks",
        total_chunks: 0,
        unique_documents: 0,
        persist_directory: "data/vectorstore",
        indexed_files: [],
      });
    }
  }, []);

  useEffect(() => {
    loadStats();
  }, [loadStats]);

  const handleQueryCompleted = (pTokens: number, cTokens: number) => {
    setTotalQueries((q) => q + 1);
    setTotalPromptTokens((pt) => pt + pTokens);
    setTotalCompletionTokens((ct) => ct + cTokens);

    const queryCost = (pTokens / 1_000_000) * 0.15 + (cTokens / 1_000_000) * 0.6;
    setTotalCostUsd((c) => c + queryCost);
  };

  const [initialChatQuery, setInitialChatQuery] = useState<string>("");

  const handleAskComparisonQuestion = (q: string) => {
    setInitialChatQuery(q);
    setActiveTab("chat");
  };

  const handleResetUsage = () => {
    setTotalQueries(0);
    setTotalPromptTokens(0);
    setTotalCompletionTokens(0);
    setTotalCostUsd(0.0);
  };

  return (
    <div className="flex min-h-screen bg-[#07090E]">
      {/* 1. Left Control Sidebar */}
      <Sidebar
        stats={stats}
        onStatsRefresh={loadStats}
        selectedProvider={selectedProvider}
        setSelectedProvider={setSelectedProvider}
        selectedModel={selectedModel}
        setSelectedModel={setSelectedModel}
        topK={topK}
        setTopK={setTopK}
        similarityThreshold={similarityThreshold}
        setSimilarityThreshold={setSimilarityThreshold}
        searchStrategy={searchStrategy}
        setSearchStrategy={setSearchStrategy}
        selectedDocFilter={selectedDocFilter}
        setSelectedDocFilter={setSelectedDocFilter}
        indexedFiles={indexedFiles}
      />

      {/* 2. Main Workspace Area */}
      <main className="flex-1 p-6 md:p-8 flex flex-col gap-6 overflow-y-auto max-w-7xl mx-auto">
        {/* Header Title */}
        <div className="flex items-center justify-between pb-2 border-b border-white/10">
          <div>
            <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
              Enterprise Document Intelligence
            </h1>
            <p className="text-xs md:text-sm text-slate-400 mt-0.5">
              Grounded Retrieval-Augmented Generation (RAG) with page citations and factual verification.
            </p>
          </div>
          <div className="hidden sm:flex items-center gap-2">
            <span className="text-xs bg-emerald-950/60 text-emerald-400 border border-emerald-500/30 px-2.5 py-1 rounded-full font-semibold flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Next.js + Webhook Active
            </span>
          </div>
        </div>

        {/* Top Summary Metrics Ribbon */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          <MetricCard
            label="Indexed Files"
            value={stats?.unique_documents ?? 0}
            icon={<FileText className="w-4 h-4" />}
            borderTopColor="#6366F1"
          />
          <MetricCard
            label="Indexed Chunks"
            value={stats?.total_chunks ?? 0}
            icon={<Layers className="w-4 h-4" />}
            borderTopColor="#38BDF8"
          />
          <MetricCard
            label="Session Tokens"
            value={(totalPromptTokens + totalCompletionTokens).toLocaleString()}
            icon={<Cpu className="w-4 h-4" />}
            borderTopColor="#10B981"
          />
          <MetricCard
            label="Est. API Cost"
            value={`$${totalCostUsd.toFixed(4)}`}
            icon={<DollarSign className="w-4 h-4" />}
            borderTopColor="#F59E0B"
          />
          <MetricCard
            label="Active Model"
            value={selectedModel}
            icon={<Sparkles className="w-4 h-4" />}
            borderTopColor="#A855F7"
          />
        </div>

        {/* Multi-Tab Navigation */}
        <div className="flex border-b border-white/10 gap-2">
          {[
            { id: "chat", label: "💬 Chat Assistant", icon: MessageSquare },
            { id: "compare", label: "⚖️ Document Comparison", icon: Scale },
            { id: "tokens", label: "📊 Token Analytics", icon: Activity },
            { id: "settings", label: "⚙️ System & ARTSA Settings", icon: Sparkles },
          ].map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-2.5 text-xs font-bold transition rounded-t-xl border-b-2 cursor-pointer ${
                  isActive
                    ? "bg-slate-900/80 text-indigo-400 border-indigo-500 shadow-sm"
                    : "text-slate-400 hover:text-slate-200 border-transparent hover:bg-slate-900/40"
                }`}
              >
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Content Panels */}
        <div className="flex-1">
          {activeTab === "chat" && (
            <ChatPanel
              topK={topK}
              similarityThreshold={similarityThreshold}
              selectedProvider={selectedProvider}
              selectedModel={selectedModel}
              searchStrategy={searchStrategy}
              onQueryCompleted={handleQueryCompleted}
              initialQuery={initialChatQuery}
            />
          )}

          {activeTab === "compare" && (
            <ComparePanel
              indexedFiles={indexedFiles}
              selectedProvider={selectedProvider}
              selectedModel={selectedModel}
              onAskQuestion={handleAskComparisonQuestion}
            />
          )}

          {activeTab === "tokens" && (
            <TokenDashboard
              totalQueries={totalQueries}
              totalPromptTokens={totalPromptTokens}
              totalCompletionTokens={totalCompletionTokens}
              totalCostUsd={totalCostUsd}
              onResetUsage={handleResetUsage}
            />
          )}

          {activeTab === "settings" && (
            <SettingsPanel />
          )}
        </div>
      </main>
    </div>
  );
}
