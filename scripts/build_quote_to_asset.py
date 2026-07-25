#!/usr/bin/env python3
"""Build a backdated Quote -> Order -> Asset chain, then verify usage buckets.

Purpose
-------
Usage rating can only be exercised against assets that already carry usage
entitlements ("wallets"), and the interesting cases are *backdated* — an asset
purchased earlier so a billing period has actually closed. Producing that state
by hand through the UI takes several minutes per account and is easy to get
subtly wrong (a line that starts today, a quote in the user's currency instead
of the account's). This script produces it reproducibly.

What it uses, and why
---------------------
The org's own utilities are used wherever they can be reached headlessly:

1. **Opportunity** — mirrors ``RLM_QuickQuote`` (``unpackaged/post_utils``)
   field-for-field. That flow is a *screen* flow so Apex cannot invoke it, but
   every automation it relies on is record-triggered, so the same insert fires
   the same behaviour (notably the account-currency defaulting added for
   multicurrency).
2. **Quote + line** — ``POST /connect/rev/sales-transaction/actions/place``
   (Place Sales Transaction) with an object graph. Direct ``QuoteLineItem`` DML
   is *not* viable for a TermDefined product: the platform requires
   ``BillingFrequency`` and simultaneously refuses to let you set it unless the
   line's BillingTreatment has ``CanChangeBillingFrequency = true``. The
   transaction API is the supported path.
3. **Order** — the standard ``createOrdersFromQuote`` invocable, which is
   exactly what the Create Order quick action runs via
   ``RLM_CreateOrdersFromQuote``.
4. **Activation** — the Draft -> Activated status transition, which is what the
   UI's Activate button does and what ``RLM_Submit_Order_on_Activation`` reacts
   to. v67.0 exposes no Connect resource for order activation.

Endpoints that older Postman collections still list are **gone** in v67.0 and
return NOT_FOUND: ``/commerce/sales-transactions/actions/place``,
``/commerce/quotes/actions/create-order``, and
``/connect/revenue-management/orders/actions/activate``.

Selling model drives which line fields are legal
------------------------------------------------
Not the product — the **selling model** behind the chosen PricebookEntry:

===========  ==========================  ==========================
model        BillingFrequency            EndDate
===========  ==========================  ==========================
TermDefined  required                    allowed
Evergreen    required                    rejected
OneTime      must be null/MilestonePlan  rejected
===========  ==========================  ==========================

A product may expose several (QB-DAT-THPT has Evergreen, Term Monthly and Term
Annual), so ``--selling-model`` picks which PricebookEntry to use.

Pack products need an anchor
----------------------------
A ``UsageModelType = Pack`` product draws down against an anchor's wallet and
cannot be sold alone — activation fails with *"the usage product is missing a
binding instance"*. Pass ``--anchor-sku`` to bind the line to an anchor asset
that already exists on the account (via ``BindingInstanceTargetId``), e.g.::

    --sku QB-TOKENS-PACK --anchor-sku QB-DB-TOKEN

Prerequisite
------------
Each target account must be reset first (no existing asset for the SKU) — the
asset is matched on account + product because ``Asset`` carries no lookup back
to the Order or Quote it came from.

Usage
-----
    python scripts/build_quote_to_asset.py --org rlm-base__pr308
    python scripts/build_quote_to_asset.py --org <alias> \
        --accounts "Infinitech,Kingsbridge Digital" \
        --sku QB-DB --start 2026-06-01 --end 2027-05-31

Exits 0 when every account reaches an asset with usage buckets, 1 otherwise.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time

DEFAULT_ACCOUNTS = "Infinitech,Kingsbridge Digital"
DEFAULT_SKU = "QB-DB"
DEFAULT_START = "2026-06-01"
DEFAULT_END = "2027-05-31"
API = "v67.0"

# CalculationStatus values that mean "done, stop polling". Anything else is
# either still in flight or a failure we surface verbatim.
CALC_READY = {"CompletedWithPricing", "CompletedWithTax", "CompletedWithoutPricing"}
CALC_FAILED = {
    "PriceCalculationFailed", "TaxCalculationFailed", "SaveFailedOrIncomplete",
    "OrderRequestFailed", "ConfigurationFailed", "ReconciliationFailed",
    "GroupRampConfigurationFailed", "PstBaseStepFailed",
}


class StepError(RuntimeError):
    """A step failed in a way that should stop this account's chain."""


