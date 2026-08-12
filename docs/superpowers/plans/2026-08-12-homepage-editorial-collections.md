# Homepage Editorial Collections Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the homepage INTRODUCTION and JOIN US collection cards with accessible editorial split layouts whose article titles sit at the upper left and whose structured previews fill the right column.

**Architecture:** Keep Hugo Blox collection querying and add one explicitly selected local view, `homepage-preview`, so this homepage-only structure cannot affect the shared editorial list view. Each recruitment page owns a Markdown `homepage_preview` front-matter field; the view renders and demotes its headings, applies safe summary fallbacks, and exposes dedicated BEM classes styled only in the homepage SCSS.

**Tech Stack:** Hugo Extended 0.135.0, Hugo Blox Bootstrap v5 module, Go templates, YAML front matter, Markdown/Goldmark, SCSS, Python 3 `unittest` generated-site regression tests.

---

## Preconditions and file map

Implement this plan from an isolated feature worktree or feature branch, not directly on `main`. At execution time, use `superpowers:using-git-worktrees` before `superpowers:subagent-driven-development`, or let the selected execution workflow establish the isolated workspace.

The repository already has Hugo Extended 0.135.0 at `$HOME/.local/bin/hugo`; `scripts/test-site.sh` prepends that directory to `PATH`. Preserve any caller-provided `HUGO_BIN`, Go proxy, checksum database, and module cache settings when running commands outside the repository script.

### Files to modify

- `tests/test_generated_site.py`
  - Create fixture-only homepage entries for summary and empty-preview fallbacks.
  - Replace obsolete concise-summary expectations with the new structured-view contract.
  - Assert heading hierarchy, links, image exclusion, multiple-item behavior, fallback behavior, CSS, responsive behavior, and isolation from generic editorial lists.
- `content/_index.md`
  - Keep the existing collection IDs and filters.
  - Move `INTRODUCTION` and `JOIN US` from `content.title` to `content.eyebrow`.
  - Select `design.view: homepage-preview` for both collections.
- `content/recruitment/recruitment2408/index.md`
  - Add the structured Introduction homepage preview without changing article body content.
- `content/recruitment/join-us/index.md`
  - Add the structured Join Us homepage preview without changing article body content.
- `layouts/partials/views/homepage-preview.html` (new)
  - Render the isolated homepage article structure, heading demotion, external-link attributes, fallback summaries, first-item eyebrow, and text-only modifier.
- `assets/scss/pages/_home.scss`
  - Replace the obsolete `#section-collection .editorial-entry:first-child` rule with scoped desktop/mobile styles for `.homepage-preview`.

### Files intentionally unchanged

- `layouts/partials/views/editorial.html`: generic Post, Diary, Recruitment, and Memory list entries remain unchanged.
- `layouts/partials/blocks/collection-config.html`: collection headings are suppressed by leaving `content.title` empty; no global collection behavior needs changing.
- `layouts/partials/landing_page.html`: the new view emits its own `<h2>`/`<h3>` hierarchy and does not depend on the theme heading rewrite.
- `assets/js/editorial.js`: the existing `[data-reveal]` progressive enhancement already supports the new `<article>`.
- Article body Markdown below front matter: homepage preview content is additive and must not rewrite full article content.

---

### Task 1: Define the generated-HTML contract with failing tests

**Files:**
- Modify: `tests/test_generated_site.py:48-223`
- Modify: `tests/test_generated_site.py:535-565`
- Modify: `tests/test_generated_site.py:609-624`
- Modify: `tests/test_generated_site.py:842-853`
- Modify: `tests/test_generated_site.py:894-905`
- Modify: `tests/test_generated_site.py:996-1014`

- [ ] **Step 1: Add fixture pages for fallback and multiple-item behavior**

Immediately after the existing `fixture_recruitment.write_text(...)` call in `GeneratedSiteTests.setUpClass`, create two fixture-only Introduction entries. The first has an explicit summary but no `homepage_preview`; the second has neither a preview nor body content:

```python
        fallback_preview_dir = fixture / "content/recruitment/homepage-preview-fallback"
        fallback_preview_dir.mkdir(parents=True)
        (fallback_preview_dir / "index.md").write_text(
            """---
title: Fixture homepage fallback preview
date: 2025-09-03
categories:
  - introduction
summary: Fixture homepage fallback summary.
---
""",
            encoding="utf-8",
        )
        empty_preview_dir = fixture / "content/recruitment/homepage-preview-empty"
        empty_preview_dir.mkdir(parents=True)
        (empty_preview_dir / "index.md").write_text(
            """---
title: Fixture homepage empty preview
date: 2025-09-02
categories:
  - introduction
---
""",
            encoding="utf-8",
        )
```

