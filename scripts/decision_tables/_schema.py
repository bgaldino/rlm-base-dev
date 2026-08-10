#!/usr/bin/env python3
"""Enum / field catalogs + canonical-spec validation for BRE Decision Tables.

Pure, dependency-free (stdlib only) so it is unit-testable from a plain
``python`` invocation with no org and no CumulusCI import. This is the Decision
Table analogue of ``scripts/expression_sets/_schema.py``.

Two roles:

1. **Enum / field catalogs** — the documented Metadata/Tooling authoring
   vocabulary and the setup objects. Read-side Connect field-name divergence is
   retained for inspectors, but definition mutation is Metadata/Tooling-only.
2. **Canonical-spec validation** — ``validate_spec(spec)`` checks an
   author-facing canonical Decision Table spec (path-agnostic) *before* it is
   translated and sent to an org, where a Tooling handler can turn a precise
   local defect into an opaque failure.

Provenance: values captured from a live v67.0 read of ``rlm-base__beta`` /
scratch orgs on 2026-07-09 (Tooling ``Metadata`` complexvalue + describes,
Connect Definitions GET, ``refreshDecisionTable`` action describe) plus the
Release 262 docs (``meta_decisiontable.htm``, ``dt_setup_objects.htm``,
``lookup_table_resources.htm``). See
``docs/references/decision-table-api-reference.md`` for the full evidence.
Unknown values in the *descriptive* enums (``usageType`` / ``type`` /
``executionType`` …) **warn** (forward-compat), they do not error. The one
exception is the *closed structural* enum ``usage`` (INPUT/OUTPUT/ROWCRITERIA):
an unrecognized/mis-cased value there is an **error**, because it silently
changes translation (see :func:`_validate_parameter` and the ``strict`` arg of
:func:`_check_enum`) rather than merely being unrecognized by the org.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

# --------------------------------------------------------------------------- #
# Verified enum catalogs (v67.0 / Release 262)
# Values observed live are noted; the sets are the documented supersets.
# --------------------------------------------------------------------------- #

# Metadata/Tooling ``dataSourceType``.
DATA_SOURCE_TYPES = {
    "ContextDefinition",
    "CsvUpload",
    "MultipleSobjects",   # observed
    "SingleSobject",      # observed
}

# `executionType` — DLO replaces DMO at v67.0. MDAPI XML casing is `Hbase`;
# Tooling returns `HBASE`. Both spellings accepted here.
EXECUTION_TYPES = {
    "DLO",      # v67.0+, replaces DMO
    "HBASE", "Hbase",  # observed (HBASE via API, Hbase in source XML)
    "HBPO",
    "SOLR",
    "SOQL",
}

CONDITION_TYPES = {"All", "Any", "Custom"}  # All observed

# Metadata/Tooling ``filterResultBy`` (hit policy).
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

# Metadata/Tooling ``dtRowLevelOverrideType``.
ROW_LEVEL_OVERRIDE_TYPES = {"Both", "Condition", "None", "Operator"}

COLLECT_OPERATORS = {"Count", "Maximum", "Minimum", "None", "Sum"}

# ---- DecisionTableParameter (a column) -----------------------------------
# ``usage`` is UPPER on Metadata/Tooling.
PARAM_USAGE = {"INPUT", "OUTPUT", "ROWCRITERIA"}  # observed INPUT/OUTPUT

PARAM_DATA_TYPES = {
    "Boolean", "Currency", "Date", "DateTime", "Number", "Percent", "String",  # String observed
}

PARAM_OPERATORS = {
    "Contains", "DoesNotExistIn", "DoesNotMatch", "Equals", "ExistsIn",
    "GreaterOrEqual", "GreaterThan", "IsNotNull", "IsNull", "LessOrEqual",
    "LessThan", "Matches", "NotEquals",
}

PARAM_SORT_TYPES = {"AscNullFirst", "AscNullLast", "DescNullFirst", "DescNullLast", "None"}

# ---- DecisionTableSourceCriteria -----------------------------------------
SOURCE_CRITERIA_VALUE_TYPES = {"Formula", "Literal", "Lookup", "Parameter", "Picklist"}
SOURCE_CRITERIA_OPERATORS = set(PARAM_OPERATORS)

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

# The field-name divergence between the supported Metadata/Tooling authoring
# shape and the optional read-only Connect representation (concept → per-surface
# key). Inspectors use it to label Connect fields with Metadata-equivalent names.
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
# Metadata/Tooling vocabulary, with UPPER-case column ``usage``. Connect
# Definitions mutation is intentionally unsupported because its representation
# is not field-compatible with this canonical shape.
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
#     "status":         "Active",                  # required on create
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
_INPUT_USAGE = {"INPUT"}

# `sourceObject` is Required-since-58.0 for **every** dataSourceType — all three
# Metadata/Tooling authoring paths reject a create without it (live-verified 262 /
# v67.0: Tooling ``FIELD_INTEGRITY_EXCEPTION`` and Metadata deploy error).
# For a CsvUpload table the value is the literal string "CSV" (there is no backing
# SObject); for the SObject types it is the object api-name.
_CSV_SOURCE_OBJECT = "CSV"

# ``fullName`` becomes a bare file-system segment
# (``<fullName>.decisionTable-meta.xml``) in both the metadata deploy's temp
# package dir (``_lifecycle.deploy_metadata_xml``) and ``_payload.meta_file_name``.
# A value containing a path separator or an absolute-path leading slash escapes
# that directory (``os.path.join`` discards everything before an absolute-looking
# segment) — reject up front rather than let a malformed spec write outside the
# temp SFDX project. Salesforce API names are themselves restricted to this
# shape (letter-led, alphanumeric + underscore), so this is not overly strict.
_FULL_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")

_TOP_LEVEL_KEYS = {
    "fullName", "setupName", "dataSourceType", "sourceObject", "executionType",
    "filterResultBy", "conditionType", "conditionCriteria", "sourceConditionLogic",
    "type", "usageType", "status", "description", "collectOperator",
    "dtRowLevelOverrideType", "doesConsiderNullValue", "hasIncrementalSyncFailed",
    "isIncrementalSyncEnabled", "isVersioned", "decisionTableParameters",
    "decisionTableSourceCriterias",
}

_PARAMETER_KEYS = {
    "dataType", "decimalScale", "domainObject", "fieldName", "fieldPath",
    "isGroupByField", "isPriorityField", "isRequired", "length", "operator",
    "sequence", "sortType", "usage",
}

_SOURCE_CRITERIA_KEYS = {
    "sourceFieldName", "operator", "value", "valueType", "sequenceNumber",
}


def _check_enum(result: ValidationResult, location: str, value: Any,
                allowed: Set[str], *, required: bool = False,
                strict: bool = False) -> None:
    """Validate ``value`` against ``allowed``.

    An unrecognized value **warns** by default — the descriptive catalogs
    (``usageType`` / ``type`` / ``executionType`` …) grow per release, so a value
    this toolkit hasn't catalogued yet may still be valid on the org (forward
    compat). ``strict=True`` makes an unrecognized value an **error** instead: use
    it for a *closed structural* enum whose value drives translation, where an
    off-catalog value can never be intentional and would silently produce a wrong
    write rather than an org-side rejection (see ``usage`` in
    :func:`_validate_parameter`).
    """
    if value is None or value == "":
        if required:
            result.error(location, "is required.")
        return
    if value not in allowed:
        message = f"unrecognized value {value!r} (known: {sorted(allowed)})."
        if strict:
            result.error(location, message)
        else:
            result.warn(location, message)


def _check_integer(result: ValidationResult, location: str, value: Any,
                   *, required: bool = False) -> None:
    if value is None or value == "":
        if required:
            result.error(location, "is required and must be an integer.")
        return
    if isinstance(value, bool) or not isinstance(value, int):
        result.error(location, f"must be an integer; got {value!r}.")


def _reject_unknown_keys(result: ValidationResult, location: str,
                         value: Dict[str, Any], allowed: Set[str]) -> None:
    """Error on any key outside the canonical spec's known vocabulary.

    ``to_metadata`` silently drops unrecognized keys, so a typo (e.g.
    ``sourceConditionLogc``) would otherwise pass validation, get ignored by the
    translator, and let a full-replace update land without the field the author
    actually intended — a validated-but-wrong definition. Unlike an unrecognized
    value in a *descriptive* enum (forward-compat, kept as a warning via
    ``_check_enum``), an unrecognized *key* can never be intentional on this
    closed, hand-maintained schema, so it errors rather than warns. The *closed
    structural* enum ``usage`` is treated the same way as an unknown key — an error
    (``_check_enum(strict=True)``) — because an off-catalog value there silently
    mistranslates the column rather than being harmlessly unrecognized.
    """
    for key in sorted(set(value) - allowed):
        prefix = f"{location}." if location else ""
        result.error(f"{prefix}{key}",
                     "is not part of the Metadata/Tooling canonical spec — check for "
                     "a typo. An unknown key is silently dropped by the translator, "
                     "so a mistyped field name would otherwise pass validation and "
                     "then be missing from the definition that is written.")


def _validate_parameter(param: Dict[str, Any], location: str, result: ValidationResult,
                        seen: Set[str]) -> None:
    if not isinstance(param, dict):
        result.error(location, "each column must be an object.")
        return
    _reject_unknown_keys(result, location, param, _PARAMETER_KEYS)
    usage = param.get("usage")
    # ``usage`` is a CLOSED, STRUCTURAL enum, not a descriptive one: it decides
    # whether the translator keeps ``operator``/``sequence`` (INPUT-only) and it is
    # matched case-sensitively (``_payload._INPUT_USAGES == {"INPUT"}``). A
    # mis-cased or off-catalog value (e.g. the Connect read-side ``"Input"``) would
    # otherwise pass as a warning, then be treated as non-INPUT — silently dropping
    # ``operator``/``sequence`` and writing a definition that no longer matches the
    # spec (and fails GET-back verification). So an unrecognized ``usage`` is an
    # ERROR, the same fail-closed treatment as an unknown key.
    _check_enum(result, f"{location}.usage", usage, PARAM_USAGE, required=True,
                strict=True)
    field_name = param.get("fieldName")
    if not field_name:
        result.error(f"{location}.fieldName", "is required.")
    else:
        key = f"{usage}:{field_name}"
        if key in seen:
            result.error(location, f"duplicate column {field_name!r} for usage {usage!r}.")
        seen.add(key)
    _check_enum(result, f"{location}.dataType", param.get("dataType"), PARAM_DATA_TYPES)
    _check_integer(result, f"{location}.decimalScale", param.get("decimalScale"))
    _check_integer(result, f"{location}.length", param.get("length"))
    if usage in _INPUT_USAGE:
        _check_enum(result, f"{location}.operator", param.get("operator"), PARAM_OPERATORS)
        if param.get("sequence") in (None, ""):
            result.warn(f"{location}.sequence",
                        "INPUT columns are normally sequenced (referenced by conditionCriteria).")
        else:
            _check_integer(result, f"{location}.sequence", param.get("sequence"))
    else:
        # OUTPUT/ROWCRITERIA carry no operator/sequence.
        if param.get("operator"):
            result.warn(f"{location}.operator", f"ignored for usage {usage!r} (INPUT-only).")
    _check_enum(result, f"{location}.sortType", param.get("sortType"), PARAM_SORT_TYPES)


def validate_spec(spec: Dict[str, Any], *, path: Optional[str] = None) -> ValidationResult:
    """Validate a Metadata/Tooling canonical Decision Table spec. Pure; no org.

    ``path`` is optional and enables one **create**-specific requirement
    (missing ``status``) — pass the authoring path (``"metadata"``/``"tooling"``)
    when validating a spec that is about to *create* a table. Leave it unset
    (the default) for update validation, where the spec's ``status`` is
    intentionally dropped and re-stamped from the live table — see
    ``update_decision_table.py`` — so a missing ``status`` there is normal,
    not a defect.
    """
    result = ValidationResult()
    if not isinstance(spec, dict):
        result.error("<root>", "spec must be a JSON object.")
        return result

    _reject_unknown_keys(result, "", spec, _TOP_LEVEL_KEYS)

    full_name = spec.get("fullName")
    if not full_name:
        result.error("fullName", "is required (the api name, e.g. 'RLM_CostBookEntries').")
    elif not (isinstance(full_name, str) and _FULL_NAME_RE.match(full_name)):
        result.error(
            "fullName",
            f"must be a valid api name (letters/digits/underscore, starting with a "
            f"letter) — got {full_name!r}. It becomes a bare file name "
            f"(<fullName>.decisionTable-meta.xml) in the metadata deploy path; a "
            f"path separator or absolute-path value would write outside the temp "
            f"SFDX project.",
        )
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
    _check_enum(result, "collectOperator", spec.get("collectOperator"), COLLECT_OPERATORS)
    _check_enum(result, "dtRowLevelOverrideType", spec.get("dtRowLevelOverrideType"),
                ROW_LEVEL_OVERRIDE_TYPES)

    if spec.get("conditionType") == "Custom" and not spec.get("conditionCriteria"):
        result.error("conditionCriteria", "is required when conditionType is 'Custom'.")
    if spec.get("filterResultBy") == "CollectOperator" and not spec.get("collectOperator"):
        result.error("collectOperator", "is required when filterResultBy is 'CollectOperator'.")

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

    if dst == "CsvUpload" and spec.get("isVersioned") is None:
        result.warn("isVersioned",
                    "CsvUpload tables are versioned by nature; consider setting "
                    "isVersioned explicitly — to_metadata() defaults it to true "
                    "when omitted, which may not match what you intend.")

    if path in ("metadata", "tooling") and not spec.get("status"):
        result.error("status",
                     "is required by Metadata/Tooling create; set it explicitly "
                     "(normally 'Draft').")

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
            elif usage == "OUTPUT":
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
                _reject_unknown_keys(result, loc, crit, _SOURCE_CRITERIA_KEYS)
                if not crit.get("sourceFieldName"):
                    result.error(f"{loc}.sourceFieldName", "is required.")
                _check_enum(result, f"{loc}.operator", crit.get("operator"),
                            SOURCE_CRITERIA_OPERATORS, required=True)
                _check_enum(result, f"{loc}.valueType", crit.get("valueType"),
                            SOURCE_CRITERIA_VALUE_TYPES, required=True)
                _check_integer(result, f"{loc}.sequenceNumber", crit.get("sequenceNumber"),
                               required=True)

    return result
