import qrcode
import os

def generate_qr(ticket_id):
    os.makedirs("qrcodes", exist_ok=True)
    path = f"qrcodes/{ticket_id}.png"

    img = qrcode.make(ticket_id)
    img.save(path)

    return path
