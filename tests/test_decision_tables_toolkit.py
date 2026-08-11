#!/usr/bin/env python3
"""Offline unit tests for the self-contained ``scripts/decision_tables/`` toolkit.

No org, no ``sf`` CLI, no pytest — a plain ``check()`` runner matching the style
of ``tests/test_expression_sets_toolkit.py``. Exercises the package's pure logic:

- ``_schema`` — enum catalogs, key prefixes, and canonical-spec validation.
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
from scripts.decision_tables._client import DecisionTableClientError, DEFINITIONS_PATH  # noqa: E402
from scripts.decision_tables._lifecycle import (  # noqa: E402
    LifecycleEngine,
    LifecycleError,
)
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
import scripts.decision_tables.upload_decision_table_data as upload_cli  # noqa: E402
import scripts.decision_tables.dump_decision_table_data as dump_cli  # noqa: E402
import scripts.decision_tables._lifecycle as _lifecycle  # noqa: E402

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
        "Id": "0lDxx0000000001AAA", "DeveloperName": name,
        # MasterLabel is the constant object label on every row (never a per-table
        # label); SetupName is the distinct per-table label describe/list should show.
        "MasterLabel": "Decision Tables", "SetupName": "Cost Book Entries",
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


def _metadata_param(param):
    """Translate the fake's Tooling parameter row to the parent Metadata shape."""
    fields = {
        "dataType": "DataType", "decimalScale": "DecimalScale",
        "domainObject": "DomainObject", "fieldName": "FieldName",
        "fieldPath": "FieldPath", "isGroupByField": "IsGroupByField",
        "isPriorityField": "IsPriorityField", "isRequired": "IsRequired",
        "length": "Length", "operator": "Operator", "sequence": "Sequence",
        "sortType": "SortType", "usage": "Usage",
    }
    return {target: param.get(source) for target, source in fields.items()}


class _FakeTransport:
    """Duck-types _client.Transport and records requests.

    Mirrors the real transport's dry-run contract: when ``dry_run`` is set, a
    **mutating** verb (anything but GET/HEAD) is logged+skipped and NOT appended to
    ``self.mutations`` — reads always execute. A confirmed (``dry_run=False``)
    mutating verb is executed and recorded. A confirmed Tooling ``DecisionTable``
    PATCH that carries ``Metadata.status`` also updates ``self.table['Status']`` so
    ``wait_for_status`` resolves on the first poll (no ``time.sleep``)."""

    def __init__(self, *, table=None, params=None, links=None, dataset_params=None,
                 criteria=None, mappings=None, source_rows=None,
                 metadata=None, csv_data=None,
                 refresh_response=None, upload_statuses=None, dry_run=False):
        self.table = table if table is not None else _table_row()
        self.params = params if params is not None else [
            _param("INPUT", "ProductId"), _param("OUTPUT", "Cost", DataType="Currency")]
        self.links = links or []
        self.dataset_params = dataset_params or []
        self.criteria = criteria or []
        self.mappings = mappings or []
        self.source_rows = source_rows if source_rows is not None else [{"Id": "01txx", "Cost": 5}]
        # Metadata complexvalue returned by the DecisionTable Tooling GET. None →
        # the default SingleSobject sample; pass a CsvUpload sample to exercise the
        # CSV branch.
        self.metadata = metadata
        # CsvUpload data-layer GET (.../{id}/data) response. None → an empty table
        # ({"rows": [], "totalRows": 0}); a dict → returned verbatim; an Exception
        # → raised (simulates a gated/disabled endpoint).
        self.csv_data = csv_data
        # Override for the refreshDecisionTable action response (a list, matching
        # the real invocable-action envelope). None → the default success/Queued.
        self.refresh_response = refresh_response
        self.upload_statuses = list(upload_statuses or ["UploadInProgress", "Completed"])
        self.upload_submitted = False
        self.dry_run = dry_run
        self.api_version = "67.0"
        self.target_org = "fake-org"
        self.logger = lambda *a, **k: None
        self.tooling_queries = []
        self.soql_queries = []
        self.mutations = []  # (method, target, body) for EXECUTED mutating verbs
        self.csv_data_calls = []  # kwargs of each get_decision_table_data call

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
            meta = dict(self.metadata if self.metadata is not None else _sample_metadata())
            meta.setdefault(
                "decisionTableParameters", [_metadata_param(p) for p in self.params]
            )
            if self.upload_submitted and self.upload_statuses:
                meta["uploadStatus"] = self.upload_statuses[0]
                if len(self.upload_statuses) > 1:
                    self.upload_statuses.pop(0)
            return dict(self.table, Metadata=meta)
        if self._skip_mutation(method, f"tooling/{sobject}", body):
            return {}
        # Reflect a Status transition so wait_for_status resolves without sleeping.
        if (method.upper() == "PATCH" and sobject == "DecisionTable"
                and isinstance(body, dict) and isinstance(body.get("Metadata"), dict)
                and body["Metadata"].get("status")):
            self.table = dict(self.table, Status=body["Metadata"]["status"])
            self.metadata = dict(body["Metadata"])
        if method.upper() == "POST" and sobject == "DecisionTable":
            # A confirmed create is immediately visible to a follow-on read/resolve.
            if isinstance(body, dict) and isinstance(body.get("Metadata"), dict):
                self.metadata = dict(body["Metadata"])
                self.table = dict(
                    self.table,
                    Id="0lDxx0000000009AAA",
                    DeveloperName=body.get("FullName") or self.table.get("DeveloperName"),
                )
            return {"id": "0lDxx0000000009AAA", "success": True}
        return {}

    def connect(self, method, path, body=None, **kw):
        if self._skip_mutation(method, path, body):
            return {}
        if path.endswith("refreshDecisionTable"):
            if self.refresh_response is not None:
                return self.refresh_response
            return [{"isSuccess": True, "outputValues": {"Status": "Queued"}}]
        return {}

    def soql(self, query):
        self.soql_queries.append(query)
        if "FROM PricingRecipeTableMapping" in query:
            return list(self.mappings)
        return list(self.source_rows)

    # -- CSV Based Decision Table data layer (dataSourceType == CsvUpload) --

    def content_version_insert(self, title, csv_text, *,
                               path_on_client="decision_table_rows.csv", dry_run=None):
        # _skip_mutation records the executed mutation (or skips it under dry-run).
        if self._skip_mutation("POST", "sobjects/ContentVersion",
                               {"Title": title, "PathOnClient": path_on_client}):
            return {}
        return {"id": "068xx0000000001AAA", "success": True}

    def upload_decision_table_csv(self, record_id, file_id, *, dry_run=None):
        path = f"connect/business-rules/decision-table/{record_id}/file"
        body = {"fileId": file_id}
        if self._skip_mutation("POST", path, body):
            return {}
        self.upload_submitted = True
        return {"message": "We are uploading and processing the CSV file."}

    def get_decision_table_data(self, record_id, *, row_filter=None, limit=None):
        # A read — always executes, even under dry_run.
        self.csv_data_calls.append({"record_id": record_id,
                                    "row_filter": row_filter, "limit": limit})
        if isinstance(self.csv_data, Exception):
            raise self.csv_data
        if self.csv_data is not None:
            return self.csv_data
        return {"rows": [], "totalRows": 0}


class _LifecycleFake:
    """Minimal transport for exercising LifecycleEngine status transitions with a
    real (non-dry-run) engine but no ``time.sleep``.

    Holds a mutable ``status``; a Tooling PATCH of ``Metadata.status`` updates it
    and records the transition, and the ``get_status`` Tooling query reads it back
    — so ``wait_for_status`` matches on the first poll (waited=0, before any
    sleep). ``connect`` records refresh and CsvUpload-version mutations."""

    def __init__(self, status="Active", *, dry_run=False, data_source_type="SingleSobject",
                 versions=None):
        self.status = status
        self.dry_run = dry_run
        self.data_source_type = data_source_type
        self.api_version = "67.0"
        self.target_org = "fake-org"
        self.logger = lambda *a, **k: None
        self.status_sets = []  # ordered list of statuses PATCHed via Tooling
        self.version_status_sets = []  # ordered list of versionStatus PATCHed via Connect
        self.connect_calls = []
        # CsvUpload file-import versions as {versionNumber: versionStatus}. Given a
        # list of dicts it is normalized; omitted → a single version {1: status}.
        # A version PATCH updates the specific version and the table Status cascades
        # (Active iff any version is active) — modeling the multi-version platform.
        if data_source_type == "CsvUpload":
            if versions is not None:
                self.versions = {int(v["versionNumber"]): v["versionStatus"] for v in versions}
            else:
                self.versions = {1: status}
        else:
            self.versions = {}

    def _recompute_status_from_versions(self):
        self.status = ("Active" if any(
            v in ("Active", "ActivationInProgress") for v in self.versions.values())
            else "Inactive")

    def tooling_query(self, query):
        if "FROM DecisionTable" in query:
            return [{"Id": "0lDxx0000000001AAA", "Status": self.status}]
        return []

    def tooling_sobject(self, method, sobject, record_id=None, suffix=None, body=None, **kw):
        if method.upper() == "GET":
            metadata = _sample_metadata(status=self.status,
                                        dataSourceType=self.data_source_type)
            if self.data_source_type == "CsvUpload":
                metadata["decisionTableFileImportVersions"] = [
                    {"versionNumber": n, "versionStatus": s}
                    for n, s in sorted(self.versions.items())
                ]
            return {"Id": record_id,
                    "Metadata": metadata}
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
        # Mirror the platform's CsvUpload cascade: PATCHing a file-import version's
        # versionStatus updates THAT version, and the table's own Status cascades
        # from whether any version is active.
        if "/versions/" in path and method.upper() == "PATCH" and isinstance(body, dict):
            new = body.get("versionStatus")
            if new:
                vnum = int(path.rsplit("/", 1)[-1])
                self.versions[vnum] = new
                self.version_status_sets.append(new)
                self._recompute_status_from_versions()
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
    check("documented collect operators", _schema.COLLECT_OPERATORS ==
          {"Count", "Maximum", "Minimum", "None", "Sum"})
    check("documented row override types", _schema.ROW_LEVEL_OVERRIDE_TYPES ==
          {"Both", "Condition", "None", "Operator"})
    check("documented sort types", _schema.PARAM_SORT_TYPES ==
          {"AscNullFirst", "AscNullLast", "DescNullFirst", "DescNullLast", "None"})
    check("documented parameter operators included",
          {"Contains", "DoesNotExistIn", "DoesNotMatch", "IsNotNull"} <=
          _schema.PARAM_OPERATORS)


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


