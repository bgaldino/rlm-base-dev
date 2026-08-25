"""Unit tests for tasks/rlm_snapshot_dev_guide.py — the multi-section TOC walk.

Exercises `_flatten_toc` (and indirectly `_find_section`/`_node_page_id`) without
a browser or CumulusCI runtime: the method takes the TOC + section filters as
arguments and uses no task state, so an instance built with `__new__` suffices.

Run:  <cci-venv-python> tests/test_snapshot_dev_guide.py
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tasks.rlm_snapshot_dev_guide import (  # noqa: E402
    SnapshotSalesforceDevGuide,
    TaskOptionsError,
)

# TaskOptionsError comes from the module under test, not from CumulusCI, so the
# assertion always names the class the code will actually raise. The task binds
# BaseTask and TaskOptionsError in one try block, so a CumulusCI that imports
# but whose cumulusci.core.tasks does not (3.12+ without setuptools: fs needs
# pkg_resources) drops it to the fallback shim while a narrower import here
# would still resolve the real class — and every raise assertion would miss.


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

    # _select_to_capture restricts the capture set to the requested sections
    # (parallel multi-section path; filter given as page_id and as title).
    t2 = _task()
    t2.options = {"section_filters": ["business_rules_engine", "Context Service"]}
    manifest = {"pages": [
        {"page_id": "business_rules_engine.htm", "section": "Business Rules Engine", "status": "pending"},
        {"page_id": "bre_child1.htm", "section": "Business Rules Engine", "status": "pending"},
        {"page_id": "context_service_overview.htm", "section": "Context Service", "status": "captured"},
        {"page_id": "ctx_child.htm", "section": "Context Service", "status": "pending"},
        {"page_id": "noise.htm", "section": "Unrelated Cloud", "status": "pending"},
    ]}
    sel = {p["page_id"] for p in t2._select_to_capture(manifest, "all")}
    check("_select_to_capture keeps only requested sections (pending)",
          sel == {"business_rules_engine.htm", "bre_child1.htm", "ctx_child.htm"})
    check("_select_to_capture excludes unrequested sections", "noise.htm" not in sel)
    sel_refresh = {p["page_id"] for p in t2._select_to_capture(manifest, "refresh")}
    check("_select_to_capture refresh re-includes captured requested-section pages",
          "context_service_overview.htm" in sel_refresh and "noise.htm" not in sel_refresh)

    # _check_doc_version_change: a version bump on a manifest with captured pages
    # must be rejected under capture/all (they'd skip those pages and mislabel
    # them), allowed under refresh (recaptures everything), and allowed under
    # discover (never fetches page bodies).
    captured_manifest = {"pages": [
        {"page_id": "a.htm", "status": "captured"},
        {"page_id": "b.htm", "status": "pending"},
    ]}
    t3 = _task()
    t3.options = {"doc_version": "264.0"}
    for mode in ("capture", "all"):
        try:
            t3._check_doc_version_change(captured_manifest, "262.0", mode)
            check(f"doc_version change raises under mode={mode}", False)
        except TaskOptionsError:
            check(f"doc_version change raises under mode={mode}", True)
    for mode in ("refresh", "discover"):
        try:
            t3._check_doc_version_change(captured_manifest, "262.0", mode)
            check(f"doc_version change allowed under mode={mode}", True)
        except TaskOptionsError:
            check(f"doc_version change allowed under mode={mode}", False)
    # Same version requested, or nothing captured yet, or no prior version at
    # all (first-ever run): none of these are a "change", so never raise.
    check("same doc_version is not a change",
          t3._check_doc_version_change(captured_manifest, "264.0", "capture") is None)
    pending_only = {"pages": [{"page_id": "a.htm", "status": "pending"}]}
    check("no captured pages yet is not a mislabel risk",
          t3._check_doc_version_change(pending_only, "262.0", "capture") is None)
    check("no previously-recorded version is a first run, not a change",
          t3._check_doc_version_change(captured_manifest, None, "capture") is None)

    # _may_record_doc_version: discover must NOT launder a version bump past the
    # guard by writing it to the manifest while old-version pages sit captured —
    # that would make a later capture/all run see "no change" and skip them.
    check("discover defers recording a version bump over captured pages",
          t3._may_record_doc_version(captured_manifest, "262.0", "discover") is False)
    check("discover may record when nothing is captured yet",
          t3._may_record_doc_version(pending_only, "262.0", "discover") is True)
    check("discover may record the same version",
          t3._may_record_doc_version(captured_manifest, "264.0", "discover") is True)
    check("discover may record on a first-ever run",
          t3._may_record_doc_version(captured_manifest, None, "discover") is True)
    check("capture/all/refresh always record (guard already vetted them)",
          all(t3._may_record_doc_version(captured_manifest, "262.0", m)
              for m in ("capture", "all", "refresh")))

    print(f"\n{_passed}/{_total} checks passed.")
    return 0 if _passed == _total else 1


if __name__ == "__main__":
    sys.exit(main())
