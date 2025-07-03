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

# ===== SOCIAL FEATURES TESTS =====

def test_social_sharing():
    """Test social sharing features"""
    # First get all causes
    response = requests.get(f"{API_URL}/causes")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    causes = response.json()
    assert len(causes) > 0, "Expected at least one cause"
    
    # Use the first cause for testing
    cause_id = causes[0]["id"]
    
    # Get share links
    response = requests.get(f"{API_URL}/causes/{cause_id}/share")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    share_data = response.json()
    
    # Verify share data structure
    assert "share_url" in share_data, "Share data missing 'share_url' field"
    assert "social_links" in share_data, "Share data missing 'social_links' field"
    
    # Verify social links
    social_links = share_data["social_links"]
    assert "facebook" in social_links, "Social links missing 'facebook'"
    assert "twitter" in social_links, "Social links missing 'twitter'"
    assert "whatsapp" in social_links, "Social links missing 'whatsapp'"
    assert "linkedin" in social_links, "Social links missing 'linkedin'"
    assert "email" in social_links, "Social links missing 'email'"
    
    # Test tracking a share
    share_platform = "facebook"
    response = requests.post(f"{API_URL}/causes/{cause_id}/share", json={"platform": share_platform})
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    share_result = response.json()
    assert "id" in share_result, "Share result missing 'id' field"
    assert "platform" in share_result, "Share result missing 'platform' field"
    assert share_result["platform"] == share_platform, f"Expected platform '{share_platform}', got '{share_result['platform']}'"
    
    print(f"Successfully tested social sharing for cause {cause_id}")
    return True

def test_comments_system():
    """Test comments system"""
    # First get all causes
    response = requests.get(f"{API_URL}/causes")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    causes = response.json()
    assert len(causes) > 0, "Expected at least one cause"
    
    # Use the first cause for testing
    cause_id = causes[0]["id"]
    
    # Get comments
    response = requests.get(f"{API_URL}/causes/{cause_id}/comments")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    comments_data = response.json()
    assert "comments" in comments_data, "Response missing 'comments' field"
    
    # Create a new comment
    comment_text = f"Test comment created at {time.time()}"
    response = requests.post(f"{API_URL}/causes/{cause_id}/comments", json={"comment": comment_text})
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    comment = response.json()
    assert "id" in comment, "Comment response missing 'id' field"
    assert "comment" in comment, "Comment response missing 'comment' field"
    assert comment["comment"] == comment_text, f"Expected comment '{comment_text}', got '{comment['comment']}'"
    
    # Get comments again to verify our new comment is there
    response = requests.get(f"{API_URL}/causes/{cause_id}/comments")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    comments_data = response.json()
    comments = comments_data["comments"]
    
    # Find our comment
    found = False
    for c in comments:
        if c["id"] == comment["id"]:
            found = True
            assert c["comment"] == comment_text, f"Expected comment '{comment_text}', got '{c['comment']}'"
            break
    
    assert found, "Could not find our new comment in the comments list"
    
    # Create a reply to our comment
    reply_text = f"Test reply created at {time.time()}"
    response = requests.post(f"{API_URL}/causes/{cause_id}/comments", 
                            json={"comment": reply_text, "parent_comment_id": comment["id"]})
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    reply = response.json()
    assert "id" in reply, "Reply response missing 'id' field"
    assert "comment" in reply, "Reply response missing 'comment' field"
    assert reply["comment"] == reply_text, f"Expected reply '{reply_text}', got '{reply['comment']}'"
    assert "parent_comment_id" in reply, "Reply response missing 'parent_comment_id' field"
    assert reply["parent_comment_id"] == comment["id"], f"Expected parent_comment_id '{comment['id']}', got '{reply['parent_comment_id']}'"
    
    # Get comments again to verify our reply is there
    response = requests.get(f"{API_URL}/causes/{cause_id}/comments")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    comments_data = response.json()
    comments = comments_data["comments"]
    
    # Find our comment and verify it has our reply
    found_comment = False
    found_reply = False
    for c in comments:
        if c["id"] == comment["id"]:
            found_comment = True
            if "replies" in c:
                for r in c["replies"]:
                    if r["id"] == reply["id"]:
                        found_reply = True
                        assert r["comment"] == reply_text, f"Expected reply '{reply_text}', got '{r['comment']}'"
                        break
            break
    
    assert found_comment, "Could not find our comment in the comments list"
    assert found_reply, "Could not find our reply in the replies list"
    
    print(f"Successfully tested comments system for cause {cause_id}")
    return True

