import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { readFileSync, existsSync } from 'fs';

// ── Resolve the Salesforce instance URL for the dev proxy ────────────────────
// Priority:
//   1. VITE_SF_INSTANCE_URL in .env.local  (written by `cci task run configure_portal_webapp`)
//   2. Fallback URL hard-coded in src/config.js (for manual / non-CCI setups)
//   3. Generic login.salesforce.com default
//
// This keeps the Vite proxy target in sync with whichever org the developer is
// targeting, without any manual edits to this file.

let sfInstance = 'https://login.salesforce.com';

// 1. Prefer .env.local (CCI-managed)
const envLocalPath = './.env.local';
if (existsSync(envLocalPath)) {
  const envContent = readFileSync(envLocalPath, 'utf-8');
  const envMatch = envContent.match(/^VITE_SF_INSTANCE_URL=(.+)$/m);
  if (envMatch?.[1]?.trim()) {
    sfInstance = envMatch[1].trim();
  }
}

// 2. Fall back to the hard-coded URL in config.js
if (sfInstance === 'https://login.salesforce.com') {
  const configSrc = readFileSync('./src/config.js', 'utf-8');
  // Match the fallback string literal after the ?? operator
  const fallbackMatch = configSrc.match(/\?\?\s*'(https:\/\/[^']+)'/);
  if (fallbackMatch?.[1]) {
    sfInstance = fallbackMatch[1];
  }
}

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    open: true,
    // ── Dev proxy ────────────────────────────────────────────────────────────
    // Routes Salesforce OAuth calls through the Vite dev server so the browser
    // never makes a cross-origin request — no CORS config needed in Salesforce
    // for local development.
    //
    // /sf-proxy/oauth2/token     → <sfInstance>/services/oauth2/token
    // /sf-proxy/oauth2/userinfo  → <sfInstance>/services/oauth2/userinfo
    //
    // Production builds use the direct Salesforce URLs (import.meta.env.PROD),
    // so CORS must be configured in Salesforce for any deployed domain.
    proxy: {
      '/sf-proxy': {
        target: sfInstance,
        changeOrigin: true,
        rewrite: path => path.replace(/^\/sf-proxy/, '/services'),
      },
      // Proxies authenticated Salesforce file-asset requests in dev so the
      // browser doesn't hit CORS restrictions when fetching branding images.
      // /sf-file-asset/... → <sfInstance>/file-asset/...
      '/sf-file-asset': {
        target: sfInstance,
        changeOrigin: true,
        rewrite: path => path.replace(/^\/sf-file-asset/, '/file-asset'),
      },
    },
  },
  build: {
    outDir: 'dist',
  },
});
