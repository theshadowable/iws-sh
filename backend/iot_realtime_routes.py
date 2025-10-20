"""
IoT Real-time Routes
WebSocket endpoints for real-time IoT monitoring and device data ingestion
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, Header, status, Query
from typing import Optional, List
from datetime import datetime, timedelta
import json
import uuid
import hashlib
import logging

from auth import get_current_user
from iot_models import (
    IoTDeviceReading, IoTDeviceRegistration, IoTDeviceCommand,
    IoTDeviceConnection, IoTMetricsSummary, DeviceStatus, ConnectionType
)
from realtime_manager import manager, broadcast_device_reading, broadcast_device_status, broadcast_alert

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/iot", tags=["iot-realtime"])


# ============================================================================
# WebSocket Endpoints
# ============================================================================

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time IoT data streaming
    Clients connect here to receive real-time device updates
    """
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "subscribe":
                # Subscribe to device updates
                device_id = message.get("device_id")
                if device_id:
                    manager.subscribe_to_device(session_id, device_id)
                    await manager.send_personal_message({
                        "type": "subscribed",
                        "device_id": device_id,
                        "message": f"Subscribed to device {device_id}"
                    }, session_id)
            
            elif message.get("type") == "unsubscribe":
                # Unsubscribe from device updates
                device_id = message.get("device_id")
                if device_id:
                    manager.unsubscribe_from_device(session_id, device_id)
                    await manager.send_personal_message({
                        "type": "unsubscribed",
                        "device_id": device_id,
                        "message": f"Unsubscribed from device {device_id}"
                    }, session_id)
            
            elif message.get("type") == "ping":
                # Keep-alive ping
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                }, session_id)
    
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error for {session_id}: {e}")
        manager.disconnect(session_id)


# ============================================================================
# Device Registration & Management
# ============================================================================

@router.post("/devices/register")
async def register_iot_device(
    registration: IoTDeviceRegistration,
    x_device_secret: str = Header(..., description="Pre-shared device secret")
):
    """
    Register new IoT device
    ESP32/Arduino devices call this endpoint to register themselves
    """
    from server import db
    
    # Check if device already exists
    existing = await db.iot_devices.find_one({"device_id": registration.device_id})
    
    if existing:
        # Update device info
        await db.iot_devices.update_one(
            {"device_id": registration.device_id},
            {"$set": {
                "device_name": registration.device_name,
                "firmware_version": registration.firmware_version,
                "hardware_version": registration.hardware_version,
                "mac_address": registration.mac_address,
                "connection_type": registration.connection_type,
                "updated_at": datetime.utcnow()
            }}
        )
        
        return {
            "success": True,
            "message": "Device updated successfully",
            "device_id": registration.device_id,
            "status": "registered"
        }
    
    # Create new device
    device_dict = registration.model_dump()
    device_dict["id"] = str(uuid.uuid4())
    device_dict["status"] = DeviceStatus.OFFLINE
    device_dict["device_secret_hash"] = hashlib.sha256(x_device_secret.encode()).hexdigest()
    device_dict["created_at"] = datetime.utcnow()
    device_dict["updated_at"] = datetime.utcnow()
    device_dict["last_seen"] = datetime.utcnow()
    
    await db.iot_devices.insert_one(device_dict)
    
    # Create connection record
    connection = IoTDeviceConnection(
        device_id=registration.device_id,
        connection_type=registration.connection_type,
        status=DeviceStatus.OFFLINE,
        last_seen=datetime.utcnow()
    )
    connection_dict = connection.model_dump()
    await db.iot_connections.insert_one(connection_dict)
    
    return {
        "success": True,
        "message": "Device registered successfully",
        "device_id": registration.device_id,
        "device_uuid": device_dict["id"],
        "mqtt_topic": f"indowater/{registration.device_id}",
        "status": "offline"
    }


@router.get("/devices/list")
async def list_iot_devices(
    current_user: dict = Depends(get_current_user),
    status: Optional[str] = Query(None)
):
    """
    List all registered IoT devices
    Admin/Technician: See all devices
    Customer: See only their devices
    """
    from server import db
    
    # Build filter
    filter_query = {}
    
    if current_user["role"] == "customer":
        filter_query["customer_id"] = current_user["id"]
    
    if status:
        filter_query["status"] = status
    
    # Get devices
    devices = []
    cursor = db.iot_devices.find(filter_query, {"_id": 0, "device_secret_hash": 0})
    async for device in cursor:
        devices.append(device)
    
    return {
        "success": True,
        "count": len(devices),
        "devices": devices
    }


