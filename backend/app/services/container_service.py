import os
import qrcode
from app.core.config import get_frontend_url

BASE_QR_DIR = "qr_codes"


def generate_qr(container_code: str, overwrite: bool = False) -> str:
    os.makedirs(BASE_QR_DIR, exist_ok=True)

    frontend_url = get_frontend_url()
    url = f"{frontend_url}/containers/{container_code}"
    qr_file = f"{BASE_QR_DIR}/{container_code}.png"
    
    print(f"Generating QR code for {container_code}: {qr_file}")
    print(f"QR code URL: {url}")

    if overwrite or not os.path.exists(qr_file):
        img = qrcode.make(url)
        img.save(qr_file)
        print(f"QR code saved: {qr_file}")

    return qr_file