# ----------------------------------------------------------------------
# sf CLI plumbing (auth is delegated to the CLI — no tokens handled here)
# ----------------------------------------------------------------------
def _run(args, timeout=300):
    env = {**os.environ, "SF_TEMP_SHOW_SECRETS": "true"}
    p = subprocess.run(args, capture_output=True, text=True, env=env, timeout=timeout)
    return p.returncode, p.stdout, p.stderr


def sf_query(org, soql):
    rc, out, err = _run(["sf", "data", "query", "-q", soql,
                         "--target-org", org, "--json"])
    try:
        d = json.loads(out)
    except json.JSONDecodeError:
        raise StepError(f"query failed: {(err or out)[:300]}")
    if "result" not in d:
        raise StepError(f"query failed: {d.get('message', out)[:300]}")
    return d["result"]["records"]


def sf_apex(org, code):
    """Run anonymous Apex; return the USER_DEBUG lines."""
    with tempfile.NamedTemporaryFile("w", suffix=".apex", delete=False) as fh:
        fh.write(code)
        path = fh.name
    try:
        rc, out, err = _run(["sf", "apex", "run", "--file", path, "--target-org", org])
        blob = out + err
        if "Executed successfully" not in blob:
            snippet = ""
            for marker in ("Error (", "System.", "Compile error"):
                i = blob.find(marker)
                if i != -1:
                    snippet = blob[i:i + 300]
                    break
            raise StepError(f"apex failed: {snippet or blob[-300:]}")
        # Log line looks like: ...|USER_DEBUG|[1]|DEBUG|MESSAGE
        # Split from the RIGHT: "USER_DEBUG|" itself contains "DEBUG|", so a
        # left split returns "[1]|DEBUG|MESSAGE" instead of the message.
        return [l.rsplit("|DEBUG|", 1)[-1].strip()
                for l in blob.splitlines()
                if "USER_DEBUG" in l and "|DEBUG|" in l]
    finally:
        os.unlink(path)


def sf_rest(org, path, method="GET", body=None):
    args = ["sf", "api", "request", "rest", path, "--target-org", org, "--method", method]
    if body is not None:
        args += ["--body", json.dumps(body)]
    rc, out, err = _run(args)
    text = out.strip() or err.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise StepError(f"{method} {path} -> unparseable response: {text[:300]}")


def esc(s):
    """Escape a value for embedding in an Apex string literal."""
    return s.replace("\\", "\\\\").replace("'", "\\'")


