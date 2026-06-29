# MCP Server Administration — Build & Activate (Salesforce v67.0)

> **Audience:** admins / build engineers who **author, deploy, and activate**
> Salesforce Hosted MCP servers in an org.
> **Companion (consumption side):** `.cursor/skills/mcp-server/SKILL.md` — how an
> MCP **client** connects to and uses an activated server.
> **RLM build wiring:** `docs/features/mcp-servers.md` (the `mcp` flag,
> `deploy_post_mcp`, `activate_mcp_servers`).

MCP Servers let an org expose capabilities (Flows, SObjects, etc.) as tools that
AI agents invoke over the Model Context Protocol. This reference covers the
**server-side lifecycle**: the deployable `McpServerDefinition` metadata type, the
Tooling-API `McpServerAccess` activation object, and their CRUD.

## Quick Rules

1. **McpServerDefinition** is the deployable metadata type — use it for the
   server definition and its tools/prompts.
2. **McpServerAccess** controls activation — it is **NOT** deployable via
   Metadata API. Use the Tooling API to create/update it post-deploy.
3. Tool backing: tools reference Flow Actions via API Catalog
   (`fa:flow-<FlowApiName>`). The Flow must exist and be active in the org.
4. Activation = creating/updating an `McpServerAccess` record with
   `Active = true` pointing to the server's `McpServerDefinition` Id (custom
   servers) or `McpServerId = null` (platform servers).
5. Deactivation flips `Active` to `false` on the same record (does not delete it).

## DO NOT

- Do NOT assume `McpServerAccess` can be deployed via `sf project deploy` —
  it will fail. Always use the Tooling API for activation state.
- Do NOT use SOQL (standard or Tooling) to query `McpServer` — use
  `McpServerDefinition` on the Tooling API instead.
- Do NOT hardcode `McpServerDefinition` IDs across orgs — query by
  `DeveloperName` to find the correct record after deploy.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│              McpServerDefinition (Metadata API)          │
│  - DeveloperName, MasterLabel, Description              │
│  - <tools> (embedded McpServerToolApiDefinition)        │
│  - <prompts> (embedded McpServerPromptDefinition)       │
└──────────────────────────┬──────────────────────────────┘
                           │ McpServerId (FK)
┌──────────────────────────▼──────────────────────────────┐
│              McpServerAccess (Tooling API only)          │
│  - DeveloperName, MasterLabel                           │
│  - Active (boolean) ← controls Inactive/Active status   │
│  - McpServerId (reference to McpServerDefinition)       │
└─────────────────────────────────────────────────────────┘
```

### Tooling API Entity Summary

| Object | Purpose | Queryable | Deployable (Metadata API) |
|--------|---------|-----------|---------------------------|
| `McpServerDefinition` | Server + tools + prompts | Yes (Tooling API) | Yes |
| `McpServerAccess` | Activation toggle | Yes (Tooling API) | **No** |
| `McpServerToolApiDefinition` | Tool→API binding details | Yes (Tooling API) | Embedded in McpServerDefinition XML |
| `McpServerPromptDefinition` | Prompt definitions | Yes (Tooling API) | Embedded in McpServerDefinition XML |

### Key Prefix Reference

| Object | Prefix | Example |
|--------|--------|---------|
| McpServerDefinition | `1g1` | `1g1g7000000037ZAAQ` |
| McpServerAccess | `1fz` | `1fzg7000001z4cPAAQ` |
| McpServerToolApiDefinition | `1g3` | `1g3g700000003h3AAA` |
| McpServerTool (parent of ApiDef) | `1g2` | `1g2g700000001c1AAA` |

---

## McpServerDefinition — Metadata Format

File location: `mcpServerDefinitions/<DeveloperName>.mcpServerDefinition-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<McpServerDefinition xmlns="http://soap.sforce.com/2006/04/metadata">
    <description>Human-readable description</description>
    <masterLabel>Display Label</masterLabel>
    <tools>
        <apiDefinition>
            <apiIdentifier>fa:flow-MyNamespace__MyFlowApiName</apiIdentifier>
            <apiSource>API_CATALOG</apiSource>
            <operation>MyNamespace__MyFlowApiName</operation>
        </apiDefinition>
        <descriptionOverride>What the tool does (shown to AI agent)</descriptionOverride>
        <toolName>auto_generated_truncated_name</toolName>
        <toolTitle>MyNamespace__MyFlowApiName</toolTitle>
    </tools>
    <!-- Additional <tools> blocks for more tools -->
    <!-- <prompts> blocks for prompt definitions -->
