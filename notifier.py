# notifier.py
import os
import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from typing import Tuple

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def make_twilio_client():
    sid   = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    frm   = os.getenv("TWILIO_PHONE_NUMBER")
    to    = os.getenv("TWILIO_TO_PHONE_NUMBER")
    
    if sid and token and frm and to:
        return Client(sid, token), frm, to
    
    logger.warning("Twilio credentials missing")
    return None, None, None

def send_sms(prayer: str, time_str: str) -> Tuple[bool, str]:
    """
    Returns (success, message). No UI calls here.
    """
    client, frm, to = make_twilio_client()
    if not client:
        return False, "SMS_NOT_CONFIGURED"
    
    body = f"🕌 Reminder: {prayer} at {time_str}. Wudhu & prepare!"
    try:
        msg = client.messages.create(body=body, from_=frm, to=to)
        logger.info(f"SMS sent, SID={msg.sid}")
        return True, f"SMS queued (SID: {msg.sid})"
    except TwilioRestException as e:
        logger.exception("Twilio API error")
        return False, f"SMS_ERROR: {e.msg}"
