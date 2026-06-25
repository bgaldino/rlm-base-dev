"""The transaction lifecycle, transcribed from the live-verified contracts.

Each function isolates one lifecycle step behind a single call so the rest of
the tool is endpoint/shape-agnostic. Bodies, response shapes, ordering hazards,
and async behavior are exactly as locked in ``scripts/txn_data_harness/CONTRACTS.md``
(verified against a Revenue Cloud R262 scratch org, API v67.0). When changing
anything here, re-verify against the org and update CONTRACTS.md in the same
change.

Step ordering (hard barriers -- see CONTRACTS.md "Timing & Sequencing"):

    (opportunity) -> place(quote) -> create_order -> set_shipping_address
        -> activate_order -> [activation auto-generates BillingSchedule + Asset]

``set_shipping_address`` is MANDATORY before ``activate_order``:
createOrderFromQuote does not copy the account's shipping address, and
activation hard-fails FAILED_ACTIVATION without it.
"""

from __future__ import annotations

import logging
import random
import time
from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional

from .auth import SfRestClient
from .discovery import Account, PostalAddress, Product
from .models import LineItem, ResolvedInvoiceLine, ResolvedInvoiceOverrides
from .term import Term

log = logging.getLogger("txn_data_harness.lifecycle")

# Account shipping fields copied onto the order before activation.
_SHIPPING_FIELDS = [
    "ShippingStreet", "ShippingCity", "ShippingState",
    "ShippingPostalCode", "ShippingCountry",
]

# Poll cadence for async/derived records (asset, billing schedule).
_POLL_INTERVAL = 5  # seconds between poll ticks

_BILLING_SCHEDULE_SUCCESS = {"ReadyForInvoicing", "CompletelyBilled"}


