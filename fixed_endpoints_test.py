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

# ===== ADMIN SETTLEMENTS ENDPOINT TEST =====

def test_admin_settlements():
    """Test GET /api/admin/settlements endpoint"""
    response = requests.get(f"{API_URL}/admin/settlements")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    settlements = response.json()
    
    # Verify the response structure
    assert "settlements" in settlements, "Settlements response missing 'settlements' field"
    assert "summary" in settlements, "Settlements response missing 'summary' field"
    
    # Verify summary structure
    summary = settlements["summary"]
    assert "total_causes" in summary, "Summary missing 'total_causes' field"
    assert "total_raised" in summary, "Summary missing 'total_raised' field"
    assert "total_pending" in summary, "Summary missing 'total_pending' field"
    assert "total_settled" in summary, "Summary missing 'total_settled' field"
    
    # Verify settlements structure
    settlement_list = settlements["settlements"]
    if len(settlement_list) > 0:
        settlement = settlement_list[0]
        assert "cause_id" in settlement, "Settlement missing 'cause_id' field"
        assert "total_donations_received" in settlement, "Settlement missing 'total_donations_received' field"
        assert "pending_amount" in settlement, "Settlement missing 'pending_amount' field"
        assert "total_settled" in settlement, "Settlement missing 'total_settled' field"
        assert "cause_name" in settlement, "Settlement missing 'cause_name' field"
        assert "cause_category" in settlement, "Settlement missing 'cause_category' field"
        assert "creator_name" in settlement, "Settlement missing 'creator_name' field"
        assert "creator_type" in settlement, "Settlement missing 'creator_type' field"
    
    print(f"Found {len(settlement_list)} settlements")
    return True

# ===== CREATE CAUSE ENDPOINT TEST =====

def test_create_cause():
    """Test POST /api/users/{user_id}/causes endpoint"""
    # First get a business user to create a cause
    response = requests.get(f"{API_URL}/businesses")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    businesses = response.json()
    assert len(businesses) > 0, "Need at least one business for cause creation test"
    
    business_id = businesses[0]["id"]
    
    # Create cause data
    cause_data = {
        "name": "Test USSD Shortcode Cause",
        "description": "Testing the USSD shortcode generation",
        "category": "Education",
        "impact_metric": "students educated",
        "cost_per_impact": 10.0,
        "goal_amount": 5000.0,
        "end_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "payment_methods_accepted": ["card", "momo", "bank_transfer"],
        "volunteer_opportunities": ["teaching", "mentoring"],
        "settlement_info": {
            "account_number": "1234567890",
            "phone_number": "+1234567890",
            "bank_name": "Test Bank",
            "bank_code": "TEST001",
            "account_type": "savings",
            "verified": False
        }
    }
    
    # Test with business creator
    response = requests.post(
        f"{API_URL}/users/{business_id}/causes?user_type=business", 
        json=cause_data
    )
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    business_cause = response.json()
    assert "id" in business_cause, "Cause response missing 'id' field"
    assert "cause_code" in business_cause, "Cause response missing 'cause_code' field"
    assert "ussd_shortcode" in business_cause, "Cause response missing 'ussd_shortcode' field"
    
    # Verify USSD shortcode format
    ussd_shortcode = business_cause["ussd_shortcode"]
    assert ussd_shortcode.startswith("*123*86*"), f"USSD shortcode should start with '*123*86*', got {ussd_shortcode}"
    assert "*[Amount]#" in ussd_shortcode, f"USSD shortcode should contain '*[Amount]#', got {ussd_shortcode}"
    
    # Now test with a customer creator
    response = requests.get(f"{API_URL}/customers")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    customers = response.json()
    assert len(customers) > 0, "Need at least one customer for cause creation test"
    
    customer_id = customers[0]["id"]
    
    # Test with customer creator
    response = requests.post(
        f"{API_URL}/users/{customer_id}/causes?user_type=customer", 
        json=cause_data
    )
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    customer_cause = response.json()
    assert "id" in customer_cause, "Cause response missing 'id' field"
    assert "cause_code" in customer_cause, "Cause response missing 'cause_code' field"
    assert "ussd_shortcode" in customer_cause, "Cause response missing 'ussd_shortcode' field"
    
    # Verify USSD shortcode format
    ussd_shortcode = customer_cause["ussd_shortcode"]
    assert ussd_shortcode.startswith("*123*86*"), f"USSD shortcode should start with '*123*86*', got {ussd_shortcode}"
    assert "*[Amount]#" in ussd_shortcode, f"USSD shortcode should contain '*[Amount]#', got {ussd_shortcode}"
    
    print(f"Created business cause with ID: {business_cause['id']} and USSD shortcode: {business_cause['ussd_shortcode']}")
    print(f"Created customer cause with ID: {customer_cause['id']} and USSD shortcode: {customer_cause['ussd_shortcode']}")
    
    return True

