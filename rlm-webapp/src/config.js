// ─────────────────────────────────────────────────────────────────────────────
// Revenue Cloud Portal — Configuration
//
// Values are resolved in priority order:
//   1. Vite env vars from .env.local  (written automatically by:
//        cci task run configure_portal_webapp --org <alias>)
//   2. Hard-coded fallbacks below     (edit for manual / non-CCI setups)
//
// See SETUP.md for step-by-step instructions on creating the Connected App.
// .env.local is gitignored — never commit it.
// ─────────────────────────────────────────────────────────────────────────────

export const config = {
  // Your Salesforce org URL — no trailing slash
  // Overridden by VITE_SF_INSTANCE_URL in .env.local when using CCI.
  instanceUrl: import.meta.env.VITE_SF_INSTANCE_URL
    ?? 'https://storm-cb1cab420af293.my.salesforce.com',

  // Consumer Key (Client ID) from your Connected App
  // Overridden by VITE_SF_CLIENT_ID in .env.local when using CCI.
  clientId: import.meta.env.VITE_SF_CLIENT_ID
    ?? '3MVG9azVmavckRRQ8GxBzLzClAlU_EMJLKYhnkTU99_kr.oYrMA8aEV0b7S6MwtaM82noGPAuQvW_WzsVVolP',

  // OAuth redirect URI — must exactly match what you set in the Connected App.
  // For local dev: 'http://localhost:5173/callback'
  // For deployed app: 'https://your-app-domain.com/callback'
  redirectUri: typeof window !== 'undefined'
    ? `${window.location.origin}/callback`
    : 'http://localhost:5173/callback',

  // Salesforce API version — Spring '26 (Release 260, v66)
  apiVersion: 'v66.0',

  // App name shown in the header
  appName: 'Revenue Cloud Portal',
};
