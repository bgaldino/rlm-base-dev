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
import datetime as dt
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
API = "v68.0"

# CalculationStatus values that mean "done, stop polling". Anything else is
# either still in flight or a failure we surface verbatim.
CALC_READY = {"CompletedWithPricing", "CompletedWithTax", "CompletedWithoutPricing"}
# Quote-side statuses. Creating the order too early fails with "the calculation
# status of the quote is invalid", so the quote must settle first.
# NB: the org returns CompletedWithTax even though the describe's picklist for
# Quote.CalculationStatus lists TaxCalculationSuccess — accept both.
QUOTE_READY = {"CompletedWithPricing", "CompletedWithTax", "TaxCalculationSuccess",
               "CompletedWithoutPricing"}
QUOTE_FAILED = {"PriceCalculationFailed", "TaxCalculationFailed", "SaveFailedOrIncomplete",
                "ConfigurationFailed", "ReconciliationFailed", "GroupRampConfigurationFailed",
                "PstBaseStepFailed", "ARCStepFailed", "QuoteRequestFailed", "CloneFailed"}
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
                billing_frequency, bind_extra=False, group=False):
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

    ``group``: put the lines in one ``QuoteLineGroup``, with ``end`` as the group's
    first period, for ``ramp_group`` to turn into a group ramp.
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

    if group:
        records.append({"referenceId": "refGroup", "record": {
            "attributes": {"type": "QuoteLineGroup", "method": "POST"},
            "Name": "Year 1", "QuoteId": "@{refQuote.id}"}})
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
        if group:
            line["QuoteLineGroupId"] = "@{refGroup.id}"
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


RAMP_CREATE_PATH = f"/services/data/{API}/connect/revenue-management/sales-transaction-contexts/{{line}}/actions/ramp-deal-create"


def ramp_line(org, quote_id, years, quantities, timeout, interval):
    """Turn the quote's single line into a YEARLY line ramp of ``years`` segments.

    Line ramp = ``ramp-deal-create`` on the placed line (the product needs
    ``Product2.CanRamp``; group ramps don't, see the ramped-quotes skill). Each segment
    copies the primary, so the per-segment quantities (required) are patched through Place
    with the returned transaction context (as scripts/df_workshop does). That Place
    always runs: measured, ramp-deal-create alone leaves the quote unchanged, as the
    segments exist only in the context until a Place saves it.
    """
    lines = sf_query(org, f"SELECT Id FROM QuoteLineItem WHERE QuoteId = '{quote_id}'")
    if len(lines) != 1:
        raise StepError(f"--ramp-years needs a single-line quote, found {len(lines)} lines")
    line_id = lines[0]["Id"]
    resp = sf_rest(org, RAMP_CREATE_PATH.format(line=line_id), "POST", {
        "transactionId": quote_id, "transactionLineId": line_id,
        "subscriptionTerm": 12 * years, "subscriptionTermUnit": "MONTHS", "segmentType": "YEARLY",
        "executionSettings": {"executePricing": True, "executeConfigRules": False}})
    if not (isinstance(resp, dict) and resp.get("success")):
        raise StepError(f"ramp-deal-create: {json.dumps(resp)[:400]}")
    context_id = resp.get("transactionContextId")
    segs = []
    for st in resp.get("salesTransactionContext", {}).get("SalesTransaction", []):
        for it in st.get("SalesTransactionItem", []):
            if it.get("ItemSegmentName"):
                if not it.get("StartDate"):
                    raise StepError(f"ramp segment {it['ItemSegmentName']} has no StartDate")
                segs.append((it["StartDate"], it["id"], it["ItemSegmentName"]))
    segs.sort()
    if len(segs) != years:
        raise StepError(f"ramp-deal-create made {len(segs)} segment(s), expected {years}")
    if not context_id:
        raise StepError("ramp-deal-create returned no transactionContextId")
    recs = [{"referenceId": "qh", "record": {"attributes": {"type": "Quote", "method": "PATCH", "id": quote_id}}}]
    for (_, sid, _), qty in zip(segs, quantities):
        recs.append({"referenceId": sid, "record": {
            "attributes": {"type": "QuoteLineItem", "method": "PATCH", "id": sid}, "Quantity": qty}})
    # Same envelope as scripts/df_workshop: the ramp's context goes in contextDetails.
    payload = {"pricingPref": "System", "taxPref": "Skip",
               "graph": {"graphId": "rampSave", "records": recs},
               "contextDetails": {"contextId": context_id}}
    out = sf_rest(org, f"/services/data/{API}/connect/rev/sales-transaction/actions/place", "POST", payload)
    if isinstance(out, list) or (isinstance(out, dict) and (out.get("errorResponse") or out.get("isSuccess") is False)):
        raise StepError(f"saving the ramp failed: {json.dumps(out)[:400]}")
    # A Place that returns cleanly can still leave the quote unchanged (measured before the
    # context was passed), and the quote is already settled from before, so wait for the
    # segments themselves, with their quantities, then for the quote.
    def saved():
        rows = sf_query(org, f"SELECT Quantity, RampIdentifier FROM QuoteLineItem WHERE QuoteId = '{quote_id}' "
                             "ORDER BY StartDate")
        return (len(rows) == years and all(r.get("RampIdentifier") for r in rows)
                and [float(r["Quantity"]) for r in rows] == [float(q) for q in quantities])
    _poll(saved, f"{years} saved ramp segments with quantities {quantities}", timeout, interval)
    wait_for_quote(org, quote_id, timeout, interval)
    return [name for _, _, name in segs]


