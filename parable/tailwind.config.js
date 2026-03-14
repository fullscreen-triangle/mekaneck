/** @type {import('tailwindcss').Config} */
const { fontFamily } = require("tailwindcss/defaultTheme");

module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        mont: ["var(--font-mont)", ...fontFamily.sans],
      },
      colors: {
        dark: "#0a0a0f",
        light: "#f8f9fc",
        primary: "#6366f1",       // indigo
        primaryDark: "#818cf8",   // lighter indigo for dark mode
        accent: "#06b6d4",        // cyan
        accentDark: "#22d3ee",
        surface: "#1e1e2e",
        surfaceLight: "#ffffff",
        muted: "#64748b",
        regime: {
          turbulent: "#ef4444",
          aperture: "#f59e0b",
          cascade: "#22c55e",
          coherent: "#06b6d4",
          locked: "#8b5cf6",
        },
      },
      animation: {
        "spin-slow": "spin 20s linear infinite",
        "pulse-glow": "pulse-glow 3s ease-in-out infinite",
        "float": "float 6s ease-in-out infinite",
      },
      keyframes: {
        "pulse-glow": {
          "0%, 100%": { opacity: 0.4 },
          "50%": { opacity: 0.8 },
        },
        "float": {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
      },
      backgroundImage: {
        "grid-pattern": "linear-gradient(rgba(99,102,241,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(99,102,241,0.03) 1px, transparent 1px)",
        "grid-pattern-dark": "linear-gradient(rgba(129,140,248,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(129,140,248,0.05) 1px, transparent 1px)",
      },
      backgroundSize: {
        "grid": "40px 40px",
      },
      boxShadow: {
        "glow": "0 0 40px rgba(99,102,241, 0.15)",
        "glow-lg": "0 0 80px rgba(99,102,241, 0.2)",
      },
    },
    screens: {
      "2xl": { max: "1535px" },
      xl: { max: "1279px" },
      lg: { max: "1023px" },
      md: { max: "767px" },
      sm: { max: "639px" },
      xs: { max: "479px" },
    },
  },
  plugins: [
    function ({ addVariant }) {
      addVariant("child", "& > *");
      addVariant("child-hover", "& > *:hover");
    },
  ],
};
