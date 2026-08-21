import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Enterprise Document Intelligence Platform",
  description: "AI-Powered RAG Platform for Document Search, Grounded QA, and Side-by-Side Comparison.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased text-slate-100 min-h-screen bg-[#07090E]">
        {children}
      </body>
    </html>
  );
}
