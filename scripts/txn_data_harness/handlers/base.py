"""Scenario handler protocol.

A handler owns the parse/discover/resolve/run pipeline for one ``kind`` of
scenario (today: ``sales_transaction``; PR 2+ adds ``invoice_ingestion``).
The dispatcher in ``generate.py`` / ``cli.py`` looks up
``SCENARIO_HANDLERS[merged["kind"]]`` after the defaults merge and delegates
through this protocol so each lifecycle stays in its own module instead of
spreading conditionals across the harness.
"""

from __future__ import annotations

from typing import ClassVar, Optional, Protocol, runtime_checkable

from ..auth import SfRestClient
from ..config import ScenarioSpec
from ..discovery import Account, OrgContext
from ..models import Manifest, ResolvedSpec


@runtime_checkable
class ScenarioHandler(Protocol):
    """Per-``kind`` entry points the dispatcher calls into.

    Implementations are stateless singletons registered in
    ``handlers/__init__.py`` as ``SCENARIO_HANDLERS[kind]``. The PST handler
    in PR 1 delegates to the existing free functions in ``runner.py`` /
    ``config.py`` -- no behavioral change. Future PRs replace the free
    functions with handler-owned implementations.
    """

    kind: ClassVar[str]

    def effective_stage(self, target_stage: str, account: Account) -> str:
        """Resolve the stage a scenario will actually reach.

        Implementations may cap the requested stage on this kind's rules
        (e.g. PST caps at ``order`` for non-billing accounts).
        """
        ...

    def stage_sequence(self, target_stage: str, with_opportunity: bool) -> list[str]:
        """Ordered list of step names this kind runs to reach ``target_stage``."""
        ...

    def remaining_steps(
        self, reached_stage: Optional[str], target_stage: str, with_opportunity: bool
    ) -> list[str]:
        """Steps still needed to reach ``target_stage`` from a checkpointed run."""
        ...

    def resolve(
        self, client: SfRestClient, ctx: OrgContext, spec: ScenarioSpec
    ) -> ResolvedSpec:
        """Bind a parsed spec's account/products to concrete org records."""
        ...

    def run(
        self,
        client: SfRestClient,
        ctx: OrgContext,
        run_id: str,
        resolved: ResolvedSpec,
        poll_timeout: int,
        max_retries: int,
    ) -> Manifest:
        """Drive one scenario through this kind's lifecycle."""
        ...
