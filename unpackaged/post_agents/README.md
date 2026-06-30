# Agentforce Agents

This bundle deploys three Agentforce **Employee Agents** plus their settings and permission sets. Quoting Assistant and Billing Employee Assistance are authored as Builder Script (`.agent`) bundles; Revenue Quote Management uses the legacy decomposed format (Bot + BotVersion + GenAiPlannerBundle). No managed package is required. (The Quoting Assistant is a ground-up custom agent rather than an OOTB template lineage; see its row below.)

## What's in the bundle

| Asset | Path | Notes |
| --- | --- | --- |
| Settings | `settings/` | `AgentPlatform`, `EinsteinCopilot`, `EinsteinGpt`. Deployed first by `deploy_agents_settings`. |
| Product Configuration & quote-line services | `classes/` | Apex invocable services behind the agent flows: `RLM_AI_QuoteLineItemLookupService` (scored product-name matching; blank product name lists every line for selection — used by both Product Configuration and Revenue Quote Management's discount flow), `RLM_AI_ProductAttributeService`, `RLM_AI_ProductAttributeSaveService`, `RLM_AI_ProductAttributeReadService`, plus the shared `inherited sharing` helper `RLM_AI_ConfigServiceUtils` (Id/prefix validation, null-safe JSON, SOQL LIKE escaping). |
| Revenue Quote Management agent | `legacy/bots/Revenue_Quote_Management/` + `legacy/genAiPlannerBundles/Revenue_Quote_Management/` | Legacy-format agent (developer name `Revenue_Quote_Management`; label "Revenue Quote Management"). Deployed as standard metadata (Bot + BotVersion + GenAiPlannerBundle). Does not require publish step — activated via `sf agent activate` after deploy. |
| Quoting Assistant agent | `aiAuthoringBundles/RLM_Quoting_Assistant/` | Builder Script `.agent` authoring bundle (developer name `RLM_Quoting_Assistant`; label "Quoting Assistant"). A ground-up, scoped demo quoting agent — tight arc (find products → create/identify quote → add line → discount → configure → totals), unified no-redundant-confirmation policy (`require_user_confirmation: False` everywhere), and a names-not-IDs presentation contract (native record cards; Id outputs flagged `is_used_by_planner: false`). Backed by the three `RLM_AI_*` helper services/flows below. Intentionally excludes asset lifecycle and usage/consumption. |
| Billing Employee Assistance agent | `aiAuthoringBundles/RLM_Billing_Employee_Assistance/` | Builder Script `.agent` authoring bundle (developer name `RLM_Billing_Employee_Assistance`; label "Billing Assistant"). |
| Quoting Assistant helper services | `classes/RLM_AI_AddProductToQuoteService`, `RLM_AI_ApplyQuoteLineDiscountsService`, `RLM_AI_QuoteDemoSummaryService` (+ tests) | Apex invocable services behind the Quoting Assistant's three helper flows (`flows/RLM_AI_Add_Product_To_Quote`, `RLM_AI_Apply_Quote_Line_Discounts`, `RLM_AI_Get_Quote_Demo_Summary`): one-call add-product (resolves product + default selling model, then the managed add-line), one-call bulk line discount (high-level targeting: applyToAll / productName / display-ordinals; percent, target-price, percent-of-list modes), and a read-only names-only quote recap. Each isolates the managed `quotingAI__*` invocation behind a `@TestVisible` invoker seam. |
| Permission sets | `permissionsets/RLM_QuotingAgent.permissionset-meta.xml`, `permissionsets/RLM_QuotingAssistant.permissionset-meta.xml`, `permissionsets/RLM_BillingEmployeeAgent.permissionset-meta.xml` | Each contains `<agentAccesses>` so Lightning users can see the agent. |

`AiAuthoringBundle` requires **API version 65.0 or higher**.

## OOTB agent templates (no managed package)

The Revenue Quote Management and Billing agents reference platform-provided templates via `agent_type: "AgentforceEmployeeAgent"` (template lineages `quotingAI__QuotingEmployeeAgent` for Quote and `billing_agents__BillingEmployeeAgent` for Billing). The Quoting Assistant is a custom Agent Script bundle.

The `quotingAI__` and `billing_agents__` prefixes look like managed-package namespaces but they are **platform-provided OOTB templates** — available without installing a package.

Planner-bundle action IDs are not committed for either agent — the platform mints them fresh from the `.agent` source on each `sf agent publish`.

### Bundle versioning is intentionally unpinned

Each `*.bundle-meta.xml` contains only `<bundleType>AGENT</bundleType>` — **no `<target>AgentName.vNN</target>` element**. This is deliberate and "timeless": every `sf agent publish authoring-bundle` (driven by `publish_agents`) auto-mints the next `BotVersion`, and `activate_agents` activates that latest version. Pinning `<target>` to a specific `.vNN` would force a version bump in source on every behavioral change (churn) and only matches the org it was last retrieved from — it does **not** help fresh deploys. **Do not re-add a `<target>` version element.** If you ever retrieve a bundle from an org and the CLI writes a `<target>…vNN</target>` back in, strip it before committing.

## Deploy / activate / assign

Driven by the `prepare_agents` flow (`cumulusci.yml`):

1. `assign_permission_set_groups` → `CopilotSalesforceUserPSG`, `CopilotSalesforceAdminPSG`
2. `deploy_agents_settings` → `unpackaged/post_agents/settings`
3. `deploy_agent_classes` → `unpackaged/post_agents/classes` (Apex invocable services used by Product Configuration flows)
4. `deploy_agent_flows` → `unpackaged/post_agents/flows` (custom autolaunched flows backing Product Configuration actions)
5. `deactivate_agents` → deactivates legacy agents so metadata can be redeployed idempotently (tolerates not-yet-deployed or already-inactive agents)
6. `deploy_legacy_agents` → `unpackaged/post_agents/legacy` (Bot + BotVersion + GenAiPlannerBundle — standard metadata deploy, no publish needed)
7. `deploy_agents` → the authoring bundles under `unpackaged/post_agents/aiAuthoringBundles`
8. `publish_agents` → runs `sf agent publish authoring-bundle` for each `aiAuthoringBundles/<Name>/` so the platform compiles the bundle into a runnable `BotVersion`
9. `activate_agents` → runs `sf agent activate` for all agents (both authoring bundles and legacy bots)
10. `deploy_agent_permission_sets` → `unpackaged/post_agents/permissionsets` (must run **after** publish/activate: each PS's `<agentAccesses>` compiles to a `botDefinition` reference)
11. `assign_permission_sets` → `RLM_QuotingAgent`, `RLM_QuotingAssistant`, `RLM_BillingEmployeeAgent` (the `ps_aea` anchor)

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
   cci task run assign_permission_sets --org <alias> -o api_names "RLM_QuotingAgent,RLM_QuotingAssistant,RLM_BillingEmployeeAgent"
   ```

4. Verify `SetupEntityAccess` rows exist for all three permission sets and current `BotDefinition` records, then hard-refresh UI.

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
     --metadata "AiAuthoringBundle:RLM_Quoting_Assistant" \
     --target-org <alias>
   ```

Repo convention:

- For custom flow-backed actions in this repo, keep `target: "flow://..."` authoritative and avoid relying on manually-curated `source` values.

### CLI warning: `Polling for SourceMembers timed out` for `AiAuthoringBundle`

- Common source-tracking noise for bundle metadata.
- If deploy/publish status is `Succeeded`, treat as non-blocking.

### Temporary context-debug subagent (reference)

If page-context behavior regresses, you can temporarily add a debug subagent to an
agent script, publish/activate, test, then remove it again before merge.

1. Add a router transition only for explicit debug requests.
2. Add this subagent block near the end of the `.agent` file:

   ```text
   subagent debug_context:

       label: "Debug Context"
       description: "Report runtime page context and routing diagnostics."

       reasoning:
           instructions: ->
               | Return a concise debug report with:
                 - currentAppName
                 - currentObjectApiName
                 - currentPageType
                 - currentRecordId
                 - inferredContextObject
                 - inferredQuoteId (if applicable)
                 - recommendedSubagent
                 - why that routing should apply
                 If any value is unavailable, say "not available".
                 Do not call business actions in this mode.
   ```

3. Publish + activate to test.
4. Remove the debug transition and `debug_context` block after troubleshooting.

## Testing the agents (`sf agent test` / `test_agents`)

Agent behavior — routing to the right subagent, invoking the right action,
honoring guardrails — is **not** verifiable by metadata deploy or `--dryrun`.
It must run against a **published + activated** agent in a live org. The repo
ships CLI Testing Center specs and a CCI task to run them.

### Layout

```text
tests/
  billing/                   # RLM_Billing_Employee_Assistance specs
    billing-routing.yaml     # router → billing subagents
    billing-actions.yaml     # business actions via conversationHistory pre-positioning
    billing-guardrail.yaml   # off-topic, ambiguous, prompt-injection, exfiltration
  quoting-assistant/         # RLM_Quoting_Assistant (Quoting Assistant) specs
    quoting-assistant-routing.yaml       # router → ProductSelection / QuoteManagement / ProductConfiguration
    quoting-assistant-actions.yaml       # one-turn add (Helper A), one-call discount (Helper B), precedence, general-tool reachability
    quoting-assistant-regression.yaml    # discount precedence + names-not-IDs guards
    quoting-assistant-guardrail.yaml     # off-topic, out-of-scope (assets/usage), ambiguous (demo posture: no adversarial assertions)
```

Each `*.yaml` is an Agentforce test spec (`name`, `subjectType: AGENT`,
`subjectName: <agent developer_name>`, `testCases`). It deploys to the org as an
`AiEvaluationDefinition` via `sf agent test create`.

### Running

```bash
# Default: quoting-assistant specs.
cci task run test_agents --org <alias>

# Run one specific agent suite.
cci task run test_agents --org <alias> -o agent billing
cci task run test_agents --org <alias> -o agent quoting-assistant

# Run one spec or a comma-separated subset within an agent suite.
cci task run test_agents --org <alias> -o agent quoting-assistant -o test_files quoting-assistant-routing,quoting-assistant-actions

# Explicit full regression across every checked-in agent suite.
cci task run test_agents --org <alias> -o agent all

# Run named files across selected suites; useful with agent all for cross-agent smoke tests.
cci task run test_agents --org <alias> -o agent all -o test_files billing-routing.yaml,quoting-assistant-routing.yaml

# Ad hoc/local suite path, for experiments or a temporarily isolated subset.
cci task run test_agents --org <alias> -o tests_path unpackaged/post_agents/tests/billing
```

> **These tests are slow — run them intentionally.** Each case is a live LLM
> evaluation against a published agent. They are **not** part of org bring-up
> (`prepare_agents`) and are never invoked automatically by the deployment flows.
> Run them only when you make a **substantive agent change** — routing, action
> wiring, guardrails, confirmation gates, or the test specs themselves — and
> before merging such a change. Use a specific `agent` value for focused
> validation, add `test_files` when only a few specs are relevant, and use
> `agent all` only when you intentionally want the full cross-agent regression.

`test_agents` (`tasks/rlm_test_agents.py`) maps the `agent` option to the
checked-in suite directories:

| `agent` value | Agent developer name | Specs |
| --- | --- | --- |
| `billing` | `RLM_Billing_Employee_Assistance` | `unpackaged/post_agents/tests/billing` |
| `quoting-assistant` | `RLM_Quoting_Assistant` | `unpackaged/post_agents/tests/quoting-assistant` |
| `all` | all of the above | every checked-in suite, run sequentially |

Use `test_files` to narrow the selected suite(s). Values are comma-separated
and can be a file name (`quoting-assistant-routing.yaml`), a stem (`quoting-assistant-routing`), a path
relative to the suite (`quoting-assistant-routing.yaml`), or a repo-relative path
(`unpackaged/post_agents/tests/quoting-assistant/quoting-assistant-routing.yaml`). When `agent all` is
selected, the task matches those names across all checked-in suite directories
and runs only the files that match.

For each selected `*.yaml`, the task derives a deterministic api-name, runs
`sf agent test create --force-overwrite` then `sf agent test run --wait`, and
**fails** if any `topic_assertion` or `actions_assertion` is non-PASS, or if
`output_validation` is non-PASS on a case that set an `expectedOutcome` (the
harmless "missing expected input" skip on cases without one is ignored). It
passes `--target-org` from the CCI org config on every call, so it never hits
your default SF CLI org by accident.

`test_quoting_assistant` exists as a convenience alias for
`cci task run test_agents --org <alias> -o agent quoting-assistant`, but new automation and
docs should use the single `test_agents` entry point.

The agent must already be published + activated (run `prepare_agents`, or the
publish/activate runbook above) before testing.

### Agent Script testing notes

These are multi-subagent **Agent Script** agents, which affects how specs read:

- This agent does **not** surface the router's `go_to_<Subagent>` transition in
  `actionsSequence`; the runtime `topic` equals the destination subagent name
  (no hash). Routing specs therefore assert `expectedTopic`, and action specs
  use `conversationHistory` to pre-position the agent inside the target subagent
  before the business action fires.
- **Single-turn flow completion reports `topic: agent_router`.** When one
  utterance drives a delegated flow to completion in a single turn (e.g.
  "Create a quote …" runs IdentifyRecordByName → CreateInitialQuote →
  Get_Quote_Record_Card and returns control to the router), the result's `topic`
  is `agent_router`, not the subagent. Requests that *stop* inside a subagent
  awaiting input (discount, sync) report the subagent. So assert the business
  action (`expectedActions`) for complete-in-one-turn cases and the subagent
  topic for the rest.
- **Omitting `expectedTopic` / `expectedActions` still emits an empty
  expectation.** `sf agent test create` always writes a `topic_sequence_match` /
  `action_sequence_match` block; when the spec leaves it unset the block has a
  blank `expectedValue` and the runtime reports it as a non-PASS that can never
  pass. The `test_agents` evaluator treats a topic/action assertion with no
  expected value as "nothing asserted" and ignores it (a real "expect no
  actions" case carries `[]`, which is preserved).
- `expectedActions` uses the **Level 1 definition name** (e.g.
  `ApplyDiscountToQuoteLine`), as it appears in results.
- **Confirmation-gated actions** (`require_user_confirmation: True` —
  `UpdateQuoteDetails`, `UpdateQuoteLineItemDetails`, `UpdateRecordFields`,
  `Confirm_Product_Configuration_Summary`, and the discount apply guarded by the
  subagent's "ask the user to confirm" constraint) only fire after an explicit
  "yes". Those specs put the confirmation prompt as the final history turn and
  use a confirming utterance.
- Guardrail/deflection routing is non-deterministic, so those cases omit
  `expectedTopic` and assert on `expectedOutcome` instead.

### Topic / action name discovery

Runtime topic names can differ from the `.agent` subagent names. After a first
run, extract the actual names and update the specs:

```bash
sf agent test run --api-name RLM_Quote_Routing --wait 15 \
  --result-format json --json --target-org <sf-alias> \
  | jq '.result.testCases[].generatedData | {topic, actionsSequence}'
```

`--use-most-recent` is broken on `sf agent test results` — use `--job-id`, or
`sf agent test resume --use-most-recent`.

### Test data dependency

The quote action/regression specs reference real org records (the Infinitech
account, its opportunity, and its 3-line draft quote). If you run against a
freshly built org, confirm equivalent data exists (or seed it) and update the
IDs/names in the specs — the `FindProducts` utterances also assume a populated
product catalog. Note one data subtlety the config specs depend on: on the
Infinitech quote, the **"Additional API"** lines have a configurable attribute
(via their ProductClassification) while **"Additional API Prod"** has none
(`BasedOnId` is null) — so attribute-configuration cases must target
"Additional API".

### CLI single-turn limitation (what these specs do NOT cover)

CLI Testing Center sends one utterance per case; `conversationHistory` only
*simulates* prior turns — it does **not** execute earlier actions, so the agent
enters each case holding **no IDs resolved by a previous action**. This bounds
what single-utterance specs can assert for **stateful, multi-record write
chains**:

- **Find-then-add** ("Add 2 units of 32GB RDIMM"): the product isn't yet a
  resolved catalog record, so the agent calls `FindProducts` first and offers to
  add — it does not fire `AddQuoteLineItemToQuote` in the same turn. The spec
  asserts the agent works toward the add, not the one-turn call.
- **Confirm-then-apply-to-all** ("Yes, discount all of them"): the confirmation
  lives only in simulated history, so the agent holds no resolved line IDs and
  asks one final go-ahead before mutating all lines. A fully-resolved **single**
  line *does* apply on "yes" (see the single-line apply case). The spec asserts
  the all-lines intent/readiness, not the loop of `ApplyDiscountToQuoteLine`.

These reflect deliberately demo-friendly agent behavior (the agent **biases
toward action** on clear, unambiguous, single-record requests, and asks once on
ambiguous or multi-record writes — record-resolution guardrails in the agent's
`system.instructions` and QuoteManagement hard constraints). True end-to-end
`create → add → discount-all` chains where action state persists across turns
belong to the **multi-turn Agent Runtime API** track (see
`~/.claude/skills/sf-ai-agentforce-testing`), a documented follow-up.

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
