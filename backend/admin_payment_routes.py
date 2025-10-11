"""
Admin Payment Routes
Handles payment settings and configuration management
"""
from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os

from auth import get_current_user, require_role
from models import User, UserRole
from payment_models import PaymentSettings, PaymentSettingsUpdate, PaymentMode


router = APIRouter(prefix="/admin/payment-settings", tags=["admin", "payments"])

# Database connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'indowater_db')]


@router.get("", response_model=PaymentSettings)
async def get_payment_settings(
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Get current payment settings
    Admin only
    """
    settings = await db.payment_settings.find_one(
        {"id": "payment_settings"},
        {"_id": 0}
    )
    
    if not settings:
        # Create default settings
        default_settings = PaymentSettings(
            payment_mode=PaymentMode.SANDBOX,
            active_gateway="midtrans",
            mode="sandbox",
            midtrans_enabled=True,
            xendit_enabled=True
        )
        
        await db.payment_settings.insert_one(default_settings.model_dump())
        return default_settings
    
    return PaymentSettings(**settings)


@router.put("", response_model=PaymentSettings)
async def update_payment_settings(
    update_data: PaymentSettingsUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Update payment settings
    Admin only - can switch between sandbox and live mode
    """
    # Get current settings
    current_settings = await db.payment_settings.find_one(
        {"id": "payment_settings"}
    )
    
    if not current_settings:
        # Create if doesn't exist
        current_settings = PaymentSettings().model_dump()
        await db.payment_settings.insert_one(current_settings)
    
    # Prepare update
    update_dict = update_data.model_dump(exclude_unset=True)
    update_dict["updated_at"] = datetime.utcnow().isoformat()
    update_dict["updated_by"] = current_user.id
    
    # If switching to live mode, update environment variables
    if update_data.payment_mode == PaymentMode.LIVE:
        # In production, you would validate that live keys are configured
        # For now, we just update the mode
        pass
    
    # Update settings
    await db.payment_settings.update_one(
        {"id": "payment_settings"},
        {"$set": update_dict}
    )
    
    # Get updated settings
    updated = await db.payment_settings.find_one(
        {"id": "payment_settings"},
        {"_id": 0}
    )
    
    return PaymentSettings(**updated)


@router.get("/statistics")
async def get_payment_statistics(
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Get payment statistics
    Admin only
    """
    # Total transactions
    total_transactions = await db.payment_transactions.count_documents({})
    
    # Successful payments
    successful_payments = await db.payment_transactions.count_documents({
        "status": "paid"
    })
    
    # Total revenue
    revenue_pipeline = [
        {
            "$match": {"status": "paid"}
        },
        {
            "$group": {
                "_id": None,
                "total_revenue": {"$sum": "$amount"},
                "count": {"$sum": 1}
            }
        }
    ]
    
    revenue_result = await db.payment_transactions.aggregate(revenue_pipeline).to_list(1)
    total_revenue = revenue_result[0]["total_revenue"] if revenue_result else 0
    
    # Pending payments
    pending_payments = await db.payment_transactions.count_documents({
        "status": "pending"
    })
    
    # Failed payments
    failed_payments = await db.payment_transactions.count_documents({
        "status": {"$in": ["failed", "expired", "cancelled"]}
    })
    
    # Payment method breakdown
    method_pipeline = [
        {
            "$match": {"status": "paid"}
        },
        {
            "$group": {
                "_id": "$payment_method",
                "count": {"$sum": 1},
                "total_amount": {"$sum": "$amount"}
            }
        }
    ]
    
    method_stats = await db.payment_transactions.aggregate(method_pipeline).to_list(10)
    
    # Recent transactions
    recent_transactions = await db.payment_transactions.find(
        {},
        {"_id": 0}
    ).sort("created_at", -1).limit(10).to_list(10)
    
    return {
        "total_transactions": total_transactions,
        "successful_payments": successful_payments,
        "pending_payments": pending_payments,
        "failed_payments": failed_payments,
        "total_revenue": total_revenue,
        "success_rate": (successful_payments / total_transactions * 100) if total_transactions > 0 else 0,
        "payment_method_breakdown": method_stats,
        "recent_transactions": recent_transactions
    }


@router.get("/transactions/export")
async def export_transactions(
    format: str = "csv",
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Export transaction data
    Admin only
    Supports CSV and Excel formats
    """
    # Get all paid transactions
    transactions = await db.payment_transactions.find(
        {"status": "paid"},
        {"_id": 0}
    ).sort("paid_at", -1).to_list(None)
    
    if format.lower() == "csv":
        # Generate CSV
        import csv
        import io
        
        output = io.StringIO()
        if transactions:
            writer = csv.DictWriter(output, fieldnames=transactions[0].keys())
            writer.writeheader()
            writer.writerows(transactions)
        
        return {
            "format": "csv",
            "data": output.getvalue(),
            "filename": f"transactions_{datetime.utcnow().strftime('%Y%m%d')}.csv"
        }
    
    elif format.lower() == "excel":
        # Generate Excel (would require openpyxl implementation)
        return {
            "format": "excel",
            "message": "Excel export coming soon",
            "count": len(transactions)
        }
    
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid format. Supported: csv, excel"
        )
