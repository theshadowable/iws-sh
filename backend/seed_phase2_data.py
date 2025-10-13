"""
Seed Phase 2 Data - Vouchers, Alerts, Tips
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import sys

# Add backend directory to path
sys.path.append('/app/backend')

from voucher_models import Voucher, VoucherStatus, DiscountType
from alert_models import Alert, AlertType, AlertSeverity, AlertStatus, WaterSavingTip

load_dotenv('/app/backend/.env')


async def seed_phase2_data():
    """Seed vouchers, sample alerts, and water saving tips"""
    
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'indowater_db')]
    
    print("🌱 Seeding Phase 2 data...")
    
    # Get demo users
    admin_user = await db.users.find_one({"email": "admin@indowater.com"})
    customer_user = await db.users.find_one({"email": "customer@indowater.com"})
    
    if not admin_user or not customer_user:
        print("❌ Demo users not found! Please run seed_demo_users.py first.")
        return
    
    admin_id = admin_user["id"]
    customer_id = customer_user["id"]
    
    # Clear existing phase 2 data
    await db.vouchers.delete_many({})
    await db.water_saving_tips.delete_many({})
    print("✓ Cleared existing Phase 2 data")
    
    # ============================================
    # SEED VOUCHERS
    # ============================================
    print("\n📝 Creating vouchers...")
    
    vouchers = [
        Voucher(
            code="WELCOME50",
            description="Welcome bonus - 50% off first top-up",
            discount_type=DiscountType.PERCENTAGE,
            discount_value=50,
            min_purchase_amount=50000,
            max_discount_amount=100000,
            usage_limit=100,
            per_customer_limit=1,
            valid_from=datetime.utcnow() - timedelta(days=1),
            valid_until=datetime.utcnow() + timedelta(days=30),
            created_by=admin_id,
            status=VoucherStatus.ACTIVE
        ),
        Voucher(
            code="HEMAT20",
            description="Save 20% on any top-up",
            discount_type=DiscountType.PERCENTAGE,
            discount_value=20,
            min_purchase_amount=100000,
            max_discount_amount=50000,
            usage_limit=None,  # Unlimited
            per_customer_limit=3,
            valid_from=datetime.utcnow() - timedelta(days=5),
            valid_until=datetime.utcnow() + timedelta(days=60),
            created_by=admin_id,
            status=VoucherStatus.ACTIVE
        ),
        Voucher(
            code="FLASH100K",
            description="Flash sale - IDR 100,000 off",
            discount_type=DiscountType.FIXED_AMOUNT,
            discount_value=100000,
            min_purchase_amount=500000,
            max_discount_amount=None,
            usage_limit=50,
            per_customer_limit=1,
            valid_from=datetime.utcnow(),
            valid_until=datetime.utcnow() + timedelta(days=7),
            created_by=admin_id,
            status=VoucherStatus.ACTIVE
        ),
        Voucher(
            code="NEWYEAR2025",
            description="New Year special - 30% off",
            discount_type=DiscountType.PERCENTAGE,
            discount_value=30,
            min_purchase_amount=200000,
            max_discount_amount=150000,
            usage_limit=200,
            per_customer_limit=2,
            valid_from=datetime.utcnow(),
            valid_until=datetime.utcnow() + timedelta(days=90),
            created_by=admin_id,
            status=VoucherStatus.ACTIVE
        ),
        Voucher(
            code="EXPIRED10",
            description="Expired voucher example",
            discount_type=DiscountType.PERCENTAGE,
            discount_value=10,
            min_purchase_amount=50000,
            max_discount_amount=25000,
            usage_limit=100,
            per_customer_limit=1,
            valid_from=datetime.utcnow() - timedelta(days=60),
            valid_until=datetime.utcnow() - timedelta(days=1),
            created_by=admin_id,
            status=VoucherStatus.EXPIRED
        )
    ]
    
    for voucher in vouchers:
        await db.vouchers.insert_one(voucher.dict())
    
    print(f"✓ Created {len(vouchers)} vouchers")
    
    # ============================================
    # SEED WATER SAVING TIPS
    # ============================================
    print("\n💡 Creating water saving tips...")
    
    tips = [
        WaterSavingTip(
            customer_id=customer_id,
            tip_category="usage_optimization",
            title="Take Shorter Showers",
            description="Reducing your shower time by just 2 minutes can save up to 10 liters per shower. Consider using a timer to track your shower duration.",
            potential_savings_percentage=15,
            priority=1
        ),
        WaterSavingTip(
            customer_id=customer_id,
            tip_category="leak_prevention",
            title="Fix Dripping Faucets Immediately",
            description="A dripping faucet can waste up to 20 liters of water per day. Check all faucets and repair any leaks promptly to avoid unnecessary water loss.",
            potential_savings_percentage=10,
            priority=1
        ),
        WaterSavingTip(
            customer_id=customer_id,
            tip_category="behavior_change",
            title="Turn Off Tap While Brushing Teeth",
            description="Leaving the tap running while brushing teeth wastes about 6 liters per minute. Turn off the tap and only use water for rinsing.",
            potential_savings_percentage=8,
            priority=2
        ),
        WaterSavingTip(
            customer_id=customer_id,
            tip_category="usage_optimization",
            title="Use a Bucket Instead of Hose",
            description="When washing your car or watering plants, use a bucket instead of a hose. This can save up to 300 liters per wash.",
            potential_savings_percentage=20,
            priority=2
        ),
        WaterSavingTip(
            customer_id=customer_id,
            tip_category="behavior_change",
            title="Reuse Water When Possible",
            description="Water used for washing vegetables can be reused for watering plants. Install a system to collect and reuse greywater.",
            potential_savings_percentage=12,
            priority=3
        ),
        WaterSavingTip(
            customer_id=customer_id,
            tip_category="leak_prevention",
            title="Check Toilet for Silent Leaks",
            description="Drop food coloring in your toilet tank. If color appears in the bowl without flushing, you have a leak that needs fixing.",
            potential_savings_percentage=15,
            priority=1
        )
    ]
    
    for tip in tips:
        await db.water_saving_tips.insert_one(tip.dict())
    
    print(f"✓ Created {len(tips)} water saving tips for customer")
    
    # ============================================
    # SUMMARY
    # ============================================
    print("\n" + "="*50)
    print("✅ Phase 2 Data Seeding Complete!")
    print("="*50)
    print(f"\n📊 Summary:")
    print(f"  • {len(vouchers)} vouchers created")
    print(f"    - 4 active vouchers")
    print(f"    - 1 expired voucher (for testing)")
    print(f"  • {len(tips)} water saving tips created")
    print(f"\n🎟️  Active Voucher Codes:")
    print(f"  • WELCOME50 - 50% off first top-up (max IDR 100K)")
    print(f"  • HEMAT20 - 20% off any top-up")
    print(f"  • FLASH100K - IDR 100K off on purchases ≥ IDR 500K")
    print(f"  • NEWYEAR2025 - 30% off")
    print(f"\n💡 Water Saving Tips:")
    print(f"  • {sum(1 for t in tips if t.priority == 1)} high priority tips")
    print(f"  • {sum(1 for t in tips if t.priority == 2)} medium priority tips")
    print(f"  • {sum(1 for t in tips if t.priority == 3)} low priority tips")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_phase2_data())
