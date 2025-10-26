# IndoWater API Endpoints Documentation

## Base URL
- Development: `http://localhost:8001/api`
- Production: `https://your-domain.com/api`

## Authentication
All endpoints require JWT Bearer token authentication (except login/register).
```
Authorization: Bearer <access_token>
```

---

## 1. SUPPORT TICKETS API
**Base Path:** `/api/tickets`
**Router File:** `backend/support_routes.py`

### Endpoints:
- `POST /api/tickets/` - Create new support ticket
- `GET /api/tickets/` - List all tickets with filters (search, status, category, priority)
- `GET /api/tickets/{id}` - Get ticket detail
- `PUT /api/tickets/{id}` - Update ticket
- `DELETE /api/tickets/{id}` - Delete ticket
- `POST /api/tickets/{id}/messages` - Add message to ticket
- `GET /api/tickets/{id}/messages` - Get ticket messages
- `POST /api/tickets/{id}/attachments` - Upload attachment with GPS+timestamp
- `GET /api/tickets/{id}/attachments/{attachment_id}` - Download attachment
- `POST /api/tickets/{id}/signature` - Add digital signature
- `PATCH /api/tickets/{id}/assign` - Assign ticket to technician
- `PATCH /api/tickets/{id}/status` - Update ticket status
- `GET /api/tickets/admin/stats` - Get ticket statistics (Admin only)

### Example Response:
```json
{
  "tickets": [],
  "total": 0,
  "page": 1,
  "limit": 10,
  "has_more": false
}
```

---

## 2. WATER CONSERVATION TIPS API
**Base Path:** `/api/tips`
**Router File:** `backend/conservation_routes.py`

### Endpoints:
- `GET /api/tips/` - List tips with filters (category, difficulty, search)
- `GET /api/tips/{id}` - Get tip detail with engagement stats
- `POST /api/tips/{id}/engage` - Like/bookmark/implement tip
- `GET /api/tips/personalized` - Get personalized tips based on usage
- `POST /api/tips/admin/create` - Create new tip (Admin only)
- `PUT /api/tips/admin/{id}` - Update tip (Admin only)
- `DELETE /api/tips/admin/{id}` - Delete tip (Admin only)

### Example Response:
```json
{
  "tips": [],
  "total": 0,
  "page": 1,
  "limit": 20,
  "has_more": false
}
```

---

## 3. VOUCHERS API
**Base Path:** `/api/vouchers`
**Router File:** `backend/voucher_routes.py`

### Endpoints:
- `POST /api/vouchers/` - Create voucher (Admin only)
- `GET /api/vouchers/` - List all vouchers
- `GET /api/vouchers/active` - Get active vouchers only
- `POST /api/vouchers/validate` - Validate voucher code
- `POST /api/vouchers/apply` - Apply voucher to transaction
- `GET /api/vouchers/usage-history` - Get voucher usage history
- `PATCH /api/vouchers/{id}/status` - Update voucher status (Admin only)

### Example Response:
```json
[
  {
    "id": "uuid",
    "code": "WELCOME50",
    "discount_type": "percentage",
    "discount_value": 50,
    "status": "active",
    "usage_count": 10
  }
]
```

---

## 4. ALERT & NOTIFICATION API
**Base Path:** `/api/alerts`
**Router File:** `backend/alert_routes.py`

### Endpoints:
- `GET /api/alerts/` - Get all alerts for current user
- `GET /api/alerts/unread-count` - Get unread alert count
- `PATCH /api/alerts/{id}/status` - Mark alert as read
- `POST /api/alerts/mark-all-read` - Mark all alerts as read
- `GET /api/alerts/preferences` - Get alert preferences ✅ FIXED
- `PUT /api/alerts/preferences` - Update alert preferences
- `GET /api/alerts/leaks` - Get leak detection events
- `GET /api/alerts/tampering` - Get device tampering events
- `GET /api/alerts/tips` - Get water saving tips alerts

### Example Response (Preferences):
```json
{
  "id": "uuid",
  "customer_id": "admin-001",
  "low_balance_enabled": true,
  "low_balance_threshold": 50000.0,
  "leak_detection_enabled": true,
  "device_tampering_enabled": true,
  "maintenance_reminders_enabled": true,
  "payment_notifications_enabled": true,
  "email_notifications": true,
  "push_notifications": false,
  "updated_at": "2025-10-26T18:59:06.088000"
}
```

---

## 5. IOT DEVICE COMMUNICATION API
**Base Path:** `/api/iot`
**Router File:** `backend/iot_routes.py`

### Purpose: For IoT devices to communicate with server

### Endpoints:
- `POST /api/iot/register` - Register new IoT device
- `POST /api/iot/reading` - Submit water meter reading
- `GET /api/iot/{device_id}/command` - Get pending commands
- `POST /api/iot/{device_id}/command/ack` - Acknowledge command
- `POST /api/iot/{device_id}/send-command` - Send command to device (Admin)
- `GET /api/iot/health` - Health check endpoint

### Example Response (Health):
```json
{
  "status": "healthy",
  "service": "IoT Device Integration",
  "timestamp": "2025-10-26T18:59:57.678762"
}
```

---

## 6. DEVICE MANAGEMENT API
**Base Path:** `/api/devices`
**Router File:** `backend/device_routes.py`

### Purpose: For device CRUD operations and monitoring (NOT IoT communication)

