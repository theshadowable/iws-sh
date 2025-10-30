#!/usr/bin/env python3
"""
Focused test for the 6 critical bug fixes
"""

import requests
import json
import time

BACKEND_URL = "https://comprehensive-fix-1.preview.emergentagent.com/api"

def test_login(email, password):
    """Login and get token"""
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={"email": email, "password": password},
        timeout=10
    )
    if response.status_code == 200:
        data = response.json()
        return data["access_token"], data["user"]
    return None, None

def test_bug_fixes():
    """Test all 6 critical bug fixes"""
    print("🚀 TESTING 6 CRITICAL BUG FIXES")
    print("=" * 50)
    
    # Login as admin
    token, user = test_login("admin@indowater.com", "admin123")
    if not token:
        print("❌ Admin login failed")
        return
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    results = {}
    
    # Bug #1: Profile Update API
    print("\n1️⃣ Testing Profile Update API (Bug #1)...")
    response = requests.put(
        f"{BACKEND_URL}/auth/profile",
        json={"full_name": f"Test Admin {int(time.time())}"},
        headers=headers,
        timeout=15
    )
    results["profile_update"] = response.status_code == 200
    print(f"   Status: {response.status_code} - {'✅ FIXED' if results['profile_update'] else '❌ FAILED'}")
    
    # Bug #2: IoT Monitoring APIs
    print("\n2️⃣ Testing IoT Monitoring APIs (Bug #2)...")
    response = requests.get(f"{BACKEND_URL}/iot/health", headers=headers, timeout=15)
    results["iot_monitoring"] = response.status_code == 200
    print(f"   Status: {response.status_code} - {'✅ FIXED' if results['iot_monitoring'] else '❌ FAILED'}")
    
    # Bug #3: Support Ticket Creation
    print("\n3️⃣ Testing Support Ticket Creation (Bug #3)...")
    response = requests.post(
        f"{BACKEND_URL}/tickets/",
        json={
            "subject": f"Test Ticket {int(time.time())}",
            "description": "Test ticket for bug fix verification",
            "category": "technical_issue",
            "priority": "medium"
        },
        headers=headers,
        timeout=15
    )
    if response.status_code in [200, 201]:
        ticket_data = response.json()
        has_ticket_number = "ticket_number" in ticket_data
        has_customer_info = "customer_name" in ticket_data and "customer_email" in ticket_data
        results["support_tickets"] = has_ticket_number and has_customer_info
        print(f"   Status: {response.status_code} - {'✅ FIXED' if results['support_tickets'] else '❌ FAILED'}")
        if not results["support_tickets"]:
            print(f"   Missing: ticket_number={has_ticket_number}, customer_info={has_customer_info}")
    else:
        results["support_tickets"] = False
        print(f"   Status: {response.status_code} - ❌ FAILED")
        try:
            error = response.json()
            print(f"   Error: {error.get('detail', 'Unknown error')}")
        except:
            pass
    
    # Bug #4: Voucher Management
    print("\n4️⃣ Testing Voucher Management (Bug #4)...")
    response = requests.get(f"{BACKEND_URL}/vouchers/", headers=headers, timeout=15)
    results["voucher_management"] = response.status_code == 200
    print(f"   Status: {response.status_code} - {'✅ FIXED' if results['voucher_management'] else '❌ FAILED'}")
    if not results["voucher_management"]:
        try:
            error = response.json()
            print(f"   Error: {error.get('detail', 'Unknown error')}")
        except:
            pass
    
    # Bug #5: Report Generation
    print("\n5️⃣ Testing Report Generation (Bug #5)...")
    report_data = {
        "start_date": "2025-01-01",
        "end_date": "2025-01-30",
        "report_type": "usage_summary",
        "include_charts": True
    }
    
    # Test PDF
    response = requests.post(f"{BACKEND_URL}/reports/export-pdf/", json=report_data, headers=headers, timeout=30)
    pdf_success = response.status_code == 200 and 'application/pdf' in response.headers.get('content-type', '')
    
    # Test Excel
    response = requests.post(f"{BACKEND_URL}/reports/export-excel/", json=report_data, headers=headers, timeout=30)
    excel_success = response.status_code == 200 and 'spreadsheet' in response.headers.get('content-type', '')
    
    results["report_generation"] = pdf_success or excel_success
    print(f"   PDF: {'✅' if pdf_success else '❌'} Excel: {'✅' if excel_success else '❌'} - {'✅ FIXED' if results['report_generation'] else '❌ FAILED'}")
    
    # Bug #6: Device Management Comprehensive
    print("\n6️⃣ Testing Device Comprehensive (Bug #6)...")
    response = requests.get(f"{BACKEND_URL}/devices/comprehensive/", headers=headers, timeout=15)
    results["device_comprehensive"] = response.status_code == 200
    print(f"   Status: {response.status_code} - {'✅ FIXED' if results['device_comprehensive'] else '❌ FAILED'}")
    if results["device_comprehensive"]:
        try:
            data = response.json()
            print(f"   Found {len(data)} devices with comprehensive data")
        except:
            pass
    
    # Summary
    print(f"\n{'=' * 50}")
    print("📊 BUG FIX SUMMARY")
    print(f"{'=' * 50}")
    
    fixed_count = sum(results.values())
    total_count = len(results)
    
    for i, (bug_name, status) in enumerate(results.items(), 1):
        status_icon = "✅ FIXED" if status else "❌ FAILED"
        print(f"Bug #{i} ({bug_name}): {status_icon}")
    
    print(f"\nOverall: {fixed_count}/{total_count} bugs fixed ({fixed_count/total_count*100:.1f}%)")
    
    if fixed_count == total_count:
        print("🎉 ALL BUGS FIXED!")
    elif fixed_count >= 4:
        print("✅ Most bugs fixed, minor issues remain")
    else:
        print("⚠️ Multiple critical issues need attention")

if __name__ == "__main__":
    test_bug_fixes()