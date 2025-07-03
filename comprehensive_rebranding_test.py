#!/usr/bin/env python3
import requests
import json
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

def test_nnoboa_rebranding():
    """Test all rebranding requirements in one comprehensive test"""
    results = {
        "api_title": {"status": "PASSED", "details": ""},
        "causes_endpoint": {"status": "PASSED", "details": ""},
        "businesses_endpoint": {"status": "PASSED", "details": ""},
        "customers_endpoint": {"status": "PASSED", "details": ""},
        "demo_users_endpoint": {"status": "PASSED", "details": ""},
        "developer_platform": {"status": "PASSED", "details": ""},
        "sdk_information": {"status": "PASSED", "details": ""},
        "account_numbers": {"status": "PASSED", "details": ""},
        "api_keys": {"status": "PASSED", "details": ""}
    }
    
    # 1. Check API Title
    try:
        with open('/app/backend/server.py', 'r') as f:
            server_code = f.read()
        
        if 'FastAPI(title="Nnoboa API"' in server_code:
            results["api_title"]["details"] = "FastAPI app initialized with 'Nnoboa API' title"
        else:
            results["api_title"]["status"] = "FAILED"
            results["api_title"]["details"] = "FastAPI app not initialized with 'Nnoboa API' title"
    except Exception as e:
        results["api_title"]["status"] = "FAILED"
        results["api_title"]["details"] = f"Error checking API title: {str(e)}"
    
    # 2. Check GET /api/causes
    try:
        response = requests.get(f"{API_URL}/causes")
        if response.status_code == 200:
            causes = response.json()
            if len(causes) > 0:
                results["causes_endpoint"]["details"] = f"Found {len(causes)} causes"
            else:
                results["causes_endpoint"]["status"] = "FAILED"
                results["causes_endpoint"]["details"] = "No causes returned"
        else:
            results["causes_endpoint"]["status"] = "FAILED"
            results["causes_endpoint"]["details"] = f"Expected status code 200, got {response.status_code}"
    except Exception as e:
        results["causes_endpoint"]["status"] = "FAILED"
        results["causes_endpoint"]["details"] = f"Error checking causes endpoint: {str(e)}"
    
    # 3. Check GET /api/businesses
    try:
        response = requests.get(f"{API_URL}/businesses")
        if response.status_code == 200:
            businesses = response.json()
            if len(businesses) > 0:
                # Check for demo business
                found_demo = False
                for business in businesses:
                    if business["name"] == "EcoTech Solutions":
                        found_demo = True
                        break
                
                if found_demo:
                    results["businesses_endpoint"]["details"] = "Found demo business 'EcoTech Solutions'"
                else:
                    results["businesses_endpoint"]["status"] = "FAILED"
                    results["businesses_endpoint"]["details"] = "Could not find demo business 'EcoTech Solutions'"
            else:
                results["businesses_endpoint"]["status"] = "FAILED"
                results["businesses_endpoint"]["details"] = "No businesses returned"
        else:
            results["businesses_endpoint"]["status"] = "FAILED"
            results["businesses_endpoint"]["details"] = f"Expected status code 200, got {response.status_code}"
    except Exception as e:
        results["businesses_endpoint"]["status"] = "FAILED"
        results["businesses_endpoint"]["details"] = f"Error checking businesses endpoint: {str(e)}"
    
    # 4. Check GET /api/customers
    try:
        response = requests.get(f"{API_URL}/customers")
        if response.status_code == 200:
            customers = response.json()
            if len(customers) > 0:
                # Check for demo customer
                found_demo = False
                for customer in customers:
                    if customer["name"] == "Sarah Green":
                        found_demo = True
                        break
                
                if found_demo:
                    results["customers_endpoint"]["details"] = "Found demo customer 'Sarah Green'"
                else:
                    results["customers_endpoint"]["status"] = "FAILED"
                    results["customers_endpoint"]["details"] = "Could not find demo customer 'Sarah Green'"
            else:
                results["customers_endpoint"]["status"] = "FAILED"
                results["customers_endpoint"]["details"] = "No customers returned"
        else:
            results["customers_endpoint"]["status"] = "FAILED"
            results["customers_endpoint"]["details"] = f"Expected status code 200, got {response.status_code}"
    except Exception as e:
        results["customers_endpoint"]["status"] = "FAILED"
        results["customers_endpoint"]["details"] = f"Error checking customers endpoint: {str(e)}"
    
    # 5. Check GET /api/admin/demo-users
    try:
        response = requests.get(f"{API_URL}/admin/demo-users")
        if response.status_code == 200:
            demo_users = response.json()
            if "businesses" in demo_users and "customers" in demo_users and "admins" in demo_users:
                # Check admin emails
                all_emails_correct = True
                for admin in demo_users["admins"]:
                    if "@nnoboa.com" not in admin["email"] or "@impactlink.com" in admin["email"]:
                        all_emails_correct = False
                        break
                
                if all_emails_correct:
                    results["demo_users_endpoint"]["details"] = "Admin emails use @nnoboa.com domain"
                else:
                    results["demo_users_endpoint"]["status"] = "FAILED"
                    results["demo_users_endpoint"]["details"] = "Some admin emails do not use @nnoboa.com domain"
            else:
                results["demo_users_endpoint"]["status"] = "FAILED"
                results["demo_users_endpoint"]["details"] = "Response missing required fields"
        else:
            results["demo_users_endpoint"]["status"] = "FAILED"
            results["demo_users_endpoint"]["details"] = f"Expected status code 200, got {response.status_code}"
    except Exception as e:
        results["demo_users_endpoint"]["status"] = "FAILED"
        results["demo_users_endpoint"]["details"] = f"Error checking demo users endpoint: {str(e)}"
    
    # 6. Check GET /api/dev/docs
    try:
        response = requests.get(f"{API_URL}/dev/docs")
        if response.status_code == 200:
            docs = response.json()
            if "title" in docs and "Nnoboa" in docs["title"] and "ImpactLink" not in docs["title"]:
                results["developer_platform"]["details"] = f"Developer platform shows '{docs['title']}'"
            else:
                results["developer_platform"]["status"] = "FAILED"
                results["developer_platform"]["details"] = "Developer platform does not show correct branding"
        else:
            results["developer_platform"]["status"] = "FAILED"
            results["developer_platform"]["details"] = f"Expected status code 200, got {response.status_code}"
    except Exception as e:
        results["developer_platform"]["status"] = "FAILED"
        results["developer_platform"]["details"] = f"Error checking developer platform: {str(e)}"
    
    # 7. Check GET /api/dev/sdk
    try:
        response = requests.get(f"{API_URL}/dev/sdk")
        if response.status_code == 200:
            sdk_info = response.json()
            if "sdks" in sdk_info:
                all_sdks_correct = True
                for sdk_type, sdk in sdk_info["sdks"].items():
                    if "name" not in sdk or "Nnoboa" not in sdk["name"] or "ImpactLink" in sdk["name"]:
                        all_sdks_correct = False
                        break
                    if "install" not in sdk or "nnoboa" not in sdk["install"].lower() or "impactlink" in sdk["install"].lower():
                        all_sdks_correct = False
                        break
                
                if all_sdks_correct:
                    results["sdk_information"]["details"] = "SDK information shows correct Nnoboa branding"
                else:
                    results["sdk_information"]["status"] = "FAILED"
                    results["sdk_information"]["details"] = "Some SDK information does not show correct branding"
            else:
                results["sdk_information"]["status"] = "FAILED"
                results["sdk_information"]["details"] = "Response missing 'sdks' field"
        else:
            results["sdk_information"]["status"] = "FAILED"
            results["sdk_information"]["details"] = f"Expected status code 200, got {response.status_code}"
    except Exception as e:
        results["sdk_information"]["status"] = "FAILED"
        results["sdk_information"]["details"] = f"Error checking SDK information: {str(e)}"
    
    # 8. Check account number format
    try:
        # Check businesses
        response = requests.get(f"{API_URL}/businesses")
        if response.status_code == 200:
            businesses = response.json()
            all_account_numbers_correct = True
            for business in businesses:
                if "account_number" in business and business["account_number"].startswith("IL"):
                    all_account_numbers_correct = False
                    break
            
            # Check customers
            response = requests.get(f"{API_URL}/customers")
            if response.status_code == 200:
                customers = response.json()
                for customer in customers:
                    if "account_number" in customer and customer["account_number"].startswith("IL"):
                        all_account_numbers_correct = False
                        break
                
                if all_account_numbers_correct:
                    results["account_numbers"]["details"] = "Account numbers do not use 'IL' prefix"
                else:
                    results["account_numbers"]["status"] = "FAILED"
                    results["account_numbers"]["details"] = "Some account numbers still use 'IL' prefix"
            else:
                results["account_numbers"]["status"] = "FAILED"
                results["account_numbers"]["details"] = f"Expected status code 200 for customers, got {response.status_code}"
        else:
            results["account_numbers"]["status"] = "FAILED"
            results["account_numbers"]["details"] = f"Expected status code 200 for businesses, got {response.status_code}"
    except Exception as e:
        results["account_numbers"]["status"] = "FAILED"
        results["account_numbers"]["details"] = f"Error checking account numbers: {str(e)}"
    
    # 9. Check API key format
    try:
        # Check businesses
        response = requests.get(f"{API_URL}/businesses")
        if response.status_code == 200:
            businesses = response.json()
            all_api_keys_correct = True
            for business in businesses:
                if "api_key" in business and business["api_key"].startswith("il_"):
                    all_api_keys_correct = False
                    break
            
            if all_api_keys_correct:
                results["api_keys"]["details"] = "API keys do not use 'il_' prefix"
            else:
                results["api_keys"]["status"] = "FAILED"
                results["api_keys"]["details"] = "Some API keys still use 'il_' prefix"
        else:
            results["api_keys"]["status"] = "FAILED"
            results["api_keys"]["details"] = f"Expected status code 200 for businesses, got {response.status_code}"
    except Exception as e:
        results["api_keys"]["status"] = "FAILED"
        results["api_keys"]["details"] = f"Error checking API keys: {str(e)}"
    
    # Print results
    print("\n===== NNOBOA REBRANDING TEST RESULTS =====\n")
    
    passed = 0
    failed = 0
    for test, result in results.items():
        status_symbol = "✅" if result["status"] == "PASSED" else "❌"
        print(f"{status_symbol} {test}: {result['details']}")
        if result["status"] == "PASSED":
            passed += 1
        else:
            failed += 1
    
    print(f"\nSUMMARY: {passed} passed, {failed} failed")
    
    return passed, failed

if __name__ == "__main__":
    passed, failed = test_nnoboa_rebranding()
    exit(0 if failed == 0 else 1)