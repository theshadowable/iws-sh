"""
Chatbot API Routes for AI-powered customer support
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os

from auth import get_current_user
from chat_models import (
    SendMessageRequest, 
    SendMessageResponse,
    CreateTicketRequest,
    CreateTicketResponse,
    ChatMessage,
    ChatSession,
    SupportTicket,
    MessageRole,
    TicketStatus
)
from chatbot_service import chatbot_service

router = APIRouter(prefix="/chat", tags=["Chatbot"])

# Database connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'indowater_db')]


@router.post("/message", response_model=SendMessageResponse)
async def send_chat_message(
    request: SendMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Send a message to the AI chatbot
    """
    try:
        customer_id = current_user["id"]
        
        # Get or create session
        if request.session_id:
            session_id = request.session_id
            # Update existing session
            await db.chat_sessions.update_one(
                {"id": session_id},
                {
                    "$set": {
                        "last_message_at": datetime.utcnow(),
                        "is_active": True
                    },
                    "$inc": {"message_count": 1}
                }
            )
        else:
            # Create new session
            session = ChatSession(
                customer_id=customer_id,
                customer_name=current_user.get("full_name"),
                customer_email=current_user.get("email")
            )
            session_id = session.id
            await db.chat_sessions.insert_one(session.dict())
        
        # Save user message
        user_msg = ChatMessage(
            session_id=session_id,
            customer_id=customer_id,
            role=MessageRole.USER,
            content=request.message
        )
        await db.chat_messages.insert_one(user_msg.dict())
        
        # Get customer context for better responses
        customer_context = {
            "name": current_user.get("full_name"),
            "email": current_user.get("email"),
        }
        
        # Get current balance if customer role
        if current_user.get("role") == "customer":
            customer_doc = await db.customers.find_one({"user_id": customer_id})
            if customer_doc:
                customer_context["balance"] = customer_doc.get("balance", 0)
        
        # Get AI response
        ai_result = await chatbot_service.send_message(
            message=request.message,
            session_id=session_id,
            customer_context=customer_context
        )
        
        # Save assistant message
        assistant_msg = ChatMessage(
            session_id=session_id,
            customer_id=customer_id,
            role=MessageRole.ASSISTANT,
            content=ai_result["response"],
            metadata={"suggested_actions": ai_result.get("suggested_actions")}
        )
        await db.chat_messages.insert_one(assistant_msg.dict())
        
        return SendMessageResponse(
            message=ai_result["response"],
            session_id=session_id,
            suggested_actions=ai_result.get("suggested_actions")
        )
        
    except Exception as e:
        print(f"Error in send_chat_message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(e)}"
        )


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """
    Get chat history for a specific session
    """
    try:
        # Verify session belongs to user
        session = await db.chat_sessions.find_one({
            "id": session_id,
            "customer_id": current_user["id"]
        })
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Get messages
        messages_cursor = db.chat_messages.find({
            "session_id": session_id
        }).sort("created_at", 1).limit(limit)
        
        messages = await messages_cursor.to_list(length=limit)
        
        return {
            "session": session,
            "messages": messages
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_chat_history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chat history: {str(e)}"
        )


@router.get("/sessions")
async def get_chat_sessions(
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all chat sessions for current user
    """
    try:
        sessions_cursor = db.chat_sessions.find({
            "customer_id": current_user["id"]
        }).sort("last_message_at", -1).limit(limit)
        
        sessions = await sessions_cursor.to_list(length=limit)
        
        return {
            "sessions": sessions,
            "total": len(sessions)
        }
        
    except Exception as e:
        print(f"Error in get_chat_sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chat sessions: {str(e)}"
        )


@router.post("/ticket", response_model=CreateTicketResponse)
async def create_support_ticket(
    request: CreateTicketRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a support ticket from chat
    """
    try:
        # Create ticket
        ticket = SupportTicket(
            customer_id=current_user["id"],
            customer_name=current_user.get("full_name", "Unknown"),
            customer_email=current_user.get("email", ""),
            subject=request.subject,
            description=request.description,
            category=request.category,
            priority=request.priority or "medium"
        )
        
        # Save to database
        await db.support_tickets.insert_one(ticket.dict())
        
        return CreateTicketResponse(
            ticket_id=ticket.id,
            status="created",
            message=f"Support ticket {ticket.id} created successfully. Our team will respond within 24 hours."
        )
        
    except Exception as e:
        print(f"Error in create_support_ticket: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create support ticket: {str(e)}"
        )


@router.get("/tickets")
async def get_support_tickets(
    status: Optional[str] = None,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """
    Get support tickets for current user
    """
    try:
        query = {"customer_id": current_user["id"]}
        
        if status:
            query["status"] = status
        
        tickets_cursor = db.support_tickets.find(query).sort("created_at", -1).limit(limit)
        tickets = await tickets_cursor.to_list(length=limit)
        
        return {
            "tickets": tickets,
            "total": len(tickets)
        }
        
    except Exception as e:
        print(f"Error in get_support_tickets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve support tickets: {str(e)}"
        )


@router.get("/ticket/{ticket_id}")
async def get_ticket_details(
    ticket_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get details of a specific support ticket
    """
    try:
        ticket = await db.support_tickets.find_one({
            "id": ticket_id,
            "customer_id": current_user["id"]
        })
        
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        return ticket
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_ticket_details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve ticket details: {str(e)}"
        )


# Admin routes for managing tickets
@router.get("/admin/tickets")
async def get_all_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 50,
    skip: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """
    Admin endpoint to get all support tickets
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        query = {}
        
        if status:
            query["status"] = status
        if priority:
            query["priority"] = priority
        
        tickets_cursor = db.support_tickets.find(query).sort("created_at", -1).skip(skip).limit(limit)
        tickets = await tickets_cursor.to_list(length=limit)
        
        total = await db.support_tickets.count_documents(query)
        
        return {
            "tickets": tickets,
            "total": total,
            "limit": limit,
            "skip": skip
        }
        
    except Exception as e:
        print(f"Error in get_all_tickets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tickets: {str(e)}"
        )


@router.put("/admin/ticket/{ticket_id}")
async def update_ticket_status(
    ticket_id: str,
    status: TicketStatus,
    notes: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Admin endpoint to update ticket status
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        if status == TicketStatus.RESOLVED or status == TicketStatus.CLOSED:
            update_data["resolved_at"] = datetime.utcnow()
        
        if notes:
            # Add notes to the ticket
            await db.support_tickets.update_one(
                {"id": ticket_id},
                {"$push": {"notes": notes}}
            )
        
        result = await db.support_tickets.update_one(
            {"id": ticket_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        return {
            "message": "Ticket updated successfully",
            "ticket_id": ticket_id,
            "new_status": status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_ticket_status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update ticket: {str(e)}"
        )
