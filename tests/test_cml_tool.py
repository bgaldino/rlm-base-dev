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

    def soql(self, query):
        return [{"IsActive": True}]

    def sobject(self, method, sobject, record_id=None, body=None, **kw):
        self.calls.append((method, f"{sobject}/{record_id}", sorted(body)))
        return {}


def main():
    rep = cml_tool.size_report("a" * 600 + "é", 1000)  # é is two bytes
    assert rep["bytes"] == 602 and rep["percent"] == 60.2 and not rep["over"], rep
    assert cml_tool.size_report("a" * 11, 10)["over"]

    model = b'message("a & b", "x");'
    stored = {"text": model.decode()}
    cml_tool.read_model = lambda t, v: stored["text"]  # the blob read, stubbed offline
    t = FakeTransport()
    version = {"Id": "V", "ExpressionSetId": "E", "IsActive": True, "_esdv": "D"}
    cml_tool.push_model(t, version, model)
    order = [c[0] + " " + c[1] for c in t.calls]
    assert order == ["PATCH industries/constraints/E/versions/V",
                     "PATCH ExpressionSetDefinitionVersion/D",
                     "PATCH industries/constraints/E/versions/V"], order
    assert t.calls[0][2] == {"status": "Inactive"} and t.calls[2][2] == {"status": "Active"}

    # A deactivation answered 200 with success false must stop before the blob is written.
    class Refusing(FakeTransport):
        def connect(self, method, path, body=None, **kw):
            super().connect(method, path, body)
            return {"success": False}
    r = Refusing()
    try:
        cml_tool.push_model(r, version, model)
    except cml_tool.ExpressionSetClientError:
        pass
    else:
        raise AssertionError("failed deactivation accepted")
    assert len(r.calls) == 1, r.calls

    # A read that comes back HTML-escaped (the Connect GET does this) must fail the push.
    stored["text"] = model.decode().replace("&", "&amp;").replace('"', "&quot;")
    try:
        cml_tool.push_model(FakeTransport(), version, model)
    except cml_tool.ExpressionSetClientError:
        pass
    else:
        raise AssertionError("escaped read-back accepted")

    # The backup is written for an active version and never overwritten for an inactive one
    # (the rerun after a failed activation, when the stored blob is the bad new model).
    import tempfile
    prev = Path(tempfile.mkdtemp()) / "m.cml.previous"
    stored["text"] = "old model"
    assert cml_tool.save_previous(FakeTransport(), {"IsActive": True}, prev) == prev
    stored["text"] = "bad new model"
    assert cml_tool.save_previous(FakeTransport(), {"IsActive": False}, prev) is None
    assert prev.read_text() == "old model"

    # A full confirmed push: the backup holds the old text because the blob is read before the PATCH.
    import argparse
    class T(FakeTransport):
        def sobject(self, method, sobject, record_id=None, body=None, **kw):
            stored["text"] = model.decode()
            return super().sobject(method, sobject, record_id, body)
    stored["text"] = "old model"
    cml_tool.constraint_versions = lambda t, api=None: [
        {"Id": "V", "ExpressionSetId": "E", "ApiName": "A", "VersionNumber": 1, "IsActive": True}]
    cml_tool.esdv_id = lambda t, v: "D"
    mf = Path(tempfile.mkdtemp()) / "m.cml"
    mf.write_bytes(model)
    cml_tool.cmd_push(T(), argparse.Namespace(api_name="A", file=str(mf), limit=None, confirm=True))
    assert Path(str(mf) + ".previous").read_text() == "old model"

    # Org-unique identifiers carry the prefix, so a second scaffold with a new prefix does not collide.
    class Recording(FakeTransport):
        def sobject(self, method, sobject, record_id=None, body=None, **kw):
            self.calls.append((sobject, body))
            return {"success": True, "id": "X"}

        def soql(self, query):
            return [{"Id": "Y"}]
    rec = Recording()
    spec = {"prefix": "P 1", "attrs": [{"dev": "Size", "values": ["S"]}],
            "products": [{"name": "Kit", "tag": "Kit"}]}
    cml_tool._build(rec, spec, {"attrs": {}, "products": {}, "esc": {}}, "PB", "CTX", "PSM")
    body = {o: b for o, b in rec.calls}
    ad = body["AttributeDefinition"]
    assert (ad["Name"], ad["DeveloperName"], ad["Code"]) == ("P 1_Size", "P_1_Size", "P 1_Size"), ad
    assert body["Product2"]["ProductCode"] == "P 1_Kit", body["Product2"]

    for bad in ({},{"prefix": "p", "attrs": [{"dev": "A"}], "products": [{"name": "n", "tag": "t"}]}):
        try:
            cml_tool.validate_spec(bad)
        except cml_tool.ExpressionSetClientError:
            continue
        raise AssertionError(f"spec accepted: {bad}")
    print("test_cml_tool: ok")


if __name__ == "__main__":
    main()
