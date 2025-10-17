"""
File Upload and OCR Processing Routes
Handles meter photo uploads and OCR extraction
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, status
from typing import Optional
import os
import uuid
from pathlib import Path
import shutil
from PIL import Image
import pytesseract
import re
from datetime import datetime

from auth import get_current_user
from models import User, UserRole

router = APIRouter(prefix="/api/upload", tags=["Upload"])

# Upload directory configuration
# Use /tmp for Render compatibility
UPLOAD_DIR = Path(os.environ.get('UPLOAD_DIR', '/tmp/uploads')) / "meter_photos"
try:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create upload directory: {e}")

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def save_upload_file(upload_file: UploadFile) -> str:
    """
    Save uploaded file to disk
    Returns: relative file path
    """
    if not allowed_file(upload_file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Generate unique filename
    file_extension = Path(upload_file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    # Return relative path
    return f"/uploads/meter_photos/{unique_filename}"


def extract_meter_reading(image_path: str) -> dict:
    """
    Extract meter reading from image using OCR
    Returns: dict with reading value and confidence
    """
    try:
        # Open image
        image = Image.open(image_path)
        
        # Preprocess image for better OCR
        # Convert to grayscale
        image = image.convert('L')
        
        # Enhance contrast
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Perform OCR
        text = pytesseract.image_to_string(image, config='--psm 6 digits')
        
        # Extract numbers using regex
        numbers = re.findall(r'\d+\.?\d*', text)
        
        if not numbers:
            return {
                "success": False,
                "reading_value": None,
                "confidence": 0.0,
                "extracted_text": text.strip(),
                "error": "No numbers detected in image"
            }
        
        # Take the largest number (usually the main reading)
        reading_value = max(numbers, key=lambda x: float(x) if x else 0)
        
        # Get confidence (simplified - in production use more sophisticated methods)
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        confidences = [int(conf) for conf in data['conf'] if conf != '-1']
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            "success": True,
            "reading_value": float(reading_value),
            "confidence": round(avg_confidence, 2),
            "extracted_text": text.strip(),
            "all_numbers": numbers
        }
        
    except Exception as e:
        return {
            "success": False,
            "reading_value": None,
            "confidence": 0.0,
            "extracted_text": "",
            "error": str(e)
        }


@router.post("/meter-photo")
async def upload_meter_photo(
    file: UploadFile = File(...),
    process_ocr: bool = Form(True),
    current_user: User = Depends(get_current_user)
):
    """
    Upload meter photo and optionally process with OCR
    """
    if current_user.role not in [UserRole.TECHNICIAN, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only technicians and admins can upload meter photos"
        )
    
    try:
        # Save file
        file_path = save_upload_file(file)
        full_path = str(UPLOAD_DIR / Path(file_path).name)
        
        result = {
            "success": True,
            "file_path": file_path,
            "file_url": f"/uploads/meter_photos/{Path(file_path).name}",
            "uploaded_by": current_user.id,
            "uploaded_at": datetime.utcnow().isoformat()
        }
        
        # Process OCR if requested
        if process_ocr:
            ocr_result = extract_meter_reading(full_path)
            result["ocr"] = ocr_result
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.post("/process-ocr")
async def process_ocr_only(
    file_path: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """
    Process OCR on an already uploaded image
    """
    if current_user.role not in [UserRole.TECHNICIAN, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only technicians and admins can process OCR"
        )
    
    # Construct full path
    full_path = str(UPLOAD_DIR / Path(file_path).name)
    
    if not Path(full_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found"
        )
    
    # Process OCR
    ocr_result = extract_meter_reading(full_path)
    
    return ocr_result


@router.post("/barcode-scan")
async def process_barcode(
    barcode_data: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """
    Process scanned barcode data
    Returns device/customer information if found
    """
    from server import db
    
    # Look for device with matching barcode
    device = await db.devices.find_one(
        {"device_id": barcode_data},
        {"_id": 0}
    )
    
    if device:
        return {
            "success": True,
            "type": "device",
            "data": device
        }
    
    # Look for customer with matching number
    customer = await db.customers.find_one(
        {"customer_number": barcode_data},
        {"_id": 0}
    )
    
    if customer:
        return {
            "success": True,
            "type": "customer",
            "data": customer
        }
    
    return {
        "success": False,
        "error": "No matching device or customer found"
    }
