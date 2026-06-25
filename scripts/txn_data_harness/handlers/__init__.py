"""Scenario handler registry.

``SCENARIO_HANDLERS`` maps a scenario ``kind`` string to its handler
singleton. Dispatch happens AFTER the defaults merge in ``config.py`` /
``generate.py`` -- the caller reads ``merged["kind"]`` (or
``manifest.kind`` on a resume) and looks up the handler here.

PR 1 ships only ``sales_transaction``. PR 4 adds ``invoice_ingestion``.
"""

from __future__ import annotations

from .base import ScenarioHandler
from .sales_transaction import SalesTransactionHandler

SCENARIO_HANDLERS: dict[str, ScenarioHandler] = {
    SalesTransactionHandler.kind: SalesTransactionHandler(),
}

__all__ = ["SCENARIO_HANDLERS", "ScenarioHandler", "SalesTransactionHandler"]
