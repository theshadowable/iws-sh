from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, status
from datetime import datetime, timedelta
from typing import List, Optional
import json

from models import User, UserRole
from auth import get_current_user, require_role
from technician_models import (
    MeterReading, MeterReadingCreate,
    WorkOrder, WorkOrderCreate, WorkOrderUpdate,
    MaintenanceSchedule, MaintenanceScheduleCreate, MaintenanceScheduleUpdate,
    LeakAlert, LeakAlertCreate, LeakAlertUpdate,
    TechnicianReport, TechnicianReportCreate,
    MeterCondition, MeterConditionCreate,
    CustomerDataTechnician
)
from technician_utils import (
    save_uploaded_file, process_ocr, detect_leak,
    generate_technician_report_data, optimize_route
)

router = APIRouter(prefix="/technician", tags=["Technician"])


# ==================== METER READING ROUTES ====================

@router.post("/meter-readings", response_model=MeterReading, status_code=status.HTTP_201_CREATED)
async def create_meter_reading(
    reading_data: MeterReadingCreate,
    current_user: User = Depends(require_role([UserRole.TECHNICIAN, UserRole.ADMIN])),
    db = None
):
    """Submit a new meter reading (manual entry)"""
    from main import db as database
    
    reading = MeterReading(**reading_data.model_dump(), technician_id=current_user.id)
    reading_dict = reading.model_dump()
    reading_dict['reading_date'] = reading_dict['reading_date'].isoformat()
    reading_dict['created_at'] = reading_dict['created_at'].isoformat()
    
    await database.meter_readings.insert_one(reading_dict)
    
    # Update device's last reading
    await database.devices.update_one(
        {"id": reading_data.device_id},
        {"$set": {"last_reading_date": reading.reading_date.isoformat()}}
    )
    
    return reading


@router.post("/meter-readings/ocr", response_model=MeterReading)
async def create_meter_reading_with_ocr(
    device_id: str = Form(...),
    reading_method: str = Form(...),
    location_lat: Optional[float] = Form(None),
    location_lng: Optional[float] = Form(None),
    notes: Optional[str] = Form(None),
    photo: UploadFile = File(...),
    current_user: User = Depends(require_role([UserRole.TECHNICIAN, UserRole.ADMIN]))
):
    """Submit meter reading with photo OCR processing"""
    from main import db as database
    
    # Save uploaded photo
    file_content = await photo.read()
    photo_path = save_uploaded_file(file_content, photo.filename, "meter_photos")
    
    # Process OCR
    reading_value, confidence = process_ocr(photo_path)
    
    if reading_value is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract reading from photo. Please enter manually."
        )
    
    # Create reading
    reading = MeterReading(
        device_id=device_id,
        reading_value=reading_value,
        reading_method=reading_method,
        technician_id=current_user.id,
        photo_path=photo_path,
        location_lat=location_lat,
        location_lng=location_lng,
        notes=notes,
        ocr_confidence=confidence
    )
    
    reading_dict = reading.model_dump()
    reading_dict['reading_date'] = reading_dict['reading_date'].isoformat()
    reading_dict['created_at'] = reading_dict['created_at'].isoformat()
    
    await database.meter_readings.insert_one(reading_dict)
    
    return reading


@router.get("/meter-readings", response_model=List[MeterReading])
async def get_meter_readings(
    device_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_role([UserRole.TECHNICIAN, UserRole.ADMIN]))
):
    """Get meter readings with optional filters"""
    from main import db as database
    
    query = {}
    if device_id:
        query['device_id'] = device_id
    if start_date:
        query['reading_date'] = {"$gte": start_date}
    if end_date:
        if 'reading_date' in query:
            query['reading_date']['$lte'] = end_date
        else:
            query['reading_date'] = {"$lte": end_date}
    
    # If technician, only show their readings
    if current_user.role == UserRole.TECHNICIAN:
        query['technician_id'] = current_user.id
    
    readings = await database.meter_readings.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    
    for reading in readings:
        if isinstance(reading.get('reading_date'), str):
            reading['reading_date'] = datetime.fromisoformat(reading['reading_date'])
        if isinstance(reading.get('created_at'), str):
            reading['created_at'] = datetime.fromisoformat(reading['created_at'])
    
    return readings


