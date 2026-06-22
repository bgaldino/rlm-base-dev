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
import threading
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

# Assets carry no order/billing FK (CONTRACTS.md), so concurrent scenarios on
# the same account+product can only be told apart by which asset id each one
# claims first. This process-wide registry hands each asset id to exactly one
# scenario, so two manifests never record the same asset id. (Attribution is
# still best-effort -- a window match isn't a hard link -- but no duplicates.)
_claimed_asset_ids: set[str] = set()
_claimed_asset_lock = threading.Lock()


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

    Under concurrency, sibling scenarios on the same account+product share this
    query window, so we claim only asset ids no other scenario has taken yet
    (``_claimed_asset_ids``) -- preventing the same asset id landing in two
    manifests. Per-scenario attribution remains best-effort.
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
            with _claimed_asset_lock:
                ids = [r["Id"] for r in rows if r["Id"] not in _claimed_asset_ids]
                _claimed_asset_ids.update(ids)
            if ids:
                log.info("order assets: %d asset(s) for %s/%s", len(ids), account.name, product.sku)
                return ids
        time.sleep(_POLL_INTERVAL)
    # Assets are a nicety, not the billing gate -- log but don't hard-fail.
    log.warning(
        "no Asset for %s/%s within %ds (continuing)", account.name, product.sku, timeout
    )
    return []


# Invoice/BillingSchedule terminal-state sets (CONTRACTS.md picklists).
_INVOICE_FAIL = {"Error", "Split Error"}
_INVOICE_DRAFT_OK = {"Draft", "Split Draft"}
_INVOICE_POSTED_OK = {"Posted", "Split Posted"}


# ---------------------------------------------------------------------------
# Step 6a -- Generate invoice (Draft). Async, ~10-15s lag, NO statusURL.
# Correlate via InvoiceLine.BillingScheduleId; tag while still mutable.
# ---------------------------------------------------------------------------
def generate_invoice(
    client: SfRestClient,
    billing_schedule_ids: list[str],
    run_id: str,
    timeout: int = 180,
) -> tuple[str, str]:
    """Generate a Draft invoice from billing schedule(s); return (id, number).

    CONTRACTS.md: generate is async and returns only
    ``{requestIdentifier, success, errors}`` -- no statusURL, no tracker. The
    invoice row appears ~10-15s later. Correlate deterministically via
    ``InvoiceLine.BillingScheduleId`` (the id we passed in), NOT by
    ReferenceEntityId (null as-generated) or CorrelationIdentifier (not
    persisted).
    """
    if not billing_schedule_ids:
        raise LifecycleError("invoice", "no billing schedule ids to invoice")
    body = {
        "billingScheduleIds": billing_schedule_ids,
        "action": "Draft",
        "invoiceDate": _iso_today(),
        "targetDate": _iso_today(),
        "correlationId": run_id,
    }
    result = client.post(
        f"/services/data/v{client.api_version}/commerce/invoicing/invoices/collection/actions/generate",
        body,
    )
    if not result or not result.get("success"):
        errs = result.get("errors") if isinstance(result, dict) else result
        raise LifecycleError("invoice", f"generate failed: {errs}")

    # Poll for the generated invoice via the billing schedule back-link.
    bs_id = billing_schedule_ids[0]
    soql = (
        "SELECT InvoiceId, Invoice.Status, Invoice.InvoiceNumber "
        f"FROM InvoiceLine WHERE BillingScheduleId = '{bs_id}'"
    )
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        rows = client.query(soql)
        rows = [r for r in rows if r.get("InvoiceId")]
        if rows:
            inv = rows[0]
            invoice_id = inv["InvoiceId"]
            status = (inv.get("Invoice") or {}).get("Status")
            number = (inv.get("Invoice") or {}).get("InvoiceNumber")
            if status in _INVOICE_FAIL:
                raise LifecycleError(
                    "invoice", f"generated invoice in {status}", record_id=invoice_id
                )
            log.info("invoice %s generated (status=%s)", invoice_id, status)
            return invoice_id, number
        time.sleep(_POLL_INTERVAL)
    raise LifecycleError(
        "invoice",
        f"no invoice for billing schedule {bs_id} within {timeout}s",
        record_id=bs_id,
    )


