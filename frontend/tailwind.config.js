/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#07090E",
        surface: "rgba(15, 23, 42, 0.65)",
        surfaceHover: "rgba(30, 41, 59, 0.75)",
        accent: "#6366F1",
        accentCyan: "#38BDF8",
        accentEmerald: "#10B981",
        accentAmber: "#F59E0B",
        accentRose: "#F43F5E",
        textPrimary: "#F8FAFC",
        textSecondary: "#94A3B8",
        borderGlass: "rgba(255, 255, 255, 0.08)",
      },
      fontFamily: {
        sans: ["var(--font-jakarta)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      backgroundImage: {
        "radial-gradient": "radial-gradient(at 10% 10%, rgba(99, 102, 241, 0.08) 0px, transparent 50%), radial-gradient(at 90% 90%, rgba(14, 165, 233, 0.06) 0px, transparent 50%)",
      },
    },
  },
  plugins: [],
};
