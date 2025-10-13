# IndoWater Database Schema Documentation

## Database: `indowater_db` (MongoDB)

This document describes all collections and their schemas in the IndoWater water management system.

---

## Collections Overview

1. **users** - User accounts (customers, technicians, admins)
2. **properties** - Physical properties/buildings  
3. **devices** - Water meters and IoT devices
4. **water_usage** - Water consumption records
5. **work_orders** - Maintenance and service tasks
6. **meter_readings** - Manual meter reading records
7. **payment_transactions** - Payment history
8. **vouchers** - Discount vouchers
9. **voucher_usage** - Voucher redemption history
10. **alerts** - System alerts and notifications
11. **alert_preferences** - User alert settings
12. **leak_detection_events** - Leak detection records
13. **device_tampering_events** - Tampering detection records
14. **water_saving_tips** - Conservation tips
15. **budget_goals** - User budget targets
16. **notifications** - User notifications

---

## Detailed Schema Definitions

### 1. users

Stores user account information for customers, technicians, and administrators.

```javascript
{
  id: String,              // Unique user ID (e.g., "admin-001", "customer-001")
  email: String,           // Email address (unique)
  full_name: String,       // Full name
  hashed_password: String, // Bcrypt hashed password
  role: String,            // "admin", "technician", or "customer"
  phone: String,           // Phone number (optional)
  address: String,         // Physical address (optional)
  is_active: Boolean,      // Account status (true/false)
  created_at: DateTime,    // Account creation timestamp
  updated_at: DateTime     // Last update timestamp
}
```

**Indexes:**
- `{ email: 1 }` - Unique index
- `{ id: 1 }` - Unique index
- `{ role: 1 }` - For filtering by role

**Sample Data:**
```javascript
{
  id: "admin-001",
  email: "admin@indowater.com",
  full_name: "Admin User",
  role: "admin",
  is_active: true
}
```

---

### 2. properties

Physical properties or buildings where water meters are installed.

```javascript
{
  id: String,           // Unique property ID
  name: String,         // Property name
  address: String,      // Physical address
  customer_id: String,  // Reference to users.id
  property_type: String, // "residential", "commercial", "industrial"
  created_at: DateTime,
  updated_at: DateTime
}
```

**Indexes:**
- `{ id: 1 }` - Unique index
- `{ customer_id: 1 }` - For querying by customer

---

### 3. devices

Water meters and IoT devices installed at properties.

```javascript
{
  id: String,             // Unique device ID
  device_id: String,      // Physical device identifier
  property_id: String,    // Reference to properties.id
  customer_id: String,    // Reference to users.id
  type: String,           // "water_meter", "flow_sensor"
  status: String,         // "active", "inactive", "maintenance"
  location: String,       // Installation location description
  installation_date: DateTime,
  last_reading: Float,    // Last recorded reading (m³)
  last_reading_date: DateTime,
  calibration_date: DateTime, // Last calibration
  created_at: DateTime,
  updated_at: DateTime
}
```

**Indexes:**
- `{ id: 1 }` - Unique index
- `{ device_id: 1 }` - Unique index
- `{ customer_id: 1 }` - For querying by customer
- `{ property_id: 1 }` - For querying by property

---

### 4. water_usage

Daily water consumption records aggregated from device readings.

```javascript
{
  id: String,              // Unique record ID
  device_id: String,       // Reference to devices.id
  customer_id: String,     // Reference to users.id
  property_id: String,     // Reference to properties.id
  date: DateTime,          // Date of consumption
  consumption: Float,      // Water consumed (m³)
  cost: Float,             // Cost in IDR
  timestamp: DateTime,     // Record timestamp
  reading_type: String,    // "automatic", "manual"
  is_anomaly: Boolean,     // Detected anomaly flag
  created_at: DateTime
}
```

**Indexes:**
- `{ id: 1 }` - Unique index
- `{ customer_id: 1, date: -1 }` - For customer history queries
- `{ device_id: 1, date: -1 }` - For device history queries
- `{ date: -1 }` - For time-based queries