# ==================== WORK ORDER / TASK MANAGEMENT ROUTES ====================

@router.get("/work-orders", response_model=List[WorkOrder])
async def get_work_orders(
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_role([UserRole.TECHNICIAN, UserRole.ADMIN]))
):
    """Get work orders assigned to technician"""
    from main import db as database
    
    query = {}
    if current_user.role == UserRole.TECHNICIAN:
        query['assigned_to'] = current_user.id
    
    if status_filter:
        query['status'] = status_filter
    
    work_orders = await database.work_orders.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    
    for order in work_orders:
        if isinstance(order.get('created_at'), str):
            order['created_at'] = datetime.fromisoformat(order['created_at'])
        if isinstance(order.get('updated_at'), str):
            order['updated_at'] = datetime.fromisoformat(order['updated_at'])
        if order.get('scheduled_date') and isinstance(order['scheduled_date'], str):
            order['scheduled_date'] = datetime.fromisoformat(order['scheduled_date'])
        if order.get('completed_date') and isinstance(order['completed_date'], str):
            order['completed_date'] = datetime.fromisoformat(order['completed_date'])
    
    return work_orders


@router.post("/work-orders", response_model=WorkOrder, status_code=status.HTTP_201_CREATED)
async def create_work_order(
    work_order_data: WorkOrderCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Create a new work order (Admin only)"""
    from main import db as database
    
    work_order = WorkOrder(**work_order_data.model_dump(), created_by=current_user.id)
    work_order_dict = work_order.model_dump()
    work_order_dict['created_at'] = work_order_dict['created_at'].isoformat()
    work_order_dict['updated_at'] = work_order_dict['updated_at'].isoformat()
    if work_order_dict.get('scheduled_date'):
        work_order_dict['scheduled_date'] = work_order_dict['scheduled_date'].isoformat()
    if work_order_dict.get('completed_date'):
        work_order_dict['completed_date'] = work_order_dict['completed_date'].isoformat()
    
    await database.work_orders.insert_one(work_order_dict)
    return work_order


@router.put("/work-orders/{order_id}", response_model=WorkOrder)
async def update_work_order(
    order_id: str,
    order_update: WorkOrderUpdate,
    current_user: User = Depends(require_role([UserRole.TECHNICIAN, UserRole.ADMIN]))
):
    """Update work order status"""
    from main import db as database
    
    update_data = order_update.model_dump(exclude_unset=True)
    update_data['updated_at'] = datetime.utcnow().isoformat()
    
    if 'scheduled_date' in update_data and update_data['scheduled_date']:
        update_data['scheduled_date'] = update_data['scheduled_date'].isoformat()
    if 'completed_date' in update_data and update_data['completed_date']:
        update_data['completed_date'] = update_data['completed_date'].isoformat()
    
    result = await database.work_orders.update_one(
        {"id": order_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    updated_order = await database.work_orders.find_one({"id": order_id}, {"_id": 0})
    if isinstance(updated_order.get('created_at'), str):
        updated_order['created_at'] = datetime.fromisoformat(updated_order['created_at'])
    if isinstance(updated_order.get('updated_at'), str):
        updated_order['updated_at'] = datetime.fromisoformat(updated_order['updated_at'])
    if updated_order.get('scheduled_date') and isinstance(updated_order['scheduled_date'], str):
        updated_order['scheduled_date'] = datetime.fromisoformat(updated_order['scheduled_date'])
    if updated_order.get('completed_date') and isinstance(updated_order['completed_date'], str):
        updated_order['completed_date'] = datetime.fromisoformat(updated_order['completed_date'])
    
    return WorkOrder(**updated_order)


# ==================== MAINTENANCE SCHEDULE ROUTES ====================

@router.get("/maintenance-schedules", response_model=List[MaintenanceSchedule])
async def get_maintenance_schedules(
    device_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    current_user: User = Depends(require_role([UserRole.TECHNICIAN, UserRole.ADMIN]))
):
    """Get maintenance schedules"""
    from main import db as database
    
    query = {}
    if current_user.role == UserRole.TECHNICIAN:
        query['assigned_to'] = current_user.id
    if device_id:
        query['device_id'] = device_id
    if status_filter:
        query['status'] = status_filter
    
    schedules = await database.maintenance_schedules.find(query, {"_id": 0}).to_list(100)
    
    for schedule in schedules:
        if isinstance(schedule.get('schedule_date'), str):
            schedule['schedule_date'] = datetime.fromisoformat(schedule['schedule_date'])
        if schedule.get('completed_date') and isinstance(schedule['completed_date'], str):
            schedule['completed_date'] = datetime.fromisoformat(schedule['completed_date'])
        if isinstance(schedule.get('created_at'), str):
            schedule['created_at'] = datetime.fromisoformat(schedule['created_at'])
        if isinstance(schedule.get('updated_at'), str):
            schedule['updated_at'] = datetime.fromisoformat(schedule['updated_at'])
    
    return schedules


@router.post("/maintenance-schedules", response_model=MaintenanceSchedule, status_code=status.HTTP_201_CREATED)
async def create_maintenance_schedule(
    schedule_data: MaintenanceScheduleCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TECHNICIAN]))
):
    """Create maintenance schedule"""
    from main import db as database
    
    schedule = MaintenanceSchedule(**schedule_data.model_dump())
    schedule_dict = schedule.model_dump()
    schedule_dict['schedule_date'] = schedule_dict['schedule_date'].isoformat()
    if schedule_dict.get('completed_date'):
        schedule_dict['completed_date'] = schedule_dict['completed_date'].isoformat()
    schedule_dict['created_at'] = schedule_dict['created_at'].isoformat()
    schedule_dict['updated_at'] = schedule_dict['updated_at'].isoformat()
    
    await database.maintenance_schedules.insert_one(schedule_dict)
    return schedule


# ==================== LEAK DETECTION ROUTES ====================

@router.get("/leak-alerts", response_model=List[LeakAlert])
async def get_leak_alerts(
    device_id: Optional[str] = None,
    is_resolved: Optional[bool] = None,
    current_user: User = Depends(require_role([UserRole.TECHNICIAN, UserRole.ADMIN]))
):
    """Get leak alerts"""
    from main import db as database
    
    query = {}
    if device_id:
        query['device_id'] = device_id
    if is_resolved is not None:
        query['is_resolved'] = is_resolved
    
    alerts = await database.leak_alerts.find(query, {"_id": 0}).to_list(100)
    
    for alert in alerts:
        if isinstance(alert.get('detected_at'), str):
            alert['detected_at'] = datetime.fromisoformat(alert['detected_at'])
        if alert.get('resolved_at') and isinstance(alert['resolved_at'], str):
            alert['resolved_at'] = datetime.fromisoformat(alert['resolved_at'])
    
    return alerts


@router.post("/leak-detection/{device_id}")
async def run_leak_detection(
    device_id: str,
    current_user: User = Depends(require_role([UserRole.TECHNICIAN, UserRole.ADMIN]))
):
    """Run leak detection for a device"""
    from main import db as database
    
    # Get water usage records for last 24 hours
    start_time = datetime.utcnow() - timedelta(hours=24)
    water_usage = await database.water_usage.find(
        {
            "device_id": device_id,
            "timestamp": {"$gte": start_time.isoformat()}
        },
        {"_id": 0}
    ).to_list(1000)
    
    # Convert timestamp strings to datetime objects for analysis
    for record in water_usage:
        if isinstance(record.get('timestamp'), str):
            record['timestamp'] = datetime.fromisoformat(record['timestamp'])
    
    # Run leak detection
    result = detect_leak(device_id, water_usage)
    
    # If leak detected, create alert
    if result['has_leak']:
        alert = LeakAlert(
            device_id=device_id,
            alert_type=result['leak_type'],
            severity="critical" if result['confidence'] > 0.8 else "warning",
            flow_rate=result['avg_flow_rate'],
            estimated_loss=result['estimated_loss_liters']
        )
        
        alert_dict = alert.model_dump()
        alert_dict['detected_at'] = alert_dict['detected_at'].isoformat()
        
        await database.leak_alerts.insert_one(alert_dict)
    
    return result


@router.put("/leak-alerts/{alert_id}/resolve", response_model=LeakAlert)
async def resolve_leak_alert(
    alert_id: str,
    resolution_notes: str,
    current_user: User = Depends(require_role([UserRole.TECHNICIAN, UserRole.ADMIN]))
):
    """Mark leak alert as resolved"""
    from main import db as database
    
    update_data = {
        "is_resolved": True,
        "resolved_at": datetime.utcnow().isoformat(),
        "resolved_by": current_user.id,
        "resolution_notes": resolution_notes
    }
    
    result = await database.leak_alerts.update_one(
        {"id": alert_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    updated_alert = await database.leak_alerts.find_one({"id": alert_id}, {"_id": 0})
    if isinstance(updated_alert.get('detected_at'), str):
        updated_alert['detected_at'] = datetime.fromisoformat(updated_alert['detected_at'])
    if updated_alert.get('resolved_at') and isinstance(updated_alert['resolved_at'], str):
        updated_alert['resolved_at'] = datetime.fromisoformat(updated_alert['resolved_at'])
    
    return LeakAlert(**updated_alert)


# ==================== REPORT GENERATION ROUTES ====================

@router.post("/reports/generate", response_model=TechnicianReport)
async def generate_technician_report(
    report_data: TechnicianReportCreate,
    current_user: User = Depends(require_role([UserRole.TECHNICIAN, UserRole.ADMIN]))
):
    """Generate technician performance report"""
    from main import db as database
    
    technician_id = current_user.id
    if current_user.role == UserRole.ADMIN and report_data.technician_id:
        technician_id = report_data.technician_id
    
    # Get readings
    readings = await database.meter_readings.find({
        "technician_id": technician_id,
        "reading_date": {
            "$gte": report_data.start_date.isoformat(),
            "$lte": report_data.end_date.isoformat()
        }
    }, {"_id": 0}).to_list(1000)
    
    # Get work orders
    work_orders = await database.work_orders.find({
        "assigned_to": technician_id,
        "created_at": {
            "$gte": report_data.start_date.isoformat(),
            "$lte": report_data.end_date.isoformat()
        }
    }, {"_id": 0}).to_list(1000)
    
    # Get issues found
    issues = await database.meter_conditions.find({
        "technician_id": technician_id,
        "check_date": {
            "$gte": report_data.start_date.isoformat(),
            "$lte": report_data.end_date.isoformat()
        },
        "is_functioning": False
    }, {"_id": 0}).to_list(1000)
    
    # Generate report data
    report_stats = generate_technician_report_data(
        technician_id,
        report_data.start_date,
        report_data.end_date,
        readings,
        work_orders,
        issues
    )
    
    # Create report
    report = TechnicianReport(
        report_type=report_data.report_type,
        technician_id=technician_id,
        start_date=report_data.start_date,
        end_date=report_data.end_date,
        **report_stats
    )
    
    report_dict = report.model_dump()
    report_dict['start_date'] = report_dict['start_date'].isoformat()
    report_dict['end_date'] = report_dict['end_date'].isoformat()
    report_dict['generated_at'] = report_dict['generated_at'].isoformat()
    
    await database.technician_reports.insert_one(report_dict)
    
    return report


# ==================== METER CONDITION CHECK ROUTES ====================

@router.post("/meter-condition", response_model=MeterCondition, status_code=status.HTTP_201_CREATED)
async def create_meter_condition_check(
    condition_data: MeterConditionCreate,
    current_user: User = Depends(require_role([UserRole.TECHNICIAN, UserRole.ADMIN]))
):
    """Submit meter condition check"""
    from main import db as database
    
    condition = MeterCondition(**condition_data.model_dump())
    condition_dict = condition.model_dump()
    condition_dict['check_date'] = condition_dict['check_date'].isoformat()
    
    await database.meter_conditions.insert_one(condition_dict)
    
    # Update device status if faulty
    if not condition.is_functioning or condition.condition_status == "faulty":
        await database.devices.update_one(
            {"id": condition_data.device_id},
            {"$set": {"status": "faulty"}}
        )
    
    return condition


@router.get("/meter-condition/{device_id}", response_model=List[MeterCondition])
async def get_meter_condition_history(
    device_id: str,
    current_user: User = Depends(require_role([UserRole.TECHNICIAN, UserRole.ADMIN]))
):
    """Get meter condition check history"""
    from main import db as database
    
    conditions = await database.meter_conditions.find(
        {"device_id": device_id},
        {"_id": 0}
    ).to_list(100)
    
    for condition in conditions:
        if isinstance(condition.get('check_date'), str):
            condition['check_date'] = datetime.fromisoformat(condition['check_date'])
    
    return conditions


# ==================== CUSTOMER DATA FOR TECHNICIANS ====================

@router.get("/customers-data", response_model=List[CustomerDataTechnician])
async def get_customers_data_for_technician(
    current_user: User = Depends(require_role([UserRole.TECHNICIAN, UserRole.ADMIN]))
):
    """Get comprehensive customer data for field work"""
    from main import db as database
    
    # Aggregate data from multiple collections
    pipeline = [
        {
            "$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "id",
                "as": "user"
            }
        },
        {"$unwind": "$user"},
        {
            "$lookup": {
                "from": "devices",
                "localField": "id",
                "foreignField": "customer_id",
                "as": "devices"
            }
        },
        {"$unwind": {"path": "$devices", "preserveNullAndEmptyArrays": True}},
        {
            "$lookup": {
                "from": "properties",
                "localField": "devices.property_id",
                "foreignField": "id",
                "as": "property"
            }
        },
        {"$unwind": {"path": "$property", "preserveNullAndEmptyArrays": True}}
    ]
    
    results = await database.customers.aggregate(pipeline).to_list(1000)
    
    customer_data_list = []
    for result in results:
        if result.get('devices'):
            customer_data = CustomerDataTechnician(
                customer_id=result['id'],
                customer_number=result['customer_number'],
                full_name=result['user']['full_name'],
                email=result['user']['email'],
                phone=result['user'].get('phone', ''),
                address=result['address'],
                property_id=result.get('property', {}).get('id', ''),
                property_name=result.get('property', {}).get('property_name', ''),
                property_type=result.get('property', {}).get('property_type', ''),
                device_id=result['devices']['id'],
                device_name=result['devices']['device_name'],
                device_status=result['devices']['status'],
                current_balance=result['devices'].get('current_balance', 0.0),
                total_water_consumed=result['devices'].get('total_water_consumed', 0.0),
                location_lat=result.get('property', {}).get('latitude'),
                location_lng=result.get('property', {}).get('longitude')
            )
            customer_data_list.append(customer_data)
    
    return customer_data_list


# ==================== ROUTE OPTIMIZATION ====================

@router.post("/optimize-route")
async def optimize_technician_route(
    work_order_ids: List[str],
    current_user: User = Depends(require_role([UserRole.TECHNICIAN, UserRole.ADMIN]))
):
    """Optimize route for multiple work orders"""
    from main import db as database
    
    # Get work orders with locations
    locations = []
    for order_id in work_order_ids:
        order = await database.work_orders.find_one({"id": order_id}, {"_id": 0})
        if order and order.get('location_lat') and order.get('location_lng'):
            locations.append({
                "id": order_id,
                "lat": order['location_lat'],
                "lng": order['location_lng']
            })
    
    if not locations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No work orders with location data found"
        )
    
    # Optimize route
    optimized_route = optimize_route(locations)
    
    return {
        "optimized_order": optimized_route,
        "total_locations": len(locations)
    }
