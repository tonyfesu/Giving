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

# ===== ADMIN PERFORMANCE METRICS TESTS =====

def test_admin_performance_metrics():
    """Test GET /api/admin/performance-metrics endpoint"""
    response = requests.get(f"{API_URL}/admin/performance-metrics")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    metrics = response.json()
    
    # Verify all required sections are present
    required_sections = [
        "overview", 
        "financial_metrics", 
        "performance_metrics", 
        "growth_analytics", 
        "category_analysis", 
        "payment_analysis", 
        "top_performers", 
        "social_engagement", 
        "badge_distribution", 
        "platform_health"
    ]
    
    for section in required_sections:
        assert section in metrics, f"Missing required section '{section}' in performance metrics"
    
    # Verify overview section
    overview = metrics["overview"]
    overview_fields = [
        "total_users", "total_businesses", "total_customers", "total_admins",
        "total_causes", "active_causes", "expired_causes", "featured_causes",
        "total_transactions", "total_contributions", "anonymous_contributions",
        "registered_contributions", "total_subscriptions", "active_subscriptions"
    ]
    
    for field in overview_fields:
        assert field in overview, f"Missing field '{field}' in overview section"
        assert isinstance(overview[field], (int, float)), f"Field '{field}' should be a number"
    
    # Verify financial metrics
    financial = metrics["financial_metrics"]
    financial_fields = [
        "total_platform_revenue", "business_impact", "customer_contributions",
        "subscription_revenue", "transaction_volume", "avg_contribution",
        "avg_transaction", "avg_business_impact"
    ]
    
    for field in financial_fields:
        assert field in financial, f"Missing field '{field}' in financial_metrics section"
        assert isinstance(financial[field], (int, float)), f"Field '{field}' should be a number"
    
    # Verify performance metrics
    performance = metrics["performance_metrics"]
    performance_fields = [
        "causes_per_business", "contributions_per_customer", 
        "avg_cause_performance", "platform_impact_efficiency"
    ]
    
    for field in performance_fields:
        assert field in performance, f"Missing field '{field}' in performance_metrics section"
        assert isinstance(performance[field], (int, float)), f"Field '{field}' should be a number"
    
    # Verify growth analytics
    growth = metrics["growth_analytics"]
    assert "recent_activity" in growth, "Missing 'recent_activity' in growth_analytics section"
    assert "growth_rates" in growth, "Missing 'growth_rates' in growth_analytics section"
    assert "trend_indicators" in growth, "Missing 'trend_indicators' in growth_analytics section"
    
    # Verify category analysis
    categories = metrics["category_analysis"]
    assert isinstance(categories, list), "category_analysis should be a list"
    if len(categories) > 0:
        category_fields = [
            "category", "total_causes", "active_causes", "total_raised", 
            "avg_performance", "market_share"
        ]
        for field in category_fields:
            assert field in categories[0], f"Missing field '{field}' in category_analysis items"
    
    # Verify payment analysis
    payments = metrics["payment_analysis"]
    assert isinstance(payments, list), "payment_analysis should be a list"
    if len(payments) > 0:
        payment_fields = [
            "method", "usage_count", "total_volume", "avg_amount", "market_share"
        ]
        for field in payment_fields:
            assert field in payments[0], f"Missing field '{field}' in payment_analysis items"
    
    # Verify top performers
    top = metrics["top_performers"]
    assert "causes" in top, "Missing 'causes' in top_performers section"
    assert "businesses" in top, "Missing 'businesses' in top_performers section"
    assert "customers" in top, "Missing 'customers' in top_performers section"
    
    # Verify social engagement
    social = metrics["social_engagement"]
    social_fields = [
        "total_shares", "total_comments", "total_reactions", "engagement_rate"
    ]
    for field in social_fields:
        assert field in social, f"Missing field '{field}' in social_engagement section"
    
    # Verify badge distribution
    badges = metrics["badge_distribution"]
    assert "business_badges" in badges, "Missing 'business_badges' in badge_distribution section"
    assert "customer_badges" in badges, "Missing 'customer_badges' in badge_distribution section"
    assert "total_badges_awarded" in badges, "Missing 'total_badges_awarded' in badge_distribution section"
    
    # Verify platform health
    health = metrics["platform_health"]
    health_fields = [
        "causes_expiring_soon", "subscription_churn_rate", 
        "cause_completion_rate", "user_engagement_score"
    ]
    for field in health_fields:
        assert field in health, f"Missing field '{field}' in platform_health section"
    
    print("All required sections and fields are present in performance metrics")
    return True

