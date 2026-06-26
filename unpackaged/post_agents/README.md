# Agentforce Agents

This bundle deploys two Agentforce **Employee Agents** plus their settings and permission sets. Both agents are **out-of-the-box (OOTB) agent templates** that ship with Salesforce Release 262 and are now authored as Builder Script (`.agent`) bundles. No managed package is required.

## What's in the bundle

| Asset | Path | Notes |
|---|---|---|
| Settings | `settings/` | `AgentPlatform`, `EinsteinCopilot`, `EinsteinGpt`. Deployed first by `deploy_agents_settings`. |
| Revenue Quote Management agent | `aiAuthoringBundles/Revenue_Quote_Management/` | Builder Script `.agent` authoring bundle. The org compiles this into `Bot` + `BotVersion` + `GenAiPlannerBundle` at publish time. |
| Billing Employee Assistance agent | `aiAuthoringBundles/Billing_Employee_Assistance/` | Builder Script `.agent` authoring bundle (upgraded from the legacy decomposed format). |
| Permission sets | `permissionsets/RLM_QuotingAgent.permissionset-meta.xml`, `permissionsets/RLM_BillingEmployeeAgent.permissionset-meta.xml` | Each contains `<agentAccesses>` so Lightning users can see the agent. |

## OOTB agent templates (no managed package)

Both bots reference platform-provided templates via `agent_type: "AgentforceEmployeeAgent"` in the `.agent` config block (template lineages `quotingAI__QuotingEmployeeAgent` for Quote and `billing_agents__BillingEmployeeAgent` for Billing).

The `quotingAI__` and `billing_agents__` prefixes look like managed-package namespaces but they're **platform-provided OOTB templates** introduced in Release 262 — they're available in scratch orgs without installing a package. Verified against `jun25_1` (scratch on Release 262): no `quotingAI`/`billing_agents` entries in `PackageLicense` or `ApexClass.NamespacePrefix`, yet the deploy succeeds and the agents run.

Planner-bundle action IDs are not committed for either agent — the platform mints them fresh from the `.agent` source on each `sf agent publish`.

## Deploy / activate / assign

Driven by the `prepare_agents` flow (`cumulusci.yml`):

1. `assign_permission_set_groups` → `CopilotSalesforceUserPSG`, `CopilotSalesforceAdminPSG`
2. `deploy_agents_settings` → `unpackaged/post_agents/settings`
3. `deploy_agents` → the whole `unpackaged/post_agents` tree
4. `publish_agents` → runs `sf agent publish authoring-bundle` for each `aiAuthoringBundles/<Name>/` so the platform compiles the bundle into a runnable `BotVersion`
5. `activate_agents` → runs `sf agent activate` for each agent discovered under `aiAuthoringBundles/`
6. `assign_permission_sets` → `RLM_QuotingAgent`, `RLM_BillingEmployeeAgent` (the `ps_aea` anchor)

Every step is gated on the `agents` feature flag (`project_config.project__custom__agents`, default `false` in `cumulusci.yml`). Standalone task invocation (e.g. `cci task run deploy_agents --org <alias>`) bypasses the gate.

## Why post-deploy publish + activation are required

Two separate platform gaps are bridged by this flow:

1. **Authoring bundles compile at publish time, not deploy time.** Deploying an `AiAuthoringBundle` puts the `.agent` source in the org but does not produce a `BotVersion`. `sf agent publish authoring-bundle` is the platform compile step. `publish_agents` (`tasks/rlm_publish_agents.py`) iterates every directory under `aiAuthoringBundles/` and runs the publish command for each.
2. **`BotVersion.Status` is not part of deployable metadata and is not DML-writable.** Fresh deploys (and freshly-published bundles) always land Inactive. `activate_agents` (`tasks/rlm_activate_agents.py`) iterates every agent name under `aiAuthoringBundles/` and runs `sf agent activate --api-name <Name> --json`, which wraps the Connect REST endpoint `POST /connect/bot-versions/{botVersionId}/activation`.

Both tasks discover agents from disk, so adding a new agent's directory under `aiAuthoringBundles/` automatically enrolls it in publish + activate. No edits to the task code are needed.

## Adding a new agent

1. Author or retrieve the `.agent` source — for a retrieve from an existing org:
   ```
   sf project retrieve start \
     --metadata "AiAuthoringBundle:<Name>" \
     --target-org <alias> \
     --api-version 67.0
   ```
   `AiAuthoringBundle` requires **API v67.0+**.
2. Validate locally before committing:
   ```
   sf agent validate authoring-bundle --api-name <Name> -o <alias> --json
   ```
   Common gotchas (see `sf-ai-agentscript` skill):
   - Every `linked` variable needs a `source:` line — if you don't have one, the variable belongs as `mutable` instead, or should be removed.
   - For `AgentforceEmployeeAgent` agents, `@MessagingSession.*` / `@MessagingEndUser.*` / `@VoiceCall.*` sources are Service-Agent-only contexts; they pass validation but are never populated at runtime, so they should be removed unless the agent will be reused on a messaging channel.
   - `complex_data_type_name` warnings on primitive types (`string`, `boolean`, `list[string]`) are informational and do not block publish.
3. Drop the bundle into `unpackaged/post_agents/aiAuthoringBundles/<Name>/`.
4. Add a permission set with `<agentAccesses>` and wire it into the `ps_aea` anchor in `cumulusci.yml`.
5. `publish_agents` and `activate_agents` auto-discover from disk; no code changes needed.
