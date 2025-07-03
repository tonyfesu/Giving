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

# ===== DEVELOPER PLATFORM API TESTS =====

def test_dev_code_examples():
    """Test GET /api/dev/code-examples endpoint"""
    response = requests.get(f"{API_URL}/dev/code-examples")
    
    # Check if the endpoint exists
    if response.status_code == 404:
        print("Code examples endpoint not implemented yet")
        return False
    
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    code_examples = response.json()
    
    # Verify code examples structure
    assert "javascript" in code_examples, "Code examples missing 'javascript' section"
    assert "python" in code_examples, "Code examples missing 'python' section"
    assert "php" in code_examples, "Code examples missing 'php' section"
    
    # Verify each language section has required fields
    for language in ["javascript", "python", "php"]:
        assert "install" in code_examples[language], f"{language} section missing 'install' field"
        assert "setup" in code_examples[language], f"{language} section missing 'setup' field"
    
    # Verify JavaScript examples
    js = code_examples["javascript"]
    assert "create_transaction" in js, "JavaScript examples missing 'create_transaction'"
    assert "create_contribution" in js, "JavaScript examples missing 'create_contribution'"
    assert "add_reaction" in js, "JavaScript examples missing 'add_reaction'"
    assert "add_comment" in js, "JavaScript examples missing 'add_comment'"
    
    # Verify Python examples
    py = code_examples["python"]
    assert "create_transaction" in py, "Python examples missing 'create_transaction'"
    assert "create_contribution" in py, "Python examples missing 'create_contribution'"
    assert "webhook_handler" in py, "Python examples missing 'webhook_handler'"
    
    print(f"Found code examples for {len(code_examples)} programming languages")
    return True

def test_dev_docs():
    """Test GET /api/dev/docs endpoint"""
    response = requests.get(f"{API_URL}/dev/docs")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    docs = response.json()
    
    # Verify documentation structure
    assert "title" in docs, "Documentation missing 'title' field"
    assert "version" in docs, "Documentation missing 'version' field"
    assert "description" in docs, "Documentation missing 'description' field"
    assert "endpoints" in docs, "Documentation missing 'endpoints' field"
    assert "examples" in docs, "Documentation missing 'examples' field"
    
    # Verify endpoints documentation
    endpoints = docs["endpoints"]
    assert "businesses" in endpoints, "Endpoints missing 'businesses' section"
    assert "causes" in endpoints, "Endpoints missing 'causes' section"
    assert "transactions" in endpoints, "Endpoints missing 'transactions' section"
    assert "contributions" in endpoints, "Endpoints missing 'contributions' section"
    
    # Verify examples
    examples = docs["examples"]
    assert "create_transaction" in examples, "Examples missing 'create_transaction'"
    assert "direct_contribution" in examples, "Examples missing 'direct_contribution'"
    assert "create_cause" in examples, "Examples missing 'create_cause'"
    
    print(f"Found documentation for {len(endpoints)} endpoint categories")
    return True

def test_dev_sdk():
    """Test GET /api/dev/sdk endpoint"""
    response = requests.get(f"{API_URL}/dev/sdk")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    sdk_info = response.json()
    
    # Verify SDK information structure
    assert "sdks" in sdk_info, "SDK information missing 'sdks' field"
    assert "webhooks" in sdk_info, "SDK information missing 'webhooks' field"
    assert "plugins" in sdk_info, "SDK information missing 'plugins' field"
    
    # Verify SDKs
    sdks = sdk_info["sdks"]
    assert "javascript" in sdks, "SDKs missing 'javascript'"
    assert "python" in sdks, "SDKs missing 'python'"
    assert "php" in sdks, "SDKs missing 'php'"
    
    # Verify each SDK has required fields
    for sdk_name, sdk in sdks.items():
        assert "name" in sdk, f"{sdk_name} SDK missing 'name' field"
        assert "version" in sdk, f"{sdk_name} SDK missing 'version' field"
        assert "install" in sdk, f"{sdk_name} SDK missing 'install' field"
        assert "docs" in sdk, f"{sdk_name} SDK missing 'docs' field"
    
    # Verify webhooks
    webhooks = sdk_info["webhooks"]
    assert "events" in webhooks, "Webhooks missing 'events' field"
    assert len(webhooks["events"]) > 0, "Expected at least one webhook event"
    
    # Verify plugins
    plugins = sdk_info["plugins"]
    assert "shopify" in plugins, "Plugins missing 'shopify'"
    assert "woocommerce" in plugins, "Plugins missing 'woocommerce'"
    
    print(f"Found information for {len(sdks)} SDKs and {len(plugins)} plugins")
    return True

