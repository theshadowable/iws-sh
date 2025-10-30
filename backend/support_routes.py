from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
import json
import os

from auth import get_current_user, User
from support_models import (
    SupportTicket, CreateTicketRequest, UpdateTicketRequest,
    AddMessageRequest, AssignTicketRequest, UpdateStatusRequest,
    AddSignatureRequest, TicketStats, TicketListResponse,
    TicketMessage, TicketAttachment, TicketSignature,
    TicketCategory, TicketPriority, TicketStatus, GPSCoordinates
)
from email_service import email_service
from file_service import file_service

router = APIRouter(prefix="/tickets", tags=["Support Tickets"])

# Database connection - import from server to avoid environment variable issues
from server import db as db_client

# Helper function to generate ticket number
async def generate_ticket_number() -> str:
    """Generate unique ticket number (TKT-2025-0001)"""
    year = datetime.utcnow().year
    
    # Count tickets created this year
    count = await db_client.support_tickets.count_documents({
        "created_at": {"$gte": datetime(year, 1, 1)}
    })
    
    ticket_number = f"TKT-{year}-{str(count + 1).zfill(4)}"
    return ticket_number

# Helper to get ticket by ID with permission check
async def get_ticket_with_permission(ticket_id: str, current_user: User):
    """Get ticket and check user permission"""
    ticket = await db_client.support_tickets.find_one({"id": ticket_id})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check permission
    user_role = current_user.role
    user_id = current_user.id
    
    # Customer can only view their own tickets
    if user_role == "customer" and ticket['customer_id'] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Admin and technician can view all tickets
    return ticket

# ============================================================================
# CUSTOMER & GENERAL ENDPOINTS
# ============================================================================

@router.post("/", response_model=SupportTicket)
async def create_ticket(
    request: CreateTicketRequest,
    current_user: User = Depends(get_current_user),

):
    """Create new support ticket - Fixed customer lookup"""
    try:
        from bson import ObjectId
        import logging
        
        logger = logging.getLogger(__name__)
        
        ticket_id = str(uuid.uuid4())
        ticket_number = await generate_ticket_number()
        now = datetime.utcnow()
        
        # Get customer info - Try both id field and _id field
        customer = await db_client.users.find_one({
            "$or": [
                {"id": current_user.id},
                {"_id": ObjectId(current_user.id)}
            ]
        })
        
        if not customer:
            # If still not found, log the issue and use current_user data
            logger.warning(f"Customer lookup failed for user_id: {current_user.id}, using current_user data")
            customer_name = current_user.full_name or current_user.email
            customer_email = current_user.email
        else:
            customer_name = customer.get('full_name', customer.get('email'))
            customer_email = customer.get('email')
        
        ticket_data = {
            "id": ticket_id,
            "ticket_number": ticket_number,
            "customer_id": current_user.id,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "assigned_to": None,
            "assigned_to_name": None,
            "category": request.category,
            "priority": request.priority,
            "status": TicketStatus.OPEN,
            "subject": request.subject,
            "description": request.description,
            "created_at": now,
            "updated_at": now,
            "resolved_at": None,
            "closed_at": None,
            "attachments": [],
            "messages_count": 0,
            "last_message_at": None,
            "signature_id": None
        }
        
        # Add GPS coordinates if provided
        if request.gps_coordinates:
            ticket_data['gps_coordinates'] = request.gps_coordinates.dict()
        
        await db_client.support_tickets.insert_one(ticket_data)
        
        # Send email notification with error handling
        try:
            email_service.send_ticket_created_notification({
                'ticket_number': ticket_number,
                'customer_name': customer_name,
                'customer_email': customer_email,
                'category': request.category,
                'priority': request.priority,
                'subject': request.subject,
                'description': request.description,
                'created_at': now.strftime('%Y-%m-%d %H:%M:%S')
            })
        except Exception as email_error:
            logger.warning(f"Failed to send email notification: {email_error}")
        
        logger.info(f"✅ Ticket created: {ticket_number}")
        return SupportTicket(**ticket_data)
        
    except Exception as e:
        logger.error(f"❌ Error creating ticket: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to create ticket: {str(e)}")

