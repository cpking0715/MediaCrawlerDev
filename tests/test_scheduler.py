# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests/test_scheduler.py
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
工作台调度器单元测试：命令构建、平台顺序、运行记录（子进程用 mock）
"""

import pytest

from workbench import config as wb_config
from workbench import db as wb_db
from workbench.scheduler import WorkbenchScheduler, build_command, list_run_records


class FakeStdout:
    def __init__(self, lines):
        self._lines = list(lines)

    async def readline(self):
        if self._lines:
            return self._lines.pop(0)
        return b""


class FakeProcess:
    def __init__(self, lines=(), returncode=0):
        self.stdout = FakeStdout([line.encode("utf-8") + b"\n" for line in lines])
        self._returncode = returncode
        self.killed = False

    async def wait(self):
        return self._returncode

    def kill(self):
        self.killed = True


@pytest.fixture
def temp_db(tmp_path):
    """把工作台数据库指向临时文件，避免污染真实数据"""
    wb_db.set_db_path(str(tmp_path / "workbench_test.db"))
    wb_db.ensure_workbench_tables()
    yield
    wb_db.set_db_path(None)


def _arg_value(cmd, flag):
    return cmd[cmd.index(flag) + 1]


def test_build_command_contains_required_args():
    cmd = build_command("xhs", keywords="编程副业,编程兼职")
    assert _arg_value(cmd, "--platform") == "xhs"
    assert _arg_value(cmd, "--lt") == wb_config.WORKBENCH_LOGIN_TYPE
    assert _arg_value(cmd, "--type") == wb_config.WORKBENCH_CRAWLER_TYPE
    assert _arg_value(cmd, "--save_data_option") == "sqlite"
    assert _arg_value(cmd, "--keywords") == "编程副业,编程兼职"
    assert cmd[-1] != "" and "main.py" in cmd[cmd.index("main.py")]


def test_platforms_order_is_preserved():
    assert wb_config.WORKBENCH_PLATFORMS == ["xhs", "dy", "bili"]


@pytest.mark.asyncio
async def test_run_platform_records_success(temp_db, monkeypatch):
    scheduler = WorkbenchScheduler()

    async def fake_spawn(cmd):
        return FakeProcess(lines=["start crawl", "all done"], returncode=0)

    monkeypatch.setattr(scheduler, "_spawn", fake_spawn)
    counts = iter([5, 8])
    monkeypatch.setattr("workbench.scheduler.count_platform_records", lambda platform: next(counts))

    record = await scheduler.run_platform("xhs", trigger="manual")

    assert record is not None
    assert record.status == "success"
    assert record.exit_code == 0
    assert record.records_added == 3
    assert "all done" in record.log_tail

    runs = list_run_records(limit=10)
    assert len(runs) == 1
    assert runs[0]["platform"] == "xhs"
    assert runs[0]["status"] == "success"
    assert runs[0]["records_added"] == 3


@pytest.mark.asyncio
async def test_run_platform_records_failure(temp_db, monkeypatch):
    scheduler = WorkbenchScheduler()

    async def fake_spawn(cmd):
        return FakeProcess(lines=["login failed: cookie expired"], returncode=1)

    monkeypatch.setattr(scheduler, "_spawn", fake_spawn)

    record = await scheduler.run_platform("dy", trigger="cron")

    assert record.status == "failed"
    assert record.exit_code == 1
    assert "cookie expired" in record.log_tail
    assert not scheduler._busy
    assert scheduler.current_platform is None


@pytest.mark.asyncio
async def test_run_platform_spawn_error_marked_failed(temp_db, monkeypatch):
    scheduler = WorkbenchScheduler()

    async def fake_spawn(cmd):
        raise FileNotFoundError("uv not found")

    monkeypatch.setattr(scheduler, "_spawn", fake_spawn)

    record = await scheduler.run_platform("bili")

    assert record.status == "failed"
    assert "spawn failed" in record.log_tail


@pytest.mark.asyncio
async def test_busy_scheduler_rejects_new_run(temp_db):
    scheduler = WorkbenchScheduler()
    scheduler._busy = True
    assert await scheduler.run_platform("xhs") is None


@pytest.mark.asyncio
async def test_run_daily_iterates_platforms_in_order(temp_db, monkeypatch):
    scheduler = WorkbenchScheduler()
    executed = []

    async def fake_run_platform(platform, trigger="manual"):
        executed.append((platform, trigger))
        return None

    monkeypatch.setattr(scheduler, "run_platform", fake_run_platform)
    await scheduler.run_daily()

    assert executed == [(p, "cron") for p in wb_config.WORKBENCH_PLATFORMS]
