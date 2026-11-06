#!/usr/bin/env python3
"""Offline tests for scripts/sfdmu_product_view.py (todo 330).

- normalize keeps what the configurator shows (category, label, override, default, flags, picklist
  values in sequence order, bundle groups and components, selling models, list prices) and drops
  record Ids, so captures from different orgs compare.
- compare reports a changed label or category, an added or removed attribute (by category and
  code, not position), a SKU only on one side, and SKUs missing from an org or not returned by PCM.
  Identical captures, and lists in a different order, report nothing.
- capture batches Product2 lookups at 200 SKUs and the PCM bulk call at 20 product Ids (the
  platform rejects more), keys products by the SKU asked for even when PCM returns a blank
  productCode, reports a SKU two products hold instead of capturing one at random, and keeps
  both of two price entries for one selling model and currency.
- Picklist values are compared with their display text, in numeric sequence order. Items that
  share a key (a duplicated attribute) are a difference, in any API order.

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
                         "values": [{"id": "0v6XX", "code": v, "displayValue": f"{v} shown", "value": v,
                                     "status": "Active", "sequence": str(len(values) - i)}
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
check("picklist values come out in sequence order, with their display text",
      [(v["code"], v["displayValue"]) for v in n["attributes"][1]["values"]], [("B", "B shown"), ("A", "A shown")])
many = V.normalize(product("P", {"C": [attr("X", "X", values=[f"v{i}" for i in range(12)])]}), {}, "P")
check("sequences sort numerically (2 before 10)",
      [v["code"] for v in many["attributes"][0]["values"]][:3], ["v11", "v10", "v9"])
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
check("a different category code reads as one removed and one added attribute",
      sorted(d.rsplit(": ", 1)[1] for d in diffs), ["added", "removed"])
extra = copy.deepcopy(base)
extra["products"]["LP001"]["attributes"].insert(0, V._attr(attr("AAA", "First"), None))
check("an inserted attribute is one difference, not a cascade", len(V.compare(base, extra)), 1)
shuffled = copy.deepcopy(base)
shuffled["products"]["LP001"]["attributes"].reverse()
check("a different list order is not a difference", V.compare(base, shuffled), [])
relabel_value = copy.deepcopy(base)
relabel_value["products"]["LP001"]["attributes"][1]["values"][0]["displayValue"] = "Renamed"
check("a renamed picklist display value is a difference", len(V.compare(base, relabel_value)), 1)
dup = copy.deepcopy(base)
twin = copy.deepcopy(dup["products"]["LP001"]["attributes"][1])
twin["default"] = "i7"  # same key, different content, so the order of the two matters
dup["products"]["LP001"]["attributes"].append(twin)
diffs = V.compare(base, dup)
check("a duplicated attribute (same key) is one difference, named as duplicated",
      (len(diffs), "duplicated (2) in candidate" in diffs[0]), (1, True))
dup_rev = copy.deepcopy(dup)
dup_rev["products"]["LP001"]["attributes"].reverse()
check("the same duplicates in another API order are not a difference", V.compare(dup, dup_rev), [])
nested = copy.deepcopy(base)
nested["products"]["LP001"]["componentGroups"][0]["childGroups"] = [
    {"code": "G2", "name": "Child group", "components": [], "childGroups": []}]
check("a nested child group is compared", any("childGroups" in d for d in V.compare(base, nested)), True)
renamed_cat = copy.deepcopy(base)
renamed_cat["products"]["LP001"]["attributes"][1]["category"]["name"] = "CPU"
diffs = V.compare(base, renamed_cat)
check("a renamed category is one field change, not a removed and added attribute",
      (len(diffs), diffs[0].endswith('"Proc" -> "CPU"')), (1, True))
fewer = copy.deepcopy(base)
fewer["products"]["LP001"]["attributes"][1]["values"].pop()
diffs = V.compare(base, fewer)
check("a dropped picklist value is reported as removed", (len(diffs), "removed" in diffs[0]), (1, True))
check("a SKU only in the baseline is reported",
      V.compare(base, {"missing": [], "notReturned": [], "products": {}}), ["LP001: only in baseline"])
check("missing and not-returned SKUs are reported on either side",
      V.compare({"missing": ["X"], "notReturned": [], "products": {}},
                {"missing": [], "notReturned": ["Y"], "products": {}}),
      ["X: missing from the org in baseline", "Y: not returned by PCM in candidate"])
check("a duplicated SKU is reported",
      V.compare({"duplicates": ["D"], "products": {}}, {"products": {}}),
      ["D: held by more than one product in baseline"])

print("capture: PCM batching and SKU keys")


class FakeTransport:
    def __init__(self, skus, blank_code=(), dup=(), dup_price=()):
        self.skus, self.blank, self.bulk_sizes, self.soql_sizes = skus, set(blank_code), [], []
        self.dup, self.dup_price = set(dup), set(dup_price)

    def soql(self, q):
        hits = [s for s in self.skus if f"'{s}'" in q]
        if "FROM PricebookEntry" in q:
            return [{"Product2": {"StockKeepingUnit": s}, "ProductSellingModel": {"Name": "One-Time"},
                     "CurrencyIsoCode": "USD", "UnitPrice": p} for s in hits
                    for p in ((10, 12) if s in self.dup_price else (10,))]
        self.soql_sizes.append(len(hits))
        return [{"Id": f"01t{s}{n}", "StockKeepingUnit": s} for s in hits
                for n in (("", "b") if s in self.dup else ("",))]

    def connect(self, method, path, body):
        self.bulk_sizes.append(len(body["productIds"]))
        return {"products": [dict(product(i[3:], {}, code="" if i[3:] in self.blank else None), id=i)
                             for i in body["productIds"]]}


skus = [f"S{i:03d}" for i in range(45)]
ft = FakeTransport(skus, blank_code={"S007"})
view = V.capture(ft, skus + ["GONE"])
check("bulk calls hold at most 20 Ids", ft.bulk_sizes, [20, 20, 5])
check("every SKU found is captured", len(view["products"]), 45)
check("a blank productCode is still keyed by the SKU asked for", "S007" in view["products"], True)
check("a SKU the org lacks is listed as missing", view["missing"], ["GONE"])
check("nothing unreturned", view["notReturned"], [])
big = [f"B{i:03d}" for i in range(450)]
ft = FakeTransport(big, dup={"B004"}, dup_price={"B005"})
view = V.capture(ft, big)
check("Product2 lookups go 200 SKUs at a time", ft.soql_sizes, [200, 200, 50])
check("a SKU two products hold is reported, not captured", (view["duplicates"], "B004" in view["products"]),
      (["B004"], False))
check("a duplicated SKU is not also listed as missing", "B004" in view["missing"], False)
check("two entries for one model and currency are both kept", view["products"]["B005"]["listPrices"],
      {"One-Time USD": [10, 12]})
quoted = FakeTransport([])
seen = []
quoted.soql = lambda q: seen.append(q) or []
V.capture(quoted, ["O'Brien"])
check("a SKU with a quote is escaped in SOQL", "'O\\'Brien'" in seen[0], True)

print("main: a platform error is a clear exit 2, not a traceback")


class FailingTransport:
    def __init__(self, *_a, **_k):
        pass

    def soql(self, _q):
        raise V.DecisionTableClientError("EPC_PAPI_PROD_DETAILS_008: limit")


saved = V.Transport
V.Transport = FailingTransport
try:
    import io
    import contextlib
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        code = V.main(["capture", "--target-org", "x@example.com", "--shape", "q3", "--sku", "A",
                       "--out", "/dev/null"])
finally:
    V.Transport = saved
check("capture exits 2 on a platform error", code, 2)
check("and names the error", "EPC_PAPI_PROD_DETAILS_008" in err.getvalue(), True)

print("=" * 60)
if _failures:
    print(f"FAIL: {len(_failures)} check(s) failed")
    sys.exit(1)
print("All checks passed")
