"""
Email & SMS notifications for shipment rescheduling.
"""

from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER

TEXTBELT_KEY = ""
try:
    from config import TEXTBELT_KEY as _key
    TEXTBELT_KEY = _key
except ImportError:
    pass

# Carrier email-to-SMS gateways (free, no account needed)
CARRIER_GATEWAYS = {
    "verizon": "{number}@vtext.com",
    "att": "{number}@txt.att.net",
    "tmobile": "{number}@tmomail.net",
    "sprint": "{number}@messaging.sprintpcs.com",
    "googlefi": "{number}@msg.fi.google.com",
    "cricket": "{number}@mms.cricketwireless.net",
    "boost": "{number}@sms.myboostmobile.com",
    "uscellular": "{number}@email.uscc.net",
    "virgin": "{number}@vmobl.com",
    "metro": "{number}@mymetropcs.com",
}

# Override the phone-to-email gateway for a specific number
# Format: "15551234567": "15551234567@txt.att.net"
GATEWAY_OVERRIDE = {}


def is_configured() -> bool:
    return bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_PHONE_NUMBER)


def send_reschedule_sms(
    to_number: str,
    client_name: str = "",
    product_type: str = "shipment",
    origin: str = "",
    destination: str = "",
    original_date: str = "",
    new_date: str = "",
    new_date_label: str = "",
    reason: str = "",
    days_moved: int = 0,
    carrier: str = "",
) -> dict:
    if not to_number:
        return {"sent": False, "reason": "No phone number"}

    body = _build_body(client_name, product_type, origin, destination, original_date, new_date, new_date_label, reason, days_moved)

    # Tier 1: Twilio
    if is_configured():
        return _send_via_twilio(to_number, body)

    # Tier 2: Textbelt
    result = _send_via_textbelt(to_number, body)
    if result.get("sent"):
        return result

    # Tier 3: Email-to-SMS gateway
    result = _send_via_gateway(to_number, body, carrier)
    if result.get("sent"):
        return result

    # Tier 4: Nothing worked, return the message for frontend clipboard
    return {"sent": False, "reason": "All providers failed", "messageBody": body, "clipboardReady": True}


def _build_body(client_name, product_type, origin, destination, original_date, new_date, new_date_label, reason, days_moved):
    greeting = f"Hi {client_name}," if client_name else "Hi,"
    product = product_type or "shipment"
    route = f"from {origin} to {destination}" if origin and destination else ""
    new_date_str = new_date_label or new_date

    return (
        f"{greeting} Lumin Stormwatch here.\n\n"
        f"Your {product} shipment {route} originally scheduled for {original_date} "
        f"has been rescheduled to {new_date_str} (+{days_moved} days) due to severe weather.\n\n"
        f"{reason}\n\n"
        f"A calendar update has been sent."
    )


def _send_via_twilio(to_number: str, body: str) -> dict:
    from twilio.rest import Client
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(body=body, from_=TWILIO_PHONE_NUMBER, to=to_number)
        print(f"  📱 Twilio SMS → {to_number}")
        return {"sent": True, "messageSid": message.sid, "to": to_number, "provider": "twilio"}
    except Exception as e:
        print(f"  ⚠️  Twilio failed: {e}")
        return {"sent": False, "reason": str(e), "provider": "twilio"}


def _send_via_textbelt(to_number: str, body: str) -> dict:
    import requests
    try:
        payload = {"phone": to_number, "message": body}
        if TEXTBELT_KEY:
            payload["key"] = TEXTBELT_KEY
        resp = requests.post("https://textbelt.com/text", data=payload, timeout=10)
        data = resp.json()
        if data.get("success"):
            print(f"  📱 Textbelt SMS → {to_number}")
            return {"sent": True, "messageSid": data.get("textId", ""), "provider": "textbelt"}
        print(f"  ⚠️  Textbelt: {data.get('error')}")
        return {"sent": False, "reason": data.get("error", "unknown"), "provider": "textbelt"}
    except Exception as e:
        print(f"  ⚠️  Textbelt error: {e}")
        return {"sent": False, "reason": str(e), "provider": "textbelt"}


