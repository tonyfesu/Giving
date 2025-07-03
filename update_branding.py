#!/usr/bin/env python3
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv('/app/backend/.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
db_name = os.environ.get('DB_NAME', 'test_database')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

async def update_admin_emails():
    """Update admin emails to use @nnoboa.com domain"""
    result = await db.admin_users.update_many(
        {"email": {"$regex": "@impactlink.com$"}},
        {"$set": {"email": "admin@nnoboa.com"}}
    )
    print(f"Updated {result.modified_count} admin emails")

async def update_account_numbers():
    """Update account numbers to use NN prefix instead of IL"""
    # Update businesses
    business_cursor = db.businesses.find({"account_number": {"$regex": "^IL"}})
    business_count = 0
    async for business in business_cursor:
        new_account_number = business["account_number"].replace("IL", "NN")
        await db.businesses.update_one(
            {"_id": business["_id"]},
            {"$set": {"account_number": new_account_number}}
        )
        business_count += 1
    
    # Update customers
    customer_cursor = db.customers.find({"account_number": {"$regex": "^IL"}})
    customer_count = 0
    async for customer in customer_cursor:
        new_account_number = customer["account_number"].replace("IL", "NN")
        await db.customers.update_one(
            {"_id": customer["_id"]},
            {"$set": {"account_number": new_account_number}}
        )
        customer_count += 1
    
    print(f"Updated {business_count} business account numbers and {customer_count} customer account numbers")

async def update_api_keys():
    """Update API keys to use nn_ prefix instead of il_"""
    # Update businesses
    business_cursor = db.businesses.find({"api_key": {"$regex": "^il_"}})
    business_count = 0
    async for business in business_cursor:
        new_api_key = business["api_key"].replace("il_", "nn_")
        await db.businesses.update_one(
            {"_id": business["_id"]},
            {"$set": {"api_key": new_api_key}}
        )
        business_count += 1
    
    # Update API keys collection
    api_key_cursor = db.api_keys.find({"key": {"$regex": "^il_"}})
    api_key_count = 0
    async for api_key in api_key_cursor:
        new_key = api_key["key"].replace("il_", "nn_")
        await db.api_keys.update_one(
            {"_id": api_key["_id"]},
            {"$set": {"key": new_key}}
        )
        api_key_count += 1
    
    print(f"Updated {business_count} business API keys and {api_key_count} API keys in the api_keys collection")

async def main():
    """Run all database updates"""
    print("Starting database updates for rebranding...")
    
    await update_admin_emails()
    await update_account_numbers()
    await update_api_keys()
    
    print("Database updates completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())