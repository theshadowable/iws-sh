# Seed Script Documentation - IndoWater Application

## 📋 Overview

Script `seed_comprehensive_data.py` adalah comprehensive seeding tool yang mengisi database dengan data demo lengkap untuk testing dan demo purposes.

## 🎯 Purpose

Script ini akan:
- ✅ Clear semua data existing di collections yang akan di-seed
- ✅ Create fresh demo data dengan relationships yang valid
- ✅ Seed data realistis dengan patterns yang natural
- ✅ Provide complete demo environment untuk testing

## 📦 What Gets Seeded

### 1. **Users (6 accounts)**
```
Admin Account:
  Email: admin@indowater.com
  Password: admin123
  Role: admin

Technician Accounts (2):
  Email: technician@indowater.com / technician2@indowater.com
  Password: tech123
  Role: technician

Customer Accounts (3):
  Email: customer@indowater.com / customer2@indowater.com / customer3@indowater.com
  Password: customer123
  Role: customer
```

### 2. **Properties (4 locations)**
- Residential: Jl. Sudirman No. 123, Jakarta Pusat
- Commercial: Jl. Thamrin No. 45, Jakarta Pusat
- Industrial: Jl. Raya Bogor KM 27, Cibinong
- Residential: Jl. Gatot Subroto No. 88, Bandung

### 3. **Devices (4 smart meters)**
- WM-2024-001 (Active)
- WM-2024-002 (Active)
- WM-2024-003 (Active)
- WM-2024-004 (Maintenance)

### 4. **Vouchers (4 promotional codes)**
```
WELCOME50:
  - 50% discount
  - Min purchase: Rp 100,000
  - Max discount: Rp 150,000
  - Usage: 25/100

HEMAT20:
  - 20% discount
  - Min purchase: Rp 200,000
  - Max discount: Rp 100,000
  - Usage: 78/200

FLASH100K:
  - Fixed Rp 100,000 discount
  - Min purchase: Rp 500,000
  - Usage: 45/50

NEWYEAR2025:
  - 25% discount
  - Min purchase: Rp 150,000
  - Max discount: Rp 200,000
  - Usage: 12/500
```

### 5. **Support Tickets (4 tickets)**
- Technical Issue (High priority, Open)
- Water Quality (Medium priority, In Progress, Assigned)
- Maintenance Repair (Critical priority, Resolved)
- General Inquiry (Low priority, Open)

### 6. **Water Conservation Tips (4 tips)**
- Fix Leaky Faucets (Easy, 15% savings, 245 views)
- Install Low-Flow Showerheads (Easy, 40% savings, 312 views)
- Collect Rainwater for Garden (Medium, 30% savings, 187 views)
- Use Dishwasher Efficiently (Easy, 25% savings, 423 views)

### 7. **Water Usage Records (90 records)**
- 30 days of historical data
- 3 active devices
- Realistic consumption patterns
- Daily readings with costs

### 8. **Payment Transactions (5 transactions)**
- Mix of paid, pending, and failed statuses
- Various payment methods (VA, QRIS, E-wallet)
- Different amounts (Rp 100K - Rp 1M)

## 🚀 How to Run

### Prerequisites
```bash
# Make sure MongoDB is running
# Make sure you're in the backend directory
cd /app/backend
```

### Run the Script
```bash
python seed_comprehensive_data.py
```

### Expected Output
```
🌱 Starting comprehensive data seeding...

👥 Seeding users...
✅ Created 6 users

🏢 Seeding properties...
✅ Created 4 properties

📟 Seeding devices...
✅ Created 4 devices

🎟️ Seeding vouchers...
✅ Created 4 vouchers

🎫 Seeding support tickets...
✅ Created 4 support tickets

💡 Seeding water conservation tips...
✅ Created 4 water conservation tips

💧 Seeding water usage data...
✅ Created 90 water usage records

💳 Seeding payment transactions...
✅ Created 5 payment transactions

==================================================
🎉 SEED COMPLETED SUCCESSFULLY!
==================================================

📊 Data Summary:
  • Users: 6
  • Properties: 4
  • Devices: 4
  • Vouchers: 4
  • Support Tickets: 4
  • Water Conservation Tips: 4
  • Water Usage Records: 90
  • Payment Transactions: 5

✨ All demo data has been seeded successfully!
```

