---
name: mcp-integration
description: >-
  The MCP surface on a Foundations-built org and the client tooling that talks to it —
  the hosted Salesforce MCP servers, the custom rlm-sales-transactions server and its two
  tool bindings, the External Client Application (RLM_McpClient) that authenticates them,
  the clone invocable behind the CLASSIC-bound tool, gateway endpoint URLs, and the
  scripts/mcp/ login, proxy and connector-config tools. Use when asked what MCP servers
  an org has, how to stand them up or connect a client, why a gateway call returns 401,
  why the clone invocable needs a 264 org, why an MCP artifact is a Tooling API record
  instead of metadata, or when a server or tool is missing after a rebuild.
---

# MCP Integration

Foundations builds the org **and** owns its whole MCP surface: the org-side artifacts
(`unpackaged/post_mcp`, `unpackaged/post_mcp_custom`, `tasks/rlm_mcp.py`, the
`prepare_mcp` flow) and the client
tooling in `scripts/mcp/` (`mcp_org.py` org/env resolution, `mcp_auth.py` PKCE login,
`mcp_multiplex_proxy.py`, `write_connector_config.py`). See `scripts/mcp/README.md`.
Gateway-endpoint research credit: Sam Check (`feature/mcp-servers`).

## Quick Rules

1. **`cci flow run prepare_mcp --org <alias>` stands up the whole org-side surface.**
   It is step 35 of `prepare_rlm_org` (36 steps; `stamp_git_commit` follows),
   gated on the `mcp` feature flag, which defaults to **off** — the flow cannot finish the
   job, because each person still runs their own browser OAuth login.
2. **`prepare_mcp` is metadata deploys, a permission set assignment and one Tooling API
   step.** `deploy_post_mcp` deploys the ECA; `deploy_post_mcp_custom` deploys the clone
   invocable and its permission set (`RLM_McpSalesTransactions`); `assign_permission_sets`
   grants it to the running user; `configure_mcp_servers` is the non-metadata step. Of the MCP server record types, only `McpServerDefinition`
   is deployable metadata. The activations (`McpServerAccess`) and the custom server's
   tools and bindings (`McpServerToolDefinition`, `McpServerToolApiDefinition`) are
   Tooling API records, which is why `configure_mcp_servers` exists at all.
3. **`configure_mcp_servers` is idempotent and reports what it did.** Every write checks
   first and logs `already`. Use `-o operation list` to audit an org without touching it,
   `-o dry_run True` to preview, and `-o platform_servers True` to also activate
   `sobject-all` and `headless-360` — off by default, because `sobject-all` grants
   read/write across every object in the org.
4. **The clone invocable is one class at API 68.0.** `unpackaged/post_mcp_custom` carries the
   async-capable copy (tracker contract); the baseline is release 264, so there is no
   version gate or overlay. It does not compile on an older org. See *Release Skew*
   below for the pre-264 history.
5. **`configure_mcp_servers` resolves prerequisites before writing.** A missing clone
   invocable fails the task with nothing modified, and an `McpServerAccess` linked to the
   wrong server (`McpServerId` must be null for hosted, the definition id for custom)
   fails rather than passing as `already`.
6. **Ordering is load-bearing.** The Apex must exist before the custom server, because
   the `CLASSIC` binding references the invocable by action path. `prepare_mcp` runs
   deploy → configure for that reason.
7. **Auth is per person, not per package.** PKCE against the ECA, with a public consumer
   key the tooling reads from the org — so there is no secret to distribute and nothing
   to commit. Tools run as the authenticated user, so CRUD/FLS/sharing apply. That includes
   the clone tool's Apex class access: `prepare_mcp` grants `RLM_McpSalesTransactions` to
   the running user only, so assign it to every other MCP user (see *Standing It Up*), or
   their `cloneSalesTransaction` call fails while the rest of the server works.
8. **The custom server is optional and temporary.** It exists until the hosted
   `revenue-cloud` server covers place and clone (and the surface folds into Headless 360).
   `mcp_custom_server: false` builds only the ECA and the hosted activations: steps 2–3 of
   `prepare_mcp` skip and `configure_mcp_servers` defaults to `custom_server False`. On the
   client, `RLM_MCP_CUSTOM_SERVER=0` drops the custom server, and `write_connector_config.py`
   then points the client straight at `revenue-cloud`, without the multiplex proxy. Turning
   the flag off does not delete a custom server an earlier build created.
9. **A rebuilt org keeps only what is in source.** Activations are org records. A server
   switched on by hand in Setup is gone at the next rebuild unless it is in
   `CORE_HOSTED` or `PLATFORM_HOSTED` in `tasks/rlm_mcp.py`.

## DO NOT

1. **DO NOT** reintroduce a 67.0 copy, an `unpackaged/post_mcp_264` overlay, or a
   version-gated deploy. The baseline is 264 / v68.0 and `unpackaged/post_mcp_custom` is
   the single source.
