# Repository Integration Guide

Use this skill when adding new features, code, metadata, data plans, or
capabilities to the rlm-base-dev repository. It covers where files go, what
needs to be wired up, dependency ordering, testing, and validation.

---

## Repository Structure at a Glance

```
rlm-base-dev/
├── cumulusci.yml              # Central orchestration: tasks, flows, feature flags, org defs
├── CLAUDE.md                  # AI workspace context (always-applied rule)
├── .forceignore               # Metadata excluded from sf push/pull/deploy
│
├── force-app/main/default/    # Core SFDX metadata (deployed at step 5 via deploy_full)
│   ├── classes/               #   Apex classes + test classes
│   ├── objects/               #   Custom fields, validation rules (NOT layouts/compactLayouts)
│   ├── permissionsets/        #   Permission sets
│   ├── profiles/              #   Admin profile (classAccesses ONLY — no layoutAssignments)
│   ├── settings/              #   Org settings
│   ├── flows/                 #   Autolaunched flows
│   ├── lwc/                   #   Lightning Web Components
│   ├── expressionSetDefinition/  # Expression sets (pricing, rating procedures)
│   ├── standardValueSets/     #   Picklist standard value sets
│   └── ...                    #   Other standard metadata types
│
├── unpackaged/                # Feature-specific metadata bundles
│   ├── pre/                   #   Deployed BEFORE force-app (step 5 of prepare_core)
│   │   ├── 1_objects/         #     Custom fields needed before main deploy
│   │   ├── 2_settings/        #     Org settings (pricing, billing, etc.)
│   │   ├── 3_permissionsetgroups/  # PSGs
│   │   └── 5_decisiontables/  #     Decision table metadata
│   ├── post_quantumbit/       #   QB-specific metadata (pricingActionParams, etc.)
│   ├── post_billing/          #   Billing metadata
│   ├── post_docgen/           #   DocGen: OmniDataTransforms, DocumentTemplates
│   ├── post_constraints/      #   Constraint Builder metadata
│   ├── post_approvals/        #   Approval flows, fields, quick actions
│   ├── post_agents/           #   Agentforce: bots, genAiFunctions, LWCs, flows
│   ├── post_prm/              #   PRM: network, experience bundle, sharing
│   ├── post_payments/         #   Payments: webhook site, settings
│   ├── post_ramp_builder/     #   Ramp Schedule V4: fields, LWC, flows, Apex
│   ├── post_collections/      #   Collections metadata
│   ├── post_commerce/         #   Commerce decision table flows
│   ├── post_tso/              #   TSO-specific metadata
│   ├── post_utils/            #   Utility flows and metadata
│   ├── post_guidedselling/    #   Guided Selling metadata
│   ├── post_procedureplans/   #   Procedure Plan metadata
│   ├── post_personas/         #   Persona profiles and PSGs (not in main flow)
│   ├── post_ux/               #   ⚠ AUTO-GENERATED — never edit directly
│   └── pre_docgen/            #   DocGen ODT seed records
│
├── templates/                 # Source-of-truth for dynamic UX assembly
│   ├── flexipages/            #   base/, standalone/{feature}/, patches/{feature}/
│   ├── layouts/               #   base/, billing/, constraints/
│   ├── applications/          #   App definitions + patches/{feature}/
│   ├── appMenus/base/         #   AppSwitcher.appMenu-meta.xml
│   ├── profiles/              #   base/ (full Admin, PRM), patches/{feature}/
│   └── objects/               #   base/, billing/, collections/ (compactLayouts, listViews)
│
├── datasets/
│   ├── sfdmu/                 # SFDMU data plans (export.json + CSVs)
│   │   ├── qb/en-US/          #   QuantumBit plans: qb-pcm, qb-pricing, qb-billing, etc.
│   │   ├── q3/en-US/          #   Q3 plans
│   │   ├── mfg/en-US/         #   Manufacturing plans
│   │   ├── scratch_data/      #   Scratch org seed data
│   │   └── procedure-plans/   #   Procedure plan sections + options
│   ├── context_plans/         # Context definition plan JSONs
│   └── constraints/           # CML constraint model data
│
├── scripts/
│   ├── apex/                  # Anonymous Apex scripts (activation, deletion, setup)
│   ├── post_process_extraction.py
│   ├── validate_sfdmu_v5_datasets.py
│   ├── ai/                    # AI agent tooling scripts
│   │   ├── query_erd.py       #   CLI data model queries against erd-data.json
│   │   └── generate_cci_reference.py  # Auto-generate CCI skill references
│   └── sync_appmenu_from_user.py
│
├── tasks/                     # Custom Python CCI task classes
│   ├── rlm_sfdmu.py           #   SFDMU load/extract/delete/idempotency
│   ├── rlm_ux_assembly.py     #   Dynamic UX assembly
│   ├── rlm_stamp_commit.py    #   Git commit stamping
│   └── ...                    #   ~30 other task modules
│
├── robot/rlm-base/
│   ├── tests/e2e/             # E2E Robot Framework tests
│   ├── tests/setup/           # Setup automation (revenue settings, analytics, etc.)
│   └── results/               # Test output (gitignored)
│
├── orgs/                      # Scratch org definition JSON files
├── docs/                      # Documentation (guides, references, features, ERDs)
└── .cursor/
    ├── rules/                 # File-specific Cursor rules (.mdc)
    └── skills/                # Progressive-disclosure AI skills
```

