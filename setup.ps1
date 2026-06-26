# ============================================================================
# MediaCrawler - One-Click Setup & Launch Script
# 
# Usage:
#   Method 1: Double-click start.bat
#   Method 2: Run in PowerShell: .\setup.ps1
#
# This script will:
#   1. Detect/install Python 3.11+
#   2. Install uv package manager
#   3. Install all Python dependencies
#   4. Install Playwright Chromium browser
#   5. Start FastAPI Web server on port 8080
#   6. Auto-open browser to the management page
# ============================================================================

$ErrorActionPreference = "Continue"
$Host.UI.RawUI.WindowTitle = "MediaCrawler Setup"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

function Write-Step { param($num, $text) Write-Host "`n[$num] $text" -ForegroundColor Cyan }
function Write-OK   { param($text) Write-Host "  [OK] $text" -ForegroundColor Green }
function Write-Warn { param($text) Write-Host "  [WARN] $text" -ForegroundColor Yellow }
function Write-Err  { param($text) Write-Host "  [ERROR] $text" -ForegroundColor Red }
function Write-Tip  { param($text) Write-Host "  $text" -ForegroundColor Gray }

# Refresh PATH from registry
function Refresh-Path {
    $machinePath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    $userPath    = [System.Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path    = "$machinePath;$userPath"
}

# ============================================================================
# Step 1: Detect / Install Python
# ============================================================================
Write-Step "1/5" "Checking Python environment..."

$pythonCmd = $null

# Common install locations
$candidatePaths = @(
    "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "C:\Python313\python.exe",
    "C:\Python312\python.exe",
    "C:\Python311\python.exe"
)

foreach ($p in $candidatePaths) {
    if (Test-Path $p) {
        $pythonCmd = $p
        break
    }
}

# Fallback: search PATH (exclude Windows Store stubs)
if (-not $pythonCmd) {
    $found = Get-Command python3 -ErrorAction SilentlyContinue
    if ($found -and $found.Source -notmatch "WindowsApps") { $pythonCmd = $found.Source }
}
if (-not $pythonCmd) {
    $found = Get-Command python -ErrorAction SilentlyContinue
    if ($found -and $found.Source -notmatch "WindowsApps") { $pythonCmd = $found.Source }
}

if (-not $pythonCmd) {
    Write-Err "Python 3.11+ not found"
    Write-Tip ""
    Write-Tip "Attempting auto-install via winget..."
    try {
        winget install Python.Python.3.11 --accept-package-agreements --accept-source-agreements --silent
        Write-Tip "Python 3.11 installed! Refreshing PATH..."
        Refresh-Path
        foreach ($p in $candidatePaths) {
            if (Test-Path $p) { $pythonCmd = $p; break }
        }
    } catch {
        Write-Err "Auto-install failed. Please install Python 3.11+ manually:"
        Write-Tip "  https://www.python.org/downloads/"
        Write-Tip "  (Check 'Add Python to PATH' during installation)"
        Read-Host "Press Enter after installing Python..."
        Refresh-Path
        $found = Get-Command python -ErrorAction SilentlyContinue
        if ($found -and $found.Source -notmatch "WindowsApps") { $pythonCmd = $found.Source }
    }
}

if (-not $pythonCmd) {
    Write-Err "Python still not found. Please install Python 3.11+ and re-run this script."
    Read-Host "Press Enter to exit..."
    exit 1
}

# Verify version >= 3.11
$pyVersion = & $pythonCmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$major, $minor = $pyVersion.Split('.')
if ([int]$major -lt 3 -or ([int]$major -eq 3 -and [int]$minor -lt 11)) {
    Write-Err "Python >= 3.11 required, current version: $pyVersion"
    exit 1
}
Write-OK "Python $pyVersion found at: $pythonCmd"

# ============================================================================
# Step 2: Detect / Install uv
# ============================================================================
Write-Step "2/5" "Checking uv package manager..."

$uvAvailable = $false
try {
    $null = & uv --version 2>&1
    if ($LASTEXITCODE -eq 0) { $uvAvailable = $true }
} catch {}

if (-not $uvAvailable) {
    Write-Tip "Installing uv..."
    try {
        $installScript = Invoke-RestMethod -Uri "https://astral.sh/uv/install.ps1" -ErrorAction Stop
        Invoke-Expression $installScript
        Refresh-Path
        # Also add ~/.local/bin to PATH
        $uvBin = Join-Path $env:USERPROFILE ".local\bin"
        if (Test-Path (Join-Path $uvBin "uv.exe")) {
            $env:Path = "$uvBin;$env:Path"
        }
        Write-OK "uv installed successfully!"
    } catch {
        Write-Warn "Online install failed, trying pip..."
        try {
            & $pythonCmd -m pip install uv --quiet 2>&1
            Refresh-Path
            Write-OK "uv installed via pip!"
        } catch {
            Write-Err "uv installation failed. Please install manually: pip install uv"
            exit 1
        }
    }
} else {
    Write-OK "uv is ready"
}

# ============================================================================
# Step 3: Install Python dependencies
# ============================================================================
Write-Step "3/5" "Installing Python dependencies..."

try {
    # Prefer Tsinghua mirror for speed in China
    $result = uv sync --index-url https://pypi.tuna.tsinghua.edu.cn/simple 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Warn "Mirror failed, falling back to default index..."
        uv sync 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "uv sync failed"
        }
    }
    Write-OK "Python dependencies installed!"
} catch {
    Write-Err "Dependency installation failed. Check your network and try again."
    exit 1
}

# ============================================================================
# Step 4: Install Playwright Chromium
# ============================================================================
Write-Step "4/5" "Installing Playwright Chromium browser..."

try {
    uv run playwright install chromium 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-OK "Chromium browser installed!"
    } else {
        Write-Warn "Chromium installation may be incomplete. Browser crawling may not work."
    }
} catch {
    Write-Warn "Chromium installation failed: $_"
}

# ============================================================================
# Step 5: Start Web Server
# ============================================================================
Write-Step "5/5" "Starting MediaCrawler Web Server..."

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  MediaCrawler is ready!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Web UI:  http://localhost:8080" -ForegroundColor Cyan
Write-Host "  API Doc: http://localhost:8080/docs" -ForegroundColor Cyan
Write-Host "  Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Auto-open browser
try {
    Start-Process "http://localhost:8080"
} catch {}

# Launch FastAPI server
uv run uvicorn api.main:app --host 0.0.0.0 --port 8080 --log-level info
