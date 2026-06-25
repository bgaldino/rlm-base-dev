"""Unit tests for tasks/rlm_snapshot_dev_guide.py — the multi-section TOC walk.

Exercises `_flatten_toc` (and indirectly `_find_section`/`_node_page_id`) without
a browser or CumulusCI runtime: the method takes the TOC + section filters as
arguments and uses no task state, so an instance built with `__new__` suffices.

Run:  <cci-venv-python> tests/test_snapshot_dev_guide.py
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tasks.rlm_snapshot_dev_guide import SnapshotSalesforceDevGuide  # noqa: E402

try:
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:  # stdlib-only fallback mirrors the task module
    TaskOptionsError = Exception


_passed = _total = 0


def check(label, cond):
    global _passed, _total
    _total += 1
    if cond:
        _passed += 1
        print(f"  [PASS] {label}")
    else:
        print(f"  [FAIL] {label}")


def _node(title, href, children=None):
    return {"text": title, "a_attr": {"href": href}, "children": children or []}


TOC = [
    _node("Business Rules Engine", "business_rules_engine.htm", [
        _node("BRE Child 1", "bre_child1.htm"),
        _node("BRE Child 2", "bre_child2.htm"),
    ]),
    _node("Context Service", "context_service_overview.htm", [
        _node("Ctx Child", "ctx_child.htm"),
    ]),
    # A title containing commas — must be selectable by page_id.
    _node("Data Processing Engine, Batch Management, and Monitor Workflow Services",
          "batch.htm", [_node("Batch Child", "batch_child.htm")]),
    _node("Unrelated Cloud", "unrelated.htm", [_node("Noise", "noise.htm")]),
]


def _task():
    # _flatten_toc uses no self.options/state, so bypass CumulusCI __init__.
    return SnapshotSalesforceDevGuide.__new__(SnapshotSalesforceDevGuide)


def main():
    t = _task()

    # Multiple sections in one call (mix of page_id and title); comma-in-title
    # section is selected by page_id.
    pages = t._flatten_toc(TOC, ["business_rules_engine", "Context Service", "batch"])
    ids = {p["page_id"] for p in pages}
    check("multi-section captures all requested subtrees",
          ids == {"business_rules_engine.htm", "bre_child1.htm", "bre_child2.htm",
                  "context_service_overview.htm", "ctx_child.htm",
                  "batch.htm", "batch_child.htm"})
    check("multi-section excludes unrequested sections",
          "noise.htm" not in ids and "unrelated.htm" not in ids)
    by_id = {p["page_id"]: p for p in pages}
    check("BRE subtree labeled by its section title",
          by_id["bre_child1.htm"]["section"] == "Business Rules Engine")
    check("Context subtree labeled by its section title",
          by_id["ctx_child.htm"]["section"] == "Context Service")
    check("comma-in-title section (selected by page_id) keeps its full title",
          by_id["batch_child.htm"]["section"].startswith("Data Processing Engine,"))

    # Singular still works (one-element list).
    one = {p["page_id"] for p in t._flatten_toc(TOC, ["Context Service"])}
    check("single section still scopes correctly",
          one == {"context_service_overview.htm", "ctx_child.htm"})

    # None => whole guide.
    every = {p["page_id"] for p in t._flatten_toc(TOC, None)}
    check("None filter walks the whole guide", "noise.htm" in every)

    # Unknown section raises.
    try:
        t._flatten_toc(TOC, ["does_not_exist"])
        check("unknown section raises", False)
    except TaskOptionsError:
        check("unknown section raises TaskOptionsError", True)

    print(f"\n{_passed}/{_total} checks passed.")
    return 0 if _passed == _total else 1


if __name__ == "__main__":
    sys.exit(main())