class LifecycleError(RuntimeError):
    """A lifecycle step failed in a way the run should surface, not swallow."""

    def __init__(self, step: str, detail: str, record_id: Optional[str] = None):
        self.step = step
        self.detail = detail
        self.record_id = record_id
        super().__init__(f"[{step}] {detail}" + (f" (id={record_id})" if record_id else ""))


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
    lines: list[LineItem],
    pricebook_id: str,
    run_id: str,
    opportunity_id: Optional[str] = None,
    start_date: Optional[date] = None,
) -> str:
    """Place a quote with one or more lines. Returns the Quote id.

    Each :class:`LineItem` becomes a QuoteLineItem in the place graph, so a
    scenario can place a **multi-line** quote (one referenceId per line). A
    line's ``discount_percent`` (0..100), when given, sets its ``Discount``
    (a standard percent field, createable). PST runs with ``pricingPref:
    "System"``, so the pricing engine *consumes* the discount and reflects it in
    the derived net prices, which flow through to the posted invoice. Verified
    live (CONTRACTS.md "Line discounts"): a 25% input drove QuoteLineItem
    ``NetUnitPrice`` to 337.50 (= 450 x 0.75) and the Posted Invoice
    ``TotalAmount`` to the discounted figure. NOTE: the engine does not
    round-trip the input onto ``QuoteLineItem.Discount`` -- that field reads back
    ``0`` post-place; the discount lives in the net prices, not that column.

    Gotchas locked in CONTRACTS.md:
      * use QuoteAccountId (AccountId is not writable on the graph record)
      * do NOT send ProductSellingModelId on the line (FLS error -- verified
        unwritable even as admin; the engine resolves the model from the PBE)
      * EndDate is selling-model-dependent (set by ``product.needs_end_date``):
        TermDefined REQUIRES it (else END_DATE_MISSING); Evergreen and OneTime
        REJECT it at createOrderFromQuote ("can't specify EndDate for
        evergreen/one-time order products"). StartDate is safe for all.
      * PST commits the Quote header even on isSuccess:false -> caller records
        the returned id for cleanup regardless.

    Term handling is per-line (see ``LineItem.term``). For TermDefined
    products the harness writes the author-input fields ``SubscriptionTerm`` +
    ``SubscriptionTermUnit`` -- the platform derives ``EndDate`` from
    ``StartDate`` + those two fields (live-verified on R262 against
    ``rlm-base__jun17_1``: input SubscriptionTerm=1 Annual + StartDate=2026-01-15
    read back as EndDate=2027-01-14, platform's inclusive ``start + term - 1
    day`` convention). The same input also drives platform recalculation of the
    auto-calc fields ``PricingTerm`` / ``PricingTermCount``; the harness writes
    neither.

    When ``line.end_date`` is set, the harness ALSO writes an explicit
    ``EndDate`` (resolved against the line's StartDate). The platform honors
    the override and prorates ``PricingTermCount`` against the actual span,
    e.g. an explicit Jan 15 -> Jan 15 next year (366 days) yields
    ``PricingTermCount = 366/365 = 1.0027`` instead of the derived 1.0. Used
    for co-terming a multi-line quote to a single calendar anchor.

    ``start_date`` (default today) sets every line's ``StartDate``; the
    platform anchors the TermDefined ``EndDate`` off it. Pass a
    per-transaction date to spread quotes over time.
    """
    if not lines:
        raise LifecycleError("quote", "no lines to place")
    start_iso = (start_date or date.today()).isoformat()
    quote_record: dict[str, Any] = {
        "attributes": {"method": "POST", "type": "Quote"},
        "Name": f"{run_id} Quote",
        "QuoteAccountId": account.id,
        "Pricebook2Id": pricebook_id,
        "Description": run_id,
    }
    if opportunity_id:
        quote_record["OpportunityId"] = opportunity_id

    records: list[dict[str, Any]] = [{"referenceId": "refQuote", "record": quote_record}]
    for i, line in enumerate(lines):
        line_record: dict[str, Any] = {
            "attributes": {"method": "POST", "type": "QuoteLineItem"},
            "QuoteId": "@{refQuote.id}",
            "Product2Id": line.product.id,
            "PricebookEntryId": line.product.pricebook_entry_id,
            "Quantity": str(line.quantity),
            "StartDate": start_iso,
        }
        # Only term-defined products take a term / EndDate. The runner is
        # responsible for ensuring TermDefined lines arrive with a Term and
        # non-TermDefined lines arrive with ``term is None``.
        if line.product.needs_end_date:
            if line.term is None:
                raise LifecycleError(
                    "quote",
                    f"TermDefined product '{line.product.sku}' has no resolved "
                    f"term; runner must populate LineItem.term",
                )
            line_record["SubscriptionTerm"] = line.term.count
            line_record["SubscriptionTermUnit"] = line.term.unit
            # Opt-in EndDate override: when set, the platform honors the
            # explicit date and prorates PricingTermCount against the
            # actual span (e.g. 366/365 == 1.0027 for a Jan 15 -> Jan 15
            # next year input). Without an override the platform derives
            # EndDate from StartDate + SubscriptionTerm (Branch A).
            if line.end_date is not None:
                line_start = start_date or date.today()
                line_record["EndDate"] = line.end_date.resolve(line_start).isoformat()
        if line.discount_percent is not None:
            line_record["Discount"] = line.discount_percent
        # Products with a proration policy require these at place time; not
        # derivable from the selling model, so they come from config per product.
        if line.period_boundary is not None:
            line_record["PeriodBoundary"] = line.period_boundary
        if line.billing_frequency is not None:
            line_record["BillingFrequency"] = line.billing_frequency
        records.append({"referenceId": f"refQuoteLine{i}", "record": line_record})

    body = {
        "pricingPref": "System",
        "taxPref": "Skip",
        "graph": {"graphId": "createQuote", "records": records},
    }
    result = client.post(
        f"/services/data/v{client.api_version}/connect/rev/sales-transaction/actions/place",
        body,
    )
    quote_id = result.get("salesTransactionId") if isinstance(result, dict) else None
    if not result or not result.get("isSuccess"):
        errs = result.get("errorResponse") if isinstance(result, dict) else result
        raise LifecycleError("quote", f"PST place failed: {errs}", record_id=quote_id)
    summary = ", ".join(
        f"{l.product.sku} x{l.quantity}"
        + (f" @{l.discount_percent}%off" if l.discount_percent is not None else "")
        + (
            f" term={l.term.count}{l.term.unit}"
            if l.term is not None
            else ""
        )
        for l in lines
    )
    log.info("quote %s placed (%d line(s): %s)", quote_id, len(lines), summary)
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
    expected_count: int = 1,
    timeout: int = 180,
) -> list[str]:
    """Wait for activation to auto-generate BillingSchedule(s) for the order.

    Correlate by BillingSchedule.ReferenceEntityId = orderId. Treat Status
    'Error' as terminal failure; only terminal success statuses unblock the
    invoice step. Multi-line orders can produce several schedules, so wait for
    the expected count instead of returning on the first row.
    """
    deadline = time.monotonic() + timeout
    soql = (
        "SELECT Id, Status FROM BillingSchedule "
        f"WHERE ReferenceEntityId = '{order_id}'"
    )
    expected_count = max(1, expected_count)
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
            ready = [
                r["Id"] for r in rows
                if r.get("Status") in _BILLING_SCHEDULE_SUCCESS
            ]
            if len(ready) >= expected_count:
                log.info(
                    "order %s generated %d/%d ready billing schedule(s)",
                    order_id, len(ready), expected_count,
                )
                return ready
        time.sleep(_POLL_INTERVAL)
    raise LifecycleError(
        "billing_schedule",
        f"fewer than {expected_count} ready BillingSchedule(s) for order "
        f"{order_id} within {timeout}s",
        record_id=order_id,
    )


