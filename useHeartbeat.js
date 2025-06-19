import { useState, useEffect, useCallback } from 'react';

/**
 * Custom hook for monitoring server heartbeat
 * @param {string} backendUrl - The backend server URL
 * @param {number} interval - Heartbeat check interval in milliseconds (default: 30000)
 * @param {boolean} autoStart - Whether to start checking automatically (default: true)
 */
const useHeartbeat = (backendUrl = 'http://localhost:5000', interval = 30000, autoStart = true) => {
  const [status, setStatus] = useState({
    isAlive: null,
    data: null,
    lastChecked: null,
    error: null,
    isChecking: false
  });

  const checkHeartbeat = useCallback(async () => {
    setStatus(prev => ({ ...prev, isChecking: true, error: null }));

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(`${backendUrl}/heartbeat`, {
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
      
      setStatus({
        isAlive: true,
        data: data,
        lastChecked: new Date(),
        error: null,
        isChecking: false
      });
    } catch (err) {
      setStatus({
        isAlive: false,
        data: null,
        lastChecked: new Date(),
        error: {
          message: err.message,
          type: err.name === 'AbortError' ? 'TIMEOUT' : 'CONNECTION_ERROR'
        },
        isChecking: false
      });
    }
  }, [backendUrl]);

  useEffect(() => {
    let intervalId;

    if (autoStart) {
      // Initial check
      checkHeartbeat();

      // Set up interval
      intervalId = setInterval(checkHeartbeat, interval);
    }

    // Cleanup
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [checkHeartbeat, interval, autoStart]);

  return {
    ...status,
    checkNow: checkHeartbeat
  };
};

export default useHeartbeat;