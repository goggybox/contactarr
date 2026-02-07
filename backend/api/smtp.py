
# -----------------------------contactarr------------------------------
# This file is part of contactarr
# Copyright (C) 2025 goggybox https://github.com/goggybox

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# that this program is licensed under. See LICENSE file. If not
# available, see <https://www.gnu.org/licenses/>.

# Please keep this header comment in all copies of the program.
# --------------------------------------------------------------------

import os
import requests
import re
import smtplib
import json
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
from backend.api.cache import apiGet, clearCache
from backend.api import config

def host():
    cnf = config.get_smtp_config()
    host = cnf['host']
    return host

def set_host(val: str):
    return config.set_config_value("SMTP_HOST", val)

def port():
    cnf = config.get_smtp_config()
    return cnf['port']

def set_port(val: str):
    return config.set_config_value("SMTP_PORT", val)

def user():
    cnf = config.get_smtp_config()
    return cnf['user']

def set_user(val: str):
    return config.set_config_value("SMTP_USER", val)

def password():
    cnf = config.get_smtp_config()
    return cnf['pass']

def set_pass(val: str):
    return config.set_config_value("SMTP_PASS", val)

def validate_recipient_string(rec_str):
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'

    # split recipients if given as list (separated by commas)
    recipients = rec_str.split(",")

    for recipient in recipients:
        if not re.match(regex, recipient):
            return False

    return True

def validate_sender(sender):
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    return re.match(regex, sender)

def send_test_email(sender, recipient):
    # validate emails
    if not validate_sender(sender):
        return {"status": 400, "issue": "sender"}
    if not validate_recipient_string(recipient):
        return {"status": 400, "issue": "recipient"}

    # split recipients if given as list (separated by commas)
    recipients = recipient.split(",")
    cnf = config.get_smtp_config()

    errors = 0
    for r in recipients:
        msg = EmailMessage()
        msg["Subject"] = "contactarr | Testing Testing 123..."
        msg["From"] = sender
        msg["To"] = r
        msg.set_content("If you are reading this, your contactarr email test was successful!")
        try:
            with smtplib.SMTP(cnf['host'], cnf['port']) as smtp:
                smtp.starttls()
                smtp.login(cnf['user'], cnf['pass'])
                smtp.send_message(msg)
        except Exception as e:
            errors += 1
    
    if errors > 0:
        return {"status": 500}

    return {"status": 200}

def send_email_stream(subject: str, html_body: str, recipients: list, sender: str):
    """
    sends individual emails to a list of recipients.
    uses SSE events to return progress updates.
    """
    cnf = config.get_smtp_config()
    total = len(recipients)
    successful = 0
    failed = 0
    results = []

    BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SRC_DIR = os.path.dirname(BACKEND_DIR)
    BANNER_PATH = os.path.join(SRC_DIR, "frontend", "emails", "server", "banner.png")
    yield f"data: {json.dumps({'type': 'start', 'total': total})}\n\n"

    try:
        print(f"[EMAIL STREAM] Connecting to SMTP...")
        with smtplib.SMTP(cnf['host'], cnf['port']) as smtp_conn:
            print(f"[EMAIL STREAM] Connected, starting TLS...")
            smtp_conn.starttls()
            print(f"[EMAIL STREAM] TLS started, logging in...")
            smtp_conn.login(cnf['user'], cnf['pass'])
            print(f"[EMAIL STREAM] Logged in successfully")

            for idx, recipient in enumerate(recipients, 1):
                print(f"[EMAIL STREAM] Processing {idx}/{total}: {recipient}")
                try:
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = subject
                    msg['From'] = sender
                    msg['To'] = recipient

                    html_with_cid = html_body.replace('src="banner.png"', 'src="cid:banner_image"')
                    msg_html = MIMEText(html_with_cid, 'html')
                    msg.attach(msg_html)

                    if os.path.exists(BANNER_PATH):
                        with open(BANNER_PATH, 'rb') as img_file:
                            img_data = img_file.read()
                            img = MIMEImage(img_data)
                            img.add_header('Content-ID', '<banner_image>')
                            img.add_header('Content-Disposition', 'inline', filename='banner.png')
                            msg.attach(img)

                    smtp_conn.sendmail(sender, [recipient], msg.as_string())
                    
                    successful += 1
                    result = {
                        "type": "progress",
                        "current": idx,
                        "total": total,
                        "recipient": recipient,
                        "status": "success",
                        "successful": successful,
                        "failed": failed
                    }
                except Exception as e:
                    failed += 1
                    result = {
                        "type": "progress",
                        "current": idx,
                        "total": total,
                        "recipient": recipient,
                        "status": "failed",
                        "error": str(e),
                        "successful": successful,
                        "failed": failed
                    }

                # BUG FIX: 'resulst' -> 'results'
                results.append(result)
                yield f"data: {json.dumps(result)}\n\n"

        print(f"[EMAIL STREAM] All done. Successful: {successful}, Failed: {failed}")
        final_data = {'type': 'complete', 'total': total, 'successful': successful, 'failed': failed, 'results': results}
        print(f"[EMAIL STREAM] Yielding complete: {final_data}")
        yield f"data: {json.dumps(final_data)}\n\n"

    except Exception as e:
        print(f"[EMAIL STREAM] CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"