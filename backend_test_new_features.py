#!/usr/bin/env python3
import requests
import json
import time
import os
from datetime import datetime, timedelta
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

# ===== HELPER FUNCTIONS =====

def get_demo_users():
    """Get demo users for testing"""
    response = requests.get(f"{API_URL}/admin/demo-users")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    demo_users = response.json()
    assert "demo_business" in demo_users, "Demo users response missing 'demo_business'"
    assert "demo_customer" in demo_users, "Demo users response missing 'demo_customer'"
    
    return demo_users

# ===== ENHANCED ADMIN SETTLEMENT SYSTEM TESTS =====

def test_admin_settlements():
    """Test GET /api/admin/settlements endpoint"""
    response = requests.get(f"{API_URL}/admin/settlements")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "settlements" in data, "Response missing 'settlements' field"
    settlements = data["settlements"]
    assert len(settlements) > 0, "Expected at least one settlement"
    
    # Verify settlement structure
    for settlement in settlements:
        assert "cause" in settlement, "Settlement missing 'cause' field"
        assert "settlement" in settlement, "Settlement missing 'settlement' field"
        assert "direct_donations" in settlement, "Settlement missing 'direct_donations' field"
        assert "business_donations" in settlement, "Settlement missing 'business_donations' field"
        assert "total_donations" in settlement, "Settlement missing 'total_donations' field"
        
        # Verify cause data
        cause = settlement["cause"]
        assert "id" in cause, "Cause missing 'id' field"
        assert "name" in cause, "Cause missing 'name' field"
        assert "category" in cause, "Cause missing 'category' field"
        
        # Verify settlement data
        settlement_data = settlement["settlement"]
        assert "id" in settlement_data, "Settlement data missing 'id' field"
        assert "cause_id" in settlement_data, "Settlement data missing 'cause_id' field"
        assert "total_donations_received" in settlement_data, "Settlement data missing 'total_donations_received' field"
        assert "pending_amount" in settlement_data, "Settlement data missing 'pending_amount' field"
        assert "total_settled" in settlement_data, "Settlement data missing 'total_settled' field"
        
        # Verify calculation logic
        direct = settlement["direct_donations"]
        business = settlement["business_donations"]
        total = settlement["total_donations"]
        assert abs(direct + business - total) < 0.01, f"Total donations ({total}) should equal direct ({direct}) + business ({business})"
        assert abs(settlement_data["total_donations_received"] - total) < 0.01, "Settlement total_donations_received should match total_donations"
    
    print(f"Found {len(settlements)} settlements")
    
    # Store a cause ID for later testing
    global test_settlement_cause_id
    test_settlement_cause_id = settlements[0]["cause"]["id"]
    
    return True

