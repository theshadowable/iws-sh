"""
Analytics Data Models
Pydantic models for analytics and reporting endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PeriodType(str, Enum):
    """Period types for analytics"""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class UsageDataPoint(BaseModel):
    """Single data point in usage timeline"""
    date: str
    consumption: float
    cost: float
    reading_value: Optional[float] = None


class UsageAnalytics(BaseModel):
    """Water usage analytics response"""
    period: PeriodType
    start_date: str
    end_date: str
    customer_id: Optional[str] = None
    total_consumption: float
    total_cost: float
    average_daily: float
    data_points: List[UsageDataPoint]
    device_count: int


class TrendData(BaseModel):
    """Trend analysis data"""
    period: str
    consumption: float
    percentage_change: Optional[float] = None
    trend: str  # "increasing", "decreasing", "stable"


class TrendAnalytics(BaseModel):
    """Consumption trends response"""
    period_type: PeriodType
    trends: List[TrendData]
    overall_trend: str
    growth_rate: float  # percentage


class PredictionDataPoint(BaseModel):
    """Predicted consumption data point"""
    date: str
    predicted_consumption: float
    confidence_lower: float
    confidence_upper: float


class PredictionAnalytics(BaseModel):
    """Usage predictions response"""
    customer_id: str
    prediction_method: str
    based_on_days: int
    predictions: List[PredictionDataPoint]
    average_predicted: float
    notes: str


class ComparisonPeriod(BaseModel):
    """Data for a single comparison period"""
    period_label: str
    start_date: str
    end_date: str
    total_consumption: float
    total_cost: float
    average_daily: float
    peak_consumption: float
    peak_date: str


class ComparisonAnalytics(BaseModel):
    """Period comparison response"""
    period1: ComparisonPeriod
    period2: ComparisonPeriod
    consumption_change: float  # percentage
    cost_change: float  # percentage
    change_direction: str  # "increase", "decrease", "same"


class AdminOverview(BaseModel):
    """Admin system-wide analytics"""
    total_devices: int
    active_devices: int
    total_customers: int
    total_consumption_30d: float
    total_consumption_all_time: float
    total_revenue_30d: float
    total_revenue_all_time: float
    average_consumption_per_device: float
    top_consumers: List[dict]
    recent_anomalies: List[dict]
    device_status_breakdown: dict


class ReportRequest(BaseModel):
    """Request body for report generation"""
    customer_id: Optional[str] = None
    start_date: str
    end_date: str
    report_type: str = "usage_summary"  # usage_summary, detailed, comparison
    include_charts: bool = True
    format: str = "pdf"  # pdf, excel


class ExportFormat(str, Enum):
    """Export format options"""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
