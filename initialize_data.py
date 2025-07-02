#!/usr/bin/env python3
import requests
import json
import time
from pprint import pprint

# Get the backend URL from the frontend .env file
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            BACKEND_URL = line.strip().split('=')[1].strip('"\'')
            break

API_URL = f"{BACKEND_URL}/api"
print(f"Testing API at: {API_URL}")

def initialize_data():
    """Initialize default data in the system"""
    print("\n===== INITIALIZING DEFAULT DATA =====")
    
    # Create a business
    business_data = {
        "name": "EcoTech Solutions",
        "description": "Sustainable technology company committed to environmental impact",
        "industry": "Technology",
        "email": "demo@ecotech.com",
        "phone": "+1-555-0100",
        "website": "https://ecotech-demo.com",
        "settlement_info": {
            "account_number": "1234567890",
            "phone_number": "+1-555-0100",
            "bank_name": "Demo Bank",
            "bank_code": "DEMO001",
            "account_type": "checking",
            "verified": True
        }
    }
    
    response = requests.post(f"{API_URL}/businesses", json=business_data)
    if response.status_code == 200:
        business = response.json()
        business_id = business["id"]
        print(f"Created business: {business['name']} (ID: {business_id})")
    else:
        print(f"Failed to create business: {response.status_code} - {response.text}")
        business_id = None
    
    # Create a customer
    customer_data = {
        "name": "Sarah Green",
        "email": "sarah@demo.com",
        "phone": "+1-555-0200",
        "settlement_info": {
            "phone_number": "+1-555-0200",
            "account_type": "momo",
            "verified": True
        }
    }
    
    response = requests.post(f"{API_URL}/customers", json=customer_data)
    if response.status_code == 200:
        customer = response.json()
        customer_id = customer["id"]
        print(f"Created customer: {customer['name']} (ID: {customer_id})")
    else:
        print(f"Failed to create customer: {response.status_code} - {response.text}")
        customer_id = None
    
    # Create causes
    if business_id and customer_id:
        causes_data = [
            {
                "name": "Education for All",
                "description": "Providing quality education access to underprivileged children worldwide",
                "category": "Education",
                "image_url": "https://images.pexels.com/photos/2219024/pexels-photo-2219024.jpeg",
                "impact_metric": "children educated for 1 month",
                "cost_per_impact": 25.0,
                "goal_amount": 10000.0,
                "end_date": "2025-10-01T00:00:00Z",
                "creator_id": business_id,
                "creator_type": "business"
            },
            {
                "name": "Clean Water Initiative",
                "description": "Building wells and water purification systems in rural communities",
                "category": "Health",
                "image_url": "https://images.unsplash.com/photo-1469571486292-0ba58a3f068b",
                "impact_metric": "people with clean water access for 1 year",
                "cost_per_impact": 50.0,
                "goal_amount": 25000.0,
                "end_date": "2026-01-01T00:00:00Z",
                "creator_id": customer_id,
                "creator_type": "customer"
            },
            {
                "name": "Forest Restoration",
                "description": "Planting trees and restoring damaged ecosystems",
                "category": "Environment",
                "impact_metric": "trees planted",
                "cost_per_impact": 2.0,
                "goal_amount": 5000.0,
                "end_date": "2025-09-01T00:00:00Z",
                "creator_id": business_id,
                "creator_type": "business"
            },
            {
                "name": "Food Security Program",
                "description": "Providing nutritious meals to families in need",
                "category": "Poverty",
                "impact_metric": "meals provided",
                "cost_per_impact": 3.0,
                "goal_amount": 15000.0,
                "end_date": "2025-11-01T00:00:00Z",
                "creator_id": customer_id,
                "creator_type": "customer"
            },
            {
                "name": "Mental Health Support",
                "description": "Providing counseling and mental health resources",
                "category": "Health",
                "impact_metric": "therapy sessions provided",
                "cost_per_impact": 75.0,
                "goal_amount": 20000.0,
                "end_date": "2025-07-15T00:00:00Z",
                "creator_id": business_id,
                "creator_type": "business"
            },
            {
                "name": "Digital Literacy Program",
                "description": "Teaching digital skills to underserved communities",
                "category": "Education",
                "impact_metric": "people trained",
                "cost_per_impact": 30.0,
                "goal_amount": 8000.0,
                "end_date": "2025-08-01T00:00:00Z",
                "creator_id": customer_id,
                "creator_type": "customer"
            }
        ]
        
        cause_ids = []
        for cause_data in causes_data:
            response = requests.post(f"{API_URL}/causes", json=cause_data)
            if response.status_code == 200:
                cause = response.json()
                cause_ids.append(cause["id"])
                print(f"Created cause: {cause['name']} (ID: {cause['id']})")
            else:
                print(f"Failed to create cause: {response.status_code} - {response.text}")
        
        # Set impact allocations for business
        if cause_ids:
            allocations = [
                {"cause_id": cause_ids[0], "percentage": 30},
                {"cause_id": cause_ids[2], "percentage": 40},
                {"cause_id": cause_ids[4], "percentage": 30}
            ]
            
            response = requests.put(f"{API_URL}/businesses/{business_id}/impact-allocation", json=allocations)
            if response.status_code == 200:
                print(f"Set impact allocations for business")
            else:
                print(f"Failed to set impact allocations: {response.status_code} - {response.text}")
        
        # Create transactions
        transactions_data = [
            {"business_id": business_id, "amount": 100.00, "customer_name": "John Doe"},
            {"business_id": business_id, "amount": 200.00, "customer_name": "Jane Smith"},
            {"business_id": business_id, "amount": 150.00, "customer_name": "Alex Johnson"},
            {"business_id": business_id, "amount": 75.50, "customer_name": "Sarah Wilson"},
            {"business_id": business_id, "amount": 120.25, "customer_name": "Michael Brown"}
        ]
        
        for txn_data in transactions_data:
            response = requests.post(f"{API_URL}/transactions", json=txn_data)
            if response.status_code == 200:
                txn = response.json()
                print(f"Created transaction: ${txn['amount']} from {txn['customer_name']}")
            else:
                print(f"Failed to create transaction: {response.status_code} - {response.text}")
        
        # Create direct contributions
        if cause_ids:
            contributions_data = [
                {
                    "customer_id": customer_id,
                    "cause_id": cause_ids[1],
                    "amount": 100.00,
                    "payment_method": {
                        "type": "card",
                        "provider": "visa",
                        "details": {"last4": "1234", "brand": "visa"}
                    },
                    "message": "Supporting clean water!",
                    "anonymous": False
                },
                {
                    "customer_id": customer_id,
                    "cause_id": cause_ids[3],
                    "amount": 200.00,
                    "payment_method": {
                        "type": "card",
                        "provider": "mastercard",
                        "details": {"last4": "5678", "brand": "mastercard"}
                    },
                    "message": "Everyone deserves food security",
                    "anonymous": False
                },
                {
                    "customer_id": customer_id,
                    "cause_id": cause_ids[5],
                    "amount": 150.00,
                    "payment_method": {
                        "type": "momo",
                        "provider": "mtn_momo",
                        "details": {"phone": "+1-555-0200"}
                    },
                    "message": "Digital literacy is important!",
                    "anonymous": False
                },
                {
                    "customer_name": "Anonymous Donor",
                    "customer_email": "anonymous@example.com",
                    "cause_id": cause_ids[0],
                    "amount": 50.00,
                    "payment_method": {
                        "type": "card",
                        "provider": "visa",
                        "details": {"last4": "9012", "brand": "visa"}
                    },
                    "message": "Education matters",
                    "anonymous": True
                },
                {
                    "customer_name": "Anonymous Donor",
                    "customer_email": "anonymous@example.com",
                    "cause_id": cause_ids[2],
                    "amount": 75.00,
                    "payment_method": {
                        "type": "card",
                        "provider": "visa",
                        "details": {"last4": "3456", "brand": "visa"}
                    },
                    "message": "Save the forests!",
                    "anonymous": True
                }
            ]
            
            for contrib_data in contributions_data:
                response = requests.post(f"{API_URL}/contributions", json=contrib_data)
                if response.status_code == 200:
                    contrib = response.json()
                    print(f"Created contribution: ${contrib['amount']} to {contrib['cause_id']}")
                else:
                    print(f"Failed to create contribution: {response.status_code} - {response.text}")
    
    return business_id, customer_id

if __name__ == "__main__":
    try:
        business_id, customer_id = initialize_data()
        print("\nInitialization complete!")
        print(f"Business ID: {business_id}")
        print(f"Customer ID: {customer_id}")
    except Exception as e:
        print(f"Error during initialization: {str(e)}")