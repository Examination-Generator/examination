import './App.css';
import { useState } from 'react';
import Login from './components/Login';
import Signup from './components/Signup';
import EditorDashboard from './components/EditorDashboard';
import UserDashboard from './components/UserDashboard';

function App() {
  const [currentView, setCurrentView] = useState('login'); // 'login', 'signup', 'editor', or 'user'
  const [userRole, setUserRole] = useState('user'); // 'editor' or 'user'

  const handleLoginSuccess = (role) => {
    setUserRole(role);
    if (role === 'editor') {
      setCurrentView('editor');
    } else {
      setCurrentView('user');
    }
  };

  return (
    <>
      {currentView === 'login' ? (
        <Login 
          onSwitchToSignup={() => setCurrentView('signup')}
          onLoginSuccess={handleLoginSuccess}
        />
      ) : currentView === 'signup' ? (
        <Signup onSwitchToLogin={() => setCurrentView('login')} />
      ) : currentView === 'editor' ? (
        <EditorDashboard onLogout={() => setCurrentView('login')} />
      ) : (
        <UserDashboard onLogout={() => setCurrentView('login')} />
      )}
    </>
  );
}

export default App;
