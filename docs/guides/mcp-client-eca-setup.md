# Connecting an MCP Client to an Org's Hosted MCP Servers

> **Detailed client-connection companion** to the canonical setup runbook.
> Provisioning the OAuth client (the **External Client App**) is **automated by
> the build** — this guide covers the two things that aren't: determining the
> right **endpoint URL** for an org's instance type, and **registering +
> authenticating** each client (Claude Code, Cursor, Claude Desktop, Postman, …).
>
> **Start here for the end-to-end flow:**
> `docs/references/mcp-server-admin.md` → **End-to-End Setup Runbook**.
>
> **Companions:**
> `.cursor/skills/mcp-server/SKILL.md` (client/consumption reference + troubleshooting),
> `docs/features/mcp-servers.md` (the `mcp` build feature).

## What you're building, and why

An MCP client authenticates to a Hosted MCP server over OAuth 2.0
**Authorization Code + PKCE**. The OAuth client **must** be an **External Client
App (ECA)** — classic **Connected Apps are not supported** for Hosted MCP.

In this repo the ECA (**`RLMQuotingMcpClient`**) is **committed and deploys
automatically** as four source-format components under `unpackaged/post_mcp/`:

| Component | Type · suffix · dir |
|-----------|---------------------|
| Parent app | `ExternalClientApplication` · `.eca-meta.xml` · `externalClientApps/` |
| Global OAuth | `ExtlClntAppGlobalOauthSettings` · `.ecaGlblOauth-meta.xml` · `extlClntAppGlobalOauthSets/` |
| Scopes | `ExtlClntAppOauthSettings` · `.ecaOauth-meta.xml` · `extlClntAppOauthSettings/` |
| Policies | `ExtlClntAppOauthConfigurablePolicies` · `.ecaOauthPlcy-meta.xml` · `extlClntAppOauthPolicies/` |

The committed files are **fully org-agnostic** — they carry no Org ID, no
consumer key, and no `oauthLink`; the platform supplies/auto-resolves all three
on deploy. **One ECA authenticates every MCP server in the org.** For how it was
made static (and the rule to re-strip those three fields if you ever re-retrieve
it), see **Maintaining the committed ECA** in `docs/references/mcp-server-admin.md`.

### Prerequisites (org side)

- The org must have **`SalesforceHostedMCP`** enabled and the target MCP server(s)
  **activated** (`McpServerAccess.Active = true`). In the RLM build this is the
  `mcp` feature flag → `prepare_mcp`. Verify:
  ```bash
  sf data query --use-tooling-api \
    -q "SELECT DeveloperName, MasterLabel, Active FROM McpServerAccess WHERE Active = true" \
    --target-org <sf_alias_or_username>
  ```
- The org must allow ECAs (scratch defs in this repo already list the
  **`ExternalClientApps`** feature). A System Administrator can deploy/authorize.

---

## Step 1 — Provision the org (build-automated)

```bash
cci flow run prepare_mcp --org <cci_alias>
```

This deploys the servers + flow **and** the committed `RLMQuotingMcpClient` ECA,
then activates the manifest servers. No ad-hoc files, no `/tmp` scaffolding. To
run/verify the pieces individually, see `docs/references/mcp-server-admin.md`.

## Step 2 — Read back the org-minted Consumer Key (once per org)

The Consumer Key is generated at deploy time and is **not** in source — retrieve it:

```bash
sf project retrieve start -m "ExtlClntAppGlobalOauthSettings:RLMQuotingMcpClient" \
  --target-org <cci-or-sf-alias> --target-metadata-dir /tmp/eca
grep -oE '<consumerKey>[^<]+</consumerKey>' \
  /tmp/eca/unpackaged/extlClntAppGlobalOauthSets/RLMQuotingMcpClient.ecaGlblOauth
```

The `<consumerKey>` value is the client's `client_id`. In the PKCE model it is
**not** a secret, but it **is** org-specific — recompute it per org.

**Confirm the scopes registered** (Tooling columns are booleans, not the CSV):
```bash
sf data query --use-tooling-api --target-org <cci-or-sf-alias> \
  -q "SELECT OauthScopesMCP_API, OauthScopesREFRESH_TOKEN FROM ExtlClntAppOauthSettings
      WHERE ExternalClientApplicationId IN
        (SELECT Id FROM ExternalClientApplication WHERE DeveloperName='RLMQuotingMcpClient')"
# expect: OauthScopesMCP_API = true, OauthScopesREFRESH_TOKEN = true
```
> The metadata enum is **`MCP`** (maps to the runtime `mcp_api` scope). A
> wrong/missing MCP scope surfaces at login as `error=invalid_scope`.

## Step 3 — Determine the endpoint URL (instance-dependent)

The server path is `<apiDomain>/<server>` using the **MasterLabel** hyphen form
(`platform_sobject_all` → `platform/sobject-all`; a custom server uses
`custom/<ApiName>`). The **host/prefix** depends on the org's instance type:

| Org instance | Endpoint |
|--------------|----------|
| Production | `https://api.salesforce.com/platform/mcp/v1/<apiDomain>/<server>` |
| Sandbox | `https://api.salesforce.com/platform/mcp/v1/sandbox/<apiDomain>/<server>` |
| Org-qualified (pins one org by My Domain) | `https://api.salesforce.com/platform/mcp/v1/d/<myDomainPrefix>/<apiDomain>/<server>` |

