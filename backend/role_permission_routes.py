"""
Role and Permission Management API Routes
Admin endpoints for managing roles, permissions, and user access
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
import os
from pymongo import MongoClient

from auth import get_current_user, User
from role_permission_models import (
    Permission, Role, CreateRoleRequest, UpdateRoleRequest,
    AssignRoleRequest, UpdateUserPermissionsRequest,
    RoleWithPermissions, UserWithRoleAndPermissions,
    DEFAULT_PERMISSIONS, DEFAULT_ROLES
)

router = APIRouter(prefix="/api/roles", tags=["Role & Permission Management"])

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'indowater')
client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Helper function to check admin access
def require_admin(current_user: User):
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

# Initialize default permissions and roles
@router.post("/initialize", status_code=status.HTTP_201_CREATED)
async def initialize_roles_and_permissions(current_user: User = Depends(get_current_user)):
    """Initialize default permissions and roles (Admin only)"""
    require_admin(current_user)
    
    # Insert default permissions
    permissions_collection = db['permissions']
    existing_perms = permissions_collection.count_documents({})
    
    if existing_perms == 0:
        permissions_collection.insert_many([p.dict() for p in DEFAULT_PERMISSIONS])
    
    # Insert default roles
    roles_collection = db['roles']
    for role_id, role_data in DEFAULT_ROLES.items():
        existing_role = roles_collection.find_one({"id": role_id})
        if not existing_role:
            role = {
                "id": role_id,
                "name": role_id,
                **role_data,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            roles_collection.insert_one(role)
    
    return {
        "message": "Roles and permissions initialized successfully",
        "permissions_count": len(DEFAULT_PERMISSIONS),
        "roles_count": len(DEFAULT_ROLES)
    }

# GET all permissions
@router.get("/permissions", response_model=List[Permission])
async def get_all_permissions(current_user: User = Depends(get_current_user)):
    """Get all available permissions"""
    require_admin(current_user)
    
    permissions_collection = db['permissions']
    permissions = list(permissions_collection.find({}, {'_id': 0}))
    
    if not permissions:
        # Return default permissions if none exist
        return DEFAULT_PERMISSIONS
    
    return permissions

# GET all roles
@router.get("/list", response_model=List[RoleWithPermissions])
async def get_all_roles(current_user: User = Depends(get_current_user)):
    """Get all roles with their permissions"""
    require_admin(current_user)
    
    roles_collection = db['roles']
    permissions_collection = db['permissions']
    users_collection = db['users']
    
    roles = list(roles_collection.find({}, {'_id': 0}))
    
    result = []
    for role in roles:
        # Get permission details
        perm_ids = role.get('permissions', [])
        perms = list(permissions_collection.find({"id": {"$in": perm_ids}}, {'_id': 0}))
        
        # Count users with this role
        user_count = users_collection.count_documents({"role": role['id']})
        
        result.append({
            **role,
            "permissions": perms,
            "user_count": user_count
        })
    
    return result

# GET specific role by ID
@router.get("/{role_id}", response_model=RoleWithPermissions)
async def get_role_by_id(role_id: str, current_user: User = Depends(get_current_user)):
    """Get specific role details"""
    require_admin(current_user)
    
    roles_collection = db['roles']
    permissions_collection = db['permissions']
    users_collection = db['users']
    
    role = roles_collection.find_one({"id": role_id}, {'_id': 0})
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Get permission details
    perm_ids = role.get('permissions', [])
    perms = list(permissions_collection.find({"id": {"$in": perm_ids}}, {'_id': 0}))
    
    # Count users with this role
    user_count = users_collection.count_documents({"role": role_id})
    
    return {
        **role,
        "permissions": perms,
        "user_count": user_count
    }

# CREATE new role
@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_role(
    request: CreateRoleRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new custom role"""
    require_admin(current_user)
    
    roles_collection = db['roles']
    
    # Check if role already exists
    existing = roles_collection.find_one({"name": request.name})
    if existing:
        raise HTTPException(status_code=400, detail="Role with this name already exists")
    
    # Create role
    role_id = f"custom_{request.name.lower().replace(' ', '_')}"
    new_role = {
        "id": role_id,
        "name": request.name,
        "display_name": request.display_name,
        "description": request.description,
        "permissions": request.permissions,
        "is_system_role": False,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    roles_collection.insert_one(new_role)
    
    return {"message": "Role created successfully", "role_id": role_id}

# UPDATE role
@router.patch("/{role_id}")
async def update_role(
    role_id: str,
    request: UpdateRoleRequest,
    current_user: User = Depends(get_current_user)
):
    """Update role details and permissions"""
    require_admin(current_user)
    
    roles_collection = db['roles']
    
    # Check if role exists
    role = roles_collection.find_one({"id": role_id})
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Prevent editing system roles (optional - you can remove this)
    if role.get('is_system_role') and role_id in ['admin', 'technician', 'customer']:
        raise HTTPException(status_code=400, detail="Cannot modify system roles")
    
    # Prepare update data
    update_data = {"updated_at": datetime.now()}
    if request.display_name is not None:
        update_data["display_name"] = request.display_name
    if request.description is not None:
        update_data["description"] = request.description
    if request.permissions is not None:
        update_data["permissions"] = request.permissions
    
    roles_collection.update_one(
        {"id": role_id},
        {"$set": update_data}
    )
    
    return {"message": "Role updated successfully"}

# DELETE role
@router.delete("/{role_id}")
async def delete_role(role_id: str, current_user: User = Depends(get_current_user)):
    """Delete a custom role (cannot delete system roles)"""
    require_admin(current_user)
    
    roles_collection = db['roles']
    users_collection = db['users']
    
    # Check if role exists
    role = roles_collection.find_one({"id": role_id})
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Prevent deleting system roles
    if role.get('is_system_role'):
        raise HTTPException(status_code=400, detail="Cannot delete system roles")
    
    # Check if any users have this role
    user_count = users_collection.count_documents({"role": role_id})
    if user_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete role: {user_count} user(s) still assigned to this role"
        )
    
    roles_collection.delete_one({"id": role_id})
    
    return {"message": "Role deleted successfully"}

