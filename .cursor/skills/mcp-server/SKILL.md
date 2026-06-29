---
name: mcp-server
description: >-
  Connect an MCP client to a Salesforce Hosted MCP server and use its tools
  (Salesforce v67.0). Use when wiring Claude Code/Desktop, Cursor, ChatGPT, or
  Postman to an org's activated MCP servers — endpoint URLs, External Client App
  + OAuth (PKCE) auth, the run-as-user permission model, and discovery. For the
  admin/build side (authoring/deploying McpServerDefinition, activating
  McpServerAccess), see docs/references/mcp-server-admin.md.
---

# Connecting to Salesforce Hosted MCP Servers (v67.0)

Salesforce Hosted MCP servers expose org capabilities (SObjects, Flows, metadata)
as tools an external MCP client invokes over the Model Context Protocol. This
skill is the **consumption** side: how a client authenticates to and uses a
server that's already **activated** in the org.

> **Admin / build side** — authoring + deploying an `McpServerDefinition`,
> activating it via the `McpServerAccess` Tooling-API object, the metadata format
> and CRUD lifecycle — lives in **`docs/references/mcp-server-admin.md`**. The RLM
> build wiring (`mcp` flag, `deploy_post_mcp`, `activate_mcp_servers`) is in
> **`docs/features/mcp-servers.md`**.

## Quick Rules

1. **Endpoint host is `api.salesforce.com`, NOT your My Domain.** The MCP gateway
   is a dedicated host; `https://<mydomain>.my.salesforce.com/...` returns "Page
   doesn't exist."
2. **Auth is an External Client App (ECA) with OAuth Auth-Code + PKCE.**
   Classic **Connected Apps are not supported**. The client holds only the ECA
   **Consumer Key** (`client_id`) — no client secret (PKCE replaces it).
3. **Required scopes:** `mcp_api` (Access Salesforce hosted MCP servers) **+**
   `refresh_token` (offline access). `mcp_api` grants MCP only — not the REST APIs.
4. **Transport is streamable HTTP** (not SSE). Claude Code uses `--transport http`.
5. **Every tool call runs as the authenticated user.** The user's CRUD/FLS/sharing
   apply on top of the server's tool set — a server can't exceed what the user can
   already do.
6. **The client auto-discovers auth from the endpoint URL alone.** A
   spec-compliant MCP client walks the standard OAuth `.well-known` metadata
   (RFC 9728 → RFC 8414) to find the auth server and scopes. You supply only the
   **endpoint URL + Consumer Key** — there is no org *registry* that lists which
   servers exist, but you do not hand-configure auth-server URLs or scopes.

## DO NOT

- Do NOT point a client at the My Domain host (`*.my.salesforce.com`) — use
  `api.salesforce.com`.
- Do NOT create a classic **Connected App** for MCP auth — use an **External
  Client App**; Connected Apps aren't supported.
- Do NOT expect a client secret — these flows use **PKCE**; configure the client
  with the Consumer Key only.
- Do NOT assume the server's tools bypass the running user's permissions — they
  don't.

---

## 1. Endpoint URL

```
https://api.salesforce.com/platform/mcp/v1/<apiDomain>/<server>
```

| Environment | URL format |
|-------------|------------|
| Production | `https://api.salesforce.com/platform/mcp/v1/<apiDomain>/<server>` |
| Sandbox / scratch | `https://api.salesforce.com/platform/mcp/v1/sandbox/<apiDomain>/<server>` |

- `<apiDomain>/<server>` is the two-segment server path. Platform servers live
  under `platform/` (a couple under `data/`); a custom server is addressed under
  its own apiDomain/name once activated.
- The `<server>` segment is the **MasterLabel** form (hyphens), not the
  `DeveloperName`: e.g. `platform_sobject_all` (DeveloperName) → path
  `platform/sobject-all`.

### Standard platform server paths

| Server (path) | Tools |
|---------------|-------|
| `platform/sobject-reads` | SObject read only |
| `platform/sobject-mutations` | create / update |
| `platform/sobject-deletes` | read + delete (no writes) |
| `platform/sobject-all` | read + create/update + delete (superset of the above) |
| `platform/salesforce-api-context` | org/API context helpers |
| `platform/metadata-experts` | metadata guidance |
| `data/data-cloud-queries` | Data Cloud queries |

