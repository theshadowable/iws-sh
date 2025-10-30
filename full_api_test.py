#!/usr/bin/env python3
"""
FULL INDOWATER API TESTING SCRIPT
Tests all endpoints mentioned in the comprehensive review request
"""

import requests
import json
import time
from datetime import datetime, timedelta

BACKEND_URL = "https://comprehensive-fix-1.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDS = {"email": "admin@indowater.com", "password": "admin123"}
TECH_CREDS = {"email": "technician@indowater.com", "password": "tech123"}
CUSTOMER_CREDS = {"email": "customer@indowater.com", "password": "customer123"}

def login(credentials):
    """Login and get token"""
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json=credentials, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token"), data.get("user")
        else:
            print(f"❌ Login failed: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None, None

def test_endpoint(method, url, headers=None, json_data=None, description=""):
    """Test a single endpoint"""
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=15)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=json_data, timeout=15)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=json_data, timeout=15)
        elif method.upper() == "PATCH":
            response = requests.patch(url, headers=headers, json=json_data, timeout=15)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=15)
        else:
            return False, f"Unsupported method: {method}"
        
        if response.status_code in [200, 201]:
            try:
                data = response.json()
                if isinstance(data, dict):
                    count = len(data.get('items', data.get('data', data.get('transactions', data.get('tickets', data.get('tips', []))))))
                elif isinstance(data, list):
                    count = len(data)
                else:
                    count = "N/A"
                return True, f"Success - Status: {response.status_code}, Data count: {count}"
            except:
                return True, f"Success - Status: {response.status_code}, Content-Type: {response.headers.get('content-type', 'unknown')}"
        else:
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', str(error_data))
            except:
                error_msg = response.text or f"HTTP {response.status_code}"
            return False, f"Failed - Status: {response.status_code}, Error: {error_msg}"
    
    except Exception as e:
        return False, f"Exception: {str(e)}"

