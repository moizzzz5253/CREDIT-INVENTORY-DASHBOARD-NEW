from app.core.network import get_local_ip
import os

API_PORT = int(os.getenv("API_PORT", "8000"))
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "5173"))


def get_base_url() -> str:
    """
    Get the backend base URL.
    In containerized environments, use API_HOST environment variable.
    Falls back to network IP detection for local development.
    """
    # Check for explicit API host (for containerized environments)
    api_host = os.getenv("API_HOST")
    if api_host:
        url = f"http://{api_host}:{API_PORT}"
        print(f"Using API_HOST environment variable: {url}")
        return url
    
    # For local development, detect network IP
    ip = get_local_ip()
    url = f"http://{ip}:{API_PORT}"
    print(f"Backend URL (detected): {url}")
    return url


def get_frontend_url() -> str:
    """
    Get the frontend base URL for QR code generation.
    Uses network IP (not localhost) so QR codes work from other devices.
    Can be overridden with FRONTEND_URL environment variable.
    In containerized environments, FRONTEND_URL should be set explicitly.
    """
    # Allow override via environment variable (recommended for containers)
    frontend_url_override = os.getenv("FRONTEND_URL")
    if frontend_url_override:
        print(f"Using FRONTEND_URL override: {frontend_url_override}")
        return frontend_url_override
    
    # For local development, get network IP (not localhost)
    ip = get_local_ip()
    
    # Ensure we're not using localhost/127.0.0.1 for QR codes
    # QR codes need network IP to work from other devices
    if ip in ["127.0.0.1", "localhost"]:
        print(f"WARNING: Network IP detection returned {ip}. QR codes may not work from other devices.")
        print("Consider setting FRONTEND_URL environment variable with your network IP.")
    
    url = f"http://{ip}:{FRONTEND_PORT}"
    print(f"Frontend URL for QR codes (detected): {url}")
    return url
