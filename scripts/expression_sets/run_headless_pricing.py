#!/usr/bin/env python3
"""Price lines through one pricing procedure with no quote record (read-only).

Wraps ``runSalesforceHeadlessPricing``: builds the ``pricingData`` the action
needs from a small request file, adds the inputs the procedure fails or prices
to zero without, runs it in one request and prints each line's result. Nothing
is saved (``persistContext`` false) and no quote changes. Use it to check a
clone's golden numbers before you activate it, or to compare two procedures.

Inputs the helper fills in when the request does not carry them:

* ``Pricebook`` and ``CurrencyIsoCode`` on the header AND on every line.
  Without them ListPrice is empty and NetUnitPrice is 0.
* ``EndDate`` = ``StartDate`` + term - 1 day for a line with ``SubscriptionTerm``
  and ``SubscriptionTermUnit``. An end date a full year out counts one term too
  many.
* ``SalesTransactionItemSource`` (a per-line string) and ``PeriodBoundary``
  ``Anniversary``; dates as date-times.

Request file (JSON): ``{"header": {...}, "lines": [{...}, ...]}``. Keys are
context attribute names (``Product``, ``PricebookEntry``, ``Quantity``,
``UnitPrice``, ``Discount``, ``SubscriptionTerm``, ``SubscriptionTermUnit``,
``SellingModelType``, ``PricingTermUnit``, ...).

Auth is the ``sf`` CLI (``--target-org`` is the SF alias, never the CCI alias).

    python scripts/expression_sets/run_headless_pricing.py --target-org <sf_alias> \
        --procedure <PricingProcedureApiName> --request lines.json \
        --pricebook <Pricebook2 Id> --currency USD --start-date 2026-11-26
"""

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.expression_sets._client import (  # noqa: E402
    DEFAULT_API_VERSION,
    ExpressionSetClientError,
    Transport,
    eprint,
    soql_literal,
)

CONTEXT_DEFINITION = "RLM_SalesTransactionContext"
MAPPING_TITLE = "quoteentitiesmapping"
RESULT_TAGS = ("ListPrice", "NetUnitPrice", "NetTotalPrice", "PricingTermCount")


def _datetime(value: Any) -> str:
    """A bare date fails proration ('StartDate and EndDate are required')."""
    text = str(value)
    return text if "T" in text else f"{text}T00:00:00.000Z"


def end_date_for_term(start: str, term: int, unit: str) -> Optional[str]:
    """``start`` + term - 1 day, for a term in Annual/Years or Months (else None)."""
    d0 = datetime.fromisoformat(str(start).replace("Z", "")[:10]).date()
    u = (unit or "").lower()
    if u in ("annual", "years", "year"):
        months = 12 * int(term)
    elif u in ("months", "month"):
        months = int(term)
    else:
        return None
    y, m = divmod(d0.month - 1 + months, 12)
    year, month = d0.year + y, m + 1
    day = d0.day
    while True:  # clamp the day to the month length
        try:
            d1 = date(year, month, day)
            break
        except ValueError:
            day -= 1
    return (d1 - timedelta(days=1)).isoformat()


def build_pricing_data(request: Dict[str, Any], *, pricebook: Optional[str],
                       currency: str, start_date: str) -> Dict[str, Any]:
    """The ``pricingData`` object: a root SalesTransaction with a line array."""
    header = dict(request.get("header") or {})
    header.setdefault("CurrencyIsoCode", currency)
    if pricebook:
        header.setdefault("Pricebook", pricebook)
    header["businessObjectType"] = "Quote"
    lines: List[Dict[str, Any]] = []
    for n, raw in enumerate(request.get("lines") or [], start=1):
        line = dict(raw)
        line.setdefault("CurrencyIsoCode", currency)
        if pricebook:
            line.setdefault("Pricebook", pricebook)
        line.setdefault("StartDate", start_date)
        if (not line.get("EndDate") and line.get("SubscriptionTerm")
                and line.get("SubscriptionTermUnit")):
            end = end_date_for_term(line["StartDate"], line["SubscriptionTerm"],
                                    line["SubscriptionTermUnit"])
            if not end:
                raise ExpressionSetClientError(
                    f"Line {n}: cannot derive EndDate for SubscriptionTermUnit "
                    f"{line['SubscriptionTermUnit']!r} (supported: Annual, Years, Months); "
                    "set EndDate on the line explicitly.")
            line["EndDate"] = end
        line["StartDate"] = _datetime(line["StartDate"])
        if line.get("EndDate"):
            line["EndDate"] = _datetime(line["EndDate"])
        line.setdefault("SalesTransactionItemSource", f"HEADLESS_LINE_{n}")
        line.setdefault("PeriodBoundary", "Anniversary")
        line["businessObjectType"] = "QuoteLineItem"
        lines.append(line)
    header["SalesTransactionItem"] = lines
    return {"SalesTransaction": header}