These dates sort both fixture entries ahead of the existing `2025-09-01` Introduction article while remaining non-future content. The existing collection count of five includes all three entries.

- [ ] **Step 2: Retain the generated fixture homepage for assertions**

Immediately after `cls.fixture_article` is assigned, add:

```python
        cls.fixture_homepage = (cls.fixture_output / "index.html").read_text(encoding="utf-8")
```

Then add this helper below `compiled_css`:

```python
    def homepage_section(self, section_id, fixture=False):
        homepage = self.fixture_homepage if fixture else self.homepage
        return homepage.split(f'id="{section_id}"', 1)[1].split("</section>", 1)[0]
```

The helper intentionally returns the section contents after the opening tag; all tests only need the section-local generated markup.

- [ ] **Step 3: Replace the obsolete concise-summary test with the structured-view test**

Replace `test_homepage_recruitment_summary_is_a_concise_safe_excerpt` with:

```python
    def test_homepage_collections_use_structured_preview_view(self):
        cases = (
            (
                "introduction",
                "INTRODUCTION",
                "浙大城市学院超算队介绍",
                "/recruitment/recruitment2408/",
                ("我们是谁？", "我们参加的比赛", "我们能提供什么？"),
            ),
            (
                "join-us",
                "JOIN US",
                "2025年超算队招新",
                "/recruitment/join-us/",
                ("招新条件", "报名及联系方式", "1004145044"),
            ),
        )

        for section_id, eyebrow, title, href, preview_strings in cases:
            with self.subTest(section_id=section_id):
                section = self.homepage_section(section_id)
                self.assertNotIn('class="section-heading', section)
                self.assertIn(
                    'class="homepage-preview homepage-preview--first" data-reveal',
                    section,
                )
                self.assertRegex(
                    section,
                    rf'<h2 class="homepage-preview__eyebrow">\s*{re.escape(eyebrow)}\s*</h2>',
                )
                self.assertRegex(
                    section,
                    rf'<h3 class="homepage-preview__title">\s*<a href="{re.escape(href)}"[^>]*>{re.escape(title)}</a>\s*</h3>',
                )
                self.assertRegex(
                    section,
                    rf'<a class="homepage-preview__read" href="{re.escape(href)}"[^>]*>\s*阅读全文 →\s*</a>',
                )
                preview = section.split('class="homepage-preview__content article-style"', 1)[1]
                preview = preview.split("</article>", 1)[0]
                self.assertIn("<h4", preview)
                self.assertNotIn("<h3", preview)
                for expected in preview_strings:
                    self.assertIn(expected, preview)
                self.assertIn("<p", preview)
                self.assertIn("<ul", preview)
                self.assertNotIn("<img", section)
                self.assertNotIn("editorial-entry__media", section)
```

This is expected to fail against the current card/editorial markup because `.homepage-preview` does not exist yet.

- [ ] **Step 4: Add fallback, multi-item, and external-link tests**

Add these methods immediately after the structured-view test:

```python
    def test_homepage_preview_falls_back_and_omits_empty_content(self):
        section = self.homepage_section("introduction", fixture=True)
        articles = re.findall(
            r'<article class="[^"]*\bhomepage-preview\b[^"]*"[^>]*>[\s\S]*?</article>',
            section,
        )

        self.assertEqual(len(articles), 3)
        self.assertEqual(section.count('class="homepage-preview__eyebrow"'), 1)
        self.assertIn("homepage-preview--first", articles[0].split(">", 1)[0])

        fallback = next(
            article for article in articles if "Fixture homepage fallback preview" in article
        )
        self.assertIn("Fixture homepage fallback summary.", fallback)
        self.assertIn('class="homepage-preview__content article-style"', fallback)

        empty = next(
            article for article in articles if "Fixture homepage empty preview" in article
        )
        self.assertIn("homepage-preview--text-only", empty.split(">", 1)[0])
        self.assertNotIn("homepage-preview__content", empty)

        external = next(article for article in articles if "浙大城市学院超算队介绍" in article)
        external_links = re.findall(
            r'<a[^>]+href="https://example.com/recruitment"[^>]*>',
            external,
        )
        self.assertEqual(len(external_links), 2)
        for link in external_links:
            self.assertIn('target="_blank"', link)
            self.assertIn('rel="noopener"', link)

    def test_homepage_preview_heading_hierarchy_and_view_isolation(self):
        self.assertEqual(self.homepage.count("<h1"), 1)
        self.assertEqual(self.homepage.count('id="introduction"'), 1)
        self.assertEqual(self.homepage.count('id="join-us"'), 1)
        self.assertEqual(self.homepage.count('class="homepage-preview__eyebrow"'), 2)
        self.assertEqual(self.homepage.count('class="homepage-preview__title"'), 2)
        for section_id in ("introduction", "join-us"):
            with self.subTest(section_id=section_id):
                section = self.homepage_section(section_id)
                self.assertLess(section.index("homepage-preview__eyebrow"), section.index("homepage-preview__title"))
                self.assertLess(section.index("homepage-preview__title"), section.index("homepage-preview__read"))
                self.assertLess(section.index("homepage-preview__read"), section.index("homepage-preview__content"))
        self.assertNotIn("homepage-preview", (self.output / "recruitment/index.html").read_text(encoding="utf-8"))

        for route in ("post", "daily", "recruitment", "memory"):
            with self.subTest(route=route):
                page = (self.output / route / "index.html").read_text(encoding="utf-8")
                self.assertIn('class="editorial-entry', page)
```

The final assertion explicitly protects the generic view rather than relying only on source-file inspection.

- [ ] **Step 5: Update existing homepage DOM assertions that describe the old view**

In `test_home_section_headings_are_h2_but_hero_remains_h1`, replace the method body with:

```python
        home = self.homepage
        self.assertEqual(home.count("<h1"), 1)
        for section_id, eyebrow in (("introduction", "INTRODUCTION"), ("join-us", "JOIN US")):
            with self.subTest(section_id=section_id):
                section = self.homepage_section(section_id)
                self.assertRegex(
                    section,
                    rf'<h2 class="homepage-preview__eyebrow">\s*{eyebrow}\s*</h2>',
                )
                self.assertIn('<h3 class="homepage-preview__title">', section)
        styles = (REPO_ROOT / "assets/scss/pages/_home.scss").read_text(encoding="utf-8")
        self.assertNotIn(".home-section .section-heading h1", styles)
```

In `test_task8_style_selectors_match_generated_home_contact_and_publication_dom`, replace the Introduction and Join Us assertions with:

```python
        collection = self.homepage_section("introduction")
        self.assertNotIn('class="section-heading', collection)
        self.assertRegex(collection, r'<article class="[^"]*homepage-preview')
        self.assertIn('<h2 class="homepage-preview__eyebrow">', collection)
        join_us = self.homepage_section("join-us")
        self.assertNotIn('class="section-heading', join_us)
        self.assertRegex(join_us, r'<article class="[^"]*homepage-preview')
        self.assertIn('<h2 class="homepage-preview__eyebrow">', join_us)
```

Keep `test_homepage_splits_introduction_and_join_us_articles`; it still verifies the high-level content split and article detail pages.

- [ ] **Step 6: Run the focused HTML-contract tests and verify RED**

Run:

```bash
python3 -m unittest \
  tests.test_generated_site.GeneratedSiteTests.test_homepage_collections_use_structured_preview_view \
  tests.test_generated_site.GeneratedSiteTests.test_homepage_preview_falls_back_and_omits_empty_content \
  tests.test_generated_site.GeneratedSiteTests.test_homepage_preview_heading_hierarchy_and_view_isolation \
  tests.test_generated_site.GeneratedSiteTests.test_home_section_headings_are_h2_but_hero_remains_h1 \
  tests.test_generated_site.GeneratedSiteTests.test_task8_style_selectors_match_generated_home_contact_and_publication_dom \
  -v
```

Expected: FAIL after the fixture and main Hugo builds complete. Failures should report missing `homepage-preview` markup or missing `.homepage-preview__eyebrow`; there must be no Python syntax error and no fixture-build error.

- [ ] **Step 7: Commit the failing contract tests**

```bash
git add tests/test_generated_site.py
git commit -m "test: define homepage preview layout contract"
```

Expected: one commit containing only the generated-site test and fixture changes.

---

### Task 2: Add structured preview content and the isolated Hugo view

**Files:**
- Modify: `content/_index.md:18-56`
- Modify: `content/recruitment/recruitment2408/index.md:1-8`
- Modify: `content/recruitment/join-us/index.md:1-8`
- Create: `layouts/partials/views/homepage-preview.html`
- Test: `tests/test_generated_site.py`

