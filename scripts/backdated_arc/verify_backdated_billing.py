#!/usr/bin/env python3
"""Verify a backdated asset change all the way to the invoice (todo 246).

One scenario per run, on one account:

1. Build a backdated asset (``scripts/build_quote_to_asset.py``), or take one
   with ``--asset``.
2. Invoice it through today and post the invoice, so periods are already billed.
3. Run the backdated action through the same invocable action (or Connect
   resource, for swap/upgrade/downgrade) that ``RLM_ARC_Assets`` calls.
   ``--order`` instead continues from an order you created in the UI.
4. Fill the order's billing/shipping fields, activate it, and wait for its
   billing schedules.
5. Invoice the new schedules through today and post. A negative invoice must
   post as a credit memo.
6. Check: every new schedule starts on the effective date, the invoice lines
   start there, and the net amount equals quantity change x period amount x
   elapsed periods (within the currency's rounding, per line).

Scenarios
---------
amend-up       +1 from the effective date
amend-down     -1 from the effective date (asset built with quantity 2)
cancel         cancel from the effective date
renew-expired  renew an asset whose term ended before the effective date
transfer       move the asset's full quantity to --target-account
swap           replace with --to-sku (swap)
upgrade        replace with --to-sku (upgrade)
downgrade      replace with --to-sku (downgrade)
rollback       backdated +1, bill it, then try to roll it back. Help (Transaction
               Rollbacks Considerations): only future-dated transactions that haven't
               started can be rolled back, so the PASS condition is the platform's refusal

Help (264, "Backdate Asset Transactions"): amend, renew and cancel can be
backdated for standard and ramped assets; transfer and swap for standard
assets only. Use a plain term product (default QB-API-PROD), billed monthly,
with an effective date on the 1st so periods align.

Run from the repo root, e.g.::

    python scripts/backdated_arc/verify_backdated_billing.py --org <sf-alias> \\
        --scenario cancel --account "Apex Dynamics"
"""
import argparse
import datetime as dt
import json
import os
import re
import shlex
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from build_quote_to_asset import (  # noqa: E402
    API, StepError, create_order, sf_apex, sf_query, sf_rest, soql_str, wait_for_calculation,
)

TODAY = dt.date.today()
BUILDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build_quote_to_asset.py")
SCENARIOS = ("amend-up", "amend-down", "cancel", "renew-expired", "transfer",
             "swap", "upgrade", "downgrade", "rollback")
SWAPS = ("swap", "upgrade", "downgrade")
POLL = 10
ID_RE = re.compile(r"^[A-Za-z0-9]{15}(?:[A-Za-z0-9]{3})?$")
INVOICE_DRAFT = {"Draft", "Split Draft"}
INVOICE_POSTED = {"Posted", "Split Posted"}
INVOICE_FAILED = {"Error", "Split Error"}


def log(msg):
    print(f"  {msg}", flush=True)


def wait(what, fn, timeout):
    deadline = time.time() + timeout
    while time.time() < deadline:
        got = fn()
        if got:
            return got
        time.sleep(POLL)
    raise StepError(f"timed out after {timeout}s waiting for {what}")


def iso_dt(day):
    return f"{day.isoformat()}T00:00:00.000Z"


def months_between(start, end):
    """Monthly periods from ``start`` through the period containing ``end``."""
    return (end.year - start.year) * 12 + end.month - start.month + 1


