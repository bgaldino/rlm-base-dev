#!/usr/bin/env python3
"""Offline unit tests for the self-contained ``scripts/decision_tables/`` toolkit.

No org, no ``sf`` CLI, no pytest — a plain ``check()`` runner matching the style
of ``tests/test_expression_sets_toolkit.py``. Exercises the package's pure logic:

- ``_schema`` — enum catalogs, key prefixes, field-name divergence map, and the
  canonical-spec validator (``validate_spec``).
- ``_resolve`` — the Tooling SOQL query builders (via a fake transport that
  records the queries it is asked to run) and definition assembly.
- ``diff_decision_tables.diff_definitions`` — the pure structural diff.
- ``dump_decision_table_data.dump_data`` — the ``dataSourceType`` branch logic.
- ``trace_decision_table.trace_recipe_mappings`` — the LookupTableId /
  FileBasedDecisionTableName correlation.
- CLI argparse wiring + JSON formatting through the fake transport.

These are independent of the CCI tasks' suites — this file tests
``scripts/decision_tables/`` only.

Run:  python tests/test_decision_tables_toolkit.py
Exit: 0 = all pass, 1 = one or more failures.
"""

import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.decision_tables import _payload  # noqa: E402
from scripts.decision_tables import _resolve  # noqa: E402
from scripts.decision_tables import _schema  # noqa: E402
from scripts.decision_tables._client import DecisionTableClientError  # noqa: E402
from scripts.decision_tables._lifecycle import LifecycleEngine, LifecycleError  # noqa: E402
from scripts.decision_tables._schema import validate_spec  # noqa: E402
from scripts.decision_tables.diff_decision_tables import diff_definitions  # noqa: E402
from scripts.decision_tables.dump_decision_table_data import dump_data  # noqa: E402
from scripts.decision_tables.trace_decision_table import trace_recipe_mappings  # noqa: E402
import scripts.decision_tables.list_decision_tables as list_cli  # noqa: E402
import scripts.decision_tables.describe_decision_table as describe_cli  # noqa: E402
import scripts.decision_tables.trace_decision_table as trace_cli  # noqa: E402
import scripts.decision_tables.create_decision_table as create_cli  # noqa: E402
import scripts.decision_tables.update_decision_table as update_cli  # noqa: E402
import scripts.decision_tables.activate_decision_table as activate_cli  # noqa: E402
import scripts.decision_tables.deactivate_decision_table as deactivate_cli  # noqa: E402
import scripts.decision_tables.refresh_decision_table as refresh_cli  # noqa: E402
import scripts.decision_tables.delete_decision_table as delete_cli  # noqa: E402

# Shipped source-format table used as the byte-identical round-trip fixture for
# the Metadata XML serializer.
_SHIPPED_XML = (Path(__file__).resolve().parents[1]
                / "unpackaged" / "pre" / "5_decisiontables"
                / "RLM_CostBookEntries.decisionTable-meta.xml")

_PASS = 0
_FAIL = 0


def check(label, condition, detail=""):
    global _PASS, _FAIL
    if condition:
        _PASS += 1
    else:
        _FAIL += 1
        print(f"  FAIL: {label}" + (f"  ({detail})" if detail else ""))


# --------------------------------------------------------------------------- #
# Fixtures + a fake transport that routes queries by content.
# --------------------------------------------------------------------------- #

def _sample_metadata(**over):
    meta = {
        "dataSourceType": "SingleSobject",
        "executionType": "HBASE",
        "filterResultBy": "OutputOrder",
        "type": "MediumVolume",
        "conditionType": "All",
        "conditionCriteria": "1",
        "dtRowLevelOverrideType": "None",
        "sourceObject": "CostBookEntry",
    }
    meta.update(over)
    return meta


def _table_row(name="RLM_CostBookEntries", **over):
    row = {
        "Id": "0lDxx0000000001AAA", "DeveloperName": name, "MasterLabel": name,
        "Status": "Active", "UsageType": "DefaultPricing",
        "SourceObject": "CostBookEntry", "LastSyncDate": "2026-07-01T00:00:00.000Z",
    }
    row.update(over)
    return row


def _param(usage, field_name, **over):
    p = {"Id": f"0lPxx{field_name}", "DecisionTableId": "0lDxx0000000001AAA",
         "FieldName": field_name, "FieldPath": field_name, "Usage": usage,
         "Operator": "Equals" if usage == "INPUT" else None,
         "Sequence": 1 if usage == "INPUT" else None,
         "DataType": "String", "IsRequired": usage == "INPUT",
         "IsGroupByField": False, "SortType": None, "DomainObject": None}
    p.update(over)
    return p


