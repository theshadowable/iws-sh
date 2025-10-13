"""
Budget and Usage Goals API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from typing import Optional, List
import os

from auth import get_current_user
from budget_models import (
    Budget,
    BudgetPeriod,
    BudgetTracking,
    BudgetComparison,
    CreateBudgetRequest,
    UpdateBudgetRequest,
    BudgetStatusResponse
)
from notification_service import get_notification_service

router = APIRouter(prefix="/budgets", tags=["Budgets"])

# Database connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'indowater_db')]


def get_period_dates(period: BudgetPeriod, reference_date: Optional[datetime] = None):
    """Get start and end dates for a budget period"""
    if reference_date is None:
        reference_date = datetime.utcnow()
    
    if period == BudgetPeriod.DAILY:
        start = reference_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
    elif period == BudgetPeriod.WEEKLY:
        # Start of week (Monday)
        days_since_monday = reference_date.weekday()
        start = (reference_date - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
    else:  # MONTHLY
        start = reference_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Next month
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1)
        else:
            end = start.replace(month=start.month + 1)
    
    return start, end


async def calculate_budget_tracking(customer_id: str, budget: Budget) -> BudgetTracking:
    """Calculate current budget tracking data"""
    period_start, period_end = get_period_dates(budget.period)
    
    # Get water usage for the period
    usage_cursor = db.water_usage.find({
        "customer_id": customer_id,
        "reading_date": {
            "$gte": period_start,
            "$lt": period_end
        }
    })
    
    usage_records = await usage_cursor.to_list(length=1000)
    
    current_usage = sum(record.get("consumption", 0) for record in usage_records)
    current_spending = sum(record.get("cost", 0) for record in usage_records)
    
    percentage_used = (current_spending / budget.limit_amount * 100) if budget.limit_amount > 0 else 0
    remaining_budget = budget.limit_amount - current_spending
    is_over_budget = current_spending > budget.limit_amount
    
    return BudgetTracking(
        customer_id=customer_id,
        period=budget.period,
        period_start=period_start,
        period_end=period_end,
        budget_limit=budget.limit_amount,
        current_spending=current_spending,
        current_usage=current_usage,
        percentage_used=percentage_used,
        remaining_budget=remaining_budget,
        is_over_budget=is_over_budget
    )


@router.post("/", response_model=Budget)
async def create_budget(
    request: CreateBudgetRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new budget"""
    try:
        # Check if budget for this period already exists
        existing = await db.budgets.find_one({
            "customer_id": current_user["id"],
            "period": request.period,
            "is_active": True
        })
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Active {request.period} budget already exists"
            )
        
        # Create budget
        budget = Budget(
            customer_id=current_user["id"],
            period=request.period,
            limit_amount=request.limit_amount,
            limit_volume=request.limit_volume,
            alert_threshold=request.alert_threshold or 80.0
        )
        
        await db.budgets.insert_one(budget.dict())
        
        return budget
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating budget: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create budget: {str(e)}"
        )


@router.get("/", response_model=List[Budget])
async def get_budgets(
    period: Optional[BudgetPeriod] = None,
    active_only: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """Get all budgets for current user"""
    try:
        query = {"customer_id": current_user["id"]}
        
        if period:
            query["period"] = period
        if active_only:
            query["is_active"] = True
        
        budgets_cursor = db.budgets.find(query).sort("created_at", -1)
        budgets = await budgets_cursor.to_list(length=100)
        
        return budgets
        
    except Exception as e:
        print(f"Error fetching budgets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve budgets: {str(e)}"
        )


@router.get("/{budget_id}", response_model=BudgetStatusResponse)
async def get_budget_status(
    budget_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get budget status with tracking data"""
    try:
        budget = await db.budgets.find_one({
            "id": budget_id,
            "customer_id": current_user["id"]
        })
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found"
            )
        
        budget_obj = Budget(**budget)
        tracking = await calculate_budget_tracking(current_user["id"], budget_obj)
        
        alert_triggered = tracking.percentage_used >= budget_obj.alert_threshold
        
        message = "On track"
        if tracking.is_over_budget:
            message = f"Over budget by IDR {abs(tracking.remaining_budget):,.0f}"
        elif alert_triggered:
            message = f"Warning: {tracking.percentage_used:.1f}% of budget used"
        
        return BudgetStatusResponse(
            budget=budget_obj,
            tracking=tracking,
            alert_triggered=alert_triggered,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching budget status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve budget status: {str(e)}"
        )


@router.put("/{budget_id}", response_model=Budget)
async def update_budget(
    budget_id: str,
    request: UpdateBudgetRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update a budget"""
    try:
        budget = await db.budgets.find_one({
            "id": budget_id,
            "customer_id": current_user["id"]
        })
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found"
            )
        
        update_data = {}
        for field, value in request.dict(exclude_none=True).items():
            update_data[field] = value
        
        update_data["updated_at"] = datetime.utcnow()
        
        await db.budgets.update_one(
            {"id": budget_id},
            {"$set": update_data}
        )
        
        updated_budget = await db.budgets.find_one({"id": budget_id})
        return Budget(**updated_budget)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating budget: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update budget: {str(e)}"
        )


