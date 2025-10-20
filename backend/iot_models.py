"""
IoT Real-time Monitoring Models
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import datetime
from enum import Enum
import uuid


class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class ConnectionType(str, Enum):
    MQTT = "mqtt"
    HTTP = "http"
    WEBSOCKET = "websocket"


# Real-time Device Reading
class IoTDeviceReading(BaseModel):
    device_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Water flow metrics
    flow_rate: float  # L/min - current water flow rate
    volume_consumed: float  # L - volume in this reading period
    total_volume: float  # L - total cumulative volume
    
    # Financial
    balance: float  # IDR - remaining balance
    cost_per_liter: float = 10.0  # IDR per liter
    
    # Device status
    valve_status: Literal["open", "closed"] = "open"
    device_status: DeviceStatus = DeviceStatus.ONLINE
    
    # Sensor readings
    temperature: Optional[float] = None  # Celsius
    pressure: Optional[float] = None  # Bar
    battery_level: Optional[int] = None  # Percentage 0-100
    signal_strength: Optional[int] = None  # RSSI in dBm
    
    # Error handling
    error_code: Optional[str] = None
    error_message: Optional[str] = None


# Device Registration
class IoTDeviceRegistration(BaseModel):
    device_id: str  # Hardware serial number
    device_name: str
    device_type: str = "smart_meter"
    connection_type: ConnectionType = ConnectionType.MQTT
    
    # Hardware info
    firmware_version: str
    hardware_version: str
    mac_address: Optional[str] = None
    
    # Configuration
    mqtt_topic: Optional[str] = None
    http_endpoint: Optional[str] = None
    
    # Association
    customer_id: Optional[str] = None
    property_id: Optional[str] = None


# Device Command (Server to Device)
class IoTDeviceCommand(BaseModel):
    command_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    command: Literal["open_valve", "close_valve", "restart", "calibrate", "update_config", "read_status"]
    parameters: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    status: Literal["pending", "sent", "acknowledged", "completed", "failed"] = "pending"


# Device Connection Info
class IoTDeviceConnection(BaseModel):
    device_id: str
    connection_type: ConnectionType
    status: DeviceStatus
    last_seen: datetime
    ip_address: Optional[str] = None
    mqtt_client_id: Optional[str] = None
    websocket_session_id: Optional[str] = None
    
    # Connection stats
    uptime_seconds: int = 0
    reconnect_count: int = 0
    packet_loss: float = 0.0  # Percentage
    latency_ms: Optional[float] = None


# Real-time Metrics Summary
class IoTMetricsSummary(BaseModel):
    device_id: str
    device_name: str
    status: DeviceStatus
    last_updated: datetime
    
    # Current readings
    current_flow_rate: float
    current_temperature: Optional[float]
    current_pressure: Optional[float]
    
    # Today's stats
    today_volume: float
    today_cost: float
    
    # Device health
    battery_level: Optional[int]
    signal_strength: Optional[int]
    valve_status: str
    
    # Alerts
    has_alerts: bool = False
    alert_count: int = 0


# WebSocket Message
class WebSocketMessage(BaseModel):
    type: Literal["device_reading", "device_status", "alert", "command", "connection"]
    device_id: str
    data: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# MQTT Configuration
class MQTTConfig(BaseModel):
    broker_host: str = "localhost"
    broker_port: int = 1883
    username: Optional[str] = None
    password: Optional[str] = None
    use_tls: bool = False
    
    # Topics
    readings_topic: str = "indowater/readings"
    commands_topic: str = "indowater/commands"
    status_topic: str = "indowater/status"