def test_validate_spec_full_name_shape():
    print("test_validate_spec_full_name_shape")
    # fullName is a Salesforce API name, not a path or arbitrary identifier.
    base = {
        "setupName": "X", "dataSourceType": "SingleSobject",
        "sourceObject": "CostBookEntry", "filterResultBy": "OutputOrder",
        "decisionTableParameters": [
            {"usage": "OUTPUT", "fieldName": "Cost", "dataType": "Currency"}],
    }
    for bad in ("/tmp/escaped", "../escaped", "a/b", "a\\b", "1LeadingDigit", ""):
        result = validate_spec({**base, "fullName": bad})
        check(f"fullName {bad!r} errors",
              any(i.location == "fullName" for i in result.errors), result.format_report())
    good = validate_spec({**base, "fullName": "RLM_Valid_Name1"})
    check("valid fullName has no fullName error",
          not any(i.location == "fullName" for i in good.errors), good.format_report())


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


def test_validate_spec_duplicate_source_criterion_sequence():
    print("test_validate_spec_duplicate_source_criterion_sequence")
    # Two source criteria sharing a sequenceNumber pass every per-field check, but
    # sourceConditionLogic references criteria by sequence ("1 AND 2"), so a duplicate
    # sequence is ambiguous. validate_spec must reject it UP FRONT, mirroring the
    # duplicate-column guard.
    dup = validate_spec(_cost_book_spec(decisionTableSourceCriterias=[
        {"sourceFieldName": "Status", "operator": "Equals", "value": "Active",
         "valueType": "Literal", "sequenceNumber": 1},
        {"sourceFieldName": "Region", "operator": "Equals", "value": "West",
         "valueType": "Literal", "sequenceNumber": 1},  # duplicate sequence
    ]))
    check("duplicate source-criterion sequenceNumber errors",
          any("duplicate sequenceNumber" in i.message for i in dup.errors),
          dup.format_report())
    check("duplicate source-criterion sequence fails validation", not dup.passed,
          dup.format_report())
    # Distinct sequences on otherwise-identical criteria stay clean.
    ok = validate_spec(_cost_book_spec(decisionTableSourceCriterias=[
        {"sourceFieldName": "Status", "operator": "Equals", "value": "Active",
         "valueType": "Literal", "sequenceNumber": 1},
        {"sourceFieldName": "Region", "operator": "Equals", "value": "West",
         "valueType": "Literal", "sequenceNumber": 2},
    ]))
    check("distinct source-criterion sequences pass", ok.passed, ok.format_report())


def test_validate_spec_duplicate_input_sequence():
    print("test_validate_spec_duplicate_input_sequence")
    # Each INPUT column needs a distinct conditionCriteria reference.
    dup = validate_spec(_cost_book_spec(decisionTableParameters=[
        {"usage": "INPUT", "fieldName": "ProductId", "dataType": "String",
         "operator": "Equals", "sequence": 1},
        {"usage": "INPUT", "fieldName": "Region", "dataType": "String",
         "operator": "Equals", "sequence": 1},  # duplicate INPUT sequence
        {"usage": "OUTPUT", "fieldName": "Cost", "dataType": "Currency"},
    ]))
    check("duplicate INPUT sequence errors",
          any("duplicate INPUT sequence" in i.message for i in dup.errors),
          dup.format_report())
    # Confirm the degenerate expression this prevents (documents WHY it is rejected).
    degenerate = _payload._derive_condition_criteria(
        [{"usage": "INPUT", "sequence": 1}, {"usage": "INPUT", "sequence": 1}], "All")
    check("duplicate INPUT sequences would derive a degenerate '1 AND 1'",
          degenerate == "1 AND 1", degenerate)
    # Distinct sequences on the same columns stay clean.
    ok = validate_spec(_cost_book_spec())
    check("distinct INPUT sequences pass", ok.passed, ok.format_report())


def test_validate_spec_boolean_typo():
    print("test_validate_spec_boolean_typo")
    # F4: _bool_from silently maps any unrecognized string to False, so an author
    # typo like "treu" would validate clean and persist a DIFFERENT definition than
    # intended. All canonical boolean fields (top-level and parameter-level) must be
    # validated against the recognized-token set.
    top = validate_spec(_cost_book_spec(isIncrementalSyncEnabled="treu"))
    check("top-level boolean typo errors",
          any(i.location == "isIncrementalSyncEnabled" for i in top.errors),
          top.format_report())
    param = validate_spec(_cost_book_spec(decisionTableParameters=[
        {"usage": "INPUT", "fieldName": "ProductId", "dataType": "String",
         "operator": "Equals", "sequence": 1, "isRequired": "treu"},  # typo
        {"usage": "OUTPUT", "fieldName": "Cost", "dataType": "Currency"},
    ]))
    check("parameter boolean typo errors",
          any(i.location.endswith(".isRequired") for i in param.errors),
          param.format_report())
    # Real bools and recognized string tokens still pass.
    ok = validate_spec(_cost_book_spec(isIncrementalSyncEnabled="true",
                                       isVersioned=False))
    check("recognized boolean tokens/bools pass", ok.passed, ok.format_report())


def _csv_upload_spec(**over):
    """A canonical CsvUpload spec (sourceObject is the literal 'CSV')."""
    spec = {
        "fullName": "RLM_CsvUploadTable", "setupName": "CSV Upload Table",
        "dataSourceType": "CsvUpload", "sourceObject": "CSV",
        "filterResultBy": "FirstMatch", "type": "Advanced",
        "decisionTableParameters": [
            {"usage": "INPUT", "fieldName": "Region", "dataType": "String",
             "operator": "Equals", "sequence": 1},
            {"usage": "OUTPUT", "fieldName": "DiscountPercent", "dataType": "Percent"},
        ],
    }
    spec.update(over)
    return spec


def test_validate_spec_csv_upload():
    print("test_validate_spec_csv_upload")
    # A CsvUpload spec with the literal 'CSV' sourceObject is clean.
    result = validate_spec(_csv_upload_spec())
    check("CsvUpload spec with sourceObject='CSV' passes", result.passed, result.format_report())
    check("CsvUpload spec has no errors", not result.errors, result.format_report())
    # Regression guard: sourceObject is REQUIRED for CsvUpload too (the old
    # carve-out let an invalid spec pass). A CsvUpload spec WITHOUT sourceObject
    # must ERROR, and the error should hint the 'CSV' convention.
    missing = validate_spec(_csv_upload_spec(sourceObject=None))
    check("CsvUpload without sourceObject errors",
          any("sourceObject" in i.location for i in missing.errors), missing.format_report())
    check("CsvUpload missing-sourceObject error hints the 'CSV' convention",
          any("sourceObject" in i.location and "CSV" in i.message for i in missing.errors),
          missing.format_report())
    # A non-'CSV' sourceObject on a CsvUpload table warns (not errors) — forward-compat.
    odd = validate_spec(_csv_upload_spec(sourceObject="CostBookEntry"))
    check("CsvUpload with a non-CSV sourceObject warns (not errors)",
          odd.passed and any("CSV" in i.message for i in odd.warnings), odd.format_report())


def test_validate_spec_create_and_structural_errors():
    print("test_validate_spec_create_and_structural_errors")
    spec = {
        "fullName": "RLM_CostBookEntries", "setupName": "Cost Book Entries",
        "dataSourceType": "SingleSobject", "sourceObject": "CostBookEntry",
        "filterResultBy": "OutputOrder",
        "decisionTableParameters": [
            {"usage": "INPUT", "fieldName": "ProductId", "dataType": "String",
             "operator": "Equals", "sequence": 1},
            {"usage": "OUTPUT", "fieldName": "Cost", "dataType": "Currency"},
        ],
    }
    # Update validation does not require status; the live value is stamped by update.
    update_result = validate_spec(spec)
    check("update validation does not require spec status",
          not any(i.location == "status" for i in update_result.errors),
          update_result.format_report())
    create_result = validate_spec(spec, require_status=True)
    check("create without status errors",
          any(i.location == "status" for i in create_result.errors),
          create_result.format_report())
    with_status = validate_spec({**spec, "status": "Draft"}, require_status=True)
    check("create with status set passes", with_status.passed,
          with_status.format_report())

    invalid = validate_spec({
        **spec,
        "conditionType": "Custom",
        "conditionCriteria": None,
        "unknownTopLevel": True,
        "decisionTableParameters": [
            {"usage": "INPUT", "fieldName": "ProductId", "operator": "Contains",
             "sequence": "one", "sortType": "AscNullFirst", "unknownColumn": 1},
            {"usage": "OUTPUT", "fieldName": "Cost"},
        ],
        "decisionTableSourceCriterias": [
            {"sourceFieldName": "UsageType", "unknownCriterion": 1},
        ],
    })
    check("Custom requires conditionCriteria",
          any(i.location == "conditionCriteria" for i in invalid.errors),
          invalid.format_report())
    check("parameter sequence must be an integer",
          any(i.location.endswith(".sequence") for i in invalid.errors),
          invalid.format_report())
    check("source criteria require operator, valueType, and sequenceNumber",
          {i.location.rsplit(".", 1)[-1] for i in invalid.errors} >=
          {"operator", "valueType", "sequenceNumber"}, invalid.format_report())
    check("unknown mutation keys are surfaced as ERRORS (a typo must block, not warn — "
          "the translator silently drops unknown keys, so a warning-only spec with a "
          "mistyped field name would validate clean and then write a wrong definition)",
          {"unknownTopLevel", "unknownColumn", "unknownCriterion"} <=
          {i.location.rsplit(".", 1)[-1] for i in invalid.errors},
          invalid.format_report())
    check("unknown mutation keys are not merely warnings",
          not ({"unknownTopLevel", "unknownColumn", "unknownCriterion"} &
               {i.location.rsplit(".", 1)[-1] for i in invalid.warnings}),
          invalid.format_report())


