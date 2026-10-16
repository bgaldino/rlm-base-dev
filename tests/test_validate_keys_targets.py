#!/usr/bin/env python3
"""Offline tests for rlm_validate_keys.collect_key_target_objects.

Pins the per-declaration key-target collection: a multi-pass plan can declare the
same object with different all-direct externalIds in different passes (e.g. `Name`
in the top-level `objects` pass unshifted as pass 1, `Code` in an `objectSets` pass),
and every distinct key-field set must be validated — not collapsed to the first.
Stdlib-only; rlm_validate_keys falls back to `object` when cumulusci is absent.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tasks"))
import rlm_validate_keys as vk  # noqa: E402

_failures = []


def check(label, got, want):
    if got == want:
        print(f"  [PASS] {label}")
    else:
        print(f"  [FAIL] {label}: got {got!r}, want {want!r}")
        _failures.append(label)


def _obj(name, external_id):
    return {"query": f"SELECT Id FROM {name}", "externalId": external_id}


# --- collect_key_target_objects ---------------------------------------------
check("flat single-field key",
      vk.collect_key_target_objects({"objects": [_obj("Product2", "StockKeepingUnit")]}),
      {"Product2": [["StockKeepingUnit"]]})

check("composite all-direct key kept as one field-set",
      vk.collect_key_target_objects({"objects": [_obj("RateCard", "Name;Type")]}),
      {"RateCard": [["Name", "Type"]]})

# The regression fix: a both-array plan declaring the same object with a different
# direct key per pass must validate BOTH, in pass order (top-level objects unshifted
# as pass 1), not collapse to the first-seen declaration.
check("both-array: distinct per-pass keys both collected, top-level first",
      vk.collect_key_target_objects({
          "objectSets": [{"objects": [_obj("Foo", "Code")]}],
          "objects": [_obj("Foo", "Name")],
      }),
      {"Foo": [["Name"], ["Code"]]})

check("identical declarations across passes are de-duplicated",
      vk.collect_key_target_objects({
          "objectSets": [
              {"objects": [_obj("Baz", "Code")]},
              {"objects": [_obj("Baz", "Code")]},
          ],
      }),
      {"Baz": [["Code"]]})

check("lowercase/mixed-case 'from' is parsed via the shared parser (not skipped)",
      vk.collect_key_target_objects({"objects": [
          {"query": "select Id from Product2", "externalId": "StockKeepingUnit"}]}),
      {"Product2": [["StockKeepingUnit"]]})

check("non-string query does not raise (returns no target)",
      vk.collect_key_target_objects({"objects": [
          {"query": ["SELECT Id FROM X"], "externalId": "Code"}]}),
      {})

check("relationship-traversal externalId is skipped (validated via parent)",
      vk.collect_key_target_objects({
          "objects": [_obj("RateCardEntry", "Product.StockKeepingUnit;RateCard.Name")]
      }),
      {})

check("externalId of Id, empty, or excluded objects are not targets",
      vk.collect_key_target_objects({
          "objects": [
              _obj("A", "Id"),
              _obj("B", ""),
              {"query": "SELECT Id FROM C", "externalId": "Code", "excluded": True},
          ]
      }),
      {})

# round-7: `excluded` is read with JS truthiness — `[]`/`{}` are falsy in Python but
# truthy in JS, so SFDMU skips such a declaration and this collector must too (else it
# queries/populates keys for an object SFDMU never loads).
check("excluded: [] is JS-truthy -> skipped (not a target)",
      vk.collect_key_target_objects({"objects": [
          {"query": "SELECT Id FROM D", "externalId": "Code", "excluded": []}]}),
      {})
check("excluded: {} is JS-truthy -> skipped (not a target)",
      vk.collect_key_target_objects({"objects": [
          {"query": "SELECT Id FROM E", "externalId": "Code", "excluded": {}}]}),
      {})
check("excluded: 0 is JS-falsy -> still a target",
      vk.collect_key_target_objects({"objects": [
          {"query": "SELECT Id FROM F", "externalId": "Code", "excluded": 0}]}),
      {"F": [["Code"]]})

# round-7: a non-string externalId (hand-edited list/dict) is truthy but would raise on
# `.split(";")` — the top-level pass can now carry it, so it must be skipped, not crash.
check("non-string (list) externalId does not raise -> no target",
      vk.collect_key_target_objects({"objects": [
          {"query": "SELECT Id FROM G", "externalId": ["Code"]}]}),
      {})
check("non-string (dict) externalId does not raise -> no target",
      vk.collect_key_target_objects({"objects": [
          {"query": "SELECT Id FROM H", "externalId": {"f": "Code"}}]}),
      {})

# --- _validate_object / _populate_nulls: per-declaration populate gating ------
# These pin the round-5 fix: POPULATE_CONFIG is object-wide but targets one key
# field, so validating the same object on a different key must NOT populate the
# config's field (and clear the count) while the requested key stays null. Uses a
# minimal fake for `self.sf`/`self.logger` — the module falls back to `object` when
# cumulusci is absent, so ValidateSourceDataKeys is constructible via __new__.
class _NullLogger:
    def info(self, *a, **k):
        pass
    warning = error = info


class _FakeBulkObj:
    def __init__(self, recorder, obj):
        self._recorder, self._obj = recorder, obj

    def update(self, updates):
        self._recorder[self._obj] = updates
        return [{"success": True, "id": u["Id"]} for u in updates]


class _FakeBulk:
    def __init__(self, recorder):
        self._recorder = recorder

    def __getattr__(self, obj):
        return _FakeBulkObj(self._recorder, obj)


class _FakeSf:
    def __init__(self, records):
        self._records = records
        self.updated = {}
        self.bulk = _FakeBulk(self.updated)

    def query(self, soql):
        return {"records": self._records, "done": True}


def _make_task(records, options=None):
    t = vk.ValidateSourceDataKeys.__new__(vk.ValidateSourceDataKeys)
    t.options = options or {}
    t.logger = _NullLogger()
    t.sf = _FakeSf(records)
    return t


# Product2 keyed on ProductCode (not the config's StockKeepingUnit): SKU present,
# ProductCode null. The config must be gated off so ProductCode itself is populated
# and no issue is silently cleared by writing the wrong field.
_pc_task = _make_task([{"Id": "1", "Name": "Widget", "StockKeepingUnit": "SKU-1", "ProductCode": None}])
_pc_task._validate_object("Product2", ["ProductCode"], populate=True)
_written = _pc_task.sf.updated.get("Product2", [{}])[0]
check(f"ProductCode-keyed Product2 populates ProductCode, not StockKeepingUnit ({_written})",
      "ProductCode" in _written and "StockKeepingUnit" not in _written, True)

# Product2 keyed on StockKeepingUnit (the config's field): config applies, so the
# derived value is written to SKU and synced to ProductCode.
_sku_task = _make_task([{"Id": "1", "Name": "Widget", "StockKeepingUnit": None, "ProductCode": None}])
_sku_task._validate_object("Product2", ["StockKeepingUnit"], populate=True)
_w2 = _sku_task.sf.updated.get("Product2", [{}])[0]
check(f"StockKeepingUnit-keyed Product2 applies config (writes SKU + syncs ProductCode) ({_w2})",
      "StockKeepingUnit" in _w2 and "ProductCode" in _w2, True)

# Composite key with a null in a TRAILING component must still report the issue in
# populate mode (report-only), not silently return 0 (the finding-1 count bug).
_comp_task = _make_task([{"Id": "1", "Name": "Std", "Type": None}])
_comp_issues = _comp_task._validate_object("RateCard", ["Name", "Type"], populate=True)
check(f"composite key with a trailing-component null still reports an issue in populate mode ({_comp_issues})",
      _comp_issues >= 1, True)

print("=" * 60)
if _failures:
    print(f"FAILED ({len(_failures)}): {_failures}")
    sys.exit(1)
print("All checks passed")
