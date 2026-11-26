#!/usr/bin/env python3
"""CML helper CLI: report model size, push a model, scaffold a test model.

Reuses the ``sf``-CLI transport of ``scripts/expression_sets`` (no access token is
handled). ``--target-org`` is the SF CLI alias or username, never the CCI alias.
Shipped models (``datasets/constraints/``) go through the CCI tasks
(``import_cml`` and ``prepare_constraints``); this tool is for everything else:
measuring a model, cycling a one-off model, and building a disposable catalog
plus constraint model for an experiment. Skill: ``.cursor/skills/constraint-models``.

    # byte length of every constraint model version (add --limit <bytes> for a share)
    python scripts/constraint_models/cml_tool.py size --target-org <sf_alias>

    # deactivate -> upload -> activate (preview unless --confirm)
    python scripts/constraint_models/cml_tool.py push --target-org <sf_alias> \
        --api-name <ExpressionSetApiName> --file model.cml --confirm

    # create classification, attributes, products, price book entries, the
    # constraint ExpressionSet and its Type associations from a JSON spec
    python scripts/constraint_models/cml_tool.py scaffold --target-org <sf_alias> \
        --spec scripts/constraint_models/example-spec.json --out ids.json --confirm
"""

import argparse
import base64
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.expression_sets._client import (  # noqa: E402
    ExpressionSetClientError,
    Transport,
    _run_sf,
    eprint,
    soql_literal,
)

# The save-size limit is an org value (it follows the Apex code size limit) and cannot be
# read from the org, so --limit is optional: without it only the byte count is reported.
DEFAULT_CONTEXT = "RLM_SalesTransactionContext"


def size_report(model_text, limit=None):
    """Return the byte length of a model and, given a limit, its share of it."""
    size = len((model_text or "").encode("utf-8"))
    rep = {"bytes": size, "limit": limit, "percent": None, "over": False}
    if limit:
        rep.update(percent=round(100.0 * size / limit, 3), over=size > limit)
    return rep


def fmt_size(rep):
    tail = f" = {rep['percent']}% of {rep['limit']:,}" if rep["limit"] else ""
    return f"{rep['bytes']:,} bytes{tail}" + ("  OVER LIMIT" if rep["over"] else "")


def constraint_versions(t, api_name=None):
    """Every constraint-model version: ExpressionSet id, version id, state."""
    where = "ExpressionSet.UsageType = 'Constraint'"
    if api_name:
        where += f" AND ExpressionSet.ApiName = '{soql_literal(api_name)}'"
    return t.soql(
        "SELECT Id, ApiName, VersionNumber, IsActive, ExpressionSetId, ExpressionSet.ApiName "
        f"FROM ExpressionSetVersion WHERE {where} ORDER BY ExpressionSet.ApiName, VersionNumber"
    )


def esdv_id(t, version):
    rows = t.soql("SELECT Id FROM ExpressionSetDefinitionVersion "
                  f"WHERE DeveloperName = '{soql_literal(version['ApiName'])}'")
    if not rows:
        raise SystemExit(f"no ExpressionSetDefinitionVersion {version['ApiName']}")
    return rows[0]["Id"]


def read_model(t, version):
    """Model text from the stored blob (ExpressionSetDefinitionVersion.ConstraintModel).

    Not the constraint-version Connect GET: that returns constraintModel HTML-escaped
    (quote -> &quot;, ampersand -> &amp;), so its length is wrong and writing it back
    breaks the model. The blob GET returns the raw text, which is not JSON, so it goes
    through the sf CLI directly.
    """
    path = (f"/services/data/v{t.api_version}/sobjects/ExpressionSetDefinitionVersion/"
            f"{esdv_id(t, version)}/ConstraintModel")
    res = _run_sf(["api", "request", "rest", path, "--target-org", t.target_org], timeout=120)
    if res.returncode != 0:
        raise ExpressionSetClientError(f"reading the model failed: {(res.stdout or res.stderr)[:300]}")
    # the CLI appends one newline to the printed body
    return res.stdout[:-1] if res.stdout.endswith("\n") else res.stdout


