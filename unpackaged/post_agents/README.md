# Agentforce Agents

This bundle deploys two Agentforce **Employee Agents** plus their settings and permission sets. Both agents are **out-of-the-box (OOTB) agent templates** authored as Builder Script (`.agent`) bundles. No managed package is required.

## What's in the bundle

| Asset | Path | Notes |
|---|---|---|
| Settings | `settings/` | `AgentPlatform`, `EinsteinCopilot`, `EinsteinGpt`. Deployed first by `deploy_agents_settings`. |
| Revenue Quote Management agent | `aiAuthoringBundles/RLM_Revenue_Quote_Management/` | Builder Script `.agent` authoring bundle (developer name `RLM_Revenue_Quote_Management`; label "Revenue Quote Management"). The org compiles this into `Bot` + `BotVersion` + `GenAiPlannerBundle` at publish time. |
| Billing Employee Assistance agent | `aiAuthoringBundles/RLM_Billing_Employee_Assistance/` | Builder Script `.agent` authoring bundle (developer name `RLM_Billing_Employee_Assistance`; label "Billing Employee Assistance"). |
| Permission sets | `permissionsets/RLM_QuotingAgent.permissionset-meta.xml`, `permissionsets/RLM_BillingEmployeeAgent.permissionset-meta.xml` | Each contains `<agentAccesses>` so Lightning users can see the agent. |

`AiAuthoringBundle` requires **API version 65.0 or higher**.

## OOTB agent templates (no managed package)

Both bots reference platform-provided templates via `agent_type: "AgentforceEmployeeAgent"` in the `.agent` config block (template lineages `quotingAI__QuotingEmployeeAgent` for Quote and `billing_agents__BillingEmployeeAgent` for Billing).

The `quotingAI__` and `billing_agents__` prefixes look like managed-package namespaces but they are **platform-provided OOTB templates** — available without installing a package.

Planner-bundle action IDs are not committed for either agent — the platform mints them fresh from the `.agent` source on each `sf agent publish`.

## Deploy / activate / assign

Driven by the `prepare_agents` flow (`cumulusci.yml`):

1. `assign_permission_set_groups` → `CopilotSalesforceUserPSG`, `CopilotSalesforceAdminPSG`
2. `deploy_agents_settings` → `unpackaged/post_agents/settings`
3. `deploy_agents` → the authoring bundles under `unpackaged/post_agents/aiAuthoringBundles`
4. `publish_agents` → runs `sf agent publish authoring-bundle` for each `aiAuthoringBundles/<Name>/` so the platform compiles the bundle into a runnable `BotVersion`
5. `activate_agents` → runs `sf agent activate` for each agent discovered under `aiAuthoringBundles/`
6. `deploy_agent_permission_sets` → `unpackaged/post_agents/permissionsets` (must run **after** publish: each PS's `<agentAccesses>` compiles to a `botDefinition` reference, and the Bot only exists once the bundle is published)
7. `assign_permission_sets` → `RLM_QuotingAgent`, `RLM_BillingEmployeeAgent` (the `ps_aea` anchor)

Every step is gated on the `agents` feature flag (`project_config.project__custom__agents`, default `true` in `cumulusci.yml`). Standalone task invocation (e.g. `cci task run deploy_agents --org <alias>`) bypasses the gate.

## Why post-deploy publish + activation are required

Two separate platform gaps are bridged by this flow:

1. **Authoring bundles compile at publish time, not deploy time.** Deploying an `AiAuthoringBundle` puts the `.agent` source in the org but does not produce a `BotVersion`. `sf agent publish authoring-bundle` is the platform compile step. `publish_agents` (`tasks/rlm_publish_agents.py`) iterates every directory under `aiAuthoringBundles/` and runs the publish command for each.
2. **`BotVersion.Status` is not part of deployable metadata and is not DML-writable.** Fresh deploys (and freshly-published bundles) always land Inactive. `activate_agents` (`tasks/rlm_activate_agents.py`) iterates every agent name under `aiAuthoringBundles/` and runs `sf agent activate --api-name <Name> --json`, which wraps the Connect REST endpoint `POST /connect/bot-versions/{botVersionId}/activation`.

Both tasks discover agents from disk, so adding a new agent's directory under `aiAuthoringBundles/` automatically enrolls it in publish + activate. No edits to the task code are needed.

## Adding a new agent

1. Author the `.agent` source, or retrieve it from an existing org:
   ```
   sf project retrieve start \
     --metadata "AiAuthoringBundle:<Name>" \
     --target-org <alias>
   ```
2. Place the `.agent` source under `unpackaged/post_agents/aiAuthoringBundles/<Name>/`.
3. Add a permission set with `<agentAccesses>` and wire it into the `ps_aea` anchor in `cumulusci.yml`.
4. `publish_agents` and `activate_agents` auto-discover from disk; no code changes needed.
