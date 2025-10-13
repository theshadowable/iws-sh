"""
Customer Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os

from auth import get_current_user, require_role, User, UserRole
from pydantic import BaseModel, Field

router = APIRouter(prefix="/customers", tags=["Customers"])

# Database connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'indowater_db')]


class BulkOperationRequest(BaseModel):
    customer_ids: List[str]


@router.get("/", response_model=List[User])
async def list_customers(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TECHNICIAN])),
    skip: int = 0,
    limit: int = 100
):
    """
    Get all customers (Admin and Technician access)
    """
    try:
        customers = await db.users.find(
            {"role": "customer"},
            {"_id": 0, "hashed_password": 0}
        ).skip(skip).limit(limit).to_list(limit)
        
        # Convert timestamp strings to datetime if needed
        for customer in customers:
            if isinstance(customer.get('created_at'), str):
                customer['created_at'] = datetime.fromisoformat(customer['created_at'])
            if isinstance(customer.get('updated_at'), str):
                customer['updated_at'] = datetime.fromisoformat(customer['updated_at'])
        
        return customers
    except Exception as e:
        print(f"Error fetching customers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch customers: {str(e)}"
        )


@router.get("/{customer_id}/devices")
async def get_customer_devices(
    customer_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TECHNICIAN]))
):
    """
    Get all devices for a specific customer
    """
    try:
        devices = await db.devices.find(
            {"customer_id": customer_id},
            {"_id": 0}
        ).to_list(100)
        return devices
    except Exception as e:
        print(f"Error fetching devices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch devices: {str(e)}"
        )


@router.get("/{customer_id}/usage")
async def get_customer_usage(
    customer_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TECHNICIAN])),
    limit: int = 10
):
    """
    Get usage history for a specific customer
    """
    try:
        usage = await db.water_usage.find(
            {"customer_id": customer_id},
            {"_id": 0}
        ).sort("timestamp", -1).limit(limit).to_list(limit)
        return usage
    except Exception as e:
        print(f"Error fetching usage: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch usage: {str(e)}"
        )


@router.get("/{customer_id}/payments")
async def get_customer_payments(
    customer_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TECHNICIAN])),
    limit: int = 10
):
    """
    Get payment history for a specific customer
    """
    try:
        payments = await db.payment_transactions.find(
            {"customer_id": customer_id},
            {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        return payments
    except Exception as e:
        print(f"Error fetching payments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch payments: {str(e)}"
        )


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: dict,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Create a new customer (Admin only)
    """
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    try:
        # Check if email already exists
        existing = await db.users.find_one({"email": customer_data["email"]})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = pwd_context.hash(customer_data["password"])
        
        # Create customer
        customer = {
            "id": customer_data.get("id", f"customer-{datetime.utcnow().timestamp()}"),
            "email": customer_data["email"],
            "full_name": customer_data["full_name"],
            "hashed_password": hashed_password,
            "role": "customer",
            "phone": customer_data.get("phone", ""),
            "address": customer_data.get("address", ""),
            "is_active": customer_data.get("is_active", True),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.users.insert_one(customer)
        
        # Remove password from response
        del customer["hashed_password"]
        return customer
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating customer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create customer: {str(e)}"
        )


@router.put("/{customer_id}", response_model=User)
async def update_customer(
    customer_id: str,
    customer_data: dict,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Update customer information (Admin only)
    """
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    try:
        # Find customer
        customer = await db.users.find_one({"id": customer_id, "role": "customer"})
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Prepare update data
        update_data = {
            "full_name": customer_data.get("full_name", customer["full_name"]),
            "phone": customer_data.get("phone", customer.get("phone", "")),
            "address": customer_data.get("address", customer.get("address", "")),
            "is_active": customer_data.get("is_active", customer["is_active"]),
            "updated_at": datetime.utcnow()
        }
        
        # Update password if provided
        if customer_data.get("password"):
            update_data["hashed_password"] = pwd_context.hash(customer_data["password"])
        
        # Update customer
        await db.users.update_one(
            {"id": customer_id},
            {"$set": update_data}
        )
        
        # Get updated customer
        updated_customer = await db.users.find_one(
            {"id": customer_id},
            {"_id": 0, "hashed_password": 0}
        )
        
        return updated_customer
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating customer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update customer: {str(e)}"
        )


@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Delete a customer (Admin only)
    """
    try:
        result = await db.users.delete_one({"id": customer_id, "role": "customer"})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        return {"message": "Customer deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting customer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete customer: {str(e)}"
        )


@router.post("/bulk-activate")
async def bulk_activate_customers(
    request: BulkOperationRequest,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Bulk activate customers (Admin only)
    """
    try:
        result = await db.users.update_many(
            {"id": {"$in": request.customer_ids}, "role": "customer"},
            {"$set": {"is_active": True, "updated_at": datetime.utcnow()}}
        )
        
        return {
            "message": f"Successfully activated {result.modified_count} customers",
            "modified_count": result.modified_count
        }
    except Exception as e:
        print(f"Error in bulk activate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate customers: {str(e)}"
        )


@router.post("/bulk-deactivate")
async def bulk_deactivate_customers(
    request: BulkOperationRequest,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Bulk deactivate customers (Admin only)
    """
    try:
        result = await db.users.update_many(
            {"id": {"$in": request.customer_ids}, "role": "customer"},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        
        return {
            "message": f"Successfully deactivated {result.modified_count} customers",
            "modified_count": result.modified_count
        }
    except Exception as e:
        print(f"Error in bulk deactivate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate customers: {str(e)}"
        )