def poll_assets(
    client: SfRestClient,
    order_id: str,
    timeout: int = 180,
) -> list[str]:
    """Wait for activation-generated Asset(s) attributable to ``order_id``.

    Asset has no direct order FK, but the data model exposes a deterministic
    one-hop linkage via AssetActionSource (CONTRACTS.md "Asset attribution"):

        Order -> OrderItem
              -> AssetActionSource.ReferenceEntityItemId
              -> AssetAction.AssetId
              -> Asset

    We query AssetActionSource rows whose ``ReferenceEntityItemId`` points at
    one of this order's OrderItems, filtered to ``CategoryEnum = 'Initial Sale'``
    so amendments/renewals/cancellations on the same OrderItem (under different
    CategoryEnum values) never bleed into an activation poll.

    Why this beats the prior account+product+created-date heuristic:

      * Bundles: a one-line input like QB-COMPLETE expands server-side into N
        component OrderItems with different Product2Ids. The old SOQL was keyed
        on the input line's Product2Id, so it never saw the component assets.
        Live: order 801WI00001HsyrdYAB produced 5 assets; the old poll captured
        1. The AAS path returns all 5.
      * Concurrency: the old SOQL also matched peer scenarios' assets in the
        same account+product+time window, and a process-global claim registry
        papered over duplicate ids at the cost of greedy over-attribution
        (peers timed out with empty asset_ids). The AAS path is per-order, so
        siblings on the same account+product never collide.
      * Replay/clock-skew: drops the client-side ``since_iso`` window entirely.

    Exit condition: ``expected_count`` is not derivable at call time -- bundles
    decouple OrderItem count from asset count, and ``count_order_items`` would
    over-count for any future scenario with non-asset-producing component
    OrderItems. Instead, the poll converges when the AAS-returned count is
    stable across two consecutive ``_POLL_INTERVAL`` ticks with count >= 1.
    Live timing measured against rlm-base__jun17_1 (2026-06-23): Asset created
    01:28:44, AAS created 01:28:45 (1s lag, simple case); same-second for the
    bundle case -- both well within one tick.

    LMA invariant: every Revenue Cloud activation produces LMA assets, so
    AssetActionSource is the complete picture -- no non-LMA escape hatch to
    worry about. An empty poll result means either the AAS write hasn't
    landed yet (handled by the stable-count loop) or activation itself
    didn't produce assets (an upstream contract violation, surfaced by the
    timeout warning).

    Failure mode: assets are best-effort relative to the billing gate, so
    the poll soft-fails on timeout (warn + return ``[]`` rather than raise).
    ``run_usage`` raises hard downstream if it can't pair a usage line,
    which is the right place for an empty-pool error to surface.
    """
    soql = (
        "SELECT AssetAction.AssetId FROM AssetActionSource "
        f"WHERE ReferenceEntityItemId IN ("
        f"SELECT Id FROM OrderItem WHERE OrderId = '{order_id}'"
        f") AND AssetAction.CategoryEnum = 'Initial Sale'"
    )
    deadline = time.monotonic() + timeout
    prev_ids: list[str] = []
    last_ids: list[str] = []
    while time.monotonic() < deadline:
        rows = client.query(soql)
        last_ids = [
            r["AssetAction"]["AssetId"]
            for r in rows
            if r.get("AssetAction") and r["AssetAction"].get("AssetId")
        ]
        if last_ids and len(last_ids) == len(prev_ids):
            log.info(
                "order %s assets: %d asset(s) attributed via AssetActionSource",
                order_id, len(last_ids),
            )
            return last_ids
        prev_ids = last_ids
        time.sleep(_POLL_INTERVAL)
    if not last_ids:
        log.warning(
            "no AssetActionSource rows for order %s within %ds -- AAS write "
            "may be delayed, or activation produced no assets (continuing)",
            order_id, timeout,
        )
    else:
        log.warning(
            "order %s asset count never stabilized within %ds; returning %d "
            "asset(s) from last poll (may be incomplete)",
            order_id, timeout, len(last_ids),
        )
    return last_ids


