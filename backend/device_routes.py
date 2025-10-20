"""
Comprehensive Device Management Routes
Enhanced endpoints for device operations, monitoring, and analytics
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta
from models import User, UserRole
from auth import get_current_user, require_role
from device_models import (
    DeviceActivity, DeviceActivityCreate, DeviceActivityType,
    DeviceStats, DeviceHealth, ConnectionStatus,
    DeviceBatchOperation, DeviceBatchResult,
    DeviceFilter, DeviceComprehensive
)

router = APIRouter(prefix="/devices", tags=["devices-enhanced"])


@router.get("/comprehensive", response_model=List[DeviceComprehensive])
async def get_devices_comprehensive(
    status: Optional[str] = None,
    device_type: Optional[str] = None,
    customer_id: Optional[str] = None,
    property_id: Optional[str] = None,
    health_status: Optional[str] = None,
    connection_status: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive device list with related data, stats, and filters
    """
    from server import db
    
    # Build query
    query = {}
    
    # Apply filters
    if status:
        query['status'] = {"$in": status.split(',')}
    if device_type:
        query['device_type'] = {"$in": device_type.split(',')}
    if customer_id:
        query['customer_id'] = customer_id
    if property_id:
        query['property_id'] = property_id
    
    # Search in device_id or device_name
    if search:
        query['$or'] = [
            {'device_id': {'$regex': search, '$options': 'i'}},
            {'device_name': {'$regex': search, '$options': 'i'}}
        ]
    
    # Customer role: only see their devices
    if current_user.role == UserRole.CUSTOMER:
        customer = await db.customers.find_one({"user_id": current_user.id})
        if customer:
            query['customer_id'] = customer['id']
        else:
            return []
    
    # Sort order
    sort_direction = -1 if sort_order == "desc" else 1
    
    # Get devices
    devices = await db.devices.find(query, {"_id": 0}).sort(sort_by, sort_direction).skip(skip).limit(limit).to_list(limit)
    
    # Enrich devices with related data
    comprehensive_devices = []
    for device in devices:
        # Get property info
        property_doc = await db.properties.find_one({"id": device['property_id']}, {"_id": 0})
        
        # Get customer info
        customer_doc = await db.customers.find_one({"id": device['customer_id']}, {"_id": 0})
        customer_user = None
        if customer_doc:
            customer_user = await db.users.find_one({"id": customer_doc['user_id']}, {"_id": 0})
        
        # Calculate device stats
        stats = await calculate_device_stats(db, device['id'])
        
        # Get activity count
        activity_count = await db.device_activities.count_documents({"device_id": device['id']})
        
        # Get alert count
        alert_count = await db.device_alerts.count_documents({"device_id": device['id'], "is_resolved": False})
        
        # Parse timestamps
        if isinstance(device.get('created_at'), str):
            device['created_at'] = datetime.fromisoformat(device['created_at'])
        if isinstance(device.get('updated_at'), str):
            device['updated_at'] = datetime.fromisoformat(device['updated_at'])
        if isinstance(device.get('installation_date'), str):
            device['installation_date'] = datetime.fromisoformat(device['installation_date'])
        if device.get('last_maintenance_date') and isinstance(device['last_maintenance_date'], str):
            device['last_maintenance_date'] = datetime.fromisoformat(device['last_maintenance_date'])
        
        comprehensive_device = DeviceComprehensive(
            id=device['id'],
            device_id=device['device_id'],
            device_name=device.get('device_name', device['device_id']),
            device_type=device.get('device_type', 'smart_meter'),
            status=device['status'],
            property_id=device['property_id'],
            property_name=property_doc.get('property_name') if property_doc else None,
            property_address=property_doc.get('address') if property_doc else None,
            customer_id=device['customer_id'],
            customer_name=customer_user.get('full_name') if customer_user else None,
            customer_phone=customer_user.get('phone') if customer_user else None,
            installation_date=device['installation_date'],
            last_maintenance_date=device.get('last_maintenance_date'),
            firmware_version=device.get('firmware_version'),
            notes=device.get('notes'),
            current_balance=device.get('current_balance', 0.0),
            total_water_consumed=device.get('total_water_consumed', 0.0),
            stats=stats,
            activity_count=activity_count,
            alert_count=alert_count,
            created_at=device['created_at'],
            updated_at=device['updated_at']
        )
        
        comprehensive_devices.append(comprehensive_device)
    
    return comprehensive_devices