2. **DO NOT** treat `cloneSalesTransaction` as complete when it returns. It may return a
   tracker id, and then the clone is *not* complete; `isAsync` says which.
3. **DO NOT** hand-activate a server in Setup and consider it done. Add it to
   `CORE_HOSTED` (or `PLATFORM_HOSTED`) in the same change, or it dies at the next
   rebuild. `-o operation list` flags anything unmanaged.
4. **DO NOT** give a hosted server's namespaced `DeveloperName` form to a **custom**
   server's `McpServerAccess`. For a custom server, `McpServerAccess.DeveloperName` must
   **equal** the definition's `DeveloperName`; the namespaced form fails
   `FIELD_INTEGRITY_EXCEPTION`.
5. **DO NOT** commit a consumer key, consumer secret, or token. The ECA's key is read
   from the org at run time by design.
6. **DO NOT** use a classic Connected App; the MCP gateway needs an External Client
   Application.
7. **DO NOT** use the My Domain host as the MCP endpoint; the gateway is
   `api.salesforce.com`.
8. **DO NOT** commit a re-retrieved ECA without stripping `OrgId`, `consumerKey` and
   `oauthLink` first.
9. **DO NOT** treat an active `McpServerAccess` row as proof a server is served (see
   *Gateway Endpoints*).
10. **DO NOT** leave a custom-server tool without a binding. The gateway then fails the
    whole server with a 500, not just that tool (*Verification Status*).

## The Surface

| Layer | Artifact | Where it lives | Applied by |
|---|---|---|---|
| Client identity | `ExternalClientApplication RLM_McpClient` + 4 OAuth/policy components | `unpackaged/post_mcp/` | `deploy_post_mcp` |
| Custom tool backing | `ApexClass RLM_CloneSalesTransaction` (+ `RLM_CloneSalesTransactionTest`), 68.0, with the tracker contract | `unpackaged/post_mcp_custom/classes/` | `deploy_post_mcp_custom` |
| Invocable access | `RLM_McpSalesTransactions` permission set | `unpackaged/post_mcp_custom/permissionsets/` | `deploy_post_mcp_custom` |
| Hosted servers | `McpServerAccess` activations | `tasks/rlm_mcp.py` → `CORE_HOSTED`, `PLATFORM_HOSTED` | `configure_mcp_servers` |
| Custom server (optional, `mcp_custom_server`) | `McpServerDefinition RLMSalesTransactions` (label `rlm-sales-transactions`) + 2 tools + 2 API bindings + its access | `tasks/rlm_mcp.py` → `CUSTOM_TOOLS` | `configure_mcp_servers` |
| Per-person auth | PKCE login | `scripts/mcp/mcp_auth.py` | one browser click |
| Connector | multiplex proxy + connector config (direct HTTP entry, no proxy, without the custom server) | `scripts/mcp/mcp_multiplex_proxy.py`, `write_connector_config.py` | local |

The custom server's two tools demonstrate both binding styles: `placeSalesTransaction`
binds `CONNECT` → `revenue-transactionmanagement`, and `cloneSalesTransaction` binds `CLASSIC` →
`/actions/custom/apex/RLM_CloneSalesTransaction`. A tool needs `@McpIntegration` to be
bound as `CONNECT`; clone does not carry it, which is why it goes through an invocable.

## Release Skew — History of the Clone Invocable

Before the baseline reached 264 the class existed in two copies, because 262 / v67.0
lacks the async members (`input.contextId`, `output.trackerId`, `output.trackerUrl`)
and ConnectApi **input** representations reject `JSON.serialize` and
`JSON.deserialize`, so no single source compiled on both. The copies were collapsed
into the single 68.0 class, now in `unpackaged/post_mcp_custom/`; the overlay directory,
`DeployMcpOverlay`, `deploy_post_mcp_264` and the parity test are gone. The class
therefore needs a 264 org. Do not backport it to 262 by adding a second copy without
a caller who still needs one — a null `trackerId` invites a caller, especially an LLM
driving this as an MCP tool, to poll a handle that will never exist.

## Standing It Up

```bash
# Org side, from this repo. Needs the mcp feature flag on for the flow path:
cci task run deploy_post_mcp --org <cci-alias>
cci task run deploy_post_mcp_custom --org <cci-alias>      # custom server only
cci task run configure_mcp_servers --org <cci-alias>       # -o custom_server False: hosted only
cci task run configure_mcp_servers --org <cci-alias> -o platform_servers True

# Or the whole flow (deploy, assign RLM_McpSalesTransactions, configure), gated on the flag:
cci flow run prepare_mcp --org <cci-alias>

# Custom server only: the flow assigns the clone permission set to the running user. Each other MCP user:
sf org assign permset --name RLM_McpSalesTransactions --on-behalf-of <username> --target-org <sf-alias>

# Client side, from this repo:
eval "$(python3 scripts/mcp/mcp_org.py env <sf-alias>)"   # RLM_MCP_ORG / RLM_MCP_ECA / ...
python3 scripts/mcp/mcp_auth.py login
python3 scripts/mcp/mcp_multiplex_proxy.py --prime
```

