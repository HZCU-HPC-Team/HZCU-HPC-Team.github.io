---
# Leave the homepage title empty to use the site title
title:
date: 2022-10-24
type: landing

sections:
  - block: hero
    content:
      title: |
        HZCU
        High-Performance Computing Team
      image:
        filename: welcome.jpg
      text: |
        <br>
        
        杭州城市大学高性能计算 （HPC） 团队是一个充满活力的学生团队，致力于解决高性能计算挑战.
  
  - block: collection
    content:
      title: Latest News
      subtitle:
      text:
      count: 5
      filters:
        author: ''
        category: ''
        exclude_featured: false
        publication_type: ''
        tag: ''
      offset: 0
      order: desc
      page_type: post
    design:
      view: card
      columns: '1'
  
  - block: markdown
    content:
      title: Accomplishments
      text: |
        - **IPCC Excellence Award**  
          *Date:* Aug. 2022

        - **CPC Excellence Award**  
          *Date:* Aug. 2023

        - **ASC2024 Second Prize**  
          *Date:* Feb. 2024
    design:
      columns: '1'

  - block: collection
    content:
      title: Latest Preprints
      text: ""
      count: 5
      filters:
        folders:
          - publication
        publication_type: 'article'
    design:
      view: citation
      columns: '1'

  - block: markdown
    content:
      title:
      subtitle:
      text: |
        {{% cta cta_link="./people/" cta_text="Meet the team →" %}}
    design:
      columns: '1'
---
