# SPDX-License-Identifier: BUSL-1.1
# Copyright (c) 2026 pyoneerC. All rights reserved.

import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("legacy_vault")

# Resend API
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "Deadhand Protocol <hello@deadhandprotocol.com>")

# Email configuration - supports Gmail SMTP (free) as fallback
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_email(to_email: str, subject: str, content: str):
    """
    Sends an email using:
    1. Resend API (Preferred)
    2. Gmail SMTP (Fallback)
    3. Mock logger (Fallback for development)
    """
    
    # 1. Try Resend (Fast & Reliable)
    if RESEND_API_KEY and "your_" not in RESEND_API_KEY:
        try:
            import resend
            resend.api_key = RESEND_API_KEY
            
            params = {
                "from": FROM_EMAIL,
                "to": [to_email],
                "reply_to": "hello@deadhandprotocol.com",
                "subject": subject,
                "html": content,
            }
            
            resend.Emails.send(params)
            logger.info(f"Email sent via Resend to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email via Resend: {str(e)}")
            # Fall through
            
    # 2. Try Gmail SMTP Fallback
    if SMTP_USER and SMTP_PASSWORD and "your_" not in SMTP_PASSWORD:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = FROM_EMAIL
            msg['To'] = to_email
            
            html_part = MIMEText(content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(msg['From'], to_email, msg.as_string())
            
            logger.info(f"Email sent via SMTP to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email via SMTP: {str(e)}")
    
    # 3. Mock / Fallback for development
    logger.info(f"--- MOCK EMAIL ---")
    logger.info(f"To: {to_email}")
    logger.info(f"Subject: {subject}")
    logger.info(f"------------------")
    
    with open("email_log.txt", "a") as f:
        f.write(f"To: {to_email}\nSubject: {subject}\nContent: {content}\n---\n")
    return True
