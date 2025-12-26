#!/usr/bin/env python3
import socket
import argparse
from pathlib import Path

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()

def write_env(path: Path, url: str):
    # Ensure the parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create or update the .env file
    content = f"VITE_API_URL={url}\n"
    path.write_text(content)

def main():
    p = argparse.ArgumentParser(description="Write VITE_API_URL to a .env file using current IP")
    p.add_argument("--port", "-p", default="8000", help="Backend port")
    p.add_argument("--scheme", "-s", default="http", help="URL scheme (http or https)")
    p.add_argument("--env-path", "-e", default=None, help="Path to .env file to write (default: .env in script directory)")
    p.add_argument("--ip", help="Explicit IP to use (skip auto-detect)")
    args = p.parse_args()

    ip = args.ip or get_local_ip()
    url = f"{args.scheme}://{ip}:{args.port}"
    
    # Default to .env in the same directory as this script
    if args.env_path is None:
        script_dir = Path(__file__).parent
        env_path = script_dir / ".env"
    else:
        env_path = Path(args.env_path)
    
    write_env(env_path, url)
    print(f"Wrote {env_path}: VITE_API_URL={url}")

if __name__ == "__main__":
    main()
