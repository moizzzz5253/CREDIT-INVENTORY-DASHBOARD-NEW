#!/usr/bin/env python3
"""
Script to update repository and push all changes to GitHub.
Ensures no changes are left behind.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Tuple

# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def print_step(message: str) -> None:
    """Print a step message."""
    print(f"{Colors.CYAN}[STEP]{Colors.RESET} {message}")

def print_success(message: str) -> None:
    """Print a success message."""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.RESET} {message}")

def print_error(message: str) -> None:
    """Print an error message."""
    print(f"{Colors.RED}[ERROR]{Colors.RESET} {message}")

def print_warning(message: str) -> None:
    """Print a warning message."""
    print(f"{Colors.YELLOW}[WARNING]{Colors.RESET} {message}")

def run_command(cmd: str, capture_output: bool = False, check: bool = True) -> Tuple[int, str]:
    """
    Run a shell command and return exit code and output.
    
    Args:
        cmd: Command to run
        capture_output: Whether to capture output
        check: Whether to raise exception on non-zero exit code
    
    Returns:
        Tuple of (exit_code, output)
    """
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
            return result.returncode, result.stdout.strip()
        else:
            result = subprocess.run(cmd, shell=True, check=check)
            return result.returncode, ""
    except subprocess.CalledProcessError as e:
        if check:
            raise
        return e.returncode, e.stdout if capture_output else ""

def get_git_status() -> dict:
    """Get current git status and categorize files."""
    status_output, _ = run_command("git status --porcelain", capture_output=True)
    
    staged = []
    modified = []
    untracked = []
    deleted = []
    
    for line in status_output.split('\n'):
        if not line.strip():
            continue
        
        code = line[:2]
        file = line[3:]
        
        if code[0] in 'ACMR' or (code[0] == 'M' and code[1] == ' '):
            if code[0].isupper():
                staged.append(file)
            else:
                modified.append(file)
        elif code == '??':
            untracked.append(file)
        elif code[0] == 'D' or code[1] == 'D':
            deleted.append(file)
    
    return {
        'staged': staged,
        'modified': modified,
        'untracked': untracked,
        'deleted': deleted
    }

def get_git_root() -> str:
    """Get the git repository root directory."""
    try:
        root, _ = run_command("git rev-parse --show-toplevel", capture_output=True)
        return root
    except:
        return None

def check_git_available() -> bool:
    """Check if git is installed and available."""
    try:
        version, _ = run_command("git --version", capture_output=True)
        return True
    except:
        return False

def get_current_branch() -> str:
    """Get the current git branch."""
    branch, _ = run_command("git rev-parse --abbrev-ref HEAD", capture_output=True)
    return branch

def get_remote_info() -> str:
    """Get git remote information."""
    remotes, _ = run_command("git remote -v", capture_output=True)
    return remotes

def get_tracking_info() -> str:
    """Get tracking branch information."""
    info, _ = run_command("git status -sb", capture_output=True)
    return info

def get_pending_commits() -> int:
    """Get number of commits ahead of remote."""
    try:
        info = get_tracking_info()
        # Parse "ahead X" from status
        if "ahead" in info:
            for word in info.split():
                if word.isdigit():
                    return int(word)
    except:
        pass
    return 0

def main():
    parser = argparse.ArgumentParser(
        description="Update repository and push all changes to GitHub"
    )
    parser.add_argument(
        '-m', '--message',
        default="Update: Sync all changes to GitHub",
        help="Commit message (default: 'Update: Sync all changes to GitHub')"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Verify git is available
    print_step("Verifying git installation...")
    if not check_git_available():
        print_error("Git is not installed or not in PATH")
        sys.exit(1)
    
    try:
        version, _ = run_command("git --version", capture_output=True)
        print_success(f"Git version: {version}")
    except Exception as e:
        print_error(f"Failed to get git version: {e}")
        sys.exit(1)
    
    # Get repository root
    repo_root = get_git_root()
    if not repo_root:
        print_error("Not in a git repository. Exiting.")
        sys.exit(1)
    
    print_step(f"Repository root: {repo_root}")
    os.chdir(repo_root)
    
    # Check remote is configured
    print_step("Checking remote configuration...")
    remotes = get_remote_info()
    if not remotes:
        print_error("No git remote configured. Please configure 'origin' remote.")
        sys.exit(1)
    print_success(f"Remote configured:\n{remotes}")
    
    # Check current branch
    current_branch = get_current_branch()
    print_step(f"Current branch: {current_branch}")
    
    # Get git status
    print_step("Analyzing repository changes...")
    status = get_git_status()
    
    # Print summary
    print(f"\n{Colors.BLUE}=== CHANGE SUMMARY ==={Colors.RESET}")
    print(f"Staged files: {len(status['staged'])}")
    print(f"Modified files: {len(status['modified'])}")
    print(f"Untracked files: {len(status['untracked'])}")
    print(f"Deleted files: {len(status['deleted'])}")
    
    if status['staged']:
        print(f"\nStaged:")
        for file in status['staged']:
            print(f"  {file}")
    
    if status['modified']:
        print(f"\nModified:")
        for file in status['modified']:
            print(f"  {file}")
    
    if status['untracked']:
        print(f"\nUntracked:")
        for file in status['untracked']:
            print(f"  {file}")
    
    if status['deleted']:
        print(f"\nDeleted:")
        for file in status['deleted']:
            print(f"  {file}")
    
    # Check if there are any changes
    total_changes = (len(status['staged']) + len(status['modified']) + 
                    len(status['untracked']) + len(status['deleted']))
    
    if total_changes == 0:
        print_warning("No changes to commit")
        sys.exit(0)
    
    # Check for pending commits
    pending = get_pending_commits()
    if pending > 0:
        print_warning(f"You have {pending} commits not yet pushed")
    
    # Confirm before proceeding
    print(f"\n{Colors.YELLOW}About to add {total_changes} changes and push to '{current_branch}'{Colors.RESET}")
    
    if not args.dry_run:
        confirmation = input("Continue? (yes/no): ").strip().lower()
        if confirmation != "yes":
            print_warning("Operation cancelled")
            sys.exit(0)
    
    # Add all changes
    print_step("Adding all changes to staging area...")
    if args.verbose:
        run_command("git add -A -v")
    else:
        run_command("git add -A")
    print_success("All changes added to staging")
    
    # Verify staged changes
    staged_files, _ = run_command("git diff --cached --name-only", capture_output=True)
    if args.verbose:
        print("Staged files:")
        for file in staged_files.split('\n'):
            if file:
                print(f"  {file}")
    
    # Create commit
    print_step(f"Creating commit with message: '{args.message}'")
    if args.dry_run:
        print_warning(f"[DRY RUN] Would commit: {args.message}")
    else:
        try:
            run_command(f'git commit -m "{args.message}"')
            print_success("Commit created successfully")
        except subprocess.CalledProcessError:
            print_error("Failed to create commit")
            sys.exit(1)
    
    # Get commit info
    if not args.dry_run:
        try:
            commit_hash, _ = run_command("git rev-parse --short HEAD", capture_output=True)
            commit_info, _ = run_command("git log -1 --format='%h %s'", capture_output=True)
            print_success(f"Latest commit: {commit_info}")
        except:
            pass
    
    # Check branch status
    print_step("Checking branch status...")
    tracking_info = get_tracking_info()
    print(tracking_info)
    
    # Push to remote
    print_step("Pushing commits to remote repository...")
    if args.dry_run:
        print_warning(f"[DRY RUN] Would push to origin/{current_branch}")
        run_command(f"git push --dry-run origin {current_branch}")
    else:
        try:
            run_command(f"git push origin {current_branch}")
            print_success(f"Successfully pushed to origin/{current_branch}")
        except subprocess.CalledProcessError:
            print_error("Failed to push commits")
            sys.exit(1)
    
    # Final verification
    print_step("Verifying push was successful...")
    final_status = get_tracking_info()
    print(final_status)
    
    print(f"\n{Colors.GREEN}=== OPERATION COMPLETE ==={Colors.RESET}")
    print_success("All changes have been uploaded to GitHub")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
