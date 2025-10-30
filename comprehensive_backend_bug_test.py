#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND API BUG TESTING - IndoWater Solution
Tests ALL backend endpoints systematically to find ALL bugs across 16 modules
Focus on finding specific reported bugs and any other issues
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# Backend URL from environment
BACKEND_URL = "https://fix-bugs-backend.preview.emergentagent.com/api"

# Demo accounts to test ALL 3 user roles
DEMO_ACCOUNTS = [
    {
        "name": "Admin",
        "email": "admin@indowater.com",
        "password": "admin123",
        "expected_role": "admin"
    },
    {
        "name": "Technician", 
        "email": "technician@indowater.com",
        "password": "tech123",
        "expected_role": "technician"
    },
    {
        "name": "Customer",
        "email": "customer@indowater.com", 
        "password": "customer123",
        "expected_role": "customer"
    }
]

class BugTestResults:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.bugs_found = []
        self.critical_bugs = []
        self.medium_bugs = []
        self.minor_bugs = []
    
    def add_test_result(self, test_name: str, success: bool, error: str = None, endpoint: str = None, method: str = "GET", user_role: str = None, severity: str = "medium"):
        self.total_tests += 1
        if success:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
            bug = {
                "test_name": test_name,
                "endpoint": endpoint,
                "method": method,
                "user_role": user_role,
                "error": error,
                "severity": severity,
                "timestamp": datetime.now().isoformat()
            }
            self.bugs_found.append(bug)
            
            if severity == "critical":
                self.critical_bugs.append(bug)
            elif severity == "medium":
                self.medium_bugs.append(bug)
            else:
                self.minor_bugs.append(bug)
    
    def print_summary(self):
        print(f"\n{'='*80}")
        print(f"🔍 COMPREHENSIVE BACKEND API BUG TESTING RESULTS")
        print(f"{'='*80}")
        print(f"📊 TOTAL TESTS: {self.total_tests}")
        print(f"✅ PASSED: {self.passed_tests} ({self.passed_tests/self.total_tests*100:.1f}%)")
        print(f"❌ FAILED: {self.failed_tests} ({self.failed_tests/self.total_tests*100:.1f}%)")
        print(f"🐛 BUGS FOUND: {len(self.bugs_found)}")
        print(f"   🔴 Critical: {len(self.critical_bugs)}")
        print(f"   🟡 Medium: {len(self.medium_bugs)}")
        print(f"   🟢 Minor: {len(self.minor_bugs)}")
        
        if self.bugs_found:
            print(f"\n{'='*80}")
            print(f"🐛 DETAILED BUG REPORT")
            print(f"{'='*80}")
            
            # Critical bugs first
            if self.critical_bugs:
                print(f"\n🔴 CRITICAL BUGS ({len(self.critical_bugs)}):")
                for i, bug in enumerate(self.critical_bugs, 1):
                    print(f"   {i}. {bug['test_name']}")
                    print(f"      Endpoint: {bug['method']} {bug['endpoint']}")
                    print(f"      User Role: {bug['user_role']}")
                    print(f"      Error: {bug['error']}")
                    print()
            
            # Medium bugs
            if self.medium_bugs:
                print(f"\n🟡 MEDIUM BUGS ({len(self.medium_bugs)}):")
                for i, bug in enumerate(self.medium_bugs, 1):
                    print(f"   {i}. {bug['test_name']}")
                    print(f"      Endpoint: {bug['method']} {bug['endpoint']}")
                    print(f"      User Role: {bug['user_role']}")
                    print(f"      Error: {bug['error']}")
                    print()
            
            # Minor bugs
            if self.minor_bugs:
                print(f"\n🟢 MINOR BUGS ({len(self.minor_bugs)}):")
                for i, bug in enumerate(self.minor_bugs, 1):
                    print(f"   {i}. {bug['test_name']}")
                    print(f"      Endpoint: {bug['method']} {bug['endpoint']}")
                    print(f"      User Role: {bug['user_role']}")
                    print(f"      Error: {bug['error']}")
                    print()

