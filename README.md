# 🔥 MediaCrawler - 自媒体平台爬虫 🕷️
> **Fork 定制版**：基于 [NanmiCoder/MediaCrawler](https://github.com/NanmiCoder/MediaCrawler) 的个性化定制分支，包含前端界面定制等优化。


<div align="center">

[![GitHub Stars](https://img.shields.io/github/stars/cpking0715/MediaCrawlerDev?style=social)](https://github.com/cpking0715/MediaCrawlerDev/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/cpking0715/MediaCrawlerDev?style=social)](https://github.com/cpking0715/MediaCrawlerDev/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/cpking0715/MediaCrawlerDev)](https://github.com/cpking0715/MediaCrawlerDev/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/cpking0715/MediaCrawlerDev)](https://github.com/cpking0715/MediaCrawlerDev/pulls)
[![License](https://img.shields.io/github/license/cpking0715/MediaCrawlerDev)](https://github.com/cpking0715/MediaCrawlerDev/blob/main/LICENSE)
[![中文](https://img.shields.io/badge/🇨🇳_中文-当前-blue)](README.md)
[![English](https://img.shields.io/badge/🇺🇸_English-Available-green)](README_en.md)
[![Español](https://img.shields.io/badge/🇪🇸_Español-Available-green)](README_es.md)
</div>



> **免责声明：**
> 
> 大家请以学习为目的使用本仓库⚠️⚠️⚠️⚠️，[爬虫违法违规的案件](https://github.com/HiddenStrawberry/Crawler_Illegal_Cases_In_China)  <br>
>
>本仓库的所有内容仅供学习和参考之用，禁止用于商业用途。任何人或组织不得将本仓库的内容用于非法用途或侵犯他人合法权益。本仓库所涉及的爬虫技术仅用于学习和研究，不得用于对其他平台进行大规模爬虫或其他非法行为。对于因使用本仓库内容而引起的任何法律责任，本仓库不承担任何责任。使用本仓库的内容即表示您同意本免责声明的所有条款和条件。
>
> 点击查看更为详细的免责声明。[点击跳转](#disclaimer)




## 📖 项目简介

一个功能强大的**多平台自媒体数据采集工具**，支持小红书、抖音、快手、B站、微博、贴吧、知乎等主流平台的公开信息抓取。

### 🔧 技术原理

- **核心技术**：基于 [Playwright](https://playwright.dev/) 浏览器自动化框架登录保存登录态
- **无需JS逆向**：利用保留登录态的浏览器上下文环境，通过 JS 表达式获取签名参数
- **优势特点**：无需逆向复杂的加密算法，大幅降低技术门槛


## ✨ 功能特性
| 平台   | 关键词搜索 | 指定帖子ID爬取 | 二级评论 | 指定创作者主页 | 登录态缓存 | IP代理池 | 生成评论词云图 | 视频/媒体下载 |
| ------ | ---------- | -------------- | -------- | -------------- | ---------- | -------- | -------------- | ------------- |
| 小红书 | ✅          | ✅              | ✅        | ✅              | ✅          | ✅        | ✅              | ✅             |
| 抖音   | ✅          | ✅              | ✅        | ✅              | ✅          | ✅        | ✅              | ✅             |
| 快手   | ✅          | ✅              | ✅        | ✅              | ✅          | ✅        | ✅              | ✅             |
| B 站   | ✅          | ✅              | ✅        | ✅              | ✅          | ✅        | ✅              | ✅             |
| 微博   | ✅          | ✅              | ✅        | ✅              | ✅          | ✅        | ✅              | ✅             |
| 贴吧   | ✅          | ✅              | ✅        | ✅              | ✅          | ✅        | ✅              | ✅             |
| 知乎   | ✅          | ✅              | ✅        | ✅              | ✅          | ✅        | ✅              | ✅             |



<strong>MediaCrawlerPro 重磅发布！开源不易，欢迎订阅支持</strong>

> 专注于学习成熟项目的架构设计，不仅仅是爬虫技术，Pro 版本的代码设计思路同样值得深入学习！

[MediaCrawlerPro](https://github.com/MediaCrawlerPro) 相较于开源版本的核心优势：

#### 🎯 核心功能升级
- ✅ **自媒体内容拆解Agent**（新增功能）
- ✅ **断点续爬功能**（重点特性）
- ✅ **多账号 + IP代理池支持**（重点特性）
- ✅ **去除 Playwright 依赖**，使用更简单
- ✅ **完整 Linux 环境支持**

#### 🏗️ 架构设计优化
- ✅ **代码重构优化**，更易读易维护（解耦 JS 签名逻辑）
- ✅ **企业级代码质量**，适合构建大型爬虫项目
- ✅ **完美架构设计**，高扩展性，源码学习价值更大

#### 🎁 额外功能
- ✅ **自媒体视频下载器桌面端**（适合学习全栈开发）
- ✅ **多平台首页信息流推荐**（HomeFeed）
- ✅ **AI Agent Skill 支持**（[OpenClaw](https://openclaw.ai/) 🦞 / Claude Code / Cursor 一键安装，让 Agent 自动爬取数据）
- [ ] **基于评论分析AI Agent正在开发中 🚀🚀**

点击查看：[MediaCrawlerPro 项目主页](https://github.com/MediaCrawlerPro) 更多介绍



## 🚀 快速开始

> 💡 **如果这个项目对您有帮助，请给个 ⭐ Star 支持一下！**

## 📋 前置依赖

### 🚀 uv 安装（推荐）

在进行下一步操作之前，请确保电脑上已经安装了 uv：

- **安装地址**：[uv 官方安装指南](https://docs.astral.sh/uv/getting-started/installation)
- **验证安装**：终端输入命令 `uv --version`，如果正常显示版本号，证明已经安装成功
- **推荐理由**：uv 是目前最强的 Python 包管理工具，速度快、依赖解析准确

### 🟢 Node.js 安装

项目依赖 Node.js，请前往官网下载安装：

- **下载地址**：https://nodejs.org/en/download/
- **版本要求**：>= 16.0.0

### 📦 Python 包安装

```shell
# 进入项目目录
cd MediaCrawler

# 使用 uv sync 命令来保证 python 版本和相关依赖包的一致性
uv sync
```

### 🌐 浏览器驱动安装（可选）

> 如果使用默认的 CDP 模式（连接已有 Chrome 浏览器），**无需安装浏览器驱动**。仅在使用标准 Playwright 模式时需要安装。

```shell
# 仅在标准 Playwright 模式下需要安装浏览器驱动
uv run playwright install
```

### 🌍 Chrome 浏览器配置（推荐）

项目默认使用 CDP 模式连接用户已有的 Chrome 浏览器，可以复用浏览器已有的登录状态、Cookie、扩展等，**大幅降低平台风控检测风险**。

使用前需要：

1. **安装最新版 Chrome 浏览器**（版本 >= 144），[下载地址](https://www.google.com/chrome/)
2. **开启远程调试功能**：在 Chrome 地址栏输入 `chrome://inspect/#remote-debugging`，勾选 **"Allow remote debugging for this browser instance"**
3. 页面显示 `Server running at: 127.0.0.1:9222` 表示已就绪

> 💡 **提示**：运行爬虫后，Chrome 浏览器会弹出确认对话框，点击"接受"即可。程序会等待用户确认，60秒内操作完成即可。
>
> 如果不想使用 CDP 模式，可以在 `config/base_config.py` 中设置 `ENABLE_CDP_MODE = False` 切换为标准 Playwright 模式。

## 🚀 运行爬虫程序

```shell
# 在 config/base_config.py 查看配置项目功能，写的有中文注释
# 关键词支持两种方式指定：
#   1. 直接配置：在 base_config.py 中设置 KEYWORDS = "关键词1,关键词2"
#   2. 文件配置：在项目根目录创建 keywords.txt，每行一个关键词（优先于 KEYWORDS）

# 从配置文件中读取关键词搜索相关的帖子并爬取帖子信息与评论
# --get_medias true 开启视频/图片媒体文件下载
uv run main.py --platform dy --lt qrcode --type search --get_medias true

# 从配置文件中读取指定的帖子ID列表获取指定帖子的信息与评论信息
uv run main.py --platform dy --lt qrcode --type detail --get_medias true

# 自定义数据保存路径
uv run main.py --platform dy --save_data_path "D:/videos"

# 打开对应APP扫二维码登录

# 其他平台爬虫使用示例，执行下面的命令查看
uv run main.py --help
```

<details>
<summary>🖥️ <strong>WebUI 可视化操作界面</strong></summary>

MediaCrawler 提供了基于 Web 的可视化操作界面，无需命令行也能轻松使用爬虫功能。

#### 启动 WebUI 服务

```shell
# 启动 API 服务器（默认端口 8080）
uv run uvicorn api.main:app --port 8080 --reload

# 或者使用模块方式启动
uv run python -m api.main
```

启动成功后，访问 `http://localhost:8080` 即可打开 WebUI 界面。

#### WebUI 功能特性

- **平台快速切换**：小红书 / 抖音 / 快手 / B站 / 微博 / 贴吧 / 知乎，一键选择
- **多种爬取模式**：搜索模式、详情模式、创作者主页模式
- **🎬 视频下载开关**：开启后自动下载视频/图片媒体文件到 data/{platform}/videos/ 目录
- **自定义保存路径**：可指定数据保存位置（默认 data/ 目录）
- **可视化配置**：设置关键词列表、爬取数量、评论数量等参数
- **实时查看**：运行状态、爬取进度、WebSocket 实时日志
- **进度追踪**：已处理视频数、目标总数、运行时间、当前关键词

#### 界面预览

全新的深色主题 WebUI，整合了所有爬虫控制功能于一个页面：

- **左侧配置面板**：平台选择 → 爬取模式 → 关键词/ID输入 → 数量配置 → 选项开关 → 开始/停止
- **右侧日志面板**：WebSocket 实时日志流，支持日志级别颜色区分
- **进度面板**：进度条、已处理/目标视频数、运行时间、当前关键词

</details>

<details>
<summary>📊 <strong>个人工作台：每日定时采集 + 数据分析</strong></summary>

在采集能力之上封装的定时工作台：每天定时抓取各平台信息入库，并提供趋势、热门、词频分析与可视化仪表盘。

```shell
# 1. 首次使用：初始化 SQLite 表结构
uv run python main.py --init_db sqlite

# 2. 启动工作台（API + 调度器 + 仪表盘，默认每天 08:00 自动采集）
uv run uvicorn api.main:app --port 8080
```

- 仪表盘：`http://localhost:8080/dashboard`
- 默认每日采集平台：小红书 / 抖音 / B站，配置见 `workbench/config.py`
- 注意：各平台 Cookie 会过期，过期后当日任务会失败并在仪表盘告警，需手动补登录

详细配置与 API 说明见 [workbench/README.md](workbench/README.md)。

</details>

<details>
<summary>🔗 <strong>使用 Python 原生 venv 管理环境（不推荐）</strong></summary>

#### 创建并激活 Python 虚拟环境

> 如果是爬取抖音和知乎，需要提前安装 nodejs 环境，版本大于等于：`16` 即可

```shell
# 进入项目根目录
cd MediaCrawler

# 创建虚拟环境
# 我的 python 版本是：3.11 requirements.txt 中的库是基于这个版本的
# 如果是其他 python 版本，可能 requirements.txt 中的库不兼容，需自行解决
python -m venv venv

# macOS & Linux 激活虚拟环境
source venv/bin/activate

# Windows 激活虚拟环境
venv\Scripts\activate
```

#### 安装依赖库

```shell
pip install -r requirements.txt
```

#### 安装 playwright 浏览器驱动

```shell
playwright install
```

#### 运行爬虫程序（原生环境）

```shell
# 项目默认是没有开启评论爬取模式，如需评论请在 config/base_config.py 中的 ENABLE_GET_COMMENTS 变量修改
# 一些其他支持项，也可以在 config/base_config.py 查看功能，写的有中文注释

# 从配置文件中读取关键词搜索相关的帖子并爬取帖子信息与评论
python main.py --platform xhs --lt qrcode --type search

# 从配置文件中读取指定的帖子ID列表获取指定帖子的信息与评论信息
python main.py --platform xhs --lt qrcode --type detail

# 打开对应APP扫二维码登录

# 其他平台爬虫使用示例，执行下面的命令查看
python main.py --help
```

</details>



## 🎬 视频/媒体下载

此 Fork 版本默认开启了视频和图片媒体文件的自动下载功能（`ENABLE_GET_MEIDAS = True`）。

### 功能说明

- 爬取帖子时，自动下载其中的视频（MP4）和图片资源
- 下载的媒体文件保存在 `data/{platform}/videos/{帖子的唯一ID}/` 目录
- 例如抖音的视频保存路径：`data/douyin/videos/{视频ID}/video.mp4`
- 同时生成结构化元数据（支持 CSV / JSON / JSONL / Excel 等格式）

### 配置方式

在 `config/base_config.py` 中：

```python
ENABLE_GET_MEIDAS = True   # True 开启媒体下载，False 关闭
CRAWLER_MAX_NOTES_COUNT = 2  # 控制下载的视频数量
```

### 命令行参数

```shell
# 开启媒体下载
uv run main.py --platform dy --get_medias true

# 指定保存路径
uv run main.py --platform dy --get_medias true --save_data_path "D:/videos"
```

### WebUI 操作

在 WebUI 控制台中，通过 **🎬 下载视频** 开关一键开启/关闭媒体下载，并可在 **保存位置** 字段自定义输出路径。

## 💾 数据保存

MediaCrawler 支持多种数据存储方式，包括 CSV、JSON、JSONL、Excel、SQLite 和 MySQL 数据库。

📖 **详细使用说明请查看：[数据存储指南](docs/data_storage_guide.md)**


[🚀 MediaCrawlerPro 重磅发布 🚀！更多的功能，更好的架构设计！开源不易，欢迎订阅支持！](https://github.com/MediaCrawlerPro)


## 💬 交流群组
- **微信交流群**：[点击加入](https://nanmicoder.github.io/MediaCrawler/%E5%BE%AE%E4%BF%A1%E4%BA%A4%E6%B5%81%E7%BE%A4.html)
- **B站账号**：[关注我](https://space.bilibili.com/434377496)，分享AI与爬虫技术知识


## 💰 赞助商展示

<a href="https://tikhub.io/?utm_source=github.com/cpking0715/MediaCrawlerDev&utm_medium=marketing_social&utm_campaign=retargeting&utm_content=carousel_ad">
<img width="500" src="docs/static/images/tikhub_banner_zh.png">
<br>
TikHub.io 提供 900+ 高稳定性数据接口，覆盖 TK、DY、XHS、Y2B、Ins、X 等 14+ 海内外主流平台，支持用户、内容、商品、评论等多维度公开数据 API，并配套 4000 万+ 已清洗结构化数据集，使用邀请码 <code>cfzyejV9</code> 注册并充值，即可额外获得 $2 赠送额度。
</a>
<br>
<br>

<a href="https://www.atlascloud.ai/?utm_source=github&utm_medium=link&utm_campaign=mei%27da%27c%27rmeidacrawler">
<img width="500" alt="Atlas Cloud" src="docs/static/images/atlas_cloud_logo_black.png#gh-light-mode-only">
<img width="500" alt="Atlas Cloud" src="docs/static/images/atlas_cloud_logo_white.png#gh-dark-mode-only">
</a>
<br>
<a href="https://www.atlascloud.ai/?utm_source=github&utm_medium=link&utm_campaign=mei%27da%27c%27rmeidacrawler">Atlas Cloud</a> 是一个全模态 AI 推理平台，让开发者通过统一的 AI API 访问视频生成、图像生成和 LLM API，无需分别维护多个厂商集成，即可调用 300+ 精选模型。Atlas Cloud 最新推出 <a href="https://www.atlascloud.ai/console/coding-plan">coding plan 优惠</a>，为开发者提供更具性价比的 API 访问预算。

---

## 🤝 成为赞助者

成为赞助者，可以将您的产品展示在这里，每天获得大量曝光！

**联系方式**：
- 微信：`relakkes`
- 邮箱：`relakkes@gmail.com`
---

## ☕ 请作者喝杯咖啡

如果这个项目对您有帮助，欢迎打赏支持，您的每一份支持都是我持续更新的动力 ❤️

<table>
<tr>
<td align="center" width="33%">
<img src="docs/static/images/wechat_pay.jpeg" width="250" alt="微信赞赏"><br>
<b>微信赞赏</b>
</td>
<td align="center" width="33%">
<img src="docs/static/images/zfb_pay.png" width="250" alt="支付宝"><br>
<b>支付宝</b>
</td>
<td align="center" width="33%">
<a href="https://buymeacoffee.com/relakkes" target="_blank">
<img src="docs/static/images/bmc_button.png" width="250" alt="Buy Me a Coffee">
</a><br>
<b>Buy Me a Coffee</b>
</td>
</tr>
</table>

---

## 📚 其他
- **常见问题**：[MediaCrawler 完整文档](https://nanmicoder.github.io/MediaCrawler/)
- **爬虫入门教程**：[CrawlerTutorial 免费教程](https://github.com/NanmiCoder/CrawlerTutorial)
- **新闻爬虫开源项目**：[NewsCrawlerCollection](https://github.com/NanmiCoder/NewsCrawlerCollection)


## ⭐ Star 趋势图

如果这个项目对您有帮助，请给个 ⭐ Star 支持一下，让更多的人看到 MediaCrawler！

[![Star History Chart](https://api.star-history.com/svg?repos=cpking0715/MediaCrawlerDev&type=Date)](https://star-history.com/#cpking0715/MediaCrawlerDev&Date)


## 📚 参考

- **小红书签名仓库**：[Cloxl 的 xhs 签名仓库](https://github.com/Cloxl/xhshow)
- **小红书客户端**：[ReaJason 的 xhs 仓库](https://github.com/ReaJason/xhs)
- **短信转发**：[SmsForwarder 参考仓库](https://github.com/pppscn/SmsForwarder)
- **内网穿透工具**：[ngrok 官方文档](https://ngrok.com/docs/)


# 免责声明
<div id="disclaimer"> 

## 1. 项目目的与性质
本项目（以下简称“本项目”）是作为一个技术研究与学习工具而创建的，旨在探索和学习网络数据采集技术。本项目专注于自媒体平台的数据爬取技术研究，旨在提供给学习者和研究者作为技术交流之用。

## 2. 法律合规性声明
本项目开发者（以下简称“开发者”）郑重提醒用户在下载、安装和使用本项目时，严格遵守中华人民共和国相关法律法规，包括但不限于《中华人民共和国网络安全法》、《中华人民共和国反间谍法》等所有适用的国家法律和政策。用户应自行承担一切因使用本项目而可能引起的法律责任。

## 3. 使用目的限制
本项目严禁用于任何非法目的或非学习、非研究的商业行为。本项目不得用于任何形式的非法侵入他人计算机系统，不得用于任何侵犯他人知识产权或其他合法权益的行为。用户应保证其使用本项目的目的纯属个人学习和技术研究，不得用于任何形式的非法活动。

## 4. 免责声明
开发者已尽最大努力确保本项目的正当性及安全性，但不对用户使用本项目可能引起的任何形式的直接或间接损失承担责任。包括但不限于由于使用本项目而导致的任何数据丢失、设备损坏、法律诉讼等。

## 5. 知识产权声明
本项目的知识产权归开发者所有。本项目受到著作权法和国际著作权条约以及其他知识产权法律和条约的保护。用户在遵守本声明及相关法律法规的前提下，可以下载和使用本项目。

## 6. 最终解释权
关于本项目的最终解释权归开发者所有。开发者保留随时更改或更新本免责声明的权利，恕不另行通知。
</div>