`<myDomainPrefix>` is the org's My Domain label (the instance-url host without
`.my.salesforce.com`). The exact custom-server URL is also shown in
**Setup → API Catalog → MCP Servers**. **Confirm** the org's auth issuer + scopes
via the per-server `.well-known` (this also disambiguates which host/prefix applies):
```bash
curl -s "https://api.salesforce.com/.well-known/oauth-protected-resource/platform/mcp/v1/d/<myDomainPrefix>/platform/sobject-all"
# scopes_supported should include "mcp_api"; authorization_servers names the issuer
```
A correct endpoint returns `HTTP 401 {"errors":[{"message":"JWT Token is required"}]}`
to an unauthenticated POST (401, not 404, proves host + path). The gateway returns
401 for *any* path under it, so 401 alone is necessary but not sufficient — pair it
with the Setup UI / `.well-known` to confirm the exact server segment.

## Step 4 — Register with the client and authenticate

The committed ECA carries callback URLs for all four clients below, so **one ECA
serves all of them** (`callbackUrl` is a newline-separated list — verified to
accept multiple). For a client not listed (Slack, ChatGPT, …), add its callback
URL to the `.ecaGlblOauth` file and redeploy `post_mcp`.

| Client | Configure | Callback URL (already on the ECA) |
|--------|-----------|-----------------------------------|
| **Claude Code** | `claude mcp add --transport http --scope user --client-id <key> --callback-port 8675 <name> <url>` | `http://localhost:8675/callback` |
| **Claude Desktop** | Connectors → **+** → add custom → Server URL → Advanced → OAuth Client ID = `<key>` | `https://claude.ai/api/mcp/auth_callback` |
| **Cursor** | add to `mcp.json`: server `url` + client id `<key>` | `cursor://anysphere.cursor-mcp/oauth/callback` |
| **Postman** | HTTP transport; OAuth2 Auth-Code-with-PKCE; scope `mcp_api refresh_token` | `https://oauth.pstmn.io/v1/callback` |

Claude Code example (one entry per server, all reusing the **same** key):
```bash
claude mcp add --transport http --scope user \
  --client-id "<CONSUMER_KEY>" --callback-port 8675 \
  rlm-sobject-all "<ENDPOINT_URL_FROM_STEP_3>"
```
- No `--client-secret` (PKCE).
- `--callback-port` **must equal** the ECA `callbackUrl` port (8675).

**Authenticate (interactive — cannot be scripted):**
1. **Restart Claude Code** if the server was added mid-session — the `/mcp` menu
   only lists servers loaded at startup.
2. Run `/mcp` → select the server → **Authenticate** (Desktop/Cursor: their connect
   button).
3. Browser opens to the org's login host; log in as the target user and approve
   the `mcp_api` + `refresh_token` consent. Tip: `sf org open --target-org <alias>`
   first so the browser already has a session for that org.
4. `/mcp` flips to `✓ connected`; the server's tools (`soqlQuery`,
   `getObjectSchema`, `getUserInfo`, `find`, …) become callable.

> The **first** auth call on a freshly deployed ECA may fail with
> `invalid code verifier` — just retry; the second attempt succeeds (a PKCE
> transient). Brand-new ECAs can also take a few minutes to propagate.

---

## Connecting to a different org later

No add/remove of the ECA is needed — it's the same committed bundle everywhere.
Per new org:
1. Confirm `SalesforceHostedMCP` + the target server is active (prereqs query).
2. `prepare_mcp` (or just `deploy_post_mcp`) against the new org — ECA deploys with it.
3. **Read back that org's Consumer Key** (step 2) — keys are per-org.
4. **Recompute the endpoint URL** for that org's instance (step 3).
5. `claude mcp add …` a new entry with the new key + URL → `/mcp` authenticate.

Everything except the Consumer Key and the endpoint URL is identical across orgs.

## Troubleshooting

| Symptom | Cause / fix |
|---------|-------------|
| `error=invalid_scope` at login | MCP scope not on the ECA — confirm `OauthScopesMCP_API = true` (step 2); redeploy `post_mcp`, wait ~30s |
| `invalid code verifier` on first auth | PKCE transient on a freshly deployed ECA — retry; the second attempt succeeds |
| Login loops / "app not found" | ECA propagation delay after first deploy — retry after a few minutes |
| `redirect_uri` mismatch | `--callback-port` ≠ the ECA `callbackUrl` port (8675), or the client's callback URL isn't on the ECA list |
| Server absent from `/mcp` menu | Session started before `claude mcp add` — restart Claude Code |
| Tool calls blocked after auth succeeds | Org has **API Access Control (ECA)** enabled — incompatible with Hosted MCP; disable it or grant "Use any API Client" (not for prod) |
| `ERR_TLS_CERT_ALTNAME_INVALID` during OAuth | The org's My Domain host serves a wildcard cert whose SANs don't match the host, injected via the RFC 8414 issuer in OAuth discovery — unfixable client-side. **Use an org whose My Domain has a valid cert** (production/sandbox `*.my.salesforce.com`, or a standard scratch org) |

## Notes & provenance

- Live-validated against an org on Salesforce v67.0 (Release 262): the four
  committed components deploy org-agnostically,
  the Consumer Key is retrieved post-deploy, `OauthScopesMCP_API` /
  `OauthScopesREFRESH_TOKEN` confirm `true`, the endpoint returns the expected 401,
  and a real multi-callback deploy persisted all four client callback URLs. The
  interactive browser login is the only step not machine-verified.