# ---------------------------------------------------------------------------
# Step 5b -- Usage consumption. Write TransactionJournal rows against the
# activated asset(s). Idempotent via deterministic ``UniqueIdentifier``.
# ---------------------------------------------------------------------------
_TJ_CHUNK = 200  # sObject Collections max records per call.


def count_order_items(client: SfRestClient, order_id: str) -> int:
    """Return the number of OrderItem rows on ``order_id``.

    ``createOrderFromQuote`` materializes one OrderItem per (bundle-expanded)
    QuoteLineItem, so this is the source of truth for "how many billing
    schedules and assets should activation produce" -- a bundle places as one
    input line but expands into many OrderItems server-side, and the input-line
    count under-counts the real downstream fan-out. Callers use this to set
    ``expected_count`` for the BillingSchedule and Asset polls.

    ``client.query`` strips the response's ``totalSize`` and only returns
    ``records``, so we use ``COUNT(Id) total`` to surface the count inside a
    record. Falls back to ``1`` if the query returns nothing -- activation
    against an empty Order is already a deterministic failure downstream.
    """
    rows = client.query(
        f"SELECT COUNT(Id) total FROM OrderItem WHERE OrderId = '{order_id}'"
    )
    if not rows:
        return 1
    return int(rows[0].get("total") or rows[0].get("expr0") or 1)


def fetch_assets_product_ids(
    client: SfRestClient, asset_ids: list[str]
) -> dict[str, str]:
    """Map ``Asset.Id -> Product2Id`` for the given assets.

    ``poll_assets`` returns ids ordered by id, not by quote-line order, so the
    usage step pairs assets to lines by ``Product2Id`` rather than by index.
    """
    if not asset_ids:
        return {}
    in_list = ", ".join(f"'{i}'" for i in asset_ids)
    rows = client.query(
        f"SELECT Id, Product2Id FROM Asset WHERE Id IN ({in_list})"
    )
    return {r["Id"]: r["Product2Id"] for r in rows if r.get("Product2Id")}


def _draw_float(rng: random.Random, lo: float, hi: float) -> float:
    if lo == hi:
        return lo
    return rng.uniform(lo, hi)


def _draw_int(rng: random.Random, lo: int, hi: int) -> int:
    if lo == hi:
        return lo
    return rng.randint(lo, hi)


def _spread_dates(now: datetime, count: int, days_back: int) -> list[date]:
    """Spread ``count`` ActivityDates evenly across the last ``days_back`` days.

    ``days_back == 0`` keeps every row on ``now.date()``. Otherwise the spread
    is deterministic given ``count`` and ``days_back`` -- last row is ``now``,
    first row is ``now - days_back``, intermediates linearly spaced -- so a
    retry under the same scheme produces the same dates.
    """
    today = now.date()
    if days_back <= 0 or count <= 1:
        return [today] * count
    step = days_back / (count - 1)
    return [today - timedelta(days=int(round(step * (count - 1 - i)))) for i in range(count)]


