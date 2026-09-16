# AI Agent Instructions — Revenue Cloud Base Foundations

> Canonical instructions for **any** AI coding agent working with this
> repository (Cursor, Claude Code, GitHub Copilot, Codex, Windsurf,
> Aider, or any future tool). Safety-critical rules that apply to every
> task. Detailed guidance lives in skill files (see Skill Index below).

## Agent Entry Points

1. Read this file for universal rules; use the **AI Agent Skill Index** below
   or [.cursor/skills/README.md](.cursor/skills/README.md) to select task guidance.
   Read a skill before using its tools, and follow its linked sub-files as needed.
2. `CLAUDE.md` is a symlink to this file; edit `AGENTS.md` only for the shared
   contract. `.github/copilot-instructions.md` is a separate pointer to it.
3. [`REVIEW.md`](REVIEW.md) governs how reviews are conducted; this file governs
   required behavior and the response protocol. Keep verification, class sweeps
   and push discipline aligned between them; do not duplicate other review detail.
4. [`CONTRIBUTING.md`](CONTRIBUTING.md) covers contribution conventions.
   Governance companions: `LICENSE.txt` (Apache-2.0), `CODE_OF_CONDUCT.md`, `SECURITY.md`.
5. [`.agents/README.md`](.agents/README.md) describes routing, model guidance and
   project context; its adapters do not override this contract. Native discovery
   links under `.agents/skills/` and `.claude/skills/` share `.cursor/skills/`
   content. [Discovery setup and fallback](docs/guides/agent-skill-discovery.md).

## Project Overview