class _FakeTransport:
    """Duck-types _client.Transport; routes tooling_query / soql / tooling_sobject
    / connect / connect_get by content. Records the queries it was asked to run.

    Mirrors the real transport's dry-run contract: when ``dry_run`` is set, a
    **mutating** verb (anything but GET/HEAD) is logged+skipped and NOT appended to
    ``self.mutations`` — reads always execute. A confirmed (``dry_run=False``)
    mutating verb is executed and recorded. A confirmed Tooling ``DecisionTable``
    PATCH that carries ``Metadata.status`` also updates ``self.table['Status']`` so
    ``wait_for_status`` resolves on the first poll (no ``time.sleep``)."""

    def __init__(self, *, table=None, params=None, links=None, dataset_params=None,
                 criteria=None, mappings=None, source_rows=None, connect_def=None,
                 dry_run=False):
        self.table = table if table is not None else _table_row()
        self.params = params if params is not None else [
            _param("INPUT", "ProductId"), _param("OUTPUT", "Cost", DataType="Currency")]
        self.links = links or []
        self.dataset_params = dataset_params or []
        self.criteria = criteria or []
        self.mappings = mappings or []
        self.source_rows = source_rows if source_rows is not None else [{"Id": "01txx", "Cost": 5}]
        self.connect_def = connect_def
        self.dry_run = dry_run
        self.api_version = "67.0"
        self.target_org = "fake-org"
        self.logger = lambda *a, **k: None
        self.tooling_queries = []
        self.soql_queries = []
        self.mutations = []  # (method, target, body) for EXECUTED mutating verbs

    def _skip_mutation(self, method, target, body):
        """Mirror the real transport: skip+return True under dry-run; else record."""
        if method.upper() in ("GET", "HEAD"):
            return False
        if self.dry_run:
            return True
        self.mutations.append((method.upper(), target, body))
        return False

    def tooling_query(self, query):
        self.tooling_queries.append(query)
        if "FROM DecisionTableParameter" in query:
            return list(self.params)
        if "FROM DecisionTableDatasetLink" in query:
            return list(self.links)
        if "FROM DecisionTblDatasetParameter" in query:
            return list(self.dataset_params)
        if "FROM DecisionTableSourceCriteria" in query:
            return list(self.criteria)
        if "FROM DecisionTable" in query:
            return [self.table]
        return []

    def tooling_sobject(self, method, sobject, record_id=None, suffix=None, body=None, **kw):
        if method.upper() == "GET" and sobject == "DecisionTable":
            return dict(self.table, Metadata=_sample_metadata())
        if self._skip_mutation(method, f"tooling/{sobject}", body):
            return {}
        # Reflect a Status transition so wait_for_status resolves without sleeping.
        if (method.upper() == "PATCH" and sobject == "DecisionTable"
                and isinstance(body, dict) and isinstance(body.get("Metadata"), dict)
                and body["Metadata"].get("status")):
            self.table = dict(self.table, Status=body["Metadata"]["status"])
        if method.upper() == "POST" and sobject == "DecisionTable":
            return {"id": "0lDxx0000000009AAA", "success": True}
        return {}

    def connect(self, method, path, body=None, **kw):
        if method.upper() in ("GET", "HEAD"):
            return self.connect_get(path)
        if self._skip_mutation(method, path, body):
            return {}
        if path.endswith("refreshDecisionTable"):
            return [{"isSuccess": True, "outputValues": {"Status": "Queued"}}]
        return {}

    def connect_get(self, path):
        return {"code": "200", "decisionTable": self.connect_def or {
            "id": "0lDxx0000000001", "sourceType": "SingleSobject",
            "decisionResultPolicy": "OutputOrder", "parameters": [{}, {}],
            "sourceCriteria": [], "rowLevelOverrideType": "None"}}

    def soql(self, query):
        self.soql_queries.append(query)
        if "FROM PricingRecipeTableMapping" in query:
            return list(self.mappings)
        return list(self.source_rows)


class _LifecycleFake:
    """Minimal transport for exercising LifecycleEngine status transitions with a
    real (non-dry-run) engine but no ``time.sleep``.

    Holds a mutable ``status``; a Tooling PATCH of ``Metadata.status`` updates it
    and records the transition, and the ``get_status`` Tooling query reads it back
    — so ``wait_for_status`` matches on the first poll (waited=0, before any
    sleep). ``connect`` records DELETE/POST verbs for the delete/refresh paths."""

    def __init__(self, status="Active", *, dry_run=False):
        self.status = status
        self.dry_run = dry_run
        self.api_version = "67.0"
        self.target_org = "fake-org"
        self.logger = lambda *a, **k: None
        self.status_sets = []  # ordered list of statuses PATCHed
        self.connect_calls = []

    def tooling_query(self, query):
        if "FROM DecisionTable" in query:
            return [{"Id": "0lDxx0000000001AAA", "Status": self.status}]
        return []

    def tooling_sobject(self, method, sobject, record_id=None, suffix=None, body=None, **kw):
        if method.upper() == "GET":
            return {"Id": record_id, "Metadata": _sample_metadata(status=self.status)}
        if method.upper() == "PATCH" and isinstance(body, dict):
            new = body.get("Metadata", {}).get("status")
            if new:
                self.status = new
                self.status_sets.append(new)
        return {}

    def connect(self, method, path, body=None, **kw):
        if method.upper() not in ("GET", "HEAD"):
            self.connect_calls.append((method.upper(), path, body))
        # Mirror the real transport: the refreshDecisionTable action returns an
        # invocable-action envelope carrying outputValues.Status="Queued".
        if path.endswith("refreshDecisionTable"):
            return [{"isSuccess": True, "outputValues": {"Status": "Queued"}}]
        return {}


# --------------------------------------------------------------------------- #
# _schema — enums, prefixes, divergence map, validator
# --------------------------------------------------------------------------- #

def test_schema_catalogs():
    print("test_schema_catalogs")
    check("5 setup-object prefixes", len(_schema.SETUP_OBJECT_PREFIXES) == 5,
          _schema.SETUP_OBJECT_PREFIXES)
    check("DecisionTable prefix 0lD", _schema.SETUP_OBJECT_PREFIXES["DecisionTable"] == "0lD")
    check("SourceCriteria prefix 0VT",
          _schema.SETUP_OBJECT_PREFIXES["DecisionTableSourceCriteria"] == "0VT")
    check("dataSourceType has SingleSobject", "SingleSobject" in _schema.DATA_SOURCE_TYPES)
    check("executionType accepts both HBASE casings",
          {"HBASE", "Hbase"} <= _schema.EXECUTION_TYPES)
    check("DLO in executionType (v67 replaces DMO)", "DLO" in _schema.EXECUTION_TYPES)
    check("param usage upper set", _schema.PARAM_USAGE == {"INPUT", "OUTPUT", "ROWCRITERIA"})
    check("param usage connect title-case", "Input" in _schema.PARAM_USAGE_CONNECT)
    # Field-name divergence map — the concept keys and both per-path names.
    fm = _schema.FIELD_NAME_MAP
    check("divergence: data_source", fm["data_source"] == ("dataSourceType", "sourceType"))
    check("divergence: hit_policy", fm["hit_policy"] == ("filterResultBy", "decisionResultPolicy"))
    check("divergence: columns", fm["columns"] == ("decisionTableParameters", "parameters"))