def create_usage_journals(
    client: SfRestClient,
    asset_id: str,
    account_id: str,
    line: LineItem,
    run_id: str,
    *,
    now: Optional[datetime] = None,
) -> list[str]:
    """Write TransactionJournal consumption rows for one asset/line.

    Emits ``records_per_line`` rows **per resolved usage target** (one resource
    binding => one set of rows; QB-DB resolves to two targets so we write two
    sets). Tags every row with a deterministic
    ``UniqueIdentifier = txn-harness-<run_id>-<asset_id>-<target_idx>-<row_idx>``
    so retries are idempotent: we pre-query existing identifiers and skip
    creates that already landed, returning ``existing_ids | new_ids`` so the
    manifest converges on the full id set across attempts.

    Posts via sObject Collections with ``allOrNone: true`` per chunk -- a bad
    chunk aborts cleanly and the retry path reuses the same identifiers.
    """
    spec = line.usage
    if spec is None or not spec.targets:
        return []
    if now is None:
        now = datetime.now(timezone.utc)
    rng = random.Random(f"{run_id}:{asset_id}")

    # Build the full expected (UniqueIdentifier, payload) set.
    expected: list[tuple[str, dict]] = []
    for t_idx, target in enumerate(spec.targets):
        n_rows = _draw_int(rng, *spec.records_per_line)
        dates = _spread_dates(now, n_rows, spec.days_back)
        for r_idx in range(n_rows):
            uid = f"txn-harness-{run_id}-{asset_id}-{t_idx}-{r_idx}"
            qty = _draw_float(rng, *spec.quantity)
            day_iso = dates[r_idx].isoformat()
            payload = {
                "attributes": {"type": "TransactionJournal"},
                "ReferenceRecordId": asset_id,
                "AccountId": account_id,
                "UsageResourceId": target.resource_id,
                "QuantityUnitOfMeasureId": target.uom_id,
                "Quantity": qty,
                "ActivityDate": day_iso,
                "StartDate": day_iso,
                "EndDate": day_iso,
                "UsageType": "UsageManagement",
                "Status": "Pending",
                "UniqueIdentifier": uid,
            }
            expected.append((uid, payload))

    if not expected:
        return []

    # Pre-flight: which UniqueIdentifiers already exist? Idempotent retry.
    expected_uids = [uid for uid, _ in expected]
    existing_by_uid: dict[str, str] = {}
    for i in range(0, len(expected_uids), _TJ_CHUNK):
        chunk = expected_uids[i:i + _TJ_CHUNK]
        in_list = ", ".join(f"'{u}'" for u in chunk)
        rows = client.query(
            f"SELECT Id, UniqueIdentifier FROM TransactionJournal "
            f"WHERE UniqueIdentifier IN ({in_list})"
        )
        for r in rows:
            existing_by_uid[r["UniqueIdentifier"]] = r["Id"]

    to_create = [p for uid, p in expected if uid not in existing_by_uid]
    new_ids: list[str] = []
    path = f"/services/data/v{client.api_version}/composite/sobjects"
    for i in range(0, len(to_create), _TJ_CHUNK):
        chunk = to_create[i:i + _TJ_CHUNK]
        result = client.post(path, {"allOrNone": True, "records": chunk})
        if not isinstance(result, list):
            raise LifecycleError(
                "usage",
                f"sObject Collections returned unexpected shape: {result!r}",
            )
        failures: list[dict] = []
        for entry in result:
            if entry.get("success"):
                new_ids.append(entry["id"])
            else:
                failures.append(entry)
        if failures:
            raise LifecycleError(
                "usage",
                f"TransactionJournal create failures ({len(failures)}/{len(chunk)}): "
                f"{failures[:3]}",
            )

    existing_ids = list(existing_by_uid.values())
    if existing_ids:
        log.info(
            "usage: reused %d existing TJ id(s) for asset %s",
            len(existing_ids), asset_id,
        )
    log.info(
        "usage: wrote %d new TJ row(s) for asset %s across %d target(s)",
        len(new_ids), asset_id, len(spec.targets),
    )
    return existing_ids + new_ids


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
    ``InvoiceLine.BillingScheduleId`` (the ids we passed in), NOT by
    ReferenceEntityId (null as-generated) or CorrelationIdentifier (not
    persisted).

    All schedules in one generate call land on a single Invoice (single-invoice
    per generate; see CONTRACTS.md). Poll via ``IN (…)`` across every schedule
    we submitted -- a bundle activates into one BillingSchedule per component
    and some slots can have ``TotalAmount = 0`` with no resulting InvoiceLine,
    so any one schedule is not a safe anchor.
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

    # Poll for the generated invoice via the billing schedule back-link across
    # all submitted schedules -- the first one to surface an InvoiceLine wins.
    in_list = ", ".join(f"'{i}'" for i in billing_schedule_ids)
    soql = (
        "SELECT InvoiceId, Invoice.Status, Invoice.InvoiceNumber "
        f"FROM InvoiceLine WHERE BillingScheduleId IN ({in_list})"
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
            if status in _INVOICE_DRAFT_OK:
                log.info("invoice %s generated (status=%s)", invoice_id, status)
                return invoice_id, number
        time.sleep(_POLL_INTERVAL)
    raise LifecycleError(
        "invoice",
        f"no invoice for {len(billing_schedule_ids)} billing schedule(s) within {timeout}s",
        record_id=billing_schedule_ids[0],
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

    status_url = result.get("statusURL") if isinstance(result, dict) else None
    deadline = time.monotonic() + timeout
    if status_url:
        _await_async_tracker(
            client, status_url, deadline, step="post", record_id=invoice_id
        )
        number = _query_invoice_number(client, invoice_id)
        log.info("invoice %s posted (tracker Completed, %s)", invoice_id, number)
        return number
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


def _query_invoice_number(client: SfRestClient, invoice_id: str) -> Optional[str]:
    rows = client.query(f"SELECT InvoiceNumber FROM Invoice WHERE Id = '{invoice_id}'")
    return rows[0].get("InvoiceNumber") if rows else None


def _await_async_tracker(
    client: SfRestClient,
    status_url: str,
    deadline: float,
    *,
    step: str,
    record_id: Optional[str] = None,
) -> None:
    """Poll an ``AsyncOperationTracker`` URL to ``Completed``.

    Shared by :func:`post_invoice` and :func:`ingest_invoice`; both endpoints
    return a ``statusURL`` pointing at the same tracker shape per CONTRACTS.md.
    Raises ``LifecycleError`` on a ``Failed``/``Error`` status or on timeout.
    """
    while time.monotonic() < deadline:
        tracker = client.get(status_url)
        tstatus = tracker.get("Status") if isinstance(tracker, dict) else None
        if tstatus == "Completed":
            return
        if tstatus in ("Failed", "Error"):
            raise LifecycleError(
                step, f"{step} tracker {tstatus}", record_id=record_id
            )
        time.sleep(_POLL_INTERVAL)
    raise LifecycleError(
        step, f"{step} did not complete within tracker deadline", record_id=record_id
    )


# ---------------------------------------------------------------------------
# Step 6c -- Ingest invoice via the Composite Graph ingest API.
# Bypasses Order/Quote/BillingSchedule entirely; used by the
# ``invoice_ingestion`` handler for standalone-billing demos. See plan
# "Standalone-Billing Invoice Ingestion path", Phase 1.
# ---------------------------------------------------------------------------
def ingest_invoice(
    client: SfRestClient,
    account: Account,
    lines: list[ResolvedInvoiceLine],
    run_id: str,
    *,
    status: str = "Draft",
    invoice_spec: Optional[ResolvedInvoiceOverrides] = None,
    timeout: int = 180,
) -> tuple[str, Optional[str], list[str]]:
    """POST a Composite-Graph-shaped Invoice to the ingest endpoint.

    Returns ``(invoice_id, invoice_number, invoice_line_ids)``. ``status`` is
    ``"Draft"`` or ``"Posted"``. Phase 1 invariant: never emits
    ``InvoiceLineTax`` records and always sets ``shouldCalculateTax: false`` --
    callers (the ingestion handler) reject ``taxable: true`` lines on Posted
    invoices at parse time so we never get here with one. The dev guide
    (R262/v67.0) caps the action body at one invoice per request; concurrency
    lives in the harness's thread pool.

    ``uniqueIdentifier`` is set to ``run_id`` so duplicate calls with the same
    run won't double-create. After the action returns ``statusURL``, polls the
    AsyncOperationTracker via :func:`_await_async_tracker` and then reads the
    persisted Invoice row back by ``UniqueIdentifier`` to recover the assigned
    id, number, and line ids.

    ``invoice_spec`` carries the scenario's ``invoice:`` overrides
    (``invoice_date``, ``due_date``, ``posted_date``, ``currency``,
    ``description``, ``tax_calculation_status``). ``None`` means all platform
    defaults; ``posted_date`` is defaulted to today on Posted status when the
    override is omitted.
    """
    if status not in ("Draft", "Posted"):
        raise LifecycleError(
            "ingest_invoice", f"invalid status '{status}' (must be Draft|Posted)"
        )
    if not lines:
        raise LifecycleError("ingest_invoice", "no invoice lines to ingest")

    spec = invoice_spec or ResolvedInvoiceOverrides()

    # Phase 1 tax invariant -- a defensive belt for the parse-time check on the
    # handler. If anything sneaks past parsing the harness must NOT silently
    # ship a tax-on payload to the org.
    if spec.should_calculate_tax:
        raise LifecycleError(
            "ingest_invoice",
            "Phase 1 invariant: shouldCalculateTax must be false (InvoiceLineTax not implemented)",
        )
    if status == "Posted" and any(l.taxable for l in lines):
        raise LifecycleError(
            "ingest_invoice",
            "Phase 1 invariant: taxable=true lines are not allowed on Posted invoices",
        )

    # Invoice graph record. The ingest action expects the typed graph shape
    # (record: {attributes: {type, method, ...}, ...fields}), NOT the generic
    # Composite Graph subrequest shape ({url, method, body}). Per the dev guide
    # at docs/salesforce/262/dev-guide/articles/connect_requests_invoice_ingestion_input.htm.md
    # ``BillToContactId`` is Required by the ingest API. The dev guide marks
    # it Required in the Invoice graph record table and a live POST without it
    # returns INVALID_API_INPUT (verified 2026-06-25, rlm-base__jun17_1).
    if not account.bill_to_contact_id:
        raise LifecycleError(
            "ingest_invoice",
            f"account '{account.name}' ({account.id}) has no Contact -- "
            "ingestion requires BillToContactId; create a Contact on the "
            "account or pin a different one in the scenario",
        )
    invoice_fields: dict[str, Any] = {
        "uniqueIdentifier": run_id,
        "billingAccountId": account.id,
        "billToContactId": account.bill_to_contact_id,
        "status": status,
        "invoiceDate": (spec.invoice_date or date.today()).isoformat(),
    }
    if spec.due_date is not None:
        invoice_fields["dueDate"] = spec.due_date.isoformat()
    if status == "Posted":
        invoice_fields["postedDate"] = (spec.posted_date or date.today()).isoformat()
        # The dev guide marks ``invoiceNumber`` Optional, but the live ingest
        # API rejects Posted payloads that omit it (verified 2026-06-25 on
        # rlm-base__jun17_1: INVALID_API_INPUT "You must specify an invoice
        # number for all posted invoices."). Default to the ``run_id`` so the
        # number is deterministic and idempotency-safe; a scenario can
        # override later via ``invoice.number`` once that knob lands.
        invoice_fields["invoiceNumber"] = run_id
    # Multi-currency orgs require ``currencyIsoCode`` on every ingest call.
    # Prefer the scenario override; fall back to the account's discovered
    # ``CurrencyIsoCode``; emit nothing on single-currency orgs (the field is
    # rejected with INVALID_FIELD if sent).
    currency = spec.currency or account.currency_iso_code
    if currency is not None:
        invoice_fields["currencyIsoCode"] = currency
    if spec.description is not None:
        invoice_fields["description"] = spec.description

    invoice_record = {
        "referenceId": "refInvoice",
        "record": {
            "attributes": {"type": "Invoice", "method": "POST"},
            **invoice_fields,
        },
    }

    # InvoiceLine.billingAddressId / shippingAddressId are both Required by the
    # ingest API (verified live 2026-06-25 on rlm-base__jun17_1: a payload
    # without them returns INVALID_API_INPUT "The BillingAddressId field of
    # the InvoiceLine record is required"). We materialise the account's
    # billing + shipping addresses as ``InvoiceAddressGroup`` graph records
    # and reference them via ``@{ref...}.id``. The dev guide marks
    # street/city/state/postalCode/country as Required on the address
    # record; a partial Account address surfaces here rather than at the org.
    if account.billing_address is None or not account.billing_address.is_complete:
        raise LifecycleError(
            "ingest_invoice",
            f"account '{account.name}' ({account.id}) has no complete "
            "BillingAddress (street/city/state/postalCode/country); "
            "InvoiceLine.billingAddressId is required by the ingest API",
        )
    if account.shipping_address is None or not account.shipping_address.is_complete:
        raise LifecycleError(
            "ingest_invoice",
            f"account '{account.name}' ({account.id}) has no complete "
            "ShippingAddress (street/city/state/postalCode/country); "
            "InvoiceLine.shippingAddressId is required by the ingest API",
        )

    def _address_record(ref: str, addr: PostalAddress) -> dict[str, Any]:
        return {
            "referenceId": ref,
            "record": {
                "attributes": {"type": "InvoiceAddressGroup", "method": "POST"},
                "invoiceId": "@{refInvoice.id}",
                "street": addr.street,
                "city": addr.city,
                "state": addr.state,
                "postalCode": addr.postal_code,
                "country": addr.country,
            },
        }

    billing_address_record = _address_record("refBillingAddress", account.billing_address)
    shipping_address_record = _address_record("refShippingAddress", account.shipping_address)

    # ``invoiceLineStartDate`` / ``invoiceLineEndDate`` are both Required by
    # the ingest API (dev guide R262/v67.0; live verified). Scenarios that
    # don't pin per-line dates inherit the invoice's invoiceDate for both
    # bounds -- a zero-duration "today" line carries clean defaults and the
    # caller can still override per line.
    invoice_date = spec.invoice_date or date.today()

    line_graph_records: list[dict[str, Any]] = []
    for idx, line in enumerate(lines, start=1):
        unit_price = float(line.unit_price)
        quantity = float(line.quantity)
        charge_amount = (
            float(line.charge_amount)
            if line.charge_amount is not None
            else unit_price * quantity
        )
        # No `taxable` field: it does not exist on InvoiceLine. The Phase 1
        # tax invariant is expressed by *omitting* InvoiceLineTax records and
        # leaving shouldCalculateTax false, not by stamping a column.
        line_fields: dict[str, Any] = {
            "invoiceId": "@{refInvoice.id}",
            "name": line.name,
            "quantity": quantity,
            "unitPrice": unit_price,
            "chargeAmount": charge_amount,
            "billingAddressId": "@{refBillingAddress.id}",
            "shippingAddressId": "@{refShippingAddress.id}",
        }
        if line.product is not None:
            line_fields["product2Id"] = line.product.id
        line_start = line.line_start_date or invoice_date
        line_end = line.line_end_date or line_start
        line_fields["invoiceLineStartDate"] = line_start.isoformat()
        line_fields["invoiceLineEndDate"] = line_end.isoformat()
        if line.description is not None:
            line_fields["description"] = line.description
        line_graph_records.append({
            "referenceId": f"refInvoiceLine{idx}",
            "record": {
                "attributes": {"type": "InvoiceLine", "method": "POST"},
                **line_fields,
            },
        })

    # ``taxCalculationStatus`` rules verified live (rlm-base__jun17_1):
    #   * Draft invoices accept ``Pending`` (the harness default).
    #   * Posted invoices REJECT ``Pending`` / ``Estimated`` with
    #     INVALID_API_INPUT "You can't specify a posted invoice with the
    #     taxCalculationStatus as estimated. Specify posted as the
    #     taxCalculationStatus." -- default to ``Posted`` for that path,
    #     keep the scenario override as an escape hatch.
    tax_calc_status = spec.tax_calculation_status or (
        "Posted" if status == "Posted" else "Pending"
    )

    body = {
        "invoices": [
            {
                "shouldCalculateTax": False,  # Phase 1 invariant
                "taxCalculationStatus": tax_calc_status,
                "correlationId": run_id,
                "graph": {
                    "graphId": "invoiceGraph",
                    "records": [
                        invoice_record,
                        billing_address_record,
                        shipping_address_record,
                        *line_graph_records,
                    ],
                },
            }
        ],
    }

    result = client.post(
        f"/services/data/v{client.api_version}/commerce/invoicing/invoices/collection/actions/ingest",
        body,
    )

    # Response shape per dev guide: {"invoices":[{"invoiceId","requestIdentifier",
    # "statusURL","success","errors":[...]}]}. Single-invoice contract means we
    # read index 0.
    invoices = (
        result.get("invoices") if isinstance(result, dict) else None
    ) or []
    if not invoices:
        raise LifecycleError("ingest_invoice", f"empty ingest response: {result}")
    row = invoices[0]
    if not row.get("success"):
        errs = row.get("errors") or row
        raise LifecycleError("ingest_invoice", f"ingest failed: {errs}")

    status_url = row.get("statusURL")
    deadline = time.monotonic() + timeout
    if status_url:
        _await_async_tracker(
            client, status_url, deadline, step="ingest_invoice"
        )

    # Recover the persisted invoice + lines by uniqueIdentifier. The action
    # response's invoiceId is the canonical id but reading back gives us
    # InvoiceNumber + the assigned InvoiceLine ids without trusting the
    # action's optional id field.
    invoice_id = row.get("invoiceId")
    if not invoice_id:
        # Fallback: query by UniqueIdentifier (the run_id idempotency key).
        rows = client.query(
            "SELECT Id, InvoiceNumber FROM Invoice "
            f"WHERE UniqueIdentifier = '{run_id}' LIMIT 1"
        )
        if not rows:
            raise LifecycleError(
                "ingest_invoice",
                f"ingest returned no invoiceId and no Invoice with UniqueIdentifier={run_id}",
            )
        invoice_id = rows[0]["Id"]
        invoice_number = rows[0].get("InvoiceNumber")
    else:
        invoice_number = _query_invoice_number(client, invoice_id)

    line_rows = client.query(
        f"SELECT Id FROM InvoiceLine WHERE InvoiceId = '{invoice_id}' ORDER BY Id"
    )
    invoice_line_ids = [r["Id"] for r in line_rows]
    log.info(
        "invoice %s ingested (status=%s, %d line(s), number=%s)",
        invoice_id,
        status,
        len(invoice_line_ids),
        invoice_number,
    )
    return invoice_id, invoice_number, invoice_line_ids
