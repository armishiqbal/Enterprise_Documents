"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Send,
  Trash2,
  Download,
  Sparkles,
  ChevronDown,
  ChevronUp,
  FileText,
  CheckCircle,
  HelpCircle,
  ExternalLink,
} from "lucide-react";
import { MarkdownRenderer } from "./MarkdownRenderer";
import { queryRAG, CitationItem, GroundingInfo } from "@/lib/api";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: CitationItem[];
  grounding?: GroundingInfo | null;
  timestamp: string;
}

interface ChatPanelProps {
  topK: number;
  similarityThreshold: number;
  selectedProvider: string;
  selectedModel: string;
  searchStrategy: string;
  onQueryCompleted: (promptTokens: number, completionTokens: number) => void;
}

const DEFAULT_SUGGESTIONS = [
  "What are the primary key points in the uploaded files?",
  "Can you summarize the core policies and compliance guidelines?",
  "What security measures or data privacy rules are specified?",
  "What financial numbers or revenue metrics are reported?",
];

export const ChatPanel: React.FC<ChatPanelProps> = ({
  topK,
  similarityThreshold,
  selectedProvider,
  selectedModel,
  searchStrategy,
  onQueryCompleted,
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome_1",
      role: "assistant",
      content:
        "Welcome to the **Enterprise Document Intelligence Platform**. Upload your files in the sidebar to perform grounded search, inspect page citations, or ask questions.",
      citations: [],
      grounding: null,
      timestamp: "Welcome",
    },
  ]);

  const [inputQuery, setInputQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [expandedCitations, setExpandedCitations] = useState<Record<string, boolean>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const toggleCitation = (msgId: string) => {
    setExpandedCitations((prev) => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  const handleSendMessage = async (queryToSend?: string) => {
    const text = queryToSend || inputQuery.trim();
    if (!text || isLoading) return;

    const userMsg: Message = {
      id: `user_${Date.now()}`,
      role: "user",
      content: text,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!queryToSend) setInputQuery("");
    setIsLoading(true);

    try {
      let apiKey = "";
      let baseUrl = "";
      if (typeof window !== "undefined" && selectedProvider !== "Local") {
        if (selectedProvider === "OpenAI") apiKey = localStorage.getItem("openai_api_key") || "";
        else if (selectedProvider === "Groq") apiKey = localStorage.getItem("groq_api_key") || "";
        else if (selectedProvider === "Custom") {
          apiKey = localStorage.getItem("custom_api_key") || "";
          baseUrl = localStorage.getItem("custom_base_url") || "";
        }
      }

      const response = await queryRAG(
        text,
        topK,
        similarityThreshold,
        selectedProvider,
        selectedModel,
        apiKey,
        baseUrl,
        searchStrategy
      );

      // Estimate tokens
      const pTokens = Math.max(1, Math.floor((text.length + 500) / 4));
      const cTokens = Math.max(1, Math.floor(response.answer.length / 4));
      onQueryCompleted(pTokens, cTokens);

      const assistantMsg: Message = {
        id: `asst_${Date.now()}`,
        role: "assistant",
        content: response.answer,
        citations: response.citations || [],
        grounding: response.grounding || null,
        timestamp: new Date().toLocaleTimeString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: Message = {
        id: `err_${Date.now()}`,
        role: "assistant",
        content: `⚠️ Error generating response: ${err.message}. Please verify the backend is running on port 8080 and try again.`,
        citations: [],
        timestamp: new Date().toLocaleTimeString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: `welcome_${Date.now()}`,
        role: "assistant",
        content: "Conversation cleared. Ready for your questions!",
        citations: [],
        grounding: null,
        timestamp: new Date().toLocaleTimeString(),
      },
    ]);
  };

  const handleExportChat = () => {
    let md = "# Enterprise Document Intelligence - Chat Export\n\n";
    for (const m of messages) {
      md += `### ${m.role.toUpperCase()} (${m.timestamp})\n${m.content}\n\n`;
      if (m.citations && m.citations.length > 0) {
        md += "**Citations:**\n";
        for (const c of m.citations) {
          md += `- [${c.filename}] (Page ${c.page_number ?? "N/A"}) - Match: ${c.score_percent}\n`;
        }
        md += "\n";
      }
    }

    const blob = new Blob([md], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `chat_export_${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-180px)] justify-between">
      {/* 1. Suggested Questions & Action Bar */}
      <div className="flex flex-col gap-3 pb-3 border-b border-white/5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-400">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>Suggested Prompts:</span>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleClearChat}
              className="flex items-center gap-1 text-xs text-slate-400 hover:text-rose-400 transition"
              title="Clear chat history"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear</span>
            </button>
            <button
              onClick={handleExportChat}
              className="flex items-center gap-1 text-xs text-slate-400 hover:text-sky-400 transition"
              title="Export chat as Markdown"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {DEFAULT_SUGGESTIONS.map((sq, i) => (
            <button
              key={i}
              onClick={() => handleSendMessage(sq)}
              className="glass-card hover:border-indigo-500/40 p-2 text-left text-xs text-slate-300 hover:text-white transition truncate rounded-lg"
            >
              ❓ {sq}
            </button>
          ))}
        </div>
      </div>

      {/* 2. Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto py-4 space-y-4 pr-2">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex flex-col ${
              m.role === "user" ? "items-end" : "items-start"
            }`}
          >
            <div
              className={`max-w-[85%] rounded-2xl p-4 space-y-2 ${
                m.role === "user"
                  ? "bg-gradient-to-r from-indigo-600 to-indigo-700 text-white shadow-lg shadow-indigo-600/20"
                  : "glass-card border border-white/10 text-slate-200"
              }`}
            >
              {/* Groundedness Badge */}
              {m.grounding && (
                <div className="pb-1">
                  <span
                    className={
                      m.grounding.groundedness_score >= 0.5
                        ? "badge-grounded-high"
                        : m.grounding.groundedness_score >= 0.3
                        ? "badge-grounded-mod"
                        : "badge-grounded-low"
                    }
                  >
                    <CheckCircle className="w-3.5 h-3.5" />
                    Groundedness: {m.grounding.score_percent} (
                    {m.grounding.confidence_label})
                  </span>
                </div>
              )}

              {/* Message Content */}
              <div className="text-sm leading-relaxed">
                <MarkdownRenderer content={m.content} />
              </div>

              {/* Citations Accordion */}
              {m.citations && m.citations.length > 0 && (
                <div className="pt-2 border-t border-white/10">
                  <button
                    onClick={() => toggleCitation(m.id)}
                    className="flex items-center gap-1.5 text-xs font-semibold text-sky-400 hover:text-sky-300 transition"
                  >
                    <FileText className="w-3.5 h-3.5" />
                    <span>
                      {m.citations.length} Source Citation(s) Available
                    </span>
                    {expandedCitations[m.id] ? (
                      <ChevronUp className="w-3.5 h-3.5" />
                    ) : (
                      <ChevronDown className="w-3.5 h-3.5" />
                    )}
                  </button>

                  {expandedCitations[m.id] && (
                    <div className="mt-2 space-y-2 pl-2 border-l-2 border-sky-500/30">
                      {m.citations.map((cite, idx) => (
                        <div
                          key={idx}
                          className="text-xs bg-slate-900/80 p-2.5 rounded-lg border border-white/5 space-y-1"
                        >
                          <div className="flex items-center justify-between text-slate-300 font-mono">
                            <span className="font-bold text-sky-300">
                              📄 {cite.filename}
                            </span>
                            <span className="text-slate-400">
                              {cite.page_number
                                ? `Page ${cite.page_number}`
                                : "Chunk"}{" "}
                              | Match:{" "}
                              <strong className="text-emerald-400">
                                {cite.score_percent}
                              </strong>
                            </span>
                          </div>
                          <p className="text-slate-400 italic text-[11px] leading-snug">
                            "{cite.snippet}"
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
            <span suppressHydrationWarning className="text-[10px] text-slate-500 mt-1 px-1">
              {m.timestamp}
            </span>
          </div>
        ))}

        {isLoading && (
          <div className="flex items-start">
            <div className="glass-card p-4 rounded-2xl flex items-center gap-3 text-slate-400 text-xs">
              <div className="w-2 h-2 rounded-full bg-indigo-500 animate-ping" />
              <span>Retrieving knowledge and generating grounded answer...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 3. Input Form (Anchored) */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (inputQuery.trim() && !isLoading) {
            handleSendMessage();
          }
        }}
        className="pt-3 flex gap-2"
      >
        <input
          type="text"
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              if (inputQuery.trim() && !isLoading) {
                handleSendMessage();
              }
            }
          }}
          placeholder="Ask a question about your uploaded enterprise documents..."
          className="glass-input flex-1 px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500"
          disabled={isLoading}
          autoFocus
        />
        <button
          type="submit"
          disabled={isLoading || !inputQuery.trim()}
          className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white px-5 py-3 rounded-xl font-bold flex items-center gap-2 shadow-lg shadow-indigo-600/20 transition cursor-pointer disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <Send className="w-4 h-4" />
          )}
          <span>{isLoading ? "Thinking..." : "Ask"}</span>
        </button>
      </form>
    </div>
  );
};
