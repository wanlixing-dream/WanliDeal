$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendPath = Join-Path $Root "backend"
$FrontendPath = Join-Path $Root "frontend"
$VenvPath = Join-Path $Root ".venv"
$EnvPath = Join-Path $Root ".env"
$EnvExamplePath = Join-Path $Root ".env.example"

Write-Host "====================================="
Write-Host " WanliDeal 一键启动脚本"
Write-Host "====================================="
Write-Host ""

if (!(Test-Path $EnvPath)) {
    if (Test-Path $EnvExamplePath) {
        Copy-Item $EnvExamplePath $EnvPath
        Write-Host "[OK] 已根据 .env.example 创建 .env"
    } else {
        Write-Host "[WARN] 未找到 .env.example，跳过 .env 创建"
    }
} else {
    Write-Host "[OK] 已找到 .env"
}

Write-Host ""

if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] 未找到 python，请先安装 Python 3.10+"
    exit 1
}

if (!(Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] 未找到 npm，请先安装 Node.js 18+"
    exit 1
}

if (!(Test-Path $VenvPath)) {
    Write-Host "[INFO] 正在创建 Python 虚拟环境..."
    python -m venv $VenvPath
    Write-Host "[OK] 虚拟环境创建完成"
} else {
    Write-Host "[OK] 已找到 Python 虚拟环境"
}

$PythonExe = Join-Path $VenvPath "Scripts\python.exe"
$PipExe = Join-Path $VenvPath "Scripts\pip.exe"

Write-Host ""
Write-Host "[INFO] 正在安装后端依赖..."
& $PipExe install -r (Join-Path $BackendPath "requirements.txt")

Write-Host ""
Write-Host "[INFO] 正在检查前端依赖..."
$NodeModulesPath = Join-Path $FrontendPath "node_modules"

if (!(Test-Path $NodeModulesPath)) {
    Write-Host "[INFO] 正在安装前端依赖..."
    Push-Location $FrontendPath
    npm install
    Pop-Location
} else {
    Write-Host "[OK] 已找到 frontend\node_modules"
}

Write-Host ""
Write-Host "[INFO] 正在启动后端服务..."
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "Set-Location '$Root'; & '$PythonExe' -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"
)

Start-Sleep -Seconds 2

Write-Host "[INFO] 正在启动前端服务..."
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "Set-Location '$FrontendPath'; npm run dev"
)

Write-Host ""
Write-Host "====================================="
Write-Host " 启动完成"
Write-Host "====================================="
Write-Host "前端地址: http://localhost:5173"
Write-Host "后端地址: http://localhost:8000"
Write-Host "健康检查: http://localhost:8000/api/health"
Write-Host ""
Write-Host "如果浏览器没有自动打开，请手动访问前端地址。"
Write-Host ""

Start-Process "http://localhost:5173"
