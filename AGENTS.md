# AI Agent Instructions — Revenue Cloud Base Foundations

> Canonical instructions for **any** AI coding agent working with this
> repository (Cursor, Claude Code, GitHub Copilot, Codex, Windsurf,
> Aider, or any future tool). Safety-critical rules that apply to every
> task. Detailed guidance lives in skill files (see Skill Index below).

## Project Overview

**Revenue Cloud Base Foundations** automates creation and configuration of
Salesforce environments for Revenue Lifecycle Management (RLM). It targets
Salesforce Release 262 (Summer '26, API v67.0), now on the `main` branch
(promoted from the `262` upgrade branch). The previous GA target, Release 260
(Spring '26), is preserved on the `release/260` branch as the prior GA reference.

Key technology stack:
- **CumulusCI (CCI)** — orchestration engine for tasks and flows
- **SFDMU v5** — data import/export (`sf sfdmu run`). **v5.0.0+ required.**
- **Salesforce DX / `sf` CLI** — metadata deployment and org management
- **Python** — custom CCI task classes in `tasks/`
- **Apex** — post-load activation scripts in `scripts/apex/`

## Repository Layout

```
cumulusci.yml          # Task/flow definitions, feature flags, org defs
config/                # Scratch org definition JSON (project-scratch-def.json)
force-app/             # Core SFDX metadata (deployed at step 5)
unpackaged/pre/        # Pre-deploy metadata (fields, settings, PSGs, DTs)
unpackaged/post_*/     # Feature-specific metadata bundles
unpackaged/post_ux/    # ⚠ AUTO-GENERATED — never edit directly
templates/             # Source-of-truth for UX assembly (step 30)
datasets/sfdmu/        # SFDMU data plans (export.json + CSVs)
datasets/context_plans/# Context definition plans
datasets/constraints/  # Configurator constraint rule data
datasets/tooling/      # Tooling API metadata exports
# Runtime-only output dirs (created by extract_* tasks; not tracked):
#   datasets/bre/        — Business Rule Engine exports (extract_bre)
#   datasets/dx/         — DX-format metadata snapshots (extract_dx_*)
scripts/apex/          # Apex activation/deletion scripts
scripts/ai/            # AI agent tooling (query_erd, generate_cci_reference)
scripts/cml/           # CML export/import/validation utilities
scripts/erd/           # ERD validation, diffing, cleanup, HTML generation, schema_diff/
scripts/soql/          # Reusable SOQL query files
scripts/build_harness/ # Build harness runner and TUI
tasks/                 # Custom Python CCI task classes
tests/                 # Shell-based integration test scripts
robot/rlm-base/        # Robot Framework tests (setup + E2E)
orgs/                  # Scratch org definition JSON files (TFID template shapes: orgs/tfid/README.md)
postman/               # Postman collections for RLM APIs
docs/                  # Documentation (lower-kebab-case filenames)
```

## DO NOT — Safety Guards

1. **DO NOT** edit files in `unpackaged/post_ux/` — edit `templates/` instead
2. **DO NOT** add `layoutAssignment` or `applicationVisibilities` to
   `force-app/` profiles — use `templates/profiles/`
3. **DO NOT** add object `.object-meta.xml` files with `actionOverrides`
   to `force-app/` — they belong in `templates/objects/`
4. **DO NOT** change `operation: Upsert` to `operation: Insert` +
   `deleteOldData: true` without explicit user approval (see SFDMU rules)
5. **DO NOT** pass `access_token` to `sf` CLI commands — use
   `org_config.username` as `--target-org`
6. **DO NOT** add `EmailTemplatePage` flexipages to `templates/flexipages/`
   — they cannot deploy via Metadata API
7. **DO NOT** commit real emails in `rlm.network-meta.xml` — use the
   placeholder; patch/revert tasks handle deploy-time substitution
8. **DO NOT** commit or push directly to `main` — all changes must go
   through a feature branch and pull request. Never use `git push origin main`
   or force-push main without explicit user approval.
9. **DO NOT** present a behavioral Robot Framework change as verified —
   or merge one — on the strength of `robot --dryrun`. Dryrun validates only
   syntax and keyword resolution; it never launches a browser or runs the
   `Execute JavaScript`/shadow-DOM logic, so it is **not** verification. Any
   behavioral change to a `robot/**/*.robot` suite (keywords, locators, JS,
   click targets, wait/assert flow) **or** the Python task wrapper that invokes
   a suite (`tasks/rlm_*.py`) must be run against a **live scratch org** before
   the PR merges. If you must commit such a change unverified, say so explicitly
   and keep the PR blocked (label `blocked: needs-live-verification`) until a
   live run passes. Exempt: comment/`[Documentation]`-only edits, and resource
   files with no behavioral change. See
   `.cursor/skills/robot-testing/SKILL.md` → **Verification**.

## Org Identity: CCI vs SF CLI

CCI and `sf` CLI use **different alias registries**:

| Context | Flag | Example |
|---------|------|---------|
| CCI task/flow | `--org <cci_alias>` | `cci task run insert_quantumbit_pricing_data --org beta` |
| SF CLI command | `--target-org <sf_alias_or_username>` | `sf data query -q "..." --target-org rlm-base__beta` |

CCI alias `beta` → SF CLI alias `rlm-base__beta`. Never mix them.

In Python tasks: use `self.org_config.username` for CLI calls,
`self.org_config.access_token` + `.instance_url` for REST API only.

---

## SFDMU v5 — Critical Rules

All data plans **must** comply with these rules. SFDMU v5 has breaking
changes from v4.

### externalId Format
- Use `;` delimiters: `Field1;Field2` (NOT `$$Field1$Field2`)
- `$$` columns in CSVs are valid for Upsert target-record matching

### The Five Confirmed v5 Bugs

**Bug 1 — All-multi-hop externalId fails validation**
`{Object} has no mandatory external Id field definition`
**Fix:** Use at least one direct field in the `externalId`.

**Bug 2 — 2-hop traversal columns cause SOQL injection in Upsert**
**Fix:** Use `operation: Insert` + `deleteOldData: true`.

**Bug 3 — Upsert with relationship-traversal externalId never matches**
Creates duplicates on every run.
**Fix:** Use `operation: Insert` + `deleteOldData: true`.
*Upstream: [SFDX-Data-Move-Utility#781](https://github.com/forcedotcom/SFDX-Data-Move-Utility/issues/781)*

**Bug 4 — `$$` composite key self-references fail on import**
When a CSV uses `$$` composite notation for a self-referential lookup
(e.g. `ParentGroup.$$Code$ParentProduct.StockKeepingUnit`), SFDMU
cannot resolve the parent record.
**Fix:** Use simple single-field references for self-referential lookups
(e.g. `ParentGroup.Code`).

**Bug 5 — Composite externalId with all-traversal fields fails upsert matching**
When `externalId` is composed entirely of relationship traversals
(e.g. `Parent.Name;OtherParent.Name`), SFDMU inserts duplicates on
every run instead of matching existing records.
**Fix:** Use `operation: Insert` + `deleteOldData: true` for objects
whose only logical key is a composite of parent lookups.

### CRITICAL — Insert + deleteOldData requires explicit approval

**Never propose changing `Upsert` to `Insert` + `deleteOldData: true` without:**
1. Explaining *why* Upsert cannot work (which Bug applies)
2. Confirming no direct-field externalId alternative exists
3. Getting **explicit user approval**

`deleteOldData: true` is destructive — it deletes all existing records
before inserting. When in doubt, keep Upsert.

### deleteOldData Deletion Order
Objects delete in **reverse array order**. Always order parent → child
in the array; deletions run child → parent.

---

## Common Workflows

```bash
cci task run insert_quantumbit_pricing_data --org beta
cci task run delete_quantumbit_pricing_data --org beta
cci task run extract_qb_pricing_data --org beta
cci task run test_qb_pricing_idempotency --org beta
cci flow run prepare_rlm_org --org beta
cci task run assemble_and_deploy_ux                                 # deploys to your DEFAULT cci org (no --org flag — set the default org to target one)
cci task run assemble_and_deploy_ux -o deploy false                 # dry-run: local assembly only, no org needed
cci flow run capture_ux_drift --org dev-sb0                          # retrieve + diff
cci flow run apply_ux_drift --org dev-sb0                            # writeback + reassemble + verify
cci task run writeback_ux_templates --org dev-sb0                    # dry-run writeback
cci task run validate_setup                                          # no org needed
python scripts/validate_sfdmu_v5_datasets.py
python scripts/ai/generate_cci_reference.py                         # after cumulusci.yml edits
```

---

## Pre-merge checklists for AI agents

Use these before opening or updating a PR. They complement the **PR Review Focus Areas** below.

### SFDMU data plans (`datasets/sfdmu/**`, `export.json`, CSVs)

1. Run `python scripts/validate_sfdmu_v5_datasets.py` and fix reported issues.
2. Keep **`externalId`** (`;` delimiters) and CSV `$$` columns aligned with the skill rules in this file — do not change `Upsert` to `Insert` + `deleteOldData: true` without explicit user approval.
3. If the plan’s behavior or objects changed, update the plan’s **README** in the same change, then run `python scripts/ai/check_plan_readme_consistency.py <plan_dir>` — it fails if the README's object table or `# N records` listings drift from the actual `export.json`/CSVs (record counts, operations, externalIds, phantom/missing objects). Must report **0 errors**.

### `cumulusci.yml` and CCI tasks

1. After editing `cumulusci.yml` (tasks, flows, options): run `python scripts/ai/generate_cci_reference.py` and commit the regenerated reference files.
2. If you rename a task or change its description, search the repo for the **old task name** in docs (`README.md`, `docs/`) and fix stale references.
3. For Python task changes in `tasks/`, follow `.cursor/skills/cci-orchestration/custom-task-authoring.md` — especially **CLI vs REST** (`username` for `sf`, not `access_token`).

### Documentation consistency

Follow `.cursor/skills/doc-consistency/SKILL.md` — it provides a
**change-surface map** (when X changes, update Y) covering task names,
flag tables, SFDMU plan READMEs, generated CCI references, skill
indexes, and more.

### Merges and unintended diffs

1. Before push, review `git diff main --stat` (or the merge base you use). Pay extra attention to **`orgs/`**, **`datasets/`**, **`unpackaged/post_ux/`**, and scratch data — unexpected churn often means files were **swept in from another branch**.
2. Changes under **`unpackaged/post_ux/`** should come from **`assemble_and_deploy_ux`** or the **UX drift** flows, not manual XML edits (see `.cursor/skills/repo-integration/ux-assembly-retrieve.md`).

---

## PR Review Focus Areas

1. **SFDMU v5 compliance** — externalId format, operation + deleteOldData
2. **Idempotency** — can the plan run twice without duplicates?
3. **Apex bulk safety** — no SOQL in loops, no single-record DML in loops
4. **cumulusci.yml** — task group, description accuracy, feature flag conditions
5. **CSV headers** — `$$` columns match externalId fields exactly
6. **UX templates** — edits in `templates/`, never `unpackaged/post_ux/`
7. **Profile/object rules** — force-app profiles stay classAccesses-only
8. **PRM Network email** — repo uses placeholder only; patch/revert in order
9. **Edition flags** — `pde`, `trial` change PSL/PS assignments and feature
   availability; verify `when:` guards match the target edition. Developer Edition
   detection is now automatic via `org_config.org_type`

---

## Responding to Automated PR Reviews

Automated reviewers (GitHub Copilot, the Codex / `chatgpt-codex-connector` bot, and
similar) post inline comments on PRs. **Policy — every agent, every PR:** each review
comment is handled to completion, and **every review round ends with zero unresolved
threads.**

**Tooling — `python scripts/ai/pr_review.py`** (or the `/pr-review <pr>` command in Claude
Code) automates the mechanical steps so a round can't be left half-finished:
`status <pr>` lists unresolved threads (paginated), `handle <pr> --comment <id> --body "…"`
replies + resolves one thread (adds 👍 **by default** — pass `--no-react` to refute a false
positive without the 👍, per the "react on valid comments" rule below), and `verify <pr>`
confirms 0 unresolved (exit 1 if any remain). It's tool-agnostic (shells out to `gh`); defaults to the current repo, or pass
`--repo owner/name`. Verifying findings and sweeping the class (steps 1–2) stay your job.

For each comment:

1. **Verify against the code.** Don't trust the bot — confirm the claim in the actual
   source and classify it *real*, *partial*, or *false positive*.
2. **Sweep the whole class.** If a finding is real, fix **every** instance of that
   pattern across the change, not just the cited line.
3. **Reply in-thread** with the resolution **and the commit SHA** (or a clear,
   evidence-backed refutation for a false positive):
   `gh api --method POST repos/<owner>/<repo>/pulls/<n>/comments/<id>/replies -f body="…"`
4. **React** 👍 on a valid comment:
   `gh api --method POST repos/<owner>/<repo>/pulls/comments/<id>/reactions -H "Accept: application/vnd.github+json" -f content="+1"`
5. **Resolve the thread** (REST cannot — use GraphQL). List threads with the full query
   root — `reviewThreads` lives under `repository(owner:, name:){ pullRequest(number:N){ … } }`
   (`pullRequest` is **not** a GraphQL root field) — and **paginate** so PRs with >100
   threads aren't truncated:
   `repository(owner:$o,name:$r){ pullRequest(number:$n){ reviewThreads(first:100, after:$cursor){ pageInfo{ hasNextPage endCursor } nodes{ id isResolved comments(first:1){ nodes{ databaseId path line } } } } } }`
   — loop, passing `endCursor` as `after`, until `hasNextPage` is false. Resolve each
   unresolved id with `mutation($tid:ID!){ resolveReviewThread(input:{threadId:$tid}){ thread{ isResolved } } }`.
6. **Confirm clean** — re-query `reviewThreads` across **all** pages (same pagination) and
   verify `unresolved == 0` for the round.

Refute false positives (with evidence) rather than changing correct code — but still
reply, and resolve the thread once the point is settled. This matters most on branches
headed for `main`, which mirror to the internal Salesforce repo for audit: a left-open
thread is a finding the audit will re-raise.

---

## AI Agent Skill Index

Skills are detailed guides for specific tasks. They live in
`.cursor/skills/` but are **plain markdown** — readable by any agent,
not Cursor-specific. Read the skill file when you need guidance on
that topic.

| I need to... | Skill File (relative to repo root) |
|-------------|-------------------------------------|
| Set up / replicate / update the local dev toolchain | `docs/guides/dev-environment-setup.md` |
| Run the containerized toolchain (Docker image + `rlm` wrapper + devcontainer) | `docker/README.md` |
| Add new features, code placement | `.cursor/skills/repo-integration/SKILL.md` |
| Work with CCI tasks, flows, CLI | `.cursor/skills/cci-orchestration/SKILL.md` |
| Wire pricing recipes/procedures/plans | `.cursor/skills/pricing-wiring/SKILL.md` |
| Author/CRUD Expression Sets (pricing procedures, etc.) via Connect/Metadata API; build step overlays | `.cursor/skills/expression-sets/SKILL.md` |
| Run build harness workflows | `.cursor/skills/build-harness/SKILL.md` |
| Build a PDE (or other org type) via runtime-only feature-flag overrides | `.cursor/skills/pde-org-build/SKILL.md` |
| Write a Python CCI task class | `.cursor/skills/cci-orchestration/custom-task-authoring.md` |
| Create/modify SFDMU data plans | `.cursor/skills/sfdmu-data-plans/SKILL.md` |
| Maintain the In-App Learning framework (`inapp` integration) | `.cursor/skills/inapp-framework/SKILL.md` |
| Understand RLM objects/relationships | `.cursor/skills/revenue-cloud-data-model/SKILL.md` |
| Validate / refresh / certify the ERD against orgs and Core source | `.cursor/skills/schema-validation/SKILL.md` |
| Consume PMOS content from Foundations (or vice versa) via cross-repo skill manifest | `.cursor/skills/pmos-integration/SKILL.md` |
| Use Revenue Cloud REST APIs | `.cursor/skills/rlm-business-apis/SKILL.md` |
| Generate, inspect, continue, or verify transaction demo data | `.cursor/skills/txn-data-harness/SKILL.md` |
| Create/deploy/activate Salesforce Hosted MCP servers (`mcp` feature, `post_mcp`, McpServerDefinition + McpServerAccess) | `.cursor/skills/mcp-server/SKILL.md` |
| Write Robot Framework tests | `.cursor/skills/robot-testing/SKILL.md` |
| Capture/apply UX drift from org | `.cursor/skills/repo-integration/ux-assembly-retrieve.md` |
| Review docs before merge | `.cursor/skills/doc-consistency/SKILL.md` |
| Create, update, register, or test AI-agent skills | `.cursor/skills/skill-authoring/SKILL.md` |
| Debug a build/deploy failure | `.cursor/skills/troubleshooting/SKILL.md` |
| Harden Apex CRUD/FLS (USER_MODE) + make a permission set self-sufficient | `.cursor/skills/apex-security-hardening/SKILL.md` |
| Process Codex/Copilot PR reviews or run the pre-merge audit (completeness sweeps) | `.cursor/skills/audit-review/SKILL.md` |
| Author/update enablement exercises per release | `.cursor/skills/release-enablement/SKILL.md` |
| Generate the QuantumBit demo-script canvas (per-release SE/partner artifact) | `.cursor/skills/qb-demo-script/SKILL.md` |
| Ground product claims against Salesforce Help (Trailhead, internal docs, SME review) | `.cursor/skills/revenue-cloud-docs/SKILL.md` |

Every top-level skill has a **Quick Rules** section, and most have **DO NOT**;
new and migrated skills should also include **Entry Conditions**, **Examples**,
and **Validation Checks** sections. Existing skills are being migrated to this
structure incrementally, so not all of them carry the full set yet. Read
`.cursor/skills/skill-authoring/SKILL.md` before creating, splitting,
registering, or testing skills.

### Skill Sub-Files (Progressive Disclosure)

Some skills split detail into sub-files to keep entry points small.
Read the sub-file only when you need that specific detail:

| Sub-file | Parent Skill | Contains |
|----------|-------------|----------|
| `repo-integration/new-feature-guide.md` | Repository Integration | Step-by-step code templates for adding a new feature |
| `repo-integration/dependency-ordering.md` | Repository Integration | Metadata/data ordering, `prepare_rlm_org` step map |
| `robot-testing/patterns.md` | Robot Testing | Shadow DOM code, keyword reference, test authoring |
| `robot-testing/setup-ui-shadow-dom.md` | Robot Testing | Setup UI: shadow vs iframe, LWS, logging (companion to `patterns.md`) |
| `repo-integration/ux-assembly-retrieve.md` | Repository Integration | Assembler vs retrieve, `post_ux` rules, drift workflow |
| `cci-orchestration/custom-task-authoring.md` | CCI Orchestration | Python task class patterns and examples |
| `cci-orchestration/tasks-reference.md` | CCI Orchestration | Auto-generated task listing (regenerate after edits) |
| `cci-orchestration/flows-reference.md` | CCI Orchestration | Auto-generated flow listing |
| `cci-orchestration/feature-flags.md` | CCI Orchestration | Auto-generated feature flag index |
| `revenue-cloud-data-model/domains/*.md` | Data Model | Per-domain object/field/relationship details |
| `revenue-cloud-data-model/cross-domain-relationships.md` | Data Model | Cross-domain FK mapping |
| `sfdmu-data-plans/plan-dependency-graph.md` | SFDMU Data Plans | Load/deletion order across plans |
| `sfdmu-data-plans/object-plan-mapping.md` | SFDMU Data Plans | Which objects belong to which plan |
| `docs/salesforce/{version}/feature-index.md` | Release Enablement | Per-area feature inventory for a Salesforce release (260, 262, …) — authoring input for `docs/enablement/{version}/` exercises |
| `docs/enablement/_template/exercise-template.md` | Release Enablement | Canonical template for `{version}-{area}-hands-on.md` exercise files |
| `docs/enablement/coverage-matrix.md` | Release Enablement | Cross-release inventory of which exercise artifacts exist where |
| `release-enablement/authoring-patterns.md` | Release Enablement | Edge-case patterns: upgrade guidance, known issues, sub-features, cross-area features, recordings placeholders, QB walkthrough handling |
| `release-enablement/resume-enablement-work.md` | Release Enablement | Cross-workstation handoff — read when picking up enablement work in a fresh conversation. 4-step re-orientation + tool grants + restart prompt template |
| `docs/enablement/master/qb-scenario-reference.md` | Release Enablement | Canonical QB catalog reference (Infinitech, Global Media accounts, products, SKUs) for exercise walkthroughs |
| `troubleshooting/large-deal-preprocess-reference.md` | Troubleshooting | Large-deal reprice → preprocess → activate signals: `CalculationStatus` enum, `ValidationResult` gate, `PreprocessingStatus` decode, PST async trackers, tax-skip |
| `docs/references/expression-set-connect-api-reference.md` | Expression Sets | Object/ID model, OAS-confirmed schema enums, every Connect/Metadata error + resolution, Metadata API authoring path, verification checklist |

### File-Specific Rules (Cursor Only)

Cursor IDE auto-injects `.cursor/rules/*.mdc` files when editing matching
file patterns. Non-Cursor agents can read these files directly for the
same guidance, or use the parent skill which covers the same content:

| Rule File | Triggers On | Equivalent Skill |
|-----------|-------------|------------------|
| `.cursor/rules/sfdmu-export-json.mdc` | `**/export.json` | `sfdmu-data-plans/SKILL.md` |
| `.cursor/rules/sfdmu-csv-data.mdc` | `datasets/sfdmu/**/*.csv` | `sfdmu-data-plans/SKILL.md` |
| `.cursor/rules/cci-task-definitions.mdc` | `cumulusci.yml` | `cci-orchestration/SKILL.md` |
| `.cursor/rules/cci-python-tasks.mdc` | `tasks/**/*.py` | `cci-orchestration/custom-task-authoring.md` |
| `.cursor/rules/apex-scripts.mdc` | `scripts/apex/**/*.apex` | `troubleshooting/SKILL.md` |
| `.cursor/rules/apex-classes.mdc` | `unpackaged/**/*.cls`, `force-app/**/*.cls` | *(stand-alone — sharing keywords, `Id.valueOf` validation, SOQL safety, test patterns; complements `repo-integration/SKILL.md` for placement)* |
| `.cursor/rules/lwc-components.mdc` | `unpackaged/**/lwc/**/*.{html,js}`, `force-app/**/lwc/**/*.{html,js}` | *(stand-alone — template syntax, ARIA/accessibility, performance, error messages; complements `repo-integration/SKILL.md` for placement)* |
| `.cursor/rules/ux-templates.mdc` | `templates/**` | `repo-integration/SKILL.md` |
| `.cursor/rules/robot-tests.mdc` | `robot/**/*.robot` | `robot-testing/SKILL.md` |
| `.cursor/rules/doc-review.mdc` | `cumulusci.yml`, `tasks/**/*.py`, `datasets/sfdmu/**/export.json`, `datasets/sfdmu/**/*.csv`, `robot/**/*.robot`, `.cursor/skills/**/*.md` | `doc-consistency/SKILL.md` |

### AI Utility Scripts

Scripts in `scripts/ai/` help agents query project data:

```bash
python scripts/ai/query_erd.py describe Product2           # Query RLM data model
python scripts/ai/query_erd.py domain Pricing               # List domain objects
python scripts/ai/generate_cci_reference.py                 # Regenerate CCI docs
python scripts/ai/skill_manifest.py --check                 # Verify cross-repo skill manifest can resolve PMOS clone
python scripts/ai/skill_manifest.py --list-skills foundations
python scripts/ai/pr_review.py status <pr>                  # Automated-PR-review helper: list unresolved threads
python scripts/ai/pr_review.py handle <pr> --comment <id> --body "…"   # reply + resolve one thread (👍 by default; --no-react to refute a false positive)
python scripts/ai/pr_review.py verify <pr>                  # confirm 0 unresolved (paginated)
python scripts/ai/check_plan_readme_consistency.py          # SFDMU plan README ↔ export.json/CSVs drift check (counts, ops, externalIds)
```

`scripts/ai/pr_review.py` executes the mechanical half of **Responding to Automated PR Reviews** (above); the `/pr-review <pr>` Claude command drives the full protocol with it.

`scripts/ai/skill_manifest.py` is the resolver for the cross-repo skill manifest at `.claude/skill-manifest.yml` — see `.cursor/skills/pmos-integration/SKILL.md` for the integration pattern.

### Schema Validation Scripts

Scripts for keeping `docs/erds/erd-data.json` aligned with canonical Revenue Cloud platform schema. See `.cursor/skills/schema-validation/SKILL.md` for the full workflow.

```bash
python scripts/erd/validate_erd_against_org.py --org <alias>           # Diff ERD vs org
python scripts/erd/validate_erd_against_org.py --org <alias> --patch   # Patch ERD with org-discovered fields
python scripts/erd/schema_diff/extract_schema.py --org <alias> --output <file>.json
python scripts/erd/schema_diff/diff_schemas.py --baseline 260.json --target 262.json --impact
python scripts/erd/cleanup_orphan_erd_fields.py --orgs <260>,<262> --dry-run    # Cross-validate orphans
python scripts/erd/build_erds.py                              # Regenerate ERD HTML viewer
```

**All schema scripts skip custom fields by default** (`__c` suffix, including project `RLM_*__c` and managed-package fields). The ERD reflects canonical platform schema only. Pass `--include-custom` only for project-internal tooling that needs to see deployed custom fields.

---

## Documentation Conventions

All `.md` files under `docs/` use **lower-kebab-case** filenames.
Placement:

| Directory | Content |
|-----------|---------|
| `docs/guides/` | How-to guides (constraints setup, docgen, build guides) |
| `docs/references/` | Reference material (CCI tasks, permissions, decision tables) |
| `docs/analysis/` | Technical analysis documents |
| `docs/features/` | Feature design docs (UX assembly, E2E framework, etc.) |
| `docs/api/` | API documentation and interactive viewers |
| `docs/enablement/` | Hands-on exercises: `master/` (living source), `{version}/` (release extracts), `_template/` |
| `docs/erds/` | ERD diagrams (Mermaid source + HTML viewer) |
| `docs/salesforce/{version}/` | Per-release feature indexes and Help portal snapshots |
| `docs/integration/` | Integration-related documentation |

---

## Agent Entry Points

This repository provides multiple entry points for different AI tools:

| File | Tool | Purpose |
|------|------|---------|
| `AGENTS.md` | Any agent | Canonical source of truth (this file) |
| `CLAUDE.md` | Claude Code, Cursor | Symlink to `AGENTS.md` |
| `.github/copilot-instructions.md` | GitHub Copilot | Pointer to `AGENTS.md` |
| `.agents/README.md` | Any agent | Tool-agnostic routing layer: instruction-stack overview, per-tool adapters (`.agents/adapters/`), model routing, and project context. Defers to `AGENTS.md`. |

`AGENTS.md`, `CLAUDE.md`, and `.github/copilot-instructions.md` resolve to the
same content — edit `AGENTS.md` only. The `.agents/` tree is a separate routing
and context layer that points back to `AGENTS.md` and never overrides it.
