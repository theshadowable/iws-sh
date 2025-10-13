"""
Notification Service for managing customer notifications
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from typing import Optional, Dict

from notification_models import (
    Notification,
    NotificationType,
    NotificationPriority,
    NotificationPreferences
)


class NotificationService:
    """Service for creating and managing notifications"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def create_notification(
        self,
        customer_id: str,
        type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        action_url: Optional[str] = None,
        action_label: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Notification:
        """
        Create a new notification
        
        Args:
            customer_id: Customer ID
            type: Notification type
            title: Notification title
            message: Notification message
            priority: Priority level
            action_url: Optional URL for action button
            action_label: Optional label for action button
            metadata: Optional additional data
        
        Returns:
            Created notification
        """
        notification = Notification(
            customer_id=customer_id,
            type=type,
            title=title,
            message=message,
            priority=priority,
            action_url=action_url,
            action_label=action_label,
            metadata=metadata
        )
        
        await self.db.notifications.insert_one(notification.dict())
        return notification
    
    async def create_low_balance_notification(
        self,
        customer_id: str,
        customer_name: str,
        current_balance: float
    ) -> Notification:
        """Create low balance notification"""
        return await self.create_notification(
            customer_id=customer_id,
            type=NotificationType.LOW_BALANCE,
            title="⚠️ Low Balance Alert",
            message=f"Hello {customer_name}, your balance is running low (IDR {current_balance:,.0f}). Please top up to avoid service interruption.",
            priority=NotificationPriority.HIGH,
            action_url="/balance-purchase",
            action_label="Top Up Now",
            metadata={"balance": current_balance}
        )
    
    async def create_payment_success_notification(
        self,
        customer_id: str,
        customer_name: str,
        amount: float,
        new_balance: float,
        reference_id: str
    ) -> Notification:
        """Create payment success notification"""
        return await self.create_notification(
            customer_id=customer_id,
            type=NotificationType.PAYMENT_SUCCESS,
            title="✅ Payment Successful",
            message=f"Your payment of IDR {amount:,.0f} was successful. Your new balance is IDR {new_balance:,.0f}.",
            priority=NotificationPriority.MEDIUM,
            action_url=f"/purchase-receipt/{reference_id}",
            action_label="View Receipt",
            metadata={"amount": amount, "balance": new_balance, "reference_id": reference_id}
        )
    
    async def create_payment_failed_notification(
        self,
        customer_id: str,
        customer_name: str,
        amount: float,
        reference_id: str
    ) -> Notification:
        """Create payment failed notification"""
        return await self.create_notification(
            customer_id=customer_id,
            type=NotificationType.PAYMENT_FAILED,
            title="❌ Payment Failed",
            message=f"Your payment of IDR {amount:,.0f} could not be processed. Please try again.",
            priority=NotificationPriority.HIGH,
            action_url="/balance-purchase",
            action_label="Try Again",
            metadata={"amount": amount, "reference_id": reference_id}
        )
    
    async def create_budget_alert_notification(
        self,
        customer_id: str,
        customer_name: str,
        budget_type: str,
        used_percentage: float,
        budget_limit: float,
        current_usage: float
    ) -> Notification:
        """Create budget alert notification"""
        return await self.create_notification(
            customer_id=customer_id,
            type=NotificationType.BUDGET_ALERT,
            title="📊 Budget Alert",
            message=f"You've used {used_percentage:.0f}% of your {budget_type} budget (IDR {current_usage:,.0f} of IDR {budget_limit:,.0f}).",
            priority=NotificationPriority.MEDIUM,
            action_url="/analytics",
            action_label="View Usage",
            metadata={
                "budget_type": budget_type,
                "used_percentage": used_percentage,
                "budget_limit": budget_limit,
                "current_usage": current_usage
            }
        )
    
    async def get_user_preferences(self, customer_id: str) -> NotificationPreferences:
        """Get or create user notification preferences"""
        prefs = await self.db.notification_preferences.find_one({"customer_id": customer_id})
        
        if not prefs:
            # Create default preferences
            default_prefs = NotificationPreferences(customer_id=customer_id)
            await self.db.notification_preferences.insert_one(default_prefs.dict())
            return default_prefs
        
        return NotificationPreferences(**prefs)
    
    async def should_send_low_balance_notification(
        self,
        customer_id: str,
        current_balance: float
    ) -> bool:
        """Check if low balance notification should be sent"""
        prefs = await self.get_user_preferences(customer_id)
        
        if not prefs.low_balance_enabled:
            return False
        
        if current_balance >= prefs.low_balance_threshold:
            return False
        
        # Check if we already sent a notification recently (within last 24 hours)
        recent_notification = await self.db.notifications.find_one({
            "customer_id": customer_id,
            "type": NotificationType.LOW_BALANCE,
            "created_at": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)}
        })
        
        return recent_notification is None
    
    async def check_and_notify_low_balance(
        self,
        customer_id: str,
        customer_name: str,
        current_balance: float
    ) -> Optional[Notification]:
        """Check balance and create notification if needed"""
        should_notify = await self.should_send_low_balance_notification(customer_id, current_balance)
        
        if should_notify:
            return await self.create_low_balance_notification(
                customer_id=customer_id,
                customer_name=customer_name,
                current_balance=current_balance
            )
        
        return None


def get_notification_service(db: AsyncIOMotorDatabase) -> NotificationService:
    """Get notification service instance"""
    return NotificationService(db)
