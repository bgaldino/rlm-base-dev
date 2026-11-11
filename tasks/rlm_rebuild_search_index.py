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

``CheckSearchIndexReadiness`` answers the question the rebuild leaves open: has the
index been built in this org, and did it complete? See its docstring for why the
answer comes from the build logs and not the index status.
"""
from datetime import datetime
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
PCM_INDEX_SNAPSHOTS_PATH = "connect/pcm/index/snapshots"

READY = "Ready"
NOT_BUILT_HERE = "Not built in this org"
BUILDING = "Building"
FAILED = "Failed"
NO_INDEX = "No index"


def _parse_time(value):
    """An API timestamp (``2026-10-27T22:18:30.000Z`` or ``…+0000``) as an aware datetime."""
    if not value or not isinstance(value, str):
        return None
    text = value.replace("Z", "+00:00")
    if len(text) > 5 and text[-5] in "+-" and text[-3] != ":":
        text = text[:-2] + ":" + text[-2:]  # +0000 -> +00:00, for fromisoformat
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None  # treated as undated, like a build still running


def index_readiness(snapshots_response, org_created):
    """
    The search index verdict for one org, from ``GET connect/pcm/index/snapshots``.

    Judged by the build LOGS of the active snapshot, not ``lastBuildStatus``: measured on a
    264 org, that field read IN_PROGRESS before, during and after a full rebuild that the
    logs show completing. A rebuild reuses the active snapshot: its log reads IN_PROGRESS
    with no completion time, then COMPLETED.

    A completed build counts only if it finished after the org was created. The entities
    behind this endpoint are org data, so a spun org may show the template's build for an
    index never built in it (unverified on a real spin; an org that copies none reads
    "No index", which is not Ready either).

    Returns (verdict, detail). ``org_created`` is the ``Organization.CreatedDate`` string.
    """
    created = _parse_time(org_created)
    if created is None:
        # Without it an inherited build would count as built here: the one false pass
        # this check exists to prevent.
        raise ValueError(f"Organization.CreatedDate is unreadable: {org_created!r}")
    snapshots = (snapshots_response or {}).get("snapshots") or []

    def logs_of(selected):
        return [log for snapshot in selected
                for index in snapshot.get("snapshotIndexes") or []
                for log in index.get("indexLogs") or []]

    def finished(log):
        return _parse_time(log.get("completionTime"))

    logs = logs_of([s for s in snapshots if s.get("activationStatus") == "ACTIVE"])
    # In flight: not terminal and not finished. A first build may run on a snapshot that
    # isn't active yet, so any snapshot counts except an expired one, whose builds are over.
    terminal = {"COMPLETED", "FAILED"}
    running = [l for l in logs_of([s for s in snapshots if s.get("activationStatus") != "EXPIRED"])
               if l.get("indexBuildStatus") not in terminal and not finished(l)]
    if not logs:
        if running:
            return BUILDING, "A build is in progress on a snapshot that is not active yet. Check again in a few minutes."
        return NO_INDEX, "No active snapshot has an index build on record. Run rebuild_search_index."

    dated = [l for l in logs if finished(l)]
    newest = max(dated, key=finished) if dated else None
    completed = [l for l in dated if l.get("indexBuildStatus") == "COMPLETED"]
    here = [l for l in completed if finished(l) > created]
    if here:
        latest = max(here, key=finished)
        detail = (f"{latest.get('indexBuildType', '?')} build completed "
                  f"{latest.get('completionTime')}, after the org was created ({org_created}).")
        if newest is not latest and newest.get("indexBuildStatus") != "COMPLETED":
            detail += (f" A later build ended {newest.get('indexBuildStatus')} at {newest.get('completionTime')} "
                       f"({newest.get('message') or 'no message'}); the completed one still serves.")
        return READY, detail
    if running:
        statuses = sorted({str(l.get("indexBuildStatus")) for l in running})
        return BUILDING, (f"A build is in progress ({', '.join(statuses)}) and none has completed in this org yet. "
                          "Check again in a few minutes.")
    if newest is not None and newest.get("indexBuildStatus") != "COMPLETED":
        # FAILED, or a terminal status this check doesn't know, named as reported.
        return FAILED, (f"The latest build ended {newest.get('indexBuildStatus')} at {newest.get('completionTime')}: "
                        f"{newest.get('message') or 'no message'}. Run rebuild_search_index.")
    if completed:
        latest = max(completed, key=finished)
        return NOT_BUILT_HERE, (f"The newest completed build ({latest.get('completionTime')}) predates the org "
                                f"({org_created}): it was inherited, not built here. Run rebuild_search_index.")
    return FAILED, "No build has completed. Run rebuild_search_index."


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


class CheckSearchIndexReadiness(BaseSalesforceApiTask):
    """Report whether the Product Catalog search index was built in this org and completed.

    Reads ``connect/pcm/index/snapshots`` and ``Organization.CreatedDate``; the verdict
    rules are in ``index_readiness``. Changes nothing. Pass ``strict`` to fail on any verdict
    other than Ready.
    """

    task_options = {
        "strict": {
            "description": "If True, fail unless the index is Ready. Default: False (report only).",
            "required": False,
        },
    }

    def _run_task(self):
        import requests

        strict = process_bool_arg(self.options.get("strict", False))
        api_version = self.project_config.project__package__api_version
        base = f"{self.org_config.instance_url}/services/data/v{api_version}"
        headers = {"Authorization": f"Bearer {self.org_config.access_token}"}

        resp = requests.get(f"{base}/{PCM_INDEX_SNAPSHOTS_PATH}", headers=headers,
                            params={"numberOfIndexLogs": 25}, timeout=60)
        if not 200 <= resp.status_code < 300:
            raise CumulusCIException(
                f"Could not read the search index snapshots: HTTP {resp.status_code} - {resp.text}")
        try:
            snapshots = resp.json()
        except ValueError:
            raise CumulusCIException(f"The search index snapshots response was not JSON: {resp.text[:500]}")
        org = requests.get(f"{base}/query", headers=headers,
                           params={"q": "SELECT CreatedDate FROM Organization"}, timeout=60)
        if not 200 <= org.status_code < 300:
            raise CumulusCIException(
                f"Could not read Organization.CreatedDate: HTTP {org.status_code} - {org.text}")
        try:
            created = org.json()["records"][0]["CreatedDate"]
        except (ValueError, KeyError, IndexError):
            raise CumulusCIException(f"Could not read Organization.CreatedDate from: {org.text[:500]}")

        try:
            verdict, detail = index_readiness(snapshots, created)
        except ValueError as e:
            raise CumulusCIException(str(e))
        except (AttributeError, TypeError) as e:
            raise CumulusCIException(f"Unexpected search index snapshots response ({e}): {resp.text[:500]}")
        log = self.logger.info if verdict == READY else self.logger.warning
        log(f"Search index: {verdict}. {detail}")
        self.return_values = {"verdict": verdict, "detail": detail}
        if strict and verdict != READY:
            raise CumulusCIException(f"Search index is not ready: {verdict}. {detail}")
        return self.return_values
