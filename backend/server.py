from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import random
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
# Backend URL for share links
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8000')

# Create the main app without a prefix
app = FastAPI(title="ImpactLink API", description="Social Impact Platform API", version="4.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer(auto_error=False)

def create_api_key():
    """Generate a simple API key for demo purposes"""
    return f"il_{uuid.uuid4().hex[:24]}"

def generate_account_number():
    """Generate a unique account number"""
    import random
    return f"IL{random.randint(1000000000, 9999999999)}"

# Enhanced Models
class PaymentMethod(BaseModel):
    type: str  # "card", "momo", "papss", "bank_transfer"
    provider: str  # "visa", "mastercard", "mtn_momo", "vodacom", "papss", "bank"
    details: Dict[str, Any] = Field(default_factory=dict)  # Store payment-specific details

class SettlementInfo(BaseModel):
    account_number: Optional[str] = None
    phone_number: Optional[str] = None
    bank_name: Optional[str] = None
    bank_code: Optional[str] = None
    account_type: str = "savings"  # savings, checking, momo
    verified: bool = False

class Subscription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_type: str  # "customer" or "business"
    plan_type: str  # "monthly", "yearly", "premium"
    amount: float
    currency: str = "USD"
    status: str = "active"  # active, paused, cancelled, expired
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: datetime
    auto_renew: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SubscriptionCreate(BaseModel):
    plan_type: str
    auto_renew: bool = True

class Customer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    phone: Optional[str] = None
    account_number: str = Field(default_factory=generate_account_number)
    preferred_causes: List[str] = Field(default_factory=list)  # cause IDs
    payment_methods: List[PaymentMethod] = Field(default_factory=list)
    settlement_info: Optional[SettlementInfo] = None
    total_contributions: float = 0.0
    contribution_count: int = 0
    badges: List[str] = Field(default_factory=list)
    subscription: Optional[Subscription] = None
    notification_preferences: Dict[str, bool] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_contribution: Optional[datetime] = None

class CustomerCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    preferred_causes: List[str] = Field(default_factory=list)
    settlement_info: Optional[SettlementInfo] = None

class Business(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    industry: str
    email: str
    phone: Optional[str] = None
    website: Optional[str] = None
    account_number: str = Field(default_factory=generate_account_number)
    api_key: str = Field(default_factory=create_api_key)
    preferred_causes: List[str] = Field(default_factory=list)  # cause IDs they want to support
    impact_allocations: Dict[str, float] = Field(default_factory=dict)
    settlement_info: Optional[SettlementInfo] = None
    total_sales: float = 0.0
    total_impact: float = 0.0
    transaction_count: int = 0
    badges: List[str] = Field(default_factory=list)
    subscription: Optional[Subscription] = None
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
    settlement_info: Optional[SettlementInfo] = None

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
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    creator_id: str  # ID of business or customer who created this cause
    creator_type: str  # "business" or "customer"
    creator_name: str
    creator_website: Optional[str] = None
    active: bool = True
    expired: bool = False
    featured: bool = False
    payment_methods_accepted: List[str] = Field(default_factory=lambda: ["card", "momo", "papss", "bank_transfer"])
    volunteer_opportunities: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CauseCreate(BaseModel):
    name: str
    description: str
    category: str
    image_url: Optional[str] = None
    impact_metric: str
    cost_per_impact: float
    goal_amount: Optional[float] = None
    end_date: Optional[datetime] = None
    creator_id: str
    creator_type: str
    payment_methods_accepted: List[str] = Field(default_factory=lambda: ["card", "momo", "papss", "bank_transfer"])
    volunteer_opportunities: List[str] = Field(default_factory=list)

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
    is_subscription: bool = False
    subscription_id: Optional[str] = None
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

# Enhanced Settlement and Payment Models
class CauseSettlement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cause_id: str
    total_donations_received: float = 0.0
    last_settlement_date: Optional[datetime] = None
    pending_amount: float = 0.0
    total_settled: float = 0.0
    settlement_account_info: Optional[SettlementInfo] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SettlementPayment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cause_id: str
    settlement_id: str
    amount: float
    payment_method: PaymentMethod
    status: str = "initiated"  # initiated, processing, completed, failed
    initiated_by: str  # admin user id
    payment_reference: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class UserCauseCreate(BaseModel):
    name: str
    description: str
    category: str
    impact_metric: str
    cost_per_impact: float
    goal_amount: float
    end_date: datetime
    image_url: Optional[str] = None
    payment_methods_accepted: List[str] = Field(default_factory=lambda: ["card", "momo", "bank_transfer"])
    volunteer_opportunities: List[str] = Field(default_factory=list)
    settlement_info: SettlementInfo

# Social Features Models
class CauseComment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cause_id: str
    user_id: str
    user_name: str
    user_type: str  # customer, business, admin
    comment: str
    parent_comment_id: Optional[str] = None  # For replies
    is_admin_response: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class CommentCreate(BaseModel):
    comment: str
    parent_comment_id: Optional[str] = None
    user_id: str
    user_type: str

class EmojiReaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cause_id: str
    user_id: str
    user_name: str
    emoji: str  # ❤️, 👍, 🎉, 😢, 😡, etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EmojiReactionCreate(BaseModel):
    emoji: str
    user_id: str
    user_type: str

class CauseShare(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cause_id: str
    share_url: str
    shared_by: Optional[str] = None
    platform: Optional[str] = None  # facebook, twitter, email, link
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Subscription plans
SUBSCRIPTION_PLANS = {
    "individual": {
        "monthly": {"price": 9.99, "features": ["unlimited_donations", "priority_support", "impact_reports"]},
        "yearly": {"price": 99.99, "features": ["unlimited_donations", "priority_support", "impact_reports", "exclusive_causes"]},
        "premium": {"price": 199.99, "features": ["all_features", "personal_cause_creation", "advanced_analytics"]}
    },
    "business": {
        "monthly": {"price": 49.99, "features": ["api_access", "custom_branding", "analytics"]},
        "yearly": {"price": 499.99, "features": ["api_access", "custom_branding", "analytics", "priority_processing"]},
        "premium": {"price": 999.99, "features": ["all_features", "white_label", "dedicated_support"]}
    }
}

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
        payment.status = "completed" if amount <= 10000 else "failed"
        payment.gateway_response = {
            "processor": "stripe",
            "card_last4": payment_method.details.get("last4", "1234"),
            "card_brand": payment_method.details.get("brand", "visa")
        }
    elif payment_method.type == "momo":
        payment.status = "completed"
        payment.gateway_response = {
            "processor": payment_method.provider,
            "phone": payment_method.details.get("phone", "+1234567890"),
            "reference": f"momo_{uuid.uuid4().hex[:8]}"
        }
    elif payment_method.type == "papss":
        payment.status = "completed"
        payment.gateway_response = {
            "processor": "papss",
            "bank_code": payment_method.details.get("bank_code", "001"),
            "reference": f"papss_{uuid.uuid4().hex[:8]}"
        }
    elif payment_method.type == "bank_transfer":
        payment.status = "completed"
        payment.gateway_response = {
            "processor": "bank",
            "account_number": payment_method.details.get("account_number", "*****1234"),
            "bank_name": payment_method.details.get("bank_name", "Example Bank")
        }
    
    if payment.status == "completed":
        payment.completed_at = datetime.utcnow()
    
    return payment

# Check if cause is expired
async def check_cause_expiry():
    """Check and mark expired causes"""
    now = datetime.utcnow()
    await db.causes.update_many(
        {"end_date": {"$lt": now}, "expired": False},
        {"$set": {"expired": True, "active": False}}
    )

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
    "cause_creator": Badge(
        id="cause_creator",
        name="Cause Creator",
        description="Created your first cause",
        icon="🎯",
        criteria={"type": "causes_created", "value": 1},
        rarity="epic"
    ),
    "subscriber": Badge(
        id="subscriber",
        name="Subscriber",
        description="Active platform subscriber",
        icon="⭐",
        criteria={"type": "subscription", "value": 1},
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
            payment_methods_count = len(user_data.get("payment_methods", []))
            criteria_met = payment_methods_count >= criteria["value"]
        elif criteria["type"] == "subscription":
            criteria_met = user_data.get("subscription") is not None
        
        if criteria_met:
            # Award badge
            collection = db.customers if user_type == "customer" else db.businesses
            await collection.update_one(
                {"id": user_id},
                {"$addToSet": {"badges": badge_id}}
            )
            awarded_badges.append(badge)
    
    return awarded_badges

# Initialize default data with demo users
async def init_default_data():
    # Check and mark expired causes
    await check_cause_expiry()
    
    # Initialize causes with demo users as creators
    existing_causes = await db.causes.count_documents({})
    if existing_causes == 0:
        # Create demo business first
        demo_business_id = str(uuid.uuid4())
        demo_business = {
            "id": demo_business_id,
            "name": "EcoTech Solutions",
            "description": "Sustainable technology company committed to environmental impact",
            "industry": "Technology",
            "email": "demo@ecotech.com",
            "phone": "+1-555-0100",
            "website": "https://ecotech-demo.com",
            "account_number": generate_account_number(),
            "api_key": create_api_key(),
            "preferred_causes": [],
            "impact_allocations": {},
            "settlement_info": {
                "account_number": "1234567890",
                "phone_number": "+1-555-0100",
                "bank_name": "Demo Bank",
                "bank_code": "DEMO001",
                "account_type": "checking",
                "verified": True
            },
            "total_sales": 15000.0,
            "total_impact": 1500.0,
            "transaction_count": 25,
            "badges": ["business_pioneer"],
            "verified": True,
            "created_at": datetime.utcnow()
        }
        await db.businesses.insert_one(demo_business)
        
        # Create demo customer
        demo_customer_id = str(uuid.uuid4())
        demo_customer = {
            "id": demo_customer_id,
            "name": "Sarah Green",
            "email": "sarah@demo.com",
            "phone": "+1-555-0200",
            "account_number": generate_account_number(),
            "preferred_causes": [],
            "payment_methods": [],
            "settlement_info": {
                "phone_number": "+1-555-0200",
                "account_type": "momo",
                "verified": True
            },
            "total_contributions": 750.0,
            "contribution_count": 15,
            "badges": ["first_contribution", "generous_giver"],
            "notification_preferences": {},
            "created_at": datetime.utcnow(),
            "last_contribution": datetime.utcnow()
        }
        await db.customers.insert_one(demo_customer)
        
        # Default causes with demo creators
        default_causes = [
            {
                "id": str(uuid.uuid4()),
                "name": "Education for All",
                "description": "Providing quality education access to underprivileged children worldwide",
                "category": "Education",
                "image_url": "https://images.pexels.com/photos/2219024/pexels-photo-2219024.jpeg",
                "impact_metric": "children educated for 1 month",
                "cost_per_impact": 25.0,
                "total_raised": 2500.0,
                "total_impact_units": 100.0,
                "goal_amount": 10000.0,
                "start_date": datetime.utcnow(),
                "end_date": datetime.utcnow() + timedelta(days=90),
                "creator_id": demo_business_id,
                "creator_type": "business",
                "creator_name": "EcoTech Solutions",
                "creator_website": "https://ecotech-demo.com",
                "active": True,
                "expired": False,
                "featured": True,
                "payment_methods_accepted": ["card", "momo", "papss", "bank_transfer"],
                "volunteer_opportunities": ["tutoring", "curriculum_development"],
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
                "total_raised": 1800.0,
                "total_impact_units": 36.0,
                "goal_amount": 25000.0,
                "start_date": datetime.utcnow(),
                "end_date": datetime.utcnow() + timedelta(days=180),
                "creator_id": demo_customer_id,
                "creator_type": "customer",
                "creator_name": "Sarah Green",
                "creator_website": None,
                "active": True,
                "expired": False,
                "featured": True,
                "payment_methods_accepted": ["card", "momo", "papss", "bank_transfer"],
                "volunteer_opportunities": ["water_testing", "community_outreach"],
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Forest Restoration",
                "description": "Planting trees and restoring damaged ecosystems",
                "category": "Environment",
                "impact_metric": "trees planted",
                "cost_per_impact": 2.0,
                "total_raised": 500.0,
                "total_impact_units": 250.0,
                "goal_amount": 5000.0,
                "start_date": datetime.utcnow(),
                "end_date": datetime.utcnow() + timedelta(days=60),
                "creator_id": demo_business_id,
                "creator_type": "business",
                "creator_name": "EcoTech Solutions",
                "creator_website": "https://ecotech-demo.com",
                "active": True,
                "expired": False,
                "featured": False,
                "payment_methods_accepted": ["card", "momo", "papss"],
                "volunteer_opportunities": ["tree_planting", "site_monitoring"],
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Food Security Program",
                "description": "Providing nutritious meals to families in need",
                "category": "Poverty",
                "impact_metric": "meals provided",
                "cost_per_impact": 3.0,
                "total_raised": 900.0,
                "total_impact_units": 300.0,
                "goal_amount": 15000.0,
                "start_date": datetime.utcnow(),
                "end_date": datetime.utcnow() + timedelta(days=120),
                "creator_id": demo_customer_id,
                "creator_type": "customer",
                "creator_name": "Sarah Green",
                "creator_website": None,
                "active": True,
                "expired": False,
                "featured": True,
                "payment_methods_accepted": ["card", "momo", "bank_transfer"],
                "volunteer_opportunities": ["meal_preparation", "delivery"],
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Mental Health Support",
                "description": "Providing counseling and mental health resources",
                "category": "Health",
                "impact_metric": "therapy sessions provided",
                "cost_per_impact": 75.0,
                "total_raised": 3000.0,
                "total_impact_units": 40.0,
                "goal_amount": 20000.0,
                "start_date": datetime.utcnow() - timedelta(days=10),
                "end_date": datetime.utcnow() + timedelta(days=5),  # Expiring soon
                "creator_id": demo_business_id,
                "creator_type": "business",
                "creator_name": "EcoTech Solutions",
                "creator_website": "https://ecotech-demo.com",
                "active": True,
                "expired": False,
                "featured": False,
                "payment_methods_accepted": ["card", "papss", "bank_transfer"],
                "volunteer_opportunities": ["peer_support", "awareness_campaigns"],
                "created_at": datetime.utcnow() - timedelta(days=10)
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Digital Literacy Program",
                "description": "Teaching digital skills to underserved communities",
                "category": "Education",
                "impact_metric": "people trained",
                "cost_per_impact": 30.0,
                "total_raised": 600.0,
                "total_impact_units": 20.0,
                "goal_amount": 8000.0,
                "start_date": datetime.utcnow() - timedelta(days=30),
                "end_date": datetime.utcnow() - timedelta(days=1),  # Expired
                "creator_id": demo_customer_id,
                "creator_type": "customer",
                "creator_name": "Sarah Green",
                "creator_website": None,
                "active": False,
                "expired": True,
                "featured": False,
                "payment_methods_accepted": ["card", "momo"],
                "volunteer_opportunities": ["teaching", "curriculum_design"],
                "created_at": datetime.utcnow() - timedelta(days=30)
            }
        ]
        
        for cause in default_causes:
            await db.causes.insert_one(cause)

    # Create default admin users
    existing_admin = await db.admin_users.count_documents({})
    if existing_admin == 0:
        admin_users = [
            {
                "id": str(uuid.uuid4()),
                "username": "admin",
                "email": "admin@impactlink.com",
                "role": "admin",
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "username": "demo_admin",
                "email": "demo.admin@impactlink.com",
                "role": "admin",
                "created_at": datetime.utcnow()
            }
        ]
        for admin in admin_users:
            await db.admin_users.insert_one(admin)

# Enhanced Cause endpoints
@api_router.get("/causes", response_model=List[Cause])
async def get_causes(
    active_only: bool = True,
    featured_only: bool = False,
    payment_method: Optional[str] = None,
    category: Optional[str] = None,
    creator_type: Optional[str] = None,
    expired: Optional[bool] = None,
    sort_by: str = "created_at",  # created_at, total_raised, end_date
    sort_order: str = "desc"  # asc, desc
):
    # Check and update expired causes
    await check_cause_expiry()
    
    query = {}
    if active_only and expired is None:
        query["active"] = True
    if featured_only:
        query["featured"] = True
    if payment_method:
        query["payment_methods_accepted"] = payment_method
    if category:
        query["category"] = category
    if creator_type:
        query["creator_type"] = creator_type
    if expired is not None:
        query["expired"] = expired
    
    # Sorting
    sort_direction = -1 if sort_order == "desc" else 1
    
    causes = await db.causes.find(query).sort(sort_by, sort_direction).to_list(1000)
    
    # Filter out causes that don't have required fields and convert to Cause objects
    valid_causes = []
    for cause in causes:
        try:
            # Ensure required fields exist
            if "creator_id" not in cause:
                cause["creator_id"] = "unknown"
            if "creator_type" not in cause:
                cause["creator_type"] = "unknown"
            if "creator_name" not in cause:
                cause["creator_name"] = "Unknown Creator"
            if "creator_website" not in cause:
                cause["creator_website"] = None
                
            valid_causes.append(Cause(**cause))
        except Exception as e:
            print(f"Error processing cause {cause.get('id', 'unknown')}: {e}")
            continue
            
    return valid_causes

@api_router.get("/causes/{cause_id}", response_model=Cause)
async def get_cause(cause_id: str):
    cause = await db.causes.find_one({"id": cause_id})
    if not cause:
        raise HTTPException(status_code=404, detail="Cause not found")
    return Cause(**cause)

@api_router.post("/causes", response_model=Cause)
async def create_cause(cause: CauseCreate):
    # Verify creator exists
    creator_collection = db.businesses if cause.creator_type == "business" else db.customers
    creator = await creator_collection.find_one({"id": cause.creator_id})
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")
    
    cause_dict = cause.dict()
    cause_dict["creator_name"] = creator["name"]
    if cause.creator_type == "business" and creator.get("website"):
        cause_dict["creator_website"] = creator["website"]
    
    cause_obj = Cause(**cause_dict)
    await db.causes.insert_one(cause_obj.dict())
    
    # Award cause creator badge
    await check_and_award_badges(cause.creator_type, cause.creator_id, creator)
    
    return cause_obj

# Enhanced direct contribution endpoints with expiry check
@api_router.post("/contributions", response_model=DirectContribution)
async def create_direct_contribution(contribution: DirectContributionCreate):
    # Verify cause exists and is not expired
    cause = await db.causes.find_one({"id": contribution.cause_id})
    if not cause:
        raise HTTPException(status_code=404, detail="Cause not found")
    
    cause_obj = Cause(**cause)
    
    # Check if cause is expired
    if cause_obj.expired or (cause_obj.end_date and cause_obj.end_date < datetime.utcnow()):
        raise HTTPException(status_code=400, detail="This cause has expired and no longer accepts contributions")
    
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

# Subscription endpoints
@api_router.post("/subscriptions", response_model=Subscription)
async def create_subscription(subscription_data: SubscriptionCreate, user_id: str, user_type: str):
    if user_type not in ["customer", "business"]:
        raise HTTPException(status_code=400, detail="Invalid user type")
    
    # Get user
    collection = db.customers if user_type == "customer" else db.businesses
    user = await collection.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user already has an active subscription
    if user.get("subscription") and user["subscription"]["status"] == "active":
        raise HTTPException(status_code=400, detail="User already has an active subscription")
    
    # Get plan details
    plan_category = "individual" if user_type == "customer" else "business"
    if subscription_data.plan_type not in SUBSCRIPTION_PLANS[plan_category]:
        raise HTTPException(status_code=400, detail="Invalid plan type")
    
    plan_details = SUBSCRIPTION_PLANS[plan_category][subscription_data.plan_type]
    
    # Calculate end date based on plan type
    if subscription_data.plan_type == "monthly":
        end_date = datetime.utcnow() + timedelta(days=30)
    elif subscription_data.plan_type == "yearly":
        end_date = datetime.utcnow() + timedelta(days=365)
    elif subscription_data.plan_type == "premium":
        end_date = datetime.utcnow() + timedelta(days=365)
    
    # Create subscription
    subscription_obj = Subscription(
        user_id=user_id,
        user_type=user_type,
        plan_type=subscription_data.plan_type,
        amount=plan_details["price"],
        end_date=end_date,
        auto_renew=subscription_data.auto_renew
    )
    
    await db.subscriptions.insert_one(subscription_obj.dict())
    
    # Update user with subscription
    await collection.update_one(
        {"id": user_id},
        {"$set": {"subscription": subscription_obj.dict()}}
    )
    
    # Award subscriber badge
    await check_and_award_badges(user_type, user_id, user)
    
    return subscription_obj

@api_router.get("/subscriptions/{user_id}")
async def get_user_subscription(user_id: str, user_type: str):
    collection = db.customers if user_type == "customer" else db.businesses
    user = await collection.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user.get("subscription", None)

@api_router.get("/subscription-plans")
async def get_subscription_plans():
    return SUBSCRIPTION_PLANS

# Enhanced leaderboard endpoints with cause-specific data
@api_router.get("/leaderboards/businesses")
async def get_business_leaderboard(metric: str = "total_impact", limit: int = 10):
    valid_metrics = ["total_impact", "total_sales", "transaction_count"]
    if metric not in valid_metrics:
        raise HTTPException(status_code=400, detail=f"Invalid metric. Choose from: {valid_metrics}")
    
    businesses = await db.businesses.find().sort(metric, -1).limit(limit).to_list(limit)
    
    leaderboard = []
    for rank, business in enumerate(businesses, 1):
        business_obj = Business(**business)
        
        # Get cause breakdown for this business
        causes_supported = []
        for cause_id in business_obj.preferred_causes:
            cause = await db.causes.find_one({"id": cause_id})
            if cause:
                causes_supported.append({
                    "id": cause["id"],
                    "name": cause["name"],
                    "category": cause["category"]
                })
        
        leaderboard.append({
            "rank": rank,
            "business": business_obj,
            "metric_value": getattr(business_obj, metric),
            "badges": business_obj.badges,
            "causes_supported": causes_supported,
            "settlement_info": business_obj.settlement_info
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
        
        # Get contribution breakdown by cause
        contributions_by_cause = await db.direct_contributions.aggregate([
            {"$match": {"customer_id": customer["id"]}},
            {"$group": {
                "_id": "$cause_id",
                "total_amount": {"$sum": "$amount"},
                "count": {"$sum": 1}
            }}
        ]).to_list(100)
        
        cause_breakdown = []
        for contrib in contributions_by_cause:
            cause = await db.causes.find_one({"id": contrib["_id"]})
            if cause:
                cause_breakdown.append({
                    "cause_name": cause["name"],
                    "category": cause["category"],
                    "total_contributed": contrib["total_amount"],
                    "contribution_count": contrib["count"]
                })
        
        leaderboard.append({
            "rank": rank,
            "customer": customer_obj,
            "metric_value": getattr(customer_obj, metric),
            "badges": customer_obj.badges,
            "cause_breakdown": cause_breakdown,
            "settlement_info": customer_obj.settlement_info
        })
    
    return {
        "metric": metric,
        "leaderboard": leaderboard
    }

@api_router.get("/leaderboards/causes")
async def get_cause_leaderboard(metric: str = "total_raised", limit: int = 10):
    valid_metrics = ["total_raised", "total_impact_units"]
    if metric not in valid_metrics:
        raise HTTPException(status_code=400, detail=f"Invalid metric. Choose from: {valid_metrics}")
    
    causes = await db.causes.find().sort(metric, -1).limit(limit).to_list(limit)
    
    leaderboard = []
    for rank, cause in enumerate(causes, 1):
        try:
            # Ensure required fields exist
            if "creator_id" not in cause:
                cause["creator_id"] = "unknown"
            if "creator_type" not in cause:
                cause["creator_type"] = "unknown"
            if "creator_name" not in cause:
                cause["creator_name"] = "Unknown Creator"
            if "creator_website" not in cause:
                cause["creator_website"] = None
                
            cause_obj = Cause(**cause)
            
            # Get contribution breakdown for this cause
            contributions = await db.direct_contributions.find({"cause_id": cause["id"]}).to_list(1000)
            
            contributor_stats = {
                "total_contributors": len(set([c.get("customer_id") for c in contributions if c.get("customer_id")])),
                "anonymous_contributions": len([c for c in contributions if not c.get("customer_id")]),
                "recent_contributions": len([c for c in contributions if datetime.fromisoformat(c["timestamp"].replace('Z', '+00:00')) > datetime.utcnow() - timedelta(days=7)])
            }
            
            leaderboard.append({
                "rank": rank,
                "cause": cause_obj,
                "metric_value": getattr(cause_obj, metric),
                "contributor_stats": contributor_stats,
                "progress_percentage": (cause_obj.total_raised / cause_obj.goal_amount * 100) if cause_obj.goal_amount else 0
            })
        except Exception as e:
            print(f"Error processing cause {cause.get('id', 'unknown')} in leaderboard: {e}")
            continue
    
    return {
        "metric": metric,
        "leaderboard": leaderboard
    }

# Customer endpoints (enhanced with settlement info)
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

@api_router.put("/customers/{customer_id}/settlement")
async def update_customer_settlement(customer_id: str, settlement_info: SettlementInfo):
    """Update customer settlement information"""
    customer = await db.customers.find_one({"id": customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    await db.customers.update_one(
        {"id": customer_id},
        {"$set": {"settlement_info": settlement_info.dict()}}
    )
    
    return {"message": "Settlement information updated successfully"}

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

@api_router.put("/businesses/{business_id}/settlement")
async def update_business_settlement(business_id: str, settlement_info: SettlementInfo):
    """Update business settlement information"""
    business = await db.businesses.find_one({"id": business_id})
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    await db.businesses.update_one(
        {"id": business_id},
        {"$set": {"settlement_info": settlement_info.dict()}}
    )
    
    return {"message": "Settlement information updated successfully"}

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

# Transaction endpoints (unchanged)
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
        "version": "4.0",
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
                "PUT /api/businesses/{id}/impact-allocation": "Set impact allocation percentages",
                "PUT /api/businesses/{id}/settlement": "Update settlement information"
            },
            "causes": {
                "GET /api/causes": "List all causes with filtering and sorting",
                "POST /api/causes": "Create a new cause",
                "GET /api/causes/{id}": "Get detailed cause information"
            },
            "transactions": {
                "POST /api/transactions": "Record a new transaction with automatic impact calculation",
                "GET /api/transactions": "List all transactions for a business"
            },
            "contributions": {
                "POST /api/contributions": "Create direct contribution (supports anonymous)",
                "GET /api/contributions": "List contributions with filters"
            },
            "subscriptions": {
                "POST /api/subscriptions": "Create user subscription",
                "GET /api/subscriptions/{user_id}": "Get user subscription details"
            },
            "leaderboards": {
                "GET /api/leaderboards/businesses": "Business leaderboard",
                "GET /api/leaderboards/customers": "Customer leaderboard",
                "GET /api/leaderboards/causes": "Cause performance leaderboard"
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
            },
            "create_cause": {
                "url": "POST /api/causes",
                "body": {
                    "name": "Education Initiative",
                    "description": "Supporting education in rural areas",
                    "category": "Education",
                    "impact_metric": "students supported",
                    "cost_per_impact": 30.0,
                    "goal_amount": 10000.0,
                    "end_date": "2025-12-31T23:59:59Z",
                    "creator_id": "business_or_customer_id",
                    "creator_type": "business"
                }
            }
        }
    }

@api_router.post("/dev/api-keys", response_model=APIKey)
async def create_api_key_endpoint(api_key_data: APIKeyCreate, business_id: str):
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
            "events": ["contribution.created", "transaction.created", "impact.milestone", "cause.expired"],
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

@api_router.get("/dev/code-examples")
async def get_code_examples():
    """Get code examples for different programming languages"""
    return {
        "javascript": {
            "install": "npm install @impactlink/js-sdk",
            "setup": """
const ImpactLink = require('@impactlink/js-sdk');
const client = new ImpactLink({
    apiKey: 'your_api_key_here',
    sandbox: true // Use sandbox for testing
});
            """,
            "create_transaction": """
// Record a transaction with automatic impact allocation
const transaction = await client.transactions.create({
    amount: 100.00,
    customerName: 'John Doe',
    metadata: { orderId: 'ORDER_123' }
});

console.log(`Impact generated: $${transaction.totalImpact}`);
            """,
            "create_contribution": """
// Create direct contribution to a cause
const contribution = await client.contributions.create({
    causeId: 'cause_id_here',
    amount: 50.00,
    paymentMethod: {
        type: 'card',
        provider: 'visa',
        details: { token: 'payment_token_here' }
    },
    customerName: 'Jane Smith',
    message: 'Supporting this great cause!'
});
            """,
            "add_reaction": """
// Add emoji reaction to a cause
const reaction = await client.causes.addReaction('cause_id_here', {
    emoji: '❤️',
    userId: 'user_id_here'
});
            """,
            "add_comment": """
// Add comment to a cause
const comment = await client.causes.addComment('cause_id_here', {
    comment: 'This is an amazing cause!',
    userId: 'user_id_here',
    userType: 'customer'
});
            """
        },
        "python": {
            "install": "pip install impactlink-python",
            "setup": """
import impactlink

client = impactlink.Client(
    api_key='your_api_key_here',
    sandbox=True  # Use sandbox for testing
)
            """,
            "create_transaction": """
# Record a transaction with automatic impact allocation
transaction = client.transactions.create(
    amount=100.00,
    customer_name='John Doe',
    metadata={'order_id': 'ORDER_123'}
)

print(f"Impact generated: ${transaction.total_impact}")
            """,
            "create_contribution": """
# Create direct contribution to a cause
contribution = client.contributions.create(
    cause_id='cause_id_here',
    amount=50.00,
    payment_method={
        'type': 'card',
        'provider': 'visa',
        'details': {'token': 'payment_token_here'}
    },
    customer_name='Jane Smith',
    message='Supporting this great cause!'
)
            """,
            "webhook_handler": """
from flask import Flask, request
import impactlink

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    payload = request.get_json()
    
    if payload['event'] == 'transaction.created':
        # Handle new transaction
        print(f"New transaction: {payload['data']['transaction_id']}")
    elif payload['event'] == 'contribution.created':
        # Handle new contribution
        print(f"New contribution: {payload['data']['contribution_id']}")
    
    return {'status': 'received'}
            """,
            "add_reaction": """
# Add emoji reaction to a cause
reaction = client.causes.add_reaction(
    cause_id='cause_id_here',
    emoji='❤️',
    user_id='user_id_here'
)
            """,
            "add_comment": """
# Add comment to a cause
comment = client.causes.add_comment(
    cause_id='cause_id_here',
    comment='This is an amazing cause!',
    user_id='user_id_here',
    user_type='customer'
)
            """
        },
        "php": {
            "install": "composer require impactlink/php-sdk",
            "setup": """
<?php
require_once 'vendor/autoload.php';

use ImpactLink\\Client;

$client = new Client([
    'api_key' => 'your_api_key_here',
    'sandbox' => true
]);
            """,
            "create_transaction": """
// Record a transaction
$transaction = $client->transactions->create([
    'amount' => 100.00,
    'customer_name' => 'John Doe',
    'metadata' => ['order_id' => 'ORDER_123']
]);

echo "Impact generated: $" . $transaction->total_impact;
            """,
            "create_contribution": """
// Create direct contribution
$contribution = $client->contributions->create([
    'cause_id' => 'cause_id_here',
    'amount' => 50.00,
    'payment_method' => [
        'type' => 'card',
        'provider' => 'visa',
        'details' => ['token' => 'payment_token_here']
    ],
    'customer_name' => 'Jane Smith',
    'message' => 'Supporting this great cause!'
]);
            """,
            "webhook_handler": """
<?php
// webhook.php
$payload = json_decode(file_get_contents('php://input'), true);

if ($payload['event'] === 'transaction.created') {
    // Handle new transaction
    error_log("New transaction: " . $payload['data']['transaction_id']);
} elseif ($payload['event'] === 'contribution.created') {
    // Handle new contribution
    error_log("New contribution: " . $payload['data']['contribution_id']);
}

http_response_code(200);
echo json_encode(['status' => 'received']);
            """,
            "add_reaction": """
// Add emoji reaction to a cause
$reaction = $client->causes->addReaction('cause_id_here', [
    'emoji' => '❤️',
    'user_id' => 'user_id_here'
]);
            """,
            "add_comment": """
// Add comment to a cause
$comment = $client->causes->addComment('cause_id_here', [
    'comment' => 'This is an amazing cause!',
    'user_id' => 'user_id_here',
    'user_type' => 'customer'
]);
            """
        }
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

# Enhanced admin endpoints
@api_router.get("/admin/dashboard")
async def get_admin_dashboard():
    # Check and update expired causes
    await check_cause_expiry()
    
    # Platform statistics
    total_businesses = await db.businesses.count_documents({})
    total_customers = await db.customers.count_documents({})
    total_causes = await db.causes.count_documents({"active": True})
    expired_causes = await db.causes.count_documents({"expired": True})
    total_transactions = await db.transactions.count_documents({})
    total_contributions = await db.direct_contributions.count_documents({})
    anonymous_contributions = await db.direct_contributions.count_documents({"customer_id": None})
    active_subscriptions = await db.subscriptions.count_documents({"status": "active"})
    
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
    
    # Causes expiring soon
    soon_expiring = await db.causes.find({
        "end_date": {"$gte": datetime.utcnow(), "$lte": datetime.utcnow() + timedelta(days=7)},
        "active": True
    }).to_list(10)
    
    return {
        "statistics": {
            "total_businesses": total_businesses,
            "total_customers": total_customers,
            "total_causes": total_causes,
            "expired_causes": expired_causes,
            "total_transactions": total_transactions,
            "total_contributions": total_contributions,
            "anonymous_contributions": anonymous_contributions,
            "active_subscriptions": active_subscriptions,
            "total_platform_impact": total_platform_impact,
            "business_impact": total_business_impact,
            "customer_contributions": total_customer_contributions
        },
        "payment_statistics": payment_stats,
        "recent_activity": {
            "transactions": [Transaction(**t) for t in recent_transactions],
            "contributions": [DirectContribution(**c) for c in recent_contributions]
        },
        "top_causes": [Cause(**c) for c in top_causes],
        "expiring_soon": [Cause(**c) for c in soon_expiring]
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

@api_router.get("/admin/demo-users")
async def get_demo_users():
    """Get demo users for platform testing"""
    demo_business = await db.businesses.find_one({"name": "EcoTech Solutions"})
    demo_customer = await db.customers.find_one({"name": "Sarah Green"})
    demo_admins = await db.admin_users.find().to_list(10)
    
    return {
        "demo_business": Business(**demo_business) if demo_business else None,
        "demo_customer": Customer(**demo_customer) if demo_customer else None,
        "demo_admins": [AdminUser(**admin) for admin in demo_admins],
        "login_instructions": {
            "business": "Use EcoTech Solutions for business demo",
            "customer": "Use Sarah Green for customer demo",
            "admin": "Use admin or demo_admin for admin functions"
        }
    }

# Enhanced Admin Settlement Endpoints
@api_router.get("/admin/settlements")
async def get_cause_settlements():
    """Get settlement information for all causes with donation tracking"""
    # Get all causes
    causes = await db.causes.find({}).to_list(1000)
    settlements = []
    
    for cause in causes:
        try:
            # Ensure required fields exist
            if "creator_id" not in cause:
                cause["creator_id"] = "unknown"
            if "creator_type" not in cause:
                cause["creator_type"] = "unknown"
            if "creator_name" not in cause:
                cause["creator_name"] = "Unknown Creator"
            if "creator_website" not in cause:
                cause["creator_website"] = None
                
            cause_obj = Cause(**cause)
            
            # Calculate donations received from direct contributions
            contributions = await db.direct_contributions.find({"cause_id": cause["id"]}).to_list(1000)
            direct_donations = sum([c.get("amount", 0) for c in contributions])
            
            # Calculate donations from business transactions
            transactions = await db.transactions.find({}).to_list(1000)
            business_donations = 0
            for txn in transactions:
                if "impact_breakdown" in txn:
                    for cause_id, amount in txn["impact_breakdown"].items():
                        if cause_id == cause["id"]:
                            try:
                                business_donations += float(amount)
                            except (ValueError, TypeError):
                                continue
            
            total_donations = direct_donations + business_donations
            
            # Get existing settlement record or create new
            settlement = await db.cause_settlements.find_one({"cause_id": cause["id"]})
            if not settlement:
                settlement = {
                    "id": str(uuid.uuid4()),
                    "cause_id": cause["id"],
                    "total_donations_received": total_donations,
                    "last_settlement_date": None,
                    "pending_amount": total_donations,
                    "total_settled": 0.0,
                    "settlement_account_info": cause.get("settlement_info"),
                    "created_at": datetime.utcnow()
                }
                await db.cause_settlements.insert_one(settlement)
            else:
                # Update total donations
                settlement["total_donations_received"] = total_donations
                settlement["pending_amount"] = total_donations - settlement.get("total_settled", 0)
                await db.cause_settlements.update_one(
                    {"cause_id": cause["id"]},
                    {"$set": {
                        "total_donations_received": total_donations,
                        "pending_amount": settlement["pending_amount"]
                    }}
                )
            
            settlements.append({
                "cause": cause_obj,
                "settlement": CauseSettlement(**settlement),
                "direct_donations": direct_donations,
                "business_donations": business_donations,
                "total_donations": total_donations
            })
        except Exception as e:
            print(f"Error processing settlement for cause {cause.get('id', 'unknown')}: {e}")
            continue
    
    return {"settlements": settlements}

@api_router.post("/admin/settlements/{cause_id}/initiate-payment")
async def initiate_settlement_payment(cause_id: str, payment_data: dict):
    """Initiate payment to cause organization"""
    # Get cause settlement info
    settlement = await db.cause_settlements.find_one({"cause_id": cause_id})
    if not settlement:
        raise HTTPException(status_code=404, detail="Settlement record not found")
    
    if settlement["pending_amount"] <= 0:
        raise HTTPException(status_code=400, detail="No pending amount to settle")
    
    # Create settlement payment record
    settlement_payment = {
        "id": str(uuid.uuid4()),
        "cause_id": cause_id,
        "settlement_id": settlement["id"],
        "amount": settlement["pending_amount"],
        "payment_method": payment_data.get("payment_method", {"type": "bank_transfer", "provider": "bank"}),
        "status": "initiated",
        "initiated_by": payment_data.get("admin_id", "admin"),
        "payment_reference": f"SETTLE_{uuid.uuid4().hex[:8]}",
        "created_at": datetime.utcnow(),
        "completed_at": None
    }
    
    await db.settlement_payments.insert_one(settlement_payment)
    
    # Update settlement record
    await db.cause_settlements.update_one(
        {"cause_id": cause_id},
        {"$set": {
            "last_settlement_date": datetime.utcnow(),
            "total_settled": settlement["total_settled"] + settlement["pending_amount"],
            "pending_amount": 0.0
        }}
    )
    
    # Simulate payment processing (in real implementation, integrate with payment gateway)
    import asyncio
    await asyncio.sleep(0.1)  # Simulate processing time
    
    # Update payment status to completed
    await db.settlement_payments.update_one(
        {"id": settlement_payment["id"]},
        {"$set": {
            "status": "completed",
            "completed_at": datetime.utcnow()
        }}
    )
    
    return {
        "message": "Settlement payment initiated successfully",
        "payment_reference": settlement_payment["payment_reference"],
        "amount": settlement_payment["amount"],
        "status": "completed"
    }

# User Cause Creation Endpoints
@api_router.post("/users/{user_id}/causes", response_model=Cause)
async def create_user_cause(user_id: str, cause_data: UserCauseCreate, user_type: str):
    """Allow users to create their own causes"""
    
    # Validate user exists
    if user_type == "business":
        user = await db.businesses.find_one({"id": user_id})
        creator_name = user["name"] if user else "Unknown Business"
        creator_website = user.get("website") if user else None
    elif user_type == "customer":
        user = await db.customers.find_one({"id": user_id})
        creator_name = user["name"] if user else "Unknown Customer"
        creator_website = None
    else:
        raise HTTPException(status_code=400, detail="Invalid user type")
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create cause object
    cause = {
        "id": str(uuid.uuid4()),
        "name": cause_data.name,
        "description": cause_data.description,
        "category": cause_data.category,
        "image_url": cause_data.image_url or f"https://images.unsplash.com/photo-{random.randint(1400000000, 1600000000)}",
        "impact_metric": cause_data.impact_metric,
        "cost_per_impact": cause_data.cost_per_impact,
        "total_raised": 0.0,
        "total_impact_units": 0.0,
        "goal_amount": cause_data.goal_amount,
        "start_date": datetime.utcnow(),
        "end_date": cause_data.end_date,
        "creator_id": user_id,
        "creator_type": user_type,
        "creator_name": creator_name,
        "creator_website": creator_website,
        "active": True,
        "expired": False,
        "featured": False,
        "payment_methods_accepted": cause_data.payment_methods_accepted,
        "volunteer_opportunities": cause_data.volunteer_opportunities,
        "settlement_info": cause_data.settlement_info.dict(),
        "created_at": datetime.utcnow()
    }
    
    await db.causes.insert_one(cause)
    
    return Cause(**cause)

# Social Features Endpoints

@api_router.get("/causes/{cause_id}/share")
async def get_cause_share_url(cause_id: str):
    """Get shareable URL for a cause"""
    cause = await db.causes.find_one({"id": cause_id})
    if not cause:
        raise HTTPException(status_code=404, detail="Cause not found")
    
    share_url = f"{BACKEND_URL}/causes/{cause_id}"
    
    return {
        "cause_id": cause_id,
        "share_url": share_url,
        "social_links": {
            "facebook": f"https://www.facebook.com/sharer/sharer.php?u={share_url}",
            "twitter": f"https://twitter.com/intent/tweet?url={share_url}&text=Check out this amazing cause: {cause['name']}",
            "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={share_url}",
            "whatsapp": f"https://wa.me/?text=Check out this amazing cause: {cause['name']} {share_url}",
            "email": f"mailto:?subject=Check out this cause&body=I thought you might be interested in this cause: {cause['name']} - {share_url}"
        }
    }

@api_router.post("/causes/{cause_id}/share")
async def track_cause_share(cause_id: str, share_data: dict):
    """Track cause share activity"""
    cause = await db.causes.find_one({"id": cause_id})
    if not cause:
        raise HTTPException(status_code=404, detail="Cause not found")
    
    share_url = f"{BACKEND_URL}/causes/{cause_id}"
    
    share_record = {
        "id": str(uuid.uuid4()),
        "cause_id": cause_id,
        "share_url": share_url,
        "shared_by": share_data.get("user_id"),
        "platform": share_data.get("platform", "link"),
        "created_at": datetime.utcnow().isoformat()  # Convert to ISO format string
    }
    
    # Insert into database with datetime object
    db_record = share_record.copy()
    db_record["created_at"] = datetime.utcnow()  # Store as datetime in DB
    await db.cause_shares.insert_one(db_record)
    
    return {
        "message": "Share tracked successfully",
        "share_record": share_record,  # Returns with ISO format string
        "share_url": share_url,
        "social_links": {
            "facebook": f"https://www.facebook.com/sharer/sharer.php?u={share_url}",
            "twitter": f"https://twitter.com/intent/tweet?url={share_url}&text=Check out this amazing cause: {cause['name']}",
            "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={share_url}",
            "whatsapp": f"https://wa.me/?text=Check out this amazing cause: {cause['name']} {share_url}",
            "email": f"mailto:?subject=Check out this cause&body=I thought you might be interested in this cause: {cause['name']} - {share_url}"
        }
    }

@api_router.get("/causes/{cause_id}/comments")
async def get_cause_comments(cause_id: str):
    """Get all comments for a cause"""
    cause = await db.causes.find_one({"id": cause_id})
    if not cause:
        raise HTTPException(status_code=404, detail="Cause not found")
    
    comments = await db.cause_comments.find({"cause_id": cause_id}).sort("created_at", 1).to_list(1000)
    
    # Organize comments and replies
    organized_comments = []
    comment_map = {}
    
    for comment in comments:
        comment_obj = CauseComment(**comment)
        comment_map[comment_obj.id] = comment_obj
        
        if comment_obj.parent_comment_id is None:
            # Top-level comment
            organized_comments.append({
                "id": comment_obj.id,  # Add ID at the top level for easier access
                "comment": comment_obj,
                "replies": []
            })
    
    # Add replies to their parent comments
    for comment in comments:
        comment_obj = CauseComment(**comment)
        if comment_obj.parent_comment_id:
            # Find parent comment in organized structure
            for org_comment in organized_comments:
                if org_comment["comment"].id == comment_obj.parent_comment_id:
                    org_comment["replies"].append(comment_obj)
                    break
    
    return {
        "cause_id": cause_id,
        "comments": organized_comments,
        "total_comments": len(comments)
    }

@api_router.post("/causes/{cause_id}/comments")
async def create_cause_comment(cause_id: str, comment_data: CommentCreate):
    """Create a comment on a cause"""
    cause = await db.causes.find_one({"id": cause_id})
    if not cause:
        raise HTTPException(status_code=404, detail="Cause not found")
    
    # Get user information from comment data
    user_id = comment_data.user_id
    user_type = comment_data.user_type
    
    if user_type == "business":
        user = await db.businesses.find_one({"id": user_id})
        user_name = user["name"] if user else "Unknown Business"
    elif user_type == "customer":
        user = await db.customers.find_one({"id": user_id})
        user_name = user["name"] if user else "Unknown Customer"
    elif user_type == "admin":
        user = await db.admin_users.find_one({"id": user_id})
        user_name = user["username"] if user else "Admin"
    else:
        raise HTTPException(status_code=400, detail="Invalid user type")
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if this is an admin response (cause creator responding)
    is_admin_response = (cause["creator_id"] == user_id and cause["creator_type"] == user_type)
    
    comment = {
        "id": str(uuid.uuid4()),
        "cause_id": cause_id,
        "user_id": user_id,
        "user_name": user_name,
        "user_type": user_type,
        "comment": comment_data.comment,
        "parent_comment_id": comment_data.parent_comment_id,
        "is_admin_response": is_admin_response,
        "created_at": datetime.utcnow(),
        "updated_at": None
    }
    
    await db.cause_comments.insert_one(comment)
    
    return CauseComment(**comment)

@api_router.get("/causes/{cause_id}/reactions")
async def get_cause_reactions(cause_id: str):
    """Get emoji reactions for a cause"""
    cause = await db.causes.find_one({"id": cause_id})
    if not cause:
        raise HTTPException(status_code=404, detail="Cause not found")
    
    reactions = await db.emoji_reactions.find({"cause_id": cause_id}).to_list(1000)
    
    # Group reactions by emoji
    reaction_counts = {}
    user_reactions = {}
    
    for reaction in reactions:
        emoji = reaction["emoji"]
        user_id = reaction["user_id"]
        
        if emoji not in reaction_counts:
            reaction_counts[emoji] = 0
        reaction_counts[emoji] += 1
        
        # Track user reactions for checking if user already reacted
        user_reactions[user_id] = emoji
    
    return {
        "cause_id": cause_id,
        "reactions": reaction_counts,  # Adding the 'reactions' field as expected by testing
        "reaction_counts": reaction_counts,
        "total_reactions": len(reactions),
        "user_reactions": user_reactions
    }

@api_router.post("/causes/{cause_id}/reactions")
async def add_cause_reaction(cause_id: str, reaction_data: EmojiReactionCreate):
    """Add emoji reaction to a cause"""
    cause = await db.causes.find_one({"id": cause_id})
    if not cause:
        raise HTTPException(status_code=404, detail="Cause not found")
    
    # Get user information from reaction data
    user_id = reaction_data.user_id
    user_type = reaction_data.user_type
    
    if user_type == "business":
        user = await db.businesses.find_one({"id": user_id})
        user_name = user["name"] if user else "Unknown Business"
    elif user_type == "customer":
        user = await db.customers.find_one({"id": user_id})
        user_name = user["name"] if user else "Unknown Customer"
    else:
        raise HTTPException(status_code=400, detail="Invalid user type")
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user already has a reaction for this cause
    existing_reaction = await db.emoji_reactions.find_one({"cause_id": cause_id, "user_id": user_id})
    
    if existing_reaction:
        # Update existing reaction
        await db.emoji_reactions.update_one(
            {"cause_id": cause_id, "user_id": user_id},
            {"$set": {"emoji": reaction_data.emoji, "created_at": datetime.utcnow()}}
        )
        # Return the updated reaction
        updated_reaction = await db.emoji_reactions.find_one({"cause_id": cause_id, "user_id": user_id})
        return EmojiReaction(**updated_reaction)
    else:
        # Create new reaction
        reaction = {
            "id": str(uuid.uuid4()),
            "cause_id": cause_id,
            "user_id": user_id,
            "user_name": user_name,
            "emoji": reaction_data.emoji,
            "created_at": datetime.utcnow()
        }
        
        await db.emoji_reactions.insert_one(reaction)
        return EmojiReaction(**reaction)

@api_router.delete("/causes/{cause_id}/reactions")
async def remove_cause_reaction(cause_id: str, user_data: dict):
    """Remove user's emoji reaction from a cause"""
    user_id = user_data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    result = await db.emoji_reactions.delete_one({"cause_id": cause_id, "user_id": user_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Reaction not found")
    
    return {"message": "Reaction removed successfully"}

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
    
    # Initialize dictionaries for tracking contributions and breakdowns
    cause_breakdown = {}
    contributions_per_cause = {}
    
    for cause_id, percentage in business_obj.impact_allocations.items():
        cause = await db.causes.find_one({"id": cause_id})
        if cause:
            cause_obj = Cause(**cause)
            
            # Calculate business contributions via transactions
            business_contribution = (business_obj.total_sales * percentage) / 100
            
            # Calculate direct contributions to this cause
            direct_contributions = await db.direct_contributions.find({"cause_id": cause_id}).to_list(1000)
            direct_contribution_total = sum([c.get("amount", 0) for c in direct_contributions])
            
            # Calculate cause health metrics
            goal_amount = cause_obj.goal_amount if cause_obj.goal_amount else 1000  # Default goal
            progress_percentage = (cause_obj.total_raised / goal_amount * 100) if goal_amount > 0 else 0
            health_status = "excellent" if progress_percentage >= 80 else "good" if progress_percentage >= 50 else "needs_attention"
            
            contributions_per_cause[cause_id] = {
                "cause_name": cause_obj.name,
                "business_contribution": business_contribution,
                "direct_contributions": direct_contribution_total,
                "total_raised": cause_obj.total_raised,
                "goal_amount": goal_amount,
                "progress_percentage": progress_percentage,
                "health_status": health_status,
                "impact_units": cause_obj.total_impact_units
            }
            
            cause_breakdown[cause_id] = {
                "name": cause_obj.name,
                "percentage": percentage,
                "category": cause_obj.category,
                "impact_metric": cause_obj.impact_metric,
                "total_contribution": business_contribution,
                "expired": cause_obj.expired,
                "amount": business_contribution,
                "impact_units": business_contribution / cause_obj.cost_per_impact if cause_obj.cost_per_impact > 0 else 0
            }
    
    return {
        "business": business_obj,
        "recent_transactions": [Transaction(**t) for t in recent_transactions],
        "cause_breakdown": cause_breakdown,
        "contributions_per_cause": contributions_per_cause,  # Enhanced field
        "total_sales": business_obj.total_sales,
        "total_impact": business_obj.total_impact,
        "impact_percentage": (business_obj.total_impact / business_obj.total_sales * 100) if business_obj.total_sales > 0 else 0,
        "badges": business_obj.badges,
        "preferred_causes": business_obj.preferred_causes,
        "settlement_info": business_obj.settlement_info
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
        "website": business_obj.website,
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