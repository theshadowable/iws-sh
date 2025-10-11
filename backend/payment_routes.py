"""
Payment Routes
Handles payment creation, webhook processing, and purchase history
"""
from fastapi import APIRouter, HTTPException, Depends, Request, status
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import List, Optional
import os
import uuid

from auth import get_current_user, require_role
from models import User, UserRole
from payment_models import (
    MidtransTransactionRequest,
    MidtransTransactionResponse,
    XenditVARequest,
    XenditVAResponse,
    XenditQRISRequest,
    XenditQRISResponse,
    XenditEWalletRequest,
    XenditEWalletResponse,
    PaymentTransaction,
    PaymentStatus,
    PaymentMethod,
    MidtransNotification,
    XenditCallbackVA,
    XenditCallbackQRIS,
    PurchaseHistoryQuery
)
from midtrans_service import MidtransService
from xendit_service import XenditService


router = APIRouter(prefix="/api/payments", tags=["payments"])

# Database connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'indowater_db')]

# Payment services
midtrans_service = MidtransService()
xendit_service = XenditService()


# ==================== PAYMENT CREATION ENDPOINTS ====================

@router.post("/create-midtrans", response_model=MidtransTransactionResponse)
async def create_midtrans_payment(
    request: MidtransTransactionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create Midtrans Snap transaction
    Returns Snap token and redirect URL
    """
    try:
        # Create Midtrans transaction
        response = midtrans_service.create_transaction(request)
        
        # Store transaction in database
        transaction = PaymentTransaction(
            customer_id=request.customer_id,
            customer_email=request.customer_email,
            customer_name=request.customer_name,
            customer_phone=request.customer_phone,
            meter_id=request.meter_id,
            amount=request.amount,
            payment_method=PaymentMethod.MIDTRANS,
            reference_id=response.reference_id,
            external_id=response.transaction_id,
            status=response.status,
            payment_url=response.snap_url,
            expires_at=response.expires_at,
            description=request.description,
            metadata={
                "snap_token": response.snap_token,
                "created_by": current_user.id
            }
        )
        
        await db.payment_transactions.insert_one(transaction.model_dump())
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create payment: {str(e)}"
        )


@router.post("/create-xendit-va", response_model=XenditVAResponse)
async def create_xendit_va_payment(
    request: XenditVARequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create Xendit Virtual Account payment
    Returns VA number for bank transfer
    """
    try:
        # Create Xendit VA
        response = xendit_service.create_virtual_account(request)
        
        # Store transaction in database
        transaction = PaymentTransaction(
            customer_id=request.customer_id,
            customer_email=request.customer_email,
            customer_name=request.customer_name,
            customer_phone=request.customer_phone,
            meter_id=request.meter_id,
            amount=request.amount,
            payment_method=PaymentMethod.XENDIT_VA,
            reference_id=response.reference_id,
            external_id=response.external_id,
            status=response.status,
            va_number=response.va_number,
            expires_at=response.expiration_date,
            description=request.description,
            metadata={
                "bank_code": response.bank_code,
                "account_name": response.account_name,
                "created_by": current_user.id
            }
        )
        
        await db.payment_transactions.insert_one(transaction.model_dump())
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create VA payment: {str(e)}"
        )


@router.post("/create-xendit-qris", response_model=XenditQRISResponse)
async def create_xendit_qris_payment(
    request: XenditQRISRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create Xendit QRIS payment
    Returns QR code for scanning
    """
    try:
        # Create Xendit QRIS
        response = xendit_service.create_qris(request)
        
        # Store transaction in database
        transaction = PaymentTransaction(
            customer_id=request.customer_id,
            customer_email=request.customer_email,
            customer_name=request.customer_name,
            meter_id=request.meter_id,
            amount=request.amount,
            payment_method=PaymentMethod.XENDIT_QRIS,
            reference_id=response.reference_id,
            external_id=response.external_id,
            status=response.status,
            qr_code_url=response.qr_code_url,
            qr_string=response.qr_string,
            expires_at=response.expires_at,
            description=request.description,
            metadata={
                "created_by": current_user.id
            }
        )
        
        await db.payment_transactions.insert_one(transaction.model_dump())
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create QRIS payment: {str(e)}"
        )


@router.post("/create-xendit-ewallet", response_model=XenditEWalletResponse)
async def create_xendit_ewallet_payment(
    request: XenditEWalletRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create Xendit E-wallet payment
    Returns checkout URL for payment
    """
    try:
        # Create Xendit E-wallet charge
        response = xendit_service.create_ewallet(request)
        
        # Store transaction in database
        transaction = PaymentTransaction(
            customer_id=request.customer_id,
            customer_email=request.customer_email,
            customer_name=request.customer_name,
            customer_phone=request.customer_phone,
            meter_id=request.meter_id,
            amount=request.amount,
            payment_method=PaymentMethod.XENDIT_EWALLET,
            reference_id=response.reference_id,
            external_id=response.external_id,
            status=response.status,
            ewallet_url=response.checkout_url,
            expires_at=response.expires_at,
            description=request.description,
            metadata={
                "ewallet_type": response.ewallet_type,
                "created_by": current_user.id
            }
        )
        
        await db.payment_transactions.insert_one(transaction.model_dump())
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create E-wallet payment: {str(e)}"
        )


