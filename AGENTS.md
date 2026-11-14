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
Salesforce environments for Revenue Lifecycle Management (RLM).

**Branches are named by role, never by release number.** `main` is the current line
and the base for every PR except next-release work (`preview/<n>`) and patches to an
earlier line (`release/<n>`). Which release each one carries is recorded in
[README → Branch Information](README.md#branch-information), and the active release and API
version in `.claude/skill-manifest.yml` (`salesforce_release_active`, `api_version_active`). Don't restate them in other instructions.

While a release is pre-GA its Help docs can still change, so **a live org of that
release is ground truth, not documentation**. Scratch orgs take the dev hub's
release. Distinguish a *fresh* org from one *upgraded* from the prior release: an
upgrade grandfathers settings and schema, so it is not evidence about fresh builds.

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
(step 30); `unpackaged/post_ux/` is generated output.

Paths: `datasets/`, `scripts/`, `tests/`, `robot/rlm-base/`. `datasets/bre/` and
`datasets/dx/` are untracked runtime output. See the [repository map](docs/references/repository-layout.md),
[org definitions](orgs/README.md), [TFID guide](orgs/tfid/README.md), and **Script Reference**.

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
8. **DO NOT** commit or push directly to `main`, a `preview/*` or a `release/*`
   branch — all changes go through a feature branch and a pull request. This
   applies to docs and agent-instruction files, not just code. Never force-push
   any of them without explicit user approval: PRs are routinely stacked on them,
   so rewriting one invalidates every one of them.
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

### v5 Bugs — only Bug 4 is live on the 5.6.4 floor

On 5.6.4+, Upsert works: **do not** introduce `operation: Insert` + `deleteOldData: true`
citing the fixed Bugs 1/2/3/5. Plans still carrying that pattern migrate only through the
gated `sfdmu-v5-optimization` initiative (live verification + per-operation approval).

**Bug 4 (still present, 5.8.0):** a `$$` lookup column (e.g. `Pricebook2.$$Name$IsStandard`)
resolves only when its parts are exactly the parent's `externalId` in the same pass;
self-references and differently keyed parents fail. **Fix:** a single-field reference
(`ParentGroup.Code`), or key the parent on those parts. `scripts/ai/check_sfdmu_layering.py`
flags it. History and fixed versions: `.cursor/skills/sfdmu-data-plans/SKILL.md` → **v5 Bugs**.

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
cci task run delete_quantumbit_pricing_data --org beta     # manual full teardown; prepare_pricing_data reloads in place
cci task run extract_qb_pricing_data --org beta
cci task run test_qb_pricing_idempotency --org beta
cci flow run prepare_rlm_org --org beta
cci task run assemble_and_deploy_ux --org beta
cci task run assemble_and_deploy_ux -o deploy false                 # dry-run: local assembly only, no org needed
python scripts/ux/ux_tool.py capture-drift --target-org <sf_alias>   # retrieve + diff
python scripts/ux/ux_tool.py apply-drift                            # writeback + verify + reassemble
python scripts/ux/ux_tool.py writeback                              # dry-run writeback
cci task run validate_setup                                          # no org needed
cci task run check_decision_table_freshness --org beta               # readiness: is any lookup stale? (-o param1 strict to fail the build)
python scripts/validate_sfdmu_v5_datasets.py
python scripts/ai/generate_cci_reference.py                         # after cumulusci.yml edits
```

---

## Pre-merge checklists for AI agents

Before opening or updating a PR, **run `python scripts/ai/pr_gate.py --base origin/<base>` first**
(`<base>`: `main`, or the `preview/*`/`release/*` branch it targets).
Every selected check gates; missing dependencies fail rather
than skip. Inspect every result, including skips. Run locally even though CI
runs the same gate. Detailed procedures, generator behavior and enforcement
history: [.cursor/skills/audit-review/merge-and-review-procedures.md](.cursor/skills/audit-review/merge-and-review-procedures.md).

### Required CI check

`Mechanical checks` from the GitHub Actions app is required on `main`, `preview/*`
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
2. Before push, inspect the diff/stat against the PR's base (`origin/main` unless
   the PR targets a `preview/*` or `release/*` branch). Watch `orgs/`, `datasets/`, `unpackaged/post_ux/` and scratch
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
   Only then request the next review.

Use `python scripts/ai/pr_review.py` (`status` / `handle` / `verify`) or the `/pr-review <pr>`
command; options, manual REST/GraphQL and pagination are in the
[review procedures](.cursor/skills/audit-review/merge-and-review-procedures.md#responding-to-automated-pr-reviews).
Verification and class sweeps remain the agent's job.

---

## AI Agent Skill Index

Skills are plain-markdown guides, one `SKILL.md` per directory under `.cursor/skills/`, readable by any agent.
**Pick one by task in the router, [`.cursor/skills/README.md`](.cursor/skills/README.md)**
("I need to…" → skill), or by its `description`; read it before using its tools. Every
top-level skill, by area:

- **Knowledge and APIs:** `revenue-cloud-data-model`, `rlm-business-apis`, `revenue-cloud-docs`, `salesforce-contracts`
- **Configuration and pricing:** `product-catalog-modeling`, `constraint-models`, `pricing-setup`, `pricing-procedures`, `pricing-wiring`, `expression-sets`, `decision-tables`, `context-service`
- **Transactions, usage and documents:** `advanced-approvals`, `transaction-line-editor`,
  `quote-negotiation-rounds`, `ramped-quotes`, `asset-lifecycle-changes`, `billing-setup`,
  `renewal-asset-creation`, `usage-consumption`, `rate-management`, `txn-data-harness`, `dro-plans`,
  `document-generation`, `odt-authoring`
- **Builds, data and environment:** `cci-orchestration` (Python tasks: `cci-orchestration/custom-task-authoring.md`), `sfdmu-data-plans`, `repo-integration` (UX drift: `repo-integration/ux-assembly-retrieve.md`), `build-harness`, `pde-org-build`, `toolchain` (containerized: `docker/README.md`), `mcp-integration`, `schema-validation`, `robot-testing`, `troubleshooting`, `apex-security-hardening`
- **Demos and enablement:** `qb-demo-script`, `release-enablement`, `df-workshop-setup`, `inapp-framework`
- **Repository maintenance:** `audit-review`, `doc-consistency`, `skill-authoring`
- **Maintainer integrations:** `todo-tracker`, `pmos-integration`

Each skill has **Quick Rules**; new ones also need **DO NOT**, **Entry Conditions**,
**Examples** and **Validation Checks**, and register in this list and the router (plus
the manifest when cross-repo discovery applies; see `skill-authoring`). Sub-files are listed only in their parent `SKILL.md`.

### Script Reference

Helper scripts are documented, with options and examples, in the skill that owns them.
Read it rather than guessing flags:

| Scripts | Owning skill |
|---------|--------------|
| `scripts/docgen/*` (install its `requirements.txt` first) | `document-generation` |
| `scripts/erd/*` | `schema-validation` |
| `scripts/context_service/*` | `context-service` |
| `scripts/expression_sets/*` | `expression-sets` |
| `tasks/rlm_cml.py` | `constraint-models` |
| `scripts/ux/*` | `repo-integration` |
| `scripts/renewal_assets/*` | `renewal-asset-creation` |
| `scripts/df_workshop/*` | `df-workshop-setup` |
| `scripts/ai/query_erd.py` | `revenue-cloud-data-model` |
| `scripts/doc_snapshot/*` | `revenue-cloud-docs` |
| `scripts/ai/skill_manifest.py` | `pmos-integration` |
| `scripts/ai/check_branch_scope.py` | `audit-review` → **Step −1** |
| `scripts/ai/pr_review.py` | **Responding to Automated PR Reviews**, above |
| `scripts/ai/pr_gate.py`, `generate_cci_reference.py`, `check_plan_readme_consistency.py`, `generate_plan_readme.py`; `scripts/validate_sfdmu_v5_datasets.py` | **Pre-merge checklists**, above |

Two Context Service rules are worth obeying without a second read (rationale in
the skill): **modifying or deleting** an existing node, attribute, or tag on an
*active* version is blocked (`RECORD_UPDATE_FAILED`) — deactivate first, though
pure *inserts* apply in place. And a runtime `contextId` is **request-scoped** —
an opaque handle that does not survive separate CLI calls, so chaining
create → query → persist needs Apex or a single Flow. Persist is **async**:
confirm via `AsyncOperationTracker`, not the returned `referenceId`.

Every agent obeys `.cursor/rules/analysis-artifacts.mdc`; the rule-to-skill table
is in `.cursor/skills/README.md`.

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
