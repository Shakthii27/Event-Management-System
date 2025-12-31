import smtplib
from email.message import EmailMessage
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SENDER_EMAIL = "shakthisridevi20151@gmail.com"
SENDER_PASSWORD = "xdosqfolpuijqksn"  # Gmail App Password

def send_mail(to_email, ticket_id, qr_path, event):
    msg = EmailMessage()
    msg["Subject"] = f"🎟 Ticket Confirmation – {event['name']}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    msg.set_content(f"""
Hello 👋,

You have successfully registered for the event!

📌 Event Details
------------------------
Event: {event['name']}
Date: {event['date']}
Time: {event['time']}
Venue: {event['venue']}

🎫 Ticket ID:
{ticket_id}

📎 Your QR code is attached to this email.
Please show it at the venue for check-in.

See you there!
""")

    # Attach QR image
    with open(qr_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="image",
            subtype="png",
            filename="ticket_qr.png"
        )

    # Send mail
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
