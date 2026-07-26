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

Commitment products need a post-assetization link
-------------------------------------------------
A commitment and its anchor are sold as SEPARATE quotes and assetized
independently, then tied together through the ``UsageCmtAssetRelatedObj``
junction (help: *Sell Commitment-Based Usage Products*, step 3)::

    --sku QB-CMT-TKN-TIER --link-commitment QB-DB-TOKEN

Nothing in the catalog can express this pairing: ``UsagePrdGrantBindingPolicy``
rejects commit products ("Select a Product with the Usage Model Type as Anchor
or Pack") and *"You can't bind a commitment-based usage product to a target."*
Without the junction the commitment is inert — consumption drains the anchor's
grant and rates at the anchor's rate. With it, consumption draws from the
committed amount first, at the discounted commit rate.

Because the junction joins two **Assets**, it is transactional data and can
never live in a design-time SFDMU plan.

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
to the Order or Quote it came from. This is now **enforced**: a preflight check
refuses to run when a matching asset already exists. Pass
``--allow-existing-asset`` to proceed anyway, in which case the post-activation
poll requires a genuinely NEW asset id rather than accepting the old one.

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
# Quote-side statuses. Creating the order too early fails with "the calculation
# status of the quote is invalid", so the quote must settle first.
# NB: the org returns CompletedWithTax even though the describe's picklist for
# Quote.CalculationStatus lists TaxCalculationSuccess — accept both.
QUOTE_READY = {"CompletedWithPricing", "CompletedWithTax", "TaxCalculationSuccess",
               "CompletedWithoutPricing"}
QUOTE_FAILED = {"PriceCalculationFailed", "TaxCalculationFailed", "SaveFailedOrIncomplete"}
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


def soql_str(value):
    """Quote a value as a SOQL string literal, escaping backslash then quote.

    Account names legitimately contain apostrophes (O'Brien), which would
    otherwise break the query -- and sf_query returns [] on failure, so the
    breakage surfaces as "no records" rather than an error.
    """
    return "'" + str(value).replace("\\", "\\\\").replace("'", "\\'") + "'"


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
def create_opportunity(org, account, skus, start, end, billing_timing,
                       selling_model, anchor_sku):
    """Create the Opportunity, mirroring RLM_QuickQuote's mapping.

    Returns the ids the Place Sales Transaction graph needs. RLM_QuickQuote is a
    SCREEN flow so Apex cannot invoke it, but every automation it depends on is
    record-triggered, so this insert fires the same behaviour (notably the
    account-currency defaulting added for multicurrency).
    """
    sku_list = ", ".join(f"'{esc(k)}'" for k in skus)
    apex = f"""
public class QuoteBuildException extends Exception {{}}

final String ACCOUNT_NAME = '{esc(account)}';
final List<String> SKUS = new List<String>{{{sku_list}}};
final Date END_DATE = Date.valueOf('{end}');

Account acct = [SELECT Id, Name, CurrencyIsoCode FROM Account
                WHERE Name = :ACCOUNT_NAME LIMIT 1];
Pricebook2 standard = [SELECT Id FROM Pricebook2 WHERE IsStandard = true LIMIT 1];
Map<String, Product2> prodBySku = new Map<String, Product2>();
for (Product2 pr : [SELECT Id, StockKeepingUnit FROM Product2
                    WHERE StockKeepingUnit IN :SKUS]) {{
    prodBySku.put(pr.StockKeepingUnit, pr);
}}

// Resolve, for EVERY sku on the quote, the PricebookEntry that pins the line to
// a selling model. A product can expose several (QB-DAT-THPT has Evergreen,
// Term Monthly and Term Annual) and the selling model dictates which line fields
// are legal, so choose deliberately rather than taking the first entry back.
String wanted = '{esc(selling_model)}';

// Bulkified on purpose: --with-sku is repeatable, so a per-SKU query here would be
// SOQL inside a loop and a large enough quote would hit the 100-query governor.
Set<Id> productIds = new Set<Id>();
for (Product2 pr : prodBySku.values()) {{ productIds.add(pr.Id); }}
Map<Id, List<PricebookEntry>> pbesByProduct = new Map<Id, List<PricebookEntry>>();
for (PricebookEntry e : [SELECT Id, UnitPrice, Product2Id,
                                ProductSellingModel.SellingModelType,
                                ProductSellingModel.Name
                         FROM PricebookEntry
                         WHERE Product2Id IN :productIds AND Pricebook2Id = :standard.Id
                           AND CurrencyIsoCode = :acct.CurrencyIsoCode
                           AND IsActive = true
                         ORDER BY ProductSellingModel.Name]) {{
    if (!pbesByProduct.containsKey(e.Product2Id)) {{
        pbesByProduct.put(e.Product2Id, new List<PricebookEntry>());
    }}
    pbesByProduct.get(e.Product2Id).add(e);
}}

for (Integer i = 0; i < SKUS.size(); i++) {{
    String sku = SKUS[i];
    Product2 prod = prodBySku.get(sku);
    if (prod == null) {{
        throw new QuoteBuildException('No product with SKU ' + sku);
    }}
    List<PricebookEntry> pbes = pbesByProduct.containsKey(prod.Id)
        ? pbesByProduct.get(prod.Id) : new List<PricebookEntry>();
    if (pbes.isEmpty()) {{
        throw new QuoteBuildException('No active ' + acct.CurrencyIsoCode
            + ' PricebookEntry for ' + sku);
    }}
    PricebookEntry pbe = pbes[0];
    if (wanted != '') {{
        // Match on selling model NAME first, then TYPE. Type alone is not unique --
        // QB-DAT-THPT exposes 'Term Monthly' and 'Term Annual', BOTH TermDefined --
        // so matching type would silently take whichever sorts first and could pair
        // a monthly billing frequency with the annual entry. An ambiguous type is
        // rejected rather than guessed.
        Boolean matched = false;
        for (PricebookEntry e : pbes) {{
            if (e.ProductSellingModel != null && e.ProductSellingModel.Name == wanted) {{
                pbe = e; matched = true; break;
            }}
        }}
        if (!matched) {{
            List<PricebookEntry> byType = new List<PricebookEntry>();
            for (PricebookEntry e : pbes) {{
                if (e.ProductSellingModel != null
                    && e.ProductSellingModel.SellingModelType == wanted) {{ byType.add(e); }}
            }}
            if (byType.size() > 1) {{
                List<String> names = new List<String>();
                for (PricebookEntry e : byType) {{ names.add(e.ProductSellingModel.Name); }}
                throw new QuoteBuildException('Selling model type ' + wanted + ' is AMBIGUOUS for '
                    + sku + ' -- it matches ' + byType.size() + ' entries: ' + String.join(names, ', ')
                    + '. Pass one of those names to --selling-model instead of the type.');
            }}
            if (byType.size() == 1) {{ pbe = byType[0]; matched = true; }}
        }}
        // Fail loudly. Falling back to pbes[0] would silently build the quote on a
        // DIFFERENT selling model than the caller asked for, and the selling model
        // dictates which line fields are legal -- so the eventual error surfaces as
        // an unrelated field validation much later.
        if (!matched) {{
            // List NAME (type) so the message is directly actionable -- the name is
            // what has to be passed back in when a type is ambiguous.
            List<String> available = new List<String>();
            for (PricebookEntry e : pbes) {{
                available.add(e.ProductSellingModel == null ? 'unknown'
                    : e.ProductSellingModel.Name + ' (' + e.ProductSellingModel.SellingModelType + ')');
            }}
            throw new QuoteBuildException('No active ' + acct.CurrencyIsoCode
                + ' PricebookEntry for ' + sku + ' with selling model ' + wanted
                + '. Available: ' + String.join(available, ', '));
        }}
    }}
    System.debug('SKU' + i + '_PRODUCT_ID=' + prod.Id);
    System.debug('SKU' + i + '_PBE_ID=' + pbe.Id);
    System.debug('SKU' + i + '_UNIT_PRICE=' + pbe.UnitPrice);
    System.debug('SKU' + i + '_SELLING_MODEL=' + (pbe.ProductSellingModel == null
        ? 'unknown' : pbe.ProductSellingModel.SellingModelType));
    System.debug('SKU' + i + '_NAME=' + sku);
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
// Same rule as --selling-model: a requested timing that matches nothing is a
// mistake, not a filter. Silently keeping treatments[0] meant `--billing-timing
// Arrear` (a typo for Arrears) produced an Advance quote that looked successful.
BillingTreatment treatment = null;
for (BillingTreatment t : treatments) {{
    if (t.Name.containsIgnoreCase('{esc(billing_timing)}')) {{ treatment = t; break; }}
}}
if (treatment == null) {{
    List<String> names = new List<String>();
    for (BillingTreatment t : treatments) {{ names.add(t.Name); }}
    throw new QuoteBuildException('No BillingTreatment name contains "{billing_timing}" for '
        + acct.CurrencyIsoCode + '. Available: ' + String.join(names, ', '));
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
String anchorSku = '{esc(anchor_sku)}';
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
System.debug('TREATMENT_ID=' + treatment.Id);
System.debug('TREATMENT_CANCHANGE=' + treatment.CanChangeBillingFrequency);
"""
    vals = {}
    for line in sf_apex(org, apex):
        if "=" in line and line.split("=", 1)[0].isupper():
            k, v = line.split("=", 1)
            vals[k] = v
    missing = {"ACCOUNT_ID", "OPP_ID", "SKU0_PBE_ID"} - set(vals)
    if missing:
        raise StepError(f"opportunity step did not report {sorted(missing)}")
    return vals


def place_quote(org, ids, account, start, end, quantity, period_boundary,
                billing_frequency, bind_extra=False):
    """Create the Quote + line via Place Sales Transaction.

    Direct QuoteLineItem DML is NOT viable for a TermDefined product: the platform
    demands BillingFrequency ("When the SellingModelType is Evergreen or
    Term-Defined, BillingFrequency can't be null") and refuses to let you set it
    unless the line's BillingTreatment has CanChangeBillingFrequency = true. That
    flag was false on every QB treatment originally, which is what made the
    transaction API the only workable path; this branch sets it true on all 15 QB
    treatments so the frequency CAN be supplied, and this function sends
    BillingFrequency explicitly in the payload. The transaction API remains the
    supported path for adding a line to a quote.
    """
    # Which line fields are legal depends on the SELLING MODEL, not the product:
    #   OneTime     -> BillingFrequency must be null; EndDate rejected
    #   Evergreen   -> EndDate rejected
    #   TermDefined -> BillingFrequency required, EndDate allowed
    #
    # Every sku after the first becomes an additional line on the SAME quote,
    # bound to the first line. That is what a Commit product requires: it is a
    # rate modifier on an anchor line, and pointing its BindingInstanceTargetId
    # at an existing Asset is rejected ("Check that you've selected the correct
    # usage product for the associated quote or order").
    records = [
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
        }
    ]

    n = sum(1 for k in ids if k.endswith("_PBE_ID"))
    for i in range(n):
        model = ids.get(f"SKU{i}_SELLING_MODEL", "TermDefined")
        line = {
            "attributes": {"type": "QuoteLineItem", "method": "POST"},
            "QuoteId": "@{refQuote.id}",
            "Product2Id": ids[f"SKU{i}_PRODUCT_ID"],
            "PricebookEntryId": ids[f"SKU{i}_PBE_ID"],
            "UnitPrice": float(ids[f"SKU{i}_UNIT_PRICE"]),
            "Quantity": quantity,
            "StartDate": start,
        }
        if model not in ("Evergreen", "OneTime"):
            line["EndDate"] = end
        if model != "OneTime":
            line["PeriodBoundary"] = period_boundary
            line["BillingTreatmentId"] = ids["TREATMENT_ID"]
            line["BillingFrequency"] = billing_frequency
        if i == 0:
            # Only the primary line may bind to a pre-existing anchor ASSET
            # (that is the Pack case).
            if ids.get("ANCHOR_ASSET_ID"):
                line["BindingInstanceTargetId"] = ids["ANCHOR_ASSET_ID"]
        elif bind_extra:
            # Opt-in only. A Commit product rejects BindingInstanceTargetId
            # entirely — pointed at an anchor Asset *or* at the anchor line in
            # the same quote it returns "We couldn't bind the usage resource".
            # Co-selling on one quote is the construct; the binding is implicit.
            line["BindingInstanceTargetId"] = "@{refLine0.id}"
        records.append({"referenceId": f"refLine{i}", "record": line})

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
        "graph": {"graphId": "buildQuoteToAsset", "records": records},
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


