#!/usr/bin/env python3
"""
COMPREHENSIVE FULL BACKEND API TESTING SCRIPT FOR INDOWATER SOLUTION
Complete bug sweep testing ALL backend API endpoints across ALL modules.

This script performs exhaustive testing of the IndoWater backend system including:
1. Authentication APIs (/api/auth/*)
2. Dashboard APIs (/api/dashboard/*)
3. User Management APIs (/api/users/*)
4. Customer Management APIs (/api/customers/*)
5. Properties APIs (/api/properties/*)
6. Device Management APIs (/api/devices/*)
7. IoT Monitoring APIs (/api/iot/*)
8. Analytics APIs (/api/analytics/*)
9. Payment APIs (/api/payments/*)
10. Voucher APIs (/api/vouchers/*)
11. Support Tickets APIs (/api/tickets/*)
12. Water Conservation Tips APIs (/api/tips/*)
13. Alert & Notification APIs (/api/alerts/*)
14. Report Generation APIs (/api/reports/*)
15. Admin Management APIs (/api/admin/*)
16. Role & Permission APIs (/api/roles/*)

Testing Goals:
- Verify ALL endpoints return correct status codes (200/201/204, not 404/500)
- Test with proper authentication (Bearer tokens)
- Validate response structure and data integrity
- Check role-based access control
- Test CRUD operations completely
- Identify ALL bugs, errors, and routing issues
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

# Backend URL from environment
BACKEND_URL = "https://fix-bugs-backend.preview.emergentagent.com/api"

# Demo accounts to test
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

class APITester:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.all_results = {}
        
    def make_request(self, method: str, url: str, headers: dict = None, json_data: dict = None, timeout: int = 15) -> Dict[str, Any]:
        """Make HTTP request and return standardized result"""
        self.total_tests += 1
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=json_data, timeout=timeout)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=json_data, timeout=timeout)
            elif method.upper() == "PATCH":
                response = requests.patch(url, headers=headers, json=json_data, timeout=timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Check if request was successful
            if response.status_code in [200, 201, 204]:
                self.passed_tests += 1
                try:
                    data = response.json() if response.content else {}
                except:
                    data = {"content_length": len(response.content), "content_type": response.headers.get('content-type', '')}
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": data,
                    "headers": dict(response.headers)
                }
            else:
                self.failed_tests += 1
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", str(error_data))
                except:
                    error_msg = response.text or f"HTTP {response.status_code}"
                
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": error_msg,
                    "headers": dict(response.headers)
                }
                
        except requests.exceptions.RequestException as e:
            self.failed_tests += 1
            return {
                "success": False,
                "error": f"Connection error: {str(e)}",
                "status_code": None
            }
        except Exception as e:
            self.failed_tests += 1
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "status_code": None
            }

    def test_login(self, email: str, password: str, expected_role: str, account_name: str) -> Dict[str, Any]:
        """Test login for a specific account"""
        print(f"\n🔐 Testing {account_name} Login...")
        print(f"   Email: {email}")
        
        login_data = {
            "email": email,
            "password": password
        }
        
        result = self.make_request("POST", f"{BACKEND_URL}/auth/login", 
                                 headers={"Content-Type": "application/json"}, 
                                 json_data=login_data)
        
        if result["success"]:
            data = result["data"]
            
            # Validate response structure
            required_fields = ["access_token", "token_type", "user"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"   ❌ FAILED - Missing required fields: {missing_fields}")
                return {"success": False, "error": f"Missing required fields: {missing_fields}"}
            
            user = data.get("user", {})
            actual_role = user.get("role")
            
            if actual_role != expected_role:
                print(f"   ❌ FAILED - Role mismatch. Expected: {expected_role}, Got: {actual_role}")
                return {"success": False, "error": f"Role mismatch. Expected: {expected_role}, Got: {actual_role}"}
            
            token = data.get("access_token")
            print(f"   ✅ SUCCESS - Role: {actual_role}, Token: {token[:20]}...")
            
            return {
                "success": True,
                "data": data,
                "token": token,
                "user": user
            }
        else:
            print(f"   ❌ FAILED - {result['error']}")
            return result

    def test_authentication_apis(self, token: str, user_role: str) -> Dict[str, Any]:
        """Test Authentication APIs (/api/auth/*)"""
        print(f"\n🔐 Testing Authentication APIs ({user_role})...")
        
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        results = {}
        
        # Test /auth/me
        print("   📋 Testing GET /api/auth/me...")
        result = self.make_request("GET", f"{BACKEND_URL}/auth/me", headers=headers)
        results["get_current_user"] = result
        if result["success"]:
            print(f"      ✅ SUCCESS - User info retrieved")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test /auth/profile update
        print("   ✏️ Testing PUT /api/auth/profile...")
        profile_data = {"full_name": f"Updated {user_role.title()} User"}
        result = self.make_request("PUT", f"{BACKEND_URL}/auth/profile", headers=headers, json_data=profile_data)
        results["update_profile"] = result
        if result["success"]:
            print(f"      ✅ SUCCESS - Profile updated")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        return results

    def test_dashboard_apis(self, token: str, user_role: str) -> Dict[str, Any]:
        """Test Dashboard APIs (/api/dashboard/*)"""
        print(f"\n📊 Testing Dashboard APIs ({user_role})...")
        
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        results = {}
        
        # Test /dashboard/stats
        print("   📈 Testing GET /api/dashboard/stats...")
        result = self.make_request("GET", f"{BACKEND_URL}/dashboard/stats", headers=headers)
        results["dashboard_stats"] = result
        if result["success"]:
            stats = result["data"]
            print(f"      ✅ SUCCESS - Dashboard stats retrieved")
            
            # Check role-specific fields
            if user_role == "admin":
                expected_fields = ["total_users", "total_customers", "total_properties", "total_devices"]
            elif user_role == "technician":
                expected_fields = ["total_devices", "active_devices"]
            else:  # customer
                expected_fields = ["total_devices", "total_balance"]
            
            missing_fields = [field for field in expected_fields if field not in stats]
            if missing_fields:
                print(f"      ⚠️  Missing expected fields for {user_role}: {missing_fields}")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        return results

    def test_user_management_apis(self, token: str, user_role: str) -> Dict[str, Any]:
        """Test User Management APIs (/api/users/*)"""
        print(f"\n👥 Testing User Management APIs ({user_role})...")
        
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        results = {}
        
        if user_role != "admin":
            print("   ⚠️  Skipping user management tests - requires admin role")
            return {"skipped": "Not admin role"}
        
        # Test GET /users
        print("   📋 Testing GET /api/users...")
        result = self.make_request("GET", f"{BACKEND_URL}/users", headers=headers)
        results["list_users"] = result
        if result["success"]:
            users = result["data"]
            print(f"      ✅ SUCCESS - Found {len(users)} users")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test POST /users (create user)
        print("   ➕ Testing POST /api/users...")
        user_data = {
            "email": f"test_user_{int(time.time())}@indowater.com",
            "password": "testpass123",
            "full_name": "Test User",
            "role": "customer",
            "phone": "+6281234567890"
        }
        result = self.make_request("POST", f"{BACKEND_URL}/users", headers=headers, json_data=user_data)
        results["create_user"] = result
        if result["success"]:
            new_user = result["data"]
            created_user_id = new_user.get("id")
            print(f"      ✅ SUCCESS - User created with ID: {created_user_id}")
            
            # Test GET /users/{user_id}
            if created_user_id:
                print(f"   🔍 Testing GET /api/users/{created_user_id}...")
                result = self.make_request("GET", f"{BACKEND_URL}/users/{created_user_id}", headers=headers)
                results["get_user"] = result
                if result["success"]:
                    print(f"      ✅ SUCCESS - User details retrieved")
                else:
                    print(f"      ❌ FAILED - {result['error']}")
                
                # Test PUT /users/{user_id}
                print(f"   ✏️ Testing PUT /api/users/{created_user_id}...")
                update_data = {"full_name": "Updated Test User"}
                result = self.make_request("PUT", f"{BACKEND_URL}/users/{created_user_id}", headers=headers, json_data=update_data)
                results["update_user"] = result
                if result["success"]:
                    print(f"      ✅ SUCCESS - User updated")
                else:
                    print(f"      ❌ FAILED - {result['error']}")
                
                # Test DELETE /users/{user_id}
                print(f"   🗑️ Testing DELETE /api/users/{created_user_id}...")
                result = self.make_request("DELETE", f"{BACKEND_URL}/users/{created_user_id}", headers=headers)
                results["delete_user"] = result
                if result["success"]:
                    print(f"      ✅ SUCCESS - User deleted")
                else:
                    print(f"      ❌ FAILED - {result['error']}")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        return results

    def test_customer_management_apis(self, token: str, user_role: str) -> Dict[str, Any]:
        """Test Customer Management APIs (/api/customers/*)"""
        print(f"\n👤 Testing Customer Management APIs ({user_role})...")
        
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        results = {}
        
        if user_role not in ["admin", "technician"]:
            print("   ⚠️  Skipping customer management tests - requires admin/technician role")
            return {"skipped": "Not admin/technician role"}
        
        # Test GET /customers
        print("   📋 Testing GET /api/customers...")
        result = self.make_request("GET", f"{BACKEND_URL}/customers", headers=headers)
        results["list_customers"] = result
        if result["success"]:
            customers = result["data"]
            print(f"      ✅ SUCCESS - Found {len(customers)} customers")
            
            # Test customer-specific endpoints if we have customers
            if customers and len(customers) > 0:
                customer_id = customers[0].get("id")
                
                # Test GET /customers/{customer_id}/devices
                print(f"   📱 Testing GET /api/customers/{customer_id}/devices...")
                result = self.make_request("GET", f"{BACKEND_URL}/customers/{customer_id}/devices", headers=headers)
                results["customer_devices"] = result
                if result["success"]:
                    print(f"      ✅ SUCCESS - Customer devices retrieved")
                else:
                    print(f"      ❌ FAILED - {result['error']}")
                
                # Test GET /customers/{customer_id}/usage
                print(f"   📊 Testing GET /api/customers/{customer_id}/usage...")
                result = self.make_request("GET", f"{BACKEND_URL}/customers/{customer_id}/usage", headers=headers)
                results["customer_usage"] = result
                if result["success"]:
                    print(f"      ✅ SUCCESS - Customer usage retrieved")
                else:
                    print(f"      ❌ FAILED - {result['error']}")
                
                # Test GET /customers/{customer_id}/payments
                print(f"   💳 Testing GET /api/customers/{customer_id}/payments...")
                result = self.make_request("GET", f"{BACKEND_URL}/customers/{customer_id}/payments", headers=headers)
                results["customer_payments"] = result
                if result["success"]:
                    print(f"      ✅ SUCCESS - Customer payments retrieved")
                else:
                    print(f"      ❌ FAILED - {result['error']}")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test POST /customers (create customer) - Admin only
        if user_role == "admin":
            print("   ➕ Testing POST /api/customers...")
            customer_data = {
                "customer_number": f"CUST{int(time.time())}",
                "full_name": "Test Customer",
                "email": f"test_customer_{int(time.time())}@indowater.com",
                "phone": "+6281234567890",
                "address": "Test Address",
                "balance": 100000
            }
            result = self.make_request("POST", f"{BACKEND_URL}/customers", headers=headers, json_data=customer_data)
            results["create_customer"] = result
            if result["success"]:
                print(f"      ✅ SUCCESS - Customer created")
            else:
                print(f"      ❌ FAILED - {result['error']}")
        
        return results

    def test_properties_apis(self, token: str, user_role: str) -> Dict[str, Any]:
        """Test Properties APIs (/api/properties/*)"""
        print(f"\n🏠 Testing Properties APIs ({user_role})...")
        
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        results = {}
        
        # Test GET /properties
        print("   📋 Testing GET /api/properties...")
        result = self.make_request("GET", f"{BACKEND_URL}/properties", headers=headers)
        results["list_properties"] = result
        if result["success"]:
            properties = result["data"]
            print(f"      ✅ SUCCESS - Found {len(properties)} properties")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test CRUD operations for admin/technician
        if user_role in ["admin", "technician"]:
            # Test POST /properties
            print("   ➕ Testing POST /api/properties...")
            property_data = {
                "name": f"Test Property {int(time.time())}",
                "address": "Test Address 123",
                "property_type": "residential",
                "area_size": 100.5,
                "owner_name": "Test Owner",
                "owner_contact": "+6281234567890"
            }
            result = self.make_request("POST", f"{BACKEND_URL}/properties", headers=headers, json_data=property_data)
            results["create_property"] = result
            if result["success"]:
                new_property = result["data"]
                property_id = new_property.get("id")
                print(f"      ✅ SUCCESS - Property created with ID: {property_id}")
                
                # Test GET /properties/{property_id}
                if property_id:
                    print(f"   🔍 Testing GET /api/properties/{property_id}...")
                    result = self.make_request("GET", f"{BACKEND_URL}/properties/{property_id}", headers=headers)
                    results["get_property"] = result
                    if result["success"]:
                        print(f"      ✅ SUCCESS - Property details retrieved")
                    else:
                        print(f"      ❌ FAILED - {result['error']}")
                    
                    # Test PUT /properties/{property_id}
                    print(f"   ✏️ Testing PUT /api/properties/{property_id}...")
                    update_data = {"name": f"Updated Test Property {int(time.time())}"}
                    result = self.make_request("PUT", f"{BACKEND_URL}/properties/{property_id}", headers=headers, json_data=update_data)
                    results["update_property"] = result
                    if result["success"]:
                        print(f"      ✅ SUCCESS - Property updated")
                    else:
                        print(f"      ❌ FAILED - {result['error']}")
                    
                    # Test DELETE /properties/{property_id} (Admin only)
                    if user_role == "admin":
                        print(f"   🗑️ Testing DELETE /api/properties/{property_id}...")
                        result = self.make_request("DELETE", f"{BACKEND_URL}/properties/{property_id}", headers=headers)
                        results["delete_property"] = result
                        if result["success"]:
                            print(f"      ✅ SUCCESS - Property deleted")
                        else:
                            print(f"      ❌ FAILED - {result['error']}")
            else:
                print(f"      ❌ FAILED - {result['error']}")
        
        return results

    def test_device_management_apis(self, token: str, user_role: str) -> Dict[str, Any]:
        """Test Device Management APIs (/api/devices/*)"""
        print(f"\n📱 Testing Device Management APIs ({user_role})...")
        
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        results = {}
        
        # Test GET /devices
        print("   📋 Testing GET /api/devices...")
        result = self.make_request("GET", f"{BACKEND_URL}/devices", headers=headers)
        results["list_devices"] = result
        if result["success"]:
            devices = result["data"]
            print(f"      ✅ SUCCESS - Found {len(devices)} devices")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test GET /devices/comprehensive
        print("   📊 Testing GET /api/devices/comprehensive...")
        result = self.make_request("GET", f"{BACKEND_URL}/devices/comprehensive", headers=headers)
        results["comprehensive_devices"] = result
        if result["success"]:
            print(f"      ✅ SUCCESS - Comprehensive device data retrieved")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test device-specific endpoints if we have devices
        if results["list_devices"]["success"] and results["list_devices"]["data"]:
            devices = results["list_devices"]["data"]
            if len(devices) > 0:
                device_id = devices[0].get("id")
                
                # Test GET /devices/{device_id}/stats
                print(f"   📈 Testing GET /api/devices/{device_id}/stats...")
                result = self.make_request("GET", f"{BACKEND_URL}/devices/{device_id}/stats", headers=headers)
                results["device_stats"] = result
                if result["success"]:
                    print(f"      ✅ SUCCESS - Device statistics retrieved")
                else:
                    print(f"      ❌ FAILED - {result['error']}")
                
                # Test GET /devices/{device_id}/activities
                print(f"   📋 Testing GET /api/devices/{device_id}/activities...")
                result = self.make_request("GET", f"{BACKEND_URL}/devices/{device_id}/activities", headers=headers)
                results["device_activities"] = result
                if result["success"]:
                    print(f"      ✅ SUCCESS - Device activities retrieved")
                else:
                    print(f"      ❌ FAILED - {result['error']}")
        
        # Test batch operations (Admin/Technician only)
        if user_role in ["admin", "technician"]:
            print("   🔄 Testing POST /api/devices/batch...")
            batch_data = {
                "device_ids": ["test-device-1", "test-device-2"],
                "operation": "activate",
                "parameters": {}
            }
            result = self.make_request("POST", f"{BACKEND_URL}/devices/batch", headers=headers, json_data=batch_data)
            results["batch_operations"] = result
            if result["success"]:
                print(f"      ✅ SUCCESS - Batch operation completed")
            else:
                print(f"      ❌ FAILED - {result['error']}")
        
        return results

    def test_iot_monitoring_apis(self, token: str, user_role: str) -> Dict[str, Any]:
        """Test IoT Monitoring APIs (/api/iot/*)"""
        print(f"\n🌐 Testing IoT Monitoring APIs ({user_role})...")
        
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        results = {}
        
        # Test GET /iot/devices
        print("   📋 Testing GET /api/iot/devices...")
        result = self.make_request("GET", f"{BACKEND_URL}/iot/devices", headers=headers)
        results["list_iot_devices"] = result
        if result["success"]:
            print(f"      ✅ SUCCESS - IoT devices retrieved")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test POST /iot/devices/register (Admin/Technician only)
        if user_role in ["admin", "technician"]:
            print("   ➕ Testing POST /api/iot/devices/register...")
            device_data = {
                "device_id": f"ESP32-TEST-{int(time.time())}",
                "device_name": "Test IoT Device",
                "device_type": "water_meter",
                "location": "Test Location",
                "customer_id": "test-customer-1",
                "firmware_version": "1.0.0"
            }
            result = self.make_request("POST", f"{BACKEND_URL}/iot/devices/register", headers=headers, json_data=device_data)
            results["register_iot_device"] = result
            if result["success"]:
                print(f"      ✅ SUCCESS - IoT device registered")
            else:
                print(f"      ❌ FAILED - {result['error']}")
        
        # Test POST /iot/data/reading
        print("   📊 Testing POST /api/iot/data/reading...")
        reading_data = {
            "device_id": "test-device-1",
            "timestamp": datetime.utcnow().isoformat(),
            "water_flow": 15.5,
            "pressure": 2.3,
            "temperature": 25.0,
            "battery_level": 85
        }
        result = self.make_request("POST", f"{BACKEND_URL}/iot/data/reading", headers=headers, json_data=reading_data)
        results["ingest_iot_data"] = result
        if result["success"]:
            print(f"      ✅ SUCCESS - IoT data ingested")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test GET /iot/devices/{device_id}/metrics
        print("   📈 Testing GET /api/iot/devices/test-device-1/metrics...")
        result = self.make_request("GET", f"{BACKEND_URL}/iot/devices/test-device-1/metrics", headers=headers)
        results["device_metrics"] = result
        if result["success"]:
            print(f"      ✅ SUCCESS - Device metrics retrieved")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test POST /iot/devices/{device_id}/command
        print("   🎛️ Testing POST /api/iot/devices/test-device-1/command...")
        command_data = {
            "command": "reset_meter",
            "parameters": {"reason": "maintenance"}
        }
        result = self.make_request("POST", f"{BACKEND_URL}/iot/devices/test-device-1/command", headers=headers, json_data=command_data)
        results["device_command"] = result
        if result["success"]:
            print(f"      ✅ SUCCESS - Device command sent")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        return results

    def test_analytics_apis(self, token: str, user_role: str, customer_id: str = None) -> Dict[str, Any]:
        """Test Analytics APIs (/api/analytics/*)"""
        print(f"\n📊 Testing Analytics APIs ({user_role})...")
        
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        results = {}
        
        # Test GET /analytics/usage
        print("   📈 Testing GET /api/analytics/usage?period=month...")
        result = self.make_request("GET", f"{BACKEND_URL}/analytics/usage?period=month", headers=headers)
        results["usage_analytics"] = result
        if result["success"]:
            data = result["data"]
            print(f"      ✅ SUCCESS - Usage analytics: {data.get('total_consumption', 0)} m³")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test GET /analytics/trends
        print("   📊 Testing GET /api/analytics/trends?period=month...")
        result = self.make_request("GET", f"{BACKEND_URL}/analytics/trends?period=month", headers=headers)
        results["trends_analytics"] = result
        if result["success"]:
            print(f"      ✅ SUCCESS - Trends analytics retrieved")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test GET /analytics/predictions
        print("   🔮 Testing GET /api/analytics/predictions?days_ahead=7...")
        url = f"{BACKEND_URL}/analytics/predictions?days_ahead=7"
        if user_role != "customer" and customer_id:
            url += f"&customer_id={customer_id}"
        result = self.make_request("GET", url, headers=headers)
        results["predictions"] = result
        if result["success"]:
            print(f"      ✅ SUCCESS - Predictions retrieved")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test GET /analytics/comparison
        print("   🔄 Testing GET /api/analytics/comparison...")
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        comparison_url = f"{BACKEND_URL}/analytics/comparison?start_date={start_date.strftime('%Y-%m-%d')}&end_date={end_date.strftime('%Y-%m-%d')}"
        result = self.make_request("GET", comparison_url, headers=headers)
        results["comparison"] = result
        if result["success"]:
            print(f"      ✅ SUCCESS - Comparison analytics retrieved")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test GET /analytics/admin/overview (Admin only)
        if user_role == "admin":
            print("   👑 Testing GET /api/analytics/admin/overview...")
            result = self.make_request("GET", f"{BACKEND_URL}/analytics/admin/overview", headers=headers)
            results["admin_overview"] = result
            if result["success"]:
                data = result["data"]
                print(f"      ✅ SUCCESS - Admin overview: {data.get('total_devices', 0)} devices")
            else:
                print(f"      ❌ FAILED - {result['error']}")
        
        return results

    def test_payment_apis(self, token: str, user_role: str) -> Dict[str, Any]:
        """Test Payment APIs (/api/payments/*)"""
        print(f"\n💳 Testing Payment APIs ({user_role})...")
        
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        results = {}
        
        # Test GET /payments/history/list
        print("   📋 Testing GET /api/payments/history/list...")
        result = self.make_request("GET", f"{BACKEND_URL}/payments/history/list", headers=headers)
        results["payment_history"] = result
        if result["success"]:
            data = result["data"]
            transactions = data.get("transactions", [])
            print(f"      ✅ SUCCESS - Found {len(transactions)} payment transactions")
            
            # Test payment detail if we have transactions
            if transactions and len(transactions) > 0:
                reference_id = transactions[0].get("reference_id")
                if reference_id:
                    print(f"   🔍 Testing GET /api/payments/{reference_id}...")
                    result = self.make_request("GET", f"{BACKEND_URL}/payments/{reference_id}", headers=headers)
                    results["payment_detail"] = result
                    if result["success"]:
                        print(f"      ✅ SUCCESS - Payment detail retrieved")
                    else:
                        print(f"      ❌ FAILED - {result['error']}")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test payment history with filters
        print("   🔍 Testing GET /api/payments/history/list?status=paid...")
        result = self.make_request("GET", f"{BACKEND_URL}/payments/history/list?status=paid", headers=headers)
        results["payment_history_filtered"] = result
        if result["success"]:
            print(f"      ✅ SUCCESS - Filtered payment history retrieved")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        return results

    def test_voucher_apis(self, token: str, user_role: str) -> Dict[str, Any]:
        """Test Voucher APIs (/api/vouchers/*)"""
        print(f"\n🎫 Testing Voucher APIs ({user_role})...")
        
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        results = {}
        
        # Test GET /vouchers
        print("   📋 Testing GET /api/vouchers...")
        result = self.make_request("GET", f"{BACKEND_URL}/vouchers", headers=headers)
        results["list_vouchers"] = result
        if result["success"]:
            vouchers = result["data"]
            print(f"      ✅ SUCCESS - Found {len(vouchers)} vouchers")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test GET /vouchers/active
        print("   ✅ Testing GET /api/vouchers/active...")
        result = self.make_request("GET", f"{BACKEND_URL}/vouchers/active", headers=headers)
        results["active_vouchers"] = result
        if result["success"]:
            print(f"      ✅ SUCCESS - Active vouchers retrieved")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test POST /vouchers/validate
        print("   🔍 Testing POST /api/vouchers/validate...")
        validate_data = {
            "voucher_code": "WELCOME50",
            "purchase_amount": 200000
        }
        result = self.make_request("POST", f"{BACKEND_URL}/vouchers/validate", headers=headers, json_data=validate_data)
        results["validate_voucher"] = result
        if result["success"]:
            print(f"      ✅ SUCCESS - Voucher validation completed")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test POST /vouchers/apply
        print("   ✅ Testing POST /api/vouchers/apply...")
        apply_data = {
            "voucher_code": "WELCOME50",
            "purchase_amount": 200000,
            "transaction_id": f"TXN{int(time.time())}"
        }
        result = self.make_request("POST", f"{BACKEND_URL}/vouchers/apply", headers=headers, json_data=apply_data)
        results["apply_voucher"] = result
        if result["success"]:
            print(f"      ✅ SUCCESS - Voucher applied successfully")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test voucher creation (Admin only)
        if user_role == "admin":
            print("   ➕ Testing POST /api/vouchers...")
            voucher_data = {
                "code": f"TEST{int(time.time())}",
                "name": "Test Voucher",
                "description": "Test voucher for API testing",
                "discount_type": "percentage",
                "discount_value": 25.0,
                "min_purchase_amount": 100000,
                "max_discount_amount": 150000,
                "usage_limit": 50,
                "per_customer_limit": 1,
                "valid_from": datetime.utcnow().isoformat(),
                "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "is_active": True
            }
            result = self.make_request("POST", f"{BACKEND_URL}/vouchers", headers=headers, json_data=voucher_data)
            results["create_voucher"] = result
            if result["success"]:
                print(f"      ✅ SUCCESS - Voucher created")
            else:
                print(f"      ❌ FAILED - {result['error']}")
        
        # Test GET /vouchers/usage-history
        print("   📊 Testing GET /api/vouchers/usage-history...")
        result = self.make_request("GET", f"{BACKEND_URL}/vouchers/usage-history", headers=headers)
        results["voucher_usage_history"] = result
        if result["success"]:
            print(f"      ✅ SUCCESS - Voucher usage history retrieved")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        return results

    def test_support_tickets_apis(self, token: str, user_role: str) -> Dict[str, Any]:
        """Test Support Tickets APIs (/api/tickets/*)"""
        print(f"\n🎫 Testing Support Tickets APIs ({user_role})...")
        
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        results = {}
        
        # Test GET /tickets/
        print("   📋 Testing GET /api/tickets/...")
        result = self.make_request("GET", f"{BACKEND_URL}/tickets/", headers=headers)
        results["list_tickets"] = result
        if result["success"]:
            data = result["data"]
            tickets = data.get("tickets", [])
            print(f"      ✅ SUCCESS - Found {len(tickets)} support tickets")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test POST /tickets/ (create ticket)
        print("   ➕ Testing POST /api/tickets/...")
        ticket_data = {
            "subject": f"Test Ticket {int(time.time())}",
            "description": "This is a test support ticket created via API testing",
            "category": "technical_issue",
            "priority": "medium"
        }
        result = self.make_request("POST", f"{BACKEND_URL}/tickets/", headers=headers, json_data=ticket_data)
        results["create_ticket"] = result
        if result["success"]:
            new_ticket = result["data"]
            ticket_id = new_ticket.get("id")
            print(f"      ✅ SUCCESS - Ticket created with ID: {ticket_id}")
            
            # Test GET /tickets/{ticket_id}
            if ticket_id:
                print(f"   🔍 Testing GET /api/tickets/{ticket_id}...")
                result = self.make_request("GET", f"{BACKEND_URL}/tickets/{ticket_id}", headers=headers)
                results["get_ticket"] = result
                if result["success"]:
                    print(f"      ✅ SUCCESS - Ticket details retrieved")
                else:
                    print(f"      ❌ FAILED - {result['error']}")
                
                # Test POST /tickets/{ticket_id}/messages
                print(f"   💬 Testing POST /api/tickets/{ticket_id}/messages...")
                message_data = {
                    "message": "This is a test message for the support ticket",
                    "is_internal": False
                }
                result = self.make_request("POST", f"{BACKEND_URL}/tickets/{ticket_id}/messages", headers=headers, json_data=message_data)
                results["add_message"] = result
                if result["success"]:
                    print(f"      ✅ SUCCESS - Message added to ticket")
                else:
                    print(f"      ❌ FAILED - {result['error']}")
                
                # Test PATCH /tickets/{ticket_id}/status (Admin/Technician only)
                if user_role in ["admin", "technician"]:
                    print(f"   🔄 Testing PATCH /api/tickets/{ticket_id}/status...")
                    status_data = {
                        "status": "in_progress",
                        "notes": "Ticket status updated via API testing"
                    }
                    result = self.make_request("PATCH", f"{BACKEND_URL}/tickets/{ticket_id}/status", headers=headers, json_data=status_data)
                    results["update_status"] = result
                    if result["success"]:
                        print(f"      ✅ SUCCESS - Ticket status updated")
                    else:
                        print(f"      ❌ FAILED - {result['error']}")
                    
                    # Test PATCH /tickets/{ticket_id}/assign
                    print(f"   👤 Testing PATCH /api/tickets/{ticket_id}/assign...")
                    assign_data = {
                        "technician_id": "technician-user-id",
                        "notes": "Ticket assigned via API testing"
                    }
                    result = self.make_request("PATCH", f"{BACKEND_URL}/tickets/{ticket_id}/assign", headers=headers, json_data=assign_data)
                    results["assign_ticket"] = result
                    if result["success"]:
                        print(f"      ✅ SUCCESS - Ticket assigned")
                    else:
                        print(f"      ❌ FAILED - {result['error']}")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test GET /tickets/admin/stats (Admin only)
        if user_role == "admin":
            print("   📊 Testing GET /api/tickets/admin/stats...")
            result = self.make_request("GET", f"{BACKEND_URL}/tickets/admin/stats", headers=headers)
            results["admin_stats"] = result
            if result["success"]:
                print(f"      ✅ SUCCESS - Admin ticket statistics retrieved")
            else:
                print(f"      ❌ FAILED - {result['error']}")
        
        return results

    def test_water_conservation_tips_apis(self, token: str, user_role: str) -> Dict[str, Any]:
        """Test Water Conservation Tips APIs (/api/tips/*)"""
        print(f"\n💡 Testing Water Conservation Tips APIs ({user_role})...")
        
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        results = {}
        
        # Test GET /tips/
        print("   📋 Testing GET /api/tips/...")
        result = self.make_request("GET", f"{BACKEND_URL}/tips/", headers=headers)
        results["list_tips"] = result
        if result["success"]:
            data = result["data"]
            tips = data.get("tips", [])
            print(f"      ✅ SUCCESS - Found {len(tips)} water conservation tips")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test GET /tips/ with category filter
        print("   🔍 Testing GET /api/tips/?category=general_savings...")
        result = self.make_request("GET", f"{BACKEND_URL}/tips/?category=general_savings", headers=headers)
        results["filter_tips"] = result
        if result["success"]:
            print(f"      ✅ SUCCESS - Filtered tips retrieved")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test GET /tips/personalized
        print("   🎯 Testing GET /api/tips/personalized...")
        result = self.make_request("GET", f"{BACKEND_URL}/tips/personalized", headers=headers)
        results["personalized_tips"] = result
        if result["success"]:
            print(f"      ✅ SUCCESS - Personalized tips retrieved")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test admin endpoints (Admin only)
        if user_role == "admin":
            # Test POST /tips/admin/create
            print("   ➕ Testing POST /api/tips/admin/create...")
            tip_data = {
                "title": f"Test Water Tip {int(time.time())}",
                "description": "This is a test water conservation tip created via API testing",
                "category": "general_savings",
                "difficulty_level": "medium",
                "potential_savings_percentage": 20.0,
                "implementation_time": "2 hours",
                "implementation_steps": [
                    "Step 1: Identify water usage areas",
                    "Step 2: Install water-saving devices",
                    "Step 3: Monitor usage reduction"
                ],
                "benefits": [
                    "Reduces water consumption",
                    "Lowers water bills"
                ],
                "required_tools": [
                    "Water meter",
                    "Basic tools"
                ],
                "status": "active"
            }
            result = self.make_request("POST", f"{BACKEND_URL}/tips/admin/create", headers=headers, json_data=tip_data)
            results["create_tip"] = result
            if result["success"]:
                new_tip = result["data"]
                tip_id = new_tip.get("id")
                print(f"      ✅ SUCCESS - Tip created with ID: {tip_id}")
                
                # Test GET /tips/{tip_id}
                if tip_id:
                    print(f"   🔍 Testing GET /api/tips/{tip_id}...")
                    result = self.make_request("GET", f"{BACKEND_URL}/tips/{tip_id}", headers=headers)
                    results["get_tip"] = result
                    if result["success"]:
                        print(f"      ✅ SUCCESS - Tip details retrieved")
                    else:
                        print(f"      ❌ FAILED - {result['error']}")
                    
                    # Test PUT /tips/admin/{tip_id}
                    print(f"   ✏️ Testing PUT /api/tips/admin/{tip_id}...")
                    update_data = {
                        "title": f"Updated Test Water Tip {int(time.time())}",
                        "potential_savings_percentage": 25.0
                    }
                    result = self.make_request("PUT", f"{BACKEND_URL}/tips/admin/{tip_id}", headers=headers, json_data=update_data)
                    results["update_tip"] = result
                    if result["success"]:
                        print(f"      ✅ SUCCESS - Tip updated")
                    else:
                        print(f"      ❌ FAILED - {result['error']}")
                    
                    # Test DELETE /tips/admin/{tip_id}
                    print(f"   🗑️ Testing DELETE /api/tips/admin/{tip_id}...")
                    result = self.make_request("DELETE", f"{BACKEND_URL}/tips/admin/{tip_id}", headers=headers)
                    results["delete_tip"] = result
                    if result["success"]:
                        print(f"      ✅ SUCCESS - Tip deleted")
                    else:
                        print(f"      ❌ FAILED - {result['error']}")
            else:
                print(f"      ❌ FAILED - {result['error']}")
        
        return results

    def test_alert_notification_apis(self, token: str, user_role: str) -> Dict[str, Any]:
        """Test Alert & Notification APIs (/api/alerts/*)"""
        print(f"\n🚨 Testing Alert & Notification APIs ({user_role})...")
        
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        results = {}
        
        # Test GET /alerts/
        print("   📋 Testing GET /api/alerts/...")
        result = self.make_request("GET", f"{BACKEND_URL}/alerts/", headers=headers)
        results["get_alerts"] = result
        if result["success"]:
            alerts = result["data"]
            print(f"      ✅ SUCCESS - Found {len(alerts)} alerts")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test GET /alerts/unread-count
        print("   🔢 Testing GET /api/alerts/unread-count...")
        result = self.make_request("GET", f"{BACKEND_URL}/alerts/unread-count", headers=headers)
        results["unread_count"] = result
        if result["success"]:
            count_data = result["data"]
            unread_count = count_data.get("unread_count", 0)
            print(f"      ✅ SUCCESS - Unread count: {unread_count}")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test POST /alerts/mark-all-read
        print("   ✅ Testing POST /api/alerts/mark-all-read...")
        result = self.make_request("POST", f"{BACKEND_URL}/alerts/mark-all-read", headers=headers)
        results["mark_all_read"] = result
        if result["success"]:
            print(f"      ✅ SUCCESS - Alerts marked as read")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test GET /alerts/preferences
        print("   ⚙️ Testing GET /api/alerts/preferences...")
        result = self.make_request("GET", f"{BACKEND_URL}/alerts/preferences", headers=headers)
        results["alert_preferences"] = result
        if result["success"]:
            print(f"      ✅ SUCCESS - Alert preferences retrieved")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test PUT /alerts/preferences
        print("   ⚙️ Testing PUT /api/alerts/preferences...")
        prefs_data = {
            "low_balance_threshold": 50000,
            "high_usage_threshold": 100.0,
            "leak_detection_enabled": True,
            "email_notifications": True,
            "sms_notifications": False,
            "push_notifications": True
        }
        result = self.make_request("PUT", f"{BACKEND_URL}/alerts/preferences", headers=headers, json_data=prefs_data)
        results["update_preferences"] = result
        if result["success"]:
            print(f"      ✅ SUCCESS - Alert preferences updated")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test GET /alerts/leaks
        print("   💧 Testing GET /api/alerts/leaks...")
        result = self.make_request("GET", f"{BACKEND_URL}/alerts/leaks", headers=headers)
        results["leak_events"] = result
        if result["success"]:
            leaks = result["data"]
            print(f"      ✅ SUCCESS - Found {len(leaks)} leak events")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test GET /alerts/tampering
        print("   🔧 Testing GET /api/alerts/tampering...")
        result = self.make_request("GET", f"{BACKEND_URL}/alerts/tampering", headers=headers)
        results["tampering_events"] = result
        if result["success"]:
            tampering = result["data"]
            print(f"      ✅ SUCCESS - Found {len(tampering)} tampering events")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test GET /alerts/tips
        print("   💡 Testing GET /api/alerts/tips...")
        result = self.make_request("GET", f"{BACKEND_URL}/alerts/tips", headers=headers)
        results["water_saving_tips"] = result
        if result["success"]:
            tips = result["data"]
            print(f"      ✅ SUCCESS - Found {len(tips)} water saving tips")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        return results

    def test_report_generation_apis(self, token: str, user_role: str, customer_id: str = None) -> Dict[str, Any]:
        """Test Report Generation APIs (/api/reports/*)"""
        print(f"\n📄 Testing Report Generation APIs ({user_role})...")
        
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        results = {}
        
        # Prepare report request data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        report_data = {
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "report_type": "usage_summary",
            "include_charts": True
        }
        
        # Add customer_id for admin users
        if user_role == "admin" and customer_id:
            report_data["customer_id"] = customer_id
        
        # Test POST /reports/export-pdf
        print("   📋 Testing POST /api/reports/export-pdf...")
        result = self.make_request("POST", f"{BACKEND_URL}/reports/export-pdf", headers=headers, json_data=report_data, timeout=30)
        results["pdf_report"] = result
        if result["success"]:
            content_type = result["headers"].get('content-type', '')
            content_length = result["data"].get('content_length', 0)
            if 'application/pdf' in content_type and content_length > 1000:
                print(f"      ✅ SUCCESS - PDF generated, size: {content_length:,} bytes")
            else:
                print(f"      ⚠️  PDF response received but may be invalid - Type: {content_type}, Size: {content_length}")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test POST /reports/export-excel
        print("   📊 Testing POST /api/reports/export-excel...")
        result = self.make_request("POST", f"{BACKEND_URL}/reports/export-excel", headers=headers, json_data=report_data, timeout=30)
        results["excel_report"] = result
        if result["success"]:
            content_type = result["headers"].get('content-type', '')
            content_length = result["data"].get('content_length', 0)
            if 'spreadsheet' in content_type and content_length > 1000:
                print(f"      ✅ SUCCESS - Excel generated, size: {content_length:,} bytes")
            else:
                print(f"      ⚠️  Excel response received but may be invalid - Type: {content_type}, Size: {content_length}")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        return results

    def test_admin_management_apis(self, token: str, user_role: str) -> Dict[str, Any]:
        """Test Admin Management APIs (/api/admin/*)"""
        print(f"\n👑 Testing Admin Management APIs ({user_role})...")
        
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        results = {}
        
        if user_role not in ["admin", "technician"]:
            print("   ⚠️  Skipping admin management tests - requires admin/technician role")
            return {"skipped": "Not admin/technician role"}
        
        # Test GET /admin/dashboard/metrics
        print("   📊 Testing GET /api/admin/dashboard/metrics...")
        result = self.make_request("GET", f"{BACKEND_URL}/admin/dashboard/metrics", headers=headers)
        results["dashboard_metrics"] = result
        if result["success"]:
            metrics = result["data"]
            print(f"      ✅ SUCCESS - Admin dashboard metrics retrieved")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test GET /admin/devices/monitoring
        print("   📱 Testing GET /api/admin/devices/monitoring...")
        result = self.make_request("GET", f"{BACKEND_URL}/admin/devices/monitoring", headers=headers)
        results["device_monitoring"] = result
        if result["success"]:
            print(f"      ✅ SUCCESS - Device monitoring data retrieved")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test POST /admin/customers/bulk
        print("   🔄 Testing POST /api/admin/customers/bulk...")
        bulk_data = {
            "customer_ids": ["test-customer-1", "test-customer-2"],
            "operation": "send_notification",
            "parameters": {
                "message": "Test bulk notification from API testing",
                "type": "info"
            }
        }
        result = self.make_request("POST", f"{BACKEND_URL}/admin/customers/bulk", headers=headers, json_data=bulk_data)
        results["bulk_operations"] = result
        if result["success"]:
            print(f"      ✅ SUCCESS - Bulk customer operation completed")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test GET /admin/maintenance
        print("   🔧 Testing GET /api/admin/maintenance...")
        result = self.make_request("GET", f"{BACKEND_URL}/admin/maintenance", headers=headers)
        results["maintenance_list"] = result
        if result["success"]:
            maintenance = result["data"]
            print(f"      ✅ SUCCESS - Maintenance schedules retrieved")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test POST /admin/maintenance
        print("   ➕ Testing POST /admin/maintenance...")
        maintenance_data = {
            "device_id": "test-device-1",
            "technician_id": "test-technician-1",
            "scheduled_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "maintenance_type": "routine_check",
            "description": "Routine maintenance check via API testing",
            "estimated_duration": 120
        }
        result = self.make_request("POST", f"{BACKEND_URL}/admin/maintenance", headers=headers, json_data=maintenance_data)
        results["create_maintenance"] = result
        if result["success"]:
            print(f"      ✅ SUCCESS - Maintenance schedule created")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test GET /admin/revenue/report
        print("   💰 Testing GET /api/admin/revenue/report...")
        result = self.make_request("GET", f"{BACKEND_URL}/admin/revenue/report", headers=headers)
        results["revenue_report"] = result
        if result["success"]:
            revenue = result["data"]
            print(f"      ✅ SUCCESS - Revenue report retrieved")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        return results

    def test_role_permission_apis(self, token: str, user_role: str) -> Dict[str, Any]:
        """Test Role & Permission APIs (/api/roles/*)"""
        print(f"\n🔐 Testing Role & Permission APIs ({user_role})...")
        
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        results = {}
        
        # Test GET /roles/list
        print("   📋 Testing GET /api/roles/list...")
        result = self.make_request("GET", f"{BACKEND_URL}/roles/list", headers=headers)
        results["list_roles"] = result
        if result["success"]:
            roles = result["data"]
            print(f"      ✅ SUCCESS - Found {len(roles)} roles")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Test GET /roles/permissions
        print("   🔑 Testing GET /api/roles/permissions...")
        result = self.make_request("GET", f"{BACKEND_URL}/roles/permissions", headers=headers)
        results["list_permissions"] = result
        if result["success"]:
            permissions = result["data"]
            print(f"      ✅ SUCCESS - Found {len(permissions)} permissions")
        else:
            print(f"      ❌ FAILED - {result['error']}")
        
        # Admin-only endpoints
        if user_role == "admin":
            # Test POST /roles/create
            print("   ➕ Testing POST /api/roles/create...")
            role_data = {
                "name": f"test_role_{int(time.time())}",
                "display_name": "Test Role",
                "description": "Test role created via API testing",
                "permissions": ["users.view", "customers.view"]
            }
            result = self.make_request("POST", f"{BACKEND_URL}/roles/create", headers=headers, json_data=role_data)
            results["create_role"] = result
            if result["success"]:
                new_role = result["data"]
                role_id = new_role.get("id")
                print(f"      ✅ SUCCESS - Role created with ID: {role_id}")
                
                # Test PUT /roles/{role_id}
                if role_id:
                    print(f"   ✏️ Testing PUT /api/roles/{role_id}...")
                    update_data = {
                        "display_name": "Updated Test Role",
                        "permissions": ["users.view", "customers.view", "devices.view"]
                    }
                    result = self.make_request("PUT", f"{BACKEND_URL}/roles/{role_id}", headers=headers, json_data=update_data)
                    results["update_role"] = result
                    if result["success"]:
                        print(f"      ✅ SUCCESS - Role updated")
                    else:
                        print(f"      ❌ FAILED - {result['error']}")
                    
                    # Test DELETE /roles/{role_id}
                    print(f"   🗑️ Testing DELETE /api/roles/{role_id}...")
                    result = self.make_request("DELETE", f"{BACKEND_URL}/roles/{role_id}", headers=headers)
                    results["delete_role"] = result
                    if result["success"]:
                        print(f"      ✅ SUCCESS - Role deleted")
                    else:
                        print(f"      ❌ FAILED - {result['error']}")
            else:
                print(f"      ❌ FAILED - {result['error']}")
            
            # Test POST /roles/assign
            print("   👤 Testing POST /api/roles/assign...")
            assign_data = {
                "user_id": "test-user-id",
                "role_name": "customer"
            }
            result = self.make_request("POST", f"{BACKEND_URL}/roles/assign", headers=headers, json_data=assign_data)
            results["assign_role"] = result
            if result["success"]:
                print(f"      ✅ SUCCESS - Role assigned to user")
            else:
                print(f"      ❌ FAILED - {result['error']}")
        
        return results

    def run_comprehensive_tests(self):
        """Run comprehensive backend API tests for all modules"""
        print("🚀 STARTING COMPREHENSIVE INDOWATER BACKEND API TESTING")
        print("=" * 80)
        print("Testing ALL 16 API modules across all user roles...")
        print("=" * 80)
        
        # Test each account
        for account in DEMO_ACCOUNTS:
            print(f"\n{'=' * 20} TESTING {account['name'].upper()} ACCOUNT {'=' * 20}")
            
            # Test login
            login_result = self.test_login(
                account["email"], 
                account["password"], 
                account["expected_role"],
                account["name"]
            )
            
            if not login_result["success"]:
                print(f"❌ {account['name']} login failed: {login_result['error']}")
                self.all_results[account["name"]] = {"login": login_result}
                continue
            
            token = login_result["token"]
            user_role = account["expected_role"]
            user = login_result["user"]
            customer_id = user.get("id")
            
            # Store results for this account
            account_results = {
                "login": login_result,
                "authentication": self.test_authentication_apis(token, user_role),
                "dashboard": self.test_dashboard_apis(token, user_role),
                "user_management": self.test_user_management_apis(token, user_role),
                "customer_management": self.test_customer_management_apis(token, user_role),
                "properties": self.test_properties_apis(token, user_role),
                "device_management": self.test_device_management_apis(token, user_role),
                "iot_monitoring": self.test_iot_monitoring_apis(token, user_role),
                "analytics": self.test_analytics_apis(token, user_role, customer_id),
                "payments": self.test_payment_apis(token, user_role),
                "vouchers": self.test_voucher_apis(token, user_role),
                "support_tickets": self.test_support_tickets_apis(token, user_role),
                "water_tips": self.test_water_conservation_tips_apis(token, user_role),
                "alerts": self.test_alert_notification_apis(token, user_role),
                "reports": self.test_report_generation_apis(token, user_role, customer_id),
                "admin_management": self.test_admin_management_apis(token, user_role),
                "roles_permissions": self.test_role_permission_apis(token, user_role)
            }
            
            self.all_results[account["name"]] = account_results
        
        # Print comprehensive summary
        self.print_comprehensive_summary()
        
        return self.all_results

    def print_comprehensive_summary(self):
        """Print detailed test summary with all failures"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE BACKEND API TEST RESULTS")
        print("=" * 80)
        
        # Collect all failed tests
        failed_tests = []
        
        for account_name, account_results in self.all_results.items():
            for api_name, api_results in account_results.items():
                if isinstance(api_results, dict):
                    for test_name, test_result in api_results.items():
                        if isinstance(test_result, dict) and not test_result.get("success", False):
                            if test_name != "skipped":
                                error = test_result.get("error", "Unknown error")
                                status_code = test_result.get("status_code", "N/A")
                                failed_tests.append({
                                    "account": account_name,
                                    "api": api_name,
                                    "test": test_name,
                                    "error": error,
                                    "status_code": status_code
                                })
        
        # Print summary statistics
        print(f"\n📈 OVERALL RESULTS:")
        print(f"   Total Tests Performed: {self.total_tests}")
        print(f"   ✅ Passed: {self.passed_tests} ({self.passed_tests/self.total_tests*100:.1f}%)")
        print(f"   ❌ Failed: {self.failed_tests} ({self.failed_tests/self.total_tests*100:.1f}%)")
        
        # Print detailed failures
        if failed_tests:
            print(f"\n❌ DETAILED FAILURE REPORT ({len(failed_tests)} failures):")
            print("-" * 80)
            
            # Group failures by API module
            failures_by_api = {}
            for failure in failed_tests:
                api_key = f"{failure['api']}"
                if api_key not in failures_by_api:
                    failures_by_api[api_key] = []
                failures_by_api[api_key].append(failure)
            
            for api_name, failures in failures_by_api.items():
                print(f"\n🔴 {api_name.upper()} API FAILURES ({len(failures)} failures):")
                for failure in failures:
                    print(f"   • {failure['account']} - {failure['test']}: {failure['error']} (HTTP {failure['status_code']})")
        
        # Print success summary
        if self.failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED! Backend APIs are working correctly.")
        else:
            print(f"\n⚠️  {self.failed_tests} tests failed. See detailed report above.")
            
            # Identify critical issues
            critical_apis = ["authentication", "dashboard", "user_management"]
            critical_failures = [f for f in failed_tests if f['api'] in critical_apis]
            if critical_failures:
                print(f"\n🚨 CRITICAL ISSUES FOUND ({len(critical_failures)} critical failures):")
                for failure in critical_failures:
                    print(f"   🔥 {failure['api']}.{failure['test']}: {failure['error']}")

def main():
    """Main function to run comprehensive backend API testing"""
    try:
        tester = APITester()
        results = tester.run_comprehensive_tests()
        
        # Save results to file
        with open("/app/comprehensive_full_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Test results saved to: /app/comprehensive_full_test_results.json")
        
        # Return exit code based on test results
        if tester.failed_tests > 0:
            sys.exit(1)
        else:
            sys.exit(0)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()