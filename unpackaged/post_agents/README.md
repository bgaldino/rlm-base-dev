# Agentforce Agents

This bundle deploys two Agentforce **Employee Agents** plus their settings and permission sets. Both agents are **out-of-the-box (OOTB) agent templates** authored as Builder Script (`.agent`) bundles. No managed package is required.

## What's in the bundle

| Asset | Path | Notes |
| --- | --- | --- |
| Settings | `settings/` | `AgentPlatform`, `EinsteinCopilot`, `EinsteinGpt`. Deployed first by `deploy_agents_settings`. |
| Product Configuration services | `classes/` | Apex invocable services used by Product Configuration flows: `RLM_AI_QuoteLineItemLookupService`, `RLM_AI_ProductAttributeService`, `RLM_AI_ProductAttributeSaveService`, `RLM_AI_ProductAttributeReadService`. |
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
3. `deploy_agent_classes` → `unpackaged/post_agents/classes` (Apex invocable services used by Product Configuration flows)
4. `deploy_agent_flows` → `unpackaged/post_agents/flows` (custom autolaunched flows backing Product Configuration actions)
5. `deploy_agents` → the authoring bundles under `unpackaged/post_agents/aiAuthoringBundles`
6. `publish_agents` → runs `sf agent publish authoring-bundle` for each `aiAuthoringBundles/<Name>/` so the platform compiles the bundle into a runnable `BotVersion`
7. `activate_agents` → runs `sf agent activate` for each agent discovered under `aiAuthoringBundles/`
8. `deploy_agent_permission_sets` → `unpackaged/post_agents/permissionsets` (must run **after** publish: each PS's `<agentAccesses>` compiles to a `botDefinition` reference, and the Bot only exists once the bundle is published)
9. `assign_permission_sets` → `RLM_QuotingAgent`, `RLM_BillingEmployeeAgent` (the `ps_aea` anchor)

Every step is gated on the `agents` feature flag (`project_config.project__custom__agents`, default `true` in `cumulusci.yml`). Standalone task invocation (e.g. `cci task run deploy_agents --org <alias>`) bypasses the gate.

## Why post-deploy publish + activation are required

Two separate platform gaps are bridged by this flow:

1. **Authoring bundles compile at publish time, not deploy time.** Deploying an `AiAuthoringBundle` puts the `.agent` source in the org but does not produce a `BotVersion`. `sf agent publish authoring-bundle` is the platform compile step. `publish_agents` (`tasks/rlm_publish_agents.py`) iterates every directory under `aiAuthoringBundles/` and runs the publish command for each.
2. **`BotVersion.Status` is not part of deployable metadata and is not DML-writable.** Fresh deploys (and freshly-published bundles) always land Inactive. `activate_agents` (`tasks/rlm_activate_agents.py`) iterates every agent name under `aiAuthoringBundles/` and runs `sf agent activate --api-name <Name> --json`, which wraps the Connect REST endpoint `POST /connect/bot-versions/{botVersionId}/activation`.

Both tasks discover agents from disk, so adding a new agent's directory under `aiAuthoringBundles/` automatically enrolls it in publish + activate. No edits to the task code are needed.

## Publish / version / activate runbook

Use this sequence whenever `.agent` source changes and you want the UI to reflect them.

1. Deploy metadata (settings/classes/flows/bundles):

   ```bash
   cci task run deploy_agents_settings --org <alias>
   cci task run deploy_agent_classes --org <alias>
   cci task run deploy_agent_flows --org <alias>
   cci task run deploy_agents --org <alias>
   ```

2. Publish bundles (creates new `BotVersion` records):

   ```bash
   cci task run publish_agents --org <alias>
   ```

   > Do **not** run `sf agent publish authoring-bundle --api-name <Name>` directly from repo root in this project. The direct CLI publish path can resolve against the default `force-app` package directory and fail to find bundles stored under `unpackaged/post_agents/aiAuthoringBundles`.

3. Activate latest versions:

   ```bash
   cci task run activate_agents --org <alias>
   ```

4. If needed, deploy/assign permission sets after publish:

   ```bash
   cci task run deploy_agent_permission_sets --org <alias>
   cci task run assign_permission_sets --org <alias>
   ```

5. Verify in Agentforce Builder by selecting the newly active version.

### Why this matters

- Deploying `AiAuthoringBundle` metadata updates authoring source only.
- Users do not see behavior changes until a new version is published and activated.

## Troubleshooting publish/version issues

### "Changes deployed but not visible in Builder"

- You are likely viewing an older active version.
- Save draft, publish, activate, then switch the Builder version dropdown to the active version.

### `Cannot find an authoring bundle in force-app`

- `sf agent publish authoring-bundle` scans the default package directory only.
- In this repo, authoring bundles live under `unpackaged/post_agents/aiAuthoringBundles`, not `force-app`.
- In this repo, use `cci task run publish_agents --org <alias>` (it stages bundles correctly and publishes from the right path).
- Symptom you will see when using the direct CLI call from repo root:
  - `Error (CannotFindBundle): Cannot find an authoring bundle in .../force-app that matches <AgentName>`

### Agent not visible in end-user panel after delete/recreate (but appears Active in Builder)

Symptoms:

- Agent is present and active in Agentforce Builder.
- User has the expected permission set assignment (for example `RLM_QuotingAgent`).
- End-user panel still shows only other agents.

Root cause:

- The agent was deleted/recreated, which changed `BotDefinition.Id`.
- The permission set's `<agentAccesses>` binding was stale/missing in `SetupEntityAccess` for the new bot definition.
- Result: user assignment exists, but effective access to the current bot definition does not.

Fix:

1. Republish + activate agents.
2. Redeploy agent permission sets **after** publish:

   ```bash
   cci task run deploy_agent_permission_sets --org <alias>
   ```

3. Reassign permission sets (if needed):

   ```bash
   cci task run assign_permission_sets --org <alias> -o api_names "RLM_QuotingAgent,RLM_BillingEmployeeAgent"
   ```

4. Verify `SetupEntityAccess` rows exist for both permission sets and current `BotDefinition` records, then hard-refresh UI.

### Publish fails with restricted picklist error on `Generative AI Function Definition ID`

Example:

`bad value for restricted picklist field: RLM_AI_Configure_Product_Attributes`

Cause:

- Action `source` bindings inside the `.agent` can become stale for custom flow-backed actions.

Fix:

1. In Builder draft, delete and re-add each affected flow action (keeps references fresh).
2. Save draft, publish, activate.
3. Retrieve updated authoring bundle back to source control:

   ```bash
   sf project retrieve start \
     --metadata "AiAuthoringBundle:RLM_Revenue_Quote_Management" \
     --target-org <alias>
   ```

Repo convention:

- For custom flow-backed actions in this repo, keep `target: "flow://..."` authoritative and avoid relying on manually-curated `source` values.

### CLI warning: `Polling for SourceMembers timed out` for `AiAuthoringBundle`

- Common source-tracking noise for bundle metadata.
- If deploy/publish status is `Succeeded`, treat as non-blocking.

## Adding a new agent

1. Author the `.agent` source, or retrieve it from an existing org:

   ```bash
   sf project retrieve start \
     --metadata "AiAuthoringBundle:<Name>" \
     --target-org <alias>
   ```

2. Place the `.agent` source under `unpackaged/post_agents/aiAuthoringBundles/<Name>/`.
3. Add a permission set with `<agentAccesses>` and wire it into the `ps_aea` anchor in `cumulusci.yml`.
4. `publish_agents` and `activate_agents` auto-discover from disk; no code changes needed.
