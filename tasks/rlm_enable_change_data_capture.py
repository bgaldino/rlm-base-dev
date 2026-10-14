"""Custom CumulusCI task to select Change Data Capture entities without breaking the build.

In 264, Change Data Capture (CDC) on Quote and Order is the only setup step for the Sales
Transaction Line Editor (STLE) and Transaction Summary to auto-refresh when a server-side
process (flow, Apex trigger, Agentforce action) changes the open quote or order.

CDC selections are ``PlatformEventChannelMember`` records on the ``ChangeEvents`` channel.
Without the CDC add-on an org can select at most five entities across all channels, and
unmanaged selections count toward that allocation. Deploying the members unconditionally
(for example from ``force-app``) would fail ``deploy_full`` on a persistent org that already
uses its allocation, so this task:

* reads the org's current selections through the Tooling API,
* adds only the requested entities that aren't selected yet,
* warns and continues, without failing the build, if anything goes wrong: the platform
  rejects a selection (for example because the allocation is used up), or the query or a
  create fails with an HTTP or network error.

Set ``raise_on_failure`` to make those failures fatal.
"""
try:
    from cumulusci.tasks.salesforce import BaseSalesforceApiTask
    from cumulusci.core.exceptions import CumulusCIException
    from cumulusci.core.utils import process_bool_arg, process_list_arg
except ImportError:  # allow import without cumulusci (e.g. offline doc tooling)
    BaseSalesforceApiTask = object
    CumulusCIException = Exception

    def process_bool_arg(val):  # type: ignore[misc]
        return str(val).strip().lower() in ("true", "1", "yes")

    def process_list_arg(val):  # type: ignore[misc]
        if val is None or isinstance(val, list):
            return val
        return [v.strip() for v in str(val).split(",") if v.strip()]


CHANNEL = "ChangeEvents"
DEFAULT_ENTITIES = ["Quote", "Order"]
DEFAULT_ALLOCATION = 5


def change_event_name(entity):
    """Return the change event name for an sObject (Quote -> QuoteChangeEvent)."""
    if entity.endswith("__c"):
        return entity[:-3] + "__ChangeEvent"
    return entity + "ChangeEvent"


class EnableChangeDataCapture(BaseSalesforceApiTask):
    """Select CDC entities on the ChangeEvents channel, skipping what's already selected.

    Each missing entity is created as a ``PlatformEventChannelMember`` through the Tooling
    API. Any failure (a rejected selection such as allocation used up or entity not
    supported, a failed query, or an HTTP or network error) is logged as a warning and the
    build continues, unless ``raise_on_failure`` is set.
    """

    task_options = {
        "entities": {
            "description": "sObjects to select for Change Data Capture. Default: Quote, Order.",
            "required": False,
        },
        "allocation": {
            "description": (
                "Selected-entity allocation used for the pre-check warning. Default: 5 "
                "(orgs without the CDC add-on). The platform is the final check."
            ),
            "required": False,
        },
        "raise_on_failure": {
            "description": (
                "If True, raise on any failure (rejected selection, failed query, HTTP or "
                "network error). Default: False: "
                "warn and continue, because a missing selection only disables STLE "
                "auto-refresh."
            ),
            "required": False,
        },
    }

    def _init_options(self, kwargs):
        super()._init_options(kwargs)
        self._parse_options()

    def _parse_options(self):
        self.entities = process_list_arg(self.options.get("entities")) or list(DEFAULT_ENTITIES)
        self.allocation = int(self.options.get("allocation") or DEFAULT_ALLOCATION)
        self.raise_on_failure = process_bool_arg(self.options.get("raise_on_failure", False))

    def _tooling_url(self, path):
        api_version = self.project_config.project__package__api_version
        return f"{self.org_config.instance_url}/services/data/v{api_version}/tooling/{path}"

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.org_config.access_token}",
            "Content-Type": "application/json",
        }

    def _selected_entities(self):
        """Return {channel: set(selectedEntity)} for every channel member in the org."""
        import requests

        resp = requests.get(
            self._tooling_url("query/"),
            headers=self._headers(),
            params={"q": "SELECT EventChannel, SelectedEntity FROM PlatformEventChannelMember"},
            timeout=60,
        )
        resp.raise_for_status()
        selected = {}
        for row in resp.json().get("records", []):
            selected.setdefault(row.get("EventChannel"), set()).add(row.get("SelectedEntity"))
        return selected

    def _run_task(self):
        import requests

        request_error = getattr(requests, "RequestException", Exception)
        try:
            selected = self._selected_entities()
        except request_error as exc:
            response = getattr(exc, "response", None)
            body = f" {response.text[:300]}" if response is not None and getattr(response, "text", "") else ""
            self._fail(f"Could not read the org's Change Data Capture selections: {exc}{body}")
            return
        on_channel = selected.get(CHANNEL, set())
        # Only change events count toward the CDC allocation; members of custom
        # platform-event channels can select other event types.
        all_entities = {
            e for entities in selected.values() for e in entities
            if e and e.endswith("ChangeEvent")
        }
        missing = [e for e in self.entities if change_event_name(e) not in on_channel]
        already = [e for e in self.entities if e not in missing]
        if already:
            self.logger.info(f"Already selected for Change Data Capture: {', '.join(already)}")
        if not missing:
            self.logger.info("Nothing to add.")
            return

        new_events = {change_event_name(e) for e in missing} - all_entities
        if len(all_entities) + len(new_events) > self.allocation:
            self.logger.warning(
                f"The org already selects {len(all_entities)} CDC entities; adding "
                f"{', '.join(missing)} may exceed the default allocation of {self.allocation}. "
                "Trying anyway (orgs with the CDC add-on allow more)."
            )

        failures = []
        for entity in missing:
            event = change_event_name(entity)
            body = {
                "FullName": f"{CHANNEL}_{event}",
                "Metadata": {"eventChannel": CHANNEL, "selectedEntity": event},
            }
            try:
                resp = requests.post(
                    self._tooling_url("sobjects/PlatformEventChannelMember/"),
                    headers=self._headers(),
                    json=body,
                    timeout=60,
                )
            except request_error as exc:
                failures.append(f"{entity}: {type(exc).__name__}: {exc}")
                continue
            if resp.status_code in (200, 201):
                self.logger.info(f"Selected {entity} for Change Data Capture ({event}).")
            else:
                failures.append(f"{entity}: HTTP {resp.status_code} {resp.text[:300]}")

        if failures:
            self._fail(
                "Could not select some entities for Change Data Capture; STLE auto-refresh "
                "won't work for them. Free up a CDC selection (Setup > Change Data Capture) "
                "or retry, then rerun this task. " + " | ".join(failures)
            )

    def _fail(self, message):
        """Raise when raise_on_failure is set; otherwise warn so the build continues."""
        if self.raise_on_failure:
            raise CumulusCIException(message)
        self.logger.warning(message)