def test_validate_spec_clean():
    print("test_validate_spec_clean")
    spec = {
        "fullName": "RLM_CostBookEntries", "setupName": "Cost Book Entries",
        "dataSourceType": "SingleSobject", "sourceObject": "CostBookEntry",
        "executionType": "Hbase", "filterResultBy": "OutputOrder",
        "conditionType": "All", "type": "MediumVolume", "usageType": "DefaultPricing",
        "decisionTableParameters": [
            {"usage": "INPUT", "fieldName": "ProductId", "dataType": "String",
             "operator": "Equals", "sequence": 1, "fieldPath": "ProductId", "isRequired": True},
            {"usage": "OUTPUT", "fieldName": "Cost", "dataType": "Currency"},
        ],
        "decisionTableSourceCriterias": [
            {"sourceFieldName": "UsageType", "operator": "Equals",
             "value": "Pricing", "valueType": "Literal", "sequenceNumber": 1},
        ],
    }
    result = validate_spec(spec)
    check("clean spec passes", result.passed, result.format_report())
    check("clean spec has no errors", not result.errors, result.format_report())


def test_validate_spec_errors():
    print("test_validate_spec_errors")
    # Missing name, source type, output column, and sourceObject for a Sobject type.
    result = validate_spec({
        "dataSourceType": "SingleSobject",
        "filterResultBy": "OutputOrder",
        "decisionTableParameters": [
            {"usage": "INPUT", "fieldName": "ProductId", "dataType": "String",
             "operator": "Equals", "sequence": 1}],
    })
    check("missing fullName errors", any("fullName" in i.location for i in result.errors))
    check("missing setupName errors", any("setupName" in i.location for i in result.errors))
    check("missing sourceObject errors", any("sourceObject" in i.location for i in result.errors))
    check("no OUTPUT column errors",
          any(i.location == "decisionTableParameters" and "OUTPUT" in i.message
              for i in result.errors))
    check("overall fails", not result.passed)


def test_validate_spec_duplicate_and_unknown():
    print("test_validate_spec_duplicate_and_unknown")
    result = validate_spec({
        "fullName": "X", "setupName": "X", "dataSourceType": "SingleSobject",
        "sourceObject": "CostBookEntry", "filterResultBy": "OutputOrder",
        "usageType": "TotallyMadeUp",  # unknown → warn, not error
        "decisionTableParameters": [
            {"usage": "INPUT", "fieldName": "ProductId", "dataType": "String",
             "operator": "Equals", "sequence": 1},
            {"usage": "INPUT", "fieldName": "ProductId", "dataType": "String",
             "operator": "Equals", "sequence": 2},  # duplicate key
            {"usage": "OUTPUT", "fieldName": "Cost", "dataType": "Currency"},
        ],
    })
    check("duplicate column errors",
          any("duplicate" in i.message for i in result.errors), result.format_report())
    check("unknown usageType warns (not errors)",
          any("TotallyMadeUp" in i.message for i in result.warnings)
          and not any("usageType" in i.location for i in result.errors))


# --------------------------------------------------------------------------- #
# _resolve — query builders + definition assembly (fake transport)
# --------------------------------------------------------------------------- #

def test_resolve_query_builders():
    print("test_resolve_query_builders")
    t = _FakeTransport()
    rows = _resolve.list_decision_tables(t, status="Active", usage_type="DefaultPricing",
                                         developer_name="A,B", limit=10)
    q = t.tooling_queries[-1]
    check("list queries DecisionTable", "FROM DecisionTable" in q, q)
    check("list applies status filter", "Status = 'Active'" in q, q)
    check("list applies usageType filter", "UsageType = 'DefaultPricing'" in q, q)
    check("list applies IN clause for names", "DeveloperName IN ('A', 'B')" in q, q)
    check("list applies limit", "LIMIT 10" in q, q)
    check("list returns rows", len(rows) == 1)


def test_resolve_missing_raises():
    print("test_resolve_missing_raises")
    t = _FakeTransport(table=None)
    t.table = None
    # tooling_query returns [] for DecisionTable when table is None
    t.tooling_query = lambda q: []
    try:
        _resolve.resolve_decision_table(t, "Nope")
        check("resolve raises on missing", False, "no exception")
    except _resolve.ResolveError:
        check("resolve raises on missing", True)


def test_load_definition_assembly():
    print("test_load_definition_assembly")
    t = _FakeTransport(
        criteria=[{"Id": "0VTxx", "SourceFieldName": "UsageType", "Operator": "Equals",
                   "Value": "Pricing", "ValueType": "Literal", "SequenceNumber": 1}])
    defn = _resolve.load_definition(t, "RLM_CostBookEntries")
    check("definition has table", defn["table"]["DeveloperName"] == "RLM_CostBookEntries")
    check("definition inlines metadata", defn["metadata"]["dataSourceType"] == "SingleSobject")
    check("definition has 2 columns", len(defn["parameters"]) == 2)
    check("definition has 1 criterion", len(defn["sourceCriteria"]) == 1)
    # The parameter query filters on the resolved table id.
    param_q = [q for q in t.tooling_queries if "FROM DecisionTableParameter" in q][0]
    check("param query filters on DecisionTableId",
          "DecisionTableId = '0lDxx0000000001AAA'" in param_q, param_q)


def test_connect_definition_unwrap():
    print("test_connect_definition_unwrap")
    t = _FakeTransport()
    cdef = _resolve.get_connect_definition(t, "0lDxx0000000001AAA")
    check("connect def unwrapped from envelope", cdef.get("sourceType") == "SingleSobject", cdef)


# --------------------------------------------------------------------------- #
# diff_definitions — pure structural diff
# --------------------------------------------------------------------------- #

def test_diff_identical():
    print("test_diff_identical")
    t = _FakeTransport()
    a = _resolve.load_definition(t, "RLM_CostBookEntries")
    b = _resolve.load_definition(t, "RLM_CostBookEntries")
    delta = diff_definitions(a, b)
    check("identical → empty attributes", not delta["attributes"], delta)
    check("identical → no column changes", not any(delta["columns"].values()), delta)


