#!/usr/bin/env python3
"""Enum / field catalogs + canonical-spec validation for BRE Decision Tables.

Pure, dependency-free (stdlib only) so it is unit-testable from a plain
``python`` invocation with no org and no CumulusCI import. This is the Decision
Table analogue of ``scripts/expression_sets/_schema.py``.

Two roles:

1. **Enum / field catalogs** — the live-verified vocabularies for the three
   authoring paths (Metadata / Tooling / Connect Definitions) and the setup
   objects. The read CLIs use these to label and validate values; Phase-2
   translators (``_payload.py``) map a canonical spec onto each path.
2. **Canonical-spec validation** — ``validate_spec(spec)`` checks an
   author-facing canonical Decision Table spec (path-agnostic) *before* it is
   translated and sent to an org, where a Connect/Tooling handler can swallow a
   real error into an opaque failure.

Provenance: values captured from a live v67.0 read of ``rlm-base__beta`` /
scratch orgs on 2026-07-09 (Tooling ``Metadata`` complexvalue + describes,
Connect Definitions GET, ``refreshDecisionTable`` action describe) plus the
Release 262 docs (``meta_decisiontable.htm``, ``dt_setup_objects.htm``,
``lookup_table_resources.htm``). See
``docs/references/decision-table-api-reference.md`` for the full evidence.
Unknown enum values **warn** (forward-compat), they do not error.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

# --------------------------------------------------------------------------- #
# Verified enum catalogs (v67.0 / Release 262)
# Values observed live are noted; the sets are the documented supersets.
# --------------------------------------------------------------------------- #

# Metadata/Tooling `dataSourceType`  ==  Connect `sourceType`.
DATA_SOURCE_TYPES = {
    "ContextDefinition",
    "CsvUpload",
    "MultipleSobjects",   # observed
    "SingleSobject",      # observed
}

# `executionType` — DLO replaces DMO at v67.0. MDAPI XML casing is `Hbase`;
# Tooling/Connect return `HBASE`. Both spellings accepted here.
EXECUTION_TYPES = {
    "DLO",      # v67.0+, replaces DMO
    "HBASE", "Hbase",  # observed (HBASE via API, Hbase in source XML)
    "HBPO",
    "SOLR",
    "SOQL",
}

CONDITION_TYPES = {"All", "Any", "Custom"}  # All observed

# Metadata `filterResultBy`  ==  Connect `decisionResultPolicy` (hit policy).
FILTER_RESULT_BY = {
    "AnyValue",
    "CollectOperator",
    "FirstMatch",
    "OutputOrder",   # observed
    "Priority",
    "RuleOrder",
    "UniqueValues",
}

# `type` (volume/execution profile).
TABLE_TYPES = {
    "Advanced",
    "HighScaleExecution",
    "HighVolume",
    "LowVolume",
    "MediumVolume",  # observed
    "RealTime",
}

STATUSES = {"ActivationInProgress", "Active", "Draft", "Inactive"}  # Active observed

# `usageType` (ExpsSetProcessType) — Revenue Cloud subset; grows per release,
# so this is representative, not exhaustive (unknown → warn).
USAGE_TYPES = {
    "Bre",
    "DefaultPricing",             # observed
    "DefaultRating",              # observed
    "PricingDiscovery",           # observed
    "RatingDiscovery",            # observed
    "RevenueStandardTax",         # observed
    "ProductCategoryQualification",
    "ProductQualification",
    "RecordAlert",
}

# Metadata/Tooling `dtRowLevelOverrideType`  ==  Connect `rowLevelOverrideType`.
ROW_LEVEL_OVERRIDE_TYPES = {"None"}  # None observed; superset undocumented

COLLECT_OPERATORS = {"None"}  # None observed; used when filterResultBy=CollectOperator

# ---- DecisionTableParameter (a column) -----------------------------------
# `usage` is UPPER on Metadata/Tooling, Title-case on Connect.
PARAM_USAGE = {"INPUT", "OUTPUT", "ROWCRITERIA"}          # observed INPUT/OUTPUT
PARAM_USAGE_CONNECT = {"Input", "Output", "RowCriteria"}  # Connect vocabulary

PARAM_DATA_TYPES = {
    "Boolean", "Currency", "Date", "DateTime", "Number", "Percent", "String",  # String observed
}

PARAM_OPERATORS = {
    "Equals", "NotEquals", "GreaterThan", "GreaterOrEqual", "LessThan",
    "LessOrEqual", "ExistsIn", "Matches", "IsNull",
}

PARAM_SORT_TYPES = {"Ascending", "Descending", "None"}

# ---- DecisionTableSourceCriteria -----------------------------------------
SOURCE_CRITERIA_VALUE_TYPES = {"Formula", "Literal", "Lookup", "Parameter", "Picklist"}

# --------------------------------------------------------------------------- #
# Setup objects — Tooling API only, with live-verified key prefixes.
# --------------------------------------------------------------------------- #

SETUP_OBJECT_PREFIXES = {
    "DecisionTable": "0lD",
    "DecisionTableParameter": "0lP",
    "DecisionTableDatasetLink": "0lX",
    "DecisionTblDatasetParameter": "0lZ",
    "DecisionTableSourceCriteria": "0VT",
}

# The field-name divergence across the three authoring paths (concept →
# per-path key). Phase-2 translators read this; the read CLIs use it to label a
# Connect response with its Metadata-equivalent concept.
FIELD_NAME_MAP = {
    # concept:          (metadata/tooling,            connect)
    "data_source":      ("dataSourceType",            "sourceType"),
    "hit_policy":       ("filterResultBy",            "decisionResultPolicy"),
    "columns":          ("decisionTableParameters",   "parameters"),
    "source_criteria":  ("decisionTableSourceCriterias", "sourceCriteria"),
    "row_override":     ("dtRowLevelOverrideType",    "rowLevelOverrideType"),
}


# --------------------------------------------------------------------------- #
# ValidationResult (mirrors scripts/expression_sets/_schema.py)
# --------------------------------------------------------------------------- #

class Severity(Enum):
    ERROR = "Error"
    WARNING = "Warning"


@dataclass
class Issue:
    severity: Severity
    location: str
    message: str


@dataclass
class ValidationResult:
    passed: bool = True
    issues: List[Issue] = field(default_factory=list)

    def error(self, location: str, message: str) -> None:
        self.issues.append(Issue(Severity.ERROR, location, message))
        self.passed = False

    def warn(self, location: str, message: str) -> None:
        self.issues.append(Issue(Severity.WARNING, location, message))

    @property
    def errors(self) -> List[Issue]:
        return [i for i in self.issues if i.severity is Severity.ERROR]

    @property
    def warnings(self) -> List[Issue]:
        return [i for i in self.issues if i.severity is Severity.WARNING]

    def merge(self, other: "ValidationResult") -> None:
        self.issues.extend(other.issues)
        if not other.passed:
            self.passed = False

    def format_report(self) -> str:
        if not self.issues:
            return "OK — no issues."
        lines = [f"[{i.severity.value}] {i.location}: {i.message}" for i in self.issues]
        lines.append(f"\n{len(self.errors)} error(s), {len(self.warnings)} warning(s).")
        return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Canonical spec validation
#
# The canonical (author-facing, path-agnostic) Decision Table spec uses the
# Metadata/Tooling vocabulary as its base (it is the source-controlled path),
# with UPPER-case column `usage`. Phase-2 `_payload.to_connect()` title-cases
# `usage` and renames the diverging keys. Validating the canonical shape here
# means one validator guards all three paths.
#
#   {
#     "fullName":       "RLM_CostBookEntries",     # api name (required)
#     "setupName":      "Cost Book Entries",       # label (required)
#     "dataSourceType": "SingleSobject",           # required
#     "sourceObject":   "CostBookEntry",           # required (all types; "CSV" for CsvUpload)
#     "executionType":  "Hbase",                   # optional
#     "filterResultBy": "OutputOrder",             # required (hit policy)
#     "conditionType":  "All",                     # optional
#     "type":           "MediumVolume",            # optional
#     "usageType":      "DefaultPricing",          # optional
#     "status":         "Active",                  # optional (deploy-time)
#     "decisionTableParameters": [
#       {"usage":"INPUT","fieldName":"ProductId","dataType":"String",
#        "operator":"Equals","sequence":1,"fieldPath":"ProductId","isRequired":true},
#       {"usage":"OUTPUT","fieldName":"Cost","dataType":"Currency"},
#     ],
#     "decisionTableSourceCriterias": [
#       {"sourceFieldName":"UsageType","operator":"Equals","value":"Pricing",
#        "valueType":"Literal","sequenceNumber":1},
#     ],
#   }
# --------------------------------------------------------------------------- #

# The `usage` values that require an operator + sequence (INPUT columns only).
_INPUT_USAGE = {"INPUT", "Input"}

# `sourceObject` is Required-since-58.0 for **every** dataSourceType — all three
# authoring paths reject a create without it (live-verified 262 / v67.0: Tooling
# `FIELD_INTEGRITY_EXCEPTION`, Connect `MISSING_ARGUMENT`, Metadata deploy error).
# For a CsvUpload table the value is the literal string "CSV" (there is no backing
# SObject); for the SObject types it is the object api-name.
_CSV_SOURCE_OBJECT = "CSV"


def _check_enum(result: ValidationResult, location: str, value: Any,
                allowed: Set[str], *, required: bool = False) -> None:
    if value is None or value == "":
        if required:
            result.error(location, "is required.")
        return
    if value not in allowed:
        result.warn(location, f"unrecognized value {value!r} (known: {sorted(allowed)}).")


def _validate_parameter(param: Dict[str, Any], location: str, result: ValidationResult,
                        seen: Set[str]) -> None:
    if not isinstance(param, dict):
        result.error(location, "each column must be an object.")
        return
    usage = param.get("usage")
    _check_enum(result, f"{location}.usage", usage,
                PARAM_USAGE | PARAM_USAGE_CONNECT, required=True)
    field_name = param.get("fieldName")
    if not field_name:
        result.error(f"{location}.fieldName", "is required.")
    else:
        key = f"{usage}:{field_name}"
        if key in seen:
            result.error(location, f"duplicate column {field_name!r} for usage {usage!r}.")
        seen.add(key)
    _check_enum(result, f"{location}.dataType", param.get("dataType"), PARAM_DATA_TYPES)
    if usage in _INPUT_USAGE:
        _check_enum(result, f"{location}.operator", param.get("operator"), PARAM_OPERATORS)
        if param.get("sequence") in (None, ""):
            result.warn(f"{location}.sequence",
                        "INPUT columns are normally sequenced (referenced by conditionCriteria).")
    else:
        # OUTPUT/ROWCRITERIA carry no operator/sequence.
        if param.get("operator"):
            result.warn(f"{location}.operator", f"ignored for usage {usage!r} (INPUT-only).")
    _check_enum(result, f"{location}.sortType", param.get("sortType"), PARAM_SORT_TYPES)


def validate_spec(spec: Dict[str, Any]) -> ValidationResult:
    """Validate a canonical Decision Table spec (path-agnostic). Pure; no org."""
    result = ValidationResult()
    if not isinstance(spec, dict):
        result.error("<root>", "spec must be a JSON object.")
        return result

    if not spec.get("fullName"):
        result.error("fullName", "is required (the api name, e.g. 'RLM_CostBookEntries').")
    if not spec.get("setupName"):
        result.error("setupName", "is required (the human label).")

    _check_enum(result, "dataSourceType", spec.get("dataSourceType"),
                DATA_SOURCE_TYPES, required=True)
    _check_enum(result, "filterResultBy", spec.get("filterResultBy"),
                FILTER_RESULT_BY, required=True)
    _check_enum(result, "executionType", spec.get("executionType"), EXECUTION_TYPES)
    _check_enum(result, "conditionType", spec.get("conditionType"), CONDITION_TYPES)
    _check_enum(result, "type", spec.get("type"), TABLE_TYPES)
    _check_enum(result, "usageType", spec.get("usageType"), USAGE_TYPES)
    _check_enum(result, "status", spec.get("status"), STATUSES)
    _check_enum(result, "dtRowLevelOverrideType", spec.get("dtRowLevelOverrideType"),
                ROW_LEVEL_OVERRIDE_TYPES)

    dst = spec.get("dataSourceType")
    source_object = spec.get("sourceObject")
    if not source_object:
        # Required for every source type (Required-since-58.0). CsvUpload gets a
        # value-convention hint so the author knows it is not an SObject name.
        hint = (" (use the literal 'CSV' for a CsvUpload table)"
                if dst == "CsvUpload" else "")
        result.error("sourceObject", f"is required (dataSourceType is {dst!r}){hint}.")
    elif dst == "CsvUpload" and source_object != _CSV_SOURCE_OBJECT:
        result.warn("sourceObject",
                    f"a CsvUpload table normally uses sourceObject "
                    f"{_CSV_SOURCE_OBJECT!r}; got {source_object!r}.")

    params = spec.get("decisionTableParameters")
    if not isinstance(params, list) or not params:
        result.error("decisionTableParameters", "at least one column is required.")
    else:
        seen: Set[str] = set()
        n_input = n_output = 0
        for i, param in enumerate(params):
            _validate_parameter(param, f"decisionTableParameters[{i}]", result, seen)
            usage = param.get("usage") if isinstance(param, dict) else None
            if usage in _INPUT_USAGE:
                n_input += 1
            elif usage in {"OUTPUT", "Output"}:
                n_output += 1
        if n_output == 0:
            result.error("decisionTableParameters", "at least one OUTPUT column is required.")
        if n_input == 0:
            result.warn("decisionTableParameters",
                        "no INPUT columns — the table will match every source row.")

    criteria = spec.get("decisionTableSourceCriterias")
    if criteria is not None:
        if not isinstance(criteria, list):
            result.error("decisionTableSourceCriterias", "must be a list when present.")
        else:
            for i, crit in enumerate(criteria):
                loc = f"decisionTableSourceCriterias[{i}]"
                if not isinstance(crit, dict):
                    result.error(loc, "each criterion must be an object.")
                    continue
                if not crit.get("sourceFieldName"):
                    result.error(f"{loc}.sourceFieldName", "is required.")
                _check_enum(result, f"{loc}.valueType", crit.get("valueType"),
                            SOURCE_CRITERIA_VALUE_TYPES)

    return result