- [ ] **Step 1: Configure both homepage collections to select the dedicated view**

In `content/_index.md`, change the Introduction block from `title: INTRODUCTION` to an empty theme title plus the dedicated eyebrow, and change its view:

```yaml
  - block: collection
    content:
      title:
      eyebrow: INTRODUCTION
      subtitle:
      text:
      count: 5
      filters:
        author: ''
        category: introduction
        exclude_featured: false
        publication_type: ''
        tag: ''
      offset: 0
      order: desc
      page_type: recruitment
    design:
      view: homepage-preview
      columns: '1'
    id: introduction
```

Apply the same change to Join Us:

```yaml
  - block: collection
    content:
      title:
      eyebrow: JOIN US
      subtitle:
      text:
      count: 5
      filters:
        author: ''
        category: join-us
        exclude_featured: false
        publication_type: ''
        tag: ''
      offset: 0
      order: desc
      page_type: recruitment
    design:
      view: homepage-preview
      columns: '1'
    id: join-us
```

Do not change either `id`, category, count, order, page type, or column count.

- [ ] **Step 2: Add the Introduction structured preview to front matter**

In `content/recruitment/recruitment2408/index.md`, insert `homepage_preview` after `categories` and before `image`:

```yaml
homepage_preview: |
  ### 我们是谁？

  浙大城市学院超算队是计算学院、浙大城市学院超算中心下属的高性能计算队伍。浙大城市学院超算中心是全省公办高校首个校级超算中心。我们热衷于计算、测量、软件在不同系统环境下的性能评估以及性能优化。

  ### 我们参加的比赛

  - **ASC世界大学生超级计算机竞赛**：全球规模最大的大学生超算竞赛，旨在推动青年人才交流和培养，提升超算应用水平。
  - **IPCC国际并行计算挑战赛**：通过解决实际计算问题，提升并行计算和高性能计算领域的技能与知识。
  - **CPC国产CPU并行应用挑战赛**：专注于国产超算平台的专业赛事。

  ### 我们能提供什么？

  - **顶级的计算资源**：提供日常训练和比赛所需的高性能服务器，并有体验校内 A800 显卡集群的机会。
  - **个人发展优势**：通过高性能计算领域的实践项目积累经验。
  - **团队协作经验**：在专属实验室中参加周常组会、知识分享、竞赛培训和课程学习。
```

Leave every line after the closing front-matter delimiter unchanged.

- [ ] **Step 3: Add the Join Us structured preview to front matter**

In `content/recruitment/join-us/index.md`, insert this field after `categories` and before `image`:

```yaml
homepage_preview: |
  ### 招新条件

  - 浙大城市学院大一至大三本科生，专业不限，对高性能计算、计算机体系结构、并行计算或异构计算有浓厚兴趣。
  - 有较强的自驱力，并具备一定的英文文档阅读能力。
  - 掌握或了解至少一种编程语言，熟悉基本的数据结构与算法知识。
  - 学有余力，成绩位于前 60%。
  - 了解 Linux、GitHub 工作流、计算机竞赛或并行框架者优先。

  ### 报名及联系方式

  请先加入招新群：**QQ 联系群 1004145044**。高年级同学和具有丰富经验的新生可将简历发送至 `hur@hzcu.edu.cn`；其他 2025 级新生可填写招新调查表。报名截止时间为 2025 年 10 月 10 日 23:59（UTC+8）。
```

Again, do not alter the full article body.

- [ ] **Step 4: Create the dedicated homepage preview view**

Create `layouts/partials/views/homepage-preview.html` with this complete template:

```go-html-template
{{- $block := .page -}}
{{- $item := .item -}}
{{- $index := .index -}}
{{- $link := $item.RelPermalink -}}
{{- $target := "" -}}
{{- if $item.Params.external_link -}}
  {{- $link = $item.Params.external_link -}}
  {{- $target = `target="_blank" rel="noopener"` -}}
{{- end -}}

{{- $preview := "" -}}
{{- with $item.Params.homepage_preview -}}
  {{- $preview = $item.RenderString . -}}
  {{- $preview = replaceRE `<h3([^>]*)>` `<h4$1>` $preview -}}
  {{- $preview = replaceRE `</h3>` `</h4>` $preview -}}
{{- else with $item.Params.summary -}}
  {{- $summary := . | plainify | htmlUnescape | strings.TrimSpace -}}
  {{- with $summary -}}
    {{- $preview = printf "<p>%s</p>" (. | transform.HTMLEscape) -}}
  {{- end -}}
{{- else with $item.Summary -}}
  {{- $summary := . | plainify | htmlUnescape | strings.TrimSpace -}}
  {{- with $summary -}}
    {{- $preview = printf "<p>%s</p>" (. | transform.HTMLEscape) -}}
  {{- end -}}
{{- end -}}

{{- $classes := slice "homepage-preview" -}}
{{- if eq $index 0 -}}
  {{- $classes = $classes | append "homepage-preview--first" -}}
{{- end -}}
{{- if not $preview -}}
  {{- $classes = $classes | append "homepage-preview--text-only" -}}
{{- end -}}

<article class="{{ delimit $classes " " }}" data-reveal>
  <header class="homepage-preview__header">
    {{- if eq $index 0 -}}
      {{- with $block.content.eyebrow -}}
        <h2 class="homepage-preview__eyebrow">{{ . | plainify }}</h2>
      {{- end -}}
    {{- end -}}
    <h3 class="homepage-preview__title"><a href="{{ $link }}" {{ $target | safeHTMLAttr }}>{{ $item.Title }}</a></h3>
    <a class="homepage-preview__read" href="{{ $link }}" {{ $target | safeHTMLAttr }}>阅读全文 →</a>
  </header>
  {{- with $preview }}
    <div class="homepage-preview__content article-style">{{ . | safeHTML }}</div>
  {{- end }}
</article>
```

Important details:

- `.page` is the collection block because Hugo Blox's `render_view.html` passes the block as `page`; do not call page methods on `$block`.
- `$item.RenderString` is the page-aware Markdown renderer and preserves local Markdown behavior.
- The two `replaceRE` calls only demote preview `<h3>` elements to `<h4>`; they do not touch the article-title `<h3>` because that title is emitted after preview rendering.
- Summary fallbacks are plainified, trimmed, escaped, and wrapped in one paragraph. They cannot inject raw HTML.
- No featured-image partial is called.

- [ ] **Step 5: Run the focused HTML-contract tests and verify GREEN**

Run the same command from Task 1 Step 6:

```bash
python3 -m unittest \
  tests.test_generated_site.GeneratedSiteTests.test_homepage_collections_use_structured_preview_view \
  tests.test_generated_site.GeneratedSiteTests.test_homepage_preview_falls_back_and_omits_empty_content \
  tests.test_generated_site.GeneratedSiteTests.test_homepage_preview_heading_hierarchy_and_view_isolation \
  tests.test_generated_site.GeneratedSiteTests.test_home_section_headings_are_h2_but_hero_remains_h1 \
  tests.test_generated_site.GeneratedSiteTests.test_task8_style_selectors_match_generated_home_contact_and_publication_dom \
  -v
```

Expected: all five tests PASS. If Hugo reports a template error, fix the template rather than weakening the assertions. The fixture Introduction section must contain exactly three `.homepage-preview` articles and one eyebrow.

- [ ] **Step 6: Run existing content split and external-link regressions**

```bash
python3 -m unittest \
  tests.test_generated_site.GeneratedSiteTests.test_homepage_splits_introduction_and_join_us_articles \
  tests.test_generated_site.GeneratedSiteTests.test_editorial_entries_keep_external_link_security_and_metadata \
  tests.test_generated_site.GeneratedSiteTests.test_editorial_sections_use_unified_index_and_entry_views \
  -v
```

Expected: all three tests PASS. This confirms that full article pages, generic Recruitment list metadata, and generic Editorial Views remain intact.

- [ ] **Step 7: Confirm article bodies were not rewritten**

Run:

```bash
git diff --word-diff=plain -- content/recruitment/recruitment2408/index.md content/recruitment/join-us/index.md
```

Expected: only `homepage_preview` front-matter additions appear; the Markdown after each second `---` delimiter has no deletion or replacement.

- [ ] **Step 8: Commit the content model and view**

```bash
git add \
  content/_index.md \
  content/recruitment/recruitment2408/index.md \
  content/recruitment/join-us/index.md \
  layouts/partials/views/homepage-preview.html
git commit -m "feat: add structured homepage collection previews"
```

Expected: one commit containing the homepage configuration, two additive preview fields, and the new isolated view.

---

### Task 3: Add the split-layout CSS contract and implementation

