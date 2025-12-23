import React, { createContext, useContext, useState, useCallback } from 'react';

const ErrorContext = createContext(null);

export const ErrorProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const pushToast = useCallback((message, type = 'error', duration = 5000) => {
    const id = Date.now() + Math.random();
    const toast = { id, message, type };
    setToasts((t) => [...t, toast]);
    // Auto-remove
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), duration);
    return id;
  }, []);

  const showError = useCallback((message, duration) => pushToast(message, 'error', duration), [pushToast]);
  const showSuccess = useCallback((message, duration) => pushToast(message, 'success', duration), [pushToast]);
  const removeToast = useCallback((id) => setToasts((t) => t.filter((x) => x.id !== id)), []);

  return (
    <ErrorContext.Provider value={{ toasts, showError, showSuccess, removeToast }}>
      {children}
    </ErrorContext.Provider>
  );
};

export const useError = () => {
  const ctx = useContext(ErrorContext);
  if (!ctx) throw new Error('useError must be used within ErrorProvider');
  return ctx;
};

export default ErrorContext;