def wait_for_quote(org, quote_id, timeout, interval):
    """Let the quote finish pricing before ordering.

    Place Sales Transaction returns as soon as the graph is accepted, but pricing
    and tax continue asynchronously. Calling createOrdersFromQuote while that is
    in flight fails with "We couldn't create an order for this quote because the
    calculation status of the quote is invalid".
    """
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        rows = sf_query(org, f"SELECT CalculationStatus FROM Quote WHERE Id = '{quote_id}'")
        if not rows:
            raise StepError("quote disappeared while polling")
        last = rows[0]["CalculationStatus"]
        if last in QUOTE_FAILED:
            raise StepError(f"quote calculation failed: {last}")
        if last in QUOTE_READY:
            return last
        time.sleep(interval)
    raise StepError(f"timed out after {timeout}s waiting for quote calculation "
                    f"(last status: {last})")


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


def link_commitment(org, account_id, commit_sku, anchor_sku):
    """Step 3 of "Sell Commitment-Based Usage Products" — the junction.

    A commitment and its anchor are sold as SEPARATE quotes and assetized
    independently. Nothing in the catalog ties them together: a commit product is
    rejected by UsagePrdGrantBindingPolicy ("Select a Product with the Usage Model
    Type as Anchor or Pack") and cannot be given a binding target at all. The link
    is made AFTER both assets exist, through UsageCmtAssetRelatedObj:

        AssetId         = the COMMITMENT asset
        RelatedObjectId = the ANCHOR asset (Account/Contract/custom also allowed)

    Without it the commitment is inert — consumption drains the anchor's grant and
    rates at the anchor's rate. With it, consumption draws from the committed
    tokens first at the discounted commit rate.

    NB: this is transactional data (it joins two Assets), so it can never live in a
    design-time SFDMU plan.
    """
    apex = f"""
Asset anchor = [SELECT Id, LifecycleStartDate, LifecycleEndDate FROM Asset
                WHERE AccountId = '{account_id}'
                  AND Product2.StockKeepingUnit = '{esc(anchor_sku)}'
                ORDER BY CreatedDate DESC LIMIT 1];
Asset cmtAsset = [SELECT Id FROM Asset
                  WHERE AccountId = '{account_id}'
                    AND Product2.StockKeepingUnit = '{esc(commit_sku)}'
                  ORDER BY CreatedDate DESC LIMIT 1];

// Re-linking the same pair would violate "You can't link multiple commitment
// products to the same anchor that have the same validity period".
List<UsageCmtAssetRelatedObj> existing = [
    SELECT Id FROM UsageCmtAssetRelatedObj
    WHERE AssetId = :cmtAsset.Id AND RelatedObjectId = :anchor.Id];
if (!existing.isEmpty()) {{
    System.debug('LINK=existing ' + existing[0].Id);
}} else {{
    UsageCmtAssetRelatedObj lnk = new UsageCmtAssetRelatedObj(
        AssetId = cmtAsset.Id,
        RelatedObjectId = anchor.Id,
        EffectiveStartDateTime = anchor.LifecycleStartDate,
        EffectiveEndDateTime = anchor.LifecycleEndDate);
    insert lnk;
    System.debug('LINK=' + lnk.Id);
}}
"""
    for line in sf_apex(org, apex):
        if line.startswith("LINK="):
            return line.split("=", 1)[1]
    raise StepError("commitment link was not created")


