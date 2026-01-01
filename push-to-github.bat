@echo off
REM Batch script to update repository and push all changes to GitHub
REM For use with Windows Command Prompt (CMD)
REM Note: For better experience, use PowerShell (push-to-github.ps1) or Python (push_to_github.py)

setlocal enabledelayedexpansion
cd /d %~dp0

echo.
echo ============================================
echo GitHub Repository Update Script (Windows CMD)
echo ============================================
echo.

REM Check if git is available
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git is not installed or not in PATH
    exit /b 1
)

for /f "tokens=*" %%i in ('git --version') do set GIT_VERSION=%%i
echo [SUCCESS] Git found: %GIT_VERSION%
echo.

REM Get repository root
for /f "tokens=*" %%i in ('git rev-parse --show-toplevel 2^>nul') do set REPO_ROOT=%%i
if "%REPO_ROOT%"=="" (
    echo [ERROR] Not in a git repository
    exit /b 1
)
echo [STEP] Repository root: %REPO_ROOT%
cd /d %REPO_ROOT%
echo.

REM Check remote
git remote -v >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No git remote configured
    exit /b 1
)
echo [STEP] Checking remote configuration...
for /f "tokens=*" %%i in ('git remote -v') do (
    echo   %%i
)
echo.

REM Get current branch
for /f "tokens=*" %%i in ('git rev-parse --abbrev-ref HEAD') do set CURRENT_BRANCH=%%i
echo [STEP] Current branch: %CURRENT_BRANCH%
echo.

REM Show status
echo [STEP] Repository changes:
echo.
git status
echo.

REM Count changes
for /f %%i in ('git status --porcelain ^| find /c /v ""') do set CHANGE_COUNT=%%i
if %CHANGE_COUNT%==0 (
    echo [WARNING] No changes to commit
    exit /b 0
)

REM Confirmation
echo.
echo [WARNING] About to add %CHANGE_COUNT% changes and push to '%CURRENT_BRANCH%'
set /p CONFIRM="Continue? (yes/no): "
if /i not "%CONFIRM%"=="yes" (
    echo [WARNING] Operation cancelled
    exit /b 0
)
echo.

REM Add all changes
echo [STEP] Adding all changes to staging area...
git add -A
if errorlevel 1 (
    echo [ERROR] Failed to add changes
    exit /b 1
)
echo [SUCCESS] All changes added
echo.

REM Commit
set /p MESSAGE="Enter commit message (default: Update: Sync all changes to GitHub): "
if "%MESSAGE%"=="" set MESSAGE=Update: Sync all changes to GitHub
echo [STEP] Creating commit: "%MESSAGE%"
git commit -m "%MESSAGE%"
if errorlevel 1 (
    echo [ERROR] Failed to create commit
    exit /b 1
)
echo [SUCCESS] Commit created
echo.

REM Push
echo [STEP] Pushing to origin/%CURRENT_BRANCH%...
git push origin %CURRENT_BRANCH%
if errorlevel 1 (
    echo [ERROR] Failed to push commits
    exit /b 1
)
echo [SUCCESS] Successfully pushed
echo.

REM Final status
echo [STEP] Final repository status:
git status -sb
echo.

echo ============================================
echo [SUCCESS] Operation complete!
echo All changes have been uploaded to GitHub
echo ============================================
echo.

pause
