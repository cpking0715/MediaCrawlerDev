# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/workbench/config.py
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
工作台集中配置：调度时间、目标平台、关键词、超时等
"""

import os
from pathlib import Path
from typing import List

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 每日采集的平台列表（按顺序串行执行），可选: xhs | dy | ks | bili | wb | tieba | zhihu
WORKBENCH_PLATFORMS: List[str] = ["xhs", "dy", "bili"]

# 每日定时运行时间（24小时制），默认每天 08:00
WORKBENCH_DAILY_HOUR = int(os.getenv("WORKBENCH_DAILY_HOUR", "8"))
WORKBENCH_DAILY_MINUTE = int(os.getenv("WORKBENCH_DAILY_MINUTE", "0"))

# 采集模式: search(关键词搜索) | detail(指定帖子) | creator(创作者主页)
WORKBENCH_CRAWLER_TYPE = "search"

# 登录方式: 定时场景建议使用 cookie（扫码登录无法无人值守）
WORKBENCH_LOGIN_TYPE = "cookie"

# 数据统一落 SQLite（自带去重），供分析层查询
WORKBENCH_SAVE_DATA_OPTION = "sqlite"

# 关键词来源：优先读取关键词文件（每行一个），不存在则回退到 WORKBENCH_KEYWORDS
WORKBENCH_KEYWORDS_FILE = str(PROJECT_ROOT / "keywords.txt")
WORKBENCH_KEYWORDS = "编程副业,编程兼职"

# 单个平台采集超时时间（秒）
WORKBENCH_PLATFORM_TIMEOUT_SECONDS = int(os.getenv("WORKBENCH_PLATFORM_TIMEOUT_SECONDS", "1800"))

# 运行日志保留的尾部行数（写入 task_run 记录）
WORKBENCH_LOG_TAIL_LINES = 30


def load_keywords() -> str:
    """读取关键词，逗号分隔。优先从 WORKBENCH_KEYWORDS_FILE 读取，文件不存在则用 WORKBENCH_KEYWORDS"""
    keywords_file = Path(WORKBENCH_KEYWORDS_FILE)
    if keywords_file.exists():
        lines = [
            line.strip()
            for line in keywords_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        if lines:
            return ",".join(lines)
    return WORKBENCH_KEYWORDS
