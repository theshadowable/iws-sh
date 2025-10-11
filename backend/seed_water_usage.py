"""
Water Usage Data Generation Script
Generates 6 months of realistic water usage data for testing analytics
"""
import asyncio
import os
import random
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import uuid


# Water usage patterns for different property types
USAGE_PATTERNS = {
    'residential': {
        'base_daily': 0.5,  # 0.5 m³ per day (500 liters)
        'variance': 0.2,
        'weekend_multiplier': 1.3,
        'seasonal_variance': 0.15
    },
    'commercial': {
        'base_daily': 2.0,  # 2 m³ per day
        'variance': 0.3,
        'weekend_multiplier': 0.7,  # Less on weekends
        'seasonal_variance': 0.1
    },
    'industrial': {
        'base_daily': 10.0,  # 10 m³ per day
        'variance': 0.4,
        'weekend_multiplier': 0.5,  # Much less on weekends
        'seasonal_variance': 0.2
    }
}

# Cost per cubic meter (in IDR)
COST_PER_M3 = 10000


def generate_daily_consumption(property_type, date, has_anomaly=False):
    """Generate realistic daily water consumption"""
    pattern = USAGE_PATTERNS.get(property_type, USAGE_PATTERNS['residential'])
    
    # Base consumption
    consumption = pattern['base_daily']
    
    # Weekend adjustment
    if date.weekday() >= 5:  # Saturday or Sunday
        consumption *= pattern['weekend_multiplier']
    
    # Seasonal variation (higher in summer months)
    month = date.month
    if month in [4, 5, 6, 7, 8, 9]:  # April to September (dry season)
        seasonal_factor = 1 + pattern['seasonal_variance']
    else:
        seasonal_factor = 1 - pattern['seasonal_variance']
    consumption *= seasonal_factor
    
    # Random daily variation
    random_factor = 1 + random.uniform(-pattern['variance'], pattern['variance'])
    consumption *= random_factor
    
    # Add anomalies (leaks, unusual usage)
    if has_anomaly:
        consumption *= random.uniform(2.0, 3.5)
    
    return round(consumption, 3)


async def seed_water_usage_data():
    """Generate and seed water usage data"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'indowater_db')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🔄 Checking existing data...")
    
    # Check existing water usage data
    existing_count = await db.water_usage.count_documents({})
    print(f"Found {existing_count} existing water usage records")
    
    if existing_count > 0:
        response = input("⚠️  Water usage data already exists. Delete and regenerate? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Seed cancelled")
            client.close()
            return
        
        # Delete existing data
        await db.water_usage.delete_many({})
        print("✓ Deleted existing water usage data")
    
    # Get customers and devices
    customers = await db.customers.find().to_list(None)
    devices = await db.devices.find().to_list(None)
    properties = await db.properties.find().to_list(None)
    
    if not customers:
        print("⚠️  No customers found. Creating sample customer...")
        sample_customer = {
            "id": "customer-sample-001",
            "full_name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+62-812-1111-1111",
            "address": "Jl. Sample No. 1, Jakarta",
            "created_at": datetime.utcnow().isoformat()
        }
        await db.customers.insert_one(sample_customer)
        customers = [sample_customer]
    
    if not devices:
        print("⚠️  No devices found. Creating sample devices...")
        for i, customer in enumerate(customers[:3]):  # Create max 3 sample devices
            sample_device = {
                "id": f"device-sample-{i+1:03d}",
                "device_serial": f"WM-{random.randint(10000, 99999)}",
                "customer_id": customer['id'],
                "property_id": properties[0]['id'] if properties else f"property-sample-{i+1:03d}",
                "device_type": "prepaid_water_meter",
                "status": "active",
                "last_reading": 0.0,
                "created_at": datetime.utcnow().isoformat()
            }
            await db.devices.insert_one(sample_device)
        devices = await db.devices.find().to_list(None)
    
    if not properties:
        print("⚠️  No properties found. Creating sample properties...")
        property_types = ['residential', 'commercial', 'industrial']
        for i in range(min(3, len(devices))):
            sample_property = {
                "id": f"property-sample-{i+1:03d}",
                "name": f"Sample Property {i+1}",
                "type": property_types[i % len(property_types)],
                "address": f"Jl. Sample No. {i+1}, Jakarta",
                "created_at": datetime.utcnow().isoformat()
            }
            await db.properties.insert_one(sample_property)
        properties = await db.properties.find().to_list(None)
    
    print(f"\n📊 Generating 6 months of water usage data...")
    print(f"   Customers: {len(customers)}")
    print(f"   Devices: {len(devices)}")
    print(f"   Properties: {len(properties)}")
    
    # Generate data for the last 6 months
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=180)
    
    water_usage_records = []
    total_records = 0
    
    # Create a mapping of device to property
    device_property_map = {}
    for device in devices:
        device_property_map[device['id']] = device.get('property_id', properties[0]['id'] if properties else None)
    
    # For each device, generate daily readings
    for device in devices:
        print(f"\n   Generating data for device: {device['id']}")
        
        # Get property type for this device
        property_id = device_property_map.get(device['id'])
        property = next((p for p in properties if p['id'] == property_id), None)
        property_type = property.get('type', 'residential') if property else 'residential'
        
        current_date = start_date
        cumulative_reading = random.uniform(100, 500)  # Starting meter reading
        
        while current_date <= end_date:
            # Add some anomalies (3% chance)
            has_anomaly = random.random() < 0.03
            
            # Generate daily consumption
            daily_consumption = generate_daily_consumption(
                property_type, 
                current_date,
                has_anomaly
            )
            
            cumulative_reading += daily_consumption
            
            # Create usage record
            record = {
                "id": str(uuid.uuid4()),
                "device_id": device['id'],
                "customer_id": device.get('customer_id', customers[0]['id']),
                "property_id": property_id,
                "reading_value": round(cumulative_reading, 3),
                "reading_date": current_date.isoformat(),
                "consumption": daily_consumption,
                "cost": round(daily_consumption * COST_PER_M3, 2),
                "meter_status": "active",
                "recorded_at": current_date.isoformat(),
                "recorded_by": "system",
                "notes": "Anomaly detected" if has_anomaly else ""
            }
            
            water_usage_records.append(record)
            total_records += 1
            
            # Move to next day
            current_date += timedelta(days=1)
        
        print(f"      ✓ Generated {total_records} records")
    
    # Insert all records
    if water_usage_records:
        print(f"\n🔄 Inserting {len(water_usage_records)} records into database...")
        await db.water_usage.insert_many(water_usage_records)
        print(f"✅ Successfully inserted {len(water_usage_records)} water usage records!")
        
        # Show statistics
        print("\n📈 Data Statistics:")
        print(f"   Total Records: {len(water_usage_records)}")
        print(f"   Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print(f"   Devices: {len(devices)}")
        
        # Calculate total consumption
        total_consumption = sum(r['consumption'] for r in water_usage_records)
        total_cost = sum(r['cost'] for r in water_usage_records)
        print(f"   Total Consumption: {total_consumption:.2f} m³")
        print(f"   Total Cost: Rp {total_cost:,.2f}")
        
        # Average daily consumption per device
        avg_daily = total_consumption / len(devices) / 180
        print(f"   Avg Daily per Device: {avg_daily:.3f} m³")
    
    client.close()
    print("\n✅ Water usage data generation complete!")


if __name__ == "__main__":
    asyncio.run(seed_water_usage_data())
