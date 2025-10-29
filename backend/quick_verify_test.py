#!/usr/bin/env python3
"""Quick verification test for bug fixes"""
import requests
import json

BACKEND_URL = "https://bug-sweep.preview.emergentagent.com/api"
ADMIN_CREDS = {"email": "admin@indowater.com", "password": "admin123"}

def test_quick_verification():
    print("🔍 Quick Bug Fix Verification Test\n")
    
    # Login
    print("1. Testing Login...")
    response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDS)
    if response.status_code == 200:
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("   ✅ Login successful\n")
    else:
        print("   ❌ Login failed")
        return
    
    tests_passed = 0
    tests_failed = 0
    
    # Test critical endpoints that were failing
    critical_tests = [
        ("GET", "/roles/list", "Role & Permission List"),
        ("GET", "/roles/permissions", "Permissions List"),
        ("GET", "/vouchers/", "Vouchers List"),
        ("GET", "/tickets/", "Support Tickets List"),
        ("GET", "/tips/", "Water Tips List"),
        ("GET", "/iot/devices/list", "IoT Devices List"),
        ("GET", "/devices", "Devices List"),
        ("GET", "/customers", "Customers List"),
        ("GET", "/properties", "Properties List"),
        ("GET", "/analytics/usage", "Analytics Usage"),
        ("GET", "/dashboard/stats", "Dashboard Stats"),
        ("GET", "/payments/history/list", "Payment History"),
        ("GET", "/alerts", "Alerts List"),
    ]
    
    print("2. Testing Critical Endpoints:\n")
    
    for method, endpoint, name in critical_tests:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=10)
            if response.status_code in [200, 201]:
                tests_passed += 1
                try:
                    data = response.json()
                    if isinstance(data, list):
                        count = len(data)
                    elif isinstance(data, dict):
                        count = len(data.get('items', data.get('data', data.get('tickets', data.get('tips', data.get('devices', []))))))
                    else:
                        count = "N/A"
                    print(f"   ✅ {name}: Status {response.status_code}, Count: {count}")
                except:
                    print(f"   ✅ {name}: Status {response.status_code}")
            else:
                tests_failed += 1
                print(f"   ❌ {name}: Status {response.status_code}")
        except Exception as e:
            tests_failed += 1
            print(f"   ❌ {name}: Error - {e}")
    
    print(f"\n📊 Results:")
    print(f"   Total: {tests_passed + tests_failed}")
    print(f"   Passed: {tests_passed} ✅")
    print(f"   Failed: {tests_failed} ❌")
    print(f"   Success Rate: {(tests_passed / (tests_passed + tests_failed) * 100):.1f}%")

if __name__ == "__main__":
    test_quick_verification()
