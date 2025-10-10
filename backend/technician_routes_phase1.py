"""
Technician API Routes - Phase 1
Endpoints for: Meter Readings, Task Management, Customer Data
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from technician_models_extended import (
    MeterReading, MeterReadingCreate, MeterReadingUpdate, MeterReadingWithDetails,
    Task, TaskCreate, TaskUpdate, TaskWithDetails,
    TaskStatus, TaskPriority, TaskType, ReadingStatus,
    TaskAssignmentRequest, TaskAssignmentResponse,
    TechnicianLocation, MeterConditionCheck, UsageHistory
)
from auth import get_current_user, require_role
from models import User, UserRole

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/technician", tags=["Technician"])


# ==================== HELPER FUNCTIONS ====================

async def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two coordinates in kilometers using Haversine formula"""
    from math import radians, cos, sin, asin, sqrt
    
    # Convert to radians
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r


async def find_nearest_technician(db: AsyncIOMotorDatabase, task_location: dict) -> Optional[str]:
    """
    Find nearest active technician to task location
    Returns technician_id or None
    """
    if not task_location.get('location_lat') or not task_location.get('location_lng'):
        return None
    
    # Get all active technicians with location data
    active_technicians = await db.technician_locations.find({
        "is_active": True,
        "timestamp": {"$gte": datetime.utcnow() - timedelta(minutes=30)}  # Active in last 30 min
    }).to_list(None)
    
    if not active_technicians:
        return None
    
    # Calculate distances
    nearest = None
    min_distance = float('inf')
    
    for tech in active_technicians:
        distance = await calculate_distance(
            task_location['location_lat'],
            task_location['location_lng'],
            tech['latitude'],
            tech['longitude']
        )
        
        if distance < min_distance:
            min_distance = distance
            nearest = tech['technician_id']
    
    # Only assign if within 50km
    if min_distance <= 50:
        return nearest
    
    return None


async def get_customer_usage_history(db: AsyncIOMotorDatabase, customer_id: str, limit: int = 12) -> List[dict]:
    """Get customer's usage history for the last N periods"""
    history = await db.usage_history.find(
        {"customer_id": customer_id}
    ).sort("period_end", -1).limit(limit).to_list(limit)
    
    return history


# ==================== METER READING ENDPOINTS ====================

