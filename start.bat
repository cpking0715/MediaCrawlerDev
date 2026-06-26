@echo off
chcp 65001 >nul
title MediaCrawler 一键启动

echo.
echo ========================================
echo   MediaCrawler 一键启动 (零门槛版)
echo ========================================
echo.
echo   1. 自动检测并安装 Python 3.11+
echo   2. 自动安装 uv 包管理器
echo   3. 自动安装所有依赖
echo   4. 自动安装 Chromium 浏览器
echo   5. 自动启动 Web 服务 (端口 8080)
echo   6. 自动打开浏览器访问管理页
echo.
echo ========================================
echo.

:: 检查是否有 Python（提前给个友好提示）
where python >nul 2>&1
if %errorlevel% neq 0 (
    where python3 >nul 2>&1
    if %errorlevel% neq 0 (
        echo [提示] 未检测到 Python，脚本将尝试通过 winget 自动安装...
        echo [提示] 如果没有 winget，请先手动安装 Python 3.11+：
        echo        https://www.python.org/downloads/
        echo        (安装时请勾选 "Add Python to PATH")
        echo.
    )
)

:: 绕过 PowerShell 执行策略，以管理员权限运行 setup.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"

:: 如果 PowerShell 退出，暂停看日志
if %errorlevel% neq 0 (
    echo.
    echo [错误] 脚本异常退出，请检查上方错误信息
    pause
)