def test_diff_detects_changes():
    print("test_diff_detects_changes")
    a = {"table": _table_row(Status="Active"), "metadata": _sample_metadata(),
         "parameters": [_param("INPUT", "ProductId"), _param("OUTPUT", "Cost", DataType="Currency")],
         "datasetLinks": [], "datasetParameters": [], "sourceCriteria": []}
    b = {"table": _table_row(Status="Inactive"),
         "metadata": _sample_metadata(filterResultBy="Priority"),
         "parameters": [_param("INPUT", "ProductId", DataType="Number"),  # changed dataType
                        _param("OUTPUT", "Margin", DataType="Percent")],   # ProductId→Cost swap
         "datasetLinks": [], "datasetParameters": [], "sourceCriteria": []}
    delta = diff_definitions(a, b)
    check("detects Status change", delta["attributes"].get("Status") ==
          {"a": "Active", "b": "Inactive"}, delta["attributes"])
    check("detects hitPolicy change", "filterResultBy" in delta["attributes"])
    check("detects removed column (OUTPUT:Cost)", "OUTPUT:Cost" in delta["columns"]["removed"])
    check("detects added column (OUTPUT:Margin)", "OUTPUT:Margin" in delta["columns"]["added"])
    check("detects changed column (INPUT:ProductId dataType)",
          any(c["column"] == "INPUT:ProductId" and "dataType" in c["fields"]
              for c in delta["columns"]["changed"]), delta["columns"]["changed"])


# --------------------------------------------------------------------------- #
# dump_data — dataSourceType branch logic
# --------------------------------------------------------------------------- #

def test_dump_single_sobject():
    print("test_dump_single_sobject")
    t = _FakeTransport(source_rows=[{"Id": "01t1", "Cost": 5}, {"Id": "01t2", "Cost": 7}])
    defn = _resolve.load_definition(t, "RLM_CostBookEntries")
    dump = dump_data(t, defn, limit=5)
    check("single-sobject samples sourceObject", "CostBookEntry" in dump["samples"])
    check("single-sobject sample rows", len(dump["samples"]["CostBookEntry"]) == 2)
    q = [q for q in t.soql_queries if "FROM CostBookEntry" in q][0]
    check("projection includes a definition field", "Cost" in q, q)


def test_dump_csv_not_applicable():
    print("test_dump_csv_not_applicable")
    t = _FakeTransport()
    defn = _resolve.load_definition(t, "RLM_CostBookEntries")
    defn["metadata"]["dataSourceType"] = "CsvUpload"
    dump = dump_data(t, defn, limit=5)
    check("csv branch reports NOT APPLICABLE",
          any("NOT APPLICABLE" in n for n in dump["notes"]), dump["notes"])
    check("csv branch samples nothing", not dump["samples"], dump["samples"])


def test_dump_empty_source_note():
    print("test_dump_empty_source_note")
    t = _FakeTransport(source_rows=[])
    defn = _resolve.load_definition(t, "RLM_CostBookEntries")
    dump = dump_data(t, defn, limit=5)
    check("empty source noted", any("0 rows" in n for n in dump["notes"]), dump["notes"])


# --------------------------------------------------------------------------- #
# trace — LookupTableId / FileBasedDecisionTableName correlation
# --------------------------------------------------------------------------- #

def test_trace_correlation():
    print("test_trace_correlation")
    t = _FakeTransport(mappings=[
        {"Id": "m1", "PricingRecipeId": "recipe1", "PricingComponentType": "ListPrice",
         "LookupTableId": "0lDxx0000000001AAA", "IsInternal": False,
         "FileBasedDecisionTableName": None}])
    table = _resolve.resolve_decision_table(t, "RLM_CostBookEntries")
    mappings = trace_recipe_mappings(t, table)
    q = t.soql_queries[-1]
    check("trace queries PricingRecipeTableMapping", "FROM PricingRecipeTableMapping" in q, q)
    check("trace matches on LookupTableId (18-char)", "0lDxx0000000001AAA" in q, q)
    check("trace also matches 15-char id", "0lDxx0000000001" in q, q)
    check("trace matches FileBasedDecisionTableName", "FileBasedDecisionTableName" in q, q)
    check("trace returns the mapping", len(mappings) == 1)


# --------------------------------------------------------------------------- #
# CLI wiring — argparse + JSON output via the fake transport (no org)
# --------------------------------------------------------------------------- #

def _run_cli_with_fake(module, argv, fake):
    """Run a CLI's main() with its Transport swapped for a fake; capture stdout."""
    orig = module.Transport
    module.Transport = lambda *a, **k: fake
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            rc = module.main(argv)
    finally:
        module.Transport = orig
    return rc, buf.getvalue()


def test_list_cli_json():
    print("test_list_cli_json")
    fake = _FakeTransport()
    rc, out = _run_cli_with_fake(
        list_cli, ["--target-org", "x", "--json"], fake)
    check("list --json exits 0", rc == 0, rc)
    data = json.loads(out)
    check("list --json emits the table row",
          data and data[0]["DeveloperName"] == "RLM_CostBookEntries", data)


def test_describe_cli_grouped():
    print("test_describe_cli_grouped")
    fake = _FakeTransport()
    rc, out = _run_cli_with_fake(
        describe_cli, ["--target-org", "x", "--developer-name", "RLM_CostBookEntries"], fake)
    check("describe exits 0", rc == 0, rc)
    check("describe groups INPUT columns", "INPUT:" in out or "INPUT" in out, out[:200])
    check("describe shows the source object", "CostBookEntry" in out, out[:200])


def test_trace_cli_json():
    print("test_trace_cli_json")
    fake = _FakeTransport(mappings=[
        {"Id": "m1", "PricingRecipeId": "recipe1", "PricingComponentType": "ListPrice",
         "LookupTableId": "0lDxx0000000001AAA", "IsInternal": False,
         "FileBasedDecisionTableName": None}])
    rc, out = _run_cli_with_fake(
        trace_cli, ["--target-org", "x", "--developer-name", "RLM_CostBookEntries", "--json"], fake)
    check("trace --json exits 0", rc == 0, rc)
    data = json.loads(out)
    check("trace --json includes mappings", len(data.get("mappings", [])) == 1, data)


# --------------------------------------------------------------------------- #
# _payload — the three canonical-spec → per-path translators + XML round-trip
# --------------------------------------------------------------------------- #

