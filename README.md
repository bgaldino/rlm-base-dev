# Revenue Cloud Base Foundations

**Salesforce Release:** 260 (Spring '26)  
**API Version:** 66.0

This repository automates the creation and configuration of Salesforce environments that require Revenue Cloud (formerly Revenue Lifecycle Management) functionality.

The main branch targets Salesforce Release 260 (Spring '26, GA). Other branches exist for different release scenarios.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Custom Tasks](#custom-tasks)
- [Documentation](#documentation)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

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
   - Required for data loading tasks
   - Installation: `npm install -g sfdmu` or `sf plugins install sfdmu`
   - Verify: `sf sfdmu --version` or `sf plugins list`
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
   - Robot Framework, SeleniumLibrary, and webdriver-manager: keep them in the **same environment as CumulusCI** so the CCI task can run the `robot` command. If you use **pipx** for CumulusCI (recommended), inject into its environment (no global install):
     ```bash
     pipx inject cumulusci robotframework robotframework-seleniumlibrary webdriver-manager "urllib3>=1.26,<2"
     ```
     `urllib3>=1.26,<2` avoids a known Selenium/urllib3 2.x issue (`Timeout value connect was <object object at ...>`). webdriver-manager provides ChromeDriver automatically (no need to install ChromeDriver in PATH). If you previously installed these with `pip install` globally, uninstall first: `python3 -m pip uninstall -y robotframework-seleniumlibrary robotframework webdriver-manager`. If you use a project virtual environment instead of pipx for CCI, install there: `pip install robotframework robotframework-seleniumlibrary webdriver-manager "urllib3>=1.26,<2"` inside the venv.
   - Chrome (or set `BROWSER=firefox`). With webdriver-manager injected, ChromeDriver is downloaded automatically when the test runs; otherwise install ChromeDriver in PATH.
   - The task uses `sf org open --url-only` to authenticate the browser; ensure the Salesforce CLI (`sf`) is installed and the org is logged in.

3. **Install SFDMU:**
   ```bash
   # Option 1: Via npm
   npm install -g sfdmu
   
   # Option 2: Via Salesforce CLI plugin
   sf plugins install sfdmu
   ```

4. **Verify installations:**
   ```bash
   sf --version
   cci version
   sf plugins list  # Should show sfdmu if installed via plugin
   ```
   **Document Builder (Robot) env only — no org or flow required:** To confirm Robot and SeleniumLibrary are in CCI’s environment before running any flow or test:
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

### List Available Flows

```bash
cci flow list
```

### List Available Tasks

```bash
cci task list
```

## Custom Tasks

This project includes custom CumulusCI tasks for Revenue Cloud-specific operations. These tasks are located in the `tasks/` directory.

### Available Custom Tasks

| Task Name | Description | Documentation |
|-----------|-------------|--------------|
| `manage_decision_tables` | Decision Table management: list (with UsageType), query, refresh, activate, deactivate, validate_lists | [docs/DECISION_TABLE_EXAMPLES.md](docs/DECISION_TABLE_EXAMPLES.md) |
| `refresh_dt_rating`, `refresh_dt_rating_discovery`, `refresh_dt_default_pricing`, `refresh_dt_asset`, `refresh_dt_pricing_discovery`, `refresh_dt_commerce` | Refresh decision tables by category (use list anchors from `cumulusci.yml`) | [docs/DECISION_TABLE_EXAMPLES.md](docs/DECISION_TABLE_EXAMPLES.md) |
| `manage_flows` | Flow management (list, query, activate, deactivate) | [docs/TASK_EXAMPLES.md](docs/TASK_EXAMPLES.md) |
| `manage_expression_sets` | Expression Set management: list, query, activate/deactivate versions | [docs/TASK_EXAMPLES.md](docs/TASK_EXAMPLES.md) |
| `cleanup_settings_for_dev` | Conditionally remove unsupported settings for dev orgs | See `cumulusci.yml` |
| `exclude_active_decision_tables` | Exclude active decision tables from deployment | See `cumulusci.yml` |
| `assign_permission_set_groups_tolerant` | Assign PSGs with tolerance for missing permissions | See `cumulusci.yml` |
| `recalculate_permission_set_groups` | Recalculate permission set groups and wait for Updated status; supports initial delay, retries, and post-trigger delay for slow orgs | See `cumulusci.yml` |
| `load_sfdmu_data` / SFDMU tasks | Load data using SFDMU; DRO tasks use dynamic AssignedTo user from target org | See `cumulusci.yml` |
| `sync_pricing_data` | Sync pricing data | See `cumulusci.yml` |
| `extend_standard_context` | Extend standard context definitions | See `cumulusci.yml` |
| `manage_context_definition` | Modify context definitions via Context Service | [docs/context_service_utility.md](docs/context_service_utility.md) |
| `manage_transaction_processing_types` | Manage TransactionProcessingType records | [docs/constraints_setup.md](docs/constraints_setup.md) |
| `deploy_post_commerce` | Deploy Commerce metadata (e.g. Commerce decision table flows) | See `cumulusci.yml` |

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
```

For detailed examples and usage, see:
- [Decision Table Examples](docs/DECISION_TABLE_EXAMPLES.md)
- [Flow and Expression Set Examples](docs/TASK_EXAMPLES.md)

### Custom Task Development

Custom tasks are Python modules in the `tasks/` directory. They inherit from CumulusCI's `BaseTask` class and are automatically discovered by CumulusCI.

To add a new custom task:
1. Create a Python file in `tasks/` (e.g., `tasks/rlm_my_task.py`)
2. Define your task class inheriting from `BaseTask`
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

## Documentation

### Main Documentation Files

- **[DECISION_TABLE_EXAMPLES.md](docs/DECISION_TABLE_EXAMPLES.md)** - Comprehensive examples for Decision Table management
- **[TASK_EXAMPLES.md](docs/TASK_EXAMPLES.md)** - Examples for Flow and Expression Set management
- **[context_service_utility.md](docs/context_service_utility.md)** - Context Service utility usage and plan examples
- **[constraints_setup.md](docs/constraints_setup.md)** - Constraints deployment order and data plan notes
- **[TOOLING_OPPORTUNITIES.md](docs/TOOLING_OPPORTUNITIES.md)** - Analysis of Spring '26 features and opportunities for new tooling tasks

### Configuration Files

- **`cumulusci.yml`** - Main CumulusCI configuration with all tasks, flows, and project settings
- **`sfdx-project.json`** - Salesforce DX project configuration
- **`orgs/`** - Scratch org definition files for different scenarios

### Key Configuration Options

The project uses custom flags in `cumulusci.yml` to control feature deployment:

```yaml
custom:
  prm: false          # Partner Relationship Management
  tso: false         # Trialforce Source Org
  qb: true           # QuantumBit
  einstein: true     # Einstein AI
  visualization: false  # Visualization components
  quantumbit: true    # QuantumBit features
  # ... and more
```

Modify these flags in `cumulusci.yml` to enable/disable features during deployment.

## Project Structure

```
rlm-base-dev/
├── force-app/              # Main Salesforce metadata (source format)
├── unpackaged/             # Conditional metadata (deployed based on flags)
│   ├── pre/               # Pre-deployment metadata
│   ├── post_*/            # Post-deployment metadata (post_utils, post_commerce, etc.)
├── tasks/                 # Custom CumulusCI tasks (e.g. enable_document_builder_toggle)
├── robot/                 # Robot Framework tests for Document Builder toggle automation
│   └── rlm-base/
│       ├── resources/     # Keywords, WebDriverManager helper (ChromeDriver via webdriver-manager)
│       ├── tests/setup/   # enable_document_builder.robot; see robot/.../setup/README.md
│       └── results/       # Runtime output (gitignored; purge with rm -f robot/rlm-base/results/*)
├── orgs/                  # Scratch org definitions
├── datasets/              # SFDMU data sets (product, billing, tax, etc.)
│   └── sfdmu/             # SFDMU export configurations (no DT/expression set plans; use CCI tasks)
├── scripts/               # Utility scripts
│   ├── apex/             # Anonymous Apex scripts
│   ├── cml/              # CML scripts
│   └── bash/             # Bash scripts
├── cumulusci.yml         # CumulusCI configuration
├── sfdx-project.json     # Salesforce DX configuration
└── README.md             # This file
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

### Prepare Constraints

```bash
# Runs the constraints deployment flow
cci flow run prepare_constraints
```

See [docs/constraints_setup.md](docs/constraints_setup.md) for the current step order and required data plans.

### Load Test Data

```bash
# Load QuantumBit product data
cci task run insert_quantumbit_pcmdata_prod

# Load billing data
cci task run insert_billing_data
```

DRO data (prepare_dro flow) uses a single **qb-dro** data plan for both scratch and non-scratch orgs: the task replaces the placeholder `__DRO_ASSIGNED_TO_USER__` with the target org’s default user Name (e.g. "User User" in scratch orgs, "Admin User" in TSO) before loading. No separate scratch-specific DRO plan is required.

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
2. Install them into CumulusCI’s environment so the `enable_document_builder_toggle` task can run the `robot` command. If you use **pipx** for CumulusCI:
   ```bash
   pipx inject cumulusci robotframework robotframework-seleniumlibrary webdriver-manager "urllib3>=1.26,<2"
   ```
3. Confirm with prerequisite-free checks (see [Verify installations](#4-verify-installations) — “Document Builder (Robot) env only”): `~/.local/pipx/venvs/cumulusci/bin/robot --version` and `~/.local/pipx/venvs/cumulusci/bin/python -c "import SeleniumLibrary; print('SeleniumLibrary OK')"`. Once the org is ready, run the task to confirm end-to-end.

### Document Builder: "Timeout value connect was &lt;object object at ...&gt;"

This comes from a Selenium/urllib3 2.x compatibility issue. Pin urllib3 to 1.x in CCI’s environment:

```bash
pipx inject cumulusci "urllib3>=1.26,<2" --force
```

Use `--force` if pipx says urllib3 is already injected. Then re-run the Document Builder task or flow.

### CumulusCI Not Found

```bash
# Install CumulusCI (prefer pipx to avoid global Python install)
pipx install cumulusci
# If you don't use pipx, use a virtual environment first, then: pip install cumulusci

# Verify installation
cci version
```

### SFDMU Not Found

```bash
# Install SFDMU
npm install -g sfdmu
# OR
sf plugins install sfdmu

# Verify installation
sf plugins list
```

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

## Contributing

When contributing to this project:

1. Follow the existing code structure and patterns
2. Document custom tasks in `cumulusci.yml` and create example documentation
3. Test changes with appropriate scratch org configurations
4. Update this README if adding new prerequisites or workflows

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
