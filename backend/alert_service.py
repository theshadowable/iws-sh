"""
Alert Generation Service
Handles automatic alert generation for low balance, leaks, tampering, etc.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from statistics import mean, stdev

from alert_models import (
    Alert, AlertType, AlertSeverity, AlertStatus,
    LeakDetectionEvent, WaterSavingTip
)


class AlertService:
    """Service for generating and managing alerts"""
    
    def __init__(self):
        mongo_url = os.environ['MONGO_URL']
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[os.environ.get('DB_NAME', 'indowater_db')]
    
    async def check_low_balance_alerts(self):
        """
        Check all customers for low balance and generate alerts
        """
        try:
            # Get all active alert preferences
            prefs_cursor = self.db.alert_preferences.find({"low_balance_enabled": True})
            prefs_list = await prefs_cursor.to_list(length=None)
            
            for pref in prefs_list:
                customer_id = pref["customer_id"]
                threshold = pref.get("low_balance_threshold", 50000)
                
                # Get customer balance
                customer = await self.db.customers.find_one({"user_id": customer_id})
                if not customer:
                    continue
                
                balance = customer.get("balance", 0)
                
                # Check if balance is below threshold
                if balance < threshold and balance > 0:
                    # Check if alert already exists (avoid duplicate alerts)
                    existing_alert = await self.db.alerts.find_one({
                        "customer_id": customer_id,
                        "alert_type": AlertType.LOW_BALANCE,
                        "status": {"$in": [AlertStatus.UNREAD, AlertStatus.READ]},
                        "created_at": {"$gte": datetime.utcnow() - timedelta(hours=24)}
                    })
                    
                    if not existing_alert:
                        # Create low balance alert
                        alert = Alert(
                            customer_id=customer_id,
                            alert_type=AlertType.LOW_BALANCE,
                            severity=AlertSeverity.WARNING if balance > threshold * 0.5 else AlertSeverity.CRITICAL,
                            title="Low Balance Alert",
                            message=f"Your balance is running low. Current balance: IDR {balance:,.0f}. Please top up to avoid service interruption.",
                            metadata={
                                "balance": balance,
                                "threshold": threshold
                            }
                        )
                        await self.db.alerts.insert_one(alert.dict())
                        print(f"Created low balance alert for customer {customer_id}")
            
        except Exception as e:
            print(f"Error checking low balance alerts: {e}")
    
    async def detect_leaks_for_customer(self, customer_id: str, device_id: str) -> Optional[LeakDetectionEvent]:
        """
        Analyze water usage patterns to detect potential leaks for a specific customer
        
        Algorithm:
        1. Get last 24 hours of usage data
        2. Calculate average consumption rate per hour
        3. Check for continuous high consumption (especially at night)
        4. Compare with historical average
        """
        try:
            # Get last 24 hours of usage data
            last_24h = datetime.utcnow() - timedelta(hours=24)
            usage_cursor = self.db.water_usage.find({
                "device_id": device_id,
                "timestamp": {"$gte": last_24h}
            }).sort("timestamp", 1)
            
            usage_data = await usage_cursor.to_list(length=None)
            
            if len(usage_data) < 10:  # Need enough data points
                return None
            
            # Calculate hourly consumption rates
            hourly_rates = []
            night_rates = []  # 11pm - 6am
            
            for i in range(1, len(usage_data)):
                prev = usage_data[i-1]
                curr = usage_data[i]
                
                time_diff = (curr["timestamp"] - prev["timestamp"]).total_seconds() / 3600  # hours
                if time_diff > 0:
                    consumption_diff = curr.get("consumption", 0) - prev.get("consumption", 0)
                    rate = consumption_diff / time_diff  # m³/hour
                    hourly_rates.append(rate)
                    
                    # Check if night time
                    hour = curr["timestamp"].hour
                    if hour >= 23 or hour < 6:
                        night_rates.append(rate)
            
            if not hourly_rates:
                return None
            
            avg_rate = mean(hourly_rates)
            
            # Get historical average (last 30 days, excluding last 24 hours)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            historical_cursor = self.db.water_usage.find({
                "device_id": device_id,
                "timestamp": {"$gte": thirty_days_ago, "$lt": last_24h}
            }).sort("timestamp", 1)
            
            historical_data = await historical_cursor.to_list(length=None)
            historical_rates = []
            
            for i in range(1, len(historical_data)):
                prev = historical_data[i-1]
                curr = historical_data[i]
                time_diff = (curr["timestamp"] - prev["timestamp"]).total_seconds() / 3600
                if time_diff > 0:
                    consumption_diff = curr.get("consumption", 0) - prev.get("consumption", 0)
                    rate = consumption_diff / time_diff
                    if rate > 0:  # Only positive rates
                        historical_rates.append(rate)
            
            if not historical_rates:
                normal_rate = 0.05  # Default baseline: 0.05 m³/hour
            else:
                normal_rate = mean(historical_rates)
            
            # Detect leak conditions
            leak_detected = False
            severity = "minor"
            
            # Condition 1: Current rate is significantly higher than normal (>200%)
            if avg_rate > normal_rate * 2 and avg_rate > 0.1:
                leak_detected = True
                severity = "moderate"
            
            # Condition 2: High continuous night consumption (potential constant leak)
            if night_rates and len(night_rates) >= 3:
                avg_night_rate = mean(night_rates)
                if avg_night_rate > 0.05 and avg_night_rate > normal_rate * 1.5:
                    leak_detected = True
                    severity = "severe"
            
            # Condition 3: Very high spike (>400% of normal)
            if avg_rate > normal_rate * 4 and avg_rate > 0.2:
                leak_detected = True
                severity = "severe"
            
            if leak_detected:
                # Calculate estimated loss
                duration_hours = 24
                estimated_loss_m3 = (avg_rate - normal_rate) * duration_hours
                estimated_cost_idr = estimated_loss_m3 * 10000  # IDR 10,000 per m³
                
                # Check if event already exists for this device in last 24 hours
                existing_event = await self.db.leak_detection_events.find_one({
                    "device_id": device_id,
                    "resolved": False,
                    "detected_at": {"$gte": last_24h}
                })
                
                if existing_event:
                    # Update existing event
                    await self.db.leak_detection_events.update_one(
                        {"id": existing_event["id"]},
                        {
                            "$set": {
                                "consumption_rate": avg_rate,
                                "severity": severity,
                                "duration_minutes": duration_hours * 60,
                                "estimated_loss_m3": estimated_loss_m3,
                                "estimated_cost_idr": estimated_cost_idr
                            }
                        }
                    )
                    return LeakDetectionEvent(**existing_event)
                else:
                    # Create new leak event
                    leak_event = LeakDetectionEvent(
                        device_id=device_id,
                        customer_id=customer_id,
                        consumption_rate=avg_rate,
                        normal_rate=normal_rate,
                        severity=severity,
                        duration_minutes=duration_hours * 60,
                        estimated_loss_m3=estimated_loss_m3,
                        estimated_cost_idr=estimated_cost_idr
                    )
                    
                    await self.db.leak_detection_events.insert_one(leak_event.dict())
                    
                    # Create alert
                    alert = Alert(
                        customer_id=customer_id,
                        alert_type=AlertType.LEAK_DETECTED,
                        severity=AlertSeverity.CRITICAL if severity == "severe" else AlertSeverity.WARNING,
                        title="Potential Water Leak Detected",
                        message=f"Unusual water consumption detected. Estimated loss: {estimated_loss_m3:.2f} m³ (IDR {estimated_cost_idr:,.0f}). Please check your water system for leaks.",
                        metadata={
                            "device_id": device_id,
                            "leak_event_id": leak_event.id,
                            "severity": severity,
                            "estimated_loss_m3": estimated_loss_m3,
                            "estimated_cost_idr": estimated_cost_idr
                        }
                    )
                    
                    await self.db.alerts.insert_one(alert.dict())
                    print(f"Leak detected for customer {customer_id}, device {device_id}")
                    
                    return leak_event
            
            return None
            
        except Exception as e:
            print(f"Error detecting leaks: {e}")
            return None
    
    async def generate_water_saving_tips(self, customer_id: str) -> List[WaterSavingTip]:
        """
        Generate personalized water saving tips based on usage patterns
        """
        try:
            tips = []
            
            # Get customer's devices
            devices = await self.db.devices.find({"customer_id": customer_id}).to_list(length=None)
            if not devices:
                return tips
            
            device_ids = [d["id"] for d in devices]
            
            # Analyze usage patterns (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            usage_cursor = self.db.water_usage.find({
                "device_id": {"$in": device_ids},
                "timestamp": {"$gte": thirty_days_ago}
            }).sort("timestamp", 1)
            
            usage_data = await usage_cursor.to_list(length=None)
            
            if not usage_data:
                return tips
            
            # Calculate daily average
            total_consumption = sum(u.get("consumption", 0) for u in usage_data)
            days = (datetime.utcnow() - thirty_days_ago).days
            daily_avg = total_consumption / days if days > 0 else 0
            
            # Check existing tips to avoid duplicates
            existing_tips = await self.db.water_saving_tips.find({
                "customer_id": customer_id,
                "generated_at": {"$gte": datetime.utcnow() - timedelta(days=7)}
            }).to_list(length=None)
            
            existing_categories = {t.get("tip_category") for t in existing_tips}
            
            # Generate tips based on usage patterns
            
            # Tip 1: High usage detected
            if daily_avg > 0.5 and "usage_optimization" not in existing_categories:
                tip = WaterSavingTip(
                    customer_id=customer_id,
                    tip_category="usage_optimization",
                    title="Optimize Your Water Usage",
                    description=f"Your daily average is {daily_avg:.2f} m³. Consider shorter showers and turning off taps when not in use. This could save you up to 20% on water costs.",
                    potential_savings_percentage=20,
                    priority=1
                )
                tips.append(tip)
            
            # Tip 2: Check for leaks
            if "leak_prevention" not in existing_categories:
                tip = WaterSavingTip(
                    customer_id=customer_id,
                    tip_category="leak_prevention",
                    title="Regular Leak Checks",
                    description="Check your faucets, pipes, and toilet for leaks regularly. A small drip can waste up to 20 liters per day.",
                    potential_savings_percentage=15,
                    priority=2
                )
                tips.append(tip)
            
            # Tip 3: Behavior change
            if "behavior_change" not in existing_categories:
                tip = WaterSavingTip(
                    customer_id=customer_id,
                    tip_category="behavior_change",
                    title="Smart Water Habits",
                    description="Use a bucket to catch water while waiting for it to heat up. Reuse water from washing vegetables for plants. Small changes make a big difference!",
                    potential_savings_percentage=10,
                    priority=3
                )
                tips.append(tip)
            
            # Save new tips
            for tip in tips:
                await self.db.water_saving_tips.insert_one(tip.dict())
            
            return tips
            
        except Exception as e:
            print(f"Error generating water saving tips: {e}")
            return []


# Singleton instance
alert_service = AlertService()
