"""
IoT Device Integration Routes
HTTP/REST API endpoints for water meter devices to send data and receive commands
"""
from fastapi import APIRouter, HTTPException, Depends, Header, status
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
import hashlib
import hmac

router = APIRouter(prefix="/iot", tags=["iot-devices"])


# Device Authentication Model
class DeviceAuth(BaseModel):
    device_id: str
    device_secret: str  # Pre-shared secret for HMAC authentication


# Device Reading Model (from device to server)
class DeviceReading(BaseModel):
    device_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    flow_rate: float  # L/min - current water flow rate
    volume_consumed: float  # L - volume in this reading period
    total_volume: float  # L - total cumulative volume
    balance: float  # IDR - remaining balance
    valve_status: Literal["open", "closed"] = "open"
    signal_strength: Optional[int] = None  # RSSI in dBm
    battery_level: Optional[int] = None  # Percentage 0-100
    temperature: Optional[float] = None  # Celsius
    pressure: Optional[float] = None  # Bar
    device_status: Literal["normal", "warning", "error"] = "normal"
    error_code: Optional[str] = None


# Device Command Model (from server to device)
class DeviceCommand(BaseModel):
    command: Literal["open_valve", "close_valve", "restart", "calibrate", "update_config"]
    parameters: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Device Registration Model
class DeviceRegistration(BaseModel):
    device_id: str  # Hardware device ID (serial number)
    device_type: str = "smart_meter"
    firmware_version: str
    hardware_version: str
    mac_address: Optional[str] = None
    customer_id: Optional[str] = None  # Link to customer if known


@router.post("/register")
async def register_device(
    registration: DeviceRegistration,
    x_device_secret: str = Header(None)
):
    """
    Register new IoT device
    Device sends its hardware ID and gets authenticated
    """
    from server import db
    
    if not x_device_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Device secret required in X-Device-Secret header"
        )
    
    # Check if device already registered
    existing = await db.devices.find_one({"device_id": registration.device_id}, {"_id": 0})
    
    if existing:
        # Update device info
        await db.devices.update_one(
            {"device_id": registration.device_id},
            {"$set": {
                "firmware_version": registration.firmware_version,
                "hardware_version": registration.hardware_version,
                "mac_address": registration.mac_address,
                "updated_at": datetime.utcnow().isoformat()
            }}
        )
        
        return {
            "success": True,
            "message": "Device info updated",
            "device_id": registration.device_id,
            "registered": True
        }
    
    # New device - create device record
    from models import Device
    from device_models import DeviceActivity, DeviceActivityType
    import uuid
    
    # If customer_id not provided, create as unassigned device
    device = Device(
        id=str(uuid.uuid4()),
        device_id=registration.device_id,
        device_name=f"Device {registration.device_id}",
        property_id="unassigned",  # To be assigned later
        customer_id="unassigned",  # To be assigned later
        status="inactive",  # Inactive until assigned to customer
        installation_date=datetime.utcnow(),
        firmware_version=registration.firmware_version
    )
    
    device_dict = device.model_dump()
    device_dict['created_at'] = device_dict['created_at'].isoformat()
    device_dict['updated_at'] = device_dict['updated_at'].isoformat()
    device_dict['installation_date'] = device_dict['installation_date'].isoformat()
    
    # Store device secret securely (hashed)
    device_dict['device_secret_hash'] = hashlib.sha256(x_device_secret.encode()).hexdigest()
    
    await db.devices.insert_one(device_dict)
    
    # Log activity
    activity = DeviceActivity(
        device_id=device.id,
        activity_type=DeviceActivityType.INSTALLATION,
        title="Device Registered",
        description=f"New device registered: {registration.device_id}",
        performed_by="system"
    )
    activity_dict = activity.model_dump()
    activity_dict['timestamp'] = activity_dict['timestamp'].isoformat()
    await db.device_activities.insert_one(activity_dict)
    
    return {
        "success": True,
        "message": "Device registered successfully",
        "device_id": registration.device_id,
        "device_uuid": device.id,
        "status": "inactive",
        "note": "Device needs to be assigned to a customer by admin"
    }


