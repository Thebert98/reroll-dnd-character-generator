/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // ---- Re:Roll "Tavern" palette (warm, cozy, adventurous) ----
        // Literal tavern swatches:
        tavern: {
          amber: "#D8BA1F", // Ale Amber
          hearth: "#E6C36B", // Hearth Gold
          oak: "#7A4B2A", // Oak Brown
          walnut: "#382417", // Dark Walnut
          parchment: "#F3E6C7", // Parchment
          charcoal: "#1E1A17", // Soot Charcoal
          forest: "#2E5B3A", // Forest Green
          burgundy: "#7A1F23", // Deep Burgundy
          iron: "#5A5F66", // Iron Grey
          candle: "#FFF3D6", // Inn Candle
          ember: "#C9772E", // warm ember (hearth fire)
        },
        // ---- Semantic tokens (same names the components already use, mapped
        //      to tavern values so the whole UI re-skins from here) ----
        brand: {
          red: "#7A1F23", // Deep Burgundy — primary/danger/error
          gold: "#D8BA1F", // Ale Amber — accents, headings, logo
          green: "#2E5B3A", // Forest Green — success / "valid"
          slate: "#382417", // Dark Walnut — surfaces
          stone: "#F3E6C7", // Parchment — light neutral text
          ember: "#C9772E", // hearth fire — highlights / re-roll
          arcane: "#E6C36B", // Hearth Gold — AI / "magic" (warm)
          sky: "#6E8CA0", // muted steel — info / links
          teal: "#3E7C5A", // mossy green — secondary success
          gray: "#5A5F66", // Iron Grey — muted text
        },
        // Warm dark surfaces (charcoal → walnut), replacing the cool ink scale.
        ink: {
          900: "#1E1A17", // Soot Charcoal — page background
          800: "#241E19", // raised panel
          700: "#2C241C", // card
          600: "#382417", // Dark Walnut — borders-strong
          500: "#4A3829",
        },
        // Legacy alias kept pointing at the (now warm) magic accent.
        arcane: "#E6C36B",
      },
      fontFamily: {
        // Tavern serif for display/logo; Merriweather for headings + body.
        display: ['"IM Fell English SC"', "Georgia", "serif"],
        heading: ['"Merriweather"', "Georgia", "serif"],
        body: ['"Merriweather"', "Georgia", "serif"],
      },
      boxShadow: {
        gold: "0 0 24px rgba(216, 186, 31, 0.25)",
        ember: "0 0 24px rgba(201, 119, 46, 0.30)",
        card: "0 1px 0 rgba(255,243,214,0.05), 0 8px 24px rgba(0,0,0,0.5)",
      },
      backgroundImage: {
        arcane: "var(--rr-arcane-pattern)",
      },
    },
  },
  plugins: [],
};
