#!/usr/bin/env python3
"""Capture and compare what users see for a data shape's products (todo 330).

`check_sfdmu_layering.py` compares CSVs, so it cannot see what the configurator shows. Both
#675 regressions were of that kind: a renamed attribute Label, and a category link left blank by a
load that failed partway. This reads the product view from a built org, through PCM's
`/connect/pcm/products/bulk` (what the configurator reads, including the product's flags,
description and unit, attributes, bundle groups and components, ungrouped bundle components and
selling models) plus standard price book entries, and
writes it as org-independent JSON: names, codes and values, never record Ids. Compare a layered
or reloaded org's capture against a single-shape baseline.

  python scripts/sfdmu_product_view.py capture --target-org <sf alias or username> \
      --shape q3 [--sku LP001 --sku OF001] --out q3-view.json
  python scripts/sfdmu_product_view.py compare baseline.json candidate.json

`capture` is read-only. Without --sku it takes every StockKeepingUnit in the shape's
`<shape>-pcm/Product2.csv`: the catalog. Other plans' Product2.csv files are Readonly lookups
(qb's still list two products qb-pcm removed). `compare` exits 1 when any product differs, and lists each difference
by SKU and path. A SKU missing from either side, or held by more than one product, counts as a
difference.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from scripts.decision_tables._client import DecisionTableClientError, Transport, soql_literal  # noqa: E402

SHAPE_PLANS = {"qb": "datasets/sfdmu/qb/en-US/qb-pcm", "q3": "datasets/sfdmu/q3/en-US/q3-pcm"}
BULK_BATCH = 20  # the PCM bulk API rejects more (EPC_PAPI_PROD_DETAILS_008)
SOQL_BATCH = 200


def shape_skus(shape: str, root: Path = REPO) -> List[str]:
    path = root / SHAPE_PLANS[shape] / "Product2.csv"
    with open(path, encoding="utf-8", newline="") as f:
        return sorted({r["StockKeepingUnit"] for r in csv.DictReader(f) if r.get("StockKeepingUnit")})


def _seq(value: Any):
    """Sort key for a platform `sequence` (a string or number; may be missing): numeric first."""
    try:
        return (0, float(value), "")
    except (TypeError, ValueError):
        return (1, 0.0, str(value))


def _attr(a: Dict[str, Any], category: Any) -> Dict[str, Any]:
    picklist = a.get("picklist") or {}
    return {
        "category": category, "code": a.get("code"), "label": a.get("label"), "name": a.get("name"),
        "nameOverride": a.get("attributeNameOverride"), "dataType": a.get("dataType"),
        "displayType": a.get("displayType"), "default": a.get("defaultValue"),
        "required": a.get("isRequired"), "hidden": a.get("isHidden"), "readOnly": a.get("isReadOnly"),
        "priceImpacting": a.get("isPriceImpacting"), "status": a.get("status"),
        "picklist": picklist.get("name"), "sequence": a.get("sequence"), "stepValue": a.get("stepValue"),
        "unit": (a.get("unitOfMeasureInfo") or {}).get("unitCode"),
        "values": [{"code": v.get("code"), "displayValue": v.get("displayValue"), "value": v.get("value"),
                    "status": v.get("status")}
                   for v in sorted(picklist.get("values") or [], key=lambda v: _seq(v.get("sequence")))],
    }


def _attributes(p: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = [_attr(a, {"code": c.get("code"), "name": c.get("name")})
           for c in (p.get("attributeCategory") or []) for a in (c.get("attributes") or [])]
    out += [_attr(a, None) for a in (p.get("attributes") or [])]
    return sorted(out, key=lambda a: (str((a["category"] or {}).get("code")), str(a["code"])))


def _component(c: Dict[str, Any]) -> Dict[str, Any]:
    prc = c.get("productRelatedComponent") or {}
    return {"sku": c.get("productCode") or c.get("name"), "name": c.get("name"),
            "quantity": prc.get("quantity"), "required": prc.get("isComponentRequired"),
            "default": prc.get("isDefaultComponent"), "quantityEditable": prc.get("isQuantityEditable"),
            "scale": prc.get("quantityScaleMethod"), "sequence": prc.get("sequence"),
            "inBundlePrice": prc.get("doesBundlePriceIncludeChild"), "excluded": prc.get("isExcluded"),
            "quoteVisibility": prc.get("quoteVisibility")}


def _components(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted((_component(c) for c in items or []), key=lambda c: (_seq(c["sequence"]), str(c["sku"])))


def _groups(p: Dict[str, Any]) -> List[Dict[str, Any]]:
    def group(g):
        return {"code": g.get("code"), "name": g.get("name"), "sequence": g.get("sequence"),
                "min": g.get("minBundleComponents"), "max": g.get("maxBundleComponents"),
                "components": _components(g.get("components")),
                "childGroups": [group(x) for x in sorted(g.get("childGroups") or [],
                                                           key=lambda x: str(x.get("code")))]}
    return [group(g) for g in sorted(p.get("productComponentGroups") or [], key=lambda g: str(g.get("code")))]


def _models(p: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = [{"name": (o.get("productSellingModel") or {}).get("name"),
            "type": (o.get("productSellingModel") or {}).get("sellingModelType"),
            "default": o.get("isDefault")} for o in p.get("productSellingModelOptions") or []]
    return sorted(out, key=lambda m: str(m["name"]))


def normalize(p: Dict[str, Any], prices: Dict[str, Dict[str, float]], sku: str) -> Dict[str, Any]:
    return {"name": p.get("name"), "description": p.get("description"), "active": p.get("isActive"),
            "nodeType": p.get("nodeType"), "unit": (p.get("unitOfMeasureInfo") or {}).get("unitCode"),
            "configureDuringSale": p.get("configureDuringSale"),
            "assetizable": p.get("isAssetizable"), "soldOnlyWithOthers": p.get("isSoldOnlyWithOtherProds"),
            "attributes": _attributes(p), "componentGroups": _groups(p),
            # Bundle components outside any group (q3's CERT007 -> ASTCERT001, LLMCERT001).
            "childProducts": _components(p.get("childProducts")),
            "sellingModels": _models(p), "listPrices": prices.get(sku, {})}


def capture(t: Transport, skus: List[str]) -> Dict[str, Any]:
    found_ids: Dict[str, List[str]] = {}
    for i in range(0, len(skus), SOQL_BATCH):
        chunk = ",".join(f"'{soql_literal(s)}'" for s in skus[i:i + SOQL_BATCH])
        for r in t.soql(f"SELECT Id, StockKeepingUnit FROM Product2 WHERE StockKeepingUnit IN ({chunk}) "
                        "ORDER BY StockKeepingUnit, Id"):
            found_ids.setdefault(r["StockKeepingUnit"], []).append(r["Id"])
    # A SKU held by two products (a duplicating reload) is reported, never silently collapsed:
    # one of them would be captured at random and the other's prices merged in.
    duplicates = sorted(s for s, v in found_ids.items() if len(v) > 1)
    ids = {s: v[0] for s, v in found_ids.items() if len(v) == 1}
    prices: Dict[str, Dict[str, float]] = {}
    for i in range(0, len(skus), SOQL_BATCH):
        chunk = ",".join(f"'{soql_literal(s)}'" for s in skus[i:i + SOQL_BATCH])
        for r in t.soql("SELECT Product2.StockKeepingUnit, ProductSellingModel.Name, CurrencyIsoCode, "
                        "UnitPrice FROM PricebookEntry WHERE Pricebook2.IsStandard = true AND IsActive = true "
                        f"AND Product2.StockKeepingUnit IN ({chunk})"):
            model = (r.get("ProductSellingModel") or {}).get("Name") or "-"
            entry = prices.setdefault(r["Product2"]["StockKeepingUnit"], {})
            key = f"{model} {r['CurrencyIsoCode']}"
            # Two active standard entries for one model and currency (a duplicating price load)
            # show as a list rather than one overwriting the other.
            entry[key] = sorted([*entry[key], r["UnitPrice"]] if isinstance(entry.get(key), list)
                                else [entry[key], r["UnitPrice"]]) if key in entry else r["UnitPrice"]
    found = sorted(ids)
    by_id = {v: k for k, v in ids.items()}  # key by the SKU asked for: productCode can be blank
    products: Dict[str, Any] = {}
    for i in range(0, len(found), BULK_BATCH):
        resp = t.connect("POST", "connect/pcm/products/bulk",
                         {"productIds": [ids[s] for s in found[i:i + BULK_BATCH]]})
        for p in (resp or {}).get("products") or []:
            sku = by_id.get(p.get("id"))
            if sku:
                products[sku] = normalize(p, prices, sku)
    return {"skus": skus, "missing": sorted(set(skus) - set(found_ids)), "duplicates": duplicates,
            "notReturned": sorted(set(ids) - set(products)),
            "products": {s: products[s] for s in sorted(products)}}


# Lists compared as sets keyed by these fields, so one inserted item doesn't misreport every later one.
LIST_KEYS = {"attributes": ("categoryCode", "code"), "componentGroups": ("code",), "components": ("sku",),
             "childProducts": ("sku",),
             "childGroups": ("code",), "sellingModels": ("name",)}


def _key(it: Dict[str, Any], fields) -> str:
    def part(f):
        if f == "categoryCode":  # a category rename is one field change, not every attribute moving
            return str((it.get("category") or {}).get("code"))
        return str(it.get(f))
    return "|".join(part(f) for f in fields)


def _keyed(items: List[Any], fields) -> Dict[str, Any]:
    """Items by key. Items that share a key are kept as one list, so their (arbitrary) API order
    can't produce a false or masked difference; diff compares them as a sorted group."""
    out: Dict[str, Any] = {}
    for it in items:
        out.setdefault(_key(it, fields), []).append(it)
    return {k: v[0] if len(v) == 1 else sorted(v, key=lambda x: json.dumps(x, sort_keys=True))
            for k, v in out.items()}


