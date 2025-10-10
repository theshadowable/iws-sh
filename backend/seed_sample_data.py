"""
Seed script to create sample data for testing technician features
Creates: customers, properties, devices, and work orders
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta
import uuid

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def seed_sample_data():
    """Create sample data for testing"""
    
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'indowater_db')]
    
    print("🔄 Creating sample data...")
    
    # Get admin and technician IDs
    admin = await db.users.find_one({"email": "admin@indowater.com"}, {"_id": 0})
    tech = await db.users.find_one({"email": "technician@indowater.com"}, {"_id": 0})
    customer_user = await db.users.find_one({"email": "customer@indowater.com"}, {"_id": 0})
    
    if not admin or not tech or not customer_user:
        print("❌ Demo users not found. Please run seed_demo_users.py first")
        return
    
    admin_id = admin['id']
    tech_id = tech['id']
    customer_user_id = customer_user['id']
    
    # Create sample properties
    properties = [
        {
            "id": str(uuid.uuid4()),
            "property_name": "Green Valley Residence",
            "property_type": "residential",
            "address": "Jl. Merdeka No. 123",
            "city": "Jakarta",
            "province": "DKI Jakarta",
            "postal_code": "12345",
            "latitude": -6.2088,
            "longitude": 106.8456,
            "owner_name": "John Doe",
            "owner_phone": "+62-812-1111-1111",
            "owner_email": "john@example.com",
            "notes": "Main residential building",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "property_name": "Sunrise Commercial Plaza",
            "property_type": "commercial",
            "address": "Jl. Sudirman No. 456",
            "city": "Jakarta",
            "province": "DKI Jakarta",
            "postal_code": "12346",
            "latitude": -6.2155,
            "longitude": 106.8280,
            "owner_name": "PT. Sunrise",
            "owner_phone": "+62-812-2222-2222",
            "owner_email": "contact@sunrise.com",
            "notes": "Commercial building with multiple units",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    ]
    
    print("Creating properties...")
    for prop in properties:
        existing = await db.properties.find_one({"id": prop["id"]})
        if not existing:
            await db.properties.insert_one(prop)
            print(f"  ✓ Created property: {prop['property_name']}")
    
    # Create sample customers
    customers = [
        {
            "id": str(uuid.uuid4()),
            "user_id": customer_user_id,
            "customer_number": "CUST-001",
            "address": "Jl. Merdeka No. 123",
            "city": "Jakarta",
            "province": "DKI Jakarta",
            "postal_code": "12345",
            "id_card_number": "3174011234567890",
            "notes": "Regular residential customer",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    ]
    
    print("\nCreating customers...")
    for customer in customers:
        existing = await db.customers.find_one({"customer_number": customer["customer_number"]})
        if not existing:
            await db.customers.insert_one(customer)
            print(f"  ✓ Created customer: {customer['customer_number']}")
    
    # Create sample devices
    devices = [
        {
            "id": str(uuid.uuid4()),
            "device_id": "METER-001",
            "device_name": "Green Valley Meter #1",
            "property_id": properties[0]["id"],
            "customer_id": customers[0]["id"],
            "status": "active",
            "installation_date": (datetime.utcnow() - timedelta(days=365)).isoformat(),
            "last_maintenance_date": (datetime.utcnow() - timedelta(days=90)).isoformat(),
            "firmware_version": "v2.1.0",
            "current_balance": 500000,
            "total_water_consumed": 150.5,
            "notes": "Main water meter",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "device_id": "METER-002",
            "device_name": "Sunrise Plaza Meter #1",
            "property_id": properties[1]["id"],
            "customer_id": customers[0]["id"],
            "status": "active",
            "installation_date": (datetime.utcnow() - timedelta(days=180)).isoformat(),
            "firmware_version": "v2.1.0",
            "current_balance": 1000000,
            "total_water_consumed": 320.8,
            "notes": "Commercial meter",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    ]
    
    print("\nCreating devices...")
    for device in devices:
        existing = await db.devices.find_one({"device_id": device["device_id"]})
        if not existing:
            await db.devices.insert_one(device)
            print(f"  ✓ Created device: {device['device_name']}")
    
    # Create sample work orders
    work_orders = [
        {
            "id": str(uuid.uuid4()),
            "title": "Monthly Meter Reading - Green Valley",
            "description": "Perform monthly meter reading at Green Valley Residence",
            "work_type": "reading",
            "priority": "medium",
            "status": "assigned",
            "assigned_to": tech_id,
            "device_id": devices[0]["id"],
            "property_id": properties[0]["id"],
            "customer_id": customers[0]["id"],
            "scheduled_date": (datetime.utcnow() + timedelta(days=2)).isoformat(),
            "location_lat": properties[0]["latitude"],
            "location_lng": properties[0]["longitude"],
            "notes": "Regular monthly reading",
            "created_by": admin_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Maintenance Check - Sunrise Plaza",
            "description": "Quarterly maintenance inspection for commercial meter",
            "work_type": "maintenance",
            "priority": "high",
            "status": "assigned",
            "assigned_to": tech_id,
            "device_id": devices[1]["id"],
            "property_id": properties[1]["id"],
            "customer_id": customers[0]["id"],
            "scheduled_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "location_lat": properties[1]["latitude"],
            "location_lng": properties[1]["longitude"],
            "notes": "Check meter calibration and physical condition",
            "created_by": admin_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "New Meter Installation - Building C",
            "description": "Install new water meter for Building C unit 301",
            "work_type": "installation",
            "priority": "urgent",
            "status": "pending",
            "property_id": properties[0]["id"],
            "scheduled_date": datetime.utcnow().isoformat(),
            "location_lat": properties[0]["latitude"],
            "location_lng": properties[0]["longitude"],
            "notes": "Customer requested urgent installation",
            "created_by": admin_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    ]
    
    print("\nCreating work orders...")
    for order in work_orders:
        existing = await db.work_orders.find_one({"id": order["id"]})
        if not existing:
            await db.work_orders.insert_one(order)
            print(f"  ✓ Created work order: {order['title']}")
    
    print("\n✅ Sample data created successfully!")
    print("\nSummary:")
    print(f"  - {len(properties)} properties")
    print(f"  - {len(customers)} customers")
    print(f"  - {len(devices)} devices")
    print(f"  - {len(work_orders)} work orders")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_sample_data())
