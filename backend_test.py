#!/usr/bin/env python3
"""
Backend API Testing Script for IndoWater Solution
Tests login endpoint for all 3 demo accounts
"""

import requests
import json
import sys
from typing import Dict, Any

# Backend URL from environment
BACKEND_URL = "https://resume-progress-15.preview.emergentagent.com/api"

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

def main():
    """Run all login tests"""
    print("=" * 60)
    print("🧪 BACKEND LOGIN TESTING - IndoWater Solution")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Testing {len(DEMO_ACCOUNTS)} demo accounts...")
    
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
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} - {result['account_name']} ({result['email']})")
        if not result["success"]:
            print(f"      Error: {result['error']}")
    
    print(f"\nResults: {success_count}/{len(DEMO_ACCOUNTS)} accounts working")
    
    if success_count == len(DEMO_ACCOUNTS):
        print("🎉 ALL TESTS PASSED - All demo accounts can login successfully!")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - Check errors above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)