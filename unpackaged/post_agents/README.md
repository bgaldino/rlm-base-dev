# Agentforce Agents

This bundle deploys two Agentforce **Employee Agents** plus their settings, planner bundles, and permission sets. Both agents are **out-of-the-box (OOTB) agent templates** that ship with Salesforce Release 262 — they were retrieved from a 262 org (`260fix2`) and committed here as source. No managed package is required.

## What's in the bundle

| Asset | Path | Notes |
|---|---|---|
| Settings | `settings/` | `AgentPlatform`, `EinsteinCopilot`, `EinsteinGpt`. Deployed first by `deploy_agents_settings`. |
| Revenue Quote Management agent | `bots/Revenue_Quote_Management/` | Decomposed `Bot` + `BotVersion` source format. |
| Billing Employee Assistance agent | `bots/Billing_Employee_Assistance/` | Decomposed `Bot` + `BotVersion` source format. |
| Planner bundles | `genAiPlannerBundles/Revenue_Quote_Management/`, `genAiPlannerBundles/Billing_Employee_Assistance/` | Topics, plugins, local actions, planner actions. |
| Permission sets | `permissionsets/RLM_QuotingAgent.permissionset-meta.xml`, `permissionsets/RLM_BillingEmployeeAgent.permissionset-meta.xml` | Each contains `<agentAccesses>` so Lightning users can see the agent. |

## OOTB agent templates (no managed package)

Both bots reference platform-provided templates:

- `Revenue_Quote_Management` → `<agentTemplate>quotingAI__QuotingEmployeeAgent</agentTemplate>`
- `Billing_Employee_Assistance` → `<agentTemplate>billing_agents__BillingEmployeeAgent</agentTemplate>`

The `quotingAI__` and `billing_agents__` prefixes look like managed-package namespaces but they're **platform-provided OOTB templates** introduced in Release 262 — they're available in scratch orgs without installing a package. Verified against `jun25_1` (scratch on Release 262): no `quotingAI`/`billing_agents` entries in `PackageLicense` or `ApexClass.NamespacePrefix`, yet the deploy succeeds and the agents run.

The planner-bundle action IDs (e.g. `BillingCollections_16jg7000000VKyX`, `GetAccountBillingSummary_179g7000000p3iE`) are **org-specific** — they were minted in the `260fix2` source org. The platform regenerates IDs on deploy into a new org, so these source IDs are essentially labels rather than addressable references after deploy.

## Deploy / activate / assign

Driven by the `prepare_agents` flow (`cumulusci.yml`):

1. `assign_permission_set_groups` → `CopilotSalesforceUserPSG`, `CopilotSalesforceAdminPSG`
2. `deploy_agents_settings` → `unpackaged/post_agents/settings`
3. `deploy_agents` → the whole `unpackaged/post_agents` tree
4. `activate_agents` → runs `scripts/apex/activateAgents.apex` (see below)
5. `assign_permission_sets` → `RLM_QuotingAgent`, `RLM_BillingEmployeeAgent` (the `ps_aea` anchor)

Every step is gated on the `agents` feature flag (`project_config.project__custom__agents`, default `false` in `cumulusci.yml`). Standalone task invocation (e.g. `cci task run deploy_agents --org <alias>`) bypasses the gate.

## Why post-deploy activation is required

`BotVersion.Status` is **not** part of the deployable bot XML and is **not** DML-writable from Apex. Fresh deploys land with `Status = 'Inactive'`. To activate, the platform exposes a Connect REST endpoint:

```
POST /services/data/v62.0/connect/bot-versions/{botVersionId}/activation
Body: {"status":"Active"}
```

`scripts/apex/activateAgents.apex` resolves the latest `BotVersion` per agent name and POSTs to that endpoint. This mirrors what `sf agent activate` does internally. If you add a new agent to this bundle, also add its `DeveloperName` to the `agentNames` set in that script.

## Adding a new agent

1. Retrieve the bot in **SFDX source format** (do not pass `--target-metadata-dir`, which yields the legacy single-file `.bot`):
   ```
   sf project retrieve start --metadata Bot:<Name> --metadata GenAiPlannerBundle:<Name> --target-org <alias>
   ```
   This emits `bots/<Name>/<Name>.bot-meta.xml` and `bots/<Name>/v1.botVersion-meta.xml` in decomposed form.
2. Move the retrieved files into `unpackaged/post_agents/bots/<Name>/` and `unpackaged/post_agents/genAiPlannerBundles/<Name>/`.
3. Add a permission set under `permissionsets/` with `<agentAccesses><agentName>...</agentName><enabled>true</enabled></agentAccesses>` so end users can see the agent.
4. Add the permset API name to the `ps_aea` anchor in `cumulusci.yml`.
5. Add the agent's `DeveloperName` to the `agentNames` set in `scripts/apex/activateAgents.apex`.
6. If the agent has org-specific action IDs in its planner bundle, accept that those IDs are essentially labels — the platform mints fresh IDs on deploy.
