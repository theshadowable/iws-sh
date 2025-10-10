"""
Extended models for Technician features - Phase 1
Includes: Meter Readings, Tasks, Enhanced Customer/Device data
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum
import uuid


# ==================== ENUMS ====================

class TariffClass(str, Enum):
    """Customer tariff classification"""
    RESIDENTIAL_BASIC = "residential_basic"
    RESIDENTIAL_PREMIUM = "residential_premium"
    COMMERCIAL_SMALL = "commercial_small"
    COMMERCIAL_LARGE = "commercial_large"
    INDUSTRIAL = "industrial"
    GOVERNMENT = "government"
    SOCIAL = "social"  # Schools, hospitals, etc.


class ReadingType(str, Enum):
    """How the meter reading was captured"""
    MANUAL = "manual"
    PHOTO = "photo"
    OCR = "ocr"
    BARCODE = "barcode"
    QR_CODE = "qr_code"


class ReadingStatus(str, Enum):
    """Status of meter reading"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SUBMITTED = "submitted"


class TaskType(str, Enum):
    """Type of technician task"""
    METER_READING = "meter_reading"
    INSTALLATION = "installation"
    REPAIR = "repair"
    MAINTENANCE = "maintenance"
    INSPECTION = "inspection"
    CUSTOMER_VISIT = "customer_visit"


class TaskStatus(str, Enum):
    """Task completion status"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task urgency level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class MeterCondition(str, Enum):
    """Physical condition of meter"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    FAULTY = "faulty"


# ==================== ENHANCED CUSTOMER MODEL ====================

class CustomerDataEnhanced(BaseModel):
    """Enhanced customer information for technician features"""
    customer_number: str  # Unique identifier
    tariff_class: TariffClass
    property_type: str  # From existing PropertyType enum
    connection_date: Optional[datetime] = None
    account_status: Literal["active", "inactive", "suspended"] = "active"
    billing_cycle: str = "monthly"  # monthly, bimonthly, etc.
    notes: Optional[str] = None


# ==================== METER READING MODELS ====================

class MeterReadingBase(BaseModel):
    """Base model for meter readings"""
    meter_id: str  # Device ID (water meter)
    customer_id: str
    reading_value: float  # Current meter reading
    reading_date: datetime = Field(default_factory=datetime.utcnow)
    reading_type: ReadingType
    technician_id: str  # Who recorded this reading
    previous_reading: Optional[float] = None
    consumption: Optional[float] = None  # Calculated: current - previous
    photo_url: Optional[str] = None
    notes: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None


class MeterReadingCreate(BaseModel):
    """Create new meter reading"""
    meter_id: str
    customer_id: str
    reading_value: float
    reading_type: ReadingType
    previous_reading: Optional[float] = None
    photo_url: Optional[str] = None
    notes: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None


class MeterReadingUpdate(BaseModel):
    """Update meter reading"""
    reading_value: Optional[float] = None
    reading_type: Optional[ReadingType] = None
    status: Optional[ReadingStatus] = None
    notes: Optional[str] = None


class MeterReading(MeterReadingBase):
    """Complete meter reading model"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: ReadingStatus = ReadingStatus.SUBMITTED
    verified_by: Optional[str] = None  # Admin/supervisor who verified
    verified_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ==================== TASK MODELS ====================

class TaskBase(BaseModel):
    """Base model for technician tasks"""
    task_type: TaskType
    title: str
    description: Optional[str] = None
    customer_id: Optional[str] = None
    meter_id: Optional[str] = None  # Device ID
    property_id: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    scheduled_date: Optional[datetime] = None
    location_address: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    estimated_duration: Optional[int] = None  # Minutes
    notes: Optional[str] = None


class TaskCreate(TaskBase):
    """Create new task"""
    assigned_to: Optional[str] = None  # Technician ID (optional for auto-assignment)


class TaskUpdate(BaseModel):
    """Update task"""
    status: Optional[TaskStatus] = None
    assigned_to: Optional[str] = None
    priority: Optional[TaskPriority] = None
    scheduled_date: Optional[datetime] = None
    notes: Optional[str] = None
    completion_notes: Optional[str] = None
    actual_duration: Optional[int] = None


class Task(TaskBase):
    """Complete task model"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: Optional[str] = None  # Technician ID
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by: str  # Admin or system
    completion_notes: Optional[str] = None
    actual_duration: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ==================== ENHANCED DEVICE/METER MODELS ====================

class MeterEnhancement(BaseModel):
    """Additional fields for meter/device model"""
    qr_code: Optional[str] = None  # QR code for identification
    barcode: Optional[str] = None  # Barcode for identification
    meter_serial_number: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    installation_date: datetime
    last_reading_date: Optional[datetime] = None
    last_maintenance_date: Optional[datetime] = None
    next_maintenance_date: Optional[datetime] = None
    meter_condition: MeterCondition = MeterCondition.GOOD
    calibration_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None


class MeterConditionCheck(BaseModel):
    """Record of meter condition inspection"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    meter_id: str
    technician_id: str
    check_date: datetime = Field(default_factory=datetime.utcnow)
    condition: MeterCondition
    is_functioning: bool
    has_leaks: bool = False
    has_damage: bool = False
    readings_accurate: bool = True
    notes: Optional[str] = None
    photos: List[str] = []  # URLs to inspection photos
    next_check_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ==================== USAGE HISTORY MODEL ====================

class UsageHistory(BaseModel):
    """Historical water usage data for a customer"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    meter_id: str
    period_start: datetime
    period_end: datetime
    opening_reading: float
    closing_reading: float
    consumption: float
    average_daily_usage: float
    billing_amount: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ==================== TECHNICIAN LOCATION MODEL ====================

class TechnicianLocation(BaseModel):
    """Real-time location tracking for technicians"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    technician_id: str
    latitude: float
    longitude: float
    accuracy: Optional[float] = None  # GPS accuracy in meters
    is_active: bool = True  # Is technician currently on duty
    current_task_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ==================== RESPONSE MODELS ====================

class TaskWithDetails(Task):
    """Task with additional details for display"""
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    technician_name: Optional[str] = None
    meter_serial: Optional[str] = None
    property_name: Optional[str] = None


class MeterReadingWithDetails(MeterReading):
    """Meter reading with additional details"""
    customer_name: Optional[str] = None
    meter_serial: Optional[str] = None
    technician_name: Optional[str] = None
    property_address: Optional[str] = None


class TaskAssignmentRequest(BaseModel):
    """Request to assign task to technician"""
    task_id: str
    technician_id: Optional[str] = None  # If None, will auto-assign
    force_assign: bool = False  # Override auto-assignment


class TaskAssignmentResponse(BaseModel):
    """Response after task assignment"""
    success: bool
    task_id: str
    assigned_to: Optional[str] = None
    assignment_type: Literal["auto", "manual"]
    message: str
