# Start all services for Cloudflare Tunnel
# Run this script to start backend, frontend, and tunnel in separate windows

param(
    [string]$TunnelName = "credit-inventory",
    [switch]$SkipTunnel = $false
)

$ErrorActionPreference = "Continue"
$projectRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $projectRoot "backend"
$frontendDir = Join-Path $projectRoot "frontend2"
$cloudflaredExe = "$env:USERPROFILE\cloudflare\cloudflared.exe"

Write-Host "=== Starting Services for Cloudflare Tunnel ===" -ForegroundColor Cyan

# Check if cloudflared exists (if not skipping)
if (-not $SkipTunnel -and -not (Test-Path $cloudflaredExe)) {
    Write-Host "WARNING: cloudflared.exe not found at $cloudflaredExe" -ForegroundColor Yellow
    Write-Host "Run setup-cloudflare-tunnel.ps1 first, or use -SkipTunnel flag" -ForegroundColor Yellow
    $SkipTunnel = $true
}

# Add cloudflared to PATH for this session
if (Test-Path "$env:USERPROFILE\cloudflare") {
    $env:Path += ";$env:USERPROFILE\cloudflare"
}

# Start Backend in new window
Write-Host "`n[1/3] Starting FastAPI Backend on 127.0.0.1:8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$backendDir'; Write-Host '=== FastAPI Backend (Tunnel Mode) ===' -ForegroundColor Cyan; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
)

# Wait a moment for backend to start
Start-Sleep -Seconds 2

# Start Frontend in new window
Write-Host "[2/3] Starting Vite Frontend on 127.0.0.1:5173..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$frontendDir'; Write-Host '=== Vite Frontend (Tunnel Mode) ===' -ForegroundColor Cyan; npm run dev -- --host 127.0.0.1 --port 5173"
)

# Wait a moment for frontend to start
Start-Sleep -Seconds 3

if (-not $SkipTunnel) {
    # Start Tunnel in new window
    Write-Host "[3/3] Starting Cloudflare Tunnel ($TunnelName)..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "Write-Host '=== Cloudflare Tunnel ===' -ForegroundColor Cyan; & '$cloudflaredExe' tunnel run $TunnelName"
    )
    
    Write-Host "`n=== All Services Started ===" -ForegroundColor Green
    Write-Host "Backend:  http://127.0.0.1:8000 (in separate window)" -ForegroundColor Cyan
    Write-Host "Frontend: http://127.0.0.1:5173 (in separate window)" -ForegroundColor Cyan
    Write-Host "Tunnel:   Running in separate window" -ForegroundColor Cyan
} else {
    Write-Host "`n=== Services Started (Tunnel Skipped) ===" -ForegroundColor Green
    Write-Host "Backend:  http://127.0.0.1:8000 (in separate window)" -ForegroundColor Cyan
    Write-Host "Frontend: http://127.0.0.1:5173 (in separate window)" -ForegroundColor Cyan
}

Write-Host "`nTo stop services: Close the PowerShell windows or run .\stop-tunnel.ps1" -ForegroundColor Gray
Write-Host "To view tunnel status: cloudflared.exe tunnel info $TunnelName" -ForegroundColor Gray

