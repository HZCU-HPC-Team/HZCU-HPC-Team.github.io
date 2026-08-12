# Spotlight Reveal Hero — Design Spec

- **Date:** 2026-08-12
- **Status:** Approved (design confirmed by user)
- **Goal:** Replace the homepage hero with a full-screen dark hero featuring a cursor-following spotlight that reveals a second image through a soft radial mask, built within the site's existing Hugo + Hugo Blox architecture and warm-editorial design system.

## Background

The team received a detailed React/Vite/Tailwind prompt for a geology-brand hero ("Lithos") whose signature mechanic is a canvas-based radial-gradient mask that reveals a second image inside a soft circle trailing the cursor. The task: port that effect into this repository — a Hugo static site with no JS package manager, no Tailwind, no React — while staying true to the site's own design system (warm editorial: paper/ink/clay palette, serif display type, progressive enhancement, reduced-motion contract).

User decisions (confirmed):

- **Content:** HPC-team wording, not the Lithos geology copy.
- **Images:** use the two image URLs from the prompt exactly.
- **Approach:** Option A — standalone spotlight hero block + site-wide header dark-state adaptation.

## Design Decisions

1. **New hero block.** Add `layouts/partials/blocks/hero-spotlight.html`, configured in `content/_index.md` as `block: hero-spotlight`, replacing the existing `block: hero`. The existing `hero.html` (light editorial hero) stays untouched as a fallback option.
2. **Dark region scoped to the hero only.** Hero uses the existing `--color-inverse` (dark ink) token; the rest of the homepage (INTRODUCTION, JOIN US, CTA) keeps the light warm-editorial styling.
3. **Header adaptation.** The global editorial header gains an `.is-over-hero` state (transparent dark background + light text, backdrop blur) while the hero is in view; reverts to the current paper style on scroll. Implemented by extending the existing scroll logic in `assets/js/editorial.js`.
4. **Fonts.** Playfair Display (italic, `display=swap`) loaded via a `<link>` emitted only from the hero-spotlight partial (progressive: other pages unaffected). Fallback chain: Playfair → `--font-display` (Iowan Old Style).
5. **Progressive enhancement.** The reveal layer is transparent by default (no-JS and reduced-motion users see the base image only). All entrance animations disabled under `prefers-reduced-motion`. Spotlight tracking is pointer-only (touch devices see the base image).
6. **Buttons use the existing clay palette** (`--color-clay` / `--color-clay-dark`) instead of the prompt's `#e8702a`, keeping the CTA within the site's warm palette while preserving the scale/transition behavior.

## Copy

| Prompt original | HPC version |
| --- | --- |
| Line 1 (italic serif): "Layers hold" | "Beyond the clock" |
| Line 2 (sans, tight tracking): "tales of time" | "HZCU HPC Team" |
| Bottom-left paragraph | 「浙大城市学院高性能计算（HPC）团队隶属于学校超算中心，专注性能评估与优化，在 ASC、IPCC、CPC 等国际竞赛中屡获佳绩。」 |
| Bottom-right paragraph + button | 「对高性能计算、并行计算与性能优化感兴趣？欢迎加入我们，一起探索计算科学的极限。」+ button "Join Us" → `/recruitment/join-us/` |

Large display lines stay English (Chinese has no italic); supporting paragraphs are Chinese.

## Page Structure

### `content/_index.md`

Replace the `hero` block with:

```yaml
- block: hero-spotlight
  content:
    title: HZCU HPC Team
    text: <markdown supported intro copy>
    image:
      base: 'https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260609_195923_b0ba8ace-1d1d-4f2c-9a28-1ab84b330680.png&w=1280&q=85'
      reveal: 'https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260609_201152_bba90a12-bf12-459f-91f0-51f237dbaf3b.png&w=1280&q=85'
    aside_left: <Chinese one-liner>
    aside_right: <Chinese one-liner>
    cta:
      text: Join Us
      url: /recruitment/join-us/
```

(Exact field names to be finalized during implementation; the block template falls back to sensible defaults when fields are absent.)

### Template `layouts/partials/blocks/hero-spotlight.html`