def test_validate_spec_usage_is_strict():
    print("test_validate_spec_usage_is_strict")
    # ``usage`` is a CLOSED structural enum (it drives whether operator/sequence are
    # kept, matched case-sensitively as {"INPUT"}), unlike the descriptive catalogs
    # that only warn. A mis-cased/off-catalog value must ERROR so a validated spec
    # can never silently write a wrong definition (drop operator/sequence) — the same
    # fail-closed treatment unknown keys get.
    base = {
        "fullName": "RLM_UsageCase", "setupName": "Usage Case",
        "dataSourceType": "SingleSobject", "sourceObject": "CostBookEntry",
        "filterResultBy": "OutputOrder",
    }
    # The Connect read-side casing "Input"/"Output" is the classic footgun — an
    # author copying from a Connect GET response would write exactly this.
    miscased = validate_spec({
        **base,
        "decisionTableParameters": [
            {"usage": "Input", "fieldName": "ProductId", "dataType": "String",
             "operator": "Equals", "sequence": 1},
            {"usage": "Output", "fieldName": "Cost", "dataType": "Currency"},
        ],
    })
    check("mis-cased usage 'Input' is an ERROR, not a warning",
          any(i.location.endswith(".usage") and "Input" in i.message
              for i in miscased.errors), miscased.format_report())
    check("mis-cased usage never lands as a mere warning",
          not any(i.location.endswith(".usage") for i in miscased.warnings),
          miscased.format_report())
    check("a spec with a mis-cased usage does not pass",
          not miscased.passed, miscased.format_report())
    # Canonical UPPER usage stays clean (no usage error/warning).
    canonical = validate_spec({
        **base,
        "decisionTableParameters": [
            {"usage": "INPUT", "fieldName": "ProductId", "dataType": "String",
             "operator": "Equals", "sequence": 1},
            {"usage": "OUTPUT", "fieldName": "Cost", "dataType": "Currency"},
        ],
    })
    check("canonical UPPER usage raises no usage issue",
          not any(i.location.endswith(".usage") for i in canonical.issues),
          canonical.format_report())


def test_validate_spec_rejects_non_string_enum_values():
    print("test_validate_spec_rejects_non_string_enum_values")
    # Enum values are ALWAYS strings in the Metadata/Tooling vocabulary; a non-string
    # (int/bool/list/dict) can never be valid, so it is a hard ERROR, not a
    # forward-compat warning. This also keeps a list/dict from reaching the enum
    # membership test / dedup set (which would crash with "TypeError: unhashable type"
    # and leak a traceback out of create/update instead of the --json result).
    base = {
        "fullName": "RLM_Malformed", "setupName": "Malformed",
        "sourceObject": "CostBookEntry", "filterResultBy": "OutputOrder",
    }
    # (a) top-level enum: status/dataSourceType as non-strings.
    top = validate_spec({
        **base, "status": [], "dataSourceType": {},
        "decisionTableParameters": [
            {"usage": "OUTPUT", "fieldName": "Cost", "dataType": "Currency"}],
    })
    check("non-string status errors (no crash)",
          any(i.location == "status" and "string" in i.message for i in top.errors),
          top.format_report())
    check("non-string dataSourceType errors (no crash)",
          any(i.location == "dataSourceType" for i in top.errors), top.format_report())
    # (b) parameter enum: usage as a list.
    param = validate_spec({
        **base, "dataSourceType": "SingleSobject",
        "decisionTableParameters": [
            {"usage": [], "fieldName": "ProductId", "dataType": "String"},
            {"usage": "OUTPUT", "fieldName": "Cost", "dataType": "Currency"}],
    })
    check("non-string parameter usage errors (no crash)",
          any(i.location.endswith(".usage") and "string" in i.message for i in param.errors),
          param.format_report())
    # (c) source-criterion enum + sequenceNumber as non-scalars (dedup-set crash site).
    crit = validate_spec({
        **base, "dataSourceType": "SingleSobject", "conditionType": "Custom",
        "conditionCriteria": "1",
        "decisionTableParameters": [
            {"usage": "OUTPUT", "fieldName": "Cost", "dataType": "Currency"}],
        "decisionTableSourceCriterias": [
            {"sourceFieldName": "Region", "operator": {}, "valueType": "Value",
             "sequenceNumber": []}],
    })
    check("non-scalar criterion operator errors (no crash)",
          any(i.location.endswith(".operator") for i in crit.errors), crit.format_report())
    check("non-scalar sequenceNumber errors (no crash)",
          any("sequenceNumber" in i.location for i in crit.errors), crit.format_report())
    for label, res in (("top", top), ("param", param), ("crit", crit)):
        check(f"malformed {label} spec fails cleanly", not res.passed, res.format_report())


def test_validate_spec_rejects_malformed_scalar_enum_and_text():
    print("test_validate_spec_rejects_malformed_scalar_enum_and_text")
    # Structural enums and text fields reject non-string values before translation.
    base = {
        "fullName": "RLM_Malformed2", "setupName": "Malformed2",
        "dataSourceType": "SingleSobject", "sourceObject": "CostBookEntry",
        "filterResultBy": "OutputOrder", "status": "Draft",
        "decisionTableParameters": [
            {"usage": "OUTPUT", "fieldName": "Cost", "dataType": "Currency"}],
    }
    # (a) an integer where a string enum is expected — must error, not warn.
    int_enum = validate_spec({**base, "filterResultBy": 7})
    check("integer enum value is a hard error (not an accepted warning)",
          not int_enum.passed
          and any(i.location == "filterResultBy" and "string" in i.message
                  for i in int_enum.errors),
          int_enum.format_report())
    # (b) a boolean where a string enum is expected — bool is an int subclass, so the
    #     old `isinstance(value, (str, int, float, bool))` scalar guard let it through.
    bool_enum = validate_spec({**base, "executionType": True})
    check("boolean enum value is a hard error",
          not bool_enum.passed
          and any(i.location == "executionType" and "string" in i.message
                  for i in bool_enum.errors),
          bool_enum.format_report())
    # (c) a list where the setupName text belongs — must error.
    list_text = validate_spec({**base, "setupName": ["x"]})
    check("non-string setupName is a hard error",
          not list_text.passed
          and any(i.location == "setupName" and "string" in i.message
                  for i in list_text.errors),
          list_text.format_report())
    # (d) a non-string column fieldName rides verbatim into the payload — must error.
    bad_field = validate_spec({
        **base,
        "decisionTableParameters": [
            {"usage": "OUTPUT", "fieldName": ["Cost"], "dataType": "Currency"}],
    })
    check("non-string parameter fieldName is a hard error",
          not bad_field.passed
          and any(i.location.endswith(".fieldName") and "string" in i.message
                  for i in bad_field.errors),
          bad_field.format_report())

    # Sweep every non-enum string field carried by the canonical translator. These
    # are local shape checks only; Salesforce remains authoritative for names,
    # expressions, lifecycle state, and supported values.
    malformed = [
        ("sourceObject", {**base, "sourceObject": ["CostBookEntry"]}),
        ("conditionCriteria", {**base, "conditionCriteria": ["1"]}),
        ("sourceConditionLogic", {**base, "sourceConditionLogic": {"x": 1}}),
        ("description", {**base, "description": ["description"]}),
        ("decisionTableParameters[0].fieldPath", {
            **base,
            "decisionTableParameters": [{
                "usage": "OUTPUT", "fieldName": "Cost", "dataType": "Currency",
                "fieldPath": ["Cost"],
            }],
        }),
        ("decisionTableParameters[0].domainObject", {
            **base,
            "decisionTableParameters": [{
                "usage": "OUTPUT", "fieldName": "Cost", "dataType": "Currency",
                "domainObject": {"name": "CostBookEntry"},
            }],
        }),
        ("decisionTableSourceCriterias[0].value", {
            **base,
            "decisionTableSourceCriterias": [{
                "sourceFieldName": "UsageType", "operator": "Equals",
                "value": ["Pricing"], "valueType": "Literal", "sequenceNumber": 1,
            }],
        }),
        ("decisionTableSourceCriterias[0].sourceFieldName", {
            **base,
            "decisionTableSourceCriterias": [{
                "sourceFieldName": ["UsageType"], "operator": "Equals",
                "value": "Pricing", "valueType": "Literal", "sequenceNumber": 1,
            }],
        }),
    ]
    for location, malformed_spec in malformed:
        result = validate_spec(malformed_spec)
        check(f"non-string {location} is a hard error",
              not result.passed
              and any(i.location == location and "string" in i.message
                      for i in result.errors),
              result.format_report())


def test_payload_miscased_usage_is_blocked_upstream():
    print("test_payload_miscased_usage_is_blocked_upstream")
    # A mis-cased "Input" would be treated as non-INPUT by the translator, dropping
    # operator/sequence from the write (demonstrated below). The DEFENSE against that
    # is strict-usage VALIDATION, which rejects the spec before it ever reaches the
    # translator — so the corrupt write is never attempted. (This is why usage must
    # error, not warn.)
    miscased_param = {"usage": "Input", "fieldName": "ProductId", "dataType": "String",
                      "operator": "Equals", "sequence": 1}
    translated = _payload._param_to_metadata(miscased_param)
    check("mis-cased usage drops operator in translation",
          "operator" not in translated and "sequence" not in translated, translated)
    # The real defense: validate_spec rejects the mis-cased usage up front, so this
    # spec never reaches the translator or an org.
    spec_miscased = {
        "fullName": "RLM_UsageCase", "setupName": "Usage Case",
        "dataSourceType": "SingleSobject", "sourceObject": "CostBookEntry",
        "filterResultBy": "OutputOrder",
        "decisionTableParameters": [
            miscased_param,
            {"usage": "OUTPUT", "fieldName": "Cost", "dataType": "Currency"},
        ],
    }
    result = _schema.validate_spec(spec_miscased)
    check("strict-usage validation blocks the mis-cased spec before translation",
          not result.passed
          and any("usage" in i.location and "Input" in i.message for i in result.errors),
          result.format_report())


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
    check("identical → no dataset-link changes", not any(delta["datasetLinks"].values()), delta)
    check("identical → no dataset-parameter changes",
          not any(delta["datasetParameters"].values()), delta)
    check("identical → no source-criteria changes",
          not any(delta["sourceCriteria"].values()), delta)


