# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

This is the HZCU HPC Team's static website, built with Hugo and Hugo Blox (the Bootstrap v5 module). The theme is consumed as Hugo modules declared in `go.mod` and `config/_default/module.yaml`; there is no checked-in theme directory, JavaScript package manager, or application server.

Use Hugo **Extended 0.135.0**, matching both GitHub Actions and Netlify. A Go toolchain is also required because Hugo downloads the module dependencies during the first build; the module declares Go 1.15 as its minimum language version.

The site carries a substantial local presentation layer ("warm editorial" redesign) over the remote theme: modular SCSS, local template overrides, and progressive JavaScript. Theme source lives in the Go module cache (`$GOMODCACHE/github.com/!hugo!blox/...`), not in this repo — read the module templates there before writing overrides, and copy only what you need.

## Commands

### Restricted-network environments (optional)

Ensure Hugo Extended 0.135.0 and Go are available on `PATH`. Whether Hugo can download modules directly from GitHub depends on the local network and credentials. When an environment requires a Go module proxy or cache setting, use the organisation-approved values and preserve values already supplied by the caller. For example:

```bash
# Replace the placeholder only when local network policy requires a proxy.
export GOPROXY="${GOPROXY:-https://your-approved-go-module-proxy}"
export GOSUMDB="${GOSUMDB:-sum.golang.org}"
export GOMODCACHE="${GOMODCACHE:-$HOME/go/pkg/mod}"
```

Do not change a caller-provided proxy, checksum database, module cache, or `HUGO_BIN` setting merely to run this repository. On restricted networks, obtain the appropriate configuration from the environment owner rather than assuming a public proxy or GitHub relay is available.

```bash
# Local development server with drafts/future-dated content visible (watch + live reload)
hugo server --buildDrafts --buildFuture --bind 127.0.0.1 --port 1313

# Local production-style validation
hugo --gc --minify

# Match the GitHub Pages build (replace the URL if needed)
HUGO_ENVIRONMENT=production hugo --minify --baseURL "https://hpc.hzcu.edu.cn/"

# Match Netlify's production build
hugo --gc --minify -b "https://hpc.hzcu.edu.cn/"
```

Run the generated-site regression suite with:

```bash
./scripts/test-site.sh
```

Generated output is written to `public/` and Hugo's generated resources to `resources/`; both are ignored by Git.

There is no third-party test framework: `scripts/test-site.sh` runs the Python standard-library generated-site regression suite, building the site (plus a fixture copy) and checking key pages. Run one test with:

```bash
python3 -m unittest tests.test_generated_site.GeneratedSiteTests.test_homepage_hero_is_terminal -v
```

Treat a clean production-style Hugo build as the repository-wide validation step. For a focused content change, run the development server and inspect the affected route in addition to building the full site.

The optional publication-import workflow uses this command (normally run by GitHub Actions when `publications.bib` changes):

```bash
python -m pip install academic==0.10.0
academic import publications.bib content/publication/ --compact
```

## Architecture

### Content model