@router.get("/{device_id}/stats", response_model=DeviceStats)
async def get_device_stats(
    device_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed statistics for a specific device"""
    from server import db
    
    # Check device exists
    device = await db.devices.find_one({"id": device_id}, {"_id": 0})
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Calculate stats
    stats = await calculate_device_stats(db, device_id)
    
    return stats


@router.get("/{device_id}/activities", response_model=List[DeviceActivity])
async def get_device_activities(
    device_id: str,
    activity_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get activity log for a specific device"""
    from server import db
    
    query = {"device_id": device_id}
    if activity_type:
        query['activity_type'] = activity_type
    
    activities = await db.device_activities.find(query, {"_id": 0}).sort("timestamp", -1).skip(skip).limit(limit).to_list(limit)
    
    # Parse timestamps
    for activity in activities:
        if isinstance(activity.get('timestamp'), str):
            activity['timestamp'] = datetime.fromisoformat(activity['timestamp'])
    
    return activities


@router.post("/{device_id}/activities", response_model=DeviceActivity)
async def create_device_activity(
    device_id: str,
    activity_data: DeviceActivityCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TECHNICIAN]))
):
    """Create a new activity log entry for a device"""
    from server import db
    
    # Verify device exists
    device = await db.devices.find_one({"id": device_id})
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Set performed_by to current user if not specified
    if not activity_data.performed_by:
        activity_data.performed_by = current_user.id
    
    activity = DeviceActivity(**activity_data.model_dump())
    activity_dict = activity.model_dump()
    activity_dict['timestamp'] = activity_dict['timestamp'].isoformat()
    
    await db.device_activities.insert_one(activity_dict)
    
    return activity


@router.post("/batch", response_model=DeviceBatchResult)
async def batch_device_operation(
    operation_data: DeviceBatchOperation,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TECHNICIAN]))
):
    """
    Perform batch operations on multiple devices
    Operations: activate, deactivate, maintenance, delete
    """
    from server import db
    
    success_devices = []
    failed_devices = []
    
    for device_id in operation_data.device_ids:
        try:
            device = await db.devices.find_one({"id": device_id})
            if not device:
                failed_devices.append({"device_id": device_id, "reason": "Device not found"})
                continue
            
            if operation_data.operation == "activate":
                await db.devices.update_one(
                    {"id": device_id},
                    {"$set": {"status": "active", "updated_at": datetime.utcnow().isoformat()}}
                )
                # Log activity
                await create_activity_log(db, device_id, DeviceActivityType.STATUS_CHANGE, 
                                        "Device Activated", f"Device activated via batch operation", current_user.id)
                
            elif operation_data.operation == "deactivate":
                await db.devices.update_one(
                    {"id": device_id},
                    {"$set": {"status": "inactive", "updated_at": datetime.utcnow().isoformat()}}
                )
                await create_activity_log(db, device_id, DeviceActivityType.STATUS_CHANGE, 
                                        "Device Deactivated", f"Device deactivated via batch operation", current_user.id)
                
            elif operation_data.operation == "maintenance":
                await db.devices.update_one(
                    {"id": device_id},
                    {"$set": {"status": "maintenance", "updated_at": datetime.utcnow().isoformat()}}
                )
                await create_activity_log(db, device_id, DeviceActivityType.MAINTENANCE, 
                                        "Maintenance Mode", f"Device set to maintenance mode", current_user.id)
                
            elif operation_data.operation == "delete":
                # Only admin can delete
                if current_user.role != UserRole.ADMIN:
                    failed_devices.append({"device_id": device_id, "reason": "Only admin can delete devices"})
                    continue
                await db.devices.delete_one({"id": device_id})
            
            success_devices.append(device_id)
            
        except Exception as e:
            failed_devices.append({"device_id": device_id, "reason": str(e)})
    
    return DeviceBatchResult(
        success_count=len(success_devices),
        failed_count=len(failed_devices),
        success_devices=success_devices,
        failed_devices=failed_devices,
        message=f"Operation completed: {len(success_devices)} succeeded, {len(failed_devices)} failed"
    )


