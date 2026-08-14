# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/workbench/topics.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#
# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

"""
产品方向（赛道）配置：分析层按此把采集到的内容归类到各赛道，
统计热度与爆点，帮助发现合适的 vibe coding 产品方向。

- name: 赛道名（仪表盘展示）
- keywords: 命中词列表，内容标题/描述/采集来源词包含任一词即归入该赛道（不区分大小写）
一条内容只归入最先命中的赛道，避免重复计数；可自行增删赛道与命中词。
"""

from typing import Dict, List

TOPIC_GROUPS: List[Dict] = [
    {
        "name": "AI编程/Vibe Coding",
        "keywords": ["vibe coding", "ai编程", "ai写代码", "cursor", "claude code", "trae"],
    },
    {
        "name": "副业变现/一人公司",
        "keywords": ["编程副业", "编程兼职", "副业", "变现", "一人公司", "独立开发", "出海"],
    },
    {
        "name": "小程序/H5",
        "keywords": ["小程序", "h5", "微信开发"],
    },
    {
        "name": "网站/落地页",
        "keywords": ["建站", "官网", "落地页", "网页开发"],
    },
    {
        "name": "小游戏",
        "keywords": ["小游戏", "游戏开发", "h5游戏"],
    },
    {
        "name": "效率工具/插件",
        "keywords": ["效率工具", "浏览器插件", "chrome插件", "自动化脚本", "办公自动化"],
    },
    {
        "name": "AI绘图/设计",
        "keywords": ["ai绘画", "ai绘图", "midjourney", "sd绘画"],
    },
    {
        "name": "AI Agent/数字人",
        "keywords": ["ai agent", "智能体", "数字人", "ai客服", "chatbot"],
    },
    {
        "name": "电商/营销工具",
        "keywords": ["tiktok推广", "电商工具", "带货", "营销工具", "进销存", "erp"],
    },
]