- `config/_default/hugo.yaml` is the core Hugo configuration: canonical URL, outputs, permalinks, taxonomies, image processing, and Markdown-related behavior.
- `config/_default/params.yaml` controls Hugo Blox presentation and features (theme, header/footer, search, CMS, citations). It also enables the local JS bundle via `plugins_js: [editorial, spotlight, terminal]` and sets `header.on_scroll: sticky` (which disables the theme's scroll-hiding headroom script). `menus.yaml` defines top-level navigation, `languages.yaml` defines the currently English-only language setup, and `module.yaml` imports the Hugo Blox theme/plugins.
- `content/` is the site's source of truth. Files use YAML front matter followed by Markdown; the site contains both Chinese and English content despite the single `en` language configuration.
- Most articles are Hugo page bundles: `content/<section>/<slug>/index.md` plus images in the same directory. Content sections use singular slugs: `post` (news), `daily` (diary), `recruitment`, `memory`, `publication`. Section-level `_index.md` files configure list pages. `content/admin/index.md` is the Decap CMS config page (`type: decap_cms`, `private: true`), driven by the `blox-plugin-decap-cms` module, with `static/uploads/` as its media target.
- Team profiles live at `content/authors/<slug>/_index.md`, with an adjacent `avatar.*`. The People block groups profiles by exact `user_groups` strings and sorts using profile parameters, so changes to group names must stay synchronized with `content/people/index.md`. Content `authors` values should refer to the appropriate author slug.
- Root-level `theme.toml`, `images/`, `preview.png`, and `content/tour/` (its nav entry is commented out in `menus.yaml`) are unreferenced leftovers from the Wowchemy starter template. `theme.toml` has no effect — the theme ships via Hugo modules.
- Shared site media belongs in `assets/media/`; bundle-specific media belongs beside its `index.md`. Files under `static/` are copied directly to the generated site.

### Landing pages and homepage sections

- `content/_index.md` (and `content/contact/index.md`, `content/people/index.md`) is a Hugo Blox landing page: an ordered `sections` array of `block: hero|collection|markdown|contact` entries composes the page. Each section may carry an explicit `id:` (e.g. `id: introduction`, `id: join-us`) — required when two blocks of the same type share a page, because the theme otherwise emits duplicate `id="section-<type>"` values.
- Collection blocks filter content with `filters` (page_type, category, tag, author, folders). **`filters.folders` matches the top-level Section only, not bundle subdirectories** — to show one specific bundle per collection block, tag the articles with a `categories:` front-matter value and filter on `filters.category`.
- The homepage hero is `block: hero-terminal` (`layouts/partials/blocks/hero-terminal.html` + `assets/scss/pages/_terminal-hero.scss` + `assets/js/terminal.js`): a dark terminal window that "types" a few HPC-flavoured commands whose output reveals the masthead. It needs no external images or fonts, and follows the same progressive-enhancement contract as `editorial.js` — all lines render visible by default, JS hides them only via a readiness class before typing, and `prefers-reduced-motion` skips the animation. The older `block: hero-spotlight` (cursor spotlight over two images) is still available as an alternative. The masthead ASCII art lives in the root-level `ascii` file (125-column "HZCU HPC TEAM", sub-zero figlet font), loaded via `readFile "ascii"` in the hero template — unlike `theme.toml` and `preview.png` it is load-bearing, not a leftover. `ascii-mobile` is the same text stacked into three ~43-column rows, swapped in below the `48rem` breakpoint by `_terminal-hero.scss`; both are asserted by the regression suite.
- The homepage splits recruitment content into two collections: `INTRODUCTION` (`category: introduction`, article `content/recruitment/recruitment2408/`) and `JOIN US` (`category: join-us`, article `content/recruitment/join-us/`). Article-level buttons to internal pages use the theme's `{{% cta cta_link="/path/" cta_text="..." %}}` shortcode.
- `content/accomplishments/index.md` (independent page) lists awards by year; `layouts/partials/editorial/listing.html` special-cases the `accomplishments` section by splitting rendered content on `<h2` boundaries and wrapping each year group in `<article class="editorial-accomplishment" data-reveal>`.

### Presentation layer

- `assets/scss/abstracts/_tokens.scss` is the design-token source of truth: warm palette (`--color-paper*`, `--color-ink`, `--color-clay*`, `--color-sage`), type scale (`--heading-hero/display/section-compact` for desktop), spacing, `--page-gutter` (page edge padding), `--content-max`/`--reading-max`. Desktop type/density convergence lives in `@media (min-width: 64rem)` blocks; base body text size is never reduced.
- `assets/scss/template.scss` imports the modular SCSS system in `assets/scss/` (base, components, pages). When mixing units inside `clamp()` in SCSS, wrap the middle argument in `calc()` (Dart Sass rejects `1.35rem + 1vw` without it); likewise avoid `min()`/`max()` with mixed units in plain property values — the Sass engine tries to evaluate them and fails with "Incompatible units".
- Local layouts and partials under `layouts/` override theme rendering: navigation header, landing-page block loop, listings (`editorial/listing.html`), article chrome (`_default/single.html`, `partials/page_header.html`), search dialog, share controls, the publication section, and the author profile widget. Copy the theme's template from the module cache as the baseline, then change only what the design requires; some overrides add accessible names (`aria-label`) or fix heading semantics (single `h1` per page, section headings demoted to `h2`).
- `assets/js/editorial.js` provides progressive enhancement only: sticky-header compact state (`.is-compact`) and `data-reveal` entrance animations via IntersectionObserver. Content is visible by default; hiding happens only after JS adds a readiness class, so no-JS and `prefers-reduced-motion` users see everything immediately. No hover motion is used on awards; interactive buttons use color + `transform: scale(1.05)` on hover/focus with transitions disabled under reduced motion.
- `assets/scss/base/_accessibility.scss` defines the global `:focus-visible` ring and reveal/reduced-motion contracts; navigation and interactive controls keep ≥44px touch targets.
- `docs/superpowers/` holds the dated design plans and specs behind the local redesign (warm editorial, desktop typography, homepage collections, spotlight hero) — read the relevant plan/spec for design intent before extending the presentation layer.

### Tests

- `tests/test_generated_site.py` builds the site and a fixture copy (with injected edge cases: SVG/GIF images, banners, gravatar, menus, long summaries) and asserts on generated HTML and compiled CSS. Several assertions intentionally scan the whitespace-stripped compiled CSS (`"".join(css.split())`) — selector strings there contain no spaces (e.g. `.home-section.cta-group.btn:hover`, `.editorial-article.page_headerh1`). Prefer asserting real generated DOM classes over guessing class names, and keep negative assertions (e.g. no hover-transform) alongside positive ones.
- `scripts/test-site.sh` wires the suite with the Hugo/Go environment (pins `GOPROXY=https://goproxy.cn`, `GOSUMDB=off`, `GOMODCACHE=$HOME/go/pkg/mod`; honors a caller-provided `HUGO_BIN`). On Windows, run it through Git Bash as `bash scripts/test-site.sh` if the exec bit was lost on checkout. The suite currently has 84 tests covering structure, accessibility, responsive images, animation contracts, and content preservation.

## Deployment

A push to `main` triggers `.github/workflows/publish.yaml`, builds with Hugo Extended 0.135.0, uploads `public/`, and deploys GitHub Pages. `netlify.toml` defines an alternative Netlify build with the same Hugo version. `.github/workflows/import-publications.yml` watches a root-level `publications.bib`, converts it into page bundles under `content/publication/`, and opens an automated pull request rather than deploying directly.