def default_effective(today):
    """The 1st of the month two months before ``today``'s month."""
    m = today.month - 3
    return dt.date(today.year + m // 12, m % 12 + 1, 1)


def soql_ids(ids):
    return ",".join(f"'{i}'" for i in ids)


# ----------------------------------------------------------------------
# Records
# ----------------------------------------------------------------------
def account_id(org, name):
    rows = sf_query(org, f"SELECT Id FROM Account WHERE Name = {soql_str(name)}")
    if len(rows) != 1:
        raise StepError(f"expected one account named {name!r}, found {len(rows)}")
    return rows[0]["Id"]


def assets(org, acct, sku):
    return sf_query(org, "SELECT Id, Quantity, LifecycleStartDate, LifecycleEndDate FROM Asset "
                         f"WHERE AccountId = '{acct}' AND Product2.StockKeepingUnit = {soql_str(sku)} "
                         "ORDER BY CreatedDate")


def build_asset(org, account, acct, sku, start, end, quantity):
    if assets(org, acct, sku):
        raise StepError(f"{account} already has a {sku} asset; pass --asset or use another account")
    cmd = [sys.executable, BUILDER, "--org", org, "--accounts", account, "--sku", sku,
           "--start", start.isoformat(), "--end", end.isoformat(), "--quantity", str(quantity),
           "--billing-frequency", "Monthly", "--skip-usage-verify"]
    log(f"build        {sku} x{quantity} {start} -> {end}")
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if p.returncode:
        raise StepError(f"asset build failed:\n{p.stdout[-1500:]}{p.stderr[-500:]}")
    rows = assets(org, acct, sku)
    if not rows:
        raise StepError("asset build reported success but no asset exists")
    return rows[-1]["Id"]


def account_orders(org, acct):
    return [r["Id"] for r in sf_query(org, f"SELECT Id FROM Order WHERE AccountId = '{acct}'")]


def schedules(org, order_ids):
    if not order_ids:
        return []
    return sf_query(org, "SELECT Id, Status, Quantity, BillingScheduleStartDate, BillingScheduleEndDate, "
                         "NextBillingDate, BillingPeriodAmount, TotalAmount, BilledAmount, CancellationDate, "
                         f"ReferenceEntityId, ReferenceEntityItemId FROM BillingSchedule WHERE ReferenceEntityId IN ({soql_ids(order_ids)}) "
                         "ORDER BY CreatedDate")


def complete_schedules(org, order_ids):
    """The orders' schedules once EVERY billable order line has one, else None.

    Schedules appear asynchronously after activation and one at a time, so "any
    schedule exists" would let a transfer's target or a swap's incoming line go
    unchecked. Matched per line, not by count per order. A schedule's
    ReferenceEntityItemId is either the OrderItem or one of its OrderItemDetail
    records (measured: a swap order had one of each), so details are mapped back to
    their line. Zero-quantity lines bill nothing and aren't waited for.
    """
    ids = soql_ids(order_ids)
    lines = {r["Id"] for r in sf_query(org, f"SELECT Id FROM OrderItem WHERE OrderId IN ({ids}) AND Quantity != 0")}
    if not lines:
        return None
    detail = {r["Id"]: r["OrderItemId"] for r in sf_query(
        org, f"SELECT Id, OrderItemId FROM OrderItemDetail WHERE OrderItem.OrderId IN ({ids})")}
    rows = schedules(org, order_ids)
    covered = {detail.get(s["ReferenceEntityItemId"], s["ReferenceEntityItemId"]) for s in rows}
    if not lines <= covered:
        return None
    # A line can carry more than one schedule; take the set only once a further poll
    # finds no new ones.
    time.sleep(POLL)
    again = schedules(org, order_ids)
    return again if {s["Id"] for s in again} == {s["Id"] for s in rows} else None


# ----------------------------------------------------------------------
# Billing
# ----------------------------------------------------------------------
def invoice_lines(org, invoice_id):
    return sf_query(org, "SELECT BillingScheduleId, ChargeAmount, InvoiceLineStartDate, InvoiceLineEndDate "
                         f"FROM InvoiceLine WHERE InvoiceId = '{invoice_id}' AND Type = 'Charge' "
                         "ORDER BY InvoiceLineStartDate")


def bill_through_today(org, sched_rows, tag):
    """Generate and post the invoice(s) for every schedule due by today; return them.

    Generate rejects the WHOLE request when any schedule is already billed past the
    target date ("don't meet the filter criteria for invoice creation"), so only
    schedules whose NextBillingDate is on or before today are sent. Only invoices
    created after the request are taken, so an older Draft on the same schedules
    isn't posted in their place.
    """
    due = [s["Id"] for s in sched_rows
           if s["Status"] == "ReadyForInvoicing" and s["NextBillingDate"]
           and dt.date.fromisoformat(s["NextBillingDate"]) <= TODAY]
    if not due:
        raise StepError(f"{tag}: no billing schedule is due by {TODAY}")
    # Margin for clock skew between this machine and the org; an older Draft would also
    # need lines on these just-due schedules, which a previous run would have posted.
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=60)).strftime("%Y-%m-%dT%H:%M:%SZ")
    resp = sf_rest(org, f"/services/data/{API}/commerce/invoicing/invoices/collection/actions/generate",
                   "POST", {"billingScheduleIds": due, "action": "Draft", "invoiceDate": TODAY.isoformat(),
                            "targetDate": TODAY.isoformat(), "correlationId": tag})
    if not isinstance(resp, dict) or not resp.get("success"):
        raise StepError(f"{tag}: generate failed: {json.dumps(resp)[:400]}")

    def drafted():
        """Draft invoice ids once every due schedule has a Draft line (generate can split)."""
        rows = sf_query(org, f"SELECT InvoiceId, BillingScheduleId, Invoice.Status FROM InvoiceLine WHERE "
                             f"BillingScheduleId IN ({soql_ids(due)}) AND Invoice.CreatedDate >= {since}")
        bad = [r["InvoiceId"] for r in rows if r["Invoice"]["Status"] in INVOICE_FAILED]
        if bad:
            raise StepError(f"{tag}: generated invoice {bad[0]} is in error")
        drafts = [r for r in rows if r["Invoice"]["Status"] in INVOICE_DRAFT]
        if set(due) <= {r["BillingScheduleId"] for r in drafts}:
            return sorted({r["InvoiceId"] for r in drafts})
        return None
    invs = wait(f"{tag} draft invoice(s) for every due schedule", drafted, 300)
    resp = sf_rest(org, f"/services/data/{API}/commerce/invoicing/invoices/collection/actions/post",
                   "POST", {"invoiceIds": invs, "correlationId": f"{tag}-post"})
    if not isinstance(resp, dict) or not resp.get("success"):
        raise StepError(f"{tag}: post failed: {json.dumps(resp)[:400]}")

    def posted():
        rows = sf_query(org, "SELECT Id, InvoiceNumber, Status, TotalAmount, Balance FROM Invoice "
                             f"WHERE Id IN ({soql_ids(invs)})")
        bad = [r for r in rows if r["Status"] in INVOICE_FAILED]
        if bad:
            raise StepError(f"{tag}: invoice {bad[0]['Id']} is {bad[0]['Status']} after post")
        return rows if len(rows) == len(invs) and all(r["Status"] in INVOICE_POSTED for r in rows) else None
    out = []
    for row in wait(f"{tag} posted invoice(s)", posted, 300):
        memo = None
        if row["TotalAmount"] < 0:
            def credited():
                r = sf_query(org, "SELECT CreditMemoNumber, Status, TotalAmount FROM CreditMemo "
                                  f"WHERE ReferenceEntityId = '{row['Id']}'")
                return r[0] if r else None
            memo = wait(f"{tag} credit memo", credited, 300)

            # The memo is applied to the invoice a moment after it posts; until then the
            # invoice still shows its full negative balance.
            def settled():
                r = sf_query(org, f"SELECT Balance FROM Invoice WHERE Id = '{row['Id']}'")
                return r if r and r[0]["Balance"] == 0 else None
            try:
                row["Balance"] = wait(f"{tag} credit memo applied", settled, 120)[0]["Balance"]
            except StepError:
                row["Balance"] = sf_query(org, f"SELECT Balance FROM Invoice WHERE Id = '{row['Id']}'")[0]["Balance"]
        lines = invoice_lines(org, row["Id"])
        log(f"invoice      {row['InvoiceNumber']} {row['TotalAmount']:.2f} ({len(lines)} line(s), balance "
            f"{row['Balance']})" + (f" -> credit memo {memo['CreditMemoNumber']} {memo['TotalAmount']:.2f} "
                                    f"{memo['Status']}" if memo else ""))
        out.append({"id": row["Id"], "number": row["InvoiceNumber"], "total": row["TotalAmount"],
                    "balance": row["Balance"], "lines": lines, "memo": memo})
    return out


