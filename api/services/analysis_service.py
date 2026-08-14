# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/api/services/analysis_service.py
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
工作台数据分析服务：直接查询 SQLite（同步引擎），
提供每日汇总、趋势、热门排行、关键词词频四类分析
"""

import re
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import jieba
from sqlalchemy import or_, types as sqlalchemy_types

from database.models import (
    BilibiliUpInfo,
    BilibiliVideo,
    BilibiliVideoComment,
    DouyinAweme,
    DouyinAwemeComment,
    DyCreator,
    XhsCreator,
    XhsNote,
    XhsNoteComment,
)
from workbench.config import PROJECT_ROOT
from workbench.db import get_session_factory
from workbench.topics import TOPIC_GROUPS

# 各平台分析配置：内容模型、评论模型、文本/链接字段、用户主页模板
PLATFORM_MODELS = {
    "xhs": {
        "label": "小红书",
        "note": XhsNote,
        "comment": XhsNoteComment,
        "url_col": "note_url",
        "note_id_col": "note_id",
        "comment_fk_col": "note_id",
        "home_tpl": "https://www.xiaohongshu.com/user/profile/{uid}",
    },
    "dy": {
        "label": "抖音",
        "note": DouyinAweme,
        "comment": DouyinAwemeComment,
        "url_col": "aweme_url",
        "note_id_col": "aweme_id",
        "comment_fk_col": "aweme_id",
        "home_tpl": "https://www.douyin.com/user/{uid}",
    },
    "bili": {
        "label": "B站",
        "note": BilibiliVideo,
        "comment": BilibiliVideoComment,
        "url_col": "video_url",
        "note_id_col": "video_id",
        "comment_fk_col": "video_id",
        "home_tpl": "https://space.bilibili.com/{uid}",
    },
}

# 创作者/UP主附加信息表（粉丝数、简介等）
CREATOR_MODELS = {
    "xhs": {"model": XhsCreator, "fans_col": "fans", "desc_col": "desc"},
    "dy": {"model": DyCreator, "fans_col": "fans", "desc_col": "desc"},
    "bili": {"model": BilibiliUpInfo, "fans_col": "total_fans", "desc_col": "sign"},
}

_stopwords: Optional[set] = None


def _load_stopwords() -> set:
    """加载停用词表（docs/hit_stopwords.txt），带缓存"""
    global _stopwords
    if _stopwords is None:
        _stopwords = set()
        stopwords_file = Path(PROJECT_ROOT) / "docs" / "hit_stopwords.txt"
        if stopwords_file.exists():
            _stopwords = {
                line.strip()
                for line in stopwords_file.read_text(encoding="utf-8").splitlines()
                if line.strip()
            }
    return _stopwords


def _parse_int(value) -> int:
    """点赞数等多为 Text 列，安全转 int"""
    if value is None:
        return 0
    try:
        return int(str(value).replace(",", "").strip())
    except (ValueError, TypeError):
        return 0


def _day_range_ms(day: datetime) -> tuple:
    """某天本地时间 [00:00, 24:00) 对应的毫秒时间戳区间"""
    start = day.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return int(start.timestamp() * 1000), int(end.timestamp() * 1000)


def _to_ms(ts) -> int:
    """内容发布时间统一转毫秒（兼容秒/毫秒两种存储）"""
    try:
        ts = int(ts or 0)
    except (ValueError, TypeError):
        return 0
    return ts * 1000 if ts < 10**12 else ts


def _content_time_ms(row) -> int:
    """内容发布时间：小红书用 time 列，其余平台用 create_time"""
    return _to_ms(getattr(row, "create_time", None) or getattr(row, "time", None))


def get_summary() -> dict:
    """今日概览：各平台内容/评论总量与今日新增"""
    now = datetime.now()
    day_start_ms, _ = _day_range_ms(now)
    result = {"date": now.strftime("%Y-%m-%d"), "platforms": []}

    session_factory = get_session_factory()
    with session_factory() as session:
        for platform, meta in PLATFORM_MODELS.items():
            note_total = session.query(meta["note"]).count()
            comment_total = session.query(meta["comment"]).count()
            note_today = session.query(meta["note"]).filter(meta["note"].add_ts >= day_start_ms).count()
            comment_today = (
                session.query(meta["comment"]).filter(meta["comment"].add_ts >= day_start_ms).count()
            )
            result["platforms"].append(
                {
                    "platform": platform,
                    "label": meta["label"],
                    "note_total": note_total,
                    "comment_total": comment_total,
                    "note_today": note_today,
                    "comment_today": comment_today,
                }
            )
    return result


def get_trends(days: int = 14) -> dict:
    """近 N 天各平台每日新增内容数走势（按 add_ts 归日）"""
    days = max(1, min(days, 90))
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_day = today - timedelta(days=days - 1)
    start_ms, _ = _day_range_ms(start_day)

    dates = [(start_day + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]
    series = {}

    session_factory = get_session_factory()
    with session_factory() as session:
        for platform, meta in PLATFORM_MODELS.items():
            counter = Counter()
            rows = session.query(meta["note"].add_ts).filter(meta["note"].add_ts >= start_ms).all()
            for (add_ts,) in rows:
                if add_ts:
                    counter[datetime.fromtimestamp(add_ts / 1000).strftime("%Y-%m-%d")] += 1
            series[platform] = [counter.get(d, 0) for d in dates]

    return {"dates": dates, "series": series}


def get_hot(limit: int = 20, days: int = 30) -> dict:
    """热门内容排行：近 N 天采集的内容按点赞数取 Top"""
    limit = max(1, min(limit, 100))
    start_ms, _ = _day_range_ms(datetime.now() - timedelta(days=days))

    candidates: List[dict] = []
    session_factory = get_session_factory()
    with session_factory() as session:
        for platform, meta in PLATFORM_MODELS.items():
            note_model = meta["note"]
            rows = (
                session.query(note_model)
                .filter(note_model.add_ts >= start_ms)
                .order_by(note_model.add_ts.desc())
                .limit(500)
                .all()
            )
            for row in rows:
                candidates.append(
                    {
                        "platform": platform,
                        "label": meta["label"],
                        "title": (getattr(row, "title", "") or getattr(row, "desc", "") or "")[:100],
                        "author": getattr(row, "nickname", "") or "",
                        "liked_count": _parse_int(getattr(row, "liked_count", 0)),
                        "url": getattr(row, meta["url_col"], "") or "",
                    }
                )

    candidates.sort(key=lambda x: x["liked_count"], reverse=True)
    return {"items": candidates[:limit]}


def get_keywords(days: int = 7, top: int = 30) -> dict:
    """关键词词频：近 N 天内容标题/描述 + 评论文本分词统计"""
    top = max(1, min(top, 100))
    start_ms, _ = _day_range_ms(datetime.now() - timedelta(days=days))
    stopwords = _load_stopwords()

    texts: List[str] = []
    session_factory = get_session_factory()
    with session_factory() as session:
        for meta in PLATFORM_MODELS.values():
            note_model, comment_model = meta["note"], meta["comment"]
            note_rows = (
                session.query(note_model.title, note_model.desc)
                .filter(note_model.add_ts >= start_ms)
                .limit(2000)
                .all()
            )
            texts.extend(f"{title or ''} {desc or ''}" for title, desc in note_rows)
            comment_rows = (
                session.query(comment_model.content)
                .filter(comment_model.add_ts >= start_ms)
                .limit(5000)
                .all()
            )
            texts.extend(content for (content,) in comment_rows if content)

    counter: Counter = Counter()
    for text in texts:
        for word in jieba.cut(text):
            word = word.strip()
            if len(word) < 2 or word in stopwords or re.fullmatch(r"[\d\s\W]+", word):
                continue
            counter[word] += 1

    words = [{"word": w, "count": c} for w, c in counter.most_common(top)]
    return {"words": words}


def _user_home_url(platform: str, user_id: str, sec_uid: str = "") -> str:
    """构建用户主页链接（抖音优先用 sec_uid）"""
    tpl = PLATFORM_MODELS[platform]["home_tpl"]
    uid = sec_uid or user_id or ""
    return tpl.format(uid=uid) if uid else ""


def _signature_of(row) -> str:
    """兼容各平台的签名/简介字段"""
    return getattr(row, "user_signature", None) or getattr(row, "sign", None) or ""


def get_keyword_users(
    keyword: Optional[str] = None,
    platform: Optional[str] = None,
    days: int = 30,
    limit: int = 50,
) -> dict:
    """关键词相关用户：发布者（内容命中关键词）+ 讨论者（评论提及或参与关键词内容的评论）

    按 (platform, user_id) 聚合，返回角色、作品/评论数、赞总量、最近动态等
    """
    limit = max(1, min(limit, 200))
    start_ms, _ = _day_range_ms(datetime.now() - timedelta(days=days))
    keyword = (keyword or "").strip()
    platforms = [platform] if platform in PLATFORM_MODELS else list(PLATFORM_MODELS)

    users: dict = {}  # (platform, user_key) -> info

    def _touch(platform_name: str, row, role: str) -> dict:
        user_id = str(getattr(row, "user_id", "") or "")
        nickname = getattr(row, "nickname", "") or ""
        user_key = user_id or nickname
        if not user_key:
            return {}
        info = users.setdefault(
            (platform_name, user_key),
            {
                "platform": platform_name,
                "user_id": user_id,
                "nickname": nickname,
                "avatar": "",
                "signature": "",
                "ip_location": "",
                "roles": set(),
                "note_count": 0,
                "comment_count": 0,
                "total_liked": 0,
                "last_active_ts": 0,
                "sample_texts": [],
                "sec_uid": getattr(row, "sec_uid", "") or "",
            },
        )
        info["roles"].add(role)
        if not info["nickname"] and nickname:
            info["nickname"] = nickname
        if not info["avatar"] and getattr(row, "avatar", None):
            info["avatar"] = row.avatar
        sig = _signature_of(row)
        if not info["signature"] and sig:
            info["signature"] = sig
        ip_loc = getattr(row, "ip_location", None)
        if not info["ip_location"] and ip_loc:
            info["ip_location"] = ip_loc
        if not info["sec_uid"] and getattr(row, "sec_uid", None):
            info["sec_uid"] = row.sec_uid
        add_ts = getattr(row, "add_ts", 0) or 0
        info["last_active_ts"] = max(info["last_active_ts"], add_ts)
        return info

    session_factory = get_session_factory()
    with session_factory() as session:
        for platform_name in platforms:
            meta = PLATFORM_MODELS[platform_name]
            note_model, comment_model = meta["note"], meta["comment"]

            # 1. 内容命中关键词的作者
            note_query = session.query(note_model).filter(note_model.add_ts >= start_ms)
            if keyword:
                like = f"%{keyword}%"
                note_query = note_query.filter(
                    (note_model.title.like(like))
                    | (note_model.desc.like(like))
                    | (note_model.source_keyword == keyword)
                )
            matched_notes = note_query.limit(1000).all()
            matched_note_ids = set()
            for row in matched_notes:
                info = _touch(platform_name, row, "author")
                if info:
                    info["note_count"] += 1
                    info["total_liked"] += _parse_int(getattr(row, "liked_count", 0))
                    text = (getattr(row, "title", "") or getattr(row, "desc", "") or "")[:60]
                    if text and len(info["sample_texts"]) < 3:
                        info["sample_texts"].append(text)
                note_id = getattr(row, meta["note_id_col"], None)
                if note_id is not None:
                    matched_note_ids.add(note_id)

            # 2. 评论者：评论提及关键词，或评论了关键词命中的内容
            comment_query = session.query(comment_model).filter(comment_model.add_ts >= start_ms)
            if keyword:
                like = f"%{keyword}%"
                conditions = [comment_model.content.like(like)]
                if matched_note_ids:
                    fk_col = getattr(comment_model, meta["comment_fk_col"])
                    conditions.append(fk_col.in_(matched_note_ids))
                comment_query = comment_query.filter(or_(*conditions))
            for row in comment_query.limit(3000).all():
                info = _touch(platform_name, row, "commenter")
                if info:
                    info["comment_count"] += 1
                    text = (getattr(row, "content", "") or "")[:60]
                    if text and len(info["sample_texts"]) < 3:
                        info["sample_texts"].append(text)

    items = []
    for info in users.values():
        activity = info["note_count"] + info["comment_count"]
        items.append(
            {
                "platform": info["platform"],
                "label": PLATFORM_MODELS[info["platform"]]["label"],
                "user_id": info["user_id"],
                "nickname": info["nickname"],
                "avatar": info["avatar"],
                "signature": info["signature"],
                "ip_location": info["ip_location"],
                "roles": sorted(info["roles"]),
                "note_count": info["note_count"],
                "comment_count": info["comment_count"],
                "total_liked": info["total_liked"],
                "last_active_ts": info["last_active_ts"],
                "home_url": _user_home_url(info["platform"], info["user_id"], info["sec_uid"]),
                "sample_texts": info["sample_texts"],
                "activity": activity,
            }
        )

    items.sort(key=lambda x: (x["activity"], x["total_liked"], x["last_active_ts"]), reverse=True)
    return {"keyword": keyword, "total": len(items), "users": items[:limit]}


def _match_topic(*texts: str) -> str:
    """按赛道命中词归类内容（不区分大小写），未命中返回空串；只归入最先命中的赛道"""
    lowered = " ".join(t or "" for t in texts).lower()
    for group in TOPIC_GROUPS:
        if any(kw in lowered for kw in group["keywords"]):
            return group["name"]
    return ""


def _topic_hint(note_count: int, avg_liked: int, overall_avg: int) -> str:
    """机会提示：结合供给量与互动水平给出方向建议"""
    if note_count == 0:
        return "尚未采集到相关内容，可补充对应采集关键词"
    if overall_avg > 0 and avg_liked >= overall_avg:
        if note_count <= 30:
            return "高互动低供给，潜在机会方向"
        return "热度高竞争也大，需找差异化爆点"
    return "互动一般，建议观察头部内容找切入点"


def get_topic_heat(days: int = 90, top: int = 5) -> dict:
    """产品方向赛道热度与爆点：把已采集内容按 TOPIC_GROUPS 归类，
    输出各赛道热度、头部爆款、赛道热词与高赞评论，辅助判断产品方向
    """
    top = max(1, min(top, 20))
    start_ms, _ = _day_range_ms(datetime.now() - timedelta(days=days))
    stopwords = _load_stopwords()

    stats = {
        g["name"]: {
            "note_count": 0,
            "comment_count": 0,
            "total_liked": 0,
            "platforms": set(),
            "items": [],
            "texts": [],
            "comments": [],
        }
        for g in TOPIC_GROUPS
    }

    session_factory = get_session_factory()
    with session_factory() as session:
        for platform, meta in PLATFORM_MODELS.items():
            note_model, comment_model = meta["note"], meta["comment"]

            # 1. 内容归类：标题/描述/采集来源词命中赛道词即计入
            id_topic: dict = {}
            rows = (
                session.query(note_model)
                .filter(note_model.add_ts >= start_ms)
                .order_by(note_model.add_ts.desc())
                .limit(3000)
                .all()
            )
            for row in rows:
                title = getattr(row, "title", "") or ""
                desc = getattr(row, "desc", "") or ""
                source_kw = getattr(row, "source_keyword", "") or ""
                topic = _match_topic(title, desc, source_kw)
                if not topic:
                    continue
                info = stats[topic]
                liked = _parse_int(getattr(row, "liked_count", 0))
                info["note_count"] += 1
                info["total_liked"] += liked
                info["platforms"].add(platform)
                info["texts"].append(f"{title} {desc}")
                info["items"].append(
                    {
                        "platform": platform,
                        "label": meta["label"],
                        "title": (title or desc)[:100],
                        "author": getattr(row, "nickname", "") or "",
                        "liked_count": liked,
                        "url": getattr(row, meta["url_col"], "") or "",
                        "source_keyword": source_kw,
                    }
                )
                note_id = getattr(row, meta["note_id_col"], None)
                if note_id is not None:
                    id_topic[note_id] = topic

            # 2. 评论归类：评论了赛道内容，或评论文本直接提及赛道命中词
            for row in (
                session.query(comment_model)
                .filter(comment_model.add_ts >= start_ms)
                .limit(5000)
                .all()
            ):
                content = getattr(row, "content", "") or ""
                fk = getattr(row, meta["comment_fk_col"], None)
                topic = id_topic.get(fk) or _match_topic(content)
                if not topic:
                    continue
                info = stats[topic]
                info["comment_count"] += 1
                info["comments"].append(
                    {
                        "content": content[:120],
                        "like_count": _parse_int(getattr(row, "like_count", 0)),
                        "nickname": getattr(row, "nickname", "") or "",
                        "platform": platform,
                        "label": meta["label"],
                    }
                )

    # 全盘平均互动水平，用于机会提示的参照
    covered = [s for s in stats.values() if s["note_count"]]
    overall_avg = sum(s["total_liked"] for s in covered) // sum(s["note_count"] for s in covered) if covered else 0

    topics_out = []
    for group in TOPIC_GROUPS:
        name = group["name"]
        info = stats[name]
        note_count = info["note_count"]
        avg_liked = info["total_liked"] // note_count if note_count else 0
        info["items"].sort(key=lambda x: x["liked_count"], reverse=True)
        info["comments"].sort(key=lambda x: x["like_count"], reverse=True)

        counter: Counter = Counter()
        for text in info["texts"]:
            for word in jieba.cut(text):
                word = word.strip().lower()
                if len(word) < 2 or word in stopwords or re.fullmatch(r"[\d\s\W]+", word):
                    continue
                counter[word] += 1

        topics_out.append(
            {
                "name": name,
                "note_count": note_count,
                "comment_count": info["comment_count"],
                "total_liked": info["total_liked"],
                "avg_liked": avg_liked,
                "platforms": sorted(info["platforms"]),
                "hot_words": [{"word": w, "count": c} for w, c in counter.most_common(10)],
                "top_items": info["items"][:top],
                "top_comments": info["comments"][:top],
                "hint": _topic_hint(note_count, avg_liked, overall_avg),
            }
        )

    topics_out.sort(key=lambda t: (t["total_liked"], t["note_count"]), reverse=True)
    return {"days": days, "overall_avg_liked": overall_avg, "topics": topics_out}


def get_user_profile(platform: str, user_id: str) -> dict:
    """单用户画像：基础信息（含创作者表粉丝数）+ 已采集的所有作品与评论"""
    meta = PLATFORM_MODELS.get(platform)
    if not meta or not user_id:
        return {"error": "invalid platform or user_id"}

    note_model, comment_model = meta["note"], meta["comment"]
    # B站 user_id 为整型列，其余平台为字符串列，按列类型转换查询值
    user_id_param: object = user_id
    if isinstance(note_model.user_id.type, sqlalchemy_types.Integer):
        try:
            user_id_param = int(user_id)
        except (ValueError, TypeError):
            pass
    profile = {
        "platform": platform,
        "label": meta["label"],
        "user_id": user_id,
        "nickname": "",
        "avatar": "",
        "signature": "",
        "ip_location": "",
        "fans": None,
        "home_url": "",
        "notes": [],
        "comments": [],
    }

    session_factory = get_session_factory()
    with session_factory() as session:
        # 作品列表
        notes = (
            session.query(note_model)
            .filter(note_model.user_id == user_id_param)
            .order_by(note_model.add_ts.desc())
            .limit(100)
            .all()
        )
        for row in notes:
            profile["notes"].append(
                {
                    "title": (getattr(row, "title", "") or getattr(row, "desc", "") or "")[:100],
                    "liked_count": _parse_int(getattr(row, "liked_count", 0)),
                    "create_time_ms": _content_time_ms(row),
                    "url": getattr(row, meta["url_col"], "") or "",
                    "source_keyword": getattr(row, "source_keyword", "") or "",
                }
            )

        # 评论列表（关联被评论内容的标题）
        comments = (
            session.query(comment_model)
            .filter(comment_model.user_id == user_id_param)
            .order_by(comment_model.add_ts.desc())
            .limit(200)
            .all()
        )
        fk_col_name = meta["comment_fk_col"]
        ref_ids = [getattr(c, fk_col_name) for c in comments if getattr(c, fk_col_name, None) is not None]
        ref_titles = {}
        if ref_ids:
            note_id_col = getattr(note_model, meta["note_id_col"])
            ref_rows = session.query(note_id_col, note_model.title).filter(note_id_col.in_(ref_ids)).all()
            ref_titles = {rid: (t or "")[:60] for rid, t in ref_rows}
        for row in comments:
            ref_id = getattr(row, fk_col_name, None)
            profile["comments"].append(
                {
                    "content": (getattr(row, "content", "") or "")[:120],
                    "create_time_ms": _to_ms(getattr(row, "create_time", 0)),
                    "ref_title": ref_titles.get(ref_id, ""),
                }
            )

        # 基础信息：取最新一条作品/评论记录
        source_row = notes[0] if notes else (comments[0] if comments else None)
        if source_row is not None:
            profile["nickname"] = getattr(source_row, "nickname", "") or ""
            profile["avatar"] = getattr(source_row, "avatar", "") or ""
            profile["signature"] = _signature_of(source_row)
            profile["ip_location"] = getattr(source_row, "ip_location", "") or ""
            profile["home_url"] = _user_home_url(
                platform, user_id, getattr(source_row, "sec_uid", "") or ""
            )

        # 创作者/UP主附加信息（粉丝数等，仅当采集过 creator 模式时有数据）
        creator_meta = CREATOR_MODELS.get(platform)
        if creator_meta:
            creator = (
                session.query(creator_meta["model"])
                .filter(creator_meta["model"].user_id == user_id_param)
                .order_by(creator_meta["model"].add_ts.desc())
                .first()
            )
            if creator:
                profile["fans"] = _parse_int(getattr(creator, creator_meta["fans_col"], None))
                if not profile["signature"]:
                    profile["signature"] = getattr(creator, creator_meta["desc_col"], "") or ""
                if not profile["nickname"]:
                    profile["nickname"] = getattr(creator, "nickname", "") or ""

    return profile
