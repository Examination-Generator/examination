import './App.css';
import { useState, useEffect } from 'react';
import Login from './components/Login';
import Signup from './components/Signup';
import EditorDashboard from './components/EditorDashboard';
import UserDashboard from './components/UserDashboard';
import SessionWarning from './components/SessionWarning';
import SessionManager from './components/SessionManager';
import { 
  isAuthenticated, 
  getCurrentUser, 
  initActivityTracking, 
  isSessionValid,
  logout 
} from './services/authService';

function App() {
  const [currentView, setCurrentView] = useState('login'); // 'login', 'signup', 'editor', or 'user'
  const [userRole, setUserRole] = useState('user'); // 'editor' or 'user'
  const [isLoading, setIsLoading] = useState(true); // Loading state for session check

  // Logging utility - only logs in development
  const debugLog = (message, ...args) => {
    if (process.env.NODE_ENV === 'development') {
      console.log(message, ...args);
    }
  };

  // Check for existing session on mount
  useEffect(() => {
    const checkSession = () => {
      debugLog('[APP] Checking existing session...');
      
      if (isAuthenticated() && isSessionValid()) {
        const user = getCurrentUser();
        debugLog('[APP] Valid session found:', user);
        
        setUserRole(user.role);
        if (user.role === 'editor') {
          setCurrentView('editor');
        } else {
          setCurrentView('user');
        }
      } else {
        debugLog('[APP] No valid session found');
        setCurrentView('login');
      }
      
      setIsLoading(false);
    };

    checkSession();
  }, []);

  // Initialize activity tracking when user is logged in
  useEffect(() => {
    let cleanup = null;

    if (currentView === 'editor' || currentView === 'user') {
      debugLog('[APP] Initializing activity tracking');
      
      cleanup = initActivityTracking(() => {
        debugLog('[APP] Session expired, redirecting to login');
        alert('Your session has expired due to inactivity. Please login again.');
        handleLogout();
      });
    }

    return () => {
      if (cleanup) {
        debugLog('[APP] Cleaning up activity tracking');
        cleanup();
      }
    };
  }, [currentView]);

  const handleLoginSuccess = (role) => {
    debugLog('[APP] Login successful, role:', role);
    setUserRole(role);
    if (role === 'editor') {
      setCurrentView('editor');
    } else {
      setCurrentView('user');
    }
  };

  const handleLogout = () => {
    debugLog('[APP] Logging out');
    logout();
    setCurrentView('login');
    setUserRole('user');
  };

  // Show loading screen while checking session
  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '1.2rem',
        color: '#666'
      }}>
        Loading...
      </div>
    );
  }

  return (
    <>
      {/* Session Warning - shown when session is about to expire */}
      {(currentView === 'editor' || currentView === 'user') && (
        <SessionWarning onLogout={handleLogout} />
      )}

      {/* Session Manager - COMPLETELY DISABLED in production */}
      {/* Only shows in development mode AND can be toggled off */}
      {/* To enable in development: Set REACT_APP_SHOW_SESSION_DEBUG=true in .env.local */}
      {process.env.NODE_ENV === 'development' && 
       process.env.REACT_APP_SHOW_SESSION_DEBUG === 'true' && 
       (currentView === 'editor' || currentView === 'user') && (
        <SessionManager showDebugInfo={true} />
      )}

      {currentView === 'login' ? (
        <Login 
          onSwitchToSignup={() => setCurrentView('signup')}
          onLoginSuccess={handleLoginSuccess}
        />
      ) : currentView === 'signup' ? (
        <Signup onSwitchToLogin={() => setCurrentView('login')} />
      ) : currentView === 'editor' ? (
        <EditorDashboard onLogout={handleLogout} />
      ) : (
        <UserDashboard onLogout={handleLogout} />
      )}
    </>
  );
}

export default App;