# ----------------------------------------------------------------------
# Orders
# ----------------------------------------------------------------------
def prepare_and_activate(org, order_id):
    """Fill the fields backdated-change orders need, then activate.

    The asset-action APIs copy neither the account's addresses nor a bill-to
    contact, and activation refuses an order without billing address + bill-to
    contact (runbook: backdated-asset-lifecycle.md).
    """
    status = sf_query(org, f"SELECT Status FROM Order WHERE Id = '{order_id}'")
    if not status:
        raise StepError(f"order {order_id} not found")
    if status[0]["Status"] == "Activated":
        log(f"activated    {order_id} (already)")
        return
    out = sf_apex(org, f"""
Order o = [SELECT Id, AccountId, Status FROM Order WHERE Id = '{order_id}'];
Account a = [SELECT BillingStreet, BillingCity, BillingState, BillingPostalCode, BillingCountry,
             ShippingStreet, ShippingCity, ShippingState, ShippingPostalCode, ShippingCountry,
             (SELECT Id FROM Contacts ORDER BY CreatedDate LIMIT 1) FROM Account WHERE Id = :o.AccountId];
if (a.Contacts.isEmpty()) {{ System.debug('ERR=account has no contact for BillToContactId'); return; }}
Boolean ship = a.ShippingStreet != null;
o.BillToContactId = a.Contacts[0].Id;
o.BillingStreet = a.BillingStreet; o.BillingCity = a.BillingCity; o.BillingState = a.BillingState;
o.BillingPostalCode = a.BillingPostalCode; o.BillingCountry = a.BillingCountry;
o.ShippingStreet = ship ? a.ShippingStreet : a.BillingStreet; o.ShippingCity = ship ? a.ShippingCity : a.BillingCity;
o.ShippingState = ship ? a.ShippingState : a.BillingState;
o.ShippingPostalCode = ship ? a.ShippingPostalCode : a.BillingPostalCode;
o.ShippingCountry = ship ? a.ShippingCountry : a.BillingCountry;
update o;
o.Status = 'Activated';
update o;
System.debug('STATUS=' + [SELECT Status FROM Order WHERE Id = :o.Id].Status);
""")
    vals = dict(l.split("=", 1) for l in out if "=" in l)
    if vals.get("ERR"):
        raise StepError(f"order {order_id}: {vals['ERR']}")
    if vals.get("STATUS") != "Activated":
        raise StepError(f"order {order_id} did not activate (Status={vals.get('STATUS')})")
    log(f"activated    {order_id}")