def test_diff_detects_changes():
    print("test_diff_detects_changes")
    input_a = _param("INPUT", "ProductId", DomainObject="Product2",
                     DecimalScale=2, IsPriorityField=False, Length=80)
    output_a = _param("OUTPUT", "Cost", DataType="Currency")
    input_b = _param("INPUT", "ProductId", DataType="Number", DomainObject="Product2",
                     DecimalScale=3, IsPriorityField=True, Length=120)
    output_b = _param("OUTPUT", "Margin", DataType="Percent")
    link_a = {"Id": "0lX-A", "DeveloperName": "Products", "MasterLabel": "Products",
              "SetupName": "Products", "SourceObject": "Product2", "IsDefault": True,
              "Description": "Default product dataset"}
    link_b = dict(link_a, Id="0lX-B", IsDefault=False)
    a = {"table": _table_row(Status="Active"),
         "metadata": _sample_metadata(
             collectOperator="None",
             decisionTableParameters=[_metadata_param(input_a), _metadata_param(output_a)]),
         "parameters": [input_a, output_a],
         "datasetLinks": [link_a],
         "datasetParameters": [{
             "DecisionTableDatasetLinkId": "0lX-A",
             "DecisionTableParameterId": input_a["Id"],
             "DatasetFieldName": "ProductCode",
             "DatasetSourceObject": "Product2",
         }],
         "sourceCriteria": [{"SourceFieldName": "Status", "Operator": "Equals",
                              "Value": "Active", "ValueType": "Literal",
                              "SequenceNumber": 1}]}
    b = {"table": _table_row(Status="Inactive"),
         "metadata": _sample_metadata(
             filterResultBy="Priority", collectOperator="Maximum",
             decisionTableParameters=[_metadata_param(input_b), _metadata_param(output_b)]),
         "parameters": [input_b, output_b],
         "datasetLinks": [link_b],
         "datasetParameters": [{
             "DecisionTableDatasetLinkId": "0lX-B",
             "DecisionTableParameterId": input_b["Id"],
             "DatasetFieldName": "StockKeepingUnit",
             "DatasetSourceObject": "Product2",
         }],
         "sourceCriteria": [{"SourceFieldName": "Status", "Operator": "Equals",
                              "Value": "Active", "ValueType": "Picklist",
                              "SequenceNumber": 2}]}
    delta = diff_definitions(a, b)
    check("detects Status change", delta["attributes"].get("Status") ==
          {"a": "Active", "b": "Inactive"}, delta["attributes"])
    check("detects hitPolicy change", "filterResultBy" in delta["attributes"])
    check("detects collectOperator change", "collectOperator" in delta["attributes"])
    check("detects removed column (OUTPUT:Cost)", "OUTPUT:Cost" in delta["columns"]["removed"])
    check("detects added column (OUTPUT:Margin)", "OUTPUT:Margin" in delta["columns"]["added"])
    check("detects changed column (INPUT:ProductId dataType)",
          any(c["column"] == "INPUT:ProductId" and "dataType" in c["fields"]
              for c in delta["columns"]["changed"]), delta["columns"]["changed"])
    input_change = next(
        c for c in delta["columns"]["changed"] if c["column"] == "INPUT:ProductId"
    )
    check("detects Metadata-only column fields",
          {"decimalScale", "isPriorityField", "length"} <= set(input_change["fields"]),
          input_change)
    check("detects dataset-link property changes",
          bool(delta["datasetLinks"]["removed"] and delta["datasetLinks"]["added"]),
          delta["datasetLinks"])
    check("detects dataset-parameter mapping changes",
          bool(delta["datasetParameters"]["removed"]
               and delta["datasetParameters"]["added"]), delta["datasetParameters"])
    check("detects full source-criteria changes",
          bool(delta["sourceCriteria"]["removed"] and delta["sourceCriteria"]["added"]),
          delta["sourceCriteria"])


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


def test_dump_csv_upload_rows():
    print("test_dump_csv_upload_rows")
    # A CsvUpload table with uploaded rows → the data GET returns the rows envelope,
    # and dump surfaces each row's typed rowData under the synthetic sample key.
    t = _FakeTransport(
        table=_table_row(SourceObject="CSV"),
        metadata=_sample_metadata(dataSourceType="CsvUpload", sourceObject="CSV"),
        csv_data={"rows": [
            {"id": "1FIxx01", "rowData": {"Region": "North", "DiscountPercent": 10}},
            {"id": "1FIxx02", "rowData": {"Region": "South", "DiscountPercent": 5}}],
            "totalRows": 2})
    defn = _resolve.load_definition(t, "RLM_CostBookEntries")
    dump = dump_data(t, defn, limit=5)
    check("csv branch samples the uploaded rows",
          "CSV (uploaded rows)" in dump["samples"], dump["samples"])
    samples = dump["samples"].get("CSV (uploaded rows)", [])
    check("csv branch surfaces rowData (id stripped)",
          samples == [{"Region": "North", "DiscountPercent": 10},
                      {"Region": "South", "DiscountPercent": 5}], samples)
    check("csv branch does NOT report NOT APPLICABLE",
          not any("NOT APPLICABLE" in n for n in dump["notes"]), dump["notes"])
    check("csv branch passes limit through to the data GET",
          t.csv_data_calls and t.csv_data_calls[-1]["limit"] == 5, t.csv_data_calls)


def test_dump_csv_upload_empty():
    print("test_dump_csv_upload_empty")
    # A CsvUpload table with no uploaded rows → a note, no samples.
    t = _FakeTransport(
        table=_table_row(SourceObject="CSV"),
        metadata=_sample_metadata(dataSourceType="CsvUpload", sourceObject="CSV"))
    defn = _resolve.load_definition(t, "RLM_CostBookEntries")
    dump = dump_data(t, defn, limit=5)
    check("empty csv table samples nothing", not dump["samples"], dump["samples"])
    check("empty csv table notes 0 uploaded rows",
          any("0 uploaded rows" in n for n in dump["notes"]), dump["notes"])


def test_dump_csv_upload_gated():
    print("test_dump_csv_upload_gated")
    # A disabled/gated data GET (a parsed, allowlisted errorCode) degrades to a
    # note (mirrors the SObject fallbacks), never an unhandled error.
    t = _FakeTransport(
        table=_table_row(SourceObject="CSV"),
        metadata=_sample_metadata(dataSourceType="CsvUpload", sourceObject="CSV"),
        csv_data=DecisionTableClientError(
            "API_DISABLED_FOR_ORG", error_codes=["FUNCTIONALITY_NOT_ENABLED"]))
    defn = _resolve.load_definition(t, "RLM_CostBookEntries")
    dump = dump_data(t, defn, limit=5)
    check("gated csv GET degrades to a note (no raise)",
          any("failed" in n.lower() for n in dump["notes"]), dump["notes"])
    check("gated csv GET samples nothing", not dump["samples"], dump["samples"])


def test_dump_csv_upload_unclassified_error_propagates():
    print("test_dump_csv_upload_unclassified_error_propagates")
    # A transport failure (timeout, non-JSON CLI error) parses NO errorCode at
    # all — that must propagate as a real failure, not be swallowed into a
    # "may be disabled" note (regression for the narrowing that only checked
    # `if exc.error_codes` instead of intersecting against the allowlist).
    t = _FakeTransport(
        table=_table_row(SourceObject="CSV"),
        metadata=_sample_metadata(dataSourceType="CsvUpload", sourceObject="CSV"),
        csv_data=DecisionTableClientError("transport timeout"))
    defn = _resolve.load_definition(t, "RLM_CostBookEntries")
    raised = False
    try:
        dump_data(t, defn, limit=5)
    except DecisionTableClientError:
        raised = True
    check("unclassified csv GET error propagates (no silent degrade)", raised)


def test_dump_csv_upload_auth_and_generic_errors_propagate():
    print("test_dump_csv_upload_auth_and_generic_errors_propagate")
    # Only FUNCTIONALITY_NOT_ENABLED / NOT_FOUND are benign ("no rows to read").
    # Authorization (INSUFFICIENT_ACCESS), bad request (INVALID_INPUT), and
    # generic/unknown (UNKNOWN_EXCEPTION) are REAL failures and must propagate —
    # never be swallowed into an empty-but-successful "may be disabled" note.
    for code in ("INSUFFICIENT_ACCESS", "INVALID_INPUT", "UNKNOWN_EXCEPTION"):
        t = _FakeTransport(
            table=_table_row(SourceObject="CSV"),
            metadata=_sample_metadata(dataSourceType="CsvUpload", sourceObject="CSV"),
            csv_data=DecisionTableClientError(code, error_codes=[code]))
        defn = _resolve.load_definition(t, "RLM_CostBookEntries")
        raised = False
        try:
            dump_data(t, defn, limit=5)
        except DecisionTableClientError:
            raised = True
        check(f"csv GET {code} propagates (not degraded to a note)", raised)
    # NOT_FOUND (no version uploaded) still degrades to a note, not a raise.
    t = _FakeTransport(
        table=_table_row(SourceObject="CSV"),
        metadata=_sample_metadata(dataSourceType="CsvUpload", sourceObject="CSV"),
        csv_data=DecisionTableClientError("no version", error_codes=["NOT_FOUND"]))
    defn = _resolve.load_definition(t, "RLM_CostBookEntries")
    dump = dump_data(t, defn, limit=5)
    check("csv GET NOT_FOUND still degrades to a note (no raise)",
          any("failed" in n.lower() for n in dump["notes"]), dump["notes"])


def test_dump_empty_source_note():
    print("test_dump_empty_source_note")
    t = _FakeTransport(source_rows=[])
    defn = _resolve.load_definition(t, "RLM_CostBookEntries")
    dump = dump_data(t, defn, limit=5)
    check("empty source noted", any("0 rows" in n for n in dump["notes"]), dump["notes"])


def _csv_all_types_data():
    """A CsvUpload data GET response with one column per dataType (typed rowData)."""
    return {"rows": [{"id": "1FIxx01", "rowData": {
        "StringOut": "café ☕", "NumberOut": -3.5, "CurrencyOut": 1234.56,
        "PercentOut": 0.5, "BoolOut": True, "DateOut": "2026-07-10",
        "DateTimeOut": "2026-07-10T14:30:00.000Z"}}], "totalRows": 1}


def test_dump_csv_upload_filter_drops_limit():
    print("test_dump_csv_upload_filter_drops_limit")
    # §7 guard: filter + limit → the platform can throw UNKNOWN_EXCEPTION, so the
    # tool drops --limit (with a note) and reads the full matched set.
    t = _FakeTransport(
        table=_table_row(SourceObject="CSV"),
        metadata=_sample_metadata(dataSourceType="CsvUpload", sourceObject="CSV"),
        csv_data=_csv_all_types_data())
    defn = _resolve.load_definition(t, "RLM_CostBookEntries")
    dump = dump_data(t, defn, limit=5, row_filter="Region:North")
    call = t.csv_data_calls[-1]
    check("filter threads row_filter into the data GET",
          call["row_filter"] == "Region:North", call)
    check("filter+limit guard drops limit to None", call["limit"] is None, call)
    check("filter+limit guard leaves a note",
          any("--limit" in n and "ignored" in n for n in dump["notes"]), dump["notes"])


def test_dump_filter_ignored_on_non_csv():
    print("test_dump_filter_ignored_on_non_csv")
    # On a SingleSobject table --filter is ignored with a note.
    t = _FakeTransport(source_rows=[{"Id": "01t1", "Cost": 5}])
    defn = _resolve.load_definition(t, "RLM_CostBookEntries")
    dump = dump_data(t, defn, limit=5, row_filter="Region:North")
    check("non-CsvUpload notes that filter was ignored",
          any("only to CsvUpload" in n for n in dump["notes"]), dump["notes"])
    check("non-CsvUpload made no CSV data GET", t.csv_data_calls == [], t.csv_data_calls)


