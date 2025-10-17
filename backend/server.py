from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from urllib.parse import quote_plus
import os
import logging

# Import models and auth
from models import (
    User, UserCreate, UserUpdate, UserLogin, Token,
    Property, PropertyCreate, PropertyUpdate,
    Customer, CustomerCreate, CustomerUpdate,
    Device, DeviceCreate, DeviceUpdate,
    Transaction, TransactionCreate, TransactionUpdate,
    WaterUsage, WaterUsageCreate,
    DeviceAlert, DeviceAlertCreate,
    Notification, NotificationCreate,
    SystemSettings, UserRole
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, require_role
)

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection with URL encoding support
def get_mongo_url():
    """
    Get MongoDB URL with proper URL encoding for username and password.
    Handles both mongodb:// and mongodb+srv:// connection strings with credentials.
    Uses proper URL parsing to handle passwords with @ symbols.
    """
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    
    # Skip encoding if no @ symbol (no credentials)
    if '@' not in mongo_url:
        return mongo_url
    
    try:
        # Determine protocol
        if mongo_url.startswith('mongodb+srv://'):
            protocol = 'mongodb+srv://'
        elif mongo_url.startswith('mongodb://'):
            protocol = 'mongodb://'
        else:
            # Unknown protocol, return as-is
            return mongo_url
        
        # Remove protocol to parse credentials
        url_without_protocol = mongo_url.replace(protocol, '', 1)
        
        # Find the LAST @ symbol (which separates credentials from host)
        # This handles passwords that contain @ symbols
        last_at_index = url_without_protocol.rfind('@')
        
        if last_at_index == -1:
            # No @ found, no credentials
            return mongo_url
        
        # Split at the last @ to separate credentials from host
        credentials_part = url_without_protocol[:last_at_index]
        host_part = url_without_protocol[last_at_index + 1:]
        
        # Split credentials into username and password at the FIRST :
        if ':' not in credentials_part:
            # No password, only username - shouldn't happen but handle it
            return mongo_url
        
        first_colon_index = credentials_part.find(':')
        username = credentials_part[:first_colon_index]
        password = credentials_part[first_colon_index + 1:]
        
        # URL encode username and password
        encoded_username = quote_plus(username)
        encoded_password = quote_plus(password)
        
        # Reconstruct the URL with encoded credentials
        encoded_url = f"{protocol}{encoded_username}:{encoded_password}@{host_part}"
        
        logging.info(f"MongoDB URL encoded successfully (username: {username})")
        return encoded_url
        
    except Exception as e:
        logging.error(f"Error encoding MongoDB URL: {e}. Using original URL - this may fail!")
        return mongo_url

mongo_url = get_mongo_url()
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'indowater_db')]

# Create FastAPI app
app = FastAPI(
    title="IndoWater Solution API", 
    version="1.0.0",
    redirect_slashes=True
)

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Mount static files for uploads
# Use /tmp for Render compatibility (writable directory)
upload_dir = Path(os.environ.get('UPLOAD_DIR', '/tmp/uploads'))
try:
    upload_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")
    logger.info(f"Upload directory created at: {upload_dir}")
except Exception as e:
    logger.warning(f"Could not create upload directory: {e}. File uploads may not work.")


# ==================== AUTHENTICATION ROUTES ====================

@api_router.post("/auth/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user (typically for customers)"""
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = User(**user_data.model_dump(exclude={"password"}))
    user_dict = user.model_dump()
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    user_dict['updated_at'] = user_dict['updated_at'].isoformat()
    user_dict['hashed_password'] = get_password_hash(user_data.password)
    
    await db.users.insert_one(user_dict)
    return user


@api_router.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login and get access token"""
    user_doc = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not verify_password(credentials.password, user_doc['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user_doc.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user_doc['id']})
    
    # Convert timestamps
    if isinstance(user_doc.get('created_at'), str):
        user_doc['created_at'] = datetime.fromisoformat(user_doc['created_at'])
    if isinstance(user_doc.get('updated_at'), str):
        user_doc['updated_at'] = datetime.fromisoformat(user_doc['updated_at'])
    
    user = User(**{k: v for k, v in user_doc.items() if k != 'hashed_password'})
    
    return Token(access_token=access_token, user=user)


@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@api_router.put("/auth/profile", response_model=User)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update current user profile"""
    update_data = user_update.model_dump(exclude_unset=True)
    
    if 'password' in update_data:
        update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
    
    update_data['updated_at'] = datetime.utcnow().isoformat()
    
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": update_data}
    )
    
    updated_user = await db.users.find_one({"id": current_user.id}, {"_id": 0})
    if isinstance(updated_user.get('created_at'), str):
        updated_user['created_at'] = datetime.fromisoformat(updated_user['created_at'])
    if isinstance(updated_user.get('updated_at'), str):
        updated_user['updated_at'] = datetime.fromisoformat(updated_user['updated_at'])
    
    return User(**{k: v for k, v in updated_user.items() if k != 'hashed_password'})


