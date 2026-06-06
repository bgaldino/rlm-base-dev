# Model Routing Guidance

Use this routing guide when planning or reviewing AI-assisted repository work. Prefer the lowest-cost option that can answer safely, and escalate when a task crosses subsystem boundaries or involves Salesforce safety-critical behavior.

## Recommended Routing

| Work type | Recommended model or execution mode | Notes |
| --- | --- | --- |
| Fast/static inventory | Efficient small model or script-only execution | Use for counts, lists, simple diffs, and deterministic repository scans. Prefer scripts when no judgment is required. |
| File-presence checks, path checks, generated-reference freshness | Script-only | Validate with deterministic commands rather than model judgment. Examples include checking whether expected files exist, whether paths are referenced, or whether generated docs are stale. |
| Skill/rule coverage classification | Efficient reasoning model | Use when mapping changed files to relevant `.cursor/skills/` or `.cursor/rules/` guidance and when classifying whether coverage is complete. |
| Cross-cutting architecture recommendations | Frontier model | Use when recommendations span tasks, flows, metadata layout, data plans, templates, scripts, or release strategy. |
| Salesforce release-impact reasoning | Most capable available model | Use for Release 262 impact analysis, feature-flag behavior, edition differences, or compatibility with prior release branches. |
| SFDMU destructive-operation review | Most capable available model | Use for any review involving `operation: Insert`, `deleteOldData: true`, deletion ordering, external IDs, or idempotency risk. |
| Security/safety review | Most capable available model | Use for credentials, org identity, CLI authentication, access tokens, packaging exposure, network metadata, or destructive automation. |
| Final report synthesis for multi-domain runs | Frontier or high-context model | Use when a run includes multiple domains or needs to reconcile findings from scripts, skills, data plans, metadata, and docs. |
| Final report synthesis for scorecard refresh only | Efficient model | Use when updating a narrowly scoped scorecard with deterministic inputs and no cross-domain recommendation work. |

## Escalation Criteria

Escalate to a frontier or most capable available model when any of the following are true:

1. More than one major subsystem changed (see definition below).
2. `cumulusci.yml` changed.
3. `datasets/sfdmu/**` changed.
4. `AGENTS.md`, `.cursor/skills/**`, `.cursor/rules/**`, or `.claude/skill-manifest.yml` changed.
5. Any recommendation touches destructive Salesforce operations, credentials, org identity, or packaging.

### What counts as a "major subsystem"

A major subsystem is one of these top-level functional areas of the repository:

| Subsystem | Primary paths |
| --- | --- |
| Orchestration | `cumulusci.yml`, `tasks/**` |
| Data plans | `datasets/sfdmu/**`, `datasets/**` |
| Metadata | `force-app/**`, `unpackaged/**` |
| UX assembly | `templates/**`, `unpackaged/post_ux/**` |
| Testing | `robot/**`, `tests/**` |
| Tooling & docs | `scripts/**`, `docs/**`, `.agents/**` |

"More than one major subsystem changed" means a single change set touches paths in two or more of these rows — for example, a PR that edits both `tasks/rlm_sync_pricing_data.py` (Orchestration) and `datasets/sfdmu/procedure-plans/export.json` (Data plans). A change confined to one row (e.g. three files all under `datasets/sfdmu/**`) is a single-subsystem change and does not trigger this criterion on its own.

## Default Decision Pattern

1. Start with script-only checks for deterministic facts.
2. Use an efficient reasoning model for classification or lightweight interpretation.
3. Escalate to a frontier model for cross-cutting design or synthesis.
4. Escalate to the most capable available model for Salesforce release impact, SFDMU destructive operations, security, credentials, org identity, or packaging risk.
