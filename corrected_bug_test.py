#!/usr/bin/env python3
"""
Corrected Backend API Bug Testing Script
Tests the ACTUAL endpoints that are registered
"""

import requests
import json
import time

# Backend URL
BACKEND_URL = "https://comprehensive-fix-1.preview.emergentagent.com/api"

# Demo accounts
DEMO_ACCOUNTS = [
    {"name": "Admin", "email": "admin@indowater.com", "password": "admin123", "expected_role": "admin"},
    {"name": "Technician", "email": "technician@indowater.com", "password": "tech123", "expected_role": "technician"},
    {"name": "Customer", "email": "customer@indowater.com", "password": "customer123", "expected_role": "customer"}
]

def test_login(email: str, password: str) -> str:
    """Test login and return token"""
    login_data = {"email": email, "password": password}
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_corrected_endpoints():
    """Test the actual registered endpoints"""
    print("🔍 TESTING CORRECTED ENDPOINTS")
    print("=" * 60)
    
    # Login as admin
    token = test_login("admin@indowater.com", "admin123")
    if not token:
        print("❌ Login failed")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    results = {}
    
    # Test 1: Profile Update (previously reported as fixed)
    print("\n👤 Testing Profile Update API...")
    update_data = {"full_name": "Updated Admin User", "phone": "+6281234567890"}
    response = requests.put(f"{BACKEND_URL}/auth/profile", json=update_data, headers=headers)
    print(f"   PUT /api/auth/profile: {response.status_code}")
    results["profile_update"] = response.status_code == 200
    
    # Test 2: IoT Monitoring APIs (using correct endpoints)
    print("\n🌐 Testing IoT Monitoring APIs...")
    
    # IoT Register
    device_data = {
        "device_id": f"ESP32-TEST-{int(time.time())}",
        "device_type": "smart_meter",
        "firmware_version": "1.0.0",
        "hardware_version": "1.0"
    }
    response = requests.post(f"{BACKEND_URL}/iot/register", json=device_data, headers={"x-device-secret": "test-secret"})
    print(f"   POST /api/iot/register: {response.status_code}")
    results["iot_register"] = response.status_code in [200, 201]
    
    # IoT Reading
    reading_data = {
        "device_id": "test-device-1",
        "flow_rate": 15.5,
        "volume_consumed": 100.0,
        "total_volume": 1000.0,
        "balance": 50000.0
    }
    response = requests.post(f"{BACKEND_URL}/iot/reading", json=reading_data, headers={"x-device-secret": "test-secret"})
    print(f"   POST /api/iot/reading: {response.status_code}")
    results["iot_reading"] = response.status_code in [200, 201]
    
    # IoT Health
    response = requests.get(f"{BACKEND_URL}/iot/health")
    print(f"   GET /api/iot/health: {response.status_code}")
    results["iot_health"] = response.status_code == 200
    
    # Test 3: Support Ticket APIs
    print("\n🎫 Testing Support Ticket APIs...")
    
    # List tickets
    response = requests.get(f"{BACKEND_URL}/tickets/", headers=headers)
    print(f"   GET /api/tickets/: {response.status_code}")
    results["tickets_list"] = response.status_code == 200
    
    # Create ticket (this was the reported bug)
    ticket_data = {
        "subject": f"Test Ticket {int(time.time())}",
        "description": "This is a test ticket",
        "category": "technical_issue",
        "priority": "medium"
    }
    response = requests.post(f"{BACKEND_URL}/tickets/", json=ticket_data, headers=headers)
    print(f"   POST /api/tickets/: {response.status_code}")
    if response.status_code != 201:
        try:
            error_detail = response.json().get("detail", "Unknown error")
            print(f"      Error: {error_detail}")
        except:
            print(f"      Error: {response.text}")
    results["tickets_create"] = response.status_code == 201
    
    # Admin stats
    response = requests.get(f"{BACKEND_URL}/tickets/admin/stats", headers=headers)
    print(f"   GET /api/tickets/admin/stats: {response.status_code}")
    results["tickets_admin_stats"] = response.status_code == 200
    
    # Test 4: Voucher APIs
    print("\n🎟️ Testing Voucher APIs...")
    
    # List vouchers
    response = requests.get(f"{BACKEND_URL}/vouchers/", headers=headers)
    print(f"   GET /api/vouchers/: {response.status_code}")
    results["vouchers_list"] = response.status_code == 200
    
    # Create voucher
    voucher_data = {
        "code": f"TEST{int(time.time())}",
        "description": "Test voucher",
        "discount_type": "percentage",
        "discount_value": 15.0,
        "min_purchase_amount": 50000,
        "max_discount_amount": 100000,
        "usage_limit": 100,
        "per_customer_limit": 1,
        "valid_from": "2025-01-27T00:00:00Z",
        "valid_until": "2025-12-31T23:59:59Z",
        "is_active": True
    }
    response = requests.post(f"{BACKEND_URL}/vouchers/", json=voucher_data, headers=headers)
    print(f"   POST /api/vouchers/: {response.status_code}")
    results["vouchers_create"] = response.status_code == 201
    
    # Validate voucher
    validate_data = {"voucher_code": "WELCOME50", "purchase_amount": 100000}
    response = requests.post(f"{BACKEND_URL}/vouchers/validate", json=validate_data, headers=headers)
    print(f"   POST /api/vouchers/validate: {response.status_code}")
    results["vouchers_validate"] = response.status_code == 200
    
    # Active vouchers
    response = requests.get(f"{BACKEND_URL}/vouchers/active", headers=headers)
    print(f"   GET /api/vouchers/active: {response.status_code}")
    results["vouchers_active"] = response.status_code == 200
    
    # Test 5: Report Generation APIs
    print("\n📄 Testing Report Generation APIs...")
    
    report_data = {
        "start_date": "2025-01-01",
        "end_date": "2025-01-31",
        "report_type": "usage_summary",
        "include_charts": True
    }
    
    # PDF Report
    response = requests.post(f"{BACKEND_URL}/reports/export-pdf", json=report_data, headers=headers)
    print(f"   POST /api/reports/export-pdf: {response.status_code}")
    results["reports_pdf"] = response.status_code == 200
    
    # Excel Report
    response = requests.post(f"{BACKEND_URL}/reports/export-excel", json=report_data, headers=headers)
    print(f"   POST /api/reports/export-excel: {response.status_code}")
    results["reports_excel"] = response.status_code == 200
    
    # Test 6: Device Management APIs
    print("\n📱 Testing Device Management APIs...")
    
    # List devices
    response = requests.get(f"{BACKEND_URL}/devices", headers=headers)
    print(f"   GET /api/devices: {response.status_code}")
    results["devices_list"] = response.status_code == 200
    
    # Comprehensive devices
    response = requests.get(f"{BACKEND_URL}/devices/comprehensive", headers=headers)
    print(f"   GET /api/devices/comprehensive: {response.status_code}")
    results["devices_comprehensive"] = response.status_code == 200
    
    # Device stats (if we have devices)
    response = requests.get(f"{BACKEND_URL}/devices/test-device-1/stats", headers=headers)
    print(f"   GET /api/devices/test-device-1/stats: {response.status_code}")
    results["devices_stats"] = response.status_code == 200
    
    # Batch operations
    batch_data = {"device_ids": ["test-device-1"], "operation": "activate", "parameters": {}}
    response = requests.post(f"{BACKEND_URL}/devices/batch", json=batch_data, headers=headers)
    print(f"   POST /api/devices/batch: {response.status_code}")
    results["devices_batch"] = response.status_code == 200
    
    # Summary
    print(f"\n{'='*60}")
    print("🎯 CORRECTED TEST RESULTS SUMMARY")
    print(f"{'='*60}")
    
    working_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    print(f"✅ Working endpoints: {working_count}/{total_count}")
    print(f"❌ Failing endpoints: {total_count - working_count}/{total_count}")
    
    print("\nDetailed Results:")
    for test_name, is_working in results.items():
        status = "✅" if is_working else "❌"
        print(f"   {status} {test_name}")
    
    # Identify critical bugs
    critical_bugs = []
    if not results.get("tickets_create", True):
        critical_bugs.append("Support Ticket Creation - Customer not found bug")
    if not results.get("vouchers_list", True):
        critical_bugs.append("Voucher List API - 404 error")
    if not results.get("reports_pdf", True):
        critical_bugs.append("PDF Report Generation - 404 error")
    if not results.get("reports_excel", True):
        critical_bugs.append("Excel Report Generation - 404 error")
    if not results.get("devices_comprehensive", True):
        critical_bugs.append("Device Comprehensive API - 404 error")
    
    if critical_bugs:
        print(f"\n🔴 CRITICAL BUGS FOUND ({len(critical_bugs)}):")
        for i, bug in enumerate(critical_bugs, 1):
            print(f"   {i}. {bug}")
    else:
        print(f"\n🎉 NO CRITICAL BUGS FOUND!")
    
    return results

if __name__ == "__main__":
    test_corrected_endpoints()