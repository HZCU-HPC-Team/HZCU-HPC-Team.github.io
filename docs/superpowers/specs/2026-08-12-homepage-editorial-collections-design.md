# 首页 Introduction 与 Join Us 双栏预览设计

日期：2026-08-12  
状态：已确认

## 1. 目标

重构首页 `INTRODUCTION` 和 `JOIN US` 两个 Collection 模块，使栏目眉题和文章标题位于模块左上，结构化文章节选填充模块右侧。设计继续使用全站既有的暖色编辑式视觉语言，并保持内容由 Hugo Markdown 管理。

成功标准：

- 桌面端形成稳定的左侧标题区与右侧内容区，比例约为 38% / 62%。
- `INTRODUCTION` 和 `JOIN US` 是左上角的小型栏目眉题，文章标题紧随其下。
- 右侧展示包含小标题、段落和列表的结构化节选，而不是纯文本自动摘要。
- 移动端按照栏目眉题、文章标题、阅读链接、结构化节选的自然顺序折叠为单列。
- 两个模块不显示特色图，右侧空间完整用于文字内容。
- 改动不影响 Post、Diary 等使用通用 Editorial View 的列表。

## 2. 范围与非目标

### 2.1 本次范围

- 调整首页两个 Collection 的 View 配置和栏目字段。
- 新增一个首页专用 Collection View。
- 为两篇 Recruitment 文章增加首页专用结构化节选字段。
- 在首页 SCSS 中增加专用双栏和响应式样式。
- 更新生成站点回归测试，覆盖结构、语义、降级和 CSS 契约。

### 2.2 非目标

- 不改写两篇文章的完整正文。
- 不修改文章详情页设计。
- 不改变 Collection 的分类筛选逻辑。
- 不修改通用 `.editorial-entry` View 或其他列表页布局。
- 不增加图片、轮播、折叠面板或客户端内容加载。
- 不把整个模块变成单一大链接。

## 3. 方案选择

采用**独立首页 Collection View**，文件为：

```text
layouts/partials/views/homepage-preview.html
```

首页两个 Collection 显式设置：

```yaml
design:
  view: homepage-preview
  columns: '1'
```

选择该方案的原因：

- 保留 Hugo Blox Collection 的查询、排序和分类筛选能力。
- 首页结构与通用文章条目结构相互隔离，避免在 `editorial.html` 中加入页面或分类条件分支。
- 模板输出可直接通过生成 HTML 回归测试验证。
- 后续首页布局调整不会误伤 Post、Diary 等列表，通用列表改动也不会影响本模块。

不采用的方案：

1. **在现有 Editorial View 中加入首页条件分支：** 文件较少，但会把首页特例混入全站通用条目模板，增加双向回归风险。
2. **改为 Markdown 或自定义 Block 并直接指定文章：** 结构控制最强，但会削弱现有分类驱动的内容模型，并让首页配置重复文章信息。

## 4. 内容模型

### 4.1 Collection 配置

两个 Collection 保持现有 ID、页面类型和分类筛选：

- `id: introduction`，筛选 `page_type: recruitment` 与 `category: introduction`。
- `id: join-us`，筛选 `page_type: recruitment` 与 `category: join-us`。

主题默认的 Section Heading 不应继续生成在条目上方。首页配置改用专用栏目字段：

```yaml
content:
  title:
  eyebrow: INTRODUCTION
```

`JOIN US` 使用同样结构。专用 View 通过传入的 Collection Block 读取 `content.eyebrow`。这样栏目文字可以进入文章条目的左侧 Header，同时避免通过 CSS 搬移独立 DOM 或保留重复的隐藏标题。

`id="introduction"` 和 `id="join-us"` 保持不变，现有锚点与测试仍可定位对应模块。

### 4.2 结构化节选字段

两篇文章分别增加 Markdown 类型的 `homepage_preview` Front Matter 字段，例如：

```yaml
homepage_preview: |
  ### 我们是谁？

  浙大城市学院超算队是……

  ### 我们参加的比赛

  - ASC 世界大学生超级计算机竞赛
  - IPCC 国际并行计算挑战赛
```

该字段只控制首页节选，不替代文章正文。内容编辑者可以独立调整首页篇幅和信息层级，而不必改变正文开头或依赖自动截断。

### 4.3 内容约束

- `homepage_preview` 可以包含小标题、段落、强调、列表和普通内链。
- 不在节选中嵌入图片、短代码、表格或脚本。
- 节选应概括正文现有内容，不新增正文中不存在的事实。
- 节选自然决定模块高度，不做字符裁切、固定高度或内部滚动。
- 两个节选应控制在相近的信息密度，但不要求像素级等高。

