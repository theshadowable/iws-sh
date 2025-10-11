#!/usr/bin/env python3
"""
Backend API Testing Script for IndoWater Solution
Tests login endpoint and payment history APIs
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Backend URL from environment
BACKEND_URL = "https://ui-fix-continue.preview.emergentagent.com/api"

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


def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 BACKEND TESTING - IndoWater Solution")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    
    # Test 1: Login for all accounts
    print(f"\n🔐 PHASE 1: Testing login for {len(DEMO_ACCOUNTS)} demo accounts...")
    
    results = []
    success_count = 0
    
    for account in DEMO_ACCOUNTS:
        result = test_login(
            account["email"],
            account["password"], 
            account["expected_role"],
            account["name"]
        )
        
        result["account_name"] = account["name"]
        result["email"] = account["email"]
        results.append(result)
        
        if result["success"]:
            success_count += 1
    
    # Login Summary
    print("\n" + "=" * 60)
    print("📊 LOGIN TEST SUMMARY")
    print("=" * 60)
    
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} - {result['account_name']} ({result['email']})")
        if not result["success"]:
            print(f"      Error: {result['error']}")
    
    print(f"\nLogin Results: {success_count}/{len(DEMO_ACCOUNTS)} accounts working")
    
    # Test 2: Payment APIs (only if customer login works)
    customer_login_success = any(r["success"] and r["account_name"] == "Customer" for r in results)
    
    if customer_login_success:
        print(f"\n💳 PHASE 2: Testing Payment History APIs...")
        payment_success = test_customer_payment_apis()
    else:
        print(f"\n❌ SKIPPING Payment API tests - Customer login failed")
        payment_success = False
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🏁 FINAL TEST SUMMARY")
    print("=" * 60)
    
    login_status = "✅ PASS" if success_count == len(DEMO_ACCOUNTS) else "❌ FAIL"
    payment_status = "✅ PASS" if payment_success else "❌ FAIL"
    
    print(f"{login_status} - Login Tests ({success_count}/{len(DEMO_ACCOUNTS)})")
    print(f"{payment_status} - Payment API Tests")
    
    overall_success = (success_count == len(DEMO_ACCOUNTS)) and payment_success
    
    if overall_success:
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print("\n⚠️  SOME TESTS FAILED - Check details above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)