@router.get("/summary/stats")
async def get_devices_summary(
    current_user: User = Depends(get_current_user)
):
    """Get summary statistics for all devices"""
    from server import db
    
    query = {}
    
    # Customer role: only their devices
    if current_user.role == UserRole.CUSTOMER:
        customer = await db.customers.find_one({"user_id": current_user.id})
        if customer:
            query['customer_id'] = customer['id']
        else:
            return {
                "total_devices": 0,
                "active_devices": 0,
                "inactive_devices": 0,
                "maintenance_devices": 0,
                "faulty_devices": 0,
                "online_devices": 0,
                "offline_devices": 0,
                "total_alerts": 0
            }
    
    # Count by status
    total_devices = await db.devices.count_documents(query)
    active_devices = await db.devices.count_documents({**query, "status": "active"})
    inactive_devices = await db.devices.count_documents({**query, "status": "inactive"})
    maintenance_devices = await db.devices.count_documents({**query, "status": "maintenance"})
    faulty_devices = await db.devices.count_documents({**query, "status": "faulty"})
    
    # Mock online/offline for now (will be real-time with IoT)
    online_devices = int(active_devices * 0.9)  # Assume 90% of active devices are online
    offline_devices = total_devices - online_devices
    
    # Count active alerts
    device_ids = [d['id'] for d in await db.devices.find(query, {"_id": 0, "id": 1}).to_list(None)]
    total_alerts = await db.device_alerts.count_documents({
        "device_id": {"$in": device_ids},
        "is_resolved": False
    })
    
    return {
        "total_devices": total_devices,
        "active_devices": active_devices,
        "inactive_devices": inactive_devices,
        "maintenance_devices": maintenance_devices,
        "faulty_devices": faulty_devices,
        "online_devices": online_devices,
        "offline_devices": offline_devices,
        "total_alerts": total_alerts
    }


# Helper Functions

