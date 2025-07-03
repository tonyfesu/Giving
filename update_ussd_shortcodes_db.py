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

# Load environment variables
load_dotenv('/app/backend/.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'test_database')

if not mongo_url:
    print("Error: MONGO_URL environment variable not set")
    sys.exit(1)

async def update_ussd_shortcodes():
    """Update all causes to have proper USSD shortcodes"""
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Get all causes
    causes = await db.causes.find().to_list(1000)
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
        result = await db.causes.update_one(
            {"id": cause_id},
            {"$set": {"ussd_shortcode": ussd_shortcode}}
        )
        
        if result.modified_count > 0:
            print(f"Updated cause {cause_id} with USSD shortcode: {ussd_shortcode}")
            updated_count += 1
        else:
            print(f"Failed to update cause {cause_id}")
    
    print(f"Updated {updated_count} causes with USSD shortcodes")
    
    # Verify all causes now have valid USSD shortcodes
    causes = await db.causes.find().to_list(1000)
    missing_after_update = [cause for cause in causes if not cause.get("ussd_shortcode")]
    
    if missing_after_update:
        print(f"WARNING: {len(missing_after_update)} causes still missing USSD shortcodes after update")
        for cause in missing_after_update:
            print(f"  - Cause ID: {cause['id']}")
    else:
        print("✅ All causes now have USSD shortcodes")

if __name__ == "__main__":
    asyncio.run(update_ussd_shortcodes())