---

### 5. work_orders

Maintenance tasks and service requests for technicians.

```javascript
{
  id: String,              // Unique work order ID
  title: String,           // Task title
  description: String,     // Detailed description
  property_id: String,     // Reference to properties.id
  customer_id: String,     // Reference to users.id (customer)
  assigned_to: String,     // Reference to users.id (technician)
  priority: String,        // "low", "medium", "high", "urgent"
  status: String,          // "pending", "in_progress", "completed", "cancelled"
  scheduled_date: DateTime, // Scheduled completion date
  completed_date: DateTime, // Actual completion date
  notes: String,           // Technician notes
  created_at: DateTime,
  updated_at: DateTime
}
```

**Indexes:**
- `{ id: 1 }` - Unique index
- `{ assigned_to: 1, status: 1 }` - For technician task lists
- `{ customer_id: 1 }` - For customer work orders
- `{ status: 1, scheduled_date: 1 }` - For scheduling

---

### 6. meter_readings

Manual meter reading records submitted by technicians.

```javascript
{
  id: String,              // Unique reading ID
  work_order_id: String,   // Reference to work_orders.id
  device_id: String,       // Reference to devices.id
  reading_value: Float,    // Meter reading (m³)
  photo_url: String,       // Photo of meter (optional)
  ocr_text: String,        // OCR extracted text (optional)
  location: Object {       // GPS coordinates
    latitude: Float,
    longitude: Float
  },
  notes: String,           // Reading notes
  submitted_by: String,    // Reference to users.id (technician)
  submitted_at: DateTime,
  verified: Boolean,       // Admin verification flag
  created_at: DateTime
}
```

**Indexes:**
- `{ id: 1 }` - Unique index
- `{ device_id: 1, submitted_at: -1 }` - For device reading history
- `{ work_order_id: 1 }` - For work order readings

---

### 7. payment_transactions

Payment records for balance purchases and water bills.

```javascript
{
  id: String,              // Unique transaction ID
  reference_id: String,    // Payment gateway reference (unique)
  customer_id: String,     // Reference to users.id
  customer_email: String,  // Customer email
  amount: Float,           // Amount in IDR
  payment_method: String,  // "midtrans", "xendit", "manual"
  payment_type: String,    // "balance_topup", "water_bill"
  status: String,          // "pending", "paid", "failed", "expired"
  payment_url: String,     // Payment gateway URL (optional)
  voucher_code: String,    // Applied voucher (optional)
  discount_amount: Float,  // Discount applied (optional)
  metadata: Object,        // Additional payment data
  created_at: DateTime,
  updated_at: DateTime,
  paid_at: DateTime        // Payment completion timestamp
}
```

**Indexes:**
- `{ id: 1 }` - Unique index
- `{ reference_id: 1 }` - Unique index
- `{ customer_id: 1, created_at: -1 }` - For customer payment history
- `{ status: 1 }` - For status filtering

---

### 8. vouchers

Discount vouchers for promotional campaigns.

```javascript
{
  id: String,              // Unique voucher ID
  code: String,            // Voucher code (unique, uppercase)
  description: String,     // Voucher description
  discount_type: String,   // "percentage", "fixed_amount"
  discount_value: Float,   // Percentage (0-100) or amount in IDR
  min_purchase_amount: Float, // Minimum purchase required (IDR)
  max_discount_amount: Float, // Maximum discount cap (IDR, optional)
  usage_limit: Integer,    // Total usage limit (null = unlimited)
  usage_count: Integer,    // Current usage count
  per_customer_limit: Integer, // Usage limit per customer
  valid_from: DateTime,    // Validity start date
  valid_until: DateTime,   // Validity end date
  status: String,          // "active", "expired", "depleted", "inactive"
  created_by: String,      // Reference to users.id (admin)
  created_at: DateTime
}
```

**Indexes:**
- `{ id: 1 }` - Unique index
- `{ code: 1 }` - Unique index
- `{ status: 1, valid_until: 1 }` - For active voucher queries

---

### 9. voucher_usage

