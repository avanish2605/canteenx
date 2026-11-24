import json
import os
import random
import threading
import urllib.error
import urllib.request
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone

from .models import EmailOTP

LOGS_DIR = Path(settings.BASE_DIR) / 'logs'
LOGS_DIR.mkdir(exist_ok=True)
EMAIL_LOG_FILE = LOGS_DIR / 'sent_emails.log'


def _log_email(to_email, subject, text_content):
    timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S %Z')
    divider = "=" * 70
    entry = (
        f"\n{divider}\n"
        f"TIME: {timestamp}\n"
        f"TO: {to_email}\n"
        f"SUBJECT: {subject}\n"
        f"{'-' * 70}\n"
        f"{text_content}\n"
        f"{divider}\n"
    )
    try:
        with open(EMAIL_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(entry)
    except Exception as e:
        print(f"[Email Logger Error] {e}")


def _build_otp_email_html(user, otp_code):
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CanteenX Verification Code</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 24px; color: #1e293b;">
  <div style="max-width: 560px; margin: 0 auto; background: #ffffff; border-radius: 20px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #ea580c 100%); padding: 32px 28px; text-align: center; color: #ffffff;">
      <div style="display: inline-block; background: rgba(255,255,255,0.15); padding: 4px 14px; border-radius: 9999px; font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 12px;">
        Account Verification
      </div>
      <h1 style="margin: 0; font-size: 26px; font-weight: 900; letter-spacing: -0.5px;">CanteenX</h1>
      <p style="margin: 6px 0 0 0; font-size: 13px; color: #fed7aa; font-weight: 500;">Medi-Caps University • Indore</p>
    </div>

    <div style="padding: 32px 28px;">
      <p style="margin: 0 0 16px 0; font-size: 15px; color: #334155;">Hello <strong>{user.full_name}</strong>,</p>
      <p style="margin: 0 0 24px 0; font-size: 14px; color: #64748b; line-height: 1.6;">
        Welcome to CanteenX! Use the 6-digit verification code below to verify your email address and activate your student account.
      </p>

      <div style="background: #fff7ed; border: 2px dashed #fdba74; border-radius: 16px; padding: 24px; text-align: center; margin-bottom: 24px;">
        <span style="font-size: 12px; font-weight: 700; color: #ea580c; text-transform: uppercase; letter-spacing: 1px;">Your Verification Code</span>
        <div style="font-size: 38px; font-weight: 900; letter-spacing: 10px; color: #c2410c; margin: 10px 0; font-family: monospace;">
          {otp_code}
        </div>
        <p style="margin: 0; font-size: 12px; color: #9a3412;">This code expires in <strong>10 minutes</strong>. Do not share it with anyone.</p>
      </div>

      <p style="margin: 0; font-size: 13px; color: #94a3b8; line-height: 1.5;">
        If you did not register for an account on CanteenX, you can safely ignore this email.
      </p>
    </div>

    <div style="background-color: #f1f5f9; padding: 18px 28px; border-top: 1px solid #e2e8f0; text-align: center; font-size: 11px; color: #64748b;">
      <p style="margin: 0;">CanteenX — Smart Campus Dining for Medi-Caps University, Indore</p>
    </div>
  </div>
</body>
</html>
"""


def _send_via_resend(to_email, subject, text_content, html_content=None):
    """Send via Resend HTTP API over HTTPS (Port 443), immune to cloud SMTP port blocks"""
    api_key = getattr(settings, 'RESEND_API_KEY', '') or os.environ.get('RESEND_API_KEY', '')
    if not api_key:
        return False
    from_email = getattr(settings, 'RESEND_FROM_EMAIL', '') or os.environ.get('RESEND_FROM_EMAIL', 'CanteenX <onboarding@resend.dev>')
    payload = json.dumps({
        'from': from_email,
        'to': [to_email] if isinstance(to_email, str) else to_email,
        'subject': subject,
        'html': html_content or f"<pre>{text_content}</pre>",
        'text': text_content,
    }).encode('utf-8')
    req = urllib.request.Request(
        'https://api.resend.com/emails',
        data=payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'CanteenX/1.0',
        },
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status in (200, 201, 202):
                print(f"[Resend API] Successfully sent email to {to_email}")
                return True
            print(f"[Resend API Warning] Failed with status {resp.status}")
            return False
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8', errors='replace')
        print(f"[Resend API HTTPError {e.code}] {err_msg}")
        return False
    except Exception as e:
        print(f"[Resend API Error] {e}")
        return False


def _send_via_brevo(to_email, subject, text_content, html_content=None):
    """Send via Brevo HTTP API over HTTPS (Port 443), works for ANY recipient address without custom domain"""
    api_key = getattr(settings, 'BREVO_API_KEY', '') or os.environ.get('BREVO_API_KEY', '')
    if not api_key:
        return False
    sender_email = getattr(settings, 'EMAIL_HOST_USER', '') or 'canteenmaill@gmail.com'
    payload = json.dumps({
        'sender': {'name': 'CanteenX Medi-Caps', 'email': sender_email},
        'to': [{'email': to_email}],
        'subject': subject,
        'htmlContent': html_content or f"<pre>{text_content}</pre>",
        'textContent': text_content,
    }).encode('utf-8')
    req = urllib.request.Request(
        'https://api.brevo.com/v3/smtp/email',
        data=payload,
        headers={
            'api-key': api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'CanteenX/1.0',
        },
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status in (200, 201, 202):
                print(f"[Brevo API] Successfully sent email to {to_email}")
                return True
            print(f"[Brevo API Warning] Failed with status {resp.status}")
            return False
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8', errors='replace')
        print(f"[Brevo API HTTPError {e.code}] {err_msg}")
        return False
    except Exception as e:
        print(f"[Brevo API Error] {e}")
        return False


def send_otp_email(user, otp_code, async_send=True):
    subject = f"[CanteenX] Your Verification Code: {otp_code}"
    text_content = f"""Dear {user.full_name},

Thank you for registering on CanteenX - Medi-Caps University, Indore!

Your 6-digit email verification code is: {otp_code}

This code is valid for 10 minutes. Enter this code in the CanteenX app to complete your registration.

If you did not request this, please ignore this email.
"""
    html_content = _build_otp_email_html(user, otp_code)

    _log_email(user.email, subject, text_content)
    print(f"[OTP Generated] For: {user.email} | OTP: {otp_code}")

    def _deliver():
        # 1. Try Brevo HTTP API (Port 443, sends to any recipient)
        if _send_via_brevo(user.email, subject, text_content, html_content):
            return

        # 2. Try Resend HTTP API (Port 443)
        if _send_via_resend(user.email, subject, text_content, html_content):
            return

        # 3. Try SMTP
        try:
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'CanteenX Medi-Caps <canteenmaill@gmail.com>')
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)
            print(f"[OTP Email Sent] To: {user.email} | Subject: {subject}")
        except Exception as e:
            print(f"[OTP Email Error] Failed to send OTP email to {user.email}: {e}")

    if async_send:
        t = threading.Thread(target=_deliver, daemon=True)
        t.start()
    else:
        _deliver()


def generate_and_send_otp(user, async_send=True):
    # Invalidate existing unused OTPs
    EmailOTP.objects.filter(user=user, is_used=False).update(is_used=True)

    # Generate 6-digit random code
    otp_code = f"{random.randint(100000, 999999)}"
    expires_at = timezone.now() + timedelta(minutes=10)

    EmailOTP.objects.create(
        user=user,
        otp_code=otp_code,
        expires_at=expires_at,
        attempts=0,
        is_used=False,
    )

    send_otp_email(user, otp_code, async_send=async_send)
    return otp_code
