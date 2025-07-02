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

# ===== CAUSE MANAGEMENT TESTS =====

def test_get_causes():
    """Test GET /api/causes endpoint"""
    response = requests.get(f"{API_URL}/causes")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    causes = response.json()
    assert len(causes) >= 4, f"Expected at least 4 default causes, got {len(causes)}"
    
    # Verify cause structure
    required_fields = ["id", "name", "description", "category", "impact_metric", "cost_per_impact"]
    for cause in causes:
        for field in required_fields:
            assert field in cause, f"Missing required field '{field}' in cause"
    
    print(f"Found {len(causes)} causes")
    return True

def test_get_causes_with_filters():
    """Test GET /api/causes with active_only and featured_only filters"""
    # Test with active_only=true
    response = requests.get(f"{API_URL}/causes?active_only=true")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    active_causes = response.json()
    
    # Test with featured_only=true
    response = requests.get(f"{API_URL}/causes?featured_only=true")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    featured_causes = response.json()
    
    # Verify all featured causes are also active
    for cause in featured_causes:
        assert cause["active"] == True, f"Featured cause {cause['id']} is not active"
        assert cause["featured"] == True, f"Cause {cause['id']} is not featured"
    
    # Test with both filters
    response = requests.get(f"{API_URL}/causes?active_only=true&featured_only=true")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    filtered_causes = response.json()
    
    # Verify filtered causes are both active and featured
    for cause in filtered_causes:
        assert cause["active"] == True, f"Filtered cause {cause['id']} is not active"
        assert cause["featured"] == True, f"Filtered cause {cause['id']} is not featured"
    
    return True

