#!/usr/bin/env python3
import requests
import json
import time
import os
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

def test_api_title_branding():
    """Test if the API documentation shows 'Nnoboa API' instead of 'ImpactLink API'"""
    # Check the API title in the OpenAPI schema
    response = requests.get(f"{BACKEND_URL}/openapi.json")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # Parse the OpenAPI schema
    openapi_schema = response.json()
    assert "info" in openapi_schema, "OpenAPI schema missing 'info' field"
    assert "title" in openapi_schema["info"], "OpenAPI schema info missing 'title' field"
    
    # Check if the title is "Nnoboa API"
    title = openapi_schema["info"]["title"]
    assert title == "Nnoboa API", f"Expected API title 'Nnoboa API', got '{title}'"
    assert "ImpactLink" not in title, f"API title '{title}' still contains 'ImpactLink'"
    
    print(f"API documentation correctly shows '{title}' instead of 'ImpactLink API'")
    return True

def test_get_causes():
    """Test GET /api/causes endpoint"""
    response = requests.get(f"{API_URL}/causes")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    causes = response.json()
    assert len(causes) > 0, f"Expected at least one cause, got {len(causes)}"
    
    # Verify cause structure
    required_fields = ["id", "name", "description", "category", "impact_metric", "cost_per_impact"]
    for cause in causes:
        for field in required_fields:
            assert field in cause, f"Missing required field '{field}' in cause"
    
    print(f"Found {len(causes)} causes")
    return True

def test_get_businesses():
    """Test GET /api/businesses endpoint"""
    response = requests.get(f"{API_URL}/businesses")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    businesses = response.json()
    assert len(businesses) > 0, "Expected at least one business"
    
    # Verify demo business exists
    found_demo = False
    for business in businesses:
        if business["name"] == "EcoTech Solutions":
            found_demo = True
            break
    
    assert found_demo, "Could not find demo business 'EcoTech Solutions'"
    
    print("Successfully retrieved businesses including demo business")
    return True

def test_get_customers():
    """Test GET /api/customers endpoint"""
    response = requests.get(f"{API_URL}/customers")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    customers = response.json()
    assert len(customers) > 0, "Expected at least one customer"
    
    # Verify demo customer exists
    found_demo = False
    for customer in customers:
        if customer["name"] == "Sarah Green":
            found_demo = True
            break
    
    assert found_demo, "Could not find demo customer 'Sarah Green'"
    
    print("Successfully retrieved customers including demo customer")
    return True

def test_get_admin_demo_users():
    """Test GET /api/admin/demo-users endpoint"""
    response = requests.get(f"{API_URL}/admin/demo-users")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    demo_users = response.json()
    assert "businesses" in demo_users, "Response missing 'businesses' field"
    assert "customers" in demo_users, "Response missing 'customers' field"
    assert "admins" in demo_users, "Response missing 'admins' field"
    
    # Verify demo business exists
    assert len(demo_users["businesses"]) > 0, "Expected at least one demo business"
    found_demo_business = False
    for business in demo_users["businesses"]:
        if business["name"] == "EcoTech Solutions":
            found_demo_business = True
            break
    assert found_demo_business, "Could not find demo business 'EcoTech Solutions'"
    
    # Verify demo customer exists
    assert len(demo_users["customers"]) > 0, "Expected at least one demo customer"
    found_demo_customer = False
    for customer in demo_users["customers"]:
        if customer["name"] == "Sarah Green":
            found_demo_customer = True
            break
    assert found_demo_customer, "Could not find demo customer 'Sarah Green'"
    
    # Verify admin users exist
    assert len(demo_users["admins"]) > 0, "Expected at least one admin user"
    
    # Check if admin emails use @nnoboa.com instead of @impactlink.com
    for admin in demo_users["admins"]:
        assert "@nnoboa.com" in admin["email"], f"Admin email {admin['email']} does not use @nnoboa.com domain"
        assert "@impactlink.com" not in admin["email"], f"Admin email {admin['email']} still uses @impactlink.com domain"
    
    print("Successfully retrieved demo users with correct email domains")
    return True

def test_developer_platform():
    """Test GET /api/dev/docs endpoint for SDK information with Nnoboa branding"""
    response = requests.get(f"{API_URL}/dev/docs")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    docs = response.json()
    assert "title" in docs, "API docs missing 'title' field"
    assert "Nnoboa" in docs["title"], f"API docs title '{docs['title']}' does not contain 'Nnoboa'"
    assert "ImpactLink" not in docs["title"], f"API docs title '{docs['title']}' still contains 'ImpactLink'"
    
    # Check base URL
    assert "base_url" in docs, "API docs missing 'base_url' field"
    assert "nnoboa.com" in docs["base_url"], f"API docs base_url '{docs['base_url']}' does not contain 'nnoboa.com'"
    assert "impactlink.com" not in docs["base_url"], f"API docs base_url '{docs['base_url']}' still contains 'impactlink.com'"
    
    print("Developer platform documentation shows correct Nnoboa branding")
    return True