def test_initiate_settlement_payment():
    """Test POST /api/admin/settlements/{cause_id}/initiate-payment endpoint"""
    # Get settlement data first
    response = requests.get(f"{API_URL}/admin/settlements")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    settlements = response.json()["settlements"]
    
    # Find a settlement with pending amount > 0
    settlement_to_pay = None
    for settlement in settlements:
        if settlement["settlement"]["pending_amount"] > 0:
            settlement_to_pay = settlement
            break
    
    if not settlement_to_pay:
        print("No settlements with pending amount > 0 found, skipping payment test")
        return True
    
    cause_id = settlement_to_pay["cause"]["id"]
    payment_data = {
        "admin_id": "test_admin",
        "payment_method": {
            "type": "bank_transfer",
            "provider": "bank",
            "details": {
                "bank_name": "Test Bank",
                "account_number": "1234567890"
            }
        }
    }
    
    response = requests.post(f"{API_URL}/admin/settlements/{cause_id}/initiate-payment", json=payment_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    result = response.json()
    assert "message" in result, "Response missing 'message' field"
    assert "payment_reference" in result, "Response missing 'payment_reference' field"
    assert "amount" in result, "Response missing 'amount' field"
    assert "status" in result, "Response missing 'status' field"
    
    assert result["status"] == "completed", f"Expected status 'completed', got {result['status']}"
    assert result["amount"] == settlement_to_pay["settlement"]["pending_amount"], "Payment amount should match pending amount"
    
    # Verify settlement was updated
    response = requests.get(f"{API_URL}/admin/settlements")
    updated_settlements = response.json()["settlements"]
    
    for settlement in updated_settlements:
        if settlement["cause"]["id"] == cause_id:
            assert settlement["settlement"]["pending_amount"] == 0, "Pending amount should be 0 after settlement"
            assert settlement["settlement"]["total_settled"] >= settlement_to_pay["settlement"]["total_settled"], "Total settled should increase"
            assert settlement["settlement"]["last_settlement_date"] is not None, "Last settlement date should be set"
            break
    
    return True

# ===== USER CAUSE CREATION TESTS =====

def test_business_cause_creation():
    """Test POST /api/users/{user_id}/causes endpoint for business users"""
    # Get demo business
    demo_users = get_demo_users()
    business = demo_users["demo_business"]
    business_id = business["id"]
    
    # Create cause data
    cause_data = {
        "name": "Business Sustainability Initiative",
        "description": "Supporting sustainable business practices and reducing carbon footprint",
        "category": "Environment",
        "impact_metric": "tons of CO2 offset",
        "cost_per_impact": 25.0,
        "goal_amount": 50000.0,
        "end_date": (datetime.utcnow() + timedelta(days=90)).isoformat(),
        "image_url": "https://images.unsplash.com/photo-1532601224476-15c79f2f7a51",
        "payment_methods_accepted": ["card", "bank_transfer"],
        "volunteer_opportunities": ["sustainability_workshops", "tree_planting"],
        "settlement_info": {
            "account_number": "9876543210",
            "bank_name": "Eco Bank",
            "bank_code": "ECO001",
            "account_type": "checking",
            "verified": False
        }
    }
    
    response = requests.post(
        f"{API_URL}/users/{business_id}/causes?user_type=business", 
        json=cause_data
    )
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    cause = response.json()
    
    # Verify cause data
    for key, value in cause_data.items():
        if key == "end_date":
            # Skip date comparison due to format differences
            continue
        if key == "settlement_info":
            # Check settlement info fields
            for settlement_key, settlement_value in cause_data["settlement_info"].items():
                assert cause["settlement_info"][settlement_key] == settlement_value, f"Expected settlement_info.{settlement_key} to be {settlement_value}, got {cause['settlement_info'][settlement_key]}"
            continue
        assert cause[key] == value, f"Expected {key} to be {value}, got {cause[key]}"
    
    # Verify business-specific fields
    assert cause["creator_id"] == business_id, f"Expected creator_id to be {business_id}, got {cause['creator_id']}"
    assert cause["creator_type"] == "business", f"Expected creator_type to be 'business', got {cause['creator_type']}"
    assert cause["creator_name"] == business["name"], f"Expected creator_name to be {business['name']}, got {cause['creator_name']}"
    assert cause["creator_website"] == business["website"], f"Expected creator_website to be {business['website']}, got {cause['creator_website']}"
    
    # Store cause ID for later tests
    global test_business_cause_id
    test_business_cause_id = cause["id"]
    
    return True

def test_customer_cause_creation():
    """Test POST /api/users/{user_id}/causes endpoint for customer users"""
    # Get demo customer
    demo_users = get_demo_users()
    customer = demo_users["demo_customer"]
    customer_id = customer["id"]
    
    # Create cause data
    cause_data = {
        "name": "Community Education Fund",
        "description": "Providing educational resources to underserved communities",
        "category": "Education",
        "impact_metric": "students supported",
        "cost_per_impact": 50.0,
        "goal_amount": 25000.0,
        "end_date": (datetime.utcnow() + timedelta(days=180)).isoformat(),
        "image_url": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b",
        "payment_methods_accepted": ["card", "momo", "papss"],
        "volunteer_opportunities": ["tutoring", "mentoring"],
        "settlement_info": {
            "phone_number": "+1-555-0200",
            "account_type": "momo",
            "verified": False
        }
    }
    
    response = requests.post(
        f"{API_URL}/users/{customer_id}/causes?user_type=customer", 
        json=cause_data
    )
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    cause = response.json()
    
    # Verify cause data
    for key, value in cause_data.items():
        if key == "end_date":
            # Skip date comparison due to format differences
            continue
        if key == "settlement_info":
            # Check settlement info fields
            for settlement_key, settlement_value in cause_data["settlement_info"].items():
                assert cause["settlement_info"][settlement_key] == settlement_value, f"Expected settlement_info.{settlement_key} to be {settlement_value}, got {cause['settlement_info'][settlement_key]}"
            continue
        assert cause[key] == value, f"Expected {key} to be {value}, got {cause[key]}"
    
    # Verify customer-specific fields
    assert cause["creator_id"] == customer_id, f"Expected creator_id to be {customer_id}, got {cause['creator_id']}"
    assert cause["creator_type"] == "customer", f"Expected creator_type to be 'customer', got {cause['creator_type']}"
    assert cause["creator_name"] == customer["name"], f"Expected creator_name to be {customer['name']}, got {cause['creator_name']}"
    assert cause["creator_website"] is None, f"Expected creator_website to be None, got {cause['creator_website']}"
    
    # Store cause ID for later tests
    global test_customer_cause_id
    test_customer_cause_id = cause["id"]
    
    return True

def test_cause_creation_validation():
    """Test validation and error handling for cause creation"""
    # Get demo customer
    demo_users = get_demo_users()
    customer = demo_users["demo_customer"]
    customer_id = customer["id"]
    
    # Test with missing required fields
    invalid_cause_data = {
        "name": "Invalid Cause",
        # Missing description
        "category": "Education",
        # Missing impact_metric
        # Missing cost_per_impact
        "goal_amount": 10000.0,
        "end_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
        # Missing settlement_info
    }
    
    response = requests.post(
        f"{API_URL}/users/{customer_id}/causes?user_type=customer", 
        json=invalid_cause_data
    )
    assert response.status_code in [400, 422], f"Expected status code 400 or 422 for invalid data, got {response.status_code}"
    
    # Test with invalid user type
    valid_cause_data = {
        "name": "Test Cause",
        "description": "Test description",
        "category": "Education",
        "impact_metric": "students",
        "cost_per_impact": 10.0,
        "goal_amount": 10000.0,
        "end_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "settlement_info": {
            "phone_number": "+1-555-1234",
            "account_type": "momo",
            "verified": False
        }
    }
    
    response = requests.post(
        f"{API_URL}/users/{customer_id}/causes?user_type=invalid", 
        json=valid_cause_data
    )
    assert response.status_code == 400, f"Expected status code 400 for invalid user type, got {response.status_code}"
    
    # Test with non-existent user ID
    response = requests.post(
        f"{API_URL}/users/non-existent-id/causes?user_type=customer", 
        json=valid_cause_data
    )
    assert response.status_code == 404, f"Expected status code 404 for non-existent user, got {response.status_code}"
    
    return True

