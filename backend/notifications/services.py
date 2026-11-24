import os
import re
import threading
from datetime import datetime
from pathlib import Path
from urllib import parse, request as urllib_request

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone

from notifications.models import Notification


# Ensure logs directory exists
LOGS_DIR = Path(settings.BASE_DIR) / 'logs'
LOGS_DIR.mkdir(exist_ok=True)
EMAIL_LOG_FILE = LOGS_DIR / 'sent_emails.log'
WHATSAPP_LOG_FILE = LOGS_DIR / 'whatsapp_messages.log'


def _frontend_url():
    return getattr(settings, 'FRONTEND_URL', 'http://127.0.0.1:5173').rstrip('/')


def _format_phone_e164(phone):
    """Normalize phone number to E.164 standard (e.g. +91XXXXXXXXXX)"""
    if not phone:
        return None
    cleaned = re.sub(r'[^\d+]', '', str(phone).strip())
    if not cleaned:
        return None
    if cleaned.startswith('+'):
        return cleaned
    if len(cleaned) == 10:
        return f"+91{cleaned}"
    if len(cleaned) == 12 and cleaned.startswith('91'):
        return f"+{cleaned}"
    return f"+{cleaned}"


def _log_email(to_email, subject, text_content):
    """Audit logging for emails (mirrors existing test_cafine_and_email.py expectation)"""
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


def _log_whatsapp(to_number, message):
    """Audit logging for WhatsApp messages"""
    timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S %Z')
    divider = "=" * 70
    entry = (
        f"\n{divider}\n"
        f"TIME: {timestamp}\n"
        f"TO: {to_number}\n"
        f"WHATSAPP MESSAGE:\n"
        f"{message}\n"
        f"{divider}\n"
    )
    try:
        with open(WHATSAPP_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(entry)
    except Exception as e:
        print(f"[WhatsApp Logger Error] {e}")


def _send_email_safe(to_email, subject, text_body, html_body=None):
    """Send email with graceful fallback and audit logging"""
    if not to_email:
        return
    _log_email(to_email, subject, text_body)

    # 1. Try Brevo HTTP API (Port 443 HTTPS, works for any recipient)
    try:
        from accounts.services import _send_via_brevo
        if _send_via_brevo(to_email, subject, text_body, html_body):
            return
    except Exception as e:
        print(f"[Brevo Hook Error] {e}")

    # 2. Try Resend HTTP API (Port 443 HTTPS)
    try:
        from accounts.services import _send_via_resend
        if _send_via_resend(to_email, subject, text_body, html_body):
            return
    except Exception as e:
        print(f"[Resend Hook Error] {e}")

    # 2. Fallback to standard SMTP
    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'CanteenX Medi-Caps <canteenmaill@gmail.com>')
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=from_email,
            to=[to_email]
        )
        if html_body:
            msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)
        print(f"[Email Sent] To: {to_email} | Subject: {subject}")
    except Exception as e:
        print(f"[Email Error] Failed to send email to {to_email}: {e}")


def _send_whatsapp_safe(to_number, message):
    """
    Send WhatsApp message using Twilio API if credentials configured,
    otherwise log safely to console and logs/whatsapp_messages.log.
    """
    normalized_to = _format_phone_e164(to_number)
    if not normalized_to:
        print("[WhatsApp Skip] No valid phone number provided.")
        return

    _log_whatsapp(normalized_to, message)

    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
    auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
    from_number = getattr(settings, 'TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')

    if not account_sid or not auth_token:
        print(f"[WhatsApp Console/Fallback] To: {normalized_to}\n{message}\n")
        return

    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        payload = parse.urlencode({
            'From': from_number if from_number.startswith('whatsapp:') else f'whatsapp:{from_number}',
            'To': f'whatsapp:{normalized_to}',
            'Body': message,
        }).encode('utf-8')

        req = urllib_request.Request(url, data=payload, method='POST')
        import base64
        auth_bytes = f"{account_sid}:{auth_token}".encode('ascii')
        base64_auth = base64.b64encode(auth_bytes).decode('ascii')
        req.add_header('Authorization', f'Basic {base64_auth}')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')

        with urllib_request.urlopen(req, timeout=10) as resp:
            print(f"[WhatsApp API Success] Sent to {normalized_to} (HTTP {resp.status})")
    except Exception as e:
        print(f"[WhatsApp API Error] Could not send via Twilio to {normalized_to}: {e}")


