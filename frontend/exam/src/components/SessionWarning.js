import { useEffect, useState } from 'react';
import { getSessionInfo } from '../services/authService';

/**
 * SessionWarning Component
 * Shows a warning modal when session is about to expire
 */
const SessionWarning = ({ onExtendSession, onLogout }) => {
    const [showWarning, setShowWarning] = useState(false);
    const [countdown, setCountdown] = useState(0);

    useEffect(() => {
        const checkSessionExpiry = () => {
            const info = getSessionInfo();
            
            // Show warning if less than 5 minutes remaining
            const minutesRemaining = Math.floor(info.timeUntilExpiry / 1000 / 60);
            
            if (minutesRemaining < 5 && minutesRemaining > 0 && info.isValid) {
                setShowWarning(true);
                setCountdown(minutesRemaining);
            } else if (minutesRemaining <= 0) {
                setShowWarning(false);
                if (onLogout) {
                    onLogout();
                }
            } else {
                setShowWarning(false);
            }
        };

        // Check every 30 seconds
        const interval = setInterval(checkSessionExpiry, 30000);
        
        // Initial check
        checkSessionExpiry();

        return () => clearInterval(interval);
    }, [onLogout]);

    const handleStayLoggedIn = () => {
        setShowWarning(false);
        if (onExtendSession) {
            onExtendSession();
        }
        // Just interacting with the page will extend the session
        // because activity tracking will update lastActivityTime
    };

    if (!showWarning) {
        return null;
    }

    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 10000
        }}>
            <div style={{
                backgroundColor: 'white',
                padding: '30px',
                borderRadius: '10px',
                maxWidth: '400px',
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
            }}>
                <h3 style={{ marginTop: 0, color: '#f59e0b' }}>
                    ⚠️ Session Expiring Soon
                </h3>
                <p>
                    Your session will expire in <strong>{countdown} minute{countdown !== 1 ? 's' : ''}</strong> due to inactivity.
                </p>
                <p>
                    Click "Stay Logged In" to continue working.
                </p>
                <div style={{
                    display: 'flex',
                    gap: '10px',
                    marginTop: '20px'
                }}>
                    <button
                        onClick={handleStayLoggedIn}
                        style={{
                            flex: 1,
                            padding: '10px 20px',
                            backgroundColor: '#10b981',
                            color: 'white',
                            border: 'none',
                            borderRadius: '5px',
                            cursor: 'pointer',
                            fontSize: '14px',
                            fontWeight: 'bold'
                        }}
                        onMouseOver={(e) => e.target.style.backgroundColor = '#059669'}
                        onMouseOut={(e) => e.target.style.backgroundColor = '#10b981'}
                    >
                        Stay Logged In
                    </button>
                    <button
                        onClick={onLogout}
                        style={{
                            flex: 1,
                            padding: '10px 20px',
                            backgroundColor: '#6b7280',
                            color: 'white',
                            border: 'none',
                            borderRadius: '5px',
                            cursor: 'pointer',
                            fontSize: '14px'
                        }}
                        onMouseOver={(e) => e.target.style.backgroundColor = '#4b5563'}
                        onMouseOut={(e) => e.target.style.backgroundColor = '#6b7280'}
                    >
                        Logout Now
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SessionWarning;