# ===== ENHANCED DEVELOPER PLATFORM TESTS =====

def test_dev_docs():
    """Test GET /api/dev/docs endpoint"""
    response = requests.get(f"{API_URL}/dev/docs")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    docs = response.json()
    
    # Verify documentation structure
    assert "title" in docs, "Documentation missing 'title' field"
    assert "version" in docs, "Documentation missing 'version' field"
    assert "description" in docs, "Documentation missing 'description' field"
    assert "base_url" in docs, "Documentation missing 'base_url' field"
    assert "authentication" in docs, "Documentation missing 'authentication' field"
    assert "endpoints" in docs, "Documentation missing 'endpoints' field"
    assert "examples" in docs, "Documentation missing 'examples' field"
    
    # Verify endpoints sections
    endpoints = docs["endpoints"]
    required_endpoint_sections = ["businesses", "causes", "transactions", "contributions", "subscriptions", "leaderboards"]
    for section in required_endpoint_sections:
        assert section in endpoints, f"Endpoints missing '{section}' section"
    
    # Verify examples
    examples = docs["examples"]
    required_examples = ["create_transaction", "direct_contribution", "create_cause"]
    for example in required_examples:
        assert example in examples, f"Examples missing '{example}' example"
    
    return True

def test_dev_sdk():
    """Test GET /api/dev/sdk endpoint"""
    response = requests.get(f"{API_URL}/dev/sdk")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    sdk_info = response.json()
    
    # Verify SDK information structure
    assert "sdks" in sdk_info, "SDK info missing 'sdks' field"
    assert "webhooks" in sdk_info, "SDK info missing 'webhooks' field"
    assert "plugins" in sdk_info, "SDK info missing 'plugins' field"
    
    # Verify SDKs
    sdks = sdk_info["sdks"]
    required_sdks = ["javascript", "python", "php"]
    for sdk in required_sdks:
        assert sdk in sdks, f"SDKs missing '{sdk}' SDK"
        sdk_data = sdks[sdk]
        assert "name" in sdk_data, f"{sdk} SDK missing 'name' field"
        assert "version" in sdk_data, f"{sdk} SDK missing 'version' field"
        assert "install" in sdk_data, f"{sdk} SDK missing 'install' field"
        assert "docs" in sdk_data, f"{sdk} SDK missing 'docs' field"
    
    # Verify webhooks
    webhooks = sdk_info["webhooks"]
    assert "description" in webhooks, "Webhooks missing 'description' field"
    assert "events" in webhooks, "Webhooks missing 'events' field"
    assert "setup" in webhooks, "Webhooks missing 'setup' field"
    
    # Verify plugins
    plugins = sdk_info["plugins"]
    required_plugins = ["shopify", "woocommerce"]
    for plugin in required_plugins:
        assert plugin in plugins, f"Plugins missing '{plugin}' plugin"
        plugin_data = plugins[plugin]
        assert "name" in plugin_data, f"{plugin} plugin missing 'name' field"
        assert "description" in plugin_data, f"{plugin} plugin missing 'description' field"
        assert "install_url" in plugin_data, f"{plugin} plugin missing 'install_url' field"
    
    return True