# ===== ENHANCED ADMIN SETTLEMENTS TESTS =====

def test_admin_settlements():
    """Test GET /api/admin/settlements endpoint"""
    response = requests.get(f"{API_URL}/admin/settlements")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    settlements_data = response.json()
    
    # Check if the response has the expected structure
    assert "settlements" in settlements_data, "Missing 'settlements' in response"
    
    settlements = settlements_data["settlements"]
    assert isinstance(settlements, list), "settlements should be a list"
    
    if len(settlements) > 0:
        # Check the first settlement for required fields
        settlement = settlements[0]
        assert "cause" in settlement, "Missing 'cause' in settlement"
        assert "settlement" in settlement, "Missing 'settlement' in settlement"
        assert "direct_donations" in settlement, "Missing 'direct_donations' in settlement"
        assert "business_donations" in settlement, "Missing 'business_donations' in settlement"
        assert "total_donations" in settlement, "Missing 'total_donations' in settlement"
        
        # Check cause fields
        cause = settlement["cause"]
        cause_fields = ["id", "name", "description", "category", "impact_metric", "cost_per_impact"]
        for field in cause_fields:
            assert field in cause, f"Missing field '{field}' in cause"
        
        # Check settlement fields
        settlement_obj = settlement["settlement"]
        settlement_fields = [
            "id", "cause_id", "total_donations_received", "pending_amount", 
            "total_settled", "created_at"
        ]
        for field in settlement_fields:
            assert field in settlement_obj, f"Missing field '{field}' in settlement object"
        
        # Verify calculations
        assert settlement["total_donations"] == settlement["direct_donations"] + settlement["business_donations"], \
            "total_donations should equal direct_donations + business_donations"
        
        assert settlement_obj["total_donations_received"] == settlement["total_donations"], \
            "settlement.total_donations_received should equal total_donations"
    
    print(f"Found {len(settlements)} settlements with correct structure")
    return True

# ===== CREATE CAUSE ENDPOINT TESTS =====

