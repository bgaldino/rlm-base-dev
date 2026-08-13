---
name: mcp-integration
description: >-
  The MCP surface on a Foundations-built org — the hosted Salesforce MCP servers, the
  custom ramp-deals-connect server and its two tool bindings, the External Client
  Application that authenticates them, and the release-gated clone invocable behind the
  CLASSIC-bound tool. Use when asked what MCP servers an org has, how to stand them up
  on a new or rebuilt org, why the clone invocable exists in two copies, why an MCP
  artifact is a Tooling API record instead of metadata, or when a server or tool is
  missing after a rebuild. Foundations owns the org-side surface; the sibling
  ramp-demo-kit owns the client tooling and the demos, reached through the cross-repo
  skill manifest.
---

# MCP Integration

Foundations builds the org **and** its MCP surface. The sibling **ramp-demo-kit** owns
what runs on a workstation — the OAuth login, the multiplex proxy, the per-demo
connector — plus the demos themselves. The dividing line is durability: anything that
must survive an org rebuild lives here as source; anything per-person or per-laptop
lives there.

Resolve the kit's clone with `resolve_repo_root(m, 'ramp_demo_kit')`; its entry point is
the root `CLAUDE.md`.

## Quick Rules

1. **`cci flow run prepare_mcp --org <alias>` stands up the whole org-side surface.**
   It is step 34 of `prepare_rlm_org`, gated on the `mcp` feature flag, which defaults
   to **off** — the flow cannot finish the job, because each person still runs their own
   browser OAuth login.
2. **Two of the three steps are not a metadata deploy.** Only `McpServerDefinition` is a
   deployable metadata type. The activations (`McpServerAccess`) and the custom server's
   tools and bindings (`McpServerToolDefinition`, `McpServerToolApiDefinition`) are
   Tooling API records, which is why `configure_mcp_servers` exists at all.
3. **`configure_mcp_servers` is idempotent and reports what it did.** Every write checks
   first and logs `already`. Use `-o operation list` to audit an org without touching it,
   `-o dry_run True` to preview, and `-o platform_servers True` to also activate
   `sobject-all` and `headless-360` — off by default, because `sobject-all` grants
   read/write across every object in the org.
4. **The clone invocable exists in two copies, on purpose.** `unpackaged/post_mcp`
   carries the 67.0 synchronous copy; `unpackaged/post_mcp_264` overlays the 68.0
   async-capable one on orgs that can compile it. See *Release Skew* below before
   editing either.
5. **Ordering is load-bearing.** The Apex must exist before the custom server, because
   the `CLASSIC` binding references the invocable by action path. `prepare_mcp` runs
   deploy → overlay → configure for that reason.
6. **Auth is per person, not per package.** PKCE against the ECA, with a public consumer
   key the tooling reads from the org — so there is no secret to distribute and nothing
   to commit.
7. **A rebuilt org keeps only what is in source.** Activations are org records. A server
   switched on by hand in Setup is gone at the next rebuild unless it is in
   `CORE_HOSTED` or `PLATFORM_HOSTED` in `tasks/rlm_mcp.py`.

## DO NOT

1. **DO NOT** reference `contextId`, `trackerId`, `trackerUrl`, or `isAsync` in
   `unpackaged/post_mcp/classes/RampCloneSalesTransaction.cls`. Those members do not
   exist on 262 / v67.0, so adding one breaks the deploy for every 262 org.
   `tests/test_mcp_overlay_parity.py` fails if you do.
2. **DO NOT** deploy `unpackaged/post_mcp_264` with a plain
   `cumulusci.tasks.salesforce.Deploy`. It must go through
   `tasks.rlm_mcp.DeployMcpOverlay`, which skips orgs below v68.0 instead of hard-failing
   the flow on them.
3. **DO NOT** treat `cloneSalesTransaction` as asynchronous on a 262 org. There is no
   tracker handle to poll there — the clone is complete when the tool returns. On 264 it
   may return a tracker id, and then it is *not* complete; `isAsync` says which.
4. **DO NOT** hand-activate a server in Setup and consider it done. Add it to
   `CORE_HOSTED` (or `PLATFORM_HOSTED`) in the same change, or it dies at the next
   rebuild. `-o operation list` flags anything unmanaged.
5. **DO NOT** give a hosted server's namespaced `DeveloperName` form to a **custom**
   server's `McpServerAccess`. For a custom server, `McpServerAccess.DeveloperName` must
   **equal** the definition's `DeveloperName`; the namespaced form fails
   `FIELD_INTEGRITY_EXCEPTION`.
6. **DO NOT** commit a consumer key, consumer secret, or token. The ECA's key is read
   from the org at run time by design.
7. **DO NOT** resurrect `unpackaged/post_ramp_builder/`. The custom Ramp Builder was
   removed in favor of the platform-native `CreateRampSchedule`; leftover empty
   directories are deletion residue, not a home for new work.

## The Surface

| Layer | Artifact | Where it lives | Applied by |
|---|---|---|---|
| Client identity | `ExternalClientApplication ClaudeMcpClientRC` + 4 OAuth/policy components | `unpackaged/post_mcp/` | `deploy_post_mcp` |
| Custom tool backing | `ApexClass RampCloneSalesTransaction` (+ test), synchronous, 67.0 | `unpackaged/post_mcp/classes/` | `deploy_post_mcp` |
| Async variant | same class at 68.0, with the tracker contract | `unpackaged/post_mcp_264/classes/` | `deploy_post_mcp_264` (v68.0+ only) |
| Hosted servers | `McpServerAccess` activations | `tasks/rlm_mcp.py` → `CORE_HOSTED`, `PLATFORM_HOSTED` | `configure_mcp_servers` |
| Custom server | `McpServerDefinition rampdealsconnect` + 2 tools + 2 API bindings + its access | `tasks/rlm_mcp.py` → `CUSTOM_TOOLS` | `configure_mcp_servers` |
| Per-person auth | PKCE login | ramp-demo-kit `tools/ramp_auth.py` | one browser click |
| Connector | multiplex proxy + per-folder `.mcp.json` | ramp-demo-kit `tools/`, `setup/link_demo.py` | local |

