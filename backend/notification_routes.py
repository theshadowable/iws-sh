"""
Notification API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os

from auth import get_current_user
from notification_models import (
    NotificationResponse,
    UpdatePreferencesRequest,
    NotificationPreferences
)
from notification_service import get_notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# Database connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'indowater_db')]


@router.get("/", response_model=NotificationResponse)
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    skip: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """
    Get notifications for current user
    """
    try:
        query = {"customer_id": current_user["id"]}
        
        if unread_only:
            query["is_read"] = False
        
        # Get notifications
        notifications_cursor = db.notifications.find(query).sort("created_at", -1).skip(skip).limit(limit)
        notifications = await notifications_cursor.to_list(length=limit)
        
        # Get unread count
        unread_count = await db.notifications.count_documents({
            "customer_id": current_user["id"],
            "is_read": False
        })
        
        # Get total count
        total = await db.notifications.count_documents({"customer_id": current_user["id"]})
        
        return NotificationResponse(
            notifications=notifications,
            unread_count=unread_count,
            total=total
        )
        
    except Exception as e:
        print(f"Error in get_notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve notifications: {str(e)}"
        )


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark a notification as read
    """
    try:
        result = await db.notifications.update_one(
            {
                "id": notification_id,
                "customer_id": current_user["id"]
            },
            {
                "$set": {
                    "is_read": True,
                    "read_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return {"message": "Notification marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in mark_notification_read: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update notification: {str(e)}"
        )


@router.post("/read-all")
async def mark_all_notifications_read(
    current_user: dict = Depends(get_current_user)
):
    """
    Mark all notifications as read for current user
    """
    try:
        result = await db.notifications.update_many(
            {
                "customer_id": current_user["id"],
                "is_read": False
            },
            {
                "$set": {
                    "is_read": True,
                    "read_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "message": f"Marked {result.modified_count} notifications as read",
            "count": result.modified_count
        }
        
    except Exception as e:
        print(f"Error in mark_all_notifications_read: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update notifications: {str(e)}"
        )


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a notification
    """
    try:
        result = await db.notifications.delete_one({
            "id": notification_id,
            "customer_id": current_user["id"]
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return {"message": "Notification deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete notification: {str(e)}"
        )


@router.get("/preferences")
async def get_notification_preferences(
    current_user: dict = Depends(get_current_user)
):
    """
    Get notification preferences for current user
    """
    try:
        service = get_notification_service(db)
        prefs = await service.get_user_preferences(current_user["id"])
        return prefs
        
    except Exception as e:
        print(f"Error in get_notification_preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve preferences: {str(e)}"
        )


@router.put("/preferences")
async def update_notification_preferences(
    request: UpdatePreferencesRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update notification preferences
    """
    try:
        # Update only provided fields
        update_data = {}
        for field, value in request.dict(exclude_none=True).items():
            update_data[field] = value
        
        update_data["updated_at"] = datetime.utcnow()
        
        # Update in database
        await db.notification_preferences.update_one(
            {"customer_id": current_user["id"]},
            {"$set": update_data},
            upsert=True
        )
        
        # Return updated preferences
        service = get_notification_service(db)
        updated_prefs = await service.get_user_preferences(current_user["id"])
        return updated_prefs
        
    except Exception as e:
        print(f"Error in update_notification_preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}"
        )


@router.post("/check-balance")
async def check_balance_and_notify(
    current_user: dict = Depends(get_current_user)
):
    """
    Check balance and create notification if low (for manual trigger)
    """
    try:
        # Get customer data
        customer = await db.customers.find_one({"user_id": current_user["id"]})
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        balance = customer.get("balance", 0)
        
        # Check and create notification if needed
        service = get_notification_service(db)
        notification = await service.check_and_notify_low_balance(
            customer_id=current_user["id"],
            customer_name=current_user.get("full_name", "Customer"),
            current_balance=balance
        )
        
        if notification:
            return {
                "message": "Low balance notification created",
                "notification": notification
            }
        else:
            return {
                "message": "Balance is sufficient or notification already sent today",
                "balance": balance
            }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in check_balance_and_notify: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check balance: {str(e)}"
        )
