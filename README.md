# Revenue Cloud Base Foundations

**Salesforce Release:** 260 (Spring '26)
**API Version:** 66.0

This repository automates the creation and configuration of Salesforce environments that require Revenue Cloud (formerly Revenue Lifecycle Management) functionality.

The main branch targets Salesforce Release 260 (Spring '26, GA). Other branches exist for different release scenarios.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Feature Flags](#feature-flags)
- [Custom Tasks](#custom-tasks)
- [Flows](#flows)
- [Data Plans](#data-plans)
- [Documentation](#documentation)
- [Project Structure](#project-structure)
- [Common Workflows](#common-workflows)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Branch Information](#branch-information)
- [Additional Resources](#additional-resources)

## Prerequisites

### Required Software

1. **Salesforce CLI** (`sf` CLI)
   - Version 2.x or later
   - Installation: https://developer.salesforce.com/tools/salesforcecli
   - Verify: `sf --version`

2. **CumulusCI** (CCI)
   - Minimum version: 4.0.0 (as specified in `cumulusci.yml`)
   - Installation: **prefer** `pipx install cumulusci` (isolated environment; avoids modifying your global Python). If you don't use pipx: create a virtual environment and run `pip install cumulusci` inside it.
   - Verify: `cci version`

3. **SFDMU (Salesforce Data Move Utility)**
   - **Version 5.0.0 or later required** (v4.x is no longer supported)
   - Required for data loading tasks
   - Installation: `sf plugins install sfdmu`
   - Verify: `sf plugins list` (should show sfdmu 5.x)
   - The `validate_setup` task checks and auto-updates the SFDMU version
   - Documentation: https://help.sfdmu.com/

4. **Python** (for custom tasks)
   - Python 3.8 or later
   - Required packages are included with CumulusCI

### Required Salesforce Access

- Salesforce org with Revenue Cloud licenses
- Appropriate permissions for metadata deployment
- For scratch orgs: Dev Hub enabled

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd rlm-base-dev
   ```

2. **Install CumulusCI:**
   ```bash
   pipx install cumulusci
   ```
   Prefer **pipx** so CumulusCI runs in an isolated environment and does not install into your global Python. If you don't use pipx, create a [virtual environment](https://docs.python.org/3/library/venv.html) first, then run `pip install cumulusci` inside it.

   **Dependencies for Document Builder automation** (required if you use `prepare_docgen` or the `enable_document_builder_toggle` task):
   - Python 3.8+
   - Robot Framework, SeleniumLibrary, and webdriver-manager: keep them in the **same environment as CumulusCI** so the CCI task can run the `robot` command. A full dependency set (including the urllib3 pin) is in **`robot/requirements.txt`**; install in the same env as CCI (e.g. `pip install -r robot/requirements.txt` in your venv). If you use **pipx** for CumulusCI (recommended), inject into its environment (no global install):
     ```bash
     pipx inject cumulusci robotframework robotframework-seleniumlibrary webdriver-manager "urllib3>=1.26,<2"
     ```
     `urllib3>=1.26,<2` avoids a known Selenium/urllib3 2.x issue (`Timeout value connect was <object object at ...>`). webdriver-manager provides ChromeDriver automatically (no need to install ChromeDriver in PATH). If you previously installed these with `pip install` globally, uninstall first: `python3 -m pip uninstall -y robotframework-seleniumlibrary robotframework webdriver-manager`. If you use a project virtual environment instead of pipx for CCI, install there: `pip install -r robot/requirements.txt` (or the packages above) inside the venv.
   - Chrome (or set `BROWSER=firefox`). With webdriver-manager installed, ChromeDriver is downloaded automatically when the test runs. If webdriver-manager is **not** installed, the test falls back to the system ChromeDriver on `PATH`.
   - The task uses `sf org open --url-only` to authenticate the browser; ensure the Salesforce CLI (`sf`) is installed and the org is logged in.

3. **Install SFDMU (v5+):**
   ```bash
   sf plugins install sfdmu
   ```

4. **Verify installations:**
   ```bash
   sf --version
   cci version
   sf plugins list  # Should show sfdmu 5.x
   ```
   **Document Builder (Robot) env only — no org or flow required:** To confirm Robot and SeleniumLibrary are in CCI's environment before running any flow or test:
   ```bash
   # Robot CLI (pipx venv path; on Windows use ...\Scripts\robot.bat)
   ~/.local/pipx/venvs/cumulusci/bin/robot --version
   # SeleniumLibrary importable in same env
   ~/.local/pipx/venvs/cumulusci/bin/python -c "import SeleniumLibrary; print('SeleniumLibrary OK')"
   ```
   If both succeed, your env is ready for `prepare_docgen` / `enable_document_builder_toggle` when prerequisites are in place.

5. **Authenticate with Salesforce:**
   ```bash
   sf org login web
   # OR for Dev Hub (for scratch orgs)
   sf org login web --alias devhub --instance-url https://login.salesforce.com
   ```

6. **Initialize CumulusCI:**
   ```bash
   cci org default <your-org-alias>
   ```

## Quick Start

### Create a Scratch Org

```bash
# Create a basic dev scratch org
cci org scratch dev <org-alias>

# Create an enhanced dev scratch org (with additional features)
cci org scratch dev_enhanced <org-alias>
```

### Deploy to an Existing Org

```bash
# Set default org
cci org default <org-alias>

# Run the main deployment flow
cci flow run prepare_rlm_org
```

### Reset default or target scratch org and run full flow

To remove your current default (or target) scratch org, create a new one, and run the full RLM prepare flow (includes billing data when applicable), use your scratch org config and alias (e.g. `beta`, `dev`, `dev_enhanced`—see `orgs/` and `cumulusci.yml` under `orgs.scratch`):

```bash
# Delete existing scratch org (use the same alias you created it with)
cci org scratch_delete <org-alias>

# Create a new scratch org (config name and alias; set as default if desired)
cci org scratch <config-name> <org-alias> --default --days 30

# Run the full prepare flow on that org
cci flow run prepare_rlm_org --org <org-alias>
```

Decision tables under `unpackaged/pre/5_decisiontables` are deployed by this flow. Active decision tables are excluded per run by moving them into a `.skip` subdirectory before deploy (no `.forceignore` changes). Permission set groups are recalculated only when they are in **Outdated** state; if all are already **Updated**, the recalc step exits without waiting.

### List Available Flows and Tasks

```bash
cci flow list
cci task list
```

## Feature Flags

The project uses custom flags in `cumulusci.yml` under `project.custom` to control feature deployment. Modify these flags or override them at runtime with `-o <flag> <value>`.

### Core Flags

| Flag | Default | Description |
|------|---------|-------------|
| `qbrix` | `false` | Use xDO base (false for dev scratch orgs without xDO licenses) |
| `tso` | `false` | Is Trialforce Source Org? (false for dev scratch orgs) |
| `qb` | `true` | QuantumBit dataset family |
| `q3` | `false` | Include Q3 data |
| `quantumbit` | `true` | QuantumBit features |
| `product_dataset` | `qb` | Default product dataset to use |
| `locale` | `en_US` | Default locale |
| `refresh` | `false` | Data refresh flag (skips initial data loads when true) |

### Data Flags

| Flag | Default | Description |
|------|---------|-------------|
| `rating` | `true` | Insert Rating design-time data |
| `rates` | `true` | Insert Rates |
| `ramps` | `true` | Insert and configure ramps |
| `clm_data` | `false` | Load Contract Lifecycle Management data |
| `constraints_data` | `true` | Load constraint model data (CML import + activation) |

### Feature Flags

| Flag | Default | Description |
|------|---------|-------------|
| `calmdelete` | `true` | Use CALM Delete |
| `tax` | `true` | Use Tax engine |
| `billing` | `true` | Use Billing |
| `payments` | `true` | Use Payments |
| `approvals` | `true` | Use Approvals |
| `clm` | `true` | Use Contract Lifecycle Management |
| `dro` | `true` | Use Dynamic Revenue Orchestration |
| `einstein` | `true` | Use Einstein AI |
| `agents` | `false` | Deploy Agentforce Agent configurations |
| `prm` | `true` | Use Partner Relationship Management |
| `prm_exp_bundle` | `false` | Use PRM Experience Bundle |
| `commerce` | `false` | Use Commerce |
| `breconfig` | `false` | Business Rules Engine configuration |
| `docgen` | `true` | Use Document Generation |
| `constraints` | `true` | Use Constraint Builder (metadata setup) |
| `guidedselling` | `false` | Use Guided Selling |
| `procedureplans` | `true` | Use Procedure Plans |
| `visualization` | `false` | Use Visualization components (Flow with Visuals, LWC styling) |

### Deployment Flags

| Flag | Default | Description |
|------|---------|-------------|
| `sharingsettings` | `false` | Deploy Sharing Settings |

## Custom Tasks

This project includes custom Python task modules in the `tasks/` directory, each registered as one or more CCI tasks in `cumulusci.yml`.

### Data Management Tasks

| Task Name | Module | Description | Documentation |
|-----------|--------|-------------|---------------|
| `load_sfdmu_data` | `rlm_sfdmu.py` | Load SFDMU data plans (supports `simulation` dry-run mode, `object_sets` pass filtering, dynamic DRO user resolution) | See `cumulusci.yml` |
| `export_cml` | `rlm_cml.py` | Export constraint model data (CSVs + blob) from an org | [Constraints Utility Guide](datasets/constraints/README.md) |
| `import_cml` | `rlm_cml.py` | Import constraint model data into an org (polymorphic resolution, dry run) | [Constraints Utility Guide](datasets/constraints/README.md) |
| `validate_cml` | `rlm_cml.py` | Validate CML file structure and ESC association coverage (no org needed) | [Constraints Utility Guide](datasets/constraints/README.md) |
| `extract_qb_rating_data` | `rlm_sfdmu.py` | Extract QuantumBit rating data from an org to CSV | See `cumulusci.yml` |
| `extract_qb_rates_data` | `rlm_sfdmu.py` | Extract QuantumBit rates data from an org to CSV | See `cumulusci.yml` |
| `post_process_extraction` | `rlm_sfdmu.py` | Post-process extracted CSV data | See `cumulusci.yml` |
| `sync_pricing_data` | `rlm_sync_pricing_data.py` | Sync pricing data (PricebookEntry/PriceAdjustmentSchedule) | See `cumulusci.yml` |

### Metadata Management Tasks

| Task Name | Module | Description | Documentation |
|-----------|--------|-------------|---------------|
| `manage_decision_tables` | `rlm_manage_decision_tables.py` | Decision Table management: list, query, refresh, activate, deactivate, validate_lists | [Decision Table Examples](docs/DECISION_TABLE_EXAMPLES.md) |
| `manage_flows` | `rlm_manage_flows.py` | Flow management (list, query, activate, deactivate) | [Task Examples](docs/TASK_EXAMPLES.md) |
| `manage_expression_sets` | `rlm_manage_expression_sets.py` | Expression Set management: list, query, activate/deactivate versions | [Task Examples](docs/TASK_EXAMPLES.md) |
| `manage_transaction_processing_types` | `rlm_manage_transaction_processing_types.py` | Manage TransactionProcessingType records (list, upsert, delete) | [Constraints Setup](docs/constraints_setup.md) |
| `manage_context_definition` | `rlm_context_service.py` | Modify context definitions via Context Service API | [Context Service Utility](docs/context_service_utility.md) |
| `extend_standard_context` | `rlm_extend_stdctx.py` | Extend standard context definitions with custom attributes | [Context Service Utility](docs/context_service_utility.md) |

### Decision Table Refresh Tasks

| Task Name | Module | Description |
|-----------|--------|-------------|
| `refresh_dt_rating` | `rlm_refresh_decision_table.py` | Refresh rating decision tables |
| `refresh_dt_rating_discovery` | `rlm_refresh_decision_table.py` | Refresh rating discovery decision tables |
| `refresh_dt_default_pricing` | `rlm_refresh_decision_table.py` | Refresh default pricing decision tables |
| `refresh_dt_pricing_discovery` | `rlm_refresh_decision_table.py` | Refresh pricing discovery decision tables |
| `refresh_dt_asset` | `rlm_refresh_decision_table.py` | Refresh asset decision tables |
| `refresh_dt_commerce` | `rlm_refresh_decision_table.py` | Refresh commerce decision tables |

### Deployment & Permissions Tasks

| Task Name | Module | Description |
|-----------|--------|-------------|
| `cleanup_settings_for_dev` | `rlm_cleanup_settings.py` | Remove unsupported settings for dev scratch orgs |
| `exclude_active_decision_tables` | `rlm_exclude_active_decision_tables.py` | Move active decision tables to `.skip` dir before deploy |
| `assign_permission_set_groups_tolerant` | `rlm_assign_permission_set_groups.py` | Assign PSGs with tolerance for missing permissions |
| `recalculate_permission_set_groups` | `rlm_recalculate_permission_set_groups.py` | Recalculate PSGs and wait for Updated status (retries, delays) |

### Activation Tasks

| Task Name | Module | Description |
|-----------|--------|-------------|
| `activate_decision_tables` | `rlm_manage_decision_tables.py` | Activate decision tables |
| `deactivate_decision_tables` | `rlm_manage_decision_tables.py` | Deactivate decision tables |
| `activate_expression_sets` | `rlm_manage_expression_sets.py` | Activate expression sets |
| `deactivate_expression_sets` | `rlm_manage_expression_sets.py` | Deactivate expression sets |
| `activate_default_payment_term` | `rlm_sfdmu.py` | Activate default payment term |
| `activate_billing_records` | `rlm_sfdmu.py` | Activate billing records |
| `activate_tax_records` | `rlm_sfdmu.py` | Activate tax records |
| `activate_price_adjustment_schedules` | `rlm_repair_pricing_schedules.py` | Activate price adjustment schedules |
| `activate_rating_records` | `rlm_sfdmu.py` | Activate rating records |
| `activate_rates` | `rlm_sfdmu.py` | Activate rates |

### Setup & Configuration Tasks

| Task Name | Module | Description | Documentation |
|-----------|--------|-------------|---------------|
| `create_rule_library` | `rlm_sfdmu.py` | Create BRE rule library | See `cumulusci.yml` |
| `create_docgen_library` | `rlm_sfdmu.py` | Create document generation library | See `cumulusci.yml` |
| `create_dro_rule_library` | `rlm_sfdmu.py` | Create DRO rule library | See `cumulusci.yml` |
| `create_tax_engine` | `rlm_sfdmu.py` | Create tax engine records | See `cumulusci.yml` |
| `validate_setup` | `rlm_validate_setup.py` | Validate local developer setup: Python, CumulusCI, Salesforce CLI, SFDMU plugin version, Node.js, Robot Framework, SeleniumLibrary, webdriver-manager, urllib3. Auto-fixes outdated SFDMU when `auto_fix=true`. No org required. | See `cumulusci.yml` |
| `enable_document_builder_toggle` | `rlm_enable_document_builder_toggle.py` | Enable Document Builder, Document Templates Export, and Design Document Templates via Robot Framework browser automation | [Robot Setup README](robot/rlm-base/tests/setup/README.md) |
| `enable_constraints_settings` | `rlm_enable_constraints_settings.py` | Set Default Transaction Type, Asset Context, and enable Constraints Engine toggle via Robot Framework | [Constraints Setup](docs/constraints_setup.md) |
| `configure_revenue_settings` | `rlm_configure_revenue_settings.py` | Configure Revenue Settings: Pricing Procedure, Usage Rating, Instant Pricing toggle, Create Orders Flow (Robot Framework) | See `cumulusci.yml` |
| `reconfigure_pricing_discovery` | `rlm_reconfigure_expression_set.py` | Reconfigure autoproc `Salesforce_Default_Pricing_Discovery_Procedure`: fix context definition, rank, start date | See `cumulusci.yml` |
| `create_procedure_plan_definition` | `rlm_create_procedure_plan_def.py` | Create Procedure Plan Definition + inactive Version via Connect API (idempotent) | [procedure-plans README](datasets/sfdmu/procedure-plans/README.md) |
| `activate_procedure_plan_version` | `rlm_create_procedure_plan_def.py` | Activate ProcedurePlanDefinitionVersion after data load (idempotent) | [procedure-plans README](datasets/sfdmu/procedure-plans/README.md) |
| `deploy_billing_id_settings` | (CCI Deploy) | Deploy Billing Settings with org-specific record IDs resolved via XPath transform SOQL queries | See `cumulusci.yml` |
| `deploy_billing_template_settings` | (CCI Deploy) | Re-enable Invoice Email/PDF toggles to trigger default template auto-creation (cycle step 3) | See `cumulusci.yml` |
| `ensure_pricing_schedules` | `rlm_repair_pricing_schedules.py` | Ensure pricing schedules exist before expression set deploy | See `cumulusci.yml` |
| `restore_rc_tso` | `rlm_restore_rc_tso.py` | Restore Revenue Cloud TSO metadata | See `cumulusci.yml` |

### Using Custom Tasks

All custom tasks are automatically available via CumulusCI. Use them like any standard CCI task:

```bash
# List decision tables (includes UsageType)
cci task run manage_decision_tables --operation list

# Validate decision table lists vs org
cci task run manage_decision_tables --operation validate_lists

# Manage flows
cci task run manage_flows --operation list --process_type ScreenFlow

# Manage expression sets
cci task run manage_expression_sets --operation list

# Export a constraint model
cci task run export_cml --org <org> -o developer_name QuantumBitComplete -o version 1 -o output_dir datasets/constraints/qb/QuantumBitComplete

# Import a constraint model (with dry run)
cci task run import_cml --org <org> -o data_dir datasets/constraints/qb/QuantumBitComplete -o dataset_dirs "datasets/sfdmu/qb/en-US/qb-pcm" -o dry_run true

# Validate CML files
cci task run validate_cml -o cml_dir scripts/cml -o data_dir datasets/constraints/qb/QuantumBitComplete
```

For detailed examples and usage, see:
- [Decision Table Examples](docs/DECISION_TABLE_EXAMPLES.md)
- [Flow and Expression Set Examples](docs/TASK_EXAMPLES.md)
- [Constraints Utility Guide](datasets/constraints/README.md)

### Custom Task Development

Custom tasks are Python modules in the `tasks/` directory. They inherit from CumulusCI's `BaseTask` (or `BaseSalesforceTask` for org-connected tasks) and are automatically discovered by CumulusCI.

To add a new custom task:
1. Create a Python file in `tasks/` (e.g., `tasks/rlm_my_task.py`)
2. Define your task class inheriting from the appropriate base
3. Add task configuration to `cumulusci.yml` under `tasks:`
4. Reference the task in flows or run directly

Example task structure:
```python
from cumulusci.core.tasks import BaseTask
from cumulusci.core.exceptions import TaskOptionsError

class MyCustomTask(BaseTask):
    task_options = {
        "option1": {"description": "Description", "required": True}
    }
    
    def _run_task(self):
        # Task implementation
        pass
```

For tasks that need Salesforce org access (REST API, SOQL, etc.):
```python
from cumulusci.tasks.salesforce import BaseSalesforceTask

class MyOrgTask(BaseSalesforceTask):
    task_options = {
        "option1": {"description": "Description", "required": True}
    }
    
    def _run_task(self):
        # self.org_config provides access_token, instance_url, etc.
        pass
```

## Flows

All flows belong to the **Revenue Lifecycle Management** group. The main orchestration flow is `prepare_rlm_org`, which calls sub-flows in sequence.

### Main Orchestration

| Flow | Description |
|------|-------------|
| `prepare_rlm_org` | **Master flow** -- runs all sub-flows in order (29 steps). This is the primary flow for full org setup. |

#### prepare_rlm_org Step Order

| Step | Flow/Task | Condition |
|------|-----------|-----------|
| 1 | `prepare_core` | Always |
| 2 | `prepare_decision_tables` | Always |
| 3 | `prepare_expression_sets` | Always |
| 4 | `create_partner_central` | `prm` |
| 5 | `create_payments_webhook` | `payments` |
| 6 | `deploy_full` | Always |
| 7 | `prepare_price_adjustment_schedules` | Always |
| 8 | `prepare_scratch` | Always |
| 9 | `prepare_payments` | Always |
| 10 | `prepare_quantumbit` | Always |
| 11 | `prepare_product_data` | Always |
| 12 | `prepare_pricing_data` | Always |
| 13 | `prepare_docgen` | Always |
| 14 | `prepare_dro` | Always |
| 15 | `prepare_tax` | Always |
| 16 | `prepare_billing` | Always |
| 17 | `prepare_clm` | Always |
| 18 | `prepare_rating` | Always |
| 19 | `activate_and_deploy_expression_sets` | Always |
| 20 | `prepare_tso` | Always |
| 21 | `prepare_procedureplans` | Always |
| 22 | `prepare_prm` | Always |
| 23 | `prepare_agents` | Always |
| 24 | `prepare_constraints` | Always |
| 25 | `prepare_guidedselling` | Always |
| 26 | `prepare_visualization` | Always |
| 27 | `configure_revenue_settings` | Always |
| 28 | `reconfigure_pricing_discovery` | Always |
| 29 | `refresh_all_decision_tables` | Always |

> **Note:** "Always" means the flow/task runs as a step, but individual tasks inside each sub-flow may be gated by feature flags.

### Sub-Flows

| Flow | Description | Key Feature Flags |
|------|-------------|-------------------|
| `prepare_core` | PSL/PSG assignment, context definitions, rule libraries, settings cleanup | `clm`, `einstein`, `dro`, `breconfig`, `billing` |
| `extend_context_definitions` | Extend all standard context definitions | `commerce`, `billing`, `dro`, `clm`, `rating` |
| `prepare_expression_sets` | Deactivate, ensure pricing schedules, deploy expression sets | Scratch only |
| `prepare_product_data` | Load PCM + product image SFDMU data | `qb`, `q3` |
| `prepare_pricing_data` | Load pricing SFDMU data | `qb` |
| `prepare_scratch` | Insert scratch-only data | Scratch only, not `tso` |
| `prepare_quantumbit` | Deploy QuantumBit metadata, permissions, CALM delete | `quantumbit`, `billing`, `approvals`, `calmdelete` |
| `prepare_tso` | TSO-specific PSL/PSG/permissions/metadata | `tso` |
| `prepare_dro` | Load DRO data (dynamic user resolution) | `dro`, `qb`, `q3` |
| `prepare_clm` | Load CLM data | `clm`, `clm_data` |
| `prepare_docgen` | Create docgen library, enable Document Builder + Document Templates Export + Design Document Templates toggles, deploy metadata | `docgen` |
| `prepare_billing` | Load billing data, activate flows/records, deploy ID-based settings via XPath transforms, trigger default template auto-creation (3-step cycle) | `billing`, `qb`, `q3`, `refresh` |
| `prepare_prm` | Deploy PRM metadata, publish community, sharing rules | `prm`, `prm_exp_bundle`, `sharingsettings` |
| `prepare_tax` | Create tax engine, load data, activate records | `tax`, `qb`, `q3`, `refresh` |
| `prepare_rating` | Load rating + rates data, activate | `rating`, `rates`, `qb`, `q3`, `refresh` |
| `extract_rating` | Extract rating and rates data from an org | -- |
| `prepare_agents` | Deploy Agentforce agents, settings, permissions | `agents` |
| `refresh_all_decision_tables` | Sync pricing, refresh all DT categories | `rating`, `commerce` |
| `prepare_decision_tables` | Activate decision tables | Scratch only |
| `prepare_price_adjustment_schedules` | Activate price adjustment schedules | Scratch only |
| `prepare_procedureplans` | Deploy procedure plans metadata + `skipOrgSttPricing` setting, create PPD via Connect API, load sections/options, activate | `procedureplans` |
| `prepare_constraints` | Load TransactionProcessingTypes, deploy metadata, configure settings, import CML models, activate | `constraints`, `constraints_data`, `qb` |
| `prepare_guidedselling` | Load guided selling data, deploy metadata | `guidedselling`, `qb` |
| `prepare_visualization` | Deploy visualization components | `visualization` |
| `prepare_payments` | Deploy payments site, publish community, deploy settings | `payments` |

### Utility Flows and Tasks

| Flow/Task | Type | Description |
|-----------|------|-------------|
| `deploy_full` | Task | Full metadata deployment (source, pre/post bundles) |
| `activate_and_deploy_expression_sets` | Task | Re-deploy expression sets with Draft status transformed to Active via XPath |

## Data Plans

Data plans provide the reference data loaded during org setup. This project uses two mechanisms:

### SFDMU Data Plans

> **Requires SFDMU v5.0.0+.** All data plans have been migrated for SFDMU v5 compatibility
> and idempotency. See [Composite Key Optimizations](docs/sfdmu_composite_key_optimizations.md)
> for the full migration details and known limitations.

SFDMU data plans are located under `datasets/sfdmu/` and are loaded by the `load_sfdmu_data` task infrastructure. Each plan contains an `export.json` defining the objects, fields, and ordering for SFDMU.

#### QuantumBit (QB) Data Plans

| Data Plan | Directory | Description | Documentation |
|-----------|-----------|-------------|---------------|
| qb-pcm | `datasets/sfdmu/qb/en-US/qb-pcm/` | Product Catalog Management -- products, classifications, components, attributes | [README](datasets/sfdmu/qb/en-US/qb-pcm/README.md) |
| qb-product-images | `datasets/sfdmu/qb/en-US/qb-product-images/` | Product images and content document links | [README](datasets/sfdmu/qb/en-US/qb-product-images/README.md) |
| qb-pricing | `datasets/sfdmu/qb/en-US/qb-pricing/` | Pricing data (pricebook entries, price adjustments) | [README](datasets/sfdmu/qb/en-US/qb-pricing/README.md) |
| qb-tax | `datasets/sfdmu/qb/en-US/qb-tax/` | Tax engine data (tax treatments, policies) | [README](datasets/sfdmu/qb/en-US/qb-tax/README.md) |
| qb-billing | `datasets/sfdmu/qb/en-US/qb-billing/` | Billing data (billing terms, schedules) | [README](datasets/sfdmu/qb/en-US/qb-billing/README.md) |
| qb-dro | `datasets/sfdmu/qb/en-US/qb-dro/` | Dynamic Revenue Orchestration plans | [README](datasets/sfdmu/qb/en-US/qb-dro/README.md) |
| qb-transactionprocessingtypes | `datasets/sfdmu/qb/en-US/qb-transactionprocessingtypes/` | Transaction Processing Type records | [README](datasets/sfdmu/qb/en-US/qb-transactionprocessingtypes/README.md) |
| qb-rating | `datasets/sfdmu/qb/en-US/qb-rating/` | Rating design-time data | [README](datasets/sfdmu/qb/en-US/qb-rating/README.md) |
| qb-rates | `datasets/sfdmu/qb/en-US/qb-rates/` | Rates data | [README](datasets/sfdmu/qb/en-US/qb-rates/README.md) |

#### Procedure Plans Data Plan

| Data Plan | Directory | Description | Documentation |
|-----------|-----------|-------------|---------------|
| procedure-plans | `datasets/sfdmu/procedure-plans/` | Procedure Plan sections and options with expression set links (2-pass upsert + Connect API + activation) | [README](datasets/sfdmu/procedure-plans/README.md) |

#### Archived Data Plans

Deprecated data plans are retained in `datasets/sfdmu/_archived/` for reference. These are no longer used:

- `qb-constraints-product` -- replaced by CML utility
- `qb-constraints-component` -- replaced by CML utility
- `qb-constraints-consolidated` -- replaced by CML utility
- `qb-constraints-prc-aisummit` -- replaced by CML utility

### Constraint Model Data Plans

Constraint model data is managed by the Python-based CML utility (`tasks/rlm_cml.py`) instead of SFDMU. These plans are stored under `datasets/constraints/` and include CSVs for Expression Sets, ESC associations, and binary ConstraintModel blobs.

| Model | Directory | ESC Records | Documentation |
|-------|-----------|-------------|---------------|
| QuantumBitComplete | `datasets/constraints/qb/QuantumBitComplete/` | 43 | [Constraints Utility Guide](datasets/constraints/README.md) |
| Server2 | `datasets/constraints/qb/Server2/` | 81 | [Constraints Utility Guide](datasets/constraints/README.md) |

For details on exporting new models, importing into target orgs, polymorphic ID resolution, and CCI integration, see the [Constraints Utility Guide](datasets/constraints/README.md).

## Documentation

### Primary Guides

| Document | Description |
|----------|-------------|
| [Constraints Utility Guide](datasets/constraints/README.md) | CML constraint model export, import, validate -- architecture, workflows, polymorphic resolution |
| [Constraints Setup](docs/constraints_setup.md) | `prepare_constraints` flow order, feature flags, deployment phases |
| [Decision Table Examples](docs/DECISION_TABLE_EXAMPLES.md) | Comprehensive examples for Decision Table management tasks |
| [Task Examples](docs/TASK_EXAMPLES.md) | Examples for Flow and Expression Set management tasks |
| [Context Service Utility](docs/context_service_utility.md) | Context Service utility usage and plan examples |

### Analysis & Planning

| Document | Description |
|----------|-------------|
| [Tooling Opportunities](docs/TOOLING_OPPORTUNITIES.md) | Analysis of Spring '26 features and opportunities for new tooling tasks |
| [Composite Key Optimizations](docs/sfdmu_composite_key_optimizations.md) | SFDMU v5 migration, composite key analysis, idempotency verification |
| [RCA/RCB Unique ID Fields](docs/rca_rcb_unique_id_fields.md) | Unique ID field analysis for Revenue Cloud objects |

### SFDMU Data Plan READMEs

Each SFDMU data plan has its own detailed README documenting objects, fields, load order, external IDs, and optimization opportunities:

- [qb-pcm README](datasets/sfdmu/qb/en-US/qb-pcm/README.md) -- Product Catalog Management
- [qb-product-images README](datasets/sfdmu/qb/en-US/qb-product-images/README.md) -- Product Images
- [qb-pricing README](datasets/sfdmu/qb/en-US/qb-pricing/README.md) -- Pricing
- [qb-tax README](datasets/sfdmu/qb/en-US/qb-tax/README.md) -- Tax
- [qb-billing README](datasets/sfdmu/qb/en-US/qb-billing/README.md) -- Billing
- [qb-dro README](datasets/sfdmu/qb/en-US/qb-dro/README.md) -- Dynamic Revenue Orchestration
- [qb-transactionprocessingtypes README](datasets/sfdmu/qb/en-US/qb-transactionprocessingtypes/README.md) -- Transaction Processing Types
- [qb-rating README](datasets/sfdmu/qb/en-US/qb-rating/README.md) -- Rating
- [qb-rates README](datasets/sfdmu/qb/en-US/qb-rates/README.md) -- Rates
- [procedure-plans README](datasets/sfdmu/procedure-plans/README.md) -- Procedure Plans

### Robot Framework

- [Robot Setup README](robot/rlm-base/tests/setup/README.md) -- Browser automation for setup page toggles and picklists (Document Builder, Constraints Settings, Revenue Settings)

### Configuration Files

- **`cumulusci.yml`** -- Main CumulusCI configuration with all tasks, flows, and project settings
- **`sfdx-project.json`** -- Salesforce DX project configuration
- **`orgs/`** -- Scratch org definition files for different scenarios

## Project Structure

```
rlm-base-dev/
├── force-app/                  # Main Salesforce metadata (source format)
├── unpackaged/                 # Conditional metadata (deployed based on flags)
│   ├── pre/                    # Pre-deployment metadata
│   │   └── 5_decisiontables/   # Decision tables (active ones auto-excluded)
│   ├── post_approvals/         # Approvals metadata
│   ├── post_billing/           # Billing metadata (toggles, flexipages, billingContextDefinition)
│   ├── post_billing_id_settings/ # Billing settings with org-specific record IDs (XPath transforms)
│   ├── post_billing_template_settings/ # Re-enable invoice toggles (template auto-creation cycle step 3)
│   ├── post_commerce/          # Commerce metadata
│   ├── post_constraints/       # Constraints metadata
│   ├── post_docgen/            # Document Generation metadata
│   ├── post_guidedselling/     # Guided Selling metadata
│   ├── post_payments/          # Payments metadata
│   ├── post_prm/               # Partner Relationship Management metadata
│   ├── post_procedureplans/    # Procedure Plans metadata + RevenueManagement.settings (skipOrgSttPricing)
│   ├── post_scratch/           # Scratch org-only metadata
│   ├── post_tso/               # TSO-specific metadata
│   ├── post_utils/             # Utility metadata
│   └── post_visualization/     # Visualization metadata
├── tasks/                      # Custom CumulusCI Python task modules
│   ├── rlm_cml.py              # CML constraint utility (ExportCML, ImportCML, ValidateCML)
│   ├── rlm_sfdmu.py            # SFDMU data loading tasks
│   ├── rlm_manage_decision_tables.py
│   ├── rlm_manage_expression_sets.py
│   ├── rlm_manage_flows.py
│   ├── rlm_manage_transaction_processing_types.py
│   ├── rlm_context_service.py
│   ├── rlm_extend_stdctx.py
│   ├── rlm_enable_document_builder_toggle.py
│   ├── rlm_enable_constraints_settings.py
│   ├── rlm_configure_revenue_settings.py
│   ├── rlm_reconfigure_expression_set.py
│   ├── rlm_create_procedure_plan_def.py
│   ├── rlm_refresh_decision_table.py
│   ├── rlm_sync_pricing_data.py
│   ├── rlm_repair_pricing_schedules.py
│   ├── rlm_cleanup_settings.py
│   ├── rlm_assign_permission_set_groups.py
│   ├── rlm_recalculate_permission_set_groups.py
│   ├── rlm_exclude_active_decision_tables.py
│   ├── rlm_modify_context.py
│   ├── rlm_restore_rc_tso.py
│   └── sfdmuload.py
├── robot/                      # Robot Framework tests
│   └── rlm-base/
│       ├── resources/          # Keywords, WebDriverManager helper
│       ├── tests/setup/        # Setup page automation (Document Builder, Constraints, Revenue Settings)
│       └── results/            # Runtime output (gitignored)
├── datasets/                   # Data plans
│   ├── sfdmu/                  # SFDMU data plans
│   │   ├── qb/en-US/           # QuantumBit data plans (9 active plans)
│   │   │   ├── qb-pcm/
│   │   │   ├── qb-product-images/
│   │   │   ├── qb-pricing/
│   │   │   ├── qb-tax/
│   │   │   ├── qb-billing/
│   │   │   ├── qb-dro/
│   │   │   ├── qb-transactionprocessingtypes/
│   │   │   ├── qb-rating/
│   │   │   └── qb-rates/
│   │   ├── procedure-plans/    # Procedure Plans data plan (sections + options)
│   │   └── _archived/          # Deprecated SFDMU plans (constraints attempts)
│   ├── constraints/            # CML constraint model data plans
│   │   ├── qb/
│   │   │   ├── QuantumBitComplete/
│   │   │   └── Server2/
│   │   └── README.md           # Constraints utility guide
│   └── context_plans/          # Context definition update plans (JSON manifests)
│       ├── ConstraintEngineNodeStatus/  # Adds ConstraintEngineNodeStatus to SalesTransaction context
│       │   ├── manifest.json
│       │   └── contexts/
│       └── archive/            # Archived/previous context plans
├── scripts/                    # Utility scripts
│   ├── apex/                   # Anonymous Apex scripts
│   ├── cml/                    # CML source files (.cml) and deprecated Python scripts
│   └── bash/                   # Bash scripts
├── docs/                       # Documentation
│   ├── constraints_setup.md
│   ├── DECISION_TABLE_EXAMPLES.md
│   ├── TASK_EXAMPLES.md
│   ├── context_service_utility.md
│   ├── TOOLING_OPPORTUNITIES.md
│   ├── sfdmu_composite_key_optimizations.md
│   └── rca_rcb_unique_id_fields.md
├── orgs/                       # Scratch org definitions
├── cumulusci.yml               # CumulusCI configuration
├── sfdx-project.json           # Salesforce DX configuration
└── README.md                   # This file
```

## Common Workflows

### Full Org Setup

```bash
# 1. Create scratch org
cci org scratch dev my-org

# 2. Set as default
cci org default my-org

# 3. Run full deployment flow
cci flow run prepare_rlm_org
```

### Deploy Specific Features

```bash
# Enable a feature flag in cumulusci.yml, then:
cci flow run prepare_rlm_org
```

### Prepare Constraints (with Data)

```bash
# Run constraints flow with CML data loading enabled
cci flow run prepare_constraints --org <org> -o constraints_data true
```

This will validate CML files, import both QuantumBitComplete and Server2 models, and activate their expression sets. See [Constraints Setup](docs/constraints_setup.md) for flow details.

### Export a Constraint Model

```bash
# Export from a source org to a local data plan directory
cci task run export_cml --org <source_org> \
    -o developer_name QuantumBitComplete \
    -o version 1 \
    -o output_dir datasets/constraints/qb/QuantumBitComplete
```

See the [Constraints Utility Guide](datasets/constraints/README.md) for full export/import/validate documentation.

### Load Product Data

```bash
# Load QuantumBit PCM data
cci task run insert_quantumbit_pcm_data

# Load product images
cci task run insert_quantumbit_product_image_data
```

### Load Billing Data

```bash
cci task run insert_billing_data
```

The `prepare_billing` flow deploys Billing Settings in a 3-step cycle to properly configure ID-based fields and trigger default template auto-creation:

1. **Step 6** (`deploy_post_billing`): Enable billing toggles (`enableInvoiceEmailDelivery`, `enableInvoicePdfGeneration` = `true`) and set `billingContextDefinition`
2. **Step 7** (`deploy_billing_id_settings`): Set context mapping, DPE definition names, and record IDs via XPath transforms; disable invoice toggles (`false`)
3. **Step 8** (`deploy_billing_template_settings`): Re-enable invoice toggles (`true`) to trigger Salesforce auto-creation of default invoice preview and document templates

The ID fields (`defaultBillingTreatment`, `defaultLegalEntity`, `defaultTaxTreatment`) use XPath transform SOQL queries to resolve org-specific record IDs at deploy time. The `billingContextDefinition` must be deployed in step 6 (before step 7) because `billingContextSourceMapping` requires it to already be persisted.

DRO data (prepare_dro flow) uses a single **qb-dro** data plan for both scratch and non-scratch orgs: the task replaces the placeholder `__DRO_ASSIGNED_TO_USER__` with the target org's default user Name (e.g. "User User" in scratch orgs, "Admin User" in TSO) before loading. No separate scratch-specific DRO plan is required.

### Extract Rating Data

```bash
# Extract rating and rates data from an org
cci flow run extract_rating --org <org>
```

### Manage Decision Tables

```bash
# List all active decision tables (with UsageType)
cci task run manage_decision_tables --operation list

# Validate project list anchors against the org
cci task run manage_decision_tables --operation validate_lists

# Refresh all decision tables (full or incremental)
cci task run manage_decision_tables --operation refresh
# Or use the flow: cci flow run refresh_all_decision_tables
```
Decision table activate/deactivate and expression set version activation use CCI tasks only; the former SFDMU data plans for these have been removed.

## Troubleshooting

### Fixing a global pip install (Robot / Document Builder)

If you installed Robot Framework or SeleniumLibrary with `pip install` and got a warning about modifying the global environment:

1. Uninstall from the Python you used:
   ```bash
   python3 -m pip uninstall -y robotframework-seleniumlibrary robotframework webdriver-manager
   ```
2. Install them into CumulusCI's environment so the `enable_document_builder_toggle` task can run the `robot` command. If you use **pipx** for CumulusCI:
   ```bash
   pipx inject cumulusci robotframework robotframework-seleniumlibrary webdriver-manager "urllib3>=1.26,<2"
   ```
3. Confirm with prerequisite-free checks (see [Verify installations](#4-verify-installations) — "Document Builder (Robot) env only"): `~/.local/pipx/venvs/cumulusci/bin/robot --version` and `~/.local/pipx/venvs/cumulusci/bin/python -c "import SeleniumLibrary; print('SeleniumLibrary OK')"`. Once the org is ready, run the task to confirm end-to-end.

### Document Builder: "Timeout value connect was &lt;object object at ...&gt;"

This comes from a Selenium/urllib3 2.x compatibility issue: urllib3 2.x validates that HTTP timeouts are int/float/None, but webdriver-manager (used when opening the browser) can pass an invalid value, so the environment running Robot must use urllib3 < 2. Pin urllib3 to 1.x in CCI's environment:

```bash
pipx inject cumulusci "urllib3>=1.26,<2" --force
```

Use `--force` if pipx says urllib3 is already injected. To avoid this from the start, install Robot deps from `robot/requirements.txt` in the same environment you use for CCI. Then re-run the Document Builder task or flow.

### CumulusCI Not Found

```bash
# Install CumulusCI (prefer pipx to avoid global Python install)
pipx install cumulusci
# If you don't use pipx, use a virtual environment first, then: pip install cumulusci

# Verify installation
cci version
```

### SFDMU Not Found or Outdated

```bash
# Install or update SFDMU (v5+ required)
sf plugins install sfdmu

# Verify installation (should show 5.x)
sf plugins list
```

The `validate_setup` task checks and auto-updates SFDMU when `auto_fix=true` (the default):
```bash
cci task run validate_setup
```

### SFDMU Duplicate Records on Re-run

If you see duplicate records after running data tasks multiple times, verify you are on
SFDMU v5. The data plans have been migrated for v5 idempotency; v4.x may create duplicates
due to differences in how composite `externalId` definitions are processed. See
[Composite Key Optimizations](docs/sfdmu_composite_key_optimizations.md) for details.

### Permission Set Groups stuck Outdated / Updating

- After assigning permission set licenses or deploying PSG metadata, the platform may queue recalculation. The `recalculate_permission_set_groups` task waits with an initial delay, polls for Updated status, and retries with a delay on timeout (see `initial_delay_seconds`, `retry_count`, `retry_delay_seconds`, `post_trigger_delay_seconds` in `cumulusci.yml`). If you still hit timeouts, increase those options or run the flow again once the org has finished recalculating.

### Permission Errors

- Ensure your Salesforce user has appropriate permissions
- For scratch orgs, ensure Dev Hub is enabled
- Check org access: `sf org display`

### Deployment Errors

- Check feature flags in `cumulusci.yml` match your org's capabilities
- Review deployment logs for specific error messages
- Some features require specific licenses (e.g., Einstein, QuantumBit)

### Constraint Import Errors

- **MALFORMED_QUERY**: Product names with special characters (single quotes, backslashes) can cause SOQL issues. The CML utility automatically escapes these, but if you encounter this error, check that you're using the latest `tasks/rlm_cml.py`.
- **NOT_FOUND for ExpressionSetConstraintObj**: The target org may not have the RLM Constraints feature enabled. Enable it in Setup before running the import.
- **Could not resolve ReferenceObjectId**: The target org is missing products or PRC records that the constraint model references. Ensure the product data plan (e.g., `qb-pcm`) has been loaded first.

## Contributing

When contributing to this project:

1. Follow the existing code structure and patterns
2. Document custom tasks in `cumulusci.yml` and create example documentation
3. Test changes with appropriate scratch org configurations
4. Update this README if adding new prerequisites or workflows
5. Add detailed READMEs for new data plans
6. Register new tasks and flows in `cumulusci.yml`

## Branch Information

- **main**: Salesforce Release 260 (Spring '26, GA)
- Other branches exist for different release scenarios and preview features

## Additional Resources

- [CumulusCI Documentation](https://cumulusci.readthedocs.io/)
- [Salesforce CLI Documentation](https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/)
- [SFDMU Documentation](https://help.sfdmu.com/)
- [Revenue Cloud Developer Guide (Release 260)](https://developer.salesforce.com/docs/atlas.en-us.260.0.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/rlm_get_started.htm)
- [Revenue Cloud Help Documentation](https://help.salesforce.com/s/articleView?id=ind.revenue_lifecycle_management_get_started.htm&type=5)

**Note:** This project works with all Revenue Cloud capabilities documented in both the Developer Guide and Help Documentation for Release 260 (Spring '26).

## License

[Add your license information here]
