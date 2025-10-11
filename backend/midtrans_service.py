"""
Midtrans Payment Gateway Service
Handles Snap transaction creation and notification processing
"""
import os
import time
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException
import midtransclient

from payment_models import (
    MidtransTransactionRequest,
    MidtransTransactionResponse,
    PaymentStatus,
    MidtransNotification
)


class MidtransService:
    """Service class for Midtrans payment gateway integration"""
    
    def __init__(self):
        """Initialize Midtrans client with environment configuration"""
        self.server_key = os.getenv('MIDTRANS_SERVER_KEY')
        self.client_key = os.getenv('MIDTRANS_CLIENT_KEY')
        self.is_production = os.getenv('MIDTRANS_IS_PRODUCTION', 'false').lower() == 'true'
        self.enabled = bool(self.server_key and self.client_key)
        
        if not self.enabled:
            print("Warning: Midtrans API keys not configured. Payment gateway disabled.")
            self.snap = None
            self.core_api = None
            return
        
        # Initialize Snap client
        self.snap = midtransclient.Snap(
            is_production=self.is_production,
            server_key=self.server_key,
            client_key=self.client_key
        )
        
        # Initialize Core API client for transaction status
        self.core_api = midtransclient.CoreApi(
            is_production=self.is_production,
            server_key=self.server_key,
            client_key=self.client_key
        )
    
    def create_transaction(
        self,
        request: MidtransTransactionRequest
    ) -> MidtransTransactionResponse:
        """
        Create a new Snap transaction
        
        Args:
            request: Transaction request data
            
        Returns:
            MidtransTransactionResponse with snap token and URL
        """
        if not self.enabled:
            raise HTTPException(
                status_code=503,
                detail="Midtrans payment gateway is not configured"
            )
        try:
            # Generate unique reference ID
            reference_id = self._generate_reference_id(
                request.customer_id,
                request.meter_id
            )
            
            # Build transaction parameters
            param = {
                "transaction_details": {
                    "order_id": reference_id,
                    "gross_amount": int(request.amount)
                },
                "customer_details": {
                    "first_name": request.customer_name,
                    "email": request.customer_email,
                    "phone": request.customer_phone
                },
                "item_details": [
                    {
                        "id": "water_balance",
                        "price": int(request.amount),
                        "quantity": 1,
                        "name": request.description or "Water Meter Balance Top-up"
                    }
                ],
                "callbacks": {
                    "finish": f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/api/payments/finish"
                },
                "expiry": {
                    "unit": "hour",
                    "duration": 24
                }
            }
            
            # Add metadata
            if request.meter_id:
                param["custom_field1"] = request.meter_id
            param["custom_field2"] = request.customer_id
            
            # Create Snap transaction
            transaction = self.snap.create_transaction(param)
            
            if not transaction or 'token' not in transaction:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create Midtrans transaction"
                )
            
            # Calculate expiration time
            expires_at = datetime.utcnow() + timedelta(hours=24)
            
            return MidtransTransactionResponse(
                success=True,
                reference_id=reference_id,
                transaction_id=transaction.get('transaction_id', reference_id),
                snap_token=transaction['token'],
                snap_url=transaction.get('redirect_url', ''),
                status=PaymentStatus.PENDING,
                amount=request.amount,
                expires_at=expires_at
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Midtrans transaction creation failed: {str(e)}"
            )
    
    def verify_notification(
        self,
        notification: MidtransNotification
    ) -> bool:
        """
        Verify the authenticity of a Midtrans notification
        
        Args:
            notification: Notification data from Midtrans
            
        Returns:
            True if notification is valid
        """
        try:
            # Create signature string
            signature_string = f"{notification.order_id}{notification.status_code}{notification.gross_amount}{self.server_key}"
            
            # Generate SHA512 hash
            generated_signature = hashlib.sha512(
                signature_string.encode('utf-8')
            ).hexdigest()
            
            # Compare signatures
            return generated_signature == notification.signature_key
            
        except Exception as e:
            print(f"Signature verification error: {str(e)}")
            return False
    
    def get_transaction_status(self, order_id: str) -> dict:
        """
        Get transaction status from Midtrans
        
        Args:
            order_id: Order/Reference ID
            
        Returns:
            Transaction status data
        """
        try:
            status = self.core_api.transactions.status(order_id)
            return status
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get transaction status: {str(e)}"
            )
    
    def parse_payment_status(
        self,
        transaction_status: str,
        fraud_status: Optional[str] = None
    ) -> PaymentStatus:
        """
        Parse Midtrans transaction status to internal status
        
        Args:
            transaction_status: Midtrans transaction status
            fraud_status: Fraud detection status
            
        Returns:
            Internal PaymentStatus
        """
        # Handle fraud status
        if fraud_status == 'deny':
            return PaymentStatus.FAILED
        
        # Map transaction status
        status_mapping = {
            'capture': PaymentStatus.PAID,
            'settlement': PaymentStatus.PAID,
            'pending': PaymentStatus.PENDING,
            'deny': PaymentStatus.FAILED,
            'expire': PaymentStatus.EXPIRED,
            'cancel': PaymentStatus.CANCELLED,
            'refund': PaymentStatus.CANCELLED,
            'partial_refund': PaymentStatus.PAID
        }
        
        return status_mapping.get(
            transaction_status.lower(),
            PaymentStatus.PENDING
        )
    
    def _generate_reference_id(
        self,
        customer_id: str,
        meter_id: Optional[str] = None
    ) -> str:
        """
        Generate unique reference ID for transaction
        
        Args:
            customer_id: Customer identifier
            meter_id: Optional meter identifier
            
        Returns:
            Unique reference ID
        """
        timestamp = int(time.time())
        unique_id = uuid.uuid4().hex[:8]
        
        if meter_id:
            return f"MDT-{meter_id}-{customer_id}-{timestamp}-{unique_id}"
        else:
            return f"MDT-{customer_id}-{timestamp}-{unique_id}"
    
    def cancel_transaction(self, order_id: str) -> dict:
        """
        Cancel a pending transaction
        
        Args:
            order_id: Order/Reference ID
            
        Returns:
            Cancellation result
        """
        try:
            result = self.core_api.transactions.cancel(order_id)
            return result
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to cancel transaction: {str(e)}"
            )
