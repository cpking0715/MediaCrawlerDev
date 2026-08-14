# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/api/routers/analysis.py
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
工作台分析 API：每日汇总、趋势、热门排行、关键词词频、关键词相关用户与用户画像
查询为同步 SQLite 操作，放线程池执行避免阻塞事件循环
"""

import asyncio
from typing import Optional

from fastapi import APIRouter

from ..services import analysis_service

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/summary")
async def get_summary():
    """Get daily crawl summary: per-platform totals and today's new records"""
    return await asyncio.to_thread(analysis_service.get_summary)


@router.get("/trends")
async def get_trends(days: int = 14):
    """Get per-day note count trends for the last N days"""
    return await asyncio.to_thread(analysis_service.get_trends, days)


@router.get("/hot")
async def get_hot(limit: int = 20, days: int = 30):
    """Get hot content ranking by liked count"""
    return await asyncio.to_thread(analysis_service.get_hot, limit, days)


@router.get("/keywords")
async def get_keywords(days: int = 7, top: int = 30):
    """Get keyword frequency from recent note titles/descriptions and comments"""
    return await asyncio.to_thread(analysis_service.get_keywords, days, top)


@router.get("/users")
async def get_keyword_users(
    keyword: Optional[str] = None,
    platform: Optional[str] = None,
    days: int = 30,
    limit: int = 50,
):
    """Get users related to a keyword: authors of matched content and commenters"""
    return await asyncio.to_thread(
        analysis_service.get_keyword_users, keyword, platform, days, limit
    )


@router.get("/user_profile")
async def get_user_profile(platform: str, user_id: str):
    """Get a single user's profile with all crawled notes and comments"""
    return await asyncio.to_thread(analysis_service.get_user_profile, platform, user_id)


@router.get("/topic_heat")
async def get_topic_heat(days: int = 90, top: int = 5):
    """Get product-direction topic heat: per-topic volume, engagement, hot words and top content/comments"""
    return await asyncio.to_thread(analysis_service.get_topic_heat, days, top)