def wait_for_order(org, record_id):
    """An action can return a Quote; turn it into an order the way the UI does."""
    if record_id.startswith("801"):
        # Re-read the id: a 15-character --order would never match the 18-character ids
        # every query returns.
        rows = sf_query(org, f"SELECT Id, Status FROM Order WHERE Id = '{record_id}'")
        if not rows:
            raise StepError(f"order {record_id} not found")
        if rows[0]["Status"] != "Activated":
            wait_for_calculation(org, rows[0]["Id"], 300, POLL)
        return rows[0]["Id"]
    wait(f"quote {record_id} pricing", lambda: sf_query(
        org, f"SELECT Id FROM Quote WHERE Id = '{record_id}' AND CalculationStatus LIKE 'Completed%'"), 300)
    order = create_order(org, record_id, 300, POLL)
    wait_for_calculation(org, order, 300, POLL)
    log(f"order        {order} (from quote {record_id})")
    return order


def invocable(org, name, inputs):
    resp = sf_rest(org, f"/services/data/{API}/actions/standard/{name}", "POST", {"inputs": [inputs]})
    first = resp[0] if isinstance(resp, list) and resp else resp
    if not isinstance(first, dict) or not first.get("isSuccess"):
        raise StepError(f"{name}: {json.dumps(first)[:500]}")
    return first.get("outputValues") or {}


def pricebook_entry(org, sku, currency, model_name):
    rows = sf_query(org, "SELECT Id, Product2Id, UnitPrice FROM PricebookEntry WHERE IsActive = true "
                         f"AND Product2.StockKeepingUnit = {soql_str(sku)} AND CurrencyIsoCode = {soql_str(currency)} "
                         f"AND ProductSellingModel.Name = {soql_str(model_name)} AND Pricebook2.IsStandard = true")
    if not rows:
        raise StepError(f"no active standard-pricebook entry for {sku} / {currency} / {model_name}")
    return rows[0]