---

## Decision Tree: Where Does My Code Go?

### New metadata (Apex, LWC, fields, settings)

```
Is it foundational (needed by most features)?
  YES → force-app/main/default/<type>/
  NO  → Is it feature-specific?
    YES → unpackaged/post_<feature>/
    NO  → Ask: should it deploy before or after force-app?
      BEFORE → unpackaged/pre/<subdirectory>/
      AFTER  → unpackaged/post_<feature>/
```

**Key rule:** `force-app/` is deployed as a single bundle at step 5
(`deploy_full`). Feature bundles under `unpackaged/post_*/` are deployed
at specific flow steps, allowing dependency ordering.

### New UX metadata (flexipages, layouts, profiles, apps, compact layouts)

```
Is it a flexipage?
  New complete override for a feature → templates/flexipages/standalone/<feature>/
  Additive change to existing page    → templates/flexipages/patches/<feature>/
  Base page (no feature gate)         → templates/flexipages/base/

Is it a layout?
  Base layout     → templates/layouts/base/
  Feature layout  → templates/layouts/<feature>/

Is it compact layout or list view?
  → templates/objects/<feature>/

Is it an app definition or actionOverride patch?
  App variant    → templates/applications/
  Action patch   → templates/applications/patches/<feature>/

Is it a profile change?
  Full profile   → templates/profiles/base/
  Feature patch  → templates/profiles/patches/<feature>/
```

**Never edit `unpackaged/post_ux/`** — it's fully regenerated by
`assemble_and_deploy_ux`. **Never add layoutAssignments or
applicationVisibilities to `force-app/` profiles** — they belong in templates.

### New data plan (SFDMU)

```
datasets/sfdmu/qb/en-US/qb-<plan_name>/
├── export.json    # SFDMU configuration (objects, externalIds, operations)
├── <Object1>.csv  # Data records
├── <Object2>.csv
└── README.md      # Plan documentation (optional but recommended)
```

### New Apex script

```
scripts/apex/<scriptName>.apex
```

### New Python task class

```
tasks/rlm_<module_name>.py
```

### New Robot Framework test

```
E2E test     → robot/rlm-base/tests/e2e/<test_name>.robot
Setup task   → robot/rlm-base/tests/setup/<task_name>.robot
```

### New context definition plan

```
datasets/context_plans/<PlanName>/manifest.json
```

### New constraint model data

```
datasets/constraints/qb/<ModelName>/
```

---

## Adding a New Feature: Complete Checklist

### 1. Feature flag

Add a boolean flag under `project.custom` in `cumulusci.yml`:

```yaml
project:
  custom:
    myfeature: true    # Enable my feature
```