def test_login_all_roles(results: BugTestResults) -> Dict[str, Any]:
    """Test login for all 3 user roles"""
    print(f"\n🔐 TESTING AUTHENTICATION APIs (/api/auth/*)")
    print(f"{'='*60}")
    
    login_results = {}
    
    for account in DEMO_ACCOUNTS:
        print(f"\n   Testing {account['name']} Login...")
        
        login_data = {
            "email": account["email"],
            "password": account["password"]
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["access_token", "token_type", "user"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    results.add_test_result(
                        f"{account['name']} Login - Response Structure",
                        False,
                        f"Missing required fields: {missing_fields}",
                        "/auth/login",
                        "POST",
                        account['expected_role'],
                        "critical"
                    )
                    continue
                
                # Validate user object
                user = data.get("user", {})
                user_required_fields = ["id", "email", "full_name", "role", "is_active"]
                missing_user_fields = [field for field in user_required_fields if field not in user]
                
                if missing_user_fields:
                    results.add_test_result(
                        f"{account['name']} Login - User Object",
                        False,
                        f"Missing user fields: {missing_user_fields}",
                        "/auth/login",
                        "POST",
                        account['expected_role'],
                        "critical"
                    )
                    continue
                
                # Validate role
                actual_role = user.get("role")
                if actual_role != account['expected_role']:
                    results.add_test_result(
                        f"{account['name']} Login - Role Validation",
                        False,
                        f"Role mismatch. Expected: {account['expected_role']}, Got: {actual_role}",
                        "/auth/login",
                        "POST",
                        account['expected_role'],
                        "critical"
                    )
                    continue
                
                print(f"      ✅ SUCCESS - {account['name']} login working")
                results.add_test_result(f"{account['name']} Login", True, None, "/auth/login", "POST", account['expected_role'])
                
                login_results[account['expected_role']] = {
                    "success": True,
                    "token": data.get("access_token"),
                    "user": user
                }
                
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", str(error_data))
                except:
                    error_msg = response.text or f"HTTP {response.status_code}"
                
                print(f"      ❌ FAILED - {error_msg}")
                results.add_test_result(
                    f"{account['name']} Login",
                    False,
                    error_msg,
                    "/auth/login",
                    "POST",
                    account['expected_role'],
                    "critical"
                )
                
        except Exception as e:
            print(f"      ❌ CONNECTION ERROR - {str(e)}")
            results.add_test_result(
                f"{account['name']} Login",
                False,
                f"Connection error: {str(e)}",
                "/auth/login",
                "POST",
                account['expected_role'],
                "critical"
            )
    
    return login_results

def test_profile_update_bug(results: BugTestResults, login_results: Dict[str, Any]):
    """Test the reported Profile Update API bug (PUT /api/auth/profile) - reported 500 error"""
    print(f"\n🔧 TESTING PROFILE UPDATE BUG (PUT /api/auth/profile)")
    print(f"{'='*60}")
    
    for role, login_data in login_results.items():
        if not login_data.get("success"):
            continue
            
        print(f"\n   Testing Profile Update for {role}...")
        
        headers = {
            "Authorization": f"Bearer {login_data['token']}",
            "Content-Type": "application/json"
        }
        
        # Test profile update with various data
        update_data = {
            "full_name": f"Updated {role.title()} User",
            "phone": "+6281234567890"
        }
        
        try:
            response = requests.put(
                f"{BACKEND_URL}/auth/profile",
                json=update_data,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                updated_user = response.json()
                print(f"      ✅ SUCCESS - Profile updated for {role}")
                results.add_test_result(f"Profile Update - {role}", True, None, "/auth/profile", "PUT", role)
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", str(error_data))
                except:
                    error_msg = response.text or f"HTTP {response.status_code}"
                
                print(f"      ❌ FAILED - {error_msg}")
                results.add_test_result(
                    f"Profile Update - {role}",
                    False,
                    error_msg,
                    "/auth/profile",
                    "PUT",
                    role,
                    "critical"
                )
                
        except Exception as e:
            print(f"      ❌ ERROR - {str(e)}")
            results.add_test_result(
                f"Profile Update - {role}",
                False,
                f"Request error: {str(e)}",
                "/auth/profile",
                "PUT",
                role,
                "critical"
            )

def test_iot_monitoring_apis(results: BugTestResults, login_results: Dict[str, Any]):
    """Test IoT Monitoring APIs - reported all endpoints returning 404"""
    print(f"\n🌐 TESTING IOT MONITORING APIs (/api/iot/*)")
    print(f"{'='*60}")
    
    iot_endpoints = [
        {"path": "/iot/devices", "method": "GET", "description": "List IoT devices"},
        {"path": "/iot/devices", "method": "POST", "description": "Register IoT device", "roles": ["admin", "technician"]},
        {"path": "/iot/data", "method": "POST", "description": "Ingest IoT data", "roles": ["admin", "technician"]},
        {"path": "/iot/devices/test-device/metrics", "method": "GET", "description": "Device metrics"},
        {"path": "/iot/devices/test-device/status", "method": "GET", "description": "Device status"},
        {"path": "/iot/devices/test-device/commands", "method": "POST", "description": "Send device command", "roles": ["admin", "technician"]},
    ]
    
    for role, login_data in login_results.items():
        if not login_data.get("success"):
            continue
            
        print(f"\n   Testing IoT APIs for {role}...")
        
        headers = {
            "Authorization": f"Bearer {login_data['token']}",
            "Content-Type": "application/json"
        }
        
        for endpoint in iot_endpoints:
            # Skip role-restricted endpoints
            if endpoint.get("roles") and role not in endpoint["roles"]:
                continue
                
            print(f"      Testing {endpoint['method']} {endpoint['path']}...")
            
            try:
                if endpoint["method"] == "GET":
                    response = requests.get(
                        f"{BACKEND_URL}{endpoint['path']}",
                        headers=headers,
                        timeout=15
                    )
                elif endpoint["method"] == "POST":
                    # Prepare test data based on endpoint
                    if "devices" in endpoint["path"] and endpoint["path"].endswith("/devices"):
                        test_data = {
                            "device_id": f"ESP32-TEST-{int(time.time())}",
                            "device_name": "Test IoT Device",
                            "device_type": "water_meter",
                            "location": "Test Location",
                            "customer_id": "test-customer-1"
                        }
                    elif "data" in endpoint["path"]:
                        test_data = {
                            "device_id": "test-device-1",
                            "timestamp": datetime.now().isoformat(),
                            "water_flow": 15.5,
                            "pressure": 2.3,
                            "temperature": 25.0,
                            "battery_level": 85
                        }
                    elif "commands" in endpoint["path"]:
                        test_data = {
                            "command": "read_meter",
                            "parameters": {}
                        }
                    else:
                        test_data = {}
                    
                    response = requests.post(
                        f"{BACKEND_URL}{endpoint['path']}",
                        json=test_data,
                        headers=headers,
                        timeout=15
                    )
                
                if response.status_code in [200, 201]:
                    print(f"         ✅ SUCCESS - {endpoint['description']}")
                    results.add_test_result(
                        f"IoT {endpoint['description']} - {role}",
                        True,
                        None,
                        endpoint['path'],
                        endpoint['method'],
                        role
                    )
                elif response.status_code == 404:
                    print(f"         ❌ 404 NOT FOUND - {endpoint['description']}")
                    results.add_test_result(
                        f"IoT {endpoint['description']} - {role}",
                        False,
                        "404 Not Found - Endpoint not registered or routing issue",
                        endpoint['path'],
                        endpoint['method'],
                        role,
                        "critical"
                    )
                else:
                    error_msg = f"HTTP {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("detail", str(error_data))
                    except:
                        error_msg = response.text or f"HTTP {response.status_code}"
                    
                    print(f"         ❌ FAILED - {error_msg}")
                    results.add_test_result(
                        f"IoT {endpoint['description']} - {role}",
                        False,
                        error_msg,
                        endpoint['path'],
                        endpoint['method'],
                        role,
                        "medium"
                    )
                    
            except Exception as e:
                print(f"         ❌ ERROR - {str(e)}")
                results.add_test_result(
                    f"IoT {endpoint['description']} - {role}",
                    False,
                    f"Request error: {str(e)}",
                    endpoint['path'],
                    endpoint['method'],
                    role,
                    "critical"
                )

def test_support_tickets_bug(results: BugTestResults, login_results: Dict[str, Any]):
    """Test Support Ticket Creation bug - reported Customer not found error"""
    print(f"\n🎫 TESTING SUPPORT TICKETS APIs (/api/tickets/*)")
    print(f"{'='*60}")
    
    ticket_endpoints = [
        {"path": "/tickets/", "method": "GET", "description": "List tickets"},
        {"path": "/tickets/", "method": "POST", "description": "Create ticket"},
        {"path": "/tickets/admin/stats", "method": "GET", "description": "Admin stats", "roles": ["admin"]},
        {"path": "/tickets/test-ticket-id", "method": "GET", "description": "Get ticket detail"},
        {"path": "/tickets/test-ticket-id", "method": "PUT", "description": "Update ticket"},
        {"path": "/tickets/test-ticket-id/messages", "method": "POST", "description": "Add message"},
        {"path": "/tickets/test-ticket-id/assign", "method": "PATCH", "description": "Assign ticket", "roles": ["admin", "technician"]},
        {"path": "/tickets/test-ticket-id/status", "method": "PATCH", "description": "Update status", "roles": ["admin", "technician"]},
    ]
    
    for role, login_data in login_results.items():
        if not login_data.get("success"):
            continue
            
        print(f"\n   Testing Support Tickets for {role}...")
        
        headers = {
            "Authorization": f"Bearer {login_data['token']}",
            "Content-Type": "application/json"
        }
        
        for endpoint in ticket_endpoints:
            # Skip role-restricted endpoints
            if endpoint.get("roles") and role not in endpoint["roles"]:
                continue
                
            print(f"      Testing {endpoint['method']} {endpoint['path']}...")
            
            try:
                if endpoint["method"] == "GET":
                    response = requests.get(
                        f"{BACKEND_URL}{endpoint['path']}",
                        headers=headers,
                        timeout=15
                    )
                elif endpoint["method"] == "POST":
                    if endpoint["path"].endswith("/tickets/"):
                        # Test ticket creation - this is the reported bug
                        test_data = {
                            "subject": "Test Support Ticket",
                            "description": "This is a test ticket to check for customer not found error",
                            "category": "technical_issue",
                            "priority": "medium"
                        }
                    elif "messages" in endpoint["path"]:
                        test_data = {
                            "message": "Test message for ticket",
                            "is_internal": False
                        }
                    else:
                        test_data = {}
                    
                    response = requests.post(
                        f"{BACKEND_URL}{endpoint['path']}",
                        json=test_data,
                        headers=headers,
                        timeout=15
                    )
                elif endpoint["method"] in ["PUT", "PATCH"]:
                    if "assign" in endpoint["path"]:
                        test_data = {"technician_id": "test-technician-id"}
                    elif "status" in endpoint["path"]:
                        test_data = {"status": "in_progress", "notes": "Test status update"}
                    else:
                        test_data = {"subject": "Updated Test Ticket"}
                    
                    if endpoint["method"] == "PUT":
                        response = requests.put(
                            f"{BACKEND_URL}{endpoint['path']}",
                            json=test_data,
                            headers=headers,
                            timeout=15
                        )
                    else:
                        response = requests.patch(
                            f"{BACKEND_URL}{endpoint['path']}",
                            json=test_data,
                            headers=headers,
                            timeout=15
                        )
                
                if response.status_code in [200, 201]:
                    print(f"         ✅ SUCCESS - {endpoint['description']}")
                    results.add_test_result(
                        f"Support Ticket {endpoint['description']} - {role}",
                        True,
                        None,
                        endpoint['path'],
                        endpoint['method'],
                        role
                    )
                elif response.status_code == 404:
                    print(f"         ❌ 404 NOT FOUND - {endpoint['description']}")
                    results.add_test_result(
                        f"Support Ticket {endpoint['description']} - {role}",
                        False,
                        "404 Not Found - Endpoint not registered or routing issue",
                        endpoint['path'],
                        endpoint['method'],
                        role,
                        "critical"
                    )
                else:
                    error_msg = f"HTTP {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("detail", str(error_data))
                        
                        # Check for specific "Customer not found" error
                        if "customer" in error_msg.lower() and "not found" in error_msg.lower():
                            print(f"         ❌ CUSTOMER NOT FOUND BUG - {error_msg}")
                            results.add_test_result(
                                f"Support Ticket {endpoint['description']} - {role}",
                                False,
                                f"REPORTED BUG: {error_msg}",
                                endpoint['path'],
                                endpoint['method'],
                                role,
                                "critical"
                            )
                            continue
                    except:
                        error_msg = response.text or f"HTTP {response.status_code}"
                    
                    print(f"         ❌ FAILED - {error_msg}")
                    results.add_test_result(
                        f"Support Ticket {endpoint['description']} - {role}",
                        False,
                        error_msg,
                        endpoint['path'],
                        endpoint['method'],
                        role,
                        "medium"
                    )
                    
            except Exception as e:
                print(f"         ❌ ERROR - {str(e)}")
                results.add_test_result(
                    f"Support Ticket {endpoint['description']} - {role}",
                    False,
                    f"Request error: {str(e)}",
                    endpoint['path'],
                    endpoint['method'],
                    role,
                    "critical"
                )

def test_all_other_apis(results: BugTestResults, login_results: Dict[str, Any]):
    """Test all other API endpoints systematically"""
    print(f"\n🔍 TESTING ALL OTHER APIs")
    print(f"{'='*60}")
    
    # Define all API modules and their endpoints
    api_modules = {
        "Dashboard": [
            {"path": "/dashboard/stats", "method": "GET", "description": "Dashboard statistics"}
        ],
        "User Management": [
            {"path": "/users", "method": "GET", "description": "List users", "roles": ["admin"]},
            {"path": "/users", "method": "POST", "description": "Create user", "roles": ["admin"]},
        ],
        "Customer Management": [
            {"path": "/customers", "method": "GET", "description": "List customers", "roles": ["admin", "technician"]},
            {"path": "/customers", "method": "POST", "description": "Create customer", "roles": ["admin"]},
        ],
        "Property Management": [
            {"path": "/properties", "method": "GET", "description": "List properties"},
            {"path": "/properties", "method": "POST", "description": "Create property", "roles": ["admin", "technician"]},
        ],
        "Device Management": [
            {"path": "/devices", "method": "GET", "description": "List devices"},
            {"path": "/devices/comprehensive", "method": "GET", "description": "Comprehensive device data"},
            {"path": "/devices", "method": "POST", "description": "Create device", "roles": ["admin", "technician"]},
        ],
        "Analytics": [
            {"path": "/analytics/usage", "method": "GET", "description": "Usage analytics"},
            {"path": "/analytics/trends", "method": "GET", "description": "Consumption trends"},
            {"path": "/analytics/predictions", "method": "GET", "description": "Usage predictions"},
            {"path": "/analytics/admin/overview", "method": "GET", "description": "Admin overview", "roles": ["admin"]},
        ],
        "Payment": [
            {"path": "/payments/history/list", "method": "GET", "description": "Payment history"},
        ],
        "Voucher": [
            {"path": "/vouchers", "method": "GET", "description": "List vouchers"},
            {"path": "/vouchers", "method": "POST", "description": "Create voucher", "roles": ["admin"]},
            {"path": "/vouchers/validate", "method": "POST", "description": "Validate voucher"},
            {"path": "/vouchers/apply", "method": "POST", "description": "Apply voucher"},
        ],
        "Water Conservation Tips": [
            {"path": "/tips/", "method": "GET", "description": "List tips"},
            {"path": "/tips/admin/create", "method": "POST", "description": "Create tip", "roles": ["admin"]},
        ],
        "Alerts & Notifications": [
            {"path": "/alerts/", "method": "GET", "description": "List alerts"},
            {"path": "/alerts/unread-count", "method": "GET", "description": "Unread count"},
            {"path": "/alerts/preferences", "method": "GET", "description": "Alert preferences"},
            {"path": "/alerts/mark-all-read", "method": "POST", "description": "Mark all read"},
        ],
        "Report Generation": [
            {"path": "/reports/export-pdf", "method": "POST", "description": "Generate PDF report"},
            {"path": "/reports/export-excel", "method": "POST", "description": "Generate Excel report"},
        ],
        "Role & Permission": [
            {"path": "/roles/list", "method": "GET", "description": "List roles", "roles": ["admin"]},
            {"path": "/roles/permissions", "method": "GET", "description": "List permissions", "roles": ["admin"]},
        ],
        "Admin Management": [
            {"path": "/admin/dashboard/metrics", "method": "GET", "description": "Admin metrics", "roles": ["admin"]},
            {"path": "/admin/devices/monitoring", "method": "GET", "description": "Device monitoring", "roles": ["admin", "technician"]},
            {"path": "/admin/revenue/report", "method": "GET", "description": "Revenue report", "roles": ["admin"]},
        ]
    }
    
    for module_name, endpoints in api_modules.items():
        print(f"\n   Testing {module_name} APIs...")
        
        for role, login_data in login_results.items():
            if not login_data.get("success"):
                continue
                
            headers = {
                "Authorization": f"Bearer {login_data['token']}",
                "Content-Type": "application/json"
            }
            
            for endpoint in endpoints:
                # Skip role-restricted endpoints
                if endpoint.get("roles") and role not in endpoint["roles"]:
                    continue
                    
                print(f"      Testing {endpoint['method']} {endpoint['path']} ({role})...")
                
                try:
                    if endpoint["method"] == "GET":
                        response = requests.get(
                            f"{BACKEND_URL}{endpoint['path']}",
                            headers=headers,
                            timeout=15
                        )
                    elif endpoint["method"] == "POST":
                        # Prepare test data based on endpoint
                        test_data = {}
                        if "users" in endpoint["path"]:
                            test_data = {
                                "email": f"test_{int(time.time())}@indowater.com",
                                "password": "testpass123",
                                "full_name": "Test User",
                                "role": "customer"
                            }
                        elif "customers" in endpoint["path"]:
                            test_data = {
                                "customer_number": f"CUST{int(time.time())}",
                                "full_name": "Test Customer",
                                "email": f"customer_{int(time.time())}@indowater.com",
                                "phone": "+6281234567890",
                                "address": "Test Address"
                            }
                        elif "properties" in endpoint["path"]:
                            test_data = {
                                "name": f"Test Property {int(time.time())}",
                                "address": "Test Address",
                                "property_type": "residential",
                                "area_size": 100.0
                            }
                        elif "devices" in endpoint["path"]:
                            test_data = {
                                "device_id": f"DEV{int(time.time())}",
                                "device_type": "water_meter",
                                "customer_id": "test-customer",
                                "property_id": "test-property"
                            }
                        elif "vouchers" in endpoint["path"]:
                            if "validate" in endpoint["path"]:
                                test_data = {"voucher_code": "TEST123", "purchase_amount": 100000}
                            elif "apply" in endpoint["path"]:
                                test_data = {"voucher_code": "TEST123", "purchase_amount": 100000}
                            else:
                                test_data = {
                                    "code": f"TEST{int(time.time())}",
                                    "discount_type": "percentage",
                                    "discount_value": 10,
                                    "min_purchase_amount": 50000
                                }
                        elif "tips" in endpoint["path"]:
                            test_data = {
                                "title": "Test Water Saving Tip",
                                "description": "This is a test tip",
                                "category": "general_savings",
                                "difficulty_level": "easy",
                                "potential_savings_percentage": 15
                            }
                        elif "reports" in endpoint["path"]:
                            test_data = {
                                "start_date": (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                                "end_date": datetime.now().strftime('%Y-%m-%d'),
                                "report_type": "usage_summary"
                            }
                        
                        response = requests.post(
                            f"{BACKEND_URL}{endpoint['path']}",
                            json=test_data,
                            headers=headers,
                            timeout=15
                        )
                    
                    if response.status_code in [200, 201]:
                        print(f"         ✅ SUCCESS")
                        results.add_test_result(
                            f"{module_name} {endpoint['description']} - {role}",
                            True,
                            None,
                            endpoint['path'],
                            endpoint['method'],
                            role
                        )
                    elif response.status_code == 404:
                        print(f"         ❌ 404 NOT FOUND")
                        results.add_test_result(
                            f"{module_name} {endpoint['description']} - {role}",
                            False,
                            "404 Not Found - Endpoint not registered or routing issue",
                            endpoint['path'],
                            endpoint['method'],
                            role,
                            "critical"
                        )
                    elif response.status_code == 422:
                        print(f"         ❌ 422 VALIDATION ERROR")
                        try:
                            error_data = response.json()
                            error_msg = error_data.get("detail", str(error_data))
                        except:
                            error_msg = "Validation error"
                        results.add_test_result(
                            f"{module_name} {endpoint['description']} - {role}",
                            False,
                            f"Validation error: {error_msg}",
                            endpoint['path'],
                            endpoint['method'],
                            role,
                            "medium"
                        )
                    elif response.status_code == 500:
                        print(f"         ❌ 500 INTERNAL SERVER ERROR")
                        try:
                            error_data = response.json()
                            error_msg = error_data.get("detail", str(error_data))
                        except:
                            error_msg = "Internal server error"
                        results.add_test_result(
                            f"{module_name} {endpoint['description']} - {role}",
                            False,
                            f"Internal server error: {error_msg}",
                            endpoint['path'],
                            endpoint['method'],
                            role,
                            "critical"
                        )
                    else:
                        error_msg = f"HTTP {response.status_code}"
                        try:
                            error_data = response.json()
                            error_msg = error_data.get("detail", str(error_data))
                        except:
                            error_msg = response.text or f"HTTP {response.status_code}"
                        
                        print(f"         ❌ FAILED - {error_msg}")
                        results.add_test_result(
                            f"{module_name} {endpoint['description']} - {role}",
                            False,
                            error_msg,
                            endpoint['path'],
                            endpoint['method'],
                            role,
                            "medium"
                        )
                        
                except Exception as e:
                    print(f"         ❌ ERROR - {str(e)}")
                    results.add_test_result(
                        f"{module_name} {endpoint['description']} - {role}",
                        False,
                        f"Request error: {str(e)}",
                        endpoint['path'],
                        endpoint['method'],
                        role,
                        "critical"
                    )

def main():
    """Main testing function"""
    print(f"🔍 COMPREHENSIVE BACKEND API BUG TESTING - IndoWater Solution")
    print(f"Testing against: {BACKEND_URL}")
    print(f"Focus: Find ALL bugs across 16 API modules with 3 user roles")
    print(f"{'='*80}")
    
    results = BugTestResults()
    
    # Step 1: Test login for all roles
    login_results = test_login_all_roles(results)
    
    # Step 2: Test specific reported bugs
    test_profile_update_bug(results, login_results)
    test_iot_monitoring_apis(results, login_results)
    test_support_tickets_bug(results, login_results)
    
    # Step 3: Test all other APIs systematically
    test_all_other_apis(results, login_results)
    
    # Step 4: Print comprehensive results
    results.print_summary()
    
    return results

if __name__ == "__main__":
    results = main()
    
    # Exit with error code if critical bugs found
    if results.critical_bugs:
        sys.exit(1)
    else:
        sys.exit(0)