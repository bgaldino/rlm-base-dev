#!/usr/bin/env python3
"""Catalog resolution + quote read-back for the ramp-deals toolkit.

Two jobs, both thin over a :class:`_client.Transport` (or any object exposing
``soql``), so both are unit-testable against a fake transport with no org:

  * **resolve** — turn human-friendly names into the ids ``_payload`` needs:
    Account, Pricebook2, Product2 (→ SKU), and the PricebookEntry that ties a
    product to a pricebook. A ramp ``place`` body cannot be built from names; the
    Connect graph wants ids.
  * **read back** — after a ``place`` / ``clone`` settles, load the quote + its
    groups + lines into the plain dict shape ``_verify.verify_quote`` expects
    ({Id, TotalPrice, TotalPriceOverride, groups:[{…, lines:[…]}]}). The read-back
    is the single normalization point so authoring and verification agree on shape.

No payload logic here (that is ``_payload``); no assertions (that is ``_verify``).
Resolution and read-back only.
"""

from typing import Any, Dict, List, Optional

from . import _client


class ResolveError(RuntimeError):
    """Raised when a name cannot be resolved to exactly one record in the org."""


def _one(rows: List[Dict[str, Any]], *, what: str, needle: str) -> Dict[str, Any]:
    if not rows:
        raise ResolveError(f"{what} {needle!r} not found in org.")
    if len(rows) > 1:
        ids = ", ".join(r.get("Id", "?") for r in rows[:5])
        raise ResolveError(
            f"{what} {needle!r} is ambiguous — {len(rows)} matches ({ids}…). "
            "Pass an explicit Id instead of a name."
        )
    return rows[0]


def resolve_account_id(name: str, *, transport) -> str:
    """Resolve an Account Id from its Name (exact match, must be unique)."""
    safe = _client.soql_literal(name)
    rows = transport.soql(f"SELECT Id FROM Account WHERE Name = '{safe}'")
    return _one(rows, what="Account", needle=name)["Id"]


def resolve_pricebook_id(name: str, *, transport) -> str:
    """Resolve a Pricebook2 Id from its Name (exact match, must be unique)."""
    safe = _client.soql_literal(name)
    rows = transport.soql(f"SELECT Id FROM Pricebook2 WHERE Name = '{safe}'")
    return _one(rows, what="Pricebook2", needle=name)["Id"]


def resolve_standard_pricebook_id(*, transport) -> str:
    """Resolve the org's standard Pricebook2 Id (``IsStandard = true``)."""
    rows = transport.soql("SELECT Id FROM Pricebook2 WHERE IsStandard = true")
    return _one(rows, what="Standard Pricebook2", needle="IsStandard=true")["Id"]


def resolve_product_id(sku: str, *, transport) -> str:
    """Resolve a Product2 Id from its StockKeepingUnit (SKU), else its Name."""
    safe = _client.soql_literal(sku)
    rows = transport.soql(
        f"SELECT Id FROM Product2 WHERE StockKeepingUnit = '{safe}'"
    )
    if not rows:
        rows = transport.soql(f"SELECT Id FROM Product2 WHERE Name = '{safe}'")
    return _one(rows, what="Product2", needle=sku)["Id"]


def resolve_pricebook_entry(
    *, product_id: str, pricebook_id: str, transport
) -> Dict[str, Any]:
    """Resolve the PricebookEntry (Id + UnitPrice) for a product in a pricebook.

    Returns ``{"Id": ..., "UnitPrice": ...}``. Only active entries are considered
    — an inactive PBE cannot be sold on a quote line.
    """
    rows = transport.soql(
        "SELECT Id, UnitPrice FROM PricebookEntry "
        f"WHERE Product2Id = '{_client.soql_literal(product_id)}' "
        f"AND Pricebook2Id = '{_client.soql_literal(pricebook_id)}' "
        "AND IsActive = true"
    )
    rec = _one(rows, what="PricebookEntry",
               needle=f"Product2Id={product_id}, Pricebook2Id={pricebook_id}")
    return {"Id": rec["Id"], "UnitPrice": rec.get("UnitPrice")}


