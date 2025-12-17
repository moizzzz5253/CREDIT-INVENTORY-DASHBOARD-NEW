from app.core.network import get_local_ip

API_PORT = 8000


def get_base_url() -> str:
    ip = get_local_ip()
    print(ip)
    return f"http://{ip}:{API_PORT}"
