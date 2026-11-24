"""
Test Cafine Menu, Email Dispatching, and Canteen Owner Order Acceptance Control
"""
import sys
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

def request(method, path, body=None, token=None):
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode('utf-8') if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Content-Type', 'application/json')
    if token:
        req.add_header('Authorization', f'Bearer {token}')

    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8')
            return resp.status, json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        err_content = e.read().decode('utf-8')
        try:
            parsed = json.loads(err_content)
        except Exception:
            parsed = err_content
        return e.code, parsed

def log(msg, ok=True):
    icon = "[OK]" if ok else "[FAIL]"
    print(f"{icon} {msg}")

def run_tests():
    print("=" * 65)
    print("TEST: CAFINE MENU & OWNER ACCEPTANCE EMAIL WORKFLOW")
    print("=" * 65)

    # 1. Verify Cafine exists and has dishes
    code, canteens = request('GET', '/api/canteens/')
    assert code == 200, f"Failed to get canteens: {code}"
    canteens_list = canteens.get('results', canteens) if isinstance(canteens, dict) else canteens
    cafine = next((c for c in canteens_list if c['name'] == 'Cafine'), None)
    assert cafine is not None, f"Cafine canteen not found! Available: {[c['name'] for c in canteens_list]}"
    log(f"Found Canteen: '{cafine['name']}' (ID: {cafine['id']}) - {cafine['location']}")

    # 2. Verify dishes under Cafine
    code, items_data = request('GET', f"/api/food/items/?canteen={cafine['id']}&page_size=100")
    assert code == 200, f"Failed to get items: {code}"
    total_count = items_data.get('count', len(items_data)) if isinstance(items_data, dict) else len(items_data)
    cafine_items = items_data.get('results', items_data) if isinstance(items_data, dict) else items_data
    log(f"Cafine has {total_count} active dishes across all categories (loaded {len(cafine_items)} on page).")
    assert total_count >= 60, f"Expected at least 60 items, got {total_count}"

    # Sample check of specific items from user prompt:
    sample_names = ['Tea (Regular)', 'Classic Burger', 'Salad Sub', 'Cheesy Garlic Bread', 'Nutella Milkshake']
    for s_name in sample_names:
        code, search_res = request('GET', f"/api/food/items/?canteen={cafine['id']}&search={urllib.parse.quote(s_name)}")
        items = search_res.get('results', search_res) if isinstance(search_res, dict) else search_res
        assert len(items) > 0, f"Item '{s_name}' not found via search!"
        item = items[0]
        log(f"Verified menu item: '{item['name']}' @ Rs. {item['price']}")

    # 3. Authenticate Student
    code, student_data = request('POST', '/api/auth/login/', {
        "email": "student@medicaps.ac.in",
        "password": "Student@123"
    })
    assert code == 200, f"Student login failed: {code}"
    student_jwt = student_data['access']
    log(f"Student authenticated: {student_data['user']['full_name']}")

    # 4. Authenticate Cafine Owner / Admin
    code, cafine_admin_data = request('POST', '/api/auth/login/', {
        "email": "cafine@medicaps.ac.in",
        "password": "Cafine@123"
    })
    assert code == 200, f"Cafine Admin login failed: {code} {cafine_admin_data}"
    cafine_admin_jwt = cafine_admin_data['access']
    log(f"Cafine Owner authenticated: {cafine_admin_data['user']['email']}")

    # 5. Student places order from Cafine
    # Clear cart and add classic burger & tea
    request('DELETE', '/api/cart/clear/', token=student_jwt)
    code, b_res = request('GET', f"/api/food/items/?canteen={cafine['id']}&search=Classic+Burger")
    burger_item = b_res['results'][0]
    code, t_res = request('GET', f"/api/food/items/?canteen={cafine['id']}&search=Tea")
    tea_item = t_res['results'][0]

    request('POST', '/api/cart/add/', {"food_item_id": burger_item['id'], "quantity": 1}, token=student_jwt)
    request('POST', '/api/cart/add/', {"food_item_id": tea_item['id'], "quantity": 2}, token=student_jwt)

    code, order = request('POST', '/api/orders/create/', {
        "payment_method": "cash",
        "special_instructions": "Table near Engineering block lawn"
    }, token=student_jwt)
    assert code == 201, f"Order creation failed: {code} {order}"
    order_id = order['id']
    pickup_pin = order['pickup_pin']
    log(f"Order #{order['order_number']} placed! Initial Status: [{order['status'].upper()}] - PIN: {pickup_pin}")
    assert order['status'] == 'placed', f"Status must be 'placed' (pending owner acceptance), got '{order['status']}'"

    # 6. Verify Placed Email was dispatched
    log_file = Path("logs/sent_emails.log")
    assert log_file.exists(), "sent_emails.log file not found!"
    log_content = ""
    for _ in range(15):
        log_content = log_file.read_text(encoding='utf-8')
        if f"#{order['order_number']}" in log_content:
            break
        time.sleep(0.2)
    assert f"#{order['order_number']}" in log_content, "Order placed email not found in log!"
    assert "PENDING CANTEEN ACCEPTANCE" in log_content or "Waiting for Cafine Acceptance" in log_content, "Missing pending acceptance text in email!"
    log("Verified: Email 1 (Order Received - Pending Acceptance) successfully sent to student@medicaps.ac.in!")

    # 7. Cafine Owner views order in KDS and ACCEPTS IT
    code, admin_orders = request('GET', '/api/orders/admin/orders/?status=placed', token=cafine_admin_jwt)
    assert code == 200, f"Admin orders failed: {code}"
    admin_orders_list = admin_orders.get('results', admin_orders) if isinstance(admin_orders, dict) else admin_orders
    matched_admin_order = next((o for o in admin_orders_list if o['id'] == order_id), None)
    assert matched_admin_order is not None, "Order did not appear in Cafine owner's placed orders queue!"
    log(f"Cafine owner received order #{order['order_number']} in kitchen queue.")

    # Owner clicks 'Accept Order'
    code, accepted_order = request('PATCH', f"/api/orders/admin/orders/{order_id}/status/", {
        "status": "accepted"
    }, token=cafine_admin_jwt)
    assert code == 200, f"Order acceptance failed: {code} {accepted_order}"
    assert accepted_order['status'] == 'accepted', f"Order status is not accepted: {accepted_order['status']}"
    log(f"Cafine Owner clicked 'Accept Order' -> Status successfully transitioned to [{accepted_order['status'].upper()}]!")

    # 8. Verify Confirmation Email was dispatched with Pickup PIN
    for _ in range(15):
        log_content = log_file.read_text(encoding='utf-8')
        if f"Order Confirmed & Accepted! #{order['order_number']}" in log_content:
            break
        time.sleep(0.2)
    assert f"Order Confirmed & Accepted! #{order['order_number']}" in log_content, "Acceptance confirmation email not logged!"
    assert pickup_pin in log_content, f"4-digit PIN {pickup_pin} not in confirmation email body!"
    log(f"Verified: Email 2 (Order Confirmed & Accepted with PIN: {pickup_pin}) sent to student@medicaps.ac.in!")

    # 9. Verify Student can now see Accepted Status and Digital Token
    code, student_view = request('GET', f"/api/orders/{order_id}/", token=student_jwt)
    assert code == 200, f"Student get order failed: {code}"
    assert student_view['status'] == 'accepted', f"Expected accepted, got {student_view['status']}"
    log(f"Student live status updated: '{student_view['status_display']}' (PIN: {student_view['pickup_pin']})")

    # 10. Cafine transitions to 'ready' and counter completes pickup
    request('PATCH', f"/api/orders/admin/orders/{order_id}/status/", {"status": "ready"}, token=cafine_admin_jwt)
    log("Order marked READY in kitchen.")

    # Verify PIN at counter
    code, pin_result = request('POST', '/api/orders/admin/verify-pin/', {"pickup_pin": pickup_pin}, token=cafine_admin_jwt)
    assert code == 200, f"PIN verify failed: {code} {pin_result}"
    assert pin_result['id'] == order_id, "Verified wrong order"
    log(f"Counter staff verified student PIN {pickup_pin} for Order #{pin_result['order_number']}.")

    # Hand over & complete
    code, completed_order = request('PATCH', f"/api/orders/admin/orders/{order_id}/status/", {"status": "completed"}, token=cafine_admin_jwt)
    assert code == 200 and completed_order['status'] == 'completed', "Failed to complete order"
    log("Order fulfilled & completed!")

    print("=" * 65)
    print("ALL CAFINE, EMAIL & OWNER ACCEPTANCE CONTROLS VERIFIED 100%!")
    print("=" * 65)

if __name__ == '__main__':
    try:
        run_tests()
    except Exception as e:
        log(f"ERROR: {e}", ok=False)
        sys.exit(1)