@router.post("/reading")
async def receive_device_reading(
    reading: DeviceReading,
    x_device_secret: str = Header(None)
):
    """
    Receive water usage reading from IoT device
    Device sends flow rate, volume, balance, status data
    """
    from server import db
    
    if not x_device_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Device secret required"
        )
    
    # Find device
    device = await db.devices.find_one({"device_id": reading.device_id}, {"_id": 0})
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found. Please register device first."
        )
    
    # Verify device secret
    expected_hash = device.get('device_secret_hash')
    provided_hash = hashlib.sha256(x_device_secret.encode()).hexdigest()
    
    if expected_hash != provided_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid device secret"
        )
    
    # Store water usage reading
    from models import WaterUsage
    import uuid
    
    # Calculate cost based on volume (simplified, should use pricing tier)
    cost = reading.volume_consumed / 1000 * 10000  # Convert L to m³, multiply by rate
    
    water_usage = WaterUsage(
        id=str(uuid.uuid4()),
        device_id=device['id'],
        flow_rate=reading.flow_rate,
        volume=reading.volume_consumed,
        balance_before=device.get('current_balance', 0),
        balance_after=reading.balance,
        timestamp=reading.timestamp
    )
    
    usage_dict = water_usage.model_dump()
    usage_dict['timestamp'] = usage_dict['timestamp'].isoformat()
    
    # Add IoT-specific data
    usage_dict['reading_date'] = reading.timestamp.isoformat()
    usage_dict['customer_id'] = device.get('customer_id', 'unassigned')
    usage_dict['water_consumed'] = reading.volume_consumed / 1000  # Convert to m³
    usage_dict['cost'] = cost
    usage_dict['reading_type'] = 'automatic'
    usage_dict['signal_strength'] = reading.signal_strength
    usage_dict['battery_level'] = reading.battery_level
    
    await db.water_usage.insert_one(usage_dict)
    
    # Update device status
    update_data = {
        "current_balance": reading.balance,
        "total_water_consumed": reading.total_volume / 1000,  # Convert to m³
        "valve_status": reading.valve_status,
        "signal_strength": reading.signal_strength,
        "battery_level": reading.battery_level,
        "device_status": reading.device_status,
        "last_reading_date": reading.timestamp.isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    await db.devices.update_one(
        {"device_id": reading.device_id},
        {"$set": update_data}
    )
    
    # Check for alerts
    alerts = []
    
    # Low balance alert
    if reading.balance < 50000:
        alerts.append("low_balance")
        # Create alert
        from models import DeviceAlert, AlertType
        alert = DeviceAlert(
            id=str(uuid.uuid4()),
            device_id=device['id'],
            alert_type=AlertType.LOW_BALANCE,
            message=f"Low balance: Rp {reading.balance:,.0f}",
            severity="warning",
            is_resolved=False,
            timestamp=datetime.utcnow()
        )
        alert_dict = alert.model_dump()
        alert_dict['timestamp'] = alert_dict['timestamp'].isoformat()
        
        # Check if alert already exists
        existing_alert = await db.device_alerts.find_one({
            "device_id": device['id'],
            "alert_type": "low_balance",
            "is_resolved": False
        })
        if not existing_alert:
            await db.device_alerts.insert_one(alert_dict)
    
    # Low battery alert
    if reading.battery_level and reading.battery_level < 20:
        alerts.append("low_battery")
    
    # Error status alert
    if reading.device_status == "error":
        alerts.append("device_error")
    
    # Determine action based on balance
    action = None
    if reading.balance <= 0:
        action = "close_valve"  # Auto-close valve if balance depleted
    elif reading.valve_status == "closed" and reading.balance > 10000:
        action = "open_valve"  # Auto-open if balance sufficient
    
    return {
        "success": True,
        "message": "Reading received",
        "device_id": reading.device_id,
        "timestamp": reading.timestamp.isoformat(),
        "balance": reading.balance,
        "volume_consumed": reading.volume_consumed,
        "alerts": alerts,
        "action": action,
        "device_status": device.get('status', 'active')
    }


@router.get("/{device_id}/command")
async def get_device_command(
    device_id: str,
    x_device_secret: str = Header(None)
):
    """
    Device polls for pending commands
    Server returns any pending command for the device
    """
    from server import db
    
    if not x_device_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Device secret required"
        )
    
    # Find device
    device = await db.devices.find_one({"device_id": device_id}, {"_id": 0})
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Verify device secret
    expected_hash = device.get('device_secret_hash')
    provided_hash = hashlib.sha256(x_device_secret.encode()).hexdigest()
    
    if expected_hash != provided_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid device secret"
        )
    
    # Check for pending commands
    command = await db.device_commands.find_one({
        "device_id": device['id'],
        "status": "pending"
    }, {"_id": 0})
    
    if command:
        # Mark command as delivered
        await db.device_commands.update_one(
            {"id": command['id']},
            {"$set": {
                "status": "delivered",
                "delivered_at": datetime.utcnow().isoformat()
            }}
        )
        
        return {
            "has_command": True,
            "command": command['command'],
            "parameters": command.get('parameters'),
            "command_id": command['id']
        }
    
    return {
        "has_command": False,
        "command": None
    }


