import React from 'react';
import useHeartbeat from './useHeartbeat';

const ExampleUsage = () => {
  // Using the hook with default settings
  const heartbeat = useHeartbeat();

  // Or with custom settings
  // const heartbeat = useHeartbeat('https://api.example.com', 60000, true);

  return (
    <div style={{ padding: '20px' }}>
      <h2>Server Status</h2>
      
      {heartbeat.isChecking && <p>Checking server...</p>}
      
      {heartbeat.isAlive === true && (
        <div style={{ color: 'green' }}>
          ✅ Server is alive
          {heartbeat.data && (
            <div>
              <p>Status: {heartbeat.data.status}</p>
              <p>Message: {heartbeat.data.message}</p>
            </div>
          )}
        </div>
      )}
      
      {heartbeat.isAlive === false && (
        <div style={{ color: 'red' }}>
          ❌ Server is down
          {heartbeat.error && <p>Error: {heartbeat.error.message}</p>}
        </div>
      )}
      
      {heartbeat.lastChecked && (
        <p>Last checked: {heartbeat.lastChecked.toLocaleString()}</p>
      )}
      
      <button onClick={heartbeat.checkNow} disabled={heartbeat.isChecking}>
        Check Now
      </button>
    </div>
  );
};

export default ExampleUsage;