CLONE_PATH = f"/services/data/{API}/connect/rev/sales-transaction/actions/clone"


def _poll(fn, what, timeout, interval):
    """Wait until ``fn()`` is true: after a ramp call the quote may still read as settled."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if fn():
            return
        time.sleep(interval)
    raise StepError(f"timed out after {timeout}s waiting for {what}")


def _place(org, payload, what):
    out = sf_rest(org, f"/services/data/{API}/connect/rev/sales-transaction/actions/place", "POST", payload)
    if isinstance(out, list) or (isinstance(out, dict) and (out.get("errorResponse") or out.get("isSuccess") is False)):
        raise StepError(f"{what} failed: {json.dumps(out)[:400]}")


def _patch(sobject, rec_id, **fields):
    # The referenceId must be the record's own Id: EditGroup matches groups by it, and a
    # label such as "g" fails with "Index 0 out of bounds for length 0" (measured).
    return {"referenceId": rec_id, "record": dict({"attributes": {"type": sobject, "method": "PATCH", "id": rec_id}},
                                                  **fields)}


def ramp_segments(org, quote_id):
    """The quote's ramp segment groups in date order (the RampScheduleGroup parent left out).

    By StartDate, not SortOrder: the platform rewrites SortOrder (1 became -999999999).
    """
    return sf_query(org, "SELECT Id, SortOrder, IsRamped, SegmentType, StartDate, EndDate, ParentQuoteLineGroupId "
                         f"FROM QuoteLineGroup WHERE QuoteId = '{quote_id}' AND Type != 'RampScheduleGroup' "
                         "ORDER BY StartDate NULLS FIRST")


def _segments_settled(segs, n):
    return len(segs) == n and all(g.get("IsRamped") and g.get("SortOrder") is not None and g.get("StartDate")
                                  and g.get("EndDate") for g in segs)


def ramp_group(org, quote_id, start, years, quantities, timeout, interval):
    """Turn the quote's single group into a YEARLY group ramp of ``years`` segments.

    The ramped-quotes skill's sequence: EditGroup marks the group as segment 1, then each
    clone of the last segment adds the next year. Measured on 264: neither creates the
    multi-schedule RampScheduleGroup parent, and an order without one fails activation
    ("Specify a ramp schedule group for ramp segment", todo 159), so the parent is added
    and the segments reparented to it. Clones copy the quantity, so the per-segment
    quantities are patched last. Unlike a line ramp, the product needs no CanRamp.
    """
    groups = ramp_segments(org, quote_id)
    if len(groups) != 1:
        raise StepError(f"--ramp-kind group needs a single-group quote, found {len(groups)} groups")
    first = dt.date.fromisoformat(start)
    # Yearly segments are exactly 365 days (ramped-quotes skill), not calendar years.
    _place(org, {"groupRampAction": "EditGroup", "pricingPref": "System", "taxPref": "Skip",
                 "graph": {"graphId": "rampEdit", "records": [
                     _patch("Quote", quote_id),
                     _patch("QuoteLineGroup", groups[0]["Id"], StartDate=start,
                            EndDate=(first + dt.timedelta(days=364)).isoformat(),
                            SortOrder=1, IsRamped=True, SegmentType="Yearly")]}}, "EditGroup")
    _poll(lambda: _segments_settled(ramp_segments(org, quote_id), 1), "EditGroup to ramp the group", timeout, interval)
    wait_for_quote(org, quote_id, timeout, interval)
    for n in range(2, years + 1):
        last = ramp_segments(org, quote_id)[-1]
        if not last.get("IsRamped"):
            # A clone of a group EditGroup never converted still succeeds (ramped-quotes skill).
            raise StepError(f"segment group {last['Id']} isn't ramped; EditGroup didn't take")
        out = sf_rest(org, CLONE_PATH, "POST", {"salesTransactionId": quote_id, "recordIds": [last["Id"]],
                                                "options": {"lineScope": "AllLines"}})
        if not (isinstance(out, dict) and out.get("success")):
            raise StepError(f"cloning segment {n - 1}: {json.dumps(out)[:400]}")
        _poll(lambda: _segments_settled(ramp_segments(org, quote_id), n), f"segment {n} from the clone",
              timeout, interval)
        wait_for_quote(org, quote_id, timeout, interval)
    segs = ramp_segments(org, quote_id)
    if not _segments_settled(segs, years):
        raise StepError(f"the group ramp has {len(segs)} segment group(s), expected {years} ramped ones: {segs}")
    for prev, cur in zip(segs, segs[1:]):
        # Each clone must follow the previous segment; a clone of the wrong one overlaps it.
        if dt.date.fromisoformat(cur["StartDate"]) != dt.date.fromisoformat(prev["EndDate"]) + dt.timedelta(days=1):
            raise StepError(f"ramp segments aren't contiguous: {prev['StartDate']}..{prev['EndDate']} "
                            f"then {cur['StartDate']}..{cur['EndDate']}")
    parents = sf_query(org, f"SELECT Id FROM QuoteLineGroup WHERE QuoteId = '{quote_id}' AND Type = 'RampScheduleGroup'")
    if not parents:
        _place(org, {"pricingPref": "System", "taxPref": "Skip", "graph": {"graphId": "rampSchedule", "records": [
            _patch("Quote", quote_id),
            {"referenceId": "schedule", "record": {"attributes": {"type": "QuoteLineGroup", "method": "POST"},
                                                   "Name": "Ramp Schedule - 1", "QuoteId": quote_id,
                                                   "Type": "RampScheduleGroup"}}]}}, "adding the ramp schedule group")
        parents = sf_query(org, f"SELECT Id FROM QuoteLineGroup WHERE QuoteId = '{quote_id}' "
                                "AND Type = 'RampScheduleGroup'")
    if len(parents) != 1:
        raise StepError(f"expected one RampScheduleGroup on the quote, found {len(parents)}")
    orphans = [g["Id"] for g in segs if g.get("ParentQuoteLineGroupId") != parents[0]["Id"]]
    if orphans:
        # DML, not Place: a Place that reparents a group to one it creates fails with
        # "Cyclic dependencies detected" (measured).
        sf_apex(org, "List<QuoteLineGroup> gs = new List<QuoteLineGroup>();\n"
                     + "".join(f"gs.add(new QuoteLineGroup(Id = '{g}', ParentQuoteLineGroupId = '{parents[0]['Id']}'));\n"
                               for g in orphans) + "update gs;")
        if any(g.get("ParentQuoteLineGroupId") != parents[0]["Id"] for g in ramp_segments(org, quote_id)):
            raise StepError("reparenting the segments to the RampScheduleGroup didn't take")
    lines = sf_query(org, "SELECT Id, QuoteLineGroupId FROM QuoteLineItem "
                          f"WHERE QuoteId = '{quote_id}' ORDER BY StartDate")
    by_group = {g["Id"]: [l["Id"] for l in lines if l["QuoteLineGroupId"] == g["Id"]] for g in segs}
    if any(len(v) != 1 for v in by_group.values()) or len(lines) != years:
        raise StepError(f"expected one line per segment, found {by_group}")
    recs = [_patch("Quote", quote_id)] + [_patch("QuoteLineItem", by_group[g["Id"]][0], Quantity=qty)
                                          for g, qty in zip(segs, quantities)]
    # Force, not System: a System reprice of a CompletedWithPricing quote runs delta pricing,
    # which can skip lines it considers unchanged. A cloned segment can keep its clone-time price
    # (PriceWaterfallIdentifier still names the clone source) until a Force reprice (todo 160).
    _place(org, {"pricingPref": "Force", "taxPref": "Skip",
                 "graph": {"graphId": "rampQuantities", "records": recs}}, "setting the segment quantities")

    def saved():
        rows = {r["QuoteLineGroupId"]: r for r in sf_query(
            org, f"SELECT QuoteLineGroupId, Quantity, RampIdentifier FROM QuoteLineItem WHERE QuoteId = '{quote_id}'")}
        return ([float(rows[g["Id"]]["Quantity"]) if g["Id"] in rows else None for g in segs]
                == [float(q) for q in quantities] and all(r.get("RampIdentifier") for r in rows.values()))
    _poll(saved, f"segment quantities {quantities} with ramp identifiers", timeout, interval)
    wait_for_quote(org, quote_id, timeout, interval)
    # A line whose waterfall identifier doesn't start with its own Id (usually it names the clone
    # source; blank also fails) wasn't fully priced after the clone (todo 160). Force should leave none.
    stale = {r["Id"]: r.get("PriceWaterfallIdentifier")
             for r in sf_query(org, "SELECT Id, PriceWaterfallIdentifier FROM QuoteLineItem "
                                    f"WHERE QuoteId = '{quote_id}'")
             if (r.get("PriceWaterfallIdentifier") or "").split(":")[0] != r["Id"]}
    if stale:
        raise StepError("ramp line(s) not priced on their own Id after the Force reprice (todo 160); "
                        f"line -> PriceWaterfallIdentifier: {stale}")
    return [f"{g['StartDate']}..{g['EndDate']}" for g in segs]


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

    # --require-term-end must fail BEFORE the quote is placed and the order activated:
    # the resolved selling model is already known here (create_opportunity emitted
    # SKU0_SELLING_MODEL), so a OneTime/Evergreen resolution — or a missing --end —
    # is caught now, not after an invalid no-end asset has been persisted. Deferring
    # it to the post-activation block would leave one no-end asset behind per row
    # (build_renewal_buckets.py drives one run per bucket). The post-activation
    # end-date assertion below still runs to confirm the term LANDED on --end.
    model0 = ids.get("SKU0_SELLING_MODEL")
    term_less = model0 in ("OneTime", "Evergreen")
    if args.require_term_end:
        if not args.end:
            raise StepError("--require-term-end set but no --end was given; a bucketed "
                            "asset needs a term end to verify against.")
        if term_less:
            raise StepError(f"--require-term-end set but the resolved selling model is "
                            f"{model0}, which has no lifecycle end; a bucketed asset needs "
                            f"a TermDefined model. Pass --selling-model NAME (e.g. "
                            f"'Term Annual').")

    group = bool(args.ramp_years) and args.ramp_kind == "group"
    # A group ramp's lines start as segment 1: one Yearly segment of 365 days.
    line_end = (dt.date.fromisoformat(args.start) + dt.timedelta(days=364)).isoformat() if group else args.end
    quote_id = place_quote(org, ids, account, args.start, line_end,
                           args.quantity, args.period_boundary, args.billing_frequency,
                           args.bind_extra_lines, group=group)
    print(f"  quote        {quote_id}  (starts {args.start})")

    qcalc = wait_for_quote(org, quote_id, args.timeout, args.interval)
    print(f"  quote calc   {qcalc}")

    if group:
        names = ramp_group(org, quote_id, args.start, args.ramp_years, args.ramp_quantities,
                           args.timeout, args.interval)
        print(f"  group ramp   {len(names)} yearly segment(s): {', '.join(names)}"
              + f"  quantities={args.ramp_quantities}")
    elif args.ramp_years:
        names = ramp_line(org, quote_id, args.ramp_years, args.ramp_quantities, args.timeout, args.interval)
        print(f"  ramp         {len(names)} yearly segment(s): {', '.join(names)}"
              + f"  quantities={args.ramp_quantities}")

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
        # Activating the order fires CreateAssetOrderEvent, and
        # RLM_Platform_Event_CreateAssetOrderEvent_Stamp_Asset_Renewal_Info refreshes the
        # rate decision tables -- including Commitment_based_Rate_Adjustment, which was
        # missing from that chain until it was added. On an org built before that fix the
        # commitment rate is looked up against a stale table and consumption rates at the
        # undiscounted anchor rate, so the table has to be refreshed by hand there.
        # This script was given an SF CLI alias, but cci's --org takes the CCI alias (a
        # different registry), so the hint names the placeholder rather than reusing it.
        print("  note         commitment rate table refreshes via CreateAssetOrderEvent; on an "
              "org built\n               before that was wired up, refresh it before recording "
              "usage:\n"
              "                 cci task run refresh_dt_asset --org <cci_alias>")

    # Usage-bucket verification is meaningful only for usage products (Anchor/
    # Pack/Commit). A plain renewal term product (the renewal-asset-creation use
    # case) carries no entitlements, so the counts are legitimately zero and the
    # assertion would fail a perfectly good asset. --skip-usage-verify turns the
    # check into an informational print for those products; the asset itself is
    # still confirmed to exist above.
    if not args.skip_usage_verify:
        counts = verify_usage_buckets(org, [a["Id"] for a in assets])
        for k, v in counts.items():
            print(f"  {'OK ' if v else 'GAP'}          {k} = {v}")
        if not all(counts.values()):
            raise StepError("asset created but usage buckets are incomplete: "
                            + ", ".join(f"{k}={v}" for k, v in counts.items() if not v))
    else:
        print("  skip         usage-bucket verification (--skip-usage-verify)")

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

    # Symmetric end-date check. A zero exit alone does not prove the term LANDED where
    # asked: callers that bucket by expiry (build_renewal_buckets.py) need the derived
    # LifecycleEndDate to match --end, or an asset silently falls in the wrong window.
    # For a TermDefined line the platform derives the end from the requested EndDate, so
    # any mismatch — including a null end where one was asked for — fails loudly. OneTime
    # and Evergreen lines have no lifecycle end, so there is nothing to verify (and under
    # --require-term-end a term_less model has already failed above, before placement).
    # model0/term_less were resolved before the quote was placed and are reused here.
    if args.end and not term_less:
        for a in assets:
            actual_end = str(a["LifecycleEndDate"])[:10] if a["LifecycleEndDate"] else None
            if actual_end != args.end:
                raise StepError(f"asset lifecycle end is {actual_end}, expected {args.end} "
                                f"— term end did not take (selling model={model0})")
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
    ap.add_argument("--skip-usage-verify", action="store_true",
                    help="skip the usage-bucket assertion after activation. Use for a "
                         "plain renewal term product (no entitlements) so a valid, "
                         "non-usage asset is not failed for having zero buckets. Default "
                         "off for THIS script — i.e. a standalone run of a usage-anchor SKU "
                         "(QB-DB etc.) still verifies. (build_renewal_buckets.py passes this "
                         "flag by default; pass its --verify-usage to re-enable there.)")
    ap.add_argument("--selling-model", default="", metavar="NAME_OR_TYPE",
                    help="pick the PricebookEntry by selling model NAME (e.g. "
                         "'Term Monthly') or TYPE (TermDefined/Evergreen/OneTime). "
                         "A type matching several entries is rejected as ambiguous. "
                         "Default: first by model name")
    ap.add_argument("--require-term-end", action="store_true",
                    help="fail if the resolved selling model has no lifecycle end "
                         "(OneTime/Evergreen) or no --end was given, instead of exempting "
                         "it from the end-date check. Use when the caller buckets by expiry "
                         "(build_renewal_buckets.py passes it) and a no-end asset is a hard "
                         "error, not an exempt case.")
    ap.add_argument("--billing-timing", default="Advance",
                    help="substring used to pick among a currency's BillingTreatments "
                         "(default: Advance)")
    ap.add_argument("--billing-frequency", default="Monthly",
                    choices=["MilestonePlan", "Monthly", "Quarterly", "Semi-Annual", "Annual"],
                    help="mandatory for TermDefined/Evergreen lines (default: Monthly)")
    ap.add_argument("--period-boundary", default="Anniversary",
                    choices=["AlignToCalendar", "Anniversary", "DayOfPeriod", "LastDayOfPeriod"],
                    help="line period boundary (default: Anniversary)")
    ap.add_argument("--ramp-years", type=int, default=0,
                    help="make the line a YEARLY line ramp of N segments (ramp-deal-create). The "
                         "product needs Product2.CanRamp, and --start/--end must span N years")
    ap.add_argument("--ramp-quantities", type=lambda v: [float(x) for x in v.split(",")], default=None,
                    help="with --ramp-years: comma-separated quantity per segment, e.g. 1,2")
    ap.add_argument("--ramp-kind", choices=["line", "group"], default="line",
                    help="with --ramp-years: a line ramp (default) or a group ramp (one QuoteLineGroup "
                         "per year under a RampScheduleGroup; no CanRamp needed)")
    ap.add_argument("--timeout", type=int, default=300, help="per-poll timeout seconds")
    ap.add_argument("--interval", type=int, default=10, help="poll interval seconds")
    args = ap.parse_args()
    if args.ramp_years < 0 or any(q < 1 for q in args.ramp_quantities or []):
        ap.error("--ramp-years and every --ramp-quantities value must be positive")
    if args.ramp_years and not args.ramp_quantities:
        ap.error("--ramp-years needs --ramp-quantities (one quantity per segment; only that form was measured)")
    if args.ramp_quantities and len(args.ramp_quantities) != args.ramp_years:
        ap.error("--ramp-quantities needs one value per --ramp-years segment")
    if args.ramp_kind == "group" and not args.ramp_years:
        ap.error("--ramp-kind group needs --ramp-years")
    if args.ramp_years and args.with_sku:
        ap.error("--ramp-years ramps a single-line quote; drop --with-sku")
    if args.ramp_years:
        # Checked before any org call: a mismatch would otherwise fail after the quote exists.
        try:
            first = dt.date.fromisoformat(args.start)
        except (TypeError, ValueError):
            ap.error(f"--ramp-years needs --start as YYYY-MM-DD, got {args.start!r}")
        try:
            want = first.replace(year=first.year + args.ramp_years) - dt.timedelta(days=1)
        except ValueError:  # a 29 February start
            want = first.replace(year=first.year + args.ramp_years, day=28)
        if args.end != want.isoformat():
            ap.error(f"--ramp-years {args.ramp_years} needs --end {want} (N years from --start)")
        year1 = first.replace(year=first.year + 1) - dt.timedelta(days=1) if (first.month, first.day) != (2, 29) else None
        if args.ramp_kind == "group" and year1 != first + dt.timedelta(days=364):
            # A Yearly segment 1 is 365 days, but clones end later segments on calendar dates
            # (measured: 2027-05-01..2028-04-30), so a year 1 with 29 February would drift.
            ap.error("--ramp-kind group: year 1 from --start contains 29 February, so its 365-day segment "
                     "wouldn't end on the anniversary; pick another --start")

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
    outcome = ("created an asset (usage buckets NOT verified: --skip-usage-verify)"
               if args.skip_usage_verify else "reached an asset with usage buckets")
    print(f"{ok}/{len(accounts)} account(s) {outcome}")
    for account, msg in failures:
        print(f"  FAIL  {account}: {msg}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