### 2. Metadata

Place metadata in the appropriate directory (see decision tree above).
If creating a new `unpackaged/post_<feature>/` bundle, create a deploy task:

```yaml
tasks:
  deploy_post_myfeature:
    description: Deploy My Feature Metadata
    class_path: cumulusci.tasks.salesforce.Deploy
    group: Revenue Lifecycle Management
    options:
      path: unpackaged/post_myfeature
```

### 3. Data plan (if needed)

Create `datasets/sfdmu/qb/en-US/qb-myfeature/`:
- `export.json` with objects, externalIds, operations
- CSV files for each object

Register CCI tasks:

```yaml
tasks:
  insert_qb_myfeature_data:
    group: Revenue Lifecycle Management
    description: Insert My Feature Data
    class_path: tasks.rlm_sfdmu.LoadSFDMUData
    options:
      pathtoexportjson: *myfeature_dataset

  # Optional: deletion task (Apex or DeleteSFDMUData)
  delete_qb_myfeature_data:
    group: Data Maintenance
    description: Delete My Feature data in dependency order
    class_path: cumulusci.tasks.apex.anon.AnonymousApexTask
    options:
      path: scripts/apex/deleteMyFeatureData.apex

  # Optional: extraction task
  extract_qb_myfeature_data:
    group: Data Management - Extract
    description: "Extract qb-myfeature from org to CSV."
    class_path: tasks.rlm_sfdmu.ExtractSFDMUData
    options:
      pathtoexportjson: *myfeature_dataset

  # Optional: idempotency test
  test_qb_myfeature_idempotency:
    group: Data Management - Idempotency
    description: Idempotency test for qb-myfeature.
    class_path: tasks.rlm_sfdmu.TestSFDMUIdempotency
    options:
      pathtoexportjson: *myfeature_dataset
      use_extraction_roundtrip: false
```

Add a dataset path anchor:

```yaml
project:
  custom:
    myfeature_dataset: &myfeature_dataset "datasets/sfdmu/qb/en-US/qb-myfeature"
```

### 4. Permission sets (if needed)

Define a PS anchor and add an assign task in the flow:

```yaml
project:
  custom:
    ps_myfeature: &ps_myfeature
      - RLM_MyFeature

# In the flow:
    task: assign_permission_sets
    when: project_config.project__custom__myfeature
    options:
      api_names: *ps_myfeature
```

### 5. Context definition changes (if needed)

Create a context plan in `datasets/context_plans/MyFeature/manifest.json`
and register a task:

```yaml
tasks:
  apply_context_myfeature:
    group: Revenue Lifecycle Management
    description: Apply MyFeature context attributes
    class_path: tasks.rlm_context_service.ManageContextDefinition
    options:
      developer_name: RLM_SalesTransactionContext
      plan_file: datasets/context_plans/MyFeature/manifest.json
      translate_plan: true
      activate: true
```

### 6. Flow (sub-flow)

Create a `prepare_myfeature` flow that orchestrates all steps:

```yaml
flows:
  prepare_myfeature:
    group: Revenue Lifecycle Management
    description: >
      Deploy and configure My Feature: metadata, data, permissions,
      context definitions.
    steps:
      1:
        task: deploy_post_myfeature
        when: project_config.project__custom__myfeature
      2:
        task: insert_qb_myfeature_data
        when: project_config.project__custom__myfeature and project_config.project__custom__qb
      3:
        task: apply_context_myfeature
        when: project_config.project__custom__myfeature
      4:
        task: assign_permission_sets
        when: project_config.project__custom__myfeature
        options:
          api_names: *ps_myfeature
```

### 7. Wire into `prepare_rlm_org`

Add the sub-flow as a step in the main flow. Choose the step number based
on dependency ordering:

```yaml
flows:
  prepare_rlm_org:
    steps:
      # ... existing steps ...
      XX:
        flow: prepare_myfeature
```

