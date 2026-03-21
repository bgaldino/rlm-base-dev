# Revenue Cloud Portal — Setup Guide

This guide explains how to run the webapp against your CCI-provisioned org.

---

## Recommended: CCI-Automated Setup

If you are using CumulusCI to build your org, the portal can be set up automatically.

### 1 — Enable the portal feature flag

In your local `cumulusci.yml`, set `portal: true` under `project.custom`:

```yaml
project:
  custom:
    portal: true   # ← change from false
```

### 2 — Run (or re-run) the org setup flow

```bash
cci flow run prepare_rlm_org --org <alias>
```

The flow automatically runs `prepare_portal` at the end, which:

1. Deploys the **RLM Portal** Connected App to the org (`deploy_portal_connected_app`)
2. Reads its Consumer Key via the Tooling API and writes `rlm-webapp/.env.local`
   with `VITE_SF_INSTANCE_URL` and `VITE_SF_CLIENT_ID` (`configure_portal_webapp`)

> **Tip:** You can also run just the portal tasks against an existing org:
> ```bash
> cci task run deploy_portal_connected_app --org <alias>
> cci task run configure_portal_webapp --org <alias>
> ```

### 3 — Install & run

```bash
cd rlm-webapp
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) and click **Connect with Salesforce**.
The org URL and Client ID are loaded automatically from `.env.local` — no manual edits needed.

---

## Manual Setup (without CCI)

Use this path if you are not using CumulusCI or need to set up against an existing org.

### Step 1 — Create a Connected App

1. In your Salesforce org, go to **Setup → App Manager → New Connected App**.

2. Fill in the basics:
   - **Connected App Name:** `RLM Portal`
   - **API Name:** `RLMPortal`
   - **Contact Email:** your email

3. Under **OAuth Settings**, check **Enable OAuth Settings**:
   - **Callback URL:** `http://localhost:5173/callback`
     *(Add additional URLs here if you deploy the app, e.g. `https://myapp.example.com/callback`)*
   - **Selected OAuth Scopes:**
     - `Access and manage your data (api)`
     - `Perform requests at any time (refresh_token, offline_access)`
     - `Access unique user identifiers (openid)`
   - Check **Enable Proof Key for Code Exchange (PKCE) Extension for Supported Authorization Flows**
   - Uncheck **Require Secret for Web Server Flow** (browser SPA — no client secret)

4. Click **Save**. Salesforce may take 2–10 minutes to activate the new app.

5. After saving, click **Manage Consumer Details** and copy the **Consumer Key**.

---

### Step 2 — Configure CORS

> **Local dev only:** The Vite dev server proxies OAuth requests, so CORS is not needed
> for `npm run dev`. Only configure this when deploying to a real domain.

1. Go to **Setup → Security → CORS → New**.
2. Enter `http://localhost:5173` as the **Origin URL Pattern**. Save.
3. Scroll down, click **Edit** under **Cross-Origin Resource Sharing (CORS) Policy Settings**.
4. Check **Enable CORS for OAuth endpoints**. Save.

Without step 4, the token exchange returns `Failed to fetch` even if your origin is listed.

---

### Step 3 — Edit `src/config.js`

Open `rlm-webapp/src/config.js` and update the fallback values:

```js
instanceUrl: import.meta.env.VITE_SF_INSTANCE_URL
  ?? 'https://YOUR-ORG.my.salesforce.com',   // ← your org

clientId: import.meta.env.VITE_SF_CLIENT_ID
  ?? 'YOUR_CONSUMER_KEY_HERE',               // ← from Step 1
```

Alternatively, create `rlm-webapp/.env.local` (gitignored):

```
VITE_SF_INSTANCE_URL=https://YOUR-ORG.my.salesforce.com
VITE_SF_CLIENT_ID=YOUR_CONSUMER_KEY_HERE
```

> **Tip:** Your org's My Domain URL is in **Setup → My Domain → Current My Domain URL**.

---

### Step 4 — Install & run

```bash
cd rlm-webapp
npm install
npm run dev
```

---

## Deploying to Heroku

Salesforce employees can host the app on Heroku for free using the employee benefit.

1. Build the app:
   ```bash
   cd rlm-webapp
   npm run build      # outputs to rlm-webapp/dist/
   ```

2. Deploy `dist/` to Heroku (static buildpack or similar).

3. Add your Heroku URL as an additional **Callback URL** in the Connected App.
   With CCI, use the `extra_callback_urls` option:
   ```bash
   cci task run configure_portal_webapp --org <alias> \
     -o extra_callback_urls https://my-portal.herokuapp.com/callback
   ```

4. Add the Heroku origin to **Setup → Security → CORS** in Salesforce.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `Failed to fetch` on callback | OAuth CORS endpoint not enabled | Setup → CORS → Edit → check **Enable CORS for OAuth endpoints** |
| `Token exchange failed: CORS error` | Origin not in CORS allowlist | Add your origin to Setup → CORS |
| `No authorization code received` | Redirect URI mismatch | Ensure callback URL in Connected App matches exactly |
| `Session expired` on page load | Session storage cleared | Normal — just log in again |
| Products/Quotes/Orders empty | No data loaded or API version mismatch | Run `cci flow run prepare_rlm_org --org <alias>` first |
| `INSUFFICIENT_ACCESS_ON_CROSS_REFERENCE_ENTITY` | OAuth user lacks permissions | Assign the appropriate Permission Set to the user |
| `.env.local` not picked up | Vite server not restarted after CCI write | Stop and restart `npm run dev` |

---

## API objects queried

The app calls the Salesforce REST API (v66.0) and reads these standard objects:

- **Product Catalog:** `Product2`, `ProductCatalog`, `ProductCategory`, `PricebookEntry`
- **Quotes:** `Quote`, `QuoteLineItem`
- **Orders:** `Order`, `OrderItem`
- **Branding:** `BrandingSet`, `BrandingSetProperty`, `ContentAsset`, `ContentVersion`

All queries are read-only (`SELECT`). The app does not write to or modify any Salesforce data.
