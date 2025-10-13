"""
Voucher Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os

from auth import get_current_user, require_role
from voucher_models import (
    Voucher, VoucherUsage, VoucherStatus, DiscountType,
    CreateVoucherRequest, VoucherValidationRequest, 
    VoucherValidationResponse, ApplyVoucherRequest
)

router = APIRouter(prefix="/vouchers", tags=["Vouchers"])

# Database connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'indowater_db')]


@router.post("/", response_model=Voucher)
async def create_voucher(
    request: CreateVoucherRequest,
    current_user: dict = Depends(require_role(["admin"]))
):
    """
    Create a new promotional voucher (Admin only)
    """
    try:
        # Check if code already exists
        existing = await db.vouchers.find_one({"code": request.code.upper()})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Voucher code already exists"
            )
        
        # Validate discount value
        if request.discount_type == DiscountType.PERCENTAGE:
            if request.discount_value <= 0 or request.discount_value > 100:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Percentage discount must be between 0 and 100"
                )
        elif request.discount_value <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discount value must be greater than 0"
            )
        
        # Validate dates
        if request.valid_from >= request.valid_until:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="valid_until must be after valid_from"
            )
        
        voucher = Voucher(
            code=request.code.upper(),
            description=request.description,
            discount_type=request.discount_type,
            discount_value=request.discount_value,
            min_purchase_amount=request.min_purchase_amount,
            max_discount_amount=request.max_discount_amount,
            usage_limit=request.usage_limit,
            per_customer_limit=request.per_customer_limit,
            valid_from=request.valid_from,
            valid_until=request.valid_until,
            created_by=current_user.id
        )
        
        await db.vouchers.insert_one(voucher.dict())
        return voucher
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating voucher: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create voucher: {str(e)}"
        )


@router.post("/validate", response_model=VoucherValidationResponse)
async def validate_voucher(
    request: VoucherValidationRequest,
    current_user = Depends(get_current_user)
):
    """
    Validate a voucher code and calculate discount
    """
    try:
        customer_id = current_user.id
        
        # Find voucher
        voucher = await db.vouchers.find_one({"code": request.voucher_code.upper()})
        if not voucher:
            return VoucherValidationResponse(
                valid=False,
                message="Invalid voucher code",
                final_amount=request.purchase_amount
            )
        
        voucher_obj = Voucher(**voucher)
        now = datetime.utcnow()
        
        # Check if voucher is active
        if voucher_obj.status != VoucherStatus.ACTIVE:
            return VoucherValidationResponse(
                valid=False,
                message="This voucher is no longer active",
                final_amount=request.purchase_amount
            )
        
        # Check date validity
        if now < voucher_obj.valid_from:
            return VoucherValidationResponse(
                valid=False,
                message="This voucher is not yet valid",
                final_amount=request.purchase_amount
            )
        
        if now > voucher_obj.valid_until:
            return VoucherValidationResponse(
                valid=False,
                message="This voucher has expired",
                final_amount=request.purchase_amount
            )
        
        # Check usage limit
        if voucher_obj.usage_limit is not None and voucher_obj.usage_count >= voucher_obj.usage_limit:
            return VoucherValidationResponse(
                valid=False,
                message="This voucher has reached its usage limit",
                final_amount=request.purchase_amount
            )
        
        # Check per-customer limit
        customer_usage_count = await db.voucher_usage.count_documents({
            "voucher_id": voucher_obj.id,
            "customer_id": customer_id
        })
        
        if voucher_obj.per_customer_limit and customer_usage_count >= voucher_obj.per_customer_limit:
            return VoucherValidationResponse(
                valid=False,
                message="You have already used this voucher the maximum number of times",
                final_amount=request.purchase_amount
            )
        
        # Check minimum purchase amount
        if request.purchase_amount < voucher_obj.min_purchase_amount:
            return VoucherValidationResponse(
                valid=False,
                message=f"Minimum purchase amount is IDR {voucher_obj.min_purchase_amount:,.0f}",
                final_amount=request.purchase_amount
            )
        
        # Calculate discount
        if voucher_obj.discount_type == DiscountType.PERCENTAGE:
            discount_amount = request.purchase_amount * (voucher_obj.discount_value / 100)
        else:  # FIXED_AMOUNT
            discount_amount = voucher_obj.discount_value
        
        # Apply max discount cap if exists
        if voucher_obj.max_discount_amount:
            discount_amount = min(discount_amount, voucher_obj.max_discount_amount)
        
        # Ensure discount doesn't exceed purchase amount
        discount_amount = min(discount_amount, request.purchase_amount)
        final_amount = request.purchase_amount - discount_amount
        
        return VoucherValidationResponse(
            valid=True,
            message="Voucher applied successfully!",
            voucher=voucher_obj,
            discount_amount=discount_amount,
            final_amount=final_amount
        )
        
    except Exception as e:
        print(f"Error validating voucher: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate voucher: {str(e)}"
        )


@router.post("/apply", response_model=VoucherValidationResponse)
async def apply_voucher(
    request: ApplyVoucherRequest,
    current_user = Depends(get_current_user)
):
    """
    Apply voucher and record usage (call this when payment is successful)
    """
    try:
        customer_id = current_user.id
        
        # Validate voucher first
        validation = await validate_voucher(
            VoucherValidationRequest(
                voucher_code=request.voucher_code,
                purchase_amount=request.purchase_amount
            ),
            current_user
        )
        
        if not validation.valid:
            return validation
        
        voucher = validation.voucher
        
        # Record usage
        usage = VoucherUsage(
            voucher_id=voucher.id,
            voucher_code=voucher.code,
            customer_id=customer_id,
            customer_email=current_user.email,
            purchase_amount=request.purchase_amount,
            discount_amount=validation.discount_amount,
            final_amount=validation.final_amount
        )
        
        await db.voucher_usage.insert_one(usage.dict())
        
        # Increment usage count
        await db.vouchers.update_one(
            {"id": voucher.id},
            {"$inc": {"usage_count": 1}}
        )
        
        # Check if usage limit reached and update status
        if voucher.usage_limit and voucher.usage_count + 1 >= voucher.usage_limit:
            await db.vouchers.update_one(
                {"id": voucher.id},
                {"$set": {"status": VoucherStatus.DEPLETED}}
            )
        
        return validation
        
    except Exception as e:
        print(f"Error applying voucher: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply voucher: {str(e)}"
        )


@router.get("/", response_model=List[Voucher])
async def list_vouchers(
    status: Optional[VoucherStatus] = None,
    current_user: dict = Depends(require_role(["admin"]))
):
    """
    List all vouchers (Admin only)
    """
    try:
        query = {}
        if status:
            query["status"] = status
        
        vouchers = await db.vouchers.find(query).sort("created_at", -1).to_list(length=100)
        return [Voucher(**v) for v in vouchers]
        
    except Exception as e:
        print(f"Error listing vouchers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list vouchers: {str(e)}"
        )


@router.get("/active", response_model=List[Voucher])
async def list_active_vouchers(
    current_user: dict = Depends(get_current_user)
):
    """
    List currently active vouchers available to customers
    """
    try:
        now = datetime.utcnow()
        
        vouchers = await db.vouchers.find({
            "status": VoucherStatus.ACTIVE,
            "valid_from": {"$lte": now},
            "valid_until": {"$gte": now}
        }).sort("created_at", -1).to_list(length=50)
        
        return [Voucher(**v) for v in vouchers]
        
    except Exception as e:
        print(f"Error listing active vouchers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list active vouchers: {str(e)}"
        )


@router.get("/usage-history", response_model=List[VoucherUsage])
async def get_voucher_usage_history(
    current_user = Depends(get_current_user)
):
    """
    Get customer's voucher usage history
    """
    try:
        customer_id = current_user.id
        
        usage = await db.voucher_usage.find(
            {"customer_id": customer_id}
        ).sort("used_at", -1).to_list(length=50)
        
        return [VoucherUsage(**u) for u in usage]
        
    except Exception as e:
        print(f"Error getting usage history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get usage history: {str(e)}"
        )


@router.patch("/{voucher_id}/status")
async def update_voucher_status(
    voucher_id: str,
    new_status: VoucherStatus,
    current_user: dict = Depends(require_role(["admin"]))
):
    """
    Update voucher status (Admin only)
    """
    try:
        result = await db.vouchers.update_one(
            {"id": voucher_id},
            {"$set": {"status": new_status}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Voucher not found"
            )
        
        return {"message": "Voucher status updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating voucher status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update voucher status: {str(e)}"
        )