The RLM build activates `platform/sobject-all`, `platform/metadata-experts`,
`platform/salesforce-api-context`, plus the custom `RLMQuotingMCP`.

---

## 2. Authentication — External Client App + OAuth (PKCE)

A client authenticates through an **External Client App (ECA)** configured on the
org. (Admins set this up once; create it in a Dev Hub and package/install it —
ECAs can't be created directly in a scratch org's Setup UI, and propagation can
take ~30 min.) At runtime the client discovers the auth server and scopes
automatically from the endpoint's OAuth `.well-known` metadata (see §4) and runs
Auth-Code + PKCE — you provide only the endpoint URL and the ECA Consumer Key.

**ECA OAuth settings the admin must set:**

- **Scopes:** `Access Salesforce hosted MCP servers (mcp_api)` **+**
  `Perform requests at any time (refresh_token, offline_access)`.
- **Issue JSON Web Token (JWT)-based access tokens for named users** = on.
- **Require Proof Key for Code Exchange (PKCE)** = on.
- Deselect Client Credentials, JWT Bearer, Device, Token Exchange, and both
  "Require Secret" options (PKCE replaces the secret).
- **Callback URL** must match the client (see table below).
- Optionally restrict authentication to a **Permission Set** + IP allowlist via
  the ECA's OAuth Policies.

**OAuth endpoints:** prod `https://login.salesforce.com/services/oauth2/{authorize,token}`;
sandbox `https://test.salesforce.com/services/oauth2/{authorize,token}`.

The client is configured with the ECA **Consumer Key** as its OAuth client id and
**no secret**.

### Per-client callback URLs

| Client | Callback URL |
|--------|--------------|
| Claude Desktop / web | `https://claude.ai/api/mcp/auth_callback` |
| Claude Code (CLI) | `http://localhost:<port>/callback` (port must match `--callback-port`) |
| Cursor | `cursor://anysphere.cursor-mcp/oauth/callback` |
| Postman (desktop) | `https://oauth.pstmn.io/v1/callback` (web: `/v1/browser-callback`) |
| ChatGPT | copied from its Advanced settings |

---

## 3. Client connection examples

### Claude Code (CLI)

One entry **per server** (and per org), all reusing the **same** Consumer Key —
the ECA is server-agnostic (see §4b). Name entries by org so multiple orgs coexist.
Platform servers use the org-qualified path; the custom server uses `custom/<ApiName>`:

```bash
# Platform servers — org-qualified path (PREFIX = the org's My Domain prefix)
claude mcp add --transport http --scope user --client-id "$CONSUMER_KEY" --callback-port 8675 \
  rlm-sobject-all      https://api.salesforce.com/platform/mcp/v1/d/$PREFIX/platform/sobject-all
claude mcp add --transport http --scope user --client-id "$CONSUMER_KEY" --callback-port 8675 \
  rlm-metadata-experts https://api.salesforce.com/platform/mcp/v1/d/$PREFIX/platform/metadata-experts
claude mcp add --transport http --scope user --client-id "$CONSUMER_KEY" --callback-port 8675 \
  rlm-api-context      https://api.salesforce.com/platform/mcp/v1/d/$PREFIX/platform/salesforce-api-context

# Custom server — simple custom/<ApiName> path (copy verbatim from Setup → API Catalog → MCP Servers)
claude mcp add --transport http --scope user --client-id "$CONSUMER_KEY" --callback-port 8675 \
  rlm-quoting          https://api.salesforce.com/platform/mcp/v1/custom/RLMQuotingMCP
```

- `--client-id` = the ECA **Consumer Key** (same for every entry); no
  `--client-secret` (PKCE).
- `--callback-port` must match the ECA's `http://localhost:<port>/callback`.
- Authenticate with `/mcp` in the session; verify with `claude mcp list`
  (expect `✓ Connected`). After the first server authenticates, additional
  same-key entries usually go `✓ Connected` automatically (shared token).

### Claude Desktop

Customize → Connectors → **+** → Add custom connector → **Server URL** (the
`api.salesforce.com/...` endpoint) → **Advanced settings** → paste the Consumer
Key into **OAuth Client ID** → Connect.

### Cursor

