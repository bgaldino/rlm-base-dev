#!/usr/bin/env python3
"""Offline tests for scripts/sfdmu_product_view.py (todo 330).

- normalize keeps what the configurator shows (category, label, override, default, flags, picklist
  values in sequence order, bundle groups and components, ungrouped bundle components, selling
  models, list prices) and drops record Ids, so captures from different orgs compare.
- compare reports a changed label or category, an added or removed attribute (by category and
  code, not position), a SKU only on one side, SKUs missing from an org or not returned by PCM, and
  a capture's uncovered fields on either side.
  Identical captures, and lists in a different order, report nothing.
- capture batches Product2 lookups at 200 SKUs and the PCM bulk call at 20 product Ids (the
  platform rejects more), keys products by the SKU asked for even when PCM returns a blank
  productCode, reports a SKU two products hold instead of capturing one at random, and keeps
  both of two price entries for one selling model and currency. Selling models (in list prices and
  in the selling-model list) are told apart by Name and SellingModelType.
- Picklist values are compared with their display text, in numeric sequence order. Items that
  share a key (a duplicated attribute) are a difference, in any API order.
- Classification components and a product's base classification resolve to the classification's
  code, and a component's parent and child selling model to `Name;SellingModelType` and its
  relationship type to its name. A blank lookup is None and one that can't be resolved keeps its
  Id as `unresolved <kind> <id>`. Category membership comes from SOQL.
- audit_fields: every READ key reaches the normalized view (each is mutated and the view must
  change), a filled key PCM starts returning is reported by level, and capture then exits 3.

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
            "picklist": {"id": "0v5XX", "name": f"{code} Picklist", "dataType": "Text", "description": "pd",
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
                                            "quantityScaleMethod": "Proportional", "sequence": 10,
                                            "doesBundlePriceIncludeChild": False, "isExcluded": True,
                                            "quoteVisibility": "Always"}}]}],
            "productSellingModelOptions": [{"id": "0iOXX", "isDefault": True, "productSellingModel": {
                "id": "0jPXX", "name": "Term Annual", "sellingModelType": "TermDefined", "pricingTerm": 1,
                "pricingTermUnit": "Annual", "status": "Active", "doesAutoRenewByDefault": False}}]}


print("normalize: what the configurator shows, without record Ids")
p = product("LP001", {"PROC": [attr("CPU", "Processor", default="i5")]}, loose=[attr("COLOR", "Color")])
n = V.normalize(p, {"LP001": {"Term Annual;TermDefined USD": 1000}}, "LP001")
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
      [{"name": "Term Annual", "type": "TermDefined", "default": True, "pricingTerm": 1,
        "pricingTermUnit": "Annual", "status": "Active", "autoRenew": False}])
check("list prices by selling model and currency", n["listPrices"], {"Term Annual;TermDefined USD": 1000})
uom = product("U", {"C": [dict(attr("X", "X"), sequence=3, stepValue=5, unitOfMeasureInfo={"id": "0hEXX", "unitCode": "GB"})]})
uom["unitOfMeasureInfo"] = {"id": "0hEXX", "name": "Minutes", "unitCode": "m"}
uom["description"] = "Shown in the catalog"
nu = V.normalize(uom, {}, "U")
check("the product's unit and description are captured by value", (nu["unit"], nu["description"]),
      ({"code": "m", "name": "Minutes", "scale": None, "rounding": None}, "Shown in the catalog"))
check("an attribute's unit, step and display order are captured",
      {k: nu["attributes"][0][k] for k in ("unit", "stepValue", "sequence")},
      {"unit": {"code": "GB", "name": None, "scale": None, "rounding": None}, "stepValue": 5, "sequence": 3})
check("the unit's record Id is not", "0hEXX" in json.dumps(nu), False)
check("no record Ids anywhere", any(s in json.dumps(n) for s in ("0tjXX", "0v5XX", "0v6XX", "0dSXX", "0jPXX", "01tLP001")), False)

ungrouped = product("CERT", {})
ungrouped["productComponentGroups"] = []
ungrouped["childProducts"] = [{"productCode": "AST", "name": "Asset cert", "productRelatedComponent": {
    "id": "0dSXX", "quantity": 1, "isComponentRequired": True, "isDefaultComponent": True,
    "doesBundlePriceIncludeChild": True, "quantityScaleMethod": "Proportional", "isExcluded": False,
    "quoteVisibility": "Never"}}]
un = V.normalize(ungrouped, {}, "CERT")
check("an ungrouped bundle component is captured",
      [(c["sku"], c["required"], c["inBundlePrice"], c["excluded"], c["quoteVisibility"]) for c in un["childProducts"]],
      [("AST", True, True, False, "Never")])
check("a grouped component carries the same flags",
      {k: n["componentGroups"][0]["components"][0][k] for k in ("inBundlePrice", "excluded", "quoteVisibility")},
      {"inBundlePrice": False, "excluded": True, "quoteVisibility": "Always"})
dropped = copy.deepcopy(un)
dropped["childProducts"] = []
check("removing an ungrouped component is a difference",
      V.compare({"products": {"CERT": un}}, {"products": {"CERT": dropped}}),
      ["CERT/childProducts[AST]: removed"])
requant = copy.deepcopy(un)
requant["childProducts"][0]["quantity"] = 2
check("changing its quantity is a difference",
      V.compare({"products": {"CERT": un}}, {"products": {"CERT": requant}}),
      ["CERT/childProducts[AST]/quantity: 1 -> 2"])

term = copy.deepcopy(n)
term["sellingModels"][0]["pricingTermUnit"] = "Months"
check("a selling model's term unit change is a difference",
      V.compare({"products": {"LP001": n}}, {"products": {"LP001": term}}),
      ["LP001/sellingModels[Term Annual|TermDefined]/pricingTermUnit: \"Annual\" -> \"Months\""])
limits = product("Q", {})
prc = limits["productComponentGroups"][0]["components"][0]["productRelatedComponent"]
prc.update(minQuantity=1, maxQuantity=5)
nl = V.normalize(limits, {}, "Q")
check("a component's quantity limits are captured",
      {k: nl["componentGroups"][0]["components"][0][k] for k in ("minQuantity", "maxQuantity")},
      {"minQuantity": 1, "maxQuantity": 5})
widened = copy.deepcopy(nl)
widened["componentGroups"][0]["components"][0]["maxQuantity"] = 10
check("and a changed maximum is a difference",
      V.compare({"products": {"Q": nl}}, {"products": {"Q": widened}}),
      ["Q/componentGroups[G1]/components[CHILD]/maxQuantity: 5 -> 10"])
klass = product("LPB", {})
klass["productComponentGroups"][0]["components"] = [
    {"productCode": None, "name": None, "id": "11BXX", "nodeType": "productClass",
     "productRelatedComponent": {"id": "0dSXX", "productClassificationId": "11BXX", "quantity": 1}}]
nk = V.normalize(klass, {}, "LPB", {"11BXX": "SFT001"})
check("a classification component is keyed by its classification code, not its Id",
      (nk["componentGroups"][0]["components"][0]["sku"], nk["componentGroups"][0]["components"][0]["classification"],
       "11BXX" in json.dumps(nk)), ("classification:SFT001", "SFT001", False))

print("audit_fields: every filled PCM key is compared or deliberately skipped")
check("the fixtures' keys are all covered", V.audit_fields([p, ungrouped, uom, limits, klass]), [])
# Every READ key must reach the output: change it in a fixture and the normalized view must change.
# (A key listed in READ that normalize never reads would make the coverage audit lie.)
UNIT = {"unitCode": "GB", "name": "Gigabyte", "scale": 2, "roundingMethod": "Up"}
rich = product("R", {"C": [dict(attr("X", "X"), description="d", sequence=1, stepValue=1,
                                unitOfMeasureInfo=dict(UNIT))]}, loose=[attr("L", "L")])
rich.update(description="d", displayUrl="/u", productClassification={"id": "11BXX"},
            unitOfMeasureInfo=dict(UNIT, unitCode="m"))
rich["childProducts"] = copy.deepcopy(rich["productComponentGroups"][0]["components"])
rprc = rich["productComponentGroups"][0]["components"][0]["productRelatedComponent"]
rprc.update(minQuantity=1, maxQuantity=2, unitOfMeasureInfo=dict(UNIT, unitCode="EA"), productClassificationId="11BXX",
            parentSellingModelId="0jPXX", childSellingModelId="0jPXX", productRelationshipTypeId="0yoXX")
rich["productComponentGroups"][0]["childGroups"] = [{"code": "G2", "components": [], "childGroups": []}]
rich["productComponentGroups"][0]["isExcluded"] = False
for a_ in [a for c in rich["attributeCategory"] for a in c["attributes"]] + rich["attributes"]:
    for v in a_["picklist"]["values"]:
        v["name"] = v["code"]
CLS = {"11BXX": "SFT001", "11BYY": "OTHER", "0jPXX": "Term Monthly", "0yoXX": "Bundle"}


def nodes(level, prod):
    """The dicts at one audit level of a product (mirrors audit_fields' walk)."""
    attrs = [a for c in prod["attributeCategory"] for a in c["attributes"]] + prod["attributes"]
    comps = [c for g in prod["productComponentGroups"] for c in g["components"]] + prod["childProducts"]
    units = [u for u in [prod.get("unitOfMeasureInfo")] + [a.get("unitOfMeasureInfo") for a in attrs]
             + [c["productRelatedComponent"].get("unitOfMeasureInfo") for c in comps] if u]
    return {"unit": units, "classificationRef": [prod["productClassification"]], "product": [prod], "category": prod["attributeCategory"], "attribute": attrs,
            "picklist": [a["picklist"] for a in attrs], "picklistValue": [v for a in attrs for v in a["picklist"]["values"]],
            "group": prod["productComponentGroups"], "component": comps,
            "relatedComponent": [c["productRelatedComponent"] for c in comps],
            "sellingModelOption": prod["productSellingModelOptions"],
            "sellingModel": [o["productSellingModel"] for o in prod["productSellingModelOptions"]]}[level]


silent = []
for level, keys in V.READ.items():
    for key in sorted(keys):
        mutated = copy.deepcopy(rich)
        targets = [node for node in nodes(level, mutated) if key in node]
        if not targets:
            silent.append(f"{level}.{key} (not in the fixture)")
            continue
        for node in targets:
            old = node[key]
            node[key] = ({"id": "11BYY"} if key == "productClassification" else "11BYY" if key.endswith("Id")
                      else dict(old, unitCode="ZZ") if key == "unitOfMeasureInfo" else [] if isinstance(old, list)
                      else {} if isinstance(old, dict) else (not old) if isinstance(old, bool)
                      else 99 if isinstance(old, (int, float)) else f"{old}-changed")
        if V.normalize(mutated, {}, "R", CLS) == V.normalize(rich, {}, "R", CLS):
            silent.append(f"{level}.{key}")
check("every READ key changes the normalized view", silent, [])
novel = copy.deepcopy(p)
novel["attributeCategory"][0]["attributes"][0]["newPlatformField"] = "x"
novel["productSellingModelOptions"][0]["productSellingModel"]["billingCycle"] = "Monthly"
check("a key PCM starts returning is reported, by level",
      V.audit_fields([novel]), ["attribute.newPlatformField", "sellingModel.billingCycle"])
blank = copy.deepcopy(p)
blank["attributeCategory"][0]["attributes"][0]["emptyField"] = None
check("an empty key is not", V.audit_fields([blank]), [])
unit_extra = copy.deepcopy(rich)
unit_extra["unitOfMeasureInfo"]["productUnitKey"] = 1
unit_extra["attributeCategory"][0]["attributes"][0]["unitOfMeasureInfo"]["attributeUnitKey"] = 1
(unit_extra["productComponentGroups"][0]["components"][0]["productRelatedComponent"]
 ["unitOfMeasureInfo"]["groupedUnitKey"]) = 1
unit_extra["childProducts"][0]["productRelatedComponent"]["unitOfMeasureInfo"] = dict(UNIT, ungroupedUnitKey=1)
klass_extra = copy.deepcopy(rich)
klass_extra["productClassification"]["code"] = "SFT001"
check("keys inside each unit (product, attribute, grouped and ungrouped component) and the "
      "classification reference are audited too",
      V.audit_fields([unit_extra, klass_extra]),
      ["classificationRef.code", "unit.attributeUnitKey", "unit.groupedUnitKey", "unit.productUnitKey",
       "unit.ungroupedUnitKey"])
sm = copy.deepcopy(rich)
sm_prc = sm["productComponentGroups"][0]["components"][0]["productRelatedComponent"]
sm_prc.update(parentSellingModelId=None, childSellingModelId="0jPZZ")
sm_c = V.normalize(sm, {}, "R", CLS)["componentGroups"][0]["components"][0]
check("a component's selling models and relationship type are captured by name; a blank one is None "
      "and an unresolved one keeps its Id",
      [V.normalize(rich, {}, "R", CLS)["componentGroups"][0]["components"][0][k]
       for k in ("parentSellingModel", "childSellingModel", "relationshipType")]
      + [sm_c["parentSellingModel"], sm_c["childSellingModel"]],
      ["Term Monthly", "Term Monthly", "Bundle", None, "unresolved selling model 0jPZZ"])
same_models = {"products": {"S": {"sellingModels": [{"name": "Annual", "type": "TermDefined", "default": True},
                                                   {"name": "Annual", "type": "Evergreen", "default": False}]}}}
swapped = copy.deepcopy(same_models)
for m_ in swapped["products"]["S"]["sellingModels"]:
    m_["default"] = not m_["default"]
check("selling models sharing a name are matched by type: a swapped default reads as two default changes, not type changes",
      sorted(V.compare(same_models, swapped)),
      ["S/sellingModels[Annual|Evergreen]/default: false -> true",
       "S/sellingModels[Annual|TermDefined]/default: true -> false"])
check("and the same pair in either order is no difference",
      V.compare(same_models, {"products": {"S": {"sellingModels": same_models["products"]["S"]["sellingModels"][::-1]}}}), [])
check("a capture with uncovered fields fails compare on either side",
      V.compare({"uncoveredFields": ["unit.a"], "products": {}}, {"uncoveredFields": ["unit.b"], "products": {}}),
      ["unit.a: returned by PCM but not compared (capture exited 3) in baseline",
       "unit.b: returned by PCM but not compared (capture exited 3) in candidate"])

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
            return [{"Product2": {"StockKeepingUnit": s},
                     "ProductSellingModel": {"Name": "One-Time", "SellingModelType": "OneTime"},
                     "CurrencyIsoCode": "USD", "UnitPrice": p} for s in hits
                    for p in ((10, 12) if s in self.dup_price else (10,))]
        if "FROM ProductClassification" in q:
            return [{"Id": "11BXX", "Code": "SFT001"}]
        if "FROM ProductSellingModel" in q:
            return [{"Id": "0jPXX", "Name": "Term Monthly", "SellingModelType": "TermDefined"}]
        if "FROM ProductRelationshipType" in q:
            return [{"Id": "0yoXX", "Name": "Bundle to Bundle Component Relationship"}]
        if "FROM ProductCategoryProduct" in q:
            return [{"Product": {"StockKeepingUnit": s}, "IsPrimaryCategory": True,
                     "ProductCategory": {"Code": "PC-1", "Catalog": {"Code": "CAT-1"}}} for s in hits]
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
check("category membership is read from ProductCategoryProduct",
      view["products"]["S001"]["categories"], [{"category": "PC-1", "catalog": "CAT-1", "primary": True}])
check("a blank productCode is still keyed by the SKU asked for", "S007" in view["products"], True)
check("a SKU the org lacks is listed as missing", view["missing"], ["GONE"])
check("nothing unreturned", view["notReturned"], [])
same_name = FakeTransport(["S1"])
same_name.soql = lambda q, _f=same_name.soql: ([
    {"Product2": {"StockKeepingUnit": "S1"}, "ProductSellingModel": {"Name": "Annual", "SellingModelType": st},
     "CurrencyIsoCode": "USD", "UnitPrice": up} for st, up in (("TermDefined", 100), ("Evergreen", 90))]
    if "FROM PricebookEntry" in q else _f(q))
check("two selling models that share a name but not a type keep separate prices",
      V.capture(same_name, ["S1"])["products"]["S1"]["listPrices"],
      {"Annual;TermDefined USD": 100, "Annual;Evergreen USD": 90})
refd = FakeTransport(["S1"])
refd.connect = lambda m, p, b: {"products": [dict(product("S1", {}), id="01tS1", childProducts=[
    {"productCode": "C", "name": "C", "productRelatedComponent": {
        "parentSellingModelId": "0jPXX", "childSellingModelId": "0jPXX", "productRelationshipTypeId": "0yoXX"}}])]}
rc = V.capture(refd, ["S1"])["products"]["S1"]["childProducts"][0]
check("capture keys a selling model by name and type, and a relationship type by name",
      [rc["parentSellingModel"], rc["childSellingModel"], rc["relationshipType"]],
      ["Term Monthly;TermDefined", "Term Monthly;TermDefined", "Bundle to Bundle Component Relationship"])
big = [f"B{i:03d}" for i in range(450)]
ft = FakeTransport(big, dup={"B004"}, dup_price={"B005"})
view = V.capture(ft, big)
check("Product2 lookups go 200 SKUs at a time", ft.soql_sizes, [200, 200, 50])
check("a SKU two products hold is reported, not captured", (view["duplicates"], "B004" in view["products"]),
      (["B004"], False))
check("a duplicated SKU is not also listed as missing", "B004" in view["missing"], False)
check("two entries for one model and currency are both kept", view["products"]["B005"]["listPrices"],
      {"One-Time;OneTime USD": [10, 12]})
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

print("main: exit 3 when PCM returns a filled field the tool doesn't cover")


class NovelTransport(FakeTransport):
    def connect(self, method, path, body):
        resp = super().connect(method, path, body)
        resp["products"][0]["brandNewField"] = "x"
        return resp


import tempfile
out = pathlib.Path(tempfile.mkdtemp()) / "view.json"
V.Transport = lambda *_a, **_k: NovelTransport(["N1"])
try:
    err = io.StringIO()
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
        code = V.main(["capture", "--target-org", "x@example.com", "--shape", "q3", "--sku", "N1", "--out", str(out)])
finally:
    V.Transport = saved
check("capture exits 3", code, 3)
check("names the uncovered field", "product.brandNewField" in err.getvalue(), True)
check("and still writes the capture", json.loads(out.read_text())["uncoveredFields"], ["product.brandNewField"])

print("=" * 60)
if _failures:
    print(f"FAIL: {len(_failures)} check(s) failed")
    sys.exit(1)
print("All checks passed")
