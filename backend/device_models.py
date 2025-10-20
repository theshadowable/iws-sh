"""
Enhanced Device Models for Comprehensive Device Management
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum
import uuid


class DeviceType(str, Enum):
    SMART_METER = "smart_meter"
    FLOW_METER = "flow_meter"
    PRESSURE_SENSOR = "pressure_sensor"
    VALVE_CONTROLLER = "valve_controller"


class DeviceHealth(str, Enum):
    EXCELLENT = "excellent"  # 90-100%
    GOOD = "good"  # 70-89%
    FAIR = "fair"  # 50-69%
    POOR = "poor"  # <50%


class ConnectionStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    IDLE = "idle"


class DeviceActivityType(str, Enum):
    INSTALLATION = "installation"
    MAINTENANCE = "maintenance"
    REPAIR = "repair"
    CONFIGURATION = "configuration"
    STATUS_CHANGE = "status_change"
    FIRMWARE_UPDATE = "firmware_update"
    CALIBRATION = "calibration"
    READING = "reading"
    ALERT = "alert"


# Device Activity Log Model
class DeviceActivityBase(BaseModel):
    device_id: str
    activity_type: DeviceActivityType
    title: str
    description: str
    performed_by: Optional[str] = None  # user_id who performed action
    metadata: Optional[dict] = None  # Additional JSON data
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DeviceActivityCreate(DeviceActivityBase):
    pass


class DeviceActivity(DeviceActivityBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))


# Enhanced Device Stats Model
class DeviceStats(BaseModel):
    device_id: str
    total_usage: float = 0.0  # Total m³ consumed
    total_cost: float = 0.0  # Total IDR spent
    avg_daily_usage: float = 0.0  # Average m³ per day
    peak_usage: float = 0.0  # Peak m³ in single day
    uptime_percentage: float = 100.0  # % time device online
    last_reading_date: Optional[datetime] = None
    health_score: float = 100.0  # 0-100
    health_status: DeviceHealth = DeviceHealth.EXCELLENT
    connection_status: ConnectionStatus = ConnectionStatus.ONLINE
    alert_count: int = 0  # Active alerts count
    maintenance_due_days: Optional[int] = None  # Days until next maintenance


# Batch Operations Models
class DeviceBatchOperation(BaseModel):
    device_ids: List[str]
    operation: Literal["activate", "deactivate", "maintenance", "delete"]
    notes: Optional[str] = None
    performed_by: str  # user_id


class DeviceBatchResult(BaseModel):
    success_count: int
    failed_count: int
    success_devices: List[str]
    failed_devices: List[dict]  # [{device_id, reason}]
    message: str


# Device Filter Model
class DeviceFilter(BaseModel):
    status: Optional[List[str]] = None
    device_type: Optional[List[str]] = None
    customer_id: Optional[str] = None
    property_id: Optional[str] = None
    health_status: Optional[List[str]] = None
    connection_status: Optional[List[str]] = None
    search: Optional[str] = None  # Search in device_id, device_name
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[Literal["asc", "desc"]] = "desc"
    skip: int = 0
    limit: int = 50


# Device with Related Data (for comprehensive view)
class DeviceComprehensive(BaseModel):
    # Basic device info
    id: str
    device_id: str
    device_name: str
    device_type: Optional[str] = "smart_meter"
    status: str
    
    # Relations
    property_id: str
    property_name: Optional[str] = None
    property_address: Optional[str] = None
    customer_id: str
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    
    # Device details
    installation_date: datetime
    last_maintenance_date: Optional[datetime] = None
    firmware_version: Optional[str] = None
    notes: Optional[str] = None
    
    # Financial
    current_balance: float = 0.0
    total_water_consumed: float = 0.0
    
    # Stats & Health
    stats: Optional[DeviceStats] = None
    
    # Activity count
    activity_count: int = 0
    alert_count: int = 0
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
