import React, { useState, useEffect } from 'react';
import axios from 'axios';

const HeartbeatComponent = () => {
  const [serverStatus, setServerStatus] = useState(null);
  const [lastChecked, setLastChecked] = useState(null);
  const [error, setError] = useState(null);
  const [isChecking, setIsChecking] = useState(false);

  // Backend URL - adjust this to match your backend server
  const BACKEND_URL = 'http://localhost:5000';
  const HEARTBEAT_INTERVAL = 30000; // Check every 30 seconds

  const checkHeartbeat = async () => {
    setIsChecking(true);
    setError(null);
    
    try {
      const response = await axios.get(`${BACKEND_URL}/heartbeat`, {
        timeout: 5000, // 5 second timeout
      });
      
      setServerStatus(response.data);
      setLastChecked(new Date());
    } catch (err) {
      setError({
        message: err.message,
        code: err.code,
        status: err.response?.status
      });
      setServerStatus(null);
    } finally {
      setIsChecking(false);
    }
  };

  // Alternative using fetch API
  const checkHeartbeatFetch = async () => {
    setIsChecking(true);
    setError(null);
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch(`${BACKEND_URL}/heartbeat`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }
      
      const data = await response.json();
      setServerStatus(data);
      setLastChecked(new Date());
    } catch (err) {
      setError({
        message: err.message,
        code: err.name === 'AbortError' ? 'TIMEOUT' : 'ERROR'
      });
      setServerStatus(null);
    } finally {
      setIsChecking(false);
    }
  };

  // Set up automatic heartbeat checking
  useEffect(() => {
    // Initial check
    checkHeartbeat();
    
    // Set up interval
    const intervalId = setInterval(checkHeartbeat, HEARTBEAT_INTERVAL);
    
    // Cleanup on unmount
    return () => clearInterval(intervalId);
  }, []);

  const formatUptime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    return `${hours}h ${minutes}m ${secs}s`;
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h2>Server Heartbeat Monitor</h2>
      
      <div style={{ marginBottom: '20px' }}>
        <button 
          onClick={checkHeartbeat} 
          disabled={isChecking}
          style={{
            padding: '10px 20px',
            fontSize: '16px',
            cursor: isChecking ? 'not-allowed' : 'pointer',
            backgroundColor: isChecking ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '5px'
          }}
        >
          {isChecking ? 'Checking...' : 'Check Now'}
        </button>
      </div>

      {error && (
        <div style={{ 
          padding: '10px', 
          backgroundColor: '#f8d7da', 
          border: '1px solid #f5c6cb',
          borderRadius: '5px',
          marginBottom: '20px'
        }}>
          <strong>Error:</strong> {error.message}
          {error.code && <span> (Code: {error.code})</span>}
          {error.status && <span> (Status: {error.status})</span>}
        </div>
      )}

      {serverStatus && (
        <div style={{ 
          padding: '15px', 
          backgroundColor: '#d4edda', 
          border: '1px solid #c3e6cb',
          borderRadius: '5px'
        }}>
          <h3 style={{ marginTop: 0 }}>Server Status: {serverStatus.status}</h3>
          <p><strong>Message:</strong> {serverStatus.message}</p>
          <p><strong>Timestamp:</strong> {new Date(serverStatus.timestamp).toLocaleString()}</p>
          <p><strong>Uptime:</strong> {formatUptime(serverStatus.uptime_seconds)}</p>
        </div>
      )}

      {lastChecked && (
        <p style={{ marginTop: '10px', color: '#666' }}>
          Last checked: {lastChecked.toLocaleString()}
        </p>
      )}
    </div>
  );
};

export default HeartbeatComponent;