"""
Chat and Support Ticket Models for AI-powered customer support
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Message role types"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Individual chat message"""
    id: str = Field(default_factory=lambda: str(datetime.utcnow().timestamp()))
    session_id: str
    customer_id: str
    role: MessageRole
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = None


class ChatSession(BaseModel):
    """Chat session/conversation"""
    id: str = Field(default_factory=lambda: f"session_{datetime.utcnow().timestamp()}")
    customer_id: str
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    message_count: int = 0
    tags: List[str] = []


class TicketPriority(str, Enum):
    """Support ticket priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketStatus(str, Enum):
    """Support ticket status"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketCategory(str, Enum):
    """Support ticket categories"""
    BILLING = "billing"
    TECHNICAL = "technical"
    PAYMENT = "payment"
    USAGE = "usage"
    ACCOUNT = "account"
    OTHER = "other"


class SupportTicket(BaseModel):
    """Customer support ticket"""
    id: str = Field(default_factory=lambda: f"ticket_{datetime.utcnow().timestamp()}")
    customer_id: str
    customer_name: str
    customer_email: str
    subject: str
    description: str
    category: TicketCategory
    priority: TicketPriority = TicketPriority.MEDIUM
    status: TicketStatus = TicketStatus.OPEN
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    assigned_to: Optional[str] = None
    session_id: Optional[str] = None
    notes: List[str] = []


# Request/Response models
class SendMessageRequest(BaseModel):
    """Request to send a chat message"""
    message: str
    session_id: Optional[str] = None


class SendMessageResponse(BaseModel):
    """Response from chatbot"""
    message: str
    session_id: str
    suggested_actions: Optional[List[dict]] = None


class CreateTicketRequest(BaseModel):
    """Request to create a support ticket"""
    subject: str
    description: str
    category: TicketCategory
    priority: Optional[TicketPriority] = TicketPriority.MEDIUM


class CreateTicketResponse(BaseModel):
    """Response after creating ticket"""
    ticket_id: str
    status: str
    message: str
