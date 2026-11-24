import json
import urllib.request
import urllib.error

BASE_URL = 'http://127.0.0.1:8000'

def request(endpoint, method='GET', data=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f"Bearer {token}"
    body = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            return response.status, json.loads(res_body) if res_body else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        return e.code, json.loads(err_body) if err_body else {'error': str(e)}

def run_tests():
    print("=== STARTING CANTEENX END-TO-END VERIFICATION ===")

    # 1. Student Login
    status, res = request('/api/auth/login/', 'POST', {
        'email': 'student@medicaps.ac.in',
        'password': 'Student@123'
    })
    assert status == 200, f"Student login failed: {res}"
    student_token = res['access']
    print(f"✓ Student Login Success: {res['user']['full_name']} (Role: {res['user']['role']})")

    # 2. Canteen Admin Login
    status, res = request('/api/auth/login/', 'POST', {
        'email': 'canteen@medicaps.ac.in',
        'password': 'Canteen@123'
    })
    assert status == 200, f"Canteen Admin login failed: {res}"
    admin_token = res['access']
    print(f"✓ Canteen Admin Login Success: {res['user']['full_name']} (Role: {res['user']['role']})")

    # 3. Super Admin Login
    status, res = request('/api/auth/login/', 'POST', {
        'email': 'admin@medicaps.ac.in',
        'password': 'Admin@123'
    })
    assert status == 200, f"Super Admin login failed: {res}"
    superadmin_token = res['access']
    print(f"✓ Super Admin Login Success: {res['user']['full_name']} (Role: {res['user']['role']})")

    # 4. Fetch Canteens
    status, res = request('/api/canteens/')
    assert status == 200 and len(res['results']) > 0, "Fetch canteens failed"
    canteen_id = res['results'][0]['id']
    print(f"✓ Canteens Verified ({len(res['results'])} available)")

    # 5. Fetch Menu Items
    status, res = request('/api/food/items/')
    assert status == 200 and len(res['results']) > 0, "Fetch food items failed"
    food_item = res['results'][0]
    print(f"✓ Menu Verified ({len(res['results'])} items found, sample: '{food_item['name']}' at ₹{food_item['price']})")

    # 6. Add to Cart
    status, res = request('/api/cart/add/', 'POST', {
        'food_item_id': food_item['id'],
        'quantity': 2
    }, token=student_token)
    assert status == 200, f"Add to cart failed: {res}"
    print(f"✓ Cart Add Success: {res['item_count']} item(s), Total: ₹{res['total']}")

    # 7. View Cart
    status, res = request('/api/cart/', token=student_token)
    assert status == 200 and len(res['items']) > 0, "Get cart failed"
    cart_item_id = res['items'][0]['id']
    print(f"✓ Cart Retrieval Success: {res['items'][0]['food_item_detail']['name']} x {res['items'][0]['quantity']}")

    # 8. Place Order
    status, res = request('/api/orders/create/', 'POST', {
        'payment_method': 'cash',
        'special_instructions': 'Extra spicy please, Medi-Caps student order'
    }, token=student_token)
    assert status == 201, f"Order placement failed: {res}"
    order_id = res['id']
    order_number = res['order_number']
    print(f"✓ Order Placed Success: #{order_number} (Total: ₹{res['total_amount']})")

    # 9. Student View Order Timeline
    status, res = request(f'/api/orders/{order_id}/', token=student_token)
    assert status == 200 and res['status'] == 'placed', "Order detail failed"
    print(f"✓ Student Order Detail Verified (Status: {res['status']})")

    # 10. Admin Advance Order Status: placed -> accepted -> preparing -> ready -> completed
    for next_status in ['accepted', 'preparing', 'ready', 'completed']:
        status, res = request(f'/api/orders/admin/orders/{order_id}/status/', 'PATCH', {
            'status': next_status
        }, token=admin_token)
        assert status == 200 and res['status'] == next_status, f"Status update to {next_status} failed"
        print(f"  → Kitchen updated #{order_number} to: {next_status.upper()}")
    print("✓ Full Order Lifecycle Processing Verified!")

    # 11. Student Notifications Check
    status, res = request('/api/notifications/', token=student_token)
    assert status == 200, "Fetch notifications failed"
    notifications = res['results'] if 'results' in res else res
    print(f"✓ Student Notifications Verified ({len(notifications)} notifications received for order updates)")

    # 12. Admin Dashboard & Analytics Check
    status, res = request('/api/admin/dashboard/', token=admin_token)
    assert status == 200 and 'revenue_today' in res, "Admin dashboard failed"
    print(f"✓ Canteen Admin Dashboard Verified (Today's Revenue: ₹{res['revenue_today']}, Completed: {res['completed_today']})")

    # 13. Super Admin Stats Check
    status, res = request('/api/admin/superadmin/stats/', token=superadmin_token)
    assert status == 200 and 'total_revenue' in res, "Super admin stats failed"
    print(f"✓ Super Admin Console Verified (Total Students: {res['total_students']}, Global Revenue: ₹{res['total_revenue']})")

    print("\n🎉 ALL 13 END-TO-END VERIFICATION CHECKS PASSED PERFECTLY! 🎉")

if __name__ == '__main__':
    run_tests()
