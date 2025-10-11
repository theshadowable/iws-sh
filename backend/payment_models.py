from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from datetime import datetime
from enum import Enum
import uuid


# Enums for Payment
class PaymentMethod(str, Enum):
    MIDTRANS = "midtrans"
    XENDIT_VA = "xendit_va"
    XENDIT_QRIS = "xendit_qris"
    XENDIT_EWALLET = "xendit_ewallet"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PAID = "paid"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class PaymentMode(str, Enum):
    SANDBOX = "sandbox"
    LIVE = "live"


class XenditVABank(str, Enum):
    BCA = "BCA"
    BNI = "BNI"
    BRI = "BRI"
    MANDIRI = "MANDIRI"
    PERMATA = "PERMATA"


class XenditEWallet(str, Enum):
    OVO = "OVO"
    DANA = "DANA"
    LINKAJA = "LINKAJA"
    SHOPEEPAY = "SHOPEEPAY"


# Payment Transaction Models
class PaymentTransactionBase(BaseModel):
    customer_id: str
    customer_email: EmailStr
    customer_name: str
    customer_phone: Optional[str] = None
    meter_id: Optional[str] = None
    amount: float = Field(..., gt=0, description="Amount in IDR")
    payment_method: PaymentMethod
    description: Optional[str] = None


class PaymentTransactionCreate(PaymentTransactionBase):
    # Additional fields for specific payment methods
    va_bank: Optional[XenditVABank] = None  # For Xendit VA
    ewallet_type: Optional[XenditEWallet] = None  # For Xendit E-wallet


class PaymentTransaction(PaymentTransactionBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reference_id: str  # Unique reference for this transaction
    external_id: Optional[str] = None  # Payment gateway transaction ID
    status: PaymentStatus = PaymentStatus.PENDING
    payment_url: Optional[str] = None  # Midtrans Snap URL or Xendit payment URL
    va_number: Optional[str] = None  # For Virtual Account payments
    qr_code_url: Optional[str] = None  # For QRIS payments
    qr_string: Optional[str] = None  # QR code data
    ewallet_url: Optional[str] = None  # E-wallet redirect URL
    expires_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = None


# Midtrans specific models
class MidtransTransactionRequest(BaseModel):
    customer_id: str
    customer_email: EmailStr
    customer_name: str
    customer_phone: str
    amount: float = Field(..., gt=0)
    meter_id: Optional[str] = None
    description: Optional[str] = "Water meter balance top-up"


class MidtransTransactionResponse(BaseModel):
    success: bool
    reference_id: str
    transaction_id: str
    snap_token: str
    snap_url: str
    status: PaymentStatus
    amount: float
    expires_at: datetime


# Xendit specific models
class XenditVARequest(BaseModel):
    customer_id: str
    customer_email: EmailStr
    customer_name: str
    customer_phone: Optional[str] = None
    amount: float = Field(..., gt=0)
    meter_id: Optional[str] = None
    bank_code: XenditVABank
    description: Optional[str] = "Water meter balance top-up"


class XenditVAResponse(BaseModel):
    success: bool
    reference_id: str
    external_id: str
    va_number: str
    bank_code: str
    status: PaymentStatus
    amount: float
    expected_amount: float
    expiration_date: datetime
    account_name: str


class XenditQRISRequest(BaseModel):
    customer_id: str
    customer_email: EmailStr
    customer_name: str
    amount: float = Field(..., gt=0)
    meter_id: Optional[str] = None
    description: Optional[str] = "Water meter balance top-up"


class XenditQRISResponse(BaseModel):
    success: bool
    reference_id: str
    external_id: str
    qr_code_url: str
    qr_string: str
    status: PaymentStatus
    amount: float
    expires_at: datetime


class XenditEWalletRequest(BaseModel):
    customer_id: str
    customer_email: EmailStr
    customer_name: str
    customer_phone: str
    amount: float = Field(..., gt=0)
    meter_id: Optional[str] = None
    ewallet_type: XenditEWallet
    description: Optional[str] = "Water meter balance top-up"


class XenditEWalletResponse(BaseModel):
    success: bool
    reference_id: str
    external_id: str
    checkout_url: str
    ewallet_type: str
    status: PaymentStatus
    amount: float
    expires_at: datetime


# Payment Settings Models
class PaymentSettings(BaseModel):
    id: str = Field(default="payment_settings")
    payment_mode: PaymentMode = PaymentMode.SANDBOX
    midtrans_enabled: bool = True
    xendit_enabled: bool = True
    midtrans_server_key: Optional[str] = None
    midtrans_client_key: Optional[str] = None
    xendit_secret_key: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[str] = None  # Admin user ID


class PaymentSettingsUpdate(BaseModel):
    payment_mode: Optional[PaymentMode] = None
    midtrans_enabled: Optional[bool] = None
    xendit_enabled: Optional[bool] = None


# Purchase History Models
class PurchaseHistoryQuery(BaseModel):
    customer_id: Optional[str] = None
    status: Optional[PaymentStatus] = None
    payment_method: Optional[PaymentMethod] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=50, le=100)
    skip: int = Field(default=0, ge=0)


# Webhook Models
class MidtransNotification(BaseModel):
    order_id: str
    status_code: str
    gross_amount: str
    transaction_status: str
    transaction_id: str
    transaction_time: str
    payment_type: str
    fraud_status: Optional[str] = None
    signature_key: str


class XenditCallbackVA(BaseModel):
    id: str
    external_id: str
    account_number: str
    bank_code: str
    amount: float
    transaction_timestamp: str
    payment_id: str
    status: Optional[str] = None


class XenditCallbackQRIS(BaseModel):
    id: str
    external_id: str
    amount: float
    qr_id: str
    status: str
    created: str
    updated: str


# Receipt Models
class Receipt(BaseModel):
    transaction_id: str
    reference_id: str
    customer_name: str
    customer_email: EmailStr
    amount: float
    payment_method: str
    status: str
    paid_at: Optional[datetime] = None
    created_at: datetime
    receipt_number: str
    meter_id: Optional[str] = None
    balance_added: Optional[float] = None
