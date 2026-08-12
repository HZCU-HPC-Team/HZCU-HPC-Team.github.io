import base64
import os
import re
import shutil
from html.parser import HTMLParser
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_ROUTES = ("/", "/people/", "/post/", "/daily/", "/recruitment/", "/memory/", "/accomplishments/", "/contact/")
AUTHOR_ROUTE = "/author/sizhe-qiao-乔思喆/"
REQUIRED_HOME_STRINGS = (
    "HZCU HPC Team",
    "浙大城市学院高性能计算",
    "INTRODUCTION",
    "Meet the team",
)
SVG_HERO = b'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 8"><rect width="12" height="8" fill="#b95232"/></svg>'''
ANIMATED_GIF_HERO = base64.b64decode(
    "R0lGODlhAQABAIAAAAAAAP///yH/C05FVFNDQVBFMi4wAwEAAAAh+QQACAAAACwAAAAAAQABAAACAkQBADs="
)


class TagInspector(HTMLParser):
    """Collect start tags and attributes from generated HTML."""

    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def find_all(self, tag):
        return [attrs for candidate, attrs in self.tags if candidate == tag]

    def find_all_with_class(self, tag, class_name):
        return [
            attrs
            for attrs in self.find_all(tag)
            if class_name in attrs.get("class", "").split()
        ]


class GeneratedSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.destination = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.destination.cleanup)
        cls.fixture_root = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.fixture_root.cleanup)
        fixture = Path(cls.fixture_root.name) / "site"
        shutil.copytree(REPO_ROOT, fixture, ignore=shutil.ignore_patterns(".git", "public", "resources", ".hugo_build.lock"))
        cls.fixture_menus = fixture / "config/_default/menus.yaml"
        fixture_params = fixture / "config/_default/params.yaml"
        fixture_params.write_text(fixture_params.read_text(encoding="utf-8").replace("gravatar: false", "gravatar: true"), encoding="utf-8")
        cls.fixture_menus.write_text(
            cls.fixture_menus.read_text(encoding="utf-8")
            + """
  - name: Resources
    identifier: resources
    url: resources
    weight: 80
  - name: Exact child
    parent: resources
    url: post/2025-06-03-ASC2024-prize/
    weight: 10
  - name: Descendant child
    parent: resources
    url: post
    weight: 20
  - name: Empty child
    parent: resources
    url: ""
    weight: 30
  - name: External child
    parent: resources
    url: https://example.com
    weight: 40
""",
            encoding="utf-8",
        )
        fixture_recruitment = fixture / "content/recruitment/recruitment2408/index.md"
        fixture_recruitment.write_text(
            fixture_recruitment.read_text(encoding="utf-8").replace(
                "date: 2025-09-01", "date: 2025-09-01\nexternal_link: https://example.com/recruitment\nsummary: \"<script>alert(1)</script> "
                + "x" * 400
                + "\""
            ),
            encoding="utf-8",
        )
        fallback_preview_dir = fixture / "content/recruitment/homepage-preview-fallback"
        fallback_preview_dir.mkdir(parents=True)
        (fallback_preview_dir / "index.md").write_text(
            """---
title: Fixture homepage fallback preview
date: 2025-09-03
categories:
  - introduction
summary: 'Fixture homepage fallback summary. 5 < 10 && <script>alert(1)</script> &amp; ok'
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
summary: "  "
---
""",
            encoding="utf-8",
        )
        blank_preview_dir = fixture / "content/recruitment/homepage-preview-blank"
        blank_preview_dir.mkdir(parents=True)
        (blank_preview_dir / "index.md").write_text(
            """---
title: Fixture homepage blank preview
date: 2025-08-31
categories:
  - introduction
homepage_preview: "  "
---
这是用于自动摘要的固定装置正文。
""",
            encoding="utf-8",
        )
        fixture_memory = fixture / "content/memory/example/index.md"
        fixture_memory.write_text(
            fixture_memory.read_text(encoding="utf-8").replace(
                "abstract: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis posuere tellusac convallis placerat. Proin tincidunt magna sed ex sollicitudin condimentum. Sed ac faucibus dolor, scelerisque sollicitudin nisi. Cras purus urna, suscipit quis sapien eu, pulvinar tempor diam.'",
                "abstract: \"<script>alert(2)</script> " + "y" * 400 + "\"",
            ),
            encoding="utf-8",
        )
        event_dir = fixture / "content/event/editorial-fixture"
        event_dir.mkdir(parents=True)
        (fixture / "content/event/_index.md").write_text("---\ntitle: Events\nview: card\n---\n", encoding="utf-8")
        (event_dir / "index.md").write_text(
            "---\ntitle: Editorial fixture event\ndate: 2026-01-01T10:00:00Z\ndate_end: 2026-01-01T11:00:00Z\nlocation: Fixture Hall\n---\n",
            encoding="utf-8",
        )
        small_post_dir = fixture / "content/post/editorial-small"
        small_post_dir.mkdir(parents=True)
        shutil.copy(fixture / "assets/media/icon.png", small_post_dir / "featured.png")
        (small_post_dir / "index.md").write_text(
            "---\ntitle: Editorial small\ndate: 2026-01-01\nimage:\n  path: featured.png\n  placement: 2\n  caption: Small fixture caption\n---\nFixture entry.",
            encoding="utf-8",
        )
        wide_featured_source = fixture / "assets/media/banner.jpg"
        for placement in (1, 2, 3):
            placement_dir = fixture / f"content/post/editorial-placement-{placement}"
            placement_dir.mkdir(parents=True)
            shutil.copy(wide_featured_source, placement_dir / "featured.jpg")
            (placement_dir / "index.md").write_text(
                f"---\ntitle: Editorial placement {placement}\ndate: 2026-01-01\nimage:\n  path: featured.jpg\n  placement: {placement}\n  caption: Placement {placement} caption\n---\nFixture entry.",
                encoding="utf-8",
            )
        homepage = fixture / "content/_index.md"
        homepage.write_text(homepage.read_text(encoding="utf-8").replace("filename: banner.jpg", "filename: icon.png", 1), encoding="utf-8")
        for extension, fixture_data in (("svg", SVG_HERO), ("gif", ANIMATED_GIF_HERO)):
            post_dir = fixture / f"content/post/editorial-{extension}"
            post_dir.mkdir(parents=True)
            (post_dir / f"featured.{extension}").write_bytes(fixture_data)
            (post_dir / "index.md").write_text(
                f"---\ntitle: Editorial {extension}\ndate: 2026-01-01\nimage:\n  path: featured.{extension}\n---\nFixture entry.",
                encoding="utf-8",
            )
        raster_banner_dir = fixture / "content/post/editorial-banner-raster"
        raster_banner_dir.mkdir(parents=True)
        shutil.copy(fixture / "assets/media/banner.jpg", raster_banner_dir / "banner.jpg")
        (raster_banner_dir / "index.md").write_text(
            "---\ntitle: Editorial raster banner\ndate: 2026-01-01\nbanner:\n  image: banner.jpg\n  caption: Raster banner caption\n---\nFixture entry.",
            encoding="utf-8",
        )
        svg_banner_dir = fixture / "content/post/editorial-banner-svg"
        svg_banner_dir.mkdir(parents=True)
        (svg_banner_dir / "banner.svg").write_bytes(SVG_HERO)
        (svg_banner_dir / "index.md").write_text(
            "---\ntitle: Editorial SVG banner\ndate: 2026-01-01\nbanner:\n  image: banner.svg\n  caption: SVG banner caption\n---\nFixture entry.",
            encoding="utf-8",
        )
        both_images_dir = fixture / "content/post/editorial-banner-featured"
        both_images_dir.mkdir(parents=True)
        shutil.copy(fixture / "assets/media/icon.png", both_images_dir / "featured.png")
        (both_images_dir / "banner.svg").write_bytes(SVG_HERO)
        (both_images_dir / "index.md").write_text(
            "---\ntitle: Editorial banner and featured\ndate: 2026-01-01\nbanner:\n  image: banner.svg\n  caption: Hidden banner caption\nimage:\n  path: featured.png\n  caption: Visible featured caption\n---\nFixture entry.",
            encoding="utf-8",
        )
        empty_banner_dir = fixture / "content/post/editorial-banner-empty-alt"
        empty_banner_dir.mkdir(parents=True)
        (empty_banner_dir / "banner.svg").write_bytes(SVG_HERO)
        (empty_banner_dir / "index.md").write_text(
            "---\ntitle: Editorial empty-alt banner\ndate: 2026-01-01\nbanner:\n  image: banner.svg\n---\nFixture entry.",
            encoding="utf-8",
        )
        fixture_publication_index = fixture / "content/publication/_index.md"
        fixture_publication_index.write_text(
            fixture_publication_index.read_text(encoding="utf-8")
            + "\nFixture publication introduction with **editorial context**.\n",
            encoding="utf-8",
        )
        image_fixture = fixture / "content/post/editorial-image-fixtures"
        image_fixture.mkdir(parents=True)
        (image_fixture / "diagram.svg").write_bytes(SVG_HERO)
        (image_fixture / "animated.gif").write_bytes(ANIMATED_GIF_HERO)
        shutil.copy(fixture / "assets/media/icon.png", image_fixture / "small.png")
        (image_fixture / "index.md").write_text(
            "---\ntitle: Editorial image fixtures\ndate: 2026-01-01\n---\n"
            '![Diagram alt](diagram.svg "SVG caption")\n\n'
            "![Animation alt](animated.gif)\n\n"
            "![Small raster](small.png)\n\n"
            '![Remote image](https://example.com/remote.png "Remote title")\n',
            encoding="utf-8",
        )
        cls.fixture_output = Path(tempfile.mkdtemp())
        cls.addClassCleanup(shutil.rmtree, cls.fixture_output)
        fixture_environment = environment = os.environ.copy()
        fixture_environment.update({"PATH": f"{Path.home() / '.local/bin'}:{fixture_environment.get('PATH', '')}", "GOPROXY": "https://goproxy.cn", "GOSUMDB": "off", "GOMODCACHE": str(Path.home() / "go/pkg/mod")})
        fixture_environment.setdefault("HUGO_BIN", "hugo")
        fixture_result = subprocess.run(
            [fixture_environment["HUGO_BIN"], "--destination", str(cls.fixture_output)],
            cwd=fixture,
            env=fixture_environment,
            capture_output=True,
            text=True,
        )
        if fixture_result.returncode:
            raise RuntimeError(f"Hugo fixture build failed with exit code {fixture_result.returncode}:\n{fixture_result.stdout}\n{fixture_result.stderr}")
        cls.fixture_article = (cls.fixture_output / "post/2025-06-03-ASC2024-prize/index.html").read_text(encoding="utf-8")
        cls.fixture_homepage = (cls.fixture_output / "index.html").read_text(encoding="utf-8")
        environment = os.environ.copy()
        environment.update(
            {
                "PATH": f"{Path.home() / '.local/bin'}:{environment.get('PATH', '')}",
                "GOPROXY": "https://goproxy.cn",
                "GOSUMDB": "off",
                "GOMODCACHE": str(Path.home() / "go/pkg/mod"),
            }
        )
        environment.setdefault("HUGO_BIN", "hugo")
        result = subprocess.run(
            [environment["HUGO_BIN"], "--destination", cls.destination.name],
            cwd=REPO_ROOT,
            env=environment,
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise RuntimeError(
                f"Hugo build failed with exit code {result.returncode}:\n"
                f"{result.stdout}\n{result.stderr}"
            )
        cls.output = Path(cls.destination.name)
        cls.homepage = (cls.output / "index.html").read_text(encoding="utf-8")

    def generated_page_path(self, route):
        return self.output / ("index.html" if route == "/" else f"{route.strip('/')}/index.html")

    def inspect_generated_page(self, route):
        inspector = TagInspector()
        inspector.feed(self.generated_page_path(route).read_text(encoding="utf-8"))
        return inspector

    def compiled_css(self):
        return "\n".join(
            stylesheet.read_text(encoding="utf-8")
            for stylesheet in self.output.rglob("*.css")
        )

    def homepage_section(self, section_id, fixture=False):
        homepage = self.fixture_homepage if fixture else self.homepage
        return homepage.split(f'id="{section_id}"', 1)[1].split("</section>", 1)[0]

    def test_key_pages_have_exactly_one_primary_heading(self):
        for route in REQUIRED_ROUTES + (AUTHOR_ROUTE, "/publication/", "/post/2025-06-03-ASC2024-prize/"):
            with self.subTest(route=route):
                headings = self.inspect_generated_page(route).find_all("h1")
                self.assertEqual(len(headings), 1, f"{route} should have one h1")

        homepage = self.inspect_generated_page("/")
        self.assertGreaterEqual(len(homepage.find_all_with_class("h2", "homepage-preview__eyebrow")), 1)

    def test_key_route_images_have_alternative_text(self):
        for route in REQUIRED_ROUTES + (
            "/publication/",
            "/post/2025-06-03-ASC2024-prize/",
            "/daily/2025-12-21/",
        ):
            with self.subTest(route=route):
                images = self.inspect_generated_page(route).find_all("img")
                for image in images:
                    self.assertIn("alt", image, f"{route}: {image}")
                    if image["alt"] == "":
                        self.assertEqual(image.get("aria-hidden"), "true", f"{route}: {image}")

    def test_empty_caption_banner_is_marked_decorative(self):
        banner = self.fixture_output / "post/editorial-banner-empty-alt/index.html"
        inspector = TagInspector()
        inspector.feed(banner.read_text(encoding="utf-8"))
        images = [
            image
            for image in inspector.find_all_with_class("img", "article-banner")
            if image.get("alt") == ""
        ]
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0].get("aria-hidden"), "true")

    def test_all_generated_pages_preserve_structure_and_skip_target(self):
        for output_path in self.output.rglob("*.html"):
            with self.subTest(page=output_path.relative_to(self.output)):
                inspector = TagInspector()
                inspector.feed(output_path.read_text(encoding="utf-8"))
                if not inspector.find_all("body"):
                    continue
                if output_path.relative_to(self.output) == Path("admin/index.html"):
                    continue
                ids = [attrs["id"] for _, attrs in inspector.tags if "id" in attrs]
                self.assertEqual(len(ids), len(set(ids)))
                mains = inspector.find_all("main")
                self.assertEqual(len(mains), 1)
                self.assertEqual(mains[0].get("id"), "main-content")
                skip_links = inspector.find_all_with_class("a", "skip-link")
                self.assertTrue(any(link.get("href") == "#main-content" for link in skip_links))

    def test_navigation_touch_targets_and_focus_ring_are_compiled(self):
        css = self.compiled_css()
        normalized_css = "".join(css.split())
        self.assertIn(":focus-visible", css)
        for selector in (
            ".editorial-brand",
            ".editorial-menu-link",
            ".editorial-menu-detailssummary",
            ".editorial-search",
            ".editorial-submenua",
            ".editorial-menu-toggle",
        ):
            with self.subTest(selector=selector):
                self.assertRegex(normalized_css, rf"{re.escape(selector)}[^{{]*\{{[^}}]*min-height:(?:2\.75rem|44px)")
        self.assertIn("outline:3pxsolidvar(--color-clay)", normalized_css)
        self.assertIn(".skip-link:focus", css)

    def test_editorial_header_stays_visible_and_nav_font_is_light(self):
        css = "\n".join(path.read_text(encoding="utf-8") for path in self.output.rglob("*.css"))
        self.assertRegex(css, r"\.editorial-header[^}]+position:\s*sticky")
        self.assertNotRegex(css, r"\.editorial-header[^}]+(?:display:\s*none|visibility:\s*hidden)")
        navigation = (REPO_ROOT / "assets/scss/components/_navigation.scss").read_text(encoding="utf-8")
        self.assertIn('"Anthropic Sans", "Styrene A", Inter', navigation)
        self.assertIn("font-family:anthropic sans,styrene a,Inter,helvetica neue,Arial,sans-serif", css)
        self.assertRegex(css, r"\.editorial-menu-link[^}]+font-weight:\s*450")
        self.assertRegex(css, r"\.editorial-menu-link[^}]+letter-spacing:\s*0?\.01em")
        article = (self.output / "post/2025-06-03-ASC2024-prize/index.html").read_text(encoding="utf-8")
        self.assertNotRegex(article, r"<script[^>]*wowchemy-headroom")
        self.assertIn('"use_headroom":false', article)
        source = (REPO_ROOT / "assets/js/editorial.js").read_text(encoding="utf-8")
        self.assertIn('header.classList.toggle("is-compact", window.scrollY > 24)', source)
        self.assertNotRegex(source, r"classList\.(?:add|toggle)\(\s*['\"](?:is-)?hidden")
        self.assertNotRegex(source, r"\.style\.(?:display|visibility)\s*=")

    def test_article_content_contains_static_overflow_guards(self):
        css = self.compiled_css()
        self.assertRegex(css, r"\.editorial-article\s*\{[^}]*overflow-wrap:\s*anywhere")
        self.assertRegex(
            css,
            r"\.editorial-article\s+\.article-style\s+(?:pre,\.editorial-article\s+\.article-style\s+)?\.highlight\s*\{[^}]*overflow-x:\s*auto",
        )
        self.assertRegex(
            css,
            r"\.editorial-article\s+\.article-style\s+table\s*\{[^}]*overflow-x:\s*auto",
        )

    def test_required_routes_are_generated(self):
        for route in REQUIRED_ROUTES:
            with self.subTest(route=route):
                output_path = self.output / route.strip("/") / "index.html" if route != "/" else self.output / "index.html"
                self.assertTrue(output_path.is_file(), f"Missing generated route: {route}")

    def test_homepage_contains_required_strings(self):
        for expected in REQUIRED_HOME_STRINGS:
            with self.subTest(expected=expected):
                self.assertIn(expected, self.homepage)

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

    def test_svg_and_animated_gif_hero_assets_build_with_original_paths(self):
        for extension, fixture_data in (("svg", SVG_HERO), ("gif", ANIMATED_GIF_HERO)):
            with self.subTest(extension=extension):
                fixture_root = tempfile.TemporaryDirectory()
                self.addCleanup(fixture_root.cleanup)
                fixture = Path(fixture_root.name) / "site"
                shutil.copytree(
                    REPO_ROOT,
                    fixture,
                    ignore=shutil.ignore_patterns(".git", "public", "resources", ".hugo_build.lock"),
                )
                image_name = f"hero.{extension}"
                (fixture / "assets/media" / image_name).write_bytes(fixture_data)
                homepage = fixture / "content/_index.md"
                homepage.write_text(
                    homepage.read_text(encoding="utf-8").replace(
                        "        base:", f"        filename: {image_name}\n        base:", 1
                    ),
                    encoding="utf-8",
                )
                destination = Path(tempfile.mkdtemp())
                self.addCleanup(shutil.rmtree, destination)
                environment = os.environ.copy()
                environment.update(
                    {
                        "PATH": f"{Path.home() / '.local/bin'}:{environment.get('PATH', '')}",
                        "GOPROXY": "https://goproxy.cn",
                        "GOSUMDB": "off",
                        "GOMODCACHE": str(Path.home() / "go/pkg/mod"),
                    }
                )
                environment.setdefault("HUGO_BIN", "hugo")
                result = subprocess.run(
                    [environment["HUGO_BIN"], "--destination", str(destination)],
                    cwd=fixture,
                    env=environment,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, f"Hugo build failed:\n{result.stdout}\n{result.stderr}")
                generated_homepage = (destination / "index.html").read_text(encoding="utf-8")
                self.assertIn(f"hero.{extension}", generated_homepage)
                self.assertNotIn("srcset=", generated_homepage)

    def test_editorial_entries_preserve_event_metadata_and_location(self):
        page = (self.fixture_output / "event/index.html").read_text(encoding="utf-8")
        self.assertIn("Fixture Hall", page)
        self.assertRegex(page, r"(?:Jan|2026)")

    def test_editorial_media_passthrough_and_responsive_candidates_are_safe(self):
        page = (self.fixture_output / "post/index.html").read_text(encoding="utf-8")
        for extension in ("svg", "gif"):
            with self.subTest(extension=extension):
                entry = page.split(f"Editorial {extension}", 1)[1].split("</article>", 1)[0]
                self.assertIn(f"featured.{extension}", entry)
                self.assertNotIn("srcset=", entry)

    def test_editorial_summary_policy_removes_html_and_bounds_all_sources(self):
        for route in ("recruitment", "memory"):
            with self.subTest(route=route):
                fixture = (self.fixture_output / f"{route}/index.html").read_text(encoding="utf-8")
                summary = fixture.split('class="editorial-entry__summary"', 1)[1].split("</div>", 1)[0]
                self.assertNotIn("<script>", summary)
                self.assertLess(len(summary), 250)

    def test_people_directory_preserves_groups_members_and_accessible_portraits(self):
        import re

        page = (self.output / "people/index.html").read_text(encoding="utf-8")
        self.assertIn('class="editorial-people"', page)
        self.assertIn('class="editorial-person"', page)
        self.assertEqual(page.count("<main"), 1)
        ids = re.findall(r'\bid="([^"]+)"', page)
        self.assertEqual(len(ids), len(set(ids)))
        directory = page.split('class="editorial-people"', 1)[1]
        self.assertEqual(page.count("<h1"), 1)
        self.assertIn("Meet the Team", directory)

        expected_groups = {
            "Mentor": ("Rui Hu", "Kui Su 苏奎"),
            "Team members": (
                "Guobin Zhang 张国宾",
                "Menglin Feng 冯梦琳",
                "Sizhe Qiao 乔思喆",
                "Xunuo Xie 谢许诺",
                "Yanan Sheng 盛亚楠",
                "Yuhan Guo",
                "Yuxiang Chen",
                "Binhao Gong 龚斌豪",
                "Zheng Cai 蔡政",
                "Jiawei Lin 林家为",
                "Junchen Lv 吕俊辰",
                "Wenjia Qu 屈文佳",
            ),
            "Alumni": ("Eason W 王绅懿", "Nuo Xu 许诺", "Zhuhan Bao 鲍竹涵", "Chengdong S 沈铖栋", "Lingkai Li 李凌凯"),
        }
        for group, members in expected_groups.items():
            with self.subTest(group=group):
                self.assertRegex(directory, rf"<h2[^>]*>{re.escape(group)}</h2>")
                for member in members:
                    self.assertIn(member, directory)

        portraits = re.findall(r'<img[^>]*class="[^"]*editorial-person__portrait[^"]*"[^>]*>', directory)
        self.assertTrue(portraits)
        for portrait in portraits:
            with self.subTest(portrait=portrait):
                self.assertRegex(portrait, r'alt="Portrait of [^"]+"')
                self.assertIn("srcset=", portrait)
                self.assertIn("sizes=", portrait)

    def test_people_avatar_template_avoids_raster_upscaling_and_preserves_passthrough(self):
        template = (REPO_ROOT / "layouts/partials/blocks/people.html").read_text(encoding="utf-8")
        self.assertIn('and site.Params.features.avatar.gravatar $person.Params.email', template)
        self.assertIn('eq $avatar.MediaType.SubType "svg"', template)
        self.assertIn('eq $avatar.MediaType.SubType "gif"', template)
        self.assertIn("if le . $avatar.Width", template)
        self.assertIn("srcset=", template)
        self.assertIn("sizes=", template)

    def test_people_social_links_are_accessible(self):
        import re

        page = (self.output / "people/index.html").read_text(encoding="utf-8")
        social = re.findall(r'<ul class="network-icon editorial-person__social"[^>]*>.*?</ul>', page, re.S)
        self.assertTrue(social)
        for links in social:
            self.assertNotRegex(links.split(">", 1)[0], r'aria-hidden')
            self.assertRegex(links, r'<a[^>]+aria-label="[^"]+"[^>]+title="[^"]+"')

    def test_gravatar_enabled_falls_back_for_empty_email_and_hashes_nonempty_email(self):
        page = (self.fixture_output / "people/index.html").read_text(encoding="utf-8")
        self.assertIn("/author/binhao-gong", page)
        self.assertNotIn("s.gravatar.com/avatar/d41d8cd98f00b204e9800998ecf8427e", page)
        self.assertIn("s.gravatar.com/avatar/", page)

    def test_editorial_landmarks_and_hero_ids_are_unique(self):
        for route in ("/", "/post/", "/daily/"):
            with self.subTest(route=route):
                path = self.output / ("index.html" if route == "/" else f"{route.strip('/')}/index.html")
                page = path.read_text(encoding="utf-8")
                self.assertEqual(page.count("<main"), 1)
                ids = re.findall(r'\bid="([^"]+)"', page)
                self.assertTrue(ids, f"No IDs found on generated page: {path}")
                self.assertEqual(len(ids), len(set(ids)))

    def test_small_raster_candidates_do_not_upscale(self):
        homepage = (self.fixture_output / "index.html").read_text(encoding="utf-8")
        hero = homepage.split('class="hero-spotlight"', 1)[1].split("</section>", 1)[0]
        self.assertNotIn("srcset=", hero)
        listing = (self.fixture_output / "post/index.html").read_text(encoding="utf-8")
        entry = listing.split("Editorial small", 1)[1].split("</article>", 1)[0]
        widths = [int(width) for width in re.findall(r"\s(\d+)w", entry)]
        self.assertTrue(widths)
        self.assertTrue(all(width <= 512 for width in widths))

    def test_text_link_colors_meet_wcag_contrast(self):
        import re

        def rgb(hex_color):
            return tuple(int(hex_color[index:index + 2], 16) / 255 for index in (1, 3, 5))

        def luminance(hex_color):
            channels = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in rgb(hex_color)]
            return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

        def contrast(foreground, background):
            light, dark = sorted((luminance(foreground), luminance(background)), reverse=True)
            return (light + 0.05) / (dark + 0.05)

        tokens = (REPO_ROOT / "assets/scss/abstracts/_tokens.scss").read_text(encoding="utf-8")
        typography = (REPO_ROOT / "assets/scss/base/_typography.scss").read_text(encoding="utf-8")
        entries = (REPO_ROOT / "assets/scss/components/_entries.scss").read_text(encoding="utf-8")
        colors = dict(re.findall(r"--(color-(?:paper|clay-dark)): (#[0-9a-f]{6})", tokens))
        self.assertIn("color: var(--color-clay-dark)", typography)
        self.assertIn("color: var(--color-clay-dark)", entries)
        self.assertGreaterEqual(contrast(colors["color-clay-dark"], colors["color-paper"]), 4.5)

    def test_editorial_sections_use_unified_index_and_entry_views(self):
        for route in ("post", "daily", "recruitment", "memory"):
            with self.subTest(route=route):
                page = (self.output / route / "index.html").read_text(encoding="utf-8")
                self.assertIn('class="editorial-index"', page)
                self.assertIn('class="editorial-entry', page)

    def test_editorial_entries_support_text_fallback_and_image_accessibility(self):
        diary = (self.output / "daily" / "index.html").read_text(encoding="utf-8")
        self.assertIn('class="editorial-entry text-only"', diary)
        self.assertIn("Sizhe", diary)
        self.assertNotIn('src=""', diary)
        self.assertNotIn("featured-image-placeholder", diary)
        post = (self.output / "post" / "index.html").read_text(encoding="utf-8")
        self.assertRegex(post, r'class="editorial-entry[^\"]*with-image')
        self.assertIn("srcset=", post)
        self.assertIn("aria-label=\"Read", post)

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

    def test_homepage_preview_falls_back_and_omits_empty_content(self):
        section = self.homepage_section("introduction", fixture=True)
        articles = re.findall(
            r'<article class="[^"]*\bhomepage-preview\b[^"]*"[^>]*>[\s\S]*?</article>',
            section,
        )

        self.assertEqual(len(articles), 4)
        self.assertEqual(section.count('class="homepage-preview__eyebrow"'), 1)
        self.assertIn("homepage-preview--first", articles[0].split(">", 1)[0])

        fallback = next(
            article for article in articles if "Fixture homepage fallback preview" in article
        )
        self.assertIn("Fixture homepage fallback summary.", fallback)
        self.assertIn("&lt;", fallback)
        self.assertIn("&amp;&amp;", fallback)
        self.assertNotIn("<script>", fallback)
        self.assertIn('class="homepage-preview__content article-style"', fallback)

        empty = next(
            article for article in articles if "Fixture homepage empty preview" in article
        )
        self.assertIn("homepage-preview--text-only", empty.split(">", 1)[0])
        self.assertNotIn("homepage-preview__content", empty)

        blank = next(
            article for article in articles if "Fixture homepage blank preview" in article
        )
        self.assertIn('class="homepage-preview__content article-style"', blank)
        self.assertNotIn("homepage-preview--text-only", blank.split(">", 1)[0])
        self.assertIn("这是用于自动摘要的固定装置正文。", blank)

        content_divs = re.findall(
            r'<div class="homepage-preview__content article-style">[\s\S]*?</div>',
            section,
        )
        self.assertTrue(content_divs)
        for content_div in content_divs:
            self.assertNotRegex(content_div, r"</h[12]>")

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

    def test_editorial_entries_keep_external_link_security_and_metadata(self):
        fixture = (self.fixture_output / "recruitment" / "index.html").read_text(encoding="utf-8")
        self.assertIn("editorial-entry__metadata", fixture)
        self.assertIn("editorial-entry__summary", fixture)
        self.assertIn('href="https://example.com/recruitment" target="_blank" rel="noopener"', fixture)

    def test_editorial_index_has_unique_heading_and_pagination(self):
        for route in ("post", "daily", "recruitment", "memory"):
            with self.subTest(route=route):
                page = (self.output / route / "index.html").read_text(encoding="utf-8")
                self.assertRegex(page, r'<section[^>]+aria-labelledby="[^"]+"')
                editorial_index = page.split('<section class="editorial-index"', 1)[1].split("</section>", 1)[0]
                self.assertEqual(editorial_index.count("<h1"), 1)
                self.assertNotIn('id="main-content"', editorial_index)

    def test_view_proxies_preserve_publication_citation(self):
        views = REPO_ROOT / "layouts/partials/views"
        for view in ("card", "compact", "list"):
            proxy = (views / f"{view}.html").read_text(encoding="utf-8")
            self.assertIn('partial "views/editorial" .', proxy)
            self.assertIn('"event" "project" "publication"', proxy)
        publication = (self.output / "publication" / "index.html").read_text(encoding="utf-8")
        self.assertIn("citation", publication)

    def test_warm_editorial_design_tokens_compile(self):
        css = "\n".join(
            stylesheet.read_text(encoding="utf-8")
            for stylesheet in self.output.rglob("*.css")
        )
        normalized_css = "".join(css.split())
        for token in (
            "--color-paper:#f2efe7",
            "--color-ink:#1f1e1a",
            "--color-clay:#b95232",
            "--font-display:",
            "--content-max:90rem",
        ):
            with self.subTest(token=token):
                self.assertIn(token, normalized_css)

    def test_homepage_keeps_meet_the_team_cta_content(self):
        for expected in (
            'href="./people/"',
            "Meet the team",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, self.homepage)
        self.assertGreaterEqual(self.homepage.count('class="cta-group"'), 1)
        self.assertIn('class="cta-group" data-reveal', self.homepage)

    def test_homepage_introduction_join_us_entries_split_title_left_preview_right(self):
        """INTRODUCTION/JOIN US cards split: metadata+title+Read top-left, preview fills the right column."""
        css = "".join(self.compiled_css().split())
        for selector in ("#introduction.editorial-entry.text-only", "#join-us.editorial-entry.text-only"):
            with self.subTest(selector=selector):
                block = re.search(re.escape(selector) + r"[^{]*\{([^}]*)\}", css)
                self.assertIsNotNone(block, f"split-layout rule missing from compiled CSS: {selector}")
                self.assertIn("grid-template-columns:", block.group(1))
                self.assertIn("grid-template-areas:", block.group(1))
        mobile = re.search(r"@media\(max-width:35\.99rem\)\{[^@]*#introduction\.editorial-entry\.text-only[^{]*\{([^}]*)\}", css)
        self.assertIsNotNone(mobile, "mobile reset rule missing for #introduction split layout")
        self.assertIn("grid-template-columns:1fr", mobile.group(1))
        self.assertIn("grid-template-areas:", mobile.group(1))

    def test_homepage_splits_introduction_and_join_us_articles(self):
        for expected in ("INTRODUCTION", "JOIN US"):
            with self.subTest(expected=expected):
                self.assertIn(expected, self.homepage)
        self.assertIn("浙大城市学院超算队介绍", self.homepage)
        self.assertIn("2025年超算队招新", self.homepage)
        intro_article = (self.output / "recruitment/recruitment2408/index.html").read_text(encoding="utf-8")
        self.assertIn("我们是谁", intro_article)
        self.assertIn("我们参加的比赛", intro_article)
        self.assertIn('href="/accomplishments/"', intro_article)
        self.assertNotIn("招新条件", intro_article)
        join_article = (self.output / "recruitment/join-us/index.html").read_text(encoding="utf-8")
        self.assertIn("招新条件", join_article)
        self.assertIn("报名及联系方式", join_article)
        self.assertIn("1004145044", join_article)

    def test_article_inline_cta_matches_warm_pill_design(self):
        css = "".join(self.compiled_css().split())
        cta_button = re.search(r"\.editorial-article\.article-style\.cta-group\.btn\{([^}]*)\}", css)
        self.assertIsNotNone(cta_button, "article inline CTA button rule missing from compiled CSS")
        for expected in ("border-radius:999px", "color:var(--color-paper)", "background:var(--color-clay-dark)", "font-weight:500", "min-height:44px"):
            with self.subTest(expected=expected):
                self.assertIn(expected, cta_button.group(1))
        cta_hover = re.search(r"\.editorial-article\.article-style\.cta-group\.btn:hover[^{]*\{([^}]*)\}", css)
        self.assertIsNotNone(cta_hover, "article inline CTA hover rule missing from compiled CSS")
        self.assertIn("transform:scale(1.05)", cta_hover.group(1))
        self.assertIn("color:var(--color-ink)", cta_hover.group(1))
        self.assertIn("background:var(--color-clay-light)", cta_hover.group(1))
        self.assertNotIn("background:var(--color-ink)", cta_hover.group(1))
        reduced = re.search(r"prefers-reduced-motion:reduce\)\{[^}]*\.editorial-article\.article-style\.cta-group\.btn\{([^}]*)\}", css)
        self.assertIsNotNone(reduced, "article inline CTA reduced-motion rule missing from compiled CSS")
        self.assertIn("transition:none", reduced.group(1))

    def test_meet_the_team_cta_is_a_light_pill_button(self):
        css = self.compiled_css()
        normalized_css = "".join(css.split())
        cta_button = re.search(r"\.home-section\.cta-group\.btn\{([^}]*)\}", normalized_css)
        self.assertIsNotNone(cta_button, "home CTA button rule missing from compiled CSS")
        for expected in ("border-radius:999px", "font-weight:500", "min-height:44px", "font-size:1.1rem"):
            with self.subTest(expected=expected):
                self.assertIn(expected, cta_button.group(1))
        for expected in ('href="./people/"', "Meet the team"):
            with self.subTest(expected=expected):
                self.assertIn(expected, self.homepage)
        self.assertNotIn('id="accomplishments"', self.homepage)

    def test_page_gutter_is_wider_for_edge_spacing(self):
        tokens = (REPO_ROOT / "assets/scss/abstracts/_tokens.scss").read_text(encoding="utf-8")
        self.assertIn("--page-gutter: clamp(1.5rem, 5vw, 6rem)", tokens)
        css = self.compiled_css()
        self.assertIn("--page-gutter:clamp(1.5rem,5vw,6rem)", "".join(css.split()))

    def test_meet_the_team_cta_is_centered_and_zooms_on_hover(self):
        css = "".join(self.compiled_css().split())
        cta_group = re.search(r"\.home-section\.cta-group\{([^}]*)\}", css)
        self.assertIsNotNone(cta_group, "home CTA group rule missing from compiled CSS")
        self.assertIn("justify-content:center", cta_group.group(1))
        cta_hover = re.search(r"\.home-section\.cta-group\.btn:hover[^{]*\{([^}]*)\}", css)
        self.assertIsNotNone(cta_hover, "home CTA hover rule missing from compiled CSS")
        self.assertIn("transform:scale(1.05)", cta_hover.group(1))
        self.assertIn("color:var(--color-ink)", cta_hover.group(1))
        self.assertIn("background:var(--color-clay-light)", cta_hover.group(1))
        self.assertNotIn("background:var(--color-ink)", cta_hover.group(1))
        reduced = re.search(r"prefers-reduced-motion:reduce\)\{[^}]*\.home-section\.cta-group\.btn\{([^}]*)\}", css)
        self.assertIsNotNone(reduced, "CTA reduced-motion rule missing from compiled CSS")
        self.assertIn("transition:none", reduced.group(1))

    def test_home_and_contact_section_containers_keep_content_away_from_edges(self):
        home_scss = (REPO_ROOT / "assets/scss/pages/_home.scss").read_text(encoding="utf-8")
        self.assertIn(".home-section > .container", home_scss)
        self.assertIn("padding-inline: var(--page-gutter)", home_scss)
        css = "".join(self.compiled_css().split())
        section_container = re.search(r"\.home-section>\.container\{([^}]*)\}", css)
        self.assertIsNotNone(section_container, "home section container rule missing from compiled CSS")
        self.assertIn("padding-inline:var(--page-gutter)", section_container.group(1))
        hero_container = re.search(r"\.home-section\.wg-hero>\.container\{([^}]*)\}", css)
        self.assertIsNotNone(hero_container, "hero container rule missing from compiled CSS")
        self.assertIn("padding-inline:0", hero_container.group(1))
        contact = (self.output / "contact/index.html").read_text(encoding="utf-8")
        self.assertIn('id="section-contact"', contact)

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
            r"@media\(max-width:47\.99rem\)\{(?:[^{}]*\{[^}]*\})*?\.homepage-preview\{([^}]*)\}",
            css,
        )
        self.assertIsNotNone(mobile, "homepage preview mobile layout rule missing")
        self.assertIn("grid-template-columns:1fr", mobile.group(1))

        mobile_content = re.search(
            r"@media\(max-width:47\.99rem\)\{(?:[^{}]*\{[^}]*\})*?\.homepage-preview__content\{([^}]*)\}",
            css,
        )
        self.assertIsNotNone(mobile_content, "homepage preview mobile content rule missing")
        self.assertIn("border-top:1pxsolidvar(--color-line)", mobile_content.group(1))
        self.assertIn("border-left:0", mobile_content.group(1))
        self.assertIn("padding-left:0", mobile_content.group(1))

        text_only = re.search(r"\.homepage-preview--text-only\{([^}]*)\}", css)
        self.assertIsNotNone(text_only, "homepage preview text-only layout rule missing")
        self.assertIn("grid-template-columns:minmax(0,48rem)", text_only.group(1))

        mobile_text_only = re.search(
            r"@media\(max-width:47\.99rem\)\{(?:[^{}]*\{[^}]*\})*?\.homepage-preview--text-only\{([^}]*)\}",
            css,
        )
        self.assertIsNotNone(mobile_text_only, "homepage preview mobile text-only layout rule missing")
        self.assertIn("grid-template-columns:1fr", mobile_text_only.group(1))

        self.assertNotRegex(
            css,
            r"\.homepage-preview[^{}]*:hover[^{}]*\{[^}]*transform:",
        )
        self.assertNotIn("#section-collection.editorial-entry:first-child", css)

        home_styles = (REPO_ROOT / "assets/scss/pages/_home.scss").read_text(encoding="utf-8")
        self.assertIn(".homepage-preview__eyebrow", home_styles)

    def test_editorial_header_background_differs_from_page_background(self):
        tokens = (REPO_ROOT / "assets/scss/abstracts/_tokens.scss").read_text(encoding="utf-8")
        self.assertIn("--color-clay-light: #cf7a5c", tokens)
        css = "".join(self.compiled_css().split())
        header_rule = re.search(r"\.editorial-header\{([^}]*)\}", css)
        self.assertIsNotNone(header_rule, "editorial header rule missing from compiled CSS")
        self.assertIn("background:var(--color-paper-deep)", header_rule.group(1))
        self.assertIn("background:var(--color-paper)", css)

    def test_article_title_is_compact_on_desktop(self):
        article_scss = (REPO_ROOT / "assets/scss/pages/_article.scss").read_text(encoding="utf-8")
        self.assertRegex(article_scss, r"font-size: clamp\(1\.75rem, [^;]+2\.75rem\)")
        css = "".join(self.compiled_css().split())
        title_rule = re.search(r"\.editorial-article\.page_headerh1\{([^}]*)\}", css)
        self.assertIsNotNone(title_rule, "article title rule missing from compiled CSS")
        self.assertIn("font-size:clamp(1.75rem", title_rule.group(1))
        self.assertNotIn("5.5rem", title_rule.group(1))

    def test_accomplishments_page_preserves_years_awards_and_details(self):
        page = (self.output / "accomplishments/index.html").read_text(encoding="utf-8")
        for expected in (
            "2022年",
            "2023年",
            "2024年",
            "2025年",
            "IPCC Excellence Award",
            "CPC Excellence Award",
            "ASC2024 Second Prize (Team 1)",
            "ASC2024 Second Prize (Team 2)",
            "ACM China - International Parallel Computing Challenge Excellence Award",
            "ASC24 Student Supercomputer Challenge Preliminary Second Prize",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, page)

    def test_homepage_removes_accomplishments_but_independent_page_keeps_awards(self):
        self.assertNotIn('id="accomplishments"', self.homepage)
        self.assertNotIn("ACCOMPLISHMENTS", self.homepage)
        accomplishments = (self.output / "accomplishments/index.html").read_text(encoding="utf-8")
        for expected in ("Accomplishments", "2022年", "2023年", "2024年", "2025年", "IPCC Excellence Award", "ASC2024 Second Prize"):
            with self.subTest(expected=expected):
                self.assertIn(expected, accomplishments)

    def test_accomplishments_is_left_aligned_year_grouped_and_reveals_without_hover_motion(self):
        page = (self.output / "accomplishments/index.html").read_text(encoding="utf-8")
        self.assertRegex(page, r'<h1[^>]*>\s*Accomplishments\s*</h1>')
        self.assertLess(page.index("Accomplishments</h1>"), page.index("2022年"))
        for year in ("2022年", "2023年", "2024年", "2025年"):
            with self.subTest(year=year):
                self.assertIn(year, page)
        for award in (
            "IPCC Excellence Award",
            "CPC Excellence Award",
            "ASC2024 Second Prize (Team 1)",
            "ASC2024 Second Prize (Team 2)",
        ):
            with self.subTest(award=award):
                self.assertIn(award, page)
        self.assertGreaterEqual(page.count('class="editorial-accomplishment" data-reveal'), 4)

        css = "".join(
            stylesheet.read_text(encoding="utf-8")
            for stylesheet in self.output.rglob("*.css")
        )
        normalized_css = "".join(css.split())
        self.assertIn(
            ".editorial-accomplishment[data-reveal].is-reveal-ready{opacity:0;transform:translateY(12px)",
            normalized_css,
        )
        self.assertIn(
            "@media(prefers-reduced-motion:reduce){.editorial-accomplishment[data-reveal],.editorial-accomplishment[data-reveal].is-reveal-ready{opacity:1;transform:none",
            normalized_css,
        )
        self.assertNotRegex(normalized_css, r"editorial-accomplishment[^{}]*:hover[^{}]*transform")
        self.assertNotIn("#accomplishments", normalized_css)

    def test_desktop_type_scale_and_people_density_are_constrained(self):
        css = self.compiled_css()
        people = (REPO_ROOT / "assets/scss/components/_people.scss").read_text(encoding="utf-8")
        self.assertIn("@media (min-width: 64rem)", people)
        self.assertIn("grid-template-columns: repeat(4", people)
        self.assertIn("max-width: 80rem", people)
        self.assertRegex(people, r"font-size: clamp\(1\.2rem, [^;]+, 1\.5rem\)")
        self.assertIn("--heading-hero-compact", css)
        self.assertIn("--heading-display-compact", css)
        self.assertIn("#profile-page .portrait-title h1", css)
        list_styles = (REPO_ROOT / "assets/scss/pages/_list.scss").read_text(encoding="utf-8")
        self.assertRegex(
            list_styles,
            r"@media \(min-width: 64rem\)[\s\S]*\.editorial-index h1\s*\{[^}]*font-size:\s*var\(--heading-display-compact\)",
        )

    def test_home_section_headings_use_section_scale_not_display_scale(self):
        home_styles = (REPO_ROOT / "assets/scss/pages/_home.scss").read_text(encoding="utf-8")
        desktop_section_heading = re.search(
            r"@media \(min-width: 64rem\)[\s\S]*\.home-section \.section-heading h2\s*\{([^}]+)\}",
            home_styles,
        )
        self.assertIsNotNone(desktop_section_heading)
        self.assertIn("font-size: var(--heading-section-compact)", desktop_section_heading.group(1))
        self.assertNotIn("--heading-display-compact", desktop_section_heading.group(1))

        css = self.compiled_css()
        normalized_css = "".join(css.split())
        self.assertIn("--heading-section-compact:clamp(1.75rem,1.3rem+1.2vw,3.25rem)", normalized_css)

        list_styles = (REPO_ROOT / "assets/scss/pages/_list.scss").read_text(encoding="utf-8")
        self.assertRegex(
            list_styles,
            r"@media \(min-width: 64rem\)[\s\S]*\.editorial-index h1\s*\{[^}]*font-size:\s*var\(--heading-display-compact\)",
        )
        self.assertIn("--heading-display-compact:clamp(2.25rem,1.6rem+1.8vw,4.5rem)", normalized_css)

    def test_contact_page_preserves_description_email_and_form_controls(self):
        page = (self.output / "contact/index.html").read_text(encoding="utf-8")
        for expected in (
            "我们是一支精心选拔",
            "推动计算科学的前沿",
            "hur@hzcu.edu.cn",
            'id="inputName"',
            'id="inputEmail"',
            'name="message"',
            'type="submit"',
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, page)

    def test_publication_page_preserves_filters_and_citation_entries(self):
        page = (self.output / "publication/index.html").read_text(encoding="utf-8")
        self.assertIn('class="filter-search form-control form-control-sm"', page)
        self.assertIn('data-filter-group="pubtype"', page)
        self.assertIn('data-filter-group="year"', page)
        self.assertIn('value="*"', page)
        self.assertEqual(page.count('class="pub-list-item view-citation"'), 3)
        self.assertIn("citation", page)

    def test_non_home_landing_page_has_a_page_heading_and_demotes_slider_headings(self):
        tour = self.generated_page_path("/tour/").read_text(encoding="utf-8")
        self.assertEqual(tour.count("<h1"), 1)
        self.assertRegex(tour, r'<h1 class="sr-only">Tour</h1>')
        self.assertNotIn('<h1 class="hero-title">', tour)
        for title in ("Welcome to the group", "Lunch &amp; Learn", "World-Class Semiconductor Lab"):
            with self.subTest(title=title):
                self.assertRegex(tour, rf'<h2 class="hero-title\s*">[\s\S]*?{title}')

    def test_author_profile_keeps_profile_content_and_has_primary_heading(self):
        page = self.generated_page_path(AUTHOR_ROUTE).read_text(encoding="utf-8")
        self.assertEqual(page.count("<h1"), 1)
        self.assertIn("Sizhe Qiao 乔思喆", page)
        self.assertIn("世界一分为二", page)
        self.assertIn('class="avatar avatar-circle"', page)

    def test_home_section_headings_are_h2_but_hero_remains_h1(self):
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

    def test_author_profile_social_links_are_accessible(self):
        page = self.generated_page_path("/author/yanan-sheng-盛亚楠/").read_text(encoding="utf-8")
        social = re.search(r'<ul class="network-icon"[^>]*>.*?</ul>', page, re.S)
        self.assertIsNotNone(social)
        self.assertNotIn("aria-hidden", social.group(0).split(">", 1)[0])
        links = re.findall(r'<a[^>]*>.*?</a>', social.group(0), re.S)
        self.assertTrue(links)
        for link in links:
            self.assertRegex(link, r'aria-label="[^"]+"')
            self.assertRegex(link, r'title="[^"]+"')
            self.assertRegex(link, r'<i[^>]+aria-hidden="true"')

    def test_gravatar_enabled_author_profiles_fall_back_for_empty_email(self):
        page = (self.fixture_output / "author/rui-hu/index.html").read_text(encoding="utf-8")
        self.assertNotIn("d41d8cd98f00b204e9800998ecf8427e", page)
        self.assertNotIn("?s=270')", page)
        self.assertRegex(page, r'<img[^>]+class="avatar [^"]+"[^>]+src="/author/rui-hu/avatar')

    def test_search_close_and_share_icons_have_accessible_touch_targets(self):
        article = self.output / "post/2025-06-03-ASC2024-prize/index.html"
        page = article.read_text(encoding="utf-8")
        close = re.search(r'<a[^>]+class="js-search"[^>]*>.*?</a>', page)
        self.assertIsNotNone(close)
        self.assertIn('aria-label="Close"', close.group(0))
        self.assertRegex(close.group(0), r'<i[^>]+aria-hidden="true"')
        self.assertRegex(page, r'<h2 class="search-title">Search</h2>')
        share_links = re.findall(r'<a[^>]+class=(?:"share-btn-[^"]+"|share-btn-[^\s>]+)[^>]*>.*?</a>', page, re.S)
        self.assertTrue(share_links)
        for link in share_links:
            self.assertRegex(link, r'aria-label=(?:"Share (?:on|by) [^"]+"|Share(?:on|by)[^\s>]+)')
            self.assertRegex(link, r'<i[^>]+aria-hidden=(?:"true"|true)')
        css = self.compiled_css()
        normalized_css = "".join(css.split())
        self.assertRegex(
            normalized_css,
            r"\.col-search-close\.js-search,\.share>li>a\{[^}]*min-width:44px;min-height:44px",
        )
        self.assertRegex(normalized_css, r"\.search-headerh2\{[^}]*margin:0[^}]*line-height:1")

    def test_task8_style_selectors_match_generated_home_contact_and_publication_dom(self):
        home_sections = re.findall(r'<section[^>]*class="[^"]*home-section[^"]*"[^>]*>', self.homepage)
        self.assertGreaterEqual(len(home_sections), 3)
        self.assertIn("wg-hero-spotlight", home_sections[0])
        self.assertTrue(all("wg-hero-spotlight" not in section for section in home_sections[1:]))

        collection = self.homepage_section("introduction")
        self.assertNotIn('class="section-heading', collection)
        self.assertRegex(collection, r'<article class="[^"]*homepage-preview')
        self.assertIn('<h2 class="homepage-preview__eyebrow">', collection)
        join_us = self.homepage_section("join-us")
        self.assertNotIn('class="section-heading', join_us)
        self.assertRegex(join_us, r'<article class="[^"]*homepage-preview')
        self.assertIn('<h2 class="homepage-preview__eyebrow">', join_us)

        self.assertIn('class="cta-group"', self.homepage)

        contact = (self.output / "contact/index.html").read_text(encoding="utf-8")
        contact_section = contact.split('id="section-contact"', 1)[1].split("</section>", 1)[0]
        self.assertIn("wg-contact", contact_section.split(">", 1)[0])
        self.assertRegex(contact_section, r'class="section-heading[^"]*"[\s\S]*?<h2')
        self.assertIn('class="form-control', contact_section)

        accomplishments = (self.output / "accomplishments/index.html").read_text(encoding="utf-8")
        editorial_index = accomplishments.split('class="editorial-index"', 1)[1].split("</section>", 1)[0]
        self.assertIn('class="editorial-index__intro article-style"', editorial_index)

        publication = (self.output / "publication/index.html").read_text(encoding="utf-8")
        publication_controls = publication.split('class="form-row mb-4"', 1)[1].split('id="container-publications"', 1)[0]
        self.assertIn('class="filter-search', publication_controls)
        self.assertEqual(publication_controls.count('class="pub-filters'), 2)
        publication_container = publication.split('id="container-publications"', 1)[1].split("</div>\n\n    </div>", 1)[0]
        wrappers = re.findall(r'<div class="grid-sizer[^"]*isotope-item[^"]*">[\s\S]*?<div class="pub-list-item', publication_container)
        self.assertEqual(len(wrappers), 3)

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

    def test_publication_optional_intro_uses_scoped_plain_content_styles(self):
        page = (self.fixture_output / "publication/index.html").read_text(encoding="utf-8")
        wrapper = page.split('class="universal-wrapper"', 1)[1].split('class="form-row mb-4"', 1)[0]
        self.assertRegex(
            wrapper,
            r'<div class="row">\s*<div class="col-lg-12">\s*<div class="article-style"><p>Fixture publication introduction with <strong>editorial context</strong>\.</p>',
        )

        css = "\n".join(
            stylesheet.read_text(encoding="utf-8")
            for stylesheet in self.fixture_output.rglob("*.css")
        )
        normalized_css = "".join(css.split())
        self.assertIn(".universal-wrapper>.row>.col-lg-12>.article-style{", normalized_css)
        self.assertNotIn("}.article-style{max-width:", normalized_css)

    def test_publication_filters_have_accessible_names(self):
        page = (self.output / "publication/index.html").read_text(encoding="utf-8")
        search = re.search(r'<input[^>]*class="filter-search[^>]*>', page)
        pubtype = re.search(r'<select[^>]*class="pub-filters pubtype-select[^>]*>', page)
        year = re.search(r'<select[^>]*class="pub-filters form-control[^>]*data-filter-group="year"[^>]*>', page)
        self.assertIsNotNone(search)
        self.assertIsNotNone(pubtype)
        self.assertIsNotNone(year)
        self.assertIn('aria-label="Search..."', search.group(0))
        self.assertIn('aria-label="Type"', pubtype.group(0))
        self.assertIn('aria-label="Date"', year.group(0))

    def test_publication_terminal_rule_targets_only_final_isotope_wrapper(self):
        styles = (REPO_ROOT / "assets/scss/pages/_list.scss").read_text(encoding="utf-8")
        self.assertIn("#container-publications > .isotope-item:last-child .pub-list-item", styles)
        self.assertNotIn("#container-publications .pub-list-item:last-child", styles)

        class DirectChildren(HTMLParser):
            def __init__(self):
                super().__init__()
                self.in_container = False
                self.container_depth = 0
                self.children = []

            def handle_starttag(self, tag, attrs):
                attributes = dict(attrs)
                if tag == "div" and attributes.get("id") == "container-publications":
                    self.in_container = True
                    self.container_depth = 1
                    return
                if self.in_container:
                    if self.container_depth == 1 and tag == "div":
                        self.children.append(attributes.get("class", ""))
                    self.container_depth += 1

            def handle_startendtag(self, tag, attrs):
                if self.in_container and self.container_depth > 1:
                    return

            def handle_endtag(self, tag):
                if not self.in_container:
                    return
                self.container_depth -= 1
                if self.container_depth == 0:
                    self.in_container = False

        page = (self.output / "publication/index.html").read_text(encoding="utf-8")
        parser = DirectChildren()
        parser.feed(page)
        self.assertEqual(len(parser.children), 3)
        self.assertTrue(all("isotope-item" in classes.split() for classes in parser.children))
        self.assertIn("isotope-item", parser.children[-1].split())

    def test_warm_editorial_rhythm_styles_compile_for_home_and_lists(self):
        css = "\n".join(
            stylesheet.read_text(encoding="utf-8")
            for stylesheet in self.output.rglob("*.css")
        )
        normalized_css = "".join(css.split())
        for selector in (
            ".home-section:not(:first-of-type)",
            ".home-section .section-heading h2",
            ".homepage-preview",
            ".home-section .cta-group",
            ".wg-contact .form-control",
            ".editorial-index__intro",
            ".filter-search,.pub-filters{min-height:44px",
            "#container-publications .pub-list-item",
            ".editorial-index .article-style",
        ):
            with self.subTest(selector=selector):
                self.assertIn(selector.replace(" ", ""), normalized_css)

    def test_editorial_menu_overrides_bootstrap_collapse_on_desktop(self):
        css = "".join(
            stylesheet.read_text(encoding="utf-8")
            for stylesheet in self.output.rglob("*.css")
        )
        normalized_css = "".join(css.split())
        self.assertIn("@media(min-width:992px){.editorial-menu.collapse{display:flex}", normalized_css)
        self.assertIn(".editorial-menu.collapse:not(.show){display:none}", normalized_css)

    def test_skip_link_target_exists_on_every_generated_page(self):
        for route in REQUIRED_ROUTES:
            output_path = self.output / route.strip("/") / "index.html" if route != "/" else self.output / "index.html"
            with self.subTest(route=route):
                page = output_path.read_text(encoding="utf-8")
                self.assertIn('id="main-content"', page)

    def test_editorial_navigation_and_footer_are_emitted(self):
        for expected in (
            'class="skip-link"',
            "editorial-header",
            'aria-label="Primary navigation"',
            "editorial-footer-grid",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, self.homepage)

    def test_mobile_navigation_is_accessible(self):
        self.assertIn('aria-controls="editorial-menu"', self.homepage)
        self.assertIn('aria-expanded="false"', self.homepage)
        self.assertRegex(self.homepage, r'<button[^>]+aria-label="[^"]+"')

    def test_article_uses_editorial_structure_and_preserves_content(self):
        page = self.output / "post/2025-06-03-ASC2024-prize/index.html"
        article = page.read_text(encoding="utf-8")
        self.assertEqual(article.count("<main"), 1)
        self.assertEqual(article.count('id="main-content"'), 1)
        self.assertIn('<article class="editorial-article">', article)
        self.assertRegex(article, r'class="[^"]*\bpage_header\b[^"]*"')
        self.assertIn('class="article-container"', article)
        self.assertIn('class="article-style"', article)
        self.assertIn('class="page_footer"', article)
        self.assertEqual(article.count("<h1"), 1)
        self.assertIn("喜报 | 我校超算团队蝉联ASC世界大学生超算竞赛国际二等奖", article)
        self.assertIn("在第12届ASC世界大学生超级计算机竞赛", article)

    def test_article_raster_images_use_safe_responsive_dimensions(self):
        article = self.output / "post/2025-06-03-ASC2024-prize/index.html"
        page = article.read_text(encoding="utf-8")
        for alt in ("团队获奖证书1", "团队获奖证书2"):
            with self.subTest(alt=alt):
                image = re.search(rf'<img[^>]*alt="{alt}"[^>]*>', page)
                self.assertIsNotNone(image)
                tag = image.group(0)
                self.assertIn("srcset=", tag)
                self.assertIn("sizes=", tag)
                self.assertRegex(tag, r'width="\d+"')
                self.assertRegex(tag, r'height="\d+"')
                self.assertIn('loading="lazy"', tag)
                self.assertIn("data-zoomable", tag)
                widths = [int(width) for width in re.findall(r"\s(\d+)w", tag)]
                self.assertTrue(widths)
                self.assertEqual(len(widths), len(set(widths)))
                self.assertLessEqual(max(widths), 1200)

    def test_raster_banner_candidates_are_unique_and_capped(self):
        page = (self.fixture_output / "post/editorial-banner-raster/index.html").read_text(encoding="utf-8")
        banner = re.search(r'<img[^>]*class="article-banner"[^>]*>', page).group(0)
        widths = [int(width) for width in re.findall(r"\s(\d+)w", banner)]
        self.assertTrue(widths)
        self.assertEqual(len(widths), len(set(widths)))
        self.assertLessEqual(max(widths), 1600)

    def test_diary_image_preserves_alt_and_dimensions(self):
        page = (self.output / "daily/2025-11-28/index.html").read_text(encoding="utf-8")
        image = re.search(r'<img[^>]*alt="此乃美食。"[^>]*>', page)
        self.assertIsNotNone(image)
        self.assertRegex(image.group(0), r'width="\d+"')
        self.assertRegex(image.group(0), r'height="\d+"')

    def test_article_image_edge_fixtures_use_safe_passthrough_and_fallback(self):
        page = (self.fixture_output / "post/editorial-image-fixtures/index.html").read_text(encoding="utf-8")
        svg = re.search(r'<img[^>]*alt="Diagram alt"[^>]*>', page).group(0)
        gif = re.search(r'<img[^>]*alt="Animation alt"[^>]*>', page).group(0)
        raster = re.search(r'<img[^>]*alt="Small raster"[^>]*>', page).group(0)
        remote = re.search(r'<img[^>]*alt="Remote image"[^>]*>', page).group(0)
        self.assertIn("diagram.svg", svg)
        self.assertNotIn("srcset=", svg)
        self.assertIn("animated.gif", gif)
        self.assertNotIn("srcset=", gif)
        self.assertIn("srcset=", raster)
        raster_widths = re.findall(r"\s(\d+)w", raster)
        self.assertTrue(raster_widths)
        self.assertTrue(all(int(width) <= 512 for width in raster_widths))
        self.assertIn('src="https://example.com/remote.png"', remote)
        self.assertIn('loading="lazy"', remote)
        self.assertIn("Remote title", page)
        self.assertNotIn("<figcaption><", page)

    def test_article_featured_images_preserve_placement_captions_and_safe_candidates(self):
        page = (self.fixture_output / "post/editorial-small/index.html").read_text(encoding="utf-8")
        featured_wrapper = page.split('class="article-header ', 1)[1].split("</div>", 1)[0]
        wrapper_classes = featured_wrapper.split('"', 1)[0].split()
        featured = re.search(r'<img[^>]*class="featured-image"[^>]*>', page).group(0)
        self.assertIn("container", wrapper_classes)
        self.assertNotIn("article-container", wrapper_classes)
        self.assertIn("Small fixture caption", featured_wrapper)
        self.assertIn("srcset=", featured)
        self.assertIn("sizes=", featured)
        featured_widths = re.findall(r"\s(\d+)w", featured)
        self.assertTrue(featured_widths)
        self.assertTrue(all(int(width) <= 512 for width in featured_widths))
        for extension in ("svg", "gif"):
            with self.subTest(extension=extension):
                fixture = (self.fixture_output / f"post/editorial-{extension}/index.html").read_text(encoding="utf-8")
                wrapper = fixture.split('class="article-header ', 1)[1].split("</div>", 1)[0]
                image = re.search(r'<img[^>]*class="featured-image"[^>]*>', fixture).group(0)
                self.assertIn(f"featured.{extension}", image)
                self.assertNotIn("srcset=", image)
                if extension == "gif":
                    self.assertIn('style="max-width: 1px;"', wrapper)

    def test_svg_banner_passes_through_without_raster_dimensions(self):
        page = (self.fixture_output / "post/editorial-banner-svg/index.html").read_text(encoding="utf-8")
        banner = re.search(r'<img[^>]*class="article-banner"[^>]*>', page).group(0)
        self.assertIn("banner.svg", banner)
        self.assertNotIn("srcset=", banner)
        self.assertNotIn("width=", banner)
        self.assertNotIn("height=", banner)

    def test_featured_images_use_placement_specific_sizes_and_candidates(self):
        expectations = {
            1: ("(min-width: 720px) 720px, 100vw", 720),
            2: ("(min-width: 1200px) 1200px, 100vw", 1200),
            3: ("(min-width: 2560px) 2560px, 100vw", 1707),
        }
        for placement, (sizes, max_width) in expectations.items():
            with self.subTest(placement=placement):
                page = (self.fixture_output / f"post/editorial-placement-{placement}/index.html").read_text(encoding="utf-8")
                featured = re.search(r'<img[^>]*class="featured-image"[^>]*>', page).group(0)
                self.assertIn(f'sizes="{sizes}"', featured)
                self.assertIn(f'alt="Placement {placement} caption"', featured)
                widths = [int(width) for width in re.findall(r"\s(\d+)w", featured)]
                self.assertTrue(widths)
                self.assertLessEqual(max(widths), max_width)
                if placement == 3:
                    self.assertGreater(max(widths), 1200)

    def test_visible_featured_image_suppresses_banner(self):
        page = (self.fixture_output / "post/editorial-banner-featured/index.html").read_text(encoding="utf-8")
        self.assertIn("featured.png", page)
        self.assertIn("Visible featured caption", page)
        self.assertNotIn("banner.svg", page)
        self.assertNotIn("Hidden banner caption", page)

    def test_search_dialog_does_not_duplicate_the_page_h1(self):
        article = (self.output / "post/2025-06-03-ASC2024-prize/index.html").read_text(encoding="utf-8")
        self.assertEqual(article.count("<h1"), 1)
        self.assertRegex(article, r'<(?:h2|div) class="search-title">Search</(?:h2|div)>')

    def test_descendant_page_marks_its_menu_section_as_current_location(self):
        article = self.output / "post" / "2025-06-03-ASC2024-prize" / "index.html"
        page = article.read_text(encoding="utf-8")
        self.assertRegex(
            page,
            r'<a class="editorial-menu-link is-active" href="/post" aria-current="location">\s*<span>Post</span>',
        )

    def test_fixture_dropdown_states_and_external_links_are_generated(self):
        page = self.fixture_article
        self.assertIn('class="editorial-menu-details is-active"', page)
        self.assertIn('<summary aria-current="location">', page)
        self.assertRegex(page, r'<a class="is-active" href="/post/2025-06-03-ASC2024-prize/" aria-current="page">')
        self.assertRegex(page, r'<a class="is-active" href="/post" aria-current="location">')
        self.assertRegex(page, r'<a class="" href="https://example.com" target="_blank" rel="noopener">')
        self.assertNotRegex(page, r'<a class="is-active" href="/"')

    def test_editorial_script_is_bundled_and_exposes_motion_hooks(self):
        scripts = re.findall(r'<script[^>]+src="([^"]+)"', self.homepage)
        self.assertTrue(any("wowchemy" in src for src in scripts))
        source = (REPO_ROOT / "assets/js/editorial.js").read_text(encoding="utf-8")
        for expected in ("prefers-reduced-motion", "IntersectionObserver", "data-editorial-header"):
            with self.subTest(expected=expected):
                self.assertIn(expected, source)
        self.assertIn('data-editorial-header', self.homepage)
        self.assertIn('data-reveal', self.homepage)
        bundles = "\n".join(stylesheet.read_text(encoding="utf-8") for stylesheet in self.output.rglob("*.js"))
        for expected in ("IntersectionObserver", "prefers-reduced-motion", "data-editorial-header"):
            with self.subTest(bundle_expected=expected):
                self.assertIn(expected, bundles)

    def test_editorial_motion_progressively_enhances_visible_content(self):
        source = (REPO_ROOT / "assets/js/editorial.js").read_text(encoding="utf-8")
        accessibility = (REPO_ROOT / "assets/scss/base/_accessibility.scss").read_text(encoding="utf-8")
        hidden_rule = re.search(r"\[data-reveal\]\.is-reveal-ready\s*\{([^}]+)\}", accessibility, re.S)
        self.assertIsNotNone(hidden_rule)
        self.assertIn("opacity: 0", hidden_rule.group(1))
        self.assertNotRegex(accessibility, r"(?m)^\[data-reveal\]\s*\{[^}]*opacity:\s*0")
        ready_add = 'element.classList.add("is-reveal-ready")'
        observe = "observer.observe(element)"
        self.assertIn(ready_add, source)
        self.assertIn(observe, source)
        self.assertLess(source.index(ready_add), source.index(observe))

        fallback = re.search(
            r'if \(reducedMotion\.matches \|\| !\("IntersectionObserver" in window\)\) \{([^}]+)\}',
            source,
            re.S,
        )
        self.assertIsNotNone(fallback)
        self.assertIn("showAll()", fallback.group(1))
        self.assertIn("return", fallback.group(1))
        self.assertIn('element.classList.add("is-visible")', source)
        self.assertIn("observer.unobserve(entry.target)", source)
        delay_cap = re.search(r"Math\.min\(index % (\d+), (\d+)\) \* (\d+)", source)
        self.assertIsNotNone(delay_cap)
        self.assertLessEqual(int(delay_cap.group(2)) * int(delay_cap.group(3)), 180)

    def test_compact_header_state_has_a_visual_css_contract(self):
        navigation = (REPO_ROOT / "assets/scss/components/_navigation.scss").read_text(encoding="utf-8")
        compact = re.search(r"\.editorial-header\.is-compact\s+\.editorial-nav-container\s*\{([^}]+)\}", navigation, re.S)
        self.assertIsNotNone(compact)
        self.assertRegex(compact.group(1), r"min-height:\s*[0-9.]+rem")
        self.assertIn("transition:", navigation)

    def test_reduced_motion_css_is_compiled(self):
        css = "\n".join(stylesheet.read_text(encoding="utf-8") for stylesheet in self.output.rglob("*.css"))
        normalized_css = "".join(css.split())
        self.assertIn("@media(prefers-reduced-motion:reduce)", normalized_css)
        self.assertIn("[data-reveal].is-reveal-ready", normalized_css)
        self.assertIn(".editorial-header.is-compact .editorial-nav-container", css)

    def test_dark_theme_is_not_emitted(self):
        self.assertNotIn("theme-dropdown", self.homepage)


if __name__ == "__main__":
    unittest.main()
