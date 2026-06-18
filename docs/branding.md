# Re:Roll — Branding implementation (Tavern theme)

How the **Re:Roll Character Builder** "Tavern" style book maps onto the frontend.
Warm, cozy, and adventurous — candlelight on wood grain and parchment.

> This is an **alternate branding** explored on the `claude/tavern-rebrand`
> branch and intentionally **not merged to `main`**. `main` carries the earlier
> (cool gold/arcane) Re:Roll theme.

## Identity

- **Name:** Re:Roll — Character Builder.
- **Tagline (display):** *Roll. Create. Adventure.*
- **Hero line:** *Your next legend awaits at the tavern.*
- **Descriptor:** The AI-powered fantasy character builder for tabletop RPG adventurers.

## Color palette (warm tavern)

| Token | Hex | Use |
|-------|-----|-----|
| `tavern-amber` / `brand-gold` (Ale Amber) | `#D8BA1F` | Accents, headings, logo, focus |
| `tavern-hearth` (Hearth Gold) | `#E6C36B` | Soft glow / "magic" accent |
| `tavern-oak` (Oak Brown) | `#7A4B2A` | Secondary trim |
| `tavern-walnut` / `brand-slate` (Dark Walnut) | `#382417` | Surfaces / borders |
| `tavern-parchment` / `brand-stone` (Parchment) | `#F3E6C7` | Light neutral text |
| `tavern-charcoal` (Soot Charcoal) | `#1E1A17` | Page background |
| `tavern-forest` / `brand-green` (Forest Green) | `#2E5B3A` | Success / "valid" |
| `tavern-burgundy` / `brand-red` (Deep Burgundy) | `#7A1F23` | Primary action / danger / errors |
| `tavern-iron` / `brand-gray` (Iron Grey) | `#5A5F66` | Muted text |
| `tavern-candle` (Inn Candle) | `#FFF3D6` | Brightest highlights |
| `tavern-ember` / `brand-ember` | `#C9772E` | Hearth-fire highlights / re-roll |

Dark surfaces use an `ink` scale shifted from cool blue to warm charcoal→walnut
(`ink-900` charcoal → `ink-600` walnut).

## Typography

- **IM Fell English SC** (`font-display`) — the logo and display moments
  (old-printing-press tavern serif).
- **Merriweather** (`font-heading` / `font-body`) — headings, UI, and body.

## How the re-skin works

The components built earlier route every color through semantic `brand-*` and
`ink-*` tokens, so this entire theme is achieved mostly by **re-pointing those
tokens** (in `tailwind.config.js`) to tavern values and swapping the fonts —
plus warming the SVG favicon/d20/logo and the headline copy. No component logic
changes.

## Asset slots

Brand marks are SVG (favicon medallion, d20, wordmark). Photographic tavern art
(dragon/innkeeper hero, header banner, OG image) drops into
`frontend/public/brand/` as documented there.
