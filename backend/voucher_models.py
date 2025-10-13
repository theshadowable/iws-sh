"""
Voucher and Discount Models
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


class DiscountType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"


class VoucherStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    DEPLETED = "depleted"
    INACTIVE = "inactive"


class Voucher(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str = Field(..., description="Unique voucher code")
    description: str = Field(..., description="Voucher description")
    discount_type: DiscountType
    discount_value: float = Field(..., description="Percentage (0-100) or fixed amount in IDR")
    min_purchase_amount: float = Field(default=0, description="Minimum purchase amount in IDR")
    max_discount_amount: Optional[float] = Field(default=None, description="Maximum discount cap in IDR")
    usage_limit: Optional[int] = Field(default=None, description="Total usage limit (None = unlimited)")
    usage_count: int = Field(default=0, description="Current usage count")
    per_customer_limit: Optional[int] = Field(default=1, description="Usage limit per customer")
    valid_from: datetime
    valid_until: datetime
    status: VoucherStatus = Field(default=VoucherStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(..., description="Admin user ID who created this voucher")
    
    class Config:
        use_enum_values = True


class VoucherUsage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    voucher_id: str
    voucher_code: str
    customer_id: str
    customer_email: str
    purchase_amount: float
    discount_amount: float
    final_amount: float
    used_at: datetime = Field(default_factory=datetime.utcnow)
    transaction_id: Optional[str] = None


class VoucherValidationRequest(BaseModel):
    voucher_code: str
    purchase_amount: float


class VoucherValidationResponse(BaseModel):
    valid: bool
    message: str
    voucher: Optional[Voucher] = None
    discount_amount: float = 0
    final_amount: float = 0


class CreateVoucherRequest(BaseModel):
    code: str
    description: str
    discount_type: DiscountType
    discount_value: float
    min_purchase_amount: float = 0
    max_discount_amount: Optional[float] = None
    usage_limit: Optional[int] = None
    per_customer_limit: int = 1
    valid_from: datetime
    valid_until: datetime


class ApplyVoucherRequest(BaseModel):
    voucher_code: str
    purchase_amount: float