def resolve_line_ids(
    line: Dict[str, Any], *, pricebook_id: str, transport
) -> Dict[str, Any]:
    """Resolve one caller-friendly line spec into writable QuoteLineItem fields.

    Accepts a line dict that may carry ``sku`` / ``product`` (a name-or-SKU) and/or
    ``Product2Id`` and/or ``PricebookEntryId``. Fills in ``Product2Id``,
    ``PricebookEntryId`` and (when absent) ``UnitPrice`` from the resolved PBE,
    leaving all other keys (Quantity, StartDate, EndDate, …) untouched. The
    ``sku`` / ``product`` helper keys are stripped from the returned dict so they
    do not leak into the ``place`` body.
    """
    out = {k: v for k, v in line.items() if k not in ("sku", "product")}

    product_id = out.get("Product2Id")
    if not product_id:
        needle = line.get("sku") or line.get("product")
        if not needle:
            raise ResolveError(
                "line has no Product2Id and no 'sku'/'product' to resolve one from"
            )
        product_id = resolve_product_id(needle, transport=transport)
        out["Product2Id"] = product_id

    if not out.get("PricebookEntryId"):
        pbe = resolve_pricebook_entry(
            product_id=product_id, pricebook_id=pricebook_id, transport=transport
        )
        out["PricebookEntryId"] = pbe["Id"]
        out.setdefault("UnitPrice", pbe["UnitPrice"])

    return out


# --- read-back ------------------------------------------------------------- #

def read_quote(quote_id: str, *, transport) -> Dict[str, Any]:
    """Load a quote + its ramped groups + lines into the ``_verify`` dict shape.

    Returns:
        {"Id", "TotalPrice", "TotalPriceOverride",
         "groups": [{"Id","IsRamped","SegmentType","SortOrder","StartDate",
                     "EndDate","lines":[{"Id","Product2Id","RampIdentifier",
                     "SegmentIdentifier","TotalPrice"}, …]}, …]}

    Two queries (quote+groups, then all lines), stitched client-side by
    QuoteLineGroupId — cheaper and clearer than a correlated subquery, and keeps
    the shape identical to what the offline tests build by hand.
    """
    safe = _client.soql_literal(quote_id)
    quote_rows = transport.soql(
        "SELECT Id, TotalPrice, TotalPriceOverride, "
        "(SELECT Id, IsRamped, SegmentType, SortOrder, StartDate, EndDate "
        " FROM QuoteLineGroups ORDER BY SortOrder) "
        f"FROM Quote WHERE Id = '{safe}'"
    )
    if not quote_rows:
        raise ResolveError(f"Quote {quote_id} not found in org.")
    q = quote_rows[0]

    line_rows = transport.soql(
        "SELECT Id, Product2Id, QuoteLineGroupId, RampIdentifier, "
        "SegmentIdentifier, TotalPrice "
        f"FROM QuoteLineItem WHERE QuoteId = '{safe}'"
    )
    lines_by_group: Dict[str, List[Dict[str, Any]]] = {}
    for ln in line_rows:
        lines_by_group.setdefault(ln.get("QuoteLineGroupId"), []).append({
            "Id": ln.get("Id"),
            "Product2Id": ln.get("Product2Id"),
            "RampIdentifier": ln.get("RampIdentifier"),
            "SegmentIdentifier": ln.get("SegmentIdentifier"),
            "TotalPrice": ln.get("TotalPrice"),
        })

    groups = []
    group_wrapper = q.get("QuoteLineGroups") or {}
    for g in (group_wrapper.get("records") or []):
        groups.append({
            "Id": g.get("Id"),
            "IsRamped": g.get("IsRamped"),
            "SegmentType": g.get("SegmentType"),
            "SortOrder": g.get("SortOrder"),
            "StartDate": g.get("StartDate"),
            "EndDate": g.get("EndDate"),
            "lines": lines_by_group.get(g.get("Id"), []),
        })

    return {
        "Id": q.get("Id"),
        "TotalPrice": q.get("TotalPrice"),
        "TotalPriceOverride": q.get("TotalPriceOverride"),
        "groups": groups,
    }