def run_action(org, scenario, asset, effective, args):
    """Run the backdated action; return the order ids to activate, in order."""
    if scenario in ("amend-up", "amend-down", "rollback"):
        out = invocable(org, "initiateAmendment", {
            "amendAssetIds": [asset], "amendStartDate": iso_dt(effective),
            "quantityChange": -1 if scenario == "amend-down" else 1, "amendOutputType": "Order"})
        return [wait_for_order(org, out["amendRecordId"])]
    if scenario == "cancel":
        out = invocable(org, "initiateCancellation", {
            "cancelAssetIds": [asset], "cancelStartDate": iso_dt(effective), "cancelOutputType": "Order"})
        return [wait_for_order(org, out["cancelRecordId"])]
    if scenario == "renew-expired":
        out = invocable(org, "initiateRenewal", {
            "renewAssetIds": [asset], "renewOutputType": "Order",
            # Required for an expired asset: without it the platform answers "Select
            # Override Renewal Term to renew expired or future-dated assets".
            "renewStartDate": iso_dt(effective),
            "renewEndDate": iso_dt(effective.replace(year=effective.year + 1) - dt.timedelta(days=1))})
        return [wait_for_order(org, out["renewRecordId"])]
    if scenario == "transfer":
        # Asset.Quantity stays null on these assets; CurrentQuantity carries the count.
        qty = sf_query(org, f"SELECT CurrentQuantity FROM Asset WHERE Id = '{asset}'")[0]["CurrentQuantity"]
        out = invocable(org, "initiateTransfer", {
            "transferRecords": [{"assetId": asset, "transferQuantity": qty}],
            "transferDate": iso_dt(effective), "outputRecordType": "Order",
            "targetAccountId": account_id(org, args.target_account)})
        # Help: activate the source order first, then the destination order.
        return [wait_for_order(org, out["assetTransferSourceId"]),
                wait_for_order(org, out["assetTransferTargetId"])]
    if scenario in SWAPS:
        a = sf_query(org, "SELECT CurrentQuantity, CurrencyIsoCode, LifecycleEndDate, AccountId FROM Asset "
                          f"WHERE Id = '{asset}'")[0]
        pbe = pricebook_entry(org, args.to_sku, a["CurrencyIsoCode"], args.selling_model)
        # BillingFrequency is only settable with an explicit BillingTreatment ("Add a Billing
        # Treatment to make sure that you can change the Billing Frequency"). Reuse the
        # outgoing asset's, which the builder picked for this currency.
        treatment = sf_query(org, "SELECT BillingTreatmentId FROM OrderItem WHERE BillingTreatmentId != null "
                                  f"AND Order.AccountId = '{a['AccountId']}' ORDER BY CreatedDate LIMIT 1")
        if not treatment:
            raise StepError("no billing treatment on the account's original order line")
        body = {"swapStartDate": iso_dt(effective), "outputRecordType": "Quote", "swapGroups": {"groups": [{
            "referenceId": "BD246", "outGroup": {"swapAssets": [{"assetId": asset, "quantity": a["CurrentQuantity"]}]},
            "inGroup": {"graphId": "bd246Swap", "records": [{"referenceId": "refQuoteLine0", "record": {
                "attributes": {"type": "QuoteLineItem", "method": "POST"},
                "Product2Id": pbe["Product2Id"], "PricebookEntryId": pbe["Id"], "UnitPrice": pbe["UnitPrice"],
                "Quantity": str(int(a["CurrentQuantity"])), "StartDate": effective.isoformat(),
                # Without an end date pricing fails: "Specify either the end date or add the
                # Subscription Term and subscription term unit parameters". The incoming
                # product co-terms with the outgoing asset.
                "EndDate": a["LifecycleEndDate"][:10], "BillingFrequency": "Monthly",
                "BillingTreatmentId": treatment[0]["BillingTreatmentId"],
                "PeriodBoundary": "Anniversary"}}]}}]}}
        resp = sf_rest(org, f"/services/data/{API}/revenue/transaction-management/assets/actions/{scenario}",
                       "POST", body)
        rid = resp.get("salesTransactionId") if isinstance(resp, dict) else None
        if not rid:
            raise StepError(f"{scenario}: {json.dumps(resp)[:500]}")
        return [wait_for_order(org, rid)]
    raise StepError(f"unknown scenario {scenario}")


