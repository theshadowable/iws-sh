"""
Comprehensive Seed Script for IndoWater Application
Seeds all required demo data: users, properties, devices, vouchers, tickets, tips, etc.
"""

import asyncio
import os
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import uuid
import random

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB connection
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017/indowater')

def get_password_hash(password):
    return pwd_context.hash(password)

async def seed_all_data():
    """Seed comprehensive demo data for all collections"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.get_default_database()
    
    print("🌱 Starting comprehensive data seeding...\n")
    
    # ============================================
    # 1. SEED USERS (Admin, Technicians, Customers)
    # ============================================
    print("👥 Seeding users...")
    users_collection = db['users']
    await users_collection.delete_many({})  # Clear existing
    
    demo_users = [
        {
            'id': str(uuid.uuid4()),
            'email': 'admin@indowater.com',
            'full_name': 'Admin User',
            'hashed_password': get_password_hash('admin123'),
            'role': 'admin',
            'is_active': True,
            'created_at': datetime.utcnow()
        },
        {
            'id': str(uuid.uuid4()),
            'email': 'technician@indowater.com',
            'full_name': 'Technician User',
            'hashed_password': get_password_hash('tech123'),
            'role': 'technician',
            'is_active': True,
            'created_at': datetime.utcnow()
        },
        {
            'id': str(uuid.uuid4()),
            'email': 'customer@indowater.com',
            'full_name': 'Customer User',
            'hashed_password': get_password_hash('customer123'),
            'role': 'customer',
            'is_active': True,
            'created_at': datetime.utcnow()
        },
        {
            'id': str(uuid.uuid4()),
            'email': 'technician2@indowater.com',
            'full_name': 'Budi Santoso',
            'hashed_password': get_password_hash('tech123'),
            'role': 'technician',
            'is_active': True,
            'created_at': datetime.utcnow()
        },
        {
            'id': str(uuid.uuid4()),
            'email': 'customer2@indowater.com',
            'full_name': 'Siti Nurhaliza',
            'hashed_password': get_password_hash('customer123'),
            'role': 'customer',
            'is_active': True,
            'created_at': datetime.utcnow()
        },
        {
            'id': str(uuid.uuid4()),
            'email': 'customer3@indowater.com',
            'full_name': 'Ahmad Rahman',
            'hashed_password': get_password_hash('customer123'),
            'role': 'customer',
            'is_active': True,
            'created_at': datetime.utcnow()
        }
    ]
    
    await users_collection.insert_many(demo_users)
    print(f"✅ Created {len(demo_users)} users")
    
    # Get user IDs for reference
    admin_user = demo_users[0]
    tech1_user = demo_users[1]
    tech2_user = demo_users[3]
    customer1_user = demo_users[2]
    customer2_user = demo_users[4]
    customer3_user = demo_users[5]
    
    # ============================================
    # 2. SEED PROPERTIES
    # ============================================
    print("\n🏢 Seeding properties...")
    properties_collection = db['properties']
    await properties_collection.delete_many({})
    
    demo_properties = [
        {
            'id': str(uuid.uuid4()),
            'property_type': 'residential',
            'address': 'Jl. Sudirman No. 123, Jakarta Pusat',
            'city': 'Jakarta',
            'postal_code': '10110',
            'customer_id': customer1_user['id'],
            'customer_name': customer1_user['full_name'],
            'status': 'active',
            'created_at': datetime.utcnow()
        },
        {
            'id': str(uuid.uuid4()),
            'property_type': 'commercial',
            'address': 'Jl. Thamrin No. 45, Jakarta Pusat',
            'city': 'Jakarta',
            'postal_code': '10350',
            'customer_id': customer2_user['id'],
            'customer_name': customer2_user['full_name'],
            'status': 'active',
            'created_at': datetime.utcnow()
        },
        {
            'id': str(uuid.uuid4()),
            'property_type': 'industrial',
            'address': 'Jl. Raya Bogor KM 27, Cibinong',
            'city': 'Bogor',
            'postal_code': '16914',
            'customer_id': customer3_user['id'],
            'customer_name': customer3_user['full_name'],
            'status': 'active',
            'created_at': datetime.utcnow()
        },
        {
            'id': str(uuid.uuid4()),
            'property_type': 'residential',
            'address': 'Jl. Gatot Subroto No. 88, Bandung',
            'city': 'Bandung',
            'postal_code': '40262',
            'customer_id': customer1_user['id'],
            'customer_name': customer1_user['full_name'],
            'status': 'active',
            'created_at': datetime.utcnow()
        }
    ]
    
    await properties_collection.insert_many(demo_properties)
    print(f"✅ Created {len(demo_properties)} properties")
    
    # ============================================
    # 3. SEED DEVICES
    # ============================================
    print("\n📟 Seeding devices...")
    devices_collection = db['devices']
    await devices_collection.delete_many({})
    
    demo_devices = [
        {
            'id': str(uuid.uuid4()),
            'device_id': 'WM-2024-001',
            'device_type': 'smart_meter',
            'property_id': demo_properties[0]['id'],
            'customer_id': customer1_user['id'],
            'status': 'active',
            'last_reading': 1234.56,
            'installation_date': datetime.utcnow() - timedelta(days=180),
            'created_at': datetime.utcnow()
        },
        {
            'id': str(uuid.uuid4()),
            'device_id': 'WM-2024-002',
            'device_type': 'smart_meter',
            'property_id': demo_properties[1]['id'],
            'customer_id': customer2_user['id'],
            'status': 'active',
            'last_reading': 5678.90,
            'installation_date': datetime.utcnow() - timedelta(days=150),
            'created_at': datetime.utcnow()
        },
        {
            'id': str(uuid.uuid4()),
            'device_id': 'WM-2024-003',
            'device_type': 'smart_meter',
            'property_id': demo_properties[2]['id'],
            'customer_id': customer3_user['id'],
            'status': 'active',
            'last_reading': 9876.54,
            'installation_date': datetime.utcnow() - timedelta(days=200),
            'created_at': datetime.utcnow()
        },
        {
            'id': str(uuid.uuid4()),
            'device_id': 'WM-2024-004',
            'device_type': 'smart_meter',
            'property_id': demo_properties[3]['id'],
            'customer_id': customer1_user['id'],
            'status': 'maintenance',
            'last_reading': 456.78,
            'installation_date': datetime.utcnow() - timedelta(days=90),
            'created_at': datetime.utcnow()
        }
    ]
    
    await devices_collection.insert_many(demo_devices)
    print(f"✅ Created {len(demo_devices)} devices")
    
    # ============================================
    # 4. SEED VOUCHERS
    # ============================================
    print("\n🎟️ Seeding vouchers...")
    vouchers_collection = db['vouchers']
    await vouchers_collection.delete_many({})
    
    now = datetime.utcnow()
    demo_vouchers = [
        {
            'id': str(uuid.uuid4()),
            'code': 'WELCOME50',
            'description': 'Welcome bonus 50% discount for new customers',
            'discount_type': 'percentage',
            'discount_value': 50,
            'min_purchase_amount': 100000,
            'max_discount_amount': 150000,
            'usage_limit': 100,
            'per_customer_limit': 1,
            'usage_count': 25,
            'status': 'active',
            'valid_from': now - timedelta(days=30),
            'valid_until': now + timedelta(days=60),
            'created_by': admin_user['id'],
            'created_at': now - timedelta(days=30)
        },
        {
            'id': str(uuid.uuid4()),
            'code': 'HEMAT20',
            'description': 'Hemat 20% untuk pembelian minimum Rp 200.000',
            'discount_type': 'percentage',
            'discount_value': 20,
            'min_purchase_amount': 200000,
            'max_discount_amount': 100000,
            'usage_limit': 200,
            'per_customer_limit': 2,
            'usage_count': 78,
            'status': 'active',
            'valid_from': now - timedelta(days=15),
            'valid_until': now + timedelta(days=45),
            'created_by': admin_user['id'],
            'created_at': now - timedelta(days=15)
        },
        {
            'id': str(uuid.uuid4()),
            'code': 'FLASH100K',
            'description': 'Flash sale - Potongan Rp 100.000',
            'discount_type': 'fixed_amount',
            'discount_value': 100000,
            'min_purchase_amount': 500000,
            'max_discount_amount': None,
            'usage_limit': 50,
            'per_customer_limit': 1,
            'usage_count': 45,
            'status': 'active',
            'valid_from': now - timedelta(days=7),
            'valid_until': now + timedelta(days=7),
            'created_by': admin_user['id'],
            'created_at': now - timedelta(days=7)
        },
        {
            'id': str(uuid.uuid4()),
            'code': 'NEWYEAR2025',
            'description': 'New Year Special - 25% discount',
            'discount_type': 'percentage',
            'discount_value': 25,
            'min_purchase_amount': 150000,
            'max_discount_amount': 200000,
            'usage_limit': 500,
            'per_customer_limit': 3,
            'usage_count': 12,
            'status': 'active',
            'valid_from': now - timedelta(days=5),
            'valid_until': now + timedelta(days=90),
            'created_by': admin_user['id'],
            'created_at': now - timedelta(days=5)
        }
    ]
    
    await vouchers_collection.insert_many(demo_vouchers)
    print(f"✅ Created {len(demo_vouchers)} vouchers")
    
    # ============================================
    # 5. SEED SUPPORT TICKETS
    # ============================================
    print("\n🎫 Seeding support tickets...")
    tickets_collection = db['support_tickets']
    await tickets_collection.delete_many({})
    
    demo_tickets = [
        {
            'id': str(uuid.uuid4()),
            'ticket_number': 'TKT-2024-001',
            'subject': 'Water meter showing incorrect reading',
            'description': 'The water meter at my property is showing unusually high readings. Please check.',
            'category': 'technical_issue',
            'priority': 'high',
            'status': 'open',
            'customer_id': customer1_user['id'],
            'customer_name': customer1_user['full_name'],
            'customer_email': customer1_user['email'],
            'assigned_to': None,
            'assigned_to_name': None,
            'created_at': now - timedelta(days=2),
            'updated_at': now - timedelta(days=2),
            'attachments': []
        },
        {
            'id': str(uuid.uuid4()),
            'ticket_number': 'TKT-2024-002',
            'subject': 'Water quality concern',
            'description': 'Water has a slight discoloration. Is it safe to drink?',
            'category': 'water_quality',
            'priority': 'medium',
            'status': 'in_progress',
            'customer_id': customer2_user['id'],
            'customer_name': customer2_user['full_name'],
            'customer_email': customer2_user['email'],
            'assigned_to': tech1_user['id'],
            'assigned_to_name': tech1_user['full_name'],
            'created_at': now - timedelta(days=5),
            'updated_at': now - timedelta(days=1),
            'attachments': []
        },
        {
            'id': str(uuid.uuid4()),
            'ticket_number': 'TKT-2024-003',
            'subject': 'Pipe leak at main connection',
            'description': 'There is a leak at the main water connection. Need immediate repair.',
            'category': 'maintenance_repairs',
            'priority': 'critical',
            'status': 'resolved',
            'customer_id': customer3_user['id'],
            'customer_name': customer3_user['full_name'],
            'customer_email': customer3_user['email'],
            'assigned_to': tech2_user['id'],
            'assigned_to_name': tech2_user['full_name'],
            'created_at': now - timedelta(days=7),
            'updated_at': now - timedelta(hours=12),
            'attachments': []
        },
        {
            'id': str(uuid.uuid4()),
            'ticket_number': 'TKT-2024-004',
            'subject': 'Billing inquiry',
            'description': 'I have a question about my last month bill. It seems higher than usual.',
            'category': 'general_inquiry',
            'priority': 'low',
            'status': 'open',
            'customer_id': customer1_user['id'],
            'customer_name': customer1_user['full_name'],
            'customer_email': customer1_user['email'],
            'assigned_to': None,
            'assigned_to_name': None,
            'created_at': now - timedelta(hours=6),
            'updated_at': now - timedelta(hours=6),
            'attachments': []
        }
    ]
    
    await tickets_collection.insert_many(demo_tickets)
    print(f"✅ Created {len(demo_tickets)} support tickets")
    
    # ============================================
    # 6. SEED WATER CONSERVATION TIPS
    # ============================================
    print("\n💡 Seeding water conservation tips...")
    tips_collection = db['water_conservation_tips']
    await tips_collection.delete_many({})
    
    demo_tips = [
        {
            'id': str(uuid.uuid4()),
            'title': 'Fix Leaky Faucets Immediately',
            'description': 'A dripping faucet can waste up to 20 liters of water per day. Check all faucets regularly and fix leaks promptly.',
            'category': 'leak_prevention',
            'difficulty_level': 'easy',
            'potential_savings_percentage': 15.0,
            'implementation_time': '30 minutes',
            'tags': ['maintenance', 'leaks', 'DIY'],
            'is_active': True,
            'view_count': 245,
            'like_count': 89,
            'implementation_count': 34,
            'created_by': admin_user['id'],
            'created_at': now - timedelta(days=60),
            'updated_at': now - timedelta(days=60)
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Install Low-Flow Showerheads',
            'description': 'Low-flow showerheads can reduce water usage by up to 50% without compromising water pressure.',
            'category': 'best_practices',
            'difficulty_level': 'easy',
            'potential_savings_percentage': 40.0,
            'implementation_time': '20 minutes',
            'tags': ['efficiency', 'bathroom', 'upgrade'],
            'is_active': True,
            'view_count': 312,
            'like_count': 156,
            'implementation_count': 67,
            'created_by': admin_user['id'],
            'created_at': now - timedelta(days=45),
            'updated_at': now - timedelta(days=45)
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Collect Rainwater for Garden',
            'description': 'Install a rainwater collection system to water your garden instead of using tap water.',
            'category': 'general_savings',
            'difficulty_level': 'medium',
            'potential_savings_percentage': 30.0,
            'implementation_time': '2 hours',
            'tags': ['garden', 'rainwater', 'outdoor'],
            'is_active': True,
            'view_count': 187,
            'like_count': 72,
            'implementation_count': 23,
            'created_by': admin_user['id'],
            'created_at': now - timedelta(days=30),
            'updated_at': now - timedelta(days=30)
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Use Dishwasher Efficiently',
            'description': 'Run dishwasher only when full and use eco mode to save water and energy.',
            'category': 'best_practices',
            'difficulty_level': 'easy',
            'potential_savings_percentage': 25.0,
            'implementation_time': '5 minutes',
            'tags': ['kitchen', 'appliances', 'habits'],
            'is_active': True,
            'view_count': 423,
            'like_count': 201,
            'implementation_count': 178,
            'created_by': admin_user['id'],
            'created_at': now - timedelta(days=20),
            'updated_at': now - timedelta(days=20)
        }
    ]
    
    await tips_collection.insert_many(demo_tips)
    print(f"✅ Created {len(demo_tips)} water conservation tips")
    
    # ============================================
    # 7. SEED WATER USAGE DATA
    # ============================================
    print("\n💧 Seeding water usage data...")
    usage_collection = db['water_usage']
    await usage_collection.delete_many({})
    
    usage_records = []
    for device in demo_devices[:3]:  # Only for first 3 devices
        # Generate 30 days of data
        for days_ago in range(30, 0, -1):
            reading_date = now - timedelta(days=days_ago)
            
            # Different consumption patterns
            if device['device_type'] == 'smart_meter':
                base_consumption = random.uniform(0.5, 2.5)  # Residential
            else:
                base_consumption = random.uniform(5.0, 15.0)  # Commercial/Industrial
                
            usage_records.append({
                'id': str(uuid.uuid4()),
                'device_id': device['id'],
                'customer_id': device['customer_id'],
                'reading_date': reading_date,
                'consumption_liters': base_consumption * 1000,  # Convert to liters
                'cost': base_consumption * 10000,  # IDR 10,000 per m³
                'created_at': reading_date
            })
    
    if usage_records:
        await usage_collection.insert_many(usage_records)
    print(f"✅ Created {len(usage_records)} water usage records")
    
    # ============================================
    # 8. SEED PAYMENT TRANSACTIONS
    # ============================================
    print("\n💳 Seeding payment transactions...")
    payments_collection = db['payment_transactions']
    await payments_collection.delete_many({})
    
    payment_statuses = ['paid', 'paid', 'paid', 'pending', 'failed']
    payment_methods = ['virtual_account', 'qris', 'ewallet']
    
    demo_payments = []
    for i in range(5):
        demo_payments.append({
            'id': str(uuid.uuid4()),
            'reference_id': f'PAY-{now.strftime("%Y%m%d")}-{str(i+1).zfill(4)}',
            'customer_id': random.choice([customer1_user['id'], customer2_user['id'], customer3_user['id']]),
            'amount': random.choice([100000, 200000, 500000, 1000000]),
            'payment_method': random.choice(payment_methods),
            'status': payment_statuses[i],
            'created_at': now - timedelta(days=random.randint(1, 30)),
            'updated_at': now - timedelta(days=random.randint(0, 15))
        })
    
    await payments_collection.insert_many(demo_payments)
    print(f"✅ Created {len(demo_payments)} payment transactions")
    
    # ============================================
    # SUMMARY
    # ============================================
    print("\n" + "="*50)
    print("🎉 SEED COMPLETED SUCCESSFULLY!")
    print("="*50)
    print("\n📊 Data Summary:")
    print(f"  • Users: {len(demo_users)}")
    print(f"  • Properties: {len(demo_properties)}")
    print(f"  • Devices: {len(demo_devices)}")
    print(f"  • Vouchers: {len(demo_vouchers)}")
    print(f"  • Support Tickets: {len(demo_tickets)}")
    print(f"  • Water Conservation Tips: {len(demo_tips)}")
    print(f"  • Water Usage Records: {len(usage_records)}")
    print(f"  • Payment Transactions: {len(demo_payments)}")
    
    print("\n🔐 Login Credentials:")
    print("  Admin:")
    print("    Email: admin@indowater.com")
    print("    Password: admin123")
    print("\n  Technician:")
    print("    Email: technician@indowater.com")
    print("    Password: tech123")
    print("\n  Customer:")
    print("    Email: customer@indowater.com")
    print("    Password: customer123")
    
    print("\n✨ All demo data has been seeded successfully!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_all_data())
