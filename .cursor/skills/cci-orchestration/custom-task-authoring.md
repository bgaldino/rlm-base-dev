# Custom CCI Task Authoring Guide

How to write Python task classes for this CumulusCI project. All custom tasks
live in `tasks/` and are registered in `cumulusci.yml`.

---

## Base Class Selection

| Base Class | Import | Use When | Org Required? |
|------------|--------|----------|---------------|
| `BaseTask` | `from cumulusci.core.tasks import BaseTask` | Local tasks, Robot wrappers, org API via `self.org_config` | Depends |
| `SFDXBaseTask` | `from cumulusci.tasks.sfdx import SFDXBaseTask` | Tasks that call `sf` CLI or need `access_token`/`instance_url` | Yes |
| `BaseSalesforceTask` | `from cumulusci.tasks.salesforce import BaseSalesforceTask` | Deprecated — prefer `BaseTask` | Yes |
| `BaseSalesforceApiTask` | `from cumulusci.tasks.salesforce import BaseSalesforceApiTask` | Tasks using CCI's built-in REST client (`self.sf`) | Yes |
| `AnonymousApexTask` | `from cumulusci.tasks.apex.anon import AnonymousApexTask` | Run an Apex script file (no custom class needed) | Yes |
| `Deploy` | `from cumulusci.tasks.salesforce import Deploy` | Deploy metadata (no custom class needed) | Yes |
| `SalesforceCommand` | `from cumulusci.tasks.command import SalesforceCommand` | Run an `sf` CLI command directly | Yes |
| `Command` | `from cumulusci.tasks.command import Command` | Run a shell command | No |

### Decision tree

1. **No org needed** (local file ops, validation) → `BaseTask`
2. **Running Robot Framework tests** → `BaseTask` + subprocess Robot
3. **Calling REST/Connect/Tooling API directly** → `BaseTask` with manual
   `self.org_config.access_token` / `self.org_config.instance_url`
4. **Calling `sf` CLI** → `SFDXBaseTask` or `SalesforceCommand` (no class)
5. **Deploying metadata from a path** → `Deploy` (no class needed)
6. **Running Apex** → `AnonymousApexTask` (no class needed)

---

## Import Pattern

Always guard CCI imports with try/except so the module can be imported for
linting and testing without CCI installed:

```python
try:
    from cumulusci.tasks.sfdx import SFDXBaseTask
    from cumulusci.core.exceptions import TaskOptionsError, CommandException
    from cumulusci.core.keychain import BaseProjectKeychain
except ImportError:
    SFDXBaseTask = object
    TaskOptionsError = Exception
    CommandException = Exception
    BaseProjectKeychain = object
```

---

## Task Options

Options are declared as a class-level dict `task_options`:

```python
class MyTask(BaseTask):
    task_options = {
        "operation": {
            "description": "What to do: 'list', 'refresh', 'activate'",
            "required": True,
        },
        "developer_names": {
            "description": "List of DeveloperNames to operate on",
            "required": False,
        },
        "dry_run": {
            "description": "Preview without making changes",
            "required": False,
        },
    }
```

Access options in `_run_task` via `self.options`:

```python
def _run_task(self):
    operation = self.options.get("operation", "list")
    dev_names = self.options.get("developer_names", [])
    dry_run = self.options.get("dry_run", False)
```

Option values can be:
- Strings, booleans, numbers (scalar)
- Lists (YAML sequences) — accessed from `self.options` as Python lists
- YAML anchor references (`*anchor_name`) — resolved by YAML loader

---

## `_run_task()` — The Main Entry Point

CCI calls `_run_task()` to execute the task. All task logic goes here (or in
methods called from here).

### Pattern A: BaseTask with REST API

Most new tasks in this project use `BaseTask` and access the org directly:

```python
class ManageDecisionTables(BaseTask):
    task_options = { ... }

    def _run_task(self):
        operation = self.options.get("operation", "list")
        access_token = self.org_config.access_token
        instance_url = self.org_config.instance_url

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        # REST API call
        url = f"{instance_url}/services/data/v66.0/query/"
        params = {"q": "SELECT Id, DeveloperName FROM DecisionTable"}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        records = response.json().get("records", [])

        for record in records:
            self.logger.info(f"  {record['DeveloperName']}")
```

### Pattern B: SFDXBaseTask with manual keychain

Older tasks in this project use a boilerplate `_prep_runtime()` pattern:

