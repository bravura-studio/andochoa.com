/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./content/**/*.{md,mdx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "rgb(var(--background) / <alpha-value>)",
        foreground: "rgb(var(--foreground) / <alpha-value>)",
        border: "rgb(var(--border) / <alpha-value>)",
        surface: "rgb(var(--surface) / <alpha-value>)",
        "surface-elevated": "rgb(var(--surface-elevated) / <alpha-value>)",
        "text-dim": "rgb(var(--text-dim) / <alpha-value>)",
        "text-muted": "rgb(var(--text-muted) / <alpha-value>)",
        terminal: "rgb(var(--terminal-green) / <alpha-value>)",
      },
      fontFamily: {
        mono: ["var(--font-geist-mono)"],
      },
      boxShadow: {
        terminal: "0 20px 60px rgba(0, 0, 0, 0.35)",
      },
      animation: {
        blink: "blink 1.2s step-end infinite",
        "fade-up": "fade-up 0.7s ease-out both",
      },
      keyframes: {
        blink: {
          "0%, 45%": { opacity: "1" },
          "45.01%, 100%": { opacity: "0" },
        },
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(18px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      borderRadius: {
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
      },
    },
  },
  plugins: [],
};
