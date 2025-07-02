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
app = FastAPI(title="ImpactLink API", description="Social Impact Platform API", version="3.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer(auto_error=False)

def create_api_key():
    """Generate a simple API key for demo purposes"""
    return f"il_{uuid.uuid4().hex[:24]}"

# Enhanced Models
class PaymentMethod(BaseModel):
    type: str  # "card", "momo", "papss", "bank_transfer"
    provider: str  # "visa", "mastercard", "mtn_momo", "vodacom", "papss", "bank"
    details: Dict[str, Any] = Field(default_factory=dict)  # Store payment-specific details

class UserCausePreference(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_type: str  # "customer" or "business"
    cause_id: str
    priority: int = 1  # 1 = highest priority
    notification_enabled: bool = True
    monthly_target: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Customer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    phone: Optional[str] = None
    preferred_causes: List[str] = Field(default_factory=list)  # cause IDs
    payment_methods: List[PaymentMethod] = Field(default_factory=list)
    total_contributions: float = 0.0
    contribution_count: int = 0
    badges: List[str] = Field(default_factory=list)
    notification_preferences: Dict[str, bool] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_contribution: Optional[datetime] = None

class CustomerCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    preferred_causes: List[str] = Field(default_factory=list)

class Business(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    industry: str
    email: str
    phone: Optional[str] = None
    website: Optional[str] = None
    api_key: str = Field(default_factory=create_api_key)
    preferred_causes: List[str] = Field(default_factory=list)  # cause IDs they want to support
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
    preferred_causes: List[str] = Field(default_factory=list)

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
    payment_methods_accepted: List[str] = Field(default_factory=lambda: ["card", "momo", "papss", "bank_transfer"])
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CauseCreate(BaseModel):
    name: str
    description: str
    category: str
    image_url: Optional[str] = None
    impact_metric: str
    cost_per_impact: float
    goal_amount: Optional[float] = None
    payment_methods_accepted: List[str] = Field(default_factory=lambda: ["card", "momo", "papss", "bank_transfer"])

class Payment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    amount: float
    currency: str = "USD"
    method: PaymentMethod
    status: str = "pending"  # pending, completed, failed, refunded
    transaction_id: Optional[str] = None
    gateway_response: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class DirectContribution(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: Optional[str] = None  # None for anonymous contributions
    customer_name: Optional[str] = None  # For anonymous contributors
    customer_email: Optional[str] = None  # For anonymous contributors
    cause_id: str
    amount: float
    payment: Payment
    message: Optional[str] = None
    anonymous: bool = False
    impact_units: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DirectContributionCreate(BaseModel):
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    cause_id: str
    amount: float
    payment_method: PaymentMethod
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

class APIKey(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    key: str = Field(default_factory=create_api_key)
    name: str
    description: str
    business_id: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None

class APIKeyCreate(BaseModel):
    name: str
    description: str
    permissions: List[str] = Field(default_factory=list)

# Payment Processing Functions
async def process_payment(payment_method: PaymentMethod, amount: float, currency: str = "USD") -> Payment:
    """Simulate payment processing for different methods"""
    payment = Payment(
        amount=amount,
        currency=currency,
        method=payment_method,
        status="pending",
        transaction_id=f"txn_{uuid.uuid4().hex[:12]}"
    )
    
    # Simulate payment processing based on method type
    if payment_method.type == "card":
        # Simulate card processing
        payment.status = "completed" if amount <= 10000 else "failed"
        payment.gateway_response = {
            "processor": "stripe",
            "card_last4": payment_method.details.get("last4", "1234"),
            "card_brand": payment_method.details.get("brand", "visa")
        }
    
    elif payment_method.type == "momo":
        # Simulate mobile money processing
        payment.status = "completed"
        payment.gateway_response = {
            "processor": payment_method.provider,
            "phone": payment_method.details.get("phone", "+1234567890"),
            "reference": f"momo_{uuid.uuid4().hex[:8]}"
        }
    
    elif payment_method.type == "papss":
        # Simulate PAPSS processing
        payment.status = "completed"
        payment.gateway_response = {
            "processor": "papss",
            "bank_code": payment_method.details.get("bank_code", "001"),
            "reference": f"papss_{uuid.uuid4().hex[:8]}"
        }
    
    elif payment_method.type == "bank_transfer":
        # Simulate bank transfer
        payment.status = "completed"
        payment.gateway_response = {
            "processor": "bank",
            "account_number": payment_method.details.get("account_number", "*****1234"),
            "bank_name": payment_method.details.get("bank_name", "Example Bank")
        }
    
    if payment.status == "completed":
        payment.completed_at = datetime.utcnow()
    
    return payment

# Badge definitions (enhanced)
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
    "payment_pioneer": Badge(
        id="payment_pioneer",
        name="Payment Pioneer",
        description="Used multiple payment methods",
        icon="💳",
        criteria={"type": "payment_methods", "value": 2},
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
        elif criteria["type"] == "payment_methods":
            # Check how many different payment methods user has used
            payment_methods_count = len(user_data.get("payment_methods", []))
            criteria_met = payment_methods_count >= criteria["value"]
        
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
    # Initialize causes with payment methods
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
                "payment_methods_accepted": ["card", "momo", "papss", "bank_transfer"],
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
                "payment_methods_accepted": ["card", "momo", "papss", "bank_transfer"],
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
                "payment_methods_accepted": ["card", "momo", "papss"],
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
                "payment_methods_accepted": ["card", "momo", "bank_transfer"],
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
                "payment_methods_accepted": ["card", "papss", "bank_transfer"],
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

# Customer endpoints (enhanced)
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

@api_router.put("/customers/{customer_id}/causes")
async def update_customer_preferred_causes(customer_id: str, cause_ids: List[str]):
    """Update customer's preferred causes"""
    customer = await db.customers.find_one({"id": customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Validate that all cause IDs exist
    for cause_id in cause_ids:
        cause = await db.causes.find_one({"id": cause_id})
        if not cause:
            raise HTTPException(status_code=404, detail=f"Cause {cause_id} not found")
    
    await db.customers.update_one(
        {"id": customer_id},
        {"$set": {"preferred_causes": cause_ids}}
    )
    
    return {"message": "Preferred causes updated successfully", "cause_count": len(cause_ids)}

@api_router.post("/customers/{customer_id}/payment-methods")
async def add_customer_payment_method(customer_id: str, payment_method: PaymentMethod):
    """Add a payment method to customer"""
    customer = await db.customers.find_one({"id": customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    await db.customers.update_one(
        {"id": customer_id},
        {"$push": {"payment_methods": payment_method.dict()}}
    )
    
    return {"message": "Payment method added successfully"}

# Enhanced direct contribution endpoints with payment processing
@api_router.post("/contributions", response_model=DirectContribution)
async def create_direct_contribution(contribution: DirectContributionCreate):
    # Verify cause exists
    cause = await db.causes.find_one({"id": contribution.cause_id})
    if not cause:
        raise HTTPException(status_code=404, detail="Cause not found")
    
    cause_obj = Cause(**cause)
    
    # Check if payment method is accepted by this cause
    if contribution.payment_method.type not in cause_obj.payment_methods_accepted:
        raise HTTPException(
            status_code=400, 
            detail=f"Payment method {contribution.payment_method.type} not accepted by this cause"
        )
    
    # Process payment
    payment = await process_payment(contribution.payment_method, contribution.amount)
    
    if payment.status != "completed":
        raise HTTPException(status_code=400, detail="Payment processing failed")
    
    # Calculate impact units
    impact_units = contribution.amount / cause_obj.cost_per_impact
    
    # Create contribution
    contribution_obj = DirectContribution(
        customer_id=contribution.customer_id,
        customer_name=contribution.customer_name,
        customer_email=contribution.customer_email,
        cause_id=contribution.cause_id,
        amount=contribution.amount,
        payment=payment,
        message=contribution.message,
        anonymous=contribution.anonymous,
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
    
    # Update customer totals if registered customer
    if contribution.customer_id:
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
async def get_contributions(
    customer_id: Optional[str] = None, 
    cause_id: Optional[str] = None,
    anonymous_only: bool = False
):
    query = {}
    if customer_id:
        query["customer_id"] = customer_id
    if cause_id:
        query["cause_id"] = cause_id
    if anonymous_only:
        query["customer_id"] = None
    
    contributions = await db.direct_contributions.find(query).sort("timestamp", -1).to_list(1000)
    return [DirectContribution(**contribution) for contribution in contributions]

# Enhanced business endpoints
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

@api_router.put("/businesses/{business_id}/causes")
async def update_business_preferred_causes(business_id: str, cause_ids: List[str]):
    """Update business's preferred causes"""
    business = await db.businesses.find_one({"id": business_id})
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Validate that all cause IDs exist
    for cause_id in cause_ids:
        cause = await db.causes.find_one({"id": cause_id})
        if not cause:
            raise HTTPException(status_code=404, detail=f"Cause {cause_id} not found")
    
    await db.businesses.update_one(
        {"id": business_id},
        {"$set": {"preferred_causes": cause_ids}}
    )
    
    return {"message": "Preferred causes updated successfully", "cause_count": len(cause_ids)}

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
async def get_causes(
    active_only: bool = True, 
    featured_only: bool = False,
    payment_method: Optional[str] = None
):
    query = {}
    if active_only:
        query["active"] = True
    if featured_only:
        query["featured"] = True
    if payment_method:
        query["payment_methods_accepted"] = payment_method
    
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

# Transaction endpoints (unchanged from previous version)
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

# Payment methods endpoints
@api_router.get("/payment-methods")
async def get_supported_payment_methods():
    """Get all supported payment methods and their providers"""
    return {
        "payment_methods": [
            {
                "type": "card",
                "name": "Credit/Debit Card",
                "providers": ["visa", "mastercard", "amex", "discover"],
                "description": "Secure card payments via Stripe/PayPal"
            },
            {
                "type": "momo",
                "name": "Mobile Money",
                "providers": ["mtn_momo", "vodacom", "orange_money", "airtel_money"],
                "description": "Mobile money payments across Africa"
            },
            {
                "type": "papss",
                "name": "PAPSS",
                "providers": ["papss"],
                "description": "Pan-African Payment and Settlement System"
            },
            {
                "type": "bank_transfer",
                "name": "Bank Transfer",
                "providers": ["local_bank", "swift"],
                "description": "Direct bank account transfers"
            }
        ]
    }

# Developer Platform endpoints
@api_router.get("/dev/docs")
async def get_api_documentation():
    """Get API documentation for developers"""
    return {
        "title": "ImpactLink Developer API",
        "version": "3.0",
        "description": "Complete API for integrating social impact into your applications",
        "base_url": "https://api.impactlink.com",
        "authentication": {
            "type": "API Key",
            "header": "Authorization: Bearer YOUR_API_KEY",
            "description": "Get your API key from the business dashboard"
        },
        "endpoints": {
            "businesses": {
                "POST /api/businesses": "Create a new business account",
                "GET /api/businesses/{id}": "Get business details",
                "PUT /api/businesses/{id}/impact-allocation": "Set impact allocation percentages"
            },
            "transactions": {
                "POST /api/transactions": "Record a new transaction with automatic impact calculation",
                "GET /api/transactions": "List all transactions for a business"
            },
            "causes": {
                "GET /api/causes": "List all available causes",
                "GET /api/causes/{id}": "Get detailed cause information"
            },
            "contributions": {
                "POST /api/contributions": "Create direct contribution (supports anonymous)",
                "GET /api/contributions": "List contributions with filters"
            },
            "external": {
                "POST /api/external/transaction": "Create transaction via API key (for e-commerce integration)",
                "GET /api/external/business/impact": "Get business impact data via API key"
            }
        },
        "examples": {
            "create_transaction": {
                "url": "POST /api/external/transaction",
                "headers": {"Authorization": "Bearer il_your_api_key_here"},
                "body": {
                    "amount": 100.00,
                    "customer_name": "John Doe"
                }
            },
            "direct_contribution": {
                "url": "POST /api/contributions",
                "body": {
                    "cause_id": "cause_uuid_here",
                    "amount": 50.00,
                    "payment_method": {
                        "type": "card",
                        "provider": "visa",
                        "details": {"last4": "1234", "brand": "visa"}
                    },
                    "customer_name": "Anonymous Donor",
                    "message": "Keep up the great work!"
                }
            }
        }
    }

@api_router.post("/dev/api-keys", response_model=APIKey)
async def create_api_key(api_key_data: APIKeyCreate, business_id: str):
    """Create a new API key for a business"""
    business = await db.businesses.find_one({"id": business_id})
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    api_key_obj = APIKey(
        name=api_key_data.name,
        description=api_key_data.description,
        business_id=business_id,
        permissions=api_key_data.permissions
    )
    
    await db.api_keys.insert_one(api_key_obj.dict())
    return api_key_obj

@api_router.get("/dev/api-keys", response_model=List[APIKey])
async def get_business_api_keys(business_id: str):
    """Get all API keys for a business"""
    api_keys = await db.api_keys.find({"business_id": business_id}).to_list(100)
    return [APIKey(**api_key) for api_key in api_keys]

@api_router.get("/dev/sdk")
async def get_sdk_information():
    """Get SDK and integration information"""
    return {
        "sdks": {
            "javascript": {
                "name": "ImpactLink JS SDK",
                "version": "1.0.0",
                "install": "npm install @impactlink/js-sdk",
                "docs": "https://docs.impactlink.com/sdk/javascript"
            },
            "python": {
                "name": "ImpactLink Python SDK",
                "version": "1.0.0",
                "install": "pip install impactlink-python",
                "docs": "https://docs.impactlink.com/sdk/python"
            },
            "php": {
                "name": "ImpactLink PHP SDK",
                "version": "1.0.0",
                "install": "composer require impactlink/php-sdk",
                "docs": "https://docs.impactlink.com/sdk/php"
            }
        },
        "webhooks": {
            "description": "Get real-time notifications for contributions and transactions",
            "events": ["contribution.created", "transaction.created", "impact.milestone"],
            "setup": "Configure webhook URLs in your business dashboard"
        },
        "plugins": {
            "shopify": {
                "name": "ImpactLink for Shopify",
                "description": "Add social impact to your Shopify store",
                "install_url": "https://apps.shopify.com/impactlink"
            },
            "woocommerce": {
                "name": "ImpactLink for WooCommerce",
                "description": "WordPress plugin for WooCommerce stores",
                "install_url": "https://wordpress.org/plugins/impactlink"
            }
        }
    }

# Leaderboard endpoints (enhanced)
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
            "badges": business_obj.badges,
            "preferred_causes": business_obj.preferred_causes
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
            "badges": customer_obj.badges,
            "preferred_causes": customer_obj.preferred_causes
        })
    
    return {
        "metric": metric,
        "leaderboard": leaderboard
    }

# Badge endpoints (unchanged)
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

# Admin endpoints (enhanced)
@api_router.get("/admin/dashboard")
async def get_admin_dashboard():
    # Platform statistics
    total_businesses = await db.businesses.count_documents({})
    total_customers = await db.customers.count_documents({})
    total_causes = await db.causes.count_documents({"active": True})
    total_transactions = await db.transactions.count_documents({})
    total_contributions = await db.direct_contributions.count_documents({})
    anonymous_contributions = await db.direct_contributions.count_documents({"customer_id": None})
    
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
    
    # Payment method statistics
    payment_stats = await db.direct_contributions.aggregate([
        {"$group": {"_id": "$payment.method.type", "count": {"$sum": 1}, "total": {"$sum": "$amount"}}}
    ]).to_list(10)
    
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
            "anonymous_contributions": anonymous_contributions,
            "total_platform_impact": total_platform_impact,
            "business_impact": total_business_impact,
            "customer_contributions": total_customer_contributions
        },
        "payment_statistics": payment_stats,
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
        "badges": business_obj.badges,
        "preferred_causes": business_obj.preferred_causes
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
        "preferred_causes": business_obj.preferred_causes,
        "impact_message": f"Every purchase you make helps {business_obj.name} contribute to social causes!"
    }

# External API endpoints (enhanced)
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
    
    # Update last used timestamp for API key
    await db.businesses.update_one(
        {"api_key": credentials.credentials},
        {"$set": {"last_api_use": datetime.utcnow()}}
    )
    
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
async def get_external_causes(payment_method: Optional[str] = None):
    """Public API to get all active causes"""
    return await get_causes(active_only=True, payment_method=payment_method)

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