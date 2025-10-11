"""
Analytics Routes
Handles water usage analytics, trends, predictions, and comparisons
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from typing import Optional, List
import os
import statistics

from auth import get_current_user, require_role
from models import User, UserRole
from analytics_models import (
    PeriodType,
    UsageAnalytics,
    UsageDataPoint,
    TrendAnalytics,
    TrendData,
    PredictionAnalytics,
    PredictionDataPoint,
    ComparisonAnalytics,
    ComparisonPeriod,
    AdminOverview
)


router = APIRouter(prefix="/analytics", tags=["analytics"])

# Database connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'indowater_db')]


def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime"""
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        return datetime.strptime(date_str, '%Y-%m-%d')


def calculate_period_bounds(period: PeriodType, end_date: Optional[datetime] = None):
    """Calculate start and end dates for a period"""
    if end_date is None:
        end_date = datetime.utcnow()
    
    if period == PeriodType.DAY:
        start_date = end_date - timedelta(days=1)
    elif period == PeriodType.WEEK:
        start_date = end_date - timedelta(days=7)
    elif period == PeriodType.MONTH:
        start_date = end_date - timedelta(days=30)
    elif period == PeriodType.YEAR:
        start_date = end_date - timedelta(days=365)
    else:
        start_date = end_date - timedelta(days=30)
    
    return start_date, end_date