# ==============================================================================
# HTML EMAIL TEMPLATES BUILDERS
# ==============================================================================

def _get_base_html(title, header_badge, body_content, order):
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 24px; color: #1e293b;">
  <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 20px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
    <!-- Top Brand Header -->
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #ea580c 100%); padding: 32px 28px; text-align: center; color: #ffffff;">
      <div style="display: inline-block; background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); padding: 4px 12px; border-radius: 9999px; font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 12px;">
        {header_badge}
      </div>
      <h1 style="margin: 0; font-size: 26px; font-weight: 900; letter-spacing: -0.5px;">CanteenX</h1>
      <p style="margin: 6px 0 0 0; font-size: 13px; color: #fed7aa; font-weight: 500;">Medi-Caps University Campus Dining • Indore</p>
    </div>

    <!-- Main Content -->
    <div style="padding: 32px 28px;">
      {body_content}
    </div>

    <!-- Footer -->
    <div style="background-color: #f1f5f9; padding: 20px 28px; border-top: 1px solid #e2e8f0; text-align: center; font-size: 11px; color: #64748b;">
      <p style="margin: 0 0 6px 0; font-weight: 600;">CanteenX — Smart Campus Dining for Medi-Caps University</p>
      <p style="margin: 0;">For queries or counter assistance, visit {order.canteen.name} ({order.canteen.location}).</p>
    </div>
  </div>
</body>
</html>
"""


def _generate_items_html(order):
    rows = ""
    for item in order.items.all():
        rows += f"""
        <tr style="border-bottom: 1px solid #f1f5f9;">
          <td style="padding: 12px 0; font-weight: 600; font-size: 13px; color: #0f172a;">{item.item_name}</td>
          <td style="padding: 12px 8px; text-align: center; font-size: 13px; color: #475569;">x{item.quantity}</td>
          <td style="padding: 12px 0; text-align: right; font-weight: 700; font-size: 13px; color: #0f172a;">Rs. {item.subtotal:.2f}</td>
        </tr>
        """
    return f"""
    <table style="width: 100%; border-collapse: collapse; margin-top: 16px;">
      <thead>
        <tr style="border-bottom: 2px solid #e2e8f0; text-align: left; font-size: 11px; text-transform: uppercase; color: #64748b; letter-spacing: 0.5px;">
          <th style="padding-bottom: 8px;">Dish</th>
          <th style="padding-bottom: 8px; text-align: center;">Qty</th>
          <th style="padding-bottom: 8px; text-align: right;">Total</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
    """


# ==============================================================================
# INDIVIDUAL EVENT HANDLERS
# ==============================================================================

def handle_order_placed(order):
    student = order.student
    to_email = student.email
    phone = student.mobile
    canteen = order.canteen

    subject = f"[CanteenX] Order Received #{order.order_number} - Waiting for {canteen.name} Acceptance"

    items_list_text = "\n".join([
        f"  - {item.quantity}x {item.item_name} @ Rs. {item.item_price:.2f} = Rs. {item.subtotal:.2f}"
        for item in order.items.all()
    ])

    text_body = f"""Dear {student.full_name},

Thank you for ordering on CanteenX - Medi-Caps University, Indore!

Your order has been SUBMITTED and is currently AWAITING ACCEPTANCE by {canteen.name}.

ORDER DETAILS:
- Order Number: #{order.order_number}
- Canteen: {canteen.name} ({canteen.location})
- Time: {timezone.localtime(order.created_at).strftime('%d %b %Y, %I:%M %p')}
- Payment: {order.payment_method.upper()} (Rs. {order.total_amount:.2f})

ITEMS ORDERED:
{items_list_text}

TOTAL: Rs. {order.total_amount:.2f}

STATUS: PENDING CANTEEN ACCEPTANCE
Once {canteen.name} accepts your order, you will receive an acceptance email with your pickup PIN.