### Endpoints:
- `GET /api/devices/comprehensive` - Get comprehensive device list with filters
- `GET /api/devices/{device_id}/stats` - Get device statistics
- `GET /api/devices/{device_id}/activities` - Get device activity logs
- `POST /api/devices/{device_id}/activities` - Create activity log
- `POST /api/devices/batch` - Batch operations (activate/deactivate/maintenance/delete)
- `GET /api/devices/summary/stats` - Get device summary statistics

### Example Response (Summary):
```json
{
  "total_devices": 4,
  "active_devices": 3,
  "inactive_devices": 0,
  "maintenance_devices": 0,
  "faulty_devices": 1,
  "online_devices": 3,
  "offline_devices": 1,
  "total_alerts": 0
}
```

---

## 7. ROLE & PERMISSION MANAGEMENT API
**Base Path:** `/api/roles`
**Router File:** `backend/role_permission_routes.py`

### Note: No root "/" endpoint available

### Endpoints:
- `POST /api/roles/initialize` - Initialize default permissions and roles (Admin only)
- `GET /api/roles/permissions` - List all permissions
- `GET /api/roles/list` - List all roles with permissions ✅ USE THIS
- `GET /api/roles/{role_id}` - Get role detail
- `POST /api/roles/create` - Create new role (Admin only)
- `PATCH /api/roles/{role_id}` - Update role (Admin only)
- `DELETE /api/roles/{role_id}` - Delete role (Admin only)
- `POST /api/roles/assign` - Assign role to user (Admin only)
- `GET /api/roles/users/detailed` - Get users with roles and permissions

### Example Response (List):
```json
[
  {
    "id": "admin",
    "name": "Administrator",
    "description": "Full system access",
    "permissions": ["users.view", "users.create", "..."]
  }
]
```

---

## 8. ANALYTICS API
**Base Path:** `/api/analytics`
**Router File:** `backend/analytics_routes.py`

### Endpoints:
- `GET /api/analytics/usage` - Get usage data with period filters
- `GET /api/analytics/trends` - Get consumption trends with growth rates
- `GET /api/analytics/predictions` - Get 7-day forecast
- `GET /api/analytics/comparison` - Compare two time periods
- `GET /api/analytics/admin/overview` - System-wide metrics (Admin only)

---

## 9. PAYMENT API
**Base Path:** `/api/payments`
**Router File:** `backend/payment_routes.py`

### Endpoints:
- `POST /api/payments/create` - Create new payment
- `GET /api/payments/history/list` - Get payment history with filters
- `GET /api/payments/{reference_id}` - Get payment detail
- `POST /api/payments/callback` - Payment gateway callback

---

## 10. CUSTOMER MANAGEMENT API
**Base Path:** `/api/customers`
**Router File:** `backend/customer_routes.py`

### Endpoints:
- `GET /api/customers/` - List all customers (Admin/Technician)
- `POST /api/customers/` - Create new customer (Admin/Technician)
- `GET /api/customers/{customer_id}` - Get customer detail
- `PUT /api/customers/{customer_id}` - Update customer
- `DELETE /api/customers/{customer_id}` - Delete customer
- `GET /api/customers/{customer_id}/devices` - Get customer devices
- `GET /api/customers/{customer_id}/usage` - Get customer usage data
- `GET /api/customers/{customer_id}/payments` - Get customer payments

---

## Common Query Parameters

### Pagination:
- `page` - Page number (default: 1)
- `limit` - Items per page (default: 20, max: 100)
- `skip` - Number of items to skip

### Filters:
- `search` - Search term
- `status` - Filter by status (active, inactive, etc.)
- `category` - Filter by category
- `sort_by` - Sort field (created_at, updated_at, etc.)
- `sort_order` - Sort direction (asc, desc)

### Date Filters:
- `start_date` - Filter from date (ISO format)
- `end_date` - Filter to date (ISO format)
- `period` - Time period (day, week, month, year)

---

## Error Responses

### 401 Unauthorized:
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden:
```json
{
  "detail": "Admin access required"
}
```

### 404 Not Found:
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error:
```json
{
  "detail": "Failed to process request: <error_message>"
}
```

---

## Testing Notes

### Demo Accounts:
```
Admin:
  Email: admin@indowater.com
  Password: admin123

Technician:
  Email: technician@indowater.com
  Password: tech123

Customer:
  Email: customer@indowater.com
  Password: customer123
```

### Login Example:
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@indowater.com","password":"admin123"}'
```

### Authenticated Request Example:
```bash
TOKEN="<your_access_token>"
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/api/tickets/
```

---

## Status Summary

✅ **Working & Verified:**
- Support Tickets API
- Water Conservation Tips API
- Vouchers API
- Alert & Notification API (Alert Preferences fixed)
- IoT Device Communication API
- Device Management API
- Role & Permission API
- Analytics API
- Payment API
- Customer Management API

⚠️ **Important Notes:**
1. All routes registered correctly in `backend/server.py`
2. `/api/iot/` for device communication, `/api/devices/` for device management
3. `/api/roles/` has no root endpoint, use `/api/roles/list` instead
4. Database requires seeding for testing (run seed scripts)
5. All endpoints require JWT authentication except `/api/auth/login` and `/api/auth/register`

---

**Last Updated:** October 26, 2025
**Version:** 1.0.0
