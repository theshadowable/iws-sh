from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
import os

from auth import get_current_user, User
from conservation_models import (
    WaterConservationTip, TipEngagement, CreateTipRequest, UpdateTipRequest,
    EngageTipRequest, PersonalizedTipRequest, TipStats, TipListResponse,
    TipDetailWithEngagement, TipCategory, DifficultyLevel
)
from tip_recommendation_service import TipRecommendationService

router = APIRouter(prefix="/tips", tags=["Water Conservation Tips"])

# Database connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db_client = client[os.environ.get('DB_NAME', 'indowater_db')]

# ============================================================================
# CUSTOMER ENDPOINTS
# ============================================================================

@router.get("/", response_model=TipListResponse)
async def get_tips(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),

):
    """Get water conservation tips with filters"""
    try:
        query = {"is_active": True}
        
        # Apply filters
        if category:
            query['category'] = category
        if difficulty:
            query['difficulty_level'] = difficulty
        if search:
            query['$or'] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"tags": {"$regex": search, "$options": "i"}}
            ]
        
        # Count total
        total = await db_client.water_conservation_tips.count_documents(query)
        
        # Get paginated tips
        skip = (page - 1) * limit
        cursor = db_client.water_conservation_tips.find(query).sort("created_at", -1).skip(skip).limit(limit)
        tips = await cursor.to_list(length=limit)
        
        has_more = (skip + len(tips)) < total
        
        return TipListResponse(
            tips=[WaterConservationTip(**t) for t in tips],
            total=total,
            page=page,
            limit=limit,
            has_more=has_more
        )
        
    except Exception as e:
        print(f"❌ Error getting tips: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/random", response_model=WaterConservationTip)
async def get_random_tip(
    current_user: User = Depends(get_current_user),

):
    """Get random water conservation tip for dashboard"""
    try:
        # Get random tip
        tips = list(db_client.water_conservation_tips.aggregate([
            {"$match": {"is_active": True}},
            {"$sample": {"size": 1}}
        ]))
        
        if not tips:
            raise HTTPException(status_code=404, detail="No tips available")
        
        return WaterConservationTip(**tips[0])
        
    except Exception as e:
        print(f"❌ Error getting random tip: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/personalized", response_model=List[WaterConservationTip])
async def get_personalized_tips(
    limit: int = Query(5, ge=1, le=20),
    exclude_viewed: bool = False,
    current_user: User = Depends(get_current_user),

):
    """Get personalized tips based on user's water usage patterns"""
    try:
        # Initialize recommendation service
        tip_service = TipRecommendationService(db_client)
        
        # Get personalized recommendations
        tips = await tip_service.get_personalized_tips(current_user.id, limit)
        
        # Filter out viewed tips if requested
        if exclude_viewed:
            viewed_tip_ids = set()
            engagements_cursor = db_client.tip_engagements.find({
                "customer_id": current_user.id,
                "viewed_at": {"$exists": True}
            })
            engagements = await engagements_cursor.to_list(1000)
            for eng in engagements:
                viewed_tip_ids.add(eng['tip_id'])
            
            tips = [t for t in tips if t['id'] not in viewed_tip_ids]
        
        return [WaterConservationTip(**t) for t in tips]
        
    except Exception as e:
        print(f"❌ Error getting personalized tips: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{tip_id}", response_model=TipDetailWithEngagement)
async def get_tip_detail(
    tip_id: str,
    current_user: User = Depends(get_current_user),

):
    """Get tip detail with user engagement data"""
    try:
        # Get tip
        tip = await db_client.water_conservation_tips.find_one({"id": tip_id})
        if not tip:
            raise HTTPException(status_code=404, detail="Tip not found")
        
        # Get user engagement
        engagement = await db_client.tip_engagements.find_one({
            "tip_id": tip_id,
            "customer_id": current_user.id
        })
        
        # Auto-track view
        if not engagement:
            engagement_data = {
                "id": str(uuid.uuid4()),
                "tip_id": tip_id,
                "customer_id": current_user.id,
                "viewed_at": datetime.utcnow(),
                "liked": False,
                "bookmarked": False,
                "implemented": False
            }
            await db_client.tip_engagements.insert_one(engagement_data)
            
            # Increment view count
            await db_client.water_conservation_tips.update_one(
                {"id": tip_id},
                {"$inc": {"view_count": 1}}
            )
            
            engagement = engagement_data
        elif not engagement.get('viewed_at'):
            # Update viewed_at if not set
            await db_client.tip_engagements.update_one(
                {"id": engagement['id']},
                {"$set": {"viewed_at": datetime.utcnow()}}
            )
            await db_client.water_conservation_tips.update_one(
                {"id": tip_id},
                {"$inc": {"view_count": 1}}
            )
            engagement = await db_client.tip_engagements.find_one({"id": engagement['id']})
        
        # Refresh tip data (for updated view count)
        tip = await db_client.water_conservation_tips.find_one({"id": tip_id})
        
        return TipDetailWithEngagement(
            tip=WaterConservationTip(**tip),
            user_engagement=TipEngagement(**engagement) if engagement else None,
            is_viewed=bool(engagement.get('viewed_at')),
            is_liked=engagement.get('liked', False),
            is_bookmarked=engagement.get('bookmarked', False),
            is_implemented=engagement.get('implemented', False)
        )
        
    except Exception as e:
        print(f"❌ Error getting tip detail: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{tip_id}/engage")
