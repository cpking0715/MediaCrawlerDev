# 个人工作台(Workbench)

基于 MediaCrawler 采集能力的每日定时抓取 + 数据分析工作台。

## 架构

```
FastAPI 服务(api/main.py, 单进程常驻)
    └── APScheduler 调度器(workbench/scheduler.py)
            └── 每日定时按平台串行启动子进程: main.py --platform X --type search --save_data_option sqlite
                    └── 数据落 SQLite(database/sqlite_tables.db, 自带去重)
    └── 分析 API(api/routers/analysis.py + api/services/analysis_service.py)
    └── 仪表盘(浏览器访问 /dashboard, api/webui/dashboard.html)
```

## 启动方式

```shell
# 1. 首次使用: 初始化 SQLite 表结构
uv run python main.py --init_db sqlite

# 2. 启动工作台(API + 调度器 + 仪表盘)
uv run uvicorn api.main:app --port 8080
```

- 仪表盘: http://localhost:8080/dashboard
- API 文档: http://localhost:8080/docs
- 默认每天 08:00 自动采集,服务需保持运行

## 配置(workbench/config.py)

| 配置项 | 默认值 | 说明 |
| --- | --- | --- |
| `WORKBENCH_PLATFORMS` | `["xhs", "dy", "bili"]` | 每日采集平台,按顺序串行 |
| `WORKBENCH_DAILY_HOUR/MINUTE` | 8 / 0 | 每日定时时间,可用环境变量 `WORKBENCH_DAILY_HOUR` 覆盖 |
| `WORKBENCH_CRAWLER_TYPE` | `search` | 采集模式 |
| `WORKBENCH_LOGIN_TYPE` | `cookie` | 定时场景必须用 cookie(扫码无法无人值守) |
| `WORKBENCH_KEYWORDS_FILE` | 根目录 `keywords.txt` | 关键词来源,每行一个 |
| `WORKBENCH_PLATFORM_TIMEOUT_SECONDS` | 1800 | 单平台采集超时 |

## API 一览

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/schedule/status` | 调度状态、下次运行时间、平台与关键词 |
| GET | `/api/schedule/runs` | 采集运行历史(含失败原因日志尾部) |
| POST | `/api/schedule/run/{platform}` | 手动触发单平台采集 |
| POST | `/api/schedule/run` | 手动触发全部平台的每日采集 |
| GET | `/api/analysis/summary` | 各平台数据总量与今日新增 |
| GET | `/api/analysis/trends?days=14` | 近 N 天每日新增趋势 |
| GET | `/api/analysis/hot?limit=20&days=30` | 热门内容排行(按点赞) |
| GET | `/api/analysis/keywords?days=7&top=30` | 关键词词频 |

## 定时场景的配置建议

工作台调度默认以 `--lt cookie` 运行爬虫。为适合无人值守,建议同步调整 `config/base_config.py`:

- `CDP_CONNECT_EXISTING = False`:不依赖你手动打开的浏览器,由程序自行启动。
- `HEADLESS = True` 或 `CDP_HEADLESS = True`:无头运行(注意部分平台无头模式反检测能力下降)。
- `LOGIN_TYPE = "cookie"`,并确保持久化登录态 `SAVE_LOGIN_STATE = True`。

## 登录态风险说明(重要)

各平台 Cookie 均会过期。过期后当日该平台的定时任务会失败:

1. 失败会被记录在 `workbench_task_run` 表与 `/api/schedule/runs`;
2. 仪表盘顶部会显示红色告警;
3. 需要你手动登录一次(例如临时用 `--lt qrcode` 跑一次该平台),之后定时任务自动恢复。

本项目不做自动破解登录,请遵守各平台服务条款与 robots.txt,控制抓取频率。