def cmd_size(t, args):
    rows = []
    for v in constraint_versions(t, args.api_name):
        rep = size_report(read_model(t, v), args.limit)
        rep.update(model=v["ExpressionSet"]["ApiName"], version=v["VersionNumber"], active=v["IsActive"])
        rows.append(rep)
    if args.json:
        print(json.dumps(rows, indent=2))
    for r in rows:
        if not args.json:
            print(f"{r['model']} v{r['version']} active={r['active']}: {fmt_size(r)}")
    return 1 if any(r["over"] for r in rows) else 0


def push_model(t, version, model_bytes):
    """Deactivate if active, store the model, activate. All through the resource."""
    path = f"industries/constraints/{version['ExpressionSetId']}/versions/{version['Id']}"
    if version["IsActive"]:
        t.connect("PATCH", path, {"status": "Inactive"})
    t.sobject("PATCH", "ExpressionSetDefinitionVersion", version["_esdv"],
              {"ConstraintModel": base64.b64encode(model_bytes).decode()})
    res = t.connect("PATCH", path, {"status": "Active"})
    if isinstance(res, dict) and res.get("success") is False:
        raise ExpressionSetClientError(f"activation reported failure: {json.dumps(res)[:400]}")
    # Read back: the stored blob must equal the file and the version must be active.
    stored = read_model(t, version)
    active = t.soql(f"SELECT IsActive FROM ExpressionSetVersion WHERE Id = '{version['Id']}'")
    if stored.strip() != model_bytes.decode("utf-8").strip():
        raise ExpressionSetClientError("stored model differs from the file after push")
    if not (active and active[0]["IsActive"]):
        raise ExpressionSetClientError("version is not active after push")


def cmd_push(t, args):
    versions = constraint_versions(t, args.api_name)
    if not versions:
        raise SystemExit(f"no constraint model named {args.api_name}")
    version = versions[-1]
    version["_esdv"] = esdv_id(t, version)
    data = Path(args.file).read_bytes()
    rep = size_report(data.decode("utf-8"), args.limit)
    eprint(f"{version['ApiName']}: {fmt_size(rep)}")
    if not args.confirm:
        eprint("preview only; add --confirm to deactivate, upload and activate")
        return 0
    push_model(t, version, data)
    print("pushed, read back identical, version active")
    return 0


def validate_spec(spec):
    for key in ("prefix", "attrs", "products"):
        if not spec.get(key):
            raise SystemExit(f"spec needs a non-empty '{key}'")
    for a in spec["attrs"]:
        if not a.get("dev") or not a.get("values"):
            raise SystemExit("each attr needs 'dev' and 'values'")
    for p in spec["products"]:
        if not p.get("name") or not p.get("tag"):
            raise SystemExit("each product needs 'name' and 'tag'")


def _one(t, soql, what):
    rows = t.soql(soql)
    if not rows:
        raise SystemExit(f"{what} not found")
    return rows[0]["Id"]


def _create(t, obj, rec):
    r = t.sobject("POST", obj, None, rec)
    if not (isinstance(r, dict) and r.get("success")):
        raise ExpressionSetClientError(f"create {obj} failed: {r}")
    return r["id"]