# ----------------------------------------------------------------------
# Checks
# ----------------------------------------------------------------------
def check(new_scheds, invoices, effective, scale):
    """Return a list of failures for the post-change billing.

    Per schedule: it starts on the effective date, its first invoice line starts
    there, and its lines sum to sign x |BillingPeriodAmount| x the periods elapsed
    since then. The expectation comes from the platform's own period amount, so this
    proves the invoice matches the schedule, not the price. Each line is rounded to
    the currency's precision (JPY has none), so half a unit of it is allowed per line.
    """
    fails = []
    periods = months_between(effective, TODAY)
    lines = [l for inv in invoices for l in inv["lines"]]
    by_sched = {}
    for l in lines:
        by_sched.setdefault(l["BillingScheduleId"], []).append(l)
    expected_total = 0.0
    for s in new_scheds:
        if not s["Quantity"]:
            # A zero-quantity line must bill nothing; it isn't waited for, and isn't required.
            billed = sum(l["ChargeAmount"] for l in by_sched.get(s["Id"], []))
            if abs(billed) > 0.5 * 10 ** -scale * max(len(by_sched.get(s["Id"], [])), 1):
                fails.append(f"zero-quantity schedule {s['Id']} billed {billed:.2f}")
            continue
        if s["BillingPeriodAmount"] is None:
            fails.append(f"schedule {s['Id']} has no period amount")
            continue
        # The schedule's own dates stay out of the output (CodeQL treats Billing* fields as
        # private); the effective date and the schedule id are enough to look it up.
        if dt.date.fromisoformat(s["BillingScheduleStartDate"]) != effective:
            fails.append(f"schedule {s['Id']} doesn't start on the effective date {effective}")
        mine = by_sched.get(s["Id"], [])
        if not mine:
            fails.append(f"schedule {s['Id']} was not invoiced")
            continue
        first = min(l["InvoiceLineStartDate"] for l in mine)
        if dt.date.fromisoformat(first) != effective:
            fails.append(f"schedule {s['Id']}: first invoice line starts {first}, expected {effective}")
        expected = (1 if s["Quantity"] > 0 else -1) * abs(s["BillingPeriodAmount"]) * periods
        actual = sum(l["ChargeAmount"] for l in mine)
        expected_total += expected
        if abs(actual - expected) > 0.5 * 10 ** -scale * len(mine):
            fails.append(f"schedule {s['Id']} billed {actual:.2f}, expected {expected:.2f} "
                         f"({periods} period(s) since {effective})")
    stray = len(set(by_sched) - {s["Id"] for s in new_scheds})
    if stray:
        fails.append(f"invoice lines for {stray} schedule(s) outside the change")
    for inv in invoices:
        if inv["total"] < 0 and not inv["memo"]:
            fails.append(f"negative invoice {inv['number']} has no credit memo")
        if inv["total"] < 0 and inv.get("balance") not in (0, 0.0):
            fails.append(f"negative invoice {inv['number']} has balance {inv.get('balance')}, expected 0")
    log(f"check        {len(new_scheds)} new schedule(s), billed {sum(l['ChargeAmount'] for l in lines):.2f}, "
        f"expected {expected_total:.2f}")
    return fails


def check_shape(scenario, new_scheds, order_account, acct):
    """The change must look like the scenario: right accounts, right signs.

    Without this, UI mode would PASS an order of another sign class (an amend +1 run as
    --scenario cancel) or one on another account. Signs can't tell cancel from
    amend-down, amend-up from renew, or swap from upgrade/downgrade.
    """
    fails = []
    orders = list(order_account)
    if order_account[orders[0]] != acct:
        fails.append(f"order {orders[0]} is not on the asset's account")
    if scenario == "transfer" and (len(orders) != 2 or order_account[orders[1]] == acct):
        fails.append("a transfer needs a target order on another account")
    signs = sorted(1 if s["Quantity"] > 0 else -1 for s in new_scheds if s["Quantity"])
    want = {"amend-up": "positive", "renew-expired": "positive", "amend-down": "negative", "cancel": "negative"}
    if scenario in want:
        ok = signs and all(x == (1 if want[scenario] == "positive" else -1) for x in signs)
        if not ok:
            fails.append(f"{scenario} needs only {want[scenario]} schedules, got signs {signs}")
    elif scenario in SWAPS + ("transfer",) and signs != [-1, 1]:
        fails.append(f"{scenario} needs one outgoing (-) and one incoming (+) schedule, got signs {signs}")
    if scenario == "transfer" and not fails:
        out = [s for s in new_scheds if s["Quantity"] < 0][0]
        if order_account[out["ReferenceEntityId"]] != acct:
            fails.append("the transfer's negative schedule is not on the source account")
    return fails