def test_dump_cli_filter_flag(tmp_dummy=None):
    print("test_dump_cli_filter_flag")
    # The CLI wires --filter → row_filter; the note surfaces in --json output.
    t = _FakeTransport(
        table=_table_row(SourceObject="CSV"),
        metadata=_sample_metadata(dataSourceType="CsvUpload", sourceObject="CSV"),
        csv_data=_csv_all_types_data())
    rc, out = _run_cli_with_fake(
        dump_cli, ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
                   "--filter", "StringOut:café ☕", "--json"], t)
    check("dump --filter exits 0", rc == 0, out[:300])
    check("dump --filter threads row_filter",
          t.csv_data_calls and t.csv_data_calls[-1]["row_filter"] == "StringOut:café ☕",
          t.csv_data_calls)
    check("dump --filter drops limit (guard)",
          t.csv_data_calls and t.csv_data_calls[-1]["limit"] is None, t.csv_data_calls)
    check("dump --filter note in json", "ignored" in out, out[:400])


def _all_types_spec(**over):
    """A CsvUpload spec with one INPUT + one OUTPUT column of each of the 7 dataTypes."""
    types = ["String", "Number", "Currency", "Percent", "Boolean", "Date", "DateTime"]
    params = [{"usage": "INPUT", "fieldName": "Key", "dataType": "String",
               "operator": "Equals", "sequence": 1}]
    params += [{"usage": "OUTPUT", "fieldName": f"{t}Out", "dataType": t} for t in types]
    spec = {"fullName": "RLM_AllTypes", "setupName": "All Types",
            "dataSourceType": "CsvUpload", "sourceObject": "CSV",
            "filterResultBy": "FirstMatch", "type": "Advanced",
            "decisionTableParameters": params}
    spec.update(over)
    return spec


def test_translator_csv_upload_all_types():
    print("test_translator_csv_upload_all_types")
    # All 7 column dataTypes survive both supported translators.
    spec = _all_types_spec()
    want = {"String", "Number", "Currency", "Percent", "Boolean", "Date", "DateTime"}
    meta = _payload.to_metadata(spec)
    meta_types = {p["dataType"] for p in meta["decisionTableParameters"]}
    check("metadata preserves all 7 output dataTypes", want <= meta_types, meta_types)
    tool = _payload.to_tooling(spec)
    tool_types = {p["dataType"] for p in tool["Metadata"]["decisionTableParameters"]}
    check("tooling preserves all 7 output dataTypes", want <= tool_types, tool_types)


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
    orig_sleep = upload_cli.time.sleep if module is upload_cli else None
    module.Transport = lambda *a, **k: fake
    if orig_sleep is not None:
        upload_cli.time.sleep = lambda *a, **k: None
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            rc = module.main(argv)
    finally:
        module.Transport = orig
        if orig_sleep is not None:
            upload_cli.time.sleep = orig_sleep
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
    # The label line must show the per-table SetupName, never the constant MasterLabel
    # ("Decision Tables") that is identical on every row.
    label_line = next((ln for ln in out.splitlines() if "label" in ln.lower()), "")
    check("describe shows SetupName as the label", "Cost Book Entries" in label_line, label_line)
    check("describe never shows the constant MasterLabel as the label",
          "Decision Tables" not in label_line, label_line)


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
# _payload — Metadata/Tooling translators + XML round-trip
# --------------------------------------------------------------------------- #

def _cost_book_spec(**over):
    """The canonical spec mirroring the shipped RLM_CostBookEntries table."""
    spec = {
        "fullName": "RLM_CostBookEntries", "setupName": "Cost Book Entries",
        "dataSourceType": "SingleSobject", "sourceObject": "CostBookEntry",
        "executionType": "HBASE", "filterResultBy": "OutputOrder",
        "conditionType": "All", "type": "MediumVolume", "usageType": "DefaultPricing",
        "status": "Active", "collectOperator": "None",
        "dtRowLevelOverrideType": "None",
        "decisionTableParameters": [
            {"usage": "INPUT", "fieldName": "ProductId", "dataType": "String",
             "operator": "Equals", "sequence": 1, "isRequired": True},
            {"usage": "INPUT", "fieldName": "CurrencyIsoCode", "dataType": "String",
             "operator": "Equals", "sequence": 2, "isRequired": True},
            {"usage": "OUTPUT", "fieldName": "Cost", "dataType": "String"},
        ],
    }
    spec.update(over)
    return spec


def test_translator_metadata():
    print("test_translator_metadata")
    spec = _cost_book_spec(
        sourceConditionLogic="1",
        decisionTableParameters=[
            {"usage": "INPUT", "fieldName": "ProductId", "dataType": "String",
             "operator": "Equals", "sequence": 1, "isRequired": True,
             "decimalScale": 2, "isPriorityField": True, "length": 80},
            {"usage": "INPUT", "fieldName": "CurrencyIsoCode", "dataType": "String",
             "operator": "Equals", "sequence": 2, "isRequired": True},
            {"usage": "OUTPUT", "fieldName": "Cost", "dataType": "String"},
        ],
    )
    body = _payload.to_metadata(spec)
    check("metadata keeps dataSourceType name", body["dataSourceType"] == "SingleSobject")
    check("metadata keeps filterResultBy name", body["filterResultBy"] == "OutputOrder")
    check("metadata does NOT emit fullName", "fullName" not in body)
    check("metadata synthesizes conditionCriteria from INPUT sequences",
          body.get("conditionCriteria") == "1 AND 2", body.get("conditionCriteria"))
    check("metadata always emits the 4 default bools",
          {"doesConsiderNullValue", "hasIncrementalSyncFailed",
           "isIncrementalSyncEnabled", "isVersioned"} <= set(body))
    cols = body["decisionTableParameters"]
    inp = [c for c in cols if c["usage"] == "INPUT"][0]
    out = [c for c in cols if c["usage"] == "OUTPUT"][0]
    check("metadata INPUT column keeps operator+sequence",
          inp.get("operator") == "Equals" and inp.get("sequence") == 1)
    check("metadata OUTPUT column drops operator+sequence",
          "operator" not in out and "sequence" not in out)
    check("metadata usage stays UPPER-case", inp["usage"] == "INPUT")
    check("metadata preserves sourceConditionLogic", body.get("sourceConditionLogic") == "1")
    check("metadata preserves documented parameter fields",
          inp.get("decimalScale") == 2 and inp.get("isPriorityField") is True
          and inp.get("length") == 80, inp)


def test_translator_tooling():
    print("test_translator_tooling")
    body = _payload.to_tooling(_cost_book_spec())
    check("tooling wraps FullName", body.get("FullName") == "RLM_CostBookEntries")
    check("tooling nests Metadata body", isinstance(body.get("Metadata"), dict))
    check("tooling Metadata carries columns",
          len(body["Metadata"]["decisionTableParameters"]) == 3)
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


def test_translator_csv_upload():
    print("test_translator_csv_upload")
    spec = _csv_upload_spec()
    # Metadata/Tooling body keeps dataSourceType=CsvUpload + sourceObject="CSV".
    meta = _payload.to_metadata(spec)
    check("metadata CsvUpload keeps dataSourceType",
          meta.get("dataSourceType") == "CsvUpload", meta.get("dataSourceType"))
    check("metadata CsvUpload carries sourceObject='CSV'",
          meta.get("sourceObject") == "CSV", meta.get("sourceObject"))
    check("metadata CsvUpload keeps both columns",
          len(meta["decisionTableParameters"]) == 2)


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
# _lifecycle — explicit lifecycle transitions (no org, no sleep)
# --------------------------------------------------------------------------- #


def test_activate_deactivate_csv_upload_is_version_first():
    print("test_activate_deactivate_csv_upload_is_version_first")
    # A CsvUpload table's own Status is a platform-derived mirror of its file-
    # import version's versionStatus — activate()/deactivate() must PATCH the
    # Connect versions endpoint, not the Tooling DecisionTable.Metadata.status.
    fake = _LifecycleFake(status="Draft", data_source_type="CsvUpload")
    engine = LifecycleEngine(fake, max_wait_seconds=1)

    engine.activate("0lDxx0000000001AAA")
    check("csv activate PATCHes the version, not Metadata.status",
          fake.connect_calls == [("PATCH", f"{DEFINITIONS_PATH}/0lDxx0000000001AAA/versions/1",
                                   {"versionStatus": "Active"})],
          fake.connect_calls)
    check("csv activate never PATCHed Tooling Metadata.status", fake.status_sets == [],
          fake.status_sets)
    check("csv activate PATCHed the Connect version's versionStatus",
          fake.version_status_sets == ["Active"], fake.version_status_sets)
    check("table Status cascaded to Active via the fake's version PATCH",
          fake.status == "Active")

    fake.connect_calls.clear()
    engine.deactivate("0lDxx0000000001AAA")
    check("csv deactivate PATCHes the version, not Metadata.status",
          fake.connect_calls == [("PATCH", f"{DEFINITIONS_PATH}/0lDxx0000000001AAA/versions/1",
                                   {"versionStatus": "Inactive"})],
          fake.connect_calls)
    check("csv deactivate never PATCHed Tooling Metadata.status", fake.status_sets == [],
          fake.status_sets)
    check("csv deactivate PATCHed the Connect version's versionStatus",
          fake.version_status_sets == ["Active", "Inactive"], fake.version_status_sets)
    check("table Status cascaded to Inactive via the fake's version PATCH",
          fake.status == "Inactive")


def test_activate_deactivate_sobject_is_table_first():
    print("test_activate_deactivate_sobject_is_table_first")
    # Non-CsvUpload tables are unaffected by the version-first branch — they
    # still PATCH Metadata.status directly (regression guard for the existing
    # SingleSobject/MultiSobject/etc. behavior).
    fake = _LifecycleFake(status="Draft", data_source_type="SingleSobject")
    engine = LifecycleEngine(fake, max_wait_seconds=1)

    engine.activate("0lDxx0000000001AAA")
    check("sobject activate PATCHes Metadata.status, not a version",
          fake.status_sets == ["Active"], fake.status_sets)
    check("sobject activate never called Connect", fake.connect_calls == [],
          fake.connect_calls)


