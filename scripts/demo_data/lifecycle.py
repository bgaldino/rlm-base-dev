"""The transaction lifecycle, transcribed from the live-verified contracts.

Each function isolates one lifecycle step behind a single call so the rest of
the tool is endpoint/shape-agnostic. Bodies, response shapes, ordering hazards,
and async behavior are exactly as locked in ``scripts/demo_data/CONTRACTS.md``
(verified against ``rlm-base__jun17_1`` v67.0). When changing anything here,
re-verify against the org and update CONTRACTS.md in the same change.

Step ordering (hard barriers -- see CONTRACTS.md "Timing & Sequencing"):

    (opportunity) -> place(quote) -> create_order -> set_shipping_address
        -> activate_order -> [activation auto-generates BillingSchedule + Asset]

``set_shipping_address`` is MANDATORY before ``activate_order``:
createOrderFromQuote does not copy the account's shipping address, and
activation hard-fails FAILED_ACTIVATION without it.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Optional

from .auth import SfRestClient
from .discovery import Account, Product

log = logging.getLogger("demo_data.lifecycle")

# Account shipping fields copied onto the order before activation.
_SHIPPING_FIELDS = [
    "ShippingStreet", "ShippingCity", "ShippingState",
    "ShippingPostalCode", "ShippingCountry",
]

# Poll cadence for async/derived records (asset, billing schedule).
_POLL_INTERVAL = 5  # seconds between poll ticks


class LifecycleError(RuntimeError):
    """A lifecycle step failed in a way the run should surface, not swallow."""

    def __init__(self, step: str, detail: str, record_id: Optional[str] = None):
        self.step = step
        self.detail = detail
        self.record_id = record_id
        super().__init__(f"[{step}] {detail}" + (f" (id={record_id})" if record_id else ""))


@dataclass
class Manifest:
    """Source-of-truth record of everything a scenario created, by stage.

    Written even on partial failure (PST commits the quote header even when the
    place reports isSuccess:false), so cleanup can find orphans. ``run_id`` is
    the durable tag stamped on records and passed as invoice correlationId.
    """

    run_id: str
    opportunity_id: Optional[str] = None
    quote_id: Optional[str] = None
    order_id: Optional[str] = None
    order_number: Optional[str] = None
    billing_schedule_ids: list[str] = field(default_factory=list)
    asset_ids: list[str] = field(default_factory=list)
    invoice_id: Optional[str] = None
    invoice_number: Optional[str] = None
    reached_stage: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return dict(self.__dict__)


def _iso_today() -> str:
    return date.today().isoformat()


def _iso_days(days: int) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


def _sobject_path(client: SfRestClient, obj: str, record_id: str = "") -> str:
    base = f"/services/data/v{client.api_version}/sobjects/{obj}"
    return f"{base}/{record_id}" if record_id else base


# ---------------------------------------------------------------------------
# Step 1 -- Opportunity (optional head). Synchronous standard sObject create.
# ---------------------------------------------------------------------------
def create_opportunity(
    client: SfRestClient,
    account: Account,
    stage_name: str,
    run_id: str,
) -> str:
    body = {
        "Name": f"{run_id} Opportunity",
        "AccountId": account.id,
        "StageName": stage_name,
        "CloseDate": _iso_days(30),
        "Description": run_id,
    }
    result = client.post(_sobject_path(client, "Opportunity"), body)
    if not result or not result.get("success"):
        raise LifecycleError("opportunity", f"create failed: {result}")
    opp_id = result["id"]
    log.info("opportunity %s created", opp_id)
    return opp_id


# ---------------------------------------------------------------------------
# Step 2 -- Quote via Place Sales Transaction (PST). Synchronous (no polling).
# ---------------------------------------------------------------------------
def place_sales_transaction(
    client: SfRestClient,
    account: Account,
    product: Product,
    pricebook_id: str,
    run_id: str,
    quantity: int = 1,
    opportunity_id: Optional[str] = None,
    term_months: int = 12,
) -> str:
    """Place a quote. Returns the Quote id (salesTransactionId).

    Gotchas locked in CONTRACTS.md:
      * use QuoteAccountId (AccountId is not writable on the graph record)
      * do NOT send ProductSellingModelId on the line (FLS error)
      * term/subscription lines need StartDate + EndDate (else END_DATE_MISSING)
      * PST commits the Quote header even on isSuccess:false -> caller records
        the returned id for cleanup regardless.
    """
    quote_record: dict[str, Any] = {
        "attributes": {"method": "POST", "type": "Quote"},
        "Name": f"{run_id} Quote",
        "QuoteAccountId": account.id,
        "Pricebook2Id": pricebook_id,
        "Description": run_id,
    }
    if opportunity_id:
        quote_record["OpportunityId"] = opportunity_id

    line_record = {
        "attributes": {"method": "POST", "type": "QuoteLineItem"},
        "QuoteId": "@{refQuote.id}",
        "Product2Id": product.id,
        "PricebookEntryId": product.pricebook_entry_id,
        "Quantity": str(quantity),
        "StartDate": _iso_today(),
        "EndDate": _iso_days(term_months * 30),
    }

    body = {
        "pricingPref": "System",
        "taxPref": "Skip",
        "graph": {
            "graphId": "createQuote",
            "records": [
                {"referenceId": "refQuote", "record": quote_record},
                {"referenceId": "refQuoteLine0", "record": line_record},
            ],
        },
    }
    result = client.post(
        f"/services/data/v{client.api_version}/connect/rev/sales-transaction/actions/place",
        body,
    )
    quote_id = result.get("salesTransactionId") if isinstance(result, dict) else None
    if not result or not result.get("isSuccess"):
        errs = result.get("errorResponse") if isinstance(result, dict) else result
        raise LifecycleError("quote", f"PST place failed: {errs}", record_id=quote_id)
    log.info("quote %s placed", quote_id)
    return quote_id


# ---------------------------------------------------------------------------
# Step 3 -- Order via createOrderFromQuote standard action. Synchronous.
# ---------------------------------------------------------------------------
def create_order_from_quote(client: SfRestClient, quote_id: str) -> tuple[str, str]:
    """Returns (order_id, order_number). Quote must have QuoteAccountId set."""
    body = {"inputs": [{"quoteRecordId": quote_id}]}
    result = client.post(
        f"/services/data/v{client.api_version}/actions/standard/createOrderFromQuote",
        body,
    )
    entry = result[0] if isinstance(result, list) and result else None
    if not entry or not entry.get("isSuccess"):
        errs = entry.get("errors") if entry else result
        raise LifecycleError("order", f"createOrderFromQuote failed: {errs}")
    out = entry.get("outputValues", {})
    order_id = out.get("orderId")
    order_number = out.get("orderNumber")
    if not order_id:
        raise LifecycleError("order", f"no orderId in output: {entry}")
    log.info("order %s (%s) created", order_id, order_number)
    return order_id, order_number


# ---------------------------------------------------------------------------
# Step 3b -- Set shipping address (MANDATORY before activate). PATCH -> 204.
# ---------------------------------------------------------------------------
def set_shipping_address(client: SfRestClient, order_id: str, account: Account) -> None:
    """Copy the account's shipping address onto the order.

    createOrderFromQuote leaves the order's shipping address null, and
    activation hard-fails FAILED_ACTIVATION without it. We read the address off
    the account at call time (the discovery Account does not carry it).
    """
    recs = client.query(
        f"SELECT {', '.join(_SHIPPING_FIELDS)} FROM Account WHERE Id = '{account.id}'"
    )
    if not recs:
        raise LifecycleError("activate", f"account {account.id} not found for shipping")
    shipping = {f: recs[0].get(f) for f in _SHIPPING_FIELDS if recs[0].get(f)}
    if not shipping:
        raise LifecycleError(
            "activate",
            f"account {account.name} has no shipping address to copy onto the order",
        )
    client.patch(_sobject_path(client, "Order", order_id), shipping)
    log.info("order %s shipping address set (%s)", order_id, shipping.get("ShippingCity"))


# ---------------------------------------------------------------------------
# Step 4 -- Activate order. Plain Order.Status PATCH (NOT the connect endpoint).
# PATCH returns 204 empty body on success.
# ---------------------------------------------------------------------------
def activate_order(client: SfRestClient, order_id: str) -> None:
    client.patch(_sobject_path(client, "Order", order_id), {"Status": "Activated"})
    log.info("order %s activated", order_id)


# ---------------------------------------------------------------------------
# Step 5 (derived) -- poll for activation-generated BillingSchedule + Asset.
# ---------------------------------------------------------------------------
def poll_billing_schedules(
    client: SfRestClient,
    order_id: str,
    timeout: int = 180,
) -> list[str]:
    """Wait for activation to auto-generate BillingSchedule(s) for the order.

    Correlate by BillingSchedule.ReferenceEntityId = orderId. Treat Status
    'Error' as terminal failure; a timeout with zero rows is also a failure.
    """
    deadline = time.monotonic() + timeout
    soql = (
        "SELECT Id, Status FROM BillingSchedule "
        f"WHERE ReferenceEntityId = '{order_id}'"
    )
    while time.monotonic() < deadline:
        rows = client.query(soql)
        if rows:
            errored = [r["Id"] for r in rows if r.get("Status") == "Error"]
            if errored:
                raise LifecycleError(
                    "billing_schedule",
                    f"BillingSchedule in Error for order {order_id}: {errored}",
                    record_id=errored[0],
                )
            ids = [r["Id"] for r in rows]
            log.info("order %s generated %d billing schedule(s)", order_id, len(ids))
            return ids
        time.sleep(_POLL_INTERVAL)
    raise LifecycleError(
        "billing_schedule",
        f"no BillingSchedule for order {order_id} within {timeout}s",
        record_id=order_id,
    )


def poll_assets(
    client: SfRestClient,
    account: Account,
    product: Product,
    since_iso: str,
    timeout: int = 180,
) -> list[str]:
    """Wait for activation-generated Asset(s).

    Asset has no order FK, so correlate by account + product + a created-date
    window (CONTRACTS.md). ``since_iso`` is a SOQL datetime literal (UTC, e.g.
    2026-06-22T22:00:00Z) captured just before activation.
    """
    deadline = time.monotonic() + timeout
    soql = (
        "SELECT Id FROM Asset "
        f"WHERE AccountId = '{account.id}' AND Product2Id = '{product.id}' "
        f"AND CreatedDate >= {since_iso}"
    )
    while time.monotonic() < deadline:
        rows = client.query(soql)
        if rows:
            ids = [r["Id"] for r in rows]
            log.info("order assets: %d asset(s) for %s/%s", len(ids), account.name, product.sku)
            return ids
        time.sleep(_POLL_INTERVAL)
    # Assets are a nicety, not the billing gate -- log but don't hard-fail.
    log.warning(
        "no Asset for %s/%s within %ds (continuing)", account.name, product.sku, timeout
    )
    return []
