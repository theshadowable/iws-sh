"""
Seed API Routes - Temporary endpoint to populate production database
⚠️ SECURITY: This endpoint should be disabled after initial seeding
"""
from fastapi import APIRouter, HTTPException, Header
from motor.motor_asyncio import AsyncIOMotorClient
from auth import get_password_hash
from datetime import datetime
import os

router = APIRouter(prefix="/seed", tags=["seed"])

# Security key - must match SEED_SECRET_KEY environment variable
SEED_SECRET_KEY = os.environ.get('SEED_SECRET_KEY', 'indowater-seed-2025-secure')

@router.post("/demo-users")
async def seed_demo_users(x_seed_key: str = Header(None)):
    """
    Seed demo users to production database
    
    ⚠️ SECURITY WARNING: This endpoint should only be used once during initial deployment
    
    Usage:
    ```
    curl -X POST https://indowater.onrender.com/api/seed/demo-users \
         -H "x-seed-key: indowater-seed-2025-secure"
    ```
    
    Or visit in browser:
    https://indowater.onrender.com/api/seed/demo-users?key=indowater-seed-2025-secure
    """
    # Check security key from header or query param
    if x_seed_key != SEED_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid seed key")
    
    from server import db
    
    try:
        # Check existing users
        existing_count = await db.users.count_documents({})
        
        # Demo users data
        demo_users = [
            {
                "id": "admin-001",
                "email": "admin@indowater.com",
                "full_name": "Admin User",
                "role": "admin",
                "phone": "+62-812-3456-7890",
                "is_active": True,
                "hashed_password": get_password_hash("admin123"),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "id": "tech-001",
                "email": "technician@indowater.com",
                "full_name": "Technician User",
                "role": "technician",
                "phone": "+62-812-3456-7891",
                "is_active": True,
                "hashed_password": get_password_hash("tech123"),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "id": "cust-001",
                "email": "customer@indowater.com",
                "full_name": "Customer User",
                "role": "customer",
                "phone": "+62-812-3456-7892",
                "is_active": True,
                "hashed_password": get_password_hash("customer123"),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        ]
        
        created_users = []
        existing_users = []
        
        for user in demo_users:
            # Check if user already exists
            existing = await db.users.find_one({"email": user["email"]})
            if existing:
                existing_users.append(user['email'])
            else:
                await db.users.insert_one(user)
                created_users.append({
                    "email": user['email'],
                    "role": user['role']
                })
        
        return {
            "success": True,
            "message": "Demo users seeded successfully",
            "summary": {
                "existing_users_before": existing_count,
                "created": len(created_users),
                "already_existed": len(existing_users),
                "total_users_now": await db.users.count_documents({})
            },
            "created_users": created_users,
            "existing_users": existing_users,
            "credentials": {
                "admin": {
                    "email": "admin@indowater.com",
                    "password": "admin123"
                },
                "technician": {
                    "email": "technician@indowater.com",
                    "password": "tech123"
                },
                "customer": {
                    "email": "customer@indowater.com",
                    "password": "customer123"
                }
            },
            "⚠️_warning": "Please disable this endpoint after seeding by removing seed_routes from server.py"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Seeding failed: {str(e)}")


@router.get("/demo-users")
async def seed_demo_users_get(key: str = None):
    """
    Alternative GET endpoint for browser access
    Usage: https://indowater.onrender.com/api/seed/demo-users?key=indowater-seed-2025-secure
    """
    if key != SEED_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid seed key. Add ?key=YOUR_SECRET_KEY to URL")
    
    # Call the POST endpoint logic
    return await seed_demo_users(x_seed_key=key)


@router.post("/water-usage")
async def seed_water_usage(x_seed_key: str = Header(None)):
    """
    Seed sample water usage data for analytics testing
    
    Usage:
    ```
    curl -X POST https://indowater.onrender.com/api/seed/water-usage \
         -H "x-seed-key: indowater-seed-2025-secure"
    ```
    """
    if x_seed_key != SEED_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid seed key")
    
    from server import db
    from datetime import timedelta
    import random
    
    try:
        # Check if admin user exists (required for seeding)
        admin = await db.users.find_one({"email": "admin@indowater.com"})
        if not admin:
            raise HTTPException(status_code=400, detail="Demo users must be seeded first. Call /api/seed/demo-users first.")
        
        # Check for existing devices
        device_count = await db.devices.count_documents({})
        if device_count == 0:
            # Create sample device
            device = {
                "id": "device-001",
                "device_id": "IW-001",
                "customer_id": "cust-001",
                "property_id": "prop-001",
                "device_type": "smart_meter",
                "status": "active",
                "installation_date": datetime.utcnow().isoformat(),
                "current_balance": 500000,
                "total_water_consumed": 0,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            await db.devices.insert_one(device)
        
        # Generate 30 days of water usage data
        usage_records = []
        base_date = datetime.utcnow() - timedelta(days=30)
        
        for day in range(30):
            current_date = base_date + timedelta(days=day)
            
            # Generate 4-6 readings per day
            readings_per_day = random.randint(4, 6)
            for reading in range(readings_per_day):
                reading_time = current_date + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
                
                usage_record = {
                    "id": f"usage-{day:03d}-{reading:02d}",
                    "device_id": "device-001",
                    "customer_id": "cust-001",
                    "reading_date": reading_time.isoformat(),
                    "water_consumed": round(random.uniform(0.5, 2.5), 2),  # m³
                    "cost": round(random.uniform(5000, 25000), 2),  # IDR
                    "reading_type": "automatic",
                    "created_at": reading_time.isoformat()
                }
                usage_records.append(usage_record)
        
        # Insert all records
        if usage_records:
            await db.water_usage.insert_many(usage_records)
        
        return {
            "success": True,
            "message": "Water usage data seeded successfully",
            "summary": {
                "records_created": len(usage_records),
                "date_range": f"{base_date.date()} to {datetime.utcnow().date()}",
                "days": 30
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Seeding failed: {str(e)}")
