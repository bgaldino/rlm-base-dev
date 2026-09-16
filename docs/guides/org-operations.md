# Org Operations

[Home](../../README.md) · [Documentation](../index.md) · [Local installation](local-installation.md)

Commands for building, configuring and troubleshooting Revenue Cloud environments.
Complete the [installation and access prerequisites](local-installation.md#prerequisites) first,
then run these commands from the repository root. Use a CumulusCI org alias with
CCI commands; Salesforce CLI aliases are a separate registry. Commands without
`--org` use the default CCI org, so confirm it before running a deployment.

- [Quick start](#quick-start)
- [Build harness and TUI](#build-harness-and-tui)
- [Task examples](#using-custom-tasks)
- [Common workflows](#common-workflows)
- [PRM Network email](#prm-network-email)
- [Troubleshooting](#troubleshooting)

For the full sequence, read the [build-process guide](prepare-rlm-org-build-guide.md).
Use the generated [task reference](../../.cursor/skills/cci-orchestration/tasks-reference.md),
[flow reference](../../.cursor/skills/cci-orchestration/flows-reference.md), and
[feature flags](../../.cursor/skills/cci-orchestration/feature-flags.md) for options,
flow definitions, and flag conditions.

## Quick Start

### Create a Scratch Org

```bash
# Create a basic dev scratch org
cci org scratch dev <org-alias>

# Create an enterprise scratch org (with additional features like SalesCloudEinstein)
cci org scratch ent <org-alias>
```

### Deploy to an Existing Org

```bash
# Register the existing org if it does not yet have a CCI alias
cci org connect <cci-alias>
# For a sandbox, add --sandbox to the connect command

# Set default org (an SF CLI alias alone cannot be used here)
cci org default <cci-alias>

# Run the main deployment flow
cci flow run prepare_rlm_org
```

### Reset default or target scratch org and run full flow

To remove your current default (or target) scratch org, create a new one, and run the full RLM prepare flow (includes billing data when applicable), use your scratch org config and alias (e.g. `beta`, `dev`, `ent`—see `orgs/` and `cumulusci.yml` under `orgs.scratch`):

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

## Build Harness and TUI

Use the local build harness to profile, resume, and report on `prepare_rlm_org`
runs across the standard `dev` and `ent` scratch org scenarios:

```bash
python scripts/build_harness/harness.py run
python scripts/build_harness/harness.py report --run-id <run_id>
```

For an interactive scratch org build manager, launch the Textual TUI from the
repo root:

```bash
./tui-cci
```

See [`docs/guides/build-harness.md`](../../docs/guides/build-harness.md) for the full
CLI/TUI workflow, run artifacts, resume behavior, and test commands.

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
- [Decision Table Examples](../../docs/references/decision-table-examples.md)
- [Flow and Expression Set Examples](../../docs/references/task-examples.md)
- [Constraints Utility Guide](../../datasets/constraints/README.md)

## Common Workflows

### Full Org Setup

```bash
# 1. Create scratch org using an existing definition
cci org scratch dev-sb0 my-org

# 2. Set as default
cci org default my-org

# 3. Run full deployment flow
cci flow run prepare_rlm_org
```

### Skip UX Assembly

```bash
# Run full flow without assembling/deploying any UX metadata (useful for isolated testing)
cci flow run prepare_rlm_org -o ux false
```

### Assemble and Deploy UX Metadata

```bash
# Assemble all UX metadata and deploy (same as step 29)
cci flow run prepare_ux

# Dry-run only — inspect unpackaged/post_ux/ without deploying
cci task run assemble_and_deploy_ux -o deploy false

# Regenerate and deploy a single flexipage by full filename
cci task run assemble_and_deploy_ux \
    -o metadata_name RLM_Quote_Record_Page.flexipage-meta.xml

# Assemble only layouts (no deploy)
cci task run assemble_and_deploy_ux -o metadata_type layouts -o deploy false
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

This will validate CML files, import all four constraint models (QuantumBitComplete, Server2, QuantumBitPCM, and QuantumBitBundle), then deactivate all four versions and activate **two** of them — `Server2_V1` and `QuantumBitBundle_V1`. QuantumBitComplete and QuantumBitPCM are imported but left inactive for A/B comparison. See [Constraints Setup](../../docs/guides/constraints-setup.md) for flow details.

### Export a Constraint Model

```bash
# Export from a source org to a local data plan directory
cci task run export_cml --org <source_org> \
    -o developer_name QuantumBitComplete \
    -o version 1 \
    -o output_dir datasets/constraints/qb/QuantumBitComplete
```

See the [Constraints Utility Guide](../../datasets/constraints/README.md) for full export/import/validate documentation.

### App Launcher order

```bash
# Capture the running user's order as a reference snapshot (writes templates/appMenus/base/; no deploy)
python scripts/sync_appmenu_from_user.py

# Apply the App Launcher order (runs as step 2 of prepare_ux on all ux=true orgs)
cci flow run prepare_ux --org <org>

# Apply the App Launcher order only, without the rest of prepare_ux
# (reorder_app_launcher orders by its priority_app_labels option via Aura saveOrder; assemble_and_deploy_ux
#  does NOT handle appMenus, and AppSwitcher can't deploy via the Metadata API when the AppMenu contains
#  managed ConnectedApp/Network entries — the Trialforce case)
cci org default <cci-alias>
cci task run reorder_app_launcher
```

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

1. **Step 1** (`deploy_post_billing`): Enable billing toggles (`enableInvoiceEmailDelivery`, `enableInvoicePdfGeneration` = `true`) and set `billingContextDefinition`
2. **Step 9** (`deploy_billing_id_settings`): Set context mapping, DPE definition names, and record IDs via XPath transforms; disable invoice toggles (`false`)
3. **Step 10** (`deploy_billing_template_settings`): Re-enable invoice toggles (`true`) to trigger Salesforce auto-creation of default invoice preview and document templates

The ID fields (`defaultBillingTreatment`, `defaultLegalEntity`, `defaultTaxTreatment`) use XPath transform SOQL queries to resolve org-specific record IDs at deploy time. The `billingContextDefinition` must be deployed in step 1 (before step 9) because `billingContextSourceMapping` requires it to already be persisted.

For **QuantumBit** (`dro=true`, `qb=true`), `prepare_dro` uses one **qb-dro**
plan for scratch and non-scratch orgs. `insert_qb_dro_data` replaces
`__DRO_ASSIGNED_TO_USER__` in `FulfillmentStepDefinition.csv`, `User.csv`, and
`UserAndGroup.csv` with the target org's default user Name before loading. No
separate scratch-specific **QuantumBit** DRO plan is required.

For **Q3** (`dro=true`, `q3=true`, `qb=false`), the flow selects
`insert_q3_dro_data_scratch` for scratch orgs and `insert_q3_dro_data_prod` for
non-scratch orgs. The QB path takes precedence when `qb=true`.

In `prepare_dro` step 5 → `update_product_fulfillment_decomp_rules`, an Apex
update applies the workaround for the Release 260 ExecuteOnRuleId-on-insert bug.
That step runs whenever `dro=true`. See the
[generated flow](../../.cursor/skills/cci-orchestration/flows-reference.md#prepare_dro)
for the complete sequence and conditions.

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

## PRM Network Email

The tracked `unpackaged/post_prm/force-app/main/default/networks/rlm.network-meta.xml`
stores `rlm-network-sender@example.com` as its sender placeholder. Never commit an
org's real sender address to this file.

For the Experience Bundle deployment, `prepare_prm` runs
`patch_network_email_for_deploy` → `deploy_post_prm` →
`revert_network_email_after_deploy` when `prm`, `prm_exp_bundle`, and `tso` are
enabled. The patch reads the existing Network's sender address, which is immutable
after creation, and substitutes it locally for deployment; the revert restores
the placeholder afterward. Community creation precedes the patch.

If deployment fails after the patch, restore the placeholder before committing:

```bash
cci task run revert_network_email_after_deploy
git diff -- unpackaged/post_prm/force-app/main/default/networks/rlm.network-meta.xml
```

See the [task implementations](../../tasks/rlm_community.py) and the
[generated PRM flow](../../.cursor/skills/cci-orchestration/flows-reference.md#prepare_prm)
for the full behavior and conditions.

## Troubleshooting

### Fixing a global pip install (headless robot tasks)

If you installed Robot Framework or SeleniumLibrary with `pip install` and got a warning about modifying the global environment:

1. Uninstall from the Python you used:
   ```bash
   python3 -m pip uninstall -y robotframework-seleniumlibrary robotframework selenium webdriver-manager
   ```
2. Install them into CumulusCI's environment so headless robot tasks can run. If you use **pipx** for CumulusCI:
   ```bash
   pipx inject cumulusci --force -r robot/requirements.txt
   ```
   For project-venv CCI, activate its venv and run `python -m pip install --upgrade -r robot/requirements.txt` instead.
3. Follow [setup validation for your CCI environment](local-installation.md#step-11--verify-the-full-setup). Robot and urllib3 auto-fixes target pipx only; venv users must install requirements in their venv and disable those auto-fixes. Once the org is ready, run the task to confirm end-to-end.

### Headless robot: Chrome/Chromium or ChromeDriver not found

Robot tasks run headless and require Chrome or Chromium plus ChromeDriver. Use the [validation command for your CCI environment](local-installation.md#step-11--verify-the-full-setup) to diagnose. Common fixes:

- **Chrome/Chromium missing:** Install per [Setup for headless robot runs](local-installation.md#setup-for-headless-robot-runs) (macOS: `brew install chromium`; Linux: `apt install chromium`).
- **ChromeDriver missing:** Install webdriver-manager in the CCI environment (`pipx inject cumulusci webdriver-manager` for pipx, or `python -m pip install webdriver-manager` inside the CCI venv) so it downloads ChromeDriver at runtime, or install chromedriver on PATH (e.g. `apt install chromium-driver` on Debian/Ubuntu).
- **CI:** Set `CHROME_BIN` to the browser path (e.g. `/usr/bin/chromium`).

### Document Builder: "Timeout value connect was &lt;object object at ...&gt;"

This is a Selenium 3.x / urllib3 2.x compatibility issue. Selenium 3.x passes `socket._GLOBAL_DEFAULT_TIMEOUT` (a sentinel `object()`) to `urllib3.PoolManager`, which urllib3 2.x rejects. This project requires `selenium>=4.10`, which does not have this issue — if you see this error, an older selenium may still be installed in the environment running CCI. For pipx, upgrade it:

```bash
pipx inject cumulusci --force -r robot/requirements.txt
```

The pipx `--force` flag replaces already-installed packages. For project-venv CCI, activate the venv and run `python -m pip install --upgrade -r robot/requirements.txt` instead. Then re-run the Document Builder task or flow.

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
# Install or update SFDMU (v5.6.4+ required)
sf plugins install sfdmu

# Verify installation (should show 5.6.4 or later)
sf plugins list
```

The `validate_setup` task checks and auto-updates SFDMU when `auto_fix=true` (the default):
```bash
cci task run validate_setup
```

### SFDMU Duplicate Records on Re-run

If you see duplicate records after reloading data, verify SFDMU v5.6.4 or later
and review the plan's operations and its required task/flow sequence. A compatible
plugin does not make every plan safe to rerun: Insert operations can duplicate
rows, and delete-and-reinsert plans can fail when live records block deletion.
See the [data-plan reloading guidance](data-plans.md#sfdmu-data-plans) and the
per-plan README before another run.

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
