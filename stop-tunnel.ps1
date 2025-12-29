# Stop all tunnel services

Write-Host "=== Stopping Tunnel Services ===" -ForegroundColor Cyan

# Stop all PowerShell jobs
$jobs = Get-Job
if ($jobs) {
    Write-Host "Stopping background jobs..." -ForegroundColor Yellow
    $jobs | Stop-Job
    $jobs | Remove-Job
    Write-Host "Jobs stopped." -ForegroundColor Green
} else {
    Write-Host "No background jobs found." -ForegroundColor Gray
}

# Stop cloudflared processes
$cloudflaredProcesses = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue
if ($cloudflaredProcesses) {
    Write-Host "Stopping cloudflared processes..." -ForegroundColor Yellow
    $cloudflaredProcesses | Stop-Process -Force
    Write-Host "cloudflared stopped." -ForegroundColor Green
} else {
    Write-Host "No cloudflared processes found." -ForegroundColor Gray
}

# Stop uvicorn processes (if running directly)
$uvicornProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*uvicorn*" }
if ($uvicornProcesses) {
    Write-Host "Stopping uvicorn processes..." -ForegroundColor Yellow
    $uvicornProcesses | Stop-Process -Force
    Write-Host "uvicorn stopped." -ForegroundColor Green
}

# Stop node processes (Vite)
$nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*vite*" }
if ($nodeProcesses) {
    Write-Host "Stopping Vite processes..." -ForegroundColor Yellow
    $nodeProcesses | Stop-Process -Force
    Write-Host "Vite stopped." -ForegroundColor Green
}

Write-Host "`n=== All Services Stopped ===" -ForegroundColor Green
Write-Host "You can now run your dev servers normally." -ForegroundColor Cyan