def test_emoji_reactions():
    """Test emoji reactions system"""
    # First get all causes
    response = requests.get(f"{API_URL}/causes")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    causes = response.json()
    assert len(causes) > 0, "Expected at least one cause"
    
    # Use the first cause for testing
    cause_id = causes[0]["id"]
    
    # Get reactions
    response = requests.get(f"{API_URL}/causes/{cause_id}/reactions")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    reactions_data = response.json()
    assert "reactions" in reactions_data, "Response missing 'reactions' field"
    assert "user_reactions" in reactions_data, "Response missing 'user_reactions' field"
    
    # Create a new reaction
    emoji = "❤️"
    response = requests.post(f"{API_URL}/causes/{cause_id}/reactions", json={"emoji": emoji})
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    reaction = response.json()
    assert "id" in reaction, "Reaction response missing 'id' field"
    assert "emoji" in reaction, "Reaction response missing 'emoji' field"
    assert reaction["emoji"] == emoji, f"Expected emoji '{emoji}', got '{reaction['emoji']}'"
    
    # Get reactions again to verify our new reaction is counted
    response = requests.get(f"{API_URL}/causes/{cause_id}/reactions")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    reactions_data = response.json()
    reactions = reactions_data["reactions"]
    
    # Verify our emoji is in the reactions
    assert emoji in reactions, f"Could not find our emoji '{emoji}' in the reactions"
    
    # Update our reaction to a different emoji
    new_emoji = "👍"
    response = requests.post(f"{API_URL}/causes/{cause_id}/reactions", json={"emoji": new_emoji})
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # Get reactions again to verify our updated reaction
    response = requests.get(f"{API_URL}/causes/{cause_id}/reactions")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    reactions_data = response.json()
    reactions = reactions_data["reactions"]
    
    # Verify our new emoji is in the reactions
    assert new_emoji in reactions, f"Could not find our new emoji '{new_emoji}' in the reactions"
    
    # Delete our reaction
    response = requests.delete(f"{API_URL}/causes/{cause_id}/reactions")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    print(f"Successfully tested emoji reactions for cause {cause_id}")
    return True

# ===== SAMPLE DATA TESTS =====

def test_sample_data():
    """Test that sample data is accessible"""
    # Test causes
    response = requests.get(f"{API_URL}/causes")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    causes = response.json()
    assert len(causes) >= 6, f"Expected at least 6 causes, got {len(causes)}"
    
    # Verify cause categories
    categories = set(cause["category"] for cause in causes)
    print(f"Found causes in {len(categories)} categories: {', '.join(categories)}")
    
    # Test demo users
    response = requests.get(f"{API_URL}/admin/demo-users")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    demo_users = response.json()
    assert "businesses" in demo_users, "Demo users response missing 'businesses' field"
    assert "customers" in demo_users, "Demo users response missing 'customers' field"
    assert "admins" in demo_users, "Demo users response missing 'admins' field"
    
    businesses = demo_users["businesses"]
    customers = demo_users["customers"]
    admins = demo_users["admins"]
    
    assert len(businesses) >= 1, f"Expected at least 1 demo business, got {len(businesses)}"
    assert len(customers) >= 1, f"Expected at least 1 demo customer, got {len(customers)}"
    assert len(admins) >= 1, f"Expected at least 1 demo admin, got {len(admins)}"
    
    # Verify EcoTech Solutions business
    found_ecotech = False
    for business in businesses:
        if business["name"] == "EcoTech Solutions":
            found_ecotech = True
            break
    
    assert found_ecotech, "Could not find 'EcoTech Solutions' demo business"
    
    # Verify Sarah Green customer
    found_sarah = False
    for customer in customers:
        if customer["name"] == "Sarah Green":
            found_sarah = True
            break
    
    assert found_sarah, "Could not find 'Sarah Green' demo customer"
    
    print(f"Successfully verified sample data: {len(causes)} causes, {len(businesses)} businesses, {len(customers)} customers, {len(admins)} admins")
    return True

if __name__ == "__main__":
    # Run tests for Social Features
    print("\n===== TESTING SOCIAL FEATURES =====")
    run_test("Social Sharing", test_social_sharing)
    run_test("Comments System", test_comments_system)
    run_test("Emoji Reactions", test_emoji_reactions)
    
    # Run tests for Sample Data
    print("\n===== TESTING SAMPLE DATA =====")
    run_test("Sample Data Verification", test_sample_data)
    
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