@router.get("/", response_model=TicketListResponse)
async def get_tickets(
    status: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),

):
    """Get tickets (filtered by user role)"""
    try:
        query = {}
        
        # Customer can only see their own tickets
        if current_user.role == "customer":
            query['customer_id'] = current_user.id
        
        # Technician sees assigned tickets
        elif current_user.role == "technician":
            query['$or'] = [
                {'assigned_to': current_user.id},
                {'assigned_to': None}  # Unassigned tickets
            ]
        
        # Admin sees all tickets (no filter)
        
        # Apply filters
        if status:
            query['status'] = status
        if category:
            query['category'] = category
        if priority:
            query['priority'] = priority
        
        # Count total
        total = await db_client.support_tickets.count_documents(query)
        
        # Get paginated tickets
        skip = (page - 1) * limit
        cursor = db_client.support_tickets.find(query).sort("created_at", -1).skip(skip).limit(limit)
        tickets = await cursor.to_list(length=limit)
        
        has_more = (skip + len(tickets)) < total
        
        return TicketListResponse(
            tickets=[SupportTicket(**t) for t in tickets],
            total=total,
            page=page,
            limit=limit,
            has_more=has_more
        )
        
    except Exception as e:
        print(f"❌ Error getting tickets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ticket_id}", response_model=SupportTicket)
async def get_ticket_detail(
    ticket_id: str,
    current_user: User = Depends(get_current_user),

):
    """Get ticket detail"""
    ticket = await get_ticket_with_permission(ticket_id, current_user)
    return SupportTicket(**ticket)

@router.put("/{ticket_id}", response_model=SupportTicket)
async def update_ticket(
    ticket_id: str,
    request: UpdateTicketRequest,
    current_user: User = Depends(get_current_user),

):
    """Update ticket (customer can update their own tickets if status is OPEN)"""
    ticket = await get_ticket_with_permission(ticket_id, current_user)
    
    # Only allow updates if ticket is OPEN
    if ticket['status'] != TicketStatus.OPEN:
        raise HTTPException(status_code=400, detail="Cannot update ticket that is not OPEN")
    
    # Prepare update data
    update_data = {"updated_at": datetime.utcnow()}
    
    if request.category:
        update_data['category'] = request.category
    if request.priority:
        update_data['priority'] = request.priority
    if request.subject:
        update_data['subject'] = request.subject
    if request.description:
        update_data['description'] = request.description
    
    await db_client.support_tickets.update_one(
        {"id": ticket_id},
        {"$set": update_data}
    )
    
    updated_ticket = await db_client.support_tickets.find_one({"id": ticket_id})
    return SupportTicket(**updated_ticket)

@router.delete("/{ticket_id}")
async def delete_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_user),

):
    """Delete ticket (only customer's own OPEN tickets or admin)"""
    ticket = await get_ticket_with_permission(ticket_id, current_user)
    
    # Customer can only delete their own OPEN tickets
    if current_user.role == "customer":
        if ticket['status'] != TicketStatus.OPEN:
            raise HTTPException(status_code=400, detail="Can only delete OPEN tickets")
    
    # Delete ticket and related data
    await db_client.support_tickets.delete_one({"id": ticket_id})
    await db_client.ticket_messages.delete_many({"ticket_id": ticket_id})
    
    # Delete attachments and signatures
    for attachment in ticket.get('attachments', []):
        file_service.delete_file(attachment['id'], 'attachment')
    
    if ticket.get('signature_id'):
        file_service.delete_file(ticket['signature_id'], 'signature')
    
    return {"message": "Ticket deleted successfully"}

# ============================================================================
# TICKET MESSAGES
# ============================================================================

@router.post("/{ticket_id}/messages", response_model=TicketMessage)
async def add_message(
    ticket_id: str,
    request: AddMessageRequest,
    current_user: User = Depends(get_current_user),

):
    """Add message to ticket"""
    ticket = await get_ticket_with_permission(ticket_id, current_user)
    
    # Cannot add message to closed tickets
    if ticket['status'] == TicketStatus.CLOSED:
        raise HTTPException(status_code=400, detail="Cannot add message to closed ticket")
    
    message_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    # Get user info
    user = await db_client.users.find_one({"id": current_user.id})
    
    message_data = {
        "id": message_id,
        "ticket_id": ticket_id,
        "user_id": current_user.id,
        "user_name": user.get('full_name', user.get('email')),
        "user_role": current_user.role,
        "message": request.message,
        "created_at": now,
        "is_internal": request.is_internal if current_user.role in ["admin", "technician"] else False,
        "attachments": []
    }
    
    await db_client.ticket_messages.insert_one(message_data)
    
    # Update ticket
    await db_client.support_tickets.update_one(
        {"id": ticket_id},
        {
            "$set": {"last_message_at": now, "updated_at": now},
            "$inc": {"messages_count": 1}
        }
    )
    
    print(f"✅ Message added to ticket {ticket['ticket_number']}")
    return TicketMessage(**message_data)

