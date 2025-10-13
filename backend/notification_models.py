"""
Notification Models for customer alerts and notifications
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    """Types of notifications"""
    LOW_BALANCE = "low_balance"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    USAGE_ALERT = "usage_alert"
    BUDGET_ALERT = "budget_alert"
    SYSTEM = "system"
    METER_STATUS = "meter_status"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Notification(BaseModel):
    """Customer notification"""
    id: str = Field(default_factory=lambda: f"notif_{datetime.utcnow().timestamp()}")
    customer_id: str
    type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    title: str
    message: str
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None
    action_url: Optional[str] = None
    action_label: Optional[str] = None
    metadata: Optional[dict] = None


class NotificationPreferences(BaseModel):
    """User notification preferences"""
    customer_id: str
    low_balance_enabled: bool = True
    low_balance_threshold: float = 5000.0  # IDR
    payment_alerts: bool = True
    usage_alerts: bool = True
    budget_alerts: bool = True
    system_alerts: bool = True
    email_notifications: bool = False
    sms_notifications: bool = False
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Request/Response models
class UpdatePreferencesRequest(BaseModel):
    """Request to update notification preferences"""
    low_balance_enabled: Optional[bool] = None
    low_balance_threshold: Optional[float] = None
    payment_alerts: Optional[bool] = None
    usage_alerts: Optional[bool] = None
    budget_alerts: Optional[bool] = None
    system_alerts: Optional[bool] = None
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None


class NotificationResponse(BaseModel):
    """Response with notifications"""
    notifications: List[Notification]
    unread_count: int
    total: int
