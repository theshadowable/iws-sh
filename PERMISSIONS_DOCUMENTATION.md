# Roles & Permissions System - IndoWater Application

## Overview
Sistem Roles & Permissions yang komprehensif untuk mengatur akses pengguna ke berbagai fitur aplikasi IndoWater.

## Total Permissions: 45

### Permission Categories (14 Categories)

#### 1. Dashboard (1 permission)
- `dashboard.view` - View Dashboard

#### 2. Users (5 permissions)
- `users.view` - View Users
- `users.create` - Create Users
- `users.edit` - Edit Users
- `users.delete` - Delete Users
- `users.manage` - Manage Users

#### 3. Customers (4 permissions)
- `customers.view` - View Customers
- `customers.create` - Create Customers
- `customers.edit` - Edit Customers
- `customers.delete` - Delete Customers

#### 4. Devices (4 permissions)
- `devices.view` - View Devices
- `devices.create` - Create Devices
- `devices.edit` - Edit Devices
- `devices.delete` - Delete Devices

#### 5. IoT (2 permissions)
- `iot.view` - View IoT Monitoring
- `iot.manage` - Manage IoT

#### 6. Analytics (2 permissions)
- `analytics.view` - View Analytics
- `analytics.export` - Export Reports

#### 7. Payments (2 permissions)
- `payments.view` - View Payments
- `payments.manage` - Manage Payments

#### 8. Vouchers (4 permissions)
- `vouchers.view` - View Vouchers
- `vouchers.create` - Create Vouchers
- `vouchers.edit` - Edit Vouchers
- `vouchers.delete` - Delete Vouchers

#### 9. Properties (4 permissions)
- `properties.view` - View Properties
- `properties.create` - Create Properties
- `properties.edit` - Edit Properties
- `properties.delete` - Delete Properties

#### 10. Alerts (2 permissions)
- `alerts.view` - View Alerts
- `alerts.manage` - Manage Alerts

#### 11. Support Tickets (8 permissions) 🆕
- `tickets.view` - View support tickets
- `tickets.create` - Create support tickets
- `tickets.edit` - Edit support tickets
- `tickets.delete` - Delete support tickets
- `tickets.assign` - Assign tickets to technicians
- `tickets.reply` - Reply to ticket messages
- `tickets.approve` - Approve maintenance/repair tickets
- `tickets.manage` - Full ticket management access

#### 12. Water Conservation Tips (5 permissions) 🆕
- `tips.view` - View water conservation tips
- `tips.create` - Create water conservation tips
- `tips.edit` - Edit water conservation tips
- `tips.delete` - Delete water conservation tips
- `tips.manage` - Full tips management access

#### 13. Reports (Included in Analytics)
- Reports functionality is part of analytics permissions

#### 14. Settings (2 permissions)
- `settings.view` - View Settings
- `settings.manage` - Manage Settings

---

## System Roles (3 Default Roles)

### 1. Administrator (admin)
**Full system access with all permissions**

**Total Permissions**: 45 (ALL)

**Access to**:
- ✅ Full Dashboard Access
- ✅ Complete User Management (view, create, edit, delete, manage)
- ✅ Complete Customer Management
- ✅ Complete Device Management
- ✅ IoT Monitoring & Management
- ✅ Analytics & Report Export
- ✅ Payment Management
- ✅ Voucher Management
- ✅ Property Management
- ✅ Alert Management
- ✅ **Full Support Tickets Management** (view, create, edit, delete, assign, reply, approve, manage)
- ✅ **Full Water Tips Management** (view, create, edit, delete, manage)
- ✅ System Settings Management

**Navigation Access**:
- Dashboard
- Users
- Roles & Access
- Customers
- Properties
- Devices
- IoT Monitoring
- **Support Tickets** 🆕
- **Water Tips** 🆕
- Vouchers
- Payment Settings
- Analytics

---

### 2. Technician (technician)
**Field technician with device and customer access**

**Total Permissions**: 15

**Access to**:
- ✅ Dashboard View
- ✅ View & Edit Customers
- ✅ View & Edit Devices
- ✅ IoT Monitoring & Management
- ✅ View & Edit Properties
- ✅ View Alerts
- ✅ **View, Create, Edit, Reply to Support Tickets** 🆕
- ✅ **View Water Conservation Tips** 🆕

