#!/usr/bin/env python3
"""
Backend API Testing Script for IndoWater Solution
Tests login, analytics, reporting, and payment history APIs
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# Backend URL from environment
BACKEND_URL = "https://work-continuity-1.preview.emergentagent.com/api"

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
    
    # Prepare login data
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        # Make login request
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
            
            # Validate user object
            user = data.get("user", {})
            user_required_fields = ["id", "email", "full_name", "role", "is_active"]
            missing_user_fields = [field for field in user_required_fields if field not in user]
            
            if missing_user_fields:
                return {
                    "success": False,
                    "error": f"Missing user fields: {missing_user_fields}",
                    "response": data
                }
            
            # Validate role
            actual_role = user.get("role")
            if actual_role != expected_role:
                return {
                    "success": False,
                    "error": f"Role mismatch. Expected: {expected_role}, Got: {actual_role}",
                    "response": data
                }
            
            # Validate token type
            if data.get("token_type") != "bearer":
                return {
                    "success": False,
                    "error": f"Invalid token type. Expected: bearer, Got: {data.get('token_type')}",
                    "response": data
                }
            
            # Validate JWT token exists and is not empty
            token = data.get("access_token")
            if not token or len(token) < 10:
                return {
                    "success": False,
                    "error": "Invalid or missing JWT token",
                    "response": data
                }
            
            print(f"   ✅ SUCCESS - Role: {actual_role}, Active: {user.get('is_active')}")
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
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ CONNECTION ERROR - {str(e)}")
        return {
            "success": False,
            "error": f"Connection error: {str(e)}"
        }
    except Exception as e:
        print(f"   ❌ UNEXPECTED ERROR - {str(e)}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }

def test_payment_history_api(token: str, customer_id: str) -> Dict[str, Any]:
    """Test payment history API endpoints"""
    print(f"\n💳 Testing Payment History APIs...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "history_list": {"success": False, "error": None, "data": None},
        "history_filters": {"success": False, "error": None, "data": None},
        "history_pagination": {"success": False, "error": None, "data": None},
        "transaction_detail": {"success": False, "error": None, "data": None}
    }
    
    try:
        # Test 1: Get all payment history
        print("   📋 Testing GET /api/payments/history/list...")
        response = requests.get(
            f"{BACKEND_URL}/payments/history/list",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            transactions = data.get("transactions", [])
            total = data.get("total", 0)
            
            print(f"      ✅ SUCCESS - Found {len(transactions)} transactions (total: {total})")
            
            if len(transactions) >= 7:
                print(f"      ✅ Expected 7 transactions, found {len(transactions)}")
                results["history_list"] = {"success": True, "data": data}
                
                # Test 2: Filter by status - paid
                print("   🔍 Testing status filter (paid)...")
                response = requests.get(
                    f"{BACKEND_URL}/payments/history/list?status=paid",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    paid_data = response.json()
                    paid_transactions = paid_data.get("transactions", [])
                    paid_count = len([t for t in paid_transactions if t.get("status") == "paid"])
                    
                    print(f"      ✅ Paid filter - Found {paid_count} paid transactions")
                    results["history_filters"] = {"success": True, "data": paid_data}
                else:
                    error_msg = f"Status filter failed: {response.status_code}"
                    print(f"      ❌ {error_msg}")
                    results["history_filters"] = {"success": False, "error": error_msg}
                
                # Test 3: Pagination
                print("   📄 Testing pagination (limit=3, skip=0)...")
                response = requests.get(
                    f"{BACKEND_URL}/payments/history/list?limit=3&skip=0",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    page_data = response.json()
                    page_transactions = page_data.get("transactions", [])
                    
                    if len(page_transactions) <= 3:
                        print(f"      ✅ Pagination working - Got {len(page_transactions)} transactions")
                        results["history_pagination"] = {"success": True, "data": page_data}
                    else:
                        error_msg = f"Pagination failed - Expected ≤3, got {len(page_transactions)}"
                        print(f"      ❌ {error_msg}")
                        results["history_pagination"] = {"success": False, "error": error_msg}
                else:
                    error_msg = f"Pagination failed: {response.status_code}"
                    print(f"      ❌ {error_msg}")
                    results["history_pagination"] = {"success": False, "error": error_msg}
                
                # Test 4: Get transaction details
                if transactions:
                    first_transaction = transactions[0]
                    reference_id = first_transaction.get("reference_id")
                    
                    if reference_id:
                        print(f"   🔍 Testing GET /api/payments/{reference_id}...")
                        response = requests.get(
                            f"{BACKEND_URL}/payments/{reference_id}",
                            headers=headers,
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            detail_data = response.json()
                            
                            # Verify customer can only access their own transactions
                            if detail_data.get("customer_id") == customer_id:
                                print(f"      ✅ Transaction detail retrieved successfully")
                                print(f"      ✅ Authorization check passed - customer can access own transaction")
                                results["transaction_detail"] = {"success": True, "data": detail_data}
                            else:
                                error_msg = "Authorization failed - wrong customer_id in response"
                                print(f"      ❌ {error_msg}")
                                results["transaction_detail"] = {"success": False, "error": error_msg}
                        else:
                            error_msg = f"Transaction detail failed: {response.status_code}"
                            print(f"      ❌ {error_msg}")
                            results["transaction_detail"] = {"success": False, "error": error_msg}
                    else:
                        error_msg = "No reference_id found in first transaction"
                        print(f"      ❌ {error_msg}")
                        results["transaction_detail"] = {"success": False, "error": error_msg}
            else:
                error_msg = f"Expected 7 transactions, found {len(transactions)}"
                print(f"      ❌ {error_msg}")
                results["history_list"] = {"success": False, "error": error_msg}
        else:
            error_msg = f"History list failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                pass
            print(f"      ❌ {error_msg}")
            results["history_list"] = {"success": False, "error": error_msg}
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Connection error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results


def test_analytics_api(token: str, user_role: str, customer_id: str = None) -> Dict[str, Any]:
    """Test analytics API endpoints"""
    print(f"\n📊 Testing Analytics APIs ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "usage_month": {"success": False, "error": None, "data": None},
        "usage_week": {"success": False, "error": None, "data": None},
        "trends": {"success": False, "error": None, "data": None},
        "predictions": {"success": False, "error": None, "data": None},
        "admin_overview": {"success": False, "error": None, "data": None}
    }
    
    try:
        # Test 1: Monthly usage analytics
        print("   📈 Testing GET /api/analytics/usage?period=month...")
        response = requests.get(
            f"{BACKEND_URL}/analytics/usage?period=month",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["period", "start_date", "end_date", "total_consumption", "total_cost", "average_daily", "data_points", "device_count"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                results["usage_month"] = {"success": False, "error": f"Missing fields: {missing_fields}"}
                print(f"      ❌ Missing required fields: {missing_fields}")
            else:
                print(f"      ✅ SUCCESS - Total consumption: {data['total_consumption']} m³, Cost: Rp {data['total_cost']:,.2f}")
                print(f"      ✅ Data points: {len(data['data_points'])}, Devices: {data['device_count']}")
                results["usage_month"] = {"success": True, "data": data}
        else:
            error_msg = f"Monthly usage failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                pass
            print(f"      ❌ {error_msg}")
            results["usage_month"] = {"success": False, "error": error_msg}
        
        # Test 2: Weekly usage analytics
        print("   📈 Testing GET /api/analytics/usage?period=week...")
        response = requests.get(
            f"{BACKEND_URL}/analytics/usage?period=week",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"      ✅ SUCCESS - Weekly consumption: {data['total_consumption']} m³")
            results["usage_week"] = {"success": True, "data": data}
        else:
            error_msg = f"Weekly usage failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["usage_week"] = {"success": False, "error": error_msg}
        
        # Test 3: Consumption trends
        print("   📊 Testing GET /api/analytics/trends?period=month...")
        response = requests.get(
            f"{BACKEND_URL}/analytics/trends?period=month",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["period_type", "trends", "overall_trend", "growth_rate"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                results["trends"] = {"success": False, "error": f"Missing fields: {missing_fields}"}
                print(f"      ❌ Missing required fields: {missing_fields}")
            else:
                print(f"      ✅ SUCCESS - Overall trend: {data['overall_trend']}, Growth rate: {data['growth_rate']}%")
                print(f"      ✅ Trend periods: {len(data['trends'])}")
                results["trends"] = {"success": True, "data": data}
        else:
            error_msg = f"Trends failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["trends"] = {"success": False, "error": error_msg}
        
        # Test 4: Predictions (only for customers or with customer_id)
        if user_role == "customer" or customer_id:
            print("   🔮 Testing GET /api/analytics/predictions?days_ahead=7...")
            url = f"{BACKEND_URL}/analytics/predictions?days_ahead=7"
            if user_role != "customer" and customer_id:
                url += f"&customer_id={customer_id}"
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["customer_id", "prediction_method", "based_on_days", "predictions", "average_predicted"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    results["predictions"] = {"success": False, "error": f"Missing fields: {missing_fields}"}
                    print(f"      ❌ Missing required fields: {missing_fields}")
                else:
                    print(f"      ✅ SUCCESS - Predictions: {len(data['predictions'])} days, Avg predicted: {data['average_predicted']} m³")
                    print(f"      ✅ Method: {data['prediction_method']}, Based on: {data['based_on_days']} days")
                    results["predictions"] = {"success": True, "data": data}
            else:
                error_msg = f"Predictions failed: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('detail', '')}"
                except:
                    pass
                print(f"      ❌ {error_msg}")
                results["predictions"] = {"success": False, "error": error_msg}
        else:
            print("   🔮 Skipping predictions test - requires customer context")
            results["predictions"] = {"success": True, "data": {"skipped": "No customer context"}}
        
        # Test 5: Admin overview (only for admin)
        if user_role == "admin":
            print("   👑 Testing GET /api/analytics/admin/overview...")
            response = requests.get(
                f"{BACKEND_URL}/analytics/admin/overview",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_devices", "active_devices", "total_customers", "total_consumption_30d", "total_revenue_30d"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    results["admin_overview"] = {"success": False, "error": f"Missing fields: {missing_fields}"}
                    print(f"      ❌ Missing required fields: {missing_fields}")
                else:
                    print(f"      ✅ SUCCESS - Devices: {data['total_devices']} (active: {data['active_devices']})")
                    print(f"      ✅ Customers: {data['total_customers']}, 30d consumption: {data['total_consumption_30d']} m³")
                    print(f"      ✅ 30d revenue: Rp {data['total_revenue_30d']:,.2f}")
                    results["admin_overview"] = {"success": True, "data": data}
            else:
                error_msg = f"Admin overview failed: {response.status_code}"
                print(f"      ❌ {error_msg}")
                results["admin_overview"] = {"success": False, "error": error_msg}
        else:
            print("   👑 Skipping admin overview - requires admin role")
            results["admin_overview"] = {"success": True, "data": {"skipped": "Not admin"}}
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Connection error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results


def test_report_generation_api(token: str, user_role: str, customer_id: str = None) -> Dict[str, Any]:
    """Test report generation API endpoints"""
    print(f"\n📄 Testing Report Generation APIs ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "pdf_report": {"success": False, "error": None, "data": None},
        "excel_report": {"success": False, "error": None, "data": None}
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
    
    # Add customer_id for admin users
    if user_role == "admin" and customer_id:
        report_data["customer_id"] = customer_id
    
    try:
        # Test 1: PDF Report Generation
        print("   📋 Testing POST /api/reports/export-pdf...")
        response = requests.post(
            f"{BACKEND_URL}/reports/export-pdf",
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
        print("   📊 Testing POST /api/reports/export-excel...")
        response = requests.post(
            f"{BACKEND_URL}/reports/export-excel",
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
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Connection error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results


def test_alert_notification_apis(token: str, user_role: str, customer_id: str = None) -> Dict[str, Any]:
    """Test alert and notification system APIs"""
    print(f"\n🚨 Testing Alert & Notification APIs ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "get_alerts": {"success": False, "error": None, "data": None},
        "unread_count": {"success": False, "error": None, "data": None},
        "mark_all_read": {"success": False, "error": None, "data": None},
        "alert_preferences": {"success": False, "error": None, "data": None},
        "leak_events": {"success": False, "error": None, "data": None},
        "tampering_events": {"success": False, "error": None, "data": None},
        "water_saving_tips": {"success": False, "error": None, "data": None}
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
        
        # Test 3: Mark all as read
        print("   ✅ Testing POST /api/alerts/mark-all-read...")
        response = requests.post(
            f"{BACKEND_URL}/alerts/mark-all-read",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            mark_data = response.json()
            print(f"      ✅ SUCCESS - {mark_data.get('message', 'Marked alerts as read')}")
            results["mark_all_read"] = {"success": True, "data": mark_data}
        else:
            error_msg = f"Mark all read failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["mark_all_read"] = {"success": False, "error": error_msg}
        
        # Test 4: Get alert preferences
        print("   ⚙️ Testing GET /api/alerts/preferences...")
        response = requests.get(
            f"{BACKEND_URL}/alerts/preferences",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            prefs = response.json()
            print(f"      ✅ SUCCESS - Got alert preferences")
            results["alert_preferences"] = {"success": True, "data": prefs}
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
            print(f"      ✅ SUCCESS - Found {len(leaks)} leak events")
            results["leak_events"] = {"success": True, "data": leaks}
        else:
            error_msg = f"Leak events failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["leak_events"] = {"success": False, "error": error_msg}
        
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
        
        # Test 7: Get water saving tips
        print("   💡 Testing GET /api/alerts/tips...")
        response = requests.get(
            f"{BACKEND_URL}/alerts/tips",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            tips = response.json()
            print(f"      ✅ SUCCESS - Found {len(tips)} water saving tips")
            results["water_saving_tips"] = {"success": True, "data": tips}
        else:
            error_msg = f"Water saving tips failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["water_saving_tips"] = {"success": False, "error": error_msg}
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Connection error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results


def test_dashboard_apis(token: str, user_role: str) -> Dict[str, Any]:
    """Test dashboard statistics APIs"""
    print(f"\n📊 Testing Dashboard APIs ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "dashboard_stats": {"success": False, "error": None, "data": None}
    }
    
    try:
        # Test Dashboard Stats
        print("   📈 Testing GET /api/dashboard/stats...")
        response = requests.get(
            f"{BACKEND_URL}/dashboard/stats",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            stats = response.json()
            print(f"      ✅ SUCCESS - Dashboard stats retrieved")
            
            # Check role-specific fields
            if user_role == "admin":
                expected_fields = ["total_users", "total_customers", "total_properties", "total_devices", "active_devices", "total_transactions", "total_revenue"]
            elif user_role == "technician":
                expected_fields = ["total_devices", "active_devices", "maintenance_devices", "faulty_devices"]
            else:  # customer
                expected_fields = ["total_devices", "total_balance", "total_water_consumed", "total_transactions"]
            
            missing_fields = [field for field in expected_fields if field not in stats]
            if missing_fields:
                error_msg = f"Missing expected fields for {user_role}: {missing_fields}"
                print(f"      ❌ {error_msg}")
                results["dashboard_stats"] = {"success": False, "error": error_msg}
            else:
                print(f"      ✅ All expected fields present for {user_role}")
                results["dashboard_stats"] = {"success": True, "data": stats}
        else:
            error_msg = f"Dashboard stats failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["dashboard_stats"] = {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"Dashboard API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        results["dashboard_stats"] = {"success": False, "error": error_msg}
    
    return results


def test_user_management_apis(token: str, user_role: str) -> Dict[str, Any]:
    """Test user management APIs"""
    print(f"\n👥 Testing User Management APIs ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "list_users": {"success": False, "error": None, "data": None},
        "create_user": {"success": False, "error": None, "data": None},
        "get_user": {"success": False, "error": None, "data": None},
        "update_user": {"success": False, "error": None, "data": None},
        "delete_user": {"success": False, "error": None, "data": None}
    }
    
    if user_role != "admin":
        print("   ⚠️  Skipping user management tests - requires admin role")
        for key in results:
            results[key] = {"success": True, "data": {"skipped": "Not admin"}}
        return results
    
    try:
        # Test 1: List Users
        print("   📋 Testing GET /api/users...")
        response = requests.get(
            f"{BACKEND_URL}/users",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            users = response.json()
            print(f"      ✅ SUCCESS - Found {len(users)} users")
            results["list_users"] = {"success": True, "data": users}
        else:
            error_msg = f"List users failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["list_users"] = {"success": False, "error": error_msg}
        
        # Test 2: Create User
        print("   ➕ Testing POST /api/users...")
        user_data = {
            "email": f"test_user_{int(time.time())}@indowater.com",
            "password": "testpass123",
            "full_name": "Test User",
            "role": "customer",
            "phone": "+6281234567890"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/users",
            json=user_data,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 201:
            new_user = response.json()
            created_user_id = new_user.get("id")
            print(f"      ✅ SUCCESS - User created with ID: {created_user_id}")
            results["create_user"] = {"success": True, "data": new_user}
            
            # Test 3: Get User by ID
            if created_user_id:
                print(f"   🔍 Testing GET /api/users/{created_user_id}...")
                response = requests.get(
                    f"{BACKEND_URL}/users/{created_user_id}",
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    user_detail = response.json()
                    print(f"      ✅ SUCCESS - User details retrieved")
                    results["get_user"] = {"success": True, "data": user_detail}
                else:
                    error_msg = f"Get user failed: {response.status_code}"
                    print(f"      ❌ {error_msg}")
                    results["get_user"] = {"success": False, "error": error_msg}
                
                # Test 4: Update User
                print(f"   ✏️ Testing PUT /api/users/{created_user_id}...")
                update_data = {
                    "full_name": "Updated Test User",
                    "phone": "+6289876543210"
                }
                
                response = requests.put(
                    f"{BACKEND_URL}/users/{created_user_id}",
                    json=update_data,
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    updated_user = response.json()
                    print(f"      ✅ SUCCESS - User updated")
                    results["update_user"] = {"success": True, "data": updated_user}
                else:
                    error_msg = f"Update user failed: {response.status_code}"
                    print(f"      ❌ {error_msg}")
                    results["update_user"] = {"success": False, "error": error_msg}
                
                # Test 5: Delete User
                print(f"   🗑️ Testing DELETE /api/users/{created_user_id}...")
                response = requests.delete(
                    f"{BACKEND_URL}/users/{created_user_id}",
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    print(f"      ✅ SUCCESS - User deleted")
                    results["delete_user"] = {"success": True, "data": {"deleted": True}}
                else:
                    error_msg = f"Delete user failed: {response.status_code}"
                    print(f"      ❌ {error_msg}")
                    results["delete_user"] = {"success": False, "error": error_msg}
        else:
            error_msg = f"Create user failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["create_user"] = {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"User management API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results


def test_customer_management_apis(token: str, user_role: str) -> Dict[str, Any]:
    """Test customer management APIs"""
    print(f"\n👤 Testing Customer Management APIs ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "list_customers": {"success": False, "error": None, "data": None},
        "create_customer": {"success": False, "error": None, "data": None},
        "customer_devices": {"success": False, "error": None, "data": None},
        "customer_usage": {"success": False, "error": None, "data": None},
        "customer_payments": {"success": False, "error": None, "data": None}
    }
    
    if user_role not in ["admin", "technician"]:
        print("   ⚠️  Skipping customer management tests - requires admin/technician role")
        for key in results:
            results[key] = {"success": True, "data": {"skipped": "Not admin/technician"}}
        return results
    
    try:
        # Test 1: List Customers
        print("   📋 Testing GET /api/customers...")
        response = requests.get(
            f"{BACKEND_URL}/customers",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            customers = response.json()
            print(f"      ✅ SUCCESS - Found {len(customers)} customers")
            results["list_customers"] = {"success": True, "data": customers}
            
            # Test customer-specific endpoints if we have customers
            if customers and len(customers) > 0:
                customer_id = customers[0].get("id")
                
                # Test 2: Customer Devices
                print(f"   📱 Testing GET /api/customers/{customer_id}/devices...")
                response = requests.get(
                    f"{BACKEND_URL}/customers/{customer_id}/devices",
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    devices = response.json()
                    print(f"      ✅ SUCCESS - Found {len(devices)} devices for customer")
                    results["customer_devices"] = {"success": True, "data": devices}
                else:
                    error_msg = f"Customer devices failed: {response.status_code}"
                    print(f"      ❌ {error_msg}")
                    results["customer_devices"] = {"success": False, "error": error_msg}
                
                # Test 3: Customer Usage
                print(f"   📊 Testing GET /api/customers/{customer_id}/usage...")
                response = requests.get(
                    f"{BACKEND_URL}/customers/{customer_id}/usage",
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    usage = response.json()
                    print(f"      ✅ SUCCESS - Retrieved customer usage data")
                    results["customer_usage"] = {"success": True, "data": usage}
                else:
                    error_msg = f"Customer usage failed: {response.status_code}"
                    print(f"      ❌ {error_msg}")
                    results["customer_usage"] = {"success": False, "error": error_msg}
                
                # Test 4: Customer Payments
                print(f"   💳 Testing GET /api/customers/{customer_id}/payments...")
                response = requests.get(
                    f"{BACKEND_URL}/customers/{customer_id}/payments",
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    payments = response.json()
                    print(f"      ✅ SUCCESS - Retrieved customer payments")
                    results["customer_payments"] = {"success": True, "data": payments}
                else:
                    error_msg = f"Customer payments failed: {response.status_code}"
                    print(f"      ❌ {error_msg}")
                    results["customer_payments"] = {"success": False, "error": error_msg}
        else:
            error_msg = f"List customers failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["list_customers"] = {"success": False, "error": error_msg}
        
        # Test 5: Create Customer (Admin only)
        if user_role == "admin":
            print("   ➕ Testing POST /api/customers...")
            import time
            customer_data = {
                "customer_number": f"CUST{int(time.time())}",
                "full_name": "Test Customer",
                "email": f"test_customer_{int(time.time())}@indowater.com",
                "phone": "+6281234567890",
                "address": "Test Address",
                "balance": 100000
            }
            
            response = requests.post(
                f"{BACKEND_URL}/customers",
                json=customer_data,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 201:
                new_customer = response.json()
                print(f"      ✅ SUCCESS - Customer created")
                results["create_customer"] = {"success": True, "data": new_customer}
            else:
                error_msg = f"Create customer failed: {response.status_code}"
                print(f"      ❌ {error_msg}")
                results["create_customer"] = {"success": False, "error": error_msg}
        else:
            results["create_customer"] = {"success": True, "data": {"skipped": "Not admin"}}
            
    except Exception as e:
        error_msg = f"Customer management API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results


def test_property_management_apis(token: str, user_role: str) -> Dict[str, Any]:
    """Test property management APIs"""
    print(f"\n🏠 Testing Property Management APIs ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "list_properties": {"success": False, "error": None, "data": None},
        "create_property": {"success": False, "error": None, "data": None},
        "get_property": {"success": False, "error": None, "data": None},
        "update_property": {"success": False, "error": None, "data": None},
        "delete_property": {"success": False, "error": None, "data": None}
    }
    
    try:
        # Test 1: List Properties
        print("   📋 Testing GET /api/properties...")
        response = requests.get(
            f"{BACKEND_URL}/properties",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            properties = response.json()
            print(f"      ✅ SUCCESS - Found {len(properties)} properties")
            results["list_properties"] = {"success": True, "data": properties}
        else:
            error_msg = f"List properties failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["list_properties"] = {"success": False, "error": error_msg}
        
        # Test CRUD operations for admin/technician
        if user_role in ["admin", "technician"]:
            # Test 2: Create Property
            print("   ➕ Testing POST /api/properties...")
            import time
            property_data = {
                "name": f"Test Property {int(time.time())}",
                "address": "Test Address 123",
                "property_type": "residential",
                "area_size": 100.5,
                "owner_name": "Test Owner",
                "owner_contact": "+6281234567890"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/properties",
                json=property_data,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 201:
                new_property = response.json()
                property_id = new_property.get("id")
                print(f"      ✅ SUCCESS - Property created with ID: {property_id}")
                results["create_property"] = {"success": True, "data": new_property}
                
                # Test 3: Get Property
                if property_id:
                    print(f"   🔍 Testing GET /api/properties/{property_id}...")
                    response = requests.get(
                        f"{BACKEND_URL}/properties/{property_id}",
                        headers=headers,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        property_detail = response.json()
                        print(f"      ✅ SUCCESS - Property details retrieved")
                        results["get_property"] = {"success": True, "data": property_detail}
                    else:
                        error_msg = f"Get property failed: {response.status_code}"
                        print(f"      ❌ {error_msg}")
                        results["get_property"] = {"success": False, "error": error_msg}
                    
                    # Test 4: Update Property
                    print(f"   ✏️ Testing PUT /api/properties/{property_id}...")
                    update_data = {
                        "name": f"Updated Test Property {int(time.time())}",
                        "area_size": 150.0
                    }
                    
                    response = requests.put(
                        f"{BACKEND_URL}/properties/{property_id}",
                        json=update_data,
                        headers=headers,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        updated_property = response.json()
                        print(f"      ✅ SUCCESS - Property updated")
                        results["update_property"] = {"success": True, "data": updated_property}
                    else:
                        error_msg = f"Update property failed: {response.status_code}"
                        print(f"      ❌ {error_msg}")
                        results["update_property"] = {"success": False, "error": error_msg}
                    
                    # Test 5: Delete Property (Admin only)
                    if user_role == "admin":
                        print(f"   🗑️ Testing DELETE /api/properties/{property_id}...")
                        response = requests.delete(
                            f"{BACKEND_URL}/properties/{property_id}",
                            headers=headers,
                            timeout=15
                        )
                        
                        if response.status_code == 200:
                            print(f"      ✅ SUCCESS - Property deleted")
                            results["delete_property"] = {"success": True, "data": {"deleted": True}}
                        else:
                            error_msg = f"Delete property failed: {response.status_code}"
                            print(f"      ❌ {error_msg}")
                            results["delete_property"] = {"success": False, "error": error_msg}
                    else:
                        results["delete_property"] = {"success": True, "data": {"skipped": "Not admin"}}
            else:
                error_msg = f"Create property failed: {response.status_code}"
                print(f"      ❌ {error_msg}")
                results["create_property"] = {"success": False, "error": error_msg}
        else:
            print("   ⚠️  Skipping property CRUD tests - requires admin/technician role")
            for key in ["create_property", "get_property", "update_property", "delete_property"]:
                results[key] = {"success": True, "data": {"skipped": "Not admin/technician"}}
            
    except Exception as e:
        error_msg = f"Property management API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results


def test_device_management_apis(token: str, user_role: str) -> Dict[str, Any]:
    """Test device management APIs"""
    print(f"\n📱 Testing Device Management APIs ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "list_devices": {"success": False, "error": None, "data": None},
        "comprehensive_devices": {"success": False, "error": None, "data": None},
        "device_stats": {"success": False, "error": None, "data": None},
        "device_activities": {"success": False, "error": None, "data": None},
        "batch_operations": {"success": False, "error": None, "data": None}
    }
    
    try:
        # Test 1: List Devices
        print("   📋 Testing GET /api/devices...")
        response = requests.get(
            f"{BACKEND_URL}/devices",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            devices = response.json()
            print(f"      ✅ SUCCESS - Found {len(devices)} devices")
            results["list_devices"] = {"success": True, "data": devices}
        else:
            error_msg = f"List devices failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["list_devices"] = {"success": False, "error": error_msg}
        
        # Test 2: Comprehensive Device Listing
        print("   📊 Testing GET /api/devices/comprehensive...")
        response = requests.get(
            f"{BACKEND_URL}/devices/comprehensive",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            comprehensive_devices = response.json()
            print(f"      ✅ SUCCESS - Comprehensive device data retrieved")
            results["comprehensive_devices"] = {"success": True, "data": comprehensive_devices}
        else:
            error_msg = f"Comprehensive devices failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["comprehensive_devices"] = {"success": False, "error": error_msg}
        
        # Test device-specific endpoints if we have devices
        if results["list_devices"]["success"] and results["list_devices"]["data"]:
            devices = results["list_devices"]["data"]
            if len(devices) > 0:
                device_id = devices[0].get("id")
                
                # Test 3: Device Statistics
                print(f"   📈 Testing GET /api/devices/{device_id}/stats...")
                response = requests.get(
                    f"{BACKEND_URL}/devices/{device_id}/stats",
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    device_stats = response.json()
                    print(f"      ✅ SUCCESS - Device statistics retrieved")
                    results["device_stats"] = {"success": True, "data": device_stats}
                else:
                    error_msg = f"Device stats failed: {response.status_code}"
                    print(f"      ❌ {error_msg}")
                    results["device_stats"] = {"success": False, "error": error_msg}
                
                # Test 4: Device Activities
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
        
        # Test 5: Batch Operations (Admin/Technician only)
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
            
            if response.status_code == 200:
                batch_result = response.json()
                print(f"      ✅ SUCCESS - Batch operation completed")
                results["batch_operations"] = {"success": True, "data": batch_result}
            else:
                error_msg = f"Batch operations failed: {response.status_code}"
                print(f"      ❌ {error_msg}")
                results["batch_operations"] = {"success": False, "error": error_msg}
        else:
            results["batch_operations"] = {"success": True, "data": {"skipped": "Not admin/technician"}}
            
    except Exception as e:
        error_msg = f"Device management API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results


def test_iot_monitoring_apis(token: str, user_role: str) -> Dict[str, Any]:
    """Test IoT monitoring APIs"""
    print(f"\n🌐 Testing IoT Monitoring APIs ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "list_iot_devices": {"success": False, "error": None, "data": None},
        "register_iot_device": {"success": False, "error": None, "data": None},
        "ingest_iot_data": {"success": False, "error": None, "data": None},
        "device_metrics": {"success": False, "error": None, "data": None}
    }
    
    try:
        # Test 1: List IoT Devices
        print("   📋 Testing GET /api/iot/devices...")
        response = requests.get(
            f"{BACKEND_URL}/iot/devices",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            iot_devices = response.json()
            print(f"      ✅ SUCCESS - Found {len(iot_devices)} IoT devices")
            results["list_iot_devices"] = {"success": True, "data": iot_devices}
        else:
            error_msg = f"List IoT devices failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["list_iot_devices"] = {"success": False, "error": error_msg}
        
        # Test 2: Register IoT Device (Admin/Technician only)
        if user_role in ["admin", "technician"]:
            print("   ➕ Testing POST /api/iot/devices...")
            import time
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
            
            if response.status_code == 201:
                new_device = response.json()
                device_id = new_device.get("device_id")
                print(f"      ✅ SUCCESS - IoT device registered: {device_id}")
                results["register_iot_device"] = {"success": True, "data": new_device}
                
                # Test 3: Ingest IoT Data
                print(f"   📊 Testing POST /api/iot/data...")
                iot_data = {
                    "device_id": device_id,
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
                
                if response.status_code == 200:
                    ingest_result = response.json()
                    print(f"      ✅ SUCCESS - IoT data ingested")
                    results["ingest_iot_data"] = {"success": True, "data": ingest_result}
                else:
                    error_msg = f"IoT data ingest failed: {response.status_code}"
                    print(f"      ❌ {error_msg}")
                    results["ingest_iot_data"] = {"success": False, "error": error_msg}
                
                # Test 4: Device Metrics
                print(f"   📈 Testing GET /api/iot/devices/{device_id}/metrics...")
                response = requests.get(
                    f"{BACKEND_URL}/iot/devices/{device_id}/metrics",
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    metrics = response.json()
                    print(f"      ✅ SUCCESS - Device metrics retrieved")
                    results["device_metrics"] = {"success": True, "data": metrics}
                else:
                    error_msg = f"Device metrics failed: {response.status_code}"
                    print(f"      ❌ {error_msg}")
                    results["device_metrics"] = {"success": False, "error": error_msg}
            else:
                error_msg = f"Register IoT device failed: {response.status_code}"
                print(f"      ❌ {error_msg}")
                results["register_iot_device"] = {"success": False, "error": error_msg}
        else:
            print("   ⚠️  Skipping IoT device registration - requires admin/technician role")
            for key in ["register_iot_device", "ingest_iot_data", "device_metrics"]:
                results[key] = {"success": True, "data": {"skipped": "Not admin/technician"}}
            
    except Exception as e:
        error_msg = f"IoT monitoring API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results


def test_payment_apis(token: str, user_role: str, customer_id: str = None) -> Dict[str, Any]:
    """Test payment APIs"""
    print(f"\n💳 Testing Payment APIs ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "payment_history": {"success": False, "error": None, "data": None},
        "payment_detail": {"success": False, "error": None, "data": None}
    }
    
    try:
        # Test 1: Payment History
        print("   📋 Testing GET /api/payments/history/list...")
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
            
            # Test 2: Payment Detail (if we have transactions)
            if transactions and len(transactions) > 0:
                reference_id = transactions[0].get("reference_id")
                if reference_id:
                    print(f"   🔍 Testing GET /api/payments/{reference_id}...")
                    response = requests.get(
                        f"{BACKEND_URL}/payments/{reference_id}",
                        headers=headers,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        payment_detail = response.json()
                        print(f"      ✅ SUCCESS - Payment detail retrieved")
                        results["payment_detail"] = {"success": True, "data": payment_detail}
                    else:
                        error_msg = f"Payment detail failed: {response.status_code}"
                        print(f"      ❌ {error_msg}")
                        results["payment_detail"] = {"success": False, "error": error_msg}
            else:
                results["payment_detail"] = {"success": True, "data": {"skipped": "No transactions"}}
        else:
            error_msg = f"Payment history failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["payment_history"] = {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"Payment API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results


def test_voucher_apis(token: str, user_role: str) -> Dict[str, Any]:
    """Test voucher APIs"""
    print(f"\n🎫 Testing Voucher APIs ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "list_vouchers": {"success": False, "error": None, "data": None},
        "create_voucher": {"success": False, "error": None, "data": None},
        "validate_voucher": {"success": False, "error": None, "data": None},
        "apply_voucher": {"success": False, "error": None, "data": None},
        "active_vouchers": {"success": False, "error": None, "data": None}
    }
    
    try:
        # Test 1: List Vouchers
        print("   📋 Testing GET /api/vouchers...")
        response = requests.get(
            f"{BACKEND_URL}/vouchers",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            vouchers = response.json()
            print(f"      ✅ SUCCESS - Found {len(vouchers)} vouchers")
            results["list_vouchers"] = {"success": True, "data": vouchers}
        else:
            error_msg = f"List vouchers failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["list_vouchers"] = {"success": False, "error": error_msg}
        
        # Test 2: Create Voucher (Admin only)
        if user_role == "admin":
            print("   ➕ Testing POST /api/vouchers...")
            from datetime import datetime, timedelta
            import time
            
            voucher_data = {
                "code": f"TEST{int(time.time())}",
                "description": "Test voucher for API testing",
                "discount_type": "percentage",
                "discount_value": 15,
                "min_purchase_amount": 50000,
                "max_discount_amount": 100000,
                "usage_limit": 100,
                "per_customer_limit": 2,
                "valid_from": datetime.utcnow().isoformat(),
                "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat()
            }
            
            response = requests.post(
                f"{BACKEND_URL}/vouchers",
                json=voucher_data,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                new_voucher = response.json()
                voucher_code = new_voucher.get("code")
                print(f"      ✅ SUCCESS - Voucher created: {voucher_code}")
                results["create_voucher"] = {"success": True, "data": new_voucher}
                
                # Test 3: Validate Voucher
                print(f"   ✅ Testing POST /api/vouchers/validate...")
                validation_data = {
                    "voucher_code": voucher_code,
                    "purchase_amount": 100000
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/vouchers/validate",
                    json=validation_data,
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    validation_result = response.json()
                    print(f"      ✅ SUCCESS - Voucher validation completed")
                    results["validate_voucher"] = {"success": True, "data": validation_result}
                else:
                    error_msg = f"Voucher validation failed: {response.status_code}"
                    print(f"      ❌ {error_msg}")
                    results["validate_voucher"] = {"success": False, "error": error_msg}
                
                # Test 4: Apply Voucher
                print(f"   🎯 Testing POST /api/vouchers/apply...")
                apply_data = {
                    "voucher_code": voucher_code,
                    "purchase_amount": 100000,
                    "transaction_id": f"TXN{int(time.time())}"
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/vouchers/apply",
                    json=apply_data,
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    apply_result = response.json()
                    print(f"      ✅ SUCCESS - Voucher applied")
                    results["apply_voucher"] = {"success": True, "data": apply_result}
                else:
                    error_msg = f"Voucher apply failed: {response.status_code}"
                    print(f"      ❌ {error_msg}")
                    results["apply_voucher"] = {"success": False, "error": error_msg}
            else:
                error_msg = f"Create voucher failed: {response.status_code}"
                print(f"      ❌ {error_msg}")
                results["create_voucher"] = {"success": False, "error": error_msg}
        else:
            print("   ⚠️  Skipping voucher creation - requires admin role")
            for key in ["create_voucher", "validate_voucher", "apply_voucher"]:
                results[key] = {"success": True, "data": {"skipped": "Not admin"}}
        
        # Test 5: Active Vouchers
        print("   🔍 Testing GET /api/vouchers/active...")
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
        error_msg = f"Voucher API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results


def test_support_tickets_apis(token: str, user_role: str) -> Dict[str, Any]:
    """Test support tickets APIs"""
    print(f"\n🎫 Testing Support Tickets APIs ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "list_tickets": {"success": False, "error": None, "data": None},
        "create_ticket": {"success": False, "error": None, "data": None},
        "get_ticket": {"success": False, "error": None, "data": None},
        "update_ticket": {"success": False, "error": None, "data": None},
        "add_message": {"success": False, "error": None, "data": None},
        "assign_technician": {"success": False, "error": None, "data": None},
        "update_status": {"success": False, "error": None, "data": None},
        "admin_stats": {"success": False, "error": None, "data": None}
    }
    
    try:
        # Test 1: List Tickets
        print("   📋 Testing GET /api/tickets...")
        response = requests.get(
            f"{BACKEND_URL}/tickets",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            tickets = response.json()
            print(f"      ✅ SUCCESS - Found {len(tickets)} tickets")
            results["list_tickets"] = {"success": True, "data": tickets}
        else:
            error_msg = f"List tickets failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["list_tickets"] = {"success": False, "error": error_msg}
        
        # Test 2: Create Ticket
        print("   ➕ Testing POST /api/tickets...")
        import time
        ticket_data = {
            "subject": f"Test Ticket {int(time.time())}",
            "description": "This is a test ticket created via API testing",
            "category": "technical_issue",
            "priority": "medium"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/tickets",
            json=ticket_data,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 201:
            new_ticket = response.json()
            ticket_id = new_ticket.get("id")
            print(f"      ✅ SUCCESS - Ticket created with ID: {ticket_id}")
            results["create_ticket"] = {"success": True, "data": new_ticket}
            
            # Test 3: Get Ticket Detail
            if ticket_id:
                print(f"   🔍 Testing GET /api/tickets/{ticket_id}...")
                response = requests.get(
                    f"{BACKEND_URL}/tickets/{ticket_id}",
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    ticket_detail = response.json()
                    print(f"      ✅ SUCCESS - Ticket details retrieved")
                    results["get_ticket"] = {"success": True, "data": ticket_detail}
                else:
                    error_msg = f"Get ticket failed: {response.status_code}"
                    print(f"      ❌ {error_msg}")
                    results["get_ticket"] = {"success": False, "error": error_msg}
                
                # Test 4: Update Ticket
                print(f"   ✏️ Testing PUT /api/tickets/{ticket_id}...")
                update_data = {
                    "description": "Updated test ticket description",
                    "priority": "high"
                }
                
                response = requests.put(
                    f"{BACKEND_URL}/tickets/{ticket_id}",
                    json=update_data,
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    updated_ticket = response.json()
                    print(f"      ✅ SUCCESS - Ticket updated")
                    results["update_ticket"] = {"success": True, "data": updated_ticket}
                else:
                    error_msg = f"Update ticket failed: {response.status_code}"
                    print(f"      ❌ {error_msg}")
                    results["update_ticket"] = {"success": False, "error": error_msg}
                
                # Test 5: Add Message
                print(f"   💬 Testing POST /api/tickets/{ticket_id}/messages...")
                message_data = {
                    "message": "This is a test message for the ticket",
                    "is_internal": False
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/tickets/{ticket_id}/messages",
                    json=message_data,
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 201:
                    message_result = response.json()
                    print(f"      ✅ SUCCESS - Message added to ticket")
                    results["add_message"] = {"success": True, "data": message_result}
                else:
                    error_msg = f"Add message failed: {response.status_code}"
                    print(f"      ❌ {error_msg}")
                    results["add_message"] = {"success": False, "error": error_msg}
                
                # Admin/Technician specific tests
                if user_role in ["admin", "technician"]:
                    # Test 6: Assign Technician
                    print(f"   👨‍🔧 Testing PATCH /api/tickets/{ticket_id}/assign...")
                    assign_data = {
                        "technician_id": "test-technician-1"
                    }
                    
                    response = requests.patch(
                        f"{BACKEND_URL}/tickets/{ticket_id}/assign",
                        json=assign_data,
                        headers=headers,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        assign_result = response.json()
                        print(f"      ✅ SUCCESS - Technician assigned")
                        results["assign_technician"] = {"success": True, "data": assign_result}
                    else:
                        error_msg = f"Assign technician failed: {response.status_code}"
                        print(f"      ❌ {error_msg}")
                        results["assign_technician"] = {"success": False, "error": error_msg}
                    
                    # Test 7: Update Status
                    print(f"   🔄 Testing PATCH /api/tickets/{ticket_id}/status...")
                    status_data = {
                        "status": "in_progress"
                    }
                    
                    response = requests.patch(
                        f"{BACKEND_URL}/tickets/{ticket_id}/status",
                        json=status_data,
                        headers=headers,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        status_result = response.json()
                        print(f"      ✅ SUCCESS - Status updated")
                        results["update_status"] = {"success": True, "data": status_result}
                    else:
                        error_msg = f"Update status failed: {response.status_code}"
                        print(f"      ❌ {error_msg}")
                        results["update_status"] = {"success": False, "error": error_msg}
                else:
                    for key in ["assign_technician", "update_status"]:
                        results[key] = {"success": True, "data": {"skipped": "Not admin/technician"}}
        else:
            error_msg = f"Create ticket failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["create_ticket"] = {"success": False, "error": error_msg}
        
        # Test 8: Admin Statistics
        if user_role == "admin":
            print("   📊 Testing GET /api/tickets/admin/stats...")
            response = requests.get(
                f"{BACKEND_URL}/tickets/admin/stats",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                admin_stats = response.json()
                print(f"      ✅ SUCCESS - Admin statistics retrieved")
                results["admin_stats"] = {"success": True, "data": admin_stats}
            else:
                error_msg = f"Admin stats failed: {response.status_code}"
                print(f"      ❌ {error_msg}")
                results["admin_stats"] = {"success": False, "error": error_msg}
        else:
            results["admin_stats"] = {"success": True, "data": {"skipped": "Not admin"}}
            
    except Exception as e:
        error_msg = f"Support tickets API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results


def test_water_tips_apis(token: str, user_role: str) -> Dict[str, Any]:
    """Test water conservation tips APIs"""
    print(f"\n💡 Testing Water Conservation Tips APIs ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "list_tips": {"success": False, "error": None, "data": None},
        "create_tip": {"success": False, "error": None, "data": None},
        "update_tip": {"success": False, "error": None, "data": None},
        "delete_tip": {"success": False, "error": None, "data": None},
        "get_tip": {"success": False, "error": None, "data": None},
        "engage_tip": {"success": False, "error": None, "data": None}
    }
    
    try:
        # Test 1: List Tips
        print("   📋 Testing GET /api/tips...")
        response = requests.get(
            f"{BACKEND_URL}/tips",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            tips = response.json()
            print(f"      ✅ SUCCESS - Found {len(tips)} water conservation tips")
            results["list_tips"] = {"success": True, "data": tips}
        else:
            error_msg = f"List tips failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["list_tips"] = {"success": False, "error": error_msg}
        
        # Admin-only tests
        if user_role == "admin":
            # Test 2: Create Tip
            print("   ➕ Testing POST /api/tips/admin/create...")
            import time
            tip_data = {
                "title": f"Test Water Saving Tip {int(time.time())}",
                "description": "This is a test water conservation tip created via API testing",
                "category": "saving_water",
                "difficulty": "easy",
                "estimated_savings_percentage": 15,
                "estimated_time_minutes": 30,
                "implementation_steps": [
                    "Step 1: Turn off the tap while brushing teeth",
                    "Step 2: Use a cup for rinsing instead of running water"
                ],
                "benefits": [
                    "Reduces water consumption",
                    "Lowers water bills"
                ],
                "required_tools": [
                    "Cup for rinsing"
                ]
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
                
                # Test 3: Update Tip
                if tip_id:
                    print(f"   ✏️ Testing PUT /api/tips/admin/{tip_id}...")
                    update_data = {
                        "title": f"Updated Test Water Saving Tip {int(time.time())}",
                        "estimated_savings_percentage": 20
                    }
                    
                    response = requests.put(
                        f"{BACKEND_URL}/tips/admin/{tip_id}",
                        json=update_data,
                        headers=headers,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        updated_tip = response.json()
                        print(f"      ✅ SUCCESS - Tip updated")
                        results["update_tip"] = {"success": True, "data": updated_tip}
                    else:
                        error_msg = f"Update tip failed: {response.status_code}"
                        print(f"      ❌ {error_msg}")
                        results["update_tip"] = {"success": False, "error": error_msg}
                    
                    # Test 4: Get Tip Detail
                    print(f"   🔍 Testing GET /api/tips/{tip_id}...")
                    response = requests.get(
                        f"{BACKEND_URL}/tips/{tip_id}",
                        headers=headers,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        tip_detail = response.json()
                        print(f"      ✅ SUCCESS - Tip details retrieved")
                        results["get_tip"] = {"success": True, "data": tip_detail}
                    else:
                        error_msg = f"Get tip failed: {response.status_code}"
                        print(f"      ❌ {error_msg}")
                        results["get_tip"] = {"success": False, "error": error_msg}
                    
                    # Test 5: Engage with Tip
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
                        engage_result = response.json()
                        print(f"      ✅ SUCCESS - Tip engagement recorded")
                        results["engage_tip"] = {"success": True, "data": engage_result}
                    else:
                        error_msg = f"Engage tip failed: {response.status_code}"
                        print(f"      ❌ {error_msg}")
                        results["engage_tip"] = {"success": False, "error": error_msg}
                    
                    # Test 6: Delete Tip
                    print(f"   🗑️ Testing DELETE /api/tips/admin/{tip_id}...")
                    response = requests.delete(
                        f"{BACKEND_URL}/tips/admin/{tip_id}",
                        headers=headers,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        print(f"      ✅ SUCCESS - Tip deleted")
                        results["delete_tip"] = {"success": True, "data": {"deleted": True}}
                    else:
                        error_msg = f"Delete tip failed: {response.status_code}"
                        print(f"      ❌ {error_msg}")
                        results["delete_tip"] = {"success": False, "error": error_msg}
            else:
                error_msg = f"Create tip failed: {response.status_code}"
                print(f"      ❌ {error_msg}")
                results["create_tip"] = {"success": False, "error": error_msg}
        else:
            print("   ⚠️  Skipping admin tip management - requires admin role")
            for key in ["create_tip", "update_tip", "delete_tip", "get_tip", "engage_tip"]:
                results[key] = {"success": True, "data": {"skipped": "Not admin"}}
            
    except Exception as e:
        error_msg = f"Water tips API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results


def test_role_permission_apis(token: str, user_role: str) -> Dict[str, Any]:
    """Test role and permission APIs"""
    print(f"\n🔐 Testing Role & Permission APIs ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "list_roles": {"success": False, "error": None, "data": None},
        "create_role": {"success": False, "error": None, "data": None},
        "update_role": {"success": False, "error": None, "data": None},
        "delete_role": {"success": False, "error": None, "data": None},
        "assign_role": {"success": False, "error": None, "data": None},
        "list_permissions": {"success": False, "error": None, "data": None}
    }
    
    if user_role != "admin":
        print("   ⚠️  Skipping role & permission tests - requires admin role")
        for key in results:
            results[key] = {"success": True, "data": {"skipped": "Not admin"}}
        return results
    
    try:
        # Test 1: List Roles
        print("   📋 Testing GET /api/roles...")
        response = requests.get(
            f"{BACKEND_URL}/roles",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            roles = response.json()
            print(f"      ✅ SUCCESS - Found {len(roles)} roles")
            results["list_roles"] = {"success": True, "data": roles}
        else:
            error_msg = f"List roles failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["list_roles"] = {"success": False, "error": error_msg}
        
        # Test 2: List Permissions
        print("   🔑 Testing GET /api/permissions...")
        response = requests.get(
            f"{BACKEND_URL}/permissions",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            permissions = response.json()
            print(f"      ✅ SUCCESS - Found {len(permissions)} permissions")
            results["list_permissions"] = {"success": True, "data": permissions}
        else:
            error_msg = f"List permissions failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["list_permissions"] = {"success": False, "error": error_msg}
        
        # Test 3: Create Role
        print("   ➕ Testing POST /api/roles...")
        import time
        role_data = {
            "name": f"test_role_{int(time.time())}",
            "description": "Test role created via API testing",
            "permissions": ["users.view", "customers.view"]
        }
        
        response = requests.post(
            f"{BACKEND_URL}/roles",
            json=role_data,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 201:
            new_role = response.json()
            role_id = new_role.get("id")
            print(f"      ✅ SUCCESS - Role created with ID: {role_id}")
            results["create_role"] = {"success": True, "data": new_role}
            
            # Test 4: Update Role
            if role_id:
                print(f"   ✏️ Testing PUT /api/roles/{role_id}...")
                update_data = {
                    "description": "Updated test role description",
                    "permissions": ["users.view", "customers.view", "properties.view"]
                }
                
                response = requests.put(
                    f"{BACKEND_URL}/roles/{role_id}",
                    json=update_data,
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    updated_role = response.json()
                    print(f"      ✅ SUCCESS - Role updated")
                    results["update_role"] = {"success": True, "data": updated_role}
                else:
                    error_msg = f"Update role failed: {response.status_code}"
                    print(f"      ❌ {error_msg}")
                    results["update_role"] = {"success": False, "error": error_msg}
                
                # Test 5: Assign Role to User
                print(f"   👤 Testing POST /api/roles/{role_id}/assign...")
                assign_data = {
                    "user_id": "test-user-1"
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/roles/{role_id}/assign",
                    json=assign_data,
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    assign_result = response.json()
                    print(f"      ✅ SUCCESS - Role assigned to user")
                    results["assign_role"] = {"success": True, "data": assign_result}
                else:
                    error_msg = f"Assign role failed: {response.status_code}"
                    print(f"      ❌ {error_msg}")
                    results["assign_role"] = {"success": False, "error": error_msg}
                
                # Test 6: Delete Role
                print(f"   🗑️ Testing DELETE /api/roles/{role_id}...")
                response = requests.delete(
                    f"{BACKEND_URL}/roles/{role_id}",
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    print(f"      ✅ SUCCESS - Role deleted")
                    results["delete_role"] = {"success": True, "data": {"deleted": True}}
                else:
                    error_msg = f"Delete role failed: {response.status_code}"
                    print(f"      ❌ {error_msg}")
                    results["delete_role"] = {"success": False, "error": error_msg}
        else:
            error_msg = f"Create role failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["create_role"] = {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"Role & permission API error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results


def test_admin_management_apis(token: str, user_role: str) -> Dict[str, Any]:
    """Test admin management APIs"""
    print(f"\n👑 Testing Admin Management APIs ({user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "dashboard_metrics": {"success": False, "error": None, "data": None},
        "device_monitoring": {"success": False, "error": None, "data": None},
        "bulk_customers": {"success": False, "error": None, "data": None},
        "maintenance_create": {"success": False, "error": None, "data": None},
        "maintenance_list": {"success": False, "error": None, "data": None},
        "revenue_report": {"success": False, "error": None, "data": None}
    }
    
    try:
        # Test 1: Dashboard metrics (Admin only)
        if user_role == "admin":
            print("   📊 Testing GET /api/admin/dashboard/metrics...")
            response = requests.get(
                f"{BACKEND_URL}/admin/dashboard/metrics",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                metrics = response.json()
                required_fields = ["total_customers", "active_customers", "total_devices", "online_devices"]
                missing_fields = [field for field in required_fields if field not in metrics]
                
                if missing_fields:
                    error_msg = f"Missing required fields: {missing_fields}"
                    print(f"      ❌ {error_msg}")
                    results["dashboard_metrics"] = {"success": False, "error": error_msg}
                else:
                    print(f"      ✅ SUCCESS - Customers: {metrics['total_customers']}, Devices: {metrics['total_devices']}")
                    results["dashboard_metrics"] = {"success": True, "data": metrics}
            else:
                error_msg = f"Dashboard metrics failed: {response.status_code}"
                print(f"      ❌ {error_msg}")
                results["dashboard_metrics"] = {"success": False, "error": error_msg}
        else:
            print("   📊 Skipping dashboard metrics - requires admin role")
            results["dashboard_metrics"] = {"success": True, "data": {"skipped": "Not admin"}}
        
        # Test 2: Device monitoring (Admin/Technician)
        if user_role in ["admin", "technician"]:
            print("   🖥️ Testing GET /api/admin/devices/monitoring...")
            response = requests.get(
                f"{BACKEND_URL}/admin/devices/monitoring",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                devices = response.json()
                print(f"      ✅ SUCCESS - Found {len(devices)} devices for monitoring")
                results["device_monitoring"] = {"success": True, "data": devices}
            else:
                error_msg = f"Device monitoring failed: {response.status_code}"
                print(f"      ❌ {error_msg}")
                results["device_monitoring"] = {"success": False, "error": error_msg}
        else:
            print("   🖥️ Skipping device monitoring - requires admin/technician role")
            results["device_monitoring"] = {"success": True, "data": {"skipped": "Not admin/technician"}}
        
        # Test 3: Bulk customer operations (Admin only)
        if user_role == "admin":
            print("   👥 Testing POST /api/admin/customers/bulk...")
            bulk_data = {
                "customer_ids": ["test-customer-1", "test-customer-2"],
                "action": "send_notification",
                "parameters": {
                    "title": "Test Notification",
                    "message": "This is a test notification from bulk operation"
                }
            }
            
            response = requests.post(
                f"{BACKEND_URL}/admin/customers/bulk",
                json=bulk_data,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                bulk_result = response.json()
                print(f"      ✅ SUCCESS - Bulk operation completed")
                results["bulk_customers"] = {"success": True, "data": bulk_result}
            else:
                error_msg = f"Bulk customers failed: {response.status_code}"
                print(f"      ❌ {error_msg}")
                results["bulk_customers"] = {"success": False, "error": error_msg}
        else:
            print("   👥 Skipping bulk customers - requires admin role")
            results["bulk_customers"] = {"success": True, "data": {"skipped": "Not admin"}}
        
        # Test 4: Create maintenance schedule (Admin only)
        if user_role == "admin":
            print("   🔧 Testing POST /api/admin/maintenance...")
            from datetime import datetime, timedelta
            future_date = datetime.utcnow() + timedelta(days=7)
            
            maintenance_data = {
                "device_id": "test-device-1",
                "maintenance_type": "routine_inspection",
                "scheduled_date": future_date.isoformat(),
                "priority": "medium",
                "description": "Routine maintenance check",
                "notes": "Test maintenance schedule"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/admin/maintenance",
                json=maintenance_data,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                maintenance = response.json()
                print(f"      ✅ SUCCESS - Maintenance scheduled")
                results["maintenance_create"] = {"success": True, "data": maintenance}
            else:
                error_msg = f"Maintenance create failed: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('detail', '')}"
                except:
                    pass
                print(f"      ❌ {error_msg}")
                results["maintenance_create"] = {"success": False, "error": error_msg}
        else:
            print("   🔧 Skipping maintenance create - requires admin role")
            results["maintenance_create"] = {"success": True, "data": {"skipped": "Not admin"}}
        
        # Test 5: List maintenance schedules (Admin/Technician)
        if user_role in ["admin", "technician"]:
            print("   📋 Testing GET /api/admin/maintenance...")
            response = requests.get(
                f"{BACKEND_URL}/admin/maintenance",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                schedules = response.json()
                print(f"      ✅ SUCCESS - Found {len(schedules)} maintenance schedules")
                results["maintenance_list"] = {"success": True, "data": schedules}
            else:
                error_msg = f"Maintenance list failed: {response.status_code}"
                print(f"      ❌ {error_msg}")
                results["maintenance_list"] = {"success": False, "error": error_msg}
        else:
            print("   📋 Skipping maintenance list - requires admin/technician role")
            results["maintenance_list"] = {"success": True, "data": {"skipped": "Not admin/technician"}}
        
        # Test 6: Revenue report (Admin only)
        if user_role == "admin":
            print("   💰 Testing GET /api/admin/revenue/report...")
            response = requests.get(
                f"{BACKEND_URL}/admin/revenue/report?period=monthly",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                revenue = response.json()
                required_fields = ["total_revenue", "total_transactions", "revenue_by_payment_method"]
                missing_fields = [field for field in required_fields if field not in revenue]
                
                if missing_fields:
                    error_msg = f"Missing required fields: {missing_fields}"
                    print(f"      ❌ {error_msg}")
                    results["revenue_report"] = {"success": False, "error": error_msg}
                else:
                    print(f"      ✅ SUCCESS - Revenue: Rp {revenue['total_revenue']:,.2f}, Transactions: {revenue['total_transactions']}")
                    results["revenue_report"] = {"success": True, "data": revenue}
            else:
                error_msg = f"Revenue report failed: {response.status_code}"
                print(f"      ❌ {error_msg}")
                results["revenue_report"] = {"success": False, "error": error_msg}
        else:
            print("   💰 Skipping revenue report - requires admin role")
            results["revenue_report"] = {"success": True, "data": {"skipped": "Not admin"}}
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Connection error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"   ❌ {error_msg}")
        for key in results:
            if not results[key]["success"]:
                results[key]["error"] = error_msg
    
    return results


def test_comprehensive_backend_apis():
    """Test ALL backend API endpoints comprehensively as requested"""
    print("=" * 80)
    print("🧪 COMPREHENSIVE BACKEND API TESTING - Water Management System")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    
    # Test accounts
    test_accounts = [
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
    
    all_results = {}
    
    for account in test_accounts:
        print(f"\n{'='*60}")
        print(f"🔐 Testing {account['name']} Account")
        print(f"{'='*60}")
        
        # Login
        login_result = test_login(
            account["email"],
            account["password"], 
            account["expected_role"],
            account["name"]
        )
        
        if not login_result["success"]:
            print(f"\n❌ CRITICAL: {account['name']} login failed - skipping tests")
            all_results[account["name"]] = {"login": False}
            continue
        
        token = login_result["token"]
        user = login_result["user"]
        user_role = user["role"]
        customer_id = user["id"] if user_role == "customer" else None
        
        print(f"\n✅ {account['name']} login successful - Role: {user_role}")
        
        # Test Dashboard APIs
        dashboard_results = test_dashboard_apis(token, user_role)
        
        # Test User Management APIs
        user_mgmt_results = test_user_management_apis(token, user_role)
        
        # Test Customer Management APIs
        customer_mgmt_results = test_customer_management_apis(token, user_role)
        
        # Test Property Management APIs
        property_results = test_property_management_apis(token, user_role)
        
        # Test Device Management APIs
        device_results = test_device_management_apis(token, user_role)
        
        # Test IoT Monitoring APIs
        iot_results = test_iot_monitoring_apis(token, user_role)
        
        # Test Analytics APIs
        analytics_results = test_analytics_api(token, user_role, customer_id)
        
        # Test Payment APIs
        payment_results = test_payment_apis(token, user_role, customer_id)
        
        # Test Voucher APIs
        voucher_results = test_voucher_apis(token, user_role)
        
        # Test Support Tickets APIs
        support_results = test_support_tickets_apis(token, user_role)
        
        # Test Water Conservation Tips APIs
        tips_results = test_water_tips_apis(token, user_role)
        
        # Test Alert & Notification System
        alert_results = test_alert_notification_apis(token, user_role, customer_id)
        
        # Test Report Generation
        report_results = test_report_generation_api(token, user_role, customer_id)
        
        # Test Admin Management APIs
        admin_results = test_admin_management_apis(token, user_role)
        
        # Test Role & Permission APIs
        role_results = test_role_permission_apis(token, user_role)
        
        all_results[account["name"]] = {
            "login": True,
            "dashboard": dashboard_results,
            "user_management": user_mgmt_results,
            "customer_management": customer_mgmt_results,
            "property_management": property_results,
            "device_management": device_results,
            "iot_monitoring": iot_results,
            "analytics": analytics_results,
            "payments": payment_results,
            "vouchers": voucher_results,
            "support_tickets": support_results,
            "water_tips": tips_results,
            "alerts": alert_results,
            "reports": report_results,
            "admin": admin_results,
            "roles": role_results
        }
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE BACKEND API TEST SUMMARY")
    print("=" * 80)
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for account_name, account_results in all_results.items():
        print(f"\n{account_name} Account:")
        
        if not account_results["login"]:
            print("  ❌ Login failed - tests skipped")
            continue
        
        # Test all categories
        categories = ["dashboard", "user_management", "customer_management", "property_management", 
                     "device_management", "iot_monitoring", "analytics", "payments", "vouchers", 
                     "support_tickets", "water_tips", "alerts", "reports", "admin", "roles"]
        
        for category in categories:
            if category in account_results:
                category_results = account_results[category]
                for test_name, result in category_results.items():
                    total_tests += 1
                    if result["success"]:
                        passed_tests += 1
                        status = "✅ PASS"
                    else:
                        status = "❌ FAIL"
                        failed_tests.append(f"{account_name} - {category}: {test_name}")
                    
                    print(f"  {status} - {category.replace('_', ' ').title()}: {test_name}")
                    if not result["success"] and result["error"]:
                        print(f"        Error: {result['error']}")
    
    print(f"\nOverall Results: {passed_tests}/{total_tests} tests passed")
    
    if failed_tests:
        print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
        for failed_test in failed_tests:
            print(f"  - {failed_test}")
    
    if passed_tests == total_tests:
        print("🎉 ALL BACKEND API TESTS PASSED!")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - Check errors above")
        return False


def test_analytics_and_reports():
    """Test analytics and report generation for both admin and customer"""
    print("=" * 80)
    print("🧪 ANALYTICS & REPORTING API TESTING - IndoWater Solution")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    
    # Test accounts
    test_accounts = [
        {
            "name": "Admin",
            "email": "admin@indowater.com",
            "password": "admin123",
            "expected_role": "admin"
        },
        {
            "name": "Customer",
            "email": "customer@indowater.com", 
            "password": "customer123",
            "expected_role": "customer"
        }
    ]
    
    all_results = {}
    
    for account in test_accounts:
        print(f"\n{'='*60}")
        print(f"🔐 Testing {account['name']} Account")
        print(f"{'='*60}")
        
        # Login
        login_result = test_login(
            account["email"],
            account["password"], 
            account["expected_role"],
            account["name"]
        )
        
        if not login_result["success"]:
            print(f"\n❌ CRITICAL: {account['name']} login failed - skipping tests")
            all_results[account["name"]] = {"login": False, "analytics": {}, "reports": {}}
            continue
        
        token = login_result["token"]
        user = login_result["user"]
        user_role = user["role"]
        customer_id = user["id"] if user_role == "customer" else None
        
        print(f"\n✅ {account['name']} login successful - Role: {user_role}")
        
        # Test Analytics APIs
        analytics_results = test_analytics_api(token, user_role, customer_id)
        
        # Test Report Generation
        report_results = test_report_generation_api(token, user_role, customer_id)
        
        all_results[account["name"]] = {
            "login": True,
            "analytics": analytics_results,
            "reports": report_results
        }
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 ANALYTICS & REPORTING TEST SUMMARY")
    print("=" * 80)
    
    total_tests = 0
    passed_tests = 0
    
    for account_name, account_results in all_results.items():
        print(f"\n{account_name} Account:")
        
        if not account_results["login"]:
            print("  ❌ Login failed - tests skipped")
            continue
        
        # Analytics tests
        analytics = account_results["analytics"]
        for test_name, result in analytics.items():
            total_tests += 1
            if result["success"]:
                passed_tests += 1
                status = "✅ PASS"
            else:
                status = "❌ FAIL"
            
            print(f"  {status} - Analytics: {test_name}")
            if not result["success"] and result["error"]:
                print(f"        Error: {result['error']}")
        
        # Report tests
        reports = account_results["reports"]
        for test_name, result in reports.items():
            total_tests += 1
            if result["success"]:
                passed_tests += 1
                status = "✅ PASS"
            else:
                status = "❌ FAIL"
            
            print(f"  {status} - Reports: {test_name}")
            if not result["success"] and result["error"]:
                print(f"        Error: {result['error']}")
    
    print(f"\nOverall Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL ANALYTICS & REPORTING TESTS PASSED!")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - Check errors above")
        return False


def test_customer_payment_apis():
    """Test customer login and payment APIs"""
    print("=" * 70)
    print("🧪 PAYMENT HISTORY API TESTING - IndoWater Solution")
    print("=" * 70)
    print(f"Backend URL: {BACKEND_URL}")
    
    # First login as customer
    customer_account = {
        "name": "Customer",
        "email": "customer@indowater.com", 
        "password": "customer123",
        "expected_role": "customer"
    }
    
    login_result = test_login(
        customer_account["email"],
        customer_account["password"], 
        customer_account["expected_role"],
        customer_account["name"]
    )
    
    if not login_result["success"]:
        print("\n❌ CRITICAL: Customer login failed - cannot test payment APIs")
        return False
    
    # Extract token and customer info
    token = login_result["token"]
    user = login_result["user"]
    customer_id = user["id"]
    
    print(f"\n✅ Customer login successful - ID: {customer_id}")
    
    # Test payment APIs
    payment_results = test_payment_history_api(token, customer_id)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 PAYMENT API TEST SUMMARY")
    print("=" * 70)
    
    test_cases = [
        ("Payment History List", payment_results["history_list"]),
        ("Status Filtering", payment_results["history_filters"]),
        ("Pagination", payment_results["history_pagination"]),
        ("Transaction Detail", payment_results["transaction_detail"])
    ]
    
    success_count = 0
    for test_name, result in test_cases:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not result["success"] and result["error"]:
            print(f"      Error: {result['error']}")
        
        if result["success"]:
            success_count += 1
    
    print(f"\nResults: {success_count}/{len(test_cases)} payment API tests passed")
    
    if success_count == len(test_cases):
        print("🎉 ALL PAYMENT API TESTS PASSED!")
        return True
    else:
        print("⚠️  SOME PAYMENT API TESTS FAILED - Check errors above")
        return False


def test_voucher_and_customer_management_fixes():
    """Test voucher and customer management APIs to verify the fixes"""
    print("=" * 80)
    print("🎫 VOUCHER & CUSTOMER MANAGEMENT API TESTING - Fix Verification")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    
    # Test accounts needed
    admin_account = {
        "name": "Admin",
        "email": "admin@indowater.com",
        "password": "admin123",
        "expected_role": "admin"
    }
    
    technician_account = {
        "name": "Technician",
        "email": "technician@indowater.com",
        "password": "tech123",
        "expected_role": "technician"
    }
    
    customer_account = {
        "name": "Customer",
        "email": "customer@indowater.com", 
        "password": "customer123",
        "expected_role": "customer"
    }
    
    results = {
        "admin_login": {"success": False, "error": None},
        "technician_login": {"success": False, "error": None},
        "customer_login": {"success": False, "error": None},
        "voucher_get_no_slash": {"success": False, "error": None},
        "voucher_get_with_slash": {"success": False, "error": None},
        "voucher_get_status_filter": {"success": False, "error": None},
        "voucher_post": {"success": False, "error": None},
        "customer_get_no_slash": {"success": False, "error": None},
        "customer_get_with_slash": {"success": False, "error": None},
        "customer_post": {"success": False, "error": None}
    }
    
    # Step 1: Login as Admin
    print(f"\n🔐 STEP 1: Admin Login...")
    admin_login = test_login(
        admin_account["email"],
        admin_account["password"], 
        admin_account["expected_role"],
        admin_account["name"]
    )
    
    if not admin_login["success"]:
        print(f"❌ CRITICAL: Admin login failed - {admin_login['error']}")
        results["admin_login"] = {"success": False, "error": admin_login["error"]}
        return results
    
    admin_token = admin_login["token"]
    results["admin_login"] = {"success": True, "error": None}
    print(f"✅ Admin login successful")
    
    # Step 2: Login as Customer
    print(f"\n🔐 STEP 2: Customer Login...")
    customer_login = test_login(
        customer_account["email"],
        customer_account["password"], 
        customer_account["expected_role"],
        customer_account["name"]
    )
    
    if not customer_login["success"]:
        print(f"❌ CRITICAL: Customer login failed - {customer_login['error']}")
        results["customer_login"] = {"success": False, "error": customer_login["error"]}
        return results
    
    customer_token = customer_login["token"]
    results["customer_login"] = {"success": True, "error": None}
    print(f"✅ Customer login successful")
    
    # Step 3: Create Voucher (HIGH PRIORITY TEST)
    print(f"\n🎫 STEP 3: Create Voucher (POST /api/vouchers) - HIGH PRIORITY...")
    
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    valid_from = now
    valid_until = now + timedelta(days=30)
    
    voucher_data = {
        "code": "TESTFIX2025",
        "description": "Test voucher after fix",
        "discount_type": "percentage",
        "discount_value": 25,
        "min_purchase_amount": 100000,
        "max_discount_amount": 150000,
        "usage_limit": 50,
        "per_customer_limit": 1,
        "valid_from": valid_from.isoformat(),
        "valid_until": valid_until.isoformat()
    }
    
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"   Creating voucher: {voucher_data['code']}")
        print(f"   Discount: {voucher_data['discount_value']}% (max {voucher_data['max_discount_amount']:,} IDR)")
        print(f"   Min purchase: {voucher_data['min_purchase_amount']:,} IDR")
        
        response = requests.post(
            f"{BACKEND_URL}/vouchers/",
            json=voucher_data,
            headers=headers,
            timeout=15
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            voucher_response = response.json()
            
            # Validate response structure
            required_fields = ["id", "code", "description", "discount_type", "discount_value", 
                             "min_purchase_amount", "max_discount_amount", "usage_limit", 
                             "per_customer_limit", "valid_from", "valid_until", "status"]
            missing_fields = [field for field in required_fields if field not in voucher_response]
            
            if missing_fields:
                error_msg = f"Missing required fields in response: {missing_fields}"
                print(f"   ❌ {error_msg}")
                results["voucher_creation"] = {"success": False, "error": error_msg}
            else:
                voucher_id = voucher_response["id"]
                print(f"   ✅ SUCCESS - Voucher created with ID: {voucher_id}")
                print(f"   ✅ Code: {voucher_response['code']}, Status: {voucher_response['status']}")
                results["voucher_creation"] = {"success": True, "error": None, "voucher_id": voucher_id}
        else:
            error_msg = f"Voucher creation failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                error_msg += f" - {response.text}"
            print(f"   ❌ {error_msg}")
            results["voucher_creation"] = {"success": False, "error": error_msg}
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Connection error: {str(e)}"
        print(f"   ❌ {error_msg}")
        results["voucher_creation"] = {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"   ❌ {error_msg}")
        results["voucher_creation"] = {"success": False, "error": error_msg}
    
    # Step 4: List Vouchers (GET /api/vouchers)
    print(f"\n📋 STEP 4: List Vouchers (GET /api/vouchers)...")
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/vouchers/",
            headers=headers,
            timeout=15
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            vouchers = response.json()
            
            if isinstance(vouchers, list):
                print(f"   ✅ SUCCESS - Found {len(vouchers)} vouchers")
                
                # Check if our newly created voucher is in the list
                testfix_voucher = next((v for v in vouchers if v.get("code") == "TESTFIX2025"), None)
                if testfix_voucher:
                    print(f"   ✅ TESTFIX2025 voucher found in list")
                else:
                    print(f"   ⚠️  TESTFIX2025 voucher not found in list")
                
                # Check for existing TEST1760376128 voucher mentioned in requirements
                test_old_voucher = next((v for v in vouchers if v.get("code") == "TEST1760376128"), None)
                if test_old_voucher:
                    print(f"   ✅ TEST1760376128 voucher found in list")
                else:
                    print(f"   ⚠️  TEST1760376128 voucher not found in list")
                
                results["voucher_list"] = {"success": True, "error": None}
            else:
                error_msg = f"Expected list response, got: {type(vouchers)}"
                print(f"   ❌ {error_msg}")
                results["voucher_list"] = {"success": False, "error": error_msg}
        else:
            error_msg = f"List vouchers failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                error_msg += f" - {response.text}"
            print(f"   ❌ {error_msg}")
            results["voucher_list"] = {"success": False, "error": error_msg}
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Connection error: {str(e)}"
        print(f"   ❌ {error_msg}")
        results["voucher_list"] = {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"   ❌ {error_msg}")
        results["voucher_list"] = {"success": False, "error": error_msg}
    
    # Step 5: List Vouchers with Filter (GET /api/vouchers?status=active)
    print(f"\n🔍 STEP 5: List Active Vouchers (GET /api/vouchers?status=active)...")
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/vouchers/?status=active",
            headers=headers,
            timeout=15
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            active_vouchers = response.json()
            
            if isinstance(active_vouchers, list):
                active_count = len([v for v in active_vouchers if v.get("status") == "active"])
                print(f"   ✅ SUCCESS - Found {len(active_vouchers)} vouchers ({active_count} active)")
                results["voucher_list_filter"] = {"success": True, "error": None}
            else:
                error_msg = f"Expected list response, got: {type(active_vouchers)}"
                print(f"   ❌ {error_msg}")
                results["voucher_list_filter"] = {"success": False, "error": error_msg}
        else:
            error_msg = f"Filter vouchers failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                error_msg += f" - {response.text}"
            print(f"   ❌ {error_msg}")
            results["voucher_list_filter"] = {"success": False, "error": error_msg}
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Connection error: {str(e)}"
        print(f"   ❌ {error_msg}")
        results["voucher_list_filter"] = {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"   ❌ {error_msg}")
        results["voucher_list_filter"] = {"success": False, "error": error_msg}
    
    # Step 6: Validate Voucher as Customer (POST /api/vouchers/validate)
    print(f"\n✅ STEP 6: Validate Voucher as Customer (POST /api/vouchers/validate)...")
    
    customer_headers = {
        "Authorization": f"Bearer {customer_token}",
        "Content-Type": "application/json"
    }
    
    validation_data = {
        "voucher_code": "TESTFIX2025",
        "purchase_amount": 200000  # 200,000 IDR (above min purchase of 100,000)
    }
    
    try:
        print(f"   Validating voucher: {validation_data['voucher_code']}")
        print(f"   Purchase amount: {validation_data['purchase_amount']:,} IDR")
        
        response = requests.post(
            f"{BACKEND_URL}/vouchers/validate",
            json=validation_data,
            headers=customer_headers,
            timeout=15
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            validation_response = response.json()
            
            # Validate response structure
            required_fields = ["valid", "message", "discount_amount", "final_amount"]
            missing_fields = [field for field in required_fields if field not in validation_response]
            
            if missing_fields:
                error_msg = f"Missing required fields in validation response: {missing_fields}"
                print(f"   ❌ {error_msg}")
                results["voucher_validation"] = {"success": False, "error": error_msg}
            else:
                is_valid = validation_response["valid"]
                message = validation_response["message"]
                discount_amount = validation_response["discount_amount"]
                final_amount = validation_response["final_amount"]
                
                if is_valid:
                    expected_discount = 200000 * 0.25  # 25% of 200,000 = 50,000
                    expected_discount = min(expected_discount, 150000)  # Cap at max_discount_amount
                    expected_final = 200000 - expected_discount
                    
                    print(f"   ✅ SUCCESS - Voucher is valid")
                    print(f"   ✅ Message: {message}")
                    print(f"   ✅ Discount: {discount_amount:,.0f} IDR (expected: {expected_discount:,.0f})")
                    print(f"   ✅ Final amount: {final_amount:,.0f} IDR (expected: {expected_final:,.0f})")
                    
                    # Verify discount calculation
                    if abs(discount_amount - expected_discount) < 1:  # Allow small floating point differences
                        print(f"   ✅ Discount calculation correct")
                        results["voucher_validation"] = {"success": True, "error": None}
                    else:
                        error_msg = f"Discount calculation incorrect. Expected: {expected_discount}, Got: {discount_amount}"
                        print(f"   ❌ {error_msg}")
                        results["voucher_validation"] = {"success": False, "error": error_msg}
                else:
                    error_msg = f"Voucher validation failed: {message}"
                    print(f"   ❌ {error_msg}")
                    results["voucher_validation"] = {"success": False, "error": error_msg}
        else:
            error_msg = f"Voucher validation failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                error_msg += f" - {response.text}"
            print(f"   ❌ {error_msg}")
            results["voucher_validation"] = {"success": False, "error": error_msg}
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Connection error: {str(e)}"
        print(f"   ❌ {error_msg}")
        results["voucher_validation"] = {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"   ❌ {error_msg}")
        results["voucher_validation"] = {"success": False, "error": error_msg}
    
    return results


def main():
    """Run comprehensive Phase 2 backend API testing"""
    print("=" * 80)
    print("🧪 COMPREHENSIVE PHASE 2 BACKEND TESTING - IndoWater Solution")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print("\nTesting Features:")
    print("  1. Analytics APIs (usage, trends, predictions, comparison, admin overview)")
    print("  2. Report Generation APIs (PDF/Excel export)")
    print("  3. Alert & Notification System (alerts, leak detection, tampering, tips)")
    print("  4. Admin Management APIs (dashboard metrics, device monitoring, bulk operations, maintenance, revenue reports)")
    
    # Run comprehensive Phase 2 testing
    phase2_success = test_comprehensive_phase2_apis()
    
    # Also run existing voucher tests for completeness
    print(f"\n🎫 ADDITIONAL: Testing Voucher System APIs...")
    voucher_results = test_voucher_system_apis()
    
    # Voucher Test Summary
    print("\n" + "=" * 80)

def test_voucher_and_customer_management_fixes():
    """Test voucher and customer management APIs to verify the fixes"""
    print("=" * 80)
    print("🎫 VOUCHER & CUSTOMER MANAGEMENT API TESTING - Fix Verification")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    
    # Test accounts needed
    admin_account = {
        "name": "Admin",
        "email": "admin@indowater.com",
        "password": "admin123",
        "expected_role": "admin"
    }
    
    technician_account = {
        "name": "Technician",
        "email": "technician@indowater.com",
        "password": "tech123",
        "expected_role": "technician"
    }
    
    customer_account = {
        "name": "Customer",
        "email": "customer@indowater.com", 
        "password": "customer123",
        "expected_role": "customer"
    }
    
    results = {
        "admin_login": {"success": False, "error": None},
        "technician_login": {"success": False, "error": None},
        "customer_login": {"success": False, "error": None},
        "voucher_get_no_slash": {"success": False, "error": None},
        "voucher_get_with_slash": {"success": False, "error": None},
        "voucher_get_status_filter": {"success": False, "error": None},
        "voucher_post": {"success": False, "error": None},
        "customer_get_no_slash": {"success": False, "error": None},
        "customer_get_with_slash": {"success": False, "error": None},
        "customer_post": {"success": False, "error": None}
    }
    
    # Step 1: Login as all three roles
    print(f"\n🔐 STEP 1: Testing Login for All Roles...")
    
    # Admin login
    admin_login = test_login(
        admin_account["email"],
        admin_account["password"], 
        admin_account["expected_role"],
        admin_account["name"]
    )
    
    if admin_login["success"]:
        admin_token = admin_login["token"]
        results["admin_login"] = {"success": True, "error": None}
        print(f"✅ Admin login successful")
    else:
        results["admin_login"] = {"success": False, "error": admin_login["error"]}
        print(f"❌ Admin login failed: {admin_login['error']}")
    
    # Technician login
    technician_login = test_login(
        technician_account["email"],
        technician_account["password"], 
        technician_account["expected_role"],
        technician_account["name"]
    )
    
    if technician_login["success"]:
        technician_token = technician_login["token"]
        results["technician_login"] = {"success": True, "error": None}
        print(f"✅ Technician login successful")
    else:
        results["technician_login"] = {"success": False, "error": technician_login["error"]}
        print(f"❌ Technician login failed: {technician_login['error']}")
    
    # Customer login
    customer_login = test_login(
        customer_account["email"],
        customer_account["password"], 
        customer_account["expected_role"],
        customer_account["name"]
    )
    
    if customer_login["success"]:
        customer_token = customer_login["token"]
        results["customer_login"] = {"success": True, "error": None}
        print(f"✅ Customer login successful")
    else:
        results["customer_login"] = {"success": False, "error": customer_login["error"]}
        print(f"❌ Customer login failed: {customer_login['error']}")
    
    # Step 2: Test Voucher Management APIs (Admin only)
    if admin_login["success"]:
        print(f"\n🎫 STEP 2: Testing Voucher Management APIs (Admin)...")
        
        admin_headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
        
        # Test GET /api/vouchers (without trailing slash)
        print(f"   📋 Testing GET /api/vouchers (no trailing slash)...")
        try:
            response = requests.get(f"{BACKEND_URL}/vouchers", headers=admin_headers, timeout=15)
            print(f"      Status Code: {response.status_code}")
            
            if response.status_code == 200:
                vouchers = response.json()
                print(f"      ✅ SUCCESS - Found {len(vouchers)} vouchers")
                results["voucher_get_no_slash"] = {"success": True, "error": None}
            elif response.status_code == 307:
                print(f"      ❌ REDIRECT ERROR (307) - This should be fixed")
                results["voucher_get_no_slash"] = {"success": False, "error": "307 redirect error"}
            else:
                error_msg = f"Failed with status {response.status_code}"
                print(f"      ❌ {error_msg}")
                results["voucher_get_no_slash"] = {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            print(f"      ❌ {error_msg}")
            results["voucher_get_no_slash"] = {"success": False, "error": error_msg}
        
        # Test GET /api/vouchers/ (with trailing slash)
        print(f"   📋 Testing GET /api/vouchers/ (with trailing slash)...")
        try:
            response = requests.get(f"{BACKEND_URL}/vouchers/", headers=admin_headers, timeout=15)
            print(f"      Status Code: {response.status_code}")
            
            if response.status_code == 200:
                vouchers = response.json()
                print(f"      ✅ SUCCESS - Found {len(vouchers)} vouchers")
                results["voucher_get_with_slash"] = {"success": True, "error": None}
            elif response.status_code == 307:
                print(f"      ❌ REDIRECT ERROR (307) - This should be fixed")
                results["voucher_get_with_slash"] = {"success": False, "error": "307 redirect error"}
            else:
                error_msg = f"Failed with status {response.status_code}"
                print(f"      ❌ {error_msg}")
                results["voucher_get_with_slash"] = {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            print(f"      ❌ {error_msg}")
            results["voucher_get_with_slash"] = {"success": False, "error": error_msg}
        
        # Test GET /api/vouchers?voucher_status=active (status parameter)
        print(f"   🔍 Testing GET /api/vouchers?voucher_status=active (status filter)...")
        try:
            response = requests.get(f"{BACKEND_URL}/vouchers?voucher_status=active", headers=admin_headers, timeout=15)
            print(f"      Status Code: {response.status_code}")
            
            if response.status_code == 200:
                vouchers = response.json()
                active_count = len([v for v in vouchers if v.get("status") == "active"])
                print(f"      ✅ SUCCESS - Found {len(vouchers)} vouchers ({active_count} active)")
                results["voucher_get_status_filter"] = {"success": True, "error": None}
            elif response.status_code == 500:
                print(f"      ❌ INTERNAL SERVER ERROR (500) - Status parameter conflict should be fixed")
                results["voucher_get_status_filter"] = {"success": False, "error": "500 internal server error - status parameter conflict"}
            else:
                error_msg = f"Failed with status {response.status_code}"
                print(f"      ❌ {error_msg}")
                results["voucher_get_status_filter"] = {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            print(f"      ❌ {error_msg}")
            results["voucher_get_status_filter"] = {"success": False, "error": error_msg}
        
        # Test POST /api/vouchers (create new voucher)
        print(f"   ➕ Testing POST /api/vouchers (create voucher)...")
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        
        voucher_data = {
            "code": f"TESTFIX{int(now.timestamp())}",
            "description": "Test voucher for fix verification",
            "discount_type": "percentage",
            "discount_value": 15,
            "min_purchase_amount": 50000,
            "max_discount_amount": 75000,
            "usage_limit": 100,
            "per_customer_limit": 2,
            "valid_from": now.isoformat(),
            "valid_until": (now + timedelta(days=30)).isoformat()
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/vouchers", json=voucher_data, headers=admin_headers, timeout=15)
            print(f"      Status Code: {response.status_code}")
            
            if response.status_code == 200:
                voucher = response.json()
                print(f"      ✅ SUCCESS - Created voucher: {voucher.get('code')}")
                results["voucher_post"] = {"success": True, "error": None}
            elif response.status_code == 500:
                print(f"      ❌ INTERNAL SERVER ERROR (500) - This should be fixed")
                results["voucher_post"] = {"success": False, "error": "500 internal server error"}
            else:
                error_msg = f"Failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('detail', '')}"
                except:
                    pass
                print(f"      ❌ {error_msg}")
                results["voucher_post"] = {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            print(f"      ❌ {error_msg}")
            results["voucher_post"] = {"success": False, "error": error_msg}
    
    # Step 3: Test Customer Management APIs (Admin and Technician)
    if admin_login["success"] or technician_login["success"]:
        print(f"\n👥 STEP 3: Testing Customer Management APIs...")
        
        # Use admin token if available, otherwise technician
        test_token = admin_token if admin_login["success"] else technician_token
        test_role = "Admin" if admin_login["success"] else "Technician"
        
        test_headers = {
            "Authorization": f"Bearer {test_token}",
            "Content-Type": "application/json"
        }
        
        # Test GET /api/customers (without trailing slash)
        print(f"   👤 Testing GET /api/customers (no trailing slash) - {test_role}...")
        try:
            response = requests.get(f"{BACKEND_URL}/customers", headers=test_headers, timeout=15)
            print(f"      Status Code: {response.status_code}")
            
            if response.status_code == 200:
                customers = response.json()
                print(f"      ✅ SUCCESS - Found {len(customers)} customers")
                results["customer_get_no_slash"] = {"success": True, "error": None}
            elif response.status_code == 307:
                print(f"      ❌ REDIRECT ERROR (307) - This should be fixed")
                results["customer_get_no_slash"] = {"success": False, "error": "307 redirect error"}
            else:
                error_msg = f"Failed with status {response.status_code}"
                print(f"      ❌ {error_msg}")
                results["customer_get_no_slash"] = {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            print(f"      ❌ {error_msg}")
            results["customer_get_no_slash"] = {"success": False, "error": error_msg}
        
        # Test GET /api/customers/ (with trailing slash)
        print(f"   👤 Testing GET /api/customers/ (with trailing slash) - {test_role}...")
        try:
            response = requests.get(f"{BACKEND_URL}/customers/", headers=test_headers, timeout=15)
            print(f"      Status Code: {response.status_code}")
            
            if response.status_code == 200:
                customers = response.json()
                print(f"      ✅ SUCCESS - Found {len(customers)} customers")
                results["customer_get_with_slash"] = {"success": True, "error": None}
            elif response.status_code == 307:
                print(f"      ❌ REDIRECT ERROR (307) - This should be fixed")
                results["customer_get_with_slash"] = {"success": False, "error": "307 redirect error"}
            else:
                error_msg = f"Failed with status {response.status_code}"
                print(f"      ❌ {error_msg}")
                results["customer_get_with_slash"] = {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            print(f"      ❌ {error_msg}")
            results["customer_get_with_slash"] = {"success": False, "error": error_msg}
        
        # Test POST /api/customers (create new customer) - Admin only
        if admin_login["success"]:
            print(f"   ➕ Testing POST /api/customers (create customer) - Admin...")
            
            customer_data = {
                "full_name": "Test Customer Fix Verification",
                "email": f"testcustomer{int(now.timestamp())}@example.com",
                "password": "testpass123",
                "phone": "+62812345678",
                "address": "Test Address 123",
                "is_active": True
            }
            
            try:
                response = requests.post(f"{BACKEND_URL}/customers", json=customer_data, headers=admin_headers, timeout=15)
                print(f"      Status Code: {response.status_code}")
                
                if response.status_code == 201:
                    customer = response.json()
                    print(f"      ✅ SUCCESS - Created customer: {customer.get('customer_number')}")
                    results["customer_post"] = {"success": True, "error": None}
                elif response.status_code == 500:
                    print(f"      ❌ INTERNAL SERVER ERROR (500) - This should be fixed")
                    results["customer_post"] = {"success": False, "error": "500 internal server error"}
                else:
                    error_msg = f"Failed with status {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg += f" - {error_data.get('detail', '')}"
                    except:
                        pass
                    print(f"      ❌ {error_msg}")
                    results["customer_post"] = {"success": False, "error": error_msg}
            except Exception as e:
                error_msg = f"Exception: {str(e)}"
                print(f"      ❌ {error_msg}")
                results["customer_post"] = {"success": False, "error": error_msg}
        else:
            print(f"   ⏭️  Skipping POST /api/customers - Admin login required")
            results["customer_post"] = {"success": True, "error": "Skipped - Admin required"}
    
    return results
    print("🎫 VOUCHER SYSTEM TEST SUMMARY")
    print("=" * 80)
    
    voucher_test_cases = [
        ("Admin Login", voucher_results["admin_login"]),
        ("Customer Login", voucher_results["customer_login"]),
        ("Voucher Creation (POST /api/vouchers)", voucher_results["voucher_creation"]),
        ("List Vouchers (GET /api/vouchers)", voucher_results["voucher_list"]),
        ("Filter Active Vouchers", voucher_results["voucher_list_filter"]),
        ("Voucher Validation (POST /api/vouchers/validate)", voucher_results["voucher_validation"])
    ]
    
    voucher_success_count = 0
    for test_name, result in voucher_test_cases:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not result["success"] and result["error"]:
            print(f"      Error: {result['error']}")
        
        if result["success"]:
            voucher_success_count += 1
    
    voucher_all_passed = voucher_success_count == len(voucher_test_cases)
    
    # Final Summary
    print("\n" + "=" * 80)
    print("🏁 FINAL COMPREHENSIVE TEST SUMMARY")
    print("=" * 80)
    
    phase2_status = "✅ PASS" if phase2_success else "❌ FAIL"
    voucher_status = "✅ PASS" if voucher_all_passed else "❌ FAIL"
    
    print(f"{phase2_status} - Phase 2 APIs (Analytics, Reports, Alerts, Admin Management)")
    print(f"{voucher_status} - Voucher System APIs ({voucher_success_count}/{len(voucher_test_cases)})")
    
    overall_success = phase2_success and voucher_all_passed
    
    if overall_success:
        print("\n🎉 ALL COMPREHENSIVE TESTS PASSED!")
        print("✅ Analytics APIs working correctly")
        print("✅ Report Generation (PDF/Excel) working correctly")
        print("✅ Alert & Notification System working correctly")
        print("✅ Admin Management APIs working correctly")
        print("✅ Voucher System working correctly")
        return True
    else:
        print("\n⚠️  SOME TESTS FAILED - Check details above")
        if not phase2_success:
            print("❌ Phase 2 APIs need attention")
        if not voucher_all_passed:
            print("❌ Voucher System needs attention")
        return False


# Duplicate function removed - using the one defined earlier

def test_customer_management_apis_duplicate():
    """Test customer management APIs after litellm dependency fix"""
    print("=" * 80)
    print("👥 CUSTOMER MANAGEMENT API TESTING - IndoWater Solution")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    
    # Test accounts needed
    admin_account = {
        "name": "Admin",
        "email": "admin@indowater.com",
        "password": "admin123",
        "expected_role": "admin"
    }
    
    technician_account = {
        "name": "Technician",
        "email": "technician@indowater.com",
        "password": "tech123",
        "expected_role": "technician"
    }
    
    results = {
        "admin_login": {"success": False, "error": None},
        "technician_login": {"success": False, "error": None},
        "list_customers": {"success": False, "error": None},
        "create_customer": {"success": False, "error": None, "customer_id": None},
        "customer_devices": {"success": False, "error": None},
        "customer_usage": {"success": False, "error": None},
        "customer_payments": {"success": False, "error": None}
    }
    
    # Step 1: Login as Admin
    print(f"\n🔐 STEP 1: Admin Login...")
    admin_login = test_login(
        admin_account["email"],
        admin_account["password"], 
        admin_account["expected_role"],
        admin_account["name"]
    )
    
    if not admin_login["success"]:
        print(f"❌ CRITICAL: Admin login failed - {admin_login['error']}")
        results["admin_login"] = {"success": False, "error": admin_login["error"]}
        return results
    
    admin_token = admin_login["token"]
    results["admin_login"] = {"success": True, "error": None}
    print(f"✅ Admin login successful")
    
    # Step 2: Login as Technician
    print(f"\n🔐 STEP 2: Technician Login...")
    technician_login = test_login(
        technician_account["email"],
        technician_account["password"], 
        technician_account["expected_role"],
        technician_account["name"]
    )
    
    if not technician_login["success"]:
        print(f"❌ CRITICAL: Technician login failed - {technician_login['error']}")
        results["technician_login"] = {"success": False, "error": technician_login["error"]}
        return results
    
    technician_token = technician_login["token"]
    results["technician_login"] = {"success": True, "error": None}
    print(f"✅ Technician login successful")
    
    admin_headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    technician_headers = {
        "Authorization": f"Bearer {technician_token}",
        "Content-Type": "application/json"
    }
    
    # Step 3: List Customers (GET /api/customers)
    print(f"\n👥 STEP 3: List Customers (GET /api/customers)...")
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/customers/",
            headers=admin_headers,
            timeout=15
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            customers = response.json()
            
            if isinstance(customers, list):
                print(f"   ✅ SUCCESS - Found {len(customers)} customers")
                results["list_customers"] = {"success": True, "error": None}
            else:
                error_msg = f"Expected list response, got: {type(customers)}"
                print(f"   ❌ {error_msg}")
                results["list_customers"] = {"success": False, "error": error_msg}
        else:
            error_msg = f"List customers failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                error_msg += f" - {response.text}"
            print(f"   ❌ {error_msg}")
            results["list_customers"] = {"success": False, "error": error_msg}
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Connection error: {str(e)}"
        print(f"   ❌ {error_msg}")
        results["list_customers"] = {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"   ❌ {error_msg}")
        results["list_customers"] = {"success": False, "error": error_msg}
    
    # Step 4: Create Customer (POST /api/customers) - Admin only
    print(f"\n👤 STEP 4: Create Customer (POST /api/customers) - Admin Only...")
    
    import time
    timestamp = int(time.time())
    customer_data = {
        "id": f"test-customer-{timestamp}",
        "email": f"testcustomer{timestamp}@indowater.com",
        "full_name": f"Test Customer {timestamp}",
        "password": "testpass123",
        "phone": "+62812345678",
        "address": "Test Address, Jakarta",
        "is_active": True
    }
    
    try:
        print(f"   Creating customer: {customer_data['email']}")
        
        response = requests.post(
            f"{BACKEND_URL}/customers/",
            json=customer_data,
            headers=admin_headers,
            timeout=15
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 201:
            customer_response = response.json()
            
            # Validate response structure
            required_fields = ["id", "email", "full_name", "role"]
            missing_fields = [field for field in required_fields if field not in customer_response]
            
            if missing_fields:
                error_msg = f"Missing required fields in response: {missing_fields}"
                print(f"   ❌ {error_msg}")
                results["create_customer"] = {"success": False, "error": error_msg}
            else:
                customer_id = customer_response["id"]
                print(f"   ✅ SUCCESS - Customer created with ID: {customer_id}")
                print(f"   ✅ Email: {customer_response['email']}, Role: {customer_response['role']}")
                results["create_customer"] = {"success": True, "error": None, "customer_id": customer_id}
        else:
            error_msg = f"Customer creation failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                error_msg += f" - {response.text}"
            print(f"   ❌ {error_msg}")
            results["create_customer"] = {"success": False, "error": error_msg}
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Connection error: {str(e)}"
        print(f"   ❌ {error_msg}")
        results["create_customer"] = {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"   ❌ {error_msg}")
        results["create_customer"] = {"success": False, "error": error_msg}
    
    # Get a customer ID for testing (use existing customer or newly created one)
    test_customer_id = results["create_customer"].get("customer_id")
    if not test_customer_id:
        # Try to get existing customer ID from the demo customer
        test_customer_id = "customer-demo-id"  # This should be the demo customer ID
    
    # Step 5: Get Customer Devices (GET /api/customers/{customer_id}/devices)
    print(f"\n📱 STEP 5: Get Customer Devices (GET /api/customers/{{customer_id}}/devices)...")
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/customers/{test_customer_id}/devices",
            headers=technician_headers,  # Test with technician access
            timeout=15
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            devices = response.json()
            
            if isinstance(devices, list):
                print(f"   ✅ SUCCESS - Found {len(devices)} devices for customer")
                results["customer_devices"] = {"success": True, "error": None}
            else:
                error_msg = f"Expected list response, got: {type(devices)}"
                print(f"   ❌ {error_msg}")
                results["customer_devices"] = {"success": False, "error": error_msg}
        else:
            error_msg = f"Get customer devices failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                error_msg += f" - {response.text}"
            print(f"   ❌ {error_msg}")
            results["customer_devices"] = {"success": False, "error": error_msg}
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Connection error: {str(e)}"
        print(f"   ❌ {error_msg}")
        results["customer_devices"] = {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"   ❌ {error_msg}")
        results["customer_devices"] = {"success": False, "error": error_msg}
    
    # Step 6: Get Customer Usage (GET /api/customers/{customer_id}/usage)
    print(f"\n📊 STEP 6: Get Customer Usage (GET /api/customers/{{customer_id}}/usage)...")
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/customers/{test_customer_id}/usage",
            headers=admin_headers,  # Test with admin access
            timeout=15
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            usage = response.json()
            
            if isinstance(usage, list):
                print(f"   ✅ SUCCESS - Found {len(usage)} usage records for customer")
                results["customer_usage"] = {"success": True, "error": None}
            else:
                error_msg = f"Expected list response, got: {type(usage)}"
                print(f"   ❌ {error_msg}")
                results["customer_usage"] = {"success": False, "error": error_msg}
        else:
            error_msg = f"Get customer usage failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                error_msg += f" - {response.text}"
            print(f"   ❌ {error_msg}")
            results["customer_usage"] = {"success": False, "error": error_msg}
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Connection error: {str(e)}"
        print(f"   ❌ {error_msg}")
        results["customer_usage"] = {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"   ❌ {error_msg}")
        results["customer_usage"] = {"success": False, "error": error_msg}
    
    # Step 7: Get Customer Payments (GET /api/customers/{customer_id}/payments)
    print(f"\n💳 STEP 7: Get Customer Payments (GET /api/customers/{{customer_id}}/payments)...")
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/customers/{test_customer_id}/payments",
            headers=technician_headers,  # Test with technician access
            timeout=15
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            payments = response.json()
            
            if isinstance(payments, list):
                print(f"   ✅ SUCCESS - Found {len(payments)} payment records for customer")
                results["customer_payments"] = {"success": True, "error": None}
            else:
                error_msg = f"Expected list response, got: {type(payments)}"
                print(f"   ❌ {error_msg}")
                results["customer_payments"] = {"success": False, "error": error_msg}
        else:
            error_msg = f"Get customer payments failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                error_msg += f" - {response.text}"
            print(f"   ❌ {error_msg}")
            results["customer_payments"] = {"success": False, "error": error_msg}
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Connection error: {str(e)}"
        print(f"   ❌ {error_msg}")
        results["customer_payments"] = {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"   ❌ {error_msg}")
        results["customer_payments"] = {"success": False, "error": error_msg}
    
    return results


def test_voucher_and_customer_apis():
    """Test both voucher and customer management APIs as requested"""
    print("=" * 100)
    print("🧪 COMPREHENSIVE VOUCHER & CUSTOMER MANAGEMENT API TESTING")
    print("=" * 100)
    print("Testing after litellm dependency fix")
    print(f"Backend URL: {BACKEND_URL}")
    
    # Test voucher management APIs
    print("\n" + "🎫" * 20 + " VOUCHER MANAGEMENT TESTS " + "🎫" * 20)
    voucher_results = test_voucher_management_apis()
    
    # Test customer management APIs  
    print("\n" + "👥" * 20 + " CUSTOMER MANAGEMENT TESTS " + "👥" * 20)
    customer_results = test_customer_management_apis()
    
    # Overall summary
    print("\n" + "=" * 100)
    print("🏆 OVERALL TEST RESULTS SUMMARY")
    print("=" * 100)
    
    # Voucher test summary
    voucher_test_cases = [
        ("Admin Login", voucher_results["admin_login"]),
        ("Customer Login", voucher_results["customer_login"]),
        ("Voucher Creation", voucher_results["voucher_creation"]),
        ("List Vouchers", voucher_results["voucher_list"]),
        ("Filter Active Vouchers", voucher_results["voucher_list_filter"]),
        ("Voucher Validation", voucher_results["voucher_validation"])
    ]
    
    voucher_success = sum(1 for _, result in voucher_test_cases if result["success"])
    voucher_total = len(voucher_test_cases)
    
    # Customer test summary
    customer_test_cases = [
        ("Admin Login", customer_results["admin_login"]),
        ("Technician Login", customer_results["technician_login"]),
        ("List Customers", customer_results["list_customers"]),
        ("Create Customer", customer_results["create_customer"]),
        ("Customer Devices", customer_results["customer_devices"]),
        ("Customer Usage", customer_results["customer_usage"]),
        ("Customer Payments", customer_results["customer_payments"])
    ]
    
    customer_success = sum(1 for _, result in customer_test_cases if result["success"])
    customer_total = len(customer_test_cases)
    
    total_success = voucher_success + customer_success
    total_tests = voucher_total + customer_total
    
    print(f"Voucher Management APIs: {voucher_success}/{voucher_total} passed")
    print(f"Customer Management APIs: {customer_success}/{customer_total} passed")
    print(f"Overall: {total_success}/{total_tests} tests passed")
    
    # Detailed results
    print("\n📋 DETAILED RESULTS:")
    print("\n🎫 Voucher Management:")
    for test_name, result in voucher_test_cases:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"  {status} - {test_name}")
        if not result["success"] and result["error"]:
            print(f"        Error: {result['error']}")
    
    print("\n👥 Customer Management:")
    for test_name, result in customer_test_cases:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"  {status} - {test_name}")
        if not result["success"] and result["error"]:
            print(f"        Error: {result['error']}")
    
    if total_success == total_tests:
        print("\n🎉 ALL TESTS PASSED! Backend APIs are working correctly after litellm fix.")
        return True
    else:
        print("\n⚠️  SOME TESTS FAILED - Check detailed results above")
        return False


if __name__ == "__main__":
    # Run comprehensive backend API testing as requested
    success = test_comprehensive_backend_apis()
    
    if success:
        print("\n🎉 ALL BACKEND API TESTS COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n⚠️  SOME BACKEND API TESTS FAILED - Check output above")
        sys.exit(1)