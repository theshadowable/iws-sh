from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class TicketCategory(str, Enum):
    TECHNICAL_ISSUE = "technical_issue"
    WATER_QUALITY = "water_quality"
    MAINTENANCE_REPAIRS = "maintenance_repairs"
    GENERAL_INQUIRY = "general_inquiry"

class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    APPROVE = "approve"
    CLOSED = "closed"

class SignatureType(str, Enum):
    APPROVAL = "approval"
    COMPLETION = "completion"

# Request/Response Models
class GPSCoordinates(BaseModel):
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    timestamp: Optional[datetime] = None

class TicketAttachment(BaseModel):
    id: str
    ticket_id: str
    file_path: str
    file_name: str
    file_type: str
    file_size: int
    uploaded_by: str
    uploaded_at: datetime
    gps_coordinates: Optional[GPSCoordinates] = None
    timestamp_metadata: Optional[datetime] = None

class TicketMessage(BaseModel):
    id: str
    ticket_id: str
    user_id: str
    user_name: str
    user_role: str
    message: str
    created_at: datetime
    is_internal: bool = False  # For admin/technician notes only
    attachments: List[str] = []

class TicketSignature(BaseModel):
    id: str
    ticket_id: str
    signature_data: str  # Base64 encoded signature image
    signed_by: str
    signed_by_name: str
    signed_at: datetime
    signature_type: SignatureType
    gps_coordinates: Optional[GPSCoordinates] = None

class SupportTicket(BaseModel):
    id: str
    ticket_number: str  # Human-readable ticket number (e.g., TKT-2025-0001)
    customer_id: str
    customer_name: str
    customer_email: str
    assigned_to: Optional[str] = None  # Technician ID
    assigned_to_name: Optional[str] = None
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus
    subject: str
    description: str
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    attachments: List[TicketAttachment] = []
    messages_count: int = 0
    last_message_at: Optional[datetime] = None
    signature_id: Optional[str] = None

# Create Ticket Request
class CreateTicketRequest(BaseModel):
    category: TicketCategory
    priority: TicketPriority
    subject: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    gps_coordinates: Optional[GPSCoordinates] = None

# Update Ticket Request
class UpdateTicketRequest(BaseModel):
    category: Optional[TicketCategory] = None
    priority: Optional[TicketPriority] = None
    subject: Optional[str] = None
    description: Optional[str] = None

# Add Message Request
class AddMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    is_internal: bool = False

# Assign Ticket Request
class AssignTicketRequest(BaseModel):
    assigned_to: str  # Technician ID

# Update Status Request
class UpdateStatusRequest(BaseModel):
    status: TicketStatus
    notes: Optional[str] = None

# Add Signature Request
class AddSignatureRequest(BaseModel):
    signature_data: str  # Base64 encoded
    signature_type: SignatureType
    gps_coordinates: Optional[GPSCoordinates] = None

# Ticket Statistics
class TicketStats(BaseModel):
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    resolved_tickets: int
    closed_tickets: int
    critical_tickets: int
    my_assigned_tickets: int
    avg_resolution_time: float  # In hours
    tickets_by_category: dict
    tickets_by_priority: dict

# Ticket List Response
class TicketListResponse(BaseModel):
    tickets: List[SupportTicket]
    total: int
    page: int
    limit: int
    has_more: bool