View Order Pass: {_frontend_url()}/orders/{order.id}
"""

    html_content = f"""
    <div style="background-color: #fffbeb; border: 1px solid #fde68a; border-radius: 12px; padding: 16px; margin-bottom: 24px;">
      <p style="margin: 0; font-size: 14px; font-weight: 700; color: #b45309;">STATUS: PENDING CANTEEN ACCEPTANCE</p>
      <p style="margin: 4px 0 0 0; font-size: 13px; color: #92400e;">
        {canteen.name} is reviewing capacity. Your official pickup PIN activates upon order confirmation.
      </p>
    </div>

    <h2 style="margin: 0 0 8px 0; font-size: 18px; font-weight: 800; color: #0f172a;">Order Placed: #{order.order_number}</h2>
    <p style="margin: 0 0 16px 0; font-size: 13px; color: #475569;">
      Canteen: <strong>{canteen.name}</strong> • Total: <strong>Rs. {order.total_amount:.2f}</strong> ({order.payment_method.upper()})
    </p>

    {_generate_items_html(order)}

    <div style="margin-top: 24px; text-align: center;">
      <a href="{_frontend_url()}/orders/{order.id}" style="display: inline-block; background: #ea580c; color: #ffffff; text-decoration: none; font-weight: 700; font-size: 13px; padding: 12px 24px; border-radius: 10px;">
        Track Live Status
      </a>
    </div>
    """
    html_body = _get_base_html(subject, "Order Booked", html_content, order)
    _send_email_safe(to_email, subject, text_body, html_body)

    # WhatsApp message
    wa_msg = (
        f"🍔 *CanteenX: Order Placed!*\n"
        f"Hi {student.full_name}, your order *#{order.order_number}* for *{canteen.name}* has been placed successfully.\n\n"
        f"💰 *Total:* ₹{order.total_amount:.2f} ({order.payment_method.upper()})\n"
        f"⏳ *Status:* Waiting for canteen confirmation.\n\n"
        f"Track live: {_frontend_url()}/orders/{order.id}"
    )
    _send_whatsapp_safe(phone, wa_msg)


def handle_order_accepted(order):
    student = order.student
    to_email = student.email
    phone = student.mobile
    canteen = order.canteen

    subject = f"[CanteenX] Order Confirmed & Accepted! #{order.order_number} - PIN: {order.pickup_pin}"

    prep_str = f"~{order.estimated_prep_minutes} minutes" if order.estimated_prep_minutes else "10-15 minutes"
    ready_time_str = timezone.localtime(order.estimated_ready_at).strftime('%I:%M %p') if order.estimated_ready_at else "Shortly"

    items_list_text = "\n".join([
        f"  - {item.quantity}x {item.item_name} @ Rs. {item.item_price:.2f} = Rs. {item.subtotal:.2f}"
        for item in order.items.all()
    ])

    text_body = f"""Dear {student.full_name},

GREAT NEWS! {canteen.name} has ACCEPTED your order #{order.order_number}!

YOUR 4-DIGIT PICKUP PIN: {order.pickup_pin}
(Call out or show this PIN at the counter to claim your food)

ESTIMATED PREPARATION TIME: {prep_str}
ESTIMATED READY TIME: ~{ready_time_str}

ORDER SUMMARY:
- Order Number: #{order.order_number}
- Canteen: {canteen.name} ({canteen.location})
- Pickup PIN: {order.pickup_pin}
- Total Amount: Rs. {order.total_amount:.2f}

ITEMS:
{items_list_text}