@router.post("/meter-readings", response_model=MeterReading, status_code=status.HTTP_201_CREATED)
async def create_meter_reading(
    reading_data: MeterReadingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(lambda: None)
):
    """
    Create a new meter reading (manual or photo-based)
    Only technicians can create readings
    """
    # Check if user is technician
    if current_user.role != UserRole.TECHNICIAN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only technicians can submit meter readings"
        )
    
    # Verify meter exists
    meter = await db.devices.find_one({"id": reading_data.meter_id}, {"_id": 0})
    if not meter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meter not found"
        )
    
    # Verify customer exists
    customer = await db.customers.find_one({"id": reading_data.customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Get previous reading if not provided
    if reading_data.previous_reading is None:
        last_reading = await db.meter_readings.find_one(
            {"meter_id": reading_data.meter_id},
            {"_id": 0, "reading_value": 1},
            sort=[("reading_date", -1)]
        )
        previous_reading = last_reading['reading_value'] if last_reading else 0.0
    else:
        previous_reading = reading_data.previous_reading
    
    # Calculate consumption
    consumption = reading_data.reading_value - previous_reading
    
    # Create reading object
    reading = MeterReading(
        **reading_data.model_dump(),
        technician_id=current_user.id,
        previous_reading=previous_reading,
        consumption=consumption
    )
    
    # Insert to database
    reading_dict = reading.model_dump()
    reading_dict['created_at'] = reading_dict['created_at'].isoformat()
    reading_dict['updated_at'] = reading_dict['updated_at'].isoformat()
    reading_dict['reading_date'] = reading_dict['reading_date'].isoformat()
    
    await db.meter_readings.insert_one(reading_dict)
    
    # Update meter's last reading date
    await db.devices.update_one(
        {"id": reading_data.meter_id},
        {"$set": {
            "last_reading_date": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }}
    )
    
    logger.info(f"Meter reading created: {reading.id} by technician {current_user.id}")
    
    return reading


@router.get("/meter-readings", response_model=List[MeterReadingWithDetails])
async def get_meter_readings(
    technician_id: Optional[str] = Query(None, description="Filter by technician"),
    customer_id: Optional[str] = Query(None, description="Filter by customer"),
    meter_id: Optional[str] = Query(None, description="Filter by meter"),
    status: Optional[ReadingStatus] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(lambda: None)
):
    """
    Get meter readings with filters
    Technicians see their own readings, Admins see all
    """
    # Build filter
    filters = {}
    
    if current_user.role == UserRole.TECHNICIAN:
        filters['technician_id'] = current_user.id
    elif technician_id:
        filters['technician_id'] = technician_id
    
    if customer_id:
        filters['customer_id'] = customer_id
    if meter_id:
        filters['meter_id'] = meter_id
    if status:
        filters['status'] = status
    
    # Get readings
    readings = await db.meter_readings.find(
        filters, {"_id": 0}
    ).sort("reading_date", -1).skip(skip).limit(limit).to_list(limit)
    
    # Enrich with details
    enriched_readings = []
    for reading in readings:
        # Convert timestamps
        if isinstance(reading.get('created_at'), str):
            reading['created_at'] = datetime.fromisoformat(reading['created_at'])
        if isinstance(reading.get('updated_at'), str):
            reading['updated_at'] = datetime.fromisoformat(reading['updated_at'])
        if isinstance(reading.get('reading_date'), str):
            reading['reading_date'] = datetime.fromisoformat(reading['reading_date'])
        if isinstance(reading.get('verified_at'), str):
            reading['verified_at'] = datetime.fromisoformat(reading['verified_at'])
        
        # Get customer name
        customer = await db.customers.find_one({"id": reading['customer_id']}, {"_id": 0})
        user_data = await db.users.find_one({"id": customer['user_id']}, {"_id": 0}) if customer else None
        
        # Get meter serial
        meter = await db.devices.find_one({"id": reading['meter_id']}, {"_id": 0})
        
        # Get technician name
        tech = await db.users.find_one({"id": reading['technician_id']}, {"_id": 0})
        
        enriched_readings.append(MeterReadingWithDetails(
            **reading,
            customer_name=user_data.get('full_name') if user_data else None,
            meter_serial=meter.get('device_id') if meter else None,
            technician_name=tech.get('full_name') if tech else None
        ))
    
    return enriched_readings


@router.get("/meter-readings/{reading_id}", response_model=MeterReadingWithDetails)
async def get_meter_reading(
    reading_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(lambda: None)
):
    """Get a specific meter reading by ID"""
    reading = await db.meter_readings.find_one({"id": reading_id}, {"_id": 0})
    
    if not reading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meter reading not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.TECHNICIAN and reading['technician_id'] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own readings"
        )
    
    # Convert timestamps
    if isinstance(reading.get('created_at'), str):
        reading['created_at'] = datetime.fromisoformat(reading['created_at'])
    if isinstance(reading.get('updated_at'), str):
        reading['updated_at'] = datetime.fromisoformat(reading['updated_at'])
    if isinstance(reading.get('reading_date'), str):
        reading['reading_date'] = datetime.fromisoformat(reading['reading_date'])
    
    # Enrich with details
    customer = await db.customers.find_one({"id": reading['customer_id']}, {"_id": 0})
    user_data = await db.users.find_one({"id": customer['user_id']}, {"_id": 0}) if customer else None
    meter = await db.devices.find_one({"id": reading['meter_id']}, {"_id": 0})
    tech = await db.users.find_one({"id": reading['technician_id']}, {"_id": 0})
    
    return MeterReadingWithDetails(
        **reading,
        customer_name=user_data.get('full_name') if user_data else None,
        meter_serial=meter.get('device_id') if meter else None,
        technician_name=tech.get('full_name') if tech else None
    )


# ==================== TASK MANAGEMENT ENDPOINTS ====================

@router.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(lambda: None)
):
    """
    Create a new task
    Can be created by Admin or system
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.TECHNICIAN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create tasks"
        )
    
    # Create task
    task = Task(
        **task_data.model_dump(exclude={'assigned_to'}),
        created_by=current_user.id,
        status=TaskStatus.PENDING if not task_data.assigned_to else TaskStatus.ASSIGNED,
        assigned_to=task_data.assigned_to,
        assigned_at=datetime.utcnow() if task_data.assigned_to else None
    )
    
    # Insert to database
    task_dict = task.model_dump()
    task_dict['created_at'] = task_dict['created_at'].isoformat()
    task_dict['updated_at'] = task_dict['updated_at'].isoformat()
    if task_dict.get('scheduled_date'):
        task_dict['scheduled_date'] = task_dict['scheduled_date'].isoformat()
    if task_dict.get('assigned_at'):
        task_dict['assigned_at'] = task_dict['assigned_at'].isoformat()
    if task_dict.get('started_at'):
        task_dict['started_at'] = task_dict['started_at'].isoformat()
    if task_dict.get('completed_at'):
        task_dict['completed_at'] = task_dict['completed_at'].isoformat()
    
    await db.tasks.insert_one(task_dict)
    
    logger.info(f"Task created: {task.id} by {current_user.id}")
    
    return task


@router.get("/tasks", response_model=List[TaskWithDetails])
async def get_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    task_type: Optional[TaskType] = Query(None, description="Filter by type"),
    assigned_to: Optional[str] = Query(None, description="Filter by technician"),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(lambda: None)
):
    """
    Get tasks with filters
    Technicians see their assigned tasks + active tasks of others
    Admins see all tasks
    """
    # Build filter
    filters = {}
    
    if status:
        filters['status'] = status
    if priority:
        filters['priority'] = priority
    if task_type:
        filters['task_type'] = task_type
    if assigned_to:
        filters['assigned_to'] = assigned_to
    
    # Role-based filtering
    if current_user.role == UserRole.TECHNICIAN:
        # Technician sees: their own tasks OR active tasks from others
        filters['$or'] = [
            {'assigned_to': current_user.id},
            {'status': TaskStatus.IN_PROGRESS}
        ]
    
    # Get tasks
    tasks = await db.tasks.find(
        filters, {"_id": 0}
    ).sort([("priority", -1), ("scheduled_date", 1)]).skip(skip).limit(limit).to_list(limit)
    
    # Enrich with details
    enriched_tasks = []
    for task in tasks:
        # Convert timestamps
        if isinstance(task.get('created_at'), str):
            task['created_at'] = datetime.fromisoformat(task['created_at'])
        if isinstance(task.get('updated_at'), str):
            task['updated_at'] = datetime.fromisoformat(task['updated_at'])
        if isinstance(task.get('scheduled_date'), str):
            task['scheduled_date'] = datetime.fromisoformat(task['scheduled_date'])
        if isinstance(task.get('assigned_at'), str):
            task['assigned_at'] = datetime.fromisoformat(task['assigned_at'])
        if isinstance(task.get('started_at'), str):
            task['started_at'] = datetime.fromisoformat(task['started_at'])
        if isinstance(task.get('completed_at'), str):
            task['completed_at'] = datetime.fromisoformat(task['completed_at'])
        
        # Get customer info
        customer_name = None
        customer_phone = None
        if task.get('customer_id'):
            customer = await db.customers.find_one({"id": task['customer_id']}, {"_id": 0})
            if customer:
                user = await db.users.find_one({"id": customer['user_id']}, {"_id": 0})
                customer_name = user.get('full_name') if user else None
                customer_phone = user.get('phone') if user else None
        
        # Get technician name
        technician_name = None
        if task.get('assigned_to'):
            tech = await db.users.find_one({"id": task['assigned_to']}, {"_id": 0})
            technician_name = tech.get('full_name') if tech else None
        
        # Get meter serial
        meter_serial = None
        if task.get('meter_id'):
            meter = await db.devices.find_one({"id": task['meter_id']}, {"_id": 0})
            meter_serial = meter.get('device_id') if meter else None
        
        # Get property name
        property_name = None
        if task.get('property_id'):
            prop = await db.properties.find_one({"id": task['property_id']}, {"_id": 0})
            property_name = prop.get('property_name') if prop else None
        
        enriched_tasks.append(TaskWithDetails(
            **task,
            customer_name=customer_name,
            customer_phone=customer_phone,
            technician_name=technician_name,
            meter_serial=meter_serial,
            property_name=property_name
        ))
    
    return enriched_tasks


@router.get("/tasks/my-tasks", response_model=List[TaskWithDetails])
async def get_my_tasks(
    status: Optional[TaskStatus] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(lambda: None)
):
    """Get tasks assigned to current technician"""
    if current_user.role != UserRole.TECHNICIAN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only technicians can access this endpoint"
        )
    
    filters = {'assigned_to': current_user.id}
    if status:
        filters['status'] = status
    
    tasks = await db.tasks.find(
        filters, {"_id": 0}
    ).sort([("priority", -1), ("scheduled_date", 1)]).to_list(None)
    
    # Enrich tasks (similar to get_tasks)
    enriched_tasks = []
    for task in tasks:
        # Convert timestamps
        if isinstance(task.get('created_at'), str):
            task['created_at'] = datetime.fromisoformat(task['created_at'])
        if isinstance(task.get('updated_at'), str):
            task['updated_at'] = datetime.fromisoformat(task['updated_at'])
        if isinstance(task.get('scheduled_date'), str):
            task['scheduled_date'] = datetime.fromisoformat(task['scheduled_date'])
        if isinstance(task.get('assigned_at'), str):
            task['assigned_at'] = datetime.fromisoformat(task['assigned_at'])
        if isinstance(task.get('started_at'), str):
            task['started_at'] = datetime.fromisoformat(task['started_at'])
        if isinstance(task.get('completed_at'), str):
            task['completed_at'] = datetime.fromisoformat(task['completed_at'])
        
        enriched_tasks.append(TaskWithDetails(**task))
    
    return enriched_tasks


@router.get("/tasks/{task_id}", response_model=TaskWithDetails)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(lambda: None)
):
    """Get a specific task by ID"""
    task = await db.tasks.find_one({"id": task_id}, {"_id": 0})
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.TECHNICIAN and task.get('assigned_to') != current_user.id:
        # Technician can view if task is in progress (visible to all)
        if task.get('status') != TaskStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your assigned tasks or active tasks"
            )
    
    # Convert timestamps
    if isinstance(task.get('created_at'), str):
        task['created_at'] = datetime.fromisoformat(task['created_at'])
    if isinstance(task.get('updated_at'), str):
        task['updated_at'] = datetime.fromisoformat(task['updated_at'])
    if isinstance(task.get('scheduled_date'), str):
        task['scheduled_date'] = datetime.fromisoformat(task['scheduled_date'])
    if isinstance(task.get('assigned_at'), str):
        task['assigned_at'] = datetime.fromisoformat(task['assigned_at'])
    if isinstance(task.get('started_at'), str):
        task['started_at'] = datetime.fromisoformat(task['started_at'])
    if isinstance(task.get('completed_at'), str):
        task['completed_at'] = datetime.fromisoformat(task['completed_at'])
    
    return TaskWithDetails(**task)


@router.put("/tasks/{task_id}", response_model=Task)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(lambda: None)
):
    """
    Update a task
    Technicians can update their assigned tasks
    Admins can update any task
    """
    # Get existing task
    task = await db.tasks.find_one({"id": task_id}, {"_id": 0})
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.TECHNICIAN:
        if task.get('assigned_to') != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your assigned tasks"
            )
    
    # Build update dict
    update_data = task_update.model_dump(exclude_unset=True)
    update_data['updated_at'] = datetime.utcnow().isoformat()
    
    # Handle status changes
    if update_data.get('status'):
        if update_data['status'] == TaskStatus.IN_PROGRESS and not task.get('started_at'):
            update_data['started_at'] = datetime.utcnow().isoformat()
        elif update_data['status'] == TaskStatus.COMPLETED and not task.get('completed_at'):
            update_data['completed_at'] = datetime.utcnow().isoformat()
    
    # Handle scheduled_date
    if update_data.get('scheduled_date'):
        update_data['scheduled_date'] = update_data['scheduled_date'].isoformat()
    
    # Update in database
    await db.tasks.update_one(
        {"id": task_id},
        {"$set": update_data}
    )
    
    # Get updated task
    updated_task = await db.tasks.find_one({"id": task_id}, {"_id": 0})
    
    # Convert timestamps
    if isinstance(updated_task.get('created_at'), str):
        updated_task['created_at'] = datetime.fromisoformat(updated_task['created_at'])
    if isinstance(updated_task.get('updated_at'), str):
        updated_task['updated_at'] = datetime.fromisoformat(updated_task['updated_at'])
    if isinstance(updated_task.get('scheduled_date'), str):
        updated_task['scheduled_date'] = datetime.fromisoformat(updated_task['scheduled_date'])
    if isinstance(updated_task.get('assigned_at'), str):
        updated_task['assigned_at'] = datetime.fromisoformat(updated_task['assigned_at'])
    if isinstance(updated_task.get('started_at'), str):
        updated_task['started_at'] = datetime.fromisoformat(updated_task['started_at'])
    if isinstance(updated_task.get('completed_at'), str):
        updated_task['completed_at'] = datetime.fromisoformat(updated_task['completed_at'])
    
    logger.info(f"Task updated: {task_id} by {current_user.id}")
    
    return Task(**updated_task)


@router.post("/tasks/assign", response_model=TaskAssignmentResponse)
async def assign_task(
    assignment: TaskAssignmentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(lambda: None)
):
    """
    Assign task to technician
    Auto-assignment based on location or manual assignment by admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can assign tasks"
        )
    
    # Get task
    task = await db.tasks.find_one({"id": assignment.task_id}, {"_id": 0})
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    assigned_to = None
    assignment_type = "manual"
    
    # Auto-assignment logic
    if not assignment.technician_id:
        assigned_to = await find_nearest_technician(db, task)
        assignment_type = "auto"
        
        if not assigned_to:
            return TaskAssignmentResponse(
                success=False,
                task_id=assignment.task_id,
                assigned_to=None,
                assignment_type="auto",
                message="No active technicians found nearby"
            )
    else:
        assigned_to = assignment.technician_id
    
    # Verify technician exists and is active
    technician = await db.users.find_one({
        "id": assigned_to,
        "role": "technician",
        "is_active": True
    }, {"_id": 0})
    
    if not technician:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Technician not found or inactive"
        )
    
    # Update task
    await db.tasks.update_one(
        {"id": assignment.task_id},
        {"$set": {
            "assigned_to": assigned_to,
            "status": TaskStatus.ASSIGNED,
            "assigned_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }}
    )
    
    logger.info(f"Task {assignment.task_id} assigned to {assigned_to} ({assignment_type})")
    
    return TaskAssignmentResponse(
        success=True,
        task_id=assignment.task_id,
        assigned_to=assigned_to,
        assignment_type=assignment_type,
        message=f"Task successfully assigned to {technician['full_name']}"
    )


# ==================== CUSTOMER DATA ENDPOINTS ====================

@router.get("/customers/{customer_id}/usage-history", response_model=List[UsageHistory])
async def get_customer_usage_history(
    customer_id: str,
    limit: int = Query(12, ge=1, le=60),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(lambda: None)
):
    """Get customer's water usage history"""
    # Verify customer exists
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Get usage history
    history = await get_customer_usage_history(db, customer_id, limit)
    
    # Convert timestamps
    for item in history:
        if isinstance(item.get('created_at'), str):
            item['created_at'] = datetime.fromisoformat(item['created_at'])
        if isinstance(item.get('period_start'), str):
            item['period_start'] = datetime.fromisoformat(item['period_start'])
        if isinstance(item.get('period_end'), str):
            item['period_end'] = datetime.fromisoformat(item['period_end'])
    
    return [UsageHistory(**item) for item in history]