def _cost_book_spec(**over):
    """The canonical spec mirroring the shipped RLM_CostBookEntries table."""
    spec = {
        "fullName": "RLM_CostBookEntries", "setupName": "Cost Book Entries",
        "dataSourceType": "SingleSobject", "sourceObject": "CostBookEntry",
        "executionType": "Hbase", "filterResultBy": "OutputOrder",
        "conditionType": "All", "type": "MediumVolume", "usageType": "DefaultPricing",
        "status": "Active",
        "decisionTableParameters": [
            {"usage": "INPUT", "fieldName": "ProductId", "dataType": "String",
             "operator": "Equals", "sequence": 1, "isRequired": True},
            {"usage": "OUTPUT", "fieldName": "Cost", "dataType": "String"},
        ],
    }
    spec.update(over)
    return spec


def test_translator_metadata():
    print("test_translator_metadata")
    body = _payload.to_metadata(_cost_book_spec())
    check("metadata keeps dataSourceType name", body["dataSourceType"] == "SingleSobject")
    check("metadata keeps filterResultBy name", body["filterResultBy"] == "OutputOrder")
    check("metadata does NOT emit fullName", "fullName" not in body)
    check("metadata synthesizes conditionCriteria from INPUT seq",
          body.get("conditionCriteria") == "1", body.get("conditionCriteria"))
    check("metadata always emits the 3 default bools",
          {"doesConsiderNullValue", "hasIncrementalSyncFailed",
           "isIncrementalSyncEnabled"} <= set(body))
    cols = body["decisionTableParameters"]
    inp = [c for c in cols if c["usage"] == "INPUT"][0]
    out = [c for c in cols if c["usage"] == "OUTPUT"][0]
    check("metadata INPUT column keeps operator+sequence",
          inp.get("operator") == "Equals" and inp.get("sequence") == 1)
    check("metadata OUTPUT column drops operator+sequence",
          "operator" not in out and "sequence" not in out)
    check("metadata usage stays UPPER-case", inp["usage"] == "INPUT")


def test_translator_tooling():
    print("test_translator_tooling")
    body = _payload.to_tooling(_cost_book_spec())
    check("tooling wraps FullName", body.get("FullName") == "RLM_CostBookEntries")
    check("tooling nests Metadata body", isinstance(body.get("Metadata"), dict))
    check("tooling Metadata carries columns",
          len(body["Metadata"]["decisionTableParameters"]) == 2)
    patch = _payload.tooling_metadata_only(_cost_book_spec())
    check("tooling PATCH body omits FullName (id in URL)", "FullName" not in patch)
    check("tooling PATCH body is Metadata-only", set(patch) == {"Metadata"})
    # A real Tooling Metadata PATCH REQUIRES status (a status-free body is rejected
    # with FIELD_INTEGRITY_EXCEPTION), so the caller stamps the table's CURRENT LIVE
    # status. The spec's own status is always dropped first, so live_status — never
    # the spec's — is what lands. (_cost_book_spec()'s own status is "Active".)
    spec_active = _cost_book_spec()
    live = _payload.tooling_metadata_only(spec_active, live_status="Inactive")
    check("tooling PATCH stamps the passed live status",
          live["Metadata"].get("status") == "Inactive", live["Metadata"].get("status"))
    check("tooling PATCH never carries the spec's own status",
          live["Metadata"].get("status") != spec_active["status"])


def test_translator_connect():
    print("test_translator_connect")
    body = _payload.to_connect(_cost_book_spec())
    check("connect renames dataSourceType→sourceType",
          body.get("sourceType") == "SingleSobject" and "dataSourceType" not in body)
    check("connect renames filterResultBy→decisionResultPolicy",
          body.get("decisionResultPolicy") == "OutputOrder" and "filterResultBy" not in body)
    check("connect renames decisionTableParameters→parameters",
          "parameters" in body and "decisionTableParameters" not in body)
    check("connect requires status (passed through)", body.get("status") == "Active")
    inp = [c for c in body["parameters"] if c["usage"] == "Input"][0]
    check("connect title-cases usage (INPUT→Input)", inp["usage"] == "Input")
    check("connect adds columnMapping per column", inp.get("columnMapping") == "ProductId")
    # status defaulting when the spec omits it
    spec = _cost_book_spec()
    del spec["status"]
    check("connect defaults missing status to Draft",
          _payload.to_connect(spec)["status"] == "Draft")


def test_metadata_xml_roundtrip():
    print("test_metadata_xml_roundtrip")
    produced = _payload.to_metadata_xml(_cost_book_spec())
    shipped = _SHIPPED_XML.read_text(encoding="utf-8")
    check("to_metadata_xml is byte-identical to the shipped source XML",
          produced == shipped,
          "produced XML diverged from RLM_CostBookEntries.decisionTable-meta.xml")
    check("meta_file_name derives the source-format name",
          _payload.meta_file_name(_cost_book_spec()) ==
          "RLM_CostBookEntries.decisionTable-meta.xml")


# --------------------------------------------------------------------------- #
# _lifecycle — active-edit guard + guarded-update transitions (no org, no sleep)
# --------------------------------------------------------------------------- #

def test_assert_editable_guard():
    print("test_assert_editable_guard")
    engine = LifecycleEngine(_LifecycleFake(status="Active"))
    raised = False
    try:
        engine.assert_editable(_table_row(Status="Active"))
    except LifecycleError as exc:
        raised = "active" in str(exc).lower()
    check("assert_editable raises on Active", raised)
    # In-progress activation is likewise locked.
    raised2 = False
    try:
        engine.assert_editable(_table_row(Status="ActivationInProgress"))
    except LifecycleError:
        raised2 = True
    check("assert_editable raises on ActivationInProgress", raised2)
    # Draft/Inactive are editable — no raise.
    ok = True
    try:
        engine.assert_editable(_table_row(Status="Draft"))
        engine.assert_editable(_table_row(Status="Inactive"))
    except LifecycleError:
        ok = False
    check("assert_editable allows Draft/Inactive", ok)


def test_guarded_update_active_roundtrip():
    print("test_guarded_update_active_roundtrip")
    fake = _LifecycleFake(status="Active")
    engine = LifecycleEngine(fake, max_wait_seconds=1)
    calls = []
    engine.run_guarded_update(
        table_row={"Id": "0lDxx0000000001AAA", "Status": "Active"},
        mutate=lambda: calls.append("mutate"),
        activate_after=True, reactivate_on_failure=True, verb="update")
    check("guarded update called mutate once", calls == ["mutate"], calls)
    check("guarded update deactivated then reactivated",
          fake.status_sets == ["Inactive", "Active"], fake.status_sets)
    check("guarded update left the table Active", fake.status == "Active")


