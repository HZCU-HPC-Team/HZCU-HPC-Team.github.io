---
# Leave the homepage title empty to use the site title
title: HZCU-HPCT
date: 2022-10-24
type: landing

sections:
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


---