def tag_invoice(client: SfRestClient, invoice_id: str, run_id: str) -> None:
    """Stamp run_id on the (Draft) invoice via Description.

    Description is PATCH-writable on both Draft and Posted invoices and survives
    posting, so the run_id pseudo-tag enables bulk cleanup by
    ``Description LIKE 'DEMO-%'``. The order FK (ReferenceEntityId) is NOT
    settable on Draft invoices (verified: "Can't change this field's value on
    Draft invoices") -- use ``link_invoice_to_order`` after posting for that.
    """
    client.patch(_sobject_path(client, "Invoice", invoice_id), {"Description": run_id})
    log.info("invoice %s tagged (%s)", invoice_id, run_id)


def link_invoice_to_order(client: SfRestClient, invoice_id: str, order_id: str) -> None:
    """Set Invoice.ReferenceEntityId -> Order so poll-by-orderId reads naturally.

    Optional/cosmetic: correlation already works via InvoiceLine.BillingScheduleId.
    ReferenceEntityId is only writable once the invoice is Posted (Draft rejects
    it), so call this AFTER post_invoice.
    """
    client.patch(
        _sobject_path(client, "Invoice", invoice_id),
        {"ReferenceEntityId": order_id},
    )
    log.info("invoice %s linked to order %s", invoice_id, order_id)


# ---------------------------------------------------------------------------
# Step 6b -- Post invoice. Returns statusURL -> AsyncOperationTracker.
# ---------------------------------------------------------------------------
def post_invoice(
    client: SfRestClient,
    invoice_id: str,
    run_id: str,
    timeout: int = 180,
) -> Optional[str]:
    """Post a Draft invoice and confirm completion; return the InvoiceNumber.

    CONTRACTS.md: post returns a ``statusURL`` to an AsyncOperationTracker
    (unlike generate). We poll that tracker to Completed; if no statusURL comes
    back, fall back to polling Invoice.Status = Posted. The human-readable
    InvoiceNumber is assigned at post time (null while Draft), so we read it
    back once posting completes.
    """
    body = {"invoiceIds": [invoice_id], "correlationId": run_id}
    result = client.post(
        f"/services/data/v{client.api_version}/commerce/invoicing/invoices/collection/actions/post",
        body,
    )
    if not result or not result.get("success"):
        errs = result.get("errors") if isinstance(result, dict) else result
        raise LifecycleError("post", f"post failed: {errs}", record_id=invoice_id)

    def _invoice_number() -> Optional[str]:
        rows = client.query(f"SELECT InvoiceNumber FROM Invoice WHERE Id = '{invoice_id}'")
        return rows[0].get("InvoiceNumber") if rows else None

    status_url = result.get("statusURL") if isinstance(result, dict) else None
    deadline = time.monotonic() + timeout
    if status_url:
        while time.monotonic() < deadline:
            tracker = client.get(status_url)
            tstatus = tracker.get("Status") if isinstance(tracker, dict) else None
            if tstatus == "Completed":
                number = _invoice_number()
                log.info("invoice %s posted (tracker Completed, %s)", invoice_id, number)
                return number
            if tstatus in ("Failed", "Error"):
                raise LifecycleError(
                    "post", f"post tracker {tstatus}", record_id=invoice_id
                )
            time.sleep(_POLL_INTERVAL)
    else:
        # Fallback: poll the invoice status directly.
        soql = f"SELECT Status, InvoiceNumber FROM Invoice WHERE Id = '{invoice_id}'"
        while time.monotonic() < deadline:
            rows = client.query(soql)
            status = rows[0].get("Status") if rows else None
            if status in _INVOICE_POSTED_OK:
                number = rows[0].get("InvoiceNumber")
                log.info("invoice %s posted (status=%s, %s)", invoice_id, status, number)
                return number
            if status in _INVOICE_FAIL:
                raise LifecycleError(
                    "post", f"invoice in {status} after post", record_id=invoice_id
                )
            time.sleep(_POLL_INTERVAL)
    raise LifecycleError(
        "post", f"post did not complete within {timeout}s", record_id=invoice_id
    )