</McpServerDefinition>
```

### Tool Element Reference

| Element | Required | Description |
|---------|----------|-------------|
| `apiDefinition/apiIdentifier` | Yes | API Catalog identifier. Format: `fa:flow-<FlowApiName>` for Flows |
| `apiDefinition/apiSource` | Yes | Always `API_CATALOG` for Flow-backed tools |
| `apiDefinition/operation` | Yes | The specific operation (usually the Flow API name) |
| `descriptionOverride` | No | Custom description shown to AI (overrides auto-generated) |
| `toolName` | Yes | System-generated truncated identifier (max ~64 chars) |
| `toolTitle` | Yes | Display name (usually matches the Flow API name) |

### Supported apiSource Values

| Value | Backing | apiIdentifier Format |
|-------|---------|---------------------|
| `API_CATALOG` | Flow Action | `fa:flow-<FlowApiName>` |

### Naming constraint

An MCP **server name** must start with a letter, be alphanumeric only, and be
2–40 chars — **no underscores** (e.g. `RLMQuotingMCP`, not `RLM_QuotingMCP`). The
`<masterLabel>` (friendly display name) *may* contain spaces.

---

## McpServerAccess — Tooling API Schema

### Fields

| Field | Type | Createable | Updateable | Description |
|-------|------|-----------|-----------|-------------|
| `Id` | id | — | — | Record ID (prefix `1fz`) |
| `DeveloperName` | string | Yes | Yes | Unique name (match the server's DeveloperName) |
| `MasterLabel` | string | Yes | Yes | Display label |
| `Language` | picklist | Yes | Yes | Language code (default `en_US`) |
| `Active` | boolean | Yes | Yes | `true` = server is active, `false` = inactive |
| `McpServerId` | reference | Yes | Yes | FK to McpServerDefinition ID. `null` = platform-wide |

### Platform-Provided Servers

Orgs with MCP enabled ship several built-in platform servers, each represented by
an `McpServerAccess` record with `McpServerId = null` (applies org-wide, not to a
specific custom definition). Known `DeveloperName` → `MasterLabel`:

| `DeveloperName` | `MasterLabel` | Notes |
|-----------------|---------------|-------|
| `platform_sobject_all` | `sobject-all` | Full SObject tools: read + create/update + delete |
| `platform_sobject_deletes` | `sobject-deletes` | Strict subset of `sobject-all` (read + delete, no writes) |
| `platform_metadata_experts` | `metadata-experts` | — |
| `platform_salesforce_api_context` | `salesforce-api-context` | — |

These have **no** `McpServerDefinition` and are inactive until an `McpServerAccess`
record activates them. **There is no API that enumerates available-but-inactive
platform servers**, so a server's `DeveloperName` only becomes discoverable after
it is activated once (in Setup → API Catalog → MCP Servers): then read it via
`SELECT DeveloperName, MasterLabel, Language FROM McpServerAccess WHERE McpServerId = null`.
Do not modify or delete an existing platform record's label/linkage.

---

## CRUD Operations

### Deploy a new MCP Server (Metadata API)

```bash
sf project deploy start \
  --source-dir path/to/mcpServerDefinitions/ \
  --target-org <username>
```

The server deploys as **Inactive**. Activation is a separate step.

### Retrieve an MCP Server

```bash
sf project retrieve start \
  --metadata "McpServerDefinition:<DeveloperName>" \
  --target-org <username> \
  --output-dir <dir>
