---
# Leave the homepage title empty to use the site title
title: HZCU-HPCT
date: 2022-10-24
type: landing

sections:
  - block: hero-terminal
    content:
      headline: Beyond the clock
      title: HZCU HPC Team
      tagline: 超越时钟，探索计算的极限
      aside_left: 浙大城市学院超算队隶属于学校超算中心，专注性能评估与优化，在 ASC、IPCC、CPC 等国际竞赛中屡获佳绩。
      aside_right: 对高性能计算、AI、GPU 计算等方向感兴趣？欢迎加入我们，一起探索计算科学的极限。
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

# ERROR：Bao Zhuhan: 当前Publication页面无实际超链接，该部分停用
  # - block: collection
  #   content:
  #     title: Latest Preprints
  #     text: ""
  #     count: 5
  #     filters:
  #       folders:
  #         - publication
  #       publication_type: 'article'
  #   design:
  #     view: citation
  #     columns: '1'

  - block: markdown
    content:
      title:
      subtitle:
      text: |
        {{% cta cta_link="./people/" cta_text="Meet the team →" %}}
    design:
      columns: '1'
    id: meet-the-team


---
