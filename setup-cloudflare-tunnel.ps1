# Cloudflare Tunnel Setup Script for Windows
# Run this script to download, install, and configure cloudflared

param(
    [string]$TunnelName = "credit-inventory",
    [string]$ConfigPath = "$env:USERPROFILE\.cloudflared\config.yml"
)

Write-Host "=== Cloudflare Tunnel Setup ===" -ForegroundColor Cyan

# Step 1: Download cloudflared
Write-Host "`n[1/5] Downloading cloudflared..." -ForegroundColor Yellow
$cloudflareDir = "$env:USERPROFILE\cloudflare"
New-Item -ItemType Directory -Force -Path $cloudflareDir | Out-Null

$downloadUrl = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
$cloudflaredExe = "$cloudflareDir\cloudflared.exe"

if (Test-Path $cloudflaredExe) {
    Write-Host "cloudflared.exe already exists, skipping download." -ForegroundColor Green
} else {
    try {
        Invoke-WebRequest -Uri $downloadUrl -OutFile $cloudflaredExe -ErrorAction Stop
        Write-Host "Downloaded cloudflared.exe successfully." -ForegroundColor Green
    } catch {
        Write-Host "Error downloading cloudflared: $_" -ForegroundColor Red
        exit 1
    }
}

# Step 2: Add to PATH for current session
Write-Host "`n[2/5] Adding cloudflared to PATH (current session)..." -ForegroundColor Yellow
$env:Path += ";$cloudflareDir"
Write-Host "Added to PATH." -ForegroundColor Green

# Step 3: Verify installation
Write-Host "`n[3/5] Verifying installation..." -ForegroundColor Yellow
try {
    $version = & "$cloudflaredExe" --version
    Write-Host "cloudflared version: $version" -ForegroundColor Green
} catch {
    Write-Host "Error running cloudflared: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Login
Write-Host "`n[4/5] Cloudflare Login..." -ForegroundColor Yellow
Write-Host "This will open your browser. Please log in and authorize the tunnel." -ForegroundColor Cyan
$login = Read-Host "Press Enter to start login (or 'skip' to skip)"
if ($login -ne "skip") {
    & "$cloudflaredExe" tunnel login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Login failed. Please try again." -ForegroundColor Red
        exit 1
    }
}

# Step 5: Create tunnel
Write-Host "`n[5/5] Creating tunnel: $TunnelName" -ForegroundColor Yellow
$createTunnel = Read-Host "Create tunnel? (Y/n)"
if ($createTunnel -ne "n" -and $createTunnel -ne "N") {
    & "$cloudflaredExe" tunnel create $TunnelName
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Tunnel creation failed or tunnel already exists." -ForegroundColor Yellow
    } else {
        Write-Host "Tunnel created successfully!" -ForegroundColor Green
    }
}

# Get tunnel ID
Write-Host "`n=== Getting Tunnel Information ===" -ForegroundColor Cyan
& "$cloudflaredExe" tunnel list

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Note your tunnel ID from above"
Write-Host "2. Edit config.yml at: $ConfigPath"
Write-Host "3. Add DNS CNAME records in Cloudflare Dashboard"
Write-Host "4. Run start-tunnel.ps1 to start services"

Write-Host "`nTo add cloudflared to PATH permanently:" -ForegroundColor Cyan
Write-Host "[Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path', 'User') + ';$cloudflareDir', 'User')" -ForegroundColor Gray