View Live Pass: {_frontend_url()}/orders/{order.id}
"""

    html_content = f"""
    <div style="background-color: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 24px;">
      <span style="font-size: 11px; font-weight: 700; color: #047857; text-transform: uppercase; letter-spacing: 1px;">Counter Pickup PIN</span>
      <div style="font-size: 38px; font-weight: 900; font-family: monospace; color: #065f46; letter-spacing: 4px; margin: 8px 0;">
        {order.pickup_pin}
      </div>
      <p style="margin: 0; font-size: 12px; color: #047857;">Show this PIN at the counter to receive your food.</p>
    </div>

    <div style="background-color: #fff7ed; border: 1px solid #fed7aa; border-radius: 12px; padding: 14px 18px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <span style="font-size: 11px; font-weight: 700; color: #c2410c; text-transform: uppercase;">Estimated Preparation</span>
        <p style="margin: 2px 0 0 0; font-size: 14px; font-weight: 800; color: #9a3412;">{prep_str} (Ready around ~{ready_time_str})</p>
      </div>
    </div>

    <h2 style="margin: 0 0 8px 0; font-size: 18px; font-weight: 800; color: #0f172a;">Confirmed Order: #{order.order_number}</h2>
    {_generate_items_html(order)}

    <div style="margin-top: 24px; text-align: center;">
      <a href="{_frontend_url()}/orders/{order.id}" style="display: inline-block; background: #10b981; color: #ffffff; text-decoration: none; font-weight: 700; font-size: 13px; padding: 12px 24px; border-radius: 10px;">
        Open Digital Meal Pass
      </a>
    </div>
    """
    html_body = _get_base_html(subject, "Order Accepted", html_content, order)
    _send_email_safe(to_email, subject, text_body, html_body)

    # WhatsApp message
    wa_msg = (
        f"✅ *CanteenX: Order Accepted!*\n"
        f"Great news {student.full_name}! *{canteen.name}* has accepted order *#{order.order_number}*.\n\n"
        f"🔑 *Pickup PIN:* *{order.pickup_pin}*\n"
        f"⏱️ *Prep Time:* {prep_str} (Est: ~{ready_time_str})\n\n"
        f"View your digital pass: {_frontend_url()}/orders/{order.id}"
    )
    _send_whatsapp_safe(phone, wa_msg)


def handle_order_preparing(order):
    student = order.student
    to_email = student.email
    phone = student.mobile
    canteen = order.canteen

    subject = f"[CanteenX] 👨‍🍳 Kitchen Started Preparing Your Food! #{order.order_number}"

    text_body = f"""Hello {student.full_name},

Your order #{order.order_number} is now being freshly prepared at {canteen.name}!

Counter: {canteen.name} ({canteen.location})
Pickup PIN: {order.pickup_pin}

We'll notify you as soon as the counter marks it READY FOR PICKUP!

Digital Pass: {_frontend_url()}/orders/{order.id}
"""

    html_content = f"""
    <div style="background-color: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px; padding: 16px; margin-bottom: 24px; text-align: center;">
      <span style="font-size: 28px;">🍳</span>
      <h2 style="margin: 8px 0 4px 0; font-size: 18px; font-weight: 800; color: #1e40af;">Cooking in Progress!</h2>
      <p style="margin: 0; font-size: 13px; color: #1e3a8a;">
        The chefs at {canteen.name} are whipping up your meal right now. Keep your pickup PIN handy!
      </p>
    </div>

    <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; text-align: center; margin-bottom: 20px;">
      <span style="font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase;">Counter Pickup PIN</span>
      <div style="font-size: 32px; font-weight: 900; font-family: monospace; color: #0f172a; letter-spacing: 4px; margin: 4px 0;">
        {order.pickup_pin}
      </div>
    </div>
    """
    html_body = _get_base_html(subject, "Preparing Order", html_content, order)
    _send_email_safe(to_email, subject, text_body, html_body)

    wa_msg = (
        f"👨‍🍳 *CanteenX: Cooking Started!*\n"
        f"Hi {student.full_name}, your food for order *#{order.order_number}* is now being prepared at *{canteen.name}*.\n"
        f"🔑 *Pickup PIN:* *{order.pickup_pin}*"
    )
    _send_whatsapp_safe(phone, wa_msg)


def handle_order_ready(order):
    student = order.student
    to_email = student.email
    phone = student.mobile
    canteen = order.canteen

    subject = f"[CanteenX] 🔔 YOUR ORDER IS READY FOR PICKUP! #{order.order_number} - PIN: {order.pickup_pin}"

    text_body = f"""Hello {student.full_name},

Your order #{order.order_number} is now READY FOR PICKUP at {canteen.name}!

