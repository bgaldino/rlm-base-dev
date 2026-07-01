"""Sales-transaction quote-path handler (kind: ``sales_txn_quote``).

PST chain: ``opportunity_created -> quote_placed -> order_draft ->
order_activated -> usage_upload -> invoice_draft -> invoice_posted`` with
``opportunity_created`` optional (prepended only when ``with_opportunity=True``
or the target stage is ``opportunity_created`` itself).

All execution logic -- stage math, retry-with-backoff, summary shape -- lives
on :class:`SalesTransactionBaseHandler`. This subclass only declares the
stages walked by the quote-path and the one public-stage -> internal-step
mapping that diverges from the 1:1 default.
"""

from __future__ import annotations

from typing import ClassVar

from .. import runner
from ..models import STAGES_QUOTE
from .sales_transaction_base import SalesTransactionBaseHandler


class SalesTxnQuoteHandler(SalesTransactionBaseHandler):
    """PST handler driving Opportunity -> Quote -> Order -> Activate -> Usage
    -> Invoice -> Post. Inherits :class:`SalesTransactionBaseHandler` for the
    stage math, retry loop, and PST-shaped summary; only declares its public
    stage list and the one diverging internal step name.
    """

    kind: ClassVar[str] = "sales_txn_quote"
    STAGES: ClassVar[list[str]] = STAGES_QUOTE
    # Only ``order_draft`` diverges from the public-stage name: the
    # quote-path creates the Order from a placed Quote, so the internal
    # step is ``order_from_quote``. Every other stage maps 1:1 by name
    # (see :meth:`SalesTransactionBaseHandler._internal_step`).
    STEP_GRAPH: ClassVar[dict[str, str]] = {
        "order_draft": "order_from_quote",
    }


# Legacy view of STEP_GRAPH: ``target_stage -> [public stages to walk]``.
# Built from :func:`runner.stage_sequence` so the canonical sequencing rule
# stays a single source of truth. Kept for back-compat with existing tests
# (``test_handlers.test_step_graph_matches_stage_sequence``).
STEP_GRAPH: dict[str, list[str]] = {
    stage: runner.stage_sequence(stage, with_opportunity=False)
    for stage in STAGES_QUOTE
}