async def calculate_device_stats(db, device_id: str) -> DeviceStats:
    """Calculate comprehensive statistics for a device"""
    
    # Get device
    device = await db.devices.find_one({"id": device_id}, {"_id": 0})
    if not device:
        return None
    
    # Calculate usage stats from water_usage collection
    usage_pipeline = [
        {"$match": {"device_id": device_id}},
        {"$group": {
            "_id": None,
            "total_usage": {"$sum": "$water_consumed"},
            "total_cost": {"$sum": "$cost"},
            "count": {"$sum": 1}
        }}
    ]
    usage_stats = await db.water_usage.aggregate(usage_pipeline).to_list(1)
    
    total_usage = usage_stats[0]['total_usage'] if usage_stats else 0.0
    total_cost = usage_stats[0]['total_cost'] if usage_stats else 0.0
    
    # Calculate daily average (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_pipeline = [
        {"$match": {
            "device_id": device_id,
            "reading_date": {"$gte": thirty_days_ago.isoformat()}
        }},
        {"$group": {
            "_id": None,
            "total": {"$sum": "$water_consumed"}
        }}
    ]
    daily_stats = await db.water_usage.aggregate(daily_pipeline).to_list(1)
    avg_daily_usage = (daily_stats[0]['total'] / 30) if daily_stats else 0.0
    
    # Find peak usage day
    peak_pipeline = [
        {"$match": {"device_id": device_id}},
        {"$group": {
            "_id": {"$substr": ["$reading_date", 0, 10]},
            "daily_total": {"$sum": "$water_consumed"}
        }},
        {"$sort": {"daily_total": -1}},
        {"$limit": 1}
    ]
    peak_stats = await db.water_usage.aggregate(peak_pipeline).to_list(1)
    peak_usage = peak_stats[0]['daily_total'] if peak_stats else 0.0
    
    # Get last reading date
    last_reading = await db.water_usage.find_one(
        {"device_id": device_id},
        {"_id": 0, "reading_date": 1},
        sort=[("reading_date", -1)]
    )
    last_reading_date = None
    if last_reading:
        last_reading_date = datetime.fromisoformat(last_reading['reading_date']) if isinstance(last_reading['reading_date'], str) else last_reading['reading_date']
    
    # Calculate uptime (mock for now, will be real with IoT)
    uptime_percentage = 95.0 if device['status'] == 'active' else 0.0
    
    # Calculate health score
    health_score = calculate_health_score(device, last_reading_date)
    health_status = get_health_status(health_score)
    
    # Determine connection status (mock for now)
    connection_status = ConnectionStatus.ONLINE if device['status'] == 'active' else ConnectionStatus.OFFLINE
    
    # Count active alerts
    alert_count = await db.device_alerts.count_documents({
        "device_id": device_id,
        "is_resolved": False
    })
    
    # Calculate maintenance due days
    maintenance_due_days = None
    if device.get('last_maintenance_date'):
        last_maint = device['last_maintenance_date']
        if isinstance(last_maint, str):
            last_maint = datetime.fromisoformat(last_maint)
        # Assume maintenance every 180 days
        next_maint = last_maint + timedelta(days=180)
        maintenance_due_days = (next_maint - datetime.utcnow()).days
    
    return DeviceStats(
        device_id=device_id,
        total_usage=round(total_usage, 2),
        total_cost=round(total_cost, 2),
        avg_daily_usage=round(avg_daily_usage, 2),
        peak_usage=round(peak_usage, 2),
        uptime_percentage=round(uptime_percentage, 1),
        last_reading_date=last_reading_date,
        health_score=round(health_score, 1),
        health_status=health_status,
        connection_status=connection_status,
        alert_count=alert_count,
        maintenance_due_days=maintenance_due_days
    )


def calculate_health_score(device: dict, last_reading_date: datetime = None) -> float:
    """Calculate device health score (0-100)"""
    score = 100.0
    
    # Deduct for inactive status
    if device['status'] == 'inactive':
        score -= 50
    elif device['status'] == 'faulty':
        score -= 70
    elif device['status'] == 'maintenance':
        score -= 30
    
    # Deduct for old last reading (no recent data)
    if last_reading_date:
        days_since_reading = (datetime.utcnow() - last_reading_date).days
        if days_since_reading > 7:
            score -= min(30, days_since_reading * 2)
    else:
        score -= 40  # No readings at all
    
    # Deduct for overdue maintenance
    if device.get('last_maintenance_date'):
        last_maint = device['last_maintenance_date']
        if isinstance(last_maint, str):
            last_maint = datetime.fromisoformat(last_maint)
        days_since_maint = (datetime.utcnow() - last_maint).days
        if days_since_maint > 180:  # Overdue
            score -= min(20, (days_since_maint - 180) / 10)
    
    return max(0, min(100, score))


def get_health_status(health_score: float) -> DeviceHealth:
    """Convert health score to status"""
    if health_score >= 90:
        return DeviceHealth.EXCELLENT
    elif health_score >= 70:
        return DeviceHealth.GOOD
    elif health_score >= 50:
        return DeviceHealth.FAIR
    else:
        return DeviceHealth.POOR


async def create_activity_log(db, device_id: str, activity_type: DeviceActivityType, 
                             title: str, description: str, performed_by: str):
    """Helper to create activity log"""
    activity = DeviceActivity(
        device_id=device_id,
        activity_type=activity_type,
        title=title,
        description=description,
        performed_by=performed_by
    )
    activity_dict = activity.model_dump()
    activity_dict['timestamp'] = activity_dict['timestamp'].isoformat()
    
    await db.device_activities.insert_one(activity_dict)
