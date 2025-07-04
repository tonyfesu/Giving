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
        "overview", "financial_metrics", "performance_metrics", 
        "growth_analytics", "category_analysis", "payment_analysis",
        "top_performers", "social_engagement", "badge_distribution", 
        "platform_health"
    ]
    
    for section in required_sections:
        assert section in metrics, f"Performance metrics missing '{section}' section"
    
    # Verify overview section
    overview = metrics["overview"]
    required_overview_fields = [
        "total_users", "total_businesses", "total_customers", "total_admins",
        "total_causes", "active_causes", "expired_causes", "featured_causes",
        "total_transactions", "total_contributions", "anonymous_contributions",
        "registered_contributions", "total_subscriptions", "active_subscriptions",
        "subscription_retention_rate"
    ]
    
    for field in required_overview_fields:
        assert field in overview, f"Overview section missing '{field}' field"
    
    # Verify financial metrics section
    financial = metrics["financial_metrics"]
    required_financial_fields = [
        "total_platform_revenue", "business_impact", "customer_contributions",
        "subscription_revenue", "transaction_volume", "avg_contribution",
        "avg_transaction", "avg_business_impact", "max_single_contribution",
        "min_single_contribution"
    ]
    
    for field in required_financial_fields:
        assert field in financial, f"Financial metrics section missing '{field}' field"
    
    # Verify performance metrics section
    performance = metrics["performance_metrics"]
    required_performance_fields = [
        "causes_per_business", "contributions_per_customer", 
        "avg_cause_performance", "platform_impact_efficiency"
    ]
    
    for field in required_performance_fields:
        assert field in performance, f"Performance metrics section missing '{field}' field"
    
    # Verify growth analytics section
    growth = metrics["growth_analytics"]
    assert "recent_activity" in growth, "Growth analytics missing 'recent_activity' field"
    assert "growth_rates" in growth, "Growth analytics missing 'growth_rates' field"
    assert "trend_indicators" in growth, "Growth analytics missing 'trend_indicators' field"
    
    # Verify category analysis
    category_analysis = metrics["category_analysis"]
    assert isinstance(category_analysis, list), "Category analysis should be a list"
    if len(category_analysis) > 0:
        category = category_analysis[0]
        required_category_fields = [
            "category", "total_causes", "active_causes", "total_raised",
            "avg_performance", "market_share"
        ]
        for field in required_category_fields:
            assert field in category, f"Category analysis item missing '{field}' field"
    
    # Verify payment analysis
    payment_analysis = metrics["payment_analysis"]
    assert isinstance(payment_analysis, list), "Payment analysis should be a list"
    if len(payment_analysis) > 0:
        payment = payment_analysis[0]
        required_payment_fields = [
            "method", "usage_count", "total_volume", "avg_amount", "market_share"
        ]
        for field in required_payment_fields:
            assert field in payment, f"Payment analysis item missing '{field}' field"
    
    # Verify top performers
    top_performers = metrics["top_performers"]
    assert "causes" in top_performers, "Top performers missing 'causes' field"
    assert "businesses" in top_performers, "Top performers missing 'businesses' field"
    assert "customers" in top_performers, "Top performers missing 'customers' field"
    
    # Verify social engagement
    social = metrics["social_engagement"]
    required_social_fields = [
        "total_shares", "total_comments", "total_reactions", "engagement_rate"
    ]
    for field in required_social_fields:
        assert field in social, f"Social engagement missing '{field}' field"
    
    # Verify badge distribution
    badges = metrics["badge_distribution"]
    assert "business_badges" in badges, "Badge distribution missing 'business_badges' field"
    assert "customer_badges" in badges, "Badge distribution missing 'customer_badges' field"
    assert "total_badges_awarded" in badges, "Badge distribution missing 'total_badges_awarded' field"
    
    # Verify platform health
    health = metrics["platform_health"]
    required_health_fields = [
        "causes_expiring_soon", "subscription_churn_rate", 
        "cause_completion_rate", "user_engagement_score"
    ]
    for field in required_health_fields:
        assert field in health, f"Platform health missing '{field}' field"
    
    # Verify data consistency
    assert overview["total_businesses"] + overview["total_customers"] + overview["total_admins"] == overview["total_users"], "User counts don't add up correctly"
    assert overview["active_causes"] + overview["expired_causes"] >= overview["total_causes"], "Cause counts don't add up correctly"
    assert overview["anonymous_contributions"] + overview["registered_contributions"] == overview["total_contributions"], "Contribution counts don't add up correctly"
    
    print("All performance metrics sections verified successfully")
    return True

# ===== ADMIN SETTLEMENTS TESTS =====

def test_admin_settlements():
    """Test GET /api/admin/settlements endpoint"""
    response = requests.get(f"{API_URL}/admin/settlements")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    settlements_data = response.json()
    
    # Verify settlements structure
    assert "settlements" in settlements_data, "Settlements response missing 'settlements' field"
    assert "summary" in settlements_data, "Settlements response missing 'summary' field"
    
    # Verify summary structure
    summary = settlements_data["summary"]
    required_summary_fields = [
        "total_causes", "total_raised", "total_pending", "total_settled"
    ]
    for field in required_summary_fields:
        assert field in summary, f"Summary missing '{field}' field"
    
    # Verify settlements list
    settlements = settlements_data["settlements"]
    assert isinstance(settlements, list), "Settlements should be a list"
    
    if len(settlements) > 0:
        settlement = settlements[0]
        required_settlement_fields = [
            "id", "cause_id", "cause_name", "cause_category", "creator_name", 
            "creator_type", "total_donations_received", "pending_amount", 
            "total_settled", "created_at"
        ]
        for field in required_settlement_fields:
            assert field in settlement, f"Settlement missing '{field}' field"
    
    # Verify data consistency
    assert summary["total_causes"] == len(settlements), "Total causes doesn't match number of settlements"
    
    total_raised = sum(s["total_donations_received"] for s in settlements)
    total_pending = sum(s["pending_amount"] for s in settlements)
    total_settled = sum(s["total_settled"] for s in settlements)
    
    assert abs(summary["total_raised"] - total_raised) < 0.01, "Total raised doesn't match sum of individual settlements"
    assert abs(summary["total_pending"] - total_pending) < 0.01, "Total pending doesn't match sum of individual settlements"
    assert abs(summary["total_settled"] - total_settled) < 0.01, "Total settled doesn't match sum of individual settlements"
    
    # Verify that for each settlement, total_donations_received = pending_amount + total_settled
    for settlement in settlements:
        expected_pending = settlement["total_donations_received"] - settlement["total_settled"]
        assert abs(settlement["pending_amount"] - expected_pending) < 0.01, f"Settlement {settlement['id']} has inconsistent amounts"
    
    print(f"Verified {len(settlements)} settlements with consistent data")
    return True

# Run the tests
if __name__ == "__main__":
    print(f"Starting admin dashboard API tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run admin performance metrics test
    run_test("Admin Performance Metrics", test_admin_performance_metrics)
    
    # Run admin settlements test
    run_test("Admin Settlements", test_admin_settlements)
    
    # Print summary
    print("\n" + "="*80)
    print(f"SUMMARY: {test_results['passed']} passed, {test_results['failed']} failed")
    print("="*80)
    
    for test in test_results["tests"]:
        status_symbol = "✅" if test["status"] == "PASSED" else "❌"
        error_msg = f" - Error: {test.get('error', '')}" if "error" in test else ""
        print(f"{status_symbol} {test['name']}: {test['status']}{error_msg}")