def _send_via_gateway(to_number: str, body: str, carrier: str = "") -> dict:
    """
    Send SMS via carrier email-to-SMS gateway.
    Completely free, no account needed. Requires a configured SMTP server.
    """
    import smtplib
    from email.mime.text import MIMEText
    from config import EMAIL_SMTP_HOST, EMAIL_SMTP_PORT, EMAIL_FROM, EMAIL_PASSWORD

    clean = to_number.strip().lstrip("+")
    if len(clean) == 11 and clean.startswith("1"):
        clean = clean[1:]

    if carrier:
        template = CARRIER_GATEWAYS.get(carrier.lower())
    else:
        template = GATEWAY_OVERRIDE.get(to_number.strip())

    if not template:
        print(f"  ⚠️  No carrier gateway for {to_number}")
        return {"sent": False, "reason": "No carrier specified"}

    to_email = template.format(number=clean)

    if not EMAIL_SMTP_HOST or not EMAIL_FROM or not EMAIL_PASSWORD:
        print(f"  ⚠️  SMTP not configured — cannot use email-to-SMS gateway")
        return {"sent": False, "reason": "SMTP not configured"}

    try:
        msg = MIMEText(body)
        msg["From"] = EMAIL_FROM
        msg["To"] = to_email
        msg["Subject"] = "Lumin Shipment Update"

        with smtplib.SMTP(EMAIL_SMTP_HOST, EMAIL_SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, [to_email], msg.as_string())

        print(f"  📱 Email-to-SMS → {to_number} via {carrier or 'gateway'}")
        return {"sent": True, "to": to_number, "provider": f"gateway/{carrier or 'custom'}"}

    except Exception as e:
        print(f"  ⚠️  Gateway SMS failed: {e}")
        return {"sent": False, "reason": str(e), "provider": "gateway"}


def send_reschedule_email(
    to_email: str,
    client_name: str = "",
    product_type: str = "shipment",
    origin: str = "",
    destination: str = "",
    original_date: str = "",
    new_date: str = "",
    new_date_label: str = "",
    reason: str = "",
    days_moved: int = 0,
) -> dict:
    """Send a nicely formatted email to notify a client of shipment rescheduling."""
    if not to_email:
        return {"sent": False, "reason": "No email address"}

    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from config import EMAIL_SMTP_HOST, EMAIL_SMTP_PORT, EMAIL_FROM, EMAIL_PASSWORD

    if not EMAIL_SMTP_HOST or not EMAIL_FROM or not EMAIL_PASSWORD:
        return {"sent": False, "reason": "SMTP not configured. Set EMAIL_FROM and EMAIL_PASSWORD in .env"}

    greeting = f"Hi {client_name}," if client_name else "Hi,"
    product = product_type or "shipment"
    route = f"from {origin} to {destination}" if origin and destination else ""
    new_date_str = new_date_label or new_date

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#0a0f1a;padding:40px 20px;margin:0">
<table width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;margin:0 auto">
  <tr><td style="padding-bottom:24px">
    <h1 style="color:#5ff0e4;font-size:20px;margin:0">⚡ Lumin Stormwatch</h1>
    <p style="color:#64748b;font-size:12px;margin:4px 0 0">Supply Chain Intelligence</p>
  </td></tr>
  <tr><td style="background:#111827;border:1px solid #1e293b;border-radius:12px;padding:32px">
    <h2 style="color:#f1f5f9;font-size:18px;margin:0 0 16px">Shipment Rescheduled</h2>
    <p style="color:#cbd5e1;font-size:14px;line-height:1.6;margin:0 0 24px">
      {greeting}<br><br>
      Your <strong>{product}</strong> shipment {route} originally scheduled for <strong style="text-decoration:line-through;color:#f87171">{original_date}</strong> has been rescheduled due to severe weather conditions along the shipping corridor.
    </p>
    <table width="100%" cellpadding="16" cellspacing="0" style="background:#0f172a;border:1px solid #1e293b;border-radius:8px;margin-bottom:24px">
      <tr><td style="color:#64748b;font-size:12px;padding-bottom:4px">New Delivery Date</td></tr>
      <tr><td style="color:#5ff0e4;font-size:22px;font-weight:700;padding-top:0">{new_date_str}</td></tr>
      <tr><td style="color:#64748b;font-size:12px;padding-top:8px">{days_moved} days later than originally planned</td></tr>
    </table>
    <p style="color:#94a3b8;font-size:13px;line-height:1.6;margin:0 0 24px;padding:16px;background:#0f172a;border-left:3px solid #f59e0b;border-radius:0 8px 8px 0">
      <strong style="color:#f59e0b">Reason:</strong> {reason}
    </p>
    <p style="color:#cbd5e1;font-size:13px;line-height:1.6;margin:0">
      A calendar update has been sent separately. If you have any questions, please contact your logistics coordinator.
    </p>
  </td></tr>
  <tr><td style="padding-top:16px;color:#475569;font-size:11px;text-align:center">
    Powered by Lumin · AI Supply Chain Intelligence
  </td></tr>
</table>
</body>
</html>"""

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"Lumin Stormwatch <{EMAIL_FROM}>"
        msg["To"] = to_email
        msg["Subject"] = f"⚡ Shipment Rescheduled — {product} {route}"
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(EMAIL_SMTP_HOST, EMAIL_SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, [to_email], msg.as_string())

        print(f"  ✉️  Email sent → {to_email}")
        return {"sent": True, "to": to_email, "provider": "email"}

    except Exception as e:
        print(f"  ❌ Email failed: {e}")
        return {"sent": False, "reason": str(e), "provider": "email"}
