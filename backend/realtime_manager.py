"""
Real-time Data Manager
Handles WebSocket connections and broadcasts real-time IoT data to connected clients
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, List
from datetime import datetime
import json
import asyncio
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time data streaming"""
    
    def __init__(self):
        # Store active connections: {session_id: websocket}
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Store device subscriptions: {device_id: set of session_ids}
        self.device_subscriptions: Dict[str, Set[str]] = {}
        
        # Store user subscriptions: {user_id: session_id}
        self.user_connections: Dict[str, str] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str, user_id: str = None):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        
        if user_id:
            self.user_connections[user_id] = session_id
        
        logger.info(f"WebSocket connected: {session_id} (user: {user_id})")
        return session_id
    
    def disconnect(self, session_id: str, user_id: str = None):
        """Remove WebSocket connection"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        
        # Remove from device subscriptions
        for device_id in list(self.device_subscriptions.keys()):
            if session_id in self.device_subscriptions[device_id]:
                self.device_subscriptions[device_id].remove(session_id)
                
                if not self.device_subscriptions[device_id]:
                    del self.device_subscriptions[device_id]
        
        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]
        
        logger.info(f"WebSocket disconnected: {session_id}")
    
    def subscribe_to_device(self, session_id: str, device_id: str):
        """Subscribe a connection to device updates"""
        if device_id not in self.device_subscriptions:
            self.device_subscriptions[device_id] = set()
        
        self.device_subscriptions[device_id].add(session_id)
        logger.info(f"Session {session_id} subscribed to device {device_id}")
    
    def unsubscribe_from_device(self, session_id: str, device_id: str):
        """Unsubscribe a connection from device updates"""
        if device_id in self.device_subscriptions:
            self.device_subscriptions[device_id].discard(session_id)
            
            if not self.device_subscriptions[device_id]:
                del self.device_subscriptions[device_id]
    
    async def send_personal_message(self, message: dict, session_id: str):
        """Send message to specific connection"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {session_id}: {e}")
                self.disconnect(session_id)
    
    async def broadcast_to_device_subscribers(self, device_id: str, message: dict):
        """Broadcast message to all connections subscribed to a device"""
        if device_id not in self.device_subscriptions:
            return
        
        disconnected_sessions = []
        
        for session_id in self.device_subscriptions[device_id]:
            if session_id in self.active_connections:
                websocket = self.active_connections[session_id]
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {session_id}: {e}")
                    disconnected_sessions.append(session_id)
        
        # Clean up disconnected sessions
        for session_id in disconnected_sessions:
            self.disconnect(session_id)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected_sessions = []
        
        for session_id, websocket in list(self.active_connections.items()):
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {session_id}: {e}")
                disconnected_sessions.append(session_id)
        
        # Clean up disconnected sessions
        for session_id in disconnected_sessions:
            self.disconnect(session_id)
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)
    
    def get_device_subscriber_count(self, device_id: str) -> int:
        """Get number of subscribers for a device"""
        return len(self.device_subscriptions.get(device_id, set()))


# Global connection manager instance
manager = ConnectionManager()


# Helper functions for broadcasting IoT data
async def broadcast_device_reading(device_id: str, reading_data: dict):
    """Broadcast device reading to all subscribers"""
    message = {
        "type": "device_reading",
        "device_id": device_id,
        "data": reading_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.broadcast_to_device_subscribers(device_id, message)


async def broadcast_device_status(device_id: str, status_data: dict):
    """Broadcast device status change to all subscribers"""
    message = {
        "type": "device_status",
        "device_id": device_id,
        "data": status_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.broadcast_to_device_subscribers(device_id, message)


async def broadcast_alert(device_id: str, alert_data: dict):
    """Broadcast alert to all subscribers"""
    message = {
        "type": "alert",
        "device_id": device_id,
        "data": alert_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.broadcast_to_device_subscribers(device_id, message)