@router.get("/usage", response_model=UsageAnalytics)
async def get_usage_analytics(
    period: PeriodType = Query(PeriodType.MONTH),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    customer_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get water usage analytics
    - Customers can only view their own data
    - Admins can view any customer or system-wide data
    """
    # Permission check
    if current_user.role == UserRole.CUSTOMER:
        customer_id = current_user.id
    elif customer_id is None and current_user.role != UserRole.ADMIN:
        customer_id = current_user.id
    
    # Calculate date range
    if start_date and end_date:
        start = parse_date(start_date)
        end = parse_date(end_date)
    else:
        start, end = calculate_period_bounds(period)
    
    # Build query
    query = {
        "reading_date": {
            "$gte": start.isoformat(),
            "$lte": end.isoformat()
        }
    }
    
    if customer_id:
        query["customer_id"] = customer_id
    
    # Fetch data
    usage_records = await db.water_usage.find(
        query,
        {"_id": 0}
    ).sort("reading_date", 1).to_list(None)
    
    if not usage_records:
        return UsageAnalytics(
            period=period,
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            customer_id=customer_id,
            total_consumption=0,
            total_cost=0,
            average_daily=0,
            data_points=[],
            device_count=0
        )
    
    # Calculate statistics
    total_consumption = sum(r['consumption'] for r in usage_records)
    total_cost = sum(r['cost'] for r in usage_records)
    days = (end - start).days + 1
    average_daily = total_consumption / days if days > 0 else 0
    
    # Get unique devices
    device_ids = set(r['device_id'] for r in usage_records)
    device_count = len(device_ids)
    
    # Prepare data points
    data_points = [
        UsageDataPoint(
            date=r['reading_date'],
            consumption=r['consumption'],
            cost=r['cost'],
            reading_value=r.get('reading_value')
        )
        for r in usage_records
    ]
    
    return UsageAnalytics(
        period=period,
        start_date=start.isoformat(),
        end_date=end.isoformat(),
        customer_id=customer_id,
        total_consumption=round(total_consumption, 3),
        total_cost=round(total_cost, 2),
        average_daily=round(average_daily, 3),
        data_points=data_points,
        device_count=device_count
    )


@router.get("/trends", response_model=TrendAnalytics)
async def get_consumption_trends(
    period: PeriodType = Query(PeriodType.MONTH),
    customer_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get consumption trends over time
    Returns trend data grouped by period
    """
    # Permission check
    if current_user.role == UserRole.CUSTOMER:
        customer_id = current_user.id
    
    # Get data for the last 6 months
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=180)
    
    query = {
        "reading_date": {
            "$gte": start_date.isoformat(),
            "$lte": end_date.isoformat()
        }
    }
    
    if customer_id:
        query["customer_id"] = customer_id
    
    # Fetch data
    usage_records = await db.water_usage.find(
        query,
        {"_id": 0, "reading_date": 1, "consumption": 1}
    ).sort("reading_date", 1).to_list(None)
    
    if not usage_records:
        return TrendAnalytics(
            period_type=period,
            trends=[],
            overall_trend="stable",
            growth_rate=0
        )
    
    # Group by period
    period_data = {}
    
    for record in usage_records:
        record_date = parse_date(record['reading_date'])
        
        if period == PeriodType.DAY:
            key = record_date.strftime('%Y-%m-%d')
        elif period == PeriodType.WEEK:
            key = record_date.strftime('%Y-W%W')
        elif period == PeriodType.MONTH:
            key = record_date.strftime('%Y-%m')
        else:
            key = record_date.strftime('%Y')
        
        if key not in period_data:
            period_data[key] = 0
        period_data[key] += record['consumption']
    
    # Calculate trends
    trends = []
    period_keys = sorted(period_data.keys())
    
    for i, key in enumerate(period_keys):
        consumption = period_data[key]
        
        # Calculate percentage change from previous period
        percentage_change = None
        trend = "stable"
        
        if i > 0:
            prev_consumption = period_data[period_keys[i-1]]
            if prev_consumption > 0:
                percentage_change = ((consumption - prev_consumption) / prev_consumption) * 100
                
                if percentage_change > 5:
                    trend = "increasing"
                elif percentage_change < -5:
                    trend = "decreasing"
        
        trends.append(TrendData(
            period=key,
            consumption=round(consumption, 3),
            percentage_change=round(percentage_change, 2) if percentage_change is not None else None,
            trend=trend
        ))
    
    # Calculate overall trend
    if len(trends) >= 2:
        first_half = sum(t.consumption for t in trends[:len(trends)//2])
        second_half = sum(t.consumption for t in trends[len(trends)//2:])
        
        if first_half > 0:
            growth_rate = ((second_half - first_half) / first_half) * 100
        else:
            growth_rate = 0
        
        if growth_rate > 5:
            overall_trend = "increasing"
        elif growth_rate < -5:
            overall_trend = "decreasing"
        else:
            overall_trend = "stable"
    else:
        growth_rate = 0
        overall_trend = "stable"
    
    return TrendAnalytics(
        period_type=period,
        trends=trends,
        overall_trend=overall_trend,
        growth_rate=round(growth_rate, 2)
    )


@router.get("/predictions", response_model=PredictionAnalytics)
async def get_usage_predictions(
    customer_id: Optional[str] = None,
    days_ahead: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_user)
):
    """
    Predict future water usage using simple moving average
    """
    # Permission check
    if current_user.role == UserRole.CUSTOMER:
        customer_id = current_user.id
    elif not customer_id:
        raise HTTPException(
            status_code=400,
            detail="customer_id is required for predictions"
        )
    
    # Get last 30 days of data
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    usage_records = await db.water_usage.find(
        {
            "customer_id": customer_id,
            "reading_date": {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat()
            }
        },
        {"_id": 0, "reading_date": 1, "consumption": 1}
    ).sort("reading_date", -1).to_list(None)
    
    if len(usage_records) < 7:
        raise HTTPException(
            status_code=400,
            detail="Insufficient data for predictions (minimum 7 days required)"
        )
    
    # Calculate moving average
    consumptions = [r['consumption'] for r in usage_records[:14]]  # Last 14 days
    moving_avg = statistics.mean(consumptions)
    std_dev = statistics.stdev(consumptions) if len(consumptions) > 1 else 0
    
    # Detect weekly pattern (weekday vs weekend)
    weekday_consumptions = []
    weekend_consumptions = []
    
    for record in usage_records[:14]:
        record_date = parse_date(record['reading_date'])
        if record_date.weekday() >= 5:
            weekend_consumptions.append(record['consumption'])
        else:
            weekday_consumptions.append(record['consumption'])
    
    weekday_avg = statistics.mean(weekday_consumptions) if weekday_consumptions else moving_avg
    weekend_avg = statistics.mean(weekend_consumptions) if weekend_consumptions else moving_avg
    
    # Generate predictions
    predictions = []
    current_date = end_date
    
    for i in range(days_ahead):
        current_date += timedelta(days=1)
        
        # Use weekday/weekend pattern
        if current_date.weekday() >= 5:
            predicted = weekend_avg
        else:
            predicted = weekday_avg
        
        # Add slight random variation but keep it realistic
        variation = std_dev * 0.5
        
        predictions.append(PredictionDataPoint(
            date=current_date.strftime('%Y-%m-%d'),
            predicted_consumption=round(predicted, 3),
            confidence_lower=round(max(0, predicted - variation), 3),
            confidence_upper=round(predicted + variation, 3)
        ))
    
    average_predicted = statistics.mean([p.predicted_consumption for p in predictions])
    
    return PredictionAnalytics(
        customer_id=customer_id,
        prediction_method="moving_average_with_weekly_pattern",
        based_on_days=len(usage_records),
        predictions=predictions,
        average_predicted=round(average_predicted, 3),
        notes=f"Predictions based on {len(usage_records)} days of historical data using 7-day moving average with weekday/weekend pattern detection"
    )


@router.get("/comparison", response_model=ComparisonAnalytics)
async def compare_periods(
    period1_start: str,
    period1_end: str,
    period2_start: str,
    period2_end: str,
    customer_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Compare water usage between two time periods
    """
    # Permission check
    if current_user.role == UserRole.CUSTOMER:
        customer_id = current_user.id
    
    # Parse dates
    p1_start = parse_date(period1_start)
    p1_end = parse_date(period1_end)
    p2_start = parse_date(period2_start)
    p2_end = parse_date(period2_end)
    
    async def get_period_data(start: datetime, end: datetime, label: str):
        query = {
            "reading_date": {
                "$gte": start.isoformat(),
                "$lte": end.isoformat()
            }
        }
        
        if customer_id:
            query["customer_id"] = customer_id
        
        records = await db.water_usage.find(query, {"_id": 0}).to_list(None)
        
        if not records:
            return ComparisonPeriod(
                period_label=label,
                start_date=start.isoformat(),
                end_date=end.isoformat(),
                total_consumption=0,
                total_cost=0,
                average_daily=0,
                peak_consumption=0,
                peak_date=""
            )
        
        total_consumption = sum(r['consumption'] for r in records)
        total_cost = sum(r['cost'] for r in records)
        days = (end - start).days + 1
        average_daily = total_consumption / days if days > 0 else 0
        
        # Find peak consumption
        peak_record = max(records, key=lambda x: x['consumption'])
        
        return ComparisonPeriod(
            period_label=label,
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            total_consumption=round(total_consumption, 3),
            total_cost=round(total_cost, 2),
            average_daily=round(average_daily, 3),
            peak_consumption=round(peak_record['consumption'], 3),
            peak_date=peak_record['reading_date']
        )
    
    # Get data for both periods
    period1 = await get_period_data(p1_start, p1_end, "Period 1")
    period2 = await get_period_data(p2_start, p2_end, "Period 2")
    
    # Calculate changes
    if period1.total_consumption > 0:
        consumption_change = ((period2.total_consumption - period1.total_consumption) / period1.total_consumption) * 100
    else:
        consumption_change = 0
    
    if period1.total_cost > 0:
        cost_change = ((period2.total_cost - period1.total_cost) / period1.total_cost) * 100
    else:
        cost_change = 0
    
    # Determine direction
    if consumption_change > 1:
        change_direction = "increase"
    elif consumption_change < -1:
        change_direction = "decrease"
    else:
        change_direction = "same"
    
    return ComparisonAnalytics(
        period1=period1,
        period2=period2,
        consumption_change=round(consumption_change, 2),
        cost_change=round(cost_change, 2),
        change_direction=change_direction
    )


@router.get("/admin/overview", response_model=AdminOverview)
async def get_admin_overview(
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Get system-wide analytics overview
    Admin only
    """
    # Get device statistics
    total_devices = await db.devices.count_documents({})
    active_devices = await db.devices.count_documents({"status": "active"})
    
    # Get customer count
    total_customers = await db.customers.count_documents({})
    
    # Get consumption for last 30 days
    end_date = datetime.utcnow()
    start_date_30d = end_date - timedelta(days=30)
    
    usage_30d = await db.water_usage.find(
        {
            "reading_date": {
                "$gte": start_date_30d.isoformat(),
                "$lte": end_date.isoformat()
            }
        },
        {"_id": 0, "consumption": 1, "cost": 1}
    ).to_list(None)
    
    total_consumption_30d = sum(r['consumption'] for r in usage_30d)
    total_revenue_30d = sum(r['cost'] for r in usage_30d)
    
    # Get all-time consumption
    all_usage = await db.water_usage.find(
        {},
        {"_id": 0, "consumption": 1, "cost": 1}
    ).to_list(None)
    
    total_consumption_all = sum(r['consumption'] for r in all_usage)
    total_revenue_all = sum(r['cost'] for r in all_usage)
    
    # Average consumption per device
    if total_devices > 0:
        avg_per_device = total_consumption_30d / total_devices
    else:
        avg_per_device = 0
    
    # Top consumers (last 30 days)
    top_consumers_pipeline = [
        {
            "$match": {
                "reading_date": {
                    "$gte": start_date_30d.isoformat(),
                    "$lte": end_date.isoformat()
                }
            }
        },
        {
            "$group": {
                "_id": "$customer_id",
                "total_consumption": {"$sum": "$consumption"},
                "total_cost": {"$sum": "$cost"}
            }
        },
        {
            "$sort": {"total_consumption": -1}
        },
        {
            "$limit": 5
        }
    ]
    
    top_consumers = await db.water_usage.aggregate(top_consumers_pipeline).to_list(5)
    
    # Get customer details for top consumers
    top_consumers_detailed = []
    for consumer in top_consumers:
        customer = await db.customers.find_one(
            {"id": consumer['_id']},
            {"_id": 0, "full_name": 1, "email": 1}
        )
        if customer:
            top_consumers_detailed.append({
                "customer_id": consumer['_id'],
                "customer_name": customer.get('full_name', 'Unknown'),
                "customer_email": customer.get('email', ''),
                "consumption": round(consumer['total_consumption'], 3),
                "cost": round(consumer['total_cost'], 2)
            })
    
    # Recent anomalies (consumption > 2x average)
    if usage_30d:
        avg_consumption = statistics.mean([r['consumption'] for r in usage_30d])
        threshold = avg_consumption * 2
        
        anomalies = await db.water_usage.find(
            {
                "reading_date": {
                    "$gte": start_date_30d.isoformat(),
                    "$lte": end_date.isoformat()
                },
                "consumption": {"$gt": threshold}
            },
            {"_id": 0}
        ).sort("reading_date", -1).limit(5).to_list(5)
    else:
        anomalies = []
    
    # Device status breakdown
    device_statuses = await db.devices.aggregate([
        {
            "$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }
        }
    ]).to_list(None)
    
    device_status_breakdown = {item['_id']: item['count'] for item in device_statuses}
    
    return AdminOverview(
        total_devices=total_devices,
        active_devices=active_devices,
        total_customers=total_customers,
        total_consumption_30d=round(total_consumption_30d, 3),
        total_consumption_all_time=round(total_consumption_all, 3),
        total_revenue_30d=round(total_revenue_30d, 2),
        total_revenue_all_time=round(total_revenue_all, 2),
        average_consumption_per_device=round(avg_per_device, 3),
        top_consumers=top_consumers_detailed,
        recent_anomalies=anomalies,
        device_status_breakdown=device_status_breakdown
    )
