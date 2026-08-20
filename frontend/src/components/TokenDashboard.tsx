"use client";

import React from "react";
import { DollarSign, Activity, Cpu, Layers, RotateCcw } from "lucide-react";
import { MetricCard } from "./MetricCard";

interface TokenDashboardProps {
  totalQueries: number;
  totalPromptTokens: number;
  totalCompletionTokens: number;
  totalCostUsd: number;
  onResetUsage: () => void;
}

export const TokenDashboard: React.FC<TokenDashboardProps> = ({
  totalQueries,
  totalPromptTokens,
  totalCompletionTokens,
  totalCostUsd,
  onResetUsage,
}) => {
  const totalTokens = totalPromptTokens + totalCompletionTokens;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Activity className="w-5 h-5 text-indigo-400" />
            <span>Token Usage & API Cost Analytics</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Live session tracking of query volume, prompt/completion tokens, and estimated expenses.
          </p>
        </div>
        <button
          onClick={onResetUsage}
          className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 bg-slate-900/80 border border-white/10 px-3 py-1.5 rounded-lg transition"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset Session Counter</span>
        </button>
      </div>

      {/* Primary Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="Total Queries"
          value={totalQueries}
          icon={<Activity className="w-4 h-4" />}
          borderTopColor="#6366F1"
        />
        <MetricCard
          label="Prompt Tokens"
          value={totalPromptTokens.toLocaleString()}
          icon={<Layers className="w-4 h-4" />}
          borderTopColor="#38BDF8"
        />
        <MetricCard
          label="Completion Tokens"
          value={totalCompletionTokens.toLocaleString()}
          icon={<Cpu className="w-4 h-4" />}
          borderTopColor="#10B981"
        />
        <MetricCard
          label="Est. API Cost (USD)"
          value={`$${totalCostUsd.toFixed(5)}`}
          icon={<DollarSign className="w-4 h-4" />}
          borderTopColor="#F59E0B"
        />
      </div>

      {/* Pricing Model Reference */}
      <div className="glass-card p-5 space-y-3 border-indigo-500/20">
        <h3 className="text-sm font-bold text-indigo-400 flex items-center gap-2">
          <span>💡 Model Pricing Reference Table</span>
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="border-b border-white/10 text-slate-400 uppercase tracking-wider">
              <tr>
                <th className="py-2 px-3">Model</th>
                <th className="py-2 px-3">Input Price / 1M Tokens</th>
                <th className="py-2 px-3">Output Price / 1M Tokens</th>
                <th className="py-2 px-3">Category</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 font-mono">
              <tr className="hover:bg-slate-900/40">
                <td className="py-2.5 px-3 font-semibold text-slate-100">gpt-4o-mini</td>
                <td className="py-2.5 px-3 text-emerald-400">$0.15</td>
                <td className="py-2.5 px-3 text-emerald-400">$0.60</td>
                <td className="py-2.5 px-3 text-slate-400">OpenAI Fast</td>
              </tr>
              <tr className="hover:bg-slate-900/40">
                <td className="py-2.5 px-3 font-semibold text-slate-100">gpt-4o</td>
                <td className="py-2.5 px-3 text-amber-400">$2.50</td>
                <td className="py-2.5 px-3 text-amber-400">$10.00</td>
                <td className="py-2.5 px-3 text-slate-400">OpenAI Flagship</td>
              </tr>
              <tr className="hover:bg-slate-900/40">
                <td className="py-2.5 px-3 font-semibold text-slate-100">llama-3.3-70b-versatile</td>
                <td className="py-2.5 px-3 text-sky-400">$0.59</td>
                <td className="py-2.5 px-3 text-sky-400">$0.79</td>
                <td className="py-2.5 px-3 text-slate-400">Groq High Speed</td>
              </tr>
              <tr className="hover:bg-slate-900/40">
                <td className="py-2.5 px-3 font-semibold text-slate-100">SentenceTransformers</td>
                <td className="py-2.5 px-3 text-emerald-300">$0.00 (Free)</td>
                <td className="py-2.5 px-3 text-emerald-300">$0.00 (Free)</td>
                <td className="py-2.5 px-3 text-slate-400">Local Vector Embeddings</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
