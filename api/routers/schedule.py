# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/api/routers/schedule.py
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
工作台调度 API：调度状态、手动触发、运行历史
"""

import asyncio
from typing import Optional

from fastapi import APIRouter, HTTPException

from workbench import config as wb_config
from workbench.scheduler import list_run_records, workbench_scheduler

router = APIRouter(prefix="/schedule", tags=["schedule"])

VALID_PLATFORMS = {"xhs", "dy", "ks", "bili", "wb", "tieba", "zhihu"}


@router.get("/status")
async def get_schedule_status():
    """Get scheduler status: next run time, platforms, keywords, running state"""
    return workbench_scheduler.status()


@router.get("/runs")
async def get_run_history(limit: int = 50, platform: Optional[str] = None):
    """Get crawl run history (newest first)"""
    runs = await asyncio.to_thread(list_run_records, limit, platform)
    return {"runs": runs}


@router.post("/run/{platform}")
async def trigger_manual_run(platform: str):
    """Manually trigger a crawl for one platform (runs in background)"""
    if platform not in VALID_PLATFORMS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid platform: {platform}. Supported: {sorted(VALID_PLATFORMS)}",
        )
    if workbench_scheduler._busy:
        raise HTTPException(status_code=400, detail="A crawl task is already running")

    asyncio.create_task(workbench_scheduler.run_platform(platform, trigger="manual"))
    return {
        "status": "ok",
        "message": f"Crawl started for platform: {platform}",
        "platform": platform,
    }


@router.post("/run")
async def trigger_manual_run_all():
    """Manually trigger the full daily crawl (all configured platforms, sequential)"""
    if workbench_scheduler._busy:
        raise HTTPException(status_code=400, detail="A crawl task is already running")

    asyncio.create_task(workbench_scheduler.run_daily())
    return {
        "status": "ok",
        "message": "Daily crawl started",
        "platforms": wb_config.WORKBENCH_PLATFORMS,
    }
