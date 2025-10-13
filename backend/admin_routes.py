"""
Real-time Monitoring and Admin Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os

from auth import get_current_user, require_role
from monitoring_models import (
    DeviceMonitoring, DeviceStatus, RealTimeConsumption, DashboardMetrics,
    BulkCustomerRequest, BulkCustomerResult, BulkCustomerAction,
    MaintenanceSchedule, CreateMaintenanceRequest, RevenueReport
)
from alert_service import alert_service

router = APIRouter(prefix="/admin", tags=["Admin Management"])

# Database connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'indowater_db')]


@router.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    current_user: dict = Depends(require_role(["admin"]))
):
    """
    Get real-time dashboard metrics for admin
    """
    try:
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Total and active customers
        total_customers = await db.customers.count_documents({})
        active_customers = await db.customers.count_documents({"status": "active"})
        
        # Device counts
        total_devices = await db.devices.count_documents({})
        online_devices = await db.devices.count_documents({"status": "online"})
        offline_devices = await db.devices.count_documents({"status": "offline"})
        
        # Devices with active alerts
        alert_device_ids = await db.alerts.distinct("metadata.device_id", {
            "status": {"$in": ["unread", "read"]},
            "alert_type": {"$in": ["leak_detected", "device_tampering"]}
        })
        devices_with_alerts = len(alert_device_ids)
        
        # Revenue today
        revenue_today_pipeline = [
            {"$match": {
                "status": "paid",
                "paid_at": {"$gte": today_start}
            }},
            {"$group": {
                "_id": None,
                "total": {"$sum": "$amount"}
            }}
        ]
        revenue_today_result = await db.payment_transactions.aggregate(revenue_today_pipeline).to_list(1)
        total_revenue_today = revenue_today_result[0]["total"] if revenue_today_result else 0
        
        # Revenue this month
        revenue_month_pipeline = [
            {"$match": {
                "status": "paid",
                "paid_at": {"$gte": month_start}
            }},
            {"$group": {
                "_id": None,
                "total": {"$sum": "$amount"}
            }}
        ]
        revenue_month_result = await db.payment_transactions.aggregate(revenue_month_pipeline).to_list(1)
        total_revenue_month = revenue_month_result[0]["total"] if revenue_month_result else 0
        
        # Water consumption today
        consumption_today_pipeline = [
            {"$match": {
                "timestamp": {"$gte": today_start}
            }},
            {"$group": {
                "_id": None,
                "total": {"$sum": "$volume"}
            }}
        ]
        consumption_today_result = await db.water_usage.aggregate(consumption_today_pipeline).to_list(1)
        total_consumption_today = consumption_today_result[0]["total"] if consumption_today_result else 0
        
        # Water consumption this month
        consumption_month_pipeline = [
            {"$match": {
                "timestamp": {"$gte": month_start}
            }},
            {"$group": {
                "_id": None,
                "total": {"$sum": "$volume"}
            }}
        ]
        consumption_month_result = await db.water_usage.aggregate(consumption_month_pipeline).to_list(1)
        total_consumption_month = consumption_month_result[0]["total"] if consumption_month_result else 0
        
        # Low balance customers (balance < 50,000)
        low_balance_customers = await db.customers.count_documents({"balance": {"$lt": 50000, "$gt": 0}})
        
        # Pending maintenance
        pending_maintenance = await db.maintenance_schedules.count_documents({
            "status": {"$in": ["scheduled", "in_progress"]}
        })
        
        # Active leaks
        active_leaks = await db.leak_detection_events.count_documents({"resolved": False})
        
        return DashboardMetrics(
            total_customers=total_customers,
            active_customers=active_customers,
            total_devices=total_devices,
            online_devices=online_devices,
            offline_devices=offline_devices,
            devices_with_alerts=devices_with_alerts,
            total_revenue_today=total_revenue_today,
            total_revenue_month=total_revenue_month,
            total_consumption_today=total_consumption_today,
            total_consumption_month=total_consumption_month,
            low_balance_customers=low_balance_customers,
            pending_maintenance=pending_maintenance,
            active_leaks=active_leaks
        )
        
    except Exception as e:
        print(f"Error getting dashboard metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard metrics: {str(e)}"
        )


@router.get("/devices/monitoring", response_model=List[DeviceMonitoring])
async def get_devices_monitoring(
    status_filter: Optional[DeviceStatus] = None,
    has_alerts: Optional[bool] = None,
    limit: int = 100,
    current_user: dict = Depends(require_role(["admin", "technician"]))
):
    """
    Get real-time monitoring data for all devices
    """
    try:
        # Build query
        query = {}
        if status_filter:
            query["status"] = status_filter
        
        devices = await db.devices.find(query).limit(limit).to_list(length=limit)
        
        monitoring_data = []
        
        for device in devices:
            device_id = device["id"]
            customer_id = device.get("customer_id", "")
            
            # Get customer info
            customer = await db.customers.find_one({"id": customer_id})
            if not customer:
                continue
            
            user = await db.users.find_one({"id": customer.get("user_id")})
            customer_name = user.get("full_name", "Unknown") if user else "Unknown"
            
            # Get today's consumption
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            usage_today = await db.water_usage.find({
                "device_id": device_id,
                "timestamp": {"$gte": today_start}
            }).to_list(length=None)
            
            total_today = sum(u.get("volume", 0) for u in usage_today)
            
            # Calculate current flow rate (last 2 readings)
            recent_usage = await db.water_usage.find({
                "device_id": device_id
            }).sort("timestamp", -1).limit(2).to_list(2)
            
            flow_rate = 0
            if len(recent_usage) == 2:
                time_diff = (recent_usage[0]["timestamp"] - recent_usage[1]["timestamp"]).total_seconds() / 3600
                if time_diff > 0:
                    volume_diff = recent_usage[0].get("consumption", 0) - recent_usage[1].get("consumption", 0)
                    flow_rate = volume_diff / time_diff
            
            # Get alerts count
            alerts_count = await db.alerts.count_documents({
                "customer_id": customer_id,
                "status": {"$in": ["unread", "read"]},
                "metadata.device_id": device_id
            })
            
            # Apply alerts filter
            if has_alerts is not None:
                if has_alerts and alerts_count == 0:
                    continue
                if not has_alerts and alerts_count > 0:
                    continue
            
            monitoring = DeviceMonitoring(
                device_id=device_id,
                customer_id=customer_id,
                customer_name=customer_name,
                location=device.get("location"),
                status=device.get("status", DeviceStatus.ONLINE),
                current_consumption_rate=flow_rate,
                total_consumption_today=total_today,
                balance=customer.get("balance", 0),
                alerts_count=alerts_count,
                metadata={
                    "device_type": device.get("device_type"),
                    "meter_id": device.get("meter_id")
                }
            )
            
            monitoring_data.append(monitoring)
        
        return monitoring_data
        
    except Exception as e:
        print(f"Error getting devices monitoring: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get devices monitoring: {str(e)}"
        )


@router.post("/customers/bulk", response_model=BulkCustomerResult)
async def bulk_customer_action(
    request: BulkCustomerRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_role(["admin"]))
):
    """
    Perform bulk actions on multiple customers
    """
    try:
        results = []
        success_count = 0
        failure_count = 0
        
        for customer_id in request.customer_ids:
            try:
                if request.action == BulkCustomerAction.ACTIVATE:
                    result = await db.customers.update_one(
                        {"id": customer_id},
                        {"$set": {"status": "active", "updated_at": datetime.utcnow()}}
                    )
                    if result.matched_count > 0:
                        results.append({"customer_id": customer_id, "status": "success", "message": "Activated"})
                        success_count += 1
                    else:
                        results.append({"customer_id": customer_id, "status": "error", "message": "Customer not found"})
                        failure_count += 1
                
                elif request.action == BulkCustomerAction.DEACTIVATE:
                    result = await db.customers.update_one(
                        {"id": customer_id},
                        {"$set": {"status": "inactive", "updated_at": datetime.utcnow()}}
                    )
                    if result.matched_count > 0:
                        results.append({"customer_id": customer_id, "status": "success", "message": "Deactivated"})
                        success_count += 1
                    else:
                        results.append({"customer_id": customer_id, "status": "error", "message": "Customer not found"})
                        failure_count += 1
                
                elif request.action == BulkCustomerAction.UPDATE_BALANCE:
                    amount = request.parameters.get("amount", 0)
                    operation = request.parameters.get("operation", "add")  # add or set
                    
                    if operation == "add":
                        result = await db.customers.update_one(
                            {"id": customer_id},
                            {"$inc": {"balance": amount}, "$set": {"updated_at": datetime.utcnow()}}
                        )
                    else:  # set
                        result = await db.customers.update_one(
                            {"id": customer_id},
                            {"$set": {"balance": amount, "updated_at": datetime.utcnow()}}
                        )
                    
                    if result.matched_count > 0:
                        results.append({"customer_id": customer_id, "status": "success", "message": f"Balance {operation}ed"})
                        success_count += 1
                    else:
                        results.append({"customer_id": customer_id, "status": "error", "message": "Customer not found"})
                        failure_count += 1
                
                elif request.action == BulkCustomerAction.SEND_NOTIFICATION:
                    title = request.parameters.get("title", "Notification")
                    message = request.parameters.get("message", "")
                    
                    from alert_models import Alert, AlertType, AlertSeverity, AlertStatus
                    
                    alert = Alert(
                        customer_id=customer_id,
                        alert_type=AlertType.SYSTEM_NOTIFICATION,
                        severity=AlertSeverity.INFO,
                        title=title,
                        message=message
                    )
                    
                    await db.alerts.insert_one(alert.dict())
                    results.append({"customer_id": customer_id, "status": "success", "message": "Notification sent"})
                    success_count += 1
                
            except Exception as e:
                results.append({"customer_id": customer_id, "status": "error", "message": str(e)})
                failure_count += 1
        
        return BulkCustomerResult(
            success_count=success_count,
            failure_count=failure_count,
            results=results,
            message=f"Completed: {success_count} successful, {failure_count} failed"
        )
        
    except Exception as e:
        print(f"Error in bulk customer action: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform bulk action: {str(e)}"
        )


@router.post("/maintenance", response_model=MaintenanceSchedule)
async def create_maintenance_schedule(
    request: CreateMaintenanceRequest,
    current_user: dict = Depends(require_role(["admin"]))
):
    """
    Create a maintenance schedule
    """
    try:
        # Get device and customer info
        device = await db.devices.find_one({"id": request.device_id})
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
        customer = await db.customers.find_one({"id": device.get("customer_id")})
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        user = await db.users.find_one({"id": customer.get("user_id")})
        customer_name = user.get("full_name", "Unknown") if user else "Unknown"
        
        # Get technician name if assigned
        technician_name = None
        if request.assigned_technician_id:
            tech_user = await db.users.find_one({"id": request.assigned_technician_id})
            technician_name = tech_user.get("full_name") if tech_user else None
        
        schedule = MaintenanceSchedule(
            device_id=request.device_id,
            customer_id=device.get("customer_id"),
            customer_name=customer_name,
            maintenance_type=request.maintenance_type,
            scheduled_date=request.scheduled_date,
            assigned_technician_id=request.assigned_technician_id,
            assigned_technician_name=technician_name,
            priority=request.priority,
            description=request.description,
            notes=request.notes,
            created_by=current_user["id"]
        )
        
        await db.maintenance_schedules.insert_one(schedule.dict())
        
        # Create notification for customer
        from alert_models import Alert, AlertType, AlertSeverity
        
        alert = Alert(
            customer_id=device.get("customer_id"),
            alert_type=AlertType.MAINTENANCE_DUE,
            severity=AlertSeverity.INFO,
            title="Maintenance Scheduled",
            message=f"A {request.maintenance_type} maintenance has been scheduled for {request.scheduled_date.strftime('%Y-%m-%d %H:%M')}. {request.description}",
            metadata={"schedule_id": schedule.id}
        )
        
        await db.alerts.insert_one(alert.dict())
        
        return schedule
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating maintenance schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create maintenance schedule: {str(e)}"
        )


@router.get("/maintenance", response_model=List[MaintenanceSchedule])
async def get_maintenance_schedules(
    status_filter: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: dict = Depends(require_role(["admin", "technician"]))
):
    """
    Get maintenance schedules
    """
    try:
        query = {}
        
        if status_filter:
            query["status"] = status_filter
        
        if start_date and end_date:
            query["scheduled_date"] = {"$gte": start_date, "$lte": end_date}
        elif start_date:
            query["scheduled_date"] = {"$gte": start_date}
        elif end_date:
            query["scheduled_date"] = {"$lte": end_date}
        
        # If technician, only show their assigned schedules
        if current_user.get("role") == "technician":
            query["assigned_technician_id"] = current_user["id"]
        
        schedules = await db.maintenance_schedules.find(query).sort("scheduled_date", 1).to_list(length=100)
        
        return [MaintenanceSchedule(**s) for s in schedules]
        
    except Exception as e:
        print(f"Error getting maintenance schedules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get maintenance schedules: {str(e)}"
        )


@router.get("/revenue/report", response_model=RevenueReport)
async def generate_revenue_report(
    period: str = "monthly",
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: dict = Depends(require_role(["admin"]))
):
    """
    Generate comprehensive revenue report
    """
    try:
        # Set date range based on period if not provided
        if not start_date or not end_date:
            end_date = datetime.utcnow()
            if period == "daily":
                start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == "weekly":
                start_date = end_date - timedelta(days=7)
            elif period == "monthly":
                start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif period == "yearly":
                start_date = end_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Total revenue and transactions
        revenue_pipeline = [
            {"$match": {
                "status": "paid",
                "paid_at": {"$gte": start_date, "$lte": end_date}
            }},
            {"$group": {
                "_id": None,
                "total_revenue": {"$sum": "$amount"},
                "total_transactions": {"$sum": 1}
            }}
        ]
        
        revenue_result = await db.payment_transactions.aggregate(revenue_pipeline).to_list(1)
        total_revenue = revenue_result[0]["total_revenue"] if revenue_result else 0
        total_transactions = revenue_result[0]["total_transactions"] if revenue_result else 0
        
        # Revenue by payment method
        payment_method_pipeline = [
            {"$match": {
                "status": "paid",
                "paid_at": {"$gte": start_date, "$lte": end_date}
            }},
            {"$group": {
                "_id": "$payment_method",
                "total": {"$sum": "$amount"}
            }}
        ]
        
        payment_method_result = await db.payment_transactions.aggregate(payment_method_pipeline).to_list(None)
        revenue_by_payment_method = {r["_id"]: r["total"] for r in payment_method_result}
        
        # Revenue by day
        daily_pipeline = [
            {"$match": {
                "status": "paid",
                "paid_at": {"$gte": start_date, "$lte": end_date}
            }},
            {"$group": {
                "_id": {
                    "$dateToString": {"format": "%Y-%m-%d", "date": "$paid_at"}
                },
                "revenue": {"$sum": "$amount"},
                "transactions": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        daily_result = await db.payment_transactions.aggregate(daily_pipeline).to_list(None)
        revenue_by_day = [{"date": r["_id"], "revenue": r["revenue"], "transactions": r["transactions"]} for r in daily_result]
        
        # Top customers
        top_customers_pipeline = [
            {"$match": {
                "status": "paid",
                "paid_at": {"$gte": start_date, "$lte": end_date}
            }},
            {"$group": {
                "_id": "$customer_id",
                "total_spent": {"$sum": "$amount"},
                "transaction_count": {"$sum": 1}
            }},
            {"$sort": {"total_spent": -1}},
            {"$limit": 10}
        ]
        
        top_customers_result = await db.payment_transactions.aggregate(top_customers_pipeline).to_list(10)
        
        top_customers = []
        for customer_data in top_customers_result:
            customer = await db.customers.find_one({"id": customer_data["_id"]})
            if customer:
                user = await db.users.find_one({"id": customer.get("user_id")})
                top_customers.append({
                    "customer_id": customer_data["_id"],
                    "name": user.get("full_name", "Unknown") if user else "Unknown",
                    "email": user.get("email", "") if user else "",
                    "total_spent": customer_data["total_spent"],
                    "transaction_count": customer_data["transaction_count"]
                })
        
        # Total water consumption
        consumption_pipeline = [
            {"$match": {
                "timestamp": {"$gte": start_date, "$lte": end_date}
            }},
            {"$group": {
                "_id": None,
                "total": {"$sum": "$volume"}
            }}
        ]
        
        consumption_result = await db.water_usage.aggregate(consumption_pipeline).to_list(1)
        total_water_consumption = consumption_result[0]["total"] if consumption_result else 0
        
        # Calculate average transaction value
        avg_transaction_value = total_revenue / total_transactions if total_transactions > 0 else 0
        
        return RevenueReport(
            period=period,
            start_date=start_date,
            end_date=end_date,
            total_revenue=total_revenue,
            total_transactions=total_transactions,
            total_water_consumption=total_water_consumption,
            avg_transaction_value=avg_transaction_value,
            revenue_by_payment_method=revenue_by_payment_method,
            revenue_by_day=revenue_by_day,
            top_customers=top_customers
        )
        
    except Exception as e:
        print(f"Error generating revenue report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate revenue report: {str(e)}"
        )
