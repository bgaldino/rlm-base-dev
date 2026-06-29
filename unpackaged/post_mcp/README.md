# `unpackaged/post_mcp` — Salesforce Hosted MCP bundle

Metadata deployed by **`deploy_post_mcp`** and activated by
**`activate_mcp_servers`**, both run from the **`prepare_mcp`** flow (a
conditional sub-flow of `prepare_ai` inside `prepare_rlm_org`). Gated by the
opt-in **`mcp`** feature flag. Full writeup: `docs/features/mcp-servers.md`;
admin/lifecycle: `docs/references/mcp-server-admin.md`.

```
post_mcp/
├── mcpServerDefinitions/
│   └── RLMQuotingMCP.mcpServerDefinition-meta.xml       # custom server (9 tools)
├── flows/
│   └── RLM_Create_Opportunity_Agentforce.flow-meta.xml # backing flow for 1 tool
├── externalClientApps/
│   └── RLMQuotingMcpClient.eca-meta.xml                 # client ECA (OAuth + PKCE)
├── extlClntAppOauthSettings/
│   └── RLMQuotingMcpClient.ecaOauth-meta.xml            #   scopes: mcp_api + refresh_token
├── extlClntAppGlobalOauthSets/
│   └── RLMQuotingMcpClient.ecaGlblOauth-meta.xml        #   PKCE, multi-client callbacks
└── extlClntAppOauthPolicies/
    └── RLMQuotingMcpClient.ecaOauthPlcy-meta.xml        #   refresh-token TTL, permitted users
```

The four ECA components are a **fully org-agnostic** External Client App that lets
an MCP client authenticate (OAuth Auth-Code + PKCE). They carry **no** `orgScopedExternalApp`,
`consumerKey`, or `oauthLink` — the org supplies/auto-resolves all three on deploy —
so the bundle deploys to any org with zero edits. Connecting a client afterward is
the **End-to-End Setup Runbook** in `docs/references/mcp-server-admin.md`. If you
re-retrieve the ECA to update it, strip those three fields again before committing.

## Source-format bundle (no `package.xml`)

This is a **source-format** bundle, like every other `unpackaged/post_*/`
folder. CumulusCI's `Deploy` task picks the format by a single test
(`cumulusci/core/sfdx.py` → `get_source_format_for_path`): **`package.xml`
present → MDAPI (deploy as-is); absent → SFDX (run `sf project convert source`
first).** With no `package.xml` here, CCI converts to MDAPI at deploy time and
synthesizes the manifest automatically.

For that conversion to pick up the files, they **must** use source-format names
with the `-meta.xml` suffix — **all** of them: `*.mcpServerDefinition-meta.xml`,
`flows/*.flow-meta.xml`, **and** the four ECA files
(`*.eca-meta.xml`, `*.ecaOauth-meta.xml`, `*.ecaGlblOauth-meta.xml`,
`*.ecaOauthPlcy-meta.xml`). `McpServerDefinition` is in the SF CLI source-tracking
registry (`directoryName: mcpServerDefinitions`, `suffix: mcpServerDefinition`),
so `sf project convert source` preserves the files and emits the correct
`package.xml`.

> ⚠ Renaming any of these to bare mdapi names (e.g. `*.mcpServerDefinition` or
> `*.eca`, no `-meta.xml`) **without** adding a `package.xml` makes source
> conversion emit a "appears to be in metadata format" warning and risk skipping
> them — the deploy becomes a silent no-op for those components. Keep the
> `-meta.xml` suffix on every file. Validate with a **0-warning** dry-run:
> `sf project deploy start --source-dir unpackaged/post_mcp --target-org <org> --dry-run`.

## Naming constraint

An MCP **server name** must start with a letter, be alphanumeric only, and be
2–40 chars — **no underscores** (hence `RLMQuotingMCP`, not `RLM_QuotingMCP`).
The `<masterLabel>` (friendly display name) *may* contain spaces
(`RLM Quoting MCP`).

## Deploy ≠ activate (and how to add a server)

Deploy and activation are **decoupled**, and activation is **manifest-only**:
deploying a server's `McpServerDefinition` does **not** turn it on. A server is
activated only when it is explicitly declared in the activation manifest at
**`datasets/tooling/McpServerAccess/`** (see that folder's README). There is
intentionally **no auto-discovery** — activation is a deliberate, reviewable,
source-controlled decision, not a side effect of a deploy.

So enabling another custom server is **two** changes:

1. **Deploy the definition** — add
   `mcpServerDefinitions/<NewName>.mcpServerDefinition-meta.xml` here (respect
   the no-underscore naming rule above, and keep the `-meta.xml` suffix), plus
   any new backing flow at `flows/<Flow>.flow-meta.xml`, then `deploy_post_mcp`.
   No `package.xml` to edit — source conversion picks up the new files
   automatically.
2. **Declare activation** — add a row to
   `datasets/tooling/McpServerAccess/custom_servers.json`, then
   `activate_mcp_servers`.

A custom server declared in the manifest but **not** deployed makes
`activate_mcp_servers` **hard-fail before any write**. A server deployed but
**not** declared is simply left inactive (its `McpServerId` is resolved at
runtime by `DeveloperName`; never hardcoded).

Activation is idempotent (create-if-absent, reactivate-if-disabled,
no-op-if-active) and respects manually-managed `McpServerAccess` records (only
`Active = true` is enforced; existing label/linkage left untouched). Full
contract and examples: `datasets/tooling/McpServerAccess/README.md`.
