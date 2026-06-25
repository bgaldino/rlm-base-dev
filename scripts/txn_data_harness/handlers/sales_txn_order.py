"""Direct-order PST handler (kind: ``sales_txn_order``) -- Phase 3 placeholder.

This handler drives the direct-Order PST chain: place an Order via the same
PST ``actions/place`` endpoint with Order/OrderItem graph entities (no
preceding Quote). Its lifecycle differs from :class:`SalesTxnQuoteHandler`
only at the head -- the post-Order tail (``order_activated -> usage_upload ->
invoice_draft -> invoice_posted``) is shared via
:class:`SalesTransactionBaseHandler`.

**Not registered yet.** :mod:`scripts.txn_data_harness.handlers.__init__` does
not include this handler in ``SCENARIO_HANDLERS`` and
:data:`scripts.txn_data_harness.config._VALID_KINDS` does not include
``sales_txn_order`` -- any YAML using ``kind: sales_txn_order`` fails at
parse time with the standard unknown-kind error. Both happen in Phase 3 once
the live PST direct-Order probe (Phase 0) characterizes the contract; see
``docs/contracts-sales-txn-order.md``.

The class exists now so Phase 2 can ship the handler-owned-execution refactor
without leaving an unreachable branch in the code -- it is importable,
type-checks, and trips ``order_direct``'s ``NotImplementedError`` if anyone
manually constructs it and calls ``run``.
"""

from __future__ import annotations

from typing import ClassVar

from ..models import STAGES_ORDER
from .sales_transaction_base import SalesTransactionBaseHandler


class SalesTxnOrderHandler(SalesTransactionBaseHandler):
    """PST handler for the direct-Order path.

    ``STAGES_ORDER`` omits ``quote_placed`` -- the order-path skips the Quote
    step entirely. ``STEP_GRAPH`` maps the public ``order_draft`` stage to
    the ``order_direct`` step, which is a Phase 3 stub raising
    ``NotImplementedError`` until the live probe ships.
    """

    kind: ClassVar[str] = "sales_txn_order"
    STAGES: ClassVar[list[str]] = STAGES_ORDER
    STEP_GRAPH: ClassVar[dict[str, str]] = {
        "order_draft": "order_direct",
    }
