// ─────────────────────────────────────────────────────────────────────────────
// Salesforce OAuth 2.0 PKCE flow helpers
//
// Flow:
//   1. initiateOAuth()  → stores verifier, redirects to Salesforce /authorize
//   2. handleCallback() → exchanges code for tokens, stores them in sessionStorage
//   3. getAuth()        → returns { accessToken, instanceUrl } or null
//   4. logout()         → clears all stored auth state
// ─────────────────────────────────────────────────────────────────────────────

const KEYS = {
  verifier:    'rlm_pkce_verifier',
  state:       'rlm_pkce_state',
  baseInstance:'rlm_base_instance',
  accessToken: 'rlm_access_token',
  instanceUrl: 'rlm_instance_url',
  userInfo:    'rlm_user_info',
};

// ── PKCE helpers ──────────────────────────────────────────────────────────────

function generateVerifier() {
  const arr = new Uint8Array(32);
  crypto.getRandomValues(arr);
  return btoa(String.fromCharCode(...arr))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}

async function generateChallenge(verifier) {
  const data = new TextEncoder().encode(verifier);
  const digest = await crypto.subtle.digest('SHA-256', data);
  return btoa(String.fromCharCode(...new Uint8Array(digest)))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}

function generateState() {
  const arr = new Uint8Array(16);
  crypto.getRandomValues(arr);
  return Array.from(arr, b => b.toString(16).padStart(2, '0')).join('');
}

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Kick off the PKCE authorization flow.
 * Stores the verifier + state, then redirects the browser to Salesforce.
 */
export async function initiateOAuth(instanceUrl, clientId, redirectUri) {
  const verifier  = generateVerifier();
  const challenge = await generateChallenge(verifier);
  const state     = generateState();

  sessionStorage.setItem(KEYS.verifier,     verifier);
  sessionStorage.setItem(KEYS.state,        state);
  sessionStorage.setItem(KEYS.baseInstance, instanceUrl);

  const params = new URLSearchParams({
    response_type:         'code',
    client_id:             clientId,
    redirect_uri:          redirectUri,
    code_challenge:        challenge,
    code_challenge_method: 'S256',
    state,
    scope: 'api refresh_token openid',
  });

  window.location.href = `${instanceUrl}/services/oauth2/authorize?${params}`;
}

/**
 * Called on the /callback route after Salesforce redirects back.
 * Exchanges the authorization code for tokens.
 *
 * @param {string} clientId   - Connected App consumer key
 * @param {string} redirectUri
 * @returns {Promise<{accessToken: string, instanceUrl: string}>}
 */
export async function handleCallback(clientId, redirectUri) {
  const params  = new URLSearchParams(window.location.search);
  const code    = params.get('code');
  const state   = params.get('state');
  const error   = params.get('error');

  if (error) {
    throw new Error(`Salesforce OAuth error: ${error} — ${params.get('error_description') ?? ''}`);
  }
  if (!code) {
    throw new Error('No authorization code received from Salesforce.');
  }

  const savedState    = sessionStorage.getItem(KEYS.state);
  const verifier      = sessionStorage.getItem(KEYS.verifier);
  const baseInstance  = sessionStorage.getItem(KEYS.baseInstance);

  if (state !== savedState) {
    throw new Error('OAuth state mismatch — possible CSRF attack. Please try logging in again.');
  }
  if (!verifier || !baseInstance) {
    throw new Error('Missing PKCE verifier or instance URL. Please try logging in again.');
  }

  const body = new URLSearchParams({
    grant_type:    'authorization_code',
    client_id:     clientId,
    redirect_uri:  redirectUri,
    code,
    code_verifier: verifier,
  });

  // In dev mode the Vite proxy forwards /sf-proxy/* → <sfInstance>/services/*
  // so the browser never makes a cross-origin request (no CORS config needed
  // in Salesforce for local dev).  In production builds the direct SF URL is used,
  // which requires the deployed origin to be in Salesforce's CORS allowlist.
  const isDev = import.meta.env.DEV;
  const tokenUrl = isDev
    ? '/sf-proxy/oauth2/token'
    : `${baseInstance}/services/oauth2/token`;

  const response = await fetch(tokenUrl, {
    method:  'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(`Token exchange failed: ${err.error_description ?? response.statusText}`);
  }

  const data = await response.json();

  // Salesforce returns the real instance URL in the token response (may differ from login URL)
  const resolvedInstance = data.instance_url ?? baseInstance;

  sessionStorage.setItem(KEYS.accessToken, data.access_token);
  sessionStorage.setItem(KEYS.instanceUrl, resolvedInstance);

  // Clean up PKCE scratch keys
  sessionStorage.removeItem(KEYS.verifier);
  sessionStorage.removeItem(KEYS.state);
  sessionStorage.removeItem(KEYS.baseInstance);

  // Fetch and cache basic user info (also proxied in dev)
  try {
    const userinfoUrl = isDev
      ? '/sf-proxy/oauth2/userinfo'
      : `${resolvedInstance}/services/oauth2/userinfo`;
    const userResp = await fetch(userinfoUrl, {
      headers: { Authorization: `Bearer ${data.access_token}` },
    });
    if (userResp.ok) {
      const user = await userResp.json();
      sessionStorage.setItem(KEYS.userInfo, JSON.stringify({
        name:     user.name,
        email:    user.email,
        username: user.preferred_username,
        orgId:    user.organization_id,
      }));
    }
  } catch (_) { /* non-fatal */ }

  return { accessToken: data.access_token, instanceUrl: resolvedInstance };
}

/**
 * Returns the stored auth state, or null if not authenticated.
 * @returns {{ accessToken: string, instanceUrl: string, user: object|null } | null}
 */
export function getAuth() {
  const accessToken = sessionStorage.getItem(KEYS.accessToken);
  const instanceUrl = sessionStorage.getItem(KEYS.instanceUrl);
  if (!accessToken || !instanceUrl) return null;

  let user = null;
  try {
    const raw = sessionStorage.getItem(KEYS.userInfo);
    if (raw) user = JSON.parse(raw);
  } catch (_) { /* ignore */ }

  return { accessToken, instanceUrl, user };
}

/** Returns true if the user has a stored access token. */
export function isAuthenticated() {
  return !!sessionStorage.getItem(KEYS.accessToken);
}

/** Clears all auth state from sessionStorage. */
export function logout() {
  Object.values(KEYS).forEach(k => sessionStorage.removeItem(k));
}
