from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uuid
from datetime import datetime

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class Business(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    industry: str
    email: str
    phone: Optional[str] = None
    website: Optional[str] = None
    impact_allocations: Dict[str, float] = Field(default_factory=dict)  # cause_id -> percentage
    total_sales: float = 0.0
    total_impact: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BusinessCreate(BaseModel):
    name: str
    description: str
    industry: str
    email: str
    phone: Optional[str] = None
    website: Optional[str] = None

class Cause(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    category: str
    impact_metric: str  # e.g., "children educated", "trees planted", "meals provided"
    cost_per_impact: float  # cost to achieve one unit of impact
    total_raised: float = 0.0
    total_impact_units: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    business_id: str
    amount: float
    customer_name: Optional[str] = None
    impact_breakdown: Dict[str, Dict[str, float]] = Field(default_factory=dict)  # cause_id -> {amount, impact_units}
    total_impact_amount: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ImpactAllocation(BaseModel):
    cause_id: str
    percentage: float

class TransactionCreate(BaseModel):
    business_id: str
    amount: float
    customer_name: Optional[str] = None

# Initialize default causes
async def init_default_causes():
    existing_causes = await db.causes.count_documents({})
    if existing_causes == 0:
        default_causes = [
            {
                "id": str(uuid.uuid4()),
                "name": "Education for All",
                "description": "Providing quality education access to underprivileged children worldwide",
                "category": "Education",
                "impact_metric": "children educated for 1 month",
                "cost_per_impact": 25.0,
                "total_raised": 0.0,
                "total_impact_units": 0.0,
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Clean Water Initiative",
                "description": "Building wells and water purification systems in rural communities",
                "category": "Health",
                "impact_metric": "people with clean water access for 1 year",
                "cost_per_impact": 50.0,
                "total_raised": 0.0,
                "total_impact_units": 0.0,
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Forest Restoration",
                "description": "Planting trees and restoring damaged ecosystems",
                "category": "Environment",
                "impact_metric": "trees planted",
                "cost_per_impact": 2.0,
                "total_raised": 0.0,
                "total_impact_units": 0.0,
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Food Security Program",
                "description": "Providing nutritious meals to families in need",
                "category": "Poverty",
                "impact_metric": "meals provided",
                "cost_per_impact": 3.0,
                "total_raised": 0.0,
                "total_impact_units": 0.0,
                "created_at": datetime.utcnow()
            }
        ]
        
        for cause in default_causes:
            await db.causes.insert_one(cause)

# Business endpoints
@api_router.post("/businesses", response_model=Business)
async def create_business(business: BusinessCreate):
    business_dict = business.dict()
    business_obj = Business(**business_dict)
    await db.businesses.insert_one(business_obj.dict())
    return business_obj

@api_router.get("/businesses", response_model=List[Business])
async def get_businesses():
    businesses = await db.businesses.find().to_list(1000)
    return [Business(**business) for business in businesses]

@api_router.get("/businesses/{business_id}", response_model=Business)
async def get_business(business_id: str):
    business = await db.businesses.find_one({"id": business_id})
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return Business(**business)

@api_router.put("/businesses/{business_id}/impact-allocation")
async def update_impact_allocation(business_id: str, allocations: List[ImpactAllocation]):
    business = await db.businesses.find_one({"id": business_id})
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Validate percentages sum to 100 or less
    total_percentage = sum(allocation.percentage for allocation in allocations)
    if total_percentage > 100:
        raise HTTPException(status_code=400, detail="Total allocation cannot exceed 100%")
    
    # Update impact allocations
    impact_allocations = {allocation.cause_id: allocation.percentage for allocation in allocations}
    await db.businesses.update_one(
        {"id": business_id},
        {"$set": {"impact_allocations": impact_allocations}}
    )
    
    return {"message": "Impact allocation updated successfully", "total_percentage": total_percentage}

# Cause endpoints
@api_router.get("/causes", response_model=List[Cause])
async def get_causes():
    causes = await db.causes.find().to_list(1000)
    return [Cause(**cause) for cause in causes]

@api_router.get("/causes/{cause_id}", response_model=Cause)
async def get_cause(cause_id: str):
    cause = await db.causes.find_one({"id": cause_id})
    if not cause:
        raise HTTPException(status_code=404, detail="Cause not found")
    return Cause(**cause)

# Transaction endpoints
@api_router.post("/transactions", response_model=Transaction)
async def create_transaction(transaction: TransactionCreate):
    # Get business details
    business = await db.businesses.find_one({"id": transaction.business_id})
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    business_obj = Business(**business)
    
    # Calculate impact breakdown
    impact_breakdown = {}
    total_impact_amount = 0.0
    
    for cause_id, percentage in business_obj.impact_allocations.items():
        impact_amount = (transaction.amount * percentage) / 100
        total_impact_amount += impact_amount
        
        # Get cause details to calculate impact units
        cause = await db.causes.find_one({"id": cause_id})
        if cause:
            cause_obj = Cause(**cause)
            impact_units = impact_amount / cause_obj.cost_per_impact
            
            impact_breakdown[cause_id] = {
                "amount": impact_amount,
                "impact_units": impact_units,
                "cause_name": cause_obj.name,
                "impact_metric": cause_obj.impact_metric
            }
            
            # Update cause totals
            await db.causes.update_one(
                {"id": cause_id},
                {
                    "$inc": {
                        "total_raised": impact_amount,
                        "total_impact_units": impact_units
                    }
                }
            )
    
    # Create transaction
    transaction_obj = Transaction(
        business_id=transaction.business_id,
        amount=transaction.amount,
        customer_name=transaction.customer_name,
        impact_breakdown=impact_breakdown,
        total_impact_amount=total_impact_amount
    )
    
    await db.transactions.insert_one(transaction_obj.dict())
    
    # Update business totals
    await db.businesses.update_one(
        {"id": transaction.business_id},
        {
            "$inc": {
                "total_sales": transaction.amount,
                "total_impact": total_impact_amount
            }
        }
    )
    
    return transaction_obj

@api_router.get("/transactions", response_model=List[Transaction])
async def get_transactions(business_id: Optional[str] = None):
    query = {}
    if business_id:
        query["business_id"] = business_id
    
    transactions = await db.transactions.find(query).sort("timestamp", -1).to_list(1000)
    return [Transaction(**transaction) for transaction in transactions]

# Impact dashboard endpoints
@api_router.get("/impact/dashboard/{business_id}")
async def get_impact_dashboard(business_id: str):
    business = await db.businesses.find_one({"id": business_id})
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    business_obj = Business(**business)
    
    # Get recent transactions
    recent_transactions = await db.transactions.find(
        {"business_id": business_id}
    ).sort("timestamp", -1).limit(10).to_list(10)
    
    # Get cause breakdown
    cause_breakdown = {}
    for cause_id, percentage in business_obj.impact_allocations.items():
        cause = await db.causes.find_one({"id": cause_id})
        if cause:
            cause_obj = Cause(**cause)
            cause_breakdown[cause_id] = {
                "name": cause_obj.name,
                "percentage": percentage,
                "category": cause_obj.category,
                "impact_metric": cause_obj.impact_metric,
                "total_contribution": (business_obj.total_sales * percentage) / 100
            }
    
    return {
        "business": business_obj,
        "recent_transactions": [Transaction(**t) for t in recent_transactions],
        "cause_breakdown": cause_breakdown,
        "total_sales": business_obj.total_sales,
        "total_impact": business_obj.total_impact,
        "impact_percentage": (business_obj.total_impact / business_obj.total_sales * 100) if business_obj.total_sales > 0 else 0
    }

# Public impact page
@api_router.get("/impact/public/{business_id}")
async def get_public_impact(business_id: str):
    business = await db.businesses.find_one({"id": business_id})
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    business_obj = Business(**business)
    
    # Get cause breakdown for public view
    cause_breakdown = {}
    for cause_id, percentage in business_obj.impact_allocations.items():
        cause = await db.causes.find_one({"id": cause_id})
        if cause:
            cause_obj = Cause(**cause)
            total_contribution = (business_obj.total_sales * percentage) / 100
            impact_units = total_contribution / cause_obj.cost_per_impact if cause_obj.cost_per_impact > 0 else 0
            
            cause_breakdown[cause_id] = {
                "name": cause_obj.name,
                "description": cause_obj.description,
                "category": cause_obj.category,
                "impact_metric": cause_obj.impact_metric,
                "percentage": percentage,
                "total_contribution": total_contribution,
                "impact_units": impact_units
            }
    
    return {
        "business_name": business_obj.name,
        "business_description": business_obj.description,
        "total_sales": business_obj.total_sales,
        "total_impact": business_obj.total_impact,
        "cause_breakdown": cause_breakdown,
        "impact_message": f"Every purchase you make helps {business_obj.name} contribute to social causes!"
    }

# Initialize app
@app.on_event("startup")
async def startup_event():
    await init_default_causes()

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()