# ----------------------------------------------------------------------
# Steps
# ----------------------------------------------------------------------
def create_opportunity(org, account, sku, term, start, end, billing_timing,
                       selling_model, anchor_sku):
    """Create the Opportunity, mirroring RLM_QuickQuote's mapping.

    Returns the ids the Place Sales Transaction graph needs. RLM_QuickQuote is a
    SCREEN flow so Apex cannot invoke it, but every automation it depends on is
    record-triggered, so this insert fires the same behaviour (notably the
    account-currency defaulting added for multicurrency).
    """
    apex = f"""
public class QuoteBuildException extends Exception {{}}

final String ACCOUNT_NAME = '{esc(account)}';
final String SKU = '{esc(sku)}';
final Date END_DATE = Date.valueOf('{end}');

Account acct = [SELECT Id, Name, CurrencyIsoCode FROM Account
                WHERE Name = :ACCOUNT_NAME LIMIT 1];
Pricebook2 standard = [SELECT Id FROM Pricebook2 WHERE IsStandard = true LIMIT 1];
Product2 prod = [SELECT Id FROM Product2 WHERE StockKeepingUnit = :SKU LIMIT 1];

// A product can expose several selling models (QB-DAT-THPT has Evergreen,
// Term Monthly and Term Annual), and the PricebookEntry is what pins the line to
// one. The selling model then dictates which line fields are legal, so choose it
// deliberately rather than taking whichever entry comes back first.
List<PricebookEntry> pbes = [SELECT Id, UnitPrice, ProductSellingModel.SellingModelType,
                                    ProductSellingModel.Name
                             FROM PricebookEntry
                             WHERE Product2Id = :prod.Id AND Pricebook2Id = :standard.Id
                               AND CurrencyIsoCode = :acct.CurrencyIsoCode
                               AND IsActive = true
                             ORDER BY ProductSellingModel.Name];
if (pbes.isEmpty()) {{
    throw new QuoteBuildException('No active ' + acct.CurrencyIsoCode
        + ' PricebookEntry for ' + SKU + ' — qb-pricing may not cover this currency.');
}}
PricebookEntry pbe = pbes[0];
String wanted = '{selling_model}';
if (wanted != '') {{
    Boolean found = false;
    for (PricebookEntry e : pbes) {{
        if (e.ProductSellingModel != null
            && e.ProductSellingModel.SellingModelType == wanted) {{
            pbe = e; found = true; break;
        }}
    }}
    if (!found) {{
        List<String> avail = new List<String>();
        for (PricebookEntry e : pbes) {{
            avail.add(e.ProductSellingModel == null ? 'null'
                      : e.ProductSellingModel.SellingModelType);
        }}
        throw new QuoteBuildException(SKU + ' has no ' + wanted
            + ' selling model; available: ' + String.join(avail, ', '));
    }}
}}

// The line needs an explicit BillingTreatment: BillingFrequency is mandatory for
// TermDefined selling models, and the platform rejects it both when no treatment
// is referenced ("Add a Billing Treatment...") and when the referenced treatment
// has CanChangeBillingFrequency = false ("Update the Billing Treatment ..."):
// both the reference AND the flag are required.
List<BillingTreatment> treatments = [
    SELECT Id, Name, CanChangeBillingFrequency FROM BillingTreatment
    WHERE Status = 'Active' AND CurrencyIsoCode = :acct.CurrencyIsoCode
    ORDER BY Name];
if (treatments.isEmpty()) {{
    throw new QuoteBuildException('No active BillingTreatment for '
        + acct.CurrencyIsoCode + ' — qb-billing may not cover this currency.');
}}
BillingTreatment treatment = treatments[0];
for (BillingTreatment t : treatments) {{
    if (t.Name.containsIgnoreCase('{billing_timing}')) {{ treatment = t; break; }}
}}

// StageName/Name/Pricebook mirror RLM_QuickQuote's Create_New_Opportunity.
Opportunity opp = new Opportunity(
    AccountId = acct.Id,
    Name = 'New Opportunity for ' + acct.Name,
    StageName = 'Proposal/Quote',
    CloseDate = END_DATE,
    Pricebook2Id = standard.Id,
    CurrencyIsoCode = acct.CurrencyIsoCode);
insert opp;

// A Pack product draws down against an anchor's wallet and cannot stand alone:
// activating an unbound Pack line fails with "the usage product is missing a
// binding instance". QuoteLineItem.BindingInstanceTargetId points the Pack at
// the anchor Asset that already exists on this account.
String anchorSku = '{anchor_sku}';
if (anchorSku != '') {{
    List<Asset> anchors = [SELECT Id FROM Asset
                           WHERE AccountId = :acct.Id
                             AND Product2.StockKeepingUnit = :anchorSku
                           ORDER BY CreatedDate DESC LIMIT 1];
    if (anchors.isEmpty()) {{
        throw new QuoteBuildException('No ' + anchorSku + ' asset on ' + acct.Name
            + ' to bind to — build the anchor first.');
    }}
    System.debug('ANCHOR_ASSET_ID=' + anchors[0].Id);
}}

System.debug('ACCOUNT_ID=' + acct.Id);
System.debug('CURRENCY=' + acct.CurrencyIsoCode);
System.debug('OPP_ID=' + opp.Id);
System.debug('PRICEBOOK_ID=' + standard.Id);
System.debug('PRODUCT_ID=' + prod.Id);
System.debug('PBE_ID=' + pbe.Id);
System.debug('UNIT_PRICE=' + pbe.UnitPrice);
System.debug('SELLING_MODEL=' + (pbe.ProductSellingModel == null ? 'unknown'
    : pbe.ProductSellingModel.SellingModelType));
System.debug('SELLING_MODEL_NAME=' + (pbe.ProductSellingModel == null ? '-'
    : pbe.ProductSellingModel.Name));
System.debug('TREATMENT_ID=' + treatment.Id);
System.debug('TREATMENT_CANCHANGE=' + treatment.CanChangeBillingFrequency);
"""
    vals = {}
    for line in sf_apex(org, apex):
        if "=" in line and line.split("=", 1)[0].isupper():
            k, v = line.split("=", 1)
            vals[k] = v
    missing = {"ACCOUNT_ID", "OPP_ID", "PBE_ID", "SELLING_MODEL"} - set(vals)
    if missing:
        raise StepError(f"opportunity step did not report {sorted(missing)}")
    return vals