Without the custom server, `export RLM_MCP_CUSTOM_SERVER=0` (before or after the `eval`;
`env` does not pin the server list) and skip the login and the proxy:
`write_connector_config.py <sf-alias>` writes a direct HTTP entry and the client logs in.

Env vars: `RLM_MCP_ORG`, `RLM_MCP_ECA`, `RLM_MCP_PROFILES`, `RLM_MCP_STATE`,
`RLM_MCP_AUTH_DIR`, `RLM_MCP_CUSTOM_SERVER`. Nothing here seeds demo data; that needs judgement about the
existing catalog, since a QuantumBit-loaded org already has most of it.

## Gateway Endpoints

Default (org-pinned), verified 2026-10-17 on a production My Domain for
`platform/headless-360`, `industries/revenue-cloud` and `custom/<name>`:

```
https://api.salesforce.com/platform/mcp/v1/d/<My Domain prefix>/<namespace>/<server>
# custom server: .../d/<prefix>/custom/RLMSalesTransactions
```

- Legacy forms: `/v1/<ns>/<server>` and `/v1/sandbox/<ns>/<server>`.
- Enhanced domains add an org-type label (sandbox, scratch, develop, demo,
  trailblaze, ...) that is **not** part of the prefix. Scratch orgs use either
  `.scratch.` or `.sandbox.`.
- Non-production types fall back to the legacy base (sandbox/scratch to `/sandbox`)
  because pinned routing is unverified there. `mcp_org.gateway_bases` implements this;
  `SF_MCP_BASES` overrides it, but only while `SF_INSTANCE` names the same org, so an
  override eval'd for one org does not follow the shell to another (`SF_CSEC` is scoped
  the same way). Re-run `mcp_org.py env` after changing orgs.
- A Salesforce CLI token gets **401**; an ECA token with the `mcp_api` scope is required.
- A Tooling `McpServerAccess` row with `Active=true` does **not** mean the server is
  served. Some servers need org permissions (for example RevMCP, for `revenue-cloud`).
  Verify with an MCP `initialize` plus `tools/list`.

## ECA Settings and Client Connections

ECA settings that matter: PKCE required; consumer secret optional; JWT-based access
tokens for named users **on**; client credentials, auth-code-and-credentials, device,
JWT bearer and token exchange **off**; refresh token rotation on. `client_credentials`
in the scripts is explicit opt-in (`SF_AUTH_MODE=client_credentials`) and needs that
flow enabled on the ECA.

| Client | Callback / how |
|---|---|
| Claude Code | `claude mcp add --transport http --client-id <consumer key> --callback-port <port> <name> <url>`; callback `http://localhost:<port>/callback` |
| Claude Desktop / claude.ai | `https://claude.ai/api/mcp/auth_callback` |
| Cursor | `cursor://anysphere.cursor-mcp/oauth/callback` |
| MCP Inspector | `http://localhost:6274/oauth/callback/debug` |

The shipped ECA registers only the localhost `/callback`, `localhost:1717` and claude.ai
callbacks. Add others only for clients actually used.

## Validation Checks

```bash
# Audit an org without changing it. Flags servers activated by hand.
cci task run configure_mcp_servers --org <cci-alias> -o operation list

# Raw org state
sf data query -q "SELECT DeveloperName, MasterLabel, Active FROM McpServerAccess" \
  --target-org <sf-alias> --use-tooling-api
sf data query -q "SELECT ToolName, McpServerId FROM McpServerToolDefinition" \
  --target-org <sf-alias> --use-tooling-api

# ECA OAuth scopes — mcp_api and refresh_token are the ones that matter
sf data query -q "SELECT DeveloperName, OauthScopesMCP_API, OauthScopesREFRESH_TOKEN \
  FROM ExtlClntAppOauthSettings" --target-org <sf-alias>
```

`configure_mcp_servers` fails fast with a legible message when the org has no
`McpServerDefinition` entity at all, which means it lacks the MCP feature.

## Verification Status

**`RLM_CloneSalesTransaction` passes its tests, 6/6, on storm-LATEST (264, 2026-10-17).**
`RunSpecifiedTests` on the deploy ran 0 tests there, so they were run separately with
`sf apex run test`.

- `configure_mcp_servers` on storm-LATEST created the `RLMSalesTransactions` server, both
  tools, both bindings and the access row, and the gateway's `tools/list` on
  `.../d/<prefix>/custom/RLMSalesTransactions` returned both tools. `tools/call` on
  `placeSalesTransaction` was not run (it writes a transaction).
