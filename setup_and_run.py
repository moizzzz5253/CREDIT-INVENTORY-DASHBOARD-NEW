#!/usr/bin/env python3
"""
Setup and run script for CREDIT Inventory Dashboard.
This script sets up both backend and frontend environments and runs them in separate terminals.
"""

import subprocess
import sys
import os
import time
from pathlib import Path

# Get the root directory (where this script is located)
ROOT_DIR = Path(__file__).parent.absolute()
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend2"

def run_command(command, cwd=None, shell=True, check=True):
    """Run a command and return the result."""
    print(f"Running: {command}")
    result = subprocess.run(
        command,
        cwd=cwd,
        shell=shell,
        check=check,
        capture_output=False
    )
    return result

def setup_backend():
    """Set up the backend environment."""
    print("\n" + "="*60)
    print("Setting up Backend...")
    print("="*60)
    
    # Navigate to backend directory
    os.chdir(BACKEND_DIR)
    print(f"Current directory: {os.getcwd()}")
    
    # Remove existing venv if it exists (to create fresh one)
    venv_path = BACKEND_DIR / "venv"
    if venv_path.exists():
        print("Removing existing venv...")
        import shutil
        shutil.rmtree(venv_path)
    
    # Create new virtual environment
    print("Creating new virtual environment...")
    run_command(f'python -m venv venv', cwd=BACKEND_DIR)
    
    # Determine the activation script path based on OS
    if sys.platform == "win32":
        activate_script = venv_path / "Scripts" / "activate.bat"
        python_exe = venv_path / "Scripts" / "python.exe"
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:
        activate_script = venv_path / "bin" / "activate"
        python_exe = venv_path / "bin" / "python"
        pip_exe = venv_path / "bin" / "pip"
    
    # Install requirements
    print("Installing requirements.txt...")
    run_command(f'"{pip_exe}" install --upgrade pip', cwd=BACKEND_DIR)
    run_command(f'"{pip_exe}" install -r requirements.txt', cwd=BACKEND_DIR)
    
    print("Backend setup complete!")
    return activate_script, python_exe

def run_backend(activate_script, python_exe):
    """Run the backend in a new PowerShell terminal."""
    print("\n" + "="*60)
    print("Starting Backend Server...")
    print("="*60)
    
    # Create a PowerShell command that:
    # 1. Changes to backend directory
    # 2. Activates venv
    # 3. Runs the backend
    if sys.platform == "win32":
        # Use the Python executable directly from venv
        backend_script = f'''cd "{BACKEND_DIR}"
& "{python_exe}" run_dev.py
pause
'''
    else:
        backend_script = f'''cd "{BACKEND_DIR}"
source "{activate_script}"
python run_dev.py
'''
    
    # Save the script to a temporary file
    script_path = ROOT_DIR / "start_backend.ps1"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(backend_script)
    
    # Run in new PowerShell window
    if sys.platform == "win32":
        subprocess.Popen([
            'powershell.exe',
            '-NoExit',
            '-File',
            str(script_path)
        ])
    else:
        print("Backend would run here on non-Windows systems")
        run_command(f'"{python_exe}" run_dev.py', cwd=BACKEND_DIR, check=False)

def setup_frontend():
    """Set up the frontend environment."""
    print("\n" + "="*60)
    print("Setting up Frontend...")
    print("="*60)
    
    # Navigate to frontend2 directory
    os.chdir(FRONTEND_DIR)
    print(f"Current directory: {os.getcwd()}")
    
    # Check if node_modules exists, if not, install everything
    node_modules = FRONTEND_DIR / "node_modules"
    
    if not node_modules.exists():
        print("Installing npm packages (this may take a few minutes)...")
        run_command('npm install', cwd=FRONTEND_DIR)
    else:
        print("node_modules exists. Installing/updating packages...")
        run_command('npm install', cwd=FRONTEND_DIR)
    
    # Install specific packages if needed (they should be in package.json, but ensure they're installed)
    print("Ensuring all required packages are installed...")
    
    # Check package.json to see what's needed
    package_json = FRONTEND_DIR / "package.json"
    if package_json.exists():
        print("Package.json found. Dependencies should be installed.")
    else:
        print("Warning: package.json not found!")
    
    print("Frontend setup complete!")

def run_frontend():
    """Run the frontend in a new PowerShell terminal."""
    print("\n" + "="*60)
    print("Starting Frontend Server...")
    print("="*60)
    
    # First, run update_env.py to set up the .env file
    print("Setting up .env file with current IP...")
    update_env_script = FRONTEND_DIR / "update_env.py"
    if update_env_script.exists():
        run_command(f'python "{update_env_script}"', cwd=FRONTEND_DIR)
    else:
        print("Warning: update_env.py not found. You may need to set VITE_API_URL manually.")
    
    # Create a PowerShell command to run the frontend
    frontend_script = f'''
cd "{FRONTEND_DIR}"
npm run dev
pause
'''
    
    # Save the script to a temporary file
    script_path = ROOT_DIR / "start_frontend.ps1"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(frontend_script)
    
    # Run in new PowerShell window
    if sys.platform == "win32":
        subprocess.Popen([
            'powershell.exe',
            '-NoExit',
            '-File',
            str(script_path)
        ])
    else:
        print("Frontend would run here on non-Windows systems")
        run_command('npm run dev', cwd=FRONTEND_DIR, check=False)

def main():
    """Main function to set up and run everything."""
    print("\n" + "="*60)
    print("CREDIT Inventory Dashboard - Setup and Run Script")
    print("="*60)
    
    # Check if we're in the right directory
    if not BACKEND_DIR.exists():
        print(f"Error: Backend directory not found at {BACKEND_DIR}")
        sys.exit(1)
    
    if not FRONTEND_DIR.exists():
        print(f"Error: Frontend directory not found at {FRONTEND_DIR}")
        sys.exit(1)
    
    try:
        # Setup backend
        activate_script, python_exe = setup_backend()
        
        # Wait a moment
        time.sleep(1)
        
        # Run backend in new terminal
        run_backend(activate_script, python_exe)
        
        # Wait a moment before starting frontend setup
        print("\nWaiting 3 seconds before starting frontend setup...")
        time.sleep(3)
        
        # Setup frontend
        setup_frontend()
        
        # Wait a moment
        time.sleep(1)
        
        # Run frontend in new terminal
        run_frontend()
        
        print("\n" + "="*60)
        print("Setup Complete!")
        print("="*60)
        print("\nBackend and Frontend should now be running in separate PowerShell windows.")
        print("Backend: http://<your-ip>:8000")
        print("Frontend: Check the frontend terminal for the local URL")
        print("\nPress Ctrl+C in this window to exit (servers will continue running).")
        
        # Keep script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nExiting setup script. Servers will continue running in their own windows.")
    
    except subprocess.CalledProcessError as e:
        print(f"\nError occurred: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