@router.delete("/{budget_id}")
async def delete_budget(
    budget_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a budget"""
    try:
        result = await db.budgets.delete_one({
            "id": budget_id,
            "customer_id": current_user["id"]
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found"
            )
        
        return {"message": "Budget deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting budget: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete budget: {str(e)}"
        )


@router.get("/tracking/current")
async def get_current_tracking(
    current_user: dict = Depends(get_current_user)
):
    """Get current budget tracking for all active budgets"""
    try:
        budgets_cursor = db.budgets.find({
            "customer_id": current_user["id"],
            "is_active": True
        })
        
        budgets = await budgets_cursor.to_list(length=10)
        
        tracking_data = []
        for budget_dict in budgets:
            budget = Budget(**budget_dict)
            tracking = await calculate_budget_tracking(current_user["id"], budget)
            tracking_data.append({
                "budget": budget,
                "tracking": tracking
            })
        
        return tracking_data
        
    except Exception as e:
        print(f"Error fetching current tracking: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tracking data: {str(e)}"
        )


@router.get("/comparison/{period}")
async def get_budget_comparison(
    period: BudgetPeriod,
    current_user: dict = Depends(get_current_user)
):
    """Compare current period with previous period"""
    try:
        # Get budget for this period
        budget = await db.budgets.find_one({
            "customer_id": current_user["id"],
            "period": period,
            "is_active": True
        })
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No active {period} budget found"
            )
        
        budget_obj = Budget(**budget)
        
        # Current period tracking
        current_tracking = await calculate_budget_tracking(current_user["id"], budget_obj)
        
        # Previous period tracking
        if period == BudgetPeriod.DAILY:
            prev_date = datetime.utcnow() - timedelta(days=1)
        elif period == BudgetPeriod.WEEKLY:
            prev_date = datetime.utcnow() - timedelta(weeks=1)
        else:  # MONTHLY
            prev_date = datetime.utcnow() - timedelta(days=30)
        
        prev_period_start, prev_period_end = get_period_dates(period, prev_date)
        
        # Get previous period usage
        prev_usage_cursor = db.water_usage.find({
            "customer_id": current_user["id"],
            "reading_date": {
                "$gte": prev_period_start,
                "$lt": prev_period_end
            }
        })
        
        prev_usage_records = await prev_usage_cursor.to_list(length=1000)
        prev_usage = sum(record.get("consumption", 0) for record in prev_usage_records)
        prev_spending = sum(record.get("cost", 0) for record in prev_usage_records)
        
        previous_tracking = BudgetTracking(
            customer_id=current_user["id"],
            period=period,
            period_start=prev_period_start,
            period_end=prev_period_end,
            budget_limit=budget_obj.limit_amount,
            current_spending=prev_spending,
            current_usage=prev_usage,
            percentage_used=(prev_spending / budget_obj.limit_amount * 100) if budget_obj.limit_amount > 0 else 0,
            remaining_budget=budget_obj.limit_amount - prev_spending,
            is_over_budget=prev_spending > budget_obj.limit_amount
        )
        
        # Calculate changes
        spending_change = 0
        usage_change = 0
        
        if prev_spending > 0:
            spending_change = ((current_tracking.current_spending - prev_spending) / prev_spending) * 100
        
        if prev_usage > 0:
            usage_change = ((current_tracking.current_usage - prev_usage) / prev_usage) * 100
        
        # Generate insights
        insights = []
        if spending_change > 0:
            insights.append(f"Spending increased by {spending_change:.1f}% compared to previous {period}")
        elif spending_change < 0:
            insights.append(f"Spending decreased by {abs(spending_change):.1f}% compared to previous {period}")
        else:
            insights.append(f"Spending remained stable compared to previous {period}")
        
        if current_tracking.is_over_budget:
            insights.append("⚠️ Currently over budget")
        elif current_tracking.percentage_used >= budget_obj.alert_threshold:
            insights.append(f"⚠️ Approaching budget limit ({current_tracking.percentage_used:.1f}% used)")
        
        return BudgetComparison(
            customer_id=current_user["id"],
            period=period,
            current_period=current_tracking,
            previous_period=previous_tracking,
            spending_change=spending_change,
            usage_change=usage_change,
            insights=insights
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error comparing budgets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare budgets: {str(e)}"
        )
