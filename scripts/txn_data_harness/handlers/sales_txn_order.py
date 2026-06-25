"""Direct-order PST handler (kind: ``sales_txn_order``).

Drives the direct-Order PST chain: place an Order via the same PST
``actions/place`` endpoint with Order/OrderAction/OrderItem graph entities
(no preceding Quote), then create the
``AppUsageType=RevenueLifecycleManagement`` ``AppUsageAssignment`` row that
gates the Revenue Cloud assetization pipeline. Without that row, the order
activates as a silent no-op (Status flips, but no BillingSchedule, no Asset,
no AsyncOperationTracker fires) -- ``createOrderFromQuote`` writes it
implicitly on the quote path, so the order path has to do it explicitly.

The lifecycle differs from :class:`SalesTxnQuoteHandler` only at the head
-- the post-Order tail (``order_activated -> usage_upload -> invoice_draft ->
invoice_posted``) is shared via :class:`SalesTransactionBaseHandler`.

Live-verified contract: ``docs/contracts-sales-txn-order.md`` (R262, API v67.0).
"""

from __future__ import annotations

from typing import ClassVar

from ..models import STAGES_ORDER
from .sales_transaction_base import SalesTransactionBaseHandler


class SalesTxnOrderHandler(SalesTransactionBaseHandler):
    """PST handler for the direct-Order path.

    ``STAGES_ORDER`` omits ``quote_placed`` -- the order-path skips the Quote
    step entirely. ``STEP_GRAPH`` maps the public ``order_draft`` stage to
    the ``order_direct`` step, which places the Order + writes the
    AppUsageAssignment row in one step.
    """

    kind: ClassVar[str] = "sales_txn_order"
    STAGES: ClassVar[list[str]] = STAGES_ORDER
    STEP_GRAPH: ClassVar[dict[str, str]] = {
        "order_draft": "order_direct",
    }
