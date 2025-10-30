#!/usr/bin/env python3
"""
Comprehensive Backend API Bug Testing Script for IndoWater Solution
Tests ALL endpoints to find 404, 500, and 422 errors as requested in review
Focus: IoT Monitoring, Support Tickets, Vouchers, Device Management, Reports, and ALL other endpoints
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# Backend URL from environment
BACKEND_URL = "https://comprehensive-fix-1.preview.emergentagent.com/api"

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

def test_login(email: str, password: str, expected_role: str, account_name: str) -> Dict[str, Any]:
    """Test login for a specific account"""
    print(f"\n🔐 Testing {account_name} Login...")
    print(f"   Email: {email}")
    
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            user = data.get("user", {})
            token = data.get("access_token")
            
            print(f"   ✅ SUCCESS - Role: {user.get('role')}, Active: {user.get('is_active')}")
            print(f"   Token: {token[:20]}...")
            
            return {
                "success": True,
                "data": data,
                "token": token,
                "user": user
            }
        else:
            error_msg = "Unknown error"
            try:
                error_data = response.json()
                error_msg = error_data.get("detail", str(error_data))
            except:
                error_msg = response.text or f"HTTP {response.status_code}"
            
            print(f"   ❌ FAILED - {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "status_code": response.status_code
            }
            
    except Exception as e:
        print(f"   ❌ ERROR - {str(e)}")
        return {
            "success": False,
            "error": f"Error: {str(e)}"
        }

def test_profile_update_api(token: str, user_role: str) -> Dict[str, Any]:
    """Test Profile Update API - Previously reported bug"""
    print(f"\n👤 Testing Profile Update API ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test profile update with basic data
    update_data = {
        "full_name": f"Updated {user_role.title()} User",
        "phone": "+6281234567890"
    }
    
    try:
        print("   ✏️ Testing PUT /api/auth/profile...")
        response = requests.put(
            f"{BACKEND_URL}/auth/profile",
            json=update_data,
            headers=headers,
            timeout=15
        )
        
        print(f"      Status Code: {response.status_code}")
        
        if response.status_code == 200:
            updated_user = response.json()
            print(f"      ✅ SUCCESS - Profile updated successfully")
            return {"success": True, "data": updated_user}
        else:
            error_msg = f"Profile update failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                pass
            print(f"      ❌ FAILED - {error_msg}")
            return {"success": False, "error": error_msg, "status_code": response.status_code}
            
    except Exception as e:
        error_msg = f"Profile update error: {str(e)}"
        print(f"      ❌ ERROR - {error_msg}")
        return {"success": False, "error": error_msg}

def test_iot_monitoring_apis(token: str, user_role: str) -> Dict[str, Any]:
    """Test IoT Monitoring APIs - Reported 404 errors"""
    print(f"\n🌐 Testing IoT Monitoring APIs ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "list_iot_devices": {"success": False, "error": None, "status_code": None},
        "register_iot_device": {"success": False, "error": None, "status_code": None},
        "ingest_iot_data": {"success": False, "error": None, "status_code": None},
        "device_metrics": {"success": False, "error": None, "status_code": None},
        "device_status": {"success": False, "error": None, "status_code": None},
        "device_commands": {"success": False, "error": None, "status_code": None}
    }
    
    try:
        # Test 1: List IoT Devices
        print("   📋 Testing GET /api/iot/devices...")
        response = requests.get(
            f"{BACKEND_URL}/iot/devices",
            headers=headers,
            timeout=15
        )
        
        print(f"      Status Code: {response.status_code}")
        results["list_iot_devices"]["status_code"] = response.status_code
        
        if response.status_code == 200:
            iot_devices = response.json()
            print(f"      ✅ SUCCESS - Found {len(iot_devices)} IoT devices")
            results["list_iot_devices"] = {"success": True, "data": iot_devices, "status_code": 200}
        else:
            error_msg = f"List IoT devices failed: {response.status_code}"
            print(f"      ❌ FAILED - {error_msg}")
            results["list_iot_devices"] = {"success": False, "error": error_msg, "status_code": response.status_code}
        
        # Test 2: Register IoT Device
        print("   ➕ Testing POST /api/iot/devices...")
        device_data = {
            "device_id": f"ESP32-TEST-{int(time.time())}",
            "device_name": "Test IoT Device",
            "device_type": "water_meter",
            "location": "Test Location",
            "customer_id": "test-customer-1"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/iot/devices",
            json=device_data,
            headers=headers,
            timeout=15
        )
        
        print(f"      Status Code: {response.status_code}")
        results["register_iot_device"]["status_code"] = response.status_code
        
        if response.status_code == 201:
            new_device = response.json()
            device_id = new_device.get("device_id")
            print(f"      ✅ SUCCESS - IoT device registered: {device_id}")
            results["register_iot_device"] = {"success": True, "data": new_device, "status_code": 201}
        else:
            error_msg = f"Register IoT device failed: {response.status_code}"
            print(f"      ❌ FAILED - {error_msg}")
            results["register_iot_device"] = {"success": False, "error": error_msg, "status_code": response.status_code}
        
        # Test 3: Ingest IoT Data
        print("   📊 Testing POST /api/iot/data...")
        iot_data = {
            "device_id": "test-device-1",
            "timestamp": "2025-01-27T10:00:00Z",
            "water_flow": 15.5,
            "pressure": 2.3,
            "temperature": 25.0,
            "battery_level": 85
        }
        
        response = requests.post(
            f"{BACKEND_URL}/iot/data",
            json=iot_data,
            headers=headers,
            timeout=15
        )
        
        print(f"      Status Code: {response.status_code}")
        results["ingest_iot_data"]["status_code"] = response.status_code
        
        if response.status_code == 200:
            ingest_result = response.json()
            print(f"      ✅ SUCCESS - IoT data ingested")
            results["ingest_iot_data"] = {"success": True, "data": ingest_result, "status_code": 200}
        else:
            error_msg = f"IoT data ingest failed: {response.status_code}"
            print(f"      ❌ FAILED - {error_msg}")
            results["ingest_iot_data"] = {"success": False, "error": error_msg, "status_code": response.status_code}
        
        # Test 4: Device Metrics
        print("   📈 Testing GET /api/iot/devices/test-device-1/metrics...")
        response = requests.get(
            f"{BACKEND_URL}/iot/devices/test-device-1/metrics",
            headers=headers,
            timeout=15
        )
        
        print(f"      Status Code: {response.status_code}")
        results["device_metrics"]["status_code"] = response.status_code
        
        if response.status_code == 200:
            metrics = response.json()
            print(f"      ✅ SUCCESS - Device metrics retrieved")
            results["device_metrics"] = {"success": True, "data": metrics, "status_code": 200}
        else:
            error_msg = f"Device metrics failed: {response.status_code}"
            print(f"      ❌ FAILED - {error_msg}")
            results["device_metrics"] = {"success": False, "error": error_msg, "status_code": response.status_code}
        
        # Test 5: Device Status
        print("   🔍 Testing GET /api/iot/devices/test-device-1/status...")
        response = requests.get(
            f"{BACKEND_URL}/iot/devices/test-device-1/status",
            headers=headers,
            timeout=15
        )
        
        print(f"      Status Code: {response.status_code}")
        results["device_status"]["status_code"] = response.status_code
        
        if response.status_code == 200:
            status = response.json()
            print(f"      ✅ SUCCESS - Device status retrieved")
            results["device_status"] = {"success": True, "data": status, "status_code": 200}
        else:
            error_msg = f"Device status failed: {response.status_code}"
            print(f"      ❌ FAILED - {error_msg}")
            results["device_status"] = {"success": False, "error": error_msg, "status_code": response.status_code}
        
        # Test 6: Device Commands
        print("   🎛️ Testing POST /api/iot/devices/test-device-1/commands...")
        command_data = {
            "command": "restart",
            "parameters": {}
        }
        
        response = requests.post(
            f"{BACKEND_URL}/iot/devices/test-device-1/commands",
            json=command_data,
            headers=headers,
            timeout=15
        )
        
        print(f"      Status Code: {response.status_code}")
        results["device_commands"]["status_code"] = response.status_code
        
        if response.status_code == 200:
            command_result = response.json()
            print(f"      ✅ SUCCESS - Device command sent")
            results["device_commands"] = {"success": True, "data": command_result, "status_code": 200}
        else:
            error_msg = f"Device commands failed: {response.status_code}"
            print(f"      ❌ FAILED - {error_msg}")
            results["device_commands"] = {"success": False, "error": error_msg, "status_code": response.status_code}
            
    except Exception as e:
        error_msg = f"IoT monitoring API error: {str(e)}"
        print(f"   ❌ ERROR - {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results

def test_support_ticket_apis(token: str, user_role: str) -> Dict[str, Any]:
    """Test Support Ticket APIs - Reported Customer not found bug"""
    print(f"\n🎫 Testing Support Ticket APIs ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "list_tickets": {"success": False, "error": None, "status_code": None},
        "create_ticket": {"success": False, "error": None, "status_code": None},
        "get_ticket": {"success": False, "error": None, "status_code": None},
        "update_ticket": {"success": False, "error": None, "status_code": None},
        "admin_stats": {"success": False, "error": None, "status_code": None}
    }
    
    try:
        # Test 1: List Tickets
        print("   📋 Testing GET /api/tickets/...")
        response = requests.get(
            f"{BACKEND_URL}/tickets/",
            headers=headers,
            timeout=15
        )
        
        print(f"      Status Code: {response.status_code}")
        results["list_tickets"]["status_code"] = response.status_code
        
        if response.status_code == 200:
            tickets_data = response.json()
            tickets = tickets_data.get("tickets", [])
            print(f"      ✅ SUCCESS - Found {len(tickets)} tickets")
            results["list_tickets"] = {"success": True, "data": tickets_data, "status_code": 200}
        else:
            error_msg = f"List tickets failed: {response.status_code}"
            print(f"      ❌ FAILED - {error_msg}")
            results["list_tickets"] = {"success": False, "error": error_msg, "status_code": response.status_code}
        
        # Test 2: Create Ticket - This is the reported bug
        print("   ➕ Testing POST /api/tickets/...")
        ticket_data = {
            "subject": f"Test Ticket {int(time.time())}",
            "description": "This is a test ticket to verify the API functionality",
            "category": "technical_issue",
            "priority": "medium"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/tickets/",
            json=ticket_data,
            headers=headers,
            timeout=15
        )
        
        print(f"      Status Code: {response.status_code}")
        results["create_ticket"]["status_code"] = response.status_code
        
        if response.status_code == 201:
            new_ticket = response.json()
            ticket_id = new_ticket.get("id")
            print(f"      ✅ SUCCESS - Ticket created: {ticket_id}")
            results["create_ticket"] = {"success": True, "data": new_ticket, "status_code": 201}
            
            # Test 3: Get Ticket Detail
            if ticket_id:
                print(f"   🔍 Testing GET /api/tickets/{ticket_id}...")
                response = requests.get(
                    f"{BACKEND_URL}/tickets/{ticket_id}",
                    headers=headers,
                    timeout=15
                )
                
                print(f"      Status Code: {response.status_code}")
                results["get_ticket"]["status_code"] = response.status_code
                
                if response.status_code == 200:
                    ticket_detail = response.json()
                    print(f"      ✅ SUCCESS - Ticket detail retrieved")
                    results["get_ticket"] = {"success": True, "data": ticket_detail, "status_code": 200}
                else:
                    error_msg = f"Get ticket failed: {response.status_code}"
                    print(f"      ❌ FAILED - {error_msg}")
                    results["get_ticket"] = {"success": False, "error": error_msg, "status_code": response.status_code}
                
                # Test 4: Update Ticket
                print(f"   ✏️ Testing PUT /api/tickets/{ticket_id}...")
                update_data = {
                    "status": "in_progress",
                    "notes": "Updated via API test"
                }
                
                response = requests.put(
                    f"{BACKEND_URL}/tickets/{ticket_id}",
                    json=update_data,
                    headers=headers,
                    timeout=15
                )
                
                print(f"      Status Code: {response.status_code}")
                results["update_ticket"]["status_code"] = response.status_code
                
                if response.status_code == 200:
                    updated_ticket = response.json()
                    print(f"      ✅ SUCCESS - Ticket updated")
                    results["update_ticket"] = {"success": True, "data": updated_ticket, "status_code": 200}
                else:
                    error_msg = f"Update ticket failed: {response.status_code}"
                    print(f"      ❌ FAILED - {error_msg}")
                    results["update_ticket"] = {"success": False, "error": error_msg, "status_code": response.status_code}
        else:
            error_msg = f"Create ticket failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                pass
            print(f"      ❌ FAILED - {error_msg}")
            results["create_ticket"] = {"success": False, "error": error_msg, "status_code": response.status_code}
        
        # Test 5: Admin Stats
        print("   📊 Testing GET /api/tickets/admin/stats...")
        response = requests.get(
            f"{BACKEND_URL}/tickets/admin/stats",
            headers=headers,
            timeout=15
        )
        
        print(f"      Status Code: {response.status_code}")
        results["admin_stats"]["status_code"] = response.status_code
        
        if response.status_code == 200:
            stats = response.json()
            print(f"      ✅ SUCCESS - Admin stats retrieved")
            results["admin_stats"] = {"success": True, "data": stats, "status_code": 200}
        else:
            error_msg = f"Admin stats failed: {response.status_code}"
            print(f"      ❌ FAILED - {error_msg}")
            results["admin_stats"] = {"success": False, "error": error_msg, "status_code": response.status_code}
            
    except Exception as e:
        error_msg = f"Support ticket API error: {str(e)}"
        print(f"   ❌ ERROR - {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results

def test_voucher_apis(token: str, user_role: str) -> Dict[str, Any]:
    """Test Voucher APIs - Reported 404 errors"""
    print(f"\n🎟️ Testing Voucher APIs ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "list_vouchers": {"success": False, "error": None, "status_code": None},
        "create_voucher": {"success": False, "error": None, "status_code": None},
        "validate_voucher": {"success": False, "error": None, "status_code": None},
        "apply_voucher": {"success": False, "error": None, "status_code": None},
        "active_vouchers": {"success": False, "error": None, "status_code": None}
    }
    
    try:
        # Test 1: List Vouchers
        print("   📋 Testing GET /api/vouchers...")
        response = requests.get(
            f"{BACKEND_URL}/vouchers",
            headers=headers,
            timeout=15
        )
        
        print(f"      Status Code: {response.status_code}")
        results["list_vouchers"]["status_code"] = response.status_code
        
        if response.status_code == 200:
            vouchers = response.json()
            print(f"      ✅ SUCCESS - Found {len(vouchers)} vouchers")
            results["list_vouchers"] = {"success": True, "data": vouchers, "status_code": 200}
        else:
            error_msg = f"List vouchers failed: {response.status_code}"
            print(f"      ❌ FAILED - {error_msg}")
            results["list_vouchers"] = {"success": False, "error": error_msg, "status_code": response.status_code}
        
        # Test 2: Create Voucher (Admin only)
        if user_role == "admin":
            print("   ➕ Testing POST /api/vouchers...")
            voucher_data = {
                "code": f"TEST{int(time.time())}",
                "description": "Test voucher for API testing",
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
            
            response = requests.post(
                f"{BACKEND_URL}/vouchers",
                json=voucher_data,
                headers=headers,
                timeout=15
            )
            
            print(f"      Status Code: {response.status_code}")
            results["create_voucher"]["status_code"] = response.status_code
            
            if response.status_code == 201:
                new_voucher = response.json()
                print(f"      ✅ SUCCESS - Voucher created: {new_voucher.get('code')}")
                results["create_voucher"] = {"success": True, "data": new_voucher, "status_code": 201}
            else:
                error_msg = f"Create voucher failed: {response.status_code}"
                print(f"      ❌ FAILED - {error_msg}")
                results["create_voucher"] = {"success": False, "error": error_msg, "status_code": response.status_code}
        else:
            results["create_voucher"] = {"success": True, "data": {"skipped": "Not admin"}, "status_code": None}
        
        # Test 3: Validate Voucher
        print("   ✅ Testing POST /api/vouchers/validate...")
        validate_data = {
            "voucher_code": "WELCOME50",
            "purchase_amount": 100000
        }
        
        response = requests.post(
            f"{BACKEND_URL}/vouchers/validate",
            json=validate_data,
            headers=headers,
            timeout=15
        )
        
        print(f"      Status Code: {response.status_code}")
        results["validate_voucher"]["status_code"] = response.status_code
        
        if response.status_code == 200:
            validation_result = response.json()
            print(f"      ✅ SUCCESS - Voucher validation completed")
            results["validate_voucher"] = {"success": True, "data": validation_result, "status_code": 200}
        else:
            error_msg = f"Validate voucher failed: {response.status_code}"
            print(f"      ❌ FAILED - {error_msg}")
            results["validate_voucher"] = {"success": False, "error": error_msg, "status_code": response.status_code}
        
        # Test 4: Apply Voucher
        print("   🎯 Testing POST /api/vouchers/apply...")
        apply_data = {
            "voucher_code": "WELCOME50",
            "purchase_amount": 100000,
            "transaction_id": f"TXN{int(time.time())}"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/vouchers/apply",
            json=apply_data,
            headers=headers,
            timeout=15
        )
        
        print(f"      Status Code: {response.status_code}")
        results["apply_voucher"]["status_code"] = response.status_code
        
        if response.status_code == 200:
            apply_result = response.json()
            print(f"      ✅ SUCCESS - Voucher applied")
            results["apply_voucher"] = {"success": True, "data": apply_result, "status_code": 200}
        else:
            error_msg = f"Apply voucher failed: {response.status_code}"
            print(f"      ❌ FAILED - {error_msg}")
            results["apply_voucher"] = {"success": False, "error": error_msg, "status_code": response.status_code}
        
        # Test 5: Active Vouchers
        print("   🔍 Testing GET /api/vouchers/active...")
        response = requests.get(
            f"{BACKEND_URL}/vouchers/active",
            headers=headers,
            timeout=15
        )
        
        print(f"      Status Code: {response.status_code}")
        results["active_vouchers"]["status_code"] = response.status_code
        
        if response.status_code == 200:
            active_vouchers = response.json()
            print(f"      ✅ SUCCESS - Found {len(active_vouchers)} active vouchers")
            results["active_vouchers"] = {"success": True, "data": active_vouchers, "status_code": 200}
        else:
            error_msg = f"Active vouchers failed: {response.status_code}"
            print(f"      ❌ FAILED - {error_msg}")
            results["active_vouchers"] = {"success": False, "error": error_msg, "status_code": response.status_code}
            
    except Exception as e:
        error_msg = f"Voucher API error: {str(e)}"
        print(f"   ❌ ERROR - {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results

def test_report_generation_apis(token: str, user_role: str) -> Dict[str, Any]:
    """Test Report Generation APIs - Reported 404 errors"""
    print(f"\n📄 Testing Report Generation APIs ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "export_pdf": {"success": False, "error": None, "status_code": None},
        "export_excel": {"success": False, "error": None, "status_code": None}
    }
    
    # Prepare report request data
    from datetime import datetime, timedelta
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    report_data = {
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "report_type": "usage_summary",
        "include_charts": True
    }
    
    try:
        # Test 1: PDF Report Generation
        print("   📋 Testing POST /api/reports/export-pdf...")
        response = requests.post(
            f"{BACKEND_URL}/reports/export-pdf",
            json=report_data,
            headers=headers,
            timeout=30
        )
        
        print(f"      Status Code: {response.status_code}")
        results["export_pdf"]["status_code"] = response.status_code
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            content_length = len(response.content)
            print(f"      ✅ SUCCESS - PDF generated, size: {content_length:,} bytes")
            results["export_pdf"] = {"success": True, "data": {"size": content_length, "type": content_type}, "status_code": 200}
        else:
            error_msg = f"PDF generation failed: {response.status_code}"
            print(f"      ❌ FAILED - {error_msg}")
            results["export_pdf"] = {"success": False, "error": error_msg, "status_code": response.status_code}
        
        # Test 2: Excel Report Generation
        print("   📊 Testing POST /api/reports/export-excel...")
        response = requests.post(
            f"{BACKEND_URL}/reports/export-excel",
            json=report_data,
            headers=headers,
            timeout=30
        )
        
        print(f"      Status Code: {response.status_code}")
        results["export_excel"]["status_code"] = response.status_code
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            content_length = len(response.content)
            print(f"      ✅ SUCCESS - Excel generated, size: {content_length:,} bytes")
            results["export_excel"] = {"success": True, "data": {"size": content_length, "type": content_type}, "status_code": 200}
        else:
            error_msg = f"Excel generation failed: {response.status_code}"
            print(f"      ❌ FAILED - {error_msg}")
            results["export_excel"] = {"success": False, "error": error_msg, "status_code": response.status_code}
            
    except Exception as e:
        error_msg = f"Report generation API error: {str(e)}"
        print(f"   ❌ ERROR - {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results

def test_device_management_apis(token: str, user_role: str) -> Dict[str, Any]:
    """Test Device Management APIs"""
    print(f"\n📱 Testing Device Management APIs ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "list_devices": {"success": False, "error": None, "status_code": None},
        "comprehensive_devices": {"success": False, "error": None, "status_code": None},
        "create_device": {"success": False, "error": None, "status_code": None},
        "device_stats": {"success": False, "error": None, "status_code": None},
        "batch_operations": {"success": False, "error": None, "status_code": None}
    }
    
    try:
        # Test 1: List Devices
        print("   📋 Testing GET /api/devices...")
        response = requests.get(
            f"{BACKEND_URL}/devices",
            headers=headers,
            timeout=15
        )
        
        print(f"      Status Code: {response.status_code}")
        results["list_devices"]["status_code"] = response.status_code
        
        if response.status_code == 200:
            devices = response.json()
            print(f"      ✅ SUCCESS - Found {len(devices)} devices")
            results["list_devices"] = {"success": True, "data": devices, "status_code": 200}
        else:
            error_msg = f"List devices failed: {response.status_code}"
            print(f"      ❌ FAILED - {error_msg}")
            results["list_devices"] = {"success": False, "error": error_msg, "status_code": response.status_code}
        
        # Test 2: Comprehensive Device Listing - Reported missing
        print("   📊 Testing GET /api/devices/comprehensive...")
        response = requests.get(
            f"{BACKEND_URL}/devices/comprehensive",
            headers=headers,
            timeout=15
        )
        
        print(f"      Status Code: {response.status_code}")
        results["comprehensive_devices"]["status_code"] = response.status_code
        
        if response.status_code == 200:
            comprehensive_devices = response.json()
            print(f"      ✅ SUCCESS - Comprehensive device data retrieved")
            results["comprehensive_devices"] = {"success": True, "data": comprehensive_devices, "status_code": 200}
        else:
            error_msg = f"Comprehensive devices failed: {response.status_code}"
            print(f"      ❌ FAILED - {error_msg}")
            results["comprehensive_devices"] = {"success": False, "error": error_msg, "status_code": response.status_code}
        
        # Test 3: Create Device (Admin/Technician only)
        if user_role in ["admin", "technician"]:
            print("   ➕ Testing POST /api/devices...")
            device_data = {
                "device_id": f"DEV-TEST-{int(time.time())}",
                "device_name": "Test Device",
                "device_type": "water_meter",
                "customer_id": "test-customer-1",
                "property_id": "test-property-1",
                "installation_date": "2025-01-27T10:00:00Z",
                "status": "active"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/devices",
                json=device_data,
                headers=headers,
                timeout=15
            )
            
            print(f"      Status Code: {response.status_code}")
            results["create_device"]["status_code"] = response.status_code
            
            if response.status_code == 201:
                new_device = response.json()
                print(f"      ✅ SUCCESS - Device created")
                results["create_device"] = {"success": True, "data": new_device, "status_code": 201}
            else:
                error_msg = f"Create device failed: {response.status_code}"
                print(f"      ❌ FAILED - {error_msg}")
                results["create_device"] = {"success": False, "error": error_msg, "status_code": response.status_code}
        else:
            results["create_device"] = {"success": True, "data": {"skipped": "Not admin/technician"}, "status_code": None}
        
        # Test 4: Device Statistics
        print("   📈 Testing GET /api/devices/test-device-1/stats...")
        response = requests.get(
            f"{BACKEND_URL}/devices/test-device-1/stats",
            headers=headers,
            timeout=15
        )
        
        print(f"      Status Code: {response.status_code}")
        results["device_stats"]["status_code"] = response.status_code
        
        if response.status_code == 200:
            device_stats = response.json()
            print(f"      ✅ SUCCESS - Device statistics retrieved")
            results["device_stats"] = {"success": True, "data": device_stats, "status_code": 200}
        else:
            error_msg = f"Device stats failed: {response.status_code}"
            print(f"      ❌ FAILED - {error_msg}")
            results["device_stats"] = {"success": False, "error": error_msg, "status_code": response.status_code}
        
        # Test 5: Batch Operations
        if user_role in ["admin", "technician"]:
            print("   🔄 Testing POST /api/devices/batch...")
            batch_data = {
                "device_ids": ["test-device-1", "test-device-2"],
                "operation": "activate",
                "parameters": {}
            }
            
            response = requests.post(
                f"{BACKEND_URL}/devices/batch",
                json=batch_data,
                headers=headers,
                timeout=15
            )
            
            print(f"      Status Code: {response.status_code}")
            results["batch_operations"]["status_code"] = response.status_code
            
            if response.status_code == 200:
                batch_result = response.json()
                print(f"      ✅ SUCCESS - Batch operation completed")
                results["batch_operations"] = {"success": True, "data": batch_result, "status_code": 200}
            else:
                error_msg = f"Batch operations failed: {response.status_code}"
                print(f"      ❌ FAILED - {error_msg}")
                results["batch_operations"] = {"success": False, "error": error_msg, "status_code": response.status_code}
        else:
            results["batch_operations"] = {"success": True, "data": {"skipped": "Not admin/technician"}, "status_code": None}
            
    except Exception as e:
        error_msg = f"Device management API error: {str(e)}"
        print(f"   ❌ ERROR - {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results

def test_additional_endpoints(token: str, user_role: str) -> Dict[str, Any]:
    """Test additional endpoints across all modules"""
    print(f"\n🔍 Testing Additional Endpoints ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "analytics_usage": {"success": False, "error": None, "status_code": None},
        "analytics_trends": {"success": False, "error": None, "status_code": None},
        "alert_preferences": {"success": False, "error": None, "status_code": None},
        "conservation_tips": {"success": False, "error": None, "status_code": None},
        "customer_management": {"success": False, "error": None, "status_code": None},
        "admin_dashboard": {"success": False, "error": None, "status_code": None}
    }
    
    try:
        # Test Analytics Usage
        print("   📊 Testing GET /api/analytics/usage...")
        response = requests.get(
            f"{BACKEND_URL}/analytics/usage?period=month",
            headers=headers,
            timeout=15
        )
        
        print(f"      Status Code: {response.status_code}")
        results["analytics_usage"]["status_code"] = response.status_code
        
        if response.status_code == 200:
            usage_data = response.json()
            print(f"      ✅ SUCCESS - Analytics usage data retrieved")
            results["analytics_usage"] = {"success": True, "data": usage_data, "status_code": 200}
        else:
            error_msg = f"Analytics usage failed: {response.status_code}"
            print(f"      ❌ FAILED - {error_msg}")
            results["analytics_usage"] = {"success": False, "error": error_msg, "status_code": response.status_code}
        
        # Test Analytics Trends
        print("   📈 Testing GET /api/analytics/trends...")
        response = requests.get(
            f"{BACKEND_URL}/analytics/trends?period=month",
            headers=headers,
            timeout=15
        )
        
        print(f"      Status Code: {response.status_code}")
        results["analytics_trends"]["status_code"] = response.status_code
        
        if response.status_code == 200:
            trends_data = response.json()
            print(f"      ✅ SUCCESS - Analytics trends data retrieved")
            results["analytics_trends"] = {"success": True, "data": trends_data, "status_code": 200}
        else:
            error_msg = f"Analytics trends failed: {response.status_code}"
            print(f"      ❌ FAILED - {error_msg}")
            results["analytics_trends"] = {"success": False, "error": error_msg, "status_code": response.status_code}
        
        # Test Alert Preferences
        print("   🚨 Testing GET /api/alerts/preferences...")
        response = requests.get(
            f"{BACKEND_URL}/alerts/preferences",
            headers=headers,
            timeout=15
        )
        
        print(f"      Status Code: {response.status_code}")
        results["alert_preferences"]["status_code"] = response.status_code
        
        if response.status_code == 200:
            prefs_data = response.json()
            print(f"      ✅ SUCCESS - Alert preferences retrieved")
            results["alert_preferences"] = {"success": True, "data": prefs_data, "status_code": 200}
        else:
            error_msg = f"Alert preferences failed: {response.status_code}"
            print(f"      ❌ FAILED - {error_msg}")
            results["alert_preferences"] = {"success": False, "error": error_msg, "status_code": response.status_code}
        
        # Test Conservation Tips
        print("   💡 Testing GET /api/tips/...")
        response = requests.get(
            f"{BACKEND_URL}/tips/",
            headers=headers,
            timeout=15
        )
        
        print(f"      Status Code: {response.status_code}")
        results["conservation_tips"]["status_code"] = response.status_code
        
        if response.status_code == 200:
            tips_data = response.json()
            print(f"      ✅ SUCCESS - Conservation tips retrieved")
            results["conservation_tips"] = {"success": True, "data": tips_data, "status_code": 200}
        else:
            error_msg = f"Conservation tips failed: {response.status_code}"
            print(f"      ❌ FAILED - {error_msg}")
            results["conservation_tips"] = {"success": False, "error": error_msg, "status_code": response.status_code}
        
        # Test Customer Management
        if user_role in ["admin", "technician"]:
            print("   👤 Testing GET /api/customers...")
            response = requests.get(
                f"{BACKEND_URL}/customers",
                headers=headers,
                timeout=15
            )
            
            print(f"      Status Code: {response.status_code}")
            results["customer_management"]["status_code"] = response.status_code
            
            if response.status_code == 200:
                customers_data = response.json()
                print(f"      ✅ SUCCESS - Customer management data retrieved")
                results["customer_management"] = {"success": True, "data": customers_data, "status_code": 200}
            else:
                error_msg = f"Customer management failed: {response.status_code}"
                print(f"      ❌ FAILED - {error_msg}")
                results["customer_management"] = {"success": False, "error": error_msg, "status_code": response.status_code}
        else:
            results["customer_management"] = {"success": True, "data": {"skipped": "Not admin/technician"}, "status_code": None}
        
        # Test Admin Dashboard
        if user_role == "admin":
            print("   👑 Testing GET /api/admin/dashboard/metrics...")
            response = requests.get(
                f"{BACKEND_URL}/admin/dashboard/metrics",
                headers=headers,
                timeout=15
            )
            
            print(f"      Status Code: {response.status_code}")
            results["admin_dashboard"]["status_code"] = response.status_code
            
            if response.status_code == 200:
                dashboard_data = response.json()
                print(f"      ✅ SUCCESS - Admin dashboard data retrieved")
                results["admin_dashboard"] = {"success": True, "data": dashboard_data, "status_code": 200}
            else:
                error_msg = f"Admin dashboard failed: {response.status_code}"
                print(f"      ❌ FAILED - {error_msg}")
                results["admin_dashboard"] = {"success": False, "error": error_msg, "status_code": response.status_code}
        else:
            results["admin_dashboard"] = {"success": True, "data": {"skipped": "Not admin"}, "status_code": None}
            
    except Exception as e:
        error_msg = f"Additional endpoints API error: {str(e)}"
        print(f"   ❌ ERROR - {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results

def main():
    """Main testing function"""
    print("=" * 80)
    print("🔍 COMPREHENSIVE BACKEND API BUG TESTING")
    print("=" * 80)
    print("Testing ALL endpoints to find 404, 500, and 422 errors")
    print("Focus: IoT Monitoring, Support Tickets, Vouchers, Device Management, Reports")
    print("=" * 80)
    
    all_results = {}
    
    # Test each account
    for account in DEMO_ACCOUNTS:
        print(f"\n{'='*60}")
        print(f"🧪 TESTING WITH {account['name'].upper()} ACCOUNT")
        print(f"{'='*60}")
        
        # Login
        login_result = test_login(
            account["email"], 
            account["password"], 
            account["expected_role"],
            account["name"]
        )
        
        if not login_result["success"]:
            print(f"❌ Login failed for {account['name']}, skipping tests")
            all_results[account["name"]] = {"login": login_result}
            continue
        
        token = login_result["token"]
        user_role = account["expected_role"]
        user = login_result["user"]
        
        # Store results for this account
        account_results = {
            "login": login_result,
            "profile_update": test_profile_update_api(token, user_role),
            "iot_monitoring": test_iot_monitoring_apis(token, user_role),
            "support_tickets": test_support_ticket_apis(token, user_role),
            "vouchers": test_voucher_apis(token, user_role),
            "reports": test_report_generation_apis(token, user_role),
            "device_management": test_device_management_apis(token, user_role),
            "additional_endpoints": test_additional_endpoints(token, user_role)
        }
        
        all_results[account["name"]] = account_results
    
    # Generate comprehensive bug report
    print(f"\n{'='*80}")
    print("🐛 COMPREHENSIVE BUG REPORT")
    print(f"{'='*80}")
    
    critical_bugs = []
    routing_issues = []
    validation_issues = []
    implementation_bugs = []
    
    for account_name, account_results in all_results.items():
        if "login" not in account_results or not account_results["login"]["success"]:
            continue
            
        user_role = account_results["login"]["user"]["role"]
        
        for test_category, test_results in account_results.items():
            if test_category == "login":
                continue
                
            if isinstance(test_results, dict):
                for test_name, test_result in test_results.items():
                    if isinstance(test_result, dict) and not test_result.get("success", True):
                        status_code = test_result.get("status_code")
                        error = test_result.get("error", "Unknown error")
                        
                        bug_info = {
                            "endpoint": f"{test_category}/{test_name}",
                            "method": "GET/POST/PUT",
                            "status_code": status_code,
                            "error": error,
                            "user_role": user_role,
                            "account": account_name
                        }
                        
                        if status_code == 404:
                            routing_issues.append(bug_info)
                        elif status_code == 500:
                            implementation_bugs.append(bug_info)
                        elif status_code == 422:
                            validation_issues.append(bug_info)
                        else:
                            critical_bugs.append(bug_info)
    
    # Print bug summary
    print(f"\n📊 BUG SUMMARY:")
    print(f"   🔴 404 Routing Issues: {len(routing_issues)}")
    print(f"   🔴 500 Implementation Bugs: {len(implementation_bugs)}")
    print(f"   🔴 422 Validation Issues: {len(validation_issues)}")
    print(f"   🔴 Other Critical Bugs: {len(critical_bugs)}")
    
    # Detailed bug reports
    if routing_issues:
        print(f"\n🔴 404 ROUTING ISSUES ({len(routing_issues)}):")
        for i, bug in enumerate(routing_issues, 1):
            print(f"   {i}. {bug['endpoint']} - {bug['user_role']} - {bug['error']}")
    
    if implementation_bugs:
        print(f"\n🔴 500 IMPLEMENTATION BUGS ({len(implementation_bugs)}):")
        for i, bug in enumerate(implementation_bugs, 1):
            print(f"   {i}. {bug['endpoint']} - {bug['user_role']} - {bug['error']}")
    
    if validation_issues:
        print(f"\n🔴 422 VALIDATION ISSUES ({len(validation_issues)}):")
        for i, bug in enumerate(validation_issues, 1):
            print(f"   {i}. {bug['endpoint']} - {bug['user_role']} - {bug['error']}")
    
    if critical_bugs:
        print(f"\n🔴 OTHER CRITICAL BUGS ({len(critical_bugs)}):")
        for i, bug in enumerate(critical_bugs, 1):
            print(f"   {i}. {bug['endpoint']} - {bug['user_role']} - {bug['error']}")
    
    total_bugs = len(routing_issues) + len(implementation_bugs) + len(validation_issues) + len(critical_bugs)
    
    print(f"\n{'='*80}")
    print(f"🎯 TESTING COMPLETE - TOTAL BUGS FOUND: {total_bugs}")
    print(f"{'='*80}")
    
    if total_bugs == 0:
        print("✅ NO CRITICAL BUGS FOUND - ALL ENDPOINTS WORKING!")
    else:
        print("❌ BUGS FOUND - REQUIRES SYSTEMATIC FIXING")
    
    return all_results

if __name__ == "__main__":
    main()