### 4.4 降级策略

若 `homepage_preview` 缺失或渲染后为空，View 按以下顺序降级：

1. Front Matter `summary`；
2. Hugo `.Summary`；
3. 若以上均为空，则只输出栏目眉题、文章标题和阅读链接，不生成空白右栏占位；条目增加 `.homepage-preview--text-only` 修饰类并收敛为单列标题区。

降级摘要作为普通文字输出，不伪造结构化标题。

## 5. 模板结构与数据流

Hugo Blox Collection Block 继续执行现有查询和排序，并通过 `functions/render_view` 将以下数据传给专用 View：

- `page`：当前 Collection Block，可读取 `content.eyebrow`；
- `item`：匹配的 Recruitment 页面；
- `index`：Collection 内条目索引。

专用 View 输出语义结构：

```html
<article class="homepage-preview" data-reveal>
  <header class="homepage-preview__header">
    <h2 class="homepage-preview__eyebrow">INTRODUCTION</h2>
    <h3 class="homepage-preview__title">
      <a href="…">浙大城市学院超算队介绍</a>
    </h3>
    <a class="homepage-preview__read" href="…">阅读全文 →</a>
  </header>

  <div class="homepage-preview__content article-style">
    <!-- homepage_preview 渲染后的结构化 HTML -->
  </div>
</article>
```

具体模板职责：

1. 从 `item.RelPermalink` 获取站内链接；若未来文章设置 `external_link`，沿用安全的新窗口属性处理方式。
2. 从 Collection Block 获取栏目眉题，不根据标题文本、URL、Section ID 或分类名作隐式判断。
3. 使用页面上下文渲染 `homepage_preview` Markdown，保留合法的段落、列表与链接。
4. 将结构化节选中的标题统一降一级，使作者在字段中自然书写 `###` 时，最终输出为 `<h4>`；文章条目自身的标题保持 `<h3>`。
5. 不请求、不处理也不输出 Featured Image。
6. 保留 `data-reveal`，沿用现有渐进增强机制。

如果以后某个分类匹配多篇文章，Collection 会按现有排序依次输出多个同构 `<article>`；不会把多篇文章合并进一个双栏网格。

## 6. 视觉布局

### 6.1 桌面端

每个 `.homepage-preview` 是一个两栏 Grid：

```text
┌─────────────────────────────────────────────────────────────┐
│  INTRODUCTION                                               │
│                                                             │
│  浙大城市学院超算队介绍     │  我们是谁？                   │
│                              │  结构化节选正文……             │
│  阅读全文 →                 │                              │
│                              │  我们参加的比赛               │
│                              │  结构化节选正文/列表……        │
└─────────────────────────────────────────────────────────────┘
```

- 使用 `grid-template-columns: minmax(0, 0.75fr) minmax(0, 1.25fr)`，形成约 38% / 62% 的列比例。
- 模块顶部使用 3px 陶土色强调线。
- 左栏顶部依次放置栏目眉题、文章标题和“阅读全文 →”。
- 栏目眉题使用小号、大写、增加字距的界面字体；文章标题使用编辑式衬线字体。
- 右栏使用 1px 左分隔线和内边距，不添加独立卡片背景、阴影或圆角。
- 右栏内容占满可用列宽，但正文单段保持舒适的阅读行长。
- 模块不设置固定高度；较长的 Join Us 节选可以自然拉高区块。
- 模块之间继续使用页面现有的边线和留白形成节奏。

### 6.2 移动端

在现有移动端断点 `47.99rem` 以下改为单列。DOM 顺序与视觉顺序一致：

1. 栏目眉题；
2. 文章标题；
3. “阅读全文 →”；
4. 水平分隔线；
5. 结构化节选。

移动端要求：

- 不隐藏节选，不使用折叠交互。
- 正文不低于 16px。
- 移除右栏左边线，改为内容顶部水平分隔线。
- 保持全局 `--page-gutter`，避免内容贴边。
- 标题和节选不通过 CSS `order` 重新排序。

### 6.3 多条目行为

当前每个分类只有一篇文章。若未来新增多篇：

- 每篇文章生成一个完整 `.homepage-preview`。
- 每篇条目都有自己的顶部边线、标题区和内容区。
- 栏目眉题只在该 Collection 的第一篇条目中输出，后续条目保留文章标题和阅读链接，避免重复朗读同一模块标题。
- 第一篇之后的条目仍维持 `<h3>` 文章标题层级。

## 7. 样式边界

样式写入现有：