- **A CONNECT identifier is the API's `<api-domain>-<api-sub-domain>`, lowercased**
  (core `ConnectMcpOasSpecProvider`), and only operations whose OpenAPI `x-sfdc`
  block declares an MCP integration are listed. 264 re-catalogued place from
  `industries-revenue` to Revenue/TransactionManagement, so the binding is
  `revenue-transactionmanagement`. The old identifier now fails with
  `No "industries-revenue" identifier found for source "CONNECT"` — RevMCP is not the
  cause (it gates the hosted `revenue-cloud` server, not this lookup). A wrong
  operation on a valid identifier fails differently, and lists the valid operations:
  `No operation "<op>" found for identifier "<id>" ... Valid operations ... [...]`.
  Use that to discover operations, as with `revenue-price` and
  `revenue-productcatalogmanagement`.
- **A tool with no binding makes the gateway answer 500 for the whole server**
  ("An error occurred while retrieving server ..."). For that reason the task deletes
  a tool whose binding it cannot create. `placeSalesTransaction` is the reason the
  server exists: the hosted `revenue-cloud` server exposes only a limited place
  operation, and core's `PlaceSalesTransaction` carries the MCP annotation that makes
  a CONNECT binding possible.
- **An identifier the org does not resolve is a warning, not a failure.** The task
  removes that tool, skips any other tool bound to the same identifier, and still
  serves the rest of the server, so `prepare_rlm_org` with `mcp` on is not stopped at
  step 35 by a catalog it cannot change. Any other binding failure still fails the
  task. Re-run it once the org resolves the identifier; it creates only what is missing.
- **An org bound under `industries-revenue` by an earlier run is rebound, not failed.**
  `LEGACY_BINDINGS` in `tasks/rlm_mcp.py` lists bindings that no longer resolve; the
  task deletes such a binding and creates the current one (`ToolId` is unique, so it
  cannot add a second). A binding to anything else not expected still fails the task.
- **Direct mode (custom server off) is not verified live.** Only the shape of the
  `.mcp.json` HTTP entry is tested; Claude Code's own OAuth (metadata discovery, the
  `mcp_api` scope, a public client) against the gateway has not been run. The verified
  client path is the proxy, with the custom server on.
- Pre-264 orgs: the `_preflight_custom` check refuses before any write, `dry_run`
  included, because the 68.0 class cannot exist there. Pass `-o custom_server False`
  to configure only the hosted servers.

The class does not compile until `RevenueManagementSettings.enableCoreCPQ` and
`enableTransactionCloning` are **on** — `ConnectApi.CloneSalesTransactionConnect` is
invisible otherwise, and it fails as `Type is not visible`, which reads like a permission
problem and is not one (`RevenueLifecycleManagementUserPsl` does not fix it).
`prepare_rlm_org` sets both through `unpackaged/pre/1_settings/RevenueManagement`
(deployed by `prepare_core`, step 1) and the scratch definitions under `orgs/`, so this
only bites a bare org. On a **264** org,
note that a scratch create from `config/project-scratch-def.json` currently leaves
`RevenueManagementSettings` entirely unapplied — see *Scratch Orgs on a 264 Dev Hub*.

## Scratch Orgs on a 264 Dev Hub

`sf org create scratch` against a 264 dev hub reports
`status: 68, code: ProblemDeployingSettings` and this error:

```
[Error] RevenueManagement : Error parsing file: Element {}enableScaleAttributes
        invalid at this location in type DeclarativeMetadataForSettings
```

The org is still created and **the shell exit code is 0**, so a harness that gates on the
exit code alone treats it as good. The failure is per settings file, not global —
`Order`, `Quote`, and `IndustriesPricing` all applied on the org used here — but the whole
`RevenueManagementSettings` block is dropped, which is what silently left `enableCoreCPQ`
false and produced the `Type is not visible` diagnosis above.

`enableScaleAttributes` is declared in `config/project-scratch-def.json`, 14 files under
`orgs/`, and `unpackaged/pre/1_settings/RevenueManagement.settings-meta.xml`. Deploying
that last file to a 264 org fails with the same parse error, so **build step 1 is exposed
too** — `cleanup_settings_for_dev` does not strip this field. A 262-built org such as
`laulima26` is unaffected and does not carry the field in its retrieved settings at all,
consistent with 264 having dropped it. This is a 264-cutover item, not an MCP one; it is
recorded here because it is what the MCP Apex failure turned out to be.

## Related

- `.cursor/skills/pmos-integration/SKILL.md` — the cross-repo manifest mechanism
- `scripts/mcp/README.md` — client tooling reference
- `.cursor/skills/cci-orchestration/tasks-reference.md` — generated entries for the three MCP tasks
