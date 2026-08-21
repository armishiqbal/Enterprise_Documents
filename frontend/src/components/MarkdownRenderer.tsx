import React from "react";

interface MarkdownRendererProps {
  content: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  if (!content) return null;

  // Split lines
  const lines = content.split("\n");
  const elements: React.ReactNode[] = [];
  let inCodeBlock = false;
  let codeBlockContent: string[] = [];
  let codeBlockLang = "";

  lines.forEach((line, idx) => {
    // Code block toggle
    if (line.trim().startsWith("```")) {
      if (inCodeBlock) {
        elements.push(
          <pre
            key={`code-${idx}`}
            className="bg-slate-950 p-3 rounded-lg border border-white/10 text-xs font-mono overflow-x-auto my-2 text-indigo-300"
          >
            <code>{codeBlockContent.join("\n")}</code>
          </pre>
        );
        codeBlockContent = [];
        inCodeBlock = false;
      } else {
        inCodeBlock = true;
        codeBlockLang = line.trim().slice(3).trim();
      }
      return;
    }

    if (inCodeBlock) {
      codeBlockContent.push(line);
      return;
    }

    // Headings
    if (line.startsWith("### ")) {
      elements.push(
        <h4 key={`h3-${idx}`} className="text-sm font-bold text-sky-400 mt-2 mb-1">
          {renderInline(line.slice(4))}
        </h4>
      );
      return;
    }
    if (line.startsWith("## ")) {
      elements.push(
        <h3 key={`h2-${idx}`} className="text-base font-extrabold text-indigo-300 mt-3 mb-1.5">
          {renderInline(line.slice(3))}
        </h3>
      );
      return;
    }
    if (line.startsWith("# ")) {
      elements.push(
        <h2 key={`h1-${idx}`} className="text-lg font-extrabold text-white mt-3 mb-2">
          {renderInline(line.slice(2))}
        </h2>
      );
      return;
    }

    // Horizontal rule
    if (line.trim() === "---" || line.trim() === "***") {
      elements.push(<hr key={`hr-${idx}`} className="border-white/10 my-2" />);
      return;
    }

    // Bullet points
    if (
      line.trim().startsWith("• ") ||
      line.trim().startsWith("- ") ||
      line.trim().startsWith("* ")
    ) {
      const bulletText = line.trim().replace(/^[•\-\*]\s+/, "");
      elements.push(
        <div key={`bullet-${idx}`} className="flex items-start gap-2 my-1 pl-1 text-slate-200">
          <span className="text-indigo-400 font-bold">•</span>
          <span className="flex-1 leading-relaxed">{renderInline(bulletText)}</span>
        </div>
      );
      return;
    }

    // Empty line
    if (!line.trim()) {
      elements.push(<div key={`empty-${idx}`} className="h-1" />);
      return;
    }

    // Normal paragraph
    elements.push(
      <p key={`p-${idx}`} className="my-1 leading-relaxed text-slate-200">
        {renderInline(line)}
      </p>
    );
  });

  return <div className="space-y-0.5 text-sm">{elements}</div>;
};

// Helper for inline markdown parsing (**bold**, *italic*, `code`)
function renderInline(text: string): React.ReactNode {
  if (!text) return "";

  // Split by inline code, bold, italic
  const parts: React.ReactNode[] = [];
  const regex = /(\*\*.*?\*\*|\*.*?\*|`.*?`)/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }

    const token = match[0];
    if (token.startsWith("**") && token.endsWith("**")) {
      parts.push(
        <strong key={match.index} className="font-bold text-white">
          {token.slice(2, -2)}
        </strong>
      );
    } else if (token.startsWith("*") && token.endsWith("*")) {
      parts.push(
        <em key={match.index} className="italic text-slate-300">
          {token.slice(1, -1)}
        </em>
      );
    } else if (token.startsWith("`") && token.endsWith("`")) {
      parts.push(
        <code
          key={match.index}
          className="bg-slate-900 text-sky-300 px-1.5 py-0.5 rounded text-xs font-mono border border-white/10"
        >
          {token.slice(1, -1)}
        </code>
      );
    }
    lastIndex = regex.lastIndex;
  }

  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  return parts.length > 0 ? parts : text;
}
