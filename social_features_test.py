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

# ===== SETUP FUNCTIONS =====

def get_demo_users():
    """Get demo users for testing"""
    # Get demo business
    response = requests.get(f"{API_URL}/businesses")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    businesses = response.json()
    
    demo_business = None
    for business in businesses:
        if business["name"] == "EcoTech Solutions":
            demo_business = business
            break
    
    assert demo_business is not None, "Demo business 'EcoTech Solutions' not found"
    
    # Get demo customer
    response = requests.get(f"{API_URL}/customers")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    customers = response.json()
    
    demo_customer = None
    for customer in customers:
        if customer["name"] == "Sarah Green":
            demo_customer = customer
            break
    
    assert demo_customer is not None, "Demo customer 'Sarah Green' not found"
    
    # Get admin user
    response = requests.get(f"{API_URL}/admin/businesses")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # Get a cause
    response = requests.get(f"{API_URL}/causes")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    causes = response.json()
    assert len(causes) > 0, "No causes found"
    
    return {
        "business": demo_business,
        "customer": demo_customer,
        "cause": causes[0]
    }

# ===== SHARE FEATURE TESTS =====

def test_get_cause_share_url():
    """Test GET /api/causes/{cause_id}/share endpoint"""
    demo_data = get_demo_users()
    cause_id = demo_data["cause"]["id"]
    
    response = requests.get(f"{API_URL}/causes/{cause_id}/share")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    share_data = response.json()
    assert "cause_id" in share_data, "Share data missing 'cause_id' field"
    assert "share_url" in share_data, "Share data missing 'share_url' field"
    assert "social_links" in share_data, "Share data missing 'social_links' field"
    
    # Verify social links
    social_links = share_data["social_links"]
    required_platforms = ["facebook", "twitter", "whatsapp", "linkedin", "email"]
    for platform in required_platforms:
        assert platform in social_links, f"Social links missing '{platform}' platform"
        assert social_links[platform].startswith("http") or social_links[platform].startswith("mailto"), f"Invalid {platform} link format"
    
    # Verify share URL format
    assert cause_id in share_data["share_url"], f"Share URL should contain cause ID"
    
    print(f"Share URL: {share_data['share_url']}")
    print(f"Social links: {json.dumps(social_links, indent=2)}")
    
    return True

def test_track_cause_share():
    """Test POST /api/causes/{cause_id}/share endpoint"""
    demo_data = get_demo_users()
    cause_id = demo_data["cause"]["id"]
    
    # Test share tracking for different platforms
    platforms = ["facebook", "twitter", "whatsapp", "linkedin", "email", "link"]
    
    for platform in platforms:
        share_data = {
            "user_id": demo_data["customer"]["id"],
            "platform": platform
        }
        
        response = requests.post(f"{API_URL}/causes/{cause_id}/share", json=share_data)
        assert response.status_code == 200, f"Expected status code 200 for {platform} share, got {response.status_code}"
        
        result = response.json()
        assert "message" in result, f"Share tracking response for {platform} missing 'message' field"
        assert result["message"] == "Share tracked successfully", f"Unexpected message for {platform} share: {result['message']}"
    
    # Test anonymous share (no user_id)
    share_data = {
        "platform": "link"
    }
    
    response = requests.post(f"{API_URL}/causes/{cause_id}/share", json=share_data)
    assert response.status_code == 200, f"Expected status code 200 for anonymous share, got {response.status_code}"
    
    # Test with invalid cause ID
    response = requests.post(f"{API_URL}/causes/invalid-id/share", json=share_data)
    assert response.status_code == 404, f"Expected status code 404 for invalid cause ID, got {response.status_code}"
    
    return True

# ===== COMMENTS SYSTEM TESTS =====

