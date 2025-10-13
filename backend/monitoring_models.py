"""
Real-time Monitoring and Device Management Models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    WARNING = "warning"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class DeviceHealth(BaseModel):
    battery_level: Optional[float] = Field(None, description="Battery percentage (0-100)")
    signal_strength: Optional[float] = Field(None, description="Signal strength (0-100)")
    last_reading_at: Optional[datetime] = None
    consecutive_failures: int = Field(default=0)
    uptime_percentage: float = Field(default=100.0, description="Uptime in last 30 days (%)")


class DeviceMonitoring(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    customer_id: str
    customer_name: str
    location: Optional[str] = None
    status: DeviceStatus = Field(default=DeviceStatus.ONLINE)
    health: DeviceHealth = Field(default_factory=DeviceHealth)
    current_consumption_rate: float = Field(default=0, description="Current flow rate (m³/hour)")
    total_consumption_today: float = Field(default=0, description="Total consumption today (m³)")
    balance: float = Field(default=0, description="Customer balance (IDR)")
    alerts_count: int = Field(default=0, description="Active alerts count")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class RealTimeConsumption(BaseModel):
    device_id: str
    customer_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    instant_flow_rate: float = Field(..., description="Liters per minute")
    cumulative_consumption: float = Field(..., description="Total m³ since start")
    balance_remaining: float = Field(..., description="IDR")
    estimated_runtime_hours: float = Field(..., description="Hours until balance depletes at current rate")


class BulkCustomerAction(str, Enum):
    ACTIVATE = "activate"
    DEACTIVATE = "deactivate"
    UPDATE_BALANCE = "update_balance"
    RESET_PASSWORD = "reset_password"
    SEND_NOTIFICATION = "send_notification"


class BulkCustomerRequest(BaseModel):
    customer_ids: List[str]
    action: BulkCustomerAction
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Action-specific parameters")


class BulkCustomerResult(BaseModel):
    success_count: int
    failure_count: int
    results: List[Dict[str, Any]]
    message: str


class MaintenanceSchedule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    customer_id: str
    customer_name: str
    maintenance_type: str = Field(..., description="routine, repair, inspection, calibration")
    scheduled_date: datetime
    assigned_technician_id: Optional[str] = None
    assigned_technician_name: Optional[str] = None
    status: str = Field(default="scheduled", description="scheduled, in_progress, completed, cancelled")
    priority: str = Field(default="normal", description="low, normal, high, urgent")
    description: str
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(..., description="Admin user ID")
    
    class Config:
        use_enum_values = True


class CreateMaintenanceRequest(BaseModel):
    device_id: str
    maintenance_type: str
    scheduled_date: datetime
    assigned_technician_id: Optional[str] = None
    priority: str = "normal"
    description: str
    notes: Optional[str] = None


class RevenueReport(BaseModel):
    period: str = Field(..., description="daily, weekly, monthly, yearly")
    start_date: datetime
    end_date: datetime
    total_revenue: float = Field(..., description="Total revenue in IDR")
    total_transactions: int
    total_water_consumption: float = Field(..., description="Total water consumed in m³")
    avg_transaction_value: float
    revenue_by_payment_method: Dict[str, float]
    revenue_by_day: List[Dict[str, Any]]
    top_customers: List[Dict[str, Any]]
    growth_percentage: Optional[float] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class DashboardMetrics(BaseModel):
    total_customers: int
    active_customers: int
    total_devices: int
    online_devices: int
    offline_devices: int
    devices_with_alerts: int
    total_revenue_today: float
    total_revenue_month: float
    total_consumption_today: float
    total_consumption_month: float
    low_balance_customers: int
    pending_maintenance: int
    active_leaks: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