```python
class RefreshDecisionTable(SFDXBaseTask):
    keychain_class = BaseProjectKeychain
    task_options = { ... }

    def _init_options(self, kwargs):
        super()._init_options(kwargs)
        self.env = self._get_env()

    def _load_keychain(self):
        if not hasattr(self, 'keychain') or not self.keychain:
            keychain_class = self.get_keychain_class() or BaseProjectKeychain
            keychain_key = (self.get_keychain_key()
                           if keychain_class.encrypted else None)
            self.keychain = keychain_class(
                self.project_config or self.universal_config, keychain_key
            )
            if self.project_config:
                self.project_config.keychain = self.keychain

    def _prep_runtime(self):
        self._load_keychain()
        self.access_token = self.options.get(
            "access_token", self.org_config.access_token
        )
        self.instance_url = self.options.get(
            "instance_url", self.org_config.instance_url
        )

    def _run_task(self):
        self._prep_runtime()
        # ... use self.access_token, self.instance_url
```

**For new tasks, prefer Pattern A** (`BaseTask` + `self.org_config`) — it's
simpler and doesn't need the keychain boilerplate.

### Pattern C: Robot Framework wrapper

Tasks that drive a browser use Robot Framework subprocess:

```python
class RunE2ETests(BaseTask):
    task_options = {
        "suite": {"description": "Robot test suite path", "required": False},
        "outputdir": {"description": "Output directory", "required": False},
        "headed": {"description": "Headed Chrome", "required": False},
    }

    def _run_task(self):
        cmd = ["python", "-m", "robot"]
        cmd.extend(["--variable", f"ORG:{self.org_config.username}"])
        cmd.extend(["--outputdir", self.options.get("outputdir", "results")])

        # Pass feature flags as Robot variables
        for flag in ["billing", "rating", "dro"]:
            val = self.project_config.project__custom.get(flag, False)
            cmd.extend(["--variable", f"{flag.upper()}:{val}"])

        cmd.append(self.options.get("suite", "robot/tests"))
        result = subprocess.run(cmd, cwd=str(Path.cwd()))
        if result.returncode != 0:
            raise CommandException(f"Robot exited with {result.returncode}")
```

### Pattern D: No org required

```python
class ValidateSetup(BaseTask):
    task_options = {
        "auto_fix": {"description": "Auto-fix issues", "required": False},
        "fail_on_error": {"description": "Raise on failure", "required": False},
    }

    def _run_task(self):
        # No self.org_config usage — runs without an org
        checks = []
        checks.append(self._check_python_version())
        checks.append(self._check_sf_cli())
        # ...
```

---

## Accessing Project Configuration

```python
# Feature flags
billing_enabled = self.project_config.project__custom__billing
tso_mode = self.project_config.project__custom__tso

# All custom settings as dict
custom = dict(self.project_config.config.get("project", {}).get("custom", {}))

# API version
api_version = self.project_config.project__package__api_version  # "66.0"
```

---

## REST API Patterns

### SOQL Query (REST)

```python
headers = {"Authorization": f"Bearer {self.org_config.access_token}"}
url = f"{self.org_config.instance_url}/services/data/v66.0/query/"
resp = requests.get(url, headers=headers, params={"q": soql})
resp.raise_for_status()
records = resp.json().get("records", [])
```

### Tooling API

```python
url = f"{self.org_config.instance_url}/services/data/v66.0/tooling/query/"
resp = requests.get(url, headers=headers, params={"q": tooling_soql})
```

### Connect API

```python
url = f"{self.org_config.instance_url}/services/data/v66.0/connect/..."
resp = requests.post(url, headers=headers, json=payload)
```

### PATCH/POST with error handling

```python
resp = requests.patch(url, headers=headers, json=body)
if resp.status_code >= 400:
    self.logger.error(f"API error {resp.status_code}: {resp.text}")
    raise TaskOptionsError(f"Failed: {resp.status_code}")
```

---

## Registering in `cumulusci.yml`

Every task must be registered with at minimum `group`, `description`, and
`class_path`:

```yaml
tasks:
  my_new_task:
    group: Revenue Lifecycle Management
    description: >
      One or two sentences describing exactly what objects/APIs are affected
      and what the task does. Be specific.
    class_path: tasks.my_module.MyTaskClass
    options:
      operation: list
```

### Task groups used in this project

| Group | Purpose |
|-------|---------|
| `Revenue Lifecycle Management` | Core RLM tasks (deploy, configure, create) |
| `Data Maintenance` | Delete/reset data plans |
| `Data Management - Extract` | Extract data from org to CSV |
| `Data Management - Idempotency` | Idempotency tests |
| `UX Personalization` | Flexipage/layout/profile assembly |
| `E2E Testing` | Robot Framework UI tests |
| `Partner Relationship Management` | PRM-specific tasks |

---

## Existing Task Modules Index

