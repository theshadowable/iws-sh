"""
Role and Permission Management Models
Handles user roles, permissions, and access control
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Permission Categories
class PermissionCategory:
    DASHBOARD = "dashboard"
    USERS = "users"
    CUSTOMERS = "customers"
    DEVICES = "devices"
    IOT = "iot"
    ANALYTICS = "analytics"
    PAYMENTS = "payments"
    VOUCHERS = "vouchers"
    REPORTS = "reports"
    PROPERTIES = "properties"
    ALERTS = "alerts"
    SETTINGS = "settings"
    TICKETS = "tickets"
    TIPS = "tips"

# Permission Actions
class PermissionAction:
    VIEW = "view"
    CREATE = "create"
    EDIT = "edit"
    DELETE = "delete"
    MANAGE = "manage"

# Permission Model
class Permission(BaseModel):
    id: str
    name: str
    category: str
    action: str
    description: str

# Role Model
class Role(BaseModel):
    id: str
    name: str  # e.g., "admin", "technician", "customer", "manager", "viewer"
    display_name: str
    description: str
    permissions: List[str] = []  # List of permission IDs
    is_system_role: bool = False  # System roles cannot be deleted
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# User Role Assignment
class UserRoleAssignment(BaseModel):
    user_id: str
    role_id: str
    custom_permissions: List[str] = []  # Additional permissions beyond role
    assigned_by: str
    assigned_at: datetime = Field(default_factory=datetime.now)

# Request Models
class CreateRoleRequest(BaseModel):
    name: str
    display_name: str
    description: str
    permissions: List[str]

class UpdateRoleRequest(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None

class AssignRoleRequest(BaseModel):
    user_id: str
    role_id: str
    custom_permissions: Optional[List[str]] = []

class UpdateUserPermissionsRequest(BaseModel):
    user_id: str
    custom_permissions: List[str]

# Response Models
class RoleWithPermissions(BaseModel):
    id: str
    name: str
    display_name: str
    description: str
    permissions: List[Permission]
    is_system_role: bool
    user_count: int = 0
    created_at: datetime
    updated_at: datetime

class UserWithRoleAndPermissions(BaseModel):
    id: str
    email: str
    full_name: str
    role: Role
    custom_permissions: List[Permission] = []
    all_permissions: List[str] = []  # Combined role + custom permissions

# Default System Permissions
DEFAULT_PERMISSIONS = [
    # Dashboard
    Permission(id="dashboard.view", name="View Dashboard", category="dashboard", action="view", description="Access to dashboard"),
    
    # Users
    Permission(id="users.view", name="View Users", category="users", action="view", description="View user list"),
    Permission(id="users.create", name="Create Users", category="users", action="create", description="Create new users"),
    Permission(id="users.edit", name="Edit Users", category="users", action="edit", description="Edit user details"),
    Permission(id="users.delete", name="Delete Users", category="users", action="delete", description="Delete users"),
    Permission(id="users.manage", name="Manage Users", category="users", action="manage", description="Full user management"),
    
    # Customers
    Permission(id="customers.view", name="View Customers", category="customers", action="view", description="View customer list"),
    Permission(id="customers.create", name="Create Customers", category="customers", action="create", description="Create new customers"),
    Permission(id="customers.edit", name="Edit Customers", category="customers", action="edit", description="Edit customer details"),
    Permission(id="customers.delete", name="Delete Customers", category="customers", action="delete", description="Delete customers"),
    
    # Devices
    Permission(id="devices.view", name="View Devices", category="devices", action="view", description="View device list"),
    Permission(id="devices.create", name="Create Devices", category="devices", action="create", description="Register new devices"),
    Permission(id="devices.edit", name="Edit Devices", category="devices", action="edit", description="Edit device details"),
    Permission(id="devices.delete", name="Delete Devices", category="devices", action="delete", description="Delete devices"),
    
    # IoT
    Permission(id="iot.view", name="View IoT Monitoring", category="iot", action="view", description="View IoT device monitoring"),
    Permission(id="iot.manage", name="Manage IoT", category="iot", action="manage", description="Manage IoT devices and data"),
    
    # Analytics
    Permission(id="analytics.view", name="View Analytics", category="analytics", action="view", description="View analytics and reports"),
    Permission(id="analytics.export", name="Export Reports", category="analytics", action="manage", description="Export PDF/Excel reports"),
    
    # Payments
    Permission(id="payments.view", name="View Payments", category="payments", action="view", description="View payment transactions"),
    Permission(id="payments.manage", name="Manage Payments", category="payments", action="manage", description="Manage payment settings"),
    
    # Vouchers
    Permission(id="vouchers.view", name="View Vouchers", category="vouchers", action="view", description="View vouchers"),
    Permission(id="vouchers.create", name="Create Vouchers", category="vouchers", action="create", description="Create vouchers"),
    Permission(id="vouchers.edit", name="Edit Vouchers", category="vouchers", action="edit", description="Edit vouchers"),
    Permission(id="vouchers.delete", name="Delete Vouchers", category="vouchers", action="delete", description="Delete vouchers"),
    
    # Properties
    Permission(id="properties.view", name="View Properties", category="properties", action="view", description="View properties"),
    Permission(id="properties.create", name="Create Properties", category="properties", action="create", description="Create properties"),
    Permission(id="properties.edit", name="Edit Properties", category="properties", action="edit", description="Edit properties"),
    Permission(id="properties.delete", name="Delete Properties", category="properties", action="delete", description="Delete properties"),
    
    # Alerts
    Permission(id="alerts.view", name="View Alerts", category="alerts", action="view", description="View alerts and notifications"),
    Permission(id="alerts.manage", name="Manage Alerts", category="alerts", action="manage", description="Manage alert settings"),
    
    # Support Tickets
    Permission(id="tickets.view", name="View Tickets", category="tickets", action="view", description="View support tickets"),
    Permission(id="tickets.create", name="Create Tickets", category="tickets", action="create", description="Create support tickets"),
    Permission(id="tickets.edit", name="Edit Tickets", category="tickets", action="edit", description="Edit support tickets"),
    Permission(id="tickets.delete", name="Delete Tickets", category="tickets", action="delete", description="Delete support tickets"),
    Permission(id="tickets.assign", name="Assign Tickets", category="tickets", action="manage", description="Assign tickets to technicians"),
    Permission(id="tickets.reply", name="Reply to Tickets", category="tickets", action="manage", description="Reply to ticket messages"),
    Permission(id="tickets.approve", name="Approve Tickets", category="tickets", action="manage", description="Approve maintenance/repair tickets"),
    Permission(id="tickets.manage", name="Manage Tickets", category="tickets", action="manage", description="Full ticket management access"),
    
    # Water Conservation Tips
    Permission(id="tips.view", name="View Tips", category="tips", action="view", description="View water conservation tips"),
    Permission(id="tips.create", name="Create Tips", category="tips", action="create", description="Create water conservation tips"),
    Permission(id="tips.edit", name="Edit Tips", category="tips", action="edit", description="Edit water conservation tips"),
    Permission(id="tips.delete", name="Delete Tips", category="tips", action="delete", description="Delete water conservation tips"),
    Permission(id="tips.manage", name="Manage Tips", category="tips", action="manage", description="Full tips management access"),
    
    # Settings
    Permission(id="settings.view", name="View Settings", category="settings", action="view", description="View system settings"),
    Permission(id="settings.manage", name="Manage Settings", category="settings", action="manage", description="Manage system settings"),
]

# Default System Roles
DEFAULT_ROLES = {
    "admin": {
        "display_name": "Administrator",
        "description": "Full system access with all permissions",
        "permissions": [p.id for p in DEFAULT_PERMISSIONS],
        "is_system_role": True
    },
    "technician": {
        "display_name": "Technician",
        "description": "Field technician with device and customer access",
        "permissions": [
            "dashboard.view",
            "customers.view",
            "customers.edit",
            "devices.view",
            "devices.edit",
            "iot.view",
            "iot.manage",
            "properties.view",
            "properties.edit",
            "alerts.view",
            "tickets.view",
            "tickets.create",
            "tickets.edit",
            "tickets.reply",
            "tips.view"
        ],
        "is_system_role": True
    },
    "customer": {
        "display_name": "Customer",
        "description": "End customer with limited access",
        "permissions": [
            "dashboard.view",
            "analytics.view",
            "payments.view",
            "alerts.view",
            "tickets.view",
            "tickets.create",
            "tips.view"
        ],
        "is_system_role": True
    }
}
