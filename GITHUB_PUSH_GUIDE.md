# GitHub Push Scripts - Complete Guide

This directory contains scripts to safely update the repository and push all changes to GitHub without leaving anything behind.

## Scripts Provided

### 1. PowerShell Script (`push-to-github.ps1`)
**Platform:** Windows PowerShell 5.1+

#### Usage:
```powershell
# Basic usage with default commit message
.\push-to-github.ps1

# Custom commit message
.\push-to-github.ps1 -CommitMessage "My custom update message"

# Dry run to see what would happen
.\push-to-github.ps1 -DryRun

# Verbose output
.\push-to-github.ps1 -Verbose

# Combine options
.\push-to-github.ps1 -CommitMessage "Fix: Resolve bugs" -DryRun -Verbose
```

#### Features:
- ✅ Comprehensive change detection (staged, modified, untracked, deleted)
- ✅ Remote configuration verification
- ✅ Branch tracking status
- ✅ Dry-run mode for safety
- ✅ Verbose output option
- ✅ Colored console output for clarity
- ✅ Error handling and validation
- ✅ Final verification after push

### 2. Python Script (`push_to_github.py`)
**Platform:** Windows, macOS, Linux (requires Python 3.6+)

#### Usage:
```bash
# Basic usage with default commit message
python push_to_github.py

# Custom commit message
python push_to_github.py -m "My custom update message"
python push_to_github.py --message "My custom update message"

# Dry run to see what would happen
python push_to_github.py --dry-run

# Verbose output
python push_to_github.py -v
python push_to_github.py --verbose

# Combine options
python push_to_github.py -m "Fix: Resolve bugs" --dry-run -v
```

#### Features:
- ✅ Cross-platform compatibility
- ✅ Comprehensive change detection
- ✅ Remote configuration verification
- ✅ Branch tracking status
- ✅ Dry-run mode for safety
- ✅ Verbose output option
- ✅ Colored console output
- ✅ Error handling and validation
- ✅ Final verification after push

## Pre-Push Checklist

Before running either script, ensure:

1. **Git is installed** and accessible from your terminal/PowerShell
2. **You're in a git repository** (the project root directory)
3. **Remote 'origin' is configured** (typically points to GitHub)
4. **You have authentication** configured for GitHub (SSH keys or personal access tokens)
5. **You have write permissions** to the repository

## What the Scripts Do

The scripts perform the following steps in order:

1. **Verification Phase**
   - Check git is installed and available
   - Verify repository is valid
   - Confirm remote is configured
   - Display current branch

2. **Analysis Phase**
   - Scan all changes (staged, modified, untracked, deleted)
   - Count files in each category
   - Display detailed summary of changes
   - Check for pending commits

3. **Confirmation Phase**
   - Show total number of changes
   - Ask for user confirmation (unless `--dry-run`)
   - Allow cancellation

4. **Execution Phase**
   - Stage ALL changes with `git add -A`
   - Create commit with provided message
   - Push to remote branch

5. **Verification Phase**
   - Verify push was successful
   - Display final repository status

## What Gets Pushed

The scripts use `git add -A` which captures:
- ✅ **Modified files** - Changed but not staged
- ✅ **New files** - Untracked files
- ✅ **Deleted files** - Removed files
- ✅ **Already staged files** - Files in the staging area
- ❌ **Ignored files** - Files in `.gitignore` are skipped (as intended)

### Important Note About `.gitignore`
Files matching patterns in `.gitignore` are NOT pushed. Common excluded items:
- `venv/`, `venvPC/` - Python virtual environments
- `node_modules/` - npm packages
- `.env` - Environment files with secrets
- Other build artifacts and cache directories

If you need to force-push ignored files, you must explicitly `git add -f <filename>` first.

## Safety Features

Both scripts include multiple safety mechanisms:

1. **Dry-Run Mode**
   ```powershell
   .\push-to-github.ps1 -DryRun
   ```
   Shows what would happen without making changes

2. **Change Summary**
   Before proceeding, the script displays all changes so you can review

3. **User Confirmation**
   You must confirm (type "yes") before any changes are made

4. **Error Handling**
   Scripts exit gracefully on any git operation failure

## Troubleshooting

### "Git is not installed or not in PATH"
- Ensure Git is installed on your system
- Add Git to your PATH environment variable

### "No git remote configured"
- Set up a remote with: `git remote add origin <github-url>`
- Verify with: `git remote -v`

### "Permission denied" on PowerShell
```powershell
# Enable script execution (run once)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Failed to push commits"
Common causes:
- No GitHub authentication configured (set up SSH keys or personal access tokens)
- Remote URL is incorrect
- Branch is protected and requires pull requests
- Network connection issues

Solutions:
```bash
# Test connection
git push --dry-run origin main

# Check authentication
git -c credential.helper= ls-remote https://github.com/<user>/<repo>.git
```

### "You have X commits not yet pushed"
This means previous pushes were unsuccessful. The script will push all pending commits.

## Current Repository Status

**Before running the script:**
- Branch: `main`
- Commits ahead of origin: 3
- Files to be added: 15+ modified, 6+ untracked, 1 deleted

**All these will be included in the push.**

## Example Workflow

### Using PowerShell (Windows)
```powershell
# Navigate to repository
cd 'c:\Cursor IDE\CREDIT-INVENTORY-DASHBOARD-NEW'

# Dry run first to verify
.\push-to-github.ps1 -DryRun -Verbose

# Actual push with custom message
.\push-to-github.ps1 -CommitMessage "Feat: Add location system and component updates"
```

### Using Python (Any Platform)
```bash
# Navigate to repository
cd 'path/to/CREDIT-INVENTORY-DASHBOARD-NEW'

# Dry run first to verify
python push_to_github.py --dry-run -v

# Actual push with custom message
python push_to_github.py -m "Feat: Add location system and component updates"
```

## Scheduling Regular Pushes

### Windows Task Scheduler
```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy RemoteSigned -File 'C:\path\to\push-to-github.ps1'"
$trigger = New-ScheduledTaskTrigger -AtLogon
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries
Register-ScheduledTask -Action $action -Trigger $trigger -Principal $principal -Settings $settings -TaskName "GitPushRepository" -Description "Automatic push to GitHub"
```

### Linux/macOS Cron
```bash
# Edit crontab
crontab -e

# Add line to run daily at 10 AM
0 10 * * * cd /path/to/repo && python3 push_to_github.py -m "Automated daily push"
```

## Support & Issues

If you encounter issues:

1. **Run in dry-run mode first** to see what would happen
2. **Check git status manually**: `git status`
3. **Verify authentication**: `git ls-remote origin`
4. **Check network connectivity**: `ping github.com`
5. **Review git logs**: `git log --oneline -5`

## Additional Git Commands for Manual Control

```bash
# See what would be added
git add -A --dry-run

# Stage only specific files
git add <file1> <file2>

# Unstage files
git reset HEAD <file>

# View detailed changes
git diff

# Push with specific options
git push -u origin main  # Set upstream
git push --force        # Force push (use with caution!)
git push --tags        # Push tags along with commits
```

---

**Created:** January 2026
**Purpose:** Safe, automated repository updates and GitHub pushes