**Revenue Cloud Base Foundations** automates creation and configuration of
Salesforce environments for Revenue Lifecycle Management (RLM). **`main` is now the
Release 264 (Winter '27, API v68.0) line**, promoted from the `264` branch (the two
are in sync). The `262` branch carries any remaining Release 262 (Summer '26, v67.0)
patches through 262 GA; `release/262` and `release/260` are frozen references.

264 is pre-GA — no release notes or v68.0 Metadata Coverage Report yet — so **a
live 264 org is ground truth, not documentation**. The dev hub is on API 68.0, so
every scratch org it creates is a 264 org, and `main` (the 264 line) builds against
it. Distinguish a *fresh* 264 org from a 262 org *upgraded* to 264: an upgrade
grandfathers settings and schema, so it is not evidence about fresh builds.

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

`cumulusci.yml` defines tasks/flows/flags; `tasks/` implements Python CCI tasks.
`force-app/` holds core metadata (step 5); `unpackaged/pre/` precedes it and
`unpackaged/post_*/` holds feature bundles. `templates/` is the UX source
(step 29); `unpackaged/post_ux/` is generated output.

Data lives under `datasets/`; utility scripts under `scripts/`; offline tests
under `tests/`; Robot suites under `robot/rlm-base/`. `datasets/bre/` and
`datasets/dx/` are runtime extraction output, not tracked source. See the
[repository map](docs/references/repository-layout.md), [org definitions](orgs/README.md),
[TFID guide](orgs/tfid/README.md), and **Script Reference** below for detail.

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

Historical Bugs 1/2/3/5 and their fixed versions are documented in
`.cursor/skills/sfdmu-data-plans/SKILL.md` → **v5 Bugs**.

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

Before opening or updating a PR, **run `python scripts/ai/pr_gate.py --base origin/264` first**.
Every selected check gates; missing dependencies fail rather
than skip. Inspect every result, including skips. Run locally even though CI
runs the same gate. Detailed procedures, generator behavior and enforcement
history: [.cursor/skills/audit-review/merge-and-review-procedures.md](.cursor/skills/audit-review/merge-and-review-procedures.md).

### Required CI check

`Mechanical checks` from the GitHub Actions app is required on `main`, `264`
and `release/*`. Running or missing checks block landing. Do not path-filter
away the workflow, rename the published job, or introduce another job with
that same name. Skip directives in commit messages leave the required check
pending; even quoting one can suppress workflows. Name the directives without
writing their literal syntax in commit messages. An admin bypass is a deliberate
decision to record, not a workaround.

### SFDMU data plans (`datasets/sfdmu/**`, `export.json`, CSVs)

1. Run `python scripts/validate_sfdmu_v5_datasets.py`: expect **0 Critical,
   0 High**. Treat any such finding as new.
2. Keep `externalId` delimiters and CSV `$$` columns aligned with the SFDMU
   rules above; destructive operation changes require explicit approval.
3. Every tracked plan needs a README. Update it when behavior or objects change,
   including object tables, operations, externalIds and record counts. Run
   `python scripts/ai/check_plan_readme_consistency.py --strict <plan_dir>`
   (omit the directory for repo-wide validation): require **0 errors, 0 warnings**.
   Regenerate marked tables with `python scripts/ai/generate_plan_readme.py <plan_dir>`
   after changes rather than editing generated rows; preserve handwritten narrative.

### `cumulusci.yml` and CCI tasks

1. After task/flow/option edits, run `python scripts/ai/generate_cci_reference.py`
   and commit the regenerated references.
2. After inserting or removing flow steps, run `python tests/test_doc_build_steps.py`
   to catch shifted documentation citations.
3. After renaming a task or changing its description, search `README.md` and
   `docs/` for the old name and repair stale references.
4. For Python tasks, follow `.cursor/skills/cci-orchestration/custom-task-authoring.md`;
   use `username` for CLI calls, never `access_token`.

### Documentation consistency

Follow `.cursor/skills/doc-consistency/SKILL.md` and its change-surface map.
Update task names, feature flags, plan READMEs, generated references and skill
indexes in the same change as their source.

### Merges and unintended diffs

1. Before merging, run `python scripts/ai/check_branch_scope.py --pr <n>`.
   Rebuild a `FOREIGN` branch from the base; do not revert on top of it.
   A `STACKED` branch must not merge before its parent. Pass `--pr` for both
   signals; see `.cursor/skills/audit-review/SKILL.md` → **Step −1**.
2. Before push, inspect the diff/stat against the intended base (`origin/264`
   for this line). Watch `orgs/`, `datasets/`, `unpackaged/post_ux/` and scratch
   data for unrelated changes inherited from another branch.
3. Changes under `unpackaged/post_ux/` must come from `assemble_and_deploy_ux`
   or the UX drift flows, never manual XML edits; see
   `.cursor/skills/repo-integration/ux-assembly-retrieve.md`.

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

Read [`REVIEW.md`](REVIEW.md) for review standards, severity and push discipline.
**Every agent, every PR: handle every comment to completion and finish every
review round with zero unresolved threads.**

1. Verify each finding against source; classify it **real**, **partial**, or
   **false positive**. Refute false positives with evidence instead of changing
   correct code.
2. For a real finding, fix **every instance of its class** across the change.
3. Batch the whole round, verify locally, then **push once**; do not push while
   a review is running against the previous head.
4. Reply to each thread with the resolution and **commit SHA**, or an
   evidence-backed refutation. React 👍 to valid findings, then resolve threads
   once addressed. False positives still need replies and resolution.
5. Verify zero unresolved threads across **all pages**, not just the first 100.

Use `python scripts/ai/pr_review.py`: `status <pr>` lists paginated threads;
`handle <pr> --comment <id> --body "…"` replies, reacts and resolves;
`verify <pr>` fails if any remain. Use `--no-react` when refuting a false
positive and `--repo owner/name` to override the current repo. The
`/pr-review <pr>` Claude command drives the same workflow. Verification and
class sweeps remain the agent's job. Manual REST/GraphQL commands and pagination:
[review procedures](.cursor/skills/audit-review/merge-and-review-procedures.md#responding-to-automated-pr-reviews).

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
| Create renewal-ready assets across the 4 expiry windows + layer lifecycle event history (Renewal/Upsell/Downsell) | `.cursor/skills/renewal-asset-creation/SKILL.md` |
| Prep a clone as a DF Hands-On workshop org (capture/replay seeded quotes+config, verify before templating) | `.cursor/skills/df-workshop-setup/SKILL.md` |
| Validate / refresh / certify the ERD against orgs and Core source | `.cursor/skills/schema-validation/SKILL.md` |
| Consume PMOS content from Foundations (or vice versa) via cross-repo skill manifest | `.cursor/skills/pmos-integration/SKILL.md` |
| Use Revenue Cloud REST APIs | `.cursor/skills/rlm-business-apis/SKILL.md` |
| Build/verify a multi-year group **ramp** quote (place→EditGroup→clone) + per-segment/compound uplift | `.cursor/skills/ramped-quotes/SKILL.md` |
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
| `scripts/renewal_assets/*` — renewal-asset expiry-bucket spread (`build_renewal_buckets.py`, reuses `build_quote_to_asset.py`) + lifecycle event-history augment/reset Apex | `renewal-asset-creation/SKILL.md` |
| `scripts/df_workshop/*` — capture (`extract_workshop_quotes.py`) and replay (`insert_workshop_quotes.py`) DF workshop org drift | `df-workshop-setup/SKILL.md` |
| `scripts/ai/query_erd.py` — query the RLM data model offline | `revenue-cloud-data-model/SKILL.md` |
| `scripts/ai/check_help_corpus_text_artifacts.py` — non-gating spot-check for glued-link text artifacts in the Help snapshot | `revenue-cloud-docs/SKILL.md` |
| `scripts/ai/skill_manifest.py` — cross-repo skill manifest resolver | `pmos-integration/SKILL.md` |
| `scripts/ai/pr_review.py` — automated-PR-review helper | **Responding to Automated PR Reviews**, above |
| `scripts/ai/check_branch_scope.py` — fail a branch carrying commits it does not own (already upstream, or another open PR's) | `audit-review/SKILL.md` → **Step −1** |
| `scripts/ai/pr_gate.py` — run the mechanical checks a change needs and report the status of every one (incl. skipped) | **Pre-merge checklists**, above |
| `scripts/ai/generate_cci_reference.py`, `scripts/ai/check_plan_readme_consistency.py`, `scripts/ai/generate_plan_readme.py`, `scripts/validate_sfdmu_v5_datasets.py` | **Pre-merge checklists**, above |

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