Counter: {canteen.name} ({canteen.location})
YOUR PICKUP PIN: {order.pickup_pin}

Please head over to the counter now to collect your freshly prepared food!

View Digital Pass: {_frontend_url()}/orders/{order.id}
"""

    html_content = f"""
    <div style="background-color: #faf5ff; border: 2px solid #c084fc; border-radius: 16px; padding: 24px; text-align: center; margin-bottom: 24px;">
      <span style="font-size: 36px;">🔔</span>
      <h2 style="margin: 8px 0 4px 0; font-size: 22px; font-weight: 900; color: #6b21a8;">Hot & Ready for Pickup!</h2>
      <p style="margin: 0; font-size: 14px; color: #7e22ce;">
        Please proceed to <strong>{canteen.name}</strong> counter immediately.
      </p>

      <div style="background-color: #ffffff; border: 1px dashed #c084fc; border-radius: 12px; padding: 16px; margin: 16px auto 0 auto; max-width: 260px;">
        <span style="font-size: 11px; font-weight: 700; color: #6b21a8; text-transform: uppercase;">Call out this PIN</span>
        <div style="font-size: 42px; font-weight: 900; font-family: monospace; color: #581c87; letter-spacing: 5px; margin: 4px 0;">
          {order.pickup_pin}
        </div>
      </div>
    </div>

    <div style="text-align: center;">
      <a href="{_frontend_url()}/orders/{order.id}" style="display: inline-block; background: #9333ea; color: #ffffff; text-decoration: none; font-weight: 700; font-size: 14px; padding: 14px 28px; border-radius: 12px;">
        Show Pass at Counter
      </a>
    </div>
    """
    html_body = _get_base_html(subject, "Ready for Pickup", html_content, order)
    _send_email_safe(to_email, subject, text_body, html_body)

    # WhatsApp message
    wa_msg = (
        f"🔔 *CanteenX: ORDER READY FOR PICKUP!*\n"
        f"Your meal is hot & packed at *{canteen.name}*!\n\n"
        f"🔑 *SHOW PICKUP PIN:* *{order.pickup_pin}*\n"
        f"📍 *Location:* {canteen.location}\n\n"
        f"Show digital pass: {_frontend_url()}/orders/{order.id}"
    )
    _send_whatsapp_safe(phone, wa_msg)


def handle_order_completed(order):
    student = order.student
    to_email = student.email
    phone = student.mobile
    canteen = order.canteen

    subject = f"[CanteenX] 🧾 Tax & Order Invoice - #{order.order_number} ({canteen.name})"

    items_list_text = "\n".join([
        f"  - {item.quantity}x {item.item_name} @ Rs. {item.item_price:.2f} = Rs. {item.subtotal:.2f}"
        for item in order.items.all()
    ])

    text_body = f"""Hello {student.full_name},

Thank you for picking up your order from {canteen.name}! Here is your final tax invoice receipt:

INVOICE SUMMARY:
- Invoice / Order Number: #{order.order_number}
- Date: {timezone.localtime(order.created_at).strftime('%d %b %Y, %I:%M %p')}
- Canteen: {canteen.name} ({canteen.location})
- Student Enrollment: {getattr(getattr(student, 'student_profile', None), 'enrollment_number', 'N/A')}
- Subtotal: Rs. {order.subtotal:.2f}
- University Food Tax Subsidy: Rs. 0.00 (0% subsidized)
- Total Paid: Rs. {order.total_amount:.2f}
- Payment Method: {order.payment_method.upper()} (PAID)

ITEMS:
{items_list_text}

Rate your dining experience: {_frontend_url()}/orders/{order.id}