# ===== ENHANCED BUSINESS DASHBOARD API TESTS =====

def test_business_dashboard_contributions_per_cause():
    """Test business dashboard API for contributions per cause"""
    # First get all businesses
    response = requests.get(f"{API_URL}/businesses")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    businesses = response.json()
    assert len(businesses) > 0, "Expected at least one business"
    
    # Use the first business for testing
    business_id = businesses[0]["id"]
    
    # Get business dashboard
    response = requests.get(f"{API_URL}/impact/dashboard/{business_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    dashboard = response.json()
    
    # Verify dashboard structure for contributions per cause
    assert "cause_breakdown" in dashboard, "Dashboard missing 'cause_breakdown' field"
    
    cause_breakdown = dashboard["cause_breakdown"]
    if len(cause_breakdown) > 0:
        # Verify first cause breakdown structure
        first_cause_id = list(cause_breakdown.keys())[0]
        cause_data = cause_breakdown[first_cause_id]
        
        assert "name" in cause_data, "Cause breakdown missing 'name' field"
        assert "category" in cause_data, "Cause breakdown missing 'category' field"
        assert "impact_metric" in cause_data, "Cause breakdown missing 'impact_metric' field"
        assert "amount" in cause_data, "Cause breakdown missing 'amount' field"
        assert "percentage" in cause_data, "Cause breakdown missing 'percentage' field"
        assert "impact_units" in cause_data, "Cause breakdown missing 'impact_units' field"
    
    print(f"Found breakdown for {len(cause_breakdown)} causes")
    return True

def test_business_dashboard_cause_health():
    """Test business dashboard API for cause health metrics"""
    # First get all causes
    response = requests.get(f"{API_URL}/causes")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    causes = response.json()
    assert len(causes) > 0, "Expected at least one cause"
    
    # Use the first cause for testing
    cause_id = causes[0]["id"]
    
    # Get cause details
    response = requests.get(f"{API_URL}/causes/{cause_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    cause = response.json()
    
    # Verify cause health metrics
    assert "total_raised" in cause, "Cause missing 'total_raised' field"
    assert "total_impact_units" in cause, "Cause missing 'total_impact_units' field"
    assert "goal_amount" in cause, "Cause missing 'goal_amount' field"
    
    # Calculate progress percentage if goal amount is set
    if cause["goal_amount"]:
        progress_percentage = (cause["total_raised"] / cause["goal_amount"]) * 100
        print(f"Cause '{cause['name']}' progress: {progress_percentage:.2f}%")
    
    # Get cause in leaderboard to check health metrics
    response = requests.get(f"{API_URL}/leaderboards/causes")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    leaderboard = response.json()
    
    # Find our cause in the leaderboard
    found = False
    for entry in leaderboard["leaderboard"]:
        if entry["cause"]["id"] == cause_id:
            found = True
            assert "progress_percentage" in entry, "Leaderboard entry missing 'progress_percentage' field"
            assert "contributor_stats" in entry, "Leaderboard entry missing 'contributor_stats' field"
            
            # Verify contributor stats
            stats = entry["contributor_stats"]
            assert "total_contributors" in stats, "Contributor stats missing 'total_contributors' field"
            assert "anonymous_contributions" in stats, "Contributor stats missing 'anonymous_contributions' field"
            assert "recent_contributions" in stats, "Contributor stats missing 'recent_contributions' field"
            break
    
    if not found and len(leaderboard["leaderboard"]) > 0:
        # If our specific cause wasn't found, at least verify the structure of the first entry
        entry = leaderboard["leaderboard"][0]
        assert "progress_percentage" in entry, "Leaderboard entry missing 'progress_percentage' field"
        assert "contributor_stats" in entry, "Leaderboard entry missing 'contributor_stats' field"
    
    print(f"Successfully tested cause health metrics")
    return True

# ===== API ERROR FIXES TESTS =====

def test_causes_api_no_500_errors():
    """Test that /api/causes endpoint doesn't return 500 errors"""
    response = requests.get(f"{API_URL}/causes")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    causes = response.json()
    assert len(causes) > 0, "Expected at least one cause"
    
    # Test with various filters to ensure no 500 errors
    filter_combinations = [
        "?active_only=true",
        "?featured_only=true",
        "?active_only=true&featured_only=true",
        "?sort_by=total_raised&sort_order=desc",
        "?sort_by=created_at&sort_order=asc"
    ]
    
    for filters in filter_combinations:
        response = requests.get(f"{API_URL}/causes{filters}")
        assert response.status_code == 200, f"Expected status code 200 for filters '{filters}', got {response.status_code}"
    
    print(f"Successfully tested /api/causes endpoint with {len(filter_combinations)} filter combinations")
    return True

def test_leaderboards_causes_no_500_errors():
    """Test that /api/leaderboards/causes endpoint doesn't return 500 errors"""
    response = requests.get(f"{API_URL}/leaderboards/causes")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    leaderboard = response.json()
    assert "metric" in leaderboard, "Leaderboard response missing 'metric' field"
    assert "leaderboard" in leaderboard, "Leaderboard response missing 'leaderboard' field"
    
    # Test with different metrics
    metrics = ["total_raised", "total_impact_units"]
    for metric in metrics:
        response = requests.get(f"{API_URL}/leaderboards/causes?metric={metric}")
        assert response.status_code == 200, f"Expected status code 200 for metric '{metric}', got {response.status_code}"
    
    # Test with limit parameter
    limits = [5, 10, 20]
    for limit in limits:
        response = requests.get(f"{API_URL}/leaderboards/causes?limit={limit}")
        assert response.status_code == 200, f"Expected status code 200 for limit '{limit}', got {response.status_code}"
        
        leaderboard = response.json()
        assert len(leaderboard["leaderboard"]) <= limit, f"Expected at most {limit} entries, got {len(leaderboard['leaderboard'])}"
    
    print(f"Successfully tested /api/leaderboards/causes endpoint with various parameters")
    return True

def test_admin_settlements_no_500_errors():
    """Test that /api/admin/settlements endpoint doesn't return 500 errors"""
    response = requests.get(f"{API_URL}/admin/settlements")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    settlements = response.json()
    
    # Verify settlements structure
    assert "settlements" in settlements, "Response missing 'settlements' field"
    
    # If there are settlements, verify they have the correct structure
    if len(settlements["settlements"]) > 0:
        settlement = settlements["settlements"][0]
        assert "cause_id" in settlement, "Settlement missing 'cause_id' field"
        assert "cause_name" in settlement, "Settlement missing 'cause_name' field"
        assert "total_donations_received" in settlement, "Settlement missing 'total_donations_received' field"
        assert "pending_amount" in settlement, "Settlement missing 'pending_amount' field"
        assert "total_settled" in settlement, "Settlement missing 'total_settled' field"
    
    print(f"Successfully tested /api/admin/settlements endpoint")
    return True

if __name__ == "__main__":
    # Run tests for Developer Platform API
    print("\n===== TESTING DEVELOPER PLATFORM API =====")
    run_test("Developer Code Examples", test_dev_code_examples)
    run_test("Developer Documentation", test_dev_docs)
    run_test("Developer SDK Information", test_dev_sdk)
    
    # Run tests for Enhanced Business Dashboard APIs
    print("\n===== TESTING ENHANCED BUSINESS DASHBOARD APIs =====")
    run_test("Business Dashboard - Contributions Per Cause", test_business_dashboard_contributions_per_cause)
    run_test("Business Dashboard - Cause Health", test_business_dashboard_cause_health)
    
    # Run tests for API Error Fixes
    print("\n===== TESTING API ERROR FIXES =====")
    run_test("Causes API - No 500 Errors", test_causes_api_no_500_errors)
    run_test("Leaderboards Causes API - No 500 Errors", test_leaderboards_causes_no_500_errors)
    run_test("Admin Settlements API - No 500 Errors", test_admin_settlements_no_500_errors)
    
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