def test_sdk_information():
    """Test GET /api/dev/sdk endpoint for SDK names and package names with Nnoboa branding"""
    response = requests.get(f"{API_URL}/dev/sdk")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    sdk_info = response.json()
    assert "sdks" in sdk_info, "SDK info missing 'sdks' field"
    
    # Check SDK names and package names
    for sdk_type, sdk in sdk_info["sdks"].items():
        assert "name" in sdk, f"{sdk_type} SDK missing 'name' field"
        assert "Nnoboa" in sdk["name"], f"{sdk_type} SDK name '{sdk['name']}' does not contain 'Nnoboa'"
        assert "ImpactLink" not in sdk["name"], f"{sdk_type} SDK name '{sdk['name']}' still contains 'ImpactLink'"
        
        assert "install" in sdk, f"{sdk_type} SDK missing 'install' field"
        assert "nnoboa" in sdk["install"].lower(), f"{sdk_type} SDK install command '{sdk['install']}' does not contain 'nnoboa'"
        assert "impactlink" not in sdk["install"].lower(), f"{sdk_type} SDK install command '{sdk['install']}' still contains 'impactlink'"
        
        assert "docs" in sdk, f"{sdk_type} SDK missing 'docs' field"
        assert "nnoboa.com" in sdk["docs"], f"{sdk_type} SDK docs URL '{sdk['docs']}' does not contain 'nnoboa.com'"
        assert "impactlink.com" not in sdk["docs"], f"{sdk_type} SDK docs URL '{sdk['docs']}' still contains 'impactlink.com'"
    
    # Check plugins
    if "plugins" in sdk_info:
        for plugin_type, plugin in sdk_info["plugins"].items():
            assert "name" in plugin, f"{plugin_type} plugin missing 'name' field"
            assert "Nnoboa" in plugin["name"], f"{plugin_type} plugin name '{plugin['name']}' does not contain 'Nnoboa'"
            assert "ImpactLink" not in plugin["name"], f"{plugin_type} plugin name '{plugin['name']}' still contains 'ImpactLink'"
    
    print("SDK information shows correct Nnoboa branding")
    return True

def test_account_number_format():
    """Test if account numbers use Nnoboa prefix instead of ImpactLink prefix"""
    # Check businesses
    response = requests.get(f"{API_URL}/businesses")
    businesses = response.json()
    
    for business in businesses:
        assert "account_number" in business, f"Business {business['id']} missing 'account_number' field"
        # Check if account number starts with "IL" (old format)
        assert not business["account_number"].startswith("IL"), f"Business account number '{business['account_number']}' still uses 'IL' prefix"
    
    # Check customers
    response = requests.get(f"{API_URL}/customers")
    customers = response.json()
    
    for customer in customers:
        assert "account_number" in customer, f"Customer {customer['id']} missing 'account_number' field"
        # Check if account number starts with "IL" (old format)
        assert not customer["account_number"].startswith("IL"), f"Customer account number '{customer['account_number']}' still uses 'IL' prefix"
    
    print("Account numbers do not use 'IL' prefix")
    return True

def test_api_key_format():
    """Test if API keys use Nnoboa prefix instead of ImpactLink prefix"""
    # Check businesses
    response = requests.get(f"{API_URL}/businesses")
    businesses = response.json()
    
    for business in businesses:
        assert "api_key" in business, f"Business {business['id']} missing 'api_key' field"
        # Check if API key starts with "il_" (old format)
        assert not business["api_key"].startswith("il_"), f"Business API key '{business['api_key']}' still uses 'il_' prefix"
    
    print("API keys do not use 'il_' prefix")
    return True

if __name__ == "__main__":
    print("\n===== TESTING NNOBOA REBRANDING =====")
    
    # Test API title and branding
    run_test("API Title and Branding", test_api_title_branding)
    
    # Test core functionality
    run_test("GET /api/causes", test_get_causes)
    run_test("GET /api/businesses", test_get_businesses)
    run_test("GET /api/customers", test_get_customers)
    run_test("GET /api/admin/demo-users", test_get_admin_demo_users)
    
    # Test developer platform
    run_test("Developer Platform", test_developer_platform)
    run_test("SDK Information", test_sdk_information)
    
    # Test account number and API key formats
    run_test("Account Number Format", test_account_number_format)
    run_test("API Key Format", test_api_key_format)
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"TEST SUMMARY: {test_results['passed']} passed, {test_results['failed']} failed")
    print(f"{'='*80}")
    
    for test in test_results["tests"]:
        status_symbol = "✅" if test["status"] == "PASSED" else "❌"
        print(f"{status_symbol} {test['name']}")
        if test["status"] == "FAILED" and "error" in test:
            print(f"   Error: {test['error']}")
    
    print(f"{'='*80}")
    
    # Exit with appropriate status code
    exit(0 if test_results["failed"] == 0 else 1)