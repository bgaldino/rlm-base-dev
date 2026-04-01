# CumulusCI Orchestration Skill

Use this skill when working with CumulusCI (CCI) — the automation engine for
this Salesforce project. It covers general CCI concepts, CLI usage, and this
project's specific configuration.

---

## What is CumulusCI?

CumulusCI is a Python-based automation framework for Salesforce projects. It
provides:

- **Tasks** — single units of work (deploy metadata, load data, run Apex, etc.)
- **Flows** — ordered sequences of tasks and sub-flows
- **Orgs** — named org configurations (scratch orgs, sandboxes, persistent)
- **Feature flags** — boolean settings that gate task/flow execution via `when:`
  clauses

Configuration lives in `cumulusci.yml` at the project root.

---

## CLI Quick Reference

### Task commands

```bash
cci task list                           # list all tasks, grouped
cci task info <task_name>               # show task description, options, class
cci task run <task_name> --org <alias>   # run a single task against an org
cci task run <task_name> -o key value   # pass an option override
```

### Flow commands

```bash
cci flow list                           # list all flows, grouped
cci flow info <flow_name>               # show flow steps and conditions
cci flow run <flow_name> --org <alias>  # run a flow against an org
```

### Org commands

```bash
cci org list                            # list all configured orgs
cci org info <alias>                    # show org details (username, instance)
cci org scratch <config> <alias>        # create a scratch org
cci org connect <alias>                 # connect to a persistent org (sandbox/prod)
cci org default <alias>                 # set the default org
cci org scratch_delete <alias>          # delete a scratch org
cci org browser <alias>                 # open org in browser
```

### Useful flags

```bash
--org <alias>           # target org (overrides default)
-o <key> <value>        # override a task/flow option
--debug                 # verbose CCI debug logging
--no-prompt             # skip confirmation prompts
```

---

## Project Configuration (`cumulusci.yml`)

This project's `cumulusci.yml` (~3000 lines) is organized into these sections:

### 1. Scratch Org Definitions (`orgs.scratch`)

17 scratch org configs, each referencing a JSON definition in `orgs/`. Key orgs:
- `beta` — general-purpose development
- `dev-sb0` — sandbox-like development
- `tfid-*` — Trialforce-based orgs for various configurations
- `dev_preview` / `dev_previous` — API version testing

### 2. Project Settings (`project`)

```yaml
project:
  name: rlm-base
  package:
    name: rlm-base
    api_version: "66.0"    # Spring '26
  source_format: sfdx
```

### 3. Feature Flags (`project.custom`)

36 boolean flags control which features are deployed. Common flags:

| Flag | Default | Purpose |
|------|---------|---------|
| `qb` | `true` | Include QuantumBit product data |
| `tso` | `false` | Trialforce Source Org mode |
| `billing` | `true` | Enable billing features |
| `rating` | `true` | Insert rating design-time data |
| `rates` | `true` | Insert rate cards |
| `ux` | `true` | Assemble/deploy dynamic UX |
| `dro` | `true` | Dynamic Revenue Orchestration |
| `constraints` | `true` | Constraint Builder |
| `prm` | `true` | Partner Relationship Management |
| `docgen` | `true` | Document Generation |

Flags are referenced in flow `when:` clauses:
```yaml
when: project_config.project__custom__billing
```

Compound conditions are supported:
```yaml
when: project_config.project__custom__billing and not project_config.project__custom__refresh
when: org_config.scratch and not project_config.project__custom__tso
```

> For the complete list of flags, defaults, and every `when:` clause referencing
> them, load `feature-flags.md` in this skill directory.

### 4. YAML Anchors (`project.custom`)

The file uses YAML anchors (`&name`) extensively for:
- **Permission set lists** (`&rlm_psl_api_names`, `&rlm_psg_api_names`, etc.)
- **Decision table lists** (`&dt_rating_decision_tables`, etc.)
- **Context definition settings** (`&sales_transaction_context_name`, etc.)
- **Dataset paths** (`&quantumbit_product_dataset`, etc.)
- **Sleep durations** (`&sleep_default`)

These anchors are referenced with `*name` in task/flow options.

### 5. Tasks (`tasks`)

~115 custom task definitions using this naming convention:
- `insert_qb_{plan}_data` / `insert_quantumbit_{plan}_data` — load a data plan
- `delete_qb_{plan}_data` / `delete_quantumbit_{plan}_data` — delete plan data
- `extract_qb_{plan}_data` — extract from org to CSV
- `test_qb_{plan}_idempotency` — idempotency test
- `activate_{thing}` — run Apex activation script
- `deploy_*` — deploy metadata bundles
- `refresh_dt_*` — refresh decision tables
- `manage_*` — comprehensive management tasks (list, query, activate, etc.)

Every task must have a `group` and `description`. The `class_path` points to
either a built-in CCI class or a custom class in `tasks/`.

> For the complete task listing by group with descriptions and options, load
> `tasks-reference.md` in this skill directory.

### 6. Flows (`flows`)

34 flows organized as a hierarchy. The main entry point is `prepare_rlm_org`
(31 steps), which calls sub-flows:

```
prepare_rlm_org
├── 1. prepare_core (PSLs, PSGs, context defs, deploy_pre)
├── 2. prepare_decision_tables
├── 3. prepare_expression_sets
├── 4. prepare_payments
├── 5. deploy_full (force-app/main/default)
├── 6. prepare_price_adjustment_schedules
├── 7. prepare_scratch (scratch-only data)
├── 8. prepare_payments (re-run)
├── 9. prepare_quantumbit (utils, approvals, QB metadata)
├── 10. prepare_product_data (PCM, Q3, product images)
├── 11. prepare_pricing_data (pricing delete + insert)
├── 12. prepare_docgen
├── 13. prepare_dro
├── 14. prepare_tax
├── 15. prepare_billing
├── 16. prepare_analytics
├── 17. prepare_clm
├── 18. prepare_rating (delete, insert, activate for rating+rates)
├── 19. activate_and_deploy_expression_sets
├── 20. prepare_tso (TSO-specific PSLs, PSGs, deploy)
├── 21. prepare_procedureplans
├── 22. prepare_prm
├── 23. prepare_agents
├── 24. prepare_constraints
├── 25. prepare_guidedselling
├── 26. prepare_revenue_settings
├── 27. prepare_pricing_discovery
├── 28. prepare_ramp_builder
├── 29. prepare_ux (when: ux=true)
├── 30. refresh_all_decision_tables
└── 31. stamp_git_commit
```

> For the complete flow listing with all steps and `when:` conditions, load
> `flows-reference.md` in this skill directory.

---

## `when:` Clause Reference

CCI evaluates `when:` as a Python expression at runtime. Available variables:

| Variable | Type | Description |
|----------|------|-------------|
| `project_config.project__custom__<flag>` | varies | Feature flag from `project.custom` |
| `org_config.scratch` | bool | `True` if the target org is a scratch org |

Operators: `and`, `or`, `not`, parentheses for grouping.

Examples:
```yaml
when: project_config.project__custom__billing
when: project_config.project__custom__dro and project_config.project__custom__qb
when: org_config.scratch and not project_config.project__custom__tso
when: "project_config.project__custom__quantumbit or project_config.project__custom__tso"
when: "not (project_config.project__custom__quantumbit or project_config.project__custom__tso)"
```

---

## Custom Task Classes (`tasks/`)

This project has 32 Python files in `tasks/` defining 38+ custom CCI task
classes. They fall into these categories:

| Category | Classes | Base Class |
|----------|---------|------------|
| SFDMU data ops | `LoadSFDMUData`, `ExtractSFDMUData`, `DeleteSFDMUData`, `TestSFDMUIdempotency` | `SFDXBaseTask` |
| REST/Connect API | `RefreshDecisionTable`, `ExtendStandardContext`, `ManageContextDefinition`, `ManageDecisionTables`, `ManageExpressionSets`, `ManageFlows`, `ManageTransactionProcessingTypes` | `SFDXBaseTask` / `BaseTask` |
| Metadata deploy | `AssembleAndDeployUX`, `StampGitCommit`, `CleanupSettingsForDev`, `FixDocumentTemplateBinaries` | `SFDXBaseTask` |
| Robot Framework | `RunE2ETests`, `ReorderAppLauncher`, `EnableAnalyticsReplication`, `ConfigureRevenueSettings`, `EnableDocumentBuilderToggle`, `EnableConstraintsSettings` | `BaseTask` |
| Local-only (no org) | `ValidateSetup` | `BaseTask` |
| Community/PRM | `PatchNetworkEmailForDeploy`, `RevertNetworkEmailAfterDeploy`, `PatchPaymentsSiteForDeploy`, `RevertPaymentsSiteAfterDeploy` | varies |
| CML (Constraints) | `ExportCML`, `ImportCML`, `ValidateCML` | `SFDXBaseTask` |

> For detailed task authoring guidance (base class selection, option patterns,
> `_run_task` conventions), load `custom-task-authoring.md` in this skill directory.

---

## Self-Updating Reference Files

Three files in this directory are **auto-generated** from `cumulusci.yml`:

- `tasks-reference.md` — all tasks by group
- `flows-reference.md` — all flows with step trees
- `feature-flags.md` — feature flags with usage index

**To regenerate after editing `cumulusci.yml`:**

```bash
python scripts/ai/generate_cci_reference.py
```

Subset generation:
```bash
python scripts/ai/generate_cci_reference.py --tasks-only
python scripts/ai/generate_cci_reference.py --flows-only
python scripts/ai/generate_cci_reference.py --flags-only
python scripts/ai/generate_cci_reference.py --dry-run
```

---

## Common Workflows

```bash
# Full org setup
cci flow run prepare_rlm_org --org beta

# Run a single data plan
cci task run insert_quantumbit_pricing_data --org beta

# Delete before re-load
cci task run delete_quantumbit_pricing_data --org beta

# Extract data from an org
cci task run extract_qb_pricing_data --org beta

# Idempotency test
cci task run test_qb_pricing_idempotency --org beta

# Activate records
cci task run activate_rating_records --org beta

# Deploy and assemble UX
cci task run assemble_and_deploy_ux --org dev-sb0

# UX dry-run (assemble only, no deploy)
cci task run assemble_and_deploy_ux -o deploy false --org dev-sb0

# Stamp git commit
cci task run stamp_git_commit --org beta

# Validate local setup (no org needed)
cci task run validate_setup

# Task info
cci task info insert_quantumbit_pricing_data

# Flow info
cci flow info prepare_rlm_org
```

---

## Related Skills and Rules

- **SFDMU Data Plans** — `../.cursor/skills/sfdmu-data-plans/SKILL.md`
- **Revenue Cloud Data Model** — `../.cursor/skills/revenue-cloud-data-model/SKILL.md`
- **CCI Task Definitions Rule** — `../.cursor/rules/cci-task-definitions.mdc` (triggers on `cumulusci.yml`)
- **CCI Python Tasks Rule** — `../.cursor/rules/cci-python-tasks.mdc` (triggers on `tasks/**/*.py`)