Voucher redemption history.

```javascript
{
  id: String,              // Unique usage ID
  voucher_id: String,      // Reference to vouchers.id
  voucher_code: String,    // Voucher code used
  customer_id: String,     // Reference to users.id
  customer_email: String,  // Customer email
  purchase_amount: Float,  // Original amount (IDR)
  discount_amount: Float,  // Discount applied (IDR)
  final_amount: Float,     // Final amount after discount (IDR)
  used_at: DateTime,       // Usage timestamp
  transaction_id: String   // Reference to payment_transactions.id (optional)
}
```

**Indexes:**
- `{ id: 1 }` - Unique index
- `{ voucher_id: 1 }` - For voucher usage tracking
- `{ customer_id: 1, used_at: -1 }` - For customer voucher history

---

### 10. alerts

System alerts and notifications for users.

```javascript
{
  id: String,              // Unique alert ID
  customer_id: String,     // Reference to users.id
  type: String,            // "leak_detected", "low_balance", "high_usage", "device_offline"
  severity: String,        // "low", "medium", "high", "critical"
  title: String,           // Alert title
  message: String,         // Alert message
  data: Object,            // Additional alert data
  status: String,          // "unread", "read", "acknowledged"
  created_at: DateTime,
  read_at: DateTime,       // Read timestamp (optional)
  acknowledged_at: DateTime // Acknowledged timestamp (optional)
}
```

**Indexes:**
- `{ id: 1 }` - Unique index
- `{ customer_id: 1, status: 1, created_at: -1 }` - For user alerts
- `{ type: 1, created_at: -1 }` - For alert type filtering

---

### 11. alert_preferences

User preferences for alert notifications.

```javascript
{
  id: String,              // Unique preference ID
  customer_id: String,     // Reference to users.id (unique)
  leak_alerts: Boolean,    // Enable leak detection alerts
  usage_alerts: Boolean,   // Enable high usage alerts
  balance_alerts: Boolean, // Enable low balance alerts
  device_alerts: Boolean,  // Enable device offline alerts
  email_notifications: Boolean,   // Enable email notifications
  push_notifications: Boolean,    // Enable push notifications
  threshold_usage: Float,  // Usage threshold for alerts (m³)
  threshold_balance: Float, // Balance threshold for alerts (IDR)
  created_at: DateTime,
  updated_at: DateTime
}
```

**Indexes:**
- `{ id: 1 }` - Unique index
- `{ customer_id: 1 }` - Unique index

---

### 12. leak_detection_events

Leak detection event records.

```javascript
{
  id: String,              // Unique event ID
  device_id: String,       // Reference to devices.id
  customer_id: String,     // Reference to users.id
  detected_at: DateTime,   // Detection timestamp
  flow_rate: Float,        // Flow rate at detection (L/min)
  duration_minutes: Float, // Continuous flow duration (minutes)
  estimated_loss: Float,   // Estimated water loss (m³)
  confidence: Float,       // Detection confidence (0-1)
  status: String,          // "active", "resolved", "false_positive"
  resolved_at: DateTime,   // Resolution timestamp (optional)
  notes: String            // Resolution notes (optional)
}
```

**Indexes:**
- `{ id: 1 }` - Unique index
- `{ customer_id: 1, detected_at: -1 }` - For customer leak history
- `{ device_id: 1, status: 1 }` - For device leak status

---

### 13. device_tampering_events

Device tampering detection records.

```javascript
{
  id: String,              // Unique event ID
  device_id: String,       // Reference to devices.id
  customer_id: String,     // Reference to users.id
  detected_at: DateTime,   // Detection timestamp
  tampering_type: String,  // "magnetic", "physical", "bypass"
  severity: String,        // "low", "medium", "high"
  description: String,     // Event description
  status: String,          // "active", "investigated", "resolved"
  investigated_by: String, // Reference to users.id (technician, optional)
  investigated_at: DateTime, // Investigation timestamp (optional)
  resolution: String       // Investigation resolution (optional)
}
```