def test_wait_for_status_timeout_message():
    print("test_wait_for_status_timeout_message")
    restore = _no_sleep()
    try:
        # Activation timeout: the table never leaves Inactive while we poll for Active.
        act_fake = _LifecycleFake(status="Inactive")
        act_msg = None
        try:
            LifecycleEngine(act_fake, max_wait_seconds=1, poll_interval_seconds=1) \
                .wait_for_status("0lDxx0000000001AAA", "Active")
        except LifecycleError as exc:
            act_msg = str(exc)
        # Deactivation timeout: the table stays Active while we poll for Inactive.
        deact_fake = _LifecycleFake(status="Active")
        deact_msg = None
        try:
            LifecycleEngine(deact_fake, max_wait_seconds=1, poll_interval_seconds=1) \
                .wait_for_status("0lDxx0000000001AAA", "Inactive")
        except LifecycleError as exc:
            deact_msg = str(exc)
    finally:
        restore()
    check("activation timeout reports target and last status",
          act_msg and "Status=Active" in act_msg and "'Inactive'" in act_msg, act_msg)
    check("deactivation timeout reports target and last status",
          deact_msg and "Status=Inactive" in deact_msg and "'Active'" in deact_msg,
          deact_msg)


def test_refresh_uses_platform_flag():
    print("test_refresh_uses_platform_flag")
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



# --------------------------------------------------------------------------- #
# Mutator CLIs — preview-vs-confirm gating via the fake transport (no org)
# --------------------------------------------------------------------------- #

def test_create_cli_tooling_preview_vs_confirm(tmp_spec):
    print("test_create_cli_tooling_preview_vs_confirm")
    # Preview: dry_run transport → no mutation recorded.
    fake_p = _FakeTransport(dry_run=True)
    rc, out = _run_cli_with_fake(
        create_cli, ["--target-org", "x", "--spec", tmp_spec, "--json"], fake_p)
    check("create preview exits 0", rc == 0, out[:300])
    check("create preview performs NO mutation", fake_p.mutations == [], fake_p.mutations)
    check("create preview reports dryRun=True", json.loads(out).get("dryRun") is True)
    # Confirm: non-dry transport → a Tooling POST is executed + recorded.
    fake_c = _FakeTransport(dry_run=False)
    rc, out = _run_cli_with_fake(
        create_cli, ["--target-org", "x", "--spec", tmp_spec,
                     "--confirm", "--json"], fake_c)
    check("create confirm exits 0", rc == 0, out[:300])
    check("create confirm records a POST DecisionTable",
          any(m[0] == "POST" and m[1] == "tooling/DecisionTable" for m in fake_c.mutations),
          fake_c.mutations)
    check("create confirm reports dryRun=False", json.loads(out).get("dryRun") is False)


def test_create_cli_honors_requested_active_status(tmp_spec):
    print("test_create_cli_honors_requested_active_status")
    # The platform is the authority: create sends the spec's requested status AS-IS
    # (no Draft-then-activate two-step, no GET-back verifier). tmp_spec's status is
    # Active, so the single definition POST carries Metadata.status == "Active", and
    # the CLI then polls wait_for_status past the async ActivationInProgress.
    fake = _FakeTransport(dry_run=False)
    rc, out = _run_cli_with_fake(
        create_cli, ["--target-org", "x", "--spec", tmp_spec,
                     "--confirm", "--json"], fake)
    check("create-Active exits 0", rc == 0, out[:300])
    posts = [m for m in fake.mutations if m[0] == "POST" and m[1] == "tooling/DecisionTable"]
    check("a single definition POST carries the requested Active status",
          len(posts) == 1 and posts[0][2].get("Metadata", {}).get("status") == "Active",
          [p[2].get("Metadata", {}).get("status") for p in posts])
    check("create does NOT do a Draft-then-activate two-step (no status PATCH)",
          not any(m[0] == "PATCH" for m in fake.mutations), fake.mutations)
    summary = json.loads(out)
    check("summary reports the requested status and the created id",
          summary.get("requestedStatus") == "Active" and bool(summary.get("id")),
          summary)


def test_create_cli_failure_emits_json_with_error(tmp_spec):
    print("test_create_cli_failure_emits_json_with_error")
    # A rejected write (the platform is the authority — e.g. it refuses the status)
    # must exit 1 and still emit the structured --json summary carrying the error,
    # so a caller can read a clean failure rather than an empty stdout.
    fake = _FakeTransport(dry_run=False)
    orig = fake.tooling_sobject

    def _boom(method, sobject, record_id=None, suffix=None, body=None, **kw):
        if method.upper() == "POST" and sobject == "DecisionTable":
            raise DecisionTableClientError(
                "INVALID_INPUT: rejected", error_codes=["INVALID_INPUT"])
        return orig(method, sobject, record_id=record_id, suffix=suffix, body=body, **kw)

    fake.tooling_sobject = _boom
    rc, out = _run_cli_with_fake(
        create_cli, ["--target-org", "x", "--spec", tmp_spec,
                     "--confirm", "--json"], fake)
    check("create failure exits 1", rc == 1, (rc, out[:300]))
    summary = json.loads(out)
    check("failure summary carries the error string",
          "rejected" in (summary.get("error") or ""), summary)


def test_create_cli_generate_only_no_org(tmp_spec, tmp_out_xml):
    print("test_create_cli_generate_only_no_org")
    fake = _FakeTransport(dry_run=True)
    rc, out = _run_cli_with_fake(
        create_cli, ["--spec", tmp_spec, "--generate-only", tmp_out_xml, "--json"], fake)
    check("generate-only exits 0", rc == 0, out[:300])
    check("generate-only performs NO org mutation", fake.mutations == [])
    produced = Path(tmp_out_xml).read_text(encoding="utf-8")
    check("generate-only wrote a DecisionTable XML",
          produced.startswith('<?xml') and "<DecisionTable" in produced, produced[:80])


def test_create_cli_generate_only_rejects_malformed_text(tmp_path_factory):
    print("test_create_cli_generate_only_rejects_malformed_text")
    spec_path = tmp_path_factory("malformed_generate_spec.json")
    output_path = tmp_path_factory("malformed.decisionTable-meta.xml")
    Path(spec_path).write_text(
        json.dumps(_cost_book_spec(conditionCriteria=["1"])), encoding="utf-8"
    )
    fake = _FakeTransport(dry_run=True)
    rc, out = _run_cli_with_fake(
        create_cli,
        ["--spec", spec_path, "--generate-only", output_path, "--json"],
        fake,
    )
    check("malformed generate-only exits nonzero", rc == 1, (rc, out[:300]))
    check("malformed generate-only writes no XML", not Path(output_path).exists())
    check("malformed generate-only performs no org mutation", fake.mutations == [])
    payload = json.loads(out)
    check("malformed generate-only emits a JSON error", bool(payload.get("error")), payload)


def test_create_cli_requires_target_org(tmp_spec):
    print("test_create_cli_requires_target_org")
    fake = _FakeTransport(dry_run=True)
    rc, out = _run_cli_with_fake(
        create_cli, ["--spec", tmp_spec, "--json"], fake)
    check("org create without --target-org exits 2", rc == 2, rc)
    payload = json.loads(out)
    check("missing target-org error emits JSON",
          payload.get("action") == "create" and bool(payload.get("error")), payload)


def test_create_cli_invalid_spec_blocks(tmp_path_factory):
    print("test_create_cli_invalid_spec_blocks")
    bad = tmp_path_factory("bad_spec.json")
    Path(bad).write_text(json.dumps({"dataSourceType": "SingleSobject"}), encoding="utf-8")
    fake = _FakeTransport(dry_run=False)
    rc, _ = _run_cli_with_fake(
        create_cli, ["--target-org", "x", "--spec", bad, "--confirm"],
        fake)
    check("invalid spec exits 1", rc == 1, rc)
    check("invalid spec performs NO mutation", fake.mutations == [], fake.mutations)


def test_create_cli_premutation_failures_emit_json(tmp_path_factory):
    print("test_create_cli_premutation_failures_emit_json")
    # --json advertises structured result output, and the mutation-failure path already
    # emits JSON. A caller passing --json must get the SAME contract on the PRE-mutation
    # failure phases (unreadable spec, schema rejection) — valid JSON on stdout carrying
    # "error" — never empty stdout that forces it to switch to stderr parsing based on
    # which phase failed. Both inputs below are realistic automation mistakes: a spec
    # path that doesn't exist, and a well-formed-but-invalid spec.
    fake = _FakeTransport(dry_run=False)
    # (a) unreadable spec file.
    rc, out = _run_cli_with_fake(
        create_cli, ["--target-org", "x", "--spec", tmp_path_factory("does_not_exist.json"),
                     "--confirm", "--json"], fake)
    check("missing spec exits 1", rc == 1, rc)
    payload = json.loads(out)  # must be valid JSON, not empty stdout
    check("missing-spec JSON carries an error", bool(payload.get("error")), payload)
    check("missing-spec performs NO mutation", fake.mutations == [], fake.mutations)
    # (b) schema-invalid spec (missing required fields).
    bad = tmp_path_factory("invalid_spec.json")
    Path(bad).write_text(json.dumps({"dataSourceType": "SingleSobject"}), encoding="utf-8")
    fake2 = _FakeTransport(dry_run=False)
    rc2, out2 = _run_cli_with_fake(
        create_cli, ["--target-org", "x", "--spec", bad, "--confirm", "--json"], fake2)
    check("invalid spec exits 1", rc2 == 1, rc2)
    payload2 = json.loads(out2)
    check("invalid-spec JSON carries an error and the action",
          bool(payload2.get("error")) and payload2.get("action") == "create", payload2)
    check("invalid-spec performs NO mutation", fake2.mutations == [], fake2.mutations)
    # (c) generate-only output path is not writable (a directory, not a file).
    valid = Path(tmp_path_factory("valid_generate_spec.json"))
    valid.write_text(json.dumps(_cost_book_spec()), encoding="utf-8")
    output_dir = Path(tmp_path_factory("xml_output_dir"))
    output_dir.mkdir()
    fake3 = _FakeTransport(dry_run=True)
    rc3, out3 = _run_cli_with_fake(
        create_cli,
        ["--spec", str(valid), "--generate-only", str(output_dir), "--json"],
        fake3,
    )
    check("generate-only write failure exits 1", rc3 == 1, (rc3, out3[:300]))
    payload3 = json.loads(out3)
    check("generate-only write failure emits JSON",
          payload3.get("generateOnly") == str(output_dir)
          and bool(payload3.get("error")), payload3)


