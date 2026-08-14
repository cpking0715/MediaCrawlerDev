# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/workbench/scheduler.py
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
工作台调度器：基于 APScheduler 的每日定时采集，
按平台串行以子进程方式运行 main.py，并把运行记录写入 workbench_task_run 表
"""

import asyncio
import shutil
import sys
import time
from collections import deque
from typing import List, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from tools import utils
from workbench import config as wb_config
from workbench.db import count_platform_records, ensure_workbench_tables, get_session_factory
from workbench.models import TaskRun

DAILY_JOB_ID = "workbench_daily_crawl"


def build_command(platform: str, keywords: Optional[str] = None) -> List[str]:
    """构建单平台采集命令，参考 api/services/crawler_manager.py 的 _build_command"""
    if shutil.which("uv"):
        cmd = ["uv", "run", "python", "main.py"]
    else:
        cmd = [sys.executable, "main.py"]

    cmd.extend(["--platform", platform])
    cmd.extend(["--lt", wb_config.WORKBENCH_LOGIN_TYPE])
    cmd.extend(["--type", wb_config.WORKBENCH_CRAWLER_TYPE])
    cmd.extend(["--save_data_option", wb_config.WORKBENCH_SAVE_DATA_OPTION])

    if wb_config.WORKBENCH_CRAWLER_TYPE == "search":
        kw = keywords if keywords is not None else wb_config.load_keywords()
        if kw:
            cmd.extend(["--keywords", kw])

    return cmd


class WorkbenchScheduler:
    """每日定时采集调度器（FastAPI 单进程内常驻）"""

    def __init__(self):
        self._scheduler: Optional[AsyncIOScheduler] = None
        self._busy = False
        self.current_platform: Optional[str] = None

    # ---------- 调度器生命周期 ----------

    def start(self) -> None:
        ensure_workbench_tables()
        self._scheduler = AsyncIOScheduler()
        self._scheduler.add_job(
            self.run_daily,
            CronTrigger(hour=wb_config.WORKBENCH_DAILY_HOUR, minute=wb_config.WORKBENCH_DAILY_MINUTE),
            id=DAILY_JOB_ID,
            replace_existing=True,
        )
        self._scheduler.start()
        utils.logger.info(
            f"[Workbench] scheduler started, daily at "
            f"{wb_config.WORKBENCH_DAILY_HOUR:02d}:{wb_config.WORKBENCH_DAILY_MINUTE:02d}, "
            f"platforms: {wb_config.WORKBENCH_PLATFORMS}"
        )

    def shutdown(self) -> None:
        if self._scheduler:
            self._scheduler.shutdown(wait=False)
            self._scheduler = None

    def next_run_time(self) -> Optional[str]:
        if not self._scheduler:
            return None
        job = self._scheduler.get_job(DAILY_JOB_ID)
        if job and job.next_run_time:
            return job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
        return None

    def status(self) -> dict:
        return {
            "running": self._busy,
            "current_platform": self.current_platform,
            "next_run_time": self.next_run_time(),
            "daily_time": f"{wb_config.WORKBENCH_DAILY_HOUR:02d}:{wb_config.WORKBENCH_DAILY_MINUTE:02d}",
            "platforms": wb_config.WORKBENCH_PLATFORMS,
            "crawler_type": wb_config.WORKBENCH_CRAWLER_TYPE,
            "login_type": wb_config.WORKBENCH_LOGIN_TYPE,
            "keywords": wb_config.load_keywords(),
            "platform_timeout_seconds": wb_config.WORKBENCH_PLATFORM_TIMEOUT_SECONDS,
        }

    # ---------- 采集执行 ----------

    async def run_daily(self) -> None:
        """每日定时任务：按配置顺序串行采集各平台"""
        if self._busy:
            utils.logger.warning("[Workbench] daily crawl skipped, another crawl is running")
            return
        for platform in wb_config.WORKBENCH_PLATFORMS:
            await self.run_platform(platform, trigger="cron")

    async def run_platform(self, platform: str, trigger: str = "manual") -> Optional[TaskRun]:
        """运行单个平台的采集子进程并记录结果；忙碌时返回 None"""
        if self._busy:
            return None

        self._busy = True
        self.current_platform = platform
        run_record = self._create_run_record(platform, trigger)
        before_count = count_platform_records(platform)
        cmd = build_command(platform)
        utils.logger.info(f"[Workbench] start crawl: {' '.join(cmd)}")

        log_tail = deque(maxlen=wb_config.WORKBENCH_LOG_TAIL_LINES)
        exit_code: Optional[int] = None
        status = "failed"

        try:
            process = await self._spawn(cmd)
            try:
                exit_code = await asyncio.wait_for(
                    self._drain_output(process, log_tail),
                    timeout=wb_config.WORKBENCH_PLATFORM_TIMEOUT_SECONDS,
                )
                status = "success" if exit_code == 0 else "failed"
            except asyncio.TimeoutError:
                status = "timeout"
                utils.logger.warning(f"[Workbench] crawl timeout for platform: {platform}")
                try:
                    process.kill()
                except Exception:
                    pass
                await process.wait()
        except FileNotFoundError as e:
            log_tail.append(f"spawn failed: {e}")
        except Exception as e:
            log_tail.append(f"unexpected error: {e}")

        records_added = max(count_platform_records(platform) - before_count, 0)
        self._finish_run_record(run_record, status, exit_code, records_added, "\n".join(log_tail))
        utils.logger.info(
            f"[Workbench] crawl finished: platform={platform}, status={status}, "
            f"exit_code={exit_code}, records_added={records_added}"
        )

        self._busy = False
        self.current_platform = None
        return run_record

    async def _spawn(self, cmd: List[str]):
        """启动采集子进程（独立方法便于测试 mock）"""
        return await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(wb_config.PROJECT_ROOT),
        )

    @staticmethod
    async def _drain_output(process, log_tail: deque) -> int:
        """持续读取子进程输出到日志尾部缓冲，返回退出码"""
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            text = line.decode("utf-8", errors="replace").rstrip()
            if text:
                log_tail.append(text)
                utils.logger.info(f"[Crawler] {text}")
        return await process.wait()

    # ---------- 运行记录持久化 ----------

    @staticmethod
    def _create_run_record(platform: str, trigger: str) -> TaskRun:
        record = TaskRun(
            platform=platform,
            trigger=trigger,
            status="running",
            started_at=int(time.time() * 1000),
        )
        session_factory = get_session_factory()
        with session_factory() as session:
            session.add(record)
            session.commit()
            session.refresh(record)
        return record

    @staticmethod
    def _finish_run_record(
        record: TaskRun,
        status: str,
        exit_code: Optional[int],
        records_added: int,
        log_tail: str,
    ) -> None:
        session_factory = get_session_factory()
        with session_factory() as session:
            db_record = session.get(TaskRun, record.id)
            if db_record:
                db_record.status = status
                db_record.exit_code = exit_code
                db_record.records_added = records_added
                db_record.log_tail = log_tail
                db_record.finished_at = int(time.time() * 1000)
                session.commit()
            record.status = status
            record.exit_code = exit_code
            record.records_added = records_added
            record.log_tail = log_tail


def list_run_records(limit: int = 50, platform: Optional[str] = None) -> List[dict]:
    """查询运行记录（按时间倒序）"""
    session_factory = get_session_factory()
    with session_factory() as session:
        query = session.query(TaskRun)
        if platform:
            query = query.filter(TaskRun.platform == platform)
        query = query.order_by(TaskRun.id.desc()).limit(limit)
        return [
            {
                "id": r.id,
                "platform": r.platform,
                "trigger": r.trigger,
                "status": r.status,
                "started_at": r.started_at,
                "finished_at": r.finished_at,
                "exit_code": r.exit_code,
                "records_added": r.records_added,
                "log_tail": r.log_tail,
            }
            for r in query.all()
        ]


# 全局单例
workbench_scheduler = WorkbenchScheduler()
