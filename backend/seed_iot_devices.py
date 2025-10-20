"""
Seed Sample IoT Devices for Testing
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timedelta
import hashlib
import uuid
import random

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')

async def seed_iot_devices():
    """Seed sample IoT devices and readings"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.indowater
    
    print("🔄 Seeding IoT devices...")
    
    # Sample devices
    devices = [
        {
            "id": str(uuid.uuid4()),
            "device_id": "ESP32-WM-001",
            "device_name": "Water Meter - Building A",
            "device_type": "smart_meter",
            "firmware_version": "v1.2.3",
            "hardware_version": "v2.0",
            "mac_address": "AA:BB:CC:DD:EE:01",
            "connection_type": "wifi",
            "status": "online",
            "device_secret_hash": hashlib.sha256("secret123".encode()).hexdigest(),
            "customer_id": "unassigned",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_seen": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "device_id": "ESP32-WM-002",
            "device_name": "Water Meter - Building B",
            "device_type": "smart_meter",
            "firmware_version": "v1.2.3",
            "hardware_version": "v2.0",
            "mac_address": "AA:BB:CC:DD:EE:02",
            "connection_type": "wifi",
            "status": "online",
            "device_secret_hash": hashlib.sha256("secret456".encode()).hexdigest(),
            "customer_id": "unassigned",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_seen": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "device_id": "ESP32-WM-003",
            "device_name": "Water Meter - Main Supply",
            "device_type": "smart_meter",
            "firmware_version": "v1.2.2",
            "hardware_version": "v2.0",
            "mac_address": "AA:BB:CC:DD:EE:03",
            "connection_type": "wifi",
            "status": "offline",
            "device_secret_hash": hashlib.sha256("secret789".encode()).hexdigest(),
            "customer_id": "unassigned",
            "created_at": datetime.utcnow() - timedelta(days=30),
            "updated_at": datetime.utcnow() - timedelta(hours=2),
            "last_seen": datetime.utcnow() - timedelta(hours=2)
        },
        {
            "id": str(uuid.uuid4()),
            "device_id": "ESP32-WM-004",
            "device_name": "Water Meter - Garden",
            "device_type": "smart_meter",
            "firmware_version": "v1.2.3",
            "hardware_version": "v2.0",
            "mac_address": "AA:BB:CC:DD:EE:04",
            "connection_type": "wifi",
            "status": "warning",
            "device_secret_hash": hashlib.sha256("secretabc".encode()).hexdigest(),
            "customer_id": "unassigned",
            "created_at": datetime.utcnow() - timedelta(days=15),
            "updated_at": datetime.utcnow(),
            "last_seen": datetime.utcnow()
        }
    ]
    
    # Clear existing IoT devices
    await db.iot_devices.delete_many({})
    print("  Cleared existing IoT devices")
    
    # Insert devices
    if devices:
        await db.iot_devices.insert_many(devices)
        print(f"  ✓ Created {len(devices)} IoT devices")
    
    # Generate sample readings for online devices
    print("🔄 Generating sample IoT readings...")
    
    readings = []
    now = datetime.utcnow()
    
    for device in devices:
        if device["status"] in ["online", "warning"]:
            # Generate readings for last 24 hours
            for i in range(48):  # Every 30 minutes
                timestamp = now - timedelta(minutes=30 * i)
                
                # Simulate realistic water flow patterns
                hour = timestamp.hour
                base_flow = 15.0  # Base flow rate
                
                # Higher flow during day, lower at night
                if 6 <= hour < 22:
                    flow_multiplier = random.uniform(1.5, 3.0)
                else:
                    flow_multiplier = random.uniform(0.1, 0.5)
                
                flow_rate = base_flow * flow_multiplier + random.uniform(-2, 2)
                flow_rate = max(0, flow_rate)  # No negative flow
                
                reading = {
                    "id": str(uuid.uuid4()),
                    "device_id": device["device_id"],
                    "timestamp": timestamp,
                    "flow_rate": round(flow_rate, 2),
                    "volume_consumed": round(flow_rate * 0.5, 2),  # 30 min = 0.5 hour
                    "total_volume": round(random.uniform(1000, 5000), 2),
                    "balance": round(random.uniform(50000, 500000), 2),
                    "valve_status": "open" if flow_rate > 0 else "closed",
                    "device_status": "normal",
                    "temperature": round(random.uniform(20, 35), 1),
                    "pressure": round(random.uniform(2.0, 4.5), 2),
                    "battery_level": random.randint(60, 100),
                    "signal_strength": random.randint(-60, -30),
                    "received_at": timestamp,
                    "cost_per_liter": 10
                }
                
                readings.append(reading)
    
    # Clear existing readings
    await db.iot_readings.delete_many({})
    
    # Insert readings
    if readings:
        await db.iot_readings.insert_many(readings)
        print(f"  ✓ Created {len(readings)} sample readings")
    
    # Create connection records
    connections = []
    for device in devices:
        if device["status"] in ["online", "warning"]:
            connection = {
                "device_id": device["device_id"],
                "connection_type": device["connection_type"],
                "status": device["status"],
                "last_seen": device["last_seen"],
                "ip_address": f"192.168.1.{random.randint(100, 200)}",
                "rssi": random.randint(-60, -30)
            }
            connections.append(connection)
    
    # Clear and insert connections
    await db.iot_connections.delete_many({})
    if connections:
        await db.iot_connections.insert_many(connections)
        print(f"  ✓ Created {len(connections)} connection records")
    
    print("\n✅ IoT devices seeding complete!")
    print("\nSample Device Credentials:")
    print("="*60)
    print("Device ID: ESP32-WM-001")
    print("Device Secret: secret123")
    print("Status: Online")
    print()
    print("Device ID: ESP32-WM-002")
    print("Device Secret: secret456")
    print("Status: Online")
    print()
    print("Device ID: ESP32-WM-003")
    print("Device Secret: secret789")
    print("Status: Offline")
    print()
    print("Device ID: ESP32-WM-004")
    print("Device Secret: secretabc")
    print("Status: Warning")
    print("="*60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_iot_devices())
