#!/usr/bin/env python3
"""Unit tests for scripts.context_service._delete.

Self-contained — no pytest (matches this repo's lightweight test convention; see
tests/test_context_apply.py). Run from the repo root with base Python:

    python tests/test_context_delete.py

Exits 0 when all checks pass, 1 otherwise.

Coverage (all offline — a fake transport, no org is touched):
  * ``plan_custom_teardown`` — refuses up front when a custom artifact has an
    **inherited** dependent (the platform will not remove it), mirroring the
    ``plan_target_deletion`` guard; and returns the ordered set when the teardown
    is clean.
  * ``execute`` — on a mid-list DELETE failure it attaches the partial-deleted
    list to the raised error (``partial_deleted``) so the operator is not blind
    to what a reverse-order teardown already removed.
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

import scripts.context_service._delete as _delete  # noqa: E402
import scripts.context_service._client as _client  # noqa: E402

RESULTS = []


def check(name, condition):
    RESULTS.append((name, bool(condition)))
    print(f"  [{'PASS' if condition else 'FAIL'}] {name}")


# --------------------------------------------------------------------------- #
# Fake transport — records DELETE paths, optionally raises on one of them
# --------------------------------------------------------------------------- #

class FakeTransport:
    """Minimal Transport stand-in for the deleter.

    ``fail_on`` — a substring of a DELETE path that should raise
    ``ContextClientError`` (simulating a mid-list platform failure). Every other
    DELETE is recorded and succeeds.
    """

    def __init__(self, fail_on=None, dry_run=False):
        self.dry_run = dry_run
        self.logger = lambda *a, **k: None
        self.deleted_paths = []
        self.fail_on = fail_on

    def request(self, method, path, body=None, *, dry_run=None):
        if method == "DELETE" and self.fail_on and self.fail_on in path:
            raise _client.ContextClientError(
                "simulated platform DELETE failure",
                error_codes=["RECORD_UPDATE_FAILED"],
            )
        self.deleted_paths.append(path)
        return {}


def _deleter(transport):
    return _delete.ContextDeleter(transport)


# --------------------------------------------------------------------------- #
# Catalog fixtures (flat artifact dicts, the shape build_artifact_catalog emits)
# --------------------------------------------------------------------------- #

def _art(kind, name, art_id, *, base=None, node_id=None, attr_id=None, depth=0,
         path=None):
    """One catalog artifact. ``base`` (baseReference) truthy => inherited."""
    return {
        "kind": kind, "name": name, "id": art_id, "baseReference": base,
        "depth": depth, "path": path or f"/{kind}/{art_id}",
        "context_node_id": node_id,
        "context_attribute_id": attr_id,
        "context_mapping_id": None,
        "context_node_mapping_id": None,
        "parent_context_node_id": None,
    }


def _catalog_custom_node_with_inherited_attr():
    """A custom node carrying an INHERITED attribute (the block case).

    The node itself is custom (deletable), but the attribute on it comes from the
    standard base — the platform will not remove it, so a child->parent teardown
    would fail mid-execute. plan_custom_teardown must refuse up front.
    """
    node = _art("node", "CustomNode", "11nCustom", base=None, node_id="11nCustom")
    inh_attr = _art("attribute", "CustomNode.InheritedAttr", "11aInh",
                    base="SalesTransactionContext__stdctx/v/InheritedAttr",
                    node_id="11nCustom", attr_id="11aInh")
    return [node, inh_attr]


def _catalog_all_custom():
    """A fully custom subtree — a custom node with a custom attribute + tag.
    Nothing inherited depends on the node, so the teardown is clean."""
    node = _art("node", "CustomNode", "11nCustom", base=None, node_id="11nCustom")
    attr = _art("attribute", "CustomNode.Attr__c", "11aC", base=None,
                node_id="11nCustom", attr_id="11aC")
    tag = _art("tag", "CustomNode.Attr__c:MyTag", "11tC", base=None,
               node_id="11nCustom", attr_id="11aC")
    return [node, attr, tag]


# --------------------------------------------------------------------------- #
# A3 — plan_custom_teardown inherited-dependent pre-flight
# --------------------------------------------------------------------------- #

def test_custom_teardown_refuses_inherited_dependent():
    catalog = _catalog_custom_node_with_inherited_attr()
    raised = False
    msg = ""
    try:
        _deleter(FakeTransport()).plan_custom_teardown(catalog)
    except _delete.DeletePreflightError as exc:
        raised = True
        msg = str(exc)
    check("custom teardown with an inherited dependent raises DeletePreflightError",
          raised)
    if raised:
        check("the refusal names the offending custom artifact",
              "CustomNode" in msg)
        check("the refusal names the inherited dependent",
              "InheritedAttr" in msg)
        check("the refusal explains the platform will not remove it",
              "inherited dependent" in msg)


def test_custom_teardown_clean_returns_ordered_set():
    catalog = _catalog_all_custom()
    ordered = _deleter(FakeTransport()).plan_custom_teardown(catalog)
    kinds = [a["kind"] for a in ordered]
    check("clean custom teardown returns every custom artifact", len(ordered) == 3)
    # DELETE_ORDER is child->parent: tag before attribute before node.
    check("teardown order is child->parent (tag < attribute < node)",
          kinds.index("tag") < kinds.index("attribute") < kinds.index("node"))


def test_custom_teardown_empty_catalog_is_empty():
    check("empty catalog -> empty teardown",
          _deleter(FakeTransport()).plan_custom_teardown([]) == [])


# --------------------------------------------------------------------------- #
# B3 — execute attaches partial_deleted on a mid-list failure
# --------------------------------------------------------------------------- #

def _ordered_three():
    return [
        _art("tag", "N.A:Tag", "11t1", path="/tag/11t1"),
        _art("attr-mapping", "N.A", "11am2", path="/attr-mapping/11am2"),
        _art("attribute", "N.A", "11a3", path="/attribute/11a3"),
    ]


def test_execute_attaches_partial_deleted_on_midlist_failure():
    # Fail on the SECOND artifact: the first must already be recorded as deleted,
    # and that partial list must ride out on the raised exception.
    t = FakeTransport(fail_on="/attr-mapping/")
    raised = False
    partial = None
    try:
        _deleter(t).execute(_ordered_three())
    except _client.ContextClientError as exc:
        raised = True
        partial = getattr(exc, "partial_deleted", None)
    check("a mid-list DELETE failure re-raises ContextClientError", raised)
    check("the first artifact was actually DELETEd before the failure",
          t.deleted_paths == ["/tag/11t1"])
    check("the raised error carries a partial_deleted list", isinstance(partial, list))
    if isinstance(partial, list):
        check("partial_deleted contains exactly the already-deleted artifact",
              len(partial) == 1 and partial[0]["id"] == "11t1")
        check("partial_deleted does NOT include the failed or later artifacts",
              all(p["id"] != "11am2" and p["id"] != "11a3" for p in partial))


def test_execute_failure_on_first_has_empty_partial():
    t = FakeTransport(fail_on="/tag/")
    partial = "unset"
    try:
        _deleter(t).execute(_ordered_three())
    except _client.ContextClientError as exc:
        partial = getattr(exc, "partial_deleted", "missing")
    check("failure on the very first artifact still attaches partial_deleted",
          isinstance(partial, list))
    check("partial_deleted is empty when nothing was deleted yet",
          partial == [])


def test_execute_success_deletes_all_in_order():
    t = FakeTransport()  # nothing fails
    summary = _deleter(t).execute(_ordered_three())
    check("clean execute reports the full deleted count", summary["count"] == 3)
    check("clean execute DELETEs every artifact in the given order",
          t.deleted_paths == ["/tag/11t1", "/attr-mapping/11am2", "/attribute/11a3"])


# --------------------------------------------------------------------------- #

def main():
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    print(f"Running {len(tests)} delete test groups...\n")
    for t in tests:
        t()
    print()
    passed = sum(1 for _, ok in RESULTS if ok)
    total = len(RESULTS)
    print(f"{passed}/{total} checks passed.")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
