# Re:Roll — Branding implementation

How the **Re:Roll Character Builder** style book maps onto the frontend.

## Identity

- **Name:** Re:Roll — Character Builder (formerly the working title "Arcane Architect").
- **Tagline:** *Roll your legend. Build your story.*
- **Descriptor:** AI-powered D&D character generator.
- **Mascot:** Dicewyrm (a friendly red dragon) — see asset slots below.

## Color palette

| Token | Hex | Use |
|-------|-----|-----|
| `brand-red` (Dragon Red) | `#B71A1A` | Primary buttons, primary actions |
| `brand-gold` (Ancient Gold) | `#D4AF37` | Logo, headings, accents, focus |
| `brand-green` (Forest Green) | `#2E7D32` | Success / "valid" states |
| `brand-slate` (Deep Slate) | `#1E2D3B` | Surfaces / borders |
| `brand-stone` (Stone) | `#C7C6BB` | Light neutral text |
| `brand-ember` | `#FF6A10` | Highlights, re-roll energy |
| `brand-arcane` | `#6B4DFF` | AI / magic affordances |
| `brand-sky` | `#36AAFF` | Info / links |
| `brand-teal` | `#20C997` | Secondary success |
| `brand-gray` | `#7A806C` | Muted text |

Dark UI surfaces use an `ink` scale derived from Deep Slate
(`ink-900` page → `ink-600` deep slate).

## Typography

- **Cinzel** (`font-display`) — the logo and hero display moments.
- **Sora** (`font-heading`) — section titles and UI headings.
- **Inter** (`font-body`) — body text and inputs.

## Components (style-book spec)

- **Buttons:** Primary (Dragon Red), Secondary (Deep Slate outline), Ghost
  (text only), Danger (Ember/Red).
- **Tags/Badges:** New, Popular, AI Generated, Homebrew, Official.
- **Cards:** dark `ink-700` surface, gold hairline accent on hover.
- **Inputs:** dark field, gold/sky focus ring.

## Icons

Class icons (Fighter, Wizard, Rogue, Cleric, Ranger, Bard, Warlock, Paladin,
Druid, Monk, Barbarian, Sorcerer) and action icons (**Generate, Re-Roll, Lock
Field, Save, Export**) — implemented as inline SVG components for crispness.

## Asset approach

Brand **marks** are authored as SVG (sharp at any size): favicon/d20 die, the
Re:Roll wordmark, and the arcane background pattern. Photographic raster art
(dragon hero logo, Dicewyrm mascot illustration, header/social banners) is **not**
generated here — drop final art into `frontend/public/brand/` at these slots:

| File | Purpose | Recommended size |
|------|---------|------------------|
| `public/brand/logo.png` | Full dragon hero logo | 1200×630 transparent |
| `public/brand/mascot-dicewyrm.png` | Mascot illustration | 512×512 transparent |
| `public/brand/header-banner.jpg` | Marketing header | 1600×400 |
| `public/og-image.png` | Social / OpenGraph preview | 1200×630 |

Until those exist, the app uses the SVG logo lockup and renders fine without them.

## Rollout (PRs)

1. Design tokens & typography (this doc).
2. Brand assets — favicon, d20 mark, wordmark/logo, pattern, meta.
3. App shell & copy — Re:Roll naming, header logo, taglines, footer.
4. UI components — buttons, badges, cards, inputs.
5. Character sheet theming & action icons.