We hope you enjoy your meal!
Medi-Caps University CanteenX
"""

    html_content = f"""
    <div style="border-bottom: 2px dashed #cbd5e1; padding-bottom: 16px; margin-bottom: 20px;">
      <div style="display: flex; justify-content: space-between; align-items: flex-start;">
        <div>
          <span style="font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase;">Final Invoice Receipt</span>
          <h2 style="margin: 2px 0 0 0; font-size: 20px; font-weight: 900; color: #0f172a;">#{order.order_number}</h2>
        </div>
        <div style="text-align: right;">
          <span style="font-size: 11px; font-weight: 800; background: #ecfdf5; color: #059669; padding: 4px 10px; border-radius: 9999px; border: 1px solid #a7f3d0;">
            FULFILLED & PAID
          </span>
          <p style="margin: 4px 0 0 0; font-size: 11px; color: #64748b;">
            {timezone.localtime(order.updated_at).strftime('%d %b %Y, %I:%M %p')}
          </p>
        </div>
      </div>
    </div>

    <!-- Student & Canteen Meta Table -->
    <table style="width: 100%; font-size: 12px; color: #475569; margin-bottom: 20px;">
      <tr>
        <td style="padding: 4px 0;"><strong>Billed To:</strong> {student.full_name} ({getattr(getattr(student, 'student_profile', None), 'enrollment_number', 'N/A')})</td>
        <td style="padding: 4px 0; text-align: right;"><strong>Canteen:</strong> {canteen.name}</td>
      </tr>
      <tr>
        <td style="padding: 4px 0;"><strong>Payment:</strong> {order.payment_method.upper()}</td>
        <td style="padding: 4px 0; text-align: right;"><strong>Campus Location:</strong> {canteen.location}</td>
      </tr>
    </table>

    {_generate_items_html(order)}

    <!-- Totals Breakdown -->
    <div style="margin-top: 16px; border-top: 2px solid #e2e8f0; padding-top: 12px;">
      <table style="width: 100%; font-size: 13px;">
        <tr>
          <td style="padding: 4px 0; color: #64748b;">Subtotal</td>
          <td style="padding: 4px 0; text-align: right; font-weight: 600; color: #0f172a;">Rs. {order.subtotal:.2f}</td>
        </tr>
        <tr>
          <td style="padding: 4px 0; color: #64748b;">Campus Tax Subsidy</td>
          <td style="padding: 4px 0; text-align: right; font-weight: 600; color: #16a34a;">Rs. 0.00 (0%)</td>
        </tr>
        <tr style="font-size: 16px; font-weight: 900; color: #0f172a; border-top: 1px solid #e2e8f0;">
          <td style="padding: 8px 0;">Total Paid</td>
          <td style="padding: 8px 0; text-align: right; color: #ea580c;">Rs. {order.total_amount:.2f}</td>
        </tr>
      </table>
    </div>

    <div style="margin-top: 28px; text-align: center;">
      <a href="{_frontend_url()}/orders/{order.id}" style="display: inline-block; background: #0f172a; color: #ffffff; text-decoration: none; font-weight: 700; font-size: 13px; padding: 12px 24px; border-radius: 10px;">
        Leave Food Rating & Review
      </a>
    </div>
    """
    html_body = _get_base_html(subject, "Final Tax Invoice", html_content, order)
    _send_email_safe(to_email, subject, text_body, html_body)

    # WhatsApp message
    wa_msg = (
        f"🧾 *CanteenX: Final Invoice - #{order.order_number}*\n"
        f"Thank you for dining at *{canteen.name}*, {student.full_name}!\n\n"
        f"💵 *Amount Paid:* ₹{order.total_amount:.2f} ({order.payment_method.upper()})\n"
        f"✅ *Status:* Handed over & fulfilled\n\n"
        f"Rate your meal & view full invoice: {_frontend_url()}/orders/{order.id}"
    )
    _send_whatsapp_safe(phone, wa_msg)


def handle_order_cancelled(order):
    student = order.student
    to_email = student.email
    phone = student.mobile
    canteen = order.canteen

    subject = f"[CanteenX] Order Update: #{order.order_number} Cancelled"
    reason = order.cancellation_reason or "Item unavailable or kitchen closed"

    text_body = f"""Hello {student.full_name},

We regret to inform you that order #{order.order_number} for {canteen.name} could not be fulfilled and has been cancelled.

Reason provided by canteen:
"{reason}"

If any online payment was deducted, it will be refunded automatically to your source account.