def test_guarded_update_leave_deactivated():
    print("test_guarded_update_leave_deactivated")
    fake = _LifecycleFake(status="Active")
    engine = LifecycleEngine(fake, max_wait_seconds=1)
    engine.run_guarded_update(
        table_row={"Id": "0lDxx0000000001AAA", "Status": "Active"},
        mutate=lambda: None, activate_after=False, verb="update")
    check("activate_after=False leaves table Inactive", fake.status == "Inactive")
    check("activate_after=False never reactivates", fake.status_sets == ["Inactive"])


def test_guarded_update_connect_failure_left_deactivated():
    print("test_guarded_update_connect_failure_left_deactivated")
    # A Connect mutate that fails must leave the table DEACTIVATED (half-applied
    # body not re-enabled) — reactivate_on_failure=False for the connect path.
    fake = _LifecycleFake(status="Active")
    engine = LifecycleEngine(fake, max_wait_seconds=1)

    def _boom():
        raise DecisionTableClientError("connect PATCH rejected")

    raised = False
    try:
        engine.run_guarded_update(
            table_row={"Id": "0lDxx0000000001AAA", "Status": "Active"},
            mutate=_boom, activate_after=True, reactivate_on_failure=False, verb="update")
    except DecisionTableClientError:
        raised = True
    check("connect-path failure re-raises", raised)
    check("connect-path failure leaves table Inactive (not reactivated)",
          fake.status == "Inactive", fake.status_sets)


def test_guarded_update_tooling_failure_reactivates():
    print("test_guarded_update_tooling_failure_reactivates")
    # An atomic Tooling PATCH that fails leaves the record byte-identical, so the
    # table IS reactivated (reactivate_on_failure=True) — a failed edit never
    # knocks a live table offline. The failure is still re-raised.
    fake = _LifecycleFake(status="Active")
    engine = LifecycleEngine(fake, max_wait_seconds=1)

    def _boom():
        raise DecisionTableClientError("tooling PATCH rejected")

    raised = False
    try:
        engine.run_guarded_update(
            table_row={"Id": "0lDxx0000000001AAA", "Status": "Active"},
            mutate=_boom, activate_after=True, reactivate_on_failure=True, verb="update")
    except DecisionTableClientError:
        raised = True
    check("tooling-path failure re-raises", raised)
    check("tooling-path failure reactivates (record unchanged)",
          fake.status == "Active" and fake.status_sets == ["Inactive", "Active"],
          fake.status_sets)


def test_refresh_uses_live_verified_flag():
    print("test_refresh_uses_live_verified_flag")
    fake = _LifecycleFake(status="Active")
    engine = LifecycleEngine(fake)
    outcome = engine.refresh("RLM_MyTable", incremental=True)
    check("refresh posts to the refreshDecisionTable action",
          fake.connect_calls and fake.connect_calls[-1][1].endswith("refreshDecisionTable"),
          fake.connect_calls)
    body = fake.connect_calls[-1][2]
    sent = body["inputs"][0]
    check("refresh sends isDecisionTableIncremental (NOT isIncremental)",
          "isDecisionTableIncremental" in sent and "isIncremental" not in sent, sent)
    check("refresh passes the incremental flag through",
          sent["isDecisionTableIncremental"] is True)
    check("refresh reports Queued status", outcome.get("status") == "Queued", outcome)


def test_delete_paths():
    print("test_delete_paths")
    fake = _LifecycleFake(status="Inactive")
    engine = LifecycleEngine(fake)
    res_c = engine.delete_connect("0lDxx0000000001AAA")
    check("delete_connect issues a Connect DELETE",
          fake.connect_calls[-1][0] == "DELETE"
          and fake.connect_calls[-1][1].endswith("/0lDxx0000000001AAA"), fake.connect_calls)
    check("delete_connect result path=connect", res_c["path"] == "connect")


# --------------------------------------------------------------------------- #
# Mutator CLIs — preview-vs-confirm gating via the fake transport (no org)
# --------------------------------------------------------------------------- #

def test_create_cli_tooling_preview_vs_confirm(tmp_spec):
    print("test_create_cli_tooling_preview_vs_confirm")
    # Preview: dry_run transport → no mutation recorded.
    fake_p = _FakeTransport(dry_run=True)
    rc, out = _run_cli_with_fake(
        create_cli, ["--target-org", "x", "--spec", tmp_spec,
                     "--path", "tooling", "--json"], fake_p)
    check("create preview exits 0", rc == 0, out[:300])
    check("create preview performs NO mutation", fake_p.mutations == [], fake_p.mutations)
    check("create preview reports dryRun=True", json.loads(out).get("dryRun") is True)
    # Confirm: non-dry transport → a Tooling POST is executed + recorded.
    fake_c = _FakeTransport(dry_run=False)
    rc, out = _run_cli_with_fake(
        create_cli, ["--target-org", "x", "--spec", tmp_spec,
                     "--path", "tooling", "--confirm", "--json"], fake_c)
    check("create confirm exits 0", rc == 0, out[:300])
    check("create confirm records a POST DecisionTable",
          any(m[0] == "POST" and m[1] == "tooling/DecisionTable" for m in fake_c.mutations),
          fake_c.mutations)
    check("create confirm reports dryRun=False", json.loads(out).get("dryRun") is False)


def test_create_cli_generate_only_no_org(tmp_spec, tmp_out_xml):
    print("test_create_cli_generate_only_no_org")
    fake = _FakeTransport(dry_run=True)
    rc, out = _run_cli_with_fake(
        create_cli, ["--target-org", "x", "--spec", tmp_spec,
                     "--generate-only", tmp_out_xml, "--json"], fake)
    check("generate-only exits 0", rc == 0, out[:300])
    check("generate-only performs NO org mutation", fake.mutations == [])
    produced = Path(tmp_out_xml).read_text(encoding="utf-8")
    check("generate-only wrote a DecisionTable XML",
          produced.startswith('<?xml') and "<DecisionTable" in produced, produced[:80])


