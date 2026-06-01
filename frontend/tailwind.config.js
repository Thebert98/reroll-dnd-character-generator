/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Re:Roll brand palette (see docs/branding.md / the style book).
        brand: {
          red: "#B71A1A", // Dragon Red — primary action
          gold: "#D4AF37", // Ancient Gold — accents, headings, logo
          green: "#2E7D32", // Forest Green — success / "valid"
          slate: "#1E2D3B", // Deep Slate — surfaces
          stone: "#C7C6BB", // Stone — light neutral text
          ember: "#FF6A10", // Ember Orange
          arcane: "#6B4DFF", // Arcane Purple — AI / magic
          sky: "#36AAFF", // Sky Blue — info / links
          teal: "#20C997", // Teal
          gray: "#7A806C", // Neutral Gray
        },
        // Dark UI surfaces derived from Deep Slate (panels in the style book).
        ink: {
          900: "#0B1118", // page background
          800: "#0F1620", // raised panel
          700: "#16202C", // card
          600: "#1E2D3B", // deep slate / borders-strong
          500: "#26333F",
        },
        // Keep the old `arcane` alias pointing at Arcane Purple so components
        // migrate incrementally without breaking between PRs.
        arcane: "#6B4DFF",
      },
      fontFamily: {
        display: ['"Cinzel"', "serif"], // logo + display headings
        heading: ['"Sora"', "system-ui", "sans-serif"], // section headings / UI
        body: ['"Inter"', "system-ui", "sans-serif"], // body text
      },
      boxShadow: {
        gold: "0 0 24px rgba(212, 175, 55, 0.25)",
        ember: "0 0 24px rgba(255, 106, 16, 0.25)",
        card: "0 1px 0 rgba(255,255,255,0.04), 0 8px 24px rgba(0,0,0,0.45)",
      },
      backgroundImage: {
        // Subtle arcane runes pattern (defined in index.css via CSS var).
        arcane: "var(--rr-arcane-pattern)",
      },
    },
  },
  plugins: [],
};
