import React, { useState, useEffect, useRef } from 'react';

const WebSocketHeartbeat = ({ wsUrl = 'ws://localhost:5000/ws/heartbeat' }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastHeartbeat, setLastHeartbeat] = useState(null);
  const [connectionError, setConnectionError] = useState(null);
  const [heartbeatData, setHeartbeatData] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  const connectWebSocket = () => {
    try {
      // Clean up existing connection
      if (wsRef.current) {
        wsRef.current.close();
      }

      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setConnectionError(null);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'heartbeat') {
            setHeartbeatData(data);
            setLastHeartbeat(new Date());
          }
        } catch (error) {
          console.error('Error parsing message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionError('WebSocket connection error');
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        
        // Attempt to reconnect after 5 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('Attempting to reconnect...');
          connectWebSocket();
        }, 5000);
      };
    } catch (error) {
      setConnectionError(error.message);
      setIsConnected(false);
    }
  };

  useEffect(() => {
    connectWebSocket();

    // Cleanup on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [wsUrl]);

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
    }
  };

  const reconnect = () => {
    disconnect();
    setTimeout(connectWebSocket, 100);
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h2>WebSocket Heartbeat Monitor</h2>
      
      <div style={{ marginBottom: '20px' }}>
        <span style={{
          display: 'inline-block',
          width: '12px',
          height: '12px',
          borderRadius: '50%',
          backgroundColor: isConnected ? '#4CAF50' : '#f44336',
          marginRight: '10px'
        }}></span>
        <strong>Status:</strong> {isConnected ? 'Connected' : 'Disconnected'}
      </div>

      {connectionError && (
        <div style={{
          padding: '10px',
          backgroundColor: '#f8d7da',
          border: '1px solid #f5c6cb',
          borderRadius: '5px',
          marginBottom: '20px'
        }}>
          <strong>Error:</strong> {connectionError}
        </div>
      )}

      {heartbeatData && (
        <div style={{
          padding: '15px',
          backgroundColor: '#d4edda',
          border: '1px solid #c3e6cb',
          borderRadius: '5px',
          marginBottom: '20px'
        }}>
          <h3 style={{ marginTop: 0 }}>Latest Heartbeat</h3>
          <p><strong>Status:</strong> {heartbeatData.status}</p>
          <p><strong>Server Time:</strong> {new Date(heartbeatData.timestamp).toLocaleString()}</p>
          <p><strong>Uptime:</strong> {Math.floor(heartbeatData.uptime_seconds / 60)} minutes</p>
        </div>
      )}

      {lastHeartbeat && (
        <p style={{ color: '#666' }}>
          Last heartbeat received: {lastHeartbeat.toLocaleString()}
        </p>
      )}

      <div style={{ marginTop: '20px' }}>
        <button
          onClick={reconnect}
          style={{
            padding: '10px 20px',
            marginRight: '10px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          Reconnect
        </button>
        
        <button
          onClick={disconnect}
          disabled={!isConnected}
          style={{
            padding: '10px 20px',
            backgroundColor: isConnected ? '#dc3545' : '#ccc',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: isConnected ? 'pointer' : 'not-allowed'
          }}
        >
          Disconnect
        </button>
      </div>
    </div>
  );
};

export default WebSocketHeartbeat;