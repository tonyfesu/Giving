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

# Get a cause ID for testing
def get_test_cause_id():
    response = requests.get(f"{API_URL}/causes")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    causes = response.json()
    assert len(causes) > 0, "No causes found for testing"
    return causes[0]["id"]

# ===== SHARE FEATURE TESTS =====

def test_share_feature():
    """Test POST /api/causes/{cause_id}/share endpoint with the fixed implementation"""
    cause_id = get_test_cause_id()
    
    # Test with the specific payload mentioned in the review request
    share_data = {
        "user_id": "test_user", 
        "platform": "facebook"
    }
    
    response = requests.post(f"{API_URL}/causes/{cause_id}/share", json=share_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    print("Share Feature Response:", json.dumps(data, indent=2))
    
    # Verify response includes all required fields
    assert "message" in data, "Response missing 'message' field"
    assert "share_record" in data, "Response missing 'share_record' field"
    assert "share_url" in data, "Response missing 'share_url' field"
    assert "social_links" in data, "Response missing 'social_links' field"
    
    # Verify share_record structure
    share_record = data["share_record"]
    assert "id" in share_record, "Share record missing 'id' field"
    assert "cause_id" in share_record, "Share record missing 'cause_id' field"
    assert "share_url" in share_record, "Share record missing 'share_url' field"
    assert "shared_by" in share_record, "Share record missing 'shared_by' field"
    assert "platform" in share_record, "Share record missing 'platform' field"
    assert "created_at" in share_record, "Share record missing 'created_at' field"
    
    # Verify social_links structure
    social_links = data["social_links"]
    expected_platforms = ["facebook", "twitter", "linkedin", "whatsapp", "email"]
    for platform in expected_platforms:
        assert platform in social_links, f"Social links missing '{platform}' platform"
    
    return True

# ===== COMMENTS SYSTEM TESTS =====

def test_comments_system():
    """Test POST /api/causes/{cause_id}/comments endpoint with the fixed implementation"""
    cause_id = get_test_cause_id()
    
    # Test with the specific payload mentioned in the review request
    comment_data = {
        "comment": "Great cause!",
        "user_id": "customer_id",
        "user_type": "customer"
    }
    
    response = requests.post(f"{API_URL}/causes/{cause_id}/comments", json=comment_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    print("Comments System Response:", json.dumps(data, indent=2))
    
    # Verify comment is created and user info is properly resolved
    assert "id" in data, "Response missing 'id' field"
    assert "user_id" in data, "Response missing 'user_id' field"
    assert "user_type" in data, "Response missing 'user_type' field"
    assert "user_name" in data, "Response missing 'user_name' field"
    assert "comment" in data, "Response missing 'comment' field"
    
    assert data["user_id"] == comment_data["user_id"], f"Expected user_id {comment_data['user_id']}, got {data['user_id']}"
    assert data["user_type"] == comment_data["user_type"], f"Expected user_type {comment_data['user_type']}, got {data['user_type']}"
    assert data["comment"] == comment_data["comment"], f"Expected comment {comment_data['comment']}, got {data['comment']}"
    
    return True

# ===== EMOJI REACTIONS TESTS =====

def test_reactions_get():
    """Test GET /api/causes/{cause_id}/reactions endpoint with the fixed implementation"""
    cause_id = get_test_cause_id()
    
    response = requests.get(f"{API_URL}/causes/{cause_id}/reactions")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    print("Reactions GET Response:", json.dumps(data, indent=2))
    
    # Verify 'reactions' field is present
    assert "reactions" in data, "Response missing 'reactions' field"
    
    return True

def test_reactions_post():
    """Test POST /api/causes/{cause_id}/reactions endpoint with the fixed implementation"""
    cause_id = get_test_cause_id()
    
    # Test with the specific payload mentioned in the review request
    reaction_data = {
        "emoji": "❤️",
        "user_id": "customer_id",
        "user_type": "customer"
    }
    
    response = requests.post(f"{API_URL}/causes/{cause_id}/reactions", json=reaction_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    print("Reactions POST Response:", json.dumps(data, indent=2))
    
    assert "message" in data, "Response missing 'message' field"
    assert "emoji" in data, "Response missing 'emoji' field"
    
    return True

def test_reactions_delete():
    """Test DELETE /api/causes/{cause_id}/reactions endpoint with the fixed implementation"""
    cause_id = get_test_cause_id()
    
    # First, add a reaction to ensure there's something to delete
    reaction_data = {
        "emoji": "❤️",
        "user_id": "customer_id",
        "user_type": "customer"
    }
    
    response = requests.post(f"{API_URL}/causes/{cause_id}/reactions", json=reaction_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # Now delete the reaction
    user_data = {
        "user_id": "customer_id"
    }
    
    response = requests.delete(f"{API_URL}/causes/{cause_id}/reactions", json=user_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    print("Reactions DELETE Response:", json.dumps(data, indent=2))
    
    assert "message" in data, "Response missing 'message' field"
    
    return True

if __name__ == "__main__":
    # Run tests for the fixed social features
    print("\n===== TESTING FIXED SOCIAL FEATURES =====")
    
    # Share Feature Test
    run_test("Share Feature", test_share_feature)
    
    # Comments System Test
    run_test("Comments System", test_comments_system)
    
    # Emoji Reactions Tests
    run_test("Reactions GET", test_reactions_get)
    run_test("Reactions POST", test_reactions_post)
    run_test("Reactions DELETE", test_reactions_delete)
    
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