# ==================== USER MANAGEMENT ROUTES (Admin Only) ====================

@api_router.get("/users", response_model=List[User])
async def get_users(
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    skip: int = 0,
    limit: int = 100
):
    """Get all users (Admin only)"""
    users = await db.users.find({}, {"_id": 0, "hashed_password": 0}).skip(skip).limit(limit).to_list(limit)
    
    for user in users:
        if isinstance(user.get('created_at'), str):
            user['created_at'] = datetime.fromisoformat(user['created_at'])
        if isinstance(user.get('updated_at'), str):
            user['updated_at'] = datetime.fromisoformat(user['updated_at'])
    
    return users


@api_router.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Create a new user (Admin only)"""
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = User(**user_data.model_dump(exclude={"password"}))
    user_dict = user.model_dump()
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    user_dict['updated_at'] = user_dict['updated_at'].isoformat()
    user_dict['hashed_password'] = get_password_hash(user_data.password)
    
    await db.users.insert_one(user_dict)
    return user


@api_router.get("/users/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Get user by ID (Admin only)"""
    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0, "hashed_password": 0})
    
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    if isinstance(user_doc.get('created_at'), str):
        user_doc['created_at'] = datetime.fromisoformat(user_doc['created_at'])
    if isinstance(user_doc.get('updated_at'), str):
        user_doc['updated_at'] = datetime.fromisoformat(user_doc['updated_at'])
    
    return User(**user_doc)


@api_router.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Update user (Admin only)"""
    update_data = user_update.model_dump(exclude_unset=True)
    
    if 'password' in update_data:
        update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
    
    update_data['updated_at'] = datetime.utcnow().isoformat()
    
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = await db.users.find_one({"id": user_id}, {"_id": 0, "hashed_password": 0})
    if isinstance(updated_user.get('created_at'), str):
        updated_user['created_at'] = datetime.fromisoformat(updated_user['created_at'])
    if isinstance(updated_user.get('updated_at'), str):
        updated_user['updated_at'] = datetime.fromisoformat(updated_user['updated_at'])
    
    return User(**updated_user)


@api_router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Delete user (Admin only)"""
    result = await db.users.delete_one({"id": user_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}


# ==================== PROPERTY ROUTES ====================

@api_router.get("/properties", response_model=List[Property])
async def get_properties(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """Get all properties"""
    properties = await db.properties.find({}, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    
    for prop in properties:
        if isinstance(prop.get('created_at'), str):
            prop['created_at'] = datetime.fromisoformat(prop['created_at'])
        if isinstance(prop.get('updated_at'), str):
            prop['updated_at'] = datetime.fromisoformat(prop['updated_at'])
    
    return properties


@api_router.post("/properties", response_model=Property, status_code=status.HTTP_201_CREATED)
async def create_property(
    property_data: PropertyCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TECHNICIAN]))
):
    """Create a new property"""
    property_obj = Property(**property_data.model_dump())
    property_dict = property_obj.model_dump()
    property_dict['created_at'] = property_dict['created_at'].isoformat()
    property_dict['updated_at'] = property_dict['updated_at'].isoformat()
    
    await db.properties.insert_one(property_dict)
    return property_obj


