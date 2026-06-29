# `unpackaged/post_mcp` — Salesforce Hosted MCP bundle

Metadata deployed by **`deploy_post_mcp`** and activated by
**`activate_mcp_servers`**, both run from the **`prepare_mcp`** flow (a
conditional sub-flow of `prepare_ai` inside `prepare_rlm_org`). Gated by the
opt-in **`mcp`** feature flag. Full writeup: `docs/features/mcp-servers.md`;
lifecycle/skill: `.cursor/skills/mcp-server/SKILL.md`.

```
post_mcp/
├── mcpServerDefinitions/
│   └── RLMQuotingMCP.mcpServerDefinition-meta.xml       # custom server (9 tools)
└── flows/
    └── RLM_Create_Opportunity_Agentforce.flow-meta.xml # backing flow for 1 tool
```

## Source-format bundle (no `package.xml`)

This is a **source-format** bundle, like every other `unpackaged/post_*/`
folder. CumulusCI's `Deploy` task picks the format by a single test
(`cumulusci/core/sfdx.py` → `get_source_format_for_path`): **`package.xml`
present → MDAPI (deploy as-is); absent → SFDX (run `sf project convert source`
first).** With no `package.xml` here, CCI converts to MDAPI at deploy time and
synthesizes the manifest automatically.

For that conversion to pick up the files, they **must** use source-format names
with the `-meta.xml` suffix (`*.mcpServerDefinition-meta.xml`,
`flows/*.flow-meta.xml`). `McpServerDefinition` **is** in the SF CLI
source-tracking registry as of CLI 2.140.6 (`directoryName: mcpServerDefinitions`,
`suffix: mcpServerDefinition`), so `sf project convert source` preserves both
files and emits the correct `package.xml`. Verified live: a source-format
`deploy_post_mcp` lands the `RLMQuotingMCP` definition in the org (non-empty
4 KB payload, `McpServerDefinition` Id `1g1…`).

> ⚠ If you ever rename these to bare mdapi names (`*.mcpServerDefinition`, no
> `-meta.xml`) **without** adding a `package.xml`, source conversion will skip
> them and the deploy becomes a silent no-op. Keep the `-meta.xml` suffix.

## Naming constraint (learned live)

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
