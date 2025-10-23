from typing import List, Dict
from datetime import datetime, timedelta
import random

class TipRecommendationService:
    """
    Service untuk memberikan rekomendasi tips berdasarkan pola penggunaan air customer
    """
    
    def __init__(self, db):
        self.db = db
    
    async def get_personalized_tips(self, customer_id: str, limit: int = 5) -> List[Dict]:
        """
        Generate personalized water conservation tips based on customer usage patterns
        """
        try:
            # Get customer's water usage data (last 30 days)
            usage_data = await self._get_customer_usage(customer_id)
            
            # Analyze usage patterns
            analysis = self._analyze_usage_patterns(usage_data)
            
            # Get all active tips
            cursor = self.db.water_conservation_tips.find({"is_active": True})
            all_tips = await cursor.to_list(length=None)
            
            # Get tips already viewed by customer
            viewed_tips = set()
            cursor = self.db.tip_engagements.find({"customer_id": customer_id})
            async for engagement in cursor:
                viewed_tips.add(engagement['tip_id'])
            
            # Score and rank tips based on relevance
            scored_tips = []
            for tip in all_tips:
                score = self._calculate_tip_relevance(tip, analysis, viewed_tips)
                scored_tips.append((score, tip))
            
            # Sort by score (highest first) and return top N
            scored_tips.sort(reverse=True, key=lambda x: x[0])
            recommended_tips = [tip for score, tip in scored_tips[:limit]]
            
            return recommended_tips
            
        except Exception as e:
            print(f"Error getting personalized tips: {str(e)}")
            # Fallback to random tips
            return await self._get_random_tips(limit)
    
    async def _get_customer_usage(self, customer_id: str) -> List[Dict]:
        """Get customer's water usage data for last 30 days"""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        cursor = self.db.water_usage.find({
            "customer_id": customer_id,
            "timestamp": {"$gte": thirty_days_ago}
        }).sort("timestamp", -1)
        
        usage_data = await cursor.to_list(length=None)
        
        return usage_data
    
    def _analyze_usage_patterns(self, usage_data: List[Dict]) -> Dict:
        """Analyze water usage patterns"""
        if not usage_data:
            return {
                "avg_daily_consumption": 0,
                "total_consumption": 0,
                "has_high_consumption": False,
                "has_night_usage": False,
                "consumption_trend": "stable",
                "days_with_data": 0
            }
        
        # Calculate metrics
        total_consumption = sum(record.get('consumption', 0) for record in usage_data)
        days_with_data = len(set(record['timestamp'].date() for record in usage_data if 'timestamp' in record))
        avg_daily_consumption = total_consumption / max(days_with_data, 1)
        
        # Check for high consumption (>500L per day)
        has_high_consumption = avg_daily_consumption > 500
        
        # Check for night-time usage (potential leak indicator)
        night_records = [r for r in usage_data if 'timestamp' in r and r['timestamp'].hour >= 23 or r['timestamp'].hour <= 5]
        has_night_usage = len(night_records) > len(usage_data) * 0.1  # More than 10% at night
        
        # Analyze trend (compare first half vs second half)
        mid_point = len(usage_data) // 2
        if mid_point > 0:
            first_half_avg = sum(r.get('consumption', 0) for r in usage_data[:mid_point]) / mid_point
            second_half_avg = sum(r.get('consumption', 0) for r in usage_data[mid_point:]) / (len(usage_data) - mid_point)
            
            if second_half_avg > first_half_avg * 1.2:
                consumption_trend = "increasing"
            elif second_half_avg < first_half_avg * 0.8:
                consumption_trend = "decreasing"
            else:
                consumption_trend = "stable"
        else:
            consumption_trend = "stable"
        
        return {
            "avg_daily_consumption": avg_daily_consumption,
            "total_consumption": total_consumption,
            "has_high_consumption": has_high_consumption,
            "has_night_usage": has_night_usage,
            "consumption_trend": consumption_trend,
            "days_with_data": days_with_data
        }
    
    def _calculate_tip_relevance(self, tip: Dict, analysis: Dict, viewed_tips: set) -> float:
        """Calculate relevance score for a tip (0-100)"""
        score = 50.0  # Base score
        
        # Penalty for already viewed tips
        if tip['id'] in viewed_tips:
            score -= 20
        
        # Boost based on category relevance
        category = tip.get('category', '')
        
        if analysis['has_night_usage'] and category == 'leak_prevention':
            score += 30
        
        if analysis['has_high_consumption'] and category in ['general_savings', 'saran_penghematan_prabayar']:
            score += 25
        
        if analysis['consumption_trend'] == 'increasing' and category == 'best_practices':
            score += 20
        
        # Boost based on difficulty (prioritize easy tips for new users)
        if tip.get('difficulty_level') == 'easy':
            score += 10
        
        # Boost based on potential savings
        if tip.get('potential_savings_percentage', 0) > 15:
            score += 15
        
        # Boost based on popularity (but not too much)
        if tip.get('like_count', 0) > 10:
            score += 5
        
        # Random factor for variety
        score += random.uniform(-5, 5)
        
        return max(0, min(100, score))  # Clamp between 0-100
    
    async def _get_random_tips(self, limit: int) -> List[Dict]:
        """Fallback: get random tips"""
        all_tips = list(self.db.water_conservation_tips.find({"is_active": True}))
        random.shuffle(all_tips)
        return all_tips[:limit]