```

### Activate (Tooling API)

**First activation** (no McpServerAccess record exists yet):

```
POST /services/data/v67.0/tooling/sobjects/McpServerAccess/
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "DeveloperName": "<ServerDeveloperName>",
  "MasterLabel": "<ServerLabel>",
  "Language": "en_US",
  "Active": true,
  "McpServerId": "<McpServerDefinition_Id>"
}
```

**Re-activation** (record exists with `Active = false`):

```
PATCH /services/data/v67.0/tooling/sobjects/McpServerAccess/<McpServerAccess_Id>
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "Active": true
}
```

### Deactivate (Tooling API)

```
PATCH /services/data/v67.0/tooling/sobjects/McpServerAccess/<McpServerAccess_Id>
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "Active": false
}
```

### Delete (Tooling API)

```
DELETE /services/data/v67.0/tooling/sobjects/McpServerAccess/<McpServerAccess_Id>
Authorization: Bearer <access_token>
```

### Query (Tooling API)

```
GET /services/data/v67.0/tooling/query/?q=SELECT+Id,DeveloperName,Active,McpServerId+FROM+McpServerAccess+WHERE+DeveloperName='<ServerDeveloperName>'
```

---

## Activation Lifecycle

```
Deploy McpServerDefinition ──► Server exists (Inactive)
                                      │
                            POST McpServerAccess
                            (Active=true, McpServerId=<Id>)
                                      │
                                      ▼
                              Server is Active
                                      │
                          PATCH Active=false
                                      │
                                      ▼
                              Server is Inactive
                              (record persists)
                                      │
                          PATCH Active=true
                                      │
                                      ▼
                              Server is Active again
```

---

## Automation Pattern (Apex / CCI Task)

In the RLM build, activation is automated by the `activate_mcp_servers` CCI task
(`tasks/rlm_activate_mcp_servers.py`), driven by the source-controlled manifest at
`datasets/tooling/McpServerAccess/`. To activate an MCP Server programmatically
from Apex instead:

```apex
// Example: activate an MCP Server named "My_Server" after deploy.
// Replace the DeveloperName with your actual server name.

String serverDevName = 'My_Server';

// 1. Find the McpServerDefinition by DeveloperName
HttpRequest req = new HttpRequest();
req.setEndpoint(Url.getOrgDomainUrl().toExternalForm()
    + '/services/data/v67.0/tooling/query/?q='
    + EncodingUtil.urlEncode(
        'SELECT Id FROM McpServerDefinition WHERE DeveloperName = \'' + serverDevName + '\'',
        'UTF-8'));
req.setMethod('GET');
req.setHeader('Authorization', 'Bearer ' + UserInfo.getSessionId());
Http http = new Http();
HttpResponse res = http.send(req);
// Parse the Id from response...
String mcpServerId = '<parsed_id>';

// 2. Check if McpServerAccess already exists
req = new HttpRequest();
req.setEndpoint(Url.getOrgDomainUrl().toExternalForm()
    + '/services/data/v67.0/tooling/query/?q='
    + EncodingUtil.urlEncode(
        'SELECT Id, Active FROM McpServerAccess WHERE McpServerId = \'' + mcpServerId + '\'',
        'UTF-8'));
req.setMethod('GET');
req.setHeader('Authorization', 'Bearer ' + UserInfo.getSessionId());
res = http.send(req);
// Parse response...

// 3a. If no record exists → POST to create
req = new HttpRequest();
req.setEndpoint(Url.getOrgDomainUrl().toExternalForm()
    + '/services/data/v67.0/tooling/sobjects/McpServerAccess/');
req.setMethod('POST');
req.setHeader('Authorization', 'Bearer ' + UserInfo.getSessionId());
req.setHeader('Content-Type', 'application/json');
req.setBody(JSON.serialize(new Map<String, Object>{
    'DeveloperName' => serverDevName,
    'MasterLabel' => serverDevName,
    'Language' => 'en_US',
    'Active' => true,
    'McpServerId' => mcpServerId
}));
res = http.send(req);

// 3b. If record exists but Active=false → PATCH to activate
req = new HttpRequest();
req.setEndpoint(Url.getOrgDomainUrl().toExternalForm()
    + '/services/data/v67.0/tooling/sobjects/McpServerAccess/<existing_record_id>');