Layers (all inside `<section class="hero-spotlight">`):

1. Base layer: `<div class="hero-spotlight__base hero-zoom" role="img" aria-label="..." style="background-image: url(BG_IMAGE_1)">`
2. Reveal layer: `<div class="hero-spotlight__reveal" data-spotlight-reveal style="background-image: url(BG_IMAGE_2)">`
3. Hidden canvas: `<canvas data-spotlight-canvas aria-hidden="true">`
4. Heading (z-50, `pointer-events-none`): `<h1>` with two block spans (line 1 italic Playfair, line 2 sans) + the static copy lines
5. Bottom-left paragraph (hidden < sm)
6. Bottom-right block: paragraph + Join Us button (anchor styled as pill CTA)

Emits `<link rel="preconnect">` + Playfair stylesheet link when the block is present.

## Styling — `assets/scss/pages/_spotlight-hero.scss`

New file, imported by `template.scss` after `pages/home`.

- `.hero-spotlight`: `position: relative; width: 100%; height: 100dvh; overflow: hidden; background: var(--color-inverse);`
- `.hero-spotlight__base` / `__reveal`: `position: absolute; inset: 0; background-position: center; background-size: cover; background-repeat: no-repeat;`
- `.hero-spotlight__reveal`: `z-index: 30; opacity: 0;` → JS sets `opacity: 1` only after a mask has been applied (no-JS safe). JS applies `maskImage` / `webkitMaskImage` with `maskSize: 100% 100%`.
- `canvas[data-spotlight-canvas]`: `position: absolute; inset: 0; pointer-events: none; display: none;`
- `.hero-spotlight__heading`: `position: absolute; top: 14%; left: 0; right: 0; z-index: 50; display: flex; flex-direction: column; align-items: center; text-align: center; padding-inline: 1.25rem; pointer-events: none;`
  - Line 1: `font-family: 'Playfair Display', var(--font-display); font-style: italic; letter-spacing: -0.05em;`
  - Line 2: `letter-spacing: -0.08em; margin-top: -0.25rem;`
  - Type scale (maps prompt's `text-5xl → sm:text-7xl → md:text-8xl`): `font-size: clamp(3rem, 2rem + 4vw, 4.5rem)` on mobile, stepping up at `sm` and `md` breakpoints to a max of `6rem` (aligned with the site's `--heading-hero` family). Both lines `color: white; line-height: 0.95;`
- `.hero-spotlight__aside-left`: `position: absolute; bottom: 3.5rem; left: 2.5rem/3.5rem; z-index: 50; max-width: 260px; display: none` → `block` at `sm`. `color: rgba(255,255,255,0.8); font-size: 0.875rem; line-height: 1.625;`
- `.hero-spotlight__aside-right`: `position: absolute; bottom: 2.5rem (6rem at sm); left/right: 1.25rem (auto at sm, right 2.5rem/3.5rem); z-index: 50; max-width: 260px; display: flex; flex-direction: column; align-items: flex-start; gap: 1rem/1.25rem;`
- CTA button: `background: var(--color-clay); color: var(--color-paper); border-radius: 999px; padding: 0.75rem 1.75rem; font-weight: 500; min-height: 44px; transition: background-color 180ms var(--ease-out), transform 180ms var(--ease-out), box-shadow 180ms;` hover/focus: `background: var(--color-clay-dark); transform: scale(1.03);` focus-visible uses the site ring contract (light ring for contrast on dark).
- Entrance animation classes (`.hero-anim`, `.hero-reveal`, `.hero-fade`, `.hero-zoom`) with the prompt's keyframes (`heroReveal` blur-rise 1.1s, `heroFadeUp` 1s, `heroZoom` 1.8s), `cubic-bezier(0.16,1,0.3,1)` (matches `--ease-out`), delays 0.25s / 0.42s / 0.7s / 0.85s. All wrapped in `@include reduce-motion { animation: none; opacity: 1; }`.
- z-order: base 10 → reveal 30 → heading/asides 50 (matches prompt).

### Header dark state — `assets/scss/components/_navigation.scss`