**Detailed Permissions**:
```
dashboard.view
customers.view
customers.edit
devices.view
devices.edit
iot.view
iot.manage
properties.view
properties.edit
alerts.view
tickets.view
tickets.create
tickets.edit
tickets.reply
tips.view
```

**Navigation Access**:
- Dashboard
- Work Orders
- Task Map
- Meter Reading
- Customers
- Properties
- Devices
- IoT Monitoring
- Support Tickets (can view, create, edit, reply)
- Water Tips (view only)

**Ticket Workflow**:
- Can view all tickets
- Can create new tickets
- Can edit ticket details
- Can reply to ticket messages
- Can attach photos/documents with GPS metadata
- **Cannot assign tickets to other technicians**
- **Cannot approve maintenance tickets** (Admin only)

---

### 3. Customer (customer)
**End customer with limited access**

**Total Permissions**: 7

**Access to**:
- ✅ Dashboard View
- ✅ Analytics View
- ✅ View Payments
- ✅ View Alerts
- ✅ **View & Create Support Tickets** 🆕
- ✅ **View Water Conservation Tips** 🆕

**Detailed Permissions**:
```
dashboard.view
analytics.view
payments.view
alerts.view
tickets.view
tickets.create
tips.view
```

**Navigation Access**:
- Dashboard
- My Devices
- Analytics
- Top-Up Balance
- Purchase History
- Transactions
- Support Tickets (can view own tickets, create new)
- Water Tips (view only)

**Ticket Workflow**:
- Can view only their own tickets
- Can create new support tickets
- Can view ticket messages
- Can attach files to their tickets
- **Cannot edit tickets after creation**
- **Cannot delete tickets**
- **Cannot reply to messages** (only admin/technician can reply)

---

## Permission Implementation

### Backend Implementation
**Location**: `/app/backend/role_permission_models.py`

**Key Components**:
1. `PermissionCategory` - Defines 14 permission categories
2. `PermissionAction` - Defines action types (view, create, edit, delete, manage)
3. `Permission` - Permission model
4. `Role` - Role model with permissions list
5. `DEFAULT_PERMISSIONS` - List of all 45 system permissions
6. `DEFAULT_ROLES` - Configuration for 3 system roles

### Database Collections
1. **permissions** - Stores all permission definitions
2. **roles** - Stores role configurations
3. **users** - User collection with role field

### Seeding Script
**Location**: `/app/backend/seed_permissions.py`

**Run Command**:
```bash
cd /app/backend && python seed_permissions.py
```

**What it does**:
- Creates/updates all 45 permissions in database
- Creates/updates 3 system roles (admin, technician, customer)
- Shows detailed breakdown of permissions by role
- Non-destructive (updates existing, creates new)

---

## How to Use

### For Developers

#### 1. Check User Permission in Backend
```python
from auth import get_current_user

@router.get("/admin/tickets")
async def get_admin_tickets(current_user = Depends(get_current_user)):
    # Check if user has permission
    if current_user.role != "admin" and "tickets.manage" not in current_user.permissions:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Proceed with logic
    ...
```

#### 2. Protect Routes by Role
```python
@router.post("/tickets/{ticket_id}/assign")
async def assign_ticket(
    ticket_id: str,
    current_user = Depends(get_current_user)
):
    # Only admin and technicians can assign
    if current_user.role not in ["admin", "technician"]:
        raise HTTPException(status_code=403, detail="Access denied")
    ...
```

#### 3. Frontend Route Protection
```javascript
// In App.js
<Route
  path="/admin/tickets"
  element={
    <ProtectedRoute allowedRoles={['admin']}>
      <AdminTickets />
    </ProtectedRoute>
  }
/>
```

### For Administrators

#### 1. View All Roles & Permissions
- Navigate to **Roles & Access** page
- View all system roles
- See permissions grouped by category

#### 2. Create Custom Role
- Click "Create Role" button
- Enter role name and description
- Select permissions by category
- Save role

#### 3. Assign Role to User
- Go to Users page or Roles & Access page
- Click "Assign Role" for a user
- Select role from dropdown
- Optional: Add custom permissions
- Save assignment