**Ordering rules:**
- PSLs/PSGs → before metadata deploy
- Metadata deploy → before data loading
- Products (PCM) → before pricing/billing/tax/rating
- Rating → before rates (FK dependency)
- UX assembly (step 29) → near end, after all referenced components exist
- `stamp_git_commit` (step 31) → always last

### 8. UX changes (if needed)

Add flexipages/layouts to the appropriate `templates/` directory. The
assembler picks them up automatically based on the feature flag.

For a new standalone flexipage:
```
templates/flexipages/standalone/myfeature/RLM_MyObject_Record_Page.flexipage-meta.xml
```

For a layout:
```
templates/layouts/myfeature/MyObject-RLM MyObject Layout.layout-meta.xml
```

For a profile patch:
```
templates/profiles/patches/myfeature/Admin.profile.patch.xml
```

### 9. Regenerate CCI references

```bash
python scripts/ai/generate_cci_reference.py
```

### 10. `.forceignore` updates (if needed)

If UX metadata for the feature was moved from `force-app/` or
`unpackaged/post_*/` to `templates/`, add `.forceignore` entries to
prevent the old paths from being picked up:

```
# MyFeature UX metadata — deployed via prepare_ux
unpackaged/post_myfeature/flexipages
```

---

## Adding a Custom Python Task

### 1. Create the module

```
tasks/rlm_myfeature.py
```

Use `BaseTask` for most tasks. See the CCI Python Tasks rule
(`.cursor/rules/cci-python-tasks.mdc`) and the custom task authoring guide
(`.cursor/skills/cci-orchestration/custom-task-authoring.md`).

### 2. Register in `cumulusci.yml`

```yaml
tasks:
  my_task:
    group: Revenue Lifecycle Management
    description: >
      Specific description of what this task does and which objects/APIs
      it affects.
    class_path: tasks.rlm_myfeature.MyTask
    options:
      operation: list
```

### 3. Wire into a flow (if needed)

Add the task to an existing or new flow with appropriate `when:` gating.

---

## Dependency Ordering Rules

### Metadata dependencies

| Depends On | Must Deploy First | Reason |
|-----------|-------------------|--------|
| Custom fields | `unpackaged/pre/` or `force-app` | Referenced by flows, LWC, Apex |
| Expression sets | `force-app/expressionSetDefinition/` | Referenced by pricing/rating procedures |
| Decision tables | `unpackaged/pre/5_decisiontables/` | Referenced by pricing/rating flows |
| Permission sets | `force-app/permissionsets/` | Must exist before assignment |
| Context definitions | Extended at runtime | Created by `extend_context_*` tasks |
| Apex classes | Same bundle or `force-app/classes/` | Referenced by GenAI functions, LWC |

### Data dependencies

| Load Order | Plan | Depends On |
|-----------|------|------------|
| 1 | qb-pcm (products) | None |
| 2 | qb-pricing | qb-pcm (Product2 must exist) |
| 3 | qb-billing | qb-pcm |
| 4 | qb-tax | qb-pcm |
| 5 | qb-dro | qb-pcm |
| 6 | qb-rating | qb-pcm |
| 7 | qb-rates | qb-pcm + qb-rating (PURs must exist) |
| 8 | qb-clm | qb-pcm |
| 9 | qb-approvals | post_approvals metadata + email templates |

### Deletion order

Deletion runs in reverse dependency order (children before parents):
1. Delete rates data (FK to PURs)
2. Delete rating data (PUG → PURP → PUR)
3. Delete billing data
4. Delete pricing data
5. Delete PCM data (products last)

---

## Testing and Validation

### Idempotency tests

Every data plan should have an idempotency test that loads the plan twice
and asserts no record count increase:

```yaml
test_qb_myfeature_idempotency:
    group: Data Management - Idempotency
    description: Idempotency test for qb-myfeature.
    class_path: tasks.rlm_sfdmu.TestSFDMUIdempotency
    options:
      pathtoexportjson: *myfeature_dataset
      use_extraction_roundtrip: false
```

### SFDMU v5 validation

Run the dataset validator to check all data plans:

```bash
python scripts/validate_sfdmu_v5_datasets.py
python scripts/validate_sfdmu_v5_datasets.py --fix-all --dry-run
```

