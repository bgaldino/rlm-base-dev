# Salesforce Hosted MCP Servers — Feature Documentation

> **Target release:** API v67.0 (Summer '26 / Release 262)
> **Deployment path:** `unpackaged/post_mcp`
> **Feature flag:** `mcp` (default `false` — opt-in)
> **Skill:** `.cursor/skills/mcp-server/SKILL.md`

---

## Overview

Salesforce Hosted MCP (Model Context Protocol) servers expose org capabilities —
Flows, Apex, SObjects — as tools that external AI agents can invoke over MCP. This
feature wires two things into the RLM build:

1. A **custom MCP server**, `RLMQuotingMCP`, that surfaces the Revenue Cloud quoting
   actions (create/amend/renew quotes, manage quote lines, apply discounts) plus an
   opportunity-creation flow as MCP tools.
2. **Activation** of that custom server plus the two platform SObject MCP servers
   (`platform_sobject_all`, `platform_sobject_deletes`).

It is gated by the opt-in `mcp` feature flag and runs as the `prepare_mcp` flow,
which `prepare_rlm_org` reaches via the shared `prepare_ai` flow at step 22
(`prepare_ai` → `prepare_agents` then `prepare_mcp`, each behind its own flag).

The org-level feature `SalesforceHostedMCP` is already enabled in every scratch/org
definition (`config/project-scratch-def.json`, `orgs/*.json`), so no additional
org-feature gate is required.

---

## The deploy-vs-activate split (important)

MCP servers have a **two-part lifecycle**, and the two halves use different APIs:

| Concern | Object | API | In this repo |
|---------|--------|-----|--------------|
| Server **definition** (+ its tools) | `McpServerDefinition` | Metadata API (deployable) | `deploy_post_mcp` → `unpackaged/post_mcp` |
| Server **activation** (on/off) | `McpServerAccess` | **Tooling API only** (NOT deployable) | `activate_mcp_servers` task |

A deployed `McpServerDefinition` is **Inactive** until an `McpServerAccess` record
exists with `Active = true`. That activation record cannot be deployed via the
Metadata API — it must be created/updated through the Tooling API, which is what the
`activate_mcp_servers` task does.

### Source-format bundle

`unpackaged/post_mcp` is a **source-format** bundle, like every other
`deploy_post_<x>` folder — no `package.xml`. `McpServerDefinition` is in the SF
CLI source-tracking registry (as of CLI 2.140.6:
`directoryName: mcpServerDefinitions`, `suffix: mcpServerDefinition`), so CCI's
`Deploy` task detects the source format, runs `sf project convert source` (which
preserves both files and synthesizes the manifest), and deploys via the Metadata
API. The files must keep the source-format `-meta.xml` suffix for conversion to
pick them up.

```
unpackaged/post_mcp/
├── mcpServerDefinitions/
│   └── RLMQuotingMCP.mcpServerDefinition-meta.xml          # the custom server (9 tools)
└── flows/
    └── RLM_Create_Opportunity_Agentforce.flow-meta.xml    # backing flow for 1 tool
```

> **Naming constraint:** an MCP server name must start with a letter, be alphanumeric
> only, and be 2–40 characters. Underscores are rejected — hence `RLMQuotingMCP`, not
> `RLM_QuotingMCP`. The `<masterLabel>` (friendly display name) may contain spaces.

---

## Tools

`RLMQuotingMCP` exposes 9 Flow-Action–backed tools (`apiSource = API_CATALOG`):

| Tool (operation) | Backing flow source |
|------------------|---------------------|
| `quotingAI__createInitialQuoteOnOpp` | Managed quoting package |
| `quotingAI__addQuoteLineItemToQuote` | Managed quoting package |
| `quotingAI__updateQuoteLineItemDetails` | Managed quoting package |
| `quotingAI__updateQuoteDetails` | Managed quoting package |
| `quotingAI__applyDiscountToQuoteLine` | Managed quoting package |
| `quotingAI__queryQuoteLineRecords` | Managed quoting package |
| `quotingAI__createAmendmentQuote` | Managed quoting package |
| `quotingAI__createRenewalQuote` | Managed quoting package |
| `RLM_Create_Opportunity_Agentforce` | **This repo** (`unpackaged/post_mcp/flows`) |

The 8 `quotingAI__*` tools depend on the managed quoting package flows existing in
the target org. If those flows are absent the server still deploys, but those tools
won't resolve at runtime. `RLM_Create_Opportunity_Agentforce` ships in this bundle
(an active `AutoLaunchedFlow` over standard objects: Account, Pricebook2, Opportunity).

---

## Activation behavior (`activate_mcp_servers`)

The task (`tasks/rlm_activate_mcp_servers.py`) upserts `McpServerAccess` rows.
Activation is **manifest-driven**: it activates **only** the servers declared in
the source-controlled manifest at **`datasets/tooling/McpServerAccess/`** (JSON
arrays of `McpServerAccess` payloads). By default that manifest declares:

- `platform_sobject_all` (platform, `McpServerId = null`)
- `platform_sobject_deletes` (platform, `McpServerId = null`)
- `RLMQuotingMCP` (custom — its `McpServerId` resolved at runtime from the
  deployed definition)

**No auto-discovery:** deploying an `McpServerDefinition` does **not** activate
it — a server goes live only when added to the manifest (a reviewable, auditable
diff). To enable another server: deploy its definition **and** add a manifest
row. See `datasets/tooling/McpServerAccess/README.md` for the JSON contract and
the manifest-only rationale. The `manifest_dir` option can point at a different
payload folder per org/flow.

Key properties:

- **Precheck / hard-fail before any write.** All targets are resolved first; if the
  custom `McpServerDefinition` isn't deployed, the task raises immediately and writes
  nothing (no partial state).
- **Activate-if-absent, reactivate-if-disabled, no-op-if-active.** Because `mcp` is
  opt-in, running the task expresses intent to enable the set — it will reactivate a
  previously admin-disabled server.
- **Respects manually-managed records.** If an access record already exists with a
  different `MasterLabel`/`McpServerId`, those are left as-is (logged, not
  overwritten); only `Active = true` is enforced.
- **Idempotent.** A second run reports everything already active, zero changes.
- Matches `McpServerAccess` by `DeveloperName` **and** `McpServerId` (DeveloperName
  alone is not assumed unique across namespaces).

---

## Usage

```bash
# Opt in by setting the flag (cumulusci.yml: project__custom__mcp: true), then:
cci flow run prepare_mcp --org <cci_alias>

# Or the individual tasks:
cci task run deploy_post_mcp --org <cci_alias>
cci task run activate_mcp_servers --org <cci_alias>

# Verify activation (SF CLI alias / username):
sf data query --use-tooling-api \
  -q "SELECT DeveloperName, Active, McpServerId FROM McpServerAccess" \
  --target-org <sf_alias_or_username>
```

`prepare_mcp` also runs automatically inside `prepare_rlm_org` when `mcp` is enabled.