@router.get("/devices/{device_id}")
async def get_iot_device(
    device_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get IoT device details"""
    from server import db
    
    device = await db.iot_devices.find_one({"device_id": device_id}, {"_id": 0, "device_secret_hash": 0})
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Check permissions
    if current_user["role"] == "customer" and device.get("customer_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get connection info
    connection = await db.iot_connections.find_one({"device_id": device_id}, {"_id": 0})
    
    # Get latest reading
    latest_reading = await db.iot_readings.find_one(
        {"device_id": device_id},
        {"_id": 0},
        sort=[("timestamp", -1)]
    )
    
    return {
        "success": True,
        "device": device,
        "connection": connection,
        "latest_reading": latest_reading
    }


# ============================================================================
# Device Data Ingestion (HTTP)
# ============================================================================

@router.post("/data/ingest")
async def ingest_device_data(
    reading: IoTDeviceReading,
    x_device_secret: str = Header(..., description="Device authentication secret")
):
    """
    Ingest data from IoT device via HTTP POST
    ESP32/Arduino devices can POST data here
    """
    from server import db
    
    # Verify device exists and authenticate
    device = await db.iot_devices.find_one({"device_id": reading.device_id})
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not registered")
    
    # Verify device secret
    expected_hash = device.get("device_secret_hash")
    provided_hash = hashlib.sha256(x_device_secret.encode()).hexdigest()
    
    if expected_hash != provided_hash:
        raise HTTPException(status_code=401, detail="Invalid device secret")
    
    # Store reading
    reading_dict = reading.model_dump()
    reading_dict["id"] = str(uuid.uuid4())
    reading_dict["received_at"] = datetime.utcnow()
    
    await db.iot_readings.insert_one(reading_dict)
    
    # Update device status and last_seen
    await db.iot_devices.update_one(
        {"device_id": reading.device_id},
        {"$set": {
            "status": reading.device_status.value,
            "last_seen": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }}
    )
    
    # Update connection info
    await db.iot_connections.update_one(
        {"device_id": reading.device_id},
        {"$set": {
            "status": reading.device_status,
            "last_seen": datetime.utcnow()
        }},
        upsert=True
    )
    
    # Broadcast to WebSocket subscribers
    await broadcast_device_reading(reading.device_id, reading_dict)
    
    # Check for alerts
    if reading.flow_rate > 100:  # High flow rate
        alert_data = {
            "type": "high_flow",
            "message": f"High flow rate detected: {reading.flow_rate} L/min",
            "severity": "warning"
        }
        await broadcast_alert(reading.device_id, alert_data)
    
    if reading.battery_level and reading.battery_level < 20:  # Low battery
        alert_data = {
            "type": "low_battery",
            "message": f"Low battery: {reading.battery_level}%",
            "severity": "warning"
        }
        await broadcast_alert(reading.device_id, alert_data)
    
    return {
        "success": True,
        "message": "Data received successfully",
        "reading_id": reading_dict["id"],
        "timestamp": reading.timestamp
    }


# ============================================================================
# Real-time Metrics & Analytics
# ============================================================================

@router.get("/metrics/realtime/{device_id}")
async def get_realtime_metrics(
    device_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get real-time metrics for a device
    Returns current status, latest readings, and today's summary
    """
    from server import db
    
    # Get device
    device = await db.iot_devices.find_one({"device_id": device_id}, {"_id": 0})
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Check permissions
    if current_user["role"] == "customer" and device.get("customer_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get latest reading
    latest_reading = await db.iot_readings.find_one(
        {"device_id": device_id},
        {"_id": 0},
        sort=[("timestamp", -1)]
    )
    
    # Get today's stats
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    today_readings = []
    cursor = db.iot_readings.find(
        {"device_id": device_id, "timestamp": {"$gte": today_start}},
        {"_id": 0}
    )
    async for reading in cursor:
        today_readings.append(reading)
    
    # Calculate today's totals
    today_volume = sum(r.get("volume_consumed", 0) for r in today_readings)
    today_cost = sum(r.get("volume_consumed", 0) * r.get("cost_per_liter", 10) / 1000 for r in today_readings)
    
    # Build metrics summary
    metrics = IoTMetricsSummary(
        device_id=device_id,
        device_name=device.get("device_name", "Unknown"),
        status=device.get("status", DeviceStatus.OFFLINE),
        last_updated=latest_reading.get("timestamp") if latest_reading else datetime.utcnow(),
        current_flow_rate=latest_reading.get("flow_rate", 0) if latest_reading else 0,
        current_temperature=latest_reading.get("temperature") if latest_reading else None,
        current_pressure=latest_reading.get("pressure") if latest_reading else None,
        today_volume=today_volume,
        today_cost=today_cost,
        battery_level=latest_reading.get("battery_level") if latest_reading else None,
        signal_strength=latest_reading.get("signal_strength") if latest_reading else None,
        valve_status=latest_reading.get("valve_status", "unknown") if latest_reading else "unknown",
        has_alerts=False,
        alert_count=0
    )
    
    return {
        "success": True,
        "metrics": metrics.model_dump(),
        "latest_reading": latest_reading,
        "today_readings_count": len(today_readings)
    }


@router.get("/metrics/history/{device_id}")
async def get_device_history(
    device_id: str,
    hours: int = Query(24, description="Hours of history to retrieve"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get historical readings for a device
    Used for charts and analytics
    """
    from server import db
    
    # Get device
    device = await db.iot_devices.find_one({"device_id": device_id}, {"_id": 0})
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Check permissions
    if current_user["role"] == "customer" and device.get("customer_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get readings from last N hours
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    
    readings = []
    cursor = db.iot_readings.find(
        {"device_id": device_id, "timestamp": {"$gte": time_threshold}},
        {"_id": 0},
        sort=[("timestamp", 1)]
    )
    
    async for reading in cursor:
        readings.append(reading)
    
    return {
        "success": True,
        "device_id": device_id,
        "hours": hours,
        "count": len(readings),
        "readings": readings
    }


# ============================================================================
# Device Commands
# ============================================================================

@router.post("/commands/send")
async def send_device_command(
    command: IoTDeviceCommand,
    current_user: dict = Depends(get_current_user)
):
    """
    Send command to IoT device
    Admin/Technician can send commands to control devices
    """
    from server import db
    
    # Check permissions
    if current_user["role"] not in ["admin", "technician"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Verify device exists
    device = await db.iot_devices.find_one({"device_id": command.device_id})
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Store command
    command_dict = command.model_dump()
    command_dict["issued_by"] = current_user["id"]
    command_dict["issued_at"] = datetime.utcnow()
    
    await db.iot_commands.insert_one(command_dict)
    
    # Broadcast command to device (via WebSocket or MQTT)
    await manager.broadcast_to_device_subscribers(command.device_id, {
        "type": "command",
        "device_id": command.device_id,
        "data": command_dict
    })
    
    return {
        "success": True,
        "message": "Command sent successfully",
        "command_id": command.command_id,
        "device_id": command.device_id
    }


@router.get("/commands/{device_id}")
async def get_device_commands(
    device_id: str,
    limit: int = Query(50, le=200),
    current_user: dict = Depends(get_current_user)
):
    """Get command history for a device"""
    from server import db
    
    # Verify device
    device = await db.iot_devices.find_one({"device_id": device_id})
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Get commands
    commands = []
    cursor = db.iot_commands.find(
        {"device_id": device_id},
        {"_id": 0},
        sort=[("issued_at", -1)],
        limit=limit
    )
    
    async for cmd in cursor:
        commands.append(cmd)
    
    return {
        "success": True,
        "device_id": device_id,
        "count": len(commands),
        "commands": commands
    }


# ============================================================================
# Connection Status
# ============================================================================

@router.get("/status/connections")
async def get_connection_status(
    current_user: dict = Depends(get_current_user)
):
    """
    Get WebSocket connection status
    Shows how many clients are connected and subscribed
    """
    return {
        "success": True,
        "total_connections": manager.get_connection_count(),
        "active_subscriptions": len(manager.device_subscriptions),
        "timestamp": datetime.utcnow().isoformat()
    }
