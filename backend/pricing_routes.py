"""
Multi-tier Pricing System Routes
Manage pricing tiers and calculate bills based on customer tier and usage
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime
from models import User, UserRole
from auth import get_current_user, require_role
from pricing_models import (
    PricingTier, PricingTierCreate, PricingTierUpdate,
    CustomerTier, PricingModel, PriceTierRange,
    BillCalculationRequest, BillCalculationResult,
    CustomerTierAssignment, DEFAULT_PRICING_TIERS
)

router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.get("/tiers", response_model=List[PricingTier])
async def get_pricing_tiers(
    customer_tier: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user)
):
    """Get all pricing tiers with optional filters"""
    from server import db
    
    query = {}
    if customer_tier:
        query['customer_tier'] = customer_tier
    if is_active is not None:
        query['is_active'] = is_active
    
    tiers = await db.pricing_tiers.find(query, {"_id": 0}).to_list(None)
    
    # Parse timestamps
    for tier in tiers:
        if isinstance(tier.get('created_at'), str):
            tier['created_at'] = datetime.fromisoformat(tier['created_at'])
        if isinstance(tier.get('updated_at'), str):
            tier['updated_at'] = datetime.fromisoformat(tier['updated_at'])
        if isinstance(tier.get('effective_date'), str):
            tier['effective_date'] = datetime.fromisoformat(tier['effective_date'])
    
    return tiers


@router.get("/tiers/{tier_id}", response_model=PricingTier)
async def get_pricing_tier(
    tier_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get specific pricing tier by ID"""
    from server import db
    
    tier = await db.pricing_tiers.find_one({"id": tier_id}, {"_id": 0})
    if not tier:
        raise HTTPException(status_code=404, detail="Pricing tier not found")
    
    # Parse timestamps
    if isinstance(tier.get('created_at'), str):
        tier['created_at'] = datetime.fromisoformat(tier['created_at'])
    if isinstance(tier.get('updated_at'), str):
        tier['updated_at'] = datetime.fromisoformat(tier['updated_at'])
    if isinstance(tier.get('effective_date'), str):
        tier['effective_date'] = datetime.fromisoformat(tier['effective_date'])
    
    return PricingTier(**tier)