```text
assets/scss/pages/_home.scss
```

仅使用以下专用命名空间：

```scss
.homepage-preview
.homepage-preview__header
.homepage-preview__eyebrow
.homepage-preview__title
.homepage-preview__read
.homepage-preview__content
```

第一篇条目通过 `.homepage-preview--first` 修饰类标记，以控制栏目眉题只输出一次；不得复用或改写通用 `.editorial-entry` 的布局规则。

现有 `_home.scss` 中仅针对默认 `#section-collection .editorial-entry:first-child` 的规则会在新 View 下失效，应删除或替换为专用选择器，避免保留死样式。

颜色、字体、间距和断点复用现有 Design Tokens，不引入新的调色板或字体依赖。

## 8. 语义与可访问性

- 首页 Hero 保留唯一的 `<h1>`。
- 每个 Collection 的栏目眉题使用 `<h2>`。
- 每篇文章标题使用 `<h3>`。
- 结构化节选中由作者写入的三级 Markdown 标题最终输出为 `<h4>`，形成 `h1 → h2 → h3 → h4` 的清晰层级。
- 文章标题和“阅读全文 →”都是正常链接；整个 `<article>` 不作为链接。
- 阅读入口使用中文可见文本，最小触控高度为 44px。
- 标题链接和阅读链接沿用或扩展全局 `:focus-visible` 焦点环。
- Hover 只改变颜色、边线或下划线，不位移元素。
- 内容链接不能只靠颜色表示，至少保留下划线或其他非颜色提示。
- `data-reveal` 仅作渐进增强：没有 JavaScript 时内容可见；`prefers-reduced-motion` 下不执行位移动画。
- 右侧节选中的链接维持正常键盘顺序和可点击行为。

## 9. 测试设计

更新 `tests/test_generated_site.py`，验证生成 DOM 和编译 CSS，而不是只检查源文件字符串。

### 9.1 内容和 DOM

1. 首页仍包含 `INTRODUCTION`、`JOIN US` 及两篇文章标题。
2. `id="introduction"` 和 `id="join-us"` 各出现一次。
3. 两个模块各包含 `.homepage-preview`。
4. 栏目眉题为 `<h2 class="homepage-preview__eyebrow">`。
5. 文章标题为 `<h3 class="homepage-preview__title">`。
6. 标题链接和“阅读全文 →”均指向对应文章。
7. 右侧输出 Front Matter 中预期的小标题、段落和列表。
8. 节选标题最终为 `<h4>`，不引入额外 `<h1>` 或同级 `<h3>`。
9. 模块内不输出 Featured Image、`.editorial-entry__media` 或装饰性图片。
10. 首页仍只有 Hero 一个 `<h1>`。

### 9.2 CSS 契约

1. 桌面规则为两栏 Grid，比例约 38% / 62%。
2. 右侧内容包含左分隔线和内边距。
3. 阅读入口 `min-height` 至少为 44px。
4. 移动端断点将 Grid 改为单列。
5. 移动端移除左边线并增加顶部水平分隔线。
6. 不存在针对 `.homepage-preview` 的 Hover 位移动画。
7. Reduced Motion 契约继续覆盖 Reveal 行为。

### 9.3 降级与隔离

1. Fixture 中缺失 `homepage_preview` 的首页条目降级输出 `summary` 或 `.Summary`。
2. 缺失所有摘要时不输出空的 `.homepage-preview__content`。
3. 普通 Post、Diary 或 Recruitment 列表仍使用 `.editorial-entry`。
4. 专用 View 不改变文章详情页内容、标题或 Featured Image 行为。

## 10. 验证

实施完成后运行：

```bash
./scripts/test-site.sh
hugo --gc --minify
```

仓库要求 Hugo Extended 0.135.0。当前设计阶段环境中的 `hugo` 不在 `PATH`，实施验证前应使用已安装的正确版本，或沿用调用者提供的 `HUGO_BIN`。不得为执行验证而覆盖调用者提供的 `GOPROXY`、`GOSUMDB`、`GOMODCACHE` 或 `HUGO_BIN`。

若完整验证因本地缺少 Hugo 而无法运行，必须明确报告阻塞；不能把未执行的测试描述为通过。

## 11. 预计改动文件

```text
content/_index.md
content/recruitment/recruitment2408/index.md
content/recruitment/join-us/index.md
layouts/partials/views/homepage-preview.html
assets/scss/pages/_home.scss
tests/test_generated_site.py
```

除测试 Fixture 在测试运行期间创建的临时内容外，不需要修改其他页面模板或 JavaScript。