| Module | Classes | Purpose |
|--------|---------|---------|
| `rlm_sfdmu.py` | `LoadSFDMUData`, `ExtractSFDMUData`, `DeleteSFDMUData`, `TestSFDMUIdempotency` | SFDMU data operations |
| `rlm_extend_stdctx.py` | `ExtendStandardContext` | Extend standard context definitions |
| `rlm_context_service.py` | `ManageContextDefinition` | Context definition management via Connect API |
| `rlm_refresh_decision_table.py` | `RefreshDecisionTable` | Decision table refresh |
| `rlm_manage_decision_tables.py` | `ManageDecisionTables` | Comprehensive DT management |
| `rlm_manage_expression_sets.py` | `ManageExpressionSets` | Expression set version management |
| `rlm_manage_flows.py` | `ManageFlows` | Flow management (activate/deactivate) |
| `rlm_manage_transaction_processing_types.py` | `ManageTransactionProcessingTypes` | TPT management via Tooling API |
| `rlm_ux_assembly.py` | `AssembleAndDeployUX` | Dynamic UX metadata assembly + deploy |
| `rlm_stamp_commit.py` | `StampGitCommit` | Git commit stamping into org |
| `rlm_validate_setup.py` | `ValidateSetup` | Local environment validation |
| `rlm_robot_e2e.py` | `RunE2ETests` | E2E Robot Framework test runner |
| `rlm_reorder_app_launcher.py` | `ReorderAppLauncher` | App Launcher reordering via Aura API |
| `rlm_analytics.py` | `EnableAnalyticsReplication` | Enable CRM Analytics replication |
| `rlm_configure_revenue_settings.py` | `ConfigureRevenueSettings` | Revenue Settings page configuration |
| `rlm_enable_document_builder_toggle.py` | `EnableDocumentBuilderToggle` | Enable Document Builder toggle |
| `rlm_enable_constraints_settings.py` | `EnableConstraintsSettings` | Configure constraint engine settings |
| `rlm_community.py` | `PatchNetworkEmailForDeploy`, `RevertNetworkEmailAfterDeploy`, `PatchPaymentsSiteForDeploy`, `RevertPaymentsSiteAfterDeploy` | Network/site file patching |
| `rlm_cleanup_settings.py` | `CleanupSettingsForDev` | Remove unsupported settings before deploy |
| `rlm_apex_file.py` | `FileBasedAnonymousApexTask` | Run Apex from file (handles large scripts) |
| `rlm_docgen.py` | `FixDocumentTemplateBinaries` | Fix DocumentTemplate content binaries |
| `rlm_create_approval_email_templates.py` | `CreateApprovalEmailTemplates` | Create Lightning Email Templates via REST |
| `rlm_create_procedure_plan_def.py` | `CreateProcedurePlanDefinition`, `ActivateProcedurePlanVersion` | Procedure Plan via Connect API |
| `rlm_repair_pricing_schedules.py` | `EnsurePricingSchedules` | Ensure pricing schedules exist |
| `rlm_recalculate_permission_set_groups.py` | `RecalculatePermissionSetGroups` | PSG recalculation + polling |
| `rlm_assign_permission_set_groups.py` | `AssignPermissionSetGroupsTolerant` | PSG assignment with warning tolerance |
| `rlm_sync_pricing_data.py` | `SyncPricingData` | Sync pricing data |
| `rlm_reconfigure_expression_set.py` | `ReconfigureExpressionSet` | Reconfigure autoproc expression sets |
| `rlm_exclude_active_decision_tables.py` | `ExcludeActiveDecisionTables`, `RestoreDecisionTables` | Skip active DTs during deploy |
| `rlm_cml.py` | `ExportCML`, `ImportCML`, `ValidateCML` | Constraint Model Language operations |
| `rlm_modify_context.py` | (legacy) | Context modification helpers |
| `robot_utils.py` | (utilities) | Robot Framework utility functions |

---

## Coding Conventions

1. **No SOQL in loops** — batch-query before processing
2. **Bulk DML** — `update records;` not `update record;` in a loop
3. **Logging** — use `self.logger.info()`, `.warning()`, `.error()`
4. **Error handling** — raise `TaskOptionsError` for config errors,
   `CommandException` for runtime failures
5. **Namespace handling** — some objects require namespace prefixing in scratch
   orgs vs managed packages; check existing task patterns
6. **Non-fatal pattern** — for tasks like `stamp_git_commit` that should never
   break a flow, catch exceptions and log as warnings:
   ```python
   try:
       self._deploy()
   except Exception as exc:
       self.logger.warning(f"Non-fatal: {exc}")
   ```