def resolve_context_ids(transport: Transport) -> "tuple[str, str]":
    """The sales transaction context definition id and its QuoteEntitiesMapping id."""
    rows = transport.soql(
        "SELECT Id FROM ContextDefinition WHERE DeveloperName = "
        f"'{soql_literal(CONTEXT_DEFINITION)}'")
    cd = rows[0].get("Id") if rows else None
    if not cd:
        raise ExpressionSetClientError(f"No ContextDefinition {CONTEXT_DEFINITION}.")
    maps = transport.soql(
        "SELECT Id, Title FROM ContextMapping WHERE ContextDefinitionVersion."
        f"ContextDefinitionId = '{soql_literal(cd)}'")
    for m in maps:
        if (m.get("Title") or "").replace(" ", "").replace("_", "").lower() == MAPPING_TITLE:
            return cd, m["Id"]
    raise ExpressionSetClientError(
        "No QuoteEntitiesMapping on the context definition; pass --context-mapping-id.")


def build_action_body(procedure: str, definition_id: str, mapping_id: str,
                      pricing_data: Dict[str, Any]) -> Dict[str, Any]:
    return {"inputs": [{
        "contextDefinitionId": definition_id, "contextMappingId": mapping_id,
        "pricingProcedureId": procedure, "pricingData": json.dumps(pricing_data),
        "skipDiscovery": True, "isSkipWaterfall": True, "persistContext": False,
        "useSessionScopedContext": False, "displayContext": False, "taggedData": False,
    }]}


def _parse(value: Any) -> Any:
    """The response carries these as JSON strings; accept either form."""
    if isinstance(value, str):
        try:
            return json.loads(value)
        except ValueError:
            return value
    return value


def line_results(response: Any) -> List[Dict[str, Any]]:
    """One dict per priced line (payload order): the result tags and dataPath."""
    item = response[0] if isinstance(response, list) and response else {}
    out = item.get("outputValues") or {}
    result = _parse(out.get("pricingResult")) or {}
    rows: Dict[str, Dict[str, Any]] = {}
    for tag in RESULT_TAGS:
        entries = result.get(tag)
        for e in (entries if isinstance(entries, list) else [entries] if entries else []):
            path = e.get("dataPath") if isinstance(e, dict) else None
            if isinstance(path, list):  # live shape: ["CTX_Quote_1", "CTX_QuoteLineItem_2"]
                path = "/".join(str(p) for p in path)
            if path and "QuoteLineItem" in str(path):
                rows.setdefault(path, {})[tag] = e.get("value")
    ordered = sorted(rows.items(), key=lambda kv: int(str(kv[0]).rsplit("_", 1)[-1])
                     if str(kv[0]).rsplit("_", 1)[-1].isdigit() else 0)
    return [dict(v, dataPath=k) for k, v in ordered]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Price lines through one pricing procedure "
                                "headless (read-only; nothing is saved).")
    p.add_argument("--target-org", required=True, help="SF CLI alias/username.")
    p.add_argument("--procedure", required=True, help="Pricing procedure API name.")
    p.add_argument("--request", required=True, help="JSON file: {header, lines}.")
    p.add_argument("--pricebook", help="Pricebook2 Id for the header and every line.")
    p.add_argument("--currency", default="USD", help="CurrencyIsoCode (default USD).")
    p.add_argument("--start-date", default=date.today().isoformat(),
                   help="Default line StartDate (default: today, local date; use the org's date if it differs).")
    p.add_argument("--context-definition-id")
    p.add_argument("--context-mapping-id")
    p.add_argument("--api-version", default=DEFAULT_API_VERSION)
    p.add_argument("--print-request", action="store_true",
                   help="Print the action body and stop (no call).")
    p.add_argument("--json", action="store_true", help="Print the raw response.")
    args = p.parse_args(argv)

    try:
        request = json.loads(Path(args.request).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        eprint(f"Error: could not read the request file: {exc}")
        return 2
    try:
        data = build_pricing_data(request, pricebook=args.pricebook,
                                  currency=args.currency, start_date=args.start_date)
    except ExpressionSetClientError as exc:
        eprint(f"Error: {exc}")
        return 2
    t = Transport(args.target_org, args.api_version)
    try:
        if args.context_definition_id and args.context_mapping_id:
            cd, cm = args.context_definition_id, args.context_mapping_id
        else:
            cd, cm = resolve_context_ids(t)
        body = build_action_body(args.procedure, cd, cm, data)
        if args.print_request:
            print(json.dumps(body, indent=2))
            return 0
        response = t.connect("POST", "actions/standard/runSalesforceHeadlessPricing", body)
    except ExpressionSetClientError as exc:
        eprint(f"FAILED: {exc}")
        return 1
    if args.json:
        print(json.dumps(response, indent=2))
        return 0
    item = response[0] if isinstance(response, list) and response else {}
    errors = _parse((item.get("outputValues") or {}).get("pricingProcessErrors"))
    if errors:
        eprint(f"pricingProcessErrors: {errors}")
    rows = line_results(response)
    if not rows:
        eprint("No line results; rerun with --json to read the response.")
        return 1
    for n, r in enumerate(rows, start=1):
        cells = "  ".join(f"{k}={r.get(k)}" for k in RESULT_TAGS)
        print(f"line {n}: {cells}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