req.setMethod('PATCH');
req.setHeader('Authorization', 'Bearer ' + UserInfo.getSessionId());
req.setHeader('Content-Type', 'application/json');
req.setBody('{"Active": true}');
res = http.send(req);
```

---

## Querying Related Data

### List all tools for a server (Tooling API)

```
SELECT Id, ApiSource, ApiIdentifier, Operation, ToolId
FROM McpServerToolApiDefinition
```

### Describe available fields on any entity

```
GET /services/data/v67.0/tooling/sobjects/McpServerAccess/describe/
GET /services/data/v67.0/tooling/sobjects/McpServerDefinition/describe/
GET /services/data/v67.0/tooling/sobjects/McpServerToolApiDefinition/describe/
GET /services/data/v67.0/tooling/sobjects/McpServerPromptDefinition/describe/
```

---

## End-to-End Setup Runbook (ECA → connected client)

This is the **repeatable, org-agnostic** path to a working MCP connection on any
org. Server activation (above) is only half of client access — a client also needs
an **External Client App (ECA) with the `mcp_api` scope** to obtain a token. The
ECA is **committed to this repo and deploys automatically**, so there are no
org-specific files to edit.

Set one variable and reuse it throughout:

```bash
ORG=<cci_alias>          # your CCI org alias; for raw sf use the username
```

### Step 1 — Provision the org (one command)

```bash
cci flow run prepare_mcp --org $ORG
```

This runs `deploy_post_mcp` (deploys the `RLMQuotingMCP` server + backing flow
**and** the committed `RLMQuotingMcpClient` ECA) then `activate_mcp_servers`
(activates the 4 manifest servers). The org is now fully provisioned. To run the
pieces individually or verify, see **Activation behavior** above.

> The committed ECA (`unpackaged/post_mcp/externalClientApps/` + the three
> `extlClntAppOauth*` dirs) is **fully org-agnostic** — it carries no Org ID, no
> consumer key, and no `oauthLink` (the org mints the key and resolves the
> org-scoping at deploy). It deploys to any org with zero edits. See
> **Maintaining the committed ECA** below for how it was made static.

### Step 2 — Read back the minted Consumer Key (once per org)

The key is generated at deploy time and is **not** in source. Retrieve it:

```bash
sf project retrieve start -m "ExtlClntAppGlobalOauthSettings:RLMQuotingMcpClient" \
  --target-org $ORG --target-metadata-dir /tmp/eca
grep -oE '<consumerKey>[^<]+</consumerKey>' \
  /tmp/eca/unpackaged/extlClntAppGlobalOauthSets/RLMQuotingMcpClient.ecaGlblOauth
```

Share this key (it is **not** a secret in the PKCE model, but it is org-specific)
with whoever connects. They also need the **endpoint URL(s)** — from Setup → API
Catalog → MCP Servers, or constructed: platform = `…/v1/d/<myDomainPrefix>/platform/<label>`,
custom = `…/v1/custom/RLMQuotingMCP` (read the exact custom URL from Setup).

### Step 3 — Configure + authenticate the client (per user, per client)

These steps are **interactive OAuth** and cannot be scripted by a deploy. The
committed ECA carries callback URLs for all four clients below, so one ECA serves
all of them:

| Client | Configure | Callback URL (already on the ECA) |
|--------|-----------|-----------------------------------|
| **Claude Code** | `claude mcp add --transport http --scope user --client-id <key> --callback-port 8675 <name> <url>` | `http://localhost:8675/callback` |
| **Claude Desktop** | Connectors → **+** → add custom → Server URL → Advanced → OAuth Client ID = `<key>` | `https://claude.ai/api/mcp/auth_callback` |
| **Cursor** | add to `mcp.json`: server `url` + client id `<key>` | `cursor://anysphere.cursor-mcp/oauth/callback` |
| **Postman** | HTTP transport; OAuth2 Auth-Code-with-PKCE; scope `mcp_api refresh_token` | `https://oauth.pstmn.io/v1/callback` |