def test_update_cli_returns_platform_error(tmp_spec):
    print("test_update_cli_returns_platform_error")
    fake = _FakeTransport(table=_table_row(Status="Active"), dry_run=False)
    attempted = []
    original = fake.tooling_sobject

    def _reject_active(method, sobject, record_id=None, suffix=None, body=None, **kw):
        if method.upper() == "PATCH" and sobject == "DecisionTable":
            attempted.append((method, sobject, body))
            raise DecisionTableClientError(
                "FIELD_NOT_UPDATABLE: Can't edit an active Decision Table",
                error_codes=["FIELD_NOT_UPDATABLE"],
            )
        return original(method, sobject, record_id=record_id, suffix=suffix,
                        body=body, **kw)

    fake.tooling_sobject = _reject_active
    rc, out = _run_cli_with_fake(
        update_cli,
        ["--target-org", "x", "--spec", tmp_spec, "--confirm", "--json"],
        fake,
    )
    payload = json.loads(out)
    check("active update returns the platform failure", rc == 1 and len(attempted) == 1,
          (rc, attempted))
    check("active update JSON returns the platform error unchanged",
          payload.get("error") ==
          "FIELD_NOT_UPDATABLE: Can't edit an active Decision Table", payload)


def test_update_cli_sends_one_patch(tmp_spec):
    print("test_update_cli_sends_one_patch")
    fake = _FakeTransport(table=_table_row(Status="Inactive"), dry_run=False)
    rc, _ = _run_cli_with_fake(
        update_cli, ["--target-org", "x", "--spec", tmp_spec, "--confirm"], fake)
    check("inactive update exits 0", rc == 0, rc)
    patches = [m for m in fake.mutations if m[0] == "PATCH" and m[1] == "tooling/DecisionTable"]
    check("update sends exactly one Tooling PATCH", len(patches) == 1, patches)
    check("update stamps the resolved live status",
          patches[0][2]["Metadata"].get("status") == "Inactive", patches)
    check("update PATCH carries the complete definition",
          "decisionTableParameters" in patches[0][2]["Metadata"], patches)


def test_update_cli_missing_resolved_status_fails_closed(tmp_spec):
    print("test_update_cli_missing_resolved_status_fails_closed")
    fake = _FakeTransport(table=_table_row(Status=None), dry_run=False)
    rc, out = _run_cli_with_fake(
        update_cli, ["--target-org", "x", "--spec", tmp_spec, "--confirm"], fake)
    check("update with no resolved status exits 1", rc == 1, (rc, out[:300]))
    check("update with no resolved status performs NO definition PATCH",
          not any(m[0] == "PATCH" for m in fake.mutations), fake.mutations)


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


def test_refresh_cli_exits_nonzero_on_bad_outcomes():
    print("test_refresh_cli_exits_nonzero_on_bad_outcomes")
    cases = [
        ("isSuccess=false", [{"isSuccess": False, "outputValues": {"Status": None}}]),
        ("isSuccess absent", [{"outputValues": {"Status": "Queued"}}]),
        ("isSuccess=null", [{"isSuccess": None, "outputValues": {"Status": "Queued"}}]),
        ("isSuccess=true, status not Queued",
         [{"isSuccess": True, "outputValues": {"Status": "InProgress"}}]),
    ]
    for label, refresh_response in cases:
        fake = _FakeTransport(dry_run=False, refresh_response=refresh_response)
        rc, out = _run_cli_with_fake(
            refresh_cli, ["--target-org", "x", "--developer-name", "RLM_CostBookEntries",
                          "--confirm", "--json"], fake)
        check(f"refresh confirm exits 1 on {label}", rc == 1, (label, out[:300]))
        payload = json.loads(out)
        check(f"refresh {label} emits one JSON failure with the raw result",
              bool(payload.get("error")) and payload.get("result", {}).get("raw")
              == refresh_response, payload)


def _csv_transport(**over):
    """A fake transport shaped like a CsvUpload table for the upload-CLI tests."""
    kw = dict(table=_table_row(name="RLM_CsvUploadTable", SourceObject="CSV"),
              metadata=_sample_metadata(dataSourceType="CsvUpload", sourceObject="CSV"),
              params=[_param("INPUT", "Region"),
                      _param("OUTPUT", "DiscountPercent", DataType="Percent")])
    kw.update(over)
    return _FakeTransport(**kw)


def test_upload_header_validation():
    print("test_upload_header_validation")
    defn = _resolve.load_definition(_csv_transport(), "RLM_CsvUploadTable")
    missing, extra = upload_cli._check_headers(["Region", "Unexpected"], defn)
    check("header validation reports the missing table column",
          missing == ["DiscountPercent"], missing)
    check("header validation reports the unexpected CSV column",
          extra == ["Unexpected"], extra)


def test_upload_header_validation_ignores_rowcriteria():
    print("test_upload_header_validation_ignores_rowcriteria")
    # The CSV file contract is INPUT/OUTPUT headers only. A ROWCRITERIA column is a
    # definition-level row filter, NOT a file column — a CSV of the INPUT+OUTPUT
    # headers must validate clean, and a header matching the ROWCRITERIA field is
    # "extra" (a warning), never "missing" (a fatal reject).
    t = _csv_transport(params=[
        _param("INPUT", "Region"),
        _param("OUTPUT", "Discount", DataType="Percent"),
        _param("ROWCRITERIA", "InternalRule")])
    defn = _resolve.load_definition(t, "RLM_CsvUploadTable")
    missing, extra = upload_cli._check_headers(["Region", "Discount"], defn)
    check("ROWCRITERIA is not a required CSV header", missing == [], missing)
    check("documented INPUT/OUTPUT CSV validates clean", extra == [], extra)
    # A CSV that DOES include the ROWCRITERIA field → extra (warning), not missing.
    missing2, extra2 = upload_cli._check_headers(["Region", "Discount", "InternalRule"], defn)
    check("a ROWCRITERIA header is extra, not missing",
          missing2 == [] and extra2 == ["InternalRule"], (missing2, extra2))


def test_upload_cli_missing_header_blocks(tmp_csv):
    print("test_upload_cli_missing_header_blocks")
    bad_csv = str(Path(tmp_csv).with_name("missing_output_header.csv"))
    Path(bad_csv).write_text("Region\nNorth\n", encoding="utf-8")
    fake = _csv_transport(dry_run=False)
    rc, out = _run_cli_with_fake(
        upload_cli, ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
                     "--csv", bad_csv, "--confirm"], fake)
    check("upload with a missing definition header exits 1", rc == 1, out[:300])
    check("upload with a missing definition header performs no mutation",
          fake.mutations == [], fake.mutations)


def test_upload_cli_utf8_bom_header_accepted(tmp_csv):
    print("test_upload_cli_utf8_bom_header_accepted")
    # Excel writes UTF-8 CSVs with a leading BOM (U+FEFF) by default. Without BOM-aware
    # reading the first header parses as "﻿Region", so header validation reports the
    # real column (Region) missing plus a phantom extra ("﻿Region") and refuses an
    # otherwise-valid file. _read_csv opens files as utf-8-sig, so the BOM is consumed and
    # the upload proceeds. Encode the fixture WITH a BOM to reproduce the Excel case.
    bom_csv = str(Path(tmp_csv).with_name("bom_rows.csv"))
    Path(bom_csv).write_text("Region,DiscountPercent\nNorth,10\n", encoding="utf-8-sig")
    # Sanity: the file really begins with the BOM bytes.
    check("fixture CSV starts with a UTF-8 BOM",
          Path(bom_csv).read_bytes().startswith(b"\xef\xbb\xbf"))
    fake = _csv_transport(dry_run=False)
    rc, out = _run_cli_with_fake(
        upload_cli, ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
                     "--csv", bom_csv, "--confirm", "--json"], fake)
    check("BOM CSV uploads (exit 0)", rc == 0, out[:300])
    # The header check saw a clean "Region" (no phantom extra, no missing), so the two-phase
    # upload ran: a ContentVersion insert + a /file POST.
    check("BOM CSV inserts a ContentVersion and POSTs /file",
          any(m[0] == "POST" and m[1] == "sobjects/ContentVersion" for m in fake.mutations)
          and any(m[0] == "POST" and "/file" in m[1] for m in fake.mutations),
          fake.mutations)
    # And the parsed header used for validation carries no BOM.
    _text, header = upload_cli._read_csv(bom_csv)
    check("_read_csv strips the BOM from the first header",
          header[:2] == ["Region", "DiscountPercent"], header)


def test_upload_cli_preview_vs_confirm(tmp_csv):
    print("test_upload_cli_preview_vs_confirm")
    # Preview (no --confirm): dry-run transport → no ContentVersion / /file mutation.
    fake_p = _csv_transport(dry_run=True)
    rc, out = _run_cli_with_fake(
        upload_cli, ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
                     "--csv", tmp_csv, "--json"], fake_p)
    check("upload preview exits 0", rc == 0, out[:300])
    check("upload preview performs NO mutation", fake_p.mutations == [], fake_p.mutations)
    check("upload preview reports dryRun=True", json.loads(out).get("dryRun") is True)
    # Confirm: non-dry transport → a ContentVersion POST then a /file POST.
    fake_c = _csv_transport(dry_run=False)
    rc, out = _run_cli_with_fake(
        upload_cli, ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
                     "--csv", tmp_csv, "--confirm", "--json"], fake_c)
    check("upload confirm exits 0", rc == 0, out[:300])
    check("upload confirm inserts a ContentVersion",
          any(m[0] == "POST" and m[1] == "sobjects/ContentVersion" for m in fake_c.mutations),
          fake_c.mutations)
    file_posts = [m for m in fake_c.mutations if m[0] == "POST" and "/file" in m[1]]
    check("upload confirm POSTs the fileId to the /file sub-resource",
          len(file_posts) == 1, fake_c.mutations)
    check("upload confirm POSTs a bare append body (fileId only, no deleteAllRows)",
          file_posts and file_posts[0][2] == {"fileId": "068xx0000000001AAA"}, file_posts)
    summary = json.loads(out)
    check("upload confirm reports platform completion",
          summary.get("dryRun") is False and summary.get("uploadStatus") == "Completed",
          summary)


def test_upload_cli_file_submission_failure_emits_fileid(tmp_csv):
    print("test_upload_cli_file_submission_failure_emits_fileid")
    # Preserve the ContentVersion id when submission fails so callers can clean up.
    fake = _csv_transport(dry_run=False)

    def _fail_file_post(record_id, file_id, *, dry_run=None):
        raise DecisionTableClientError("file sub-resource POST rejected",
                                       error_codes=["UNKNOWN_EXCEPTION"])

    fake.upload_decision_table_csv = _fail_file_post
    rc, out = _run_cli_with_fake(
        upload_cli, ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
                     "--csv", tmp_csv, "--confirm", "--json"], fake)
    check("file submission failure exits 1", rc == 1, (rc, out[:300]))
    check("ContentVersion insert still happened",
          any(m[1] == "sobjects/ContentVersion" for m in fake.mutations), fake.mutations)
    summary = json.loads(out)
    check("the --json failure summary carries the fileId (orphan to clean up)",
          summary.get("fileId") == "068xx0000000001AAA", summary)
    check("the --json failure summary names the failing phase + error",
          summary.get("phase") == "file-upload"
          and "rejected" in (summary.get("error") or ""), summary)