**Indexes:**
- `{ id: 1 }` - Unique index
- `{ customer_id: 1, detected_at: -1 }` - For customer tampering history
- `{ device_id: 1, status: 1 }` - For device tampering status

---

### 14. water_saving_tips

Water conservation tips shown to users.

```javascript
{
  id: String,              // Unique tip ID
  title: String,           // Tip title
  description: String,     // Tip description
  category: String,        // "bathroom", "kitchen", "outdoor", "general"
  impact_level: String,    // "low", "medium", "high"
  estimated_savings: String, // Estimated savings description
  created_at: DateTime
}
```

**Indexes:**
- `{ id: 1 }` - Unique index
- `{ category: 1 }` - For filtering by category

---

### 15. budget_goals

User budget goals and targets.

```javascript
{
  id: String,              // Unique goal ID
  customer_id: String,     // Reference to users.id (unique)
  monthly_budget: Float,   // Monthly budget limit (IDR)
  monthly_usage_target: Float, // Monthly usage target (m³)
  start_date: DateTime,    // Goal start date
  end_date: DateTime,      // Goal end date (optional)
  current_spending: Float, // Current month spending (IDR)
  current_usage: Float,    // Current month usage (m³)
  alerts_enabled: Boolean, // Enable budget alerts
  created_at: DateTime,
  updated_at: DateTime
}
```

**Indexes:**
- `{ id: 1 }` - Unique index
- `{ customer_id: 1 }` - Unique index

---

### 16. notifications

User notification messages.

```javascript
{
  id: String,              // Unique notification ID
  user_id: String,         // Reference to users.id
  type: String,            // "info", "warning", "success", "error"
  title: String,           // Notification title
  message: String,         // Notification message
  link: String,            // Action link (optional)
  read: Boolean,           // Read status
  created_at: DateTime,
  read_at: DateTime        // Read timestamp (optional)
}
```

**Indexes:**
- `{ id: 1 }` - Unique index
- `{ user_id: 1, read: 1, created_at: -1 }` - For user notifications

---

## Database Connection

**MongoDB Connection String:**
```
MONGO_URL=mongodb://localhost:27017
```

**Database Name:**
```
DB_NAME=indowater_db
```

---

## Data Relationships

### User → Devices → Usage
```
users (customer)
  └─> properties (1:N)
       └─> devices (1:N)
            └─> water_usage (1:N)
            └─> meter_readings (1:N)
```

### Work Orders Flow
```
users (customer)
  └─> work_orders (1:N)
       ├─> assigned to users (technician)
       └─> meter_readings (1:N)
```

### Payment Flow
```
users (customer)
  └─> payment_transactions (1:N)
       └─> vouchers (N:1, optional)
            └─> voucher_usage (1:N)
```

### Alert System
```
users (customer)
  ├─> alerts (1:N)
  ├─> alert_preferences (1:1)
  ├─> leak_detection_events (1:N)
  └─> device_tampering_events (1:N)
```

---

## Seeding Scripts

The following seed scripts are available to populate the database with sample data:

1. **seed_demo_users.py** - Creates 3 demo accounts (admin, technician, customer)
2. **seed_water_usage.py** - Generates 6 months of water usage data
3. **seed_vouchers.py** - Creates sample vouchers (if exists)
4. **seed_payment_transactions.py** - Creates sample payment records (if exists)

---

## Backup and Maintenance

### Backup Command
```bash
mongodump --uri="mongodb://localhost:27017" --db=indowater_db --out=/backup/
```

### Restore Command
```bash
mongorestore --uri="mongodb://localhost:27017" --db=indowater_db /backup/indowater_db/
```

### Database Statistics
```javascript
db.stats()  // Get database statistics
db.collection.countDocuments()  // Count documents in collection
```

---

## Notes

- All timestamps are stored in UTC
- All monetary values are in Indonesian Rupiah (IDR)
- All water measurements are in cubic meters (m³)
- Passwords are hashed using bcrypt
- ObjectIDs are not used; custom string IDs are used instead for easier integration

---

**Last Updated:** October 13, 2025
**Version:** 1.0