def place_quote(org, ids, account, start, end, quantity, period_boundary,
                billing_frequency):
    """Create the Quote + line via Place Sales Transaction.

    Direct QuoteLineItem DML is NOT viable for a TermDefined product here: the
    platform demands BillingFrequency ("When the SellingModelType is Evergreen or
    Term-Defined, BillingFrequency can't be null") but refuses to let you set it
    unless the line's BillingTreatment has CanChangeBillingFrequency = true, which
    is false on every QB treatment. The transaction API resolves the frequency
    from the treatment itself, which is why it is the supported path for adding
    a line to a quote.
    """
    # Which line fields are legal depends on the SELLING MODEL, not the product:
    #   OneTime     -> "When the SellingModelType is One Time, BillingFrequency must
    #                   be null or milestone plan"
    #   Evergreen   -> "You can't specify EndDate for evergreen order products"
    #   TermDefined -> BillingFrequency required, EndDate allowed
    # Assuming TermDefined silently breaks the Pack products, which is how
    # QB-TOKENS-PACK (OneTime) and QB-DAT-THPT (Evergreen) failed.
    model = ids.get("SELLING_MODEL", "TermDefined")
    line = {
        "attributes": {"type": "QuoteLineItem", "method": "POST"},
        "QuoteId": "@{refQuote.id}",
        "Product2Id": ids["PRODUCT_ID"],
        "PricebookEntryId": ids["PBE_ID"],
        "UnitPrice": float(ids["UNIT_PRICE"]),
        "Quantity": quantity,
        "StartDate": start,
    }
    # EndDate is rejected for BOTH Evergreen and OneTime:
    #   "You can't specify EndDate for evergreen order products"
    #   "You can't specify EndDate for one-time order products"
    if model not in ("Evergreen", "OneTime"):
        line["EndDate"] = end
    if model != "OneTime":
        line["PeriodBoundary"] = period_boundary
        line["BillingTreatmentId"] = ids["TREATMENT_ID"]
        line["BillingFrequency"] = billing_frequency
    if ids.get("ANCHOR_ASSET_ID"):
        line["BindingInstanceTargetId"] = ids["ANCHOR_ASSET_ID"]

    payload = {
        "pricingPref": "system",
        "configurationPref": {
            "configurationMethod": "skip",
            "configurationOptions": {
                "validateProductCatalog": False,
                "validateAmendRenewCancel": False,
                "executeConfigurationRules": False,
                "addDefaultConfiguration": False,
            },
        },
        "graph": {
            "graphId": "buildQuoteToAsset",
            "records": [
                {
                    "referenceId": "refQuote",
                    "record": {
                        "attributes": {"type": "Quote", "method": "POST"},
                        "Name": f"New Quote For {account}",
                        "QuoteAccountId": ids["ACCOUNT_ID"],
                        "OpportunityId": ids["OPP_ID"],
                        "Pricebook2Id": ids["PRICEBOOK_ID"],
                        "CurrencyIsoCode": ids["CURRENCY"],
                        "Status": "Draft",
                        "StartDate": start,
                    },
                },
                {
                    "referenceId": "refQuoteLineItem",
                    "record": line,
                },
            ],
        },
    }
    resp = sf_rest(org, f"/services/data/{API}/connect/rev/sales-transaction/actions/place",
                   "POST", payload)
    # This API reports per-record failures in an "errorResponse" array while still
    # returning HTTP 200 AND still creating the parent Quote, so a naive "did I get
    # a quote id" check reports success on a quote that has no lines. Check the
    # explicit success flag first.
    if isinstance(resp, list) and resp and "errorCode" in resp[0]:
        raise StepError(f"place: {resp[0].get('message', resp[0])}")
    if isinstance(resp, dict):
        errors = resp.get("errorResponse") or []
        if errors or resp.get("isSuccess") is False:
            detail = "; ".join(
                f"{e.get('referenceId', '?')}: {e.get('message', e)}" for e in errors
            ) or json.dumps(resp)[:300]
            raise StepError(f"place failed: {detail}")

    quote_id = None
    if isinstance(resp, dict):
        for key in ("quoteId", "salesTransactionId", "id"):
            if resp.get(key):
                quote_id = resp[key]
                break
        if not quote_id:
            for rec in (resp.get("graph", {}) or {}).get("records", []) or []:
                if rec.get("referenceId") == "refQuote":
                    quote_id = (rec.get("record") or {}).get("id") or rec.get("id")
    if not quote_id:
        rows = sf_query(org, "SELECT Id FROM Quote WHERE OpportunityId = "
                             f"'{ids['OPP_ID']}' ORDER BY CreatedDate DESC LIMIT 1")
        if rows:
            quote_id = rows[0]["Id"]
    if not quote_id:
        raise StepError(f"place returned no quote id: {json.dumps(resp)[:400]}")

    # Belt and braces: the quote must actually carry the line we asked for.
    lines = sf_query(org, f"SELECT COUNT(Id) n FROM QuoteLineItem WHERE QuoteId = '{quote_id}'")
    if not lines or not lines[0]["n"]:
        raise StepError(f"quote {quote_id} was created with no line items")
    return quote_id


