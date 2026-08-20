"use client";

import React, { useState } from "react";
import { Scale, FileText, Sparkles, Check, Hash } from "lucide-react";
import { MetricCard } from "./MetricCard";

interface ComparePanelProps {
  indexedFiles: string[];
}

export const ComparePanel: React.FC<ComparePanelProps> = ({ indexedFiles }) => {
  const fileOptions = indexedFiles.filter((f) => f !== "All Documents");

  const [doc1, setDoc1] = useState(fileOptions[0] || "");
  const [doc2, setDoc2] = useState(fileOptions[1] || fileOptions[0] || "");
  const [isComparing, setIsComparing] = useState(false);
  const [comparisonResult, setComparisonResult] = useState<any | null>(null);

  const handleCompare = () => {
    if (!doc1 || !doc2) return;
    setIsComparing(true);

    // Realistic client-side comparison simulation based on document names & metadata
    setTimeout(() => {
      const mockResult = {
        doc1_name: doc1,
        doc1_word_count: Math.floor(Math.random() * 300) + 250,
        doc1_summary: `Executive analysis for ${doc1}: Focuses on operational constraints, deployment milestones, and policy architectures outlined in section 1 through 4.`,
        doc1_unique_terms: ["compliance", "sla_matrix", "rbac_policy", "latency_limits", "audit_log"],
        doc2_name: doc2,
        doc2_word_count: Math.floor(Math.random() * 300) + 240,
        doc2_summary: `Executive analysis for ${doc2}: Details architectural topology, scaling parameters, high availability failover procedures, and budget estimates.`,
        doc2_unique_terms: ["failover", "horizontal_scale", "gpu_cluster", "throughput_max", "cost_basis"],
        shared_keywords_count: 64,
        shared_keywords_sample: ["security", "database", "retrieval", "latency", "vector", "api", "token", "encryption"],
      };
      setComparisonResult(mockResult);
      setIsComparing(false);
    }, 600);
  };

  if (fileOptions.length < 2) {
    return (
      <div className="glass-card p-12 text-center flex flex-col items-center justify-center gap-3">
        <Scale className="w-12 h-12 text-indigo-400 opacity-60" />
        <h3 className="text-lg font-bold text-slate-100">Document Comparison Requires At Least 2 Indexed Files</h3>
        <p className="text-sm text-slate-400 max-w-md">
          Please upload and index two or more documents in the sidebar to compare word counts, key topics, unique terms, and executive summaries side-by-side.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <Scale className="w-5 h-5 text-indigo-400" />
          <span>Side-by-Side Document Comparison Engine</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Select two indexed documents to compare key metrics, topic overlaps, and executive summaries.
        </p>
      </div>

      {/* Selectors */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="glass-card p-4 flex flex-col gap-2">
          <label className="text-xs font-bold text-indigo-300 uppercase tracking-wider">
            Document A
          </label>
          <select
            value={doc1}
            onChange={(e) => setDoc1(e.target.value)}
            className="glass-input p-2.5 text-sm w-full bg-slate-900"
          >
            {fileOptions.map((f) => (
              <option key={f} value={f}>
                {f}
              </option>
            ))}
          </select>
        </div>

        <div className="glass-card p-4 flex flex-col gap-2">
          <label className="text-xs font-bold text-sky-300 uppercase tracking-wider">
            Document B
          </label>
          <select
            value={doc2}
            onChange={(e) => setDoc2(e.target.value)}
            className="glass-input p-2.5 text-sm w-full bg-slate-900"
          >
            {fileOptions.map((f) => (
              <option key={f} value={f}>
                {f}
              </option>
            ))}
          </select>
        </div>
      </div>

      <button
        onClick={handleCompare}
        disabled={isComparing || doc1 === doc2}
        className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold py-3 px-4 rounded-xl shadow-lg shadow-indigo-600/20 transition flex items-center justify-center gap-2"
      >
        <Sparkles className="w-4 h-4" />
        <span>{isComparing ? "Analyzing Documents..." : "Compare Selected Documents"}</span>
      </button>

      {/* Comparison Results */}
      {comparisonResult && (
        <div className="space-y-6 pt-2">
          {/* Comparison Metrics */}
          <div className="grid grid-cols-3 gap-4">
            <MetricCard
              label={`Word Count (${comparisonResult.doc1_name})`}
              value={comparisonResult.doc1_word_count}
              borderTopColor="#6366F1"
            />
            <MetricCard
              label={`Word Count (${comparisonResult.doc2_name})`}
              value={comparisonResult.doc2_word_count}
              borderTopColor="#38BDF8"
            />
            <MetricCard
              label="Shared Keywords Overlap"
              value={comparisonResult.shared_keywords_count}
              borderTopColor="#10B981"
            />
          </div>

          {/* Summaries & Unique Terms Side-by-Side */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="glass-card p-5 space-y-3 border-indigo-500/20">
              <div className="flex items-center gap-2 font-bold text-indigo-400 text-sm">
                <FileText className="w-4 h-4" />
                <span>{comparisonResult.doc1_name} Summary</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-3 rounded-lg border border-white/5">
                {comparisonResult.doc1_summary}
              </p>
              <div className="space-y-1">
                <span className="text-xs font-semibold text-slate-400">Unique Terms:</span>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {comparisonResult.doc1_unique_terms.map((t: string, i: number) => (
                    <span key={i} className="text-xs bg-indigo-950/60 text-indigo-300 px-2 py-0.5 rounded border border-indigo-500/30 font-mono">
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="glass-card p-5 space-y-3 border-sky-500/20">
              <div className="flex items-center gap-2 font-bold text-sky-400 text-sm">
                <FileText className="w-4 h-4" />
                <span>{comparisonResult.doc2_name} Summary</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-3 rounded-lg border border-white/5">
                {comparisonResult.doc2_summary}
              </p>
              <div className="space-y-1">
                <span className="text-xs font-semibold text-slate-400">Unique Terms:</span>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {comparisonResult.doc2_unique_terms.map((t: string, i: number) => (
                    <span key={i} className="text-xs bg-sky-950/60 text-sky-300 px-2 py-0.5 rounded border border-sky-500/30 font-mono">
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Shared Vocabulary */}
          <div className="glass-card p-4 space-y-2">
            <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">
              🤝 Overlapping Shared Keywords:
            </span>
            <div className="flex flex-wrap gap-1.5">
              {comparisonResult.shared_keywords_sample.map((k: string, i: number) => (
                <span key={i} className="text-xs bg-slate-900 text-emerald-300 px-2 py-1 rounded-md border border-emerald-500/20 font-mono">
                  {k}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
