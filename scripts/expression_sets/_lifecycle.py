#!/usr/bin/env python3
"""The toolkit's adapter over the shared expression-set lifecycle engine.

The deactivate → mutate → recover state machine — the procedure-plan cascade, the
version-state transitions, the failure recovery and health report, and the delete
rollback — lives once, in :mod:`._engine` (``LifecycleCore``), shared with the CCI
task ``tasks/rlm_expression_set_connect.py``. :class:`LifecycleEngine` adapts it to
the toolkit: every read and write goes through the injected
:class:`_client.Transport`, failures raise :class:`LifecycleError`, and a dry-run is
the transport's (``Transport(dry_run=True)``): reads run, mutating verbs are logged
and skipped, so a preview logs the real mutation sequence; only the
activation-state polls are skipped. It also carries the Connect
GET/PATCH/POST/DELETE on the expression-set resource.

See ``LifecycleCore.run_mutation`` for the guarantees. The transport is the one
dependency, so a unit test can pass a fake and assert the call sequence without an
org.
"""

import time
from typing import Any, Callable, List

from ._client import CONNECT_BASE
from ._engine import LifecycleCore


class LifecycleError(RuntimeError):
    """Raised on an activation-lifecycle failure in the Expression Set toolkit."""


class LifecycleEngine(LifecycleCore):
    """Deactivate → mutate → reactivate engine over a :class:`_client.Transport`.

    ``transport`` is the only dependency: all Connect calls, SObject PATCHes, and
    SOQL reads route through it, so its ``dry_run``/``logger`` govern the whole
    engine and a test can inject a fake.
    """

    error_class = LifecycleError
    dry_run_style = "transport"

    def __init__(
        self,
        transport,
        *,
        logger: Callable[..., None] = None,
        max_wait_seconds: int = 45,
        poll_interval_seconds: int = 3,
    ):
        super().__init__(dry_run=transport.dry_run)
        self.t = transport
        self.log = logger or transport.logger
        self.max_wait = max(0, max_wait_seconds)
        self.poll = max(1, poll_interval_seconds)

    # -- Engine I/O hooks ------------------------------------------------

    def query(self, soql: str) -> List[dict]:
        return self.t.soql(soql)

    def write_sobject(self, sobject: str, record_id: str, body: dict) -> None:
        self.t.sobject("PATCH", sobject, record_id, body)

    def delete_sobject(self, sobject: str, record_id: str) -> None:
        self.t.sobject("DELETE", sobject, record_id)

    def delete_definition(self, es_id: str) -> Any:
        return self.delete_definition_connect(es_id)

    def emit(self, level: str, message: str) -> None:
        self.log(message)

    def command_target_org(self):
        """The --target-org this run was given, for printed remedy commands."""
        return getattr(self.t, "target_org", None)

    def restore_target_org(self):
        return getattr(self.t, "target_org", None)

    def wait_for_version_state(self, version_id: str, active: bool) -> None:
        """Poll until the version reaches ``IsActive=active`` (no-op under dry-run)."""
        if self.dry_run:
            return
        self.poll_version_state(version_id, active, max_wait=self.max_wait,
                                poll=self.poll, sleep=time.sleep)

    # -- Connect resource ops ------------------------------------------

    def get_definition(self, es_id: str) -> dict:
        """GET the full expression-set definition (reads always execute)."""
        resp = self.t.get(f"{CONNECT_BASE}/{es_id}")
        if isinstance(resp, list):
            resp = resp[0] if resp and isinstance(resp[0], dict) else {}
        return resp if isinstance(resp, dict) else {}

    def patch_definition(self, es_id: str, payload: dict) -> dict:
        """Connect PATCH (full-graph replace). Skipped+logged under dry-run."""
        return self.t.connect("PATCH", f"{CONNECT_BASE}/{es_id}", payload)

    def post_definition(self, payload: dict) -> dict:
        """Connect POST-create. Skipped+logged under dry-run."""
        return self.t.connect("POST", CONNECT_BASE, payload)

    def delete_definition_connect(self, es_id: str) -> Any:
        """Connect DELETE of the whole expression set. Skipped+logged under dry-run."""
        return self.t.connect("DELETE", f"{CONNECT_BASE}/{es_id}")

    # -- ResourceInitializationType alignment --------------------------

    def ensure_resource_initialization_type(self, es_id: str, desired=None) -> None:
        """Align stored ``ExpressionSet.ResourceInitializationType`` before a PATCH
        (``LifecycleCore.ensure_resource_initialization_type_impl``)."""
        self.ensure_resource_initialization_type_impl(es_id, desired)