def create_order(org, quote_id, timeout, interval):
    """Invoke the SAME action the Create Order quick action runs.

    The quick action calls the RLM_CreateOrdersFromQuote screen flow, which in turn
    calls the standard ``createOrdersFromQuote`` invocable — so calling the
    invocable directly is the identical operation, minus the screen. The Connect
    ``/commerce/quotes/actions/create-order`` resource from older collections is
    gone in v67.0 (NOT_FOUND).

    The action is asynchronous: it returns a requestId, and the order appears a
    moment later, so poll for it rather than trusting the immediate response.
    """
    resp = sf_rest(org, f"/services/data/{API}/actions/standard/createOrdersFromQuote",
                   "POST", {"inputs": [{"quoteId": quote_id}]})
    if isinstance(resp, list) and resp:
        first = resp[0]
        if first.get("isSuccess") is False:
            errs = first.get("errors") or []
            detail = "; ".join(e.get("message", str(e)) for e in errs) or json.dumps(first)[:300]
            raise StepError(f"createOrdersFromQuote: {detail}")
        out = first.get("outputValues") or {}
        ids = out.get("orderIds")
        if ids:
            return ids[0] if isinstance(ids, list) else ids
    elif isinstance(resp, dict) and resp.get("errorCode"):
        raise StepError(f"createOrdersFromQuote: {resp.get('message', resp)}")

    deadline = time.time() + timeout
    while time.time() < deadline:
        rows = sf_query(org, f"SELECT Id FROM Order WHERE QuoteId = '{quote_id}' "
                             f"ORDER BY CreatedDate DESC LIMIT 1")
        if rows:
            return rows[0]["Id"]
        time.sleep(interval)
    raise StepError(f"no order created from quote within {timeout}s "
                    f"(response: {json.dumps(resp)[:200]})")


def wait_for_calculation(org, order_id, timeout, interval):
    """Poll CalculationStatus until terminal. Returns the final status."""
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        rows = sf_query(org, f"SELECT CalculationStatus, ValidationResult, Status "
                             f"FROM Order WHERE Id = '{order_id}'")
        if not rows:
            raise StepError("order disappeared while polling")
        last = rows[0]["CalculationStatus"]
        if last in CALC_FAILED:
            raise StepError(f"calculation failed: {last} "
                            f"(ValidationResult={rows[0]['ValidationResult']})")
        if last in CALC_READY:
            return last, rows[0]["ValidationResult"]
        time.sleep(interval)
    raise StepError(f"timed out after {timeout}s waiting for calculation "
                    f"(last status: {last})")


