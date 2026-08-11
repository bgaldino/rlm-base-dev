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
                 metadata=None, csv_data=None, upload_statuses=None,
                 refresh_response=None, dry_run=False):
        self.table = table if table is not None else _table_row()
        self.params = params if params is not None else [
            _param("INPUT", "ProductId"), _param("OUTPUT", "Cost", DataType="Currency")]
        self.links = links or []
        self.dataset_params = dataset_params or []
        self.criteria = criteria or []
        self.mappings = mappings or []
        self.source_rows = source_rows if source_rows is not None else [{"Id": "01txx", "Cost": 5}]
        self.connect_def = connect_def
        # Metadata complexvalue returned by the DecisionTable Tooling GET. None →
        # the default SingleSobject sample; pass a CsvUpload sample to exercise the
        # CSV branch.
        self.metadata = metadata
        # CsvUpload data-layer GET (.../{id}/data) response. None → an empty table
        # ({"rows": [], "totalRows": 0}); a dict → returned verbatim; an Exception
        # → raised (simulates a gated/disabled endpoint).
        self.csv_data = csv_data
        # Sequence of Metadata.uploadStatus values returned by successive Tooling
        # GETs (for the wait_for_upload_status poll). Each GET pops the next; the
        # last value sticks. None → the GET's metadata has no uploadStatus key.
        self.upload_statuses = list(upload_statuses) if upload_statuses else None
        # Override for the refreshDecisionTable action response (a list, matching
        # the real invocable-action envelope). None → the default success/Queued.
        self.refresh_response = refresh_response
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
            meta = self.metadata if self.metadata is not None else _sample_metadata()
            if self.upload_statuses:
                # Pop the next uploadStatus; the last value sticks (simulates the
                # async import reaching a terminal state across successive polls).
                nxt = (self.upload_statuses.pop(0) if len(self.upload_statuses) > 1
                       else self.upload_statuses[0])
                meta = dict(meta, uploadStatus=nxt)
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
            # A confirmed create is immediately visible to the GET-back verifier.
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
        if method.upper() in ("GET", "HEAD"):
            return self.connect_get(path)
        if self._skip_mutation(method, path, body):
            return {}
        if path.endswith("refreshDecisionTable"):
            if self.refresh_response is not None:
                return self.refresh_response
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

    # -- CSV Based Decision Table data layer (dataSourceType == CsvUpload) --

    def content_version_insert(self, title, csv_text, *,
                               path_on_client="decision_table_rows.csv", dry_run=None):
        # _skip_mutation records the executed mutation (or skips it under dry-run).
        if self._skip_mutation("POST", "sobjects/ContentVersion",
                               {"Title": title, "PathOnClient": path_on_client}):
            return {}
        return {"id": "068xx0000000001AAA", "success": True}

    def upload_decision_table_csv(self, record_id, file_id, *, delete_all_rows=False,
                                  version_number=None, dry_run=None):
        path = f"connect/business-rules/decision-table/{record_id}/file"
        if version_number is not None:
            path += f"?versionNumber={int(version_number)}"
        body = {"fileId": file_id, "deleteAllRows": bool(delete_all_rows)}
        if self._skip_mutation("POST", path, body):
            return {}
        return {"message": "We are uploading and processing the CSV file."}

    def get_decision_table_data(self, record_id, *, version_number=None,
                                row_filter=None, limit=None):
        # A read — always executes, even under dry_run.
        self.csv_data_calls.append({"record_id": record_id, "version_number": version_number,
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
    sleep). ``connect`` records DELETE/POST verbs for the delete/refresh paths."""

    def __init__(self, status="Active", *, dry_run=False, data_source_type="SingleSobject",
                 stall_confirmation=False, versions=None):
        self.status = status
        self.dry_run = dry_run
        self.data_source_type = data_source_type
        self.api_version = "67.0"
        self.target_org = "fake-org"
        self.logger = lambda *a, **k: None
        self.status_sets = []  # ordered list of statuses PATCHed via Tooling
        self.version_status_sets = []  # ordered list of versionStatus PATCHed via Connect
        self.connect_calls = []
        # When True, get_status's read reports a frozen pre-write value forever —
        # simulating a write that applied but whose confirmation poll never sees
        # the terminal state (eventual-consistency lag / a stuck poll).
        self.stall_confirmation = stall_confirmation
        self._reported_status = status
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
        self._status_reads = 0

    def _recompute_status_from_versions(self):
        self.status = ("Active" if any(
            v in ("Active", "ActivationInProgress") for v in self.versions.values())
            else "Inactive")

    def tooling_query(self, query):
        if "FROM DecisionTable" in query:
            self._status_reads += 1
            reported = self._reported_status if self.stall_confirmation else self.status
            return [{"Id": "0lDxx0000000001AAA", "Status": reported}]
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


def test_validate_spec_full_name_path_escape():
    print("test_validate_spec_full_name_path_escape")
    # fullName becomes a bare file-system segment
    # (<fullName>.decisionTable-meta.xml) in the metadata deploy temp dir — an
    # absolute-path or separator-bearing value must be rejected, not silently
    # accepted (it would write outside the temp SFDX project via os.path.join's
    # absolute-path-discards-prefix behavior).
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
    # F5: two INPUT columns sharing a sequence produce a degenerate derived
    # conditionCriteria like "1 AND 1" — one condition has no distinct column
    # reference. The dup-sequence guard previously covered only source criteria;
    # it must also reject duplicate INPUT sequences up front.
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
    # No path (update validation) — the live status is stamped by update.
    no_path = validate_spec(spec)
    check("update validation does not require spec status",
          not any(i.location == "status" for i in no_path.errors), no_path.format_report())
    # Metadata/Tooling create paths without status are blocked locally.
    for authoring_path in ("metadata", "tooling"):
        result = validate_spec(spec, path=authoring_path)
        check(f"{authoring_path} create without status errors",
              any(i.location == "status" for i in result.errors), result.format_report())
    # Metadata/Tooling create WITH status set is valid.
    with_status = validate_spec({**spec, "status": "Draft"}, path="metadata")
    check("metadata create with status set passes", with_status.passed,
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
    # can never silently write a wrong definition (drop operator/sequence + fail
    # GET-back) — the same fail-closed treatment unknown keys get.
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


def test_payload_miscased_usage_is_blocked_upstream():
    print("test_payload_miscased_usage_is_blocked_upstream")
    # A mis-cased "Input" would be treated as non-INPUT by the translator, dropping
    # operator/sequence from the write (demonstrated below). The DEFENSE against that
    # is strict-usage VALIDATION, which rejects the spec before it ever reaches the
    # translator — so the corrupt write is never attempted. (This is why usage must
    # error, not warn.) The GET-back verifier compares against the normalized payload
    # actually written, so it is not the layer that catches a mis-cased usage; if a
    # non-INPUT column legitimately drops operator, the verifier correctly does not
    # flag the (also-absent) operator as drift.
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
    check("identical → no dataset-link changes", not any(delta["datasetLinks"].values()), delta)
    check("identical → no dataset-parameter changes",
          not any(delta["datasetParameters"].values()), delta)
    check("identical → no source-criteria changes",
          not any(delta["sourceCriteria"].values()), delta)


def test_diff_detects_changes():
    print("test_diff_detects_changes")
    input_a = _param("INPUT", "ProductId", DomainObject="Product2")
    output_a = _param("OUTPUT", "Cost", DataType="Currency")
    input_b = _param("INPUT", "ProductId", DataType="Number", DomainObject="Product2")
    output_b = _param("OUTPUT", "Margin", DataType="Percent")
    link_a = {"Id": "0lX-A", "DeveloperName": "Products", "MasterLabel": "Products",
              "SetupName": "Products", "SourceObject": "Product2", "IsDefault": True,
              "Description": "Default product dataset"}
    link_b = dict(link_a, Id="0lX-B", IsDefault=False)
    a = {"table": _table_row(Status="Active"),
         "metadata": _sample_metadata(collectOperator="None"),
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
         "metadata": _sample_metadata(filterResultBy="Priority", collectOperator="Maximum"),
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


def test_dump_csv_upload_version_number_threads():
    print("test_dump_csv_upload_version_number_threads")
    # --version-number alone (no filter) → threaded through; limit is kept.
    t = _FakeTransport(
        table=_table_row(SourceObject="CSV"),
        metadata=_sample_metadata(dataSourceType="CsvUpload", sourceObject="CSV"),
        csv_data=_csv_all_types_data())
    defn = _resolve.load_definition(t, "RLM_CostBookEntries")
    dump_data(t, defn, limit=5, version_number=1)
    call = t.csv_data_calls[-1]
    check("version_number threads into the data GET", call["version_number"] == 1, call)
    check("version_number alone keeps the limit", call["limit"] == 5, call)


def test_dump_filter_version_ignored_on_non_csv():
    print("test_dump_filter_version_ignored_on_non_csv")
    # On a SingleSobject table --filter/--version-number are ignored with a note.
    t = _FakeTransport(source_rows=[{"Id": "01t1", "Cost": 5}])
    defn = _resolve.load_definition(t, "RLM_CostBookEntries")
    dump = dump_data(t, defn, limit=5, row_filter="Region:North", version_number=2)
    check("non-CsvUpload notes that filter/version were ignored",
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


def test_dump_cli_version_flag():
    print("test_dump_cli_version_flag")
    t = _FakeTransport(
        table=_table_row(SourceObject="CSV"),
        metadata=_sample_metadata(dataSourceType="CsvUpload", sourceObject="CSV"),
        csv_data=_csv_all_types_data())
    rc, out = _run_cli_with_fake(
        dump_cli, ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
                   "--version-number", "1", "--json"], t)
    check("dump --version-number exits 0", rc == 0, out[:300])
    check("dump --version-number threads version_number",
          t.csv_data_calls and t.csv_data_calls[-1]["version_number"] == 1, t.csv_data_calls)


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


def test_guarded_update_active_roundtrip():
    print("test_guarded_update_active_roundtrip")
    fake = _LifecycleFake(status="Active")
    engine = LifecycleEngine(fake, max_wait_seconds=1)
    calls = []
    engine.run_guarded_update(
        table_row={"Id": "0lDxx0000000001AAA", "Status": "Active"},
        mutate=lambda: calls.append("mutate"),
        activate_after=True, verb="update")
    check("guarded update called mutate once", calls == ["mutate"], calls)
    check("guarded update deactivated then reactivated",
          fake.status_sets == ["Inactive", "Active"], fake.status_sets)
    check("guarded update left the table Active", fake.status == "Active")


def test_guarded_update_csv_upload_composed_paths():
    print("test_guarded_update_csv_upload_composed_paths")
    record_id = "0lDxx0000000001AAA"

    success = _LifecycleFake(status="Active", data_source_type="CsvUpload")
    calls = []
    LifecycleEngine(success, max_wait_seconds=1).run_guarded_update(
        table_row={"Id": record_id, "Status": "Active"},
        mutate=lambda: calls.append("mutate"),
        activate_after=True,
        verb="update",
    )
    check("CsvUpload guarded update mutates once", calls == ["mutate"], calls)
    check("CsvUpload guarded update deactivates/reactivates the version",
          success.version_status_sets == ["Inactive", "Active"],
          success.version_status_sets)
    check("CsvUpload guarded update never PATCHes table Metadata.status",
          success.status_sets == [], success.status_sets)

    leave_off = _LifecycleFake(status="Active", data_source_type="CsvUpload")
    LifecycleEngine(leave_off, max_wait_seconds=1).run_guarded_update(
        table_row={"Id": record_id, "Status": "Active"},
        mutate=lambda: None,
        activate_after=False,
        verb="update",
    )
    check("CsvUpload guarded update honors leave-deactivated",
          leave_off.status == "Inactive"
          and leave_off.version_status_sets == ["Inactive"],
          leave_off.version_status_sets)

    rejected = _LifecycleFake(status="Active", data_source_type="CsvUpload")

    def _rejected_patch():
        raise DecisionTableClientError("tooling PATCH rejected")

    raised = False
    try:
        LifecycleEngine(rejected, max_wait_seconds=1).run_guarded_update(
            table_row={"Id": record_id, "Status": "Active"},
            mutate=_rejected_patch,
            activate_after=True,
            verb="update",
        )
    except DecisionTableClientError:
        raised = True
    check("CsvUpload rejected atomic update re-raises", raised)
    check("CsvUpload rejected atomic update restores the active version",
          rejected.status == "Active"
          and rejected.version_status_sets == ["Inactive", "Active"],
          rejected.version_status_sets)


def test_guarded_update_csv_upload_multi_version_roundtrip():
    print("test_guarded_update_csv_upload_multi_version_roundtrip")
    # A CsvUpload table with several versions where version 2 is the active one.
    # Deactivation resolves version 2 (the unique active one); reactivation must
    # re-use THAT version number, not re-resolve after v2 went Inactive (which
    # would strand the table Inactive — there is then no unique active version).
    record_id = "0lDxx0000000001AAA"
    fake = _LifecycleFake(
        status="Active", data_source_type="CsvUpload",
        versions=[{"versionNumber": 1, "versionStatus": "Inactive"},
                  {"versionNumber": 2, "versionStatus": "Active"}])
    calls = []
    LifecycleEngine(fake, max_wait_seconds=1).run_guarded_update(
        table_row={"Id": record_id, "Status": "Active"},
        mutate=lambda: calls.append("mutate"),
        activate_after=True,
        verb="update",
    )
    check("multi-version guarded update mutates once", calls == ["mutate"], calls)
    check("multi-version guarded update deactivated then reactivated version 2",
          fake.connect_calls == [
              ("PATCH", f"{DEFINITIONS_PATH}/{record_id}/versions/2", {"versionStatus": "Inactive"}),
              ("PATCH", f"{DEFINITIONS_PATH}/{record_id}/versions/2", {"versionStatus": "Active"})],
          fake.connect_calls)
    check("multi-version guarded update left version 2 Active",
          fake.versions == {1: "Inactive", 2: "Active"} and fake.status == "Active",
          fake.versions)


def test_guarded_update_leave_deactivated():
    print("test_guarded_update_leave_deactivated")
    fake = _LifecycleFake(status="Active")
    engine = LifecycleEngine(fake, max_wait_seconds=1)
    engine.run_guarded_update(
        table_row={"Id": "0lDxx0000000001AAA", "Status": "Active"},
        mutate=lambda: None, activate_after=False, verb="update")
    check("activate_after=False leaves table Inactive", fake.status == "Inactive")
    check("activate_after=False never reactivates", fake.status_sets == ["Inactive"])


def test_guarded_update_tooling_failure_reactivates():
    print("test_guarded_update_tooling_failure_reactivates")
    # An atomic Tooling PATCH that fails leaves the record byte-identical, so the
    # table IS reactivated — a failed edit never
    # knocks a live table offline. The failure is still re-raised.
    fake = _LifecycleFake(status="Active")
    engine = LifecycleEngine(fake, max_wait_seconds=1)

    def _boom():
        raise DecisionTableClientError("tooling PATCH rejected")

    raised = False
    try:
        engine.run_guarded_update(
            table_row={"Id": "0lDxx0000000001AAA", "Status": "Active"},
            mutate=_boom, activate_after=True, verb="update")
    except DecisionTableClientError:
        raised = True
    check("tooling-path failure re-raises", raised)
    check("tooling-path failure reactivates (record unchanged)",
          fake.status == "Active" and fake.status_sets == ["Inactive", "Active"],
          fake.status_sets)


def test_guarded_update_double_failure_chains_original_cause():
    print("test_guarded_update_double_failure_chains_original_cause")
    # F9: when the mutation fails AND the reactivation ALSO fails, the raised
    # LifecycleError must name BOTH — why the mutation failed and why the table is
    # still offline — and chain the original mutation failure as its __cause__ so a
    # caller printing the traceback sees the root cause, not just the reactivation
    # error. Deactivate succeeds against the fake; mutate raises; the reactivate step
    # is forced to fail by overriding engine.activate.
    fake = _LifecycleFake(status="Active")
    engine = LifecycleEngine(fake, max_wait_seconds=1)

    def _boom():
        raise DecisionTableClientError("tooling PATCH rejected")

    def _activate_fails(*a, **k):
        raise DecisionTableClientError("reactivation PATCH rejected")

    engine.activate = _activate_fails
    raised = None
    try:
        engine.run_guarded_update(
            table_row={"Id": "0lDxx0000000001AAA", "Status": "Active"},
            mutate=_boom, activate_after=True, verb="update")
    except LifecycleError as exc:
        raised = exc
    check("double failure raises LifecycleError", raised is not None, raised)
    check("double-failure message names the original mutation failure",
          raised and "tooling PATCH rejected" in str(raised), str(raised))
    check("double-failure message names the reactivation failure",
          raised and "reactivation also failed" in str(raised), str(raised))
    check("double failure chains the original mutation error as __cause__",
          raised and isinstance(raised.__cause__, DecisionTableClientError),
          raised.__cause__ if raised else None)


def test_delete_cli_deactivate_confirmation_timeout_still_reactivates():
    print("test_delete_cli_deactivate_confirmation_timeout_still_reactivates")
    # delete_decision_table.py marks the table `deactivated` BEFORE issuing the
    # deactivate PATCH, so if the write applies but its confirmation poll times out
    # (stall_confirmation freezes get_status), the guarded handler still skips the
    # DELETE and restores Active rather than abandoning the table mid-transition.
    fake = _LifecycleFake(status="Active", stall_confirmation=True)
    restore = _no_sleep()
    try:
        rc, out = _run_cli_with_fake(
            delete_cli,
            ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
             "--deactivate-first", "--confirm"],
            fake,
        )
    finally:
        restore()
    check("delete on an unconfirmed deactivation exits 1", rc == 1, (rc, out[:300]))
    check("delete was never attempted; table restored to Active",
          fake.status_sets == ["Inactive", "Active"], fake.status_sets)


def test_delete_cli_ambiguous_version_resolution_returns_controlled_error():
    print("test_delete_cli_ambiguous_version_resolution_returns_controlled_error")
    # The version-pinning lookup (resolve_guarded_version) does Tooling GETs and
    # deliberately raises LifecycleError for an ambiguous multi-version CsvUpload
    # table. It must run INSIDE the CLI's guarded try so that raise becomes a
    # controlled 'FAILED …' + exit 1, not an unhandled traceback that escapes
    # main() (and leaves --json callers with no result). Two Active versions make
    # resolve_guarded_version raise before anything is deactivated.
    fake = _LifecycleFake(
        status="Active", data_source_type="CsvUpload",
        versions=[{"versionNumber": 1, "versionStatus": "Active"},
                  {"versionNumber": 2, "versionStatus": "Active"}])
    escaped = None
    try:
        rc, out = _run_cli_with_fake(
            delete_cli,
            ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
             "--deactivate-first", "--confirm", "--json"],
            fake,
        )
    except BaseException as exc:  # noqa: BLE001 — the bug was an escaping exception
        escaped = exc
        rc, out = None, ""
    check("ambiguous version resolution does not escape main()", escaped is None, escaped)
    check("ambiguous version resolution returns exit 1 (controlled refusal)",
          rc == 1, (rc, out[:300]))
    check("nothing was deactivated before the resolution failed",
          fake.version_status_sets == [] and fake.status_sets == [],
          (fake.version_status_sets, fake.status_sets))
    # --json callers must still get a structured failure summary on the error path
    # (not an empty stdout / traceback) — the controlled-failure JSON contract.
    failure = json.loads(out)
    check("controlled failure emits a --json summary with deleted=false",
          failure.get("deleted") is False and failure.get("action") == "delete",
          failure)
    # resolve_guarded_version raised BEFORE any deactivation, so no rollback was
    # attempted — the tri-state reactivated is None ("not needed"), distinct from
    # False ("attempted and failed").
    check("the --json failure summary carries the error and no rollback",
          "unambiguous" in (failure.get("error") or "")
          and failure.get("reactivated") is None
          and failure.get("reactivationError") is None, failure)


def test_wait_for_status_timeout_message_is_operation_aware():
    print("test_wait_for_status_timeout_message_is_operation_aware")
    # The single wait_for_status poll confirms BOTH activation and deactivation, so
    # its timeout text must not hardcode "Activation is asynchronous" when confirming
    # Inactive, and it must not recommend a --max-wait flag that most reaching CLIs
    # (update/delete/deactivate) don't expose.
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
    check("activation timeout still says activation is asynchronous",
          act_msg and "Activation is asynchronous" in act_msg, act_msg)
    check("deactivation timeout does NOT claim activation is asynchronous",
          deact_msg and "Activation is asynchronous" not in deact_msg, deact_msg)
    check("deactivation timeout is worded for deactivation",
          deact_msg and "Deactivation" in deact_msg, deact_msg)
    check("neither timeout recommends a bare --max-wait flag callers may lack",
          "--max-wait" not in (act_msg or "") and "--max-wait" not in (deact_msg or ""),
          (act_msg, deact_msg))
    check("both timeouts point at a tool-agnostic re-check",
          "list_decision_tables.py" in (act_msg or "")
          and "list_decision_tables.py" in (deact_msg or ""), (act_msg, deact_msg))


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


def test_create_cli_honors_requested_active_status(tmp_spec):
    print("test_create_cli_honors_requested_active_status")
    # The platform is the authority: create sends the spec's requested status AS-IS
    # (no Draft-then-activate two-step, no GET-back verifier). tmp_spec's status is
    # Active, so the single definition POST carries Metadata.status == "Active", and
    # the CLI then polls wait_for_status past the async ActivationInProgress.
    fake = _FakeTransport(dry_run=False)
    rc, out = _run_cli_with_fake(
        create_cli, ["--target-org", "x", "--spec", tmp_spec,
                     "--path", "tooling", "--confirm", "--json"], fake)
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
                     "--path", "tooling", "--confirm", "--json"], fake)
    check("create failure exits 1", rc == 1, (rc, out[:300]))
    summary = json.loads(out)
    check("failure summary carries the error string",
          "rejected" in (summary.get("error") or ""), summary)


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
    check("deactivate-first PATCHes a definition body with columns",
          bool(defn_patches), defn_patches)
    check("definition edit stamps the live status (Inactive), never the spec's Active",
          any(p[2]["Metadata"].get("status") == "Inactive" for p in defn_patches),
          [p[2]["Metadata"].get("status") for p in defn_patches])


def test_update_cli_unreadable_live_status_fails_closed(tmp_spec):
    print("test_update_cli_unreadable_live_status_fails_closed")
    # _do_mutate() reads the table's live Status immediately before the definition
    # PATCH (a Tooling Metadata PATCH REQUIRES status). If that read returns NO row,
    # the CLI must FAIL CLOSED (LifecycleError → exit 1, no PATCH) rather than
    # silently reuse the stale pre-deactivation status (often Active) — stamping
    # which could re-activate the table mid-edit and defeat --leave-deactivated while
    # still exiting 0. On an Inactive table the CLI reaches _do_mutate directly.
    fake = _FakeTransport(table=_table_row(Status="Inactive"), dry_run=False)
    orig_query = fake.tooling_query

    def _query(q):
        # resolve_decision_table matches on DeveloperName (give it the row so
        # resolution succeeds); get_status matches on Id (return no row — the failure).
        if "FROM DecisionTable" in q and "WHERE Id =" in q:
            return []
        return orig_query(q)

    fake.tooling_query = _query
    rc, out = _run_cli_with_fake(
        update_cli, ["--target-org", "x", "--spec", tmp_spec, "--confirm"], fake)
    check("update with an unreadable live status exits 1", rc == 1, (rc, out[:300]))
    check("update with an unreadable live status performs NO definition PATCH",
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


def test_upload_cli_activate_version_read_failure_is_guarded(tmp_csv):
    print("test_upload_cli_activate_version_read_failure_is_guarded")
    # The --activate-version pre-check (get_version_status → a Tooling GET via
    # _file_import_versions) runs AFTER the upload already mutated the org. A
    # transient read failure there must NOT escape main() as a traceback and
    # suppress the accumulated --json summary — it becomes a WARNING + exit 1 with
    # the summary still emitted. Both DecisionTableClientError and LifecycleError
    # (missing/malformed Metadata) must be caught.
    fake = _csv_transport(
        dry_run=False,
        metadata=_sample_metadata(dataSourceType="CsvUpload", sourceObject="CSV"))
    orig_tooling = fake.tooling_sobject

    def _get_raises_after_upload(method, sobject, record_id=None, suffix=None, body=None, **kw):
        # Fail the version-status GET only AFTER the upload has run — load_definition
        # at the start also issues a Tooling GET, so gate the raise on the /file
        # upload mutation being recorded (the post-mutation read is the one at risk).
        if (method.upper() == "GET" and sobject == "DecisionTable"
                and any("/file" in m[1] for m in fake.mutations)):
            raise DecisionTableClientError(
                "transient status read failure", error_codes=["UNKNOWN_EXCEPTION"])
        return orig_tooling(method, sobject, record_id=record_id, suffix=suffix,
                            body=body, **kw)

    fake.tooling_sobject = _get_raises_after_upload
    escaped = None
    try:
        rc, out = _run_cli_with_fake(
            upload_cli,
            ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
             "--csv", tmp_csv, "--activate-version", "1", "--confirm", "--json"],
            fake)
    except BaseException as exc:  # noqa: BLE001 — the bug was an escaping exception
        escaped = exc
        rc, out = None, ""
    check("post-upload read failure does not escape main()", escaped is None, escaped)
    check("post-upload read failure returns exit 1", rc == 1, (rc, out[:300]))
    # The upload itself still happened and the JSON summary still emits (proving the
    # read failure was folded into the controlled exit, not a lost traceback).
    check("upload phases ran before the guarded read failure",
          any(m[1] == "sobjects/ContentVersion" for m in fake.mutations)
          and any("/file" in m[1] for m in fake.mutations), fake.mutations)
    summary = json.loads(out)
    check("the accumulated --json summary is still emitted on the read failure",
          summary.get("action") == "upload" and "fileId" in summary, summary)
    check("no version activation PATCH landed after the failed read",
          not any(m[0] == "PATCH" and "/versions/" in m[1] for m in fake.mutations),
          fake.mutations)


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
    check("upload confirm appends by default (deleteAllRows=False)",
          file_posts and file_posts[0][2].get("deleteAllRows") is False, file_posts)
    check("upload confirm reports dryRun=False", json.loads(out).get("dryRun") is False)


def test_upload_cli_overwrite_refused(tmp_csv):
    print("test_upload_cli_overwrite_refused")
    # Fail-closed: --overwrite (deleteAllRows:true) FAILS reproducibly on the pinned
    # release 262/v67.0 (uploadStatus=Failed, 0 rows loaded, pre-existing rows kept).
    # The CLI refuses it UP FRONT — exit 1, no ContentVersion, no /file POST, no
    # version activation — rather than submit a doomed write and report it as success
    # (and, with --activate-version, risk activating the stale prior rows). The old
    # regression here explicitly expected overwrite to exit 0, reporting a known-
    # broken operation as success; that is exactly what this now guards against.
    # (a) --overwrite alone.
    fake = _csv_transport(dry_run=False)
    rc, out = _run_cli_with_fake(
        upload_cli, ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
                     "--csv", tmp_csv, "--overwrite", "--confirm"], fake)
    check("--overwrite exits 1 (refused up front)", rc == 1, (rc, out[:300]))
    check("--overwrite performs NO mutation", fake.mutations == [], fake.mutations)
    # (b) --overwrite + --activate-version: still refused, and NOTHING activated (the
    # danger the fail-closed guard exists for — activating stale prior rows).
    fake2 = _csv_transport(dry_run=False)
    rc2, out2 = _run_cli_with_fake(
        upload_cli, ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
                     "--csv", tmp_csv, "--overwrite", "--activate-version", "1",
                     "--confirm", "--json"], fake2)
    check("--overwrite + --activate-version exits 1", rc2 == 1, (rc2, out2[:300]))
    check("--overwrite + --activate-version performs NO mutation (no stale activation)",
          fake2.mutations == [], fake2.mutations)
    # The refusal returns 1 BEFORE the CSV read and the --json summary plumbing, so
    # stdout carries no JSON summary (the actionable error goes to stderr via eprint).
    check("refusal is up front — no --json summary emitted to stdout",
          out2.strip() == "", out2[:200])


def test_upload_cli_version_number_and_activation(tmp_csv):
    print("test_upload_cli_version_number_and_activation")
    # The non-overwrite happy path the old overwrite test used to cover: append into a
    # specific version, then activate it. --version-number scopes the /file path;
    # --activate-version drives a Connect versions PATCH to Active (verified fail-
    # closed by engine.activate()'s poll of the table Status — here the fake table is
    # already Active, so the poll matches immediately).
    restore = _no_sleep()
    try:
        fake = _csv_transport(dry_run=False)
        rc, out = _run_cli_with_fake(
            upload_cli, ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
                         "--csv", tmp_csv, "--version-number", "1",
                         "--activate-version", "1", "--max-wait", "1",
                         "--confirm", "--json"], fake)
    finally:
        restore()
    check("append + activate exits 0", rc == 0, out[:300])
    file_posts = [m for m in fake.mutations if m[0] == "POST" and "/file" in m[1]]
    check("append leaves deleteAllRows=False (never overwrite)",
          file_posts and file_posts[0][2].get("deleteAllRows") is False, file_posts)
    check("--version-number scopes the /file path",
          file_posts and "versionNumber=1" in file_posts[0][1], file_posts)
    vpatch = [m for m in fake.mutations if m[0] == "PATCH" and "/versions/1" in m[1]]
    check("--activate-version PATCHes the version to Active",
          vpatch and vpatch[0][2].get("versionStatus") == "Active", fake.mutations)
    check("append + activate reports the activation in --json",
          json.loads(out).get("versionActivation", {}).get("activated") is True,
          json.loads(out))


def test_upload_cli_activate_version_fails_closed_on_noop_patch(tmp_csv):
    print("test_upload_cli_activate_version_fails_closed_on_noop_patch")
    # --activate-version routes through engine.activate(), which PATCHes the version's
    # versionStatus and then POLLS the table Status to Active. A no-op / partially-
    # applied PATCH (the version PATCH returns 200 but the table Status never cascades
    # to Active) must therefore FAIL the poll and surface as a WARNING + exit 1 — never
    # be reported as a successful activation off a bare 200 (the F2 finding). The
    # accumulated --json summary must still emit (the upload already mutated the org).
    restore = _no_sleep()
    try:
        # Table Status stays Inactive: the fake's version PATCH does not cascade, so
        # wait_for_status never observes Active and times out at --max-wait.
        fake = _csv_transport(
            dry_run=False,
            table=_table_row(name="RLM_CsvUploadTable", SourceObject="CSV",
                             Status="Inactive"))
        rc, out = _run_cli_with_fake(
            upload_cli,
            ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
             "--csv", tmp_csv, "--activate-version", "1", "--max-wait", "1",
             "--confirm", "--json"],
            fake)
    finally:
        restore()
    check("no-op activation PATCH fails the poll → exit 1", rc == 1, (rc, out[:300]))
    check("the version activation PATCH was still attempted",
          any(m[0] == "PATCH" and "/versions/1" in m[1] for m in fake.mutations),
          fake.mutations)
    summary = json.loads(out)
    check("a no-op activation is NOT reported as activated",
          summary.get("versionActivation", {}).get("activated") is not True, summary)
    check("the upload's --json summary still emits despite the failed activation",
          summary.get("action") == "upload" and "fileId" in summary, summary)


def test_upload_cli_phase2_failure_emits_json_with_fileid(tmp_csv):
    print("test_upload_cli_phase2_failure_emits_json_with_fileid")
    # Phase 1 (ContentVersion insert) succeeds → fileId; phase 2 (POST to /file)
    # fails. That is a PARTIAL mutation — an orphan ContentVersion now exists — so the
    # --json summary must still emit, carrying the fileId AND the failing phase, not
    # empty stdout (the F5 finding: a structured caller needs the id to clean up).
    fake = _csv_transport(dry_run=False)

    def _fail_file_post(record_id, file_id, *, delete_all_rows=False,
                        version_number=None, dry_run=None):
        raise DecisionTableClientError("file sub-resource POST rejected",
                                       error_codes=["UNKNOWN_EXCEPTION"])

    fake.upload_decision_table_csv = _fail_file_post
    rc, out = _run_cli_with_fake(
        upload_cli, ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
                     "--csv", tmp_csv, "--confirm", "--json"], fake)
    check("phase-2 upload failure exits 1", rc == 1, (rc, out[:300]))
    check("phase-1 ContentVersion insert still happened (the orphan)",
          any(m[1] == "sobjects/ContentVersion" for m in fake.mutations), fake.mutations)
    summary = json.loads(out)
    check("the --json failure summary carries the fileId (orphan to clean up)",
          summary.get("fileId") == "068xx0000000001AAA", summary)
    check("the --json failure summary names the failing phase + error",
          summary.get("phase") == "file-upload"
          and "rejected" in (summary.get("error") or ""), summary)


def test_upload_cli_activate_version_already_active_is_noop(tmp_csv):
    print("test_upload_cli_activate_version_already_active_is_noop")
    # Version 1 is already Active — --activate-version must skip the PATCH
    # rather than unconditionally re-sending it (the platform rejects a PATCH
    # of an already-Active version).
    fake = _csv_transport(
        dry_run=False,
        metadata=_sample_metadata(
            dataSourceType="CsvUpload", sourceObject="CSV",
            decisionTableFileImportVersions=[{"versionNumber": 1, "versionStatus": "Active"}],
        ),
    )
    rc, out = _run_cli_with_fake(
        upload_cli, ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
                     "--csv", tmp_csv, "--activate-version", "1", "--confirm", "--json"], fake)
    check("upload activate-version-already-active exits 0", rc == 0, out[:300])
    vpatch = [m for m in fake.mutations if m[0] == "PATCH" and "/versions/1" in m[1]]
    check("upload --activate-version skips the PATCH when already Active",
          vpatch == [], fake.mutations)


def _no_sleep():
    """Swap _lifecycle.time.sleep for a no-op; returns a restore() callable."""
    orig = _lifecycle.time.sleep
    _lifecycle.time.sleep = lambda *a, **k: None
    return lambda: setattr(_lifecycle.time, "sleep", orig)


def test_wait_for_upload_status_terminates():
    print("test_wait_for_upload_status_terminates")
    # UploadInProgress → UploadInProgress → Completed: the poll returns the terminal.
    restore = _no_sleep()
    try:
        t = _csv_transport(dry_run=False,
                           upload_statuses=["UploadInProgress", "UploadInProgress", "Completed"])
        engine = LifecycleEngine(t, max_wait_seconds=30, poll_interval_seconds=1)
        final = engine.wait_for_upload_status("0lDxx0000000001AAA")
    finally:
        restore()
    check("wait_for_upload_status returns the terminal Completed", final == "Completed", final)


def test_wait_for_upload_status_surfaces_errors():
    print("test_wait_for_upload_status_surfaces_errors")
    restore = _no_sleep()
    try:
        t = _csv_transport(dry_run=False, upload_statuses=["CompletedWithErrors"])
        engine = LifecycleEngine(t, max_wait_seconds=5, poll_interval_seconds=1)
        final = engine.wait_for_upload_status("0lDxx0000000001AAA")
    finally:
        restore()
    check("wait_for_upload_status surfaces CompletedWithErrors", final == "CompletedWithErrors",
          final)
    check("CompletedWithErrors is in the error set", "CompletedWithErrors" in _lifecycle._UPLOAD_ERROR)


def test_wait_for_upload_status_dry_run_noop():
    print("test_wait_for_upload_status_dry_run_noop")
    t = _csv_transport(dry_run=True, upload_statuses=["Completed"])
    engine = LifecycleEngine(t, max_wait_seconds=5)
    check("dry-run poll is a no-op (returns None)",
          engine.wait_for_upload_status("0lDxx0000000001AAA") is None)


def test_upload_cli_wait_for_status_flag(tmp_csv):
    print("test_upload_cli_wait_for_status_flag")
    # --wait-for-status polls to terminal Completed → exit 0, uploadStatus in json.
    restore = _no_sleep()
    try:
        fake = _csv_transport(dry_run=False,
                              upload_statuses=["UploadInProgress", "Completed"])
        rc, out = _run_cli_with_fake(
            upload_cli, ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
                         "--csv", tmp_csv, "--wait-for-status", "--max-wait", "10",
                         "--confirm", "--json"], fake)
    finally:
        restore()
    check("upload --wait-for-status (Completed) exits 0", rc == 0, out[:300])
    check("upload --wait-for-status reports uploadStatus=Completed",
          json.loads(out).get("uploadStatus") == "Completed", out[:400])


def test_upload_cli_wait_for_status_failed_exits_nonzero(tmp_csv):
    print("test_upload_cli_wait_for_status_failed_exits_nonzero")
    # A terminal CompletedWithErrors/Failed must exit non-zero so a caller can gate.
    restore = _no_sleep()
    try:
        fake = _csv_transport(dry_run=False, upload_statuses=["Failed"])
        rc, out = _run_cli_with_fake(
            upload_cli, ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
                         "--csv", tmp_csv, "--wait-for-status", "--max-wait", "5",
                         "--confirm", "--json"], fake)
    finally:
        restore()
    check("upload --wait-for-status (Failed) exits 1", rc == 1, out[:300])
    check("upload --wait-for-status reports uploadStatus=Failed",
          json.loads(out).get("uploadStatus") == "Failed", out[:400])


def test_upload_cli_no_wait_default(tmp_csv):
    print("test_upload_cli_no_wait_default")
    # Without --wait-for-status: no uploadStatus key, no GET-driven poll, exit 0.
    fake = _csv_transport(dry_run=False)
    rc, out = _run_cli_with_fake(
        upload_cli, ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
                     "--csv", tmp_csv, "--confirm", "--json"], fake)
    check("upload without --wait-for-status exits 0", rc == 0, out[:300])
    check("upload without --wait-for-status omits uploadStatus",
          "uploadStatus" not in json.loads(out), out[:400])


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


def test_delete_cli_active_refused_without_flag():
    print("test_delete_cli_active_refused_without_flag")
    fake = _FakeTransport(table=_table_row(Status="Active"), dry_run=False)
    rc, _ = _run_cli_with_fake(
        delete_cli, ["--target-org", "x", "--developer-name", "RLM_CostBookEntries",
                     "--confirm"], fake)
    check("delete of Active table without --deactivate-first exits 1", rc == 1, rc)
    check("refused delete performs NO deletion",
          not any(m[0] == "DELETE" for m in fake.mutations), fake.mutations)


def test_delete_cli_csv_upload_failure_rolls_back_version():
    print("test_delete_cli_csv_upload_failure_rolls_back_version")
    fake = _LifecycleFake(status="Active", data_source_type="CsvUpload")
    original_tooling_sobject = fake.tooling_sobject

    def _fail_delete(method, sobject, record_id=None, suffix=None, body=None, **kw):
        if method.upper() == "DELETE" and sobject == "DecisionTable":
            raise DecisionTableClientError("table is still referenced")
        return original_tooling_sobject(
            method, sobject, record_id=record_id, suffix=suffix, body=body, **kw
        )

    fake.tooling_sobject = _fail_delete
    rc, _ = _run_cli_with_fake(
        delete_cli,
        ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
         "--deactivate-first", "--confirm"],
        fake,
    )
    check("failed CsvUpload delete exits 1", rc == 1, rc)
    check("failed CsvUpload delete deactivates then restores the active version",
          fake.status == "Active"
          and fake.version_status_sets == ["Inactive", "Active"],
          fake.version_status_sets)
    check("failed CsvUpload delete never PATCHes table Metadata.status",
          fake.status_sets == [], fake.status_sets)


def test_delete_cli_rollback_failure_reports_reactivated_false():
    print("test_delete_cli_rollback_failure_reports_reactivated_false")
    # F7: when the DELETE fails AND the rollback reactivation ALSO fails, the --json
    # summary must report reactivated=false + a reactivationError — NOT reactivated=true
    # off the mere fact that a reactivation was attempted. The tri-state distinguishes
    # this ("attempted and failed, table may remain Inactive") from None ("no rollback
    # needed") and True ("restored"). Deactivate succeeds, delete fails, and the
    # reactivate (version PATCH back to Active) is made to fail too.
    fake = _LifecycleFake(status="Active", data_source_type="CsvUpload")
    orig_tooling = fake.tooling_sobject
    orig_connect = fake.connect

    def _fail_delete(method, sobject, record_id=None, suffix=None, body=None, **kw):
        if method.upper() == "DELETE" and sobject == "DecisionTable":
            raise DecisionTableClientError("table is still referenced")
        return orig_tooling(method, sobject, record_id=record_id, suffix=suffix,
                            body=body, **kw)

    def _fail_reactivate(method, path, body=None, **kw):
        # Let the deactivate version PATCH (versionStatus=Inactive) through; fail the
        # rollback reactivation (versionStatus=Active).
        if (method.upper() == "PATCH" and "/versions/" in path
                and isinstance(body, dict) and body.get("versionStatus") == "Active"):
            raise DecisionTableClientError("reactivation rejected — version conflict")
        return orig_connect(method, path, body=body, **kw)

    fake.tooling_sobject = _fail_delete
    fake.connect = _fail_reactivate
    rc, out = _run_cli_with_fake(
        delete_cli,
        ["--target-org", "x", "--developer-name", "RLM_CsvUploadTable",
         "--deactivate-first", "--confirm", "--json"],
        fake,
    )
    check("delete+rollback double-failure exits 1", rc == 1, (rc, out[:300]))
    failure = json.loads(out)
    check("double-failure reports deleted=false", failure.get("deleted") is False, failure)
    check("double-failure reports reactivated=false (attempt failed, not None/true)",
          failure.get("reactivated") is False, failure)
    check("double-failure carries the reactivationError detail",
          "reactivation rejected" in (failure.get("reactivationError") or ""), failure)
    # The deactivate version PATCH DID go out (Inactive); reactivation was attempted
    # (Active) but the fake raised, so the table remains Inactive.
    check("the deactivate version PATCH went out before the failed delete",
          fake.version_status_sets == ["Inactive"], fake.version_status_sets)


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
              test_validate_spec_full_name_path_escape,
              test_validate_spec_duplicate_and_unknown,
              test_validate_spec_duplicate_source_criterion_sequence,
              test_validate_spec_duplicate_input_sequence,
              test_validate_spec_boolean_typo,
              test_validate_spec_csv_upload,
              test_validate_spec_create_and_structural_errors,
              test_validate_spec_usage_is_strict,
              test_payload_miscased_usage_is_blocked_upstream,
              test_resolve_query_builders,
              test_resolve_missing_raises, test_load_definition_assembly,
              test_connect_definition_unwrap, test_diff_identical, test_diff_detects_changes,
              test_dump_single_sobject, test_dump_csv_upload_rows, test_dump_csv_upload_empty,
              test_dump_csv_upload_gated,
              test_dump_csv_upload_unclassified_error_propagates,
              test_dump_csv_upload_auth_and_generic_errors_propagate,
              test_dump_empty_source_note,
              # Phase B — dump --filter / --version-number + all-types translator
              test_dump_csv_upload_filter_drops_limit, test_dump_csv_upload_version_number_threads,
              test_dump_filter_version_ignored_on_non_csv, test_dump_cli_filter_flag,
              test_dump_cli_version_flag, test_translator_csv_upload_all_types,
              # Phase B — upload --wait-for-status poll (lifecycle + CLI)
              test_wait_for_upload_status_terminates, test_wait_for_upload_status_surfaces_errors,
              test_wait_for_upload_status_dry_run_noop,
              test_trace_correlation, test_list_cli_json,
              test_describe_cli_grouped, test_trace_cli_json,
              # Phase 2 — translators + XML round-trip
              test_translator_metadata, test_translator_tooling,
              test_translator_csv_upload, test_metadata_xml_roundtrip,
              # Phase 2 — lifecycle guards + transitions
              test_assert_editable_guard,
              test_activate_deactivate_csv_upload_is_version_first,
              test_activate_deactivate_sobject_is_table_first,
              test_guarded_update_active_roundtrip,
              test_guarded_update_csv_upload_composed_paths,
              test_guarded_update_csv_upload_multi_version_roundtrip,
              test_guarded_update_leave_deactivated,
              test_guarded_update_tooling_failure_reactivates,
              test_guarded_update_double_failure_chains_original_cause,
              test_wait_for_status_timeout_message_is_operation_aware,
              test_refresh_uses_live_verified_flag,
              # Phase 2 — mutator CLI activate/deactivate/refresh/delete gating
              test_activate_cli_preview_vs_confirm, test_activate_cli_skips_when_already_active,
              test_deactivate_cli_preview_vs_confirm, test_refresh_cli_preview_vs_confirm,
              test_refresh_cli_exits_nonzero_on_bad_outcomes,
              test_delete_cli_requires_confirm, test_delete_cli_active_refused_without_flag,
              test_delete_cli_csv_upload_failure_rolls_back_version,
              test_delete_cli_rollback_failure_reports_reactivated_false,
              test_delete_cli_deactivate_confirmation_timeout_still_reactivates,
              test_delete_cli_ambiguous_version_resolution_returns_controlled_error,
              # Phase 2 — CsvUpload data-load CLI gating
              test_upload_header_validation,
              test_upload_header_validation_ignores_rowcriteria,
              test_upload_cli_missing_csv_errors)
    for fn in simple:
        fn()

    # Phase 2 — create/update CLI tests that need spec/output-file fixtures.
    test_create_cli_tooling_preview_vs_confirm(spec_path)
    test_create_cli_honors_requested_active_status(spec_path)
    test_create_cli_failure_emits_json_with_error(spec_path)
    test_create_cli_generate_only_no_org(spec_path, out_xml)
    test_create_cli_generate_only_rejects_nonmetadata(spec_path)
    test_create_cli_invalid_spec_blocks(_tmp)
    test_update_cli_active_refused_without_flag(spec_path)
    test_update_cli_deactivate_first_roundtrip(spec_path)
    test_update_cli_unreadable_live_status_fails_closed(spec_path)
    # Phase B — CsvUpload upload CLI (needs a CSV fixture).
    test_upload_cli_missing_header_blocks(csv_path)
    test_upload_cli_preview_vs_confirm(csv_path)
    test_upload_cli_overwrite_refused(csv_path)
    test_upload_cli_version_number_and_activation(csv_path)
    test_upload_cli_activate_version_fails_closed_on_noop_patch(csv_path)
    test_upload_cli_phase2_failure_emits_json_with_fileid(csv_path)
    test_upload_cli_activate_version_already_active_is_noop(csv_path)
    test_upload_cli_activate_version_read_failure_is_guarded(csv_path)
    test_upload_cli_wait_for_status_flag(csv_path)
    test_upload_cli_wait_for_status_failed_exits_nonzero(csv_path)
    test_upload_cli_no_wait_default(csv_path)

    import shutil
    shutil.rmtree(tmpdir, ignore_errors=True)

    print(f"\n{_PASS} passed, {_FAIL} failed.")
    return 1 if _FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
