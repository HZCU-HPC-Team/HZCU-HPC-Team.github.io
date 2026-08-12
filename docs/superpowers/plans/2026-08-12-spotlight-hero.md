# Spotlight Reveal Hero Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the homepage hero with a full-screen dark hero whose signature mechanic is a cursor-following radial-gradient mask (canvas → `maskImage`) revealing a second image, built in Hugo + native JS/SCSS.

**Architecture:** A custom `hero-spotlight` block (theme's `parse_block_v2` renders any `layouts/partials/blocks/<type>.html`; the section gets `class="home-section wg-hero-spotlight"` automatically). Two stacked background layers (base z-10, reveal z-30), a hidden canvas as the mask data source, heading + asides at z-50. `assets/js/spotlight.js` runs the spotlight loop; `assets/js/editorial.js` gains a header `.is-over-hero` dark-state toggle. All styles go in a new `_spotlight-hero.scss`, imported by `template.scss`. The existing light `editorial-hero` partial stays untouched.

**Tech Stack:** Hugo Extended 0.135.0, Hugo Blox v5 module (theme), SCSS (Dart Sass), native JS bundled via theme's `plugins_js` (esbuild `js.Build`), Python standard-library test suite (`tests/test_generated_site.py`).

**Spec:** `docs/superpowers/specs/2026-08-12-spotlight-hero-design.md`

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `tests/test_generated_site.py` | Modify | Update hero assertions; add spotlight CSS/JS contract tests |
| `content/_index.md` | Modify | Swap `block: hero` → `block: hero-spotlight` with copy + image URLs |
| `layouts/partials/blocks/hero-spotlight.html` | Create | Hero markup: base/reveal layers, canvas, heading, asides, Playfair `<link>` |
| `assets/scss/pages/_spotlight-hero.scss` | Create | All spotlight hero styles, keyframes, reduced-motion contract |
| `assets/scss/template.scss` | Modify | Import the new file |
| `assets/scss/components/_navigation.scss` | Modify | `.editorial-header.is-over-hero` dark state |
| `assets/js/editorial.js` | Modify | Toggle `.is-over-hero` while hero in view |
| `assets/js/spotlight.js` | Create | Canvas mask spotlight loop (IIFE — shared bundle scope) |
| `config/_default/params.yaml` | Modify | `plugins_js: [editorial, spotlight]` |
| `README.md` | Modify | Fix MD040 (code fence language) |
| `docs/superpowers/specs/2026-08-12-spotlight-hero-design.md` | Modify | Fix markdownlint table spacing |

**Image URLs** (exact, from the approved prompt):
- BASE: `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260609_195923_b0ba8ace-1d1d-4f2c-9a28-1ab84b330680.png&w=1280&q=85`
- REVEAL: `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260609_201152_bba90a12-bf12-459f-91f0-51f237dbaf3b.png&w=1280&q=85`

---

### Task 1: Update tests — new hero assertions (red)

**Files:**
- Modify: `tests/test_generated_site.py`

- [ ] **Step 1: Replace `test_homepage_hero_is_editorial_split` with the spotlight variant**

Replace the whole `test_homepage_hero_is_editorial_split` method (currently asserts `editorial-hero`, `editorial-hero__copy`, `editorial-hero__media`, `srcset=`, `sizes=`, `banner`) with:

```python
    def test_homepage_hero_is_spotlight(self):
        for expected in (
            'class="hero-spotlight"',
            "data-spotlight-reveal",
            "data-spotlight-canvas",
            "hero-zoom",
            "Beyond the clock",
            "HZCU HPC Team",
            "Join Us",
            'href="/recruitment/join-us/"',
            "fonts.googleapis.com",
            "hf_20260609_195923",
            "hf_20260609_201152",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, self.homepage)
        self.assertEqual(self.homepage.count('id="section-hero-spotlight"'), 1)
```

- [ ] **Step 2: Update the SVG/GIF fixture injection**

In `test_svg_and_animated_gif_hero_assets_build_with_original_paths`, change the homepage rewrite so it injects a `filename` line above `base:` (the new block has no `filename: banner.jpg` to replace):

```python
                homepage.write_text(
                    homepage.read_text(encoding="utf-8").replace(
                        "        base:", f"        filename: {image_name}\n        base:", 1
                    ),
                    encoding="utf-8",
                )
```

- [ ] **Step 3: Update `test_small_raster_candidates_do_not_upscale`**

The hero srcset assertions live in this test (NOT in `test_editorial_landmarks_and_hero_ids_are_unique`, which only checks `<main` count and id uniqueness — leave that one unchanged). The new hero has no responsive `<img>` candidates (background-image layers), so the hero slice must assert the absence of `srcset` instead:

```python
    def test_small_raster_candidates_do_not_upscale(self):
        homepage = (self.fixture_output / "index.html").read_text(encoding="utf-8")
        hero = homepage.split('class="hero-spotlight"', 1)[1].split("</section>", 1)[0]
        self.assertNotIn("srcset=", hero)
        listing = (self.fixture_output / "post/index.html").read_text(encoding="utf-8")
        entry = listing.split("Editorial small", 1)[1].split("</article>", 1)[0]
        widths = [int(width) for width in re.findall(r"\s(\d+)w", entry)]
        self.assertTrue(widths)
        self.assertTrue(all(width <= 512 for width in widths))
```

- [ ] **Step 4: Update `test_task8_style_selectors_match_generated_home_contact_and_publication_dom`**

Change the first-section assertion from `wg-hero` to `wg-hero-spotlight`:

```python
        self.assertIn("wg-hero-spotlight", home_sections[0])
        self.assertTrue(all("wg-hero-spotlight" not in section for section in home_sections[1:]))
```

- [ ] **Step 5: Add the spotlight CSS/JS contract tests**

Add these three methods after `test_task8_style_selectors_match_generated_home_contact_and_publication_dom`:

```python
    def test_spotlight_hero_css_contract(self):
        css = "".join(self.compiled_css().split())
        self.assertRegex(css, r"\.hero-spotlight\{[^}]*height:100dvh")
        self.assertRegex(css, r"\.hero-spotlight__reveal\{[^}]*opacity:0")
        self.assertRegex(css, r"\.editorial-header\.is-over-hero\{[^}]*background")
        self.assertIn("@media(prefers-reduced-motion:reduce){", css)

    def test_spotlight_hero_js_source_contract(self):
        spotlight = (REPO_ROOT / "assets/js/spotlight.js").read_text(encoding="utf-8")
        for expected in ("SPOTLIGHT_R = 260", "maskImage", "prefers-reduced-motion", "pointer: fine", "toDataURL"):
            with self.subTest(expected=expected):
                self.assertIn(expected, spotlight)
        params = (REPO_ROOT / "config/_default/params.yaml").read_text(encoding="utf-8")
        self.assertIn("spotlight", params)
```

(Note: the regex `\.hero-spotlight__reveal\{[^}]*opacity:0` — in the compiled CSS the rule appears as `.hero-spotlight__reveal{opacity:0;...}`; if minification reorders, adjust to `[^}]*opacity:0[^}]*` in the implementation.)

- [ ] **Step 6: Run the suite to verify the new/updated tests fail (and nothing else breaks spuriously)**

Run: `./scripts/test-site.sh`
Expected: FAIL on `test_homepage_hero_is_spotlight` (no `hero-spotlight` in homepage yet), `test_spotlight_hero_css_contract`, `test_spotlight_hero_js_source_contract`, and the updated `test_small_raster_candidates_do_not_upscale` / `test_task8_style_selectors...` / SVG/GIF test. Other tests should still PASS (the old light hero assertions that pass today — e.g. `test_home_section_headings_are_h2_but_hero_remains_h1` — must still pass).

- [ ] **Step 7: Commit**

```bash
git add tests/test_generated_site.py
git commit -m "test: point homepage hero assertions at spotlight hero"
```

---

### Task 2: Hero block template + homepage front matter

**Files:**
- Create: `layouts/partials/blocks/hero-spotlight.html`
- Modify: `content/_index.md`

- [ ] **Step 1: Create the block template**

Create `layouts/partials/blocks/hero-spotlight.html`:

```html
{{/* Spotlight reveal hero: full-screen dark hero with a cursor-following
     radial mask that reveals a second image. Ported from the Lithos-style
     React prompt into Hugo; styles in assets/scss/pages/_spotlight-hero.scss,
     runtime in assets/js/spotlight.js. */}}
{{ $block := .wcBlock }}
{{ $title := $block.content.title | default site.Title }}
{{ $headline := $block.content.headline | default "Beyond the clock" }}
{{ $base_url := $block.content.image.base | default "" }}
{{ $reveal_url := $block.content.image.reveal | default "" }}
{{ $aside_left := $block.content.aside_left | default "" }}
{{ $aside_right := $block.content.aside_right | default "" }}
{{ $cta_text := $block.content.cta.text | default "Join Us" }}
{{ $cta_url := $block.content.cta.url | default "/recruitment/join-us/" }}
{{/* Optional local image overrides external URLs (used by the test suite and
     keeps the self-hosted option). SVG/GIF are referenced verbatim. */}}
{{ if $block.content.image.filename }}
  {{ with resources.Get (path.Join "media" $block.content.image.filename) }}
    {{ $base_url = .RelPermalink }}
  {{ end }}
{{ end }}

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@1,400;1,500;1,600&display=swap">

<section class="hero-spotlight" aria-labelledby="hero-spotlight-title">
  <div class="hero-spotlight__base hero-zoom" role="img" aria-label="{{ $title | plainify }}" {{ with $base_url }}style="background-image: url('{{ . }}')"{{ end }}></div>
  <div class="hero-spotlight__reveal" data-spotlight-reveal {{ with $reveal_url }}style="background-image: url('{{ . }}')"{{ end }}></div>
  <canvas class="hero-spotlight__canvas" data-spotlight-canvas aria-hidden="true"></canvas>

  <div class="hero-spotlight__heading">
    <h1 id="hero-spotlight-title">
      <span class="hero-spotlight__line hero-spotlight__line--accent hero-anim hero-reveal" style="animation-delay: 0.25s">{{ $headline }}</span>
      <span class="hero-spotlight__line hero-anim hero-reveal" style="animation-delay: 0.42s">{{ $title }}</span>
    </h1>
  </div>

  {{ with $aside_left }}
    <div class="hero-spotlight__aside hero-spotlight__aside--left hero-anim hero-fade" style="animation-delay: 0.7s">
      <p>{{ . }}</p>
    </div>
  {{ end }}
  <div class="hero-spotlight__aside hero-spotlight__aside--right hero-anim hero-fade" style="animation-delay: 0.85s">
    {{ with $aside_right }}<p>{{ . }}</p>{{ end }}
    <a class="hero-spotlight__cta" href="{{ $cta_url }}">{{ $cta_text }}</a>
  </div>
</section>
```

- [ ] **Step 2: Swap the homepage hero block**

In `content/_index.md`, replace the `- block: hero` entry (the `title/image/text` hero block) with:

```yaml
  - block: hero-spotlight
    content:
      headline: Beyond the clock
      title: HZCU HPC Team
      image:
        base: 'https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260609_195923_b0ba8ace-1d1d-4f2c-9a28-1ab84b330680.png&w=1280&q=85'
        reveal: 'https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260609_201152_bba90a12-bf12-459f-91f0-51f237dbaf3b.png&w=1280&q=85'
      aside_left: 浙大城市学院高性能计算（HPC）团队隶属于学校超算中心，专注性能评估与优化，在 ASC、IPCC、CPC 等国际竞赛中屡获佳绩。
      aside_right: 对高性能计算、并行计算与性能优化感兴趣？欢迎加入我们，一起探索计算科学的极限。
      cta:
        text: Join Us
        url: /recruitment/join-us/
```

The old `hero` block's `id:`-bearing blocks (`introduction`, `join-us`) are untouched. Do NOT keep the old `- block: hero` entry.

- [ ] **Step 3: Build to verify the block renders**

Run: `hugo --gc --minify --destination /tmp/spotlight-check`
Expected: build succeeds; `/tmp/spotlight-check/index.html` contains `class="home-section wg-hero-spotlight"`, `class="hero-spotlight"`, both image URLs, and exactly one `<h1`.

- [ ] **Step 4: Run the suite**

Run: `./scripts/test-site.sh`
Expected: `test_homepage_hero_is_spotlight`, the SVG/GIF test, `test_editorial_landmarks_and_hero_ids_are_unique`, `test_task8_style_selectors...` now PASS; `test_spotlight_hero_css_contract` and `test_spotlight_hero_js_source_contract` still FAIL (CSS/JS not implemented yet). `test_homepage_contains_required_strings` still PASSES ("HZCU HPC Team", "浙大城市学院高性能计算", "INTRODUCTION", "Meet the team" all still on the homepage).

- [ ] **Step 5: Commit**

```bash
git add layouts/partials/blocks/hero-spotlight.html content/_index.md
git commit -m "feat: add spotlight reveal hero block to homepage"
```

---

### Task 3: Spotlight hero styles

**Files:**
- Create: `assets/scss/pages/_spotlight-hero.scss`
- Modify: `assets/scss/template.scss`

- [ ] **Step 1: Create `assets/scss/pages/_spotlight-hero.scss`**

```scss
/* Full-screen dark hero with a cursor-following spotlight reveal.
   Layer order: base (z-10) < reveal (z-30) < heading/asides (z-50).
   The reveal layer is invisible until spotlight.js applies a mask. */

.home-section.wg-hero-spotlight {
  padding-block: 0;
}

.home-section.wg-hero-spotlight > .container {
  max-width: none;
  padding-inline: 0;
}

.hero-spotlight {
  position: relative;
  width: 100%;
  height: 100vh;
  height: 100dvh;
  overflow: hidden;
  background: var(--color-inverse);
}

.hero-spotlight__base,
.hero-spotlight__reveal {
  position: absolute;
  inset: 0;
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
}

.hero-spotlight__base {
  z-index: 10;
}

.hero-spotlight__reveal {
  z-index: 30;
  opacity: 0;
  transition: opacity 300ms var(--ease-out);
}

.hero-spotlight__reveal.is-visible {
  opacity: 1;
}

.hero-spotlight__canvas {
  position: absolute;
  inset: 0;
  display: none;
  pointer-events: none;
}

.hero-spotlight__heading {
  position: absolute;
  top: max(14%, 7rem);
  right: 0;
  left: 0;
  z-index: 50;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-inline: 1.25rem;
  text-align: center;
  pointer-events: none;
}

.hero-spotlight__heading h1 {
  margin: 0;
}

.hero-spotlight__line {
  display: block;
  color: #fff;
  font-size: clamp(3rem, 10vw, 4.5rem);
  font-weight: 400;
  line-height: 0.95;
  text-wrap: balance;
}

.hero-spotlight__line--accent {
  font-family: "Playfair Display", var(--font-display);
  font-style: italic;
  letter-spacing: -0.05em;
}

.hero-spotlight__line:not(.hero-spotlight__line--accent) {
  margin-top: -0.25rem;
  letter-spacing: -0.08em;
}

.hero-spotlight__aside {
  position: absolute;
  z-index: 50;
  max-width: 260px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.875rem;
  line-height: 1.625;
}

.hero-spotlight__aside p {
  margin: 0;
}

.hero-spotlight__aside--left {
  display: none;
  bottom: 3.5rem;
  left: 2.5rem;
}

.hero-spotlight__aside--right {
  right: 1.25rem;
  bottom: 2.5rem;
  left: 1.25rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--space-4);
}

.hero-spotlight__cta {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  padding: 0.75rem 1.75rem;
  border-radius: 999px;
  color: var(--color-paper);
  background: var(--color-clay);
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  transition:
    background-color 180ms var(--ease-out),
    transform 180ms var(--ease-out),
    box-shadow 180ms var(--ease-out);
}

.hero-spotlight__cta:hover,
.hero-spotlight__cta:focus-visible {
  color: var(--color-paper);
  background: var(--color-clay-dark);
  transform: scale(1.03);
}

.hero-spotlight__cta:focus-visible {
  outline-color: var(--color-paper);
}

/* Entrance animations (ported from the prompt; --ease-out matches its bezier). */

@keyframes heroReveal {
  0% { opacity: 0; transform: translateY(28px); filter: blur(12px); }
  100% { opacity: 1; transform: translateY(0); filter: blur(0); }
}

@keyframes heroFadeUp {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}

@keyframes heroZoom {
  0% { transform: scale(1.12); }
  100% { transform: scale(1); }
}

.hero-anim {
  opacity: 0;
  animation-fill-mode: forwards;
  animation-timing-function: var(--ease-out);
}

.hero-reveal {
  animation-name: heroReveal;
  animation-duration: 1.1s;
}

.hero-fade {
  animation-name: heroFadeUp;
  animation-duration: 1s;
}

.hero-zoom {
  animation: heroZoom 1.8s var(--ease-out) forwards;
}

@include reduce-motion {
  .hero-anim,
  .hero-zoom {
    animation: none;
    opacity: 1;
  }

  .hero-spotlight__reveal {
    transition: none;
  }
}

@media (min-width: 40rem) {
  .hero-spotlight__line {
    font-size: clamp(4.5rem, 12vw, 6rem);
  }

  .hero-spotlight__aside--left {
    display: block;
    left: 2.5rem;
  }

  .hero-spotlight__aside--right {
    right: 2.5rem;
    bottom: 6rem;
    left: auto;
  }
}

@media (min-width: 48rem) {
  .hero-spotlight__line {
    font-size: 6rem;
  }

  .hero-spotlight__aside--left {
    left: 3.5rem;
  }

  .hero-spotlight__aside--right {
    right: 3.5rem;
  }
}
```

- [ ] **Step 2: Import it in `template.scss`**

After `@import "pages/home";` add:

```scss
@import "pages/spotlight-hero";
```

- [ ] **Step 3: Run the suite**

Run: `./scripts/test-site.sh`
Expected: `test_spotlight_hero_css_contract` PASSES now (height:100dvh, reveal opacity:0, `.is-over-hero` rule, reduced-motion media query). `test_spotlight_hero_js_source_contract` still FAILS. If the compiled CSS reorders `opacity:0` inside the reveal rule, relax the regex to `[^}]*opacity:0[^}]*` and re-run.

- [ ] **Step 4: Commit**

```bash
git add assets/scss/pages/_spotlight-hero.scss assets/scss/template.scss
git commit -m "feat: style spotlight hero with dark layers and entrance animations"
```

---

### Task 4: Header dark state

**Files:**
- Modify: `assets/scss/components/_navigation.scss`
- Modify: `assets/js/editorial.js`

- [ ] **Step 1: Add the `.is-over-hero` styles to `_navigation.scss`**

Append at the end of the file (after the existing `@media (max-width: 991.98px)` block):

```scss
/* Dark state while a full-screen hero is in view (toggled by editorial.js). */
.editorial-header.is-over-hero {
  background: rgba(36, 36, 31, 0.65);
  border-bottom-color: transparent;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.editorial-header.is-over-hero .editorial-brand,
.editorial-header.is-over-hero .editorial-menu-link,
.editorial-header.is-over-hero .editorial-menu-details summary,
.editorial-header.is-over-hero .editorial-search {
  color: var(--color-inverse-text);
}

.editorial-header.is-over-hero .editorial-menu-toggle {
  color: var(--color-inverse-text);
  border-color: rgba(242, 239, 231, 0.4);
}

.editorial-header.is-over-hero .editorial-menu.collapse.show {
  background: var(--color-inverse);
}
```

- [ ] **Step 2: Toggle `.is-over-hero` in `editorial.js`**

In `assets/js/editorial.js`, after the `header` const, add a hero lookup, and inside `updateHeader()` add the toggle:

```js
  const header = document.querySelector("[data-editorial-header]");
  const hero = document.querySelector(".hero-spotlight");
  const revealElements = document.querySelectorAll("[data-reveal]");

  const updateHeader = () => {
    if (!header) return;
    header.classList.toggle("is-compact", window.scrollY > 24);
    if (hero) {
      header.classList.toggle("is-over-hero", hero.getBoundingClientRect().bottom > 0);
    }
  };
```

(Only the two lines above change — the `header` const line gains the new `hero` line after it, and `updateHeader` gains the `if (hero)` block.)

- [ ] **Step 3: Run the suite**

Run: `./scripts/test-site.sh`
Expected: all spotlight tests PASS except `test_spotlight_hero_js_source_contract` (still FAIL — `spotlight.js` and `params.yaml` not done). Header-related tests (e.g. `test_editorial_landmarks_and_hero_ids_are_unique`) still PASS.

- [ ] **Step 4: Commit**

```bash
git add assets/scss/components/_navigation.scss assets/js/editorial.js
git commit -m "feat: dark header state while spotlight hero is in view"
```

---

### Task 5: Spotlight runtime JS

**Files:**
- Create: `assets/js/spotlight.js`
- Modify: `config/_default/params.yaml`

- [ ] **Step 1: Create `assets/js/spotlight.js`**

IIFE (shared bundle scope with `editorial.js`). Guarded so it no-ops on non-hero pages, reduced motion, and non-fine pointers:

```js
(() => {
  const reveal = document.querySelector("[data-spotlight-reveal]");
  if (!reveal) return;
  const reducedMotion = window.matchMedia
    ? window.matchMedia("(prefers-reduced-motion: reduce)")
    : { matches: false };
  const finePointer = window.matchMedia
    ? window.matchMedia("(pointer: fine)")
    : { matches: false };
  if (reducedMotion.matches || !finePointer.matches) return;
  const canvas = document.querySelector("[data-spotlight-canvas]");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  const SPOTLIGHT_R = 260;
  const mouse = { x: 0, y: 0 };
  const smooth = { x: -999, y: -999 };
  let rafId = 0;
  let applied = false;

  const resize = () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  };
  resize();
  window.addEventListener("resize", resize);

  window.addEventListener(
    "mousemove",
    (event) => {
      mouse.x = event.clientX;
      mouse.y = event.clientY;
    },
    { passive: true },
  );

  const tick = () => {
    smooth.x += (mouse.x - smooth.x) * 0.1;
    smooth.y += (mouse.y - smooth.y) * 0.1;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const gradient = ctx.createRadialGradient(
      smooth.x,
      smooth.y,
      0,
      smooth.x,
      smooth.y,
      SPOTLIGHT_R,
    );
    gradient.addColorStop(0, "rgba(255,255,255,1)");
    gradient.addColorStop(0.4, "rgba(255,255,255,1)");
    gradient.addColorStop(0.6, "rgba(255,255,255,0.75)");
    gradient.addColorStop(0.75, "rgba(255,255,255,0.4)");
    gradient.addColorStop(0.88, "rgba(255,255,255,0.12)");
    gradient.addColorStop(1, "rgba(255,255,255,0)");
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const mask = canvas.toDataURL();
    reveal.style.maskImage = `url(${mask})`;
    reveal.style.webkitMaskImage = `url(${mask})`;
    reveal.style.maskSize = "100% 100%";
    reveal.style.webkitMaskSize = "100% 100%";

    if (!applied) {
      applied = true;
      reveal.classList.add("is-visible");
    }
    rafId = window.requestAnimationFrame(tick);
  };
  rafId = window.requestAnimationFrame(tick);

  window.addEventListener("unload", () => {
    window.cancelAnimationFrame(rafId);
  });
})();
```

- [ ] **Step 2: Register the bundle in `params.yaml`**

In `config/_default/params.yaml`, change:

```yaml
plugins_js:
  - editorial
```

to:

```yaml
plugins_js:
  - editorial
  - spotlight
```

(The theme's `site_js.html` does `resources.Get (printf "js/%s.js" .)` and bundles via `js.Build` — `assets/js/spotlight.js` matches, same as `editorial.js`.)

- [ ] **Step 3: Build + verify the bundle contains the spotlight code**

Run: `hugo --gc --minify --destination /tmp/spotlight-check2`
Then: `grep -c "maskImage" /tmp/spotlight-check2/js/wowchemy.min.js`
Expected: output ≥ 1 (the minified bundle contains the spotlight logic). If grep finds 0, check the bundle path in `/tmp/spotlight-check2/index.html` (`<script src=...wowchemy...>`) and grep that file.

- [ ] **Step 4: Run the suite**

Run: `./scripts/test-site.sh`
Expected: ALL tests PASS (including `test_spotlight_hero_js_source_contract`).

- [ ] **Step 5: Commit**

```bash
git add assets/js/spotlight.js config/_default/params.yaml
git commit -m "feat: add cursor spotlight reveal runtime"
```

---

### Task 6: Final verification, markdownlint fixes, docs

**Files:**
- Modify: `README.md` (MD040)
- Modify: `docs/superpowers/specs/2026-08-12-spotlight-hero-design.md` (MD032/MD060)
- Modify: `content/_index.md` (check old `# ERROR` comment placement — see Step 2)

- [ ] **Step 1: Fix the README MD040 warning**

In `README.md`, the Project Structure code fence (line ~52) lacks a language. Change the opening fence:

````markdown
```
content/           # 网站内容（Markdown + YAML 前置元数据）
````

to:

````markdown
```txt
content/           # 网站内容（Markdown + YAML 前置元数据）
````

- [ ] **Step 2: Fix the spec markdownlint warnings**

In `docs/superpowers/specs/2026-08-12-spotlight-hero-design.md`:
- Add a blank line before the first list (line ~12, `- **Date:**` block) if missing.
- Fix the two tables (the "Copy" section and the "File Summary" section): add spaces inside pipe delimiters (`| A | B |`), with a header separator row (`|---|---|`).

- [ ] **Step 3: Sanity-check `content/_index.md`**

Verify the `# ERROR：Bao Zhuhan` comment (which sits inside the commented-out Latest Preprints block) is still after the last active section and the file builds. Run: `hugo --gc --minify --destination /tmp/spotlight-final`
Expected: build succeeds.

- [ ] **Step 4: Full regression**

Run: `./scripts/test-site.sh`
Expected: all tests PASS (~77+ tests).

Run the production-style build:
```bash
HUGO_ENVIRONMENT=production hugo --minify --baseURL "https://hpc.hzcu.edu.cn/"
```
Expected: exit 0.

- [ ] **Step 5: Commit**

```bash
git add README.md docs/superpowers/specs/2026-08-12-spotlight-hero-design.md
git commit -m "chore: fix markdownlint warnings in README and spec"
```
