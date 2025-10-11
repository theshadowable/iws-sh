"""
Xendit Payment Gateway Service
Handles Virtual Account, QRIS, and E-wallet transactions
"""
import os
import time
import uuid
import base64
import requests
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException

from payment_models import (
    XenditVARequest,
    XenditVAResponse,
    XenditQRISRequest,
    XenditQRISResponse,
    XenditEWalletRequest,
    XenditEWalletResponse,
    PaymentStatus,
    XenditVABank,
    XenditEWallet
)


class XenditService:
    """Service class for Xendit payment gateway integration"""
    
    def __init__(self):
        """Initialize Xendit client with environment configuration"""
        self.secret_key = os.getenv('XENDIT_SECRET_KEY')
        self.public_key = os.getenv('XENDIT_PUBLIC_KEY')
        
        if not self.secret_key:
            raise ValueError("Xendit API keys not configured")
        
        # API base URL
        self.base_url = "https://api.xendit.co"
        
        # Create authorization header
        auth_string = f"{self.secret_key}:"
        auth_bytes = auth_string.encode('utf-8')
        auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')
        
        self.headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/json"
        }
    
    def create_virtual_account(
        self,
        request: XenditVARequest
    ) -> XenditVAResponse:
        """
        Create a Virtual Account payment
        
        Args:
            request: VA request data
            
        Returns:
            XenditVAResponse with VA details
        """
        try:
            # Generate unique external ID
            external_id = self._generate_external_id(
                request.customer_id,
                request.meter_id,
                "VA"
            )
            
            # Calculate expiration date (24 hours from now)
            expiration_date = datetime.utcnow() + timedelta(hours=24)
            
            # Prepare VA parameters
            va_params = {
                "external_id": external_id,
                "bank_code": request.bank_code.value,
                "name": request.customer_name[:50],  # Max 50 characters
                "expected_amount": int(request.amount),
                "is_closed": True,  # Closed VA - exact amount required
                "expiration_date": expiration_date.isoformat() + "Z",
                "is_single_use": True
            }
            
            # Create VA via API
            response = requests.post(
                f"{self.base_url}/callback_virtual_accounts",
                headers=self.headers,
                json=va_params
            )
            
            if response.status_code not in [200, 201]:
                raise HTTPException(
                    status_code=500,
                    detail=f"Xendit API error: {response.text}"
                )
            
            va = response.json()
            
            if not va or 'account_number' not in va:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create Virtual Account"
                )
            
            return XenditVAResponse(
                success=True,
                reference_id=external_id,
                external_id=va['external_id'],
                va_number=va['account_number'],
                bank_code=va['bank_code'],
                status=PaymentStatus.PENDING,
                amount=request.amount,
                expected_amount=va['expected_amount'],
                expiration_date=datetime.fromisoformat(
                    va['expiration_date'].replace('Z', '+00:00')
                ),
                account_name=va['name']
            )
            
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=500,
                detail=f"Xendit API request failed: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Xendit VA creation failed: {str(e)}"
            )
    
    def create_qris(
        self,
        request: XenditQRISRequest
    ) -> XenditQRISResponse:
        """
        Create a QRIS payment
        
        Args:
            request: QRIS request data
            
        Returns:
            XenditQRISResponse with QR code details
        """
        try:
            # Generate unique external ID
            external_id = self._generate_external_id(
                request.customer_id,
                request.meter_id,
                "QRIS"
            )
            
            # Prepare QR code parameters
            qr_params = {
                "external_id": external_id,
                "type": "DYNAMIC",
                "callback_url": f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/api/payments/webhooks/xendit/qris",
                "amount": int(request.amount)
            }
            
            # Create QR code via API
            response = requests.post(
                f"{self.base_url}/qr_codes",
                headers=self.headers,
                json=qr_params
            )
            
            if response.status_code not in [200, 201]:
                raise HTTPException(
                    status_code=500,
                    detail=f"Xendit API error: {response.text}"
                )
            
            qr = response.json()
            
            if not qr or 'qr_string' not in qr:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create QRIS"
                )
            
            # Calculate expiration (QRIS typically expires in 30 minutes)
            expires_at = datetime.utcnow() + timedelta(minutes=30)
            
            return XenditQRISResponse(
                success=True,
                reference_id=external_id,
                external_id=qr['id'],
                qr_code_url=qr.get('qr_url', ''),
                qr_string=qr['qr_string'],
                status=PaymentStatus.PENDING,
                amount=request.amount,
                expires_at=expires_at
            )
            
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=500,
                detail=f"Xendit API request failed: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Xendit QRIS creation failed: {str(e)}"
            )
    
    def create_ewallet(
        self,
        request: XenditEWalletRequest
    ) -> XenditEWalletResponse:
        """
        Create an E-wallet payment
        
        Args:
            request: E-wallet request data
            
        Returns:
            XenditEWalletResponse with checkout URL
        """
        try:
            # Generate unique external ID
            external_id = self._generate_external_id(
                request.customer_id,
                request.meter_id,
                "EWALLET"
            )
            
            # Prepare e-wallet parameters
            ewallet_params = {
                "external_id": external_id,
                "amount": int(request.amount),
                "phone": request.customer_phone,
                "ewallet_type": request.ewallet_type.value,
                "callback_url": f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/api/payments/webhooks/xendit/ewallet",
                "redirect_url": f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/payment/success"
            }
            
            # Create e-wallet charge via API
            response = requests.post(
                f"{self.base_url}/ewallets/charges",
                headers=self.headers,
                json=ewallet_params
            )
            
            if response.status_code not in [200, 201]:
                raise HTTPException(
                    status_code=500,
                    detail=f"Xendit API error: {response.text}"
                )
            
            ewallet = response.json()
            
            if not ewallet:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create E-wallet payment"
                )
            
            # Get checkout URL
            checkout_url = ewallet.get('actions', {}).get('desktop_web_checkout_url', '')
            if not checkout_url:
                checkout_url = ewallet.get('actions', {}).get('mobile_web_checkout_url', '')
            
            # Calculate expiration
            expires_at = datetime.utcnow() + timedelta(hours=1)
            
            return XenditEWalletResponse(
                success=True,
                reference_id=external_id,
                external_id=ewallet.get('id', external_id),
                checkout_url=checkout_url,
                ewallet_type=request.ewallet_type.value,
                status=PaymentStatus.PENDING,
                amount=request.amount,
                expires_at=expires_at
            )
            
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=500,
                detail=f"Xendit API request failed: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Xendit E-wallet creation failed: {str(e)}"
            )
    
    def get_va_status(self, external_id: str) -> dict:
        """Get Virtual Account status"""
        try:
            response = requests.get(
                f"{self.base_url}/callback_virtual_accounts/{external_id}",
                headers=self.headers
            )
            return response.json() if response.status_code == 200 else {}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get VA status: {str(e)}"
            )
    
    def get_qris_status(self, qr_id: str) -> dict:
        """Get QRIS payment status"""
        try:
            response = requests.get(
                f"{self.base_url}/qr_codes/{qr_id}",
                headers=self.headers
            )
            return response.json() if response.status_code == 200 else {}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get QRIS status: {str(e)}"
            )
    
    def get_ewallet_status(self, charge_id: str) -> dict:
        """Get E-wallet payment status"""
        try:
            response = requests.get(
                f"{self.base_url}/ewallets/charges/{charge_id}",
                headers=self.headers
            )
            return response.json() if response.status_code == 200 else {}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get E-wallet status: {str(e)}"
            )
    
    def parse_payment_status(self, status: str) -> PaymentStatus:
        """
        Parse Xendit status to internal status
        
        Args:
            status: Xendit payment status
            
        Returns:
            Internal PaymentStatus
        """
        status_mapping = {
            'ACTIVE': PaymentStatus.PENDING,
            'PENDING': PaymentStatus.PENDING,
            'INACTIVE': PaymentStatus.EXPIRED,
            'EXPIRED': PaymentStatus.EXPIRED,
            'COMPLETED': PaymentStatus.PAID,
            'PAID': PaymentStatus.PAID,
            'SUCCESS': PaymentStatus.PAID,
            'FAILED': PaymentStatus.FAILED,
            'VOIDED': PaymentStatus.CANCELLED
        }
        
        return status_mapping.get(
            status.upper(),
            PaymentStatus.PENDING
        )
    
    def _generate_external_id(
        self,
        customer_id: str,
        meter_id: Optional[str],
        payment_type: str
    ) -> str:
        """
        Generate unique external ID for Xendit transaction
        
        Args:
            customer_id: Customer identifier
            meter_id: Optional meter identifier
            payment_type: Type of payment (VA, QRIS, EWALLET)
            
        Returns:
            Unique external ID
        """
        timestamp = int(time.time())
        unique_id = uuid.uuid4().hex[:8]
        
        if meter_id:
            return f"XND-{payment_type}-{meter_id}-{customer_id}-{timestamp}-{unique_id}"
        else:
            return f"XND-{payment_type}-{customer_id}-{timestamp}-{unique_id}"
    
    def verify_callback_token(self, callback_token: str) -> bool:
        """
        Verify Xendit callback token
        
        Args:
            callback_token: Token from webhook header
            
        Returns:
            True if valid
        """
        expected_token = os.getenv('XENDIT_WEBHOOK_TOKEN')
        return callback_token == expected_token
