#!/usr/bin/env python3
"""Extract the DF workshop quotes from the working org as a portable replay spec.

Why a "replay spec" and not a data dump
---------------------------------------
The workshop's value records are three Quotes and their line items
(``Quote PDF`` + two ramp quotes). Their child records -- QuoteLineItem,
QuoteLineItemAttribute, QuoteLineDetail, price adjustments, ramp segments --
are *derived*: the platform generates them when a quote is created and priced
through the RLM transaction/pricing pipeline. Direct DML of a QuoteLineItem is
rejected for TermDefined products (BillingFrequency/BillingTreatment coupling),
and even where it is accepted it produces an un-priced, internally inconsistent
line. So we cannot "copy the rows" -- we must re-create each quote through
``POST /connect/rev/sales-transaction/actions/place`` (Place Sales Transaction)
and let the org generate the children.

This script therefore captures the *inputs* to that replay, not the outputs:
the quote header, the account/contact/opportunity it hangs off, and per line
the product (by SKU, not Id), quantity, selling model, dates, billing terms,
and -- for ramps -- the ramp/segment identity fields that group the segment
lines into one ramp. Every Salesforce Id is resolved to a natural key so the
spec is portable into any clone. The companion insert script consumes this
JSON; see the skill README.

Read-only. Does not mutate the source org.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import OrderedDict

API = "v68.0"

# The three quotes the DF Hands-On canvas calls out. Override with --quotes.
DEFAULT_QUOTES = [
    "Quote PDF",
    "3 Year Ramp - AI Licenses",
    "4 Year Ramp - AI Licenses",
]

# Seeded scenario Opportunities the exercise guide drives quotes *from* but which
# hang off no captured quote, so the quote-anchor sweep misses them. The Coworker
# exercises look these up by literal name (Ex.: "Starter Opportunity", "Target
# Opportunity" on Acme). Override with --seed-opps.
DEFAULT_SEED_OPPS = [
    "Starter Opportunity",
    "Target Opportunity",
]

# Seeded scenario Accounts with no seeded opportunity of their own. The guide has
# the agent create "New Opportunity for Apex Dynamics" *live*, so the account is
# the drift, not the opp. (Acme rides in on its seed opps above.) Override with
# --seed-accounts.
DEFAULT_SEED_ACCOUNTS = [
    "Apex Dynamics",
]

# Audit/system fields carry no replay value and differ per org; drop on output.
SYSTEM_FIELDS = {
    "Id", "IsDeleted", "CreatedById", "CreatedDate", "LastModifiedById",
    "LastModifiedDate", "SystemModstamp", "LastViewedDate", "LastReferencedDate",
    "LastActivityDate", "OwnerId",
}
# Compound / unqueryable-in-bulk field types we never SELECT.
SKIP_TYPES = {"address", "location", "base64", "complexvalue"}

# Fields dropped from output: real-person / seller-identity values that carry no
# replay value (the quote-header replay never uses them) and must not be committed.
# RLM_Seller_Email__c / RLM_Sales_Rep_Name__c hold the running seller's real email
# and name — scrub both.
SENSITIVE_FIELDS = {"RLM_Seller_Email__c", "RLM_Sales_Rep_Name__c"}

# reference field -> (target sobject, name expression used as the portable key)
# Resolved to natural keys so the spec does not carry org-specific Ids.
REFERENCE_KEYS = {
    "Product2Id": ("Product2", "StockKeepingUnit"),
    "Pricebook2Id": ("Pricebook2", "Name"),
    "PricebookEntryId": ("PricebookEntry", None),   # special-cased below
    "QuoteAccountId": ("Account", "Name"),
    "AccountId": ("Account", "Name"),
    "OpportunityId": ("Opportunity", "Name"),
    "ContactId": ("Contact", "Name"),
    "BillingTreatmentId": ("BillingTreatment", "Name"),
    "QuoteLineGroupId": ("QuoteLineGroup", "Name"),
    "ProductSellingModelId": ("ProductSellingModel", "Name"),
}


class ExtractError(RuntimeError):
    pass


class UnknownObjectError(ExtractError):
    """The org has no such sObject -- safe to skip an *optional* child collection.

    Distinct from a describe that failed for any other reason (auth, CLI,
    transient, malformed response): those must propagate, not be swallowed as
    "object absent", or we would write a successful-but-incomplete replay spec.
    """
    pass


def _is_unknown_object(name, msg):
    """True only when a describe error positively identifies a missing sObject."""
    hay = f"{name} {msg}".lower()
    return any(s in hay for s in (
        "not supported", "does not exist", "invalid_type", "no such sobject",
        "cannot find", "not found", "unknown sobject", "invalid sobject"))


# ----------------------------------------------------------------------
# sf CLI plumbing (auth delegated to the CLI -- no tokens handled here)
# ----------------------------------------------------------------------
def _run(args, timeout=300):
    env = {**os.environ, "SF_TEMP_SHOW_SECRETS": "true"}
    p = subprocess.run(args, capture_output=True, text=True, env=env, timeout=timeout)
    return p.returncode, p.stdout, p.stderr


def soql_str(value):
    """Quote a value as a SOQL string literal (names may contain apostrophes)."""
    return "'" + str(value).replace("\\", "\\\\").replace("'", "\\'") + "'"


def sf_query(org, soql):
    rc, out, err = _run(["sf", "data", "query", "-q", soql, "--target-org", org, "--json"])
    try:
        d = json.loads(out)
    except json.JSONDecodeError:
        raise ExtractError(f"query failed: {(err or out)[:400]}")
    if "result" not in d:
        raise ExtractError(f"query failed: {d.get('message', out)[:400]}")
    return d["result"]["records"]


_DESCRIBE_CACHE: dict[str, dict] = {}


def describe(org, sobject):
    if sobject not in _DESCRIBE_CACHE:
        rc, out, err = _run(["sf", "sobject", "describe", "--sobject", sobject,
                             "--target-org", org, "--json"])
        try:
            payload = json.loads(out)
        except json.JSONDecodeError:
            payload = None
        if payload and payload.get("status", 1) == 0 and "result" in payload:
            _DESCRIBE_CACHE[sobject] = payload["result"]
        else:
            name = (payload or {}).get("name") or ""
            msg = ((payload or {}).get("message") or err or out or "").strip()
            # Only a positively-identified missing object is skippable; every other
            # failure (auth, CLI, transient, malformed) must propagate so we never
            # silently drop a child collection into a "successful" spec.
            if _is_unknown_object(name, msg):
                raise UnknownObjectError(f"{sobject} not present in {org!r}: {msg[:200]}")
            raise ExtractError(f"describe {sobject} failed: {msg[:300]}")
    return _DESCRIBE_CACHE[sobject]


def queryable_fields(org, sobject):
    """Simple (non-compound) field names for a SELECT *-equivalent query."""
    fields = describe(org, sobject)["fields"]
    return [f["name"] for f in fields if f["type"] not in SKIP_TYPES]


def strip_attributes(rec):
    return {k: v for k, v in rec.items() if k != "attributes"}


# ----------------------------------------------------------------------
# Id -> natural key resolution (cached)
# ----------------------------------------------------------------------
_KEY_CACHE: dict[tuple, object] = {}


def resolve_key(org, field, rec_id):
    """Resolve one reference Id to a portable natural key."""
    if not rec_id or field not in REFERENCE_KEYS:
        return None
    cache_key = (field, rec_id)
    if cache_key in _KEY_CACHE:
        return _KEY_CACHE[cache_key]

    obj, name_field = REFERENCE_KEYS[field]
    if field == "PricebookEntryId":
        rows = sf_query(org,
            "SELECT Product2.StockKeepingUnit, Pricebook2.Name, CurrencyIsoCode "
            f"FROM PricebookEntry WHERE Id = {soql_str(rec_id)}")
        val = None
        if rows:
            r = rows[0]
            val = {
                "productSku": (r.get("Product2") or {}).get("StockKeepingUnit"),
                "pricebook": (r.get("Pricebook2") or {}).get("Name"),
                "currency": r.get("CurrencyIsoCode"),
            }
    else:
        rows = sf_query(org, f"SELECT {name_field} FROM {obj} WHERE Id = {soql_str(rec_id)}")
        val = rows[0].get(name_field) if rows else None

    _KEY_CACHE[cache_key] = val
    return val


def clean_record(org, rec):
    """Drop system fields and nulls; add resolved natural keys for references.

    Keeps the raw source Id under ``_sourceId`` purely for traceability/debug --
    the insert side must never use it.
    """
    rec = strip_attributes(rec)
    out = OrderedDict()
    out["_sourceId"] = rec.get("Id")
    refs = OrderedDict()
    for k, v in rec.items():
        if k in SYSTEM_FIELDS or k in SENSITIVE_FIELDS or v is None:
            continue
        out[k] = v
        if k in REFERENCE_KEYS:
            resolved = resolve_key(org, k, v)
            if resolved is not None:
                refs[k.replace("Id", "Key") if k.endswith("Id") else k + "Key"] = resolved
    if refs:
        out["_keys"] = refs
    return out


# ----------------------------------------------------------------------
# Extraction
# ----------------------------------------------------------------------
def extract_quote(org, quote_name):
    q_fields = queryable_fields(org, "Quote")
    rows = sf_query(org, f"SELECT {', '.join(q_fields)} FROM Quote "
                         f"WHERE Name = {soql_str(quote_name)}")
    if not rows:
        raise ExtractError(f"quote not found: {quote_name!r}")
    if len(rows) > 1:
        # Taking an unordered first row would make the spec nondeterministic and
        # could capture the wrong workshop quote. Fail on ambiguity instead.
        raise ExtractError(
            f"{len(rows)} quotes named {quote_name!r} in {org!r}; ambiguous. "
            "Rename/remove the duplicates (or narrow --quotes) before extracting.")
    quote = clean_record(org, rows[0])
    quote_id = rows[0]["Id"]

    # Lines
    qli_fields = queryable_fields(org, "QuoteLineItem")
    qli_rows = sf_query(org, f"SELECT {', '.join(qli_fields)} FROM QuoteLineItem "
                             f"WHERE QuoteId = {soql_str(quote_id)} ORDER BY LineNumber")
    lines = []
    line_ids = []
    for idx, r in enumerate(qli_rows):   # qli_rows is ORDER BY LineNumber
        line_ids.append(r["Id"])
        rec = clean_record(org, r)
        rec["_lineOrdinal"] = idx        # stable position, disambiguates repeated SKUs
        lines.append(rec)

    # Map source QLI id -> (SKU, ordinal) so child records carry a UNIQUE portable
    # line key. SKU alone is ambiguous when a quote repeats a product -- the ordinal
    # (position in LineNumber order) disambiguates. The raw QuoteLineItemId is
    # org-specific; the replay resolves the target QLI by ordinal on the placed quote
    # (placement order == this order), falling back to SKU when it is unique.
    qli_line = {}
    for idx, ln in enumerate(lines):
        sku = (ln.get("_keys") or {}).get("Product2Key")
        if ln.get("_sourceId"):
            qli_line[ln["_sourceId"]] = (sku, idx)

    # Child records that carry manual input (configured attrs, manual adjustments,
    # line-level pricing detail). Queried per child object, grouped by line.
    children = {}
    for child_obj, rel in (
        ("QuoteLineItemAttribute", "QuoteLineItemId"),
        ("QuoteLinePriceAdjustment", "QuoteLineItemId"),
        ("QuoteLineDetail", "QuoteLineItemId"),
    ):
        try:
            fields = queryable_fields(org, child_obj)
        except UnknownObjectError:
            continue  # object genuinely absent in this org (other failures propagate)
        if not line_ids:
            break
        id_list = ", ".join(soql_str(i) for i in line_ids)
        crows = sf_query(org, f"SELECT {', '.join(fields)} FROM {child_obj} "
                              f"WHERE {rel} IN ({id_list})")
        if crows:
            cleaned = []
            for c in crows:
                rec = clean_record(org, c)
                parent = qli_line.get(c.get(rel))
                if parent:
                    keys = rec.setdefault("_keys", OrderedDict())
                    if parent[0]:
                        keys["QuoteLineItemSku"] = parent[0]
                    keys["QuoteLineOrdinal"] = parent[1]
                cleaned.append(rec)
            children[child_obj] = cleaned

    return {
        "name": quote_name,
        "quote": quote,
        "lineItems": lines,
        "childRecords": children,
        "rampSummary": _ramp_summary(lines),
    }


def extract_anchors(org, quotes, seed_opps=(), seed_accounts=()):
    """Capture the distinct Account/Contact/Opportunity records the quotes hang
    off, plus any named seeded scenario Opportunities/Accounts the quotes do not
    reference. Unlike quote line items these are plain DML records -- the insert
    side upserts them directly (by Name) before replaying the quotes.
    """
    acct_ids, contact_ids, opp_ids = OrderedDict(), OrderedDict(), OrderedDict()
    for q in quotes:
        qr = q["quote"]
        for fld, bucket in (("QuoteAccountId", acct_ids), ("AccountId", acct_ids),
                            ("ContactId", contact_ids), ("OpportunityId", opp_ids)):
            if qr.get(fld):
                bucket[qr[fld]] = True

    # Named seeded Opportunities not attached to any captured quote. Pull each in
    # and pull its Account along too, so a fresh clone gets the parent account.
    # A requested seed name is *required* drift: a missing one would write a
    # successful-but-incomplete spec, so collect and fail rather than warn. (Opt
    # out intentionally by passing an empty --seed-opps / --seed-accounts value.)
    # A duplicate name is as fatal as a missing one: picking an unordered/oldest
    # row would silently capture the wrong seed record. Fail on ambiguity, exactly
    # as extract_quote does for quote names, and collect both classes to report at
    # once. (Opt out of a seed entirely with an empty --seed-opps/--seed-accounts.)
    missing = []
    ambiguous = []
    for name in seed_opps:
        rows = sf_query(org, "SELECT Id, AccountId FROM Opportunity "
                             f"WHERE Name = {soql_str(name)}")
        if not rows:
            missing.append(f"opportunity {name!r}")
            continue
        if len(rows) > 1:
            ambiguous.append(f"{len(rows)} opportunities named {name!r}")
            continue
        row = rows[0]
        opp_ids[row["Id"]] = True
        if row.get("AccountId"):
            acct_ids[row["AccountId"]] = True

    # Named seeded Accounts whose opportunity is created live in the exercise.
    for name in seed_accounts:
        rows = sf_query(org, f"SELECT Id FROM Account WHERE Name = {soql_str(name)}")
        if not rows:
            missing.append(f"account {name!r}")
            continue
        if len(rows) > 1:
            ambiguous.append(f"{len(rows)} accounts named {name!r}")
            continue
        acct_ids[rows[0]["Id"]] = True

    if missing:
        raise ExtractError(
            "requested seed record(s) not found in " + repr(org) + ": "
            + ", ".join(missing)
            + " -- fix the name(s), or pass an empty --seed-opps/--seed-accounts to opt out.")
    if ambiguous:
        raise ExtractError(
            "ambiguous seed record(s) in " + repr(org) + ": "
            + ", ".join(ambiguous)
            + " -- rename/remove the duplicates before extracting.")

    def fetch(sobject, ids):
        if not ids:
            return []
        fields = queryable_fields(org, sobject)
        id_list = ", ".join(soql_str(i) for i in ids)
        rows = sf_query(org, f"SELECT {', '.join(fields)} FROM {sobject} "
                             f"WHERE Id IN ({id_list})")
        return [clean_record(org, r) for r in rows]

    return {
        "accounts": fetch("Account", list(acct_ids)),
        "contacts": fetch("Contact", list(contact_ids)),
        "opportunities": fetch("Opportunity", list(opp_ids)),
    }


def _ramp_summary(lines):
    """Group lines by RampIdentifier so ramps are legible in the output."""
    ramps = {}
    for ln in lines:
        rid = ln.get("RampIdentifier")
        if not rid:
            continue
        ramps.setdefault(rid, []).append({
            "segment": ln.get("SegmentName"),
            "isPrimary": ln.get("IsPrimarySegment"),
            "quantity": ln.get("Quantity"),
            "startDate": ln.get("StartDate"),
            "endDate": ln.get("EndDate"),
            "sku": (ln.get("_keys") or {}).get("Product2Key"),
        })
    return ramps


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--org", default="df26-ws",
                    help="source org alias (sf CLI / cci mapped) [default: df26-ws]")
    ap.add_argument("--quotes", default=",".join(DEFAULT_QUOTES),
                    help="comma-separated quote Names to extract")
    ap.add_argument("--seed-opps", default=",".join(DEFAULT_SEED_OPPS),
                    help="comma-separated Opportunity Names to capture even if no "
                         "quote references them (empty string to disable)")
    ap.add_argument("--seed-accounts", default=",".join(DEFAULT_SEED_ACCOUNTS),
                    help="comma-separated Account Names to capture even if no "
                         "opportunity references them (empty string to disable)")
    ap.add_argument("--out", default="datasets/df_workshop/workshop_quotes.json",
                    help="output JSON path")
    args = ap.parse_args()

    quote_names = [q.strip() for q in args.quotes.split(",") if q.strip()]
    seed_opps = [s.strip() for s in args.seed_opps.split(",") if s.strip()]
    seed_accounts = [s.strip() for s in args.seed_accounts.split(",") if s.strip()]
    print(f"Extracting {len(quote_names)} quote(s) from org {args.org!r}")

    quotes = []
    for name in quote_names:
        print(f"  - {name}")
        quotes.append(extract_quote(args.org, name))

    print("  - anchors (accounts / contacts / opportunities)")
    anchors = extract_anchors(args.org, quotes, seed_opps, seed_accounts)

    spec = {
        "sourceOrg": args.org,
        "apiVersion": API,
        "anchors": anchors,
        "quotes": quotes,
    }
    out_dir = os.path.dirname(args.out)
    if out_dir:  # empty when --out is a bare filename; os.makedirs("") would raise
        os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(spec, fh, indent=2)
        fh.write("\n")

    n_lines = sum(len(q["lineItems"]) for q in quotes)
    n_ramps = sum(len(q["rampSummary"]) for q in quotes)
    print(f"\nWrote {args.out}: {len(quotes)} quotes, {n_lines} line items, "
          f"{n_ramps} ramp(s); anchors: {len(anchors['accounts'])} account(s), "
          f"{len(anchors['contacts'])} contact(s), "
          f"{len(anchors['opportunities'])} opportunity(ies)")


if __name__ == "__main__":
    try:
        main()
    except ExtractError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