# ==================== PAYMENT STATUS & HISTORY ====================

@router.get("/{reference_id}")
async def get_payment_status(
    reference_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get payment status by reference ID"""
    transaction = await db.payment_transactions.find_one(
        {"reference_id": reference_id},
        {"_id": 0}
    )
    
    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )
    
    # Check authorization
    if current_user.role != UserRole.ADMIN and transaction['customer_id'] != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this transaction"
        )
    
    return transaction


@router.get("/history/list")
async def get_purchase_history(
    customer_id: Optional[str] = None,
    status: Optional[PaymentStatus] = None,
    payment_method: Optional[PaymentMethod] = None,
    limit: int = 50,
    skip: int = 0,
    current_user: User = Depends(get_current_user)
):
    """Get purchase history with filters"""
    # Build query
    query = {}
    
    # Role-based filtering
    if current_user.role == UserRole.CUSTOMER:
        query["customer_id"] = current_user.id
    elif customer_id:
        query["customer_id"] = customer_id
    
    if status:
        query["status"] = status.value
    
    if payment_method:
        query["payment_method"] = payment_method.value
    
    # Get transactions
    cursor = db.payment_transactions.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit)
    
    transactions = await cursor.to_list(length=limit)
    
    # Get total count
    total = await db.payment_transactions.count_documents(query)
    
    return {
        "transactions": transactions,
        "total": total,
        "limit": limit,
        "skip": skip
    }


# ==================== WEBHOOK ENDPOINTS ====================

@router.post("/webhooks/midtrans")
async def midtrans_webhook(request: Request):
    """Handle Midtrans payment notifications"""
    try:
        # Parse notification
        notification_data = await request.json()
        notification = MidtransNotification(**notification_data)
        
        # Verify notification signature
        if not midtrans_service.verify_notification(notification):
            raise HTTPException(
                status_code=401,
                detail="Invalid notification signature"
            )
        
        # Get transaction
        transaction = await db.payment_transactions.find_one(
            {"reference_id": notification.order_id}
        )
        
        if not transaction:
            return {"status": "transaction_not_found"}
        
        # Parse payment status
        payment_status = midtrans_service.parse_payment_status(
            notification.transaction_status,
            notification.fraud_status
        )
        
        # Update transaction
        update_data = {
            "status": payment_status.value,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if payment_status == PaymentStatus.PAID:
            update_data["paid_at"] = notification.transaction_time
            
            # Update customer balance
            await update_customer_balance(
                transaction['customer_id'],
                transaction['amount'],
                transaction['meter_id']
            )
        
        await db.payment_transactions.update_one(
            {"reference_id": notification.order_id},
            {"$set": update_data}
        )
        
        return {"status": "success"}
        
    except Exception as e:
        print(f"Midtrans webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}


@router.post("/webhooks/xendit/va")
async def xendit_va_webhook(request: Request):
    """Handle Xendit Virtual Account callbacks"""
    try:
        # Verify callback token
        callback_token = request.headers.get("x-callback-token")
        if not xendit_service.verify_callback_token(callback_token):
            raise HTTPException(
                status_code=401,
                detail="Invalid callback token"
            )
        
        # Parse callback data
        callback_data = await request.json()
        callback = XenditCallbackVA(**callback_data)
        
        # Get transaction
        transaction = await db.payment_transactions.find_one(
            {"external_id": callback.external_id}
        )
        
        if not transaction:
            return {"status": "transaction_not_found"}
        
        # Update transaction status
        update_data = {
            "status": PaymentStatus.PAID.value,
            "paid_at": callback.transaction_timestamp,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await db.payment_transactions.update_one(
            {"external_id": callback.external_id},
            {"$set": update_data}
        )
        
        # Update customer balance
        await update_customer_balance(
            transaction['customer_id'],
            transaction['amount'],
            transaction.get('meter_id')
        )
        
        return {"status": "success"}
        
    except Exception as e:
        print(f"Xendit VA webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}


@router.post("/webhooks/xendit/qris")
async def xendit_qris_webhook(request: Request):
    """Handle Xendit QRIS callbacks"""
    try:
        # Verify callback token
        callback_token = request.headers.get("x-callback-token")
        if not xendit_service.verify_callback_token(callback_token):
            raise HTTPException(
                status_code=401,
                detail="Invalid callback token"
            )
        
        # Parse callback data
        callback_data = await request.json()
        callback = XenditCallbackQRIS(**callback_data)
        
        # Get transaction
        transaction = await db.payment_transactions.find_one(
            {"external_id": callback.external_id}
        )
        
        if not transaction:
            return {"status": "transaction_not_found"}
        
        # Check if already paid
        if callback.status == "COMPLETED":
            update_data = {
                "status": PaymentStatus.PAID.value,
                "paid_at": callback.updated,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await db.payment_transactions.update_one(
                {"external_id": callback.external_id},
                {"$set": update_data}
            )
            
            # Update customer balance
            await update_customer_balance(
                transaction['customer_id'],
                transaction['amount'],
                transaction.get('meter_id')
            )
        
        return {"status": "success"}
        
    except Exception as e:
        print(f"Xendit QRIS webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}


@router.post("/webhooks/xendit/ewallet")
async def xendit_ewallet_webhook(request: Request):
    """Handle Xendit E-wallet callbacks"""
    try:
        # Verify callback token
        callback_token = request.headers.get("x-callback-token")
        if not xendit_service.verify_callback_token(callback_token):
            raise HTTPException(
                status_code=401,
                detail="Invalid callback token"
            )
        
        # Parse callback data
        callback_data = await request.json()
        
        # Get transaction
        external_id = callback_data.get('external_id')
        transaction = await db.payment_transactions.find_one(
            {"external_id": external_id}
        )
        
        if not transaction:
            return {"status": "transaction_not_found"}
        
        # Check status
        if callback_data.get('status') == 'SUCCESS':
            update_data = {
                "status": PaymentStatus.PAID.value,
                "paid_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await db.payment_transactions.update_one(
                {"external_id": external_id},
                {"$set": update_data}
            )
            
            # Update customer balance
            await update_customer_balance(
                transaction['customer_id'],
                transaction['amount'],
                transaction.get('meter_id')
            )
        
        return {"status": "success"}
        
    except Exception as e:
        print(f"Xendit E-wallet webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}


# ==================== HELPER FUNCTIONS ====================

async def update_customer_balance(
    customer_id: str,
    amount: float,
    meter_id: Optional[str] = None
):
    """
    Update customer balance after successful payment
    
    Args:
        customer_id: Customer user ID
        amount: Payment amount
        meter_id: Optional meter ID
    """
    try:
        # Get customer
        customer = await db.users.find_one({"id": customer_id})
        
        if not customer:
            print(f"Customer not found: {customer_id}")
            return
        
        # Calculate balance to add (IDR 10,000 = 1 m³ of water)
        water_volume = amount / 10000
        
        # Update user balance
        current_balance = customer.get('balance', 0)
        new_balance = current_balance + water_volume
        
        await db.users.update_one(
            {"id": customer_id},
            {
                "$set": {
                    "balance": new_balance,
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        # Create balance history record
        balance_history = {
            "id": str(uuid.uuid4()),
            "customer_id": customer_id,
            "meter_id": meter_id,
            "amount": amount,
            "water_volume": water_volume,
            "previous_balance": current_balance,
            "new_balance": new_balance,
            "transaction_type": "top_up",
            "created_at": datetime.utcnow().isoformat()
        }
        
        await db.balance_history.insert_one(balance_history)
        
        print(f"Balance updated for customer {customer_id}: {current_balance} -> {new_balance} m³")
        
    except Exception as e:
        print(f"Error updating balance: {str(e)}")


@router.get("/finish")
async def payment_finish(order_id: str, status_code: str, transaction_status: str):
    """
    Handle Midtrans payment finish callback
    This is called after customer completes/cancels payment on Snap page
    """
    return {
        "status": "received",
        "order_id": order_id,
        "transaction_status": transaction_status
    }
