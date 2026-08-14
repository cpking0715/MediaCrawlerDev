# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests/test_analysis_api.py
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
工作台分析 API 测试：临时 SQLite 构造测试数据，验证四个分析接口返回结构
"""

import time

import pytest
from fastapi.testclient import TestClient

from api.main import app
from database.models import (
    BilibiliVideo,
    DouyinAweme,
    DouyinAwemeComment,
    XhsNote,
    XhsNoteComment,
)
from workbench import db as wb_db

NOW_MS = int(time.time() * 1000)
THREE_DAYS_AGO_MS = NOW_MS - 3 * 24 * 3600 * 1000


def _seed_data():
    session_factory = wb_db.get_session_factory()
    with session_factory() as session:
        session.add_all([
            XhsNote(
                note_id="xhs_1", title="数据分析入门指南", desc="数据分析 教程",
                add_ts=NOW_MS, last_modify_ts=NOW_MS, liked_count="1000",
                nickname="作者A", note_url="https://example.com/xhs/1",
            ),
            XhsNote(
                note_id="xhs_2", title="数据分析进阶", desc="数据分析 实战",
                add_ts=NOW_MS, last_modify_ts=NOW_MS, liked_count="500",
                nickname="作者B", note_url="https://example.com/xhs/2",
            ),
            XhsNote(
                note_id="xhs_3", title="三天前的旧笔记", desc="",
                add_ts=THREE_DAYS_AGO_MS, last_modify_ts=THREE_DAYS_AGO_MS,
                liked_count="100", nickname="作者C", note_url="https://example.com/xhs/3",
            ),
            XhsNoteComment(
                comment_id="c_1", note_id="xhs_1", content="数据分析很有帮助",
                add_ts=NOW_MS, last_modify_ts=NOW_MS, create_time=NOW_MS,
            ),
            XhsNoteComment(
                comment_id="c_2", note_id="xhs_1", content="学到了数据分析技巧",
                add_ts=NOW_MS, last_modify_ts=NOW_MS, create_time=NOW_MS,
            ),
            DouyinAweme(
                aweme_id=2001, title="热门数据分析视频", desc="数据分析副业",
                add_ts=NOW_MS, last_modify_ts=NOW_MS, liked_count="9999",
                nickname="作者D", aweme_url="https://example.com/dy/2001",
                user_id="dy_u1", sec_uid="sec_dy_u1", ip_location="北京",
                user_signature="数据博主", source_keyword="数据分析",
                create_time=NOW_MS // 1000,
            ),
            DouyinAwemeComment(
                comment_id=9001, aweme_id=2001, content="一直想学数据分析",
                add_ts=NOW_MS, last_modify_ts=NOW_MS, create_time=NOW_MS // 1000,
                user_id="dy_u2", nickname="评论者小王", ip_location="上海",
            ),
            BilibiliVideo(
                video_id=3001, title="B站数据分析课程", desc="数据分析",
                add_ts=NOW_MS, last_modify_ts=NOW_MS, liked_count=88,
                nickname="作者E", video_url="https://example.com/bili/3001",
            ),
        ])
        session.commit()


@pytest.fixture
def client(tmp_path):
    """临时数据库 + 测试数据 + TestClient（触发 lifespan 验证调度器启停）"""
    wb_db.set_db_path(str(tmp_path / "analysis_test.db"))
    wb_db.ensure_workbench_tables()
    _seed_data()
    with TestClient(app) as test_client:
        yield test_client
    wb_db.set_db_path(None)


def test_summary_returns_per_platform_counts(client):
    resp = client.get("/api/analysis/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert "date" in data
    by_platform = {p["platform"]: p for p in data["platforms"]}
    assert set(by_platform.keys()) == {"xhs", "dy", "bili"}
    assert by_platform["xhs"]["note_total"] == 3
    assert by_platform["xhs"]["note_today"] == 2
    assert by_platform["xhs"]["comment_today"] == 2
    assert by_platform["dy"]["note_total"] == 1
    assert by_platform["bili"]["note_total"] == 1


def test_trends_returns_date_series(client):
    resp = client.get("/api/analysis/trends", params={"days": 7})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["dates"]) == 7
    assert set(data["series"].keys()) == {"xhs", "dy", "bili"}
    # xhs 三条笔记都落在近 7 天窗口内
    assert sum(data["series"]["xhs"]) == 3
    # 今天应有 xhs 两条新增
    assert data["series"]["xhs"][-1] == 2


def test_hot_ranks_by_liked_count(client):
    resp = client.get("/api/analysis/hot", params={"limit": 20, "days": 30})
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 5
    assert items[0]["platform"] == "dy"
    assert items[0]["liked_count"] == 9999
    assert items[0]["url"] == "https://example.com/dy/2001"
    liked_values = [it["liked_count"] for it in items]
    assert liked_values == sorted(liked_values, reverse=True)


def test_keywords_returns_word_frequency(client):
    resp = client.get("/api/analysis/keywords", params={"days": 7, "top": 30})
    assert resp.status_code == 200
    words = resp.json()["words"]
    assert len(words) > 0
    assert all(set(w.keys()) == {"word", "count"} for w in words)
    counts = {w["word"]: w["count"] for w in words}
    # "数据分析"在标题/描述/评论中多次出现，分词结果（数据分析或分析）应能统计到
    fenxi_count = sum(c for w, c in counts.items() if "分析" in w)
    assert fenxi_count >= 2
    assert words[0]["count"] >= words[-1]["count"]


def test_schedule_status_endpoint(client):
    resp = client.get("/api/schedule/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["platforms"] == ["xhs", "dy", "bili"]
    assert data["running"] is False
    assert "next_run_time" in data


def test_schedule_runs_endpoint_empty(client):
    resp = client.get("/api/schedule/runs")
    assert resp.status_code == 200
    assert resp.json()["runs"] == []


def test_keyword_users_returns_authors_and_commenters(client):
    resp = client.get("/api/analysis/users", params={"keyword": "数据分析", "days": 30})
    assert resp.status_code == 200
    data = resp.json()
    assert data["keyword"] == "数据分析"
    by_key = {(u["platform"], u["user_id"] or u["nickname"]): u for u in data["users"]}
    # 作者：发布命中关键词的内容
    author = by_key[("dy", "dy_u1")]
    assert "author" in author["roles"]
    assert author["note_count"] == 1
    assert author["total_liked"] == 9999
    assert author["ip_location"] == "北京"
    assert author["home_url"] == "https://www.douyin.com/user/sec_dy_u1"
    # 评论者：评论提及关键词（同时也评论了命中内容）
    commenter = by_key[("dy", "dy_u2")]
    assert "commenter" in commenter["roles"]
    assert commenter["comment_count"] == 1


def test_keyword_users_platform_filter(client):
    resp = client.get("/api/analysis/users", params={"platform": "dy", "days": 30})
    assert resp.status_code == 200
    assert {u["platform"] for u in resp.json()["users"]} == {"dy"}


def test_user_profile_returns_notes_and_comments(client):
    # 作者画像：含作品与主页链接
    resp = client.get("/api/analysis/user_profile", params={"platform": "dy", "user_id": "dy_u1"})
    assert resp.status_code == 200
    profile = resp.json()
    assert profile["nickname"] == "作者D"
    assert profile["signature"] == "数据博主"
    assert len(profile["notes"]) == 1
    assert profile["notes"][0]["liked_count"] == 9999
    assert profile["notes"][0]["create_time_ms"] > 10**12
    assert profile["comments"] == []
    # 评论者画像：评论关联到被评论作品标题
    resp = client.get("/api/analysis/user_profile", params={"platform": "dy", "user_id": "dy_u2"})
    profile = resp.json()
    assert profile["notes"] == []
    assert len(profile["comments"]) == 1
    assert profile["comments"][0]["ref_title"] == "热门数据分析视频"


def test_user_profile_invalid_platform(client):
    resp = client.get("/api/analysis/user_profile", params={"platform": "nope", "user_id": "x"})
    assert resp.status_code == 200
    assert "error" in resp.json()


def test_topic_heat_classifies_and_ranks(client):
    resp = client.get("/api/analysis/topic_heat", params={"days": 30})
    assert resp.status_code == 200
    data = resp.json()
    topics = {t["name"]: t for t in data["topics"]}
    # 描述含"副业"的 dy 视频归入副业赛道
    side = topics["副业变现/一人公司"]
    assert side["note_count"] == 1
    assert side["total_liked"] == 9999
    assert side["avg_liked"] == 9999
    assert side["platforms"] == ["dy"]
    assert side["top_items"][0]["title"] == "热门数据分析视频"
    # 评论了赛道内容的评论也被归入
    assert side["comment_count"] == 1
    assert side["top_comments"][0]["content"] == "一直想学数据分析"
    assert "潜在机会方向" in side["hint"]
    # 未命中赛道排在其后，且提示补充采集
    assert data["topics"][0]["name"] == "副业变现/一人公司"
    assert all(t["note_count"] == 0 for t in data["topics"][1:])
    assert "尚未采集" in data["topics"][1]["hint"]
    # 赛道热词来自内容标题/描述分词
    assert any(w["word"] == "数据分析" for w in side["hot_words"])
