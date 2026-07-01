"""Scenario handler registry.

``SCENARIO_HANDLERS`` maps a scenario ``kind`` string to its handler
singleton. Dispatch happens AFTER the defaults merge in ``config.py`` /
``generate.py`` -- the caller reads ``merged["kind"]`` (or
``manifest.kind`` on a resume) and looks up the handler here.

Only handlers for kinds in :data:`scripts.txn_data_harness.config._VALID_KINDS`
are registered. The direct-Order PST contract is live-verified on R262; see
``docs/contracts-sales-txn-order.md``.
"""

from __future__ import annotations

from .base import ScenarioHandler
from .invoice_ingestion import InvoiceIngestionHandler
from .sales_txn_order import SalesTxnOrderHandler
from .sales_txn_quote import SalesTxnQuoteHandler

SCENARIO_HANDLERS: dict[str, ScenarioHandler] = {
    SalesTxnQuoteHandler.kind: SalesTxnQuoteHandler(),
    SalesTxnOrderHandler.kind: SalesTxnOrderHandler(),
    InvoiceIngestionHandler.kind: InvoiceIngestionHandler(),
}

__all__ = [
    "SCENARIO_HANDLERS",
    "ScenarioHandler",
    "InvoiceIngestionHandler",
    "SalesTxnOrderHandler",
    "SalesTxnQuoteHandler",
]
