import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          primary:   "#7C3AED", // violet-700
          secondary: "#5B21B6", // violet-800
          accent:    "#F59E0B", // amber-500
          muted:     "#EDE9FE", // violet-100
        },
        plan: {
          free:       "#6B7280", // gray-500
          pro:        "#7C3AED", // violet-700
          enterprise: "#F59E0B", // amber-500
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      animation: {
        "pulse-slow":    "pulse 3s cubic-bezier(0.4,0,0.6,1) infinite",
        "fade-in":       "fadeIn 0.4s ease-in-out",
        "slide-up":      "slideUp 0.3s ease-out",
        "glow":          "glow 2s ease-in-out infinite alternate",
      },
      keyframes: {
        fadeIn: {
          "0%":   { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%":   { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        glow: {
          "0%":   { boxShadow: "0 0 5px #7C3AED33" },
          "100%": { boxShadow: "0 0 20px #7C3AED99" },
        },
      },
      boxShadow: {
        card:  "0 4px 24px -4px rgba(124,58,237,0.12)",
        glow:  "0 0 20px rgba(124,58,237,0.35)",
      },
      borderRadius: {
        xl2: "1rem",
        xl3: "1.5rem",
      },
    },
  },
  plugins: [],
};

export default config;