def diff(a: Any, b: Any, path: str = "") -> List[str]:
    name = path.rsplit("/", 1)[-1]
    if name in LIST_KEYS and isinstance(a, list) and isinstance(b, list):
        ka, kb = _keyed(a, LIST_KEYS[name]), _keyed(b, LIST_KEYS[name])
        out = [f"{path}[{k}]: removed" for k in sorted(set(ka) - set(kb))]
        out += [f"{path}[{k}]: added" for k in sorted(set(kb) - set(ka))]
        for k in sorted(set(ka) & set(kb)):
            ga, gb = isinstance(ka[k], list), isinstance(kb[k], list)
            if ga != gb:  # one side holds two or more items with this key
                side, n = ("baseline", len(ka[k])) if ga else ("candidate", len(kb[k]))
                out.append(f"{path}[{k}]: duplicated ({n}) in {side}")
            else:
                out += diff(ka[k], kb[k], f"{path}[{k}]")
        return out
    if isinstance(a, dict) and isinstance(b, dict):
        out: List[str] = []
        for k in sorted(set(a) | set(b), key=str):
            if k not in a:
                out.append(f"{path}/{k}: added {json.dumps(b[k], sort_keys=True)[:200]}")
            elif k not in b:
                out.append(f"{path}/{k}: removed {json.dumps(a[k], sort_keys=True)[:200]}")
            else:
                out += diff(a[k], b[k], f"{path}/{k}")
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) == len(b):
            return [d for i, (x, y) in enumerate(zip(a, b)) for d in diff(x, y, f"{path}[{i}]")]
        ja, jb = [json.dumps(x, sort_keys=True) for x in a], [json.dumps(y, sort_keys=True) for y in b]
        return ([f"{path}: removed {x[:200]}" for x in ja if x not in jb]
                + [f"{path}: added {y[:200]}" for y in jb if y not in ja]
                or [f"{path}: {len(a)} -> {len(b)} items"])
    return [] if a == b else [f"{path}: {json.dumps(a, sort_keys=True)[:200]} -> {json.dumps(b, sort_keys=True)[:200]}"]


