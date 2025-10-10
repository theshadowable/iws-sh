from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime
import uuid


# Meter Reading Models
class MeterReadingBase(BaseModel):
    device_id: str
    reading_value: float
    reading_date: datetime = Field(default_factory=datetime.utcnow)
    technician_id: str
    reading_method: Literal["manual", "ocr", "barcode", "qr_code"] = "manual"
    photo_path: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    notes: Optional[str] = None
    ocr_confidence: Optional[float] = None  # OCR confidence score


class MeterReadingCreate(BaseModel):
    device_id: str
    reading_value: Optional[float] = None  # Optional if using OCR
    reading_method: Literal["manual", "ocr", "barcode", "qr_code"] = "manual"
    notes: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None


class MeterReading(MeterReadingBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Work Order / Task Models
class WorkOrderBase(BaseModel):
    title: str
    description: str
    work_type: Literal["installation", "repair", "maintenance", "inspection", "reading"]
    priority: Literal["low", "medium", "high", "urgent"] = "medium"
    status: Literal["pending", "assigned", "in_progress", "completed", "cancelled"] = "pending"
    assigned_to: Optional[str] = None  # Technician user_id
    device_id: Optional[str] = None
    property_id: Optional[str] = None
    customer_id: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    notes: Optional[str] = None


class WorkOrderCreate(WorkOrderBase):
    pass


class WorkOrderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    work_type: Optional[Literal["installation", "repair", "maintenance", "inspection", "reading"]] = None
    priority: Optional[Literal["low", "medium", "high", "urgent"]] = None
    status: Optional[Literal["pending", "assigned", "in_progress", "completed", "cancelled"]] = None
    assigned_to: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    notes: Optional[str] = None


class WorkOrder(WorkOrderBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Maintenance Schedule Models
class MaintenanceScheduleBase(BaseModel):
    device_id: str
    maintenance_type: Literal["routine_check", "calibration", "replacement", "cleaning", "pipe_inspection"]
    schedule_date: datetime
    assigned_to: Optional[str] = None
    status: Literal["scheduled", "completed", "skipped", "rescheduled"] = "scheduled"
    notes: Optional[str] = None
    recurrence: Optional[Literal["none", "weekly", "monthly", "quarterly", "yearly"]] = "none"


class MaintenanceScheduleCreate(MaintenanceScheduleBase):
    pass


class MaintenanceScheduleUpdate(BaseModel):
    schedule_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    status: Optional[Literal["scheduled", "completed", "skipped", "rescheduled"]] = None
    notes: Optional[str] = None


class MaintenanceSchedule(MaintenanceScheduleBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    completed_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Leak Alert Models
class LeakAlertBase(BaseModel):
    device_id: str
    alert_type: Literal["continuous_flow", "abnormal_spike", "zero_flow", "pattern_anomaly"]
    severity: Literal["info", "warning", "critical"] = "warning"
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    flow_rate: Optional[float] = None
    duration_hours: Optional[float] = None
    estimated_loss: Optional[float] = None  # In liters
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None


class LeakAlertCreate(LeakAlertBase):
    pass


class LeakAlertUpdate(BaseModel):
    is_resolved: bool
    resolution_notes: Optional[str] = None


class LeakAlert(LeakAlertBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))


# Technician Report Models
class TechnicianReportBase(BaseModel):
    report_type: Literal["daily", "weekly", "monthly", "custom", "device_status", "performance"]
    technician_id: str
    start_date: datetime
    end_date: datetime
    total_readings: int = 0
    total_tasks_completed: int = 0
    total_devices_visited: int = 0
    total_issues_found: int = 0
    summary: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class TechnicianReportCreate(BaseModel):
    report_type: Literal["daily", "weekly", "monthly", "custom", "device_status", "performance"]
    start_date: datetime
    end_date: datetime


class TechnicianReport(TechnicianReportBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))


# Meter Condition Check Models
class MeterConditionBase(BaseModel):
    device_id: str
    technician_id: str
    check_date: datetime = Field(default_factory=datetime.utcnow)
    condition_status: Literal["excellent", "good", "fair", "poor", "faulty"] = "good"
    is_functioning: bool = True
    reading_accuracy: Optional[Literal["accurate", "slightly_off", "inaccurate"]] = "accurate"
    physical_damage: bool = False
    display_readable: bool = True
    leak_detected: bool = False
    valve_functioning: bool = True
    battery_level: Optional[int] = None  # Percentage
    signal_strength: Optional[int] = None  # Percentage
    photo_path: Optional[str] = None
    notes: Optional[str] = None
    recommendations: Optional[str] = None


class MeterConditionCreate(MeterConditionBase):
    pass


class MeterCondition(MeterConditionBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))


# Customer Data for Technicians
class CustomerDataTechnician(BaseModel):
    """Comprehensive customer data view for technicians"""
    model_config = ConfigDict(extra="ignore")
    
    # Customer info
    customer_id: str
    customer_number: str
    full_name: str
    email: str
    phone: str
    address: str
    
    # Property info
    property_id: str
    property_name: str
    property_type: str
    
    # Device info
    device_id: str
    device_name: str
    device_status: str
    current_balance: float
    
    # Tariff and usage
    tariff_class: Optional[str] = "residential_standard"
    total_water_consumed: float = 0.0
    last_reading_date: Optional[datetime] = None
    last_reading_value: Optional[float] = None
    
    # Location
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None