`.editorial-header.is-over-hero`: `background: rgba(36,36,31,0.55); backdrop-filter: blur(8px); border-bottom-color: transparent;` with `.editorial-brand`, `.editorial-menu-link`, `.editorial-search` colored `var(--color-inverse-text)`. `.is-compact` rules still apply.

## JavaScript — `assets/js/spotlight.js`

Registered in `config/_default/params.yaml` `plugins_js: [editorial, spotlight]` (verify the theme's bundle order during implementation).

Guard: return early if `[data-spotlight-reveal]` absent OR `prefers-reduced-motion: reduce` OR no pointer support (`matchMedia('(pointer: fine)')`).

Core (ported verbatim from the prompt's React logic):

- `const SPOTLIGHT_R = 260;`
- Refs: `mouse {x,y}` (raw), `smooth {x,y}` (eased), `raf` id; `cursorPos` state init `{x: -999, y: -999}`.
- `mousemove` → store `e.clientX/clientY`.
- RAF loop: `smooth.x += (mouse.x - smooth.x) * 0.1;` (same for y), then apply mask.
- Canvas sized to `window.innerWidth/innerHeight` on mount + `resize`.
- Per frame: clear; build `radialGradient(x, y, 0, x, y, SPOTLIGHT_R)` with stops `0 → rgba(255,255,255,1)`, `0.4 → 1`, `0.6 → 0.75`, `0.75 → 0.4`, `0.88 → 0.12`, `1 → 0`; fill the arc; `canvas.toDataURL()`; apply to reveal div as `maskImage`/`webkitMaskImage` with `maskSize: '100% 100%'`. First frame with a valid mask also sets `opacity: 1` on the reveal layer.
- Cleanup on unload (remove listener, cancel RAF).

### `assets/js/editorial.js` change

In `updateHeader()`, also toggle `.is-over-hero` on the header while `scrollY` keeps the hero section in view (hero element bounds contain the current scroll position, or `scrollY < heroHeight - headerHeight` — finalize in implementation).

## Accessibility & Progressive Enhancement Contract

- Heading is the page's single `h1`; supporting paragraphs are real content (no `aria-hidden` on text that is content). Base/reveal images are decorative background layers (`aria-label` on base layer only, or omitted entirely — finalize in implementation).
- No-JS: reveal layer stays `opacity: 0` → base image fully visible; all content readable.
- `prefers-reduced-motion`: entrance animations disabled; spotlight tracking disabled (base image shown).
- Touch devices: base image shown (no cursor).
- CTA and any interactive elements keep ≥44px touch targets and the focus-visible ring contract.
- `100dvh` with `overflow: hidden` on the section; heading positioned below the fixed header's height.

## Tests

Update `tests/test_generated_site.py`:

- Homepage contains `.hero-spotlight`, `[data-spotlight-reveal]`, `[data-spotlight-canvas]`.
- Reveal layer default `opacity: 0` in compiled CSS (no-JS safe).
- Reduced-motion block disables `.hero-anim`/`.hero-zoom` (assert in whitespace-stripped CSS like existing tests).
- Header `.is-over-hero` rule exists in compiled CSS.
- Existing assertions (hero split, accessibility, etc.) must keep passing — the old `wg-hero`/`editorial-hero` assertions need review: `editorial-hero` still exists as template but is no longer on the homepage; adjust or keep tests accordingly.

Validation: `./scripts/test-site.sh` full suite + `hugo --gc --minify` production build.

## File Summary

| File | Action |
| --- | --- |
| `content/_index.md` | Edit — replace hero block with `hero-spotlight` |
| `layouts/partials/blocks/hero-spotlight.html` | New |
| `assets/scss/pages/_spotlight-hero.scss` | New |
| `assets/scss/template.scss` | Edit — import new file |
| `assets/scss/components/_navigation.scss` | Edit — `.is-over-hero` state |
| `assets/js/spotlight.js` | New |
| `assets/js/editorial.js` | Edit — header dark-state toggle |
| `config/_default/params.yaml` | Edit — `plugins_js: [editorial, spotlight]` |
| `tests/test_generated_site.py` | Edit — hero assertions |
