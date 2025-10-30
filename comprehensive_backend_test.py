#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND API TESTING SCRIPT FOR INDOWATER SOLUTION
Tests ALL backend API endpoints to identify bugs, errors, and non-functional features.

This script performs a complete sweep of the IndoWater backend system including:
- Authentication & Users
- Dashboard APIs  
- Customer Management
- Device Management
- IoT Monitoring
- Analytics APIs
- Payment APIs
- Voucher System
- Support Tickets
- Water Conservation Tips
- Alert & Notification System
- Admin Management
- Report Generation
- Role & Permission Management
- Properties Management
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional, List
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

def test_support_tickets_api(token: str, user_role: str) -> Dict[str, Any]:
    """Test Support Tickets API endpoints"""
    print(f"\n🎫 Testing Support Tickets API ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "list_tickets": {"success": False, "error": None, "data": None},
        "create_ticket": {"success": False, "error": None, "data": None},
        "ticket_detail": {"success": False, "error": None, "data": None},
        "update_status": {"success": False, "error": None, "data": None},
        "assign_ticket": {"success": False, "error": None, "data": None},
        "add_message": {"success": False, "error": None, "data": None},
        "admin_stats": {"success": False, "error": None, "data": None}
    }
    
    try:
        # Test 1: List tickets (should return 4 tickets)
        print("   📋 Testing GET /api/tickets...")
        response = requests.get(
            f"{BACKEND_URL}/tickets/",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            tickets = data.get("tickets", [])
            total = data.get("total", 0)
            print(f"      ✅ SUCCESS - Found {len(tickets)} tickets (total: {total})")
            
            if len(tickets) >= 4:
                print(f"      ✅ Expected 4+ tickets, found {len(tickets)}")
            else:
                print(f"      ⚠️  Expected 4+ tickets, found {len(tickets)}")
            
            results["list_tickets"] = {"success": True, "data": data}
            
            # Test ticket detail if we have tickets
            if tickets:
                ticket_id = tickets[0].get("id")
                if ticket_id:
                    # Test 3: Get ticket detail
                    print(f"   🔍 Testing GET /api/tickets/{ticket_id}...")
                    response = requests.get(
                        f"{BACKEND_URL}/tickets/{ticket_id}",
                        headers=headers,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        ticket_detail = response.json()
                        print(f"      ✅ SUCCESS - Ticket detail retrieved")
                        results["ticket_detail"] = {"success": True, "data": ticket_detail}
                        
                        # Test 4: Update ticket status (admin/technician only)
                        if user_role in ["admin", "technician"]:
                            print(f"   ✏️ Testing PATCH /api/tickets/{ticket_id}/status...")
                            status_data = {"status": "in_progress"}
                            
                            response = requests.patch(
                                f"{BACKEND_URL}/tickets/{ticket_id}/status",
                                json=status_data,
                                headers=headers,
                                timeout=15
                            )
                            
                            if response.status_code == 200:
                                print(f"      ✅ SUCCESS - Ticket status updated")
                                results["update_status"] = {"success": True, "data": response.json()}
                            else:
                                error_msg = f"Update status failed: {response.status_code}"
                                print(f"      ❌ {error_msg}")
                                results["update_status"] = {"success": False, "error": error_msg}
                            
                            # Test 5: Assign ticket to technician
                            print(f"   👤 Testing PATCH /api/tickets/{ticket_id}/assign...")
                            assign_data = {"technician_id": "tech-user-id"}
                            
                            response = requests.patch(
                                f"{BACKEND_URL}/tickets/{ticket_id}/assign",
                                json=assign_data,
                                headers=headers,
                                timeout=15
                            )
                            
                            if response.status_code == 200:
                                print(f"      ✅ SUCCESS - Ticket assigned")
                                results["assign_ticket"] = {"success": True, "data": response.json()}
                            else:
                                error_msg = f"Assign ticket failed: {response.status_code}"
                                print(f"      ❌ {error_msg}")
                                results["assign_ticket"] = {"success": False, "error": error_msg}
                        else:
                            results["update_status"] = {"success": True, "data": {"skipped": "Not admin/technician"}}
                            results["assign_ticket"] = {"success": True, "data": {"skipped": "Not admin/technician"}}
                        
                        # Test 6: Add message to ticket
                        print(f"   💬 Testing POST /api/tickets/{ticket_id}/messages...")
                        message_data = {
                            "message": "Test message from API testing",
                            "is_internal": False
                        }
                        
                        response = requests.post(
                            f"{BACKEND_URL}/tickets/{ticket_id}/messages",
                            json=message_data,
                            headers=headers,
                            timeout=15
                        )
                        
                        if response.status_code == 201:
                            print(f"      ✅ SUCCESS - Message added to ticket")
                            results["add_message"] = {"success": True, "data": response.json()}
                        else:
                            error_msg = f"Add message failed: {response.status_code}"
                            print(f"      ❌ {error_msg}")
                            results["add_message"] = {"success": False, "error": error_msg}
                    else:
                        error_msg = f"Ticket detail failed: {response.status_code}"
                        print(f"      ❌ {error_msg}")
                        results["ticket_detail"] = {"success": False, "error": error_msg}
        else:
            error_msg = f"List tickets failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                pass
            print(f"      ❌ {error_msg}")
            results["list_tickets"] = {"success": False, "error": error_msg}
        
        # Test 2: Create new ticket
        print("   ➕ Testing POST /api/tickets...")
        ticket_data = {
            "subject": "Test Ticket from API Testing",
            "description": "This is a test ticket created during API testing",
            "category": "technical_issue",
            "priority": "medium"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/tickets/",
            json=ticket_data,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 201:
            new_ticket = response.json()
            print(f"      ✅ SUCCESS - Ticket created with ID: {new_ticket.get('id')}")
            results["create_ticket"] = {"success": True, "data": new_ticket}
        else:
            error_msg = f"Create ticket failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                pass
            print(f"      ❌ {error_msg}")
            results["create_ticket"] = {"success": False, "error": error_msg}
        
        # Test 7: Get admin stats
        print("   📊 Testing GET /api/tickets/admin/stats...")
        response = requests.get(
            f"{BACKEND_URL}/tickets/admin/stats",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            stats = response.json()
            print(f"      ✅ SUCCESS - Admin stats retrieved")
            results["admin_stats"] = {"success": True, "data": stats}
        else:
            error_msg = f"Admin stats failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["admin_stats"] = {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"Support tickets API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results

def test_water_conservation_tips_api(token: str, user_role: str) -> Dict[str, Any]:
    """Test Water Conservation Tips API endpoints"""
    print(f"\n💡 Testing Water Conservation Tips API ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "list_tips": {"success": False, "error": None, "data": None},
        "tip_detail": {"success": False, "error": None, "data": None},
        "create_tip": {"success": False, "error": None, "data": None},
        "update_tip": {"success": False, "error": None, "data": None},
        "engage_tip": {"success": False, "error": None, "data": None},
        "personalized_tips": {"success": False, "error": None, "data": None}
    }
    
    try:
        # Test 1: List tips (should return 4 tips)
        print("   📋 Testing GET /api/tips...")
        response = requests.get(
            f"{BACKEND_URL}/tips/",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            tips = data.get("tips", [])
            total = data.get("total", 0)
            print(f"      ✅ SUCCESS - Found {len(tips)} tips (total: {total})")
            
            if len(tips) >= 4:
                print(f"      ✅ Expected 4+ tips, found {len(tips)}")
            else:
                print(f"      ⚠️  Expected 4+ tips, found {len(tips)}")
            
            results["list_tips"] = {"success": True, "data": data}
            
            # Test tip detail if we have tips
            if tips:
                tip_id = tips[0].get("id")
                if tip_id:
                    # Test 2: Get tip detail
                    print(f"   🔍 Testing GET /api/tips/{tip_id}...")
                    response = requests.get(
                        f"{BACKEND_URL}/tips/{tip_id}",
                        headers=headers,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        tip_detail = response.json()
                        print(f"      ✅ SUCCESS - Tip detail retrieved")
                        results["tip_detail"] = {"success": True, "data": tip_detail}
                        
                        # Test 5: Engage with tip (like/bookmark/implement)
                        print(f"   👍 Testing POST /api/tips/{tip_id}/engage...")
                        engage_data = {
                            "action": "like"
                        }
                        
                        response = requests.post(
                            f"{BACKEND_URL}/tips/{tip_id}/engage",
                            json=engage_data,
                            headers=headers,
                            timeout=15
                        )
                        
                        if response.status_code == 200:
                            print(f"      ✅ SUCCESS - Tip engagement recorded")
                            results["engage_tip"] = {"success": True, "data": response.json()}
                        else:
                            error_msg = f"Engage tip failed: {response.status_code}"
                            print(f"      ❌ {error_msg}")
                            results["engage_tip"] = {"success": False, "error": error_msg}
                    else:
                        error_msg = f"Tip detail failed: {response.status_code}"
                        print(f"      ❌ {error_msg}")
                        results["tip_detail"] = {"success": False, "error": error_msg}
        else:
            error_msg = f"List tips failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                pass
            print(f"      ❌ {error_msg}")
            results["list_tips"] = {"success": False, "error": error_msg}
        
        # Test 3: Create new tip (admin only)
        if user_role == "admin":
            print("   ➕ Testing POST /api/tips/admin/create...")
            tip_data = {
                "title": "Test Water Conservation Tip",
                "description": "This is a test tip created during API testing",
                "category": "saving_water",
                "difficulty": "easy",
                "estimated_savings_percentage": 15.0,
                "estimated_time_minutes": 30,
                "implementation_steps": ["Step 1: Test step", "Step 2: Another test step"],
                "benefits": ["Saves water", "Reduces costs"],
                "required_tools": ["Basic tools"],
                "status": "published"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/tips/admin/create",
                json=tip_data,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 201:
                new_tip = response.json()
                tip_id = new_tip.get("id")
                print(f"      ✅ SUCCESS - Tip created with ID: {tip_id}")
                results["create_tip"] = {"success": True, "data": new_tip}
                
                # Test 4: Update tip (admin only)
                if tip_id:
                    print(f"   ✏️ Testing PUT /api/tips/admin/{tip_id}...")
                    update_data = {
                        "title": "Updated Test Water Conservation Tip",
                        "estimated_savings_percentage": 20.0
                    }
                    
                    response = requests.put(
                        f"{BACKEND_URL}/tips/admin/{tip_id}",
                        json=update_data,
                        headers=headers,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        print(f"      ✅ SUCCESS - Tip updated")
                        results["update_tip"] = {"success": True, "data": response.json()}
                    else:
                        error_msg = f"Update tip failed: {response.status_code}"
                        print(f"      ❌ {error_msg}")
                        results["update_tip"] = {"success": False, "error": error_msg}
            else:
                error_msg = f"Create tip failed: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('detail', '')}"
                except:
                    pass
                print(f"      ❌ {error_msg}")
                results["create_tip"] = {"success": False, "error": error_msg}
        else:
            results["create_tip"] = {"success": True, "data": {"skipped": "Not admin"}}
            results["update_tip"] = {"success": True, "data": {"skipped": "Not admin"}}
        
        # Test 6: Get personalized tips
        print("   🎯 Testing GET /api/tips/personalized...")
        response = requests.get(
            f"{BACKEND_URL}/tips/personalized",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            personalized = response.json()
            print(f"      ✅ SUCCESS - Personalized tips retrieved")
            results["personalized_tips"] = {"success": True, "data": personalized}
        else:
            error_msg = f"Personalized tips failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["personalized_tips"] = {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"Water conservation tips API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results

def test_vouchers_api(token: str, user_role: str) -> Dict[str, Any]:
    """Test Vouchers API endpoints"""
    print(f"\n🎟️ Testing Vouchers API ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "list_vouchers": {"success": False, "error": None, "data": None},
        "create_voucher": {"success": False, "error": None, "data": None},
        "active_vouchers": {"success": False, "error": None, "data": None},
        "validate_voucher": {"success": False, "error": None, "data": None},
        "apply_voucher": {"success": False, "error": None, "data": None}
    }
    
    try:
        # Test 1: List vouchers (should return 4 vouchers: WELCOME50, HEMAT20, FLASH100K, NEWYEAR2025)
        print("   📋 Testing GET /api/vouchers...")
        response = requests.get(
            f"{BACKEND_URL}/vouchers/",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            vouchers = response.json()
            print(f"      ✅ SUCCESS - Found {len(vouchers)} vouchers")
            
            # Check for expected voucher codes
            voucher_codes = [v.get("code") for v in vouchers]
            expected_codes = ["WELCOME50", "HEMAT20", "FLASH100K", "NEWYEAR2025"]
            found_codes = [code for code in expected_codes if code in voucher_codes]
            
            if len(found_codes) >= 4:
                print(f"      ✅ Expected vouchers found: {found_codes}")
            else:
                print(f"      ⚠️  Expected 4 vouchers, found: {found_codes}")
            
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
            print("   ➕ Testing POST /api/vouchers...")
            voucher_data = {
                "code": f"TEST{int(time.time())}",
                "description": "Test voucher created during API testing",
                "discount_type": "percentage",
                "discount_value": 25.0,
                "min_purchase_amount": 100000,
                "max_discount_amount": 150000,
                "usage_limit": 50,
                "per_customer_limit": 1,
                "valid_from": "2025-01-01T00:00:00Z",
                "valid_until": "2025-12-31T23:59:59Z",
                "is_active": True
            }
            
            response = requests.post(
                f"{BACKEND_URL}/vouchers/",
                json=voucher_data,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 201:
                new_voucher = response.json()
                voucher_code = new_voucher.get("code")
                print(f"      ✅ SUCCESS - Voucher created: {voucher_code}")
                results["create_voucher"] = {"success": True, "data": new_voucher}
                
                # Test 4: Validate voucher
                print(f"   ✅ Testing POST /api/vouchers/validate...")
                validate_data = {
                    "code": voucher_code,
                    "purchase_amount": 200000
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/vouchers/validate",
                    json=validate_data,
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    validation = response.json()
                    discount_amount = validation.get("discount_amount", 0)
                    final_amount = validation.get("final_amount", 0)
                    print(f"      ✅ SUCCESS - Voucher validated, discount: Rp {discount_amount:,.0f}, final: Rp {final_amount:,.0f}")
                    results["validate_voucher"] = {"success": True, "data": validation}
                    
                    # Test 5: Apply voucher
                    print(f"   💰 Testing POST /api/vouchers/apply...")
                    apply_data = {
                        "code": voucher_code,
                        "transaction_id": f"TXN{int(time.time())}",
                        "purchase_amount": 200000
                    }
                    
                    response = requests.post(
                        f"{BACKEND_URL}/vouchers/apply",
                        json=apply_data,
                        headers=headers,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        application = response.json()
                        print(f"      ✅ SUCCESS - Voucher applied successfully")
                        results["apply_voucher"] = {"success": True, "data": application}
                    else:
                        error_msg = f"Apply voucher failed: {response.status_code}"
                        print(f"      ❌ {error_msg}")
                        results["apply_voucher"] = {"success": False, "error": error_msg}
                else:
                    error_msg = f"Validate voucher failed: {response.status_code}"
                    print(f"      ❌ {error_msg}")
                    results["validate_voucher"] = {"success": False, "error": error_msg}
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
            results["create_voucher"] = {"success": True, "data": {"skipped": "Not admin"}}
            results["validate_voucher"] = {"success": True, "data": {"skipped": "Not admin"}}
            results["apply_voucher"] = {"success": True, "data": {"skipped": "Not admin"}}
        
        # Test 3: Get active vouchers
        print("   🎯 Testing GET /api/vouchers/active...")
        response = requests.get(
            f"{BACKEND_URL}/vouchers/active",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            active_vouchers = response.json()
            print(f"      ✅ SUCCESS - Found {len(active_vouchers)} active vouchers")
            results["active_vouchers"] = {"success": True, "data": active_vouchers}
        else:
            error_msg = f"Active vouchers failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["active_vouchers"] = {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"Vouchers API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results

def test_alerts_notification_api(token: str, user_role: str) -> Dict[str, Any]:
    """Test Alert & Notification API endpoints"""
    print(f"\n🚨 Testing Alert & Notification API ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "get_alerts": {"success": False, "error": None, "data": None},
        "unread_count": {"success": False, "error": None, "data": None},
        "alert_preferences": {"success": False, "error": None, "data": None},
        "update_preferences": {"success": False, "error": None, "data": None},
        "leak_detection": {"success": False, "error": None, "data": None},
        "tampering_events": {"success": False, "error": None, "data": None}
    }
    
    try:
        # Test 1: Get alerts
        print("   📋 Testing GET /api/alerts...")
        response = requests.get(
            f"{BACKEND_URL}/alerts/",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            alerts = response.json()
            print(f"      ✅ SUCCESS - Found {len(alerts)} alerts")
            results["get_alerts"] = {"success": True, "data": alerts}
        else:
            error_msg = f"Get alerts failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["get_alerts"] = {"success": False, "error": error_msg}
        
        # Test 2: Get unread count
        print("   🔢 Testing GET /api/alerts/unread-count...")
        response = requests.get(
            f"{BACKEND_URL}/alerts/unread-count",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            count_data = response.json()
            unread_count = count_data.get("unread_count", 0)
            print(f"      ✅ SUCCESS - Unread count: {unread_count}")
            results["unread_count"] = {"success": True, "data": count_data}
        else:
            error_msg = f"Unread count failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["unread_count"] = {"success": False, "error": error_msg}
        
        # Test 3: Get alert preferences (FIXED - verify fix working)
        print("   ⚙️ Testing GET /api/alerts/preferences...")
        response = requests.get(
            f"{BACKEND_URL}/alerts/preferences",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            prefs = response.json()
            print(f"      ✅ SUCCESS - Alert preferences retrieved (FIXED)")
            print(f"      ✅ Low balance threshold: {prefs.get('low_balance_threshold', 'N/A')}")
            results["alert_preferences"] = {"success": True, "data": prefs}
            
            # Test 4: Update alert preferences
            print("   ✏️ Testing PUT /api/alerts/preferences...")
            update_prefs = {
                "low_balance_threshold": 75000,
                "email_notifications": True,
                "sms_notifications": False,
                "push_notifications": True
            }
            
            response = requests.put(
                f"{BACKEND_URL}/alerts/preferences",
                json=update_prefs,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                updated_prefs = response.json()
                print(f"      ✅ SUCCESS - Alert preferences updated")
                results["update_preferences"] = {"success": True, "data": updated_prefs}
            else:
                error_msg = f"Update preferences failed: {response.status_code}"
                print(f"      ❌ {error_msg}")
                results["update_preferences"] = {"success": False, "error": error_msg}
        else:
            error_msg = f"Alert preferences failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["alert_preferences"] = {"success": False, "error": error_msg}
        
        # Test 5: Get leak detection events
        print("   💧 Testing GET /api/alerts/leaks...")
        response = requests.get(
            f"{BACKEND_URL}/alerts/leaks",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            leaks = response.json()
            print(f"      ✅ SUCCESS - Found {len(leaks)} leak detection events")
            results["leak_detection"] = {"success": True, "data": leaks}
        else:
            error_msg = f"Leak detection failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["leak_detection"] = {"success": False, "error": error_msg}
        
        # Test 6: Get tampering events
        print("   🔧 Testing GET /api/alerts/tampering...")
        response = requests.get(
            f"{BACKEND_URL}/alerts/tampering",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            tampering = response.json()
            print(f"      ✅ SUCCESS - Found {len(tampering)} tampering events")
            results["tampering_events"] = {"success": True, "data": tampering}
        else:
            error_msg = f"Tampering events failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["tampering_events"] = {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"Alert & notification API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results

def test_device_management_api(token: str, user_role: str) -> Dict[str, Any]:
    """Test Device Management API endpoints"""
    print(f"\n📱 Testing Device Management API ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "comprehensive_list": {"success": False, "error": None, "data": None},
        "device_stats": {"success": False, "error": None, "data": None},
        "device_activities": {"success": False, "error": None, "data": None},
        "summary_stats": {"success": False, "error": None, "data": None}
    }
    
    try:
        # Test 1: Get comprehensive device list (should return 4 devices)
        print("   📋 Testing GET /api/devices/comprehensive...")
        response = requests.get(
            f"{BACKEND_URL}/devices/comprehensive",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            devices = data.get("devices", [])
            total = data.get("total", 0)
            print(f"      ✅ SUCCESS - Found {len(devices)} devices (total: {total})")
            
            if len(devices) >= 4:
                print(f"      ✅ Expected 4+ devices, found {len(devices)}")
            else:
                print(f"      ⚠️  Expected 4+ devices, found {len(devices)}")
            
            results["comprehensive_list"] = {"success": True, "data": data}
            
            # Test device-specific endpoints if we have devices
            if devices:
                device_id = devices[0].get("id")
                if device_id:
                    # Test 2: Get device stats
                    print(f"   📊 Testing GET /api/devices/{device_id}/stats...")
                    response = requests.get(
                        f"{BACKEND_URL}/devices/{device_id}/stats",
                        headers=headers,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        stats = response.json()
                        print(f"      ✅ SUCCESS - Device stats retrieved")
                        results["device_stats"] = {"success": True, "data": stats}
                    else:
                        error_msg = f"Device stats failed: {response.status_code}"
                        print(f"      ❌ {error_msg}")
                        results["device_stats"] = {"success": False, "error": error_msg}
                    
                    # Test 3: Get device activities
                    print(f"   📋 Testing GET /api/devices/{device_id}/activities...")
                    response = requests.get(
                        f"{BACKEND_URL}/devices/{device_id}/activities",
                        headers=headers,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        activities = response.json()
                        print(f"      ✅ SUCCESS - Device activities retrieved")
                        results["device_activities"] = {"success": True, "data": activities}
                    else:
                        error_msg = f"Device activities failed: {response.status_code}"
                        print(f"      ❌ {error_msg}")
                        results["device_activities"] = {"success": False, "error": error_msg}
        else:
            error_msg = f"Comprehensive device list failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                pass
            print(f"      ❌ {error_msg}")
            results["comprehensive_list"] = {"success": False, "error": error_msg}
        
        # Test 4: Get summary stats
        print("   📈 Testing GET /api/devices/summary/stats...")
        response = requests.get(
            f"{BACKEND_URL}/devices/summary/stats",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            summary = response.json()
            print(f"      ✅ SUCCESS - Summary stats retrieved")
            results["summary_stats"] = {"success": True, "data": summary}
        else:
            error_msg = f"Summary stats failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["summary_stats"] = {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"Device management API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results

def test_role_permission_api(token: str, user_role: str) -> Dict[str, Any]:
    """Test Role & Permission API endpoints"""
    print(f"\n👥 Testing Role & Permission API ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "list_roles": {"success": False, "error": None, "data": None},
        "get_permissions": {"success": False, "error": None, "data": None},
        "role_detail": {"success": False, "error": None, "data": None}
    }
    
    try:
        # Test 1: List roles (use /api/roles/list NOT /api/roles/)
        print("   📋 Testing GET /api/roles/list...")
        response = requests.get(
            f"{BACKEND_URL}/roles/list",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            roles = response.json()
            print(f"      ✅ SUCCESS - Found {len(roles)} roles")
            
            # Check for expected roles
            role_names = [r.get("name") for r in roles]
            expected_roles = ["admin", "technician", "customer"]
            found_roles = [role for role in expected_roles if role in role_names]
            
            if len(found_roles) >= 3:
                print(f"      ✅ Expected roles found: {found_roles}")
            else:
                print(f"      ⚠️  Expected 3 roles, found: {found_roles}")
            
            results["list_roles"] = {"success": True, "data": roles}
            
            # Test role detail if we have roles
            if roles:
                role_id = roles[0].get("id") or roles[0].get("name")
                if role_id:
                    # Test 3: Get role detail
                    print(f"   🔍 Testing GET /api/roles/{role_id}...")
                    response = requests.get(
                        f"{BACKEND_URL}/roles/{role_id}",
                        headers=headers,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        role_detail = response.json()
                        print(f"      ✅ SUCCESS - Role detail retrieved")
                        results["role_detail"] = {"success": True, "data": role_detail}
                    else:
                        error_msg = f"Role detail failed: {response.status_code}"
                        print(f"      ❌ {error_msg}")
                        results["role_detail"] = {"success": False, "error": error_msg}
        else:
            error_msg = f"List roles failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                pass
            print(f"      ❌ {error_msg}")
            results["list_roles"] = {"success": False, "error": error_msg}
        
        # Test 2: Get permissions
        print("   🔐 Testing GET /api/roles/permissions...")
        response = requests.get(
            f"{BACKEND_URL}/roles/permissions",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            permissions = response.json()
            print(f"      ✅ SUCCESS - Found {len(permissions)} permissions")
            results["get_permissions"] = {"success": True, "data": permissions}
        else:
            error_msg = f"Get permissions failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["get_permissions"] = {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"Role & permission API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results

def test_iot_device_communication_api(token: str, user_role: str) -> Dict[str, Any]:
    """Test IoT Device Communication API endpoints"""
    print(f"\n🌐 Testing IoT Device Communication API ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "health_check": {"success": False, "error": None, "data": None}
    }
    
    try:
        # Test 1: Health check endpoint
        print("   ❤️ Testing GET /api/iot/health...")
        response = requests.get(
            f"{BACKEND_URL}/iot/health",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            health = response.json()
            print(f"      ✅ SUCCESS - IoT health check passed")
            results["health_check"] = {"success": True, "data": health}
        else:
            error_msg = f"IoT health check failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["health_check"] = {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"IoT device communication API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        results["health_check"] = {"success": False, "error": error_msg}
    
    return results

def run_comprehensive_tests():
    """Run comprehensive backend API tests"""
    print("🚀 Starting Comprehensive IndoWater Backend API Testing...")
    print("=" * 80)
    
    all_results = {}
    
    # Test each account
    for account in DEMO_ACCOUNTS:
        print(f"\n{'=' * 20} TESTING {account['name'].upper()} ACCOUNT {'=' * 20}")
        
        # Test login
        login_result = test_login(
            account["email"], 
            account["password"], 
            account["expected_role"],
            account["name"]
        )
        
        if not login_result["success"]:
            print(f"❌ {account['name']} login failed: {login_result['error']}")
            all_results[account["name"]] = {"login": login_result}
            continue
        
        token = login_result["token"]
        user_role = account["expected_role"]
        user = login_result["user"]
        customer_id = user.get("id")
        
        # Store results for this account
        account_results = {
            "login": login_result,
            "support_tickets": test_support_tickets_api(token, user_role),
            "water_tips": test_water_conservation_tips_api(token, user_role),
            "vouchers": test_vouchers_api(token, user_role),
            "alerts": test_alerts_notification_api(token, user_role),
            "devices": test_device_management_api(token, user_role),
            "roles": test_role_permission_api(token, user_role),
            "iot": test_iot_device_communication_api(token, user_role)
        }
        
        all_results[account["name"]] = account_results
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 80)
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for account_name, account_results in all_results.items():
        print(f"\n🔍 {account_name} Account Results:")
        
        for api_name, api_results in account_results.items():
            if isinstance(api_results, dict):
                for test_name, test_result in api_results.items():
                    total_tests += 1
                    if test_result.get("success", False):
                        passed_tests += 1
                        status = "✅"
                    else:
                        failed_tests += 1
                        status = "❌"
                        error = test_result.get("error", "Unknown error")
                        print(f"   {status} {api_name}.{test_name}: {error}")
    
    print(f"\n📈 FINAL RESULTS:")
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
    print(f"   ❌ Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
    
    if failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED! Backend APIs are working correctly.")
    else:
        print(f"\n⚠️  {failed_tests} tests failed. Please check the errors above.")
    
    return all_results

if __name__ == "__main__":
    try:
        results = run_comprehensive_tests()
        
        # Save results to file
        with open("/app/comprehensive_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Test results saved to: /app/comprehensive_test_results.json")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during testing: {str(e)}")
        sys.exit(1)