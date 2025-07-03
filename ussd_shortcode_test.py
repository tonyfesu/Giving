#!/usr/bin/env python3
import requests
import json
import re
from pprint import pprint

# Get the backend URL from the frontend .env file
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            BACKEND_URL = line.strip().split('=')[1].strip('"\'')
            break

API_URL = f"{BACKEND_URL}/api"
print(f"Testing API at: {API_URL}")

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def run_test(test_name, test_func):
    """Run a test and track results"""
    print(f"\n{'='*80}\nTEST: {test_name}\n{'='*80}")
    try:
        result = test_func()
        if result:
            test_results["passed"] += 1
            test_results["tests"].append({"name": test_name, "status": "PASSED"})
            print(f"✅ PASSED: {test_name}")
            return True
        else:
            test_results["failed"] += 1
            test_results["tests"].append({"name": test_name, "status": "FAILED"})
            print(f"❌ FAILED: {test_name}")
            return False
    except Exception as e:
        test_results["failed"] += 1
        test_results["tests"].append({"name": test_name, "status": "FAILED", "error": str(e)})
        print(f"❌ FAILED: {test_name} - Error: {str(e)}")
        return False

def test_get_causes_ussd_shortcode():
    """Test that all causes have USSD shortcodes"""
    response = requests.get(f"{API_URL}/causes")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    causes = response.json()
    assert len(causes) > 0, f"Expected at least one cause, got {len(causes)}"
    
    # Verify all causes have cause_code and ussd_shortcode fields
    for cause in causes:
        assert "cause_code" in cause, f"Cause {cause['id']} missing 'cause_code' field"
        assert "ussd_shortcode" in cause, f"Cause {cause['id']} missing 'ussd_shortcode' field"
        
        # Verify cause_code format (6 characters, alphanumeric)
        cause_code = cause["cause_code"]
        assert len(cause_code) == 6, f"Cause code should be 6 characters, got {len(cause_code)} for {cause['id']}"
        assert re.match(r'^[A-Z0-9]{6}$', cause_code), f"Cause code should be alphanumeric, got {cause_code} for {cause['id']}"
        
        # Verify USSD shortcode format
        ussd_shortcode = cause["ussd_shortcode"]
        expected_format = f"*123*86*{cause_code}*[Amount]#"
        assert ussd_shortcode == expected_format, f"Expected USSD format {expected_format}, got {ussd_shortcode} for {cause['id']}"
    
    # Verify cause codes are unique
    cause_codes = [cause["cause_code"] for cause in causes]
    assert len(cause_codes) == len(set(cause_codes)), "Cause codes should be unique"
    
    print(f"Verified {len(causes)} causes have valid USSD shortcodes")
    return True

def test_create_cause_with_ussd():
    """Test that new causes automatically get USSD shortcodes"""
    cause_data = {
        "name": "USSD Test Cause",
        "description": "Testing USSD shortcode generation",
        "category": "Environment",
        "image_url": "https://images.unsplash.com/photo-1508514177221-188b1cf16e9d",
        "impact_metric": "trees planted",
        "cost_per_impact": 5.0,
        "goal_amount": 10000.0,
        "creator_id": "test_creator",
        "creator_type": "business"
    }
    
    response = requests.post(f"{API_URL}/causes", json=cause_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    cause = response.json()
    assert "cause_code" in cause, "New cause missing 'cause_code' field"
    assert "ussd_shortcode" in cause, "New cause missing 'ussd_shortcode' field"
    
    # Verify cause_code format (6 characters, alphanumeric)
    cause_code = cause["cause_code"]
    assert len(cause_code) == 6, f"Cause code should be 6 characters, got {len(cause_code)}"
    assert re.match(r'^[A-Z0-9]{6}$', cause_code), f"Cause code should be alphanumeric, got {cause_code}"
    
    # Verify USSD shortcode format
    ussd_shortcode = cause["ussd_shortcode"]
    expected_format = f"*123*86*{cause_code}*[Amount]#"
    assert ussd_shortcode == expected_format, f"Expected USSD format {expected_format}, got {ussd_shortcode}"
    
    print(f"Created new cause with USSD shortcode: {ussd_shortcode}")
    return True

def test_existing_demo_causes():
    """Test that all demo causes have USSD shortcodes"""
    response = requests.get(f"{API_URL}/causes")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    causes = response.json()
    
    # Check for specific demo causes
    demo_cause_names = [
        "Education for All", 
        "Clean Water Initiative", 
        "Forest Restoration", 
        "Food Security Program"
    ]
    
    found_causes = []
    for name in demo_cause_names:
        found = False
        for cause in causes:
            if cause["name"] == name:
                found = True
                found_causes.append(cause)
                assert "cause_code" in cause, f"Demo cause {name} missing 'cause_code' field"
                assert "ussd_shortcode" in cause, f"Demo cause {name} missing 'ussd_shortcode' field"
                break
        assert found, f"Demo cause '{name}' not found"
    
    print(f"Verified {len(found_causes)} demo causes have USSD shortcodes")
    return True

# Run the tests
if __name__ == "__main__":
    run_test("Get Causes USSD Shortcode", test_get_causes_ussd_shortcode)
    run_test("Create Cause with USSD", test_create_cause_with_ussd)
    run_test("Existing Demo Causes", test_existing_demo_causes)
    
    # Print summary
    print("\n" + "="*80)
    print(f"SUMMARY: {test_results['passed']} passed, {test_results['failed']} failed")
    print("="*80)
    
    for test in test_results["tests"]:
        status = "✅ PASSED" if test["status"] == "PASSED" else "❌ FAILED"
        error = f" - Error: {test.get('error', '')}" if "error" in test else ""
        print(f"{status}: {test['name']}{error}")