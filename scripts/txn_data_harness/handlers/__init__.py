"""Scenario handler registry.

``SCENARIO_HANDLERS`` maps a scenario ``kind`` string to its handler
singleton. Dispatch happens AFTER the defaults merge in ``config.py`` /
``generate.py`` -- the caller reads ``merged["kind"]`` (or
``manifest.kind`` on a resume) and looks up the handler here.
"""

from __future__ import annotations

from .base import ScenarioHandler
from .invoice_ingestion import InvoiceIngestionHandler
from .sales_transaction import SalesTransactionHandler

SCENARIO_HANDLERS: dict[str, ScenarioHandler] = {
    SalesTransactionHandler.kind: SalesTransactionHandler(),
    InvoiceIngestionHandler.kind: InvoiceIngestionHandler(),
}

__all__ = [
    "SCENARIO_HANDLERS",
    "ScenarioHandler",
    "InvoiceIngestionHandler",
    "SalesTransactionHandler",
]