def wait_for_assets(org, account_id, sku, timeout, interval, exclude_ids=frozenset()):
    """Assetization is async — poll until the NEW asset appears.

    Asset carries no lookup back to Order or OrderItem (the describe exposes no
    Order/Quote reference field), so the asset can only be matched on account +
    product. `exclude_ids` carries the ids that existed BEFORE this run, so a
    pre-existing asset cannot satisfy the poll immediately and be mistaken for the
    one just created — the caller's reset is no longer an unenforced assumption.
    """
    deadline = time.time() + timeout
    soql = ("SELECT Id, Name, CurrencyIsoCode, LifecycleStartDate, LifecycleEndDate "
            f"FROM Asset WHERE AccountId = {soql_str(account_id)} "
            f"AND Product2.StockKeepingUnit = {soql_str(sku)}")
    while time.time() < deadline:
        rows = [r for r in sf_query(org, soql) if r["Id"] not in exclude_ids]
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

    # Preflight: record the account's EXISTING assets for this SKU. Asset carries no
    # lookup back to the Order or Quote it came from, so the post-activation poll can
    # only match on account + product -- and a pre-existing asset satisfies that poll
    # immediately, before the new order assetizes. The script would then verify (and
    # link a commitment to) the OLD asset while reporting the new chain as successful.
    preexisting = {r["Id"] for r in sf_query(
        org,
        "SELECT Id FROM Asset WHERE Account.Name = "
        f"{soql_str(account)} AND Product2.StockKeepingUnit = {soql_str(args.sku)}")}
    if preexisting and not args.allow_existing_asset:
        raise StepError(
            f"{account} already has {len(preexisting)} asset(s) for {args.sku}. "
            "The post-activation poll matches on account+product, so an existing "
            "asset would be mistaken for the new one. Reset the account first "
            "(Account Utilities / RLM_AccountUtilities), or pass "
            "--allow-existing-asset to require a NEW asset id instead.")

    skus = [args.sku] + list(args.with_sku or [])
    ids = create_opportunity(org, account, skus, args.start,
                             args.end, args.billing_timing, args.selling_model,
                             args.anchor_sku)
    print(f"  opportunity  {ids['OPP_ID']}  ({ids['CURRENCY']}, "
          f"{ids.get('SKU0_SELLING_MODEL')})")

    quote_id = place_quote(org, ids, account, args.start, args.end,
                           args.quantity, args.period_boundary, args.billing_frequency,
                           args.bind_extra_lines)
    print(f"  quote        {quote_id}  (starts {args.start})")

    qcalc = wait_for_quote(org, quote_id, args.timeout, args.interval)
    print(f"  quote calc   {qcalc}")

    order_id = create_order(org, quote_id, args.timeout, args.interval)
    print(f"  order        {order_id}")

    calc, validation = wait_for_calculation(org, order_id, args.timeout, args.interval)
    print(f"  calculation  {calc}" + (f"  validation={validation}" if validation else ""))

    act = activate_order(org, order_id, args.start)
    print(f"  activation   Status={act.get('STATUS')} Sbms={act.get('SBMS')}")

    assets = wait_for_assets(org, ids['ACCOUNT_ID'], args.sku,
                             args.timeout, args.interval, exclude_ids=preexisting)
    if not assets:
        raise StepError(f"no NEW asset created within {args.timeout}s of activation")
    for a in assets:
        print(f"  asset        {a['Name']} ({a['CurrencyIsoCode']}) "
              f"{str(a['LifecycleStartDate'])[:10]} -> {str(a['LifecycleEndDate'])[:10]}")

    if args.link_commitment:
        link_id = link_commitment(org, ids["ACCOUNT_ID"], args.sku, args.link_commitment)
        print(f"  commitment   linked to {args.link_commitment} anchor ({link_id})")
        # Selling the commitment created its AssetRateAdjustment rows, but
        # Commitment_based_Rate_Adjustment is only refreshed by prepare_rlm_org --
        # nothing re-syncs it for a sale made after the build, and its siblings on the
        # same source object DO stay current, so the staleness is easy to miss.
        print("  ⚠ ACTION      refresh the commitment decision table BEFORE recording "
              "usage, or the commit rate will not be found:")
        print("                  cci org default <cci_alias>   # refresh_dt_* take no --org")
        print("                  cci task run refresh_dt_asset")

    counts = verify_usage_buckets(org, [a["Id"] for a in assets])
    for k, v in counts.items():
        print(f"  {'OK ' if v else 'GAP'}          {k} = {v}")
    if not all(counts.values()):
        raise StepError("asset created but usage buckets are incomplete: "
                        + ", ".join(f"{k}={v}" for k, v in counts.items() if not v))

    # Backdating is the whole point — fail loudly if the platform overrode it.
    # A OneTime line has no lifecycle, so there is nothing to backdate. The key is
    # SKU0_SELLING_MODEL, not SELLING_MODEL: the Apex emits it per index. Read bare
    # it was always None, so the exemption never fired and only the per-asset
    # LifecycleStartDate check below was doing any work.
    for a in assets:
        if ids.get("SKU0_SELLING_MODEL") == "OneTime" or not a["LifecycleStartDate"]:
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
    ap.add_argument("--with-sku", action="append", metavar="SKU",
                    help="additional product on the SAME quote. Repeatable. NOT for "
                         "Commit products -- they reject BindingInstanceTargetId and "
                         "must be sold as a SEPARATE quote, then joined to the anchor "
                         "asset with --link-commitment (see --bind-extra-lines below, "
                         "which is off by default for that reason)")
    ap.add_argument("--bind-extra-lines", action="store_true",
                    help="bind --with-sku lines to the first line. Off by default: "
                         "Commit products reject BindingInstanceTargetId entirely")
    ap.add_argument("--link-commitment", default="", metavar="ANCHOR_SKU",
                    help="after assetizing a COMMITMENT product, link it to this "
                         "anchor's asset via UsageCmtAssetRelatedObj. Required for "
                         "the commitment to affect rating at all - without it the "
                         "commitment is inert")
    ap.add_argument("--anchor-sku", default="",
                    help="bind the line to this product's existing asset on the "
                         "account (required for Pack products, which draw down "
                         "against an anchor and cannot stand alone)")
    # Deliberately NOT restricted to the three type values: a type is not unique
    # (QB-DAT-THPT has 'Term Monthly' and 'Term Annual', both TermDefined), so the
    # model NAME must be passable to disambiguate. Matching tries name first, then
    # type, and rejects an ambiguous type rather than guessing.
    ap.add_argument("--allow-existing-asset", action="store_true",
                    help="proceed when the account already has an asset for this SKU; "
                         "the post-activation poll then requires a NEW asset id "
                         "rather than accepting the pre-existing one")
    ap.add_argument("--selling-model", default="", metavar="NAME_OR_TYPE",
                    help="pick the PricebookEntry by selling model NAME (e.g. "
                         "'Term Monthly') or TYPE (TermDefined/Evergreen/OneTime). "
                         "A type matching several entries is rejected as ambiguous. "
                         "Default: first by model name")
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