**Files:**
- Modify: `tests/test_generated_site.py:584-599`
- Modify: `tests/test_generated_site.py:996-1014`
- Modify: `assets/scss/pages/_home.scss:88-92`

- [ ] **Step 1: Add a failing compiled-CSS contract test**

Add this method near the other homepage CSS tests:

```python
    def test_homepage_preview_split_layout_css_contract(self):
        css = "".join(self.compiled_css().split())

        layout = re.search(r"\.homepage-preview\{([^}]*)\}", css)
        self.assertIsNotNone(layout, "homepage preview layout rule missing")
        self.assertIn("display:grid", layout.group(1))
        self.assertRegex(
            layout.group(1),
            r"grid-template-columns:minmax\(0,0?\.75fr\)minmax\(0,1\.25fr\)",
        )
        self.assertIn("border-top:3pxsolidvar(--color-clay)", layout.group(1))

        content = re.search(r"\.homepage-preview__content\{([^}]*)\}", css)
        self.assertIsNotNone(content, "homepage preview content rule missing")
        self.assertIn("border-left:1pxsolidvar(--color-line)", content.group(1))
        self.assertRegex(content.group(1), r"padding-left:clamp\(")

        read_link = re.search(r"\.homepage-preview__read\{([^}]*)\}", css)
        self.assertIsNotNone(read_link, "homepage preview read-link rule missing")
        self.assertIn("min-height:44px", read_link.group(1))

        mobile = re.search(
            r"@media\(max-width:47\.99rem\)\{[\s\S]*?\.homepage-preview\{([^}]*)\}",
            css,
        )
        self.assertIsNotNone(mobile, "homepage preview mobile layout rule missing")
        self.assertIn("grid-template-columns:1fr", mobile.group(1))

        mobile_content = re.search(
            r"@media\(max-width:47\.99rem\)\{[\s\S]*?\.homepage-preview__content\{([^}]*)\}",
            css,
        )
        self.assertIsNotNone(mobile_content, "homepage preview mobile content rule missing")
        self.assertIn("border-top:1pxsolidvar(--color-line)", mobile_content.group(1))
        self.assertIn("border-left:0", mobile_content.group(1))
        self.assertIn("padding-left:0", mobile_content.group(1))

        self.assertNotRegex(
            css,
            r"\.homepage-preview[^{}]*:hover[^{}]*\{[^}]*transform:",
        )
        self.assertNotIn("#section-collection.editorial-entry:first-child", css)

        home_styles = (REPO_ROOT / "assets/scss/pages/_home.scss").read_text(encoding="utf-8")
        self.assertIn(".homepage-preview__eyebrow", home_styles)
```

The negative assertions use whitespace-normalized CSS and prevent the dead generic-home selector from returning; the final source assertion ties the eyebrow token to the homepage SCSS.

- [ ] **Step 2: Run the CSS contract test and verify RED**

```bash
python3 -m unittest \
  tests.test_generated_site.GeneratedSiteTests.test_homepage_preview_split_layout_css_contract \
  -v
```

Expected: FAIL with `homepage preview layout rule missing`. The Hugo build itself must succeed.

- [ ] **Step 3: Replace the obsolete first-card rule with scoped homepage preview styles**

In `assets/scss/pages/_home.scss`, remove:

```scss
#section-collection .editorial-entry:first-child {
  border-top-color: var(--color-clay);
  border-top-width: 3px;
  padding-top: clamp(2rem, 5vw, 4rem);
}
```

Insert this complete block in the same location, before `.home-section .cta-group`:

