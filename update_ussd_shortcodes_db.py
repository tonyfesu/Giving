#!/usr/bin/env python3
"""
Script to update all existing causes with proper USSD shortcodes.
This script would need to be run on the server with direct database access.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import sys
import random
import string

# Load environment variables
load_dotenv('/app/backend/.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'test_database')

if not mongo_url:
    print("Error: MONGO_URL environment variable not set")
    sys.exit(1)

def generate_cause_code():
    """Generate a unique cause code for USSD"""
    # Generate a 6-character alphanumeric code
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

async def update_ussd_shortcodes():
    """Update all causes to have proper USSD shortcodes"""
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Get all causes
    causes = await db.causes.find().to_list(1000)
    print(f"Found {len(causes)} causes")
    
    # Find causes with missing cause_code or ussd_shortcode
    missing_cause_code = []
    missing_ussd = []
    
    for cause in causes:
        if "cause_code" not in cause:
            missing_cause_code.append(cause)
        elif not cause.get("ussd_shortcode"):
            missing_ussd.append(cause)
    
    print(f"Found {len(missing_cause_code)} causes with missing cause_code")
    print(f"Found {len(missing_ussd)} causes with missing USSD shortcodes")
    
    # Update causes missing cause_code
    updated_cause_code_count = 0
    for cause in missing_cause_code:
        cause_id = cause["id"]
        
        # Generate cause_code
        cause_code = generate_cause_code()
        
        # Generate USSD shortcode
        ussd_shortcode = f"*123*86*{cause_code}*[Amount]#"
        
        # Update the cause
        result = await db.causes.update_one(
            {"id": cause_id},
            {"$set": {"cause_code": cause_code, "ussd_shortcode": ussd_shortcode}}
        )
        
        if result.modified_count > 0:
            print(f"Updated cause {cause_id} with cause_code: {cause_code} and USSD shortcode: {ussd_shortcode}")
            updated_cause_code_count += 1
        else:
            print(f"Failed to update cause {cause_id}")
    
    # Update causes missing only ussd_shortcode
    updated_ussd_count = 0
    for cause in missing_ussd:
        cause_id = cause["id"]
        cause_code = cause["cause_code"]
        
        # Generate USSD shortcode
        ussd_shortcode = f"*123*86*{cause_code}*[Amount]#"
        
        # Update the cause
        result = await db.causes.update_one(
            {"id": cause_id},
            {"$set": {"ussd_shortcode": ussd_shortcode}}
        )
        
        if result.modified_count > 0:
            print(f"Updated cause {cause_id} with USSD shortcode: {ussd_shortcode}")
            updated_ussd_count += 1
        else:
            print(f"Failed to update cause {cause_id}")
    
    print(f"Updated {updated_cause_code_count} causes with cause_code and USSD shortcodes")
    print(f"Updated {updated_ussd_count} causes with USSD shortcodes only")
    
    # Verify all causes now have valid USSD shortcodes
    causes = await db.causes.find().to_list(1000)
    missing_cause_code_after = [cause for cause in causes if "cause_code" not in cause]
    missing_ussd_after = [cause for cause in causes if not cause.get("ussd_shortcode")]
    
    if missing_cause_code_after:
        print(f"WARNING: {len(missing_cause_code_after)} causes still missing cause_code after update")
        for cause in missing_cause_code_after:
            print(f"  - Cause ID: {cause['id']}")
    else:
        print("✅ All causes now have cause_code")
        
    if missing_ussd_after:
        print(f"WARNING: {len(missing_ussd_after)} causes still missing USSD shortcodes after update")
        for cause in missing_ussd_after:
            print(f"  - Cause ID: {cause['id']}")
    else:
        print("✅ All causes now have USSD shortcodes")

if __name__ == "__main__":
    asyncio.run(update_ussd_shortcodes())