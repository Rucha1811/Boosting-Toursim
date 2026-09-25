/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        sand: {
          50: "#fbf8f3",
          100: "#f5efe4",
          200: "#e9ddc9",
          300: "#d9c5a4",
          400: "#c5a878",
          500: "#b08d57",
        },
        ink: {
          DEFAULT: "#1d1a16",
          soft: "#4b453c",
          muted: "#7a7266",
          faint: "#a89f92",
        },
        teal: {
          DEFAULT: "#0e5d54",
          deep: "#0a413b",
          dark: "#07322e",
          soft: "#e8f2f0",
          mid: "#2f7d73",
        },
        saffron: {
          DEFAULT: "#e0762c",
          deep: "#c0581a",
          light: "#f6e7d8",
        },
        blush: {
          DEFAULT: "#c2454f",
          light: "#f7e5e7",
        },
        marigold: {
          DEFAULT: "#e8a710",
          light: "#faf1d9",
        },
      },
      fontFamily: {
        display: ["Fraunces", "Georgia", "serif"],
        body: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 2px rgb(29 26 22 / 0.04), 0 8px 24px rgb(29 26 22 / 0.06)",
        lift: "0 2px 4px rgb(29 26 22 / 0.05), 0 16px 40px rgb(29 26 22 / 0.12)",
        ring: "0 0 0 3px rgb(228 116 44 / 0.25)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        marquee: {
          "0%": { transform: "translateX(0)" },
          "100%": { transform: "translateX(-50%)" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.6s cubic-bezier(0.22,1,0.36,1) both",
        marquee: "marquee 28s linear infinite",
      },
    },
  },
  plugins: [],
};