Explore other dishes on CanteenX: {_frontend_url()}/menu
"""

    html_content = f"""
    <div style="background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 24px;">
      <span style="font-size: 32px;">❌</span>
      <h2 style="margin: 8px 0 4px 0; font-size: 18px; font-weight: 800; color: #991b1b;">Order Cancelled</h2>
      <p style="margin: 0; font-size: 13px; color: #b91c1c;">
        Reason: <strong>"{reason}"</strong>
      </p>
    </div>

    <p style="font-size: 13px; color: #475569; text-align: center;">
      If online payment was deducted, a full refund will be initiated to your bank account.
    </p>

    <div style="margin-top: 24px; text-align: center;">
      <a href="{_frontend_url()}/menu" style="display: inline-block; background: #ea580c; color: #ffffff; text-decoration: none; font-weight: 700; font-size: 13px; padding: 12px 24px; border-radius: 10px;">
        Browse Other Canteens
      </a>
    </div>
    """
    html_body = _get_base_html(subject, "Order Cancelled", html_content, order)
    _send_email_safe(to_email, subject, text_body, html_body)

    wa_msg = (
        f"❌ *CanteenX: Order Cancelled*\n"
        f"Order *#{order.order_number}* was cancelled by *{canteen.name}*.\n"
        f"Reason: {reason}"
    )
    _send_whatsapp_safe(phone, wa_msg)


# ==============================================================================
# UNIFIED NON-BLOCKING DISPATCHER
# ==============================================================================

def dispatch_order_notifications(order, event_type, async_delivery=False):
    """
    Unified dispatcher. By default executes synchronously (fast and 100% reliable for tests
    and logging), or in a thread when async_delivery=True.
    Also creates the internal Notification database record.
    """
    # 1. Synchronously create internal database notification for user
    try:
        prep_info = f" Estimated prep time: ~{order.estimated_prep_minutes} mins." if order.estimated_prep_minutes else ""
        notification_templates = {
            'placed': (
                f"Order #{order.order_number} Placed!",
                f"Your order for {order.canteen.name} has been placed. Waiting for canteen confirmation.",
                'order_update'
            ),
            'accepted': (
                f"Order #{order.order_number} Confirmed!",
                f"Great news! {order.canteen.name} has ACCEPTED your order.{prep_info} Your 4-digit pickup PIN is {order.pickup_pin}.",
                'order_update'
            ),
            'preparing': (
                f"Order #{order.order_number} Preparing",
                f"Your food is now being freshly prepared at {order.canteen.name}.{prep_info}",
                'order_update'
            ),
            'ready': (
                f"Order #{order.order_number} Ready for Pickup!",
                f"Your order is READY FOR PICKUP at {order.canteen.name}! Show PIN: {order.pickup_pin} at the counter.",
                'order_update'
            ),
            'completed': (
                f"Order #{order.order_number} Fulfilled & Invoice Ready",
                f"Your order #{order.order_number} has been handed over. Enjoy your meal! Your final invoice receipt is available.",
                'order_update'
            ),
            'cancelled': (
                f"Order #{order.order_number} Cancelled",
                f"Your order was cancelled by {order.canteen.name}. Reason: {order.cancellation_reason or 'Item unavailable'}",
                'order_update'
            ),
        }

        if event_type in notification_templates:
            title, msg, n_type = notification_templates[event_type]
            Notification.objects.create(
                recipient=order.student,
                title=title,
                message=msg,
                notification_type=n_type,
                related_order=order,
            )
    except Exception as e:
        print(f"[Internal Notification Error] {e}")

    # 2. Multi-channel external dispatch (Email + WhatsApp)
    def _deliver():
        try:
            if event_type == 'placed':
                handle_order_placed(order)
            elif event_type == 'accepted':
                handle_order_accepted(order)
            elif event_type == 'preparing':
                handle_order_preparing(order)
            elif event_type == 'ready':
                handle_order_ready(order)
            elif event_type == 'completed':
                handle_order_completed(order)
            elif event_type == 'cancelled':
                handle_order_cancelled(order)
        except Exception as err:
            print(f"[Dispatcher Error] {err}")

    if async_delivery:
        thread = threading.Thread(target=_deliver, daemon=True)
        thread.start()
    else:
        _deliver()
