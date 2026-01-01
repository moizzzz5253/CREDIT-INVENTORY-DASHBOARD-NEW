# PowerShell Script to Update Repository and Push to GitHub
# This script ensures ALL changes are captured and pushed

param(
    [string]$CommitMessage = "Update: Sync all changes to GitHub",
    [switch]$DryRun = $false,
    [switch]$Verbose = $false
)

# Set up error handling
$ErrorActionPreference = "Stop"
$WarningPreference = "Continue"

# Colors for output
$colors = @{
    Green   = "`e[32m"
    Red     = "`e[31m"
    Yellow  = "`e[33m"
    Blue    = "`e[34m"
    Cyan    = "`e[36m"
    Reset   = "`e[0m"
}

function Write-Step {
    param([string]$Message)
    Write-Host "$($colors.Cyan)[STEP]$($colors.Reset) $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "$($colors.Green)[SUCCESS]$($colors.Reset) $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "$($colors.Red)[ERROR]$($colors.Reset) $Message" -ForegroundColor Red
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "$($colors.Yellow)[WARNING]$($colors.Reset) $Message" -ForegroundColor Yellow
}

# Get repository root
$repoRoot = git rev-parse --show-toplevel 2>$null
if (-not $repoRoot) {
    Write-Error-Custom "Not in a git repository. Exiting."
    exit 1
}

Write-Step "Repository root: $repoRoot"
cd $repoRoot

# Function to check git status
function Get-GitStatus {
    $status = git status --porcelain
    $stagedFiles = @()
    $modifiedFiles = @()
    $untrackedFiles = @()
    $deletedFiles = @()

    if ($status) {
        foreach ($line in $status) {
            $code = $line.Substring(0, 2)
            $file = $line.Substring(3)

            if ($code -match "^[A-Z]M$" -or $code -eq "M ") {
                if ($code -match "^[A-Z]") { $stagedFiles += $file } 
                else { $modifiedFiles += $file }
            }
            elseif ($code -eq "??") {
                $untrackedFiles += $file
            }
            elseif ($code -match "D") {
                $deletedFiles += $file
            }
        }
    }

    return @{
        Staged     = $stagedFiles
        Modified   = $modifiedFiles
        Untracked  = $untrackedFiles
        Deleted    = $deletedFiles
    }
}

# Function to check for excluded files
function Get-ExcludedFiles {
    $gitignore = Join-Path $repoRoot ".gitignore"
    $excluded = @()

    if (Test-Path $gitignore) {
        $ignorePatterns = @(Get-Content $gitignore | Where-Object { $_ -and -not $_.StartsWith("#") })
        
        # Check for common excluded patterns
        if ($ignorePatterns -match "venv") { $excluded += "venv*/" }
        if ($ignorePatterns -match "node_modules") { $excluded += "node_modules/" }
        if ($ignorePatterns -match "\.env") { $excluded += ".env files" }
        if ($ignorePatterns -match "\.git") { $excluded += ".git/" }
    }

    return $excluded
}

# Check git is available
Write-Step "Verifying git installation..."
$gitVersion = git --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Git is not installed or not in PATH"
    exit 1
}
Write-Success "Git version: $gitVersion"

# Check if remote is configured
Write-Step "Checking remote configuration..."
$remotes = git remote -v 2>$null
if (-not $remotes) {
    Write-Error-Custom "No git remote configured. Please configure 'origin' remote."
    exit 1
}
Write-Success "Remote configured:`n$remotes"

# Check current branch
$currentBranch = git rev-parse --abbrev-ref HEAD
Write-Step "Current branch: $currentBranch"

# Get current status
Write-Step "Analyzing repository changes..."
$gitStatus = Get-GitStatus
$excluded = Get-ExcludedFiles

Write-Host "`n$($colors.Blue)=== CHANGE SUMMARY ===$($colors.Reset)"
Write-Host "Staged files: $($gitStatus.Staged.Count)"
Write-Host "Modified files: $($gitStatus.Modified.Count)"
Write-Host "Untracked files: $($gitStatus.Untracked.Count)"
Write-Host "Deleted files: $($gitStatus.Deleted.Count)"

if ($gitStatus.Staged.Count -gt 0) {
    Write-Host "`nStaged:`n$($gitStatus.Staged -join "`n")"
}

if ($gitStatus.Modified.Count -gt 0) {
    Write-Host "`nModified:`n$($gitStatus.Modified -join "`n")"
}

if ($gitStatus.Untracked.Count -gt 0) {
    Write-Host "`nUntracked:`n$($gitStatus.Untracked -join "`n")"
}

if ($gitStatus.Deleted.Count -gt 0) {
    Write-Host "`nDeleted:`n$($gitStatus.Deleted -join "`n")"
}

if ($excluded.Count -gt 0) {
    Write-Warning-Custom "Following files are excluded by .gitignore: $($excluded -join ", ")"
}

# Check if there are any changes
$totalChanges = $gitStatus.Staged.Count + $gitStatus.Modified.Count + $gitStatus.Untracked.Count + $gitStatus.Deleted.Count

if ($totalChanges -eq 0) {
    Write-Warning-Custom "No changes to commit"
    exit 0
}

# Confirm before proceeding
Write-Host "`n$($colors.Yellow)About to add $totalChanges changes and push to '$currentBranch'$($colors.Reset)"
if (-not $DryRun) {
    $confirmation = Read-Host "Continue? (yes/no)"
    if ($confirmation -ne "yes") {
        Write-Warning-Custom "Operation cancelled"
        exit 0
    }
}

# Add all changes
Write-Step "Adding all changes to staging area..."
if ($Verbose) {
    git add -A -v
} else {
    git add -A
}

if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Failed to add changes"
    exit 1
}
Write-Success "All changes added to staging"

# Verify staged changes
$stagedAfterAdd = git diff --cached --name-only
if ($Verbose) {
    Write-Host "Staged files:`n$($stagedAfterAdd -join "`n")"
}

# Create commit
Write-Step "Creating commit with message: '$CommitMessage'"
if ($DryRun) {
    Write-Warning-Custom "[DRY RUN] Would commit: $CommitMessage"
} else {
    git commit -m "$CommitMessage"
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Failed to create commit"
        exit 1
    }
    Write-Success "Commit created successfully"
}

# Get commit info
$commitHash = git rev-parse --short HEAD
$commitInfo = git log -1 --format="%h %s"
Write-Success "Latest commit: $commitInfo"

# Check branch status
Write-Step "Checking branch status..."
$trackingInfo = git status -sb
Write-Host $trackingInfo

# Push to remote
Write-Step "Pushing commits to remote repository..."
if ($DryRun) {
    Write-Warning-Custom "[DRY RUN] Would push to origin/$currentBranch"
    git push --dry-run origin $currentBranch 2>&1 | ForEach-Object { Write-Host "  $_" }
} else {
    git push origin $currentBranch
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Failed to push commits"
        exit 1
    }
    Write-Success "Successfully pushed to origin/$currentBranch"
}

# Final verification
Write-Step "Verifying push was successful..."
$finalStatus = git status -sb
Write-Host $finalStatus

Write-Host "`n$($colors.Green)=== OPERATION COMPLETE ===$($colors.Reset)"
Write-Success "All changes have been uploaded to GitHub"
Write-Host "Repository status: $finalStatus"
