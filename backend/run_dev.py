#!/usr/bin/env python3
"""
Development server runner for the backend.
Automatically detects the local IP address and runs uvicorn with reload.
"""

import subprocess
import sys
from pathlib import Path

# Add the app directory to the Python path
backend_dir = Path(__file__).parent
app_dir = backend_dir / "app"
sys.path.insert(0, str(app_dir))

from app.core.network import get_local_ip

def main():
    ip = get_local_ip()
    print(f"Detected local IP: {ip}")
    print(f"Starting uvicorn on http://{ip}:8000")

    command = f"uvicorn app.main:app --reload --host {ip} --port 8000"
    try:
        subprocess.run(command, shell=True, cwd=backend_dir)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()