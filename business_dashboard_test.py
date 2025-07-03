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

# ===== BUSINESS DASHBOARD TESTS =====

def test_business_dashboard():
    """Test GET /api/impact/dashboard/{business_id} for EcoTech Solutions"""
    # First, get the EcoTech Solutions business ID
    response = requests.get(f"{API_URL}/businesses")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    businesses = response.json()
    ecotech_business = None
    for business in businesses:
        if business["name"] == "EcoTech Solutions":
            ecotech_business = business
            break
    
    assert ecotech_business is not None, "EcoTech Solutions business not found"
    business_id = ecotech_business["id"]
    
    # Get the business dashboard
    response = requests.get(f"{API_URL}/impact/dashboard/{business_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    dashboard = response.json()
    
    # Verify dashboard structure
    assert "business" in dashboard, "Dashboard missing business data"
    assert "recent_transactions" in dashboard, "Dashboard missing recent_transactions"
    assert "cause_breakdown" in dashboard, "Dashboard missing cause_breakdown"
    assert "total_sales" in dashboard, "Dashboard missing total_sales"
    assert "total_impact" in dashboard, "Dashboard missing total_impact"
    assert "impact_percentage" in dashboard, "Dashboard missing impact_percentage"
    
    # Verify business data
    assert dashboard["business"]["id"] == business_id, f"Expected business id {business_id}, got {dashboard['business']['id']}"
    assert dashboard["business"]["name"] == "EcoTech Solutions", f"Expected business name 'EcoTech Solutions', got {dashboard['business']['name']}"
    
    # Verify transaction data
    assert len(dashboard["recent_transactions"]) > 0, "Expected at least one transaction"
    
    # Verify cause breakdown
    assert len(dashboard["cause_breakdown"]) > 0, "Expected at least one cause in breakdown"
    
    print(f"Business dashboard metrics: Total sales: ${dashboard['total_sales']}, Total impact: ${dashboard['total_impact']}")
    print(f"Impact percentage: {dashboard['impact_percentage']}%")
    print(f"Found {len(dashboard['recent_transactions'])} recent transactions")
    print(f"Found {len(dashboard['cause_breakdown'])} causes in breakdown")
    
    return True

# ===== BUSINESS CAUSE MANAGEMENT TESTS =====

def test_causes_with_creator_filter():
    """Test GET /api/causes with creator_type filter to get business-specific causes"""
    # Get all causes
    response = requests.get(f"{API_URL}/causes")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    all_causes = response.json()
    
    # Get business-created causes
    response = requests.get(f"{API_URL}/causes?creator_type=business")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    business_causes = response.json()
    
    # Get customer-created causes
    response = requests.get(f"{API_URL}/causes?creator_type=customer")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    customer_causes = response.json()
    
    # Verify filtering
    assert len(business_causes) > 0, "Expected at least one business-created cause"
    assert len(customer_causes) > 0, "Expected at least one customer-created cause"
    assert len(all_causes) == len(business_causes) + len(customer_causes), "Sum of filtered causes should equal total causes"
    
    # Verify all business causes have correct creator_type
    for cause in business_causes:
        assert cause["creator_type"] == "business", f"Expected creator_type 'business', got {cause['creator_type']}"
        assert "creator_name" in cause, "Cause missing creator_name"
    
    # Verify all customer causes have correct creator_type
    for cause in customer_causes:
        assert cause["creator_type"] == "customer", f"Expected creator_type 'customer', got {cause['creator_type']}"
        assert "creator_name" in cause, "Cause missing creator_name"
    
    print(f"Found {len(business_causes)} business-created causes and {len(customer_causes)} customer-created causes")
    
    return True

def test_cause_health_calculation():
    """Test that cause health can be calculated from the data"""
    # Get all causes
    response = requests.get(f"{API_URL}/causes")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    causes = response.json()
    
    # Calculate health metrics for each cause
    for cause in causes:
        # Calculate progress percentage
        if cause["goal_amount"]:
            progress_percentage = (cause["total_raised"] / cause["goal_amount"]) * 100
            print(f"Cause: {cause['name']}, Progress: {progress_percentage:.2f}%")
            
            # Calculate time-based metrics
            if cause["end_date"]:
                import datetime
                end_date = datetime.datetime.fromisoformat(cause["end_date"].replace('Z', '+00:00'))
                now = datetime.datetime.utcnow()
                
                if end_date > now:
                    days_remaining = (end_date - now).days
                    print(f"  Days remaining: {days_remaining}")
                    
                    # Calculate daily target to reach goal
                    amount_remaining = cause["goal_amount"] - cause["total_raised"]
                    if days_remaining > 0:
                        daily_target = amount_remaining / days_remaining
                        print(f"  Daily target to reach goal: ${daily_target:.2f}")
    
    return True

# ===== COMMENT SYSTEM TESTS =====

def test_comment_system():
    """Test comment system for business-created causes"""
    # Get business-created causes
    response = requests.get(f"{API_URL}/causes?creator_type=business")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    business_causes = response.json()
    
    assert len(business_causes) > 0, "Expected at least one business-created cause"
    cause_id = business_causes[0]["id"]
    
    # Get comments for the cause
    response = requests.get(f"{API_URL}/causes/{cause_id}/comments")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    initial_comments = response.json()
    print(f"Found {len(initial_comments)} existing comments for cause {business_causes[0]['name']}")
    
    # Create a new comment
    comment_data = {
        "comment": "This is a test comment from the testing agent",
        "parent_comment_id": None
    }
    
    # Get the business ID (creator of the cause)
    business_id = business_causes[0]["creator_id"]
    
    # Add a comment as if from a customer
    response = requests.post(
        f"{API_URL}/causes/{cause_id}/comments?user_id=test_customer&user_name=Test Customer&user_type=customer", 
        json=comment_data
    )
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    customer_comment = response.json()
    assert customer_comment["user_type"] == "customer", f"Expected user_type 'customer', got {customer_comment['user_type']}"
    assert customer_comment["is_admin_response"] == False, "Customer comment should not be marked as admin response"
    
    # Add a reply as if from the business (creator)
    reply_data = {
        "comment": "Thank you for your comment! This is a test reply from the business.",
        "parent_comment_id": customer_comment["id"]
    }
    
    response = requests.post(
        f"{API_URL}/causes/{cause_id}/comments?user_id={business_id}&user_name={business_causes[0]['creator_name']}&user_type=business", 
        json=reply_data
    )
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    business_reply = response.json()
    assert business_reply["user_type"] == "business", f"Expected user_type 'business', got {business_reply['user_type']}"
    assert business_reply["is_admin_response"] == True, "Business reply should be marked as admin response"
    assert business_reply["parent_comment_id"] == customer_comment["id"], "Reply should reference parent comment"
    
    # Get updated comments to verify threading
    response = requests.get(f"{API_URL}/causes/{cause_id}/comments")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    updated_comments = response.json()
    assert len(updated_comments) > len(initial_comments), "Comment count should have increased"
    
    # Verify comment threading structure
    found_comment = False
    found_reply = False
    
    for comment in updated_comments:
        if comment.get("id") == customer_comment["id"]:
            found_comment = True
            if "replies" in comment:
                for reply in comment["replies"]:
                    if reply.get("id") == business_reply["id"]:
                        found_reply = True
                        assert reply["is_admin_response"] == True, "Business reply should be marked as admin response"
    
    assert found_comment, "Could not find the customer comment in the threaded comments"
    assert found_reply, "Could not find the business reply in the threaded comments"
    
    return True

# ===== DEVELOPER PLATFORM TESTS =====

def test_dev_code_examples():
    """Test GET /api/dev/code-examples endpoint"""
    response = requests.get(f"{API_URL}/dev/code-examples")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    code_examples = response.json()
    
    # Verify code examples for required languages
    assert "javascript" in code_examples, "Code examples missing JavaScript"
    assert "python" in code_examples, "Code examples missing Python"
    assert "php" in code_examples, "Code examples missing PHP"
    
    # Verify each language has required sections
    for language in ["javascript", "python", "php"]:
        assert "install" in code_examples[language], f"{language} examples missing install instructions"
        assert "setup" in code_examples[language], f"{language} examples missing setup code"
        
        # Verify social features are included
        assert "add_reaction" in code_examples[language], f"{language} examples missing emoji reaction code"
        assert "add_comment" in code_examples[language], f"{language} examples missing comment code"
    
    # Verify JavaScript has additional social features
    assert "create_transaction" in code_examples["javascript"], "JavaScript examples missing transaction code"
    assert "create_contribution" in code_examples["javascript"], "JavaScript examples missing contribution code"
    
    print(f"Found code examples for {len(code_examples)} languages with social features")
    
    return True

def test_dev_sdk_information():
    """Test GET /api/dev/sdk endpoint for enhanced SDK information"""
    response = requests.get(f"{API_URL}/dev/sdk")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    sdk_info = response.json()
    
    # Verify SDK information structure
    assert "sdks" in sdk_info, "SDK information missing 'sdks' field"
    assert "webhooks" in sdk_info, "SDK information missing 'webhooks' field"
    assert "plugins" in sdk_info, "SDK information missing 'plugins' field"
    
    # Verify SDKs for required languages
    assert "javascript" in sdk_info["sdks"], "SDK information missing JavaScript SDK"
    assert "python" in sdk_info["sdks"], "SDK information missing Python SDK"
    assert "php" in sdk_info["sdks"], "SDK information missing PHP SDK"
    
    # Verify SDK details
    for language in ["javascript", "python", "php"]:
        sdk = sdk_info["sdks"][language]
        assert "name" in sdk, f"{language} SDK missing name"
        assert "version" in sdk, f"{language} SDK missing version"
        assert "install" in sdk, f"{language} SDK missing install instructions"
        assert "docs" in sdk, f"{language} SDK missing documentation link"
    
    # Verify webhook information
    assert "events" in sdk_info["webhooks"], "Webhook information missing events"
    assert len(sdk_info["webhooks"]["events"]) > 0, "Expected at least one webhook event"
    
    # Verify plugin information
    assert "shopify" in sdk_info["plugins"], "Plugin information missing Shopify plugin"
    assert "woocommerce" in sdk_info["plugins"], "Plugin information missing WooCommerce plugin"
    
    print(f"Found SDK information for {len(sdk_info['sdks'])} languages")
    print(f"Found {len(sdk_info['webhooks']['events'])} webhook events")
    print(f"Found {len(sdk_info['plugins'])} plugins")
    
    return True

# ===== SOCIAL FEATURES TESTS =====

def test_share_functionality():
    """Test share functionality for business-created causes"""
    # Get business-created causes
    response = requests.get(f"{API_URL}/causes?creator_type=business")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    business_causes = response.json()
    
    assert len(business_causes) > 0, "Expected at least one business-created cause"
    cause_id = business_causes[0]["id"]
    
    # Get share URL and social links
    response = requests.get(f"{API_URL}/causes/{cause_id}/share")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    share_data = response.json()
    assert "share_url" in share_data, "Share response missing share_url"
    assert "social_links" in share_data, "Share response missing social_links"
    
    # Verify social links
    social_links = share_data["social_links"]
    assert "facebook" in social_links, "Social links missing Facebook"
    assert "twitter" in social_links, "Social links missing Twitter"
    assert "whatsapp" in social_links, "Social links missing WhatsApp"
    assert "linkedin" in social_links, "Social links missing LinkedIn"
    assert "email" in social_links, "Social links missing Email"
    
    # Track a share
    share_track_data = {
        "user_id": "test_user",
        "platform": "facebook"
    }
    
    response = requests.post(f"{API_URL}/causes/{cause_id}/share", json=share_track_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    result = response.json()
    assert "message" in result, "Share tracking response missing message"
    assert result["message"] == "Share tracked successfully", f"Expected message 'Share tracked successfully', got {result['message']}"
    
    print(f"Successfully tested share functionality for cause: {business_causes[0]['name']}")
    print(f"Share URL: {share_data['share_url']}")
    print(f"Social platforms: {', '.join(social_links.keys())}")
    
    return True

def test_emoji_reactions():
    """Test emoji reactions for causes"""
    # Get business-created causes
    response = requests.get(f"{API_URL}/causes?creator_type=business")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    business_causes = response.json()
    
    assert len(business_causes) > 0, "Expected at least one business-created cause"
    cause_id = business_causes[0]["id"]
    
    # Get initial reactions
    response = requests.get(f"{API_URL}/causes/{cause_id}/reactions")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    initial_reactions = response.json()
    print(f"Initial reaction counts: {initial_reactions['reaction_counts']}")
    
    # Add a reaction
    reaction_data = {
        "emoji": "❤️"
    }
    
    response = requests.post(
        f"{API_URL}/causes/{cause_id}/reactions?user_id=test_user&user_name=Test User", 
        json=reaction_data
    )
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # Get updated reactions
    response = requests.get(f"{API_URL}/causes/{cause_id}/reactions")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    updated_reactions = response.json()
    assert "❤️" in updated_reactions["reaction_counts"], "Heart emoji not found in reaction counts"
    assert updated_reactions["reaction_counts"]["❤️"] >= 1, "Expected at least one heart reaction"
    
    # Verify user reaction is tracked
    assert "test_user" in updated_reactions["user_reactions"], "User reaction not tracked"
    assert updated_reactions["user_reactions"]["test_user"] == "❤️", f"Expected user reaction '❤️', got {updated_reactions['user_reactions']['test_user']}"
    
    # Change reaction
    reaction_data = {
        "emoji": "👍"
    }
    
    response = requests.post(
        f"{API_URL}/causes/{cause_id}/reactions?user_id=test_user&user_name=Test User", 
        json=reaction_data
    )
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # Get updated reactions
    response = requests.get(f"{API_URL}/causes/{cause_id}/reactions")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    updated_reactions = response.json()
    assert "👍" in updated_reactions["reaction_counts"], "Thumbs up emoji not found in reaction counts"
    assert updated_reactions["reaction_counts"]["👍"] >= 1, "Expected at least one thumbs up reaction"
    
    # Verify user reaction was updated
    assert updated_reactions["user_reactions"]["test_user"] == "👍", f"Expected user reaction '👍', got {updated_reactions['user_reactions']['test_user']}"
    
    # Delete reaction
    response = requests.delete(f"{API_URL}/causes/{cause_id}/reactions?user_id=test_user")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # Get final reactions
    response = requests.get(f"{API_URL}/causes/{cause_id}/reactions")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    final_reactions = response.json()
    assert "test_user" not in final_reactions["user_reactions"], "User reaction should have been deleted"
    
    print(f"Successfully tested emoji reactions for cause: {business_causes[0]['name']}")
    
    return True

if __name__ == "__main__":
    # Run tests
    print("\n===== TESTING BUSINESS DASHBOARD FUNCTIONALITY =====")
    run_test("Business Dashboard API", test_business_dashboard)
    run_test("Causes with Creator Filter", test_causes_with_creator_filter)
    run_test("Cause Health Calculation", test_cause_health_calculation)
    
    print("\n===== TESTING BUSINESS CAUSE MANAGEMENT =====")
    run_test("Comment System for Business-Created Causes", test_comment_system)
    
    print("\n===== TESTING DEVELOPER PLATFORM =====")
    run_test("Developer Code Examples", test_dev_code_examples)
    run_test("Enhanced SDK Information", test_dev_sdk_information)
    
    print("\n===== TESTING SOCIAL FEATURES INTEGRATION =====")
    run_test("Share Functionality", test_share_functionality)
    run_test("Emoji Reactions", test_emoji_reactions)
    
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