def _no_sleep():
    """Swap _lifecycle.time.sleep for a no-op; returns a restore() callable."""
    orig = _lifecycle.time.sleep
    _lifecycle.time.sleep = lambda *a, **k: None
    return lambda: setattr(_lifecycle.time, "sleep", orig)


def test_upload_cli_waits_for_new_terminal_status(tmp_csv):
    print("test_upload_cli_waits_for_new_terminal_status")
    metadata = _sample_metadata(
        dataSourceType="CsvUpload", sourceObject="CSV", uploadStatus="Completed"
    )
    fake = _csv_transport(
        dry_run=False, metadata=metadata,
        upload_statuses=["Completed", "UploadInProgress", "Completed"],
    )
    rc, out = _run_cli_with_fake(
        upload_cli, ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
                     "--csv", tmp_csv, "--confirm", "--json"], fake)
    check("upload exits 0", rc == 0, out[:300])
    summary = json.loads(out)
    check("upload does not accept a stale preceding terminal status",
          summary.get("uploadStatus") == "Completed" and fake.upload_statuses == ["Completed"],
          (summary, fake.upload_statuses))
    check("upload did exactly two mutations (ContentVersion + /file)",
          [m[0] for m in fake.mutations] == ["POST", "POST"]
          and fake.mutations[0][1] == "sobjects/ContentVersion"
          and "/file" in fake.mutations[1][1], fake.mutations)


def test_upload_cli_returns_platform_terminal_errors(tmp_csv):
    print("test_upload_cli_returns_platform_terminal_errors")
    for terminal in ("CompletedWithErrors", "Failed"):
        fake = _csv_transport(
            dry_run=False, upload_statuses=["UploadInProgress", terminal]
        )
        rc, out = _run_cli_with_fake(
            upload_cli,
            ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
             "--csv", tmp_csv, "--confirm", "--json"],
            fake,
        )
        summary = json.loads(out)
        check(f"upload exits 1 on {terminal}", rc == 1, (terminal, out[:300]))
        check(f"upload returns platform status {terminal}",
              summary.get("uploadStatus") == terminal and terminal in summary.get("error", ""),
              summary)


def test_upload_cli_times_out_on_stale_status(tmp_csv):
    print("test_upload_cli_times_out_on_stale_status")
    metadata = _sample_metadata(
        dataSourceType="CsvUpload", sourceObject="CSV", uploadStatus="Completed"
    )
    fake = _csv_transport(
        dry_run=False, metadata=metadata, upload_statuses=["Completed"]
    )
    rc, out = _run_cli_with_fake(
        upload_cli,
        ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
         "--csv", tmp_csv, "--confirm", "--json"],
        fake,
    )
    summary = json.loads(out)
    check("upload exits 1 when no new status is observed", rc == 1, (rc, out[:300]))
    check("upload timeout reports the stale platform status",
          "last seen: 'Completed'" in summary.get("error", ""), summary)


def test_upload_cli_missing_csv_errors():
    print("test_upload_cli_missing_csv_errors")
    fake = _csv_transport(dry_run=False)
    rc, _ = _run_cli_with_fake(
        upload_cli, ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
                     "--csv", "/nonexistent/path/rows.csv", "--confirm"], fake)
    check("upload with a missing CSV exits 1", rc == 1, rc)
    check("upload with a missing CSV performs NO mutation", fake.mutations == [], fake.mutations)


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


def test_delete_cli_returns_platform_error():
    print("test_delete_cli_returns_platform_error")
    fake = _FakeTransport(table=_table_row(Status="Active"), dry_run=False)
    attempted = []
    original = fake.tooling_sobject

    def _reject_active(method, sobject, record_id=None, suffix=None, body=None, **kw):
        if method.upper() == "DELETE" and sobject == "DecisionTable":
            attempted.append(record_id)
            raise DecisionTableClientError(
                "INVALID_OPERATION: deactivate the table first",
                error_codes=["INVALID_OPERATION", "DEPENDENCY_EXISTS"],
            )
        return original(method, sobject, record_id=record_id, suffix=suffix,
                        body=body, **kw)

    fake.tooling_sobject = _reject_active
    rc, out = _run_cli_with_fake(
        delete_cli, ["--target-org", "x", "--developer-name", "RLM_CostBookEntries",
                     "--confirm", "--json"], fake)
    payload = json.loads(out)
    check("active delete returns the platform failure",
          rc == 1 and attempted == ["0lDxx0000000001AAA"], (rc, attempted))
    check("active delete JSON returns the platform error unchanged",
          payload.get("error") == "INVALID_OPERATION: deactivate the table first",
          payload)


def test_delete_cli_failure_emits_json():
    print("test_delete_cli_failure_emits_json")
    # A DELETE that the platform rejects (e.g. the table is still referenced by an
    # active Expression Set) surfaces as a controlled error + exit 1, and the
    # --json path still emits a structured summary with deleted=false.
    fake = _FakeTransport(table=_table_row(Status="Inactive"), dry_run=False)
    original = fake.tooling_sobject

    def _fail_delete(method, sobject, record_id=None, suffix=None, body=None, **kw):
        if method.upper() == "DELETE" and sobject == "DecisionTable":
            raise DecisionTableClientError("table is still referenced")
        return original(method, sobject, record_id=record_id, suffix=suffix,
                        body=body, **kw)

    fake.tooling_sobject = _fail_delete
    rc, out = _run_cli_with_fake(
        delete_cli,
        ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
         "--confirm", "--json"],
        fake,
    )
    check("failed delete exits 1", rc == 1, (rc, out[:300]))
    failure = json.loads(out)
    check("failed delete emits a --json summary with deleted=false",
          failure.get("deleted") is False and failure.get("action") == "delete",
          failure)


def main():
    import tempfile

    tmpdir = tempfile.mkdtemp(prefix="dt_toolkit_tests_")

    def _tmp(name):
        return str(Path(tmpdir) / name)

    # A shared valid spec file for the mutator CLI tests.
    spec_path = _tmp("cost_book_spec.json")
    Path(spec_path).write_text(json.dumps(_cost_book_spec()), encoding="utf-8")
    out_xml = _tmp("out.decisionTable-meta.xml")
    # A shared CSV file for the CsvUpload upload-CLI tests (headers = column fieldNames).
    csv_path = _tmp("rows.csv")
    Path(csv_path).write_text("Region,DiscountPercent\nNorth,10\nSouth,5\n", encoding="utf-8")

    simple = (test_schema_catalogs, test_validate_spec_clean, test_validate_spec_errors,
              test_validate_spec_full_name_shape,
              test_validate_spec_duplicate_and_unknown,
              test_validate_spec_duplicate_source_criterion_sequence,
              test_validate_spec_duplicate_input_sequence,
              test_validate_spec_boolean_typo,
              test_validate_spec_rejects_non_string_enum_values,
              test_validate_spec_rejects_malformed_scalar_enum_and_text,
              test_validate_spec_csv_upload,
              test_validate_spec_create_and_structural_errors,
              test_validate_spec_usage_is_strict,
              test_payload_miscased_usage_is_blocked_upstream,
              test_resolve_query_builders,
              test_resolve_missing_raises, test_load_definition_assembly,
              test_diff_identical, test_diff_detects_changes,
              test_dump_single_sobject, test_dump_csv_upload_rows, test_dump_csv_upload_empty,
              test_dump_csv_upload_gated,
              test_dump_csv_upload_unclassified_error_propagates,
              test_dump_csv_upload_auth_and_generic_errors_propagate,
              test_dump_empty_source_note,
              test_dump_csv_upload_filter_drops_limit,
              test_dump_filter_ignored_on_non_csv, test_dump_cli_filter_flag,
              test_translator_csv_upload_all_types,
              test_trace_correlation, test_list_cli_json,
              test_describe_cli_grouped, test_trace_cli_json,
              # Translators + XML round-trip
              test_translator_metadata, test_translator_tooling,
              test_translator_csv_upload, test_metadata_xml_roundtrip,
              # Explicit lifecycle transitions
              test_activate_deactivate_csv_upload_is_version_first,
              test_activate_deactivate_sobject_is_table_first,
              test_wait_for_status_timeout_message,
              test_refresh_uses_platform_flag,
              # Mutator CLI activate/deactivate/refresh/delete gating
              test_activate_cli_preview_vs_confirm, test_activate_cli_skips_when_already_active,
              test_deactivate_cli_preview_vs_confirm, test_refresh_cli_preview_vs_confirm,
              test_refresh_cli_exits_nonzero_on_bad_outcomes,
              test_delete_cli_requires_confirm, test_delete_cli_returns_platform_error,
              test_delete_cli_failure_emits_json,
              # CsvUpload data-load CLI gating
              test_upload_header_validation,
              test_upload_header_validation_ignores_rowcriteria,
              test_upload_cli_missing_csv_errors)
    for fn in simple:
        fn()

    # Create/update CLI tests that need spec/output-file fixtures.
    test_create_cli_tooling_preview_vs_confirm(spec_path)
    test_create_cli_honors_requested_active_status(spec_path)
    test_create_cli_failure_emits_json_with_error(spec_path)
    test_create_cli_generate_only_no_org(spec_path, out_xml)
    test_create_cli_generate_only_rejects_malformed_text(_tmp)
    test_create_cli_requires_target_org(spec_path)
    test_create_cli_invalid_spec_blocks(_tmp)
    test_create_cli_premutation_failures_emit_json(_tmp)
    test_update_cli_returns_platform_error(spec_path)
    test_update_cli_sends_one_patch(spec_path)
    test_update_cli_missing_resolved_status_fails_closed(spec_path)
    # CsvUpload upload CLI (needs a CSV fixture).
    test_upload_cli_missing_header_blocks(csv_path)
    test_upload_cli_utf8_bom_header_accepted(csv_path)
    test_upload_cli_preview_vs_confirm(csv_path)
    test_upload_cli_file_submission_failure_emits_fileid(csv_path)
    test_upload_cli_waits_for_new_terminal_status(csv_path)
    test_upload_cli_returns_platform_terminal_errors(csv_path)
    test_upload_cli_times_out_on_stale_status(csv_path)

    import shutil
    shutil.rmtree(tmpdir, ignore_errors=True)

    print(f"\n{_PASS} passed, {_FAIL} failed.")
    return 1 if _FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