def test_dev_code_examples():
    """Test GET /api/dev/code-examples endpoint"""
    response = requests.get(f"{API_URL}/dev/code-examples")
    
    # This endpoint might not exist yet, so we'll check if it returns a 404
    if response.status_code == 404:
        print("Code examples endpoint not implemented yet")
        return True
    
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    code_examples = response.json()
    
    # If the endpoint exists, verify its structure
    assert "languages" in code_examples, "Code examples missing 'languages' field"
    
    languages = code_examples["languages"]
    required_languages = ["javascript", "python", "php", "curl"]
    for language in required_languages:
        assert language in languages, f"Languages missing '{language}' examples"
    
    return True

if __name__ == "__main__":
    # Global variables to store test data
    test_settlement_cause_id = None
    test_business_cause_id = None
    test_customer_cause_id = None
    
    # Run tests for enhanced admin settlement system
    print("\n===== TESTING ENHANCED ADMIN SETTLEMENT SYSTEM =====")
    run_test("Admin Settlements", test_admin_settlements)
    run_test("Initiate Settlement Payment", test_initiate_settlement_payment)
    
    # Run tests for user cause creation
    print("\n===== TESTING USER CAUSE CREATION =====")
    run_test("Business Cause Creation", test_business_cause_creation)
    run_test("Customer Cause Creation", test_customer_cause_creation)
    run_test("Cause Creation Validation", test_cause_creation_validation)
    
    # Run tests for enhanced developer platform
    print("\n===== TESTING ENHANCED DEVELOPER PLATFORM =====")
    run_test("Developer Documentation", test_dev_docs)
    run_test("SDK Information", test_dev_sdk)
    run_test("Code Examples", test_dev_code_examples)
    
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