def test_get_cause_comments():
    """Test GET /api/causes/{cause_id}/comments endpoint"""
    demo_data = get_demo_users()
    cause_id = demo_data["cause"]["id"]
    
    response = requests.get(f"{API_URL}/causes/{cause_id}/comments")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    comments_data = response.json()
    assert "cause_id" in comments_data, "Comments data missing 'cause_id' field"
    assert "comments" in comments_data, "Comments data missing 'comments' field"
    assert "total_comments" in comments_data, "Comments data missing 'total_comments' field"
    
    # Verify comments structure
    comments = comments_data["comments"]
    for comment_obj in comments:
        assert "comment" in comment_obj, "Comment object missing 'comment' field"
        assert "replies" in comment_obj, "Comment object missing 'replies' field"
        
        comment = comment_obj["comment"]
        assert "id" in comment, "Comment missing 'id' field"
        assert "user_id" in comment, "Comment missing 'user_id' field"
        assert "user_name" in comment, "Comment missing 'user_name' field"
        assert "comment" in comment, "Comment missing 'comment' field"
        assert "is_admin_response" in comment, "Comment missing 'is_admin_response' field"
        
        # Verify replies structure
        for reply in comment_obj["replies"]:
            assert "id" in reply, "Reply missing 'id' field"
            assert "parent_comment_id" in reply, "Reply missing 'parent_comment_id' field"
            assert reply["parent_comment_id"] == comment["id"], "Reply parent_comment_id should match parent comment id"
    
    # Test with invalid cause ID
    response = requests.get(f"{API_URL}/causes/invalid-id/comments")
    assert response.status_code == 404, f"Expected status code 404 for invalid cause ID, got {response.status_code}"
    
    return True

def test_create_cause_comment():
    """Test POST /api/causes/{cause_id}/comments endpoint"""
    demo_data = get_demo_users()
    cause_id = demo_data["cause"]["id"]
    
    # Test comment creation as customer
    customer_comment_data = {
        "comment": "This is a test comment from a customer",
        "parent_comment_id": None
    }
    
    customer_id = demo_data["customer"]["id"]
    
    # Send user_id and user_type as query parameters
    response = requests.post(
        f"{API_URL}/causes/{cause_id}/comments?user_id={customer_id}&user_type=customer", 
        json=customer_comment_data
    )
    assert response.status_code == 200, f"Expected status code 200 for customer comment, got {response.status_code}"
    
    customer_comment = response.json()
    assert customer_comment["user_id"] == customer_id, f"Expected user_id {customer_id}, got {customer_comment['user_id']}"
    assert customer_comment["comment"] == customer_comment_data["comment"], f"Comment text doesn't match"
    assert customer_comment["is_admin_response"] == False, "Customer comment should not be marked as admin response"
    
    # Store comment ID for reply test
    customer_comment_id = customer_comment["id"]
    
    # Test comment creation as business
    business_comment_data = {
        "comment": "This is a test comment from a business",
        "parent_comment_id": None
    }
    
    business_id = demo_data["business"]["id"]
    
    # Send user_id and user_type as query parameters
    response = requests.post(
        f"{API_URL}/causes/{cause_id}/comments?user_id={business_id}&user_type=business", 
        json=business_comment_data
    )
    assert response.status_code == 200, f"Expected status code 200 for business comment, got {response.status_code}"
    
    business_comment = response.json()
    assert business_comment["user_id"] == business_id, f"Expected user_id {business_id}, got {business_comment['user_id']}"
    assert business_comment["comment"] == business_comment_data["comment"], f"Comment text doesn't match"
    
    # Check if this is an admin response (if business is the cause creator)
    is_admin_response = (demo_data["cause"]["creator_id"] == business_id and demo_data["cause"]["creator_type"] == "business")
    assert business_comment["is_admin_response"] == is_admin_response, f"Business comment admin response flag incorrect"
    
    # Test reply to customer comment
    reply_data = {
        "comment": "This is a reply to the customer comment",
        "parent_comment_id": customer_comment_id
    }
    
    # Send user_id and user_type as query parameters
    response = requests.post(
        f"{API_URL}/causes/{cause_id}/comments?user_id={business_id}&user_type=business", 
        json=reply_data
    )
    assert response.status_code == 200, f"Expected status code 200 for reply, got {response.status_code}"
    
    reply = response.json()
    assert reply["parent_comment_id"] == customer_comment_id, f"Reply parent_comment_id should match original comment id"
    
    # Verify comments were saved and properly threaded
    response = requests.get(f"{API_URL}/causes/{cause_id}/comments")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    comments_data = response.json()
    
    # Find our test comment and verify it has a reply
    found_comment = False
    found_reply = False
    
    for comment_obj in comments_data["comments"]:
        if comment_obj["comment"]["id"] == customer_comment_id:
            found_comment = True
            for reply_obj in comment_obj["replies"]:
                if reply_obj["id"] == reply["id"]:
                    found_reply = True
                    break
            break
    
    assert found_comment, "Could not find our test comment in the comments list"
    assert found_reply, "Could not find our test reply in the replies list"
    
    # Test with invalid cause ID
    response = requests.post(
        f"{API_URL}/causes/invalid-id/comments?user_id={customer_id}&user_type=customer", 
        json=customer_comment_data
    )
    assert response.status_code == 404, f"Expected status code 404 for invalid cause ID, got {response.status_code}"
    
    # Test with invalid user type
    response = requests.post(
        f"{API_URL}/causes/{cause_id}/comments?user_id={customer_id}&user_type=invalid_type", 
        json=customer_comment_data
    )
    assert response.status_code == 400, f"Expected status code 400 for invalid user type, got {response.status_code}"
    
    return True

