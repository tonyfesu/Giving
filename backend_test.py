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
    
    # Store business ID for later tests
    global test_business_id
    test_business_id = business["id"]
    print(f"Created business with ID: {test_business_id}")
    
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
    test_cause_ids = []
    test_transaction_id = None
    
    # Run tests
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