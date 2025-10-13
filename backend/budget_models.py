"""
Budget and Usage Goals Models
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class BudgetPeriod(str, Enum):
    """Budget period types"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class Budget(BaseModel):
    """User budget settings"""
    id: str = Field(default_factory=lambda: f"budget_{datetime.utcnow().timestamp()}")
    customer_id: str
    period: BudgetPeriod
    limit_amount: float  # IDR
    limit_volume: Optional[float] = None  # m³
    alert_threshold: float = 80.0  # Percentage (e.g., 80 means alert at 80% of limit)
    is_active: bool = True
    start_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BudgetTracking(BaseModel):
    """Current budget tracking data"""
    customer_id: str
    period: BudgetPeriod
    period_start: datetime
    period_end: datetime
    budget_limit: float
    current_spending: float
    current_usage: float  # m³
    percentage_used: float
    remaining_budget: float
    is_over_budget: bool
    alert_sent: bool = False


class BudgetComparison(BaseModel):
    """Budget comparison between periods"""
    customer_id: str
    period: BudgetPeriod
    current_period: BudgetTracking
    previous_period: BudgetTracking
    spending_change: float  # Percentage change
    usage_change: float  # Percentage change
    insights: List[str]


# Request/Response models
class CreateBudgetRequest(BaseModel):
    """Request to create a budget"""
    period: BudgetPeriod
    limit_amount: float
    limit_volume: Optional[float] = None
    alert_threshold: Optional[float] = 80.0


class UpdateBudgetRequest(BaseModel):
    """Request to update a budget"""
    limit_amount: Optional[float] = None
    limit_volume: Optional[float] = None
    alert_threshold: Optional[float] = None
    is_active: Optional[bool] = None


class BudgetStatusResponse(BaseModel):
    """Response with budget status"""
    budget: Budget
    tracking: BudgetTracking
    alert_triggered: bool
    message: str
