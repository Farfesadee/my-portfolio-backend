# # email_utils.py
# import os
# import smtplib
# from email.message import EmailMessage
# from dotenv import load_dotenv

# load_dotenv()
# SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
# SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
# SMTP_USERNAME = os.getenv("SMTP_USERNAME")
# SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
# SENDER_EMAIL = os.getenv("SENDER_EMAIL")
# RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

# def send_contact_email(name: str, email: str, message: str, latitude=None, longitude=None):
#     msg = EmailMessage()
#     msg["Subject"] = f"New Contact Message from {name}"
#     msg["From"] = SENDER_EMAIL
#     msg["To"] = RECEIVER_EMAIL
#     body = f"Name: {name}\nEmail: {email}\n\n{message}\n\nLatitude: {latitude}\nLongitude: {longitude}"
#     msg.set_content(body)
#     with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
#         smtp.starttls()
#         smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
#         smtp.send_message(msg)