def run_comprehensive_tests():
    """Run comprehensive API tests"""
    print("🚀 STARTING FULL INDOWATER API TESTING")
    print("="*80)
    
    # Login with all accounts
    admin_token, admin_user = login(ADMIN_CREDS)
    tech_token, tech_user = login(TECH_CREDS)
    customer_token, customer_user = login(CUSTOMER_CREDS)
    
    if not admin_token:
        print("❌ Admin login failed, cannot continue")
        return
    
    admin_headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    tech_headers = {"Authorization": f"Bearer {tech_token}", "Content-Type": "application/json"} if tech_token else None
    customer_headers = {"Authorization": f"Bearer {customer_token}", "Content-Type": "application/json"} if customer_token else None
    
    # Test results
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "details": []
    }
    
    def test_and_log(method, endpoint, headers, json_data=None, description="", role=""):
        results["total"] += 1
        success, message = test_endpoint(method, f"{BACKEND_URL}{endpoint}", headers, json_data, description)
        
        if success:
            results["passed"] += 1
            status = "✅"
        else:
            results["failed"] += 1
            status = "❌"
        
        result_line = f"{status} {method} {endpoint} ({role}) - {message}"
        print(result_line)
        results["details"].append(result_line)
        
        return success, message
    
    print("\n1. AUTHENTICATION & USERS (HIGH PRIORITY)")
    print("-" * 50)
    
    # Already tested login above
    test_and_log("GET", "/users", admin_headers, description="List users", role="Admin")
    
    # Create user test
    user_data = {
        "email": f"test_{int(time.time())}@indowater.com",
        "password": "testpass123",
        "full_name": "Test User API",
        "role": "customer",
        "phone": "+6281234567890"
    }
    success, msg = test_and_log("POST", "/users", admin_headers, user_data, "Create user", "Admin")
    
    if success and "test_" in str(msg):
        # Extract user ID if possible and test other operations
        test_and_log("GET", "/users/test-user-id", admin_headers, description="Get user detail", role="Admin")
        test_and_log("PUT", "/users/test-user-id", admin_headers, {"full_name": "Updated Test User"}, "Update user", "Admin")
        test_and_log("DELETE", "/users/test-user-id", admin_headers, description="Delete user", role="Admin")
    
    print("\n2. DASHBOARD APIs (HIGH PRIORITY)")
    print("-" * 50)
    test_and_log("GET", "/dashboard/stats", admin_headers, description="Dashboard stats", role="Admin")
    test_and_log("GET", "/dashboard/recent-activity", admin_headers, description="Recent activity", role="Admin")
    
    print("\n3. CUSTOMER MANAGEMENT (HIGH PRIORITY)")
    print("-" * 50)
    test_and_log("GET", "/customers", admin_headers, description="List customers", role="Admin")
    test_and_log("GET", "/customers", tech_headers, description="List customers", role="Technician")
    
    customer_data = {
        "customer_number": f"CUST{int(time.time())}",
        "full_name": "Test Customer API",
        "email": f"test_customer_{int(time.time())}@indowater.com",
        "phone": "+6281234567890",
        "address": "Test Address API",
        "balance": 100000
    }
    test_and_log("POST", "/customers", admin_headers, customer_data, "Create customer", "Admin")
    test_and_log("GET", "/customers/test-customer-id", admin_headers, description="Customer detail", role="Admin")
    test_and_log("PUT", "/customers/test-customer-id", admin_headers, {"full_name": "Updated Customer"}, "Update customer", "Admin")
    test_and_log("DELETE", "/customers/test-customer-id", admin_headers, description="Delete customer", role="Admin")
    test_and_log("GET", "/customers/test-customer-id/devices", admin_headers, description="Customer devices", role="Admin")
    test_and_log("GET", "/customers/test-customer-id/usage", admin_headers, description="Customer usage", role="Admin")
    test_and_log("GET", "/customers/test-customer-id/payments", admin_headers, description="Customer payments", role="Admin")
    
    print("\n4. DEVICE MANAGEMENT (HIGH PRIORITY)")
    print("-" * 50)
    test_and_log("GET", "/devices", admin_headers, description="List devices", role="Admin")
    
    device_data = {
        "device_id": f"DEV{int(time.time())}",
        "device_name": "Test Device API",
        "device_type": "water_meter",
        "customer_id": "test-customer-id",
        "property_id": "test-property-id",
        "installation_date": datetime.utcnow().isoformat(),
        "status": "active"
    }
    test_and_log("POST", "/devices", admin_headers, device_data, "Create device", "Admin")
    test_and_log("GET", "/devices/test-device-id", admin_headers, description="Device detail", role="Admin")
    test_and_log("PUT", "/devices/test-device-id", admin_headers, {"status": "maintenance"}, "Update device", "Admin")
    test_and_log("DELETE", "/devices/test-device-id", admin_headers, description="Delete device", role="Admin")
    test_and_log("GET", "/devices/comprehensive", admin_headers, description="Comprehensive devices", role="Admin")
    test_and_log("GET", "/devices/test-device-id/stats", admin_headers, description="Device statistics", role="Admin")
    test_and_log("GET", "/devices/test-device-id/activities", admin_headers, description="Device activities", role="Admin")
    
    batch_data = {"device_ids": ["dev1", "dev2"], "operation": "activate", "parameters": {}}
    test_and_log("POST", "/devices/batch", admin_headers, batch_data, "Batch operations", "Admin")
    
    print("\n5. IOT MONITORING (HIGH PRIORITY)")
    print("-" * 50)
    test_and_log("GET", "/iot/devices", admin_headers, description="List IoT devices", role="Admin")
    
    iot_device_data = {
        "device_id": f"ESP32-{int(time.time())}",
        "device_name": "Test IoT Device",
        "device_type": "water_meter",
        "location": "Test Location",
        "customer_id": "test-customer-id"
    }
    test_and_log("POST", "/iot/devices", admin_headers, iot_device_data, "Create IoT device", "Admin")
    test_and_log("PATCH", "/iot/devices/test-iot-id", admin_headers, {"status": "active"}, "Update IoT device", "Admin")
    test_and_log("DELETE", "/iot/devices/test-iot-id", admin_headers, description="Delete IoT device", role="Admin")
    
    register_data = {"device_id": "ESP32-TEST", "device_type": "water_meter", "location": "Test"}
    test_and_log("POST", "/iot/register", admin_headers, register_data, "Device registration", "Admin")
    
    iot_data = {
        "device_id": "ESP32-TEST",
        "timestamp": datetime.utcnow().isoformat(),
        "water_flow": 15.5,
        "pressure": 2.3,
        "temperature": 25.0
    }
    test_and_log("POST", "/iot/data", admin_headers, iot_data, "Data ingestion", "Admin")
    test_and_log("GET", "/iot/devices/ESP32-TEST/metrics", admin_headers, description="Device metrics", role="Admin")
    test_and_log("GET", "/iot/devices/ESP32-TEST/data", admin_headers, description="Historical data", role="Admin")
    
    print("\n6. ANALYTICS APIs (HIGH PRIORITY)")
    print("-" * 50)
    test_and_log("GET", "/analytics/usage", admin_headers, description="Usage data", role="Admin")
    test_and_log("GET", "/analytics/trends", admin_headers, description="Consumption trends", role="Admin")
    test_and_log("GET", "/analytics/predictions", admin_headers, description="7-day forecast", role="Admin")
    
    comparison_data = {
        "period1_start": "2025-01-01",
        "period1_end": "2025-01-15",
        "period2_start": "2024-12-01",
        "period2_end": "2024-12-15"
    }
    test_and_log("POST", "/analytics/comparison", admin_headers, comparison_data, "Compare periods", "Admin")
    test_and_log("GET", "/analytics/admin/overview", admin_headers, description="System-wide metrics", role="Admin")
    
    print("\n7. PAYMENT APIs (HIGH PRIORITY)")
    print("-" * 50)
    test_and_log("GET", "/payments/history/list", admin_headers, description="Payment history", role="Admin")
    test_and_log("GET", "/payments/test-ref-id", admin_headers, description="Payment detail", role="Admin")
    
    payment_data = {"amount": 100000, "payment_method": "virtual_account", "description": "Test payment"}
    test_and_log("POST", "/payments/create", admin_headers, payment_data, "Create payment", "Admin")
    
    callback_data = {"reference_id": "TEST-REF", "status": "paid", "amount": 100000}
    test_and_log("POST", "/payments/callback", admin_headers, callback_data, "Payment callback", "Admin")
    
    print("\n8. VOUCHER SYSTEM (HIGH PRIORITY)")
    print("-" * 50)
    test_and_log("GET", "/vouchers", admin_headers, description="List vouchers", role="Admin")
    
    voucher_data = {
        "code": f"TEST{int(time.time())}",
        "discount_type": "percentage",
        "discount_value": 25.0,
        "min_purchase_amount": 100000,
        "usage_limit": 50,
        "valid_from": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "is_active": True
    }
    test_and_log("POST", "/vouchers", admin_headers, voucher_data, "Create voucher", "Admin")
    test_and_log("GET", "/vouchers/active", admin_headers, description="Active vouchers", role="Admin")
    
    validate_data = {"voucher_code": "WELCOME50", "purchase_amount": 200000}
    test_and_log("POST", "/vouchers/validate", admin_headers, validate_data, "Validate voucher", "Admin")
    
    apply_data = {"voucher_code": "WELCOME50", "purchase_amount": 200000}
    test_and_log("POST", "/vouchers/apply", admin_headers, apply_data, "Apply voucher", "Admin")
    
    test_and_log("PATCH", "/vouchers/test-voucher-id/status", admin_headers, {"status": "active"}, "Update status", "Admin")
    test_and_log("GET", "/vouchers/usage-history", admin_headers, description="Usage history", role="Admin")
    
    print("\n9. SUPPORT TICKETS (HIGH PRIORITY)")
    print("-" * 50)
    test_and_log("GET", "/tickets/", admin_headers, description="List tickets", role="Admin")
    
    ticket_data = {
        "subject": "Test Ticket API",
        "description": "Test ticket created via API",
        "category": "technical_issue",
        "priority": "medium"
    }
    test_and_log("POST", "/tickets/", admin_headers, ticket_data, "Create ticket", "Admin")
    test_and_log("GET", "/tickets/test-ticket-id", admin_headers, description="Ticket detail", role="Admin")
    test_and_log("PUT", "/tickets/test-ticket-id", admin_headers, {"priority": "high"}, "Update ticket", "Admin")
    
    message_data = {"message": "Test message", "is_internal": False}
    test_and_log("POST", "/tickets/test-ticket-id/messages", admin_headers, message_data, "Add message", "Admin")
    test_and_log("GET", "/tickets/test-ticket-id/messages", admin_headers, description="Get messages", role="Admin")
    
    assign_data = {"technician_id": "tech-user-id"}
    test_and_log("PATCH", "/tickets/test-ticket-id/assign", admin_headers, assign_data, "Assign ticket", "Admin")
    
    status_data = {"status": "in_progress", "notes": "Working on it"}
    test_and_log("PATCH", "/tickets/test-ticket-id/status", admin_headers, status_data, "Update status", "Admin")
    test_and_log("GET", "/tickets/admin/stats", admin_headers, description="Ticket statistics", role="Admin")
    
    print("\n10. WATER CONSERVATION TIPS (HIGH PRIORITY)")
    print("-" * 50)
    test_and_log("GET", "/tips/", admin_headers, description="List tips", role="Admin")
    
    tip_data = {
        "title": "Test Water Saving Tip",
        "description": "Test tip created via API",
        "category": "general_savings",
        "difficulty_level": "medium",
        "potential_savings_percentage": 20.0,
        "implementation_time": "2 hours",
        "implementation_steps": ["Step 1", "Step 2"],
        "benefits": ["Save water", "Reduce costs"],
        "required_tools": ["Wrench"],
        "status": "published"
    }
    test_and_log("POST", "/tips/admin/create", admin_headers, tip_data, "Create tip", "Admin")
    test_and_log("GET", "/tips/test-tip-id", admin_headers, description="Tip detail", role="Admin")
    test_and_log("PUT", "/tips/admin/test-tip-id", admin_headers, {"title": "Updated Tip"}, "Update tip", "Admin")
    test_and_log("DELETE", "/tips/admin/test-tip-id", admin_headers, description="Delete tip", role="Admin")
    
    engage_data = {"action": "like"}
    test_and_log("POST", "/tips/test-tip-id/engage", admin_headers, engage_data, "Like/bookmark/implement", "Admin")
    test_and_log("GET", "/tips/personalized", admin_headers, description="Personalized tips", role="Admin")
    
    print("\n11. ALERT & NOTIFICATION SYSTEM (MEDIUM PRIORITY)")
    print("-" * 50)
    test_and_log("GET", "/alerts", admin_headers, description="List alerts", role="Admin")
    test_and_log("GET", "/alerts/unread-count", admin_headers, description="Unread count", role="Admin")
    test_and_log("PATCH", "/alerts/test-alert-id/status", admin_headers, {"status": "read"}, "Update alert status", "Admin")
    test_and_log("POST", "/alerts/mark-all-read", admin_headers, description="Mark all as read", role="Admin")
    test_and_log("GET", "/alerts/preferences", admin_headers, description="Get preferences", role="Admin")
    
    prefs_data = {"low_balance_threshold": 75000, "email_notifications": True}
    test_and_log("PUT", "/alerts/preferences", admin_headers, prefs_data, "Update preferences", "Admin")
    test_and_log("GET", "/alerts/leaks", admin_headers, description="Leak detection events", role="Admin")
    test_and_log("GET", "/alerts/tips", admin_headers, description="Water saving tips", role="Admin")
    
    print("\n12. ADMIN MANAGEMENT (MEDIUM PRIORITY)")
    print("-" * 50)
    test_and_log("GET", "/admin/dashboard/metrics", admin_headers, description="Dashboard metrics", role="Admin")
    test_and_log("GET", "/admin/devices/monitoring", admin_headers, description="Device monitoring", role="Admin")
    
    bulk_data = {"customer_ids": ["cust1", "cust2"], "operation": "send_notification", "parameters": {"message": "Test"}}
    test_and_log("POST", "/admin/customers/bulk", admin_headers, bulk_data, "Bulk operations", "Admin")
    
    maintenance_data = {
        "device_id": "test-device",
        "technician_id": "tech-id",
        "scheduled_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        "maintenance_type": "routine_check"
    }
    test_and_log("POST", "/admin/maintenance", admin_headers, maintenance_data, "Create maintenance", "Admin")
    test_and_log("GET", "/admin/maintenance", admin_headers, description="List maintenance", role="Admin")
    test_and_log("GET", "/admin/revenue/report", admin_headers, description="Revenue report", role="Admin")
    
    print("\n13. REPORT GENERATION (MEDIUM PRIORITY)")
    print("-" * 50)
    report_data = {
        "start_date": "2025-01-01",
        "end_date": "2025-01-31",
        "report_type": "usage_summary",
        "include_charts": True
    }
    test_and_log("POST", "/reports/export-pdf", admin_headers, report_data, "Generate PDF report", "Admin")
    test_and_log("POST", "/reports/export-excel", admin_headers, report_data, "Generate Excel report", "Admin")
    
    print("\n14. ROLE & PERMISSION MANAGEMENT (MEDIUM PRIORITY)")
    print("-" * 50)
    test_and_log("GET", "/roles/list", admin_headers, description="List roles", role="Admin")
    
    role_data = {"name": f"test_role_{int(time.time())}", "description": "Test role", "permissions": ["users.view"]}
    test_and_log("POST", "/roles/create", admin_headers, role_data, "Create role", "Admin")
    test_and_log("GET", "/roles/test-role-id", admin_headers, description="Role detail", role="Admin")
    test_and_log("PUT", "/roles/test-role-id", admin_headers, {"description": "Updated role"}, "Update role", "Admin")
    test_and_log("DELETE", "/roles/test-role-id", admin_headers, description="Delete role", role="Admin")
    test_and_log("GET", "/roles/permissions", admin_headers, description="List permissions", role="Admin")
    
    assign_role_data = {"user_id": "test-user", "role_name": "customer"}
    test_and_log("POST", "/roles/assign", admin_headers, assign_role_data, "Assign role to user", "Admin")
    
    print("\n15. PROPERTIES MANAGEMENT (LOW PRIORITY)")
    print("-" * 50)
    test_and_log("GET", "/properties", admin_headers, description="List properties", role="Admin")
    
    property_data = {
        "name": f"Test Property {int(time.time())}",
        "address": "Test Address",
        "property_type": "residential",
        "area_size": 100.0,
        "owner_name": "Test Owner",
        "owner_contact": "+6281234567890"
    }
    test_and_log("POST", "/properties", admin_headers, property_data, "Create property", "Admin")
    test_and_log("GET", "/properties/test-property-id", admin_headers, description="Property detail", role="Admin")
    test_and_log("PUT", "/properties/test-property-id", admin_headers, {"area_size": 150.0}, "Update property", "Admin")
    test_and_log("DELETE", "/properties/test-property-id", admin_headers, description="Delete property", role="Admin")
    
    # Print final summary
    print("\n" + "="*80)
    print("🔍 COMPREHENSIVE API TESTING COMPLETE")
    print("="*80)
    print(f"📊 TOTAL TESTS: {results['total']}")
    print(f"✅ PASSED: {results['passed']} ({results['passed']/results['total']*100:.1f}%)")
    print(f"❌ FAILED: {results['failed']} ({results['failed']/results['total']*100:.1f}%)")
    
    print(f"\n🚨 FAILED TESTS:")
    failed_tests = [detail for detail in results['details'] if detail.startswith('❌')]
    if failed_tests:
        for failed in failed_tests:
            print(f"   {failed}")
    else:
        print("   ✅ No failed tests!")
    
    print("\n🎯 RECOMMENDATIONS:")
    if results['failed'] > 0:
        print("   1. 🔥 URGENT: Fix failed endpoints")
        print("   2. ⚠️  Verify role-based access control")
        print("   3. 💡 Test with actual data in database")
    else:
        print("   ✅ Excellent! All tests passed. System is production-ready!")

if __name__ == "__main__":
    run_comprehensive_tests()