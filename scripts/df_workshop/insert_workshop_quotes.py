#!/usr/bin/env python3
"""Replay the DF workshop quotes into a clone from the portable spec.

Consumes ``datasets/df_workshop/workshop_quotes.json`` (produced by
``extract_workshop_quotes.py``) and reconstructs the quotes in a target org:

  1. Upsert the anchor Account / Contact / Opportunity records (by natural key).
  2. Resolve every product SKU + selling model to the clone's own
     Product2 / PricebookEntry ids.
  3. Re-create each quote through Place Sales Transaction
     (``POST /connect/rev/sales-transaction/actions/place``) so the platform
     generates + prices the line items, attributes and ramp segments. Direct
     QuoteLineItem DML is not viable (see extract_workshop_quotes.py).
  4. (--apply-config) Apply the bucket-B setup toggles: assign the Agentforce
     Coworker Admin perm set to the running user, and flag an active DISTI pricing
     procedure. Fails loudly if a toggle cannot be established (perm set absent, or
     an active DISTI version present) rather than certifying a partial setup.

A ramp is not a special object: it is N line records for one product sharing a
RampIdentifier, each a dated segment. We never copy the source org's opaque
RampIdentifier/SegmentIdentifier tokens: we place only the primary (Year-1)
segment, call Create Ramp Deal so the PLATFORM mints the identifiers and
generates the yearly segments, then place-with-context to reprice the later
segments to their captured quantity + discount.

Idempotency: anchors upsert by name. Quotes are matched by Name -- an existing
quote of the same name is skipped unless --replace is passed (which deletes it
first). Config toggles are no-ops when already in the desired state.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

API = "v68.0"
DEFAULT_SPEC = "datasets/df_workshop/workshop_quotes.json"
COWORKER_ADMIN_PSET = "AISearchAdmin"          # label: Agentforce Coworker Admin
DISTI_PRICING_APINAME = "RLM_PRM_DISTI_Pricing_Procedure"


class InsertError(RuntimeError):
    pass


# ----------------------------------------------------------------------
# sf CLI plumbing (auth delegated to the CLI)
# ----------------------------------------------------------------------
def _run(args, timeout=300):
    env = {**os.environ, "SF_TEMP_SHOW_SECRETS": "true"}
    p = subprocess.run(args, capture_output=True, text=True, env=env, timeout=timeout)
    return p.returncode, p.stdout, p.stderr


def soql_str(value):
    return "'" + str(value).replace("\\", "\\\\").replace("'", "\\'") + "'"


def sf_query(org, soql):
    rc, out, err = _run(["sf", "data", "query", "-q", soql, "--target-org", org, "--json"])
    try:
        d = json.loads(out)
    except json.JSONDecodeError:
        raise InsertError(f"query failed: {(err or out)[:400]}")
    if "result" not in d:
        raise InsertError(f"query failed: {d.get('message', out)[:400]}")
    return d["result"]["records"]


def sf_query_one(org, soql):
    rows = sf_query(org, soql)
    return rows[0] if rows else None


def sf_rest(org, path, method="GET", body=None):
    args = ["sf", "api", "request", "rest", path, "--target-org", org, "--method", method]
    if body is not None:
        args += ["--body", json.dumps(body)]
    rc, out, err = _run(args)
    text = out.strip() or err.strip()
    # `sf api request rest` exits nonzero on an HTTP error (4xx/5xx) or CLI failure
    # while still printing a parseable error body. Returning that body would let a
    # failed call (e.g. the ramp place-with-context reprice) pass through _place,
    # after which _report finds the step-1 quote and the command "succeeds" with
    # unrepriced segments. Gate on rc before any caller inspects the body.
    if rc != 0:
        raise InsertError(f"{method} {path} failed (exit {rc}): {text[:400]}")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise InsertError(f"{method} {path} -> unparseable response: {text[:400]}")


def sf_dml_insert(org, sobject, fields):
    """Insert one record via the CLI; return its Id."""
    pairs = " ".join(f"{k}={_cli_val(v)}" for k, v in fields.items())
    rc, out, err = _run(["sf", "data", "create", "record", "--sobject", sobject,
                         "--values", pairs, "--target-org", org, "--json"])
    # `sf ... --json` emits parseable JSON even on failure, so the parse alone is
    # not proof of success -- gate on the exit code / status too.
    try:
        d = json.loads(out)
    except json.JSONDecodeError:
        raise InsertError(f"insert {sobject} failed: {(err or out)[:400]}")
    if rc != 0 or d.get("status", 0) != 0:
        raise InsertError(f"insert {sobject} failed: {d.get('message', (err or out))[:400]}")
    try:
        return d["result"]["id"]
    except KeyError:
        raise InsertError(f"insert {sobject} failed: {(err or out)[:400]}")


def _cli_val(v):
    s = str(v)
    return f'"{s}"' if (" " in s or s == "") else s


def sf_dml_update(org, sobject, record_id, fields):
    """Update one record via the CLI (used to heal existing anchors in place)."""
    pairs = " ".join(f"{k}={_cli_val(v)}" for k, v in fields.items())
    rc, out, err = _run(["sf", "data", "update", "record", "--sobject", sobject,
                         "--record-id", record_id, "--values", pairs,
                         "--target-org", org, "--json"])
    # `sf ... --json` emits parseable JSON even on failure; a failed heal must not
    # be logged as success, so gate on the exit code / status, not just the parse.
    try:
        d = json.loads(out)
    except json.JSONDecodeError:
        raise InsertError(f"update {sobject} failed: {(err or out)[:400]}")
    if rc != 0 or d.get("status", 0) != 0:
        raise InsertError(f"update {sobject} failed: {d.get('message', (err or out))[:400]}")


# ----------------------------------------------------------------------
# Foundation resolution (clone's own ids)
# ----------------------------------------------------------------------
_PBE_CACHE: dict[tuple, dict] = {}


def resolve_pbe(org, sku, pricebook, currency, selling_model):
    """Resolve a product SKU + selling model to THIS org's PricebookEntry.

    Products carry one PBE per selling model, so the model name disambiguates a
    OneTime line from a TermDefined line on the same SKU.
    """
    key = (sku, pricebook, currency, selling_model)
    if key in _PBE_CACHE:
        return _PBE_CACHE[key]
    where = [f"Product2.StockKeepingUnit = {soql_str(sku)}",
             f"Pricebook2.Name = {soql_str(pricebook)}",
             "IsActive = true"]
    if currency:
        where.append(f"CurrencyIsoCode = {soql_str(currency)}")
    if selling_model:
        where.append(f"ProductSellingModel.Name = {soql_str(selling_model)}")
    row = sf_query_one(org, "SELECT Id, UnitPrice, Product2Id FROM PricebookEntry "
                            f"WHERE {' AND '.join(where)} LIMIT 1")
    if not row:
        raise InsertError(f"no PricebookEntry for SKU={sku!r} model={selling_model!r} "
                          f"in {pricebook!r}/{currency} -- is the QB foundation loaded?")
    val = {"pbeId": row["Id"], "productId": row["Product2Id"],
           "unitPrice": row["UnitPrice"]}
    _PBE_CACHE[key] = val
    return val


def resolve_pricebook(org, name):
    row = sf_query_one(org, f"SELECT Id FROM Pricebook2 WHERE Name = {soql_str(name)} "
                            "AND IsActive = true LIMIT 1")
    if not row:
        raise InsertError(f"pricebook not found: {name!r}")
    return row["Id"]


# ----------------------------------------------------------------------
# Anchors
# ----------------------------------------------------------------------
def upsert_anchors(org, anchors, dry_run=False):
    """Upsert Account/Contact/Opportunity by name; return {name: id} maps."""
    acct_ids, contact_ids, opp_ids = {}, {}, {}

    for a in anchors.get("accounts", []):
        name = a["Name"]
        existing = sf_query_one(org, f"SELECT Id FROM Account WHERE Name = {soql_str(name)} LIMIT 1")
        if existing:
            acct_ids[name] = existing["Id"]
            print(f"    account exists: {name}")
        elif dry_run:
            # Record a placeholder so downstream quote-payload construction can be
            # previewed on a fresh clone (where the anchor does not yet exist)
            # instead of raising "unresolved account".
            acct_ids[name] = "[dry-new-account]"
            print(f"    [dry] insert account: {name}")
        else:
            fields = {"Name": name}
            for f in ("Type", "Industry", "CurrencyIsoCode"):
                if a.get(f):
                    fields[f] = a[f]
            acct_ids[name] = sf_dml_insert(org, "Account", fields)
            print(f"    account created: {name}")

    for c in anchors.get("contacts", []):
        name = c["Name"]
        acct_name = (c.get("_keys") or {}).get("AccountKey")
        # Reproduce the source fields verbatim -- do NOT split Name. The source may
        # store a full display name in LastName with an empty FirstName (Contact.Name
        # is a formula); splitting it corrupts LastName and breaks the Name existence
        # check, inserting a duplicate on every run.
        existing = sf_query_one(org, f"SELECT Id FROM Contact WHERE Name = {soql_str(name)} LIMIT 1")
        if existing:
            contact_ids[name] = existing["Id"]
            print(f"    contact exists: {name}")
        elif dry_run:
            contact_ids[name] = "[dry-new-contact]"
            print(f"    [dry] insert contact: {name}")
        else:
            fields = {"LastName": c.get("LastName") or name.rsplit(" ", 1)[-1]}
            for f in ("FirstName", "Email", "HomePhone", "Phone", "MobilePhone",
                      "Title", "CurrencyIsoCode"):
                if c.get(f):
                    fields[f] = c[f]
            if acct_name and acct_name in acct_ids:
                fields["AccountId"] = acct_ids[acct_name]
            contact_ids[name] = sf_dml_insert(org, "Contact", fields)
            print(f"    contact created: {name}")

    for o in anchors.get("opportunities", []):
        name = o["Name"]
        keys = o.get("_keys") or {}
        acct_name = keys.get("AccountKey")
        # Resolve the source pricebook name to THIS org's Pricebook2 id. Opps
        # carry a Pricebook2 lookup; without it the quoting/Coworker flows have no
        # pricebook context, so a workshop-ready clone cannot be certified with the
        # anchor missing it. Fail here rather than silently produce unusable anchors
        # (consistent with the quote header, which hard-fails on the same lookup).
        pb_id = None
        pb_name = keys.get("Pricebook2Key")
        if pb_name:
            pb_row = sf_query_one(org, f"SELECT Id FROM Pricebook2 WHERE Name = {soql_str(pb_name)} "
                                       "AND IsActive = true LIMIT 1")
            if not pb_row:
                raise InsertError(f"pricebook {pb_name!r} not found (active) for opportunity "
                                  f"{name!r} -- is the QB foundation loaded in {org!r}?")
            pb_id = pb_row["Id"]

        existing = sf_query_one(org, "SELECT Id, Pricebook2Id, Amount FROM Opportunity "
                                     f"WHERE Name = {soql_str(name)} ORDER BY CreatedDate LIMIT 1")
        if existing:
            opp_ids[name] = existing["Id"]
            # Heal an existing opp in place (these opps may already carry quotes,
            # so we never delete/recreate): restore a missing pricebook lookup and
            # a missing/stale scenario Amount, so preexisting Starter/Target records
            # still land on the source economics.
            heal = {}
            if pb_id and not existing.get("Pricebook2Id"):
                heal["Pricebook2Id"] = pb_id
            spec_amount = o.get("Amount")
            if spec_amount is not None and existing.get("Amount") != spec_amount:
                heal["Amount"] = spec_amount
            if heal:
                detail = ", ".join(sorted(heal))
                if dry_run:
                    print(f"    [dry] heal existing opportunity {name}: {detail}")
                else:
                    sf_dml_update(org, "Opportunity", existing["Id"], heal)
                    print(f"    opportunity healed: {name} ({detail})")
            else:
                print(f"    opportunity exists: {name}")
        elif dry_run:
            opp_ids[name] = "[dry-new-opp]"
            print(f"    [dry] insert opportunity: {name}")
        else:
            fields = {"Name": name,
                      "StageName": o.get("StageName") or "Proposal/Quote",
                      "CloseDate": o.get("CloseDate") or "2026-12-31"}
            # Carry scenario-meaningful values verbatim. Amount is directly
            # writable on these opps (no OpportunityLineItems, so it is not a
            # rollup); the exercise economics depend on it (Target = $129K).
            for f in ("Amount", "Description", "CurrencyIsoCode", "Type", "LeadSource"):
                if o.get(f) is not None:
                    fields[f] = o[f]
            if acct_name and acct_name in acct_ids:
                fields["AccountId"] = acct_ids[acct_name]
            if pb_id:
                fields["Pricebook2Id"] = pb_id
            opp_ids[name] = sf_dml_insert(org, "Opportunity", fields)
            print(f"    opportunity created: {name}")

    return acct_ids, contact_ids, opp_ids


# ----------------------------------------------------------------------
# Quote replay via Place Sales Transaction
# ----------------------------------------------------------------------
PLACE_PATH = f"/services/data/{API}/connect/rev/sales-transaction/actions/place"
# Line-ramp primitive: build the ramp deal off the primary line so the PLATFORM
# mints the RampIdentifier + per-segment SegmentIdentifiers. We never copy the
# source org's opaque tokens. See the 264 dev guide, "Create Ramp Deal (POST)".
RAMP_CREATE_PATH = (f"/services/data/{API}/connect/revenue-management/"
                    "sales-transaction-contexts/{lineId}/actions/ramp-deal-create")


def _quote_header(org, quote_spec, acct_ids, opp_ids, contact_ids):
    """Shared Quote-header record + resolved (pricebook_name, currency)."""
    q = quote_spec["quote"]
    keys = q.get("_keys", {})
    acct_name = keys.get("QuoteAccountKey") or keys.get("AccountKey")
    pricebook_name = keys.get("Pricebook2Key") or "Standard Price Book"
    currency = q.get("CurrencyIsoCode") or "USD"
    account_id = acct_ids.get(acct_name)
    if not account_id:
        raise InsertError(f"unresolved account {acct_name!r} for quote {quote_spec['name']!r}")
    rec = {
        "attributes": {"type": "Quote", "method": "POST"},
        "Name": quote_spec["name"],
        "QuoteAccountId": account_id,
        "Pricebook2Id": resolve_pricebook(org, pricebook_name),
        "CurrencyIsoCode": currency,
        "Status": "Draft",
    }
    if keys.get("OpportunityKey") and opp_ids.get(keys["OpportunityKey"]):
        rec["OpportunityId"] = opp_ids[keys["OpportunityKey"]]
    if keys.get("ContactKey") and contact_ids.get(keys["ContactKey"]):
        rec["ContactId"] = contact_ids[keys["ContactKey"]]
    return rec, pricebook_name, currency


def _line_record(org, ln, pricebook_name, currency, ref):
    """Build a QuoteLineItem POST record from a spec line (no ramp identity)."""
    lk = ln.get("_keys", {})
    pbe = resolve_pbe(org, lk.get("Product2Key"), pricebook_name, currency,
                      lk.get("ProductSellingModelKey"))
    rec = {
        "attributes": {"type": "QuoteLineItem", "method": "POST"},
        "QuoteId": "@{refQuote.id}",
        "Product2Id": pbe["productId"],
        "PricebookEntryId": pbe["pbeId"],
        "Quantity": ln["Quantity"],
        "UnitPrice": ln.get("UnitPrice", pbe["unitPrice"]),
    }
    sm = ln.get("SellingModelType")
    if ln.get("StartDate"):
        rec["StartDate"] = ln["StartDate"]
    if ln.get("EndDate") and sm != "OneTime":
        rec["EndDate"] = ln["EndDate"]
    if sm and sm != "OneTime":
        for f in ("BillingFrequency", "PeriodBoundary", "SubscriptionTerm"):
            if ln.get(f) is not None:
                rec[f] = ln[f]
    if ln.get("Discount"):
        rec["Discount"] = ln["Discount"]
    return {"referenceId": ref, "record": rec}


def _place(org, payload):
    resp = sf_rest(org, PLACE_PATH, "POST", payload)
    if isinstance(resp, list) and resp and "errorCode" in resp[0]:
        raise InsertError(f"place: {resp[0].get('message', resp[0])}")
    if isinstance(resp, dict):
        errors = resp.get("errorResponse") or []
        if errors or resp.get("isSuccess") is False:
            detail = "; ".join(f"{e.get('referenceId','?')}: {e.get('message', e)}"
                               for e in errors) or json.dumps(resp)[:400]
            raise InsertError(f"place failed: {detail}")
    return resp


def _place_envelope(records, graph_id, context_id=None):
    env = {"pricingPref": "System", "taxPref": "Skip",
           "graph": {"graphId": graph_id, "records": records}}
    if context_id:
        env["contextDetails"] = {"contextId": context_id}
    else:
        env["configurationPref"] = {"configurationMethod": "Skip"}
    return env


def _is_ramp(quote_spec):
    return any(ln.get("RampIdentifier") for ln in quote_spec["lineItems"])


# -- non-ramp: all lines in one place call --------------------------------------
def replay_simple_quote(org, quote_spec, header, pricebook_name, currency, dry_run):
    records = [{"referenceId": "refQuote", "record": header}]
    for i, ln in enumerate(quote_spec["lineItems"]):
        records.append(_line_record(org, ln, pricebook_name, currency, f"refLine{i}"))
    payload = _place_envelope(records, "dfWorkshopReplay")
    if dry_run:
        n_attr = len((quote_spec.get("childRecords") or {}).get("QuoteLineItemAttribute", []))
        print(f"    [dry] would place {quote_spec['name']} ({len(records)-1} lines"
              f"{f', {n_attr} configured attribute(s)' if n_attr else ''})")
        print(json.dumps(payload, indent=2))
        return None
    _place(org, payload)
    qid = _report(org, quote_spec["name"])
    replay_attributes(org, qid, quote_spec)
    return qid


# -- configured-product attributes (QuoteLineItemAttribute) ---------------------
_ATTR_DEF_CACHE: dict[str, dict] = {}
_PICK_CACHE: dict[tuple, str] = {}


def _attr_def(org, name):
    if name not in _ATTR_DEF_CACHE:
        row = sf_query_one(org, "SELECT Id, PicklistId FROM AttributeDefinition "
                                f"WHERE Name = {soql_str(name)} LIMIT 1")
        _ATTR_DEF_CACHE[name] = row or {}
    return _ATTR_DEF_CACHE[name]


def _pick_value(org, picklist_id, value):
    key = (picklist_id, value)
    if key not in _PICK_CACHE:
        row = sf_query_one(org, "SELECT Id FROM AttributePicklistValue "
                                f"WHERE PicklistId = {soql_str(picklist_id)} "
                                f"AND Value = {soql_str(value)} LIMIT 1")
        _PICK_CACHE[key] = row["Id"] if row else None
    return _PICK_CACHE[key]


def replay_attributes(org, quote_id, quote_spec):
    """Re-create the configured-product QuoteLineItemAttribute records.

    Each source attribute maps to its line by product SKU (`_keys.QuoteLineItemSku`);
    the AttributeDefinition resolves by name and, for picklist attributes, the
    AttributePicklistValue by (picklist, value). Idempotent: skips an attribute that
    already exists on the target line for that definition.
    """
    attrs = (quote_spec.get("childRecords") or {}).get("QuoteLineItemAttribute", [])
    if not attrs:
        return
    # Target QLIs on the placed quote, ordered by LineNumber. A simple quote's lines
    # are placed in spec order (== source LineNumber order), so the i-th target line
    # matches source line ordinal i -- this disambiguates a quote that repeats a SKU,
    # where a SKU->line map would collapse every occurrence onto the last line.
    rows = sf_query(org, "SELECT Id, Product2.StockKeepingUnit FROM QuoteLineItem "
                         f"WHERE QuoteId = {soql_str(quote_id)} ORDER BY LineNumber")
    qli_by_ordinal = {i: r["Id"] for i, r in enumerate(rows)}
    qli_by_sku, sku_counts = {}, {}
    for r in rows:
        sku = (r.get("Product2") or {}).get("StockKeepingUnit")
        sku_counts[sku] = sku_counts.get(sku, 0) + 1
        qli_by_sku[sku] = r["Id"]          # fallback for pre-ordinal specs
    made = 0
    # Configured attributes are part of the required workshop state (e.g. Quote
    # PDF's six). Silently skipping an unresolvable one would let an incomplete
    # quote be templated as success -- so accumulate failures and raise after
    # processing the resolvable ones.
    unresolved = []
    for a in attrs:
        name = a.get("AttributeName")
        akeys = a.get("_keys") or {}
        sku = akeys.get("QuoteLineItemSku")
        ordinal = akeys.get("QuoteLineOrdinal")
        qli = qli_by_ordinal.get(ordinal) if ordinal is not None else None
        if qli is None and sku is not None:
            # Older spec without an ordinal: SKU is safe only when unique on the quote.
            if sku_counts.get(sku, 0) > 1:
                unresolved.append(
                    f"{name!r}: sku={sku!r} is on {sku_counts[sku]} lines and the spec "
                    "carries no line ordinal -- re-extract to disambiguate")
                continue
            qli = qli_by_sku.get(sku)
        if not (name and qli):
            unresolved.append(f"{name!r}: no target line for sku={sku!r} ordinal={ordinal!r}")
            continue
        adef = _attr_def(org, name)
        if not adef.get("Id"):
            unresolved.append(f"{name!r}: no AttributeDefinition in target")
            continue
        exists = sf_query_one(org, "SELECT Id FROM QuoteLineItemAttribute WHERE "
                                   f"QuoteLineItemId = {soql_str(qli)} AND "
                                   f"AttributeDefinitionId = {soql_str(adef['Id'])} LIMIT 1")
        if exists:
            continue
        fields = {"QuoteLineItemId": qli, "AttributeDefinitionId": adef["Id"],
                  "AttributeValue": a.get("AttributeValue")}
        # Picklist attributes need the resolved AttributePicklistValueId.
        if a.get("AttributePicklistValueId") and adef.get("PicklistId"):
            pv = _pick_value(org, adef["PicklistId"], a.get("AttributeValue"))
            if pv:
                fields["AttributePicklistValueId"] = pv
        sf_dml_insert(org, "QuoteLineItemAttribute", fields)
        made += 1
    if made:
        print(f"    added {made} configured attribute(s)")
    if unresolved:
        raise InsertError(
            f"{len(unresolved)} configured attribute(s) on quote {quote_spec['name']!r} "
            "could not be restored: " + "; ".join(unresolved)
            + " -- the clone is missing required definitions/lines; do not template it.")


# -- ramp: place primary -> ramp-deal-create -> place(contextId) + reprice ------
def replay_ramp_quote(org, quote_spec, header, pricebook_name, currency, dry_run):
    name = quote_spec["name"]
    segs = sorted(quote_spec["lineItems"], key=lambda l: l.get("StartDate") or "")
    primary = next((s for s in segs if s.get("IsPrimarySegment")), segs[0])
    n = len(segs)

    # 1. place the quote with ONLY the primary segment as a plain line.
    prim_rec = _line_record(org, primary, pricebook_name, currency, "refLine")
    payload = _place_envelope([{"referenceId": "refQuote", "record": header}, prim_rec],
                              "dfWorkshopRampPrimary")
    if dry_run:
        print(f"    [dry] ramp {name}: place primary segment {primary.get('SegmentName')} "
              f"(qty {primary['Quantity']}), then ramp-deal-create YEARLY x{n}, "
              f"then reprice {n-1} later segment(s)")
        print(json.dumps(payload, indent=2))
        return None
    _place(org, payload)

    row = sf_query_one(org, f"SELECT Id FROM Quote WHERE Name = {soql_str(name)} "
                            "ORDER BY CreatedDate DESC LIMIT 1")
    if not row:
        raise InsertError(f"ramp place returned but no quote named {name!r} found")
    qid = row["Id"]
    lrow = sf_query_one(org, f"SELECT Id FROM QuoteLineItem WHERE QuoteId = {soql_str(qid)} LIMIT 1")
    line_id = lrow["Id"]

    # 2. ramp-deal-create: platform generates N yearly segments + mints identifiers.
    #    subscriptionTerm is in MONTHS; YEARLY => term/12 segments.
    rdc = {"transactionId": qid, "transactionLineId": line_id,
           "subscriptionTerm": 12 * n, "subscriptionTermUnit": "MONTHS",
           "segmentType": "YEARLY",
           "executionSettings": {"executePricing": True, "executeConfigRules": False}}
    resp = sf_rest(org, RAMP_CREATE_PATH.format(lineId=line_id), "POST", rdc)
    if not (isinstance(resp, dict) and resp.get("success")):
        detail = (resp.get("errors") if isinstance(resp, dict) else resp) or resp
        raise InsertError(f"ramp-deal-create failed for {name!r}: {json.dumps(detail)[:400]}")
    context_id = resp.get("transactionContextId")
    if not context_id:
        raise InsertError(f"ramp-deal-create returned no transactionContextId for {name!r}")
    seg_ctx = {}
    for st in resp.get("salesTransactionContext", {}).get("SalesTransaction", []):
        for it in st.get("SalesTransactionItem", []):
            if it.get("ItemSegmentName"):
                seg_ctx[it["ItemSegmentName"]] = it["id"]

    # 3. place(contextId): reprice the NON-primary segments to their qty + discount.
    #    Year 1 (primary) already carries its qty/discount from step 1.
    recs = [{"referenceId": "qh",
             "record": {"attributes": {"type": "Quote", "method": "PATCH", "id": qid}}}]
    for s in segs:
        if s is primary or s.get("IsPrimarySegment"):
            continue
        sid = seg_ctx.get(s.get("SegmentName"))
        if not sid:
            raise InsertError(f"no generated segment for {s.get('SegmentName')!r} in {name!r} "
                              f"(got {sorted(seg_ctx)})")
        patch = {"attributes": {"type": "QuoteLineItem", "method": "PATCH", "id": sid},
                 "Quantity": s["Quantity"]}
        if s.get("Discount"):
            patch["Discount"] = s["Discount"]
        recs.append({"referenceId": sid, "record": patch})
    if len(recs) > 1:
        _place(org, _place_envelope(recs, "dfWorkshopRampApply", context_id))
    return _report(org, name)


def _report(org, name):
    row = sf_query_one(org, f"SELECT Id, CalculationStatus, LineItemCount, GrandTotal FROM Quote "
                            f"WHERE Name = {soql_str(name)} ORDER BY CreatedDate DESC LIMIT 1")
    if not row:
        raise InsertError(f"place returned but no quote named {name!r} found")
    print(f"    placed {name}: id={row['Id']} lines={row.get('LineItemCount')} "
          f"calc={row.get('CalculationStatus')} total={row.get('GrandTotal')}")
    return row["Id"]


def _expected_counts(quote_spec):
    """(expected line count, expected configured-attribute count) from the spec."""
    n_lines = len(quote_spec["lineItems"])
    n_attr = len((quote_spec.get("childRecords") or {}).get("QuoteLineItemAttribute", []))
    return n_lines, n_attr


def _assert_complete(org, quote_id, quote_spec):
    """Fail if an existing same-named quote is only partially replayed.

    Name existence is not proof of a complete replay: a failure after the first
    Place call can leave a one-line ramp or a quote missing its attributes, and a
    later normal run would skip it forever and report success. Compare the actual
    line / attribute counts to the spec and direct the operator to --replace.
    """
    name = quote_spec["name"]
    exp_lines, exp_attr = _expected_counts(quote_spec)
    row = sf_query_one(org, "SELECT LineItemCount FROM Quote "
                            f"WHERE Id = {soql_str(quote_id)} LIMIT 1")
    got_lines = (row or {}).get("LineItemCount") or 0
    arow = sf_query_one(org, "SELECT COUNT(Id) c FROM QuoteLineItemAttribute "
                             f"WHERE QuoteLineItem.QuoteId = {soql_str(quote_id)}")
    got_attr = (arow or {}).get("c") or 0
    if got_lines != exp_lines or got_attr != exp_attr:
        raise InsertError(
            f"existing quote {name!r} is incomplete (lines {got_lines}/{exp_lines}, "
            f"attributes {got_attr}/{exp_attr}) -- a prior run likely failed mid-replay. "
            "Re-run with --replace to rebuild it; do not template until it matches.")


def replay_quote(org, quote_spec, acct_ids, opp_ids, contact_ids, dry_run, replace):
    name = quote_spec["name"]
    # Quote names are not unique. Selecting one arbitrary match would let --replace
    # delete only one of several, and certify completeness against the wrong one, so
    # fail on ambiguity before skipping/replacing.
    matches = sf_query(org, f"SELECT Id FROM Quote WHERE Name = {soql_str(name)} ORDER BY CreatedDate")
    if len(matches) > 1:
        raise InsertError(
            f"{len(matches)} quotes named {name!r} in {org!r}; ambiguous -- --replace "
            "would delete only one and completeness cannot be judged. Remove the "
            "duplicate(s) before replaying.")
    existing = matches[0] if matches else None
    if existing:
        if replace and not dry_run:
            rc, out, err = _run(["sf", "data", "delete", "record", "--sobject", "Quote",
                                 "--record-id", existing["Id"], "--target-org", org, "--json"])
            ok = rc == 0
            try:
                ok = ok and json.loads(out).get("status", 0) == 0
            except json.JSONDecodeError:
                ok = False
            if not ok:
                raise InsertError(f"failed to delete existing quote {name!r} for --replace: "
                                  f"{(err or out)[:300]}")
            print(f"    deleted existing quote {name}")
        elif dry_run:
            print(f"    quote exists, skipping (use --replace): {name}")
            return existing["Id"]
        else:
            # Not replacing: only report success if it is actually complete.
            _assert_complete(org, existing["Id"], quote_spec)
            print(f"    quote exists and is complete, skipping (use --replace to rebuild): {name}")
            return existing["Id"]

    header, pricebook_name, currency = _quote_header(org, quote_spec, acct_ids, opp_ids, contact_ids)
    if _is_ramp(quote_spec):
        return replay_ramp_quote(org, quote_spec, header, pricebook_name, currency, dry_run)
    return replay_simple_quote(org, quote_spec, header, pricebook_name, currency, dry_run)


# ----------------------------------------------------------------------
# Bucket B setup toggles
# ----------------------------------------------------------------------
def apply_config(org, dry_run=False):
    # --apply-config asserts the clone should reach bucket-B state. Any toggle it
    # cannot establish is collected and raised at the end, so the command never
    # exits 0 having silently certified a partial setup.
    incomplete = []

    # 1. Assign Agentforce Coworker Admin to the running (org default) user.
    who = _run(["sf", "org", "display", "--target-org", org, "--json"])
    user = None
    try:
        user = json.loads(who[1])["result"]["username"]
    except Exception:
        pass
    ps = sf_query_one(org, f"SELECT Id FROM PermissionSet WHERE Name = {soql_str(COWORKER_ADMIN_PSET)} LIMIT 1")
    if not ps:
        # Cannot establish the required assignment; do not certify partial bucket B.
        incomplete.append(f"perm set {COWORKER_ADMIN_PSET!r} absent (provision it before --apply-config)")
    else:
        urow = sf_query_one(org, f"SELECT Id FROM User WHERE Username = {soql_str(user)} LIMIT 1")
        assigned = sf_query_one(org, "SELECT Id FROM PermissionSetAssignment WHERE "
                                     f"PermissionSetId = {soql_str(ps['Id'])} AND "
                                     f"AssigneeId = {soql_str(urow['Id'])} LIMIT 1")
        if assigned:
            print(f"    perm set already assigned: {COWORKER_ADMIN_PSET}")
        elif dry_run:
            print(f"    [dry] assign perm set {COWORKER_ADMIN_PSET} to {user}")
        else:
            sf_dml_insert(org, "PermissionSetAssignment",
                          {"PermissionSetId": ps["Id"], "AssigneeId": urow["Id"]})
            print(f"    assigned perm set {COWORKER_ADMIN_PSET} to {user}")

    # 2. Deactivate the DISTI pricing procedure. It "breaks orders" only when an
    #    active version applies it globally, so gate on ExpressionSetVersion.IsActive
    #    (IsActive lives on the *version*, not the ExpressionSet). Deactivation is a
    #    guarded, live-verified expression_sets mutation not performed here; if an
    #    active version exists, fail loudly rather than exit 0 leaving it active.
    es = sf_query_one(org, "SELECT Id, Name FROM ExpressionSet WHERE ApiName = "
                           f"{soql_str(DISTI_PRICING_APINAME)} LIMIT 1")
    if not es:
        print(f"    DISTI pricing procedure not present ({DISTI_PRICING_APINAME}) -- nothing to deactivate")
    else:
        active = sf_query_one(org, "SELECT Id, VersionNumber FROM ExpressionSetVersion WHERE "
                                   f"ExpressionSetId = {soql_str(es['Id'])} AND IsActive = true LIMIT 1")
        if not active:
            print(f"    DISTI pricing procedure {es['Name']} present but no active version -- "
                  "nothing applies globally, nothing to deactivate")
        else:
            incomplete.append(
                f"ExpressionSet {es['Name']} ({es['Id']}) has an active version "
                f"(v{active.get('VersionNumber')}) -- deactivate it via scripts/expression_sets/ "
                "(deactivate, don't delete); auto-deactivation is not wired in yet")

    if incomplete:
        raise InsertError("--apply-config could not establish bucket B: "
                          + "; ".join(incomplete))


# ----------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--org", required=True, help="TARGET org alias (the clone)")
    ap.add_argument("--spec", default=DEFAULT_SPEC, help="replay spec JSON")
    ap.add_argument("--quote", action="append",
                    help="only replay this quote name (repeatable)")
    ap.add_argument("--dry-run", action="store_true", help="print actions/payloads, mutate nothing")
    ap.add_argument("--replace", action="store_true", help="delete an existing same-named quote first")
    ap.add_argument("--apply-config", action="store_true", help="also apply bucket-B setup toggles")
    ap.add_argument("--skip-quotes", action="store_true", help="only anchors/config, no quote replay")
    args = ap.parse_args()

    with open(args.spec) as fh:
        spec = json.load(fh)

    print(f"Target org: {args.org}  (spec source: {spec.get('sourceOrg')})")

    print("Anchors:")
    acct_ids, contact_ids, opp_ids = upsert_anchors(args.org, spec.get("anchors", {}), args.dry_run)

    if not args.skip_quotes:
        print("Quotes:")
        spec_names = {q["name"] for q in spec["quotes"]}
        wanted = set(args.quote) if args.quote else None
        if wanted:
            # A misspelled/absent --quote must not silently prepare a clone without the
            # requested quote (the run would still touch anchors and exit 0).
            unknown = sorted(wanted - spec_names)
            if unknown:
                raise InsertError(
                    "requested --quote name(s) not in the spec: "
                    + ", ".join(repr(u) for u in unknown)
                    + f" (spec has: {', '.join(repr(n) for n in sorted(spec_names))})")
        for qspec in spec["quotes"]:
            if wanted and qspec["name"] not in wanted:
                continue
            replay_quote(args.org, qspec, acct_ids, opp_ids, contact_ids,
                         args.dry_run, args.replace)

    if args.apply_config:
        print("Config toggles (bucket B):")
        apply_config(args.org, args.dry_run)


if __name__ == "__main__":
    try:
        main()
    except InsertError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
