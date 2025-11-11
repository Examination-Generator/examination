import { useEffect, useState } from 'react';
import { getSessionInfo } from '../services/authService';

/**
 * SessionManager Component
 * Displays session status and time remaining (for debugging/admin view)
 */
const SessionManager = ({ showDebugInfo = false }) => {
    const [sessionInfo, setSessionInfo] = useState(null);
    const [timeRemaining, setTimeRemaining] = useState(0);

    useEffect(() => {
        const updateSessionInfo = () => {
            const info = getSessionInfo();
            setSessionInfo(info);
            
            if (info.timeUntilExpiry > 0) {
                setTimeRemaining(Math.floor(info.timeUntilExpiry / 1000 / 60)); // minutes
            } else {
                setTimeRemaining(0);
            }
        };

        // Update immediately
        updateSessionInfo();

        // Update every minute
        const interval = setInterval(updateSessionInfo, 60000);

        return () => clearInterval(interval);
    }, []);

    if (!showDebugInfo || !sessionInfo) {
        return null;
    }

    return (
        <div style={{
            position: 'fixed',
            bottom: '10px',
            right: '10px',
            padding: '10px 15px',
            backgroundColor: timeRemaining < 5 ? '#fee' : '#f0f0f0',
            border: '1px solid #ccc',
            borderRadius: '5px',
            fontSize: '12px',
            zIndex: 9999,
            boxShadow: '0 2px 5px rgba(0,0,0,0.1)'
        }}>
            <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                Session Info
            </div>
            <div>Status: {sessionInfo.isValid ? '✅ Active' : '❌ Expired'}</div>
            <div>Time remaining: {timeRemaining} min</div>
            {sessionInfo.lastActivity && (
                <div style={{ fontSize: '10px', marginTop: '5px', color: '#666' }}>
                    Last activity: {new Date(sessionInfo.lastActivity).toLocaleTimeString()}
                </div>
            )}
        </div>
    );
};

export default SessionManager;
