# Generate Cloudflare Tunnel config.yml
# Usage: .\generate-tunnel-config.ps1 -TunnelName "credit-inventory" -ApiDomain "api.yourdomain.com" -AppDomain "app.yourdomain.com"

param(
    [Parameter(Mandatory=$true)]
    [string]$TunnelName,
    
    [Parameter(Mandatory=$true)]
    [string]$ApiDomain,
    
    [Parameter(Mandatory=$true)]
    [string]$AppDomain,
    
    [string]$ConfigPath = "$env:USERPROFILE\.cloudflared\config.yml"
)

Write-Host "=== Generating Cloudflare Tunnel Config ===" -ForegroundColor Cyan

# Get tunnel ID
$cloudflaredExe = "$env:USERPROFILE\cloudflare\cloudflared.exe"
if (-not (Test-Path $cloudflaredExe)) {
    Write-Host "ERROR: cloudflared.exe not found. Run setup-cloudflare-tunnel.ps1 first." -ForegroundColor Red
    exit 1
}

$env:Path += ";$env:USERPROFILE\cloudflare"

Write-Host "Getting tunnel ID for: $TunnelName" -ForegroundColor Yellow
$tunnelList = & "$cloudflaredExe" tunnel list
$tunnelId = ($tunnelList | Select-String -Pattern "$([regex]::Escape($TunnelName))\s+([a-f0-9-]+)" | ForEach-Object { $_.Matches.Groups[1].Value })

if (-not $tunnelId) {
    Write-Host "ERROR: Could not find tunnel ID. Make sure tunnel '$TunnelName' exists." -ForegroundColor Red
    Write-Host "Run: cloudflared.exe tunnel list" -ForegroundColor Yellow
    exit 1
}

Write-Host "Found tunnel ID: $tunnelId" -ForegroundColor Green

# Get credentials file path
$credentialsFile = "$env:USERPROFILE\.cloudflared\$tunnelId.json"

if (-not (Test-Path $credentialsFile)) {
    Write-Host "WARNING: Credentials file not found at: $credentialsFile" -ForegroundColor Yellow
}

# Create config directory
$configDir = Split-Path -Parent $ConfigPath
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Force -Path $configDir | Out-Null
}

# Generate config content
$configContent = @"
tunnel: $tunnelId
credentials-file: $credentialsFile

ingress:
  # Backend API routes (must come before catch-all)
  - hostname: $ApiDomain
    service: http://localhost:8000
  
  # Frontend routes
  - hostname: $AppDomain
    service: http://localhost:5173
  
  # Catch-all: 404 for unmatched requests
  - service: http_status:404
"@

# Write config file
try {
    $configContent | Out-File -FilePath $ConfigPath -Encoding UTF8 -NoNewline
    Write-Host "`nConfig file created: $ConfigPath" -ForegroundColor Green
    
    Write-Host "`n=== Config Contents ===" -ForegroundColor Cyan
    Write-Host $configContent
    
    Write-Host "`n=== Next Steps ===" -ForegroundColor Yellow
    Write-Host "1. Add DNS CNAME records in Cloudflare Dashboard:"
    Write-Host "   - $ApiDomain → $tunnelId.cfargotunnel.com" -ForegroundColor Cyan
    Write-Host "   - $AppDomain → $tunnelId.cfargotunnel.com" -ForegroundColor Cyan
    Write-Host "2. Ensure both are proxied (orange cloud)"
    Write-Host "3. Run: .\start-tunnel.ps1" -ForegroundColor Cyan
    
} catch {
    Write-Host "ERROR: Failed to write config file: $_" -ForegroundColor Red
    exit 1
}

