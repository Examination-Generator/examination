import React from 'react';
import { useError } from '../contexts/ErrorContext';

const toastBase = {
  position: 'fixed',
  right: '20px',
  top: '20px',
  zIndex: 9999,
  display: 'flex',
  flexDirection: 'column',
  gap: '8px',
};

const Toast = ({ toast, onClose }) => {
  const bg = toast.type === 'success' ? '#16a34a' : '#dc2626';
  return (
    <div style={{ background: bg, color: 'white', padding: '10px 14px', borderRadius: 6, boxShadow: '0 4px 12px rgba(0,0,0,0.12)', minWidth: 220 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ fontSize: 14 }}>{toast.message}</div>
        <button onClick={() => onClose(toast.id)} style={{ marginLeft: 12, background: 'transparent', border: 'none', color: 'white', cursor: 'pointer' }}>✕</button>
      </div>
    </div>
  );
};

export default function ErrorToast() {
  const { toasts, removeToast } = useError();

  if (!toasts || toasts.length === 0) return null;

  return (
    <div style={toastBase} aria-live="polite">
      {toasts.map((t) => (
        <Toast key={t.id} toast={t} onClose={removeToast} />
      ))}
    </div>
  );
}
