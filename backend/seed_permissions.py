#!/usr/bin/env python3
"""
Seed Permissions and Roles
This script initializes or updates the permissions and roles in the database
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from role_permission_models import DEFAULT_PERMISSIONS, DEFAULT_ROLES

async def seed_permissions():
    """Seed permissions and roles into database"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'indowater_db')]
    
    print("🔄 Starting permissions and roles seeding...")
    
    # 1. Seed Permissions
    print("\n📋 Seeding permissions...")
    permissions_collection = db.permissions
    
    # Clear existing permissions (optional - comment out if you want to keep existing)
    # await permissions_collection.delete_many({})
    
    for permission in DEFAULT_PERMISSIONS:
        perm_dict = permission.dict()
        
        # Check if permission already exists
        existing = await permissions_collection.find_one({"id": perm_dict['id']})
        
        if existing:
            # Update existing permission
            await permissions_collection.update_one(
                {"id": perm_dict['id']},
                {"$set": perm_dict}
            )
            print(f"  ✓ Updated permission: {perm_dict['id']} - {perm_dict['name']}")
        else:
            # Insert new permission
            await permissions_collection.insert_one(perm_dict)
            print(f"  ✓ Created permission: {perm_dict['id']} - {perm_dict['name']}")
    
    total_permissions = await permissions_collection.count_documents({})
    print(f"\n✅ Total permissions in database: {total_permissions}")
    
    # 2. Seed Roles
    print("\n👥 Seeding roles...")
    roles_collection = db.roles
    
    for role_id, role_data in DEFAULT_ROLES.items():
        role_dict = {
            "id": role_id,
            "name": role_id,
            "display_name": role_data["display_name"],
            "description": role_data["description"],
            "permissions": role_data["permissions"],
            "is_system_role": role_data["is_system_role"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Check if role already exists
        existing = await roles_collection.find_one({"id": role_id})
        
        if existing:
            # Update existing role (keep created_at, update permissions and other fields)
            await roles_collection.update_one(
                {"id": role_id},
                {
                    "$set": {
                        "display_name": role_dict["display_name"],
                        "description": role_dict["description"],
                        "permissions": role_dict["permissions"],
                        "is_system_role": role_dict["is_system_role"],
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            print(f"  ✓ Updated role: {role_dict['display_name']} ({len(role_dict['permissions'])} permissions)")
        else:
            # Insert new role
            await roles_collection.insert_one(role_dict)
            print(f"  ✓ Created role: {role_dict['display_name']} ({len(role_dict['permissions'])} permissions)")
    
    total_roles = await roles_collection.count_documents({})
    print(f"\n✅ Total roles in database: {total_roles}")
    
    # 3. Display Role Breakdown
    print("\n📊 Role Permissions Breakdown:")
    print("=" * 80)
    
    for role_id, role_data in DEFAULT_ROLES.items():
        print(f"\n🔹 {role_data['display_name']} ({role_id})")
        print(f"   Description: {role_data['description']}")
        print(f"   Permissions: {len(role_data['permissions'])}")
        
        # Group permissions by category
        perms_by_category = {}
        for perm_id in role_data['permissions']:
            category = perm_id.split('.')[0]
            if category not in perms_by_category:
                perms_by_category[category] = []
            perms_by_category[category].append(perm_id)
        
        print(f"   Categories:")
        for category, perms in sorted(perms_by_category.items()):
            print(f"     - {category.capitalize()}: {len(perms)} permissions")
    
    print("\n" + "=" * 80)
    print("✅ Permissions and roles seeding complete!")
    print("\n📝 Summary:")
    print(f"   Total Permissions: {total_permissions}")
    print(f"   Total Roles: {total_roles}")
    print(f"   System Roles: admin, technician, customer")
    
    # 4. Show new permissions added
    print("\n🆕 New Permissions Added:")
    print("   Support Tickets (8 permissions):")
    print("     - tickets.view, tickets.create, tickets.edit, tickets.delete")
    print("     - tickets.assign, tickets.reply, tickets.approve, tickets.manage")
    print("\n   Water Conservation Tips (5 permissions):")
    print("     - tips.view, tips.create, tips.edit, tips.delete, tips.manage")
    
    print("\n✨ Role Access Summary:")
    print("   Admin: Full access to all features (including tickets.manage, tips.manage)")
    print("   Technician: Can view, create, edit, reply to tickets + view tips")
    print("   Customer: Can view, create tickets + view tips")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_permissions())
