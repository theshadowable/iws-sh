from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class TipCategory(str, Enum):
    GENERAL_SAVINGS = "general_savings"
    LEAK_PREVENTION = "leak_prevention"
    BEST_PRACTICES = "best_practices"
    SARAN_PENGHEMATAN_PRABAYAR = "saran_penghematan_prabayar"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

# Water Conservation Tip Model
class WaterConservationTip(BaseModel):
    id: str
    title: str
    description: str
    category: TipCategory
    potential_savings_percentage: Optional[float] = None  # Estimated savings (e.g., 10 = 10%)
    potential_savings_amount: Optional[float] = None  # Estimated savings in IDR per month
    difficulty_level: DifficultyLevel
    implementation_time: Optional[str] = None  # e.g., "5 minutes", "1 hour", "1 day"
    created_at: datetime
    updated_at: datetime
    created_by: str  # Admin ID
    is_active: bool = True
    view_count: int = 0
    like_count: int = 0
    implementation_count: int = 0
    tags: List[str] = []
    image_url: Optional[str] = None

# Tip Engagement Model
class TipEngagement(BaseModel):
    id: str
    tip_id: str
    customer_id: str
    viewed_at: Optional[datetime] = None
    liked: bool = False
    liked_at: Optional[datetime] = None
    bookmarked: bool = False
    bookmarked_at: Optional[datetime] = None
    implemented: bool = False
    implemented_at: Optional[datetime] = None
    feedback: Optional[str] = None
    estimated_savings: Optional[float] = None  # User-reported savings

# Create Tip Request
class CreateTipRequest(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20, max_length=2000)
    category: TipCategory
    potential_savings_percentage: Optional[float] = Field(None, ge=0, le=100)
    potential_savings_amount: Optional[float] = Field(None, ge=0)
    difficulty_level: DifficultyLevel
    implementation_time: Optional[str] = None
    tags: List[str] = []
    image_url: Optional[str] = None

# Update Tip Request
class UpdateTipRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=20, max_length=2000)
    category: Optional[TipCategory] = None
    potential_savings_percentage: Optional[float] = Field(None, ge=0, le=100)
    potential_savings_amount: Optional[float] = Field(None, ge=0)
    difficulty_level: Optional[DifficultyLevel] = None
    implementation_time: Optional[str] = None
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

# Engage with Tip Request
class EngageTipRequest(BaseModel):
    action: str  # "view", "like", "unlike", "bookmark", "unbookmark", "implement", "unimplement"
    feedback: Optional[str] = None
    estimated_savings: Optional[float] = None

# Personalized Tip Request
class PersonalizedTipRequest(BaseModel):
    limit: int = Field(5, ge=1, le=20)
    exclude_viewed: bool = False

# Tip Statistics
class TipStats(BaseModel):
    total_tips: int
    active_tips: int
    total_views: int
    total_likes: int
    total_implementations: int
    tips_by_category: dict
    most_popular_tips: List[dict]
    most_implemented_tips: List[dict]

# Tip List Response
class TipListResponse(BaseModel):
    tips: List[WaterConservationTip]
    total: int
    page: int
    limit: int
    has_more: bool

# Tip Detail with User Engagement
class TipDetailWithEngagement(BaseModel):
    tip: WaterConservationTip
    user_engagement: Optional[TipEngagement] = None
    is_viewed: bool = False
    is_liked: bool = False
    is_bookmarked: bool = False
    is_implemented: bool = False