# ===== EMOJI REACTIONS TESTS =====

def test_get_cause_reactions():
    """Test GET /api/causes/{cause_id}/reactions endpoint"""
    demo_data = get_demo_users()
    cause_id = demo_data["cause"]["id"]
    
    response = requests.get(f"{API_URL}/causes/{cause_id}/reactions")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    reactions_data = response.json()
    assert "cause_id" in reactions_data, "Reactions data missing 'cause_id' field"
    assert "reaction_counts" in reactions_data, "Reactions data missing 'reaction_counts' field"
    assert "total_reactions" in reactions_data, "Reactions data missing 'total_reactions' field"
    assert "user_reactions" in reactions_data, "Reactions data missing 'user_reactions' field"
    
    # Test with invalid cause ID
    response = requests.get(f"{API_URL}/causes/invalid-id/reactions")
    assert response.status_code == 404, f"Expected status code 404 for invalid cause ID, got {response.status_code}"
    
    return True

def test_add_cause_reaction():
    """Test POST /api/causes/{cause_id}/reactions endpoint"""
    demo_data = get_demo_users()
    cause_id = demo_data["cause"]["id"]
    
    # Test adding reaction as customer
    customer_id = demo_data["customer"]["id"]
    customer_reaction = {
        "emoji": "❤️"
    }
    
    # Send user_id and user_type as query parameters
    response = requests.post(
        f"{API_URL}/causes/{cause_id}/reactions?user_id={customer_id}&user_type=customer", 
        json=customer_reaction
    )
    assert response.status_code == 200, f"Expected status code 200 for customer reaction, got {response.status_code}"
    
    result = response.json()
    assert "message" in result, "Reaction response missing 'message' field"
    assert "emoji" in result, "Reaction response missing 'emoji' field"
    assert result["emoji"] == "❤️", f"Expected emoji ❤️, got {result['emoji']}"
    
    # Test adding reaction as business
    business_id = demo_data["business"]["id"]
    business_reaction = {
        "emoji": "👍"
    }
    
    # Send user_id and user_type as query parameters
    response = requests.post(
        f"{API_URL}/causes/{cause_id}/reactions?user_id={business_id}&user_type=business", 
        json=business_reaction
    )
    assert response.status_code == 200, f"Expected status code 200 for business reaction, got {response.status_code}"
    
    result = response.json()
    assert result["emoji"] == "👍", f"Expected emoji 👍, got {result['emoji']}"
    
    # Test updating existing reaction
    updated_customer_reaction = {
        "emoji": "🎉"
    }
    
    # Send user_id and user_type as query parameters
    response = requests.post(
        f"{API_URL}/causes/{cause_id}/reactions?user_id={customer_id}&user_type=customer", 
        json=updated_customer_reaction
    )
    assert response.status_code == 200, f"Expected status code 200 for updated reaction, got {response.status_code}"
    
    result = response.json()
    assert result["message"] == "Reaction updated successfully", f"Expected 'Reaction updated successfully', got {result['message']}"
    assert result["emoji"] == "🎉", f"Expected emoji 🎉, got {result['emoji']}"
    
    # Verify reactions were saved
    response = requests.get(f"{API_URL}/causes/{cause_id}/reactions")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    reactions_data = response.json()
    reaction_counts = reactions_data["reaction_counts"]
    user_reactions = reactions_data["user_reactions"]
    
    assert "🎉" in reaction_counts, "Emoji 🎉 not found in reaction counts"
    assert "👍" in reaction_counts, "Emoji 👍 not found in reaction counts"
    assert customer_id in user_reactions, f"Customer {customer_id} not found in user reactions"
    assert business_id in user_reactions, f"Business {business_id} not found in user reactions"
    assert user_reactions[customer_id] == "🎉", f"Expected customer reaction 🎉, got {user_reactions[customer_id]}"
    assert user_reactions[business_id] == "👍", f"Expected business reaction 👍, got {user_reactions[business_id]}"
    
    # Test with invalid cause ID
    response = requests.post(
        f"{API_URL}/causes/invalid-id/reactions?user_id={customer_id}&user_type=customer", 
        json=customer_reaction
    )
    assert response.status_code == 404, f"Expected status code 404 for invalid cause ID, got {response.status_code}"
    
    # Test with invalid user type
    response = requests.post(
        f"{API_URL}/causes/{cause_id}/reactions?user_id={customer_id}&user_type=invalid_type", 
        json=customer_reaction
    )
    assert response.status_code == 400, f"Expected status code 400 for invalid user type, got {response.status_code}"
    
    return True

def test_remove_cause_reaction():
    """Test DELETE /api/causes/{cause_id}/reactions endpoint"""
    demo_data = get_demo_users()
    cause_id = demo_data["cause"]["id"]
    customer_id = demo_data["customer"]["id"]
    
    # First, make sure the customer has a reaction
    customer_reaction = {
        "emoji": "❤️"
    }
    
    # Send user_id and user_type as query parameters
    response = requests.post(
        f"{API_URL}/causes/{cause_id}/reactions?user_id={customer_id}&user_type=customer", 
        json=customer_reaction
    )
    assert response.status_code == 200, f"Expected status code 200 for customer reaction, got {response.status_code}"
    
    # Now remove the reaction
    response = requests.delete(f"{API_URL}/causes/{cause_id}/reactions?user_id={customer_id}")
    assert response.status_code == 200, f"Expected status code 200 for delete reaction, got {response.status_code}"
    
    # Verify reaction was removed
    response = requests.get(f"{API_URL}/causes/{cause_id}/reactions")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    reactions_data = response.json()
    user_reactions = reactions_data["user_reactions"]
    
    assert customer_id not in user_reactions, f"Customer {customer_id} should not be in user reactions after deletion"
    
    # Test with invalid cause ID
    response = requests.delete(f"{API_URL}/causes/invalid-id/reactions?user_id={customer_id}")
    assert response.status_code == 404, f"Expected status code 404 for invalid cause ID, got {response.status_code}"
    
    return True

# ===== COMPLEX SCENARIO TESTS =====

def test_admin_response_workflow():
    """Test the admin response workflow for comments"""
    demo_data = get_demo_users()
    cause_id = demo_data["cause"]["id"]
    
    # Find a cause where the business is the creator
    business_id = demo_data["business"]["id"]
    business_created_cause = None
    
    response = requests.get(f"{API_URL}/causes")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    causes = response.json()
    
    for cause in causes:
        if cause["creator_id"] == business_id and cause["creator_type"] == "business":
            business_created_cause = cause
            break
    
    if not business_created_cause:
        # Create a new cause if none exists
        cause_data = {
            "name": "Test Cause for Admin Response",
            "description": "A test cause to verify admin responses",
            "category": "Environment",
            "impact_metric": "trees planted",
            "cost_per_impact": 5.0,
            "goal_amount": 1000.0,
            "creator_id": business_id,
            "creator_type": "business"
        }
        
        response = requests.post(f"{API_URL}/causes", json=cause_data)
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        business_created_cause = response.json()
    
    cause_id = business_created_cause["id"]
    
    # 1. Customer adds a comment
    customer_id = demo_data["customer"]["id"]
    customer_comment_data = {
        "comment": "I have a question about this cause. How exactly are the funds used?",
        "parent_comment_id": None
    }
    
    # Send user_id and user_type as query parameters
    response = requests.post(
        f"{API_URL}/causes/{cause_id}/comments?user_id={customer_id}&user_type=customer", 
        json=customer_comment_data
    )
    assert response.status_code == 200, f"Expected status code 200 for customer comment, got {response.status_code}"
    
    customer_comment = response.json()
    assert customer_comment["is_admin_response"] == False, "Customer comment should not be marked as admin response"
    
    # 2. Business (cause creator) responds to the comment
    business_reply_data = {
        "comment": "Thank you for your question! 100% of funds go directly to planting trees in affected areas.",
        "parent_comment_id": customer_comment["id"]
    }
    
    # Send user_id and user_type as query parameters
    response = requests.post(
        f"{API_URL}/causes/{cause_id}/comments?user_id={business_id}&user_type=business", 
        json=business_reply_data
    )
    assert response.status_code == 200, f"Expected status code 200 for business reply, got {response.status_code}"
    
    business_reply = response.json()
    assert business_reply["is_admin_response"] == True, "Business reply should be marked as admin response"
    
    # 3. Verify comments are properly threaded
    response = requests.get(f"{API_URL}/causes/{cause_id}/comments")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    comments_data = response.json()
    
    # Find our test comment and verify it has a reply
    found_comment = False
    found_reply = False
    
    for comment_obj in comments_data["comments"]:
        if comment_obj["comment"]["id"] == customer_comment["id"]:
            found_comment = True
            for reply_obj in comment_obj["replies"]:
                if reply_obj["id"] == business_reply["id"]:
                    found_reply = True
                    assert reply_obj["is_admin_response"] == True, "Admin response flag should be true in threaded view"
                    break
            break
    
    assert found_comment, "Could not find our test comment in the comments list"
    assert found_reply, "Could not find our admin response in the replies list"
    
    return True

def test_reaction_counting_workflow():
    """Test the emoji reaction counting workflow"""
    demo_data = get_demo_users()
    cause_id = demo_data["cause"]["id"]
    
    # Create a new customer for this test
    timestamp = int(time.time())
    customer_data = {
        "name": "Reaction Test User",
        "email": f"reaction.test{timestamp}@example.com",
        "phone": "555-123-4567"
    }
    
    response = requests.post(f"{API_URL}/customers", json=customer_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    new_customer_id = response.json()["id"]
    
    # Clear existing reactions for this cause
    business_id = demo_data["business"]["id"]
    customer_id = demo_data["customer"]["id"]
    
    requests.delete(f"{API_URL}/causes/{cause_id}/reactions?user_id={business_id}")
    requests.delete(f"{API_URL}/causes/{cause_id}/reactions?user_id={customer_id}")
    requests.delete(f"{API_URL}/causes/{cause_id}/reactions?user_id={new_customer_id}")
    
    # Add reactions from multiple users
    reactions = [
        {"emoji": "❤️", "user_id": business_id, "user_type": "business"},
        {"emoji": "❤️", "user_id": customer_id, "user_type": "customer"},
        {"emoji": "👍", "user_id": new_customer_id, "user_type": "customer"}
    ]
    
    for reaction in reactions:
        response = requests.post(f"{API_URL}/causes/{cause_id}/reactions", json=reaction)
        assert response.status_code == 200, f"Expected status code 200 for reaction, got {response.status_code}"
    
    # Verify reaction counts
    response = requests.get(f"{API_URL}/causes/{cause_id}/reactions")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    reactions_data = response.json()
    reaction_counts = reactions_data["reaction_counts"]
    
    assert "❤️" in reaction_counts, "Emoji ❤️ not found in reaction counts"
    assert "👍" in reaction_counts, "Emoji 👍 not found in reaction counts"
    assert reaction_counts["❤️"] == 2, f"Expected 2 ❤️ reactions, got {reaction_counts['❤️']}"
    assert reaction_counts["👍"] == 1, f"Expected 1 👍 reaction, got {reaction_counts['👍']}"
    
    # Update a reaction
    updated_reaction = {
        "emoji": "🎉",
        "user_id": customer_id,
        "user_type": "customer"
    }
    
    response = requests.post(f"{API_URL}/causes/{cause_id}/reactions", json=updated_reaction)
    assert response.status_code == 200, f"Expected status code 200 for updated reaction, got {response.status_code}"
    
    # Verify updated reaction counts
    response = requests.get(f"{API_URL}/causes/{cause_id}/reactions")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    reactions_data = response.json()
    reaction_counts = reactions_data["reaction_counts"]
    
    assert "❤️" in reaction_counts, "Emoji ❤️ not found in reaction counts"
    assert "👍" in reaction_counts, "Emoji 👍 not found in reaction counts"
    assert "🎉" in reaction_counts, "Emoji 🎉 not found in reaction counts"
    assert reaction_counts["❤️"] == 1, f"Expected 1 ❤️ reaction, got {reaction_counts['❤️']}"
    assert reaction_counts["👍"] == 1, f"Expected 1 👍 reaction, got {reaction_counts['👍']}"
    assert reaction_counts["🎉"] == 1, f"Expected 1 🎉 reaction, got {reaction_counts['🎉']}"
    
    # Remove a reaction
    response = requests.delete(f"{API_URL}/causes/{cause_id}/reactions?user_id={new_customer_id}")
    assert response.status_code == 200, f"Expected status code 200 for delete reaction, got {response.status_code}"
    
    # Verify final reaction counts
    response = requests.get(f"{API_URL}/causes/{cause_id}/reactions")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    reactions_data = response.json()
    reaction_counts = reactions_data["reaction_counts"]
    
    assert "❤️" in reaction_counts, "Emoji ❤️ not found in reaction counts"
    assert "🎉" in reaction_counts, "Emoji 🎉 not found in reaction counts"
    assert reaction_counts["❤️"] == 1, f"Expected 1 ❤️ reaction, got {reaction_counts['❤️']}"
    assert reaction_counts["🎉"] == 1, f"Expected 1 🎉 reaction, got {reaction_counts['🎉']}"
    assert "👍" not in reaction_counts or reaction_counts["👍"] == 0, "👍 reaction should be removed"
    
    return True

if __name__ == "__main__":
    # Run tests
    print("\n===== TESTING SOCIAL FEATURES =====")
    
    # Share Feature Tests
    run_test("Get Cause Share URL", test_get_cause_share_url)
    run_test("Track Cause Share", test_track_cause_share)
    
    # Comments System Tests
    run_test("Get Cause Comments", test_get_cause_comments)
    run_test("Create Cause Comment", test_create_cause_comment)
    
    # Emoji Reactions Tests
    run_test("Get Cause Reactions", test_get_cause_reactions)
    run_test("Add Cause Reaction", test_add_cause_reaction)
    run_test("Remove Cause Reaction", test_remove_cause_reaction)
    
    # Complex Scenario Tests
    run_test("Admin Response Workflow", test_admin_response_workflow)
    run_test("Reaction Counting Workflow", test_reaction_counting_workflow)
    
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