The custom server's two tools demonstrate both binding styles: `placeSalesTransaction`
binds `CONNECT` → `industries-revenue`, and `cloneSalesTransaction` binds `CLASSIC` →
`/actions/custom/apex/RampCloneSalesTransaction`. A tool needs `@McpIntegration` to be
bound as `CONNECT`; clone does not carry it, which is why it goes through an invocable.

## Release Skew — Why the Clone Invocable Is Duplicated

Verified by compile probe against a 262 org:

| Member | 262 / v67.0 | 264 / v68.0 |
|---|---|---|
| `cloneSalesTransaction()` call | present | present |
| `output.success`, `salesTransactionId`, `requestId`, `errors` | present | present |
| `input.contextId` — requests async | **absent** | present |
| `output.trackerId`, `output.trackerUrl` | **absent** | present |

There is no single source file that serves both. ConnectApi **input** representations
reject `JSON.serialize` and `JSON.deserialize` outright — *"Only output types from
ConnectApi support serialization"* — so a 67.0-compiled class cannot set `contextId`
reflectively either. Hence two copies and a version gate.

The 262 copy omits the tracker fields rather than exposing them as always-null, because
a null `trackerId` invites a caller — especially an LLM driving this as an MCP tool — to
poll a handle that will never exist.

`tests/test_mcp_overlay_parity.py` pins the invariants that keep the copies from
drifting: same class name, opposite async-member sets, the api versions the gate
assumes, and base-before-overlay ordering in `prepare_mcp`. **When Foundations' baseline
reaches 264, retire all of it together** — promote the overlay copy into
`unpackaged/post_mcp/`, then delete the overlay directory, `DeployMcpOverlay`, the
`deploy_post_mcp_264` task, its flow step, and that parity test.

## Standing It Up

```bash
# Org side, from this repo. Needs the mcp feature flag on for the flow path:
cci task run deploy_post_mcp --org <cci-alias>
cci task run deploy_post_mcp_264 --org <cci-alias>          # skips silently below v68.0
cci task run configure_mcp_servers --org <cci-alias>
cci task run configure_mcp_servers --org <cci-alias> -o platform_servers True

# Or all three, gated on the flag:
cci flow run prepare_mcp --org <cci-alias>

# Client side, from the ramp-demo-kit clone:
eval "$(python3 tools/ramp_org.py env <sf-alias>)"
python3 tools/ramp_auth.py login
python3 tools/mcp_multiplex_proxy.py --prime
```

Neither side seeds demo data — that needs judgement about the existing catalog, since a
QuantumBit-loaded org already has most of it. See the kit's
`reference/RUNBOOK-new-org.md`.

## Validation Checks

```bash
# Audit an org without changing it. Flags servers activated by hand.
cci task run configure_mcp_servers --org <cci-alias> -o operation list

# Keep the two clone copies honest (offline, no org):
python tests/test_mcp_overlay_parity.py

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

- `unpackaged/post_mcp` **deployed and its Apex tests executed** on a 262 / v67.0 scratch
  org: 2 components, `RampCloneSalesTransactionTest` 4/4 passing. The 264 overlay
  validated on a v68.0 org; the version gate skips and proceeds respectively.
- `configure_mcp_servers` verified live: `list` and `dry_run` on a v68 org already
  carrying the surface (all `already`), and `dry_run` on a fresh 262 org (11 planned).
- **The overlay's own tests have not been executed** — that needs a v68.0 org, and the
  only one available is a trial (TSO), where `RunSpecifiedTests` on a *check-only* deploy
  reports `numTestsRun: 0`. The overlay differs from the base copy only in the async
  members; the parity test pins that. Run them on a 264 scratch org when the dev hub
  offers one.

A scratch org needs `RevenueManagementSettings.enableCoreCPQ` and
`enableTransactionCloning` **on** before either copy will compile —
`ConnectApi.CloneSalesTransactionConnect` is not visible otherwise, and the failure reads
as `Type is not visible`, not as a missing feature. `prepare_rlm_org` sets both at step 1,
so this only bites when deploying the bundle to a bare org. It is not a permission
problem: assigning `RevenueLifecycleManagementUserPsl` does not fix it.

## Access Note

`ramp-demo-kit` is in the `salesforce-internal` GitHub EMU org with OAuth app access
restrictions. The git-EMU MCP connector gets `403`, and `gh` returns `404` unless it is
on the EMU account (`gh auth switch --hostname github.com --user <emu-account>`). A local
clone sidesteps both, which is what the manifest's `local_path_hints` prefer.

## Related

- `.claude/skill-manifest.yml` → `ramp_demo_kit` — the kit's declared tooling and demos
- `.cursor/skills/pmos-integration/SKILL.md` — the same cross-repo manifest mechanism
- `scripts/ai/skill_manifest.py --check` — confirms the kit's clone resolves
- `.cursor/skills/cci-orchestration/tasks-reference.md` — generated entries for the three MCP tasks
