import { useState } from 'react';
import { config } from '../config';
import { initiateOAuth } from '../utils/auth';

const DEFAULT_INSTANCE = config.instanceUrl.startsWith('https://YOUR')
  ? ''
  : config.instanceUrl;

export default function LoginPage() {
  const [instanceUrl, setInstanceUrl] = useState(DEFAULT_INSTANCE);
  const [loading,     setLoading]     = useState(false);
  const [error,       setError]       = useState('');

  async function handleLogin(e) {
    e.preventDefault();
    setError('');

    let url = instanceUrl.trim();
    if (!url) { setError('Please enter your Salesforce org URL.'); return; }

    // Normalise: ensure https://, strip trailing slash
    if (!url.startsWith('http')) url = 'https://' + url;
    url = url.replace(/\/$/, '');

    if (!config.clientId || config.clientId === 'YOUR_CONNECTED_APP_CLIENT_ID') {
      setError(
        'No Connected App Client ID configured. ' +
        'Edit src/config.js and set clientId, then restart the dev server.'
      );
      return;
    }

    try {
      setLoading(true);
      await initiateOAuth(url, config.clientId, config.redirectUri);
      // ↑ redirects the browser; the line below won't run
    } catch (err) {
      setError(err.message ?? 'Failed to initiate login.');
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-logo">
          <div className="login-logo-icon">☁️</div>
          <div className="login-logo-text">
            <h1>Revenue Cloud Portal</h1>
            <p>Connect to your Salesforce org</p>
          </div>
        </div>

        {error && <div className="error-banner">⚠️ {error}</div>}

        <form onSubmit={handleLogin}>
          <div className="login-form-group">
            <label htmlFor="instanceUrl">Salesforce Org URL</label>
            <input
              id="instanceUrl"
              type="text"
              className="login-input"
              placeholder="https://mycompany.my.salesforce.com"
              value={instanceUrl}
              onChange={e => setInstanceUrl(e.target.value)}
              autoFocus
              spellCheck={false}
              autoComplete="url"
            />
          </div>

          <button
            type="submit"
            className="login-btn"
            disabled={loading}
          >
            {loading
              ? <><span style={{ animation: 'spin .65s linear infinite', display: 'inline-block' }}>⏳</span> Redirecting…</>
              : <>🔐 Connect with Salesforce</>
            }
          </button>
        </form>

        <p className="login-hint">
          You'll be redirected to Salesforce to authorize access.
          <br />
          Requires a Connected App with OAuth enabled.{' '}
          <a href="https://github.com" style={{ fontSize: 'inherit' }}>See SETUP.md for instructions.</a>
        </p>
      </div>
    </div>
  );
}