def activate_order(org, order_id, activation_date):
    """Activate by status transition — the same thing the UI's Activate button does.

    There is no Connect resource for order activation in v67.0: the
    ``/connect/revenue-management/orders/actions/activate`` endpoint carried by
    older Postman collections returns NOT_FOUND, and the dev guide exposes only
    amend/renew/cancel/upgrade/downgrade/swap for revenue-management. Activation
    is the Draft -> Activated status change, which is what drives assetization and
    what the repo's RLM_Submit_Order_on_Activation flow is triggered by.
    """
    apex = f"""
Order o = [SELECT Id, Status, EffectiveDate FROM Order WHERE Id = '{order_id}'];
o.Status = 'Activated';
o.EffectiveDate = Date.valueOf('{activation_date}');
update o;
Order after = [SELECT Status, OrchestrationSbmsStatus FROM Order WHERE Id = '{order_id}'];
System.debug('STATUS=' + after.Status);
System.debug('SBMS=' + after.OrchestrationSbmsStatus);
"""
    vals = {}
    for line in sf_apex(org, apex):
        if "=" in line and line.split("=", 1)[0].isupper():
            k, v = line.split("=", 1)
            vals[k] = v
    if vals.get("STATUS") != "Activated":
        raise StepError(f"order did not activate (Status={vals.get('STATUS')})")
    return vals


def wait_for_assets(org, account_id, sku, timeout, interval):
    """Assetization is async — poll until the asset appears.

    Asset carries no lookup back to Order or OrderItem (the describe exposes no
    Order/Quote reference field), so the asset is matched on account + product
    rather than on the order. Safe here because the caller resets the account
    before building, so a matching asset can only be the one just created.
    """
    deadline = time.time() + timeout
    soql = ("SELECT Id, Name, CurrencyIsoCode, LifecycleStartDate, LifecycleEndDate "
            f"FROM Asset WHERE AccountId = '{account_id}' "
            f"AND Product2.StockKeepingUnit = '{sku}'")
    while time.time() < deadline:
        rows = sf_query(org, soql)
        if rows:
            return rows
        time.sleep(interval)
    return []


def verify_usage_buckets(org, asset_ids):
    """Confirm the wallets exist: entitlements, account rollup, buckets, rates."""
    quoted = ",".join(f"'{i}'" for i in asset_ids)
    counts = {}
    for label, soql in (
        ("TransactionUsageEntitlement",
         f"SELECT COUNT(Id) n FROM TransactionUsageEntitlement WHERE AssetId IN ({quoted})"),
        ("AssetRateCardEntry",
         f"SELECT COUNT(Id) n FROM AssetRateCardEntry WHERE AssetId IN ({quoted})"),
    ):
        rows = sf_query(org, soql)
        counts[label] = rows[0]["n"] if rows else 0

    # UsageEntitlementBucket has no AssetId; it hangs off the entitlements.
    rows = sf_query(
        org,
        "SELECT COUNT(Id) n FROM UsageEntitlementBucket WHERE TransactionUsageEntitlementId IN "
        f"(SELECT Id FROM TransactionUsageEntitlement WHERE AssetId IN ({quoted}))")
    counts["UsageEntitlementBucket"] = rows[0]["n"] if rows else 0

    rows = sf_query(
        org,
        "SELECT COUNT(Id) n FROM UsageEntitlementAccount WHERE AccountId IN "
        f"(SELECT AccountId FROM Asset WHERE Id IN ({quoted}))")
    counts["UsageEntitlementAccount"] = rows[0]["n"] if rows else 0
    return counts


