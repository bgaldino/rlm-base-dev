import time
from abc import abstractmethod

# ⚠ Guarded, matching tasks/rlm_apex_file.py and the pattern
# cci-orchestration/custom-task-authoring.md prescribes. Without this the module cannot
# be imported without CumulusCI installed, which broke the offline suite in
# tests/test_decision_table_tasks.py: it died on this import before a single check ran,
# while its docstring claimed no CumulusCI install was needed. The sibling
# rlm_manage_decision_tables.py already degraded this way; only this file did not.
try:
    import requests
    from cumulusci.tasks.sfdx import SFDXBaseTask
    from cumulusci.core.keychain import BaseProjectKeychain
    from cumulusci.core.utils import process_bool_arg
    from cumulusci.core.exceptions import CommandException
except ImportError:  # pragma: no cover - exercised only in the offline test environment
    requests = None
    SFDXBaseTask = object
    BaseProjectKeychain = object
    CommandException = Exception

    def process_bool_arg(arg):
        """Offline fallback for cumulusci.core.utils.process_bool_arg: same vocabulary,
        same TypeError on an uninterpretable value. NOT identical — CCI emits two
        DeprecationWarnings for None that this does not; both call sites pre-empt None
        with `or False`, so that path is unreachable either way."""
        if isinstance(arg, (int, bool)):
            return bool(arg)
        if arg is None:
            return False
        if isinstance(arg, str):
            if arg.lower() in ("yes", "y", "true", "on", "1"):
                return True
            if arg.lower() in ("no", "n", "false", "off", "0"):
                return False
        raise TypeError(f"Cannot interpret as boolean: `{arg}`")

CONNECTION_ATTEMPTS = 3


def queued_guidance(is_incremental):
    """What to check once a queued refresh completes. Kept identical to the copy in
    rlm_manage_decision_tables.py; tests/test_decision_table_tasks.py holds them together."""
    # ⚠ Release 264 chooses the refresh type itself unless incremental is requested
    # (AutoSelectRefreshDT, on by default): a "full" request can run as incremental, which
    # stamps LastIncrementalSyncDate and leaves LastSyncDate alone. So the guidance is the
    # same for both modes — judge completion by the later of the two stamps.
    requested = "an incremental" if is_incremental else "a full"
    return (
        f"Completion is asynchronous, and {requested} request does not fix the type that runs: "
        "a full refresh advances LastSyncDate, an incremental one only LastIncrementalSyncDate. "
        "AFTER the job completes, judge it by the later of the two."
    )


