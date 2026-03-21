import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { config } from '../config';
import { handleCallback } from '../utils/auth';

export default function CallbackPage() {
  const navigate  = useNavigate();
  const done      = useRef(false);
  const [error,   setError] = useState('');

  useEffect(() => {
    if (done.current) return;
    done.current = true;

    handleCallback(config.clientId, config.redirectUri)
      .then(() => navigate('/catalog', { replace: true }))
      .catch(err => setError(err.message ?? 'Authentication failed.'));
  }, [navigate]);

  if (error) {
    return (
      <div className="login-page">
        <div className="login-card">
          <div className="login-logo">
            <div className="login-logo-icon">❌</div>
            <div className="login-logo-text">
              <h1>Authentication Error</h1>
              <p>Could not complete login</p>
            </div>
          </div>
          <div className="error-banner">{error}</div>
          <button
            className="login-btn"
            style={{ marginTop: 16 }}
            onClick={() => navigate('/login', { replace: true })}
          >
            ← Back to Login
          </button>
          <p className="login-hint" style={{ marginTop: 12 }}>
            Common causes: CORS not configured for this origin, Client ID mismatch,
            or redirect URI mismatch. See SETUP.md.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="login-page">
      <div className="login-card" style={{ textAlign: 'center' }}>
        <div style={{ fontSize: 40, marginBottom: 16 }}>
          <span style={{ animation: 'spin .65s linear infinite', display: 'inline-block' }}>⏳</span>
        </div>
        <h2 style={{ color: 'var(--sf-navy)', marginBottom: 8 }}>Completing sign-in…</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>
          Exchanging authorization code for access token.
        </p>
      </div>
    </div>
  );
}