def test_create_cli_connect_path_default_status(tmp_spec):
    print("test_create_cli_connect_path_default_status")
    fake = _FakeTransport(dry_run=False)
    rc, _ = _run_cli_with_fake(
        create_cli, ["--target-org", "x", "--spec", tmp_spec,
                     "--path", "connect", "--confirm"], fake)
    check("connect create exits 0", rc == 0)
    posts = [m for m in fake.mutations if m[0] == "POST"]
    check("connect create issues a POST to the definitions path",
          posts and posts[-1][1].endswith("definitions"), fake.mutations)
    body = posts[-1][2]
    check("connect create body uses renamed keys",
          body.get("sourceType") == "SingleSobject" and "parameters" in body, body)


def test_create_cli_generate_only_rejects_nonmetadata(tmp_spec):
    print("test_create_cli_generate_only_rejects_nonmetadata")
    fake = _FakeTransport(dry_run=True)
    rc, _ = _run_cli_with_fake(
        create_cli, ["--target-org", "x", "--spec", tmp_spec,
                     "--path", "tooling", "--generate-only", "/tmp/x.xml"], fake)
    check("generate-only + non-metadata path exits 2", rc == 2, rc)


def test_create_cli_invalid_spec_blocks(tmp_path_factory):
    print("test_create_cli_invalid_spec_blocks")
    bad = tmp_path_factory("bad_spec.json")
    Path(bad).write_text(json.dumps({"dataSourceType": "SingleSobject"}), encoding="utf-8")
    fake = _FakeTransport(dry_run=False)
    rc, _ = _run_cli_with_fake(
        create_cli, ["--target-org", "x", "--spec", bad, "--path", "tooling", "--confirm"],
        fake)
    check("invalid spec exits 1", rc == 1, rc)
    check("invalid spec performs NO mutation", fake.mutations == [], fake.mutations)


def test_update_cli_active_refused_without_flag(tmp_spec):
    print("test_update_cli_active_refused_without_flag")
    # Active table + no --deactivate-first → the CLI must refuse (exit 1) and not
    # mutate, even under --confirm.
    fake = _FakeTransport(table=_table_row(Status="Active"), dry_run=False)
    rc, _ = _run_cli_with_fake(
        update_cli, ["--target-org", "x", "--spec", tmp_spec, "--confirm"], fake)
    check("update of Active table without --deactivate-first exits 1", rc == 1, rc)
    check("refused update performs NO PATCH",
          not any(m[0] == "PATCH" for m in fake.mutations), fake.mutations)


def test_update_cli_deactivate_first_roundtrip(tmp_spec):
    print("test_update_cli_deactivate_first_roundtrip")
    fake = _FakeTransport(table=_table_row(Status="Active"), dry_run=False)
    rc, _ = _run_cli_with_fake(
        update_cli, ["--target-org", "x", "--spec", tmp_spec,
                     "--deactivate-first", "--confirm"], fake)
    check("deactivate-first update exits 0", rc == 0, rc)
    patches = [m for m in fake.mutations if m[0] == "PATCH" and m[1] == "tooling/DecisionTable"]
    # The lifecycle engine drives the status flips: deactivate (Inactive) first,
    # reactivate (Active) last.
    statuses = [p[2]["Metadata"].get("status") for p in patches
                if isinstance(p[2].get("Metadata"), dict) and p[2]["Metadata"].get("status")]
    check("deactivate-first flips Inactive first, Active last",
          bool(statuses) and statuses[0] == "Inactive" and statuses[-1] == "Active", statuses)
    # The definition-edit PATCH is the one carrying the columns. A Tooling Metadata
    # PATCH REQUIRES status (a status-free body is rejected), so the edit stamps the
    # CURRENT LIVE status — Inactive, because the table was just deactivated — never
    # the spec's Active (which would re-activate mid-edit).
    defn_patches = [p for p in patches
                    if isinstance(p[2].get("Metadata"), dict)
                    and "decisionTableParameters" in p[2]["Metadata"]]
    check("deactivate-first PATCHes the definition body (with columns)",
          len(defn_patches) == 1, defn_patches)
    check("definition edit stamps the live status (Inactive), never the spec's Active",
          bool(defn_patches) and defn_patches[0][2]["Metadata"].get("status") == "Inactive",
          defn_patches[0][2]["Metadata"].get("status") if defn_patches else None)


def test_activate_cli_preview_vs_confirm():
    print("test_activate_cli_preview_vs_confirm")
    fake_p = _FakeTransport(table=_table_row(Status="Inactive"), dry_run=True)
    rc, _ = _run_cli_with_fake(
        activate_cli, ["--target-org", "x", "--developer-name", "RLM_CostBookEntries"], fake_p)
    check("activate preview exits 0", rc == 0, rc)
    check("activate preview performs NO mutation", fake_p.mutations == [], fake_p.mutations)
    fake_c = _FakeTransport(table=_table_row(Status="Inactive"), dry_run=False)
    rc, _ = _run_cli_with_fake(
        activate_cli, ["--target-org", "x", "--developer-name", "RLM_CostBookEntries",
                       "--confirm", "--max-wait", "1"], fake_c)
    check("activate confirm exits 0", rc == 0, rc)
    check("activate confirm PATCHes status=Active",
          any(m[0] == "PATCH" and isinstance(m[2].get("Metadata"), dict)
              and m[2]["Metadata"].get("status") == "Active" for m in fake_c.mutations),
          fake_c.mutations)


def test_activate_cli_skips_when_already_active():
    print("test_activate_cli_skips_when_already_active")
    fake = _FakeTransport(table=_table_row(Status="Active"), dry_run=False)
    rc, _ = _run_cli_with_fake(
        activate_cli, ["--target-org", "x", "--developer-name", "RLM_CostBookEntries",
                       "--confirm"], fake)
    check("activate of already-Active table exits 0", rc == 0, rc)
    check("already-Active activate performs NO mutation", fake.mutations == [], fake.mutations)