#### 4. Modify Role Permissions
- Go to Roles & Access page
- Click "Edit" on a role
- Add/remove permissions
- Save changes
- **Note**: System roles (admin, technician, customer) have protected base permissions

---

## Permission Naming Convention

Format: `{category}.{action}`

**Examples**:
- `dashboard.view`
- `tickets.create`
- `tickets.manage`
- `tips.edit`
- `users.delete`

**Actions**:
- `view` - Read-only access
- `create` - Create new records
- `edit` - Modify existing records
- `delete` - Delete records
- `manage` - Full control (includes view, create, edit, delete)

---

## Special Permission Notes

### Support Tickets Permissions

1. **tickets.view**
   - All roles can view tickets
   - Admin/Technician: See all tickets
   - Customer: See only their own tickets

2. **tickets.assign**
   - Admin only permission
   - Assign tickets to technicians
   - Change ticket assignment

3. **tickets.approve**
   - Admin only permission
   - Required for maintenance_repairs category tickets
   - Verify photos, documents, digital signature before approval

4. **tickets.manage**
   - Admin only permission
   - Full control over ticket system
   - Access to admin ticket management page

### Water Tips Permissions

1. **tips.view**
   - All roles can view tips
   - Access to tips listing and detail

2. **tips.create, tips.edit, tips.delete**
   - Admin only permissions
   - Full CRUD operations on tips

3. **tips.manage**
   - Admin only permission
   - Access to admin tips management page
   - Full control over tips system

---

## Migration Guide

### Update Existing Users
If you have existing users in your system, run this script to update their permissions:

```python
# Update existing users with new role permissions
async def update_user_permissions():
    users = await db.users.find().to_list(length=1000)
    
    for user in users:
        role = user.get('role')
        if role in DEFAULT_ROLES:
            # Update user with new permissions from their role
            await db.users.update_one(
                {'id': user['id']},
                {'$set': {'permissions': DEFAULT_ROLES[role]['permissions']}}
            )
```

### Re-initialize Permissions
To update all permissions and roles in database:
```bash
cd /app/backend && python seed_permissions.py
```

This is safe to run multiple times - it will update existing and create new permissions.

---

## Testing

### Test Permission System
1. Login as **Admin** - Should see all navigation items including Support Tickets and Water Tips
2. Login as **Technician** - Should see limited navigation, can access tickets but not tips management
3. Login as **Customer** - Should see minimal navigation, can create tickets but cannot manage

### Test Ticket Permissions
1. **Admin**: Create, view, edit, delete, assign, approve tickets
2. **Technician**: Create, view, edit, reply to tickets
3. **Customer**: Create and view own tickets only

### Test Tips Permissions
1. **Admin**: Full CRUD on tips
2. **Technician**: View tips only
3. **Customer**: View tips only

---

## Troubleshooting

### Issue: User can't access feature despite correct role
**Solution**: Re-seed permissions
```bash
cd /app/backend && python seed_permissions.py
```

### Issue: Navigation items not showing
**Solution**: Check Layout.js role-based navigation configuration

### Issue: API returns 403 Forbidden
**Solution**: 
1. Verify user has correct role
2. Check backend route permission requirements
3. Ensure user permissions are up to date

---

## Future Enhancements

Potential additions to permission system:
1. **Custom Permission Creation** - Allow admins to create custom permissions
2. **Permission Groups** - Group related permissions for easier management
3. **Time-based Permissions** - Permissions that expire after certain time
4. **Location-based Permissions** - Permissions based on user location
5. **Audit Log** - Track permission changes and usage
6. **Permission Inheritance** - Child roles inherit parent permissions

---

## Summary

✅ **45 Total Permissions** across 14 categories
✅ **3 System Roles** (Admin, Technician, Customer)
✅ **8 Support Ticket Permissions** (view, create, edit, delete, assign, reply, approve, manage)
✅ **5 Water Tips Permissions** (view, create, edit, delete, manage)
✅ **Role-based Access Control** implemented across all features
✅ **Database Seeded** with all permissions and roles
✅ **Frontend Navigation** updated with proper role checks
✅ **Backend API** protected with permission checks

The permission system is now complete and ready for production use! 🚀
