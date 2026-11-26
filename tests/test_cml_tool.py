#!/usr/bin/env python3
"""Offline test for scripts/constraint_models/cml_tool.py (no org, no sf CLI).

Run:  python tests/test_cml_tool.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.constraint_models import cml_tool  # noqa: E402


class FakeTransport:
    """Records every mutating call; answers the reads push_model never makes."""

    def __init__(self):
        self.calls = []

    def connect(self, method, path, body=None, **kw):
        self.calls.append((method, path, body))
        return {"success": True}

    def sobject(self, method, sobject, record_id=None, body=None, **kw):
        self.calls.append((method, f"{sobject}/{record_id}", sorted(body)))
        return {}


def main():
    rep = cml_tool.size_report("a" * 600 + "é", 1000)  # é is two bytes
    assert rep["bytes"] == 602 and rep["percent"] == 60.2 and not rep["over"], rep
    assert cml_tool.size_report("a" * 11, 10)["over"]

    t = FakeTransport()
    version = {"Id": "V", "ExpressionSetId": "E", "IsActive": True, "_esdv": "D"}
    cml_tool.push_model(t, version, b"type X : LineItem;")
    order = [c[0] + " " + c[1] for c in t.calls]
    assert order == ["PATCH industries/constraints/E/versions/V",
                     "PATCH ExpressionSetDefinitionVersion/D",
                     "PATCH industries/constraints/E/versions/V"], order
    assert t.calls[0][2] == {"status": "Inactive"} and t.calls[2][2] == {"status": "Active"}

    for bad in ({}, {"prefix": "p", "attrs": [{"dev": "A"}], "products": [{"name": "n", "tag": "t"}]}):
        try:
            cml_tool.validate_spec(bad)
        except SystemExit:
            continue
        raise AssertionError(f"spec accepted: {bad}")
    print("test_cml_tool: ok")


if __name__ == "__main__":
    main()
