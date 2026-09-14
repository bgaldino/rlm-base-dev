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

print("=" * 60)
if _failures:
    print(f"FAILED ({len(_failures)}): {_failures}")
    sys.exit(1)
print("All checks passed")
