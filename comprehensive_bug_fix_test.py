#!/usr/bin/env python3
"""
Comprehensive Backend API Testing - Post Bug Fix Verification
Tests all 6 critical bugs that have been fixed plus other critical endpoints
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

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
            
            # Validate response structure
            required_fields = ["access_token", "token_type", "user"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return {
                    "success": False,
                    "error": f"Missing required fields: {missing_fields}",
                    "response": data
                }
            
            user = data.get("user", {})
            actual_role = user.get("role")
            
            if actual_role != expected_role:
                return {
                    "success": False,
                    "error": f"Role mismatch. Expected: {expected_role}, Got: {actual_role}",
                    "response": data
                }
            
            token = data.get("access_token")
            print(f"   ✅ SUCCESS - Role: {actual_role}, Active: {user.get('is_active')}")
            
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

def test_profile_update_api(token: str, user_role: str, user_id: str) -> Dict[str, Any]:
    """Test Profile Update API (Bug #1 - FIXED)"""
    print(f"\n👤 Testing Profile Update API (Bug #1) - {user_role}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "update_full_name": {"success": False, "error": None, "data": None},
        "update_phone": {"success": False, "error": None, "data": None},
        "update_password": {"success": False, "error": None, "data": None}
    }
    
    try:
        # Test 1: Update full name
        print("   📝 Testing PUT /api/auth/profile (full_name)...")
        update_data = {
            "full_name": f"Updated {user_role.title()} User {int(time.time())}"
        }
        
        response = requests.put(
            f"{BACKEND_URL}/auth/profile",
            json=update_data,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            updated_user = response.json()
            if updated_user.get("full_name") == update_data["full_name"]:
                print(f"      ✅ SUCCESS - Full name updated to: {updated_user.get('full_name')}")
                results["update_full_name"] = {"success": True, "data": updated_user}
            else:
                error_msg = "Full name not updated correctly"
                print(f"      ❌ {error_msg}")
                results["update_full_name"] = {"success": False, "error": error_msg}
        else:
            error_msg = f"Profile update failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                pass
            print(f"      ❌ {error_msg}")
            results["update_full_name"] = {"success": False, "error": error_msg}
        
        # Test 2: Update phone
        print("   📞 Testing PUT /api/auth/profile (phone)...")
        update_data = {
            "phone": f"+628{int(time.time()) % 1000000000}"
        }
        
        response = requests.put(
            f"{BACKEND_URL}/auth/profile",
            json=update_data,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            updated_user = response.json()
            if updated_user.get("phone") == update_data["phone"]:
                print(f"      ✅ SUCCESS - Phone updated to: {updated_user.get('phone')}")
                results["update_phone"] = {"success": True, "data": updated_user}
            else:
                error_msg = "Phone not updated correctly"
                print(f"      ❌ {error_msg}")
                results["update_phone"] = {"success": False, "error": error_msg}
        else:
            error_msg = f"Phone update failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["update_phone"] = {"success": False, "error": error_msg}
        
        # Test 3: Update password
        print("   🔒 Testing PUT /api/auth/profile (password)...")
        update_data = {
            "password": f"newpass{int(time.time())}"
        }
        
        response = requests.put(
            f"{BACKEND_URL}/auth/profile",
            json=update_data,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            updated_user = response.json()
            # Password should not be returned in response
            if "password" not in updated_user and "hashed_password" not in updated_user:
                print(f"      ✅ SUCCESS - Password updated (not returned in response)")
                results["update_password"] = {"success": True, "data": {"password_updated": True}}
            else:
                error_msg = "Password returned in response (security issue)"
                print(f"      ❌ {error_msg}")
                results["update_password"] = {"success": False, "error": error_msg}
        else:
            error_msg = f"Password update failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["update_password"] = {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"Profile update API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results

def test_support_ticket_creation(token: str, user_role: str, user_id: str) -> Dict[str, Any]:
    """Test Support Ticket Creation (Bug #3 - FIXED)"""
    print(f"\n🎫 Testing Support Ticket Creation (Bug #3) - {user_role}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "create_ticket": {"success": False, "error": None, "data": None},
        "list_tickets": {"success": False, "error": None, "data": None}
    }
    
    try:
        # Test 1: Create support ticket
        print("   📝 Testing POST /api/tickets/...")
        ticket_data = {
            "subject": f"Test Ticket from {user_role} - {int(time.time())}",
            "description": f"This is a test ticket created by {user_role} user to verify bug fix #3",
            "category": "technical_issue",
            "priority": "medium"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/tickets/",
            json=ticket_data,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200 or response.status_code == 201:
            ticket = response.json()
            ticket_number = ticket.get("ticket_number")
            customer_info = ticket.get("customer")
            
            if ticket_number and customer_info:
                print(f"      ✅ SUCCESS - Ticket created: {ticket_number}")
                print(f"      ✅ Customer info included: {customer_info.get('full_name', 'N/A')}")
                results["create_ticket"] = {"success": True, "data": ticket}
            else:
                error_msg = "Ticket created but missing ticket_number or customer info"
                print(f"      ❌ {error_msg}")
                results["create_ticket"] = {"success": False, "error": error_msg}
        else:
            error_msg = f"Ticket creation failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
                if "Customer not found" in error_msg:
                    error_msg += " (This is the reported bug!)"
            except:
                pass
            print(f"      ❌ {error_msg}")
            results["create_ticket"] = {"success": False, "error": error_msg}
        
        # Test 2: List tickets to verify creation
        print("   📋 Testing GET /api/tickets/...")
        response = requests.get(
            f"{BACKEND_URL}/tickets/",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            tickets_data = response.json()
            tickets = tickets_data.get("tickets", [])
            print(f"      ✅ SUCCESS - Found {len(tickets)} tickets")
            results["list_tickets"] = {"success": True, "data": tickets_data}
        else:
            error_msg = f"List tickets failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["list_tickets"] = {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"Support ticket API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results

def test_report_generation(token: str, user_role: str) -> Dict[str, Any]:
    """Test Report Generation (Bug #5 - FIXED)"""
    print(f"\n📄 Testing Report Generation (Bug #5) - {user_role}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "pdf_report": {"success": False, "error": None, "data": None},
        "excel_report": {"success": False, "error": None, "data": None}
    }
    
    # Prepare report request data for date range 2025-01-01 to 2025-01-30
    report_data = {
        "start_date": "2025-01-01",
        "end_date": "2025-01-30",
        "report_type": "usage_summary",
        "include_charts": True
    }
    
    try:
        # Test 1: PDF Report Generation
        print("   📋 Testing POST /api/reports/export-pdf/...")
        response = requests.post(
            f"{BACKEND_URL}/reports/export-pdf/",
            json=report_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            content_length = len(response.content)
            
            if 'application/pdf' in content_type and content_length > 1000:
                print(f"      ✅ SUCCESS - PDF generated, size: {content_length:,} bytes")
                print(f"      ✅ Content-Type: {content_type}")
                results["pdf_report"] = {"success": True, "data": {"size": content_length, "type": content_type}}
            else:
                error_msg = f"Invalid PDF response - Type: {content_type}, Size: {content_length}"
                print(f"      ❌ {error_msg}")
                results["pdf_report"] = {"success": False, "error": error_msg}
        else:
            error_msg = f"PDF generation failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                pass
            print(f"      ❌ {error_msg}")
            results["pdf_report"] = {"success": False, "error": error_msg}
        
        # Test 2: Excel Report Generation
        print("   📊 Testing POST /api/reports/export-excel/...")
        response = requests.post(
            f"{BACKEND_URL}/reports/export-excel/",
            json=report_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            content_length = len(response.content)
            
            if 'spreadsheet' in content_type and content_length > 1000:
                print(f"      ✅ SUCCESS - Excel generated, size: {content_length:,} bytes")
                print(f"      ✅ Content-Type: {content_type}")
                results["excel_report"] = {"success": True, "data": {"size": content_length, "type": content_type}}
            else:
                error_msg = f"Invalid Excel response - Type: {content_type}, Size: {content_length}"
                print(f"      ❌ {error_msg}")
                results["excel_report"] = {"success": False, "error": error_msg}
        else:
            error_msg = f"Excel generation failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                pass
            print(f"      ❌ {error_msg}")
            results["excel_report"] = {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"Report generation API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results

def test_device_comprehensive(token: str, user_role: str) -> Dict[str, Any]:
    """Test Device Management Comprehensive (Bug #6 - FIXED)"""
    print(f"\n📱 Testing Device Comprehensive (Bug #6) - {user_role}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "comprehensive_all": {"success": False, "error": None, "data": None},
        "comprehensive_filtered": {"success": False, "error": None, "data": None}
    }
    
    try:
        # Test 1: Get comprehensive device data (all)
        print("   📊 Testing GET /api/devices/comprehensive/...")
        response = requests.get(
            f"{BACKEND_URL}/devices/comprehensive/",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            comprehensive_data = response.json()
            devices = comprehensive_data.get("devices", [])
            print(f"      ✅ SUCCESS - Found {len(devices)} devices with comprehensive data")
            
            # Check for health scores and comprehensive data structure
            if devices and len(devices) > 0:
                first_device = devices[0]
                if "health_score" in first_device:
                    print(f"      ✅ Health scores included in response")
                else:
                    print(f"      ⚠️  Health scores not found in device data")
            
            results["comprehensive_all"] = {"success": True, "data": comprehensive_data}
        else:
            error_msg = f"Comprehensive devices failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                pass
            print(f"      ❌ {error_msg}")
            results["comprehensive_all"] = {"success": False, "error": error_msg}
        
        # Test 2: Get comprehensive device data with filters
        print("   🔍 Testing GET /api/devices/comprehensive/?status=active&health=good...")
        response = requests.get(
            f"{BACKEND_URL}/devices/comprehensive/?status=active&health=good",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            filtered_data = response.json()
            devices = filtered_data.get("devices", [])
            print(f"      ✅ SUCCESS - Found {len(devices)} devices with filters applied")
            results["comprehensive_filtered"] = {"success": True, "data": filtered_data}
        else:
            error_msg = f"Filtered comprehensive devices failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["comprehensive_filtered"] = {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"Device comprehensive API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results

def test_voucher_management(token: str, user_role: str) -> Dict[str, Any]:
    """Test Voucher Management (Bug #4 - VERIFIED)"""
    print(f"\n🎟️ Testing Voucher Management (Bug #4) - {user_role}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "list_vouchers": {"success": False, "error": None, "data": None},
        "create_voucher": {"success": False, "error": None, "data": None}
    }
    
    try:
        # Test 1: List vouchers
        print("   📋 Testing GET /api/vouchers/...")
        response = requests.get(
            f"{BACKEND_URL}/vouchers/",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            vouchers = response.json()
            print(f"      ✅ SUCCESS - Found {len(vouchers)} vouchers")
            results["list_vouchers"] = {"success": True, "data": vouchers}
        else:
            error_msg = f"List vouchers failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                pass
            print(f"      ❌ {error_msg}")
            results["list_vouchers"] = {"success": False, "error": error_msg}
        
        # Test 2: Create voucher (admin only)
        if user_role == "admin":
            print("   ➕ Testing POST /api/vouchers/...")
            voucher_data = {
                "code": f"TESTFIX{int(time.time())}",
                "discount_type": "percentage",
                "discount_value": 25.0,
                "min_purchase_amount": 100000,
                "max_discount_amount": 150000,
                "usage_limit": 50,
                "per_customer_limit": 1,
                "valid_from": "2025-01-01T00:00:00Z",
                "valid_until": "2025-12-31T23:59:59Z",
                "is_active": True,
                "description": "Test voucher for bug fix verification"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/vouchers/",
                json=voucher_data,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200 or response.status_code == 201:
                voucher = response.json()
                voucher_id = voucher.get("id")
                voucher_code = voucher.get("code")
                print(f"      ✅ SUCCESS - Voucher created: {voucher_code} (ID: {voucher_id})")
                results["create_voucher"] = {"success": True, "data": voucher}
            else:
                error_msg = f"Create voucher failed: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('detail', '')}"
                except:
                    pass
                print(f"      ❌ {error_msg}")
                results["create_voucher"] = {"success": False, "error": error_msg}
        else:
            print("   ⚠️  Skipping voucher creation - requires admin role")
            results["create_voucher"] = {"success": True, "data": {"skipped": "Not admin"}}
            
    except Exception as e:
        error_msg = f"Voucher management API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results

def test_iot_monitoring(token: str, user_role: str) -> Dict[str, Any]:
    """Test IoT Monitoring APIs (Bug #2 - VERIFIED)"""
    print(f"\n🌐 Testing IoT Monitoring (Bug #2) - {user_role}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "iot_health": {"success": False, "error": None, "data": None}
    }
    
    try:
        # Test IoT Health Check
        print("   💚 Testing GET /api/iot/health...")
        response = requests.get(
            f"{BACKEND_URL}/iot/health",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            health_data = response.json()
            status = health_data.get("status", "unknown")
            print(f"      ✅ SUCCESS - IoT service status: {status}")
            results["iot_health"] = {"success": True, "data": health_data}
        else:
            error_msg = f"IoT health check failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                pass
            print(f"      ❌ {error_msg}")
            results["iot_health"] = {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"IoT monitoring API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        results["iot_health"] = {"success": False, "error": error_msg}
    
    return results

def test_other_critical_endpoints(token: str, user_role: str, user_id: str) -> Dict[str, Any]:
    """Test other critical endpoints"""
    print(f"\n🔧 Testing Other Critical Endpoints - {user_role}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "user_management": {"success": False, "error": None, "data": None},
        "analytics": {"success": False, "error": None, "data": None},
        "payment_history": {"success": False, "error": None, "data": None},
        "water_tips": {"success": False, "error": None, "data": None},
        "alerts": {"success": False, "error": None, "data": None},
        "admin_management": {"success": False, "error": None, "data": None}
    }
    
    try:
        # Test 1: User Management (Admin only)
        if user_role == "admin":
            print("   👥 Testing GET /api/users...")
            response = requests.get(
                f"{BACKEND_URL}/users",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                users = response.json()
                print(f"      ✅ SUCCESS - Found {len(users)} users")
                results["user_management"] = {"success": True, "data": users}
            else:
                error_msg = f"User management failed: {response.status_code}"
                print(f"      ❌ {error_msg}")
                results["user_management"] = {"success": False, "error": error_msg}
        else:
            results["user_management"] = {"success": True, "data": {"skipped": "Not admin"}}
        
        # Test 2: Analytics
        print("   📊 Testing GET /api/analytics/usage?period=month...")
        response = requests.get(
            f"{BACKEND_URL}/analytics/usage?period=month",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            analytics_data = response.json()
            consumption = analytics_data.get("total_consumption", 0)
            print(f"      ✅ SUCCESS - Total consumption: {consumption} m³")
            results["analytics"] = {"success": True, "data": analytics_data}
        else:
            error_msg = f"Analytics failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["analytics"] = {"success": False, "error": error_msg}
        
        # Test 3: Payment History
        print("   💳 Testing GET /api/payments/history/list...")
        response = requests.get(
            f"{BACKEND_URL}/payments/history/list",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            payment_data = response.json()
            transactions = payment_data.get("transactions", [])
            print(f"      ✅ SUCCESS - Found {len(transactions)} payment transactions")
            results["payment_history"] = {"success": True, "data": payment_data}
        else:
            error_msg = f"Payment history failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["payment_history"] = {"success": False, "error": error_msg}
        
        # Test 4: Water Conservation Tips
        print("   💡 Testing GET /api/tips/...")
        response = requests.get(
            f"{BACKEND_URL}/tips/",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            tips_data = response.json()
            tips = tips_data.get("tips", [])
            print(f"      ✅ SUCCESS - Found {len(tips)} water conservation tips")
            results["water_tips"] = {"success": True, "data": tips_data}
        else:
            error_msg = f"Water tips failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["water_tips"] = {"success": False, "error": error_msg}
        
        # Test 5: Alerts & Notifications
        print("   🚨 Testing GET /api/alerts/...")
        response = requests.get(
            f"{BACKEND_URL}/alerts/",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            alerts = response.json()
            print(f"      ✅ SUCCESS - Found {len(alerts)} alerts")
            results["alerts"] = {"success": True, "data": alerts}
        else:
            error_msg = f"Alerts failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["alerts"] = {"success": False, "error": error_msg}
        
        # Test 6: Admin Management (Admin only)
        if user_role == "admin":
            print("   👑 Testing GET /api/admin/dashboard/metrics...")
            response = requests.get(
                f"{BACKEND_URL}/admin/dashboard/metrics",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                admin_data = response.json()
                customers = admin_data.get("total_customers", 0)
                print(f"      ✅ SUCCESS - Total customers: {customers}")
                results["admin_management"] = {"success": True, "data": admin_data}
            else:
                error_msg = f"Admin management failed: {response.status_code}"
                print(f"      ❌ {error_msg}")
                results["admin_management"] = {"success": False, "error": error_msg}
        else:
            results["admin_management"] = {"success": True, "data": {"skipped": "Not admin"}}
            
    except Exception as e:
        error_msg = f"Other endpoints API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results

def main():
    """Main testing function"""
    print("=" * 80)
    print("🚀 COMPREHENSIVE BACKEND API TESTING - POST BUG FIX VERIFICATION")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Testing 6 Critical Bug Fixes + Other Critical Endpoints")
    print("=" * 80)
    
    all_results = {}
    
    # Test all 3 demo accounts
    for account in DEMO_ACCOUNTS:
        account_name = account["name"]
        print(f"\n{'=' * 60}")
        print(f"🧪 TESTING {account_name.upper()} ACCOUNT")
        print(f"{'=' * 60}")
        
        # Step 1: Login
        login_result = test_login(
            account["email"], 
            account["password"], 
            account["expected_role"],
            account_name
        )
        
        if not login_result["success"]:
            print(f"❌ {account_name} login failed: {login_result['error']}")
            all_results[account_name] = {"login": login_result}
            continue
        
        token = login_result["token"]
        user = login_result["user"]
        user_role = user["role"]
        user_id = user["id"]
        
        account_results = {
            "login": login_result
        }
        
        # Step 2: Test the 6 Fixed Bugs
        print(f"\n🔧 TESTING 6 CRITICAL BUG FIXES FOR {account_name}...")
        
        # Bug #1: Profile Update API
        account_results["profile_update"] = test_profile_update_api(token, user_role, user_id)
        
        # Bug #2: IoT Monitoring APIs
        account_results["iot_monitoring"] = test_iot_monitoring(token, user_role)
        
        # Bug #3: Support Ticket Creation
        account_results["support_tickets"] = test_support_ticket_creation(token, user_role, user_id)
        
        # Bug #4: Voucher Management
        account_results["voucher_management"] = test_voucher_management(token, user_role)
        
        # Bug #5: Report Generation
        account_results["report_generation"] = test_report_generation(token, user_role)
        
        # Bug #6: Device Management Comprehensive
        account_results["device_comprehensive"] = test_device_comprehensive(token, user_role)
        
        # Step 3: Test Other Critical Endpoints
        account_results["other_endpoints"] = test_other_critical_endpoints(token, user_role, user_id)
        
        all_results[account_name] = account_results
    
    # Generate Summary Report
    print(f"\n{'=' * 80}")
    print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
    print(f"{'=' * 80}")
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    # Summary for each account
    for account_name, account_results in all_results.items():
        print(f"\n🧪 {account_name.upper()} ACCOUNT RESULTS:")
        
        if "login" not in account_results or not account_results["login"]["success"]:
            print(f"   ❌ LOGIN FAILED - Cannot test other endpoints")
            continue
        
        print(f"   ✅ LOGIN - Success")
        
        # Test the 6 critical bug fixes
        bug_fixes = [
            ("profile_update", "Profile Update API (Bug #1)"),
            ("iot_monitoring", "IoT Monitoring APIs (Bug #2)"),
            ("support_tickets", "Support Ticket Creation (Bug #3)"),
            ("voucher_management", "Voucher Management (Bug #4)"),
            ("report_generation", "Report Generation (Bug #5)"),
            ("device_comprehensive", "Device Comprehensive (Bug #6)")
        ]
        
        for test_key, test_name in bug_fixes:
            if test_key in account_results:
                test_result = account_results[test_key]
                success_count = sum(1 for sub_test in test_result.values() if sub_test.get("success", False))
                total_count = len(test_result)
                
                if success_count == total_count:
                    print(f"   ✅ {test_name} - {success_count}/{total_count} tests passed")
                    passed_tests += total_count
                else:
                    print(f"   ❌ {test_name} - {success_count}/{total_count} tests passed")
                    failed_tests += (total_count - success_count)
                    passed_tests += success_count
                
                total_tests += total_count
        
        # Test other endpoints
        if "other_endpoints" in account_results:
            other_result = account_results["other_endpoints"]
            success_count = sum(1 for sub_test in other_result.values() if sub_test.get("success", False))
            total_count = len(other_result)
            
            if success_count == total_count:
                print(f"   ✅ Other Critical Endpoints - {success_count}/{total_count} tests passed")
            else:
                print(f"   ❌ Other Critical Endpoints - {success_count}/{total_count} tests passed")
            
            passed_tests += success_count
            failed_tests += (total_count - success_count)
            total_tests += total_count
    
    # Overall Summary
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n{'=' * 80}")
    print("🎯 OVERALL TEST RESULTS")
    print(f"{'=' * 80}")
    print(f"Total Tests Performed: {total_tests}")
    print(f"Tests Passed: {passed_tests}")
    print(f"Tests Failed: {failed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 97:
        print(f"🎉 EXCELLENT! Target success rate (97%+) achieved!")
    elif success_rate >= 90:
        print(f"✅ GOOD! Most tests passing, minor issues to address.")
    else:
        print(f"⚠️  NEEDS ATTENTION! Multiple failures detected.")
    
    # Detailed failure report
    if failed_tests > 0:
        print(f"\n{'=' * 80}")
        print("❌ DETAILED FAILURE REPORT")
        print(f"{'=' * 80}")
        
        for account_name, account_results in all_results.items():
            if "login" not in account_results or not account_results["login"]["success"]:
                print(f"\n{account_name} - LOGIN FAILURE:")
                print(f"   Error: {account_results.get('login', {}).get('error', 'Unknown error')}")
                continue
            
            account_failures = []
            
            for test_category, test_results in account_results.items():
                if test_category == "login":
                    continue
                
                for sub_test, result in test_results.items():
                    if not result.get("success", False) and result.get("error"):
                        account_failures.append(f"   {test_category}.{sub_test}: {result['error']}")
            
            if account_failures:
                print(f"\n{account_name} FAILURES:")
                for failure in account_failures:
                    print(failure)
    
    print(f"\n{'=' * 80}")
    print("✅ COMPREHENSIVE BACKEND API TESTING COMPLETE")
    print(f"{'=' * 80}")
    
    return success_rate >= 97

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)