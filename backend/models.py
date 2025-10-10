from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum
import uuid


# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    TECHNICIAN = "technician"
    CUSTOMER = "customer"


class PropertyType(str, Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    BOARDING_HOUSE = "boarding_house"
    RENTAL = "rental"
    OTHER = "other"


class DeviceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    FAULTY = "faulty"


class AlertType(str, Enum):
    LOW_BALANCE = "low_balance"
    DOOR_OPEN = "door_open"
    TILT_DETECTED = "tilt_detected"
    LOW_VOLTAGE = "low_voltage"
    NO_WATER_FLOW = "no_water_flow"


# User Models
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole
    phone: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class User(UserBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User


# Property Models
class PropertyBase(BaseModel):
    property_name: str
    property_type: PropertyType
    address: str
    city: str
    province: str
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    owner_name: str
    owner_phone: str
    owner_email: Optional[EmailStr] = None
    notes: Optional[str] = None


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):
    property_name: Optional[str] = None
    property_type: Optional[PropertyType] = None
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    owner_email: Optional[EmailStr] = None
    notes: Optional[str] = None


class Property(PropertyBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Customer Models
class CustomerBase(BaseModel):
    user_id: str
    customer_number: str
    address: str
    city: str
    province: str
    postal_code: Optional[str] = None
    id_card_number: Optional[str] = None
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    id_card_number: Optional[str] = None
    notes: Optional[str] = None


class Customer(CustomerBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Device Models
class DeviceBase(BaseModel):
    device_id: str  # Unique device identifier from hardware
    device_name: str
    property_id: str
    customer_id: str
    status: DeviceStatus = DeviceStatus.ACTIVE
    installation_date: datetime
    last_maintenance_date: Optional[datetime] = None
    firmware_version: Optional[str] = None
    notes: Optional[str] = None


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    device_name: Optional[str] = None
    property_id: Optional[str] = None
    customer_id: Optional[str] = None
    status: Optional[DeviceStatus] = None
    last_maintenance_date: Optional[datetime] = None
    firmware_version: Optional[str] = None
    notes: Optional[str] = None


class Device(DeviceBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    current_balance: float = 0.0  # In Rupiah
    total_water_consumed: float = 0.0  # In liters
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Water Usage Models
class WaterUsageBase(BaseModel):
    device_id: str
    flow_rate: float  # L/min
    volume: float  # Liters
    balance_before: float
    balance_after: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WaterUsageCreate(WaterUsageBase):
    pass


class WaterUsage(WaterUsageBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))


# Transaction Models
class TransactionBase(BaseModel):
    customer_id: str
    device_id: str
    amount: float  # In Rupiah
    payment_method: str
    transaction_type: Literal["topup", "refund"]
    status: Literal["pending", "success", "failed"]
    midtrans_order_id: Optional[str] = None
    midtrans_transaction_id: Optional[str] = None
    notes: Optional[str] = None


class TransactionCreate(BaseModel):
    device_id: str
    amount: float
    payment_method: str = "midtrans"


class TransactionUpdate(BaseModel):
    status: Literal["pending", "success", "failed"]
    midtrans_transaction_id: Optional[str] = None
    notes: Optional[str] = None


class Transaction(TransactionBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Device Alert Models
class DeviceAlertBase(BaseModel):
    device_id: str
    alert_type: AlertType
    message: str
    severity: Literal["info", "warning", "critical"]
    is_resolved: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DeviceAlertCreate(DeviceAlertBase):
    pass


class DeviceAlert(DeviceAlertBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))


# Notification Models
class NotificationBase(BaseModel):
    user_id: str
    title: str
    message: str
    notification_type: Literal["email", "push", "whatsapp", "system"]
    is_read: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class NotificationCreate(NotificationBase):
    pass


class Notification(NotificationBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))


# Settings Models
class SystemSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Real-time data settings
    realtime_mode: Literal["websocket", "polling", "both"] = "both"
    polling_interval: int = 5000  # milliseconds
    
    # Alert thresholds
    low_balance_threshold: float = 5000.0  # Rupiah
    
    # Notification settings
    email_enabled: bool = True
    whatsapp_enabled: bool = True
    push_enabled: bool = True
    
    # SMTP settings
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[str] = None
    
    # WhatsApp settings
    whatsapp_api_url: Optional[str] = None
    whatsapp_api_key: Optional[str] = None
    
    # Midtrans settings
    midtrans_server_key: Optional[str] = None
    midtrans_client_key: Optional[str] = None
    midtrans_is_production: bool = False
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)