```scss
.homepage-preview {
  display: grid;
  grid-template-columns: minmax(0, 0.75fr) minmax(0, 1.25fr);
  gap: 0;
  align-items: start;
  padding-block: clamp(2rem, 5vw, 4rem);
  border-top: 3px solid var(--color-clay);

  & + & {
    margin-top: var(--space-6);
  }

  &--text-only {
    grid-template-columns: minmax(0, 48rem);
  }

  &__header {
    min-width: 0;
    padding-right: clamp(1.5rem, 4vw, 4rem);
  }

  &__eyebrow {
    margin: 0 0 var(--space-6);
    color: var(--color-clay-dark);
    font-family: var(--font-body);
    font-size: var(--text-xs);
    font-weight: 700;
    letter-spacing: 0.16em;
    line-height: 1.2;
    text-transform: uppercase;
  }

  &__title {
    max-width: 13ch;
    margin: 0;
    font-family: var(--font-display);
    font-size: clamp(1.75rem, calc(1.35rem + 1.35vw), 3.25rem);
    letter-spacing: -0.025em;
    line-height: 1.08;

    a {
      color: var(--color-ink);
      text-decoration: none;
      transition: color 180ms ease;
    }

    a:hover,
    a:focus-visible {
      color: var(--color-clay-dark);
    }
  }

  &__read {
    display: inline-flex;
    align-items: center;
    min-height: 44px;
    margin-top: var(--space-5);
    color: var(--color-clay-dark);
    font-weight: 700;
    text-decoration: underline;
    text-decoration-thickness: 1px;
    text-underline-offset: 0.2em;
    transition: color 180ms ease;
  }

  &__read:hover,
  &__read:focus-visible {
    color: var(--color-ink);
  }

  &__content {
    min-width: 0;
    padding-left: clamp(1.5rem, 4vw, 4rem);
    border-left: 1px solid var(--color-line);
    color: var(--color-muted);

    > :first-child {
      margin-top: 0;
    }

    > :last-child {
      margin-bottom: 0;
    }

    h4 {
      max-width: 24ch;
      margin: var(--space-6) 0 var(--space-3);
      color: var(--color-ink);
      font-family: var(--font-display);
      font-size: clamp(1.25rem, calc(1.1rem + 0.45vw), 1.75rem);
      line-height: 1.2;
    }

    h4:first-child {
      margin-top: 0;
    }

    p,
    li {
      max-width: 65ch;
      font-size: 1rem;
      line-height: 1.7;
    }

    ul,
    ol {
      margin-bottom: var(--space-5);
      padding-left: 1.25rem;
    }

    a {
      color: var(--color-clay-dark);
      text-decoration: underline;
      text-decoration-thickness: 1px;
      text-underline-offset: 0.2em;
    }
  }
}
```

This keeps all layout behavior in the new namespace and introduces no image styles, fixed heights, overflow containers, shadows, or rounded card surfaces.

- [ ] **Step 4: Add the mobile single-column rules**

Inside the existing `@media (max-width: 47.99rem)` block, after the `.home-section .section-heading h2` rule, add:

```scss
  .homepage-preview {
    grid-template-columns: 1fr;

    &--text-only {
      grid-template-columns: 1fr;
    }

    &__header {
      padding-right: 0;
    }

    &__eyebrow {
      margin-bottom: var(--space-5);
    }

    &__content {
      margin-top: var(--space-5);
      padding-top: var(--space-5);
      padding-left: 0;
      border-top: 1px solid var(--color-line);
      border-left: 0;
    }
  }
```

Do not use `order`, absolute positioning, truncation, `max-height`, or `overflow`; DOM and visual order must remain identical.

- [ ] **Step 5: Align the warm-rhythm selector expectation**

In `test_warm_editorial_rhythm_styles_compile_for_home_and_lists`, replace this tuple item:

```python
            "#section-collection .editorial-entry:first-child",
```

with:

```python
            ".homepage-preview",
```

The dead generic-home selector is gone; the new scoped selector must be asserted in its place.

- [ ] **Step 6: Run the CSS and warm-rhythm tests and verify GREEN**

```bash
python3 -m unittest \
  tests.test_generated_site.GeneratedSiteTests.test_homepage_preview_split_layout_css_contract \
  tests.test_generated_site.GeneratedSiteTests.test_warm_editorial_rhythm_styles_compile_for_home_and_lists \
  tests.test_generated_site.GeneratedSiteTests.test_home_and_contact_section_containers_keep_content_away_from_edges \
  -v
```

Expected: all three tests PASS. If Hugo minification emits `.75fr`, the supplied regex accepts it; do not weaken the test to omit the actual column contract.

- [ ] **Step 7: Run accessibility and reveal regressions**

```bash
python3 -m unittest \
  tests.test_generated_site.GeneratedSiteTests.test_homepage_preview_heading_hierarchy_and_view_isolation \
  tests.test_generated_site.GeneratedSiteTests.test_key_pages_have_exactly_one_primary_heading \
  tests.test_generated_site.GeneratedSiteTests.test_editorial_motion_progressively_enhances_visible_content \
  -v
```

Expected: all three tests PASS; no JavaScript change should be required.

- [ ] **Step 8: Check SCSS and diff formatting**

```bash
git diff --check
git diff -- assets/scss/pages/_home.scss tests/test_generated_site.py
```

Expected: no whitespace errors. The SCSS diff removes the old `#section-collection` rule and adds only `.homepage-preview`-scoped rules plus the mobile block.