async def engage_with_tip(
    tip_id: str,
    request: EngageTipRequest,
    current_user: User = Depends(get_current_user),

):
    """Engage with tip (like, bookmark, implement)"""
    try:
        # Verify tip exists
        tip = await db_client.water_conservation_tips.find_one({"id": tip_id})
        if not tip:
            raise HTTPException(status_code=404, detail="Tip not found")
        
        # Get or create engagement
        engagement = await db_client.tip_engagements.find_one({
            "tip_id": tip_id,
            "customer_id": current_user.id
        })
        
        if not engagement:
            engagement = {
                "id": str(uuid.uuid4()),
                "tip_id": tip_id,
                "customer_id": current_user.id,
                "viewed_at": datetime.utcnow(),
                "liked": False,
                "bookmarked": False,
                "implemented": False
            }
            await db_client.tip_engagements.insert_one(engagement)
        
        # Process action
        update_data = {}
        tip_update = {}
        
        if request.action == "like":
            update_data['liked'] = True
            update_data['liked_at'] = datetime.utcnow()
            tip_update = {"$inc": {"like_count": 1}}
        
        elif request.action == "unlike":
            update_data['liked'] = False
            update_data['liked_at'] = None
            tip_update = {"$inc": {"like_count": -1}}
        
        elif request.action == "bookmark":
            update_data['bookmarked'] = True
            update_data['bookmarked_at'] = datetime.utcnow()
        
        elif request.action == "unbookmark":
            update_data['bookmarked'] = False
            update_data['bookmarked_at'] = None
        
        elif request.action == "implement":
            update_data['implemented'] = True
            update_data['implemented_at'] = datetime.utcnow()
            if request.feedback:
                update_data['feedback'] = request.feedback
            if request.estimated_savings:
                update_data['estimated_savings'] = request.estimated_savings
            tip_update = {"$inc": {"implementation_count": 1}}
        
        elif request.action == "unimplement":
            update_data['implemented'] = False
            update_data['implemented_at'] = None
            tip_update = {"$inc": {"implementation_count": -1}}
        
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        # Update engagement
        await db_client.tip_engagements.update_one(
            {"id": engagement['id']},
            {"$set": update_data}
        )
        
        # Update tip counts
        if tip_update:
            await db_client.water_conservation_tips.update_one(
                {"id": tip_id},
                tip_update
            )
        
        print(f"✅ Tip engagement: {request.action} on tip {tip_id}")
        return {"message": f"Successfully {request.action}d tip"}
        
    except Exception as e:
        print(f"❌ Error engaging with tip: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/bookmarked", response_model=List[WaterConservationTip])