def test_deactivate_cli_preview_vs_confirm():
    print("test_deactivate_cli_preview_vs_confirm")
    fake_p = _FakeTransport(table=_table_row(Status="Active"), dry_run=True)
    rc, _ = _run_cli_with_fake(
        deactivate_cli, ["--target-org", "x", "--developer-name", "RLM_CostBookEntries"], fake_p)
    check("deactivate preview exits 0", rc == 0, rc)
    check("deactivate preview performs NO mutation", fake_p.mutations == [], fake_p.mutations)
    fake_c = _FakeTransport(table=_table_row(Status="Active"), dry_run=False)
    rc, _ = _run_cli_with_fake(
        deactivate_cli, ["--target-org", "x", "--developer-name", "RLM_CostBookEntries",
                         "--confirm"], fake_c)
    check("deactivate confirm exits 0", rc == 0, rc)
    check("deactivate confirm PATCHes status=Inactive",
          any(m[0] == "PATCH" and isinstance(m[2].get("Metadata"), dict)
              and m[2]["Metadata"].get("status") == "Inactive" for m in fake_c.mutations),
          fake_c.mutations)


def test_refresh_cli_preview_vs_confirm():
    print("test_refresh_cli_preview_vs_confirm")
    fake_p = _FakeTransport(dry_run=True)
    rc, out = _run_cli_with_fake(
        refresh_cli, ["--target-org", "x", "--developer-name", "RLM_CostBookEntries",
                      "--incremental", "--json"], fake_p)
    check("refresh preview exits 0", rc == 0, out[:300])
    check("refresh preview performs NO mutation", fake_p.mutations == [], fake_p.mutations)
    fake_c = _FakeTransport(dry_run=False)
    rc, out = _run_cli_with_fake(
        refresh_cli, ["--target-org", "x", "--developer-name", "RLM_CostBookEntries",
                      "--confirm", "--json"], fake_c)
    check("refresh confirm exits 0", rc == 0, out[:300])
    check("refresh confirm posts the refresh action",
          any(m[0] == "POST" and m[1].endswith("refreshDecisionTable")
              for m in fake_c.mutations), fake_c.mutations)


def test_delete_cli_requires_confirm():
    print("test_delete_cli_requires_confirm")
    # Preview (no --confirm) → no delete.
    fake_p = _FakeTransport(table=_table_row(Status="Inactive"), dry_run=True)
    rc, _ = _run_cli_with_fake(
        delete_cli, ["--target-org", "x", "--developer-name", "RLM_CostBookEntries"], fake_p)
    check("delete preview exits 0", rc == 0, rc)
    check("delete preview performs NO deletion", fake_p.mutations == [], fake_p.mutations)
    # Confirm on an Inactive table → a Tooling DELETE is recorded.
    fake_c = _FakeTransport(table=_table_row(Status="Inactive"), dry_run=False)
    rc, _ = _run_cli_with_fake(
        delete_cli, ["--target-org", "x", "--developer-name", "RLM_CostBookEntries",
                     "--confirm"], fake_c)
    check("delete confirm exits 0", rc == 0, rc)
    check("delete confirm records a DELETE DecisionTable",
          any(m[0] == "DELETE" and m[1] == "tooling/DecisionTable" for m in fake_c.mutations),
          fake_c.mutations)


def test_delete_cli_active_refused_without_flag():
    print("test_delete_cli_active_refused_without_flag")
    fake = _FakeTransport(table=_table_row(Status="Active"), dry_run=False)
    rc, _ = _run_cli_with_fake(
        delete_cli, ["--target-org", "x", "--developer-name", "RLM_CostBookEntries",
                     "--confirm"], fake)
    check("delete of Active table without --deactivate-first exits 1", rc == 1, rc)
    check("refused delete performs NO deletion",
          not any(m[0] == "DELETE" for m in fake.mutations), fake.mutations)


def main():
    import tempfile

    tmpdir = tempfile.mkdtemp(prefix="dt_toolkit_tests_")

    def _tmp(name):
        return str(Path(tmpdir) / name)

    # A shared valid spec file for the mutator CLI tests.
    spec_path = _tmp("cost_book_spec.json")
    Path(spec_path).write_text(json.dumps(_cost_book_spec()), encoding="utf-8")
    out_xml = _tmp("out.decisionTable-meta.xml")

    simple = (test_schema_catalogs, test_validate_spec_clean, test_validate_spec_errors,
              test_validate_spec_duplicate_and_unknown, test_resolve_query_builders,
              test_resolve_missing_raises, test_load_definition_assembly,
              test_connect_definition_unwrap, test_diff_identical, test_diff_detects_changes,
              test_dump_single_sobject, test_dump_csv_not_applicable,
              test_dump_empty_source_note, test_trace_correlation, test_list_cli_json,
              test_describe_cli_grouped, test_trace_cli_json,
              # Phase 2 — translators + XML round-trip
              test_translator_metadata, test_translator_tooling, test_translator_connect,
              test_metadata_xml_roundtrip,
              # Phase 2 — lifecycle guards + transitions
              test_assert_editable_guard, test_guarded_update_active_roundtrip,
              test_guarded_update_leave_deactivated,
              test_guarded_update_connect_failure_left_deactivated,
              test_guarded_update_tooling_failure_reactivates,
              test_refresh_uses_live_verified_flag, test_delete_paths,
              # Phase 2 — mutator CLI activate/deactivate/refresh/delete gating
              test_activate_cli_preview_vs_confirm, test_activate_cli_skips_when_already_active,
              test_deactivate_cli_preview_vs_confirm, test_refresh_cli_preview_vs_confirm,
              test_delete_cli_requires_confirm, test_delete_cli_active_refused_without_flag)
    for fn in simple:
        fn()

    # Phase 2 — create/update CLI tests that need spec/output-file fixtures.
    test_create_cli_tooling_preview_vs_confirm(spec_path)
    test_create_cli_generate_only_no_org(spec_path, out_xml)
    test_create_cli_connect_path_default_status(spec_path)
    test_create_cli_generate_only_rejects_nonmetadata(spec_path)
    test_create_cli_invalid_spec_blocks(_tmp)
    test_update_cli_active_refused_without_flag(spec_path)
    test_update_cli_deactivate_first_roundtrip(spec_path)

    import shutil
    shutil.rmtree(tmpdir, ignore_errors=True)

    print(f"\n{_PASS} passed, {_FAIL} failed.")
    return 1 if _FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
