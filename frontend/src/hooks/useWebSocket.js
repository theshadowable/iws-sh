import { useState, useEffect, useRef, useCallback } from 'react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const WS_URL = BACKEND_URL.replace('http', 'ws');

export const useWebSocket = (sessionId) => {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [lastMessage, setLastMessage] = useState(null);
  const ws = useRef(null);
  const reconnectTimeout = useRef(null);
  const reconnectAttempts = useRef(0);
  const pingIntervalRef = useRef(null);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    // Don't connect if sessionId is invalid
    if (!sessionId || sessionId === 'undefined' || sessionId === 'null') {
      console.warn('Invalid sessionId, skipping WebSocket connection');
      return;
    }

    try {
      const wsUrl = `${WS_URL}/api/iot/ws/${sessionId}`;
      console.log('Connecting to WebSocket:', wsUrl);
      
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        reconnectAttempts.current = 0;
        
        // Send ping every 30 seconds to keep connection alive
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
        }
        
        pingIntervalRef.current = setInterval(() => {
          if (ws.current?.readyState === WebSocket.OPEN) {
            sendMessage({ type: 'ping' });
          }
        }, 30000);
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('WebSocket message:', data);
          setLastMessage(data);
          setMessages(prev => [...prev.slice(-99), data]); // Keep last 100 messages
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.current.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        
        // Clear ping interval
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }
        
        // Attempt to reconnect
        if (reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current += 1;
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
          console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttempts.current}/${maxReconnectAttempts})`);
          
          reconnectTimeout.current = setTimeout(() => {
            connect();
          }, delay);
        }
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
    }
  }, [sessionId]);

  const disconnect = useCallback(() => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
      reconnectTimeout.current = null;
    }
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((message) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
      return true;
    }
    console.warn('WebSocket not connected, cannot send message');
    return false;
  }, []);

  const subscribe = useCallback((deviceId) => {
    return sendMessage({ type: 'subscribe', device_id: deviceId });
  }, [sendMessage]);

  const unsubscribe = useCallback((deviceId) => {
    return sendMessage({ type: 'unsubscribe', device_id: deviceId });
  }, [sendMessage]);

  useEffect(() => {
    connect();
    
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    messages,
    lastMessage,
    sendMessage,
    subscribe,
    unsubscribe,
    reconnect: connect,
    disconnect
  };
};
