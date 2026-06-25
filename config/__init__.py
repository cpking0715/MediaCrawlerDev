# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/config/__init__.py
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


import os
from .base_config import *
from .db_config import *

# 如果配置了 KEYWORDS_FILE 且文件存在，从文件逐行读取关键词
if KEYWORDS_FILE:
    keywords_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), KEYWORDS_FILE)
    if os.path.exists(keywords_path):
        with open(keywords_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        if lines:
            KEYWORDS = ",".join(lines)  # 转为逗号分隔字符串，兼容现有 split(",") 逻辑