Add an entry to `mcp.json` with the server `url` set to the endpoint and the
Consumer Key as the client id (Cursor uses its native `cursor://` OAuth callback).

### ChatGPT

Settings → Apps → Create App → **Server URL** → Registration Method "User-defined
OAuth client" → paste the Consumer Key.

### Postman (best for first-time testing)

Transport **HTTP**; Auth = OAuth 2.0 "**Authorization Code (With PKCE)**"; scope
value `mcp_api refresh_token`; challenge method SHA-256; "Send client credentials
in body."

---

## 4. Discovery

Two distinct questions: *how does the client discover **auth**?* (automatic, from
the endpoint URL) and *how do you discover which **servers/endpoints** exist?*
(out-of-band — there's no client-facing registry).

### Auth discovery — automatic (OAuth `.well-known`)

A spec-compliant MCP client (Claude Code does this) needs **only the endpoint
URL**; it discovers the rest by the standard OAuth metadata chain:

1. **Unauthenticated request → 401.** Hitting the endpoint with no token returns
   `HTTP 401 {"errors":[{"message":"JWT Token is required"}]}` — the gateway is a
   JWT-bearer resource server.
2. **Protected-resource metadata (RFC 9728)** — the **path-suffixed**, per-server
   document declares the scopes:
   `GET https://api.salesforce.com/.well-known/oauth-protected-resource/platform/mcp/v1/platform/sobject-all`
   →
   ```json
   { "resource": ".../platform/mcp/v1/platform/sobject-all",
     "authorization_servers": [".../platform/mcp/v1/platform/sobject-all"],
     "scopes_supported": ["mcp_api", "refresh_token"] }
   ```
   (The **host-root** `.well-known/oauth-protected-resource` is generic and lists
   `api, sfap_api, ...` — *not* `mcp_api`. Use the per-server, path-suffixed one.)
3. **Authorization-server metadata (RFC 8414)** resolves to:
   issuer `https://login.salesforce.com`, authorize
   `…/services/oauth2/authorize`, token `…/services/oauth2/token`,
   `code_challenge_methods_supported: ["S256"]` (PKCE), grants
   `authorization_code` + `refresh_token`.

So the client runs Auth-Code + PKCE against `login.salesforce.com`
(`test.salesforce.com` for sandboxes) and attaches the resulting bearer JWT to
every MCP call. The OAuth metadata is served by the **gateway host**
(`api.salesforce.com`), **not** the org My Domain (the My Domain returns "URL No
Longer Exists" for these paths).

### Server discovery — out-of-band

There is **no client-facing registry** that lists an org's MCP endpoints; you
learn the endpoint URL out-of-band and enter it (plus the Consumer Key) in the
client. What does exist:

- **Within a session:** once connected, the standard MCP `tools/list` call returns
  the server's tools (e.g. `getUserInfo`, `soqlQuery`, `getObjectSchema`, `find`).
- **Admin / Setup:** Setup → **API Catalog → MCP Servers** lists the org's servers
  (Salesforce Servers + External Servers tabs); this is where servers are enabled.
- **Programmatic (what's activated):** query the Tooling API —
  `SELECT DeveloperName, MasterLabel, Active, McpServerId FROM McpServerAccess`
  (platform servers have `McpServerId = null`). There is no API that enumerates
  available-but-inactive platform servers.

---

## 4b. Troubleshooting auth

- **`invalid code verifier` on the FIRST `/mcp` auth call, then success on retry.**
  A PKCE verifier/challenge transient seen against a freshly-deployed ECA. It is
  **expected, not a misconfiguration** — just run `/mcp` and authenticate again;
  the second attempt succeeds. (Confirmed live.)
- **Brand-new ECA reports an invalid `client_id`/app on first use.** ECAs can take
  a few minutes to propagate. Wait ~5 min and retry before suspecting the config.
- **`ERR_TLS_CERT_ALTNAME_INVALID` during the token fetch.** The auth server the
  client was sent to (the RFC 8414 `issuer` — see §4) serves a TLS cert that
  doesn't cover its own hostname. This shows up on some non-standard scratch fleets
  whose My Domain host presents a wildcard cert with SANs for *other* subdomain
  patterns but **none** matching the scratch host itself, so the token POST fails
  cert validation. It is injected by OAuth discovery (the org's self-reported
  `issuer`), **not** by the URL you typed — so re-adding the MCP server, rewriting
  the browser authorize URL, or an `/etc/hosts` remap all fail to fix it (the client
  still POSTs to the bad-cert `token_endpoint`).
  **Fix:** use an org whose My Domain has a valid cert (production or sandbox
  `*.my.salesforce.com`, or a standard scratch org). Diagnose a host with
  `echo | openssl s_client -connect <host>:443 -servername <host> 2>/dev/null | openssl x509 -noout -text | grep -A1 "Alternative Name"` and
  `curl -s -o /dev/null -w "ssl_verify=%{ssl_verify_result}\n" -X POST https://<host>/services/oauth2/token -d "grant_type=authorization_code&code=x"`
  (`ssl_verify=0` = cert OK).

### Choosing the endpoint path (org-qualified vs simple)

The gateway returns `401 JWT-required` for **any** path shape, so a 401 does *not*
confirm the path is correct. Confirm a path with the per-server protected-resource
doc instead (`200` + JSON = valid):
`GET https://api.salesforce.com/.well-known/oauth-protected-resource/<path>`.

| Path form | RFC 8414 `issuer` | Notes |
|-----------|-------------------|-------|
| `…/v1/platform/sobject-all` (simple) | `login.salesforce.com` | generic valid cert, but org-ambiguous |
| `…/v1/d/<myDomainPrefix>/platform/sobject-all` (org-qualified) | the org's own `*.my.salesforce.com` | **prefer this** — pins the org; valid cert on a normal org |

Prefer the **org-qualified** path for **platform** servers: it deterministically
targets one org. Its `issuer` is that org's My Domain, so it only works when that
domain has a valid cert (the TLS-SAN gap above is exactly when it doesn't).

**Custom servers use a different path shape:** `…/v1/custom/<ApiName>` (e.g.
`https://api.salesforce.com/platform/mcp/v1/custom/RLMQuotingMCP`) — **no
`d/<prefix>` segment**; the custom name scopes it to the org. Do **not** guess a
custom server's path: the gateway 401s every path pre-auth and the well-known doc
echoes any path back, so neither confirms it. Read the exact URL from **Setup →
API Catalog → MCP Servers → <server> → Server URL** and use it verbatim.

### One ECA covers every server — no reauth when adding servers

The ECA governs only OAuth (`client_id` + scopes); it does **not** reference any
server. So a single ECA / Consumer Key authenticates **every** MCP server in the
org. Adding another server is just another `claude mcp add` entry reusing the same
`--client-id` — and a newly-added entry typically shows `✔ Connected`
**automatically** off the already-issued token (no per-server `/mcp` reauth).
Activating more servers on the org needs no ECA change either. For **multiple
orgs**, create one entry per (org × server), name it with the org, and use the
org-qualified path so each entry stays pinned; tokens are stored per entry, so
orgs don't collide and reauth is per-entry.

## 5. Permissions & limits

Three layers gate whether a user can invoke a server's tools:

1. **Server enablement** — the server must be activated
   (`McpServerAccess.Active = true`; Setup → API Catalog → MCP Servers).
2. **ECA OAuth policies** — can restrict authentication to a permission set, an IP
   allowlist, and refresh-token TTL/rotation.
3. **The running user's own CRUD / FLS / sharing** — every tool call executes as
   the authenticated user. The server's tool set bounds *which* operations exist
   (e.g. `sobject-reads` is read-only; `sobject-all` adds write + delete), but the
   user's permissions still apply on top.

**Known limitation:** Hosted MCP Servers are **incompatible with API Access
Control (External Client App)**. With API Access Control enabled, the server
authenticates but query tool calls are **blocked**. Workaround: disable API
Access Control, or grant "Use any API Client" (not recommended in production).

---

## Related references

- `docs/references/mcp-server-admin.md` — author/deploy/activate servers
  (McpServerDefinition metadata + McpServerAccess Tooling API + CRUD lifecycle).
- `docs/features/mcp-servers.md` — RLM build feature (`mcp` flag, `deploy_post_mcp`,
  `activate_mcp_servers`, the manifest at `datasets/tooling/McpServerAccess/`).
- `unpackaged/post_mcp/README.md` — the shipped custom-server bundle.
