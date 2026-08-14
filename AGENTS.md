# AI Agent Instructions — Revenue Cloud Base Foundations

> Canonical instructions for **any** AI coding agent working with this
> repository (Cursor, Claude Code, GitHub Copilot, Codex, Windsurf,
> Aider, or any future tool). Safety-critical rules that apply to every
> task. Detailed guidance lives in skill files (see Skill Index below).

## Project Overview

**Revenue Cloud Base Foundations** automates creation and configuration of
Salesforce environments for Revenue Lifecycle Management (RLM). **This is the
`264` branch — Release 264 (Winter '27, API v68.0)** — the active development
line. `main` is the 262 (Summer '26, v67.0) GA target; `release/262` and
`release/260` are frozen references.

264 is pre-GA — no release notes or v68.0 Metadata Coverage Report yet — so **a
live 264 org is ground truth, not documentation**. The dev hub is on API 68.0, so
every scratch org it creates is a 264 org whatever branch you built from, and
`main` is **not buildable on it**. Distinguish a *fresh* 264 org from a 262 org
*upgraded* to 264: an upgrade grandfathers settings and schema, so it is not
evidence about fresh builds.

Key technology stack:
- **CumulusCI (CCI)** — orchestration engine for tasks and flows
- **SFDMU v5** — data import/export (`sf sfdmu run`). **v5.6.4+ required**
  (5.6.4 fixed upsert matching for relationship-traversal externalIds —
  older 5.x duplicates records on rerun for Upsert plans like qb-prm;
  enforced by `validate_setup`, the Docker image build, and CI)
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
templates/             # Source-of-truth for UX assembly (step 29)
datasets/sfdmu/        # SFDMU data plans (export.json + CSVs)
datasets/context_plans/# Context definition plans
datasets/constraints/  # Configurator constraint rule data
datasets/tooling/      # Tooling API metadata exports
# Runtime-only output dirs (created by extract_* tasks; not tracked):
#   datasets/bre/        — Business Rule Engine exports (extract_bre)
#   datasets/dx/         — DX-format metadata snapshots (extract_dx_*)
scripts/apex/          # Apex activation/deletion/validation scripts
scripts/ai/            # AI agent tooling (query_erd, generate_cci_reference)
scripts/cml/           # CML export/import/validation utilities
scripts/erd/           # ERD validation, diffing, cleanup, HTML generation, schema_diff/
scripts/expression_sets/ # Standalone Expression Set lifecycle toolkit (inspect/trace/diff/export + guarded mutators; sf-CLI transport, no CCI). See its README.md
scripts/soql/          # Reusable SOQL query files
scripts/build_harness/ # Build harness runner and TUI
scripts/*.py           # Top-level utilities: dataset validation/generation and demo
                       #   drivers (validate_sfdmu_v5_datasets, expand_currency_*,
                       #   qb_usage, build_quote_to_asset, post_process_extraction)
tasks/                 # Custom Python CCI task classes
tests/                 # Offline test suites — mostly Python (`python tests/<name>.py`,
                       #   no org needed), plus two shell integration scripts
robot/rlm-base/        # Robot Framework tests (setup + E2E)
orgs/                  # Scratch org definitions (orgs/README.md; TFID: orgs/tfid/README.md)
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
8. **DO NOT** commit or push directly to `main` **or to the active release
   branch** (`264`; likewise `release/*`) — all changes go through a feature
   branch and a pull request, which is how the 262 line was built. This applies
   to docs and agent-instruction files, not just code. Never force-push any of
   them without explicit user approval: PRs are routinely stacked on the active
   release branch, so rewriting it invalidates every one of them.
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
| SF CLI command | `--target-org <sf_alias_or_username>` | `sf data query -q "..." --target-org <sf_alias_or_username>` |

CCI alias `beta` maps to an SF CLI alias `rlm-base__beta`. Never mix them.

In Python tasks: use `self.org_config.username` for CLI calls,
`self.org_config.access_token` + `.instance_url` for REST API only.

---

## SFDMU v5 — Critical Rules

All data plans **must** comply with these rules. SFDMU v5 has breaking
changes from v4.

### externalId Format
- Use `;` delimiters: `Field1;Field2` (NOT `$$Field1$Field2`)
- `$$` columns in CSVs are valid for Upsert target-record matching

### v5 Bugs — one live on the 5.6.4 floor, four fixed upstream

Because **v5.6.4 is the enforced floor** (see the tech-stack note above), the
historical Upsert-matching bugs are fixed upstream and **only Bug 4 is still
live**. On a 5.6.4+ plugin, **do not** introduce `operation: Insert` +
`deleteOldData: true` citing Bugs 1/2/3/5 — Upsert works. Existing plans that
still carry that pattern are pre-5.6.4 workarounds; migrating them back to Upsert
is the separate, gated `sfdmu-v5-optimization` initiative (needs live
verification + explicit per-operation approval — do not flip operations ad hoc;
see the CRITICAL rule below).

**Bug 4 — `$$` composite notation fails for lookup reference columns (STILL PRESENT, incl. 5.8.0)**
When a CSV uses `$$` composite notation for a **lookup reference** — self-referential
(e.g. `ParentGroup.$$Code$ParentProduct.StockKeepingUnit`) *or cross-object* — SFDMU
cannot decompose the composite value to resolve the referenced record. (The primary
`$$` externalId-matching column is unaffected.)
**Fix:** Use simple single-field references for lookup columns
(e.g. `ParentGroup.Code`). Non-destructive — no `deleteOldData`.

<details>
<summary>Bugs 1/2/3/5 — fixed at or below the 5.6.4 floor (kept for history; do NOT apply their Insert+deleteOldData workarounds on 5.6.4+)</summary>

- **Bug 1 — all-multi-hop externalId fails validation** (`{Object} has no mandatory external Id field definition`). **Fixed in 5.3.1.** *Was:* use at least one direct field in the `externalId`.
- **Bug 2 — 2-hop traversal columns produce malformed SOQL in Upsert.** **Fixed in 5.6.3.** *Was:* `operation: Insert` + `deleteOldData: true`. *Residue by design:* dotted composite segments are still dropped from child `__r` relationship queries on **extract** — the root cause of the `#N/A` blanking that `post_process_extraction.py` backfills (5.6.3 also set `#N/A` = null marker, bare `N/A` = literal).
- **Bug 3 — Upsert with relationship-traversal externalId never matches** (duplicates on every run). **Fixed in the 5.6.4 release** (commit `50be987`, `_getNestedRecordFieldValue`; source-verified). *Was:* `operation: Insert` + `deleteOldData: true`.
- **Bug 5 — composite externalId of all relationship traversals fails upsert matching** (e.g. `Parent.Name;OtherParent.Name`). **Fixed in 5.6.4** (same relationship-path matching fix). *Was:* `operation: Insert` + `deleteOldData: true` for objects whose only logical key is a composite of parent lookups.

</details>

### CRITICAL — Insert + deleteOldData requires explicit approval

**Never propose changing `Upsert` to `Insert` + `deleteOldData: true` without:**
1. Explaining *why* Upsert cannot work (on the 5.6.4+ floor Bugs 1/2/3/5 are
   fixed — cite a concrete, current reason, not those historical bugs)
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
cci task run check_decision_table_freshness --org beta               # readiness: is any lookup stale? (-o param1 strict to fail the build)
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

> **How review is *conducted* — what to look for, the severity rubric, the defect classes
> this repo actually produces, and push discipline — lives in [`REVIEW.md`](REVIEW.md) at
> the repo root.** It is read automatically alongside this file, by Claude and by Copilot.
> This section covers only the *protocol*: what to do with a review comment once it exists.

Automated reviewers (GitHub Copilot, the Codex / `chatgpt-codex-connector` bot, and
similar) post inline comments on PRs. **Policy — every agent, every PR:** each review
comment is handled to completion, and **every review round ends with zero unresolved
threads.**

**Batch fixes into one push per review round.** Every push to an open PR triggers a fresh
automated review; re-reviews are not incremental (a hosted reviewer may repeat comments
already dismissed or resolved), and a push mid-review lands against a superseded commit,
spending a whole round on findings that no longer apply. Fix everything from a round,
verify locally, then push once. See `REVIEW.md` → *Push discipline*.

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
| Edit/ship/debug **Constraint models** (CML) — configurator bundle rules, `.ffxblob`, why a model change does not take effect | `.cursor/skills/constraint-models/SKILL.md` |
| Read/extend/apply/deploy/upgrade Context Definitions (Context Service); inspect/validate context plans | `.cursor/skills/context-service/SKILL.md` |
| Inspect/author/manage, refresh, diagnose, or verify **decision tables**; wire automatic refresh at the right moment | `.cursor/skills/decision-tables/SKILL.md` |
| Find, claim, or close a durable **todo** across workstations and agents (`/rlm-todos`) | `.cursor/skills/todo-tracker/SKILL.md` |
| Run build harness workflows | `.cursor/skills/build-harness/SKILL.md` |
| Build a PDE (or other org type) via runtime-only feature-flag overrides | `.cursor/skills/pde-org-build/SKILL.md` |
| Write a Python CCI task class | `.cursor/skills/cci-orchestration/custom-task-authoring.md` |
| Create/modify SFDMU data plans | `.cursor/skills/sfdmu-data-plans/SKILL.md` |
| Maintain the In-App Learning framework (`inapp` integration) | `.cursor/skills/inapp-framework/SKILL.md` |
| Understand RLM objects/relationships | `.cursor/skills/revenue-cloud-data-model/SKILL.md` |
| Build/rate/verify metered consumption demos (usage, commitments, drawdown) | `.cursor/skills/usage-consumption/SKILL.md` |
| Validate / refresh / certify the ERD against orgs and Core source | `.cursor/skills/schema-validation/SKILL.md` |
| Consume PMOS content from Foundations (or vice versa) via cross-repo skill manifest | `.cursor/skills/pmos-integration/SKILL.md` |
| Use Revenue Cloud REST APIs | `.cursor/skills/rlm-business-apis/SKILL.md` |
| Generate, inspect, continue, or verify transaction demo data | `.cursor/skills/txn-data-harness/SKILL.md` |
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
| Author/debug OmniDataTransform (ODT) data mappers | `.cursor/skills/odt-authoring/SKILL.md` |
| Create/modify .docx document templates + DocumentTemplate lifecycle | `.cursor/skills/document-generation/SKILL.md` |

Every top-level skill has a **Quick Rules** section, and most have **DO NOT**;
new and migrated skills should also include **Entry Conditions**, **Examples**,
and **Validation Checks** sections. Existing skills are being migrated to this
structure incrementally, so not all of them carry the full set yet. Read
`.cursor/skills/skill-authoring/SKILL.md` before creating, splitting,
registering, or testing skills.

### Skill Sub-Files (Progressive Disclosure)

Most skills split detail into sub-files to keep their entry point small. Every
skill lists and describes its own sub-files, so open the parent `SKILL.md` from
the table above and read its sub-file section — there is deliberately no
second-level index here. When you add a sub-file, register it in its parent
`SKILL.md`.

### Script Reference

Helper scripts are documented in the skill that owns them, with the full option
reference and worked examples. Read that skill rather than guessing flags:

| Scripts | Owning skill |
|---------|--------------|
| `scripts/docgen/*` — ODT authoring, validation, diffing; DocumentTemplate lifecycle; generation | `document-generation/SKILL.md` (install `scripts/docgen/requirements.txt` first) |
| `scripts/erd/*` — ERD validation against orgs, cross-release schema diff, orphan cleanup, HTML build | `schema-validation/SKILL.md` |
| `scripts/context_service/*` — Context Definition inspect/validate/apply, plus the runtime context-instance lifecycle | `context-service/SKILL.md` |
| `scripts/expression_sets/*` — Expression Set inspect/trace/diff/export and guarded mutators | `expression-sets/SKILL.md` |
| `scripts/cml/*` — constraint model export/import/validate | `constraint-models/SKILL.md` |
| `scripts/ai/query_erd.py` — query the RLM data model offline | `revenue-cloud-data-model/SKILL.md` |
| `scripts/ai/skill_manifest.py` — cross-repo skill manifest resolver | `pmos-integration/SKILL.md` |
| `scripts/ai/pr_review.py` — automated-PR-review helper | **Responding to Automated PR Reviews**, above |
| `scripts/ai/generate_cci_reference.py`, `scripts/ai/check_plan_readme_consistency.py`, `scripts/validate_sfdmu_v5_datasets.py` | **Pre-merge checklists**, above |

Two Context Service rules are worth obeying without a second read (rationale in
the skill): **modifying or deleting** an existing node, attribute, or tag on an
*active* version is blocked (`RECORD_UPDATE_FAILED`) — deactivate first, though
pure *inserts* apply in place. And a runtime `contextId` is **request-scoped** —
an opaque handle that does not survive separate CLI calls, so chaining
create → query → persist needs Apex or a single Flow. Persist is **async**:
confirm via `AsyncOperationTracker`, not the returned `referenceId`.

Cursor's file-pattern rules (`.cursor/rules/*.mdc`) and the equivalent skill for
each are tabulated in `.cursor/skills/README.md`.

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
| `REVIEW.md` | Any agent + Copilot | **How pull requests get reviewed** — severity rubric, what to look for, this repo's recurring defect classes, push discipline. Distinct content, not a duplicate of this file. |
| `.agents/README.md` | Any agent | Tool-agnostic routing layer: instruction-stack overview, per-tool adapters (`.agents/adapters/`), model routing, and project context. Defers to `AGENTS.md`. |

`AGENTS.md`, `CLAUDE.md`, and `.github/copilot-instructions.md` resolve to the
same content — edit `AGENTS.md` only. `REVIEW.md` is a **separate** document with its
own content: this file governs *what the code must do*, `REVIEW.md` governs *how review
is conducted*. They overlap on three points by design — verifying a finding, sweeping a
class, and push discipline — where this file carries the short operational form and
`REVIEW.md` carries the reasoning. Keep those three in sync when either changes, and do
not add duplication beyond them. The `.agents/` tree is a separate routing and context
layer that points back to `AGENTS.md` and never overrides it.
