#!/usr/bin/env python3
"""
Test script untuk memverifikasi fungsi URL encoding MongoDB
"""
from urllib.parse import quote_plus
import os

def get_mongo_url_test(mongo_url):
    """
    Test version of get_mongo_url function
    """
    # Skip encoding if no @ symbol (no credentials)
    if '@' not in mongo_url:
        return mongo_url
    
    try:
        # Determine protocol
        if mongo_url.startswith('mongodb+srv://'):
            protocol = 'mongodb+srv://'
        elif mongo_url.startswith('mongodb://'):
            protocol = 'mongodb://'
        else:
            # Unknown protocol, return as-is
            return mongo_url
        
        # Remove protocol to parse credentials
        url_without_protocol = mongo_url.replace(protocol, '', 1)
        
        # Split credentials from host/database part
        if '@' not in url_without_protocol:
            # No credentials present
            return mongo_url
        
        credentials_part, host_part = url_without_protocol.split('@', 1)
        
        # Split credentials into username and password
        if ':' not in credentials_part:
            # No password, only username - shouldn't happen but handle it
            return mongo_url
        
        username, password = credentials_part.split(':', 1)
        
        # URL encode username and password
        encoded_username = quote_plus(username)
        encoded_password = quote_plus(password)
        
        # Reconstruct the URL with encoded credentials
        encoded_url = f"{protocol}{encoded_username}:{encoded_password}@{host_part}"
        
        print(f"✅ Encoded successfully (username: {username})")
        return encoded_url
        
    except Exception as e:
        print(f"❌ Error encoding: {e}")
        return mongo_url

# Test cases
test_cases = [
    {
        "name": "Local MongoDB (no credentials)",
        "input": "mongodb://localhost:27017",
        "expected": "mongodb://localhost:27017"
    },
    {
        "name": "MongoDB with simple password",
        "input": "mongodb://admin:password123@localhost:27017",
        "expected": "mongodb://admin:password123@localhost:27017"
    },
    {
        "name": "MongoDB with special characters @ ! $ #",
        "input": "mongodb://admin:p@ssw0rd!$#@localhost:27017/mydb",
        "expected": "mongodb://admin:p%40ssw0rd%21%24%23@localhost:27017/mydb"
    },
    {
        "name": "MongoDB Atlas with special characters",
        "input": "mongodb+srv://indowater:My$ecret!Pass@123@cluster0.mongodb.net/indowater_db?retryWrites=true",
        "expected": "mongodb+srv://indowater:My%24ecret%21Pass%40123@cluster0.mongodb.net/indowater_db?retryWrites=true"
    },
    {
        "name": "MongoDB Atlas standard",
        "input": "mongodb+srv://user:pass@cluster0.abc123.mongodb.net/dbname",
        "expected": "mongodb+srv://user:pass@cluster0.abc123.mongodb.net/dbname"
    },
    {
        "name": "Complex password with multiple special chars",
        "input": "mongodb://admin:P@ssw0rd!2025#$%@localhost:27017",
        "expected": "mongodb://admin:P%40ssw0rd%212025%23%24%25@localhost:27017"
    }
]

print("=" * 70)
print("TESTING MONGODB URL ENCODING FUNCTION")
print("=" * 70)

passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    print(f"\n🧪 Test {i}: {test['name']}")
    print(f"   Input:    {test['input']}")
    
    result = get_mongo_url_test(test['input'])
    print(f"   Output:   {result}")
    print(f"   Expected: {test['expected']}")
    
    if result == test['expected']:
        print(f"   ✅ PASSED")
        passed += 1
    else:
        print(f"   ❌ FAILED")
        failed += 1

print("\n" + "=" * 70)
print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print("=" * 70)

if failed == 0:
    print("✅ All tests passed! Function is working correctly.")
else:
    print(f"❌ {failed} test(s) failed. Please review the function.")
