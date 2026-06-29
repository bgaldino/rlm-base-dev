---
name: mcp-server
description: >-
  Salesforce MCP Server metadata and Tooling API reference for v67.0.
  Use when creating, deploying, activating, or managing MCP Servers and their
  tools/prompts in Salesforce orgs. Covers the McpServerDefinition metadata
  type, McpServerAccess activation via Tooling API, and the full CRUD lifecycle.
---

# MCP Server Management (Salesforce v67.0)

MCP Servers in Salesforce allow exposing org capabilities (Flows, Apex, etc.)
as tools that AI agents can invoke via the Model Context Protocol.

## RLM build integration

This repo ships a custom MCP server and wires deploy + activation into the build:

- **Bundle:** `unpackaged/post_mcp/` (source-format, no `package.xml` — like every
  other `deploy_post_*`; `McpServerDefinition` is in the SF CLI source-tracking
  registry as of CLI 2.140.6, so CCI converts + deploys it normally). Contains
  `mcpServerDefinitions/RLMQuotingMCP.mcpServerDefinition-meta.xml` (9
  quoting/opportunity tools) and
  `flows/RLM_Create_Opportunity_Agentforce.flow-meta.xml`.
- **Feature flag:** `mcp` (default `false`, opt-in).
- **Deploy task:** `deploy_post_mcp` (`cumulusci.tasks.salesforce.Deploy`).
- **Activation task:** `activate_mcp_servers`
  (`tasks/rlm_activate_mcp_servers.py` → `ActivateMcpServers`) — Tooling-API upsert of
  `McpServerAccess` for `RLMQuotingMCP`, `platform_sobject_all`, `platform_sobject_deletes`.
- **Flow:** `prepare_mcp`, run as a conditional sub-flow of the general `prepare_ai`
  block (step 22 of `prepare_rlm_org`: `prepare_agents` then `prepare_mcp`, each
  behind its own feature flag).
- **Naming constraint (learned live):** MCP server names must be alphanumeric, start
  with a letter, 2–40 chars — **no underscores** (hence `RLMQuotingMCP`). The
  `<masterLabel>` may contain spaces.
- See `docs/features/mcp-servers.md` for the full feature writeup.

## Quick Rules

1. **McpServerDefinition** is the only deployable metadata type — use it for
   the server definition and its tools/prompts.
2. **McpServerAccess** controls activation — it is **NOT** deployable via
   Metadata API. Use the Tooling API to create/update it post-deploy.
3. Tool backing: tools reference Flow Actions via API Catalog
   (`fa:flow-<FlowApiName>`). The Flow must exist and be active in the org.
4. Activation = creating/updating a `McpServerAccess` record with
   `Active = true` pointing to the server's `McpServerDefinition` Id.
5. Deactivation flips `Active` to `false` on the same record (does not delete it).

## DO NOT

- Do NOT assume `McpServerAccess` can be deployed via `sf project deploy` —
  it will fail. Always use Tooling API for activation state.
- Do NOT use SOQL (standard or Tooling) to query `McpServer` — use
  `McpServerDefinition` on the Tooling API instead.
- Do NOT hardcode McpServerDefinition IDs across orgs — query by
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

### Platform-Provided Record

Every org with MCP enabled has a built-in record:
- `DeveloperName`: `platform_sobject_all`
- `MasterLabel`: `sobject-all`
- `Active`: `true`
- `McpServerId`: `null` (applies org-wide, not to a specific custom server)

This controls the platform SObject MCP server — do not modify or delete it.

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
POST /services/data/v66.0/tooling/sobjects/McpServerAccess/
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
PATCH /services/data/v66.0/tooling/sobjects/McpServerAccess/<McpServerAccess_Id>
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "Active": true
}
```

### Deactivate (Tooling API)

```
PATCH /services/data/v66.0/tooling/sobjects/McpServerAccess/<McpServerAccess_Id>
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "Active": false
}
```

### Delete (Tooling API)

```
DELETE /services/data/v66.0/tooling/sobjects/McpServerAccess/<McpServerAccess_Id>
Authorization: Bearer <access_token>
```

### Query (Tooling API)

```
GET /services/data/v66.0/tooling/query/?q=SELECT+Id,DeveloperName,Active,McpServerId+FROM+McpServerAccess+WHERE+DeveloperName='<ServerDeveloperName>'
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

To activate an MCP Server programmatically after deploy:

```apex
// Example: activate an MCP Server named "My_Server" after deploy.
// Replace the DeveloperName with your actual server name.

String serverDevName = 'My_Server';

// 1. Find the McpServerDefinition by DeveloperName
HttpRequest req = new HttpRequest();
req.setEndpoint(Url.getOrgDomainUrl().toExternalForm()
    + '/services/data/v66.0/tooling/query/?q='
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
    + '/services/data/v66.0/tooling/query/?q='
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
    + '/services/data/v66.0/tooling/sobjects/McpServerAccess/');
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
    + '/services/data/v66.0/tooling/sobjects/McpServerAccess/<existing_record_id>');
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
GET /services/data/v66.0/tooling/sobjects/McpServerAccess/describe/
GET /services/data/v66.0/tooling/sobjects/McpServerDefinition/describe/
GET /services/data/v66.0/tooling/sobjects/McpServerToolApiDefinition/describe/
GET /services/data/v66.0/tooling/sobjects/McpServerPromptDefinition/describe/
```

---

## Limitations & Notes

- `McpServerDefinition` **is** in the SF CLI source-tracking registry as of CLI
  2.140.6 (`directoryName: mcpServerDefinitions`, `suffix: mcpServerDefinition`),
  so it deploys/retrieves as normal source format. On older CLIs (≤ v2.138) it was
  absent from the registry — there a source-format deploy would silently drop the
  type, and an mdapi-format bundle (with `package.xml`) was required instead.
- `McpServerAccess` is entirely Tooling API — no metadata deploy/retrieve support.
- The `McpServer` sObject name (without suffix) is **not** queryable via standard
  SOQL or the Tooling API — always use `McpServerDefinition`.
- Tool backing is currently limited to Flow Actions via API Catalog. The
  `apiSource` field is a picklist suggesting future sources may be added.
- The `toolName` field appears to be auto-generated (truncated concatenation of
  tool title and API identifier) — setting it manually during deploy has not been
  tested for conflicts.
