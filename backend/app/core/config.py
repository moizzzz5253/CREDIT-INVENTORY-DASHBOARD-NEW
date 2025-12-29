from app.core.network import get_local_ip
import os

API_PORT = 8000
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "5173"))


def get_base_url() -> str:
    ip = get_local_ip()
    print(ip)
    return f"http://{ip}:{API_PORT}"


def get_frontend_url() -> str:
    """
    Get the frontend base URL for QR code generation.
    Uses network IP (not localhost) so QR codes work from other devices.
    Can be overridden with FRONTEND_URL environment variable.
    """
    # Allow override via environment variable
    frontend_url_override = os.getenv("FRONTEND_URL")
    if frontend_url_override:
        print(f"Using FRONTEND_URL override: {frontend_url_override}")
        return frontend_url_override
    
    # Get network IP (not localhost)
    ip = get_local_ip()
    
    # Ensure we're not using localhost/127.0.0.1 for QR codes
    # QR codes need network IP to work from other devices
    if ip in ["127.0.0.1", "localhost"]:
        print(f"WARNING: Network IP detection returned {ip}. QR codes may not work from other devices.")
        print("Consider setting FRONTEND_URL environment variable with your network IP.")
    
    url = f"http://{ip}:{FRONTEND_PORT}"
    print(f"Frontend URL for QR codes: {url}")
    return url
