"""
Seed script to create demo users for IndoWater Solution
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from auth import get_password_hash
from datetime import datetime

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def seed_demo_users():
    """Create demo users in the database"""
    
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'indowater_db')]
    
    print("🔄 Checking existing users...")
    existing_count = await db.users.count_documents({})
    print(f"Found {existing_count} existing users")
    
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
    
    print("🔄 Creating demo users...")
    
    for user in demo_users:
        # Check if user already exists
        existing = await db.users.find_one({"email": user["email"]})
        if existing:
            print(f"✓ User {user['email']} already exists")
        else:
            await db.users.insert_one(user)
            print(f"✓ Created user: {user['email']} ({user['role']})")
    
    print("\n✅ Demo users setup complete!")
    print("\nDemo Credentials:")
    print("=" * 50)
    print("Admin Account:")
    print("  Email: admin@indowater.com")
    print("  Password: admin123")
    print("\nTechnician Account:")
    print("  Email: technician@indowater.com")
    print("  Password: tech123")
    print("\nCustomer Account:")
    print("  Email: customer@indowater.com")
    print("  Password: customer123")
    print("=" * 50)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_demo_users())