### UX assembly dry-run

Test UX changes without deploying:

```bash
cci task run assemble_and_deploy_ux -o deploy false --org dev-sb0
```

### Environment validation

Check the local setup is complete:

```bash
cci task run validate_setup
```

### E2E testing

Run the full quote-to-order test:

```bash
cci task run robot_e2e --org beta           # headless
cci task run robot_e2e_debug --org beta      # headed with CDP debugging
```

### CCI reference regeneration

After any `cumulusci.yml` changes:

```bash
python scripts/ai/generate_cci_reference.py
```

---

## Common Integration Patterns

### Pattern: Deploy metadata + load data + activate

Most features follow this sequence:
1. Deploy metadata bundle (`deploy_post_<feature>`)
2. Load data plan (`insert_qb_<feature>_data`)
3. Activate records via Apex (`activate_<feature>_records`)
4. Assign permission sets

### Pattern: Patch-then-deploy for org-specific values

When metadata contains org-specific values (emails, usernames):
1. **Patch** the file with the org's actual value before deploy
2. **Deploy** the metadata
3. **Revert** the file to the placeholder after deploy

Examples: `patch_network_email_for_deploy` / `revert_network_email_after_deploy`,
`patch_payments_site_for_deploy` / `revert_payments_site_after_deploy`.

### Pattern: Context definition extension

Context definitions are not deployed via metadata — they're extended at
runtime via Connect API:
1. Call `extend_context_*` task to create/extend the definition
2. Optionally apply a context plan (`manage_context_definition` with a plan file)

### Pattern: Decision table lifecycle

1. Exclude active DTs before deploy (`exclude_active_decision_tables`)
2. Deploy DT metadata
3. Restore excluded DTs (`restore_decision_tables`)
4. Activate DTs (`activate_decision_tables`)
5. Refresh DTs (`refresh_dt_*`) after all data is loaded

### Pattern: Expression set lifecycle

1. Deactivate expression sets before deploy
2. Deploy expression set definitions (with XPath transforms for record IDs)
3. Activate expression set versions after all data exists

### Pattern: Robot Framework setup automation

For UI interactions that can't be done via API (e.g., enabling toggles):
1. Create a Robot test in `robot/rlm-base/tests/setup/`
2. Create a Python task wrapper in `tasks/` that passes org credentials
   and feature flags as Robot variables
3. Register the task in `cumulusci.yml`

---

## Updating Existing Features

### Adding a field to an existing object

1. Add the field XML to `force-app/main/default/objects/<Object>/fields/`
   or the appropriate `unpackaged/post_<feature>/objects/<Object>/fields/`
2. If the field needs FLS, update the relevant permission set(s)
3. If the field appears on a layout, update the template in
   `templates/layouts/` (not `force-app/` or `unpackaged/post_ux/`)

### Adding a record to an existing data plan

1. Add the record row to the appropriate CSV in
   `datasets/sfdmu/qb/en-US/qb-<plan>/`
2. If adding a new object to the plan, add it to `export.json` (follow
   parent→child ordering)
3. Run the idempotency test to verify

### Adding a new step to an existing flow

1. Find the flow in `cumulusci.yml`
2. Add the step with appropriate numbering and `when:` condition
3. Regenerate CCI references

---

## Related Skills

- **CCI Orchestration** — `.cursor/skills/cci-orchestration/SKILL.md`
  (tasks, flows, feature flags, CLI usage)
- **SFDMU Data Plans** — `.cursor/skills/sfdmu-data-plans/SKILL.md`
  (v5 rules, export.json authoring, review checklist)
- **Revenue Cloud Data Model** — `.cursor/skills/revenue-cloud-data-model/SKILL.md`
  (object relationships, domain overview)
- **RLM Business APIs** — `.cursor/skills/rlm-business-apis/SKILL.md`
  (REST API references)
- **Custom Task Authoring** — `.cursor/skills/cci-orchestration/custom-task-authoring.md`
  (Python task class patterns)
