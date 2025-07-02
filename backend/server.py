from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import hashlib
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="ImpactLink API", description="Social Impact Platform API", version="2.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer(auto_error=False)

def create_api_key():
    """Generate a simple API key for demo purposes"""
    return f"il_{uuid.uuid4().hex[:24]}"

# Enhanced Models
class Customer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    phone: Optional[str] = None
    total_contributions: float = 0.0
    contribution_count: int = 0
    badges: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_contribution: Optional[datetime] = None

class CustomerCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None

class Business(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    industry: str
    email: str
    phone: Optional[str] = None
    website: Optional[str] = None
    api_key: str = Field(default_factory=create_api_key)
    impact_allocations: Dict[str, float] = Field(default_factory=dict)
    total_sales: float = 0.0
    total_impact: float = 0.0
    transaction_count: int = 0
    badges: List[str] = Field(default_factory=list)
    verified: bool = False
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
    image_url: Optional[str] = None
    impact_metric: str
    cost_per_impact: float
    total_raised: float = 0.0
    total_impact_units: float = 0.0
    goal_amount: Optional[float] = None
    active: bool = True
    featured: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CauseCreate(BaseModel):
    name: str
    description: str
    category: str
    image_url: Optional[str] = None
    impact_metric: str
    cost_per_impact: float
    goal_amount: Optional[float] = None

class DirectContribution(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    cause_id: str
    amount: float
    message: Optional[str] = None
    anonymous: bool = False
    impact_units: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DirectContributionCreate(BaseModel):
    customer_id: str
    cause_id: str
    amount: float
    message: Optional[str] = None
    anonymous: bool = False

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    business_id: str
    amount: float
    customer_name: Optional[str] = None
    impact_breakdown: Dict[str, Dict[str, object]] = Field(default_factory=dict)
    total_impact_amount: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ImpactAllocation(BaseModel):
    cause_id: str
    percentage: float

class TransactionCreate(BaseModel):
    business_id: str
    amount: float
    customer_name: Optional[str] = None

class Badge(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    criteria: Dict[str, object]
    rarity: str  # common, rare, epic, legendary

class AdminUser(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    role: str = "admin"
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Badge definitions
BADGES = {
    "first_contribution": Badge(
        id="first_contribution",
        name="First Step",
        description="Made your first contribution to a cause",
        icon="🌟",
        criteria={"type": "contribution_count", "value": 1},
        rarity="common"
    ),
    "generous_giver": Badge(
        id="generous_giver",
        name="Generous Giver",
        description="Contributed over $500 total",
        icon="💖",
        criteria={"type": "total_contributions", "value": 500},
        rarity="rare"
    ),
    "impact_champion": Badge(
        id="impact_champion",
        name="Impact Champion",
        description="Contributed over $1000 total",
        icon="🏆",
        criteria={"type": "total_contributions", "value": 1000},
        rarity="epic"
    ),
    "multi_cause_supporter": Badge(
        id="multi_cause_supporter",
        name="Multi-Cause Supporter",
        description="Supported 3 different causes",
        icon="🌍",
        criteria={"type": "causes_supported", "value": 3},
        rarity="rare"
    ),
    "business_pioneer": Badge(
        id="business_pioneer",
        name="Business Pioneer",
        description="First business to join ImpactLink",
        icon="🚀",
        criteria={"type": "business_rank", "value": 1},
        rarity="legendary"
    ),
    "impact_leader": Badge(
        id="impact_leader",
        name="Impact Leader",
        description="Generated over $5000 in social impact",
        icon="👑",
        criteria={"type": "total_impact", "value": 5000},
        rarity="legendary"
    ),
    "consistent_contributor": Badge(
        id="consistent_contributor",
        name="Consistent Contributor",
        description="Made contributions for 7 consecutive days",
        icon="📅",
        criteria={"type": "consecutive_days", "value": 7},
        rarity="epic"
    )
}

async def check_and_award_badges(user_type: str, user_id: str, user_data: dict):
    """Check and award badges based on user achievements"""
    awarded_badges = []
    
    for badge_id, badge in BADGES.items():
        if badge_id in user_data.get("badges", []):
            continue  # Already has this badge
            
        criteria = badge.criteria
        criteria_met = False
        
        if criteria["type"] == "contribution_count":
            criteria_met = user_data.get("contribution_count", 0) >= criteria["value"]
        elif criteria["type"] == "total_contributions":
            criteria_met = user_data.get("total_contributions", 0) >= criteria["value"]
        elif criteria["type"] == "total_impact":
            criteria_met = user_data.get("total_impact", 0) >= criteria["value"]
        elif criteria["type"] == "transaction_count":
            criteria_met = user_data.get("transaction_count", 0) >= criteria["value"]
        
        if criteria_met:
            # Award badge
            collection = db.customers if user_type == "customer" else db.businesses
            await collection.update_one(
                {"id": user_id},
                {"$addToSet": {"badges": badge_id}}
            )
            awarded_badges.append(badge)
    
    return awarded_badges

# Initialize default data
async def init_default_data():
    # Initialize causes
    existing_causes = await db.causes.count_documents({})
    if existing_causes == 0:
        default_causes = [
            {
                "id": str(uuid.uuid4()),
                "name": "Education for All",
                "description": "Providing quality education access to underprivileged children worldwide",
                "category": "Education",
                "image_url": "https://images.pexels.com/photos/2219024/pexels-photo-2219024.jpeg",
                "impact_metric": "children educated for 1 month",
                "cost_per_impact": 25.0,
                "total_raised": 0.0,
                "total_impact_units": 0.0,
                "goal_amount": 10000.0,
                "active": True,
                "featured": True,
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Clean Water Initiative",
                "description": "Building wells and water purification systems in rural communities",
                "category": "Health",
                "image_url": "https://images.unsplash.com/photo-1469571486292-0ba58a3f068b",
                "impact_metric": "people with clean water access for 1 year",
                "cost_per_impact": 50.0,
                "total_raised": 0.0,
                "total_impact_units": 0.0,
                "goal_amount": 25000.0,
                "active": True,
                "featured": True,
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
                "goal_amount": 5000.0,
                "active": True,
                "featured": False,
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
                "goal_amount": 15000.0,
                "active": True,
                "featured": True,
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Mental Health Support",
                "description": "Providing counseling and mental health resources",
                "category": "Health",
                "impact_metric": "therapy sessions provided",
                "cost_per_impact": 75.0,
                "total_raised": 0.0,
                "total_impact_units": 0.0,
                "goal_amount": 20000.0,
                "active": True,
                "featured": False,
                "created_at": datetime.utcnow()
            }
        ]
        
        for cause in default_causes:
            await db.causes.insert_one(cause)

    # Create default admin user
    existing_admin = await db.admin_users.count_documents({})
    if existing_admin == 0:
        admin_user = {
            "id": str(uuid.uuid4()),
            "username": "admin",
            "email": "admin@impactlink.com",
            "role": "admin",
            "created_at": datetime.utcnow()
        }
        await db.admin_users.insert_one(admin_user)

# Customer endpoints
@api_router.post("/customers", response_model=Customer)
async def create_customer(customer: CustomerCreate):
    # Check if email already exists
    existing = await db.customers.find_one({"email": customer.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    customer_dict = customer.dict()
    customer_obj = Customer(**customer_dict)
    await db.customers.insert_one(customer_obj.dict())
    return customer_obj

@api_router.get("/customers", response_model=List[Customer])
async def get_customers():
    customers = await db.customers.find().to_list(1000)
    return [Customer(**customer) for customer in customers]

@api_router.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str):
    customer = await db.customers.find_one({"id": customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return Customer(**customer)

# Direct contribution endpoints
@api_router.post("/contributions", response_model=DirectContribution)
async def create_direct_contribution(contribution: DirectContributionCreate):
    # Verify customer and cause exist
    customer = await db.customers.find_one({"id": contribution.customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    cause = await db.causes.find_one({"id": contribution.cause_id})
    if not cause:
        raise HTTPException(status_code=404, detail="Cause not found")
    
    cause_obj = Cause(**cause)
    
    # Calculate impact units
    impact_units = contribution.amount / cause_obj.cost_per_impact
    
    # Create contribution
    contribution_obj = DirectContribution(
        **contribution.dict(),
        impact_units=impact_units
    )
    
    await db.direct_contributions.insert_one(contribution_obj.dict())
    
    # Update cause totals
    await db.causes.update_one(
        {"id": contribution.cause_id},
        {
            "$inc": {
                "total_raised": contribution.amount,
                "total_impact_units": impact_units
            }
        }
    )
    
    # Update customer totals
    await db.customers.update_one(
        {"id": contribution.customer_id},
        {
            "$inc": {
                "total_contributions": contribution.amount,
                "contribution_count": 1
            },
            "$set": {
                "last_contribution": datetime.utcnow()
            }
        }
    )
    
    # Check and award badges
    updated_customer = await db.customers.find_one({"id": contribution.customer_id})
    await check_and_award_badges("customer", contribution.customer_id, updated_customer)
    
    return contribution_obj

@api_router.get("/contributions", response_model=List[DirectContribution])
async def get_contributions(customer_id: Optional[str] = None, cause_id: Optional[str] = None):
    query = {}
    if customer_id:
        query["customer_id"] = customer_id
    if cause_id:
        query["cause_id"] = cause_id
    
    contributions = await db.direct_contributions.find(query).sort("timestamp", -1).to_list(1000)
    return [DirectContribution(**contribution) for contribution in contributions]

# Business endpoints (enhanced)
@api_router.post("/businesses", response_model=Business)
async def create_business(business: BusinessCreate):
    business_dict = business.dict()
    business_obj = Business(**business_dict)
    await db.businesses.insert_one(business_obj.dict())
    
    # Check if this is the first business (pioneer badge)
    business_count = await db.businesses.count_documents({})
    if business_count == 1:
        await db.businesses.update_one(
            {"id": business_obj.id},
            {"$addToSet": {"badges": "business_pioneer"}}
        )
    
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
    
    total_percentage = sum(allocation.percentage for allocation in allocations)
    if total_percentage > 100:
        raise HTTPException(status_code=400, detail="Total allocation cannot exceed 100%")
    
    impact_allocations = {allocation.cause_id: allocation.percentage for allocation in allocations}
    await db.businesses.update_one(
        {"id": business_id},
        {"$set": {"impact_allocations": impact_allocations}}
    )
    
    return {"message": "Impact allocation updated successfully", "total_percentage": total_percentage}

# Enhanced cause endpoints
@api_router.get("/causes", response_model=List[Cause])
async def get_causes(active_only: bool = True, featured_only: bool = False):
    query = {}
    if active_only:
        query["active"] = True
    if featured_only:
        query["featured"] = True
    
    causes = await db.causes.find(query).to_list(1000)
    return [Cause(**cause) for cause in causes]

@api_router.get("/causes/{cause_id}", response_model=Cause)
async def get_cause(cause_id: str):
    cause = await db.causes.find_one({"id": cause_id})
    if not cause:
        raise HTTPException(status_code=404, detail="Cause not found")
    return Cause(**cause)

@api_router.post("/causes", response_model=Cause)
async def create_cause(cause: CauseCreate):
    cause_dict = cause.dict()
    cause_obj = Cause(**cause_dict)
    await db.causes.insert_one(cause_obj.dict())
    return cause_obj

# Transaction endpoints (enhanced)
@api_router.post("/transactions", response_model=Transaction)
async def create_transaction(transaction: TransactionCreate):
    business = await db.businesses.find_one({"id": transaction.business_id})
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    business_obj = Business(**business)
    
    impact_breakdown = {}
    total_impact_amount = 0.0
    
    for cause_id, percentage in business_obj.impact_allocations.items():
        impact_amount = (transaction.amount * percentage) / 100
        total_impact_amount += impact_amount
        
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
            
            await db.causes.update_one(
                {"id": cause_id},
                {
                    "$inc": {
                        "total_raised": impact_amount,
                        "total_impact_units": impact_units
                    }
                }
            )
    
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
                "total_impact": total_impact_amount,
                "transaction_count": 1
            }
        }
    )
    
    # Check and award business badges
    updated_business = await db.businesses.find_one({"id": transaction.business_id})
    await check_and_award_badges("business", transaction.business_id, updated_business)
    
    return transaction_obj

@api_router.get("/transactions", response_model=List[Transaction])
async def get_transactions(business_id: Optional[str] = None):
    query = {}
    if business_id:
        query["business_id"] = business_id
    
    transactions = await db.transactions.find(query).sort("timestamp", -1).to_list(1000)
    return [Transaction(**transaction) for transaction in transactions]

# Leaderboard endpoints
@api_router.get("/leaderboards/businesses")
async def get_business_leaderboard(metric: str = "total_impact", limit: int = 10):
    valid_metrics = ["total_impact", "total_sales", "transaction_count"]
    if metric not in valid_metrics:
        raise HTTPException(status_code=400, detail=f"Invalid metric. Choose from: {valid_metrics}")
    
    businesses = await db.businesses.find().sort(metric, -1).limit(limit).to_list(limit)
    
    leaderboard = []
    for rank, business in enumerate(businesses, 1):
        business_obj = Business(**business)
        leaderboard.append({
            "rank": rank,
            "business": business_obj,
            "metric_value": getattr(business_obj, metric),
            "badges": business_obj.badges
        })
    
    return {
        "metric": metric,
        "leaderboard": leaderboard
    }

@api_router.get("/leaderboards/customers")
async def get_customer_leaderboard(metric: str = "total_contributions", limit: int = 10):
    valid_metrics = ["total_contributions", "contribution_count"]
    if metric not in valid_metrics:
        raise HTTPException(status_code=400, detail=f"Invalid metric. Choose from: {valid_metrics}")
    
    customers = await db.customers.find().sort(metric, -1).limit(limit).to_list(limit)
    
    leaderboard = []
    for rank, customer in enumerate(customers, 1):
        customer_obj = Customer(**customer)
        leaderboard.append({
            "rank": rank,
            "customer": customer_obj,
            "metric_value": getattr(customer_obj, metric),
            "badges": customer_obj.badges
        })
    
    return {
        "metric": metric,
        "leaderboard": leaderboard
    }

# Badge endpoints
@api_router.get("/badges")
async def get_all_badges():
    return [badge.dict() for badge in BADGES.values()]

@api_router.get("/badges/{user_type}/{user_id}")
async def get_user_badges(user_type: str, user_id: str):
    if user_type not in ["customer", "business"]:
        raise HTTPException(status_code=400, detail="Invalid user type")
    
    collection = db.customers if user_type == "customer" else db.businesses
    user = await collection.find_one({"id": user_id})
    
    if not user:
        raise HTTPException(status_code=404, detail=f"{user_type.title()} not found")
    
    user_badges = user.get("badges", [])
    badge_details = [BADGES[badge_id].dict() for badge_id in user_badges if badge_id in BADGES]
    
    return {
        "user_id": user_id,
        "user_type": user_type,
        "badges": badge_details
    }

# Admin endpoints
@api_router.get("/admin/dashboard")
async def get_admin_dashboard():
    # Platform statistics
    total_businesses = await db.businesses.count_documents({})
    total_customers = await db.customers.count_documents({})
    total_causes = await db.causes.count_documents({"active": True})
    total_transactions = await db.transactions.count_documents({})
    total_contributions = await db.direct_contributions.count_documents({})
    
    # Financial metrics
    business_impact = await db.businesses.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$total_impact"}}}
    ]).to_list(1)
    
    customer_contributions = await db.customers.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$total_contributions"}}}
    ]).to_list(1)
    
    total_business_impact = business_impact[0]["total"] if business_impact else 0
    total_customer_contributions = customer_contributions[0]["total"] if customer_contributions else 0
    total_platform_impact = total_business_impact + total_customer_contributions
    
    # Recent activity
    recent_transactions = await db.transactions.find().sort("timestamp", -1).limit(5).to_list(5)
    recent_contributions = await db.direct_contributions.find().sort("timestamp", -1).limit(5).to_list(5)
    
    # Top causes by total raised
    top_causes = await db.causes.find().sort("total_raised", -1).limit(5).to_list(5)
    
    return {
        "statistics": {
            "total_businesses": total_businesses,
            "total_customers": total_customers,
            "total_causes": total_causes,
            "total_transactions": total_transactions,
            "total_contributions": total_contributions,
            "total_platform_impact": total_platform_impact,
            "business_impact": total_business_impact,
            "customer_contributions": total_customer_contributions
        },
        "recent_activity": {
            "transactions": [Transaction(**t) for t in recent_transactions],
            "contributions": [DirectContribution(**c) for c in recent_contributions]
        },
        "top_causes": [Cause(**c) for c in top_causes]
    }

@api_router.get("/admin/businesses")
async def get_admin_businesses():
    businesses = await db.businesses.find().sort("created_at", -1).to_list(1000)
    return [Business(**business) for business in businesses]

@api_router.put("/admin/businesses/{business_id}/verify")
async def verify_business(business_id: str):
    result = await db.businesses.update_one(
        {"id": business_id},
        {"$set": {"verified": True}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Business not found")
    
    return {"message": "Business verified successfully"}

@api_router.get("/admin/causes")
async def get_admin_causes():
    causes = await db.causes.find().sort("created_at", -1).to_list(1000)
    return [Cause(**cause) for cause in causes]

@api_router.put("/admin/causes/{cause_id}")
async def update_cause(cause_id: str, cause_update: CauseCreate):
    result = await db.causes.update_one(
        {"id": cause_id},
        {"$set": cause_update.dict()}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Cause not found")
    
    return {"message": "Cause updated successfully"}

# Enhanced dashboard endpoints
@api_router.get("/impact/dashboard/{business_id}")
async def get_impact_dashboard(business_id: str):
    business = await db.businesses.find_one({"id": business_id})
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    business_obj = Business(**business)
    
    recent_transactions = await db.transactions.find(
        {"business_id": business_id}
    ).sort("timestamp", -1).limit(10).to_list(10)
    
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
        "impact_percentage": (business_obj.total_impact / business_obj.total_sales * 100) if business_obj.total_sales > 0 else 0,
        "badges": business_obj.badges
    }

@api_router.get("/impact/public/{business_id}")
async def get_public_impact(business_id: str):
    business = await db.businesses.find_one({"id": business_id})
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    business_obj = Business(**business)
    
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
        "badges": business_obj.badges,
        "verified": business_obj.verified,
        "impact_message": f"Every purchase you make helps {business_obj.name} contribute to social causes!"
    }

# External API endpoints for third-party integrations
@api_router.post("/external/transaction")
async def create_external_transaction(
    transaction: TransactionCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """External API for businesses to create transactions via their systems"""
    if not credentials:
        raise HTTPException(status_code=401, detail="API key required")
    
    # Verify API key
    business = await db.businesses.find_one({"api_key": credentials.credentials})
    if not business:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Override business_id with the authenticated business
    transaction.business_id = business["id"]
    
    # Create transaction using existing logic
    return await create_transaction(transaction)

@api_router.get("/external/business/impact")
async def get_external_business_impact(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """External API for businesses to get their impact data"""
    if not credentials:
        raise HTTPException(status_code=401, detail="API key required")
    
    business = await db.businesses.find_one({"api_key": credentials.credentials})
    if not business:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return await get_impact_dashboard(business["id"])

@api_router.get("/external/causes")
async def get_external_causes():
    """Public API to get all active causes"""
    return await get_causes(active_only=True)

# Initialize app
@app.on_event("startup")
async def startup_event():
    await init_default_data()

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