import os
import qrcode
from app.core.config import get_base_url

BASE_QR_DIR = "qr_codes"


def generate_qr(container_code: str, overwrite: bool = False) -> str:
    os.makedirs(BASE_QR_DIR, exist_ok=True)

    base_url = get_base_url()
    url = f"{base_url}/containers/{container_code}/components"
    qr_file = f"{BASE_QR_DIR}/{container_code}.png"

    if overwrite or not os.path.exists(qr_file):
        img = qrcode.make(url)
        img.save(qr_file)

    return qr_file