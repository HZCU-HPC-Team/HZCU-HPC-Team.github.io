# HZCU HPC Team

> 浙大城市学院高性能计算团队官方网站

[https://hzcu-hpc-team.github.io/](https://hzcu-hpc-team.github.io/)

## 关于我们

浙大城市学院高性能计算（HPC）团队是一个充满活力的学生团队，致力于高性能计算领域。团队成员来自不同的技术背景，在算法优化、程序设计、系统架构等方向不断探索，通过参与 ASC 等竞赛和研究项目提升技术水平，培养具备高性能计算技能的专业人才。

网站内容涵盖团队介绍、竞赛成果、日常记录、招新信息等。

## 技术栈

- **静态站点生成器：** [Hugo](https://gohugo.io/) Extended 0.135.0
- **主题：** [Hugo Blox](https://hugoblox.com/)（原 Wowchemy），通过 Hugo Modules 加载
- **样式：** 模块化 SCSS，自定义「暖色调编辑风」设计系统
- **脚本：** 渐进增强（吸顶导航栏、滚动入场动画）
- **部署：** GitHub Pages（主） + Netlify（备）

## 本地开发

### 环境要求

- Hugo Extended 0.135.0
- Go 工具链（用于 Hugo 模块拉取）

### 启动开发服务器

```bash
hugo server --buildDrafts --buildFuture --bind 127.0.0.1 --port 1313
```

### 生产构建

```bash
# GitHub Pages
HUGO_ENVIRONMENT=production hugo --minify --baseURL "https://hpc.hzcu.edu.cn/"

# Netlify
hugo --gc --minify -b "https://hpc.hzcu.edu.cn/"
```

### 测试

```bash
./scripts/test-site.sh
```

## 项目结构

```txt
content/           # 网站内容（Markdown + YAML 前置元数据）
  authors/         # 团队成员档案
  post/            # 新闻与公告
  daily/           # 团队日常记录
  recruitment/     # 招新页面
  memory/          # 团队回忆录
  accomplishments/ # 获奖成就
  publication/     # 学术发表
assets/            # SCSS、JS、图片等静态资源
layouts/           # Hugo 模板覆盖
config/_default/   # Hugo 配置文件
```

## 部署

推送到 `main` 分支后，GitHub Actions（`.github/workflows/publish.yaml`）自动构建并部署到 GitHub Pages。Netlify 部署配置见 `netlify.toml`。

## 致谢

本项目基于开源项目 [Hugo Blox](https://hugoblox.com/)（Wowchemy）的 Research Group 模板构建，并在此基础上定制了「暖色调编辑风」视觉主题，感谢开源社区的支持。