@router.post("/tiers", response_model=PricingTier, status_code=status.HTTP_201_CREATED)
async def create_pricing_tier(
    tier_data: PricingTierCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Create new pricing tier (Admin only)"""
    from server import db
    
    # Validate pricing model
    if tier_data.pricing_model == PricingModel.FLAT_RATE:
        if not tier_data.flat_rate or tier_data.flat_rate <= 0:
            raise HTTPException(
                status_code=400,
                detail="flat_rate is required and must be > 0 for flat_rate pricing model"
            )
    else:
        if not tier_data.price_ranges or len(tier_data.price_ranges) == 0:
            raise HTTPException(
                status_code=400,
                detail="price_ranges is required for tiered/progressive pricing models"
            )
    
    tier = PricingTier(**tier_data.model_dump())
    tier_dict = tier.model_dump()
    tier_dict['created_at'] = tier_dict['created_at'].isoformat()
    tier_dict['updated_at'] = tier_dict['updated_at'].isoformat()
    tier_dict['effective_date'] = tier_dict['effective_date'].isoformat()
    
    await db.pricing_tiers.insert_one(tier_dict)
    
    return tier


@router.put("/tiers/{tier_id}", response_model=PricingTier)
async def update_pricing_tier(
    tier_id: str,
    tier_update: PricingTierUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Update pricing tier (Admin only)"""
    from server import db
    
    # Check if tier exists
    existing = await db.pricing_tiers.find_one({"id": tier_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Pricing tier not found")
    
    update_data = tier_update.model_dump(exclude_unset=True)
    update_data['updated_at'] = datetime.utcnow().isoformat()
    
    # Convert datetime fields
    if 'effective_date' in update_data and update_data['effective_date']:
        update_data['effective_date'] = update_data['effective_date'].isoformat()
    
    await db.pricing_tiers.update_one(
        {"id": tier_id},
        {"$set": update_data}
    )
    
    updated_tier = await db.pricing_tiers.find_one({"id": tier_id}, {"_id": 0})
    
    # Parse timestamps
    if isinstance(updated_tier.get('created_at'), str):
        updated_tier['created_at'] = datetime.fromisoformat(updated_tier['created_at'])
    if isinstance(updated_tier.get('updated_at'), str):
        updated_tier['updated_at'] = datetime.fromisoformat(updated_tier['updated_at'])
    if isinstance(updated_tier.get('effective_date'), str):
        updated_tier['effective_date'] = datetime.fromisoformat(updated_tier['effective_date'])
    
    return PricingTier(**updated_tier)


@router.delete("/tiers/{tier_id}")
async def delete_pricing_tier(
    tier_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Delete pricing tier (Admin only)"""
    from server import db
    
    result = await db.pricing_tiers.delete_one({"id": tier_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Pricing tier not found")
    
    return {"message": "Pricing tier deleted successfully"}


@router.post("/calculate", response_model=BillCalculationResult)
async def calculate_bill(
    request: BillCalculationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Calculate water bill based on customer tier and usage volume
    Supports flat rate, tiered, and progressive pricing models
    """
    from server import db
    
    # Get pricing tier
    if request.pricing_tier_id:
        pricing_tier = await db.pricing_tiers.find_one({"id": request.pricing_tier_id}, {"_id": 0})
    else:
        # Get default active tier for customer tier
        pricing_tier = await db.pricing_tiers.find_one({
            "customer_tier": request.customer_tier,
            "is_active": True
        }, {"_id": 0})
    
    if not pricing_tier:
        raise HTTPException(
            status_code=404,
            detail=f"No active pricing tier found for {request.customer_tier}"
        )
    
    # Parse to PricingTier model
    if isinstance(pricing_tier.get('created_at'), str):
        pricing_tier['created_at'] = datetime.fromisoformat(pricing_tier['created_at'])
    if isinstance(pricing_tier.get('updated_at'), str):
        pricing_tier['updated_at'] = datetime.fromisoformat(pricing_tier['updated_at'])
    if isinstance(pricing_tier.get('effective_date'), str):
        pricing_tier['effective_date'] = datetime.fromisoformat(pricing_tier['effective_date'])
    
    tier = PricingTier(**pricing_tier)
    
    # Calculate based on pricing model
    if tier.pricing_model == PricingModel.FLAT_RATE:
        breakdown, water_charge = calculate_flat_rate(request.usage_volume, tier.flat_rate)
    elif tier.pricing_model == PricingModel.TIERED:
        breakdown, water_charge = calculate_tiered(request.usage_volume, tier.price_ranges)
    elif tier.pricing_model == PricingModel.PROGRESSIVE:
        breakdown, water_charge = calculate_progressive(request.usage_volume, tier.price_ranges)
    else:
        raise HTTPException(status_code=400, detail="Unknown pricing model")
    
    # Calculate totals
    total_before_tax = water_charge + tier.admin_fee
    
    # Apply minimum charge
    if total_before_tax < tier.minimum_charge:
        total_before_tax = tier.minimum_charge
        breakdown.append({
            "range": "Minimum Charge Applied",
            "volume": 0,
            "rate": 0,
            "subtotal": tier.minimum_charge - water_charge - tier.admin_fee
        })
    
    # Calculate tax (PPN 11%)
    tax = total_before_tax * 0.11
    total_amount = total_before_tax + tax
    
    return BillCalculationResult(
        customer_tier=request.customer_tier,
        usage_volume=request.usage_volume,
        pricing_tier_id=tier.id,
        pricing_tier_name=tier.tier_name,
        pricing_model=tier.pricing_model,
        breakdown=breakdown,
        water_charge=round(water_charge, 2),
        admin_fee=tier.admin_fee,
        minimum_charge=tier.minimum_charge,
        total_before_tax=round(total_before_tax, 2),
        tax=round(tax, 2),
        total_amount=round(total_amount, 2)
    )


@router.post("/seed-defaults")
async def seed_default_pricing_tiers(
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Seed default pricing tiers (Admin only)"""
    from server import db
    
    created_count = 0
    existing_count = 0
    
    for tier_data in DEFAULT_PRICING_TIERS:
        # Check if tier already exists
        existing = await db.pricing_tiers.find_one({
            "tier_name": tier_data['tier_name']
        })
        
        if existing:
            existing_count += 1
            continue
        
        # Create tier
        tier = PricingTier(**tier_data)
        tier_dict = tier.model_dump()
        tier_dict['created_at'] = tier_dict['created_at'].isoformat()
        tier_dict['updated_at'] = tier_dict['updated_at'].isoformat()
        tier_dict['effective_date'] = tier_dict['effective_date'].isoformat()
        
        await db.pricing_tiers.insert_one(tier_dict)
        created_count += 1
    
    return {
        "success": True,
        "message": "Default pricing tiers seeded",
        "created": created_count,
        "already_existed": existing_count,
        "total": len(DEFAULT_PRICING_TIERS)
    }


@router.get("/customer-tiers")
async def get_customer_tiers():
    """Get list of available customer tiers"""
    return [
        {"value": "residential", "label": "Residential (Rumah Tangga)", "description": "Tarif bersubsidi untuk rumah tangga"},
        {"value": "private_home", "label": "Private Home (Rumah Pribadi)", "description": "Tarif untuk rumah menengah ke atas"},
        {"value": "commercial", "label": "Commercial (Komersial)", "description": "Tarif untuk usaha (toko, kantor, restoran)"},
        {"value": "industrial", "label": "Industrial (Industri)", "description": "Tarif untuk pabrik dan industri"}
    ]


# Helper Functions

def calculate_flat_rate(usage_volume: float, rate: float):
    """Calculate bill with flat rate"""
    water_charge = usage_volume * rate
    breakdown = [{
        "range": f"Flat Rate",
        "volume": usage_volume,
        "rate": rate,
        "subtotal": round(water_charge, 2)
    }]
    return breakdown, water_charge


def calculate_tiered(usage_volume: float, price_ranges: List[PriceTierRange]):
    """
    Calculate bill with tiered pricing (each block uses its own rate)
    Example: 0-10m³ @ 1500, 11-20m³ @ 2000, etc.
    """
    breakdown = []
    water_charge = 0
    remaining = usage_volume
    
    for tier_range in price_ranges:
        if remaining <= 0:
            break
        
        # Determine volume in this range
        range_min = tier_range.min_volume
        range_max = tier_range.max_volume if tier_range.max_volume else float('inf')
        
        # Volume applicable to this range
        if usage_volume <= range_min:
            continue
        
        volume_in_range = min(remaining, range_max - range_min) if tier_range.max_volume else remaining
        
        if volume_in_range > 0:
            subtotal = volume_in_range * tier_range.price_per_unit
            water_charge += subtotal
            
            breakdown.append({
                "range": tier_range.description or f"{range_min}-{range_max} m³",
                "volume": round(volume_in_range, 2),
                "rate": tier_range.price_per_unit,
                "subtotal": round(subtotal, 2)
            })
            
            remaining -= volume_in_range
    
    return breakdown, water_charge


def calculate_progressive(usage_volume: float, price_ranges: List[PriceTierRange]):
    """
    Calculate bill with progressive pricing (all usage uses the rate of highest reached tier)
    Example: If usage is 60m³ and tier is 51-100 @ 9000, all 60m³ charged at 9000
    """
    # Find which tier the usage falls into
    applicable_tier = None
    
    for tier_range in price_ranges:
        range_min = tier_range.min_volume
        range_max = tier_range.max_volume if tier_range.max_volume else float('inf')
        
        if range_min <= usage_volume < range_max or (tier_range.max_volume is None and usage_volume >= range_min):
            applicable_tier = tier_range
            break
    
    if not applicable_tier:
        # Default to first tier if not found
        applicable_tier = price_ranges[0]
    
    water_charge = usage_volume * applicable_tier.price_per_unit
    breakdown = [{
        "range": applicable_tier.description or f"Progressive Rate",
        "volume": usage_volume,
        "rate": applicable_tier.price_per_unit,
        "subtotal": round(water_charge, 2)
    }]
    
    return breakdown, water_charge