# ----------------------------------------------------------------------
def build_one(org, account, args):
    print(f"\n{'=' * 74}\n{account}\n{'=' * 74}")

    ids = create_opportunity(org, account, args.sku, args.term, args.start,
                             args.end, args.billing_timing, args.selling_model,
                             args.anchor_sku)
    print(f"  opportunity  {ids['OPP_ID']}  ({ids['CURRENCY']}, "
          f"{ids.get('SELLING_MODEL')}/{ids.get('SELLING_MODEL_NAME')})")

    quote_id = place_quote(org, ids, account, args.start, args.end,
                           args.quantity, args.period_boundary, args.billing_frequency)
    print(f"  quote        {quote_id}  (starts {args.start})")

    order_id = create_order(org, quote_id, args.timeout, args.interval)
    print(f"  order        {order_id}")

    calc, validation = wait_for_calculation(org, order_id, args.timeout, args.interval)
    print(f"  calculation  {calc}" + (f"  validation={validation}" if validation else ""))

    act = activate_order(org, order_id, args.start)
    print(f"  activation   Status={act.get('STATUS')} Sbms={act.get('SBMS')}")

    assets = wait_for_assets(org, ids['ACCOUNT_ID'], args.sku,
                             args.timeout, args.interval)
    if not assets:
        raise StepError(f"no asset created within {args.timeout}s of activation")
    for a in assets:
        print(f"  asset        {a['Name']} ({a['CurrencyIsoCode']}) "
              f"{str(a['LifecycleStartDate'])[:10]} -> {str(a['LifecycleEndDate'])[:10]}")

    counts = verify_usage_buckets(org, [a["Id"] for a in assets])
    for k, v in counts.items():
        print(f"  {'OK ' if v else 'GAP'}          {k} = {v}")
    if not all(counts.values()):
        raise StepError("asset created but usage buckets are incomplete: "
                        + ", ".join(f"{k}={v}" for k, v in counts.items() if not v))

    # Backdating is the whole point — fail loudly if the platform overrode it.
    # A OneTime line has no lifecycle, so there is nothing to backdate.
    for a in assets:
        if ids.get("SELLING_MODEL") == "OneTime" or not a["LifecycleStartDate"]:
            continue
        actual = str(a["LifecycleStartDate"])[:10]
        if actual != args.start:
            raise StepError(f"asset lifecycle start is {actual}, expected {args.start} "
                            f"— backdating did not take")
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--org", required=True, help="sf CLI alias or username")
    ap.add_argument("--accounts", default=DEFAULT_ACCOUNTS,
                    help=f"comma-separated account names (default: {DEFAULT_ACCOUNTS})")
    ap.add_argument("--sku", default=DEFAULT_SKU, help=f"product SKU (default: {DEFAULT_SKU})")
    ap.add_argument("--start", default=DEFAULT_START,
                    help=f"backdated start, YYYY-MM-DD (default: {DEFAULT_START})")
    ap.add_argument("--end", default=DEFAULT_END,
                    help=f"line end date (default: {DEFAULT_END})")
    ap.add_argument("--quantity", type=int, default=1)
    ap.add_argument("--term", type=int, default=12, help="term months (default: 12)")
    ap.add_argument("--anchor-sku", default="",
                    help="bind the line to this product's existing asset on the "
                         "account (required for Pack products, which draw down "
                         "against an anchor and cannot stand alone)")
    ap.add_argument("--selling-model", default="",
                    choices=["", "TermDefined", "Evergreen", "OneTime"],
                    help="pick the PricebookEntry for this selling model when a "
                         "product exposes several (default: first by model name)")
    ap.add_argument("--billing-timing", default="Advance",
                    help="substring used to pick among a currency's BillingTreatments "
                         "(default: Advance)")
    ap.add_argument("--billing-frequency", default="Monthly",
                    choices=["MilestonePlan", "Monthly", "Quarterly", "Semi-Annual", "Annual"],
                    help="mandatory for TermDefined/Evergreen lines (default: Monthly)")
    ap.add_argument("--period-boundary", default="Anniversary",
                    choices=["AlignToCalendar", "Anniversary", "DayOfPeriod", "LastDayOfPeriod"],
                    help="line period boundary (default: Anniversary)")
    ap.add_argument("--timeout", type=int, default=300, help="per-poll timeout seconds")
    ap.add_argument("--interval", type=int, default=10, help="poll interval seconds")
    args = ap.parse_args()

    accounts = [a.strip() for a in args.accounts.split(",") if a.strip()]
    print(f"org={args.org}  sku={args.sku}  {args.start} -> {args.end}  "
          f"accounts={len(accounts)}")

    failures = []
    for account in accounts:
        try:
            build_one(args.org, account, args)
        except StepError as exc:
            print(f"  FAILED       {exc}")
            failures.append((account, str(exc)))
        except subprocess.TimeoutExpired:
            print("  FAILED       sf CLI call timed out")
            failures.append((account, "sf CLI timeout"))

    print(f"\n{'=' * 74}")
    ok = len(accounts) - len(failures)
    print(f"{ok}/{len(accounts)} account(s) reached an asset with usage buckets")
    for account, msg in failures:
        print(f"  FAIL  {account}: {msg}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