def scenario_defaults(scenario, effective):
    """Asset term and quantity each scenario needs."""
    if scenario == "renew-expired":
        # effective is a 1st, so shifting it a year is always a valid date.
        return effective.replace(year=effective.year - 1), effective - dt.timedelta(days=1), 1
    m = effective.month - 4  # the 1st three months before the effective month
    start = dt.date(effective.year + m // 12, m % 12 + 1, 1)
    end = start.replace(year=start.year + 1) - dt.timedelta(days=1)
    return start, end, 2 if scenario == "amend-down" else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--org", required=True, help="sf CLI alias or username")
    ap.add_argument("--scenario", required=True, choices=SCENARIOS)
    ap.add_argument("--account", required=True, help="account to build the asset on (one scenario per account)")
    ap.add_argument("--sku", default="QB-API-PROD", help="plain term product (default: QB-API-PROD)")
    ap.add_argument("--effective", help="backdated effective date, a 1st of month (default: the 1st two months "
                                        "before this month)")
    ap.add_argument("--asset", help="use this existing, already-invoiced asset instead of building one")
    ap.add_argument("--prepare-only", action="store_true",
                    help="UI mode, step 1: build and invoice the asset, then stop so the change can be made "
                         "in the Managed Asset viewer")
    ap.add_argument("--order", action="append",
                    help="UI mode, step 2 (with --asset): continue from the Draft order(s) the viewer created. "
                         "Repeat for a transfer, source order first")
    ap.add_argument("--target-account", help="transfer: destination account name")
    ap.add_argument("--to-sku", help="swap/upgrade/downgrade: incoming product SKU")
    ap.add_argument("--selling-model", default="Term Annual",
                    help="swap/upgrade/downgrade: incoming product's selling model name (default: Term Annual)")
    args = ap.parse_args()
    for v in [args.asset] + (args.order or []):
        if v and not ID_RE.match(v):
            ap.error(f"{v!r} is not a Salesforce record id")
    if args.order and not args.asset:
        ap.error("--order needs --asset (the asset prepared with --prepare-only)")
    if args.order and args.scenario == "rollback":
        ap.error("rollback has no UI-order mode: Help says a started (backdated) change can't be rolled back")
    if args.order and args.scenario == "transfer" and len(args.order) != 2:
        ap.error("a transfer needs both orders: --order <source> --order <target>")
    if args.order and args.scenario != "transfer" and len(args.order) != 1:
        ap.error(f"{args.scenario} takes one --order")
    if args.prepare_only and (args.asset or args.order):
        ap.error("--prepare-only builds a new asset; don't combine it with --asset or --order")
    if args.prepare_only and args.scenario == "rollback":
        ap.error("rollback has no UI mode: Help says a started (backdated) change can't be rolled back")
    if args.scenario == "transfer" and not (args.target_account or args.order or args.prepare_only):
        ap.error("--target-account is required for transfer")
    if args.scenario in SWAPS and not (args.to_sku or args.order or args.prepare_only):
        ap.error(f"--to-sku is required for {args.scenario}")

    effective = dt.date.fromisoformat(args.effective) if args.effective else default_effective(TODAY)
    if effective.day != 1:
        ap.error("--effective must be a 1st of the month, so billing periods align")
    if effective >= TODAY:
        ap.error("--effective must be in the past")
    if args.scenario == "renew-expired" and months_between(effective, TODAY) > 12:
        ap.error("--effective is too far back: the one-year renewal term from it would end before today")
    if not args.asset and args.scenario != "renew-expired" and months_between(effective, TODAY) > 9:
        ap.error("--effective is too far back: the built asset (a one-year term from the 1st three "
                 "months before it) would end before today")
    org, tag = args.org, f"bd246-{args.scenario}-{int(time.time())}"
    print(f"org={org} scenario={args.scenario} account={args.account} effective={effective} today={TODAY}")
    try:
        acct = account_id(org, args.account)
        start, end, qty = scenario_defaults(args.scenario, effective)
        if args.asset:
            rows = sf_query(org, f"SELECT Id FROM Asset WHERE Id = '{args.asset}' AND AccountId = '{acct}'")
            if not rows:
                raise StepError(f"asset {args.asset} isn't on {args.account}")
            asset = rows[0]["Id"]
        else:
            before = set(account_orders(org, acct))
            asset = build_asset(org, args.account, acct, args.sku, start, end, qty)
            # Invoice only the order the build created, not other products on the account.
            built = [o for o in account_orders(org, acct) if o not in before]
            if not built:
                raise StepError("the asset build created no new order on the account")
            bill_through_today(org, wait("the new order's billing schedules",
                                         lambda: complete_schedules(org, built), 300), f"{tag}-base")
        log(f"asset        {asset}")
        if args.prepare_only:
            orders = "--order <source order> --order <target order>" if args.scenario == "transfer" \
                else "--order <order id>"
            sku = f" --sku {shlex.quote(args.sku)}" if args.sku != "QB-API-PROD" else ""
            print(f"READY {args.scenario}: asset {asset} on {args.account} is invoiced through {TODAY}. Make the "
                  f"change effective {effective} in the Managed Asset viewer, then run:\n  python "
                  f"{shlex.quote(sys.argv[0])} --org {shlex.quote(org)} --scenario {args.scenario} "
                  f"--account {shlex.quote(args.account)}{sku} "
                  f"--asset {asset} --effective {effective} {orders}")
            return 0
        if args.scenario == "rollback":
            amend = run_action(org, "amend-up", asset, effective, args)
            for o in amend:
                prepare_and_activate(org, o)
            bill_through_today(org, wait("amendment schedules", lambda: complete_schedules(org, amend), 300),
                               f"{tag}-amend")
            try:
                invocable(org, "initiateRollBackLastAction", {"assetIds": [asset], "outputType": "Order"})
            except StepError as exc:
                if "period has started" not in str(exc):
                    raise
                log("rollback     refused as Help documents: the amendment period has started")
                print("PASS rollback")
                return 0
            raise StepError("rollback of a started (backdated) amendment was accepted; Help says it is refused")
        elif args.order:
            orders = [wait_for_order(org, o) for o in args.order]
        else:
            orders = run_action(org, args.scenario, asset, effective, args)
        order_account = {}
        for o in orders:
            prepare_and_activate(org, o)
            order_account[o] = sf_query(org, f"SELECT AccountId FROM Order WHERE Id = '{o}'")[0]["AccountId"]
        new = wait(f"a billing schedule for every billable line of order(s) {', '.join(orders)}",
                   lambda: complete_schedules(org, orders), 300)
        # Ids, quantity and total only; check() reports a wrong start date against the effective date.
        for s in new:
            log(f"schedule     {s['Id']} qty {s['Quantity']} total {s['TotalAmount']}")
        invoices = []
        # One invoice run per account (a transfer has two); each order's account is billed.
        for a in sorted(set(order_account.values())):
            mine = [s for s in new if order_account[s["ReferenceEntityId"]] == a]
            invoices += bill_through_today(org, mine, f"{tag}-{a[-4:]}")
        try:
            cur = sf_query(org, f"SELECT CurrencyIsoCode FROM Asset WHERE Id = '{asset}'")[0]["CurrencyIsoCode"]
            scale = sf_query(org, "SELECT DecimalPlaces FROM CurrencyType WHERE IsoCode = "
                                  f"{soql_str(cur)}")[0]["DecimalPlaces"]
        except (StepError, IndexError):
            scale = 2  # single-currency org: no CurrencyIsoCode / CurrencyType
        fails = check_shape(args.scenario, new, order_account, acct) + check(new, invoices, effective, scale)
    except StepError as exc:
        print(f"FAIL {args.scenario}: {exc}")
        return 1
    for f in fails:
        print(f"FAIL {args.scenario}: {f}")
    if not fails:
        print(f"PASS {args.scenario}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