## ⚠️ Important Notes

### 🔴 **DESTRUCTIVE OPERATION**
This script will:
- ❌ DELETE all existing data in seeded collections
- ✅ CREATE fresh demo data

**Collections affected:**
- `users`
- `properties`
- `devices`
- `vouchers`
- `support_tickets`
- `water_conservation_tips`
- `water_usage`
- `payment_transactions`

### 🔒 **Not Affected**
Collections NOT touched by this script:
- `roles` (role permission system)
- `permissions` (permission definitions)
- `iot_devices` (IoT device registrations)
- `work_orders` (technician tasks)
- Other custom collections

## 🧪 When to Use

### ✅ **Good Use Cases:**
- 🆕 Setting up fresh development environment
- 🧪 Testing new features with realistic data
- 🎨 Demo presentations
- 🔄 Resetting development database
- 📚 Training and onboarding new developers

### ❌ **DO NOT Use:**
- 🚫 In production environment
- 🚫 When you have important test data
- 🚫 In shared development environments without team notification
- 🚫 When other developers are actively testing

## 🔧 Customization

### Adding More Data
To seed more data, edit the script and modify the arrays:

```python
# Example: Add more users
demo_users = [
    # ... existing users ...
    {
        'id': str(uuid.uuid4()),
        'email': 'newuser@indowater.com',
        'full_name': 'New User Name',
        'hashed_password': get_password_hash('password'),
        'role': 'customer',
        'is_active': True,
        'created_at': datetime.utcnow()
    }
]
```

### Changing Password
All demo accounts use simple passwords for testing. To change:

```python
'hashed_password': get_password_hash('your_new_password')
```

### Adjusting Quantities
To change number of records:

```python
# Water usage - change 30 to desired days
for days_ago in range(30, 0, -1):  # Change 30 here
    # ...
```

## 📝 Verification

After running the script, verify data in MongoDB:

```bash
# Connect to MongoDB
mongosh indowater

# Check collections
db.users.countDocuments()  # Should be 6
db.vouchers.countDocuments()  # Should be 4
db.support_tickets.countDocuments()  # Should be 4
db.water_conservation_tips.countDocuments()  # Should be 4

# View sample data
db.users.find().limit(1).pretty()
db.vouchers.find().limit(1).pretty()
```

Or test in application:
1. Login with admin account
2. Navigate to Users page (should show 6 users)
3. Navigate to Vouchers page (should show 4 vouchers)
4. Navigate to Support Tickets (should show 4 tickets)
5. Navigate to Water Tips Management (should show 4 tips)

## 🐛 Troubleshooting

### Script Fails to Connect to MongoDB
```bash
# Check if MongoDB is running
sudo systemctl status mongod

# Check MongoDB URL in environment
echo $MONGO_URL

# Verify connection string format
# Should be: mongodb://localhost:27017/indowater
```

### Module Not Found Errors
```bash
# Install required dependencies
cd /app/backend
pip install -r requirements.txt
```

### Permission Errors
```bash
# Run with proper permissions
python seed_comprehensive_data.py
```

## 🔄 Related Scripts

- `seed_demo_users.py` - Seeds only users (3 users)
- `seed_water_usage.py` - Seeds only water usage data
- `seed_iot_devices.py` - Seeds IoT devices with sample readings
- `seed_permissions.py` - Seeds role permission system

## 📚 Additional Resources

- See `CHANGELOG_FIXES.md` for recent changes
- See `DATABASE_SCHEMA.md` for collection structures
- See `PERMISSIONS_DOCUMENTATION.md` for role/permission details

## 🎓 Best Practices

1. ✅ **Always backup** production data before running any seed script
2. ✅ **Run in development** environment first
3. ✅ **Notify team members** before seeding shared databases
4. ✅ **Verify results** after seeding
5. ✅ **Document custom changes** if you modify the script

## 📞 Support

If you encounter issues:
1. Check MongoDB connection
2. Verify environment variables
3. Check script output for specific errors
4. Review MongoDB logs
5. Contact development team

---

**Last Updated:** 2024  
**Script Version:** 1.0  
**Maintained By:** IndoWater Development Team
