# AI Agent Instructions — Revenue Cloud Base Foundations

> Canonical instructions for **any** AI coding agent working with this
> repository (Cursor, Claude Code, GitHub Copilot, Codex, Windsurf,
> Aider, or any future tool). Safety-critical rules that apply to every
> task. Detailed guidance lives in skill files (see Skill Index below).

## Project Overview

**Revenue Cloud Base Foundations** automates creation and configuration of
Salesforce environments for Revenue Lifecycle Management (RLM). It targets
Salesforce Release 260 (Spring '26, API v66.0).

Key technology stack:
- **CumulusCI (CCI)** — orchestration engine for tasks and flows
- **SFDMU v5** — data import/export (`sf sfdmu run`). **v5.0.0+ required.**
- **Salesforce DX / `sf` CLI** — metadata deployment and org management
- **Python** — custom CCI task classes in `tasks/`
- **Apex** — post-load activation scripts in `scripts/apex/`

## Repository Layout

```
cumulusci.yml          # Task/flow definitions, feature flags, org defs
force-app/             # Core SFDX metadata (deployed at step 5)
unpackaged/pre/        # Pre-deploy metadata (fields, settings, PSGs, DTs)
unpackaged/post_*/     # Feature-specific metadata bundles
unpackaged/post_ux/    # ⚠ AUTO-GENERATED — never edit directly
templates/             # Source-of-truth for UX assembly (step 27)
datasets/sfdmu/        # SFDMU data plans (export.json + CSVs)
datasets/context_plans/# Context definition plans
scripts/apex/          # Apex activation/deletion scripts
scripts/ai/            # AI agent tooling (query_erd, generate_cci_reference)
tasks/                 # Custom Python CCI task classes
robot/rlm-base/        # Robot Framework tests (setup + E2E)
orgs/                  # Scratch org definition JSON files
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
cci task run assemble_and_deploy_ux --org dev-sb0
cci task run assemble_and_deploy_ux -o deploy false --org dev-sb0   # dry-run
cci flow run capture_ux_drift --org dev-sb0                          # retrieve + diff
cci flow run apply_ux_drift --org dev-sb0                            # writeback + reassemble + verify
cci task run writeback_ux_templates --org dev-sb0                    # dry-run writeback
cci task run validate_setup                                          # no org needed
python scripts/validate_sfdmu_v5_datasets.py
python scripts/ai/generate_cci_reference.py                         # after cumulusci.yml edits
```

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
9. **Edition flags** — `pde`, `trial`, `dev_ed` change PSL/PS assignments
   and feature availability; verify `when:` guards match the target edition

---

## AI Agent Skill Index

Skills are detailed guides for specific tasks. They live in
`.cursor/skills/` but are **plain markdown** — readable by any agent,
not Cursor-specific. Read the skill file when you need guidance on
that topic.

| I need to... | Skill File (relative to repo root) |
|-------------|-------------------------------------|
| Add new features, code placement | `.cursor/skills/repo-integration/SKILL.md` |
| Work with CCI tasks, flows, CLI | `.cursor/skills/cci-orchestration/SKILL.md` |
| Write a Python CCI task class | `.cursor/skills/cci-orchestration/custom-task-authoring.md` |
| Create/modify SFDMU data plans | `.cursor/skills/sfdmu-data-plans/SKILL.md` |
| Understand RLM objects/relationships | `.cursor/skills/revenue-cloud-data-model/SKILL.md` |
| Use Revenue Cloud REST APIs | `.cursor/skills/rlm-business-apis/SKILL.md` |
| Write Robot Framework tests | `.cursor/skills/robot-testing/SKILL.md` |
| Capture/apply UX drift from org | `docs/features/dynamic-ux-assembly.md` |
| Debug a build/deploy failure | `.cursor/skills/troubleshooting/SKILL.md` |

Each skill has a **Quick Rules** section at the top for fast reference,
and a **DO NOT** section listing critical safety constraints for that area.

### Skill Sub-Files (Progressive Disclosure)

Some skills split detail into sub-files to keep entry points small.
Read the sub-file only when you need that specific detail:

| Sub-file | Parent Skill | Contains |
|----------|-------------|----------|
| `repo-integration/new-feature-guide.md` | Repository Integration | Step-by-step code templates for adding a new feature |
| `repo-integration/dependency-ordering.md` | Repository Integration | Metadata/data ordering, `prepare_rlm_org` step map |
| `robot-testing/patterns.md` | Robot Testing | Shadow DOM code, keyword reference, test authoring |
| `cci-orchestration/custom-task-authoring.md` | CCI Orchestration | Python task class patterns and examples |
| `cci-orchestration/tasks-reference.md` | CCI Orchestration | Auto-generated task listing (regenerate after edits) |
| `cci-orchestration/flows-reference.md` | CCI Orchestration | Auto-generated flow listing |
| `cci-orchestration/feature-flags.md` | CCI Orchestration | Auto-generated feature flag index |
| `revenue-cloud-data-model/domains/*.md` | Data Model | Per-domain object/field/relationship details |
| `revenue-cloud-data-model/cross-domain-relationships.md` | Data Model | Cross-domain FK mapping |
| `sfdmu-data-plans/plan-dependency-graph.md` | SFDMU Data Plans | Load/deletion order across plans |
| `sfdmu-data-plans/object-plan-mapping.md` | SFDMU Data Plans | Which objects belong to which plan |

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
| `.cursor/rules/apex-classes.mdc` | `unpackaged/**/*.cls`, `force-app/**/*.cls` | sharing, Id validation, BFS, test patterns |
| `.cursor/rules/lwc-components.mdc` | `unpackaged/**/lwc/**/*.{html,js}` | template syntax, ARIA/a11y, perf, error messages |
| `.cursor/rules/ux-templates.mdc` | `templates/**` | `repo-integration/SKILL.md` |
| `.cursor/rules/robot-tests.mdc` | `robot/**/*.robot` | `robot-testing/SKILL.md` |

### AI Utility Scripts

Scripts in `scripts/ai/` help agents query project data:

```bash
python scripts/ai/query_erd.py describe Product2           # Query RLM data model
python scripts/ai/query_erd.py domain Pricing               # List domain objects
python scripts/ai/generate_cci_reference.py                 # Regenerate CCI docs
```

---

## Documentation Conventions

All `.md` files under `docs/` use **lower-kebab-case** filenames.
Placement: guides → `docs/guides/`, references → `docs/references/`,
analysis → `docs/analysis/`, features → `docs/features/`,
archive → `docs/archive/`, vendor PDFs → `docs/salesforce/`.

---

## Agent Entry Points

This repository provides multiple entry points for different AI tools:

| File | Tool | Purpose |
|------|------|---------|
| `AGENTS.md` | Any agent | Canonical source of truth (this file) |
| `CLAUDE.md` | Claude Code, Cursor | Symlink to `AGENTS.md` |
| `.github/copilot-instructions.md` | GitHub Copilot | Pointer to `AGENTS.md` |

All entry points resolve to the same content. Edit `AGENTS.md` only.