# ExtendStandardContext is a custom task that extends the SFDXBaseTask provided by CumulusCI.
class RefreshDecisionTable(SFDXBaseTask):

    # This task always needs an org. Without the flag, SFDXBaseTask leaves
    # salesforce_task False, the CLI builds no --org option, and every
    # refresh_dt_* task silently runs against the CCI DEFAULT org — so the
    # obvious remediation for a stale table (`cci task run refresh_dt_commerce
    # --org <alias>`) fails outright with "No such option: --org". Issue #320;
    # tests/test_cci_task_org_option.py now asserts the flag for every task.
    salesforce_task = True

    def _update_credentials(self):
        """
        Refresh the OAuth token before the task runs.

        ⚠ The flag above buys `--org`, NOT a token refresh. `SFDXBaseTask` descends from
        `Command`, which — unlike `SalesforceCommand` — never sets `salesforce_task`, and
        so inherits `BaseTask._update_credentials`, a bare `pass`. This task builds its
        own `Authorization: Bearer` header from `org_config.access_token`, and
        `_make_request` returns None on any non-2xx — so a token that failed to refresh
        would fail the DecisionTable status query, and with it the step.

        ⚠ Scope that risk honestly rather than restating it as a live danger. CCI wraps
        the sf CLI and leverages its auth, so every org here is an `SfdxOrgConfig` (or its
        `ScratchOrgConfig` subclass), which resolves `access_token` through `sfdx_info` —
        a `sf org display` behind a TTL cache — and is therefore always fresh. The
        stale-token shape needs a plain `OrgConfig` from `cci org connect`, which this
        project does not use; verified against the keychain 2026-07-27, zero plain
        `OrgConfig`. Insurance for the class, not a fix for anything seen here.
        """
        # save_if_changed, matching BaseSalesforceTask. Why there is no connected-app
        # handling: see the same method on ManageDecisionTables, which carries the single
        # record of this project's auth model rather than a second copy of it.
        with self.org_config.save_if_changed():
            self.org_config.refresh_oauth_token(self.project_config.keychain)

    # Task options are used to set up configuration settings for this particular task.
    task_options = {
        "access_token": {
            "description": "The access token for the org. Defaults to the project default",
        },
        "developerNames": {
            "description": "Required. API name of an active decision table that you want to refresh.",
            "required": True,
        },
        "isIncremental": {
            "description": "Specifies whether to trigger an incremental refresh (true) or not (false). If set to true, this field triggers an update only on changes made to the recent sObject data instead of performing a full refresh. An incremental refresh advances LastIncrementalSyncDate, not LastSyncDate. In Release 264, false lets the platform choose full or incremental itself.",
            "required": False,
        },
    }

    # Initialize the task options and environment variables    
    def _init_options(self, kwargs):
        super()._init_options(kwargs)
        self.env = self._get_env()

    # Load keychain with either the current keychain or generate a new one based on environment configuration
    def _load_keychain(self):
        if not hasattr(self, 'keychain') or not self.keychain:
            keychain_class = self.get_keychain_class() or BaseProjectKeychain
            keychain_key = self.get_keychain_key() if keychain_class.encrypted else None
            self.keychain = keychain_class(self.project_config or self.universal_config, keychain_key)
            if self.project_config:
                self.project_config.keychain = self.keychain

    # Prepare runtime by loading keychain and setting up access token and instance URL from options or defaults
    def _prep_runtime(self):
        self._load_keychain()
        self.access_token = self.options.get("access_token", self.org_config.access_token)
        self.instance_url = self.options.get("instance_url", self.org_config.instance_url)

    # Execute the task after preparation, where the core functionality will be implemented
    def _run_task(self):
        self._prep_runtime()
        
        # Debug: Print the type and content of self.options
        self.logger.info(f"Type of self.options: {type(self.options)}")
        self.logger.info(f"Content of self.options: {self.options}")

        # Check if self.options is a list (which it shouldn't be)
        if isinstance(self.options, list):
            raise TypeError("self.options is a list, but it should be a dictionary. This is likely a configuration issue.")

        # Safely get developerNames and isIncremental.
        # ⚠ process_bool_arg: CCI passes CLI options through as STRINGS, so
        # `-o isIncremental false` arrives as "false" — truthy — and would send a
        # non-boolean into a REST field documented as Boolean while logging the wrong
        # refresh mode. YAML callers pass a real bool and are unaffected.
        developer_names = self.options.get("developerNames")
        is_incremental = process_bool_arg(self.options.get("isIncremental") or False)

        # Debug: Print the values of developer_names and is_incremental
        self.logger.info(f"developer_names: {developer_names}")
        self.logger.info(f"is_incremental: {is_incremental}")

        # Check if developer_names is None or empty
        if not developer_names:
            raise ValueError("developerNames is required but was not provided or is empty")

        # Convert to list if it's a string.
        # ⚠ Split on commas. The flow always passes a real YAML list so this path is
        # latent there, but `cci task run refresh_dt_rating -o developerNames "A,B"`
        # otherwise asks the org to refresh one table literally named "A,B" — which
        # does not exist, so it would be skipped as missing below and the real tables
        # never refreshed. Same fix applied in rlm_manage_decision_tables.py.
        if isinstance(developer_names, str):
            developer_names = [part.strip() for part in developer_names.split(",") if part.strip()]
            if not developer_names:
                raise ValueError("developerNames was provided but contained no usable names")
        elif not isinstance(developer_names, list):
            raise ValueError(f"developerNames must be a string or a list of strings, but got {type(developer_names)}")

        # ⚠ Partition BEFORE refreshing, so the two failures this task used to conflate
        # get different handling. A configured table that is absent or inactive in this
        # org is a list/org mismatch — the cumulusci.yml lists are not org-scoped, and
        # refresh_dt_default_pricing runs unconditionally in refresh_all_decision_tables —
        # so it is skipped and reported, never fatal. A table that is active and still
        # does not queue is a real failure, and fails the task: before, every refresh
        # could fail and the step still exited 0.
        # De-duplicate first: each refresh draws on the org's hourly full-refresh pool.
        # DeveloperName matches case-insensitively in SOQL, so the lookup does too.
        seen = set()
        developer_names = [
            name for name in developer_names
            if not (name.lower() in seen or seen.add(name.lower()))
        ]
        found = self._query_decision_table_statuses(developer_names)
        missing, inactive, refreshable = [], [], []
        for name in developer_names:
            table = found.get(name.lower())
            if table is None:
                missing.append(name)
            elif table.get("Status") != "Active":
                inactive.append(f"{name} ({table.get('Status')})")
            else:
                # The org's spelling, not the caller's: SOQL matched case-insensitively,
                # and nothing establishes that the action does.
                refreshable.append(table["DeveloperName"])
        if missing:
            self.logger.warning(
                f"Skipping {len(missing)} decision table(s) not in this org: {', '.join(missing)}"
            )
        if inactive:
            self.logger.warning(
                f"Skipping {len(inactive)} decision table(s) that are not Active; refreshDecisionTable "
                f"needs an active table: {', '.join(inactive)}"
            )
        failed = []
        for name in refreshable:
            # ⚠ One table's exception must not abandon the tables after it.
            try:
                queued = self._refresh_decision_table(name, is_incremental)
            except Exception as exc:
                self.logger.error(f"Exception refreshing Decision Table '{name}': {exc}")
                queued = False
            if not queued:
                failed.append(name)
        self.logger.info(
            f"Refresh summary: {len(refreshable) - len(failed)} queued, "
            f"{len(failed)} not queued, {len(missing) + len(inactive)} skipped"
        )
        if failed:
            raise CommandException(
                f"Failed to queue a refresh for {len(failed)} decision table(s): {', '.join(failed)}"
            )

    def _query_decision_table_statuses(self, developer_names):
        """Return {lowercased DeveloperName: record} for the named tables in the org.

        Raises when the query itself fails: without it a missing table cannot be told
        apart from a failed refresh, and the refreshes would fail for the same reason.
        """
        quoted = ", ".join("'" + name.replace("\\", "\\\\").replace("'", "\\'") + "'" for name in developer_names)
        url, headers = self._build_url_and_headers("query")
        response = self._make_request(
            "get",
            url,
            headers=headers,
            params={"q": "SELECT DeveloperName, Status FROM DecisionTable "
                         f"WHERE DeveloperName IN ({quoted})"},
        )
        if not isinstance(response, dict) or "records" not in response:
            raise CommandException("Could not query DecisionTable to check which tables exist in this org")
        return {rec["DeveloperName"].lower(): rec for rec in response["records"]}

    # Core logic to refresh decision tables. Returns True only when the refresh queued.
    def _refresh_decision_table(self, developer_name, is_incremental):
        url, headers = self._build_url_and_headers("actions/standard/refreshDecisionTable")
        # ⚠ The action input is isDecisionTableIncremental. The action ignores an unknown
        # key, so the old `isIncremental` silently ran every incremental request as a full
        # refresh. The task option keeps its old name (issue #351).
        payload = {
            "inputs": [
                {
                    "decisionTableApiName": developer_name,
                    "isDecisionTableIncremental": is_incremental
                }
            ]
        }
        response = self._make_request("post", url, headers=headers, json=payload)
        if response:
            # Debug: Print the type and content of the response
            self.logger.info(f"Type of response: {type(response)}")
            self.logger.info(f"Content of response: {response}")

            # Handle the case where response is a list
            if isinstance(response, list):
                if len(response) > 0:
                    result = response[0]
                else:
                    self.logger.error(f"Empty response list for Decision Table '{developer_name}'")
                    return False
            elif isinstance(response, dict):
                result = response
            else:
                raise TypeError(f"Unexpected response type: {type(response)}")

            # Process the result.
            #
            # ⚠ isSuccess means the action was ACCEPTED, not that the table was rebuilt —
            # refreshDecisionTable is asynchronous. This used to print "Refresh Process
            # Success: True" and then "Refresh Status: Queued" on the very next line, a
            # self-contradicting pair that an operator scrolling a 32-step build log reads
            # as "done". This is the path EVERY refresh_dt_* task runs, so the honest
            # wording matters more here than in the manual task.
            #
            # ⚠ Fail closed on the status. Salesforce documents the output as Queued or
            # Failed, so treat only an explicit Queued as evidence of acceptance; a missing,
            # empty or unrecognised Status is NOT evidence and is reported as a failure.
            #
            # ⚠ Sentinel AFTER the strip. A whitespace-only Status is truthy, so
            # `or 'Unknown'` never fires and .strip() leaves '' — the operator reads
            # "Status:  (expected 'Queued')" and learns nothing. Kept identical to the
            # same gate in rlm_manage_decision_tables.py; the two must not drift.
            success = result.get('isSuccess')
            status = ((result.get('outputValues') or {}).get('Status') or '').strip() or 'Unknown'
            if success and status.lower() == 'queued':
                self.logger.info(
                    f"Refresh queued for Decision Table '{developer_name}' - Status: {status}. "
                    + queued_guidance(is_incremental)
                )
                return True
            elif success:
                self.logger.error(
                    f"Decision Table '{developer_name}' was accepted but reported "
                    f"Status: {status} (expected 'Queued'); treating as not queued. "
                    "If this is a new platform status rather than a failure, confirm with "
                    "check_decision_table_freshness once any queued job completes, then "
                    "extend the accepted set."
                )
            else:
                self.logger.error(f"Decision Table '{developer_name}' Refresh Process Failed")
                errors = result.get('errors', [])
                for error in errors:
                    if isinstance(error, dict):
                        self.logger.error(f"Error: {error.get('message', 'Unknown error')}")
                    else:
                        self.logger.error(f"Error: {error}")
        else:
            self.logger.error(f"No response received for Decision Table '{developer_name}'")
        return False

    # Helper to construct the request URL and headers for making API calls
    def _build_url_and_headers(self, endpoint):
        url = f"{self.instance_url}/services/data/v{self.project_config.project__package__api_version}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        return url, headers

    # Make an HTTP request using the requests library and handle the response
    def _make_request(self, method, url, **kwargs):
        # ⚠ Retry a dropped connection. A full build's refresh_dt_rating measured two
        # "Connection reset by peer" in 22 POSTs, and those tables stayed unrefreshed.
        # Resending a refresh is harmless: at worst the table is queued twice.
        for attempt in range(1, CONNECTION_ATTEMPTS + 1):
            try:
                response = requests.request(method, url, timeout=120, **kwargs)
                break
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exc:
                if attempt == CONNECTION_ATTEMPTS:
                    raise
                self.logger.warning(
                    f"{method.upper()} {url} failed ({exc}); retrying ({attempt}/{CONNECTION_ATTEMPTS - 1})"
                )
                time.sleep(2 * attempt)
        if response.ok:
            return response.json()
        else:
            self.logger.error(f"Failed {method.upper()} request to {url}: {response.text}")
            return None

    # Abstract method to get the keychain class, needs to be implemented by subclasses
    @abstractmethod
    def get_keychain_class(self):
        pass

    # Abstract method to retrieve the keychain key, needs to be implemented by subclasses
    @abstractmethod
    def get_keychain_key(self):
        pass