- [ ] **Step 9: Commit the responsive presentation**

```bash
git add assets/scss/pages/_home.scss tests/test_generated_site.py
git commit -m "style: add homepage preview split layout"
```

Expected: one commit containing the compiled-CSS test and scoped SCSS implementation.

---

### Task 4: Run complete verification and inspect the rendered homepage

**Files:**
- Verify: all files changed in Tasks 1-3
- Generated only: `public/`, `resources/` (both ignored; do not commit)

- [ ] **Step 1: Run the complete generated-site regression suite**

```bash
./scripts/test-site.sh
```

Expected: all tests PASS, including both normal and fixture Hugo builds. The command must finish with `OK`, zero failures, and zero errors; do not treat the test count as fixed.

If a test fails, invoke `superpowers:systematic-debugging` before changing implementation. Do not delete existing assertions merely to obtain a green suite.

- [ ] **Step 2: Run the production-style Hugo build with the required version**

```bash
HUGO_BIN="${HUGO_BIN:-$HOME/.local/bin/hugo}"
"$HUGO_BIN" version
"$HUGO_BIN" --gc --minify
```

Expected version output contains both `v0.135.0` and `extended`; the build exits 0 without template, Markdown, or resource-pipeline errors.

- [ ] **Step 3: Inspect generated homepage structure directly**

Run this standard-library inspection against `public/index.html`:

```bash
python3 - <<'PY'
from pathlib import Path
import re

home = Path("public/index.html").read_text(encoding="utf-8")
assert home.count("<h1") == 1
for section_id, eyebrow, title in (
    ("introduction", "INTRODUCTION", "浙大城市学院超算队介绍"),
    ("join-us", "JOIN US", "2025年超算队招新"),
):
    section = home.split(f'id="{section_id}"', 1)[1].split("</section>", 1)[0]
    assert eyebrow in section
    assert title in section
    assert 'class="homepage-preview homepage-preview--first"' in section
    assert 'class="homepage-preview__content article-style"' in section
    assert "<h4" in section
    assert "<img" not in section
    assert not re.search(r'class="section-heading', section)
print("homepage preview structure: OK")
PY
```

Expected output:

```text
homepage preview structure: OK
```

- [ ] **Step 4: Run the development server and inspect the affected route**

Start the repository server using the same Hugo binary:

```bash
HUGO_BIN="${HUGO_BIN:-$HOME/.local/bin/hugo}"
"$HUGO_BIN" server --buildDrafts --buildFuture --bind 127.0.0.1 --port 1313
```

Expected: Hugo prints a successful build and serves `http://127.0.0.1:1313/`. Inspect the homepage at desktop and mobile widths and confirm:

- INTRODUCTION and JOIN US each show the eyebrow and article title at the upper left.
- Structured headings, paragraphs, and lists occupy the right column.
- Neither module displays a featured image.
- At widths below 47.99rem, title content precedes preview content in one column.
- Links are keyboard focusable, “阅读全文 →” has a comfortable touch target, and no hover interaction shifts layout.
- With JavaScript disabled, both modules remain visible.
- With reduced motion enabled, reveal movement is absent.

Stop the server with `Ctrl-C` after inspection. Do not commit generated `public/` or `resources/` output.

- [ ] **Step 5: Verify repository scope and commit history**

```bash
git status --short
git diff --check
git log --oneline -4
```

Expected:

- No tracked implementation changes remain uncommitted.
- `git diff --check` prints nothing.
- The recent history includes:
  - `test: define homepage preview layout contract`
  - `feat: add structured homepage collection previews`
  - `style: add homepage preview split layout`
- No commit changes `layouts/partials/views/editorial.html`, `assets/js/editorial.js`, or article body content.

If verification required a legitimate fix, commit that fix separately with a precise message and rerun Steps 1-3 before completing the task.

- [ ] **Step 6: Request code review before integration**

Invoke `superpowers:requesting-code-review` against the complete feature branch diff. The review should specifically verify:

- Hugo template safety and heading demotion.
- Front-matter content remains faithful to each article.
- External-link attributes are present on both title and read links.
- Generic Editorial Views remain isolated.
- Desktop/mobile CSS matches the approved design.
- Generated-site tests cover structured, summary-fallback, and empty-preview paths.

Address confirmed findings using `superpowers:receiving-code-review`, rerun the complete suite and production build, and only then use `superpowers:finishing-a-development-branch` to choose merge, PR, or cleanup.