Then **authenticate**: Claude Code `/mcp` → pick the entry; Desktop/Cursor → their
connect button. A browser opens, you approve, done. The **first** auth call may
fail with `invalid code verifier` — just retry (a PKCE transient on a fresh ECA).
Brand-new ECAs can also take a few minutes to propagate. See
`.cursor/skills/mcp-server/SKILL.md` for per-client `claude mcp add` examples (one
entry per server, all reusing the **same** key), the org-qualified-vs-`custom/`
path rule, and full troubleshooting.

> **Notes on `mcp_api`-only clients:** Slack/ChatGPT and other clients not listed
> need their own callback URL added to the ECA's `callbackUrl` (newline-separated
> list — verified to accept multiple). Add the URL and redeploy `post_mcp`.

> For the **detailed client-connection companion** — the per-instance endpoint-URL
> table (production / sandbox / internal-test-fleet), the `.well-known` verification
> curl, the full per-client config matrix, and an expanded troubleshooting table —
> see `docs/guides/mcp-client-eca-setup.md`.

### What is and isn't automated

| Step | Automated? |
|------|-----------|
| Deploy server + flow + ECA | ✅ `deploy_post_mcp` |
| Activate servers | ✅ `activate_mcp_servers` |
| Read back consumer key | ⬜ one `sf retrieve` + grep (per org) |
| Configure each client | ⬜ per user / per client |
| Browser OAuth approval | ⬜ inherently interactive |

> **Production note:** an ECA is a persisting, auditable OAuth client. The
> committed template uses `permittedUsersPolicyType=AllSelfAuthorized` (any user
> who authorizes can use it); tighten to a permission set in the `.ecaOauthPlcy`
> for shared/production orgs.

### Maintaining the committed ECA

The ECA lives in `unpackaged/post_mcp/` as **four** source-format components, one
per metadata type. **All four files must keep the `-meta.xml` suffix** — without
it, `sf project convert source` (which CCI's Deploy runs) warns
"appears to be in metadata format" and the components are at risk of being silently
dropped (see `unpackaged/post_mcp/README.md` and the source-format note below).

| Type | Source-format filename |
|------|------------------------|
| `ExternalClientApplication` | `externalClientApps/RLMQuotingMcpClient.eca-meta.xml` |
| `ExtlClntAppOauthSettings` | `extlClntAppOauthSettings/RLMQuotingMcpClient.ecaOauth-meta.xml` |
| `ExtlClntAppGlobalOauthSettings` | `extlClntAppGlobalOauthSets/RLMQuotingMcpClient.ecaGlblOauth-meta.xml` |
| `ExtlClntAppOauthConfigurablePolicies` | `extlClntAppOauthPolicies/RLMQuotingMcpClient.ecaOauthPlcy-meta.xml` |

To keep it org-agnostic, the committed files **omit** three fields that would
otherwise pin them to one org (the platform supplies/auto-resolves all three on
deploy): `orgScopedExternalApp` (`.eca`), `consumerKey` (`.ecaGlblOauth`), and
`oauthLink` (`.ecaOauth`). If you ever re-retrieve the ECA from an org to update
it, **strip those three again** before committing. Scopes are
`<commaSeparatedOauthScopes>RefreshToken, MCP</commaSeparatedOauthScopes>`; key
flags are `isPkceRequired=true`, `isNamedUserJwtEnabled=true`,
`isConsumerSecretOptional=true`. Validate with a dry-run that reports **0
warnings**: `sf project deploy start --source-dir unpackaged/post_mcp --target-org <org> --dry-run`.

## Limitations & Notes

- `McpServerDefinition` is in the SF CLI source-tracking registry
  (`directoryName: mcpServerDefinitions`, `suffix: mcpServerDefinition`), so it
  deploys/retrieves as normal source format.
- `McpServerAccess` is entirely Tooling API — no metadata deploy/retrieve support.
- The `McpServer` sObject name (without suffix) is **not** queryable via standard
  SOQL or the Tooling API — always use `McpServerDefinition`.
- Tool backing is limited to Flow Actions via API Catalog (`apiSource` is a
  picklist, so other sources may exist).
- The `toolName` field is auto-generated (a truncated concatenation of the tool
  title and API identifier); treat it as system-managed rather than setting it
  manually.
