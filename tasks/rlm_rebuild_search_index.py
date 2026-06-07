"""Custom CumulusCI task to rebuild the Product Catalog (PCM) search index.

Starts a catalog index build via the Connect REST API
(``connect/pcm/index/deploy``) -- the same operation the ``rlmRebuildSearchIndex``
LWC (``RLM_RebuildSearchIndex`` Apex) performs from the UI, but driven from the
build so the product catalog is searchable after ``prepare_rlm_org``.

The Apex path needs a Visualforce-page session id because a Lightning session
cannot call Connect APIs; a CCI task already holds a full API session
(``org_config.access_token``), so this task talks to the REST endpoint directly
and has no dependency on the Apex/VF page being deployed.

The index build is asynchronous: this task initiates it and logs the snapshot
id, but does not wait for the build to finish (matching the LWC behavior).
"""
try:
    from cumulusci.tasks.salesforce import BaseSalesforceApiTask
    from cumulusci.core.exceptions import CumulusCIException
    from cumulusci.core.utils import process_bool_arg
except ImportError:  # allow import without cumulusci (e.g. offline doc tooling)
    BaseSalesforceApiTask = object
    CumulusCIException = Exception

    def process_bool_arg(val):  # type: ignore[misc]
        return str(val).strip().lower() in ("true", "1", "yes")


PCM_INDEX_DEPLOY_PATH = "connect/pcm/index/deploy"


class RebuildSearchIndex(BaseSalesforceApiTask):
    """Initiate a Product Catalog (PCM) search index build.

    POSTs to ``connect/pcm/index/deploy`` to start a catalog index build. The
    build runs asynchronously on the platform (allow several minutes); this task
    only initiates it and reports the snapshot id, mirroring the
    ``rlmRebuildSearchIndex`` LWC. Run it after the catalog/decision-table data
    is in place (e.g. after ``refresh_all_decision_tables`` in
    ``prepare_rlm_org``).

    On a non-2xx response the task warns and continues by default so a transient
    index-API hiccup does not abort the whole build; set ``raise_on_failure`` to
    make a failure fatal.
    """

    task_options = {
        "build_type": {
            "description": "PCM index build type. Default: FULL.",
            "required": False,
        },
        "activation_type": {
            "description": "Snapshot activation type. Default: IMMEDIATE.",
            "required": False,
        },
        "raise_on_failure": {
            "description": (
                "If True, raise on a non-2xx response instead of warning and "
                "continuing. Default: False -- the catalog index can be rebuilt "
                "later via the Build Catalog Index component."
            ),
            "required": False,
        },
    }

    def _run_task(self):
        import requests

        build_type = self.options.get("build_type") or "FULL"
        activation_type = self.options.get("activation_type") or "IMMEDIATE"
        raise_on_failure = process_bool_arg(
            self.options.get("raise_on_failure", False)
        )

        api_version = self.project_config.project__package__api_version
        url = (
            f"{self.org_config.instance_url}/services/data/v{api_version}"
            f"/{PCM_INDEX_DEPLOY_PATH}"
        )
        headers = {
            "Authorization": f"Bearer {self.org_config.access_token}",
            "Content-Type": "application/json",
        }
        body = {
            "snapshot": {"activationType": activation_type},
            "buildType": build_type,
        }

        self.logger.info(
            f"Starting PCM catalog search index build "
            f"(buildType={build_type}, activationType={activation_type})..."
        )
        try:
            resp = requests.post(url, headers=headers, json=body, timeout=60)
        except requests.RequestException as e:
            return self._handle_failure(str(e), raise_on_failure)

        if 200 <= resp.status_code < 300:
            try:
                data = resp.json()
            except ValueError:
                data = {}
            snapshot = (data or {}).get("snapshot") or {}
            snapshot_id = snapshot.get("id")
            activation_status = snapshot.get("activationStatus")
            self.logger.info(
                f"PCM catalog search index build initiated (snapshot "
                f"{snapshot_id}, activationStatus={activation_status}). "
                "Completion is asynchronous; allow several minutes."
            )
            self.return_values = {
                "snapshot_id": snapshot_id,
                "activation_status": activation_status,
            }
            return self.return_values

        return self._handle_failure(
            f"HTTP {resp.status_code} - {resp.text}", raise_on_failure
        )

    def _handle_failure(self, detail, raise_on_failure):
        message = f"PCM catalog search index build could not be started: {detail}"
        if raise_on_failure:
            raise CumulusCIException(message)
        self.logger.warning(
            message
            + " -- continuing the build; rebuild manually via the "
            "'Build Catalog Index' component if needed."
        )
        self.return_values = {"snapshot_id": None, "activation_status": None}
        return self.return_values
