"""
Multi-tier Pricing System Models
Support for different customer types with tiered pricing based on usage volume
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum
import uuid


class CustomerTier(str, Enum):
    RESIDENTIAL = "residential"  # Rumah tinggal
    COMMERCIAL = "commercial"  # Toko, kantor
    INDUSTRIAL = "industrial"  # Pabrik, industri
    PRIVATE_HOME = "private_home"  # Rumah pribadi


class PricingModel(str, Enum):
    FLAT_RATE = "flat_rate"  # Tarif tetap per m³
    TIERED = "tiered"  # Tarif bertingkat berdasarkan volume
    PROGRESSIVE = "progressive"  # Tarif naik per blok


# Price Tier Range Model (for tiered/progressive pricing)
class PriceTierRange(BaseModel):
    min_volume: float  # Minimum m³ (inclusive)
    max_volume: Optional[float] = None  # Maximum m³ (None = unlimited)
    price_per_unit: float  # IDR per m³
    description: Optional[str] = None


# Main Pricing Tier Model
class PricingTierBase(BaseModel):
    tier_name: str  # e.g., "Residential - Standard"
    customer_tier: CustomerTier
    pricing_model: PricingModel
    
    # For flat_rate model
    flat_rate: Optional[float] = None  # IDR per m³
    
    # For tiered/progressive models
    price_ranges: Optional[List[PriceTierRange]] = []
    
    # Additional charges
    admin_fee: float = 0.0  # Monthly admin fee (IDR)
    minimum_charge: float = 0.0  # Minimum monthly charge (IDR)
    
    # Metadata
    description: Optional[str] = None
    is_active: bool = True
    effective_date: datetime = Field(default_factory=datetime.utcnow)


class PricingTierCreate(PricingTierBase):
    pass


class PricingTierUpdate(BaseModel):
    tier_name: Optional[str] = None
    pricing_model: Optional[PricingModel] = None
    flat_rate: Optional[float] = None
    price_ranges: Optional[List[PriceTierRange]] = None
    admin_fee: Optional[float] = None
    minimum_charge: Optional[float] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    effective_date: Optional[datetime] = None


class PricingTier(PricingTierBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Bill Calculation Models
class BillCalculationRequest(BaseModel):
    customer_tier: CustomerTier
    usage_volume: float  # m³
    pricing_tier_id: Optional[str] = None  # If not provided, use default for tier


class BillCalculationResult(BaseModel):
    customer_tier: CustomerTier
    usage_volume: float  # m³
    pricing_tier_id: str
    pricing_tier_name: str
    pricing_model: PricingModel
    
    # Breakdown
    breakdown: List[dict]  # [{range: "0-10 m³", volume: 10, rate: 5000, subtotal: 50000}]
    
    # Totals
    water_charge: float  # Total water cost
    admin_fee: float
    minimum_charge: float
    total_before_tax: float
    tax: float = 0.0  # PPN 11%
    total_amount: float  # Final bill


# Customer Tier Assignment Model
class CustomerTierAssignment(BaseModel):
    customer_id: str
    customer_tier: CustomerTier
    pricing_tier_id: Optional[str] = None  # Custom pricing, if None use default
    assigned_by: str  # user_id
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None


# Default Pricing Tiers for Indonesia Water Utility
DEFAULT_PRICING_TIERS = [
    {
        "tier_name": "Residential - Subsidized",
        "customer_tier": "residential",
        "pricing_model": "tiered",
        "price_ranges": [
            {"min_volume": 0, "max_volume": 10, "price_per_unit": 1500, "description": "0-10 m³ (Blok I)"},
            {"min_volume": 10, "max_volume": 20, "price_per_unit": 2000, "description": "11-20 m³ (Blok II)"},
            {"min_volume": 20, "max_volume": 30, "price_per_unit": 3000, "description": "21-30 m³ (Blok III)"},
            {"min_volume": 30, "max_volume": None, "price_per_unit": 5000, "description": ">30 m³ (Blok IV)"}
        ],
        "admin_fee": 10000,
        "minimum_charge": 25000,
        "description": "Tarif bersubsidi untuk rumah tangga",
        "is_active": True
    },
    {
        "tier_name": "Private Home - Premium",
        "customer_tier": "private_home",
        "pricing_model": "tiered",
        "price_ranges": [
            {"min_volume": 0, "max_volume": 20, "price_per_unit": 3000, "description": "0-20 m³ (Blok I)"},
            {"min_volume": 20, "max_volume": 50, "price_per_unit": 4500, "description": "21-50 m³ (Blok II)"},
            {"min_volume": 50, "max_volume": None, "price_per_unit": 6000, "description": ">50 m³ (Blok III)"}
        ],
        "admin_fee": 15000,
        "minimum_charge": 50000,
        "description": "Tarif untuk rumah pribadi menengah ke atas",
        "is_active": True
    },
    {
        "tier_name": "Commercial - Standard",
        "customer_tier": "commercial",
        "pricing_model": "progressive",
        "price_ranges": [
            {"min_volume": 0, "max_volume": 50, "price_per_unit": 7500, "description": "0-50 m³"},
            {"min_volume": 50, "max_volume": 100, "price_per_unit": 9000, "description": "51-100 m³"},
            {"min_volume": 100, "max_volume": None, "price_per_unit": 11000, "description": ">100 m³"}
        ],
        "admin_fee": 25000,
        "minimum_charge": 100000,
        "description": "Tarif untuk usaha komersial (toko, kantor, restoran)",
        "is_active": True
    },
    {
        "tier_name": "Industrial - High Volume",
        "customer_tier": "industrial",
        "pricing_model": "flat_rate",
        "flat_rate": 12000,
        "admin_fee": 50000,
        "minimum_charge": 500000,
        "description": "Tarif tetap untuk industri dan pabrik",
        "is_active": True
    }
]
