"""
Comprehensive End-to-End System & 'Cherry-on-the-Top' Feature Verifier
Using Python standard library (urllib, json) - no extra dependencies needed!
"""
import sys
import json
import urllib.request
import urllib.error

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
    print("CANTEENX - COMPREHENSIVE END-TO-END VERIFICATION")
    print("=" * 65)

    # 1. Health check / Category listing
    code, categories = request('GET', '/api/food/categories/')
    assert code == 200, f"Categories failed: {code} {categories}"
    log(f"Fetched {len(categories)} food categories publicly.")

    # 2. Student Login
    code, student_data = request('POST', '/api/auth/login/', {
        "email": "student@medicaps.ac.in",
        "password": "Student@123"
    })
    assert code == 200, f"Student login failed: {code} {student_data}"
    student_jwt = student_data['access']
    log(f"Student authenticated: {student_data['user']['full_name']} ({student_data['user']['email']})")

    # 3. Canteen Admin Login
    code, admin_data = request('POST', '/api/auth/login/', {
        "email": "canteen@medicaps.ac.in",
        "password": "Canteen@123"
    })
    assert code == 200, f"Admin login failed: {code} {admin_data}"
    admin_jwt = admin_data['access']
    log(f"Canteen Admin authenticated: {admin_data['user']['email']}")

    # 4. Super Admin Login
    code, super_data = request('POST', '/api/auth/login/', {
        "email": "admin@medicaps.ac.in",
        "password": "Admin@123"
    })
    assert code == 200, f"SuperAdmin login failed: {code} {super_data}"
    super_jwt = super_data['access']
    log("Super Admin authenticated successfully.")

    # 5. Fetch Food Items
    code, items_data = request('GET', '/api/food/items/')
    assert code == 200, f"Food items failed: {code} {items_data}"
    items = items_data.get('results', items_data) if isinstance(items_data, dict) else items_data
    assert len(items) > 0, "No food items found"
    item1 = items[0]
    log(f"Available dishes retrieved: {len(items)} items. Selected #{item1['id']}: {item1['name']} (Rs. {item1['price']})")

    # 6. Cart Flow: Empty, Add item
    request('DELETE', '/api/cart/clear/', token=student_jwt)
    code, cart_data = request('POST', '/api/cart/add/', {
        "food_item_id": item1['id'],
        "quantity": 2
    }, token=student_jwt)
    assert code in [200, 201], f"Cart add failed: {code} {cart_data}"
    log(f"Cart updated: {cart_data['item_count']} item(s), total: Rs. {cart_data['total']}")

    # 7. Place Order (Atomic Transaction)
    code, order = request('POST', '/api/orders/create/', {
        "payment_method": "cash",
        "special_instructions": "Make it piping hot for Medi-Caps lunch break!"
    }, token=student_jwt)
    assert code == 201, f"Order placement failed: {code} {order}"
    order_id = order['id']
    pickup_pin = order.get('pickup_pin')
    order_number = order.get('order_number')
    log(f"Order #{order_number} placed! Total: Rs. {order['total_amount']}, Digital Pickup PIN: {pickup_pin}")
    assert pickup_pin and len(pickup_pin) == 4, f"Invalid 4-digit PIN: {pickup_pin}"

    # 8. 'Cherry on the Top': Canteen Counter PIN Verification
    code, verified_order = request('POST', '/api/orders/admin/verify-pin/', {
        "pickup_pin": pickup_pin
    }, token=admin_jwt)
    assert code == 200, f"PIN verification failed: {code} {verified_order}"
    assert verified_order['id'] == order_id, "PIN verified wrong order"
    log(f"Kitchen Counter PIN Verified! Order #{verified_order['order_number']} for {verified_order['student_name']}")

    # 9. Kitchen KDS Workflow Transitions
    for next_status in ['accepted', 'preparing', 'ready', 'completed']:
        code, updated = request('PATCH', f'/api/orders/admin/orders/{order_id}/status/', {
            "status": next_status
        }, token=admin_jwt)
        assert code == 200, f"Failed transition to {next_status}: {code} {updated}"
        log(f"Kitchen status updated -> [{next_status.upper()}]")

    # 10. 'Cherry on the Top': Student Post-Order 5-Star Rating & Review
    code, rated_order = request('POST', f'/api/orders/{order_id}/rate/', {
        "rating": 5,
        "review": "Super delicious and fast pickup at Medi-Caps Central Canteen!"
    }, token=student_jwt)
    assert code == 200, f"Order rating failed: {code} {rated_order}"
    assert rated_order['rating'] == 5, f"Rating mismatch: {rated_order.get('rating')}"
    log(f"Order rated: {rated_order['rating']} stars! Review: \"{rated_order['review']}\"")

    # 11. Student Notifications Check
    code, notes_data = request('GET', '/api/notifications/', token=student_jwt)
    assert code == 200, f"Notifications failed: {code} {notes_data}"
    notes = notes_data.get('results', notes_data) if isinstance(notes_data, dict) else notes_data
    log(f"Student live notifications: {len(notes)} unread/read alerts received.")

    # 12. Admin Dashboard & Reports Analytics
    code, dash_data = request('GET', '/api/admin/dashboard/', token=admin_jwt)
    assert code == 200, f"Dashboard stats failed: {code} {dash_data}"
    log(f"Canteen Dashboard: {dash_data['today_orders_count']} orders today, Rs. {dash_data['revenue_today']} sales")

    # 13. Super Admin Overview
    code, stats = request('GET', '/api/admin/superadmin/stats/', token=super_jwt)
    assert code == 200, f"SuperAdmin stats failed: {code} {stats}"
    log(f"Super Admin Stats: {stats['total_students']} students, {stats['total_canteens']} canteens, Rs. {stats['total_revenue']} total campus revenue")

    print("=" * 65)
    print("ALL 13 SYSTEM & ENHANCEMENT VERIFICATIONS PASSED 100%!")
    print("=" * 65)

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        log(f"ERROR: {e}", ok=False)
        sys.exit(1)
