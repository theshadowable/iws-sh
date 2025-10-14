#!/usr/bin/env python3
"""
Backend API Testing Script for IndoWater Solution
Tests login, analytics, reporting, and payment history APIs
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Backend URL from environment
BACKEND_URL = "https://smooth-sailing-1.preview.emergentagent.com/api"

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


def test_comprehensive_phase2_apis():
    """Test all Phase 2 backend APIs comprehensively"""
    print("=" * 80)
    print("🧪 COMPREHENSIVE PHASE 2 API TESTING - IndoWater Solution")
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
        
        # Test Analytics APIs
        analytics_results = test_analytics_api(token, user_role, customer_id)
        
        # Test Report Generation
        report_results = test_report_generation_api(token, user_role, customer_id)
        
        # Test Alert & Notification System
        alert_results = test_alert_notification_apis(token, user_role, customer_id)
        
        # Test Admin Management APIs
        admin_results = test_admin_management_apis(token, user_role)
        
        all_results[account["name"]] = {
            "login": True,
            "analytics": analytics_results,
            "reports": report_results,
            "alerts": alert_results,
            "admin": admin_results
        }
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE PHASE 2 TEST SUMMARY")
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
        categories = ["analytics", "reports", "alerts", "admin"]
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
                    
                    print(f"  {status} - {category.title()}: {test_name}")
                    if not result["success"] and result["error"]:
                        print(f"        Error: {result['error']}")
    
    print(f"\nOverall Results: {passed_tests}/{total_tests} tests passed")
    
    if failed_tests:
        print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
        for failed_test in failed_tests:
            print(f"  - {failed_test}")
    
    if passed_tests == total_tests:
        print("🎉 ALL PHASE 2 TESTS PASSED!")
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


def test_voucher_system_apis():
    """Test voucher system APIs - focusing on the recently fixed voucher creation"""
    print("=" * 80)
    print("🎫 VOUCHER SYSTEM API TESTING - IndoWater Solution")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    
    # Test accounts needed
    admin_account = {
        "name": "Admin",
        "email": "admin@indowater.com",
        "password": "admin123",
        "expected_role": "admin"
    }
    
    customer_account = {
        "name": "Customer",
        "email": "customer@indowater.com", 
        "password": "customer123",
        "expected_role": "customer"
    }
    
    results = {
        "admin_login": {"success": False, "error": None},
        "customer_login": {"success": False, "error": None},
        "voucher_creation": {"success": False, "error": None, "voucher_id": None},
        "voucher_list": {"success": False, "error": None},
        "voucher_list_filter": {"success": False, "error": None},
        "voucher_validation": {"success": False, "error": None}
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

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)