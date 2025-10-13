"""
Alert and Notification Models
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class AlertType(str, Enum):
    LOW_BALANCE = "low_balance"
    LEAK_DETECTED = "leak_detected"
    DEVICE_TAMPERING = "device_tampering"
    MAINTENANCE_DUE = "maintenance_due"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    SYSTEM_NOTIFICATION = "system_notification"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"
    DISMISSED = "dismissed"
    RESOLVED = "resolved"


class Alert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    status: AlertStatus = Field(default=AlertStatus.UNREAD)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


class AlertPreferences(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    low_balance_enabled: bool = True
    low_balance_threshold: float = Field(default=50000, description="Alert when balance below this amount (IDR)")
    leak_detection_enabled: bool = True
    device_tampering_enabled: bool = True
    maintenance_reminders_enabled: bool = True
    payment_notifications_enabled: bool = True
    email_notifications: bool = True
    push_notifications: bool = False
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class LeakDetectionEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    customer_id: str
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    consumption_rate: float = Field(..., description="Abnormal consumption rate (m³/hour)")
    normal_rate: float = Field(..., description="Normal consumption rate (m³/hour)")
    severity: str = Field(..., description="minor, moderate, severe")
    duration_minutes: int = Field(..., description="How long abnormal usage has been detected")
    estimated_loss_m3: float = Field(..., description="Estimated water loss in m³")
    estimated_cost_idr: float = Field(..., description="Estimated cost in IDR")
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    notes: Optional[str] = None


class DeviceTamperingEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    customer_id: str
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    event_type: str = Field(..., description="cover_opened, sensor_disconnected, etc.")
    authorized: bool = Field(default=False, description="Was this authorized by a technician?")
    technician_id: Optional[str] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    notes: Optional[str] = None


class WaterSavingTip(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    tip_category: str = Field(..., description="usage_optimization, leak_prevention, behavior_change")
    title: str
    description: str
    potential_savings_percentage: float = Field(..., description="Estimated savings in percentage")
    priority: int = Field(default=1, description="1=high, 2=medium, 3=low")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    viewed: bool = False
    viewed_at: Optional[datetime] = None
    applied: bool = False
    applied_at: Optional[datetime] = None


class CreateAlertRequest(BaseModel):
    customer_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    metadata: Optional[Dict[str, Any]] = None


class UpdateAlertStatusRequest(BaseModel):
    status: AlertStatus
    notes: Optional[str] = None
