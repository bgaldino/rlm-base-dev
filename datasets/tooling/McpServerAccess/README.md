# McpServerAccess Payloads

JSON payloads consumed by the `activate_mcp_servers` CCI task to **activate**
Salesforce Hosted MCP servers.

These files are **not** SFDMU datasets and **not** Metadata-API deploy content.
They are the source-controlled, explicit manifest of the Tooling-API
`McpServerAccess` records that
`tasks.rlm_activate_mcp_servers.ActivateMcpServers` upserts (create / reactivate
/ no-op) via `POST|PATCH /services/data/vXX/tooling/sobjects/McpServerAccess`.

`McpServerAccess` is **Tooling-API only** — it cannot be deployed via the
Metadata API — which is why activation lives here as data rather than in
`unpackaged/post_mcp` (that bundle deploys the `McpServerDefinition` itself; see
`unpackaged/post_mcp/README.md`). The two-part lifecycle is documented in
`docs/features/mcp-servers.md` and `.cursor/skills/mcp-server/SKILL.md`.

## Files

- `platform_servers.json`
  - Platform SObject MCP servers (`platform_sobject_all`,
    `platform_sobject_deletes`). These are built into the org and have **no**
    `McpServerDefinition`, so they cannot be discovered — they must be declared
    here. Each row has `"kind": "platform"` and **no** `McpServerId`
    (resolved/stored as `null`).
- `custom_servers.json`
  - Custom servers shipped by this repo and deployed via `deploy_post_mcp`
    (e.g. `RLMQuotingMCP`). Each row has `"kind": "custom"`; the task resolves
    its `McpServerId` at runtime by querying `McpServerDefinition` for the given
    `DeveloperName` (never hardcoded across orgs). A custom row whose definition
    is not deployed makes the task **hard-fail before any write**.

The task reads **both** files by default. To enable an additional server, add a
row to the appropriate file (custom servers also need their
`McpServerDefinition` added to `unpackaged/post_mcp`). No code change is
required.

## Activation is manifest-only — no auto-discovery (important)

`activate_mcp_servers` activates **only** the servers declared in this folder.
**Deploying an `McpServerDefinition` does NOT activate it** — a server is enabled
only when it has an explicit row here. There is intentionally **no
auto-discovery** of deployed definitions.

Why: activation is a deliberate, reviewable, source-controlled decision. A
server should go live because someone added it to this manifest (and that diff
was reviewed), not as an implicit side effect of a metadata deploy. This keeps
the enabled set auditable and prevents a half-built or experimental server from
being switched on just because its definition landed in the org.

**So, to enable a server you must do both:**

1. Deploy its `McpServerDefinition` (custom servers → add to
   `unpackaged/post_mcp`; platform servers are already in the org).
2. Add a row for it here, in `custom_servers.json` (custom) or
   `platform_servers.json` (platform).

A custom row whose `McpServerDefinition` is **not** deployed makes the task
**hard-fail before any write** (so a typo or missing deploy is caught loudly,
never silently skipped). Conversely, a deployed-but-undeclared server is simply
left inactive.

## JSON Contract

Each file must be a JSON **array** of `McpServerAccess` objects. Recognized keys:

| Key | Required | Notes |
| --- | --- | --- |
| `kind` | yes | `"platform"` or `"custom"`. Drives `McpServerId` resolution (platform → `null`; custom → looked up by `DeveloperName`). |
| `DeveloperName` | yes | The server's developer name. For custom servers, must match a deployed `McpServerDefinition.DeveloperName`. Custom server names are alphanumeric, start with a letter, 2–40 chars — **no underscores** (e.g. `RLMQuotingMCP`). |
| `MasterLabel` | yes | Friendly label written when the task **creates** the access record. Spaces allowed. Not overwritten on existing records (admin-managed values win). |
| `Language` | no | Defaults to `en_US`. |
| `Active` | no | Defaults to `true`. The task only ever **enforces `Active = true`** (activate / reactivate); it never sets `false`. To deactivate, use Setup or a manual Tooling PATCH. |

Notes:

- `McpServerId` is **never** put in these files for either kind — platform rows
  resolve to `null`, custom rows are resolved at runtime. This keeps the
  manifest org-portable.
- Activation is **idempotent**: existing-and-active rows are no-ops; existing
  records keep their `MasterLabel`/`McpServerId` (only `Active=true` is
  enforced, divergence is logged).
- A row may set `"Active": false` to **register** a server in the manifest
  without enabling it — the task records the declaration but never tears down an
  already-active record (it only ever moves toward active; to deactivate, use
  Setup or a manual Tooling PATCH).
- `manifest_dir` task option overrides this folder if you need a different
  payload set per org/flow (default `datasets/tooling/McpServerAccess`).