@router.post("/{device_id}/command/ack")
async def acknowledge_command(
    device_id: str,
    command_id: str,
    success: bool,
    message: Optional[str] = None,
    x_device_secret: str = Header(None)
):
    """
    Device acknowledges command execution
    """
    from server import db
    
    if not x_device_secret:
        raise HTTPException(status_code=401, detail="Device secret required")
    
    # Find device
    device = await db.devices.find_one({"device_id": device_id}, {"_id": 0})
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Update command status
    await db.device_commands.update_one(
        {"id": command_id},
        {"$set": {
            "status": "completed" if success else "failed",
            "completed_at": datetime.utcnow().isoformat(),
            "response_message": message
        }}
    )
    
    return {
        "success": True,
        "message": "Command acknowledged"
    }


@router.post("/{device_id}/send-command")
async def send_command_to_device(
    device_id: str,
    command: DeviceCommand
):
    """
    Admin/System sends command to device
    Command is queued and device will poll to get it
    """
    from server import db
    import uuid
    
    # Find device by device_id (hardware ID)
    device = await db.devices.find_one({"device_id": device_id}, {"_id": 0})
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Create command record
    command_record = {
        "id": str(uuid.uuid4()),
        "device_id": device['id'],
        "device_hardware_id": device_id,
        "command": command.command,
        "parameters": command.parameters,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "delivered_at": None,
        "completed_at": None,
        "response_message": None
    }
    
    await db.device_commands.insert_one(command_record)
    
    # Log activity
    from device_models import DeviceActivity, DeviceActivityType
    activity = DeviceActivity(
        device_id=device['id'],
        activity_type=DeviceActivityType.CONFIGURATION,
        title=f"Command Sent: {command.command}",
        description=f"Command queued for device",
        performed_by="system"
    )
    activity_dict = activity.model_dump()
    activity_dict['timestamp'] = activity_dict['timestamp'].isoformat()
    await db.device_activities.insert_one(activity_dict)
    
    return {
        "success": True,
        "message": "Command queued",
        "command_id": command_record['id'],
        "device_id": device_id,
        "command": command.command
    }


@router.get("/health")
async def iot_health_check():
    """Health check endpoint for IoT service"""
    return {
        "status": "healthy",
        "service": "IoT Device Integration",
        "timestamp": datetime.utcnow().isoformat()
    }
