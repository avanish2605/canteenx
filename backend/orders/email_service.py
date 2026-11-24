import os
from datetime import datetime
from pathlib import Path
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone

LOGS_DIR = Path(settings.BASE_DIR) / 'logs'
LOGS_DIR.mkdir(exist_ok=True)
EMAIL_LOG_FILE = LOGS_DIR / 'sent_emails.log'

def _frontend_url():
    return getattr(settings, 'FRONTEND_URL', 'http://127.0.0.1:5173').rstrip('/')

def _log_email(to_email, subject, text_content):
    """Log all dispatched emails for developer review and audit trail"""
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


def send_order_placed_email(order):
    """
    Dispatched when a student places an order.
    Status is strictly 'placed' (Awaiting Canteen Acceptance).
    """
    student = order.student
    to_email = student.email
    subject = f"[CanteenX] Order Received #{order.order_number} - Waiting for {order.canteen.name} Acceptance"

    items_list_text = "\n".join([
        f"  - {item.quantity}x {item.item_name} @ Rs. {item.item_price:.2f} = Rs. {item.subtotal:.2f}"
        for item in order.items.all()
    ])

    text_body = f"""Dear {student.full_name},

Thank you for ordering on CanteenX - Medi-Caps University, Indore!

Your order has been SUBMITTED and is currently AWAITING ACCEPTANCE by {order.canteen.name}.
The canteen staff has received your order and is reviewing kitchen capacity.

----------------------------------------------------------------------
ORDER DETAILS
----------------------------------------------------------------------
Order Number : #{order.order_number}
Canteen      : {order.canteen.name} ({order.canteen.location})
Date & Time  : {order.created_at.strftime('%d %b %Y, %I:%M %p')}
Payment Mode : {order.get_payment_method_display()}
Current Status: PENDING CANTEEN ACCEPTANCE

ITEMS ORDERED:
{items_list_text}

Total Amount : Rs. {order.total_amount:.2f}
Special Notes: {order.special_instructions or 'None'}
----------------------------------------------------------------------

WHAT HAPPENS NEXT?
As soon as the canteen staff accepts your order, you will receive an official CONFIRMATION email with your active 4-digit Counter Pickup PIN.

Track Live Status in CanteenX: {_frontend_url()}/orders/{order.id}

Warm regards,
Medi-Caps University Food Services
AB Road, Pigdamber, Rau, Indore, Madhya Pradesh 453331
"""

    items_html_rows = "".join([
        f"""<tr>
            <td style="padding: 10px 12px; border-bottom: 1px solid #e5e7eb; color: #111827; font-weight: 600;">{item.item_name}</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #e5e7eb; text-align: center; color: #374151;">{item.quantity}</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #e5e7eb; text-align: right; color: #374151;">₹{item.item_price:.2f}</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #e5e7eb; text-align: right; font-weight: 700; color: #111827;">₹{item.subtotal:.2f}</td>
        </tr>"""
        for item in order.items.all()
    ])

    html_body = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f9fafb; margin: 0; padding: 24px; }}
  .card {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; border: 1px solid #e5e7eb; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }}
  .header {{ background: linear-gradient(135deg, #111827 0%, #1f2937 50%, #c2410c 100%); padding: 32px 24px; text-align: center; color: #ffffff; }}
  .badge {{ display: inline-block; background: #fef3c7; color: #92400e; font-size: 11px; font-weight: 800; padding: 4px 12px; border-radius: 9999px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }}
  .content {{ padding: 24px; color: #374151; }}
  .table {{ width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 13px; }}
  .table th {{ background: #f3f4f6; padding: 10px 12px; text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: #4b5563; }}
  .total-row td {{ padding: 14px 12px; font-size: 16px; font-weight: 900; color: #ea580c; border-top: 2px solid #ea580c; text-align: right; }}
  .status-box {{ background: #fffbeb; border: 1px solid #fde68a; border-radius: 12px; padding: 16px; margin: 20px 0; text-align: center; }}
  .footer {{ background: #f9fafb; padding: 20px 24px; text-align: center; font-size: 11px; color: #9ca3af; border-top: 1px solid #f3f4f6; }}
</style>
</head>
<body>
  <div class="card">
    <div class="header">
      <span class="badge">Medi-Caps University • CanteenX</span>
      <h1 style="margin: 8px 0 4px 0; font-size: 22px; font-weight: 900;">Order Received</h1>
      <p style="margin: 0; font-size: 13px; color: #fed7aa;">Order #{order.order_number}</p>
    </div>

    <div class="content">
      <p style="font-size: 15px; margin-top: 0;">Hello <strong>{student.full_name}</strong>,</p>
      
      <div class="status-box">
        <div style="font-size: 24px; margin-bottom: 4px;">⏳</div>
        <div style="font-weight: 800; font-size: 14px; color: #92400e; text-transform: uppercase;">Awaiting Canteen Acceptance</div>
        <p style="margin: 6px 0 0 0; font-size: 12px; color: #78350f;">
          Your order has been transmitted to <strong>{order.canteen.name}</strong>. Canteen staff is reviewing kitchen queue and will accept shortly.
        </p>
      </div>

      <div style="background: #f9fafb; border-radius: 10px; padding: 12px 16px; margin-bottom: 20px; font-size: 12px;">
        <div style="margin-bottom: 4px;"><strong>Canteen:</strong> {order.canteen.name} ({order.canteen.location})</div>
        <div style="margin-bottom: 4px;"><strong>Payment Method:</strong> {order.get_payment_method_display()}</div>
        <div><strong>Time:</strong> {order.created_at.strftime('%d %b %Y, %I:%M %p')}</div>
      </div>

      <h3 style="font-size: 14px; font-weight: 800; margin: 20px 0 8px 0; color: #111827;">Your Food Items</h3>
      <table class="table">
        <thead>
          <tr>
            <th>Item</th>
            <th style="text-align: center;">Qty</th>
            <th style="text-align: right;">Price</th>
            <th style="text-align: right;">Total</th>
          </tr>
        </thead>
        <tbody>
          {items_html_rows}
          <tr class="total-row">
            <td colspan="3" style="text-align: right;">Final Amount:</td>
            <td>₹{order.total_amount:.2f}</td>
          </tr>
        </tbody>
      </table>

      <div style="text-align: center; margin-top: 24px;">
        <a href="{_frontend_url()}/orders/{order.id}" style="display: inline-block; background: #ea580c; color: #ffffff; font-weight: 800; font-size: 13px; padding: 12px 28px; border-radius: 10px; text-decoration: none;">Track Order Online</a>
      </div>
    </div>

    <div class="footer">
      Medi-Caps University Canteen Management System • Indore, Madhya Pradesh<br>
      This is an automated notification. For support, visit the canteen counter.
    </div>
  </div>
</body>
</html>
"""

    _send_email_safe(to_email, subject, text_body, html_body)


def send_order_accepted_email(order):
    """
    Dispatched when the canteen owner ACCEPTS the order.
    The order is now officially CONFIRMED and food is being prepared.
    Includes the official 4-digit Pickup PIN!
    """
    student = order.student
    to_email = student.email
    subject = f"[CanteenX] Order Confirmed & Accepted! #{order.order_number} - {order.canteen.name}"

    items_list_text = "\n".join([
        f"  - {item.quantity}x {item.item_name} (Rs. {item.subtotal:.2f})"
        for item in order.items.all()
    ])

    text_body = f"""Dear {student.full_name},

GREAT NEWS! Your order #{order.order_number} has been ACCEPTED & CONFIRMED by {order.canteen.name}!

Your meal is now scheduled and preparing in the kitchen.

======================================================================
YOUR DIGITAL PICKUP PASS
======================================================================
Pickup Counter  : {order.canteen.name}
Location        : {order.canteen.location}
4-DIGIT PICKUP PIN : >>> {order.pickup_pin} <<<
Order Number    : #{order.order_number}
Total Amount    : Rs. {order.total_amount:.2f}
Payment Status  : {order.get_payment_method_display()}
======================================================================

ITEMS IN PREPARATION:
{items_list_text}

INSTRUCTIONS FOR PICKUP:
1. When your food is prepared, you will receive an in-app alert or notification.
2. Head to the {order.canteen.name} counter.
3. Call out or present your 4-digit PIN: {order.pickup_pin}.
4. Collect your freshly prepared meal!

Track live order status: {_frontend_url()}/orders/{order.id}

Bon Appetit!
Medi-Caps University Food Services
"""

    items_html_rows = "".join([
        f"""<tr>
            <td style="padding: 10px 12px; border-bottom: 1px solid #e5e7eb; color: #111827; font-weight: 600;">{item.item_name}</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #e5e7eb; text-align: center; color: #374151;">{item.quantity}</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #e5e7eb; text-align: right; color: #374151;">₹{item.item_price:.2f}</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #e5e7eb; text-align: right; font-weight: 700; color: #111827;">₹{item.subtotal:.2f}</td>
        </tr>"""
        for item in order.items.all()
    ])

    html_body = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f9fafb; margin: 0; padding: 24px; }}
  .card {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; border: 1px solid #e5e7eb; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }}
  .header {{ background: linear-gradient(135deg, #065f46 0%, #047857 50%, #059669 100%); padding: 32px 24px; text-align: center; color: #ffffff; }}
  .badge {{ display: inline-block; background: #d1fae5; color: #065f46; font-size: 11px; font-weight: 800; padding: 4px 12px; border-radius: 9999px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }}
  .content {{ padding: 24px; color: #374151; }}
  .pin-card {{ background: linear-gradient(135deg, #111827 0%, #1f2937 100%); border-radius: 14px; padding: 20px; text-align: center; color: #ffffff; margin: 20px 0; border: 1px solid #374151; }}
  .pin-number {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 38px; font-weight: 900; letter-spacing: 6px; color: #fde047; margin: 8px 0; }}
  .table {{ width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 13px; }}
  .table th {{ background: #f3f4f6; padding: 10px 12px; text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: #4b5563; }}
  .total-row td {{ padding: 14px 12px; font-size: 16px; font-weight: 900; color: #059669; border-top: 2px solid #059669; text-align: right; }}
  .footer {{ background: #f9fafb; padding: 20px 24px; text-align: center; font-size: 11px; color: #9ca3af; border-top: 1px solid #f3f4f6; }}
</style>
</head>
<body>
  <div class="card">
    <div class="header">
      <span class="badge">Official Confirmation • CanteenX</span>
      <h1 style="margin: 8px 0 4px 0; font-size: 22px; font-weight: 900;">Order Accepted & Confirmed!</h1>
      <p style="margin: 0; font-size: 13px; color: #a7f3d0;">Your food is being prepared at {order.canteen.name}</p>
    </div>

    <div class="content">
      <p style="font-size: 15px; margin-top: 0;">Hello <strong>{student.full_name}</strong>,</p>
      <p style="font-size: 13px; line-height: 1.5; color: #4b5563;">
        Great news! The canteen owner of <strong>{order.canteen.name}</strong> has confirmed and accepted your order #{order.order_number}.
      </p>

      <!-- Prominent Digital Meal Pass PIN Box -->
      <div class="pin-card">
        <span style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #9ca3af; font-weight: 700;">Counter Pickup PIN</span>
        <div class="pin-number">{order.pickup_pin}</div>
        <p style="margin: 0; font-size: 11px; color: #d1d5db;">Present this 4-digit PIN at {order.canteen.name} counter to collect your food.</p>
      </div>

      <h3 style="font-size: 14px; font-weight: 800; margin: 20px 0 8px 0; color: #111827;">Confirmed Order Items</h3>
      <table class="table">
        <thead>
          <tr>
            <th>Item</th>
            <th style="text-align: center;">Qty</th>
            <th style="text-align: right;">Price</th>
            <th style="text-align: right;">Total</th>
          </tr>
        </thead>
        <tbody>
          {items_html_rows}
          <tr class="total-row">
            <td colspan="3" style="text-align: right;">Total Paid / Payable:</td>
            <td>₹{order.total_amount:.2f}</td>
          </tr>
        </tbody>
      </table>

      <div style="text-align: center; margin-top: 24px;">
        <a href="{_frontend_url()}/orders/{order.id}" style="display: inline-block; background: #059669; color: #ffffff; font-weight: 800; font-size: 13px; padding: 12px 28px; border-radius: 10px; text-decoration: none;">View Digital Meal Pass</a>
      </div>
    </div>

    <div class="footer">
      Medi-Caps University Food Services • Indore, Madhya Pradesh<br>
      Campus Hotline: (0731) 4259500 • AB Road, Indore
    </div>
  </div>
</body>
</html>
"""

    _send_email_safe(to_email, subject, text_body, html_body)


def send_order_ready_email(order):
    """Dispatched when order is marked 'ready' for student pickup"""
    student = order.student
    to_email = student.email
    subject = f"[CanteenX] 🔔 YOUR ORDER IS READY FOR PICKUP! #{order.order_number}"

    text_body = f"""Hello {student.full_name},

Your order #{order.order_number} is now READY FOR PICKUP at {order.canteen.name}!

Counter: {order.canteen.name} ({order.canteen.location})
YOUR PICKUP PIN: {order.pickup_pin}

Please head over to the counter now to collect your freshly prepared food!

View Digital Pass: {_frontend_url()}/orders/{order.id}

Medi-Caps University CanteenX
"""
    _send_email_safe(to_email, subject, text_body, None)


def send_order_cancelled_email(order):
    """Dispatched when order is cancelled / rejected by canteen owner"""
    student = order.student
    to_email = student.email
    subject = f"[CanteenX] Order Update: #{order.order_number} Cancelled"

    text_body = f"""Hello {student.full_name},

We regret to inform you that order #{order.order_number} for {order.canteen.name} could not be fulfilled and has been cancelled.

Reason provided by canteen:
"{order.cancellation_reason or 'Item unavailable or kitchen closed'}"

If any online payment was deducted, it will be refunded automatically to your source account.

Explore other dishes on CanteenX: {_frontend_url()}/menu

Medi-Caps University CanteenX
"""
    _send_email_safe(to_email, subject, text_body, None)


def _send_email_safe(to_email, subject, text_body, html_body=None):
    """Safe sender with logging and graceful fallback"""
    _log_email(to_email, subject, text_body)

    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'canteenx@medicaps.ac.in')
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=from_email,
            to=[to_email]
        )
        if html_body:
            msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=True)
        print(f"[Email Dispatched] To: {to_email} | Subject: {subject}")
    except Exception as e:
        print(f"[Email Send Error] Failed to send to {to_email}: {e}")
