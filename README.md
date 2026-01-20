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
   - Installation: `pipx install cumulusci` or `pip install cumulusci`
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
   # OR
   pip install cumulusci
   ```

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
| `manage_decision_tables` | Comprehensive Decision Table management (list, query, refresh) | [DECISION_TABLE_EXAMPLES.md](DECISION_TABLE_EXAMPLES.md) |
| `manage_flows` | Flow management (list, query, activate, deactivate) | [TASK_EXAMPLES.md](TASK_EXAMPLES.md) |
| `manage_expression_sets` | Expression Set management with version control | [TASK_EXAMPLES.md](TASK_EXAMPLES.md) |
| `cleanup_settings_for_dev` | Conditionally remove unsupported settings for dev orgs | See `cumulusci.yml` |
| `exclude_active_decision_tables` | Exclude active decision tables from deployment | See `cumulusci.yml` |
| `assign_permission_set_groups_tolerant` | Assign PSGs with tolerance for missing permissions | See `cumulusci.yml` |
| `load_sfdmu_data` | Load data using SFDMU | See `cumulusci.yml` |
| `sync_pricing_data` | Sync pricing data | See `cumulusci.yml` |
| `extend_stdctx` | Extend standard context definitions | See `cumulusci.yml` |
| `modify_context` | Modify context definitions | See `cumulusci.yml` |

### Using Custom Tasks

All custom tasks are automatically available via CumulusCI. Use them like any standard CCI task:

```bash
# List decision tables
cci task run manage_decision_tables --operation list

# Manage flows
cci task run manage_flows --operation list --process_type ScreenFlow

# Manage expression sets
cci task run manage_expression_sets --operation list
```

For detailed examples and usage, see:
- [Decision Table Examples](DECISION_TABLE_EXAMPLES.md)
- [Flow and Expression Set Examples](TASK_EXAMPLES.md)

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

- **[DECISION_TABLE_EXAMPLES.md](DECISION_TABLE_EXAMPLES.md)** - Comprehensive examples for Decision Table management
- **[TASK_EXAMPLES.md](TASK_EXAMPLES.md)** - Examples for Flow and Expression Set management
- **[TOOLING_OPPORTUNITIES.md](TOOLING_OPPORTUNITIES.md)** - Analysis of Spring '26 features and opportunities for new tooling tasks

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
│   ├── post_*/           # Post-deployment metadata (feature-specific)
├── tasks/                 # Custom CumulusCI tasks
├── orgs/                  # Scratch org definitions
├── datasets/              # SFDMU data sets
│   └── sfdmu/            # SFDMU export configurations
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

### Load Test Data

```bash
# Load QuantumBit product data
cci task run insert_quantumbit_pcmdata_prod

# Load billing data
cci task run insert_billing_data
```

### Manage Decision Tables

```bash
# List all active decision tables
cci task run manage_decision_tables --operation list

# Refresh all decision tables
cci task run manage_decision_tables --operation refresh
```

## Troubleshooting

### CumulusCI Not Found

```bash
# Install CumulusCI
pipx install cumulusci
# OR
pip install cumulusci

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
