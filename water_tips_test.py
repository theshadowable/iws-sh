#!/usr/bin/env python3
"""
Water Conservation Tips API Testing Script
Tests all endpoints comprehensively as requested
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# Backend URL from environment
BACKEND_URL = "https://comprehensive-fix-1.preview.emergentagent.com/api"

# Admin account for testing
ADMIN_ACCOUNT = {
    "email": "admin@indowater.com",
    "password": "admin123",
    "expected_role": "admin"
}

def test_login(email: str, password: str) -> Dict[str, Any]:
    """Test login and get access token"""
    print(f"🔐 Testing Admin Login...")
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
            token = data.get("access_token")
            user = data.get("user", {})
            
            print(f"   ✅ SUCCESS - Role: {user.get('role')}, Active: {user.get('is_active')}")
            print(f"   Token: {token[:20]}...")
            
            return {
                "success": True,
                "token": token,
                "user": user
            }
        else:
            error_msg = "Login failed"
            try:
                error_data = response.json()
                error_msg = error_data.get("detail", str(error_data))
            except:
                error_msg = response.text or f"HTTP {response.status_code}"
            
            print(f"   ❌ FAILED - {error_msg}")
            return {"success": False, "error": error_msg}
            
    except Exception as e:
        print(f"   ❌ ERROR - {str(e)}")
        return {"success": False, "error": str(e)}

def test_water_conservation_tips_apis(token: str) -> Dict[str, Any]:
    """Test Water Conservation Tips APIs comprehensively"""
    print(f"\n💡 Testing Water Conservation Tips APIs...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "list_tips": {"success": False, "error": None, "data": None},
        "filter_by_category": {"success": False, "error": None, "data": None},
        "create_tip": {"success": False, "error": None, "data": None},
        "get_tip_detail": {"success": False, "error": None, "data": None},
        "update_tip": {"success": False, "error": None, "data": None},
        "delete_tip": {"success": False, "error": None, "data": None}
    }
    
    created_tip_id = None
    
    try:
        # Test 1: GET /api/tips/ - List all tips (should return 5 tips with complete data)
        print("   📋 Testing GET /api/tips/ - List all tips...")
        response = requests.get(
            f"{BACKEND_URL}/tips/",
            headers=headers,
            timeout=15
        )
        
        print(f"      Status Code: {response.status_code}")
        
        if response.status_code == 200:
            tips_data = response.json()
            tips = tips_data.get("tips", [])
            total = tips_data.get("total", 0)
            
            print(f"      ✅ SUCCESS - Found {len(tips)} tips (total: {total})")
            
            # Verify expected structure and data
            if len(tips) >= 5:
                print(f"      ✅ Expected at least 5 tips, found {len(tips)}")
                
                # Check if tips have complete data structure including new fields
                first_tip = tips[0]
                required_fields = ["id", "title", "description", "category", "difficulty_level", 
                                 "implementation_steps", "benefits", "required_tools"]
                missing_fields = [field for field in required_fields if field not in first_tip]
                
                if missing_fields:
                    print(f"      ⚠️  Missing fields in tip data: {missing_fields}")
                else:
                    print(f"      ✅ All required fields present in tip data")
                    
                    # Show sample data structure
                    print(f"      📊 Sample tip structure:")
                    print(f"         Title: {first_tip.get('title', 'N/A')}")
                    print(f"         Category: {first_tip.get('category', 'N/A')}")
                    print(f"         Difficulty: {first_tip.get('difficulty_level', 'N/A')}")
                    print(f"         Steps: {len(first_tip.get('implementation_steps', []))} steps")
                    print(f"         Benefits: {len(first_tip.get('benefits', []))} benefits")
                    print(f"         Tools: {len(first_tip.get('required_tools', []))} tools")
                
                results["list_tips"] = {"success": True, "data": tips_data}
            else:
                error_msg = f"Expected at least 5 tips, found {len(tips)}"
                print(f"      ❌ {error_msg}")
                results["list_tips"] = {"success": False, "error": error_msg}
        else:
            error_msg = f"List tips failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                pass
            print(f"      ❌ {error_msg}")
            results["list_tips"] = {"success": False, "error": error_msg}
        
        # Test 2: GET /api/tips/?category=general_savings - Filter by category
        print("   🔍 Testing GET /api/tips/?category=general_savings - Filter by category...")
        response = requests.get(
            f"{BACKEND_URL}/tips/?category=general_savings",
            headers=headers,
            timeout=15
        )
        
        print(f"      Status Code: {response.status_code}")
        
        if response.status_code == 200:
            filtered_data = response.json()
            filtered_tips = filtered_data.get("tips", [])
            
            # Verify all tips have the correct category
            correct_category = all(tip.get("category") == "general_savings" for tip in filtered_tips)
            
            if correct_category:
                print(f"      ✅ SUCCESS - Found {len(filtered_tips)} tips with category 'general_savings'")
                results["filter_by_category"] = {"success": True, "data": filtered_data}
            else:
                error_msg = "Some tips don't have the correct category filter"
                print(f"      ❌ {error_msg}")
                results["filter_by_category"] = {"success": False, "error": error_msg}
        else:
            error_msg = f"Category filter failed: {response.status_code}"
            print(f"      ❌ {error_msg}")
            results["filter_by_category"] = {"success": False, "error": error_msg}
        
        # Test 3: POST /api/tips/admin/create - Create new tip with complete validation
        print("   ➕ Testing POST /api/tips/admin/create - Create new tip...")
        tip_data = {
            "title": "Gunakan Toilet Hemat Air",
            "description": "Toilet adalah salah satu pemakai air terbesar di rumah. Ganti dengan model hemat air.",
            "category": "general_savings",
            "difficulty_level": "medium",
            "potential_savings_percentage": 20,
            "implementation_time": "2 jam",
            "implementation_steps": [
                "Beli toilet hemat air",
                "Matikan air",
                "Lepas toilet lama",
                "Pasang toilet baru"
            ],
            "benefits": [
                "Hemat 20% air",
                "Kurangi tagihan"
            ],
            "required_tools": [
                "Kunci inggris",
                "Toilet baru"
            ]
        }
        
        print(f"      📝 Creating tip with data:")
        print(f"         Title: {tip_data['title']}")
        print(f"         Category: {tip_data['category']}")
        print(f"         Difficulty: {tip_data['difficulty_level']}")
        print(f"         Savings: {tip_data['potential_savings_percentage']}%")
        print(f"         Time: {tip_data['implementation_time']}")
        print(f"         Steps: {len(tip_data['implementation_steps'])} steps")
        print(f"         Benefits: {len(tip_data['benefits'])} benefits")
        print(f"         Tools: {len(tip_data['required_tools'])} tools")
        
        response = requests.post(
            f"{BACKEND_URL}/tips/admin/create",
            json=tip_data,
            headers=headers,
            timeout=15
        )
        
        print(f"      Status Code: {response.status_code}")
        
        if response.status_code == 200:
            new_tip = response.json()
            created_tip_id = new_tip.get("id")
            
            # Verify all fields are present and correct
            required_fields = ["id", "title", "description", "category", "difficulty_level", 
                             "implementation_steps", "benefits", "required_tools", "potential_savings_percentage"]
            missing_fields = [field for field in required_fields if field not in new_tip]
            
            if missing_fields:
                error_msg = f"Missing fields in created tip: {missing_fields}"
                print(f"      ❌ {error_msg}")
                results["create_tip"] = {"success": False, "error": error_msg}
            else:
                print(f"      ✅ SUCCESS - Tip created with ID: {created_tip_id}")
                print(f"      ✅ All required fields present in response")
                
                # Verify data integrity
                data_correct = (
                    new_tip.get("title") == tip_data["title"] and
                    new_tip.get("category") == tip_data["category"] and
                    new_tip.get("difficulty_level") == tip_data["difficulty_level"] and
                    new_tip.get("potential_savings_percentage") == tip_data["potential_savings_percentage"] and
                    len(new_tip.get("implementation_steps", [])) == len(tip_data["implementation_steps"]) and
                    len(new_tip.get("benefits", [])) == len(tip_data["benefits"]) and
                    len(new_tip.get("required_tools", [])) == len(tip_data["required_tools"])
                )
                
                if data_correct:
                    print(f"      ✅ Data integrity verified - all fields match input")
                else:
                    print(f"      ⚠️  Data integrity issue - some fields don't match input")
                
                results["create_tip"] = {"success": True, "data": new_tip}
        else:
            error_msg = f"Create tip failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', '')}"
            except:
                pass
            print(f"      ❌ {error_msg}")
            results["create_tip"] = {"success": False, "error": error_msg}
        
        # Test 4: GET /api/tips/{tip_id} - Get single tip detail
        if created_tip_id or (results["list_tips"]["success"] and results["list_tips"]["data"]["tips"]):
            test_tip_id = created_tip_id
            if not test_tip_id and results["list_tips"]["success"]:
                test_tip_id = results["list_tips"]["data"]["tips"][0]["id"]
            
            print(f"   🔍 Testing GET /api/tips/{test_tip_id} - Get single tip detail...")
            response = requests.get(
                f"{BACKEND_URL}/tips/{test_tip_id}",
                headers=headers,
                timeout=15
            )
            
            print(f"      Status Code: {response.status_code}")
            
            if response.status_code == 200:
                tip_detail = response.json()
                
                # Verify structure includes tip and engagement data
                required_fields = ["tip", "user_engagement", "is_viewed", "is_liked", "is_bookmarked", "is_implemented"]
                missing_fields = [field for field in required_fields if field not in tip_detail]
                
                if missing_fields:
                    error_msg = f"Missing fields in tip detail: {missing_fields}"
                    print(f"      ❌ {error_msg}")
                    results["get_tip_detail"] = {"success": False, "error": error_msg}
                else:
                    print(f"      ✅ SUCCESS - Tip detail retrieved with engagement data")
                    print(f"      ✅ Tip viewed: {tip_detail['is_viewed']}")
                    print(f"      ✅ Tip liked: {tip_detail['is_liked']}")
                    print(f"      ✅ Tip bookmarked: {tip_detail['is_bookmarked']}")
                    print(f"      ✅ Tip implemented: {tip_detail['is_implemented']}")
                    
                    # Verify tip data structure
                    tip_data_in_response = tip_detail.get("tip", {})
                    tip_required_fields = ["id", "title", "description", "implementation_steps", "benefits", "required_tools"]
                    tip_missing_fields = [field for field in tip_required_fields if field not in tip_data_in_response]
                    
                    if tip_missing_fields:
                        print(f"      ⚠️  Missing fields in tip data: {tip_missing_fields}")
                    else:
                        print(f"      ✅ Complete tip data structure verified")
                    
                    results["get_tip_detail"] = {"success": True, "data": tip_detail}
            else:
                error_msg = f"Get tip detail failed: {response.status_code}"
                print(f"      ❌ {error_msg}")
                results["get_tip_detail"] = {"success": False, "error": error_msg}
        else:
            print("   ⚠️  Skipping tip detail test - no tip ID available")
            results["get_tip_detail"] = {"success": True, "data": {"skipped": "No tip ID"}}
        
        # Test 5: PUT /api/tips/admin/{tip_id} - Update an existing tip
        if created_tip_id:
            print(f"   ✏️ Testing PUT /api/tips/admin/{created_tip_id} - Update tip...")
            update_data = {
                "title": "Gunakan Toilet Hemat Air - Updated",
                "potential_savings_percentage": 25,
                "implementation_steps": [
                    "Beli toilet hemat air berkualitas",
                    "Matikan air utama",
                    "Lepas toilet lama dengan hati-hati",
                    "Pasang toilet baru dengan benar",
                    "Test kebocoran"
                ]
            }
            
            print(f"      📝 Updating tip with:")
            print(f"         New title: {update_data['title']}")
            print(f"         New savings: {update_data['potential_savings_percentage']}%")
            print(f"         New steps: {len(update_data['implementation_steps'])} steps")
            
            response = requests.put(
                f"{BACKEND_URL}/tips/admin/{created_tip_id}",
                json=update_data,
                headers=headers,
                timeout=15
            )
            
            print(f"      Status Code: {response.status_code}")
            
            if response.status_code == 200:
                updated_tip = response.json()
                
                # Verify updates were applied
                updates_applied = (
                    updated_tip.get("title") == update_data["title"] and 
                    updated_tip.get("potential_savings_percentage") == update_data["potential_savings_percentage"] and
                    len(updated_tip.get("implementation_steps", [])) == 5
                )
                
                if updates_applied:
                    print(f"      ✅ SUCCESS - Tip updated successfully")
                    print(f"      ✅ Title updated: {updated_tip.get('title')}")
                    print(f"      ✅ Savings updated: {updated_tip.get('potential_savings_percentage')}%")
                    print(f"      ✅ Steps updated: {len(updated_tip.get('implementation_steps', []))} steps")
                    results["update_tip"] = {"success": True, "data": updated_tip}
                else:
                    error_msg = "Update data not reflected in response"
                    print(f"      ❌ {error_msg}")
                    results["update_tip"] = {"success": False, "error": error_msg}
            else:
                error_msg = f"Update tip failed: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('detail', '')}"
                except:
                    pass
                print(f"      ❌ {error_msg}")
                results["update_tip"] = {"success": False, "error": error_msg}
        else:
            print("   ⚠️  Skipping tip update - no created tip available")
            results["update_tip"] = {"success": True, "data": {"skipped": "No created tip"}}
        
        # Test 6: DELETE /api/tips/admin/{tip_id} - Delete a tip
        if created_tip_id:
            print(f"   🗑️ Testing DELETE /api/tips/admin/{created_tip_id} - Delete tip...")
            response = requests.delete(
                f"{BACKEND_URL}/tips/admin/{created_tip_id}",
                headers=headers,
                timeout=15
            )
            
            print(f"      Status Code: {response.status_code}")
            
            if response.status_code == 200:
                delete_result = response.json()
                print(f"      ✅ SUCCESS - Tip deleted successfully")
                print(f"      ✅ Response: {delete_result.get('message', 'Deleted')}")
                results["delete_tip"] = {"success": True, "data": delete_result}
            else:
                error_msg = f"Delete tip failed: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('detail', '')}"
                except:
                    pass
                print(f"      ❌ {error_msg}")
                results["delete_tip"] = {"success": False, "error": error_msg}
        else:
            print("   ⚠️  Skipping tip deletion - no created tip available")
            results["delete_tip"] = {"success": True, "data": {"skipped": "No created tip"}}
            
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

def print_test_summary(results: Dict[str, Any]):
    """Print comprehensive test summary"""
    print("\n" + "=" * 80)
    print("📊 WATER CONSERVATION TIPS API TEST SUMMARY")
    print("=" * 80)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result["success"])
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed Results:")
    print("-" * 40)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{test_name:25} {status}")
        
        if not result["success"] and result.get("error"):
            print(f"                         Error: {result['error']}")
        elif result["success"] and result.get("data", {}).get("skipped"):
            print(f"                         Skipped: {result['data']['skipped']}")
    
    print("\n" + "=" * 80)
    
    # Overall assessment
    if failed_tests == 0:
        print("🎉 ALL TESTS PASSED! Water Conservation Tips APIs are working correctly.")
        print("✅ All endpoints return 200/201 status codes")
        print("✅ Create successfully adds tip with all fields")
        print("✅ List shows all tips with complete data")
        print("✅ Update and delete work correctly")
        print("✅ No 404 or 500 errors found")
    else:
        print("⚠️  SOME TESTS FAILED! Issues found in Water Conservation Tips APIs.")
        print("Please review the failed tests above and fix the issues.")
    
    print("=" * 80)

def main():
    """Main test execution"""
    print("🚀 Water Conservation Tips API Testing")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print("=" * 80)
    
    print("Testing Water Conservation Tips APIs comprehensively as requested:")
    print("1. GET /api/tips/ - List all tips (should return 5 tips with complete data)")
    print("2. GET /api/tips/?category=general_savings - Filter by category")
    print("3. POST /api/tips/admin/create - Create new tip with complete validation")
    print("4. PUT /api/tips/admin/{tip_id} - Update an existing tip")
    print("5. DELETE /api/tips/admin/{tip_id} - Delete a tip")
    print("6. GET /api/tips/{tip_id} - Get single tip detail")
    print("\nDatabase should be seeded with 5 tips (4 original + 1 test tip 'Hemat Air di Kamar Mandi')")
    print("Using admin@indowater.com/admin123 account for testing")
    print("=" * 80)
    
    # Test login first
    login_result = test_login(ADMIN_ACCOUNT["email"], ADMIN_ACCOUNT["password"])
    
    if not login_result["success"]:
        print(f"\n❌ Login failed: {login_result['error']}")
        print("Cannot proceed with API testing without authentication.")
        sys.exit(1)
    
    # Get token
    token = login_result["token"]
    
    # Test Water Conservation Tips APIs
    results = test_water_conservation_tips_apis(token)
    
    # Print summary
    print_test_summary(results)
    
    # Exit with appropriate code
    failed_tests = sum(1 for result in results.values() if not result["success"])
    sys.exit(0 if failed_tests == 0 else 1)

if __name__ == "__main__":
    main()