def compare(base: Dict[str, Any], cand: Dict[str, Any]) -> List[str]:
    out = [f"{s}: {what} in {label}" for label, side in (("baseline", base), ("candidate", cand))
           for key, what in (("missing", "missing from the org"), ("notReturned", "not returned by PCM"),
                             ("duplicates", "held by more than one product"))
           for s in side.get(key, [])]
    bp, cp = base.get("products", {}), cand.get("products", {})
    for sku in sorted(set(bp) | set(cp)):
        if sku not in cp:
            out.append(f"{sku}: only in baseline")
        elif sku not in bp:
            out.append(f"{sku}: only in candidate")
        else:
            out += [f"{sku}{d}" for d in diff(bp[sku], cp[sku])]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("capture", help="Read the product view from an org (read-only).")
    c.add_argument("--target-org", required=True, help="SF CLI alias or username; not a CCI alias.")
    c.add_argument("--shape", choices=sorted(SHAPE_PLANS), required=True)
    c.add_argument("--sku", action="append", help="Limit to these SKUs (repeatable).")
    c.add_argument("--out", required=True)
    d = sub.add_parser("compare", help="Diff two captures; exit 1 on any difference.")
    d.add_argument("baseline")
    d.add_argument("candidate")
    args = ap.parse_args(argv)
    if args.cmd == "capture":
        skus = sorted(set(args.sku)) if args.sku else shape_skus(args.shape)
        try:
            view = {"shape": args.shape, **capture(Transport(args.target_org), skus)}
        except DecisionTableClientError as exc:
            print(f"capture failed: {exc}", file=sys.stderr)
            return 2
        Path(args.out).write_text(json.dumps(view, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"{len(view['products'])} product(s) captured, {len(view['missing'])} missing, "
              f"{len(view['duplicates'])} duplicated, {len(view['notReturned'])} not returned by PCM -> {args.out}")
        return 0
    base = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    cand = json.loads(Path(args.candidate).read_text(encoding="utf-8"))
    diffs = compare(base, cand)
    for line in diffs:
        print(line)
    print(f"{len(diffs)} difference(s)")
    return 1 if diffs else 0


if __name__ == "__main__":
    sys.exit(main())