async def get_bookmarked_tips(
    current_user: User = Depends(get_current_user),

):
    """Get user's bookmarked tips"""
    try:
        # Get bookmarked tip IDs
        engagements_cursor = db_client.tip_engagements.find({
            "customer_id": current_user.id,
            "bookmarked": True
        })
        engagements = await engagements_cursor.to_list(1000)
        
        bookmarked_tip_ids = [eng['tip_id'] for eng in engagements]
        
        # Get tips
        tips_cursor = db_client.water_conservation_tips.find({
            "id": {"$in": bookmarked_tip_ids},
            "is_active": True
        })
        tips = await tips_cursor.to_list(1000)
        
        return [WaterConservationTip(**t) for t in tips]
        
    except Exception as e:
        print(f"❌ Error getting bookmarked tips: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@router.post("/admin/create", response_model=WaterConservationTip)
async def create_tip(
    request: CreateTipRequest,
    current_user: User = Depends(get_current_user),

):
    """Create new water conservation tip (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create tips")
    
    try:
        tip_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        tip_data = {
            "id": tip_id,
            "title": request.title,
            "description": request.description,
            "category": request.category,
            "potential_savings_percentage": request.potential_savings_percentage,
            "potential_savings_amount": request.potential_savings_amount,
            "difficulty_level": request.difficulty_level,
            "implementation_time": request.implementation_time,
            "created_at": now,
            "updated_at": now,
            "created_by": current_user.id,
            "is_active": True,
            "view_count": 0,
            "like_count": 0,
            "implementation_count": 0,
            "tags": request.tags,
            "image_url": request.image_url
        }
        
        await db_client.water_conservation_tips.insert_one(tip_data)
        
        print(f"✅ Water conservation tip created: {request.title}")
        return WaterConservationTip(**tip_data)
        
    except Exception as e:
        print(f"❌ Error creating tip: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/admin/{tip_id}", response_model=WaterConservationTip)
async def update_tip(
    tip_id: str,
    request: UpdateTipRequest,
    current_user: User = Depends(get_current_user),

):
    """Update water conservation tip (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update tips")
    
    try:
        tip = await db_client.water_conservation_tips.find_one({"id": tip_id})
        if not tip:
            raise HTTPException(status_code=404, detail="Tip not found")
        
        # Prepare update data
        update_data = {"updated_at": datetime.utcnow()}
        
        if request.title is not None:
            update_data['title'] = request.title
        if request.description is not None:
            update_data['description'] = request.description
        if request.category is not None:
            update_data['category'] = request.category
        if request.potential_savings_percentage is not None:
            update_data['potential_savings_percentage'] = request.potential_savings_percentage
        if request.potential_savings_amount is not None:
            update_data['potential_savings_amount'] = request.potential_savings_amount
        if request.difficulty_level is not None:
            update_data['difficulty_level'] = request.difficulty_level
        if request.implementation_time is not None:
            update_data['implementation_time'] = request.implementation_time
        if request.tags is not None:
            update_data['tags'] = request.tags
        if request.image_url is not None:
            update_data['image_url'] = request.image_url
        if request.is_active is not None:
            update_data['is_active'] = request.is_active
        
        await db_client.water_conservation_tips.update_one(
            {"id": tip_id},
            {"$set": update_data}
        )
        
        updated_tip = await db_client.water_conservation_tips.find_one({"id": tip_id})
        print(f"✅ Tip updated: {tip_id}")
        return WaterConservationTip(**updated_tip)
        
    except Exception as e:
        print(f"❌ Error updating tip: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/admin/{tip_id}")
async def delete_tip(
    tip_id: str,
    current_user: User = Depends(get_current_user),

):
    """Delete water conservation tip (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete tips")
    
    try:
        tip = await db_client.water_conservation_tips.find_one({"id": tip_id})
        if not tip:
            raise HTTPException(status_code=404, detail="Tip not found")
        
        # Soft delete (mark as inactive)
        await db_client.water_conservation_tips.update_one(
            {"id": tip_id},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        
        print(f"✅ Tip deleted: {tip_id}")
        return {"message": "Tip deleted successfully"}
        
    except Exception as e:
        print(f"❌ Error deleting tip: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/stats", response_model=TipStats)
async def get_tip_statistics(
    current_user: User = Depends(get_current_user),

):
    """Get tip statistics (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can view statistics")
    
    try:
        # Total tips
        total_tips = await db_client.water_conservation_tips.count_documents({})
        active_tips = await db_client.water_conservation_tips.count_documents({"is_active": True})
        
        # Aggregate stats
        pipeline = [
            {"$match": {"is_active": True}},
            {"$group": {
                "_id": None,
                "total_views": {"$sum": "$view_count"},
                "total_likes": {"$sum": "$like_count"},
                "total_implementations": {"$sum": "$implementation_count"}
            }}
        ]
        
        agg_result = list(db_client.water_conservation_tips.aggregate(pipeline))
        total_views = agg_result[0]['total_views'] if agg_result else 0
        total_likes = agg_result[0]['total_likes'] if agg_result else 0
        total_implementations = agg_result[0]['total_implementations'] if agg_result else 0
        
        # By category
        tips_by_category = {}
        for category in TipCategory:
            count = await db_client.water_conservation_tips.count_documents({"category": category, "is_active": True})
            tips_by_category[category] = count
        
        # Most popular tips
        most_popular_cursor = db_client.water_conservation_tips.find({"is_active": True}).sort("view_count", -1).limit(5)
        most_popular_tips = await most_popular_cursor.to_list(1000)
        most_popular = [{"id": t['id'], "title": t['title'], "views": t['view_count']} for t in most_popular_tips]
        
        # Most implemented tips
        most_implemented_cursor = db_client.water_conservation_tips.find({"is_active": True}).sort("implementation_count", -1).limit(5)
        most_implemented_tips = await most_implemented_cursor.to_list(1000)
        most_implemented = [{"id": t['id'], "title": t['title'], "implementations": t['implementation_count']} for t in most_implemented_tips]
        
        return TipStats(
            total_tips=total_tips,
            active_tips=active_tips,
            total_views=total_views,
            total_likes=total_likes,
            total_implementations=total_implementations,
            tips_by_category=tips_by_category,
            most_popular_tips=most_popular,
            most_implemented_tips=most_implemented
        )
        
    except Exception as e:
        print(f"❌ Error getting tip stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
