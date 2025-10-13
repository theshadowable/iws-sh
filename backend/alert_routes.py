"""
Alert and Notification API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os

from auth import get_current_user, require_role
from alert_models import (
    Alert, AlertPreferences, AlertType, AlertSeverity, AlertStatus,
    CreateAlertRequest, UpdateAlertStatusRequest,
    LeakDetectionEvent, DeviceTamperingEvent, WaterSavingTip
)

router = APIRouter(prefix="/alerts", tags=["Alerts"])

# Database connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'indowater_db')]


@router.get("/", response_model=List[Alert])
async def get_alerts(
    status: Optional[AlertStatus] = None,
    alert_type: Optional[AlertType] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """
    Get customer's alerts
    """
    try:
        customer_id = current_user["id"]
        query = {"customer_id": customer_id}
        
        if status:
            query["status"] = status
        if alert_type:
            query["alert_type"] = alert_type
        
        alerts = await db.alerts.find(query).sort("created_at", -1).limit(limit).to_list(length=limit)
        return [Alert(**a) for a in alerts]
        
    except Exception as e:
        print(f"Error getting alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get alerts: {str(e)}"
        )


@router.get("/unread-count")
async def get_unread_count(
    current_user: dict = Depends(get_current_user)
):
    """
    Get count of unread alerts
    """
    try:
        customer_id = current_user["id"]
        count = await db.alerts.count_documents({
            "customer_id": customer_id,
            "status": AlertStatus.UNREAD
        })
        
        return {"unread_count": count}
        
    except Exception as e:
        print(f"Error getting unread count: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get unread count: {str(e)}"
        )


@router.patch("/{alert_id}/status")
async def update_alert_status(
    alert_id: str,
    request: UpdateAlertStatusRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update alert status (mark as read, dismissed, etc.)
    """
    try:
        customer_id = current_user["id"]
        
        update_data = {"status": request.status}
        
        if request.status == AlertStatus.READ:
            update_data["read_at"] = datetime.utcnow()
        elif request.status == AlertStatus.RESOLVED:
            update_data["resolved_at"] = datetime.utcnow()
        
        result = await db.alerts.update_one(
            {"id": alert_id, "customer_id": customer_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        return {"message": "Alert status updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating alert status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update alert status: {str(e)}"
        )


@router.post("/mark-all-read")
async def mark_all_alerts_read(
    current_user: dict = Depends(get_current_user)
):
    """
    Mark all unread alerts as read
    """
    try:
        customer_id = current_user["id"]
        
        result = await db.alerts.update_many(
            {"customer_id": customer_id, "status": AlertStatus.UNREAD},
            {"$set": {"status": AlertStatus.READ, "read_at": datetime.utcnow()}}
        )
        
        return {"message": f"Marked {result.modified_count} alerts as read"}
        
    except Exception as e:
        print(f"Error marking alerts as read: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark alerts as read: {str(e)}"
        )


@router.get("/preferences", response_model=AlertPreferences)
async def get_alert_preferences(
    current_user: dict = Depends(get_current_user)
):
    """
    Get customer's alert preferences
    """
    try:
        customer_id = current_user["id"]
        
        prefs = await db.alert_preferences.find_one({"customer_id": customer_id})
        
        if not prefs:
            # Create default preferences
            prefs = AlertPreferences(customer_id=customer_id)
            await db.alert_preferences.insert_one(prefs.dict())
        
        return AlertPreferences(**prefs)
        
    except Exception as e:
        print(f"Error getting alert preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get alert preferences: {str(e)}"
        )


@router.put("/preferences", response_model=AlertPreferences)
async def update_alert_preferences(
    preferences: AlertPreferences,
    current_user: dict = Depends(get_current_user)
):
    """
    Update customer's alert preferences
    """
    try:
        customer_id = current_user["id"]
        preferences.customer_id = customer_id
        preferences.updated_at = datetime.utcnow()
        
        await db.alert_preferences.update_one(
            {"customer_id": customer_id},
            {"$set": preferences.dict()},
            upsert=True
        )
        
        return preferences
        
    except Exception as e:
        print(f"Error updating alert preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update alert preferences: {str(e)}"
        )


@router.post("/create", response_model=Alert)
async def create_alert(
    request: CreateAlertRequest,
    current_user: dict = Depends(require_role(["admin", "technician"]))
):
    """
    Create a new alert (Admin/Technician only)
    """
    try:
        alert = Alert(
            customer_id=request.customer_id,
            alert_type=request.alert_type,
            severity=request.severity,
            title=request.title,
            message=request.message,
            metadata=request.metadata or {}
        )
        
        await db.alerts.insert_one(alert.dict())
        return alert
        
    except Exception as e:
        print(f"Error creating alert: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create alert: {str(e)}"
        )


@router.get("/leaks", response_model=List[LeakDetectionEvent])
async def get_leak_events(
    resolved: Optional[bool] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get leak detection events for customer
    """
    try:
        customer_id = current_user["id"]
        role = current_user.get("role")
        
        query = {}
        if role == "customer":
            query["customer_id"] = customer_id
        
        if resolved is not None:
            query["resolved"] = resolved
        
        events = await db.leak_detection_events.find(query).sort("detected_at", -1).to_list(length=50)
        return [LeakDetectionEvent(**e) for e in events]
        
    except Exception as e:
        print(f"Error getting leak events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get leak events: {str(e)}"
        )


@router.get("/tampering", response_model=List[DeviceTamperingEvent])
async def get_tampering_events(
    resolved: Optional[bool] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get device tampering events
    """
    try:
        customer_id = current_user["id"]
        role = current_user.get("role")
        
        query = {}
        if role == "customer":
            query["customer_id"] = customer_id
        
        if resolved is not None:
            query["resolved"] = resolved
        
        events = await db.device_tampering_events.find(query).sort("detected_at", -1).to_list(length=50)
        return [DeviceTamperingEvent(**e) for e in events]
        
    except Exception as e:
        print(f"Error getting tampering events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tampering events: {str(e)}"
        )


@router.get("/tips", response_model=List[WaterSavingTip])
async def get_water_saving_tips(
    viewed: Optional[bool] = None,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """
    Get personalized water saving tips
    """
    try:
        customer_id = current_user["id"]
        query = {"customer_id": customer_id}
        
        if viewed is not None:
            query["viewed"] = viewed
        
        tips = await db.water_saving_tips.find(query).sort([("priority", 1), ("generated_at", -1)]).limit(limit).to_list(length=limit)
        return [WaterSavingTip(**t) for t in tips]
        
    except Exception as e:
        print(f"Error getting water saving tips: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get water saving tips: {str(e)}"
        )


@router.patch("/tips/{tip_id}/viewed")
async def mark_tip_viewed(
    tip_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark a tip as viewed
    """
    try:
        customer_id = current_user["id"]
        
        result = await db.water_saving_tips.update_one(
            {"id": tip_id, "customer_id": customer_id},
            {"$set": {"viewed": True, "viewed_at": datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tip not found"
            )
        
        return {"message": "Tip marked as viewed"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error marking tip as viewed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark tip as viewed: {str(e)}"
        )
