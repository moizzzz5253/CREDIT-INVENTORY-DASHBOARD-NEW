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
    content = f"VITE_API_URL={url}\n"
    path.write_text(content)

def main():
    p = argparse.ArgumentParser(description="Write VITE_API_URL to a .env file using current IP")
    p.add_argument("--port", "-p", default="8000", help="Backend port")
    p.add_argument("--scheme", "-s", default="http", help="URL scheme (http or https)")
    p.add_argument("--env-path", "-e", default=".env", help="Path to .env file to write")
    p.add_argument("--ip", help="Explicit IP to use (skip auto-detect)")
    args = p.parse_args()

    ip = args.ip or get_local_ip()
    url = f"{args.scheme}://{ip}:{args.port}"
    env_path = Path(args.env_path)
    write_env(env_path, url)
    print(f"Wrote {env_path}: VITE_API_URL={url}")

if __name__ == "__main__":
    main()