def cmd_scaffold(t, args):
    spec = json.loads(Path(args.spec).read_text())
    validate_spec(spec)
    if not args.confirm:
        eprint(f"preview: would create {len(spec['attrs'])} attributes, "
               f"{len(spec['products'])} products and one constraint set")
        return 0
    pre = spec["prefix"]
    pb = _one(t, "SELECT Id FROM Pricebook2 WHERE IsStandard = true", "standard price book")
    ctx = _one(t, f"SELECT Id FROM ContextDefinition WHERE DeveloperName = "
                  f"'{soql_literal(spec.get('context', DEFAULT_CONTEXT))}'", "context definition")
    psm_rows = t.soql("SELECT Id FROM ProductSellingModel WHERE SellingModelType = 'OneTime' "
                      "AND Status = 'Active' LIMIT 1")
    psm = psm_rows[0]["Id"] if psm_rows else _create(
        t, "ProductSellingModel",
        {"Name": f"{pre} One Time", "SellingModelType": "OneTime", "Status": "Active"})
    ids = {"attrs": {}, "products": {}, "esc": {}}
    cls = ids["classification"] = _create(t, "ProductClassification", {
        "Name": f"{pre} Class", "Code": f"{pre}_Class", "Status": "Active"})
    for a in spec["attrs"]:
        dev = a["dev"]
        pl = _create(t, "AttributePicklist", {"Name": f"{pre} {dev}", "DataType": "Text", "Status": "Active"})
        for i, v in enumerate(a["values"]):
            _create(t, "AttributePicklistValue", {
                "PicklistId": pl, "Name": v, "Value": v, "Code": f"{pre}_{dev}_{i}",
                "DisplayValue": v, "Status": "Active", "Sequence": i + 1})
        ad = _create(t, "AttributeDefinition", {
            "Name": dev, "Label": a.get("label", dev), "DeveloperName": dev, "DataType": "Picklist",
            "PicklistId": pl, "IsActive": True, "Code": dev})
        pca = {"Name": dev, "ProductClassificationId": cls, "AttributeDefinitionId": ad,
               "Status": "Active", "IsRequired": a.get("required", False), "Sequence": len(ids["attrs"]) + 1}
        if a.get("default"):
            pca["DefaultValue"] = a["default"]
        ids["attrs"][dev] = {"definition": ad, "classattr": _create(t, "ProductClassificationAttr", pca)}
    for p in spec["products"]:
        pid = _create(t, "Product2", {"Name": p["name"], "ProductCode": p["name"], "BasedOnId": cls,
                                      "Type": "Bundle", "ConfigureDuringSale": "Allowed", "IsActive": True})
        for a in spec["attrs"]:
            ov = p.get("overrides", {}).get(a["dev"], {})
            pad = {"Name": a["dev"], "Product2Id": pid,
                   "AttributeDefinitionId": ids["attrs"][a["dev"]]["definition"],
                   "ProductClassificationAttributeId": ids["attrs"][a["dev"]]["classattr"], "Status": "Active",
                   "IsRequired": ov.get("required", a.get("required", False))}
            d = ov.get("default", a.get("default"))
            if d:
                pad["DefaultValue"] = d
            _create(t, "ProductAttributeDefinition", pad)
        _create(t, "ProductSellingModelOption", {"Product2Id": pid, "ProductSellingModelId": psm})
        _create(t, "PricebookEntry", {"Product2Id": pid, "Pricebook2Id": pb, "UnitPrice": p.get("price", 100),
                                      "IsActive": True, "ProductSellingModelId": psm})
        ids["products"][p["name"]] = pid
    api = "CM_" + re.sub(r"[^A-Za-z0-9]+", "_", pre).strip("_")
    es = ids["expressionset"] = _create(t, "ExpressionSet", {
        "ApiName": api, "Name": f"{pre} CM", "UsageType": "Constraint",
        "InterfaceSourceType": "Constraint", "ResourceInitializationType": "Off"})
    esd = _one(t, f"SELECT Id FROM ExpressionSetDefinition WHERE DeveloperName = '{api}'", "definition")
    _create(t, "ExpressionSetDefinitionContextDefinition",
            {"ExpressionSetDefinitionId": esd, "ContextDefinitionId": ctx})
    for p in spec["products"]:
        ids["esc"][p["name"]] = _create(t, "ExpressionSetConstraintObj", {
            "ExpressionSetId": es, "ReferenceObjectId": ids["products"][p["name"]],
            "ConstraintModelTag": p["tag"], "ConstraintModelTagType": "Type"})
    if args.out:
        Path(args.out).write_text(json.dumps(ids, indent=1))
    print(json.dumps(ids, indent=1))
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn in (("size", cmd_size), ("push", cmd_push), ("scaffold", cmd_scaffold)):
        s = sub.add_parser(name)
        s.add_argument("--target-org", required=True, help="SF CLI alias or username")
        s.set_defaults(fn=fn)
        if name != "scaffold":
            s.add_argument("--api-name", required=(name == "push"), help="ExpressionSet ApiName")
            s.add_argument("--limit", type=int, default=None,
                           help="org's model size limit in bytes (not readable from the org; "
                                "without it only bytes are reported)")
        if name == "size":
            s.add_argument("--json", action="store_true")
        if name == "push":
            s.add_argument("--file", required=True)
        if name != "size":
            s.add_argument("--confirm", action="store_true", help="write to the org")
        if name == "scaffold":
            s.add_argument("--spec", required=True)
            s.add_argument("--out", help="write created ids to this JSON file")
    args = p.parse_args(argv)
    try:
        return args.fn(Transport(args.target_org), args)
    except ExpressionSetClientError as exc:
        eprint(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