@router.get("/{ticket_id}/messages", response_model=List[TicketMessage])
async def get_messages(
    ticket_id: str,
    current_user: User = Depends(get_current_user),

):
    """Get all messages for a ticket"""
    ticket = await get_ticket_with_permission(ticket_id, current_user)
    
    query = {"ticket_id": ticket_id}
    
    # Customers cannot see internal messages
    if current_user.role == "customer":
        query['is_internal'] = False
    
    messages = await db_client.ticket_messages.find(query).sort("created_at", 1).to_list(1000)
    return [TicketMessage(**m) for m in messages]

# ============================================================================
# TICKET ATTACHMENTS (with GPS + Timestamp)
# ============================================================================

@router.post("/{ticket_id}/attachments", response_model=TicketAttachment)
async def upload_attachment(
    ticket_id: str,
    file: UploadFile = File(...),
    gps_latitude: Optional[float] = Form(None),
    gps_longitude: Optional[float] = Form(None),
    gps_accuracy: Optional[float] = Form(None),
    current_user: User = Depends(get_current_user),

):
    """Upload file attachment with GPS coordinates and timestamp"""
    ticket = await get_ticket_with_permission(ticket_id, current_user)
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Validate file size (max 10MB)
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        
        # Prepare GPS coordinates
        gps_coords = None
        if gps_latitude is not None and gps_longitude is not None:
            gps_coords = {
                'latitude': gps_latitude,
                'longitude': gps_longitude,
                'accuracy': gps_accuracy,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Validate GPS
            if not file_service.validate_gps_coordinates(gps_coords):
                raise HTTPException(status_code=400, detail="Invalid GPS coordinates")
        
        # Save file with metadata
        file_metadata = file_service.save_ticket_attachment(
            file_content=file_content,
            file_name=file.filename,
            file_type=file.content_type,
            ticket_id=ticket_id,
            uploaded_by=current_user.id,
            gps_coordinates=gps_coords
        )
        
        # Add to ticket attachments array
        attachment_data = {
            "id": file_metadata['id'],
            "ticket_id": ticket_id,
            "file_path": file_metadata['file_path'],
            "file_name": file_metadata['file_name'],
            "file_type": file_metadata['file_type'],
            "file_size": file_metadata['file_size'],
            "uploaded_by": current_user.id,
            "uploaded_at": datetime.fromisoformat(file_metadata['uploaded_at']),
            "gps_coordinates": GPSCoordinates(**gps_coords) if gps_coords else None,
            "timestamp_metadata": datetime.fromisoformat(file_metadata['timestamp_metadata'])
        }
        
        await db_client.support_tickets.update_one(
            {"id": ticket_id},
            {
                "$push": {"attachments": file_metadata},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        print(f"✅ Attachment uploaded to ticket {ticket['ticket_number']}")
        return TicketAttachment(**attachment_data)
        
    except Exception as e:
        print(f"❌ Error uploading attachment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ticket_id}/attachments/{attachment_id}")
async def download_attachment(
    ticket_id: str,
    attachment_id: str,
    current_user: User = Depends(get_current_user),

):
    """Download ticket attachment"""
    ticket = await get_ticket_with_permission(ticket_id, current_user)
    
    # Find attachment
    attachment = next((a for a in ticket.get('attachments', []) if a['id'] == attachment_id), None)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    file_path = attachment['file_path']
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server")
    
    return FileResponse(file_path, filename=attachment['file_name'])

# ============================================================================
# DIGITAL SIGNATURES
# ============================================================================

@router.post("/{ticket_id}/signature", response_model=TicketSignature)
async def add_signature(
    ticket_id: str,
    request: AddSignatureRequest,
    current_user: User = Depends(get_current_user),

):
    """Add digital signature to ticket (for approval or completion)"""
    ticket = await get_ticket_with_permission(ticket_id, current_user)
    
    # Validate signature type
    if request.signature_type == "approval":
        # Customer signs for approval
        if current_user.role != "customer":
            raise HTTPException(status_code=403, detail="Only customer can sign approval")
        if ticket['status'] != TicketStatus.APPROVE:
            raise HTTPException(status_code=400, detail="Ticket must be in APPROVE status")
    
    elif request.signature_type == "completion":
        # Technician signs for completion
        if current_user.role not in ["admin", "technician"]:
            raise HTTPException(status_code=403, detail="Only technician can sign completion")
        if ticket['status'] not in [TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED]:
            raise HTTPException(status_code=400, detail="Invalid ticket status for completion signature")
    
    try:
        # Validate GPS if provided
        gps_coords = None
        if request.gps_coordinates:
            gps_coords = request.gps_coordinates.dict()
            if not file_service.validate_gps_coordinates(gps_coords):
                raise HTTPException(status_code=400, detail="Invalid GPS coordinates")
        
        # Get user info
        user = await db_client.users.find_one({"id": current_user.id})
        
        # Save signature
        signature_metadata = file_service.save_signature(
            signature_data=request.signature_data,
            ticket_id=ticket_id,
            signed_by=current_user.id,
            signature_type=request.signature_type,
            gps_coordinates=gps_coords
        )
        
        # Prepare signature data
        signature_data = {
            "id": signature_metadata['id'],
            "ticket_id": ticket_id,
            "signature_data": f"/api/tickets/{ticket_id}/signature-image/{signature_metadata['id']}",
            "signed_by": current_user.id,
            "signed_by_name": user.get('full_name', user.get('email')),
            "signed_at": datetime.fromisoformat(signature_metadata['signed_at']),
            "signature_type": request.signature_type,
            "gps_coordinates": GPSCoordinates(**gps_coords) if gps_coords else None
        }
        
        # Update ticket with signature
        update_data = {
            "signature_id": signature_metadata['id'],
            "updated_at": datetime.utcnow()
        }
        
        # If approval signature, move to CLOSED
        if request.signature_type == "approval":
            update_data['status'] = TicketStatus.CLOSED
            update_data['closed_at'] = datetime.utcnow()
        
        await db_client.support_tickets.update_one(
            {"id": ticket_id},
            {"$set": update_data}
        )
        
        # Store signature in separate collection for reference
        await db_client.ticket_signatures.insert_one(signature_metadata)
        
        print(f"✅ Signature added to ticket {ticket['ticket_number']}")
        return TicketSignature(**signature_data)
        
    except Exception as e:
        print(f"❌ Error adding signature: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ticket_id}/signature-image/{signature_id}")
async def get_signature_image(
    ticket_id: str,
    signature_id: str,
    current_user: User = Depends(get_current_user),

):
    """Get signature image file"""
    ticket = await get_ticket_with_permission(ticket_id, current_user)
    
    # Get signature metadata
    signature = file_service.get_file_metadata(signature_id, 'signature')
    if not signature:
        raise HTTPException(status_code=404, detail="Signature not found")
    
    signature_path = signature['signature_path']
    if not os.path.exists(signature_path):
        raise HTTPException(status_code=404, detail="Signature file not found")
    
    return FileResponse(signature_path, media_type="image/png")

# ============================================================================
# ADMIN/TECHNICIAN ENDPOINTS
# ============================================================================

@router.patch("/{ticket_id}/assign", response_model=SupportTicket)
async def assign_ticket(
    ticket_id: str,
    request: AssignTicketRequest,
    current_user: User = Depends(get_current_user),

):
    """Assign ticket to technician (admin or technician can assign)"""
    if current_user.role not in ["admin", "technician"]:
        raise HTTPException(status_code=403, detail="Only admin or technician can assign tickets")
    
    ticket = await db_client.support_tickets.find_one({"id": ticket_id})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Verify technician exists
    technician = await db_client.users.find_one({"id": request.assigned_to, "role": "technician"})
    if not technician:
        raise HTTPException(status_code=404, detail="Technician not found")
    
    # Update ticket
    await db_client.support_tickets.update_one(
        {"id": ticket_id},
        {
            "$set": {
                "assigned_to": request.assigned_to,
                "assigned_to_name": technician.get('full_name', technician.get('email')),
                "status": TicketStatus.IN_PROGRESS if ticket['status'] == TicketStatus.OPEN else ticket['status'],
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # Send email notification to technician
    email_service.send_ticket_assigned_notification(
        {
            'ticket_number': ticket['ticket_number'],
            'customer_name': ticket['customer_name'],
            'category': ticket['category'],
            'priority': ticket['priority'],
            'subject': ticket['subject'],
            'description': ticket['description'],
            'assigned_to_name': technician.get('full_name', technician.get('email'))
        },
        technician.get('email')
    )
    
    updated_ticket = await db_client.support_tickets.find_one({"id": ticket_id})
    print(f"✅ Ticket {ticket['ticket_number']} assigned to {technician.get('full_name')}")
    return SupportTicket(**updated_ticket)

@router.patch("/{ticket_id}/status", response_model=SupportTicket)
async def update_ticket_status(
    ticket_id: str,
    request: UpdateStatusRequest,
    current_user: User = Depends(get_current_user),

):
    """Update ticket status (admin/technician)"""
    if current_user.role not in ["admin", "technician"]:
        raise HTTPException(status_code=403, detail="Only admin or technician can update status")
    
    ticket = await db_client.support_tickets.find_one({"id": ticket_id})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    old_status = ticket['status']
    new_status = request.status
    
    # Prepare update data
    update_data = {
        "status": new_status,
        "updated_at": datetime.utcnow()
    }
    
    # Set timestamps based on status
    if new_status == TicketStatus.RESOLVED and old_status != TicketStatus.RESOLVED:
        update_data['resolved_at'] = datetime.utcnow()
    
    if new_status == TicketStatus.CLOSED and old_status != TicketStatus.CLOSED:
        update_data['closed_at'] = datetime.utcnow()
    
    await db_client.support_tickets.update_one(
        {"id": ticket_id},
        {"$set": update_data}
    )
    
    # Add status update as internal message if notes provided
    if request.notes:
        message_data = {
            "id": str(uuid.uuid4()),
            "ticket_id": ticket_id,
            "user_id": current_user.id,
            "user_name": current_user.full_name if hasattr(current_user, 'full_name') else current_user.email,
            "user_role": current_user.role,
            "message": f"Status changed from {old_status} to {new_status}. Notes: {request.notes}",
            "created_at": datetime.utcnow(),
            "is_internal": True,
            "attachments": []
        }
        await db_client.ticket_messages.insert_one(message_data)
    
    # Send email notification to customer
    email_service.send_ticket_status_update_notification(
        {
            'ticket_number': ticket['ticket_number'],
            'customer_name': ticket['customer_name'],
            'customer_email': ticket['customer_email'],
            'subject': ticket['subject']
        },
        old_status,
        new_status
    )
    
    updated_ticket = await db_client.support_tickets.find_one({"id": ticket_id})
    print(f"✅ Ticket {ticket['ticket_number']} status updated: {old_status} → {new_status}")
    return SupportTicket(**updated_ticket)

@router.get("/admin/stats", response_model=TicketStats)
async def get_ticket_statistics(
    current_user: User = Depends(get_current_user),

):
    """Get ticket statistics (admin/technician)"""
    if current_user.role not in ["admin", "technician"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Total tickets
        total_tickets = await db_client.support_tickets.count_documents({})
        
        # By status
        open_tickets = await db_client.support_tickets.count_documents({"status": TicketStatus.OPEN})
        in_progress_tickets = await db_client.support_tickets.count_documents({"status": TicketStatus.IN_PROGRESS})
        resolved_tickets = await db_client.support_tickets.count_documents({"status": TicketStatus.RESOLVED})
        closed_tickets = await db_client.support_tickets.count_documents({"status": TicketStatus.CLOSED})
        
        # Critical tickets
        critical_tickets = await db_client.support_tickets.count_documents({"priority": TicketPriority.CRITICAL, "status": {"$nin": [TicketStatus.CLOSED]}})
        
        # My assigned tickets (for technician)
        my_assigned_tickets = 0
        if current_user.role == "technician":
            my_assigned_tickets = await db_client.support_tickets.count_documents({"assigned_to": current_user.id, "status": {"$nin": [TicketStatus.CLOSED]}})
        
        # Calculate average resolution time
        resolved_with_times_cursor = db_client.support_tickets.find({
            "status": {"$in": [TicketStatus.RESOLVED, TicketStatus.CLOSED]},
            "resolved_at": {"$exists": True}
        })
        resolved_with_times = await resolved_with_times_cursor.to_list(length=None)
        
        avg_resolution_time = 0
        if resolved_with_times:
            total_hours = 0
            for ticket in resolved_with_times:
                if ticket.get('resolved_at') and ticket.get('created_at'):
                    delta = ticket['resolved_at'] - ticket['created_at']
                    total_hours += delta.total_seconds() / 3600
            avg_resolution_time = total_hours / len(resolved_with_times)
        
        # By category
        tickets_by_category = {}
        for category in TicketCategory:
            count = await db_client.support_tickets.count_documents({"category": category})
            tickets_by_category[category] = count
        
        # By priority
        tickets_by_priority = {}
        for priority in TicketPriority:
            count = await db_client.support_tickets.count_documents({"priority": priority})
            tickets_by_priority[priority] = count
        
        return TicketStats(
            total_tickets=total_tickets,
            open_tickets=open_tickets,
            in_progress_tickets=in_progress_tickets,
            resolved_tickets=resolved_tickets,
            closed_tickets=closed_tickets,
            critical_tickets=critical_tickets,
            my_assigned_tickets=my_assigned_tickets,
            avg_resolution_time=avg_resolution_time,
            tickets_by_category=tickets_by_category,
            tickets_by_priority=tickets_by_priority
        )
        
    except Exception as e:
        print(f"❌ Error getting ticket stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
