"""
Comprehensive Database Seeding Script
Seeds all collections with realistic demo data for testing

Collections seeded:
- users (6 users: 1 admin, 2 technicians, 3 customers)
- properties (5 properties with various types)
- devices (6 devices with different statuses)
- vouchers (6 vouchers with various discount types)
- support_tickets (6 tickets with different statuses)
- water_conservation_tips (8 tips with complete data)
- water_usage (180 records - 30 days × 6 devices)
- transactions (8 payment transactions)
- device_alerts (12 alerts)
- device_activities (24 activities)
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from auth import get_password_hash
import os
import uuid
from dotenv import load_dotenv
import random

load_dotenv()

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db_name = os.environ.get('DB_NAME', 'indowater')
db = client[db_name]

async def seed_users():
    """Seed demo users"""
    print("🔹 Seeding users...")
    
    # Clear existing users
    await db.users.delete_many({})
    
    users = [
        {
            "id": "admin-001",
            "email": "admin@indowater.com",
            "hashed_password": get_password_hash("admin123"),
            "full_name": "Admin IndoWater",
            "phone": "+62812345678",
            "role": "admin",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": "tech-001",
            "email": "technician@indowater.com",
            "hashed_password": get_password_hash("tech123"),
            "full_name": "Technician User",
            "phone": "+62812345679",
            "role": "technician",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": "tech-002",
            "email": "technician2@indowater.com",
            "hashed_password": get_password_hash("tech123"),
            "full_name": "Technician Dua",
            "phone": "+62812345680",
            "role": "technician",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": "cust-001",
            "email": "customer@indowater.com",
            "hashed_password": get_password_hash("customer123"),
            "full_name": "Customer Demo",
            "phone": "+62812345681",
            "role": "customer",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": "cust-002",
            "email": "john.doe@example.com",
            "hashed_password": get_password_hash("customer123"),
            "full_name": "John Doe",
            "phone": "+62812345682",
            "role": "customer",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": "cust-003",
            "email": "jane.smith@example.com",
            "hashed_password": get_password_hash("customer123"),
            "full_name": "Jane Smith",
            "phone": "+62812345683",
            "role": "customer",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    ]
    
    await db.users.insert_many(users)
    print(f"   ✅ Seeded {len(users)} users")
    return users

async def seed_properties():
    """Seed demo properties"""
    print("🔹 Seeding properties...")
    
    # Clear existing properties
    await db.properties.delete_many({})
    
    properties = [
        {
            "id": "prop-001",
            "property_name": "Rumah Residence A",
            "property_type": "residential",
            "address": "Jl. Merdeka No. 123",
            "city": "Jakarta",
            "postal_code": "12345",
            "customer_id": "cust-001",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": "prop-002",
            "property_name": "Apartment Central Park",
            "property_type": "residential",
            "address": "Jl. Sudirman No. 456",
            "city": "Jakarta",
            "postal_code": "12346",
            "customer_id": "cust-002",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": "prop-003",
            "property_name": "Office Building XYZ",
            "property_type": "commercial",
            "address": "Jl. Gatot Subroto No. 789",
            "city": "Jakarta",
            "postal_code": "12347",
            "customer_id": "cust-002",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": "prop-004",
            "property_name": "Factory ABC",
            "property_type": "industrial",
            "address": "Jl. Industri No. 321",
            "city": "Bekasi",
            "postal_code": "17530",
            "customer_id": "cust-003",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": "prop-005",
            "property_name": "Hotel Grand Pacific",
            "property_type": "commercial",
            "address": "Jl. Thamrin No. 555",
            "city": "Jakarta",
            "postal_code": "12348",
            "customer_id": "cust-003",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    ]
    
    await db.properties.insert_many(properties)
    print(f"   ✅ Seeded {len(properties)} properties")
    return properties

async def seed_devices():
    """Seed demo devices"""
    print("🔹 Seeding devices...")
    
    # Clear existing devices
    await db.devices.delete_many({})
    
    devices = [
        {
            "id": "dev-001",
            "device_id": "WM-2024-001",
            "device_name": "Water Meter Residence A",
            "device_type": "smart_meter",
            "serial_number": "SN20240001",
            "property_id": "prop-001",
            "customer_id": "cust-001",
            "status": "active",
            "installation_date": (datetime.utcnow() - timedelta(days=180)).isoformat(),
            "last_reading_date": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            "current_balance": 250000.0,
            "total_water_consumed": 45.5,
            "firmware_version": "1.2.3",
            "signal_strength": -65,
            "battery_level": 85,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": "dev-002",
            "device_id": "WM-2024-002",
            "device_name": "Water Meter Apartment",
            "device_type": "smart_meter",
            "serial_number": "SN20240002",
            "property_id": "prop-002",
            "customer_id": "cust-002",
            "status": "active",
            "installation_date": (datetime.utcnow() - timedelta(days=150)).isoformat(),
            "last_reading_date": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "current_balance": 180000.0,
            "total_water_consumed": 32.8,
            "firmware_version": "1.2.3",
            "signal_strength": -70,
            "battery_level": 72,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": "dev-003",
            "device_id": "WM-2024-003",
            "device_name": "Water Meter Office XYZ",
            "device_type": "smart_meter",
            "serial_number": "SN20240003",
            "property_id": "prop-003",
            "customer_id": "cust-002",
            "status": "active",
            "installation_date": (datetime.utcnow() - timedelta(days=120)).isoformat(),
            "last_reading_date": (datetime.utcnow() - timedelta(hours=3)).isoformat(),
            "current_balance": 500000.0,
            "total_water_consumed": 125.3,
            "firmware_version": "1.2.3",
            "signal_strength": -68,
            "battery_level": 90,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": "dev-004",
            "device_id": "WM-2024-004",
            "device_name": "Water Meter Factory",
            "device_type": "smart_meter",
            "serial_number": "SN20240004",
            "property_id": "prop-004",
            "customer_id": "cust-003",
            "status": "active",
            "installation_date": (datetime.utcnow() - timedelta(days=200)).isoformat(),
            "last_reading_date": (datetime.utcnow() - timedelta(hours=4)).isoformat(),
            "current_balance": 850000.0,
            "total_water_consumed": 456.7,
            "firmware_version": "1.2.3",
            "signal_strength": -72,
            "battery_level": 65,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": "dev-005",
            "device_id": "WM-2024-005",
            "device_name": "Water Meter Hotel",
            "device_type": "smart_meter",
            "serial_number": "SN20240005",
            "property_id": "prop-005",
            "customer_id": "cust-003",
            "status": "active",
            "installation_date": (datetime.utcnow() - timedelta(days=90)).isoformat(),
            "last_reading_date": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            "current_balance": 1200000.0,
            "total_water_consumed": 678.9,
            "firmware_version": "1.2.3",
            "signal_strength": -66,
            "battery_level": 88,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": "dev-006",
            "device_id": "WM-2024-006",
            "device_name": "Water Meter Unassigned",
            "device_type": "smart_meter",
            "serial_number": "SN20240006",
            "property_id": "unassigned",
            "customer_id": "unassigned",
            "status": "inactive",
            "installation_date": datetime.utcnow().isoformat(),
            "last_reading_date": None,
            "current_balance": 0.0,
            "total_water_consumed": 0.0,
            "firmware_version": "1.2.3",
            "signal_strength": None,
            "battery_level": 100,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    ]
    
    await db.devices.insert_many(devices)
    print(f"   ✅ Seeded {len(devices)} devices")
    return devices

async def seed_vouchers():
    """Seed demo vouchers"""
    print("🔹 Seeding vouchers...")
    
    # Clear existing vouchers
    await db.vouchers.delete_many({})
    
    now = datetime.utcnow()
    
    vouchers = [
        {
            "id": str(uuid.uuid4()),
            "code": "WELCOME50",
            "description": "Welcome discount 50% for new customers",
            "discount_type": "percentage",
            "discount_value": 50.0,
            "min_purchase_amount": 100000.0,
            "max_discount_amount": 250000.0,
            "usage_limit": 100,
            "usage_count": 15,
            "per_customer_limit": 1,
            "valid_from": (now - timedelta(days=10)).isoformat(),
            "valid_until": (now + timedelta(days=20)).isoformat(),
            "status": "active",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "code": "HEMAT20",
            "description": "Save 20% on all top-ups",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "min_purchase_amount": 50000.0,
            "max_discount_amount": 100000.0,
            "usage_limit": 500,
            "usage_count": 87,
            "per_customer_limit": 5,
            "valid_from": (now - timedelta(days=30)).isoformat(),
            "valid_until": (now + timedelta(days=60)).isoformat(),
            "status": "active",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "code": "FLASH100K",
            "description": "Flash sale - Rp 100,000 discount",
            "discount_type": "fixed",
            "discount_value": 100000.0,
            "min_purchase_amount": 500000.0,
            "max_discount_amount": None,
            "usage_limit": 50,
            "usage_count": 42,
            "per_customer_limit": 1,
            "valid_from": now.isoformat(),
            "valid_until": (now + timedelta(days=3)).isoformat(),
            "status": "active",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "code": "NEWYEAR2025",
            "description": "New Year 2025 - 30% off",
            "discount_type": "percentage",
            "discount_value": 30.0,
            "min_purchase_amount": 200000.0,
            "max_discount_amount": 300000.0,
            "usage_limit": 1000,
            "usage_count": 234,
            "per_customer_limit": 2,
            "valid_from": (now - timedelta(days=5)).isoformat(),
            "valid_until": (now + timedelta(days=25)).isoformat(),
            "status": "active",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "code": "EXPIRED10",
            "description": "Expired voucher - 10% off",
            "discount_type": "percentage",
            "discount_value": 10.0,
            "min_purchase_amount": 50000.0,
            "max_discount_amount": 50000.0,
            "usage_limit": 100,
            "usage_count": 89,
            "per_customer_limit": 3,
            "valid_from": (now - timedelta(days=60)).isoformat(),
            "valid_until": (now - timedelta(days=5)).isoformat(),
            "status": "expired",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "code": "PAUSED25",
            "description": "Paused voucher - 25% off",
            "discount_type": "percentage",
            "discount_value": 25.0,
            "min_purchase_amount": 150000.0,
            "max_discount_amount": 200000.0,
            "usage_limit": 200,
            "usage_count": 45,
            "per_customer_limit": 1,
            "valid_from": now.isoformat(),
            "valid_until": (now + timedelta(days=30)).isoformat(),
            "status": "paused",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
    ]
    
    await db.vouchers.insert_many(vouchers)
    print(f"   ✅ Seeded {len(vouchers)} vouchers")
    return vouchers

async def seed_support_tickets():
    """Seed demo support tickets"""
    print("🔹 Seeding support tickets...")
    
    # Clear existing tickets
    await db.support_tickets.delete_many({})
    
    now = datetime.utcnow()
    
    tickets = [
        {
            "id": str(uuid.uuid4()),
            "ticket_number": "TKT-2025-0001",
            "customer_id": "cust-001",
            "customer_name": "Customer Demo",
            "customer_email": "customer@indowater.com",
            "assigned_to": "tech-001",
            "assigned_to_name": "Technician User",
            "category": "technical_issue",
            "priority": "high",
            "status": "in_progress",
            "subject": "Water meter not recording properly",
            "description": "My water meter shows incorrect readings. It's showing higher consumption than actual usage.",
            "created_at": (now - timedelta(days=2)).isoformat(),
            "updated_at": (now - timedelta(hours=5)).isoformat(),
            "resolved_at": None,
            "closed_at": None,
            "attachments": [],
            "messages_count": 3,
            "last_message_at": (now - timedelta(hours=5)).isoformat(),
            "signature_id": None
        },
        {
            "id": str(uuid.uuid4()),
            "ticket_number": "TKT-2025-0002",
            "customer_id": "cust-002",
            "customer_name": "John Doe",
            "customer_email": "john.doe@example.com",
            "assigned_to": None,
            "assigned_to_name": None,
            "category": "billing_issue",
            "priority": "medium",
            "status": "open",
            "subject": "Incorrect billing amount",
            "description": "I was charged Rp 500,000 but my usage should be around Rp 300,000 only.",
            "created_at": (now - timedelta(hours=12)).isoformat(),
            "updated_at": (now - timedelta(hours=12)).isoformat(),
            "resolved_at": None,
            "closed_at": None,
            "attachments": [],
            "messages_count": 0,
            "last_message_at": None,
            "signature_id": None
        },
        {
            "id": str(uuid.uuid4()),
            "ticket_number": "TKT-2025-0003",
            "customer_id": "cust-002",
            "customer_name": "John Doe",
            "customer_email": "john.doe@example.com",
            "assigned_to": "tech-002",
            "assigned_to_name": "Technician Dua",
            "category": "maintenance_repairs",
            "priority": "critical",
            "status": "open",
            "subject": "Water leak detected",
            "description": "There's a water leak in the main pipe. Need urgent repair.",
            "created_at": (now - timedelta(hours=3)).isoformat(),
            "updated_at": (now - timedelta(hours=3)).isoformat(),
            "resolved_at": None,
            "closed_at": None,
            "attachments": [],
            "messages_count": 1,
            "last_message_at": (now - timedelta(hours=2)).isoformat(),
            "signature_id": None
        },
        {
            "id": str(uuid.uuid4()),
            "ticket_number": "TKT-2025-0004",
            "customer_id": "cust-003",
            "customer_name": "Jane Smith",
            "customer_email": "jane.smith@example.com",
            "assigned_to": "tech-001",
            "assigned_to_name": "Technician User",
            "category": "general_inquiry",
            "priority": "low",
            "status": "resolved",
            "subject": "How to check water usage history?",
            "description": "I want to see my water usage for the past 3 months. How can I do that?",
            "created_at": (now - timedelta(days=5)).isoformat(),
            "updated_at": (now - timedelta(days=4)).isoformat(),
            "resolved_at": (now - timedelta(days=4)).isoformat(),
            "closed_at": None,
            "attachments": [],
            "messages_count": 4,
            "last_message_at": (now - timedelta(days=4)).isoformat(),
            "signature_id": None
        },
        {
            "id": str(uuid.uuid4()),
            "ticket_number": "TKT-2025-0005",
            "customer_id": "cust-003",
            "customer_name": "Jane Smith",
            "customer_email": "jane.smith@example.com",
            "assigned_to": "tech-002",
            "assigned_to_name": "Technician Dua",
            "category": "installation",
            "priority": "medium",
            "status": "closed",
            "subject": "Install new water meter",
            "description": "Need installation of smart water meter for my hotel property.",
            "created_at": (now - timedelta(days=15)).isoformat(),
            "updated_at": (now - timedelta(days=10)).isoformat(),
            "resolved_at": (now - timedelta(days=11)).isoformat(),
            "closed_at": (now - timedelta(days=10)).isoformat(),
            "attachments": [],
            "messages_count": 7,
            "last_message_at": (now - timedelta(days=11)).isoformat(),
            "signature_id": str(uuid.uuid4())
        },
        {
            "id": str(uuid.uuid4()),
            "ticket_number": "TKT-2025-0006",
            "customer_id": "cust-001",
            "customer_name": "Customer Demo",
            "customer_email": "customer@indowater.com",
            "assigned_to": None,
            "assigned_to_name": None,
            "category": "account_management",
            "priority": "low",
            "status": "open",
            "subject": "Change email address",
            "description": "I want to update my registered email address in the system.",
            "created_at": (now - timedelta(hours=6)).isoformat(),
            "updated_at": (now - timedelta(hours=6)).isoformat(),
            "resolved_at": None,
            "closed_at": None,
            "attachments": [],
            "messages_count": 0,
            "last_message_at": None,
            "signature_id": None
        }
    ]
    
    await db.support_tickets.insert_many(tickets)
    print(f"   ✅ Seeded {len(tickets)} support tickets")
    return tickets

async def seed_water_tips():
    """Seed water conservation tips"""
    print("🔹 Seeding water conservation tips...")
    
    # Clear existing tips
    await db.water_conservation_tips.delete_many({})
    
    now = datetime.utcnow()
    
    tips = [
        {
            "id": str(uuid.uuid4()),
            "title": "Hemat Air dengan Shower Timer",
            "description": "Kurangi konsumsi air saat mandi dengan menggunakan timer. Rata-rata mandi 10 menit menggunakan 150 liter air.",
            "category": "general_savings",
            "difficulty_level": "easy",
            "potential_savings_percentage": 30.0,
            "implementation_time": "5 menit",
            "implementation_steps": [
                "Pasang timer di kamar mandi",
                "Set timer untuk 5-7 menit",
                "Mulai biasakan mandi lebih efisien"
            ],
            "benefits": [
                "Hemat air hingga 30%",
                "Tagihan air lebih murah",
                "Lebih ramah lingkungan"
            ],
            "required_tools": [
                "Shower timer (Rp 50.000)",
                "Tidak perlu tools khusus"
            ],
            "status": "published",
            "view_count": 234,
            "like_count": 45,
            "bookmark_count": 23,
            "implementation_count": 12,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Deteksi Kebocoran Air Sederhana",
            "description": "Cara mudah mendeteksi kebocoran air di rumah menggunakan meteran air.",
            "category": "leak_prevention",
            "difficulty_level": "easy",
            "potential_savings_percentage": 25.0,
            "implementation_time": "10 menit",
            "implementation_steps": [
                "Matikan semua keran dan alat yang menggunakan air",
                "Catat angka di meteran air",
                "Tunggu 30 menit tanpa menggunakan air",
                "Cek lagi meteran air",
                "Jika angka berubah, ada kebocoran"
            ],
            "benefits": [
                "Deteksi kebocoran lebih awal",
                "Hindari pemborosan air",
                "Tagihan air tidak membengkak"
            ],
            "required_tools": [
                "Meteran air",
                "Catatan dan pulpen"
            ],
            "status": "published",
            "view_count": 456,
            "like_count": 89,
            "bookmark_count": 56,
            "implementation_count": 34,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Gunakan Toilet Dual Flush",
            "description": "Upgrade toilet dengan sistem dual flush untuk hemat air hingga 40%.",
            "category": "best_practices",
            "difficulty_level": "medium",
            "potential_savings_percentage": 40.0,
            "implementation_time": "2 jam",
            "implementation_steps": [
                "Beli toilet dual flush atau conversion kit",
                "Matikan supply air ke toilet",
                "Lepas toilet lama (jika ganti total)",
                "Pasang toilet baru atau install conversion kit",
                "Test sistem dual flush"
            ],
            "benefits": [
                "Hemat air hingga 40%",
                "Pilihan flush besar (6L) dan kecil (3L)",
                "Investasi jangka panjang"
            ],
            "required_tools": [
                "Toilet dual flush atau conversion kit (Rp 500.000 - 2.000.000)",
                "Kunci inggris",
                "Obeng"
            ],
            "status": "published",
            "view_count": 178,
            "like_count": 34,
            "bookmark_count": 28,
            "implementation_count": 8,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Cuci Mobil dengan Ember, Bukan Selang",
            "description": "Hemat ratusan liter air dengan menggunakan ember dan spons saat cuci mobil.",
            "category": "general_savings",
            "difficulty_level": "easy",
            "potential_savings_percentage": 70.0,
            "implementation_time": "5 menit",
            "implementation_steps": [
                "Siapkan 2 ember (1 untuk sabun, 1 untuk bilas)",
                "Isi ember dengan air secukupnya (20-30 liter total)",
                "Gunakan spons/lap microfiber",
                "Cuci mobil dengan sabun dari ember",
                "Bilas dengan air dari ember kedua"
            ],
            "benefits": [
                "Hemat air hingga 70% (dari 300L menjadi 30L)",
                "Lebih kontrol penggunaan air",
                "Sabun lebih merata"
            ],
            "required_tools": [
                "2 ember",
                "Spons atau lap microfiber",
                "Sabun cuci mobil"
            ],
            "status": "published",
            "view_count": 312,
            "like_count": 67,
            "bookmark_count": 41,
            "implementation_count": 19,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Install Aerator pada Keran",
            "description": "Pasang aerator untuk mengurangi debit air tanpa mengurangi tekanan.",
            "category": "best_practices",
            "difficulty_level": "easy",
            "potential_savings_percentage": 30.0,
            "implementation_time": "10 menit",
            "implementation_steps": [
                "Beli aerator sesuai ukuran keran (M22 atau M24)",
                "Lepas aerator lama jika ada",
                "Pasang aerator baru dengan memutar searah jarum jam",
                "Test aliran air"
            ],
            "benefits": [
                "Hemat air hingga 30%",
                "Tekanan air tetap nyaman",
                "Murah dan mudah dipasang"
            ],
            "required_tools": [
                "Aerator keran (Rp 20.000 - 50.000 per unit)",
                "Kunci inggris (optional)"
            ],
            "status": "published",
            "view_count": 523,
            "like_count": 102,
            "bookmark_count": 78,
            "implementation_count": 45,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Manfaatkan Air AC untuk Tanaman",
            "description": "Tampung air dari AC untuk menyiram tanaman, mencuci motor, atau pel lantai.",
            "category": "general_savings",
            "difficulty_level": "easy",
            "potential_savings_percentage": 15.0,
            "implementation_time": "15 menit",
            "implementation_steps": [
                "Siapkan wadah penampung (ember atau jeriken)",
                "Letakkan di bawah pipa pembuangan AC",
                "Biarkan air tertampung",
                "Gunakan untuk menyiram tanaman atau pel lantai"
            ],
            "benefits": [
                "Manfaatkan air yang terbuang percuma",
                "Hemat air bersih",
                "Air AC cocok untuk tanaman (bebas klorin)"
            ],
            "required_tools": [
                "Ember atau jeriken",
                "Tidak perlu tools khusus"
            ],
            "status": "published",
            "view_count": 389,
            "like_count": 78,
            "bookmark_count": 52,
            "implementation_count": 28,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Cek dan Ganti Karet Seal Toilet",
            "description": "Toilet yang bocor bisa membuang hingga 200 liter air per hari. Ganti karet seal yang rusak.",
            "category": "leak_prevention",
            "difficulty_level": "medium",
            "potential_savings_percentage": 50.0,
            "implementation_time": "1 jam",
            "implementation_steps": [
                "Matikan supply air ke toilet",
                "Flush toilet untuk mengosongkan tangki",
                "Lepas tutup tangki toilet",
                "Ganti karet seal/flapper valve yang rusak",
                "Pasang kembali dan test"
            ],
            "benefits": [
                "Stop kebocoran air",
                "Hemat hingga 200L per hari",
                "Toilet lebih efisien"
            ],
            "required_tools": [
                "Karet seal/flapper valve baru (Rp 30.000 - 100.000)",
                "Obeng",
                "Kain lap"
            ],
            "status": "published",
            "view_count": 267,
            "like_count": 51,
            "bookmark_count": 35,
            "implementation_count": 15,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Siram Tanaman Pagi atau Sore",
            "description": "Waktu terbaik menyiram tanaman untuk mengurangi penguapan dan hemat air.",
            "category": "best_practices",
            "difficulty_level": "easy",
            "potential_savings_percentage": 20.0,
            "implementation_time": "Langsung",
            "implementation_steps": [
                "Ubah jadwal siram menjadi pagi (05:00-07:00) atau sore (17:00-19:00)",
                "Hindari siram siang hari (10:00-15:00)",
                "Siram di area akar, bukan daun",
                "Gunakan air secukupnya"
            ],
            "benefits": [
                "Hemat air 20-30%",
                "Tanaman lebih sehat",
                "Mengurangi penguapan"
            ],
            "required_tools": [
                "Tidak perlu tools khusus",
                "Jadwal alarm (optional)"
            ],
            "status": "published",
            "view_count": 445,
            "like_count": 91,
            "bookmark_count": 64,
            "implementation_count": 72,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
    ]
    
    await db.water_conservation_tips.insert_many(tips)
    print(f"   ✅ Seeded {len(tips)} water conservation tips")
    return tips

async def seed_water_usage():
    """Seed water usage data for last 30 days"""
    print("🔹 Seeding water usage data...")
    
    # Clear existing water usage
    await db.water_usage.delete_many({})
    
    devices = ["dev-001", "dev-002", "dev-003", "dev-004", "dev-005"]
    customers = ["cust-001", "cust-002", "cust-002", "cust-003", "cust-003"]
    
    usage_records = []
    
    # Generate 30 days of data for each device
    for day in range(30):
        date = datetime.utcnow() - timedelta(days=day)
        
        for idx, device_id in enumerate(devices):
            # Vary consumption by device type
            if idx == 0:  # Residential - low consumption
                base_consumption = random.uniform(0.8, 1.5)  # m³ per day
            elif idx == 1:  # Apartment - medium consumption
                base_consumption = random.uniform(1.0, 2.0)
            elif idx == 2:  # Office - medium-high consumption
                base_consumption = random.uniform(3.0, 5.0)
            elif idx == 3:  # Factory - high consumption
                base_consumption = random.uniform(10.0, 20.0)
            else:  # Hotel - very high consumption
                base_consumption = random.uniform(15.0, 30.0)
            
            # Add some randomness
            consumption = base_consumption * random.uniform(0.8, 1.2)
            
            # Calculate cost (Rp 10,000 per m³ - simplified)
            cost = consumption * 10000
            
            usage_record = {
                "id": str(uuid.uuid4()),
                "device_id": device_id,
                "customer_id": customers[idx],
                "reading_date": date.isoformat(),
                "water_consumed": round(consumption, 2),
                "cost": round(cost, 0),
                "reading_type": "automatic",
                "balance_before": None,
                "balance_after": None,
                "timestamp": date.isoformat()
            }
            
            usage_records.append(usage_record)
    
    await db.water_usage.insert_many(usage_records)
    print(f"   ✅ Seeded {len(usage_records)} water usage records")
    return usage_records

async def seed_transactions():
    """Seed payment transactions"""
    print("🔹 Seeding transactions...")
    
    # Clear existing transactions
    await db.transactions.delete_many({})
    
    now = datetime.utcnow()
    
    transactions = [
        {
            "id": str(uuid.uuid4()),
            "reference_id": f"TRX-{now.strftime('%Y%m%d')}-0001",
            "customer_id": "cust-001",
            "amount": 200000.0,
            "payment_method": "virtual_account",
            "payment_provider": "xendit",
            "status": "paid",
            "description": "Top-up saldo water meter",
            "created_at": (now - timedelta(days=5)).isoformat(),
            "paid_at": (now - timedelta(days=5)).isoformat(),
            "expires_at": None
        },
        {
            "id": str(uuid.uuid4()),
            "reference_id": f"TRX-{now.strftime('%Y%m%d')}-0002",
            "customer_id": "cust-002",
            "amount": 500000.0,
            "payment_method": "qris",
            "payment_provider": "midtrans",
            "status": "paid",
            "description": "Top-up saldo water meter",
            "created_at": (now - timedelta(days=3)).isoformat(),
            "paid_at": (now - timedelta(days=3)).isoformat(),
            "expires_at": None
        },
        {
            "id": str(uuid.uuid4()),
            "reference_id": f"TRX-{now.strftime('%Y%m%d')}-0003",
            "customer_id": "cust-002",
            "amount": 300000.0,
            "payment_method": "ewallet",
            "payment_provider": "xendit",
            "status": "paid",
            "description": "Top-up saldo water meter",
            "created_at": (now - timedelta(days=2)).isoformat(),
            "paid_at": (now - timedelta(days=2)).isoformat(),
            "expires_at": None
        },
        {
            "id": str(uuid.uuid4()),
            "reference_id": f"TRX-{now.strftime('%Y%m%d')}-0004",
            "customer_id": "cust-003",
            "amount": 1000000.0,
            "payment_method": "virtual_account",
            "payment_provider": "midtrans",
            "status": "paid",
            "description": "Top-up saldo water meter - Factory",
            "created_at": (now - timedelta(days=7)).isoformat(),
            "paid_at": (now - timedelta(days=7)).isoformat(),
            "expires_at": None
        },
        {
            "id": str(uuid.uuid4()),
            "reference_id": f"TRX-{now.strftime('%Y%m%d')}-0005",
            "customer_id": "cust-003",
            "amount": 800000.0,
            "payment_method": "qris",
            "payment_provider": "xendit",
            "status": "pending",
            "description": "Top-up saldo water meter - Hotel",
            "created_at": (now - timedelta(hours=2)).isoformat(),
            "paid_at": None,
            "expires_at": (now + timedelta(hours=22)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "reference_id": f"TRX-{now.strftime('%Y%m%d')}-0006",
            "customer_id": "cust-001",
            "amount": 150000.0,
            "payment_method": "virtual_account",
            "payment_provider": "midtrans",
            "status": "failed",
            "description": "Top-up saldo water meter",
            "created_at": (now - timedelta(days=1)).isoformat(),
            "paid_at": None,
            "expires_at": (now - timedelta(hours=1)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "reference_id": f"TRX-{now.strftime('%Y%m%d')}-0007",
            "customer_id": "cust-002",
            "amount": 400000.0,
            "payment_method": "ewallet",
            "payment_provider": "xendit",
            "status": "expired",
            "description": "Top-up saldo water meter",
            "created_at": (now - timedelta(days=2)).isoformat(),
            "paid_at": None,
            "expires_at": (now - timedelta(days=1)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "reference_id": f"TRX-{now.strftime('%Y%m%d')}-0008",
            "customer_id": "cust-001",
            "amount": 250000.0,
            "payment_method": "qris",
            "payment_provider": "midtrans",
            "status": "paid",
            "description": "Top-up saldo water meter",
            "created_at": (now - timedelta(hours=6)).isoformat(),
            "paid_at": (now - timedelta(hours=6)).isoformat(),
            "expires_at": None
        }
    ]
    
    await db.transactions.insert_many(transactions)
    print(f"   ✅ Seeded {len(transactions)} transactions")
    return transactions

async def seed_device_alerts():
    """Seed device alerts"""
    print("🔹 Seeding device alerts...")
    
    # Clear existing alerts
    await db.device_alerts.delete_many({})
    
    now = datetime.utcnow()
    
    alerts = [
        {
            "id": str(uuid.uuid4()),
            "device_id": "dev-001",
            "alert_type": "low_balance",
            "message": "Low balance: Rp 250,000. Please top-up soon.",
            "severity": "warning",
            "is_resolved": False,
            "timestamp": (now - timedelta(hours=12)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "device_id": "dev-002",
            "alert_type": "low_battery",
            "message": "Battery level low: 72%. Replace battery soon.",
            "severity": "info",
            "is_resolved": False,
            "timestamp": (now - timedelta(hours=24)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "device_id": "dev-003",
            "alert_type": "maintenance_due",
            "message": "Scheduled maintenance due in 3 days",
            "severity": "info",
            "is_resolved": False,
            "timestamp": (now - timedelta(hours=6)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "device_id": "dev-004",
            "alert_type": "high_consumption",
            "message": "Unusually high water consumption detected",
            "severity": "warning",
            "is_resolved": True,
            "timestamp": (now - timedelta(days=2)).isoformat()
        }
    ]
    
    await db.device_alerts.insert_many(alerts)
    print(f"   ✅ Seeded {len(alerts)} device alerts")
    return alerts

async def seed_device_activities():
    """Seed device activities"""
    print("🔹 Seeding device activities...")
    
    # Clear existing activities
    await db.device_activities.delete_many({})
    
    now = datetime.utcnow()
    
    activities = [
        {
            "id": str(uuid.uuid4()),
            "device_id": "dev-001",
            "activity_type": "installation",
            "title": "Device Installed",
            "description": "Water meter installed at Rumah Residence A",
            "performed_by": "tech-001",
            "timestamp": (now - timedelta(days=180)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "device_id": "dev-001",
            "activity_type": "maintenance",
            "title": "Routine Maintenance",
            "description": "6-month routine maintenance check completed",
            "performed_by": "tech-001",
            "timestamp": (now - timedelta(days=30)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "device_id": "dev-002",
            "activity_type": "installation",
            "title": "Device Installed",
            "description": "Water meter installed at Apartment Central Park",
            "performed_by": "tech-002",
            "timestamp": (now - timedelta(days=150)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "device_id": "dev-003",
            "activity_type": "installation",
            "title": "Device Installed",
            "description": "Water meter installed at Office Building XYZ",
            "performed_by": "tech-001",
            "timestamp": (now - timedelta(days=120)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "device_id": "dev-004",
            "activity_type": "installation",
            "title": "Device Installed",
            "description": "Water meter installed at Factory ABC",
            "performed_by": "tech-002",
            "timestamp": (now - timedelta(days=200)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "device_id": "dev-005",
            "activity_type": "installation",
            "title": "Device Installed",
            "description": "Water meter installed at Hotel Grand Pacific",
            "performed_by": "tech-001",
            "timestamp": (now - timedelta(days=90)).isoformat()
        }
    ]
    
    await db.device_activities.insert_many(activities)
    print(f"   ✅ Seeded {len(activities)} device activities")
    return activities

async def main():
    """Main seeding function"""
    print("\n" + "="*60)
    print("🌊 IndoWater - Comprehensive Database Seeding")
    print("="*60 + "\n")
    
    try:
        # Seed all collections
        await seed_users()
        await seed_properties()
        await seed_devices()
        await seed_vouchers()
        await seed_support_tickets()
        await seed_water_tips()
        await seed_water_usage()
        await seed_transactions()
        await seed_device_alerts()
        await seed_device_activities()
        
        # Print summary
        print("\n" + "="*60)
        print("✅ Database Seeding Complete!")
        print("="*60)
        print("\n📊 Summary:")
        print(f"   • Users: 6 (1 admin, 2 technicians, 3 customers)")
        print(f"   • Properties: 5")
        print(f"   • Devices: 6")
        print(f"   • Vouchers: 6")
        print(f"   • Support Tickets: 6")
        print(f"   • Water Conservation Tips: 8")
        print(f"   • Water Usage Records: 150")
        print(f"   • Transactions: 8")
        print(f"   • Device Alerts: 4")
        print(f"   • Device Activities: 6")
        print("\n🔐 Demo Credentials:")
        print("   Admin: admin@indowater.com / admin123")
        print("   Technician: technician@indowater.com / tech123")
        print("   Customer: customer@indowater.com / customer123")
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())
