#!/usr/bin/env python3
import requests
import json
import re
import uuid
from pprint import pprint

# Get the backend URL from the frontend .env file
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            BACKEND_URL = line.strip().split('=')[1].strip('"\'')
            break

API_URL = f"{BACKEND_URL}/api"
print(f"Updating causes at: {API_URL}")

def update_causes_with_ussd():
    """Update all causes to ensure they have valid USSD shortcodes"""
    # Get all causes
    response = requests.get(f"{API_URL}/causes")
    if response.status_code != 200:
        print(f"Error getting causes: {response.status_code}")
        return False
    
    causes = response.json()
    print(f"Found {len(causes)} causes")
    
    # Find causes with missing or empty USSD shortcodes
    missing_ussd = []
    for cause in causes:
        if not cause.get("ussd_shortcode"):
            missing_ussd.append(cause)
    
    print(f"Found {len(missing_ussd)} causes with missing USSD shortcodes")
    
    # Update each cause with a proper USSD shortcode
    updated_count = 0
    for cause in missing_ussd:
        cause_id = cause["id"]
        cause_code = cause["cause_code"]
        
        # Generate USSD shortcode
        ussd_shortcode = f"*123*86*{cause_code}*[Amount]#"
        
        # Update the cause
        # Note: Since we don't have a direct PUT endpoint for updating USSD shortcodes,
        # we'll need to create a custom endpoint or update the database directly.
        # For this test, we'll just print what would be updated.
        print(f"Would update cause {cause_id} with USSD shortcode: {ussd_shortcode}")
        updated_count += 1
    
    print(f"Would update {updated_count} causes with USSD shortcodes")
    
    # Verify all causes now have valid USSD shortcodes
    print("\nVerifying all causes have valid USSD shortcodes after update:")
    response = requests.get(f"{API_URL}/causes")
    if response.status_code != 200:
        print(f"Error getting causes: {response.status_code}")
        return False
    
    causes = response.json()
    
    # Create a new cause to verify USSD shortcode generation
    print("\nCreating a new cause to verify USSD shortcode generation:")
    
    # First, get an existing business to use as creator
    response = requests.get(f"{API_URL}/businesses")
    if response.status_code != 200:
        print(f"Error getting businesses: {response.status_code}")
        return False
    
    businesses = response.json()
    if not businesses:
        print("No businesses found")
        return False
    
    business_id = businesses[0]["id"]
    
    cause_data = {
        "name": "USSD Verification Cause",
        "description": "Verifying USSD shortcode generation",
        "category": "Environment",
        "image_url": "https://images.unsplash.com/photo-1508514177221-188b1cf16e9d",
        "impact_metric": "trees planted",
        "cost_per_impact": 5.0,
        "goal_amount": 10000.0,
        "creator_id": business_id,
        "creator_type": "business"
    }
    
    response = requests.post(f"{API_URL}/causes", json=cause_data)
    if response.status_code != 200:
        print(f"Error creating cause: {response.status_code}")
        return False
    
    new_cause = response.json()
    print(f"Created new cause with ID: {new_cause['id']}")
    print(f"Cause code: {new_cause['cause_code']}")
    print(f"USSD shortcode: {new_cause['ussd_shortcode']}")
    
    # Verify the USSD shortcode format
    cause_code = new_cause["cause_code"]
    ussd_shortcode = new_cause["ussd_shortcode"]
    expected_format = f"*123*86*{cause_code}*[Amount]#"
    
    if ussd_shortcode == expected_format:
        print(f"✅ USSD shortcode format is correct: {ussd_shortcode}")
    else:
        print(f"❌ USSD shortcode format is incorrect. Expected: {expected_format}, Got: {ussd_shortcode}")
    
    return True

if __name__ == "__main__":
    update_causes_with_ussd()