# ===== ADMIN PERFORMANCE METRICS ENDPOINT TEST =====

def test_admin_performance_metrics():
    """Test GET /api/admin/performance-metrics endpoint"""
    response = requests.get(f"{API_URL}/admin/performance-metrics")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    metrics = response.json()
    
    # Verify the response structure
    assert "overview" in metrics, "Performance metrics missing 'overview' field"
    assert "financial_metrics" in metrics, "Performance metrics missing 'financial_metrics' field"
    assert "performance_metrics" in metrics, "Performance metrics missing 'performance_metrics' field"
    assert "growth_analytics" in metrics, "Performance metrics missing 'growth_analytics' field"
    assert "category_analysis" in metrics, "Performance metrics missing 'category_analysis' field"
    assert "payment_analysis" in metrics, "Performance metrics missing 'payment_analysis' field"
    assert "top_performers" in metrics, "Performance metrics missing 'top_performers' field"
    assert "social_engagement" in metrics, "Performance metrics missing 'social_engagement' field"
    assert "badge_distribution" in metrics, "Performance metrics missing 'badge_distribution' field"
    assert "platform_health" in metrics, "Performance metrics missing 'platform_health' field"
    
    # Verify overview structure
    overview = metrics["overview"]
    assert "total_users" in overview, "Overview missing 'total_users' field"
    assert "total_businesses" in overview, "Overview missing 'total_businesses' field"
    assert "total_customers" in overview, "Overview missing 'total_customers' field"
    assert "total_causes" in overview, "Overview missing 'total_causes' field"
    
    # Verify financial metrics structure
    financial = metrics["financial_metrics"]
    assert "total_platform_revenue" in financial, "Financial metrics missing 'total_platform_revenue' field"
    assert "business_impact" in financial, "Financial metrics missing 'business_impact' field"
    assert "customer_contributions" in financial, "Financial metrics missing 'customer_contributions' field"
    
    # Verify top performers structure
    top_performers = metrics["top_performers"]
    assert "causes" in top_performers, "Top performers missing 'causes' field"
    assert "businesses" in top_performers, "Top performers missing 'businesses' field"
    assert "customers" in top_performers, "Top performers missing 'customers' field"
    
    print("Performance metrics endpoint returned comprehensive data")
    return True

# Run the tests
if __name__ == "__main__":
    print(f"Starting backend API tests at {datetime.now().isoformat()}")
    
    # Run the tests
    run_test("Admin Settlements Endpoint", test_admin_settlements)
    run_test("Create Cause Endpoint", test_create_cause)
    run_test("Admin Performance Metrics Endpoint", test_admin_performance_metrics)
    
    # Print summary
    print("\n" + "="*80)
    print(f"TEST SUMMARY: {test_results['passed']} passed, {test_results['failed']} failed")
    print("="*80)
    
    for test in test_results["tests"]:
        status_symbol = "✅" if test["status"] == "PASSED" else "❌"
        error_info = f" - Error: {test.get('error', '')}" if "error" in test else ""
        print(f"{status_symbol} {test['name']}: {test['status']}{error_info}")