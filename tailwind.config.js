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
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        border: "hsl(var(--border))",
        muted: "hsl(var(--muted))",
        "muted-foreground": "hsl(var(--muted-foreground))",
        primary: "hsl(var(--primary))",
        "primary-foreground": "hsl(var(--primary-foreground))",
        accent: "hsl(var(--accent))",
        "accent-foreground": "hsl(var(--accent-foreground))",
        card: "hsl(var(--card))",
        "card-foreground": "hsl(var(--card-foreground))",
      },
      fontFamily: {
        mono: ["var(--font-jetbrains-mono)"],
      },
      boxShadow: {
        terminal: "0 0 0 1px rgba(0, 255, 65, 0.2), 0 24px 60px rgba(0, 0, 0, 0.45)",
      },
      backgroundImage: {
        grid: "linear-gradient(rgba(0,255,65,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(0,255,65,0.08) 1px, transparent 1px)",
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
    },
  },
  plugins: [],
};