# ASSIGN role to user
@router.post("/assign")
async def assign_role_to_user(
    request: AssignRoleRequest,
    current_user: User = Depends(get_current_user)
):
    """Assign a role to a user"""
    require_admin(current_user)
    
    users_collection = db['users']
    roles_collection = db['roles']
    
    # Check if user exists
    user = users_collection.find_one({"id": request.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if role exists
    role = roles_collection.find_one({"id": request.role_id})
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Update user role
    users_collection.update_one(
        {"id": request.user_id},
        {
            "$set": {
                "role": request.role_id,
                "updated_at": datetime.now()
            }
        }
    )
    
    return {"message": f"Role '{role['display_name']}' assigned to user successfully"}

# GET users with their roles and permissions
@router.get("/users/detailed", response_model=List[UserWithRoleAndPermissions])
async def get_users_with_roles(current_user: User = Depends(get_current_user)):
    """Get all users with their roles and permissions"""
    require_admin(current_user)
    
    users_collection = db['users']
    roles_collection = db['roles']
    permissions_collection = db['permissions']
    
    users = list(users_collection.find({}, {'_id': 0, 'hashed_password': 0}))
    
    result = []
    for user in users:
        role_id = user.get('role', 'customer')
        role = roles_collection.find_one({"id": role_id}, {'_id': 0})
        
        if not role:
            # Default role if not found
            role = {
                "id": "customer",
                "name": "customer",
                "display_name": "Customer",
                "description": "Default role",
                "permissions": [],
                "is_system_role": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        
        # Get all permissions for this role
        all_perm_ids = role.get('permissions', [])
        
        result.append({
            "id": user['id'],
            "email": user['email'],
            "full_name": user['full_name'],
            "role": role,
            "custom_permissions": [],
            "all_permissions": all_perm_ids
        })
    
    return result