def test_create_cause_as_business():
    """Test POST /api/users/{user_id}/causes endpoint as business"""
    # First get a business to use as creator
    response = requests.get(f"{API_URL}/businesses")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    businesses = response.json()
    assert len(businesses) > 0, "Need at least one business for cause creation test"
    
    business = businesses[0]
    business_id = business["id"]
    
    # Create cause data
    cause_data = {
        "name": "Business Sustainability Initiative",
        "description": "Supporting sustainable business practices in local communities",
        "category": "Environment",
        "impact_metric": "businesses adopting sustainable practices",
        "cost_per_impact": 500.0,
        "goal_amount": 50000.0,
        "end_date": (datetime.utcnow() + timedelta(days=90)).isoformat(),
        "payment_methods_accepted": ["card", "momo", "bank_transfer"],
        "volunteer_opportunities": ["mentoring", "workshops"],
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
    
    # Verify cause fields
    for key in ["name", "description", "category", "impact_metric", "cost_per_impact"]:
        assert cause[key] == cause_data[key], f"Expected {key} to be {cause_data[key]}, got {cause[key]}"
    
    # Verify creator information
    assert cause["creator_id"] == business_id, f"Expected creator_id {business_id}, got {cause['creator_id']}"
    assert cause["creator_type"] == "business", f"Expected creator_type 'business', got {cause['creator_type']}"
    assert cause["creator_name"] == business["name"], f"Expected creator_name {business['name']}, got {cause['creator_name']}"
    
    # Verify USSD shortcode generation
    assert "cause_code" in cause, "Missing 'cause_code' in cause"
    assert "ussd_shortcode" in cause, "Missing 'ussd_shortcode' in cause"
    assert cause["ussd_shortcode"].startswith("*123*86*"), "USSD shortcode should start with *123*86*"
    
    # Verify settlement info
    assert "settlement_info" in cause, "Missing 'settlement_info' in cause"
    settlement = cause["settlement_info"]
    assert settlement["account_number"] == cause_data["settlement_info"]["account_number"], \
        f"Expected account_number {cause_data['settlement_info']['account_number']}, got {settlement['account_number']}"
    
    print(f"Successfully created cause as business: {cause['name']} (ID: {cause['id']})")
    return True

def test_create_cause_as_customer():
    """Test POST /api/users/{user_id}/causes endpoint as customer"""
    # First get a customer to use as creator
    response = requests.get(f"{API_URL}/customers")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    customers = response.json()
    assert len(customers) > 0, "Need at least one customer for cause creation test"
    
    customer = customers[0]
    customer_id = customer["id"]
    
    # Create cause data
    cause_data = {
        "name": "Community Garden Project",
        "description": "Creating urban gardens in underserved neighborhoods",
        "category": "Environment",
        "impact_metric": "gardens established",
        "cost_per_impact": 1000.0,
        "goal_amount": 10000.0,
        "end_date": (datetime.utcnow() + timedelta(days=120)).isoformat(),
        "payment_methods_accepted": ["card", "momo"],
        "volunteer_opportunities": ["gardening", "education"],
        "settlement_info": {
            "phone_number": "+1234567890",
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
    
    # Verify cause fields
    for key in ["name", "description", "category", "impact_metric", "cost_per_impact"]:
        assert cause[key] == cause_data[key], f"Expected {key} to be {cause_data[key]}, got {cause[key]}"
    
    # Verify creator information
    assert cause["creator_id"] == customer_id, f"Expected creator_id {customer_id}, got {cause['creator_id']}"
    assert cause["creator_type"] == "customer", f"Expected creator_type 'customer', got {cause['creator_type']}"
    assert cause["creator_name"] == customer["name"], f"Expected creator_name {customer['name']}, got {cause['creator_name']}"
    
    # Verify USSD shortcode generation
    assert "cause_code" in cause, "Missing 'cause_code' in cause"
    assert "ussd_shortcode" in cause, "Missing 'ussd_shortcode' in cause"
    assert cause["ussd_shortcode"].startswith("*123*86*"), "USSD shortcode should start with *123*86*"
    
    # Verify settlement info
    assert "settlement_info" in cause, "Missing 'settlement_info' in cause"
    settlement = cause["settlement_info"]
    assert settlement["phone_number"] == cause_data["settlement_info"]["phone_number"], \
        f"Expected phone_number {cause_data['settlement_info']['phone_number']}, got {settlement['phone_number']}"
    
    print(f"Successfully created cause as customer: {cause['name']} (ID: {cause['id']})")
    return True

# ===== PAYMENT PROCESSING TESTS =====

def test_payment_processing_card():
    """Test POST /api/payments/process endpoint with card payment"""
    payment_data = {
        "amount": 100.0,
        "currency": "USD",
        "method": {
            "type": "card",
            "provider": "visa",
            "card_number": "4111 1111 1111 1111",
            "expiry": "12/25",
            "cvv": "123"
        },
        "description": "Test card payment",
        "user_id": "test_user",
        "user_type": "customer"
    }
    
    response = requests.post(f"{API_URL}/payments/process", json=payment_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    result = response.json()
    assert result["status"] == "completed", f"Expected status 'completed', got {result['status']}"
    assert result["amount"] == 100.0, f"Expected amount 100.0, got {result['amount']}"
    assert "transaction_id" in result, "Missing 'transaction_id' in result"
    
    print(f"Successfully processed card payment: {result['transaction_id']}")
    return True

def test_payment_processing_momo():
    """Test POST /api/payments/process endpoint with mobile money payment"""
    payment_data = {
        "amount": 50.0,
        "currency": "USD",
        "method": {
            "type": "momo",
            "provider": "mtn_momo",
            "phone_number": "+233123456789"
        },
        "description": "Test mobile money payment",
        "user_id": "test_user",
        "user_type": "customer"
    }
    
    response = requests.post(f"{API_URL}/payments/process", json=payment_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    result = response.json()
    assert result["status"] == "completed", f"Expected status 'completed', got {result['status']}"
    assert result["amount"] == 50.0, f"Expected amount 50.0, got {result['amount']}"
    assert "transaction_id" in result, "Missing 'transaction_id' in result"
    
    print(f"Successfully processed mobile money payment: {result['transaction_id']}")
    return True

def test_payment_processing_bank_transfer():
    """Test POST /api/payments/process endpoint with bank transfer payment"""
    payment_data = {
        "amount": 200.0,
        "currency": "USD",
        "method": {
            "type": "bank_transfer",
            "provider": "bank",
            "account_number": "1234567890",
            "bank_name": "Test Bank"
        },
        "description": "Test bank transfer payment",
        "user_id": "test_user",
        "user_type": "business"
    }
    
    response = requests.post(f"{API_URL}/payments/process", json=payment_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    result = response.json()
    assert result["status"] == "completed", f"Expected status 'completed', got {result['status']}"
    assert result["amount"] == 200.0, f"Expected amount 200.0, got {result['amount']}"
    assert "transaction_id" in result, "Missing 'transaction_id' in result"
    
    print(f"Successfully processed bank transfer payment: {result['transaction_id']}")
    return True

def test_payment_processing_papss():
    """Test POST /api/payments/process endpoint with PAPSS payment"""
    payment_data = {
        "amount": 150.0,
        "currency": "USD",
        "method": {
            "type": "papss",
            "provider": "papss",
            "papss_reference": "PAPSS12345"
        },
        "description": "Test PAPSS payment",
        "user_id": "test_user",
        "user_type": "business"
    }
    
    response = requests.post(f"{API_URL}/payments/process", json=payment_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    result = response.json()
    assert result["status"] == "completed", f"Expected status 'completed', got {result['status']}"
    assert result["amount"] == 150.0, f"Expected amount 150.0, got {result['amount']}"
    assert "transaction_id" in result, "Missing 'transaction_id' in result"
    
    print(f"Successfully processed PAPSS payment: {result['transaction_id']}")
    return True

def test_payment_processing_subscription():
    """Test POST /api/payments/process endpoint for subscription payment"""
    # First get a customer to use for subscription
    response = requests.get(f"{API_URL}/customers")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    customers = response.json()
    assert len(customers) > 0, "Need at least one customer for subscription payment test"
    
    customer = customers[0]
    customer_id = customer["id"]
    
    # Create subscription payment
    payment_data = {
        "amount": 9.99,
        "currency": "USD",
        "method": {
            "type": "card",
            "provider": "visa",
            "card_number": "4111 1111 1111 1111",
            "expiry": "12/25",
            "cvv": "123"
        },
        "description": "Monthly subscription payment",
        "user_id": customer_id,
        "user_type": "customer",
        "is_subscription": True,
        "subscription_id": "sub_" + str(int(time.time()))
    }
    
    response = requests.post(f"{API_URL}/payments/process", json=payment_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    result = response.json()
    assert result["status"] == "completed", f"Expected status 'completed', got {result['status']}"
    assert result["amount"] == 9.99, f"Expected amount 9.99, got {result['amount']}"
    assert "transaction_id" in result, "Missing 'transaction_id' in result"
    
    print(f"Successfully processed subscription payment: {result['transaction_id']}")
    return True

# ===== RUN TESTS =====

if __name__ == "__main__":
    # Admin Performance Metrics Tests
    run_test("Admin Performance Metrics", test_admin_performance_metrics)
    
    # Enhanced Admin Settlements Tests
    run_test("Admin Settlements", test_admin_settlements)
    
    # Create Cause Tests
    run_test("Create Cause as Business", test_create_cause_as_business)
    run_test("Create Cause as Customer", test_create_cause_as_customer)
    
    # Payment Processing Tests
    run_test("Payment Processing - Card", test_payment_processing_card)
    run_test("Payment Processing - Mobile Money", test_payment_processing_momo)
    run_test("Payment Processing - Bank Transfer", test_payment_processing_bank_transfer)
    run_test("Payment Processing - PAPSS", test_payment_processing_papss)
    run_test("Payment Processing - Subscription", test_payment_processing_subscription)
    
    # Print summary
    print("\n" + "="*80)
    print(f"SUMMARY: {test_results['passed']} passed, {test_results['failed']} failed")
    print("="*80)
    
    for test in test_results["tests"]:
        status_symbol = "✅" if test["status"] == "PASSED" else "❌"
        print(f"{status_symbol} {test['name']}")
        if test["status"] == "FAILED" and "error" in test:
            print(f"   Error: {test['error']}")
    
    print("="*80)