@api_router.get("/properties/{property_id}", response_model=Property)
async def get_property(
    property_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get property by ID"""
    property_doc = await db.properties.find_one({"id": property_id}, {"_id": 0})
    
    if not property_doc:
        raise HTTPException(status_code=404, detail="Property not found")
    
    if isinstance(property_doc.get('created_at'), str):
        property_doc['created_at'] = datetime.fromisoformat(property_doc['created_at'])
    if isinstance(property_doc.get('updated_at'), str):
        property_doc['updated_at'] = datetime.fromisoformat(property_doc['updated_at'])
    
    return Property(**property_doc)


@api_router.put("/properties/{property_id}", response_model=Property)
async def update_property(
    property_id: str,
    property_update: PropertyUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TECHNICIAN]))
):
    """Update property"""
    update_data = property_update.model_dump(exclude_unset=True)
    update_data['updated_at'] = datetime.utcnow().isoformat()
    
    result = await db.properties.update_one(
        {"id": property_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Property not found")
    
    updated_property = await db.properties.find_one({"id": property_id}, {"_id": 0})
    if isinstance(updated_property.get('created_at'), str):
        updated_property['created_at'] = datetime.fromisoformat(updated_property['created_at'])
    if isinstance(updated_property.get('updated_at'), str):
        updated_property['updated_at'] = datetime.fromisoformat(updated_property['updated_at'])
    
    return Property(**updated_property)


@api_router.delete("/properties/{property_id}")
async def delete_property(
    property_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Delete property (Admin only)"""
    result = await db.properties.delete_one({"id": property_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Property not found")
    
    return {"message": "Property deleted successfully"}


# ==================== CUSTOMER ROUTES ====================

@api_router.get("/customers", response_model=List[Customer])
async def get_customers(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TECHNICIAN])),
    skip: int = 0,
    limit: int = 100
):
    """Get all customers"""
    customers = await db.customers.find({}, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    
    for customer in customers:
        if isinstance(customer.get('created_at'), str):
            customer['created_at'] = datetime.fromisoformat(customer['created_at'])
        if isinstance(customer.get('updated_at'), str):
            customer['updated_at'] = datetime.fromisoformat(customer['updated_at'])
    
    return customers


@api_router.post("/customers", response_model=Customer, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Create a new customer"""
    # Check if customer number already exists
    existing = await db.customers.find_one({"customer_number": customer_data.customer_number})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer number already exists"
        )
    
    customer = Customer(**customer_data.model_dump())
    customer_dict = customer.model_dump()
    customer_dict['created_at'] = customer_dict['created_at'].isoformat()
    customer_dict['updated_at'] = customer_dict['updated_at'].isoformat()
    
    await db.customers.insert_one(customer_dict)
    return customer


@api_router.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(
    customer_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get customer by ID"""
    customer_doc = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    
    if not customer_doc:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if isinstance(customer_doc.get('created_at'), str):
        customer_doc['created_at'] = datetime.fromisoformat(customer_doc['created_at'])
    if isinstance(customer_doc.get('updated_at'), str):
        customer_doc['updated_at'] = datetime.fromisoformat(customer_doc['updated_at'])
    
    return Customer(**customer_doc)


@api_router.put("/customers/{customer_id}", response_model=Customer)
async def update_customer(
    customer_id: str,
    customer_update: CustomerUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update customer"""
    update_data = customer_update.model_dump(exclude_unset=True)
    update_data['updated_at'] = datetime.utcnow().isoformat()
    
    result = await db.customers.update_one(
        {"id": customer_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    updated_customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if isinstance(updated_customer.get('created_at'), str):
        updated_customer['created_at'] = datetime.fromisoformat(updated_customer['created_at'])
    if isinstance(updated_customer.get('updated_at'), str):
        updated_customer['updated_at'] = datetime.fromisoformat(updated_customer['updated_at'])
    
    return Customer(**updated_customer)


@api_router.delete("/customers/{customer_id}")
async def delete_customer(
    customer_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Delete customer (Admin only)"""
    result = await db.customers.delete_one({"id": customer_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return {"message": "Customer deleted successfully"}


# ==================== DEVICE ROUTES ====================

@api_router.get("/devices", response_model=List[Device])
async def get_devices(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    customer_id: Optional[str] = None,
    property_id: Optional[str] = None
):
    """Get all devices with optional filters"""
    query = {}
    if customer_id:
        query['customer_id'] = customer_id
    if property_id:
        query['property_id'] = property_id
    
    devices = await db.devices.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    
    for device in devices:
        if isinstance(device.get('created_at'), str):
            device['created_at'] = datetime.fromisoformat(device['created_at'])
        if isinstance(device.get('updated_at'), str):
            device['updated_at'] = datetime.fromisoformat(device['updated_at'])
        if isinstance(device.get('installation_date'), str):
            device['installation_date'] = datetime.fromisoformat(device['installation_date'])
        if device.get('last_maintenance_date') and isinstance(device['last_maintenance_date'], str):
            device['last_maintenance_date'] = datetime.fromisoformat(device['last_maintenance_date'])
    
    return devices


@api_router.post("/devices", response_model=Device, status_code=status.HTTP_201_CREATED)
async def create_device(
    device_data: DeviceCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TECHNICIAN]))
):
    """Create a new device"""
    # Check if device_id already exists
    existing = await db.devices.find_one({"device_id": device_data.device_id})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device ID already exists"
        )
    
    device = Device(**device_data.model_dump())
    device_dict = device.model_dump()
    device_dict['created_at'] = device_dict['created_at'].isoformat()
    device_dict['updated_at'] = device_dict['updated_at'].isoformat()
    device_dict['installation_date'] = device_dict['installation_date'].isoformat()
    if device_dict.get('last_maintenance_date'):
        device_dict['last_maintenance_date'] = device_dict['last_maintenance_date'].isoformat()
    
    await db.devices.insert_one(device_dict)
    return device


@api_router.get("/devices/{device_id}", response_model=Device)
async def get_device(
    device_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get device by ID"""
    device_doc = await db.devices.find_one({"id": device_id}, {"_id": 0})
    
    if not device_doc:
        raise HTTPException(status_code=404, detail="Device not found")
    
    if isinstance(device_doc.get('created_at'), str):
        device_doc['created_at'] = datetime.fromisoformat(device_doc['created_at'])
    if isinstance(device_doc.get('updated_at'), str):
        device_doc['updated_at'] = datetime.fromisoformat(device_doc['updated_at'])
    if isinstance(device_doc.get('installation_date'), str):
        device_doc['installation_date'] = datetime.fromisoformat(device_doc['installation_date'])
    if device_doc.get('last_maintenance_date') and isinstance(device_doc['last_maintenance_date'], str):
        device_doc['last_maintenance_date'] = datetime.fromisoformat(device_doc['last_maintenance_date'])
    
    return Device(**device_doc)


@api_router.put("/devices/{device_id}", response_model=Device)
async def update_device(
    device_id: str,
    device_update: DeviceUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TECHNICIAN]))
):
    """Update device"""
    update_data = device_update.model_dump(exclude_unset=True)
    update_data['updated_at'] = datetime.utcnow().isoformat()
    
    if 'last_maintenance_date' in update_data and update_data['last_maintenance_date']:
        update_data['last_maintenance_date'] = update_data['last_maintenance_date'].isoformat()
    
    result = await db.devices.update_one(
        {"id": device_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Device not found")
    
    updated_device = await db.devices.find_one({"id": device_id}, {"_id": 0})
    if isinstance(updated_device.get('created_at'), str):
        updated_device['created_at'] = datetime.fromisoformat(updated_device['created_at'])
    if isinstance(updated_device.get('updated_at'), str):
        updated_device['updated_at'] = datetime.fromisoformat(updated_device['updated_at'])
    if isinstance(updated_device.get('installation_date'), str):
        updated_device['installation_date'] = datetime.fromisoformat(updated_device['installation_date'])
    if updated_device.get('last_maintenance_date') and isinstance(updated_device['last_maintenance_date'], str):
        updated_device['last_maintenance_date'] = datetime.fromisoformat(updated_device['last_maintenance_date'])
    
    return Device(**updated_device)


@api_router.delete("/devices/{device_id}")
async def delete_device(
    device_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Delete device (Admin only)"""
    result = await db.devices.delete_one({"id": device_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return {"message": "Device deleted successfully"}


# ==================== DASHBOARD STATS ====================

@api_router.get("/dashboard/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics"""
    stats = {}
    
    if current_user.role == UserRole.ADMIN:
        stats['total_users'] = await db.users.count_documents({})
        stats['total_customers'] = await db.customers.count_documents({})
        stats['total_properties'] = await db.properties.count_documents({})
        stats['total_devices'] = await db.devices.count_documents({})
        stats['active_devices'] = await db.devices.count_documents({"status": "active"})
        stats['total_transactions'] = await db.transactions.count_documents({})
        
        # Calculate total revenue
        pipeline = [
            {"$match": {"status": "success", "transaction_type": "topup"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        result = await db.transactions.aggregate(pipeline).to_list(1)
        stats['total_revenue'] = result[0]['total'] if result else 0
        
    elif current_user.role == UserRole.TECHNICIAN:
        stats['total_devices'] = await db.devices.count_documents({})
        stats['active_devices'] = await db.devices.count_documents({"status": "active"})
        stats['maintenance_devices'] = await db.devices.count_documents({"status": "maintenance"})
        stats['faulty_devices'] = await db.devices.count_documents({"status": "faulty"})
        
    elif current_user.role == UserRole.CUSTOMER:
        # Get customer record
        customer = await db.customers.find_one({"user_id": current_user.id})
        if customer:
            # Get customer devices
            devices = await db.devices.find({"customer_id": customer['id']}, {"_id": 0}).to_list(100)
            stats['total_devices'] = len(devices)
            stats['total_balance'] = sum(d.get('current_balance', 0) for d in devices)
            stats['total_water_consumed'] = sum(d.get('total_water_consumed', 0) for d in devices)
            
            # Get transaction count
            stats['total_transactions'] = await db.transactions.count_documents({"customer_id": customer['id']})
    
    return stats


# Import technician routes
from technician_routes import router as technician_router
from file_upload_routes import router as upload_router

# Import payment routes
from payment_routes import router as payment_router
from admin_payment_routes import router as admin_payment_router

# Import analytics routes
from analytics_routes import router as analytics_router
from report_routes import router as report_router
from chatbot_routes import router as chatbot_router
from notification_routes import router as notification_router
from budget_routes import router as budget_router
from voucher_routes import router as voucher_router
from alert_routes import router as alert_router
from admin_routes import router as admin_router
from customer_routes import router as customer_router

# Include routers - include technician routes in api_router first
api_router.include_router(technician_router)
api_router.include_router(payment_router)
api_router.include_router(admin_payment_router)
api_router.include_router(analytics_router)
api_router.include_router(report_router)
api_router.include_router(chatbot_router)
api_router.include_router(notification_router)
api_router.include_router(budget_router)
api_router.include_router(voucher_router)
api_router.include_router(alert_router)
api_router.include_router(admin_router)
api_router.include_router(customer_router)
app.include_router(upload_router)

# Then include api_router in app
app.include_router(api_router)


# Background task for checking low balances
import asyncio
from notification_service import get_notification_service

async def check_low_balances_task():
    """Background task to check for low balances and send notifications"""
    while True:
        try:
            # Check every hour
            await asyncio.sleep(3600)
            
            notification_service = get_notification_service(db)
            
            # Get all customers with balance below threshold
            customers_cursor = db.customers.find({
                "balance": {"$lt": 5000}
            })
            
            async for customer in customers_cursor:
                try:
                    # Get user data
                    user = await db.users.find_one({"id": customer["user_id"]})
                    if not user:
                        continue
                    
                    # Check and create notification
                    await notification_service.check_and_notify_low_balance(
                        customer_id=customer["user_id"],
                        customer_name=user.get("full_name", "Customer"),
                        current_balance=customer.get("balance", 0)
                    )
                except Exception as e:
                    print(f"Error checking balance for customer {customer.get('user_id')}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in check_low_balances_task: {e}")
            await asyncio.sleep(60)  # Wait a minute before retrying


@app.on_event("startup")
async def startup_event():
    """Start background tasks on app startup"""
    asyncio.create_task(check_low_balances_task())


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
