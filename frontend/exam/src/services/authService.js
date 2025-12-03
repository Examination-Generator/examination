// Authentication API Service
// import { API_URL } from '../config';

// const API_BASE_URL = API_URL;
const API_BASE_URL = 'https://speedstarexams.co.ke/api'; // Temporary hardcode to avoid circular dependency issue

// Session configuration
const SESSION_TIMEOUT = 30 * 60 * 1000; // 30 minutes in milliseconds
const ACTIVITY_CHECK_INTERVAL = 60 * 1000; // Check every minute
const TOKEN_REFRESH_THRESHOLD = 5 * 60 * 1000; // Refresh token if expiring in 5 minutes

// Logging utility - only logs in development
const debugLog = (message, ...args) => {
    if (process.env.NODE_ENV === 'development') {
        console.log(message, ...args);
    }
};

// Activity tracker
let activityTimeout = null;
let activityCheckInterval = null;
let lastActivityTime = Date.now();

// Update last activity time
const updateActivity = () => {
    lastActivityTime = Date.now();
    localStorage.setItem('lastActivity', lastActivityTime.toString());
};

// Initialize activity tracking
export const initActivityTracking = (onSessionExpired) => {
    // Track user activity
    const events = ['mousedown', 'keydown', 'scroll', 'touchstart', 'click'];
    
    const handleActivity = () => {
        updateActivity();
        resetActivityTimeout(onSessionExpired);
    };
    
    // Add event listeners
    events.forEach(event => {
        document.addEventListener(event, handleActivity, true);
    });
    
    // Start checking for inactivity
    startActivityCheck(onSessionExpired);
    
    // Initial activity update
    updateActivity();
    
    // Return cleanup function
    return () => {
        events.forEach(event => {
            document.removeEventListener(event, handleActivity, true);
        });
        stopActivityCheck();
    };
};

// Reset activity timeout
const resetActivityTimeout = (onSessionExpired) => {
    if (activityTimeout) {
        clearTimeout(activityTimeout);
    }
    
    activityTimeout = setTimeout(() => {
        debugLog('[SESSION] Session expired due to inactivity');
        handleSessionExpired(onSessionExpired);
    }, SESSION_TIMEOUT);
};

// Start activity check interval
const startActivityCheck = (onSessionExpired) => {
    activityCheckInterval = setInterval(() => {
        const now = Date.now();
        const lastActivity = parseInt(localStorage.getItem('lastActivity') || '0', 10);
        const timeSinceActivity = now - lastActivity;
        
        // Check if session should expire
        if (timeSinceActivity > SESSION_TIMEOUT) {
            debugLog('[SESSION] Session expired due to inactivity (background check)');
            handleSessionExpired(onSessionExpired);
        }
    }, ACTIVITY_CHECK_INTERVAL);
};

// Stop activity check
const stopActivityCheck = () => {
    if (activityTimeout) {
        clearTimeout(activityTimeout);
        activityTimeout = null;
    }
    if (activityCheckInterval) {
        clearInterval(activityCheckInterval);
        activityCheckInterval = null;
    }
};

// Handle session expiration
const handleSessionExpired = (callback) => {
    stopActivityCheck();
    logout();
    if (callback) {
        callback();
    }
};

// Check if session is still valid
export const isSessionValid = () => {
    const token = localStorage.getItem('token');
    const lastActivity = parseInt(localStorage.getItem('lastActivity') || '0', 10);
    const now = Date.now();
    
    if (!token) {
        return false;
    }
    
    // Check if too much time has passed since last activity
    if (lastActivity && (now - lastActivity) > SESSION_TIMEOUT) {
        debugLog('[SESSION] Session expired');
        logout();
        return false;
    }
    
    return true;
};

// Request OTP for registration
export const requestOTP = async (phoneNumber, fullName) => {
    try {
        const response = await fetch(`${API_BASE_URL}/send-otp`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ phoneNumber, fullName, purpose: 'registration' })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error requesting OTP:', error);
        throw error;
    }
};

// Verify OTP
export const verifyOTP = async (phoneNumber, otp) => {
    try {
        const response = await fetch(`${API_BASE_URL}/verify-otp`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ phoneNumber, otp })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error verifying OTP:', error);
        throw error;
    }
};

// Register new user (after OTP verification)
export const register = async (phoneNumber, fullName, password, role = 'user') => {
    try {
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ phoneNumber, fullName, password, role })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        const data = result.data || result; // Handle both formats
        
        // Store token and user data in localStorage
        if (data.token) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            localStorage.setItem('loginTime', Date.now().toString());
            updateActivity(); // Initialize activity tracking
        }
        
        return data;
    } catch (error) {
        console.error('Error registering user:', error);
        throw error;
    }
};

// Login user
export const login = async (phoneNumber, password) => {
    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ phoneNumber, password })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        const data = result.data || result; // Handle both formats
        
        // Store token and user data in localStorage
        if (data.token) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            localStorage.setItem('loginTime', Date.now().toString());
            updateActivity(); // Initialize activity tracking
        }
        
        return data;
    } catch (error) {
        console.error('Error logging in:', error);
        throw error;
    }
};

// Logout user
export const logout = () => {
    stopActivityCheck();
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('loginTime');
    localStorage.removeItem('lastActivity');
    debugLog('[SESSION] User logged out');
};

// Get current user from localStorage
export const getCurrentUser = () => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
        try {
            return JSON.parse(userStr);
        } catch (error) {
            console.error('Error parsing user data:', error);
            return null;
        }
    }
    return null;
};

// Check if user is authenticated
export const isAuthenticated = () => {
    const token = localStorage.getItem('token');
    const user = getCurrentUser();
    return !!(token && user && isSessionValid());
};

// Get authentication token
export const getAuthToken = () => {
    return localStorage.getItem('token');
};

// Get session info for debugging
export const getSessionInfo = () => {
    const lastActivity = parseInt(localStorage.getItem('lastActivity') || '0', 10);
    const loginTime = parseInt(localStorage.getItem('loginTime') || '0', 10);
    const now = Date.now();
    
    return {
        isValid: isSessionValid(),
        loginTime: loginTime ? new Date(loginTime).toISOString() : null,
        lastActivity: lastActivity ? new Date(lastActivity).toISOString() : null,
        timeUntilExpiry: SESSION_TIMEOUT - (now - lastActivity),
        sessionTimeout: SESSION_TIMEOUT,
    };
};

// Request password reset OTP
export const requestPasswordReset = async (phoneNumber) => {
    try {
        const response = await fetch(`${API_BASE_URL}/forgot-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ phoneNumber })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error requesting password reset:', error);
        throw error;
    }
};

// Reset password
export const resetPassword = async (phoneNumber, otp, newPassword) => {
    try {
        const response = await fetch(`${API_BASE_URL}/reset-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ phoneNumber, otp, newPassword })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error resetting password:', error);
        throw error;
    }
};
