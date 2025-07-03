#!/usr/bin/env python3
import requests
import json
import time
import os
from pprint import pprint
from datetime import datetime, timedelta

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

# ===== COMPREHENSIVE CUSTOMER REGISTRATION TESTS =====

def test_comprehensive_customer_registration():
    """Test POST /api/customers endpoint with comprehensive data"""
    # Use a timestamp to ensure unique email
    timestamp = int(time.time())
    
    # Create a comprehensive customer data object
    customer_data = {
        # Basic fields
        "name": "John Doe",
        "email": f"john.doe{timestamp}@example.com",
        "phone": "+233-555-1234-5678",
        "address": {
            "street": "123 Main Street",
            "city": "Accra",
            "state": "Greater Accra",
            "postal_code": "00233",
            "country": "Ghana"
        },
        
        # Additional fields
        "date_of_birth": "1985-05-15",
        "occupation": "Software Engineer",
        "interests": ["technology", "sustainability", "education"],
        "bio": "Passionate about using technology to drive social change",
        
        # Settlement information
        "settlement_info": {
            "account_number": "9876543210",
            "phone_number": "+233-555-1234-5678",
            "bank_name": "Ghana Commercial Bank",
            "bank_code": "GCB001",
            "account_type": "savings",
            "verified": False
        },
        
        # Preferences
        "preferred_causes": [],  # Will be populated with actual cause IDs
        "newsletter_subscription": True,
        "marketing_consent": True
    }
    
    # Get some causes to add to preferred_causes
    response = requests.get(f"{API_URL}/causes")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    causes = response.json()
    if len(causes) >= 2:
        customer_data["preferred_causes"] = [causes[0]["id"], causes[1]["id"]]
    
    # Send the registration request
    response = requests.post(f"{API_URL}/customers", json=customer_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    customer = response.json()
    
    # Verify the response contains the expected fields
    assert "id" in customer, "Customer response missing 'id' field"
    assert "name" in customer, "Customer response missing 'name' field"
    assert "email" in customer, "Customer response missing 'email' field"
    assert "phone" in customer, "Customer response missing 'phone' field"
    assert "account_number" in customer, "Customer response missing 'account_number' field"
    assert "preferred_causes" in customer, "Customer response missing 'preferred_causes' field"
    assert "settlement_info" in customer, "Customer response missing 'settlement_info' field"
    
    # Verify the values match what we sent
    assert customer["name"] == customer_data["name"], f"Expected name {customer_data['name']}, got {customer['name']}"
    assert customer["phone"] == customer_data["phone"], f"Expected phone {customer_data['phone']}, got {customer['phone']}"
    
    # Verify settlement info
    settlement_info = customer["settlement_info"]
    assert settlement_info["account_number"] == customer_data["settlement_info"]["account_number"], f"Expected account_number {customer_data['settlement_info']['account_number']}, got {settlement_info['account_number']}"
    assert settlement_info["bank_name"] == customer_data["settlement_info"]["bank_name"], f"Expected bank_name {customer_data['settlement_info']['bank_name']}, got {settlement_info['bank_name']}"
    assert settlement_info["account_type"] == customer_data["settlement_info"]["account_type"], f"Expected account_type {customer_data['settlement_info']['account_type']}, got {settlement_info['account_type']}"
    
    # Verify preferred causes
    if len(customer_data["preferred_causes"]) > 0:
        assert len(customer["preferred_causes"]) == len(customer_data["preferred_causes"]), f"Expected {len(customer_data['preferred_causes'])} preferred causes, got {len(customer['preferred_causes'])}"
    
    # Store customer ID for later tests
    global test_customer_id
    test_customer_id = customer["id"]
    print(f"Created customer with ID: {test_customer_id}")
    
    return True

def test_customer_registration_validation():
    """Test validation for customer registration"""
    # Test missing required fields
    customer_data = {
        # Missing name
        "email": "missing.name@example.com",
        "phone": "+233-555-9876-5432"
    }
    
    response = requests.post(f"{API_URL}/customers", json=customer_data)
    assert response.status_code in [400, 422], f"Expected status code 400 or 422 for missing required field, got {response.status_code}"
    
    # Test duplicate email
    timestamp = int(time.time())
    email = f"duplicate{timestamp}@example.com"
    
    # Create first customer
    customer_data = {
        "name": "First Customer",
        "email": email,
        "phone": "+233-555-1111-2222"
    }
    
    response = requests.post(f"{API_URL}/customers", json=customer_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # Try to create second customer with same email
    customer_data = {
        "name": "Second Customer",
        "email": email,
        "phone": "+233-555-3333-4444"
    }
    
    response = requests.post(f"{API_URL}/customers", json=customer_data)
    assert response.status_code == 400, f"Expected status code 400 for duplicate email, got {response.status_code}"
    
    return True

def test_get_customer_by_id():
    """Test GET /api/customers/{id} endpoint with the created customer"""
    response = requests.get(f"{API_URL}/customers/{test_customer_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    customer = response.json()
    assert customer["id"] == test_customer_id, f"Expected customer id {test_customer_id}, got {customer['id']}"
    
    # Verify the customer has all the expected fields
    assert "name" in customer, "Customer response missing 'name' field"
    assert "email" in customer, "Customer response missing 'email' field"
    assert "phone" in customer, "Customer response missing 'phone' field"
    assert "account_number" in customer, "Customer response missing 'account_number' field"
    assert "preferred_causes" in customer, "Customer response missing 'preferred_causes' field"
    assert "settlement_info" in customer, "Customer response missing 'settlement_info' field"
    
    return True

# ===== COMPREHENSIVE BUSINESS REGISTRATION TESTS =====

def test_comprehensive_business_registration():
    """Test POST /api/businesses endpoint with comprehensive data"""
    # Use a timestamp to ensure unique email
    timestamp = int(time.time())
    
    # Create a comprehensive business data object
    business_data = {
        # Business info
        "name": "EcoFriendly Solutions Ltd",
        "description": "Providing sustainable solutions for businesses and communities",
        "industry": "Environmental Services",
        "business_type": "Limited Company",
        "company_size": "11-50 employees",
        "tax_id": "GH123456789",
        "website": "https://ecofriendly-solutions.example.com",
        
        # Contact info
        "contact_person": "Jane Smith",
        "email": f"info{timestamp}@ecofriendly-solutions.example.com",
        "phone": "+233-555-8765-4321",
        
        # Address info
        "business_address": {
            "street": "456 Innovation Avenue",
            "city": "Kumasi",
            "state": "Ashanti",
            "postal_code": "00234",
            "country": "Ghana"
        },
        
        # Settlement information
        "settlement_info": {
            "account_number": "1234567890",
            "bank_name": "Ecobank Ghana",
            "bank_code": "ECO001",
            "account_type": "checking",
            "verified": False
        },
        
        # Preferences
        "preferred_causes": [],  # Will be populated with actual cause IDs
        "newsletter_subscription": True,
        "marketing_consent": True
    }
    
    # Get some causes to add to preferred_causes
    response = requests.get(f"{API_URL}/causes")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    causes = response.json()
    if len(causes) >= 2:
        business_data["preferred_causes"] = [causes[0]["id"], causes[1]["id"]]
    
    # Send the registration request
    response = requests.post(f"{API_URL}/businesses", json=business_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    business = response.json()
    
    # Verify the response contains the expected fields
    assert "id" in business, "Business response missing 'id' field"
    assert "name" in business, "Business response missing 'name' field"
    assert "description" in business, "Business response missing 'description' field"
    assert "industry" in business, "Business response missing 'industry' field"
    assert "email" in business, "Business response missing 'email' field"
    assert "phone" in business, "Business response missing 'phone' field"
    assert "website" in business, "Business response missing 'website' field"
    assert "account_number" in business, "Business response missing 'account_number' field"
    assert "api_key" in business, "Business response missing 'api_key' field"
    assert "preferred_causes" in business, "Business response missing 'preferred_causes' field"
    assert "settlement_info" in business, "Business response missing 'settlement_info' field"
    
    # Verify the values match what we sent
    assert business["name"] == business_data["name"], f"Expected name {business_data['name']}, got {business['name']}"
    assert business["description"] == business_data["description"], f"Expected description {business_data['description']}, got {business['description']}"
    assert business["industry"] == business_data["industry"], f"Expected industry {business_data['industry']}, got {business['industry']}"
    assert business["phone"] == business_data["phone"], f"Expected phone {business_data['phone']}, got {business['phone']}"
    assert business["website"] == business_data["website"], f"Expected website {business_data['website']}, got {business['website']}"
    
    # Verify settlement info
    settlement_info = business["settlement_info"]
    assert settlement_info["account_number"] == business_data["settlement_info"]["account_number"], f"Expected account_number {business_data['settlement_info']['account_number']}, got {settlement_info['account_number']}"
    assert settlement_info["bank_name"] == business_data["settlement_info"]["bank_name"], f"Expected bank_name {business_data['settlement_info']['bank_name']}, got {settlement_info['bank_name']}"
    assert settlement_info["account_type"] == business_data["settlement_info"]["account_type"], f"Expected account_type {business_data['settlement_info']['account_type']}, got {settlement_info['account_type']}"
    
    # Verify preferred causes
    if len(business_data["preferred_causes"]) > 0:
        assert len(business["preferred_causes"]) == len(business_data["preferred_causes"]), f"Expected {len(business_data['preferred_causes'])} preferred causes, got {len(business['preferred_causes'])}"
    
    # Verify API key format
    assert business["api_key"].startswith("nn_"), f"Expected API key to start with 'nn_', got {business['api_key']}"
    
    # Store business ID and API key for later tests
    global test_business_id, test_business_api_key
    test_business_id = business["id"]
    test_business_api_key = business["api_key"]
    print(f"Created business with ID: {test_business_id}")
    print(f"Business API key: {test_business_api_key}")
    
    return True

def test_business_registration_validation():
    """Test validation for business registration"""
    # Test missing required fields
    business_data = {
        # Missing name
        "description": "Test business with missing name",
        "industry": "Technology",
        "email": "missing.name@example.com"
    }
    
    response = requests.post(f"{API_URL}/businesses", json=business_data)
    assert response.status_code in [400, 422], f"Expected status code 400 or 422 for missing required field, got {response.status_code}"
    
    return True

def test_get_business_by_id():
    """Test GET /api/businesses/{id} endpoint with the created business"""
    response = requests.get(f"{API_URL}/businesses/{test_business_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    business = response.json()
    assert business["id"] == test_business_id, f"Expected business id {test_business_id}, got {business['id']}"
    
    # Verify the business has all the expected fields
    assert "name" in business, "Business response missing 'name' field"
    assert "description" in business, "Business response missing 'description' field"
    assert "industry" in business, "Business response missing 'industry' field"
    assert "email" in business, "Business response missing 'email' field"
    assert "phone" in business, "Business response missing 'phone' field"
    assert "website" in business, "Business response missing 'website' field"
    assert "account_number" in business, "Business response missing 'account_number' field"
    assert "api_key" in business, "Business response missing 'api_key' field"
    assert "preferred_causes" in business, "Business response missing 'preferred_causes' field"
    assert "settlement_info" in business, "Business response missing 'settlement_info' field"
    
    return True

# ===== SUBSCRIPTION API TESTS =====

def test_get_subscription_plans():
    """Test GET /api/subscription-plans endpoint"""
    response = requests.get(f"{API_URL}/subscription-plans")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    plans = response.json()
    
    # Verify the response contains plans for both individual and business
    assert "individual" in plans, "Subscription plans missing 'individual' category"
    assert "business" in plans, "Subscription plans missing 'business' category"
    
    # Verify individual plans
    individual_plans = plans["individual"]
    assert "monthly" in individual_plans, "Individual plans missing 'monthly' plan"
    assert "yearly" in individual_plans, "Individual plans missing 'yearly' plan"
    assert "premium" in individual_plans, "Individual plans missing 'premium' plan"
    
    # Verify business plans
    business_plans = plans["business"]
    assert "monthly" in business_plans, "Business plans missing 'monthly' plan"
    assert "yearly" in business_plans, "Business plans missing 'yearly' plan"
    assert "premium" in business_plans, "Business plans missing 'premium' plan"
    
    # Verify plan structure
    for plan_type in ["monthly", "yearly", "premium"]:
        for user_type in ["individual", "business"]:
            plan = plans[user_type][plan_type]
            assert "price" in plan, f"{user_type} {plan_type} plan missing 'price' field"
            assert "features" in plan, f"{user_type} {plan_type} plan missing 'features' field"
            assert isinstance(plan["features"], list), f"Expected features to be a list, got {type(plan['features'])}"
    
    return True

def test_create_customer_subscription():
    """Test POST /api/subscriptions endpoint for customer"""
    subscription_data = {
        "plan_type": "monthly",
        "auto_renew": True
    }
    
    response = requests.post(f"{API_URL}/subscriptions?user_id={test_customer_id}&user_type=customer", json=subscription_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    subscription = response.json()
    
    # Verify the response contains the expected fields
    assert "id" in subscription, "Subscription response missing 'id' field"
    assert "user_id" in subscription, "Subscription response missing 'user_id' field"
    assert "user_type" in subscription, "Subscription response missing 'user_type' field"
    assert "plan_type" in subscription, "Subscription response missing 'plan_type' field"
    assert "amount" in subscription, "Subscription response missing 'amount' field"
    assert "currency" in subscription, "Subscription response missing 'currency' field"
    assert "status" in subscription, "Subscription response missing 'status' field"
    assert "start_date" in subscription, "Subscription response missing 'start_date' field"
    assert "end_date" in subscription, "Subscription response missing 'end_date' field"
    assert "auto_renew" in subscription, "Subscription response missing 'auto_renew' field"
    
    # Verify the values match what we sent
    assert subscription["user_id"] == test_customer_id, f"Expected user_id {test_customer_id}, got {subscription['user_id']}"
    assert subscription["user_type"] == "customer", f"Expected user_type 'customer', got {subscription['user_type']}"
    assert subscription["plan_type"] == subscription_data["plan_type"], f"Expected plan_type {subscription_data['plan_type']}, got {subscription['plan_type']}"
    assert subscription["auto_renew"] == subscription_data["auto_renew"], f"Expected auto_renew {subscription_data['auto_renew']}, got {subscription['auto_renew']}"
    assert subscription["status"] == "active", f"Expected status 'active', got {subscription['status']}"
    
    # Store subscription ID for later tests
    global test_customer_subscription_id
    test_customer_subscription_id = subscription["id"]
    print(f"Created customer subscription with ID: {test_customer_subscription_id}")
    
    return True

def test_create_business_subscription():
    """Test POST /api/subscriptions endpoint for business"""
    subscription_data = {
        "plan_type": "yearly",
        "auto_renew": True
    }
    
    response = requests.post(f"{API_URL}/subscriptions?user_id={test_business_id}&user_type=business", json=subscription_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    subscription = response.json()
    
    # Verify the response contains the expected fields
    assert "id" in subscription, "Subscription response missing 'id' field"
    assert "user_id" in subscription, "Subscription response missing 'user_id' field"
    assert "user_type" in subscription, "Subscription response missing 'user_type' field"
    assert "plan_type" in subscription, "Subscription response missing 'plan_type' field"
    assert "amount" in subscription, "Subscription response missing 'amount' field"
    assert "currency" in subscription, "Subscription response missing 'currency' field"
    assert "status" in subscription, "Subscription response missing 'status' field"
    assert "start_date" in subscription, "Subscription response missing 'start_date' field"
    assert "end_date" in subscription, "Subscription response missing 'end_date' field"
    assert "auto_renew" in subscription, "Subscription response missing 'auto_renew' field"
    
    # Verify the values match what we sent
    assert subscription["user_id"] == test_business_id, f"Expected user_id {test_business_id}, got {subscription['user_id']}"
    assert subscription["user_type"] == "business", f"Expected user_type 'business', got {subscription['user_type']}"
    assert subscription["plan_type"] == subscription_data["plan_type"], f"Expected plan_type {subscription_data['plan_type']}, got {subscription['plan_type']}"
    assert subscription["auto_renew"] == subscription_data["auto_renew"], f"Expected auto_renew {subscription_data['auto_renew']}, got {subscription['auto_renew']}"
    assert subscription["status"] == "active", f"Expected status 'active', got {subscription['status']}"
    
    # Store subscription ID for later tests
    global test_business_subscription_id
    test_business_subscription_id = subscription["id"]
    print(f"Created business subscription with ID: {test_business_subscription_id}")
    
    return True

def test_get_user_subscription():
    """Test GET /api/subscriptions/{user_id} endpoint"""
    # Test customer subscription
    response = requests.get(f"{API_URL}/subscriptions/{test_customer_id}?user_type=customer")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    subscription = response.json()
    assert subscription["id"] == test_customer_subscription_id, f"Expected subscription id {test_customer_subscription_id}, got {subscription['id']}"
    
    # Test business subscription
    response = requests.get(f"{API_URL}/subscriptions/{test_business_id}?user_type=business")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    subscription = response.json()
    assert subscription["id"] == test_business_subscription_id, f"Expected subscription id {test_business_subscription_id}, got {subscription['id']}"
    
    return True

def test_subscription_validation():
    """Test validation for subscription creation"""
    # Test invalid user type
    subscription_data = {
        "plan_type": "monthly",
        "auto_renew": True
    }
    
    response = requests.post(f"{API_URL}/subscriptions?user_id={test_customer_id}&user_type=invalid", json=subscription_data)
    assert response.status_code == 400, f"Expected status code 400 for invalid user type, got {response.status_code}"
    
    # Test invalid plan type
    subscription_data = {
        "plan_type": "invalid",
        "auto_renew": True
    }
    
    response = requests.post(f"{API_URL}/subscriptions?user_id={test_customer_id}&user_type=customer", json=subscription_data)
    assert response.status_code == 400, f"Expected status code 400 for invalid plan type, got {response.status_code}"
    
    # Test duplicate subscription (user already has an active subscription)
    subscription_data = {
        "plan_type": "premium",
        "auto_renew": True
    }
    
    response = requests.post(f"{API_URL}/subscriptions?user_id={test_customer_id}&user_type=customer", json=subscription_data)
    assert response.status_code == 400, f"Expected status code 400 for duplicate subscription, got {response.status_code}"
    
    return True

# ===== ACCOUNT NUMBER AND API KEY GENERATION TESTS =====

def test_account_number_generation():
    """Test account number generation for new users"""
    # Create a new customer to check account number format
    timestamp = int(time.time())
    customer_data = {
        "name": "Account Number Test",
        "email": f"account.test{timestamp}@example.com",
        "phone": "+233-555-9999-8888"
    }
    
    response = requests.post(f"{API_URL}/customers", json=customer_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    customer = response.json()
    assert "account_number" in customer, "Customer response missing 'account_number' field"
    
    # Verify account number format (should start with NN followed by 10 digits)
    account_number = customer["account_number"]
    assert account_number.startswith("NN"), f"Expected account number to start with 'NN', got {account_number}"
    assert len(account_number) == 12, f"Expected account number length 12, got {len(account_number)}"
    assert account_number[2:].isdigit(), f"Expected account number to have 10 digits after 'NN', got {account_number[2:]}"
    
    # Create a new business to check account number format
    business_data = {
        "name": "API Key Test",
        "description": "Testing API key generation",
        "industry": "Technology",
        "email": f"api.test{timestamp}@example.com",
        "phone": "+233-555-7777-6666"
    }
    
    response = requests.post(f"{API_URL}/businesses", json=business_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    business = response.json()
    assert "account_number" in business, "Business response missing 'account_number' field"
    assert "api_key" in business, "Business response missing 'api_key' field"
    
    # Verify account number format
    account_number = business["account_number"]
    assert account_number.startswith("NN"), f"Expected account number to start with 'NN', got {account_number}"
    assert len(account_number) == 12, f"Expected account number length 12, got {len(account_number)}"
    assert account_number[2:].isdigit(), f"Expected account number to have 10 digits after 'NN', got {account_number[2:]}"
    
    # Verify API key format
    api_key = business["api_key"]
    assert api_key.startswith("nn_"), f"Expected API key to start with 'nn_', got {api_key}"
    assert len(api_key) >= 24, f"Expected API key length at least 24, got {len(api_key)}"
    
    return True

# Run all tests
if __name__ == "__main__":
    # Customer Registration Tests
    run_test("Comprehensive Customer Registration", test_comprehensive_customer_registration)
    run_test("Customer Registration Validation", test_customer_registration_validation)
    run_test("Get Customer by ID", test_get_customer_by_id)
    
    # Business Registration Tests
    run_test("Comprehensive Business Registration", test_comprehensive_business_registration)
    run_test("Business Registration Validation", test_business_registration_validation)
    run_test("Get Business by ID", test_get_business_by_id)
    
    # Subscription API Tests
    run_test("Get Subscription Plans", test_get_subscription_plans)
    run_test("Create Customer Subscription", test_create_customer_subscription)
    run_test("Create Business Subscription", test_create_business_subscription)
    run_test("Get User Subscription", test_get_user_subscription)
    run_test("Subscription Validation", test_subscription_validation)
    
    # Account Number and API Key Generation Tests
    run_test("Account Number and API Key Generation", test_account_number_generation)
    
    # Print summary
    print("\n" + "="*80)
    print(f"SUMMARY: {test_results['passed']} passed, {test_results['failed']} failed")
    print("="*80)
    
    for test in test_results["tests"]:
        status_symbol = "✅" if test["status"] == "PASSED" else "❌"
        error_msg = f" - Error: {test.get('error', '')}" if "error" in test else ""
        print(f"{status_symbol} {test['name']}{error_msg}")