def test_create_cause():
    """Test POST /api/causes endpoint"""
    cause_data = {
        "name": "Renewable Energy Projects",
        "description": "Supporting community solar and wind energy initiatives",
        "category": "Environment",
        "image_url": "https://images.unsplash.com/photo-1508514177221-188b1cf16e9d",
        "impact_metric": "kWh of clean energy produced",
        "cost_per_impact": 0.15,
        "goal_amount": 30000.0
    }
    
    response = requests.post(f"{API_URL}/causes", json=cause_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    cause = response.json()
    for key, value in cause_data.items():
        assert cause[key] == value, f"Expected {key} to be {value}, got {cause[key]}"
    
    assert "id" in cause, "Cause response missing 'id' field"
    assert "active" in cause, "Cause response missing 'active' field"
    assert "featured" in cause, "Cause response missing 'featured' field"
    assert "total_raised" in cause, "Cause response missing 'total_raised' field"
    assert "total_impact_units" in cause, "Cause response missing 'total_impact_units' field"
    
    # Store cause ID for later tests
    global test_new_cause_id
    test_new_cause_id = cause["id"]
    print(f"Created cause with ID: {test_new_cause_id}")
    
    return True

def test_get_specific_cause():
    """Test GET /api/causes/{id} endpoint"""
    # First get all causes
    response = requests.get(f"{API_URL}/causes")
    causes = response.json()
    
    # Test with the first cause
    cause_id = causes[0]["id"]
    response = requests.get(f"{API_URL}/causes/{cause_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    cause = response.json()
    assert cause["id"] == cause_id, f"Expected cause id {cause_id}, got {cause['id']}"
    
    # Test with invalid ID
    response = requests.get(f"{API_URL}/causes/invalid-id")
    assert response.status_code == 404, f"Expected status code 404, got {response.status_code}"
    
    return True

# ===== BUSINESS MANAGEMENT TESTS =====

def test_create_business():
    """Test POST /api/businesses endpoint"""
    business_data = {
        "name": "Green Earth Cafe",
        "description": "Eco-friendly cafe with sustainable practices",
        "industry": "Food & Beverage",
        "email": "contact@greenearthcafe.com",
        "phone": "555-123-4567",
        "website": "https://greenearthcafe.com"
    }
    
    response = requests.post(f"{API_URL}/businesses", json=business_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    business = response.json()
    for key, value in business_data.items():
        assert business[key] == value, f"Expected {key} to be {value}, got {business[key]}"
    
    assert "id" in business, "Business response missing 'id' field"
    assert "impact_allocations" in business, "Business response missing 'impact_allocations' field"
    assert "total_sales" in business, "Business response missing 'total_sales' field"
    assert "total_impact" in business, "Business response missing 'total_impact' field"
    assert "api_key" in business, "Business response missing 'api_key' field"
    
    # Store business ID and API key for later tests
    global test_business_id, test_business_api_key
    test_business_id = business["id"]
    test_business_api_key = business["api_key"]
    print(f"Created business with ID: {test_business_id}")
    print(f"Business API key: {test_business_api_key}")
    
    return True

def test_get_businesses():
    """Test GET /api/businesses endpoint"""
    response = requests.get(f"{API_URL}/businesses")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    businesses = response.json()
    assert len(businesses) > 0, "Expected at least one business"
    
    # Verify our test business is in the list
    found = False
    for business in businesses:
        if business["id"] == test_business_id:
            found = True
            break
    
    assert found, f"Could not find our test business (ID: {test_business_id}) in the list"
    
    return True

def test_get_specific_business():
    """Test GET /api/businesses/{id} endpoint"""
    response = requests.get(f"{API_URL}/businesses/{test_business_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    business = response.json()
    assert business["id"] == test_business_id, f"Expected business id {test_business_id}, got {business['id']}"
    
    # Test with invalid ID
    response = requests.get(f"{API_URL}/businesses/invalid-id")
    assert response.status_code == 404, f"Expected status code 404, got {response.status_code}"
    
    return True

def test_update_impact_allocation():
    """Test PUT /api/businesses/{id}/impact-allocation endpoint"""
    # First get all causes
    response = requests.get(f"{API_URL}/causes")
    causes = response.json()
    
    # Create impact allocations (30% Education, 25% Clean Water, 20% Forest, 15% Food Security)
    allocations = [
        {"cause_id": causes[0]["id"], "percentage": 30},  # Education
        {"cause_id": causes[1]["id"], "percentage": 25},  # Clean Water
        {"cause_id": causes[2]["id"], "percentage": 20},  # Forest
        {"cause_id": causes[3]["id"], "percentage": 15},  # Food Security
    ]
    
    response = requests.put(f"{API_URL}/businesses/{test_business_id}/impact-allocation", json=allocations)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    result = response.json()
    assert result["total_percentage"] == 90, f"Expected total percentage 90, got {result['total_percentage']}"
    
    # Verify allocations were saved
    response = requests.get(f"{API_URL}/businesses/{test_business_id}")
    business = response.json()
    
    # Check each allocation
    for allocation in allocations:
        cause_id = allocation["cause_id"]
        percentage = allocation["percentage"]
        assert cause_id in business["impact_allocations"], f"Cause {cause_id} not found in impact allocations"
        assert business["impact_allocations"][cause_id] == percentage, f"Expected percentage {percentage}, got {business['impact_allocations'][cause_id]}"
    
    # Test validation: total percentage > 100%
    invalid_allocations = [
        {"cause_id": causes[0]["id"], "percentage": 60},
        {"cause_id": causes[1]["id"], "percentage": 50},
    ]
    
    response = requests.put(f"{API_URL}/businesses/{test_business_id}/impact-allocation", json=invalid_allocations)
    assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
    
    # Store cause IDs for later tests
    global test_cause_ids
    test_cause_ids = [cause["id"] for cause in causes[:4]]
    
    return True

# ===== TRANSACTION TESTS =====

def test_create_transaction():
    """Test POST /api/transactions endpoint"""
    transaction_data = {
        "business_id": test_business_id,
        "amount": 100.00,
        "customer_name": "John Doe"
    }
    
    response = requests.post(f"{API_URL}/transactions", json=transaction_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    transaction = response.json()
    assert transaction["business_id"] == test_business_id, f"Expected business_id {test_business_id}, got {transaction['business_id']}"
    assert transaction["amount"] == 100.00, f"Expected amount 100.00, got {transaction['amount']}"
    assert transaction["customer_name"] == "John Doe", f"Expected customer_name 'John Doe', got {transaction['customer_name']}"
    
    # Verify impact calculations
    assert "impact_breakdown" in transaction, "Transaction missing impact_breakdown"
    assert "total_impact_amount" in transaction, "Transaction missing total_impact_amount"
    
    # Expected impact: 30% + 25% + 20% + 15% = 90% of $100 = $90
    assert transaction["total_impact_amount"] == 90.0, f"Expected total_impact_amount 90.0, got {transaction['total_impact_amount']}"
    
    # Verify impact breakdown for each cause
    expected_impacts = {
        test_cause_ids[0]: {"percentage": 30, "amount": 30.0},  # Education
        test_cause_ids[1]: {"percentage": 25, "amount": 25.0},  # Clean Water
        test_cause_ids[2]: {"percentage": 20, "amount": 20.0},  # Forest
        test_cause_ids[3]: {"percentage": 15, "amount": 15.0},  # Food Security
    }
    
    for cause_id, expected in expected_impacts.items():
        assert cause_id in transaction["impact_breakdown"], f"Cause {cause_id} not found in impact breakdown"
        actual_amount = transaction["impact_breakdown"][cause_id]["amount"]
        assert actual_amount == expected["amount"], f"Expected impact amount {expected['amount']}, got {actual_amount}"
    
    # Store transaction ID for later tests
    global test_transaction_id
    test_transaction_id = transaction["id"]
    
    # Create a second transaction
    transaction_data = {
        "business_id": test_business_id,
        "amount": 200.00,
        "customer_name": "Jane Smith"
    }
    
    response = requests.post(f"{API_URL}/transactions", json=transaction_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # Create a third transaction
    transaction_data = {
        "business_id": test_business_id,
        "amount": 150.00,
        "customer_name": "Alex Johnson"
    }
    
    response = requests.post(f"{API_URL}/transactions", json=transaction_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    return True

def test_get_transactions():
    """Test GET /api/transactions endpoint"""
    # Get all transactions
    response = requests.get(f"{API_URL}/transactions")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    transactions = response.json()
    assert len(transactions) >= 3, f"Expected at least 3 transactions, got {len(transactions)}"
    
    # Get transactions for specific business
    response = requests.get(f"{API_URL}/transactions?business_id={test_business_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    business_transactions = response.json()
    assert len(business_transactions) >= 3, f"Expected at least 3 transactions for business, got {len(business_transactions)}"
    
    # Verify all transactions belong to our test business
    for transaction in business_transactions:
        assert transaction["business_id"] == test_business_id, f"Expected business_id {test_business_id}, got {transaction['business_id']}"
    
    return True

# ===== DASHBOARD TESTS =====

def test_impact_dashboard():
    """Test GET /api/impact/dashboard/{business_id} endpoint"""
    response = requests.get(f"{API_URL}/impact/dashboard/{test_business_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    dashboard = response.json()
    
    # Verify dashboard structure
    assert "business" in dashboard, "Dashboard missing business data"
    assert "recent_transactions" in dashboard, "Dashboard missing recent_transactions"
    assert "cause_breakdown" in dashboard, "Dashboard missing cause_breakdown"
    assert "total_sales" in dashboard, "Dashboard missing total_sales"
    assert "total_impact" in dashboard, "Dashboard missing total_impact"
    assert "impact_percentage" in dashboard, "Dashboard missing impact_percentage"
    
    # Expected totals: $100 + $200 + $150 = $450 in sales, 90% of that in impact = $405
    assert dashboard["total_sales"] == 450.0, f"Expected total_sales 450.0, got {dashboard['total_sales']}"
    assert dashboard["total_impact"] == 405.0, f"Expected total_impact 405.0, got {dashboard['total_impact']}"
    assert dashboard["impact_percentage"] == 90.0, f"Expected impact_percentage 90.0, got {dashboard['impact_percentage']}"
    
    # Verify cause breakdown
    for cause_id in test_cause_ids:
        assert cause_id in dashboard["cause_breakdown"], f"Cause {cause_id} not found in dashboard cause_breakdown"
    
    # Verify recent transactions
    assert len(dashboard["recent_transactions"]) >= 3, f"Expected at least 3 recent transactions, got {len(dashboard['recent_transactions'])}"
    
    return True

def test_public_impact():
    """Test GET /api/impact/public/{business_id} endpoint"""
    response = requests.get(f"{API_URL}/impact/public/{test_business_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    public_impact = response.json()
    
    # Verify public impact structure
    assert "business_name" in public_impact, "Public impact missing business_name"
    assert "business_description" in public_impact, "Public impact missing business_description"
    assert "total_sales" in public_impact, "Public impact missing total_sales"
    assert "total_impact" in public_impact, "Public impact missing total_impact"
    assert "cause_breakdown" in public_impact, "Public impact missing cause_breakdown"
    assert "impact_message" in public_impact, "Public impact missing impact_message"
    
    # Expected totals: $100 + $200 + $150 = $450 in sales, 90% of that in impact = $405
    assert public_impact["total_sales"] == 450.0, f"Expected total_sales 450.0, got {public_impact['total_sales']}"
    assert public_impact["total_impact"] == 405.0, f"Expected total_impact 405.0, got {public_impact['total_impact']}"
    
    # Verify cause breakdown
    for cause_id in test_cause_ids:
        assert cause_id in public_impact["cause_breakdown"], f"Cause {cause_id} not found in public impact cause_breakdown"
        
        # Verify impact units calculation
        cause_data = public_impact["cause_breakdown"][cause_id]
        assert "impact_units" in cause_data, f"Cause {cause_id} missing impact_units"
        
        # Get the original cause to verify calculations
        cause_response = requests.get(f"{API_URL}/causes/{cause_id}")
        cause = cause_response.json()
        
        # Calculate expected impact units
        percentage = None
        if cause_id == test_cause_ids[0]:
            percentage = 30
        elif cause_id == test_cause_ids[1]:
            percentage = 25
        elif cause_id == test_cause_ids[2]:
            percentage = 20
        elif cause_id == test_cause_ids[3]:
            percentage = 15
        
        expected_contribution = (450.0 * percentage) / 100
        expected_impact_units = expected_contribution / cause["cost_per_impact"]
        
        assert cause_data["total_contribution"] == expected_contribution, f"Expected contribution {expected_contribution}, got {cause_data['total_contribution']}"
        assert abs(cause_data["impact_units"] - expected_impact_units) < 0.01, f"Expected impact units {expected_impact_units}, got {cause_data['impact_units']}"
    
    return True

# ===== CUSTOMER MANAGEMENT TESTS =====

def test_create_customer():
    """Test POST /api/customers endpoint"""
    # Use a timestamp to ensure unique email
    timestamp = int(time.time())
    customer_data = {
        "name": "Emily Johnson",
        "email": f"emily.johnson{timestamp}@example.com",
        "phone": "555-789-1234"
    }
    
    response = requests.post(f"{API_URL}/customers", json=customer_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    customer = response.json()
    # Check name and phone, but not email since we modified it
    assert customer["name"] == customer_data["name"], f"Expected name to be {customer_data['name']}, got {customer['name']}"
    assert customer["phone"] == customer_data["phone"], f"Expected phone to be {customer_data['phone']}, got {customer['phone']}"
    
    assert "id" in customer, "Customer response missing 'id' field"
    assert "total_contributions" in customer, "Customer response missing 'total_contributions' field"
    assert "contribution_count" in customer, "Customer response missing 'contribution_count' field"
    assert "badges" in customer, "Customer response missing 'badges' field"
    
    # Store customer ID for later tests
    global test_customer_id
    test_customer_id = customer["id"]
    print(f"Created customer with ID: {test_customer_id}")
    
    # Create a second customer for leaderboard testing
    customer_data = {
        "name": "Michael Smith",
        "email": f"michael.smith{timestamp}@example.com",
        "phone": "555-456-7890"
    }
    
    response = requests.post(f"{API_URL}/customers", json=customer_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    global test_customer_id2
    test_customer_id2 = response.json()["id"]
    
    return True

def test_get_customers():
    """Test GET /api/customers endpoint"""
    response = requests.get(f"{API_URL}/customers")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    customers = response.json()
    assert len(customers) >= 2, f"Expected at least 2 customers, got {len(customers)}"
    
    # Verify our test customers are in the list
    found_customer1 = False
    found_customer2 = False
    for customer in customers:
        if customer["id"] == test_customer_id:
            found_customer1 = True
        elif customer["id"] == test_customer_id2:
            found_customer2 = True
    
    assert found_customer1, f"Could not find our first test customer (ID: {test_customer_id}) in the list"
    assert found_customer2, f"Could not find our second test customer (ID: {test_customer_id2}) in the list"
    
    return True

def test_get_specific_customer():
    """Test GET /api/customers/{id} endpoint"""
    response = requests.get(f"{API_URL}/customers/{test_customer_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    customer = response.json()
    assert customer["id"] == test_customer_id, f"Expected customer id {test_customer_id}, got {customer['id']}"
    
    # Test with invalid ID
    response = requests.get(f"{API_URL}/customers/invalid-id")
    assert response.status_code == 404, f"Expected status code 404, got {response.status_code}"
    
    return True

# ===== DIRECT CONTRIBUTION TESTS =====

def test_create_direct_contribution():
    """Test POST /api/contributions endpoint"""
    # First get all causes
    response = requests.get(f"{API_URL}/causes")
    causes = response.json()
    
    contribution_data = {
        "customer_id": test_customer_id,
        "cause_id": causes[0]["id"],  # Education
        "amount": 100.00,
        "message": "Supporting education for all!",
        "anonymous": False
    }
    
    response = requests.post(f"{API_URL}/contributions", json=contribution_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    contribution = response.json()
    for key, value in contribution_data.items():
        assert contribution[key] == value, f"Expected {key} to be {value}, got {contribution[key]}"
    
    assert "id" in contribution, "Contribution response missing 'id' field"
    assert "impact_units" in contribution, "Contribution response missing 'impact_units' field"
    assert "timestamp" in contribution, "Contribution response missing 'timestamp' field"
    
    # Calculate expected impact units
    cause = causes[0]
    expected_impact_units = contribution_data["amount"] / cause["cost_per_impact"]
    assert abs(contribution["impact_units"] - expected_impact_units) < 0.01, f"Expected impact units {expected_impact_units}, got {contribution['impact_units']}"
    
    # Store contribution ID for later tests
    global test_contribution_id
    test_contribution_id = contribution["id"]
    
    # Create more contributions for badge testing and leaderboard
    # Second contribution for first customer
    contribution_data = {
        "customer_id": test_customer_id,
        "cause_id": causes[1]["id"],  # Clean Water
        "amount": 200.00,
        "message": "Clean water for communities!",
        "anonymous": False
    }
    
    response = requests.post(f"{API_URL}/contributions", json=contribution_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # Third contribution for first customer (should trigger generous_giver badge)
    contribution_data = {
        "customer_id": test_customer_id,
        "cause_id": causes[2]["id"],  # Forest
        "amount": 250.00,
        "message": "Planting trees for the future!",
        "anonymous": False
    }
    
    response = requests.post(f"{API_URL}/contributions", json=contribution_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # Contribution for second customer
    contribution_data = {
        "customer_id": test_customer_id2,
        "cause_id": causes[0]["id"],  # Education
        "amount": 150.00,
        "message": "Education matters!",
        "anonymous": False
    }
    
    response = requests.post(f"{API_URL}/contributions", json=contribution_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    return True

def test_get_contributions():
    """Test GET /api/contributions endpoint with filters"""
    # Get all contributions
    response = requests.get(f"{API_URL}/contributions")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    contributions = response.json()
    assert len(contributions) >= 4, f"Expected at least 4 contributions, got {len(contributions)}"
    
    # Get contributions for specific customer
    response = requests.get(f"{API_URL}/contributions?customer_id={test_customer_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    customer_contributions = response.json()
    assert len(customer_contributions) >= 3, f"Expected at least 3 contributions for customer, got {len(customer_contributions)}"
    
    # Verify all contributions belong to our test customer
    for contribution in customer_contributions:
        assert contribution["customer_id"] == test_customer_id, f"Expected customer_id {test_customer_id}, got {contribution['customer_id']}"
    
    # Get contributions for specific cause
    response = requests.get(f"{API_URL}/causes")
    causes = response.json()
    cause_id = causes[0]["id"]  # Education
    
    response = requests.get(f"{API_URL}/contributions?cause_id={cause_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    cause_contributions = response.json()
    assert len(cause_contributions) >= 2, f"Expected at least 2 contributions for cause, got {len(cause_contributions)}"
    
    # Verify all contributions are for the specified cause
    for contribution in cause_contributions:
        assert contribution["cause_id"] == cause_id, f"Expected cause_id {cause_id}, got {contribution['cause_id']}"
    
    return True

# ===== LEADERBOARD TESTS =====

def test_business_leaderboard():
    """Test GET /api/leaderboards/businesses endpoint"""
    # Test default leaderboard (total_impact)
    response = requests.get(f"{API_URL}/leaderboards/businesses")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    leaderboard = response.json()
    assert "metric" in leaderboard, "Leaderboard response missing 'metric' field"
    assert "leaderboard" in leaderboard, "Leaderboard response missing 'leaderboard' field"
    assert leaderboard["metric"] == "total_impact", f"Expected metric 'total_impact', got {leaderboard['metric']}"
    
    # Verify leaderboard entries
    entries = leaderboard["leaderboard"]
    assert len(entries) > 0, "Expected at least one entry in the leaderboard"
    
    # Verify our test business is in the leaderboard
    found = False
    for entry in entries:
        if entry["business"]["id"] == test_business_id:
            found = True
            assert entry["metric_value"] == 405.0, f"Expected metric_value 405.0, got {entry['metric_value']}"
            break
    
    assert found, f"Could not find our test business (ID: {test_business_id}) in the leaderboard"
    
    # Test with different metrics
    for metric in ["total_sales", "transaction_count"]:
        response = requests.get(f"{API_URL}/leaderboards/businesses?metric={metric}")
        assert response.status_code == 200, f"Expected status code 200 for metric {metric}, got {response.status_code}"
        
        leaderboard = response.json()
        assert leaderboard["metric"] == metric, f"Expected metric '{metric}', got {leaderboard['metric']}"
    
    # Test with invalid metric
    response = requests.get(f"{API_URL}/leaderboards/businesses?metric=invalid_metric")
    assert response.status_code == 400, f"Expected status code 400 for invalid metric, got {response.status_code}"
    
    return True

def test_customer_leaderboard():
    """Test GET /api/leaderboards/customers endpoint"""
    # Test default leaderboard (total_contributions)
    response = requests.get(f"{API_URL}/leaderboards/customers")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    leaderboard = response.json()
    assert "metric" in leaderboard, "Leaderboard response missing 'metric' field"
    assert "leaderboard" in leaderboard, "Leaderboard response missing 'leaderboard' field"
    assert leaderboard["metric"] == "total_contributions", f"Expected metric 'total_contributions', got {leaderboard['metric']}"
    
    # Verify leaderboard entries
    entries = leaderboard["leaderboard"]
    assert len(entries) >= 2, f"Expected at least 2 entries in the leaderboard, got {len(entries)}"
    
    # Verify our test customers are in the leaderboard
    found_customer1 = False
    found_customer2 = False
    for entry in entries:
        if entry["customer"]["id"] == test_customer_id:
            found_customer1 = True
            assert entry["metric_value"] == 550.0, f"Expected metric_value 550.0, got {entry['metric_value']}"
        elif entry["customer"]["id"] == test_customer_id2:
            found_customer2 = True
            assert entry["metric_value"] == 150.0, f"Expected metric_value 150.0, got {entry['metric_value']}"
    
    assert found_customer1, f"Could not find our first test customer (ID: {test_customer_id}) in the leaderboard"
    assert found_customer2, f"Could not find our second test customer (ID: {test_customer_id2}) in the leaderboard"
    
    # Test with different metric
    response = requests.get(f"{API_URL}/leaderboards/customers?metric=contribution_count")
    assert response.status_code == 200, f"Expected status code 200 for metric contribution_count, got {response.status_code}"
    
    leaderboard = response.json()
    assert leaderboard["metric"] == "contribution_count", f"Expected metric 'contribution_count', got {leaderboard['metric']}"
    
    # Test with invalid metric
    response = requests.get(f"{API_URL}/leaderboards/customers?metric=invalid_metric")
    assert response.status_code == 400, f"Expected status code 400 for invalid metric, got {response.status_code}"
    
    return True

# ===== BADGE TESTS =====

def test_get_all_badges():
    """Test GET /api/badges endpoint"""
    response = requests.get(f"{API_URL}/badges")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    badges = response.json()
    assert len(badges) >= 7, f"Expected at least 7 badges, got {len(badges)}"
    
    # Verify badge structure
    required_fields = ["id", "name", "description", "icon", "criteria", "rarity"]
    for badge in badges:
        for field in required_fields:
            assert field in badge, f"Missing required field '{field}' in badge"
    
    # Verify specific badges exist
    badge_ids = [badge["id"] for badge in badges]
    expected_badges = ["first_contribution", "generous_giver", "impact_champion", 
                      "multi_cause_supporter", "business_pioneer", "impact_leader", 
                      "consistent_contributor"]
    
    for badge_id in expected_badges:
        assert badge_id in badge_ids, f"Expected badge '{badge_id}' not found"
    
    return True

def test_get_user_badges():
    """Test GET /api/badges/{user_type}/{user_id} endpoint"""
    # Test customer badges
    response = requests.get(f"{API_URL}/badges/customer/{test_customer_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    badge_data = response.json()
    assert "user_id" in badge_data, "Badge response missing 'user_id' field"
    assert "user_type" in badge_data, "Badge response missing 'user_type' field"
    assert "badges" in badge_data, "Badge response missing 'badges' field"
    
    assert badge_data["user_id"] == test_customer_id, f"Expected user_id {test_customer_id}, got {badge_data['user_id']}"
    assert badge_data["user_type"] == "customer", f"Expected user_type 'customer', got {badge_data['user_type']}"
    
    # Verify customer has earned expected badges
    customer_badges = [badge["id"] for badge in badge_data["badges"]]
    assert "first_contribution" in customer_badges, "Customer should have 'first_contribution' badge"
    assert "generous_giver" in customer_badges, "Customer should have 'generous_giver' badge (contributed $550)"
    assert "multi_cause_supporter" in customer_badges, "Customer should have 'multi_cause_supporter' badge (supported 3 causes)"
    
    # Test business badges
    response = requests.get(f"{API_URL}/badges/business/{test_business_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    badge_data = response.json()
    assert badge_data["user_id"] == test_business_id, f"Expected user_id {test_business_id}, got {badge_data['user_id']}"
    assert badge_data["user_type"] == "business", f"Expected user_type 'business', got {badge_data['user_type']}"
    
    # Test with invalid user type
    response = requests.get(f"{API_URL}/badges/invalid_type/{test_customer_id}")
    assert response.status_code == 400, f"Expected status code 400 for invalid user type, got {response.status_code}"
    
    # Test with invalid user ID
    response = requests.get(f"{API_URL}/badges/customer/invalid-id")
    assert response.status_code == 404, f"Expected status code 404 for invalid user ID, got {response.status_code}"
    
    return True

# ===== ADMIN DASHBOARD TESTS =====

def test_admin_dashboard():
    """Test GET /api/admin/dashboard endpoint"""
    response = requests.get(f"{API_URL}/admin/dashboard")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    dashboard = response.json()
    
    # Verify dashboard structure
    assert "statistics" in dashboard, "Admin dashboard missing 'statistics' field"
    assert "recent_activity" in dashboard, "Admin dashboard missing 'recent_activity' field"
    assert "top_causes" in dashboard, "Admin dashboard missing 'top_causes' field"
    
    # Verify statistics
    stats = dashboard["statistics"]
    required_stats = ["total_businesses", "total_customers", "total_causes", 
                     "total_transactions", "total_contributions", "total_platform_impact",
                     "business_impact", "customer_contributions"]
    
    for stat in required_stats:
        assert stat in stats, f"Admin dashboard statistics missing '{stat}' field"
    
    # Verify recent activity
    activity = dashboard["recent_activity"]
    assert "transactions" in activity, "Admin dashboard recent activity missing 'transactions' field"
    assert "contributions" in activity, "Admin dashboard recent activity missing 'contributions' field"
    
    # Verify top causes
    top_causes = dashboard["top_causes"]
    assert len(top_causes) > 0, "Expected at least one top cause"
    
    return True

def test_admin_businesses():
    """Test GET /api/admin/businesses endpoint"""
    response = requests.get(f"{API_URL}/admin/businesses")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    businesses = response.json()
    assert len(businesses) > 0, "Expected at least one business"
    
    # Verify our test business is in the list
    found = False
    for business in businesses:
        if business["id"] == test_business_id:
            found = True
            break
    
    assert found, f"Could not find our test business (ID: {test_business_id}) in the admin businesses list"
    
    return True

def test_admin_verify_business():
    """Test PUT /api/admin/businesses/{id}/verify endpoint"""
    response = requests.put(f"{API_URL}/admin/businesses/{test_business_id}/verify")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    result = response.json()
    assert "message" in result, "Verify business response missing 'message' field"
    
    # Verify business was actually verified
    response = requests.get(f"{API_URL}/businesses/{test_business_id}")
    business = response.json()
    assert business["verified"] == True, "Business should be verified after admin verification"
    
    # Test with invalid business ID
    response = requests.put(f"{API_URL}/admin/businesses/invalid-id/verify")
    assert response.status_code == 404, f"Expected status code 404 for invalid business ID, got {response.status_code}"
    
    return True

def test_admin_causes():
    """Test GET /api/admin/causes endpoint"""
    response = requests.get(f"{API_URL}/admin/causes")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    causes = response.json()
    assert len(causes) > 0, "Expected at least one cause"
    
    # Verify our test cause is in the list
    found = False
    for cause in causes:
        if cause["id"] == test_new_cause_id:
            found = True
            break
    
    assert found, f"Could not find our test cause (ID: {test_new_cause_id}) in the admin causes list"
    
    return True

# ===== EXTERNAL API TESTS =====

def test_external_transaction():
    """Test POST /api/external/transaction endpoint with API key auth"""
    transaction_data = {
        "amount": 75.50,
        "customer_name": "External Customer"
    }
    
    # Test without API key
    response = requests.post(f"{API_URL}/external/transaction", json=transaction_data)
    assert response.status_code == 401, f"Expected status code 401 without API key, got {response.status_code}"
    
    # Test with invalid API key
    headers = {"Authorization": "Bearer invalid_api_key"}
    response = requests.post(f"{API_URL}/external/transaction", json=transaction_data, headers=headers)
    assert response.status_code == 401, f"Expected status code 401 with invalid API key, got {response.status_code}"
    
    # Test with valid API key
    headers = {"Authorization": f"Bearer {test_business_api_key}"}
    response = requests.post(f"{API_URL}/external/transaction", json=transaction_data, headers=headers)
    assert response.status_code == 200, f"Expected status code 200 with valid API key, got {response.status_code}"
    
    transaction = response.json()
    assert transaction["business_id"] == test_business_id, f"Expected business_id {test_business_id}, got {transaction['business_id']}"
    assert transaction["amount"] == 75.50, f"Expected amount 75.50, got {transaction['amount']}"
    assert transaction["customer_name"] == "External Customer", f"Expected customer_name 'External Customer', got {transaction['customer_name']}"
    
    return True

def test_external_business_impact():
    """Test GET /api/external/business/impact endpoint with API key auth"""
    # Test without API key
    response = requests.get(f"{API_URL}/external/business/impact")
    assert response.status_code == 401, f"Expected status code 401 without API key, got {response.status_code}"
    
    # Test with invalid API key
    headers = {"Authorization": "Bearer invalid_api_key"}
    response = requests.get(f"{API_URL}/external/business/impact", headers=headers)
    assert response.status_code == 401, f"Expected status code 401 with invalid API key, got {response.status_code}"
    
    # Test with valid API key
    headers = {"Authorization": f"Bearer {test_business_api_key}"}
    response = requests.get(f"{API_URL}/external/business/impact", headers=headers)
    assert response.status_code == 200, f"Expected status code 200 with valid API key, got {response.status_code}"
    
    impact_data = response.json()
    assert "business" in impact_data, "External impact response missing 'business' field"
    assert "recent_transactions" in impact_data, "External impact response missing 'recent_transactions' field"
    assert "cause_breakdown" in impact_data, "External impact response missing 'cause_breakdown' field"
    assert "total_sales" in impact_data, "External impact response missing 'total_sales' field"
    assert "total_impact" in impact_data, "External impact response missing 'total_impact' field"
    
    assert impact_data["business"]["id"] == test_business_id, f"Expected business id {test_business_id}, got {impact_data['business']['id']}"
    
    return True

def test_external_causes():
    """Test GET /api/external/causes endpoint (public API)"""
    response = requests.get(f"{API_URL}/external/causes")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    causes = response.json()
    assert len(causes) > 0, "Expected at least one cause"
    
    # Verify all causes are active
    for cause in causes:
        assert cause["active"] == True, f"Cause {cause['id']} is not active"
    
    return True

# ===== COMPLEX SCENARIO TESTS =====

def test_customer_contribution_badge_flow():
    """Test the flow: Create customer → Make multiple contributions → Verify badge awarding"""
    # 1. Create a new customer with unique email
    timestamp = int(time.time())
    customer_data = {
        "name": "Sarah Williams",
        "email": f"sarah.williams{timestamp}@example.com",
        "phone": "555-222-3333"
    }
    
    response = requests.post(f"{API_URL}/customers", json=customer_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    customer = response.json()
    customer_id = customer["id"]
    
    # 2. Get all causes
    response = requests.get(f"{API_URL}/causes")
    causes = response.json()
    
    # 3. Make first contribution (should earn first_contribution badge)
    contribution_data = {
        "customer_id": customer_id,
        "cause_id": causes[0]["id"],  # Education
        "amount": 50.00,
        "message": "First contribution!",
        "anonymous": False
    }
    
    response = requests.post(f"{API_URL}/contributions", json=contribution_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # 4. Check badges - should have first_contribution
    response = requests.get(f"{API_URL}/badges/customer/{customer_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    badge_data = response.json()
    customer_badges = [badge["id"] for badge in badge_data["badges"]]
    assert "first_contribution" in customer_badges, "Customer should have 'first_contribution' badge after first contribution"
    
    # 5. Make more contributions to different causes (should earn multi_cause_supporter)
    for i, cause in enumerate(causes[1:3]):  # Clean Water and Forest
        contribution_data = {
            "customer_id": customer_id,
            "cause_id": cause["id"],
            "amount": 100.00 + (i * 50),  # 100, 150
            "message": f"Supporting {cause['name']}!",
            "anonymous": False
        }
        
        response = requests.post(f"{API_URL}/contributions", json=contribution_data)
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # 6. Make one more large contribution (should earn generous_giver)
    contribution_data = {
        "customer_id": customer_id,
        "cause_id": causes[0]["id"],  # Education again
        "amount": 250.00,
        "message": "Big contribution!",
        "anonymous": False
    }
    
    response = requests.post(f"{API_URL}/contributions", json=contribution_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # 7. Check badges - should have first_contribution, multi_cause_supporter, and generous_giver
    response = requests.get(f"{API_URL}/badges/customer/{customer_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    badge_data = response.json()
    customer_badges = [badge["id"] for badge in badge_data["badges"]]
    assert "first_contribution" in customer_badges, "Customer should have 'first_contribution' badge"
    assert "multi_cause_supporter" in customer_badges, "Customer should have 'multi_cause_supporter' badge (supported 3 causes)"
    assert "generous_giver" in customer_badges, "Customer should have 'generous_giver' badge (contributed $550 total)"
    
    # 8. Verify customer appears in leaderboard
    response = requests.get(f"{API_URL}/leaderboards/customers")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    leaderboard = response.json()
    entries = leaderboard["leaderboard"]
    
    found = False
    for entry in entries:
        if entry["customer"]["id"] == customer_id:
            found = True
            assert entry["metric_value"] == 550.0, f"Expected metric_value 550.0, got {entry['metric_value']}"
            assert len(entry["badges"]) >= 3, f"Expected at least 3 badges, got {len(entry['badges'])}"
            break
    
    assert found, f"Could not find our test customer (ID: {customer_id}) in the leaderboard"
    
    return True

def test_admin_verification_workflow():
    """Test the admin verification workflow for businesses"""
    # 1. Create a new business
    business_data = {
        "name": "Sustainable Clothing Co.",
        "description": "Eco-friendly clothing made from recycled materials",
        "industry": "Retail",
        "email": "info@sustainableclothing.com",
        "phone": "555-111-2222",
        "website": "https://sustainableclothing.com"
    }
    
    response = requests.post(f"{API_URL}/businesses", json=business_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    business = response.json()
    business_id = business["id"]
    
    # 2. Verify business is not verified by default
    assert business["verified"] == False, "Business should not be verified by default"
    
    # 3. Check business in admin dashboard
    response = requests.get(f"{API_URL}/admin/businesses")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    businesses = response.json()
    found = False
    for b in businesses:
        if b["id"] == business_id:
            found = True
            assert b["verified"] == False, "Business should not be verified in admin dashboard"
            break
    
    assert found, f"Could not find our test business (ID: {business_id}) in the admin businesses list"
    
    # 4. Verify the business through admin API
    response = requests.put(f"{API_URL}/admin/businesses/{business_id}/verify")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # 5. Check business is now verified
    response = requests.get(f"{API_URL}/businesses/{business_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    business = response.json()
    assert business["verified"] == True, "Business should be verified after admin verification"
    
    # 6. Check public impact page shows verified status
    response = requests.get(f"{API_URL}/impact/public/{business_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    public_impact = response.json()
    assert public_impact["verified"] == True, "Public impact page should show business as verified"
    
    return True

def test_comprehensive_flow():
    """Test the entire business flow from creation to impact tracking"""
    # 1. Create a new business
    business_data = {
        "name": "Mountain View Bakery",
        "description": "Artisanal bakery with locally sourced ingredients",
        "industry": "Food & Beverage",
        "email": "info@mountainviewbakery.com",
        "phone": "555-987-6543",
        "website": "https://mountainviewbakery.com"
    }
    
    response = requests.post(f"{API_URL}/businesses", json=business_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    business = response.json()
    business_id = business["id"]
    
    # 2. Get all causes
    response = requests.get(f"{API_URL}/causes")
    causes = response.json()
    
    # 3. Set impact allocations (40% Education, 40% Forest, 20% Food Security)
    allocations = [
        {"cause_id": causes[0]["id"], "percentage": 40},  # Education
        {"cause_id": causes[2]["id"], "percentage": 40},  # Forest
        {"cause_id": causes[3]["id"], "percentage": 20},  # Food Security
    ]
    
    response = requests.put(f"{API_URL}/businesses/{business_id}/impact-allocation", json=allocations)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # 4. Create multiple transactions
    transactions = [
        {"amount": 75.50, "customer_name": "Sarah Wilson"},
        {"amount": 120.25, "customer_name": "Michael Brown"},
        {"amount": 45.75, "customer_name": "Emily Davis"}
    ]
    
    for transaction_data in transactions:
        transaction_data["business_id"] = business_id
        response = requests.post(f"{API_URL}/transactions", json=transaction_data)
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # 5. Get dashboard and verify calculations
    response = requests.get(f"{API_URL}/impact/dashboard/{business_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    dashboard = response.json()
    
    # Calculate expected totals
    total_sales = sum(t["amount"] for t in transactions)
    total_impact = total_sales  # 100% allocation
    
    assert dashboard["total_sales"] == total_sales, f"Expected total_sales {total_sales}, got {dashboard['total_sales']}"
    assert abs(dashboard["total_impact"] - total_impact) < 0.01, f"Expected total_impact {total_impact}, got {dashboard['total_impact']}"
    
    # 6. Verify public impact page
    response = requests.get(f"{API_URL}/impact/public/{business_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    public_impact = response.json()
    assert public_impact["total_sales"] == total_sales, f"Expected total_sales {total_sales}, got {public_impact['total_sales']}"
    assert abs(public_impact["total_impact"] - total_impact) < 0.01, f"Expected total_impact {total_impact}, got {public_impact['total_impact']}"
    
    # 7. Verify cause breakdown
    for allocation in allocations:
        cause_id = allocation["cause_id"]
        percentage = allocation["percentage"]
        
        # Get cause details
        cause_response = requests.get(f"{API_URL}/causes/{cause_id}")
        cause = cause_response.json()
        
        # Calculate expected values
        expected_contribution = (total_sales * percentage) / 100
        expected_impact_units = expected_contribution / cause["cost_per_impact"]
        
        # Verify in public impact
        assert cause_id in public_impact["cause_breakdown"], f"Cause {cause_id} not found in public impact"
        cause_data = public_impact["cause_breakdown"][cause_id]
        
        assert cause_data["percentage"] == percentage, f"Expected percentage {percentage}, got {cause_data['percentage']}"
        assert abs(cause_data["total_contribution"] - expected_contribution) < 0.01, f"Expected contribution {expected_contribution}, got {cause_data['total_contribution']}"
        assert abs(cause_data["impact_units"] - expected_impact_units) < 0.01, f"Expected impact units {expected_impact_units}, got {cause_data['impact_units']}"
    
    return True

if __name__ == "__main__":
    # Global variables to store test data
    test_business_id = None
    test_business_api_key = None
    test_cause_ids = []
    test_transaction_id = None
    test_customer_id = None
    test_customer_id2 = None
    test_contribution_id = None
    test_new_cause_id = None
    
    # Run tests for original features
    print("\n===== TESTING ORIGINAL FEATURES =====")
    run_test("Get Causes", test_get_causes)
    run_test("Get Specific Cause", test_get_specific_cause)
    run_test("Create Business", test_create_business)
    run_test("Get Businesses", test_get_businesses)
    run_test("Get Specific Business", test_get_specific_business)
    run_test("Update Impact Allocation", test_update_impact_allocation)
    run_test("Create Transaction", test_create_transaction)
    run_test("Get Transactions", test_get_transactions)
    run_test("Impact Dashboard", test_impact_dashboard)
    run_test("Public Impact", test_public_impact)
    
    # Run tests for new features
    print("\n===== TESTING NEW FEATURES =====")
    
    # Enhanced Cause Management
    run_test("Get Causes with Filters", test_get_causes_with_filters)
    run_test("Create Cause", test_create_cause)
    
    # Customer Management
    run_test("Create Customer", test_create_customer)
    run_test("Get Customers", test_get_customers)
    run_test("Get Specific Customer", test_get_specific_customer)
    
    # Direct Contribution System
    run_test("Create Direct Contribution", test_create_direct_contribution)
    run_test("Get Contributions", test_get_contributions)
    
    # Leaderboard System
    run_test("Business Leaderboard", test_business_leaderboard)
    run_test("Customer Leaderboard", test_customer_leaderboard)
    
    # Badge System
    run_test("Get All Badges", test_get_all_badges)
    run_test("Get User Badges", test_get_user_badges)
    
    # Admin Dashboard
    run_test("Admin Dashboard", test_admin_dashboard)
    run_test("Admin Businesses", test_admin_businesses)
    run_test("Admin Verify Business", test_admin_verify_business)
    run_test("Admin Causes", test_admin_causes)
    
    # External API
    run_test("External Transaction", test_external_transaction)
    run_test("External Business Impact", test_external_business_impact)
    run_test("External Causes", test_external_causes)
    
    # Complex Scenarios
    print("\n===== TESTING COMPLEX SCENARIOS =====")
    run_test("Customer Contribution Badge Flow", test_customer_contribution_badge_flow)
    run_test("Admin Verification Workflow", test_admin_verification_workflow)
    run_test("Comprehensive Flow", test_comprehensive_flow)
    
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