import './App.css';
import { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
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

// ============================================================================
// REACT QUERY CONFIGURATION - Performance Optimization
// ============================================================================
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Cache Configuration
      staleTime: 5 * 60 * 1000, // 5 minutes - data stays fresh
      cacheTime: 10 * 60 * 1000, // 10 minutes - keep in memory
      
      // Performance Optimizations
      refetchOnWindowFocus: false, // Don't refetch when switching tabs
      refetchOnReconnect: false, // Don't auto-refetch on reconnect
      retry: 1, // Only retry failed requests once
      
      // Prevent unnecessary re-renders
      notifyOnChangeProps: 'tracked', // Only notify on tracked properties
      
      // Keep previous data while fetching new data
      keepPreviousData: true,
    },
    mutations: {
      // Retry failed mutations once
      retry: 1,
    },
  },
});

// ============================================================================
// MAIN APP COMPONENT
// ============================================================================
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
    
    // Clear React Query cache on logout
    queryClient.clear();
    debugLog('[APP] React Query cache cleared');
    
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
    <QueryClientProvider client={queryClient}>
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

      {/* React Query DevTools - Only in development */}
      {process.env.NODE_ENV === 'development' && (
        <ReactQueryDevtools 
          initialIsOpen={false} 
          position="bottom-right"
          buttonPosition="bottom-right"
        />
      )}
    </QueryClientProvider>
  );
}

export default App;