# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/workbench/models.py
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
工作台自有数据模型：采集任务运行记录
"""

from sqlalchemy import Column, Integer, String, Text, BigInteger

from database.models import Base


class TaskRun(Base):
    """单次平台采集任务的运行记录"""

    __tablename__ = "workbench_task_run"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    platform = Column(String(32), index=True, nullable=False, comment="平台: xhs|dy|bili 等")
    trigger = Column(String(16), default="cron", comment="触发方式: cron|manual")
    status = Column(String(16), index=True, default="running", comment="状态: running|success|failed|timeout")
    started_at = Column(BigInteger, comment="开始时间戳(毫秒)")
    finished_at = Column(BigInteger, comment="结束时间戳(毫秒)")
    exit_code = Column(Integer, comment="子进程退出码")
    records_added = Column(Integer, default=0, comment="本次新增数据条数")
    log_tail = Column(Text, default="", comment="运行日志尾部")
