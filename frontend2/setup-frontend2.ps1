# Ensure we're inside frontend2
if (!(Test-Path "package.json")) {
    Write-Error "Run this script inside frontend2 directory"
    exit
}

$dirs = @(
    "src/api",
    "src/components/dashboard",
    "src/components/borrow",
    "src/components/containers",
    "src/components/components",
    "src/components/ui",
    "src/layouts",
    "src/pages",
    "src/router",
    "src/utils"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

$files = @(
    "src/pages/Dashboard.jsx",
    "src/layouts/DashboardLayout.jsx",
    "src/router/AppRouter.jsx",
    "src/components/dashboard/Clock.jsx",
    "src/components/dashboard/StatCard.jsx"
)

foreach ($file in $files) {
    if (!(Test-Path $file)) {
        New-Item -ItemType File -Path $file | Out-Null
    }
}

Write-Host "frontend2 structure created successfully."
