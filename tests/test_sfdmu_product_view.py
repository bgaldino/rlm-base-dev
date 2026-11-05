#!/usr/bin/env python3
"""Offline tests for scripts/sfdmu_product_view.py (todo 330).

- normalize keeps what the configurator shows (category, label, override, default, flags, picklist
  values in sequence order, bundle groups and components, selling models, list prices) and drops
  record Ids, so captures from different orgs compare.
- compare reports a changed label or category, an added or removed attribute (by category and
  code, not position), a SKU only on one side, and SKUs missing from an org or not returned by PCM.
  Identical captures, and lists in a different order, report nothing.
- capture batches the PCM bulk call at 20 product Ids (the platform rejects more) and keys
  products by the SKU asked for, even when PCM returns a blank productCode.

Run: `python tests/test_sfdmu_product_view.py` (offline, no org).
"""
from __future__ import annotations

import copy
import importlib.util
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
spec = importlib.util.spec_from_file_location("sfdmu_product_view", REPO / "scripts" / "sfdmu_product_view.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)

_failures = []


def check(label, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'} {label}")
    if not ok:
        _failures.append(label)
        print(f"       got:  {got!r}\n       want: {want!r}")


def attr(code, label, category=None, default=None, values=("A", "B")):
    return {"id": "0tjXX0000000001", "code": code, "label": label, "name": label,
            "attributeNameOverride": label, "dataType": "Picklist", "displayType": "ComboBox",
            "defaultValue": default, "isRequired": False, "isHidden": False, "isReadOnly": False,
            "isPriceImpacting": True, "status": "Active",
            "picklist": {"id": "0v5XX", "name": f"{code} Picklist",
                         "values": [{"id": "0v6XX", "code": v, "sequence": str(len(values) - i)}
                                    for i, v in enumerate(values)]}}


def product(sku, attrs_by_cat, loose=(), code=None):
    return {"id": f"01t{sku}", "productCode": sku if code is None else code, "name": f"{sku} name",
            "isActive": True, "nodeType": "simpleProduct", "configureDuringSale": "Allowed",
            "isAssetizable": True, "isSoldOnlyWithOtherProds": False,
            "attributeCategory": [{"id": "0v3XX", "code": c, "name": c.title(), "attributes": list(a)}
                                  for c, a in attrs_by_cat.items()],
            "attributes": list(loose),
            "productComponentGroups": [{"id": "0yVXX", "code": "G1", "name": "Group", "sequence": 1,
                                        "minBundleComponents": 0, "maxBundleComponents": 2, "childGroups": [],
                                        "components": [{"productCode": "CHILD", "name": "Child", "productRelatedComponent": {
                                            "id": "0dSXX", "quantity": 1, "isComponentRequired": False,
                                            "isDefaultComponent": True, "isQuantityEditable": False,
                                            "quantityScaleMethod": "Proportional", "sequence": 10}}]}],
            "productSellingModelOptions": [{"id": "0iOXX", "isDefault": True, "productSellingModel": {
                "id": "0jPXX", "name": "Term Annual", "sellingModelType": "TermDefined"}}]}


print("normalize: what the configurator shows, without record Ids")
p = product("LP001", {"PROC": [attr("CPU", "Processor", default="i5")]}, loose=[attr("COLOR", "Color")])
n = V.normalize(p, {"LP001": {"Term Annual USD": 1000}}, "LP001")
check("category attribute carries its category", n["attributes"][1]["category"], {"code": "PROC", "name": "Proc"})
check("an uncategorized attribute has category None", n["attributes"][0]["category"], None)
check("picklist values come out in sequence order", n["attributes"][1]["values"], ["B", "A"])
check("label, override and default are kept",
      (n["attributes"][1]["label"], n["attributes"][1]["nameOverride"], n["attributes"][1]["default"]),
      ("Processor", "Processor", "i5"))
check("bundle component carries quantity and default flag",
      {k: n["componentGroups"][0]["components"][0][k] for k in ("sku", "quantity", "default")},
      {"sku": "CHILD", "quantity": 1, "default": True})
check("selling models by name and type", n["sellingModels"],
      [{"name": "Term Annual", "type": "TermDefined", "default": True}])
check("list prices by selling model and currency", n["listPrices"], {"Term Annual USD": 1000})
check("no record Ids anywhere", any(s in json.dumps(n) for s in ("0tjXX", "0v5XX", "0v6XX", "0dSXX", "0jPXX", "01tLP001")), False)

print("compare: differences by SKU and path")
base = {"missing": [], "notReturned": [], "products": {"LP001": n}}
check("identical captures: nothing", V.compare(base, copy.deepcopy(base)), [])
relabeled = copy.deepcopy(base)
relabeled["products"]["LP001"]["attributes"][1]["label"] = "CPU"
diffs = V.compare(base, relabeled)
check("a changed label is one difference", len(diffs), 1)
check("it names the SKU, the attribute and the field",
      all(s in diffs[0] for s in ("LP001", "CPU", "label", '"Processor" -> "CPU"')), True)
moved = copy.deepcopy(base)
moved["products"]["LP001"]["attributes"][1]["category"] = {"code": "SHARED", "name": "Processor"}
diffs = V.compare(base, moved)
check("a changed category reads as one removed and one added attribute",
      sorted(d.rsplit(": ", 1)[1] for d in diffs), ["added", "removed"])
extra = copy.deepcopy(base)
extra["products"]["LP001"]["attributes"].insert(0, V._attr(attr("AAA", "First"), None))
check("an inserted attribute is one difference, not a cascade", len(V.compare(base, extra)), 1)
shuffled = copy.deepcopy(base)
shuffled["products"]["LP001"]["attributes"].reverse()
check("a different list order is not a difference", V.compare(base, shuffled), [])
check("a SKU only in the baseline is reported",
      V.compare(base, {"missing": [], "notReturned": [], "products": {}}), ["LP001: only in baseline"])
check("missing and not-returned SKUs are reported on either side",
      V.compare({"missing": ["X"], "notReturned": [], "products": {}},
                {"missing": [], "notReturned": ["Y"], "products": {}}),
      ["X: missing from the org in baseline", "Y: not returned by PCM in candidate"])

print("capture: PCM batching and SKU keys")


class FakeTransport:
    def __init__(self, skus, blank_code=()):
        self.skus, self.blank, self.bulk_sizes = skus, set(blank_code), []

    def soql(self, q):
        if "FROM PricebookEntry" in q:
            return [{"Product2": {"StockKeepingUnit": s}, "ProductSellingModel": {"Name": "One-Time"},
                     "CurrencyIsoCode": "USD", "UnitPrice": 10} for s in self.skus if f"'{s}'" in q]
        return [{"Id": f"01t{s}", "StockKeepingUnit": s} for s in self.skus if f"'{s}'" in q]

    def connect(self, method, path, body):
        self.bulk_sizes.append(len(body["productIds"]))
        return {"products": [product(i[3:], {}, code="" if i[3:] in self.blank else None)
                             for i in body["productIds"]]}


skus = [f"S{i:03d}" for i in range(45)]
ft = FakeTransport(skus, blank_code={"S007"})
view = V.capture(ft, skus + ["GONE"])
check("bulk calls hold at most 20 Ids", ft.bulk_sizes, [20, 20, 5])
check("every SKU found is captured", len(view["products"]), 45)
check("a blank productCode is still keyed by the SKU asked for", "S007" in view["products"], True)
check("a SKU the org lacks is listed as missing", view["missing"], ["GONE"])
check("nothing unreturned", view["notReturned"], [])

print("=" * 60)
if _failures:
    print(f"FAIL: {len(_failures)} check(s) failed")
    sys.exit(1)
print("All checks passed")
