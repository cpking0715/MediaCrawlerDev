# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/workbench/db.py
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
工作台数据库工具：与爬虫共用 SQLite 数据库（同步引擎），
负责任务表建表与平台数据行数统计
"""

from typing import Dict, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from config.db_config import sqlite_db_config
from database.models import Base

import workbench.models  # noqa: F401  注册 TaskRun 到 Base.metadata

_engine = None
_SessionFactory = None
_db_path_override: Optional[str] = None

# 各平台计入"新增条数"统计的表（内容表 + 评论表）
PLATFORM_COUNT_TABLES: Dict[str, list] = {
    "xhs": ["xhs_note", "xhs_note_comment"],
    "dy": ["douyin_aweme", "douyin_aweme_comment"],
    "bili": ["bilibili_video", "bilibili_video_comment"],
    "ks": ["kuaishou_video", "kuaishou_video_comment"],
    "wb": ["weibo_note", "weibo_note_comment"],
    "tieba": ["tieba_note", "tieba_comment"],
    "zhihu": ["zhihu_content", "zhihu_comment"],
}


def set_db_path(path: Optional[str]) -> None:
    """覆盖数据库路径（测试用），传 None 恢复默认路径"""
    global _db_path_override, _engine, _SessionFactory
    _db_path_override = path
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionFactory = None


def get_db_path() -> str:
    return _db_path_override or sqlite_db_config["db_path"]


def get_sync_engine():
    """获取与爬虫共用的 SQLite 同步引擎（懒加载单例）"""
    global _engine, _SessionFactory
    if _engine is None:
        _engine = create_engine(
            f"sqlite:///{get_db_path()}",
            connect_args={"check_same_thread": False},
        )
        _SessionFactory = sessionmaker(bind=_engine, expire_on_commit=False)
    return _engine


def get_session_factory():
    get_sync_engine()
    return _SessionFactory


def ensure_workbench_tables() -> None:
    """确保工作台及平台数据表存在（checkfirst，幂等）"""
    Base.metadata.create_all(get_sync_engine())


def count_platform_records(platform: str) -> int:
    """统计某平台内容表+评论表的总行数，用于计算单次采集新增条数"""
    tables = PLATFORM_COUNT_TABLES.get(platform, [])
    if not tables:
        return 0
    total = 0
    with get_sync_engine().connect() as conn:
        for table in tables:
            try:
                total += conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar() or 0
            except Exception:
                # 表尚未创建等情况，按 0 计
                continue
    return total
