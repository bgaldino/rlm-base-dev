#!/usr/bin/env python3
"""Translate canonical Decision Table specs into Tooling API shapes.

The pure helpers return new structures and do not mutate their input.
"""

from typing import Any, Dict, List, Optional

# Only INPUT columns carry an operator and sequence.
_INPUT_USAGES = {"INPUT"}

# Boolean defaults included in every Tooling Metadata body.
_METADATA_DEFAULT_BOOLS = {
    "doesConsiderNullValue": False,
    "hasIncrementalSyncFailed": False,
    "isIncrementalSyncEnabled": False,
    "isVersioned": False,
}

# Scalar fields copied into the Tooling Metadata body. ``fullName`` belongs in
# the top-level ``FullName`` field instead.
_METADATA_SCALARS = (
    "setupName",
    "dataSourceType",
    "sourceObject",
    "executionType",
    "filterResultBy",
    "conditionType",
    "conditionCriteria",
    "sourceConditionLogic",
    "type",
    "usageType",
    "status",
    "description",
    "collectOperator",
    "dtRowLevelOverrideType",
)


def _bool_from(value: Any, default: bool) -> bool:
    """Coerce a spec value to a bool, treating a missing/empty value as ``default``."""
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes")
    return bool(value)


def _derive_condition_criteria(params: List[Dict[str, Any]], condition_type: Any) -> Optional[str]:
    """Build a default ``conditionCriteria`` from the INPUT columns' sequences.

    A Decision Table with INPUT columns needs a ``conditionCriteria`` boolean
    expression (e.g. ``"1 AND 2 AND 3"``) — the create fails without one. When the
    author omits it we synthesize the natural default: the INPUT sequences joined
    by ``AND`` (``OR`` when ``conditionType`` is ``Any``). ``Custom`` cannot be
    derived (the author defines the expression) → return ``None`` and let the
    platform reject a truly-missing one. Returns ``None`` when there are no INPUT
    columns (an unconditioned table needs no criteria).
    """
    if str(condition_type) == "Custom":
        return None
    seqs: List[int] = []
    for p in params:
        if not isinstance(p, dict):
            continue
        if p.get("usage") != "INPUT":
            continue
        seq = p.get("sequence")
        if seq in (None, ""):
            continue
        try:
            seqs.append(int(seq))
        except (TypeError, ValueError):
            continue
    if not seqs:
        return None
    joiner = " OR " if str(condition_type) == "Any" else " AND "
    return joiner.join(str(s) for s in sorted(seqs))


def _param_to_metadata(param: Dict[str, Any]) -> Dict[str, Any]:
    """One canonical column → its Metadata/Tooling ``decisionTableParameters`` entry.

    INPUT columns keep ``operator`` + ``sequence``; OUTPUT/ROWCRITERIA drop them.
    ``fieldPath`` defaults to ``fieldName``. Booleans ``isGroupByField`` and
    ``isRequired`` default to ``False``.
    """
    usage = param.get("usage")
    field_name = param.get("fieldName")
    out: Dict[str, Any] = {}
    if param.get("dataType") is not None:
        out["dataType"] = param["dataType"]
    if param.get("decimalScale") not in (None, ""):
        out["decimalScale"] = int(param["decimalScale"])
    if field_name is not None:
        out["fieldName"] = field_name
        out["fieldPath"] = param.get("fieldPath") or field_name
    out["isGroupByField"] = _bool_from(param.get("isGroupByField"), False)
    if param.get("isPriorityField") is not None:
        out["isPriorityField"] = _bool_from(param.get("isPriorityField"), False)
    out["isRequired"] = _bool_from(param.get("isRequired"), False)
    if param.get("length") not in (None, ""):
        out["length"] = int(param["length"])
    if usage in _INPUT_USAGES:
        if param.get("operator") is not None:
            out["operator"] = param["operator"]
        if param.get("sequence") not in (None, ""):
            out["sequence"] = int(param["sequence"])
    if param.get("sortType") is not None:
        out["sortType"] = param["sortType"]
    if param.get("domainObject") is not None:
        out["domainObject"] = param["domainObject"]
    if usage is not None:
        out["usage"] = usage
    return out


def _criteria_to_metadata(crit: Dict[str, Any]) -> Dict[str, Any]:
    """One canonical source-criterion → its ``decisionTableSourceCriterias`` entry."""
    out: Dict[str, Any] = {}
    for key in ("sourceFieldName", "operator", "value", "valueType"):
        if crit.get(key) is not None:
            out[key] = crit[key]
    if crit.get("sequenceNumber") not in (None, ""):
        out["sequenceNumber"] = int(crit["sequenceNumber"])
    return out


def to_metadata(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Canonical spec → the Metadata **body** (the ``Metadata`` complexvalue).

    :func:`to_tooling` wraps this body under ``{"FullName", "Metadata"}``.
    Field names and casing are the Metadata/Tooling vocabulary
    (``dataSourceType`` / ``filterResultBy`` / ``decisionTableParameters``;
    ``usage`` UPPER). ``fullName`` is intentionally excluded because it belongs
    in the top-level ``FullName`` field. A missing ``conditionCriteria`` is
    synthesized from the INPUT sequences.

    Returns a new dict (JSON-friendly: real ``bool``s, ``int`` sequences).
    """
    body: Dict[str, Any] = {}
    for key in _METADATA_SCALARS:
        val = spec.get(key)
        if val is not None and val != "":
            body[key] = val

    if not body.get("conditionCriteria"):
        derived = _derive_condition_criteria(
            spec.get("decisionTableParameters") or [], spec.get("conditionType")
        )
        if derived is not None:
            body["conditionCriteria"] = derived

    for key, default in _METADATA_DEFAULT_BOOLS.items():
        body[key] = _bool_from(spec.get(key), default)

    # CsvUpload tables are versioned by nature; default isVersioned to True unless
    # the spec explicitly set it to False. Treat an empty string as unset (the same
    # "missing/empty ⇒ default" rule `_bool_from` applies everywhere else).
    if spec.get("dataSourceType") == "CsvUpload" and spec.get("isVersioned") in (None, ""):
        body["isVersioned"] = True

    params = spec.get("decisionTableParameters")
    if isinstance(params, list):
        body["decisionTableParameters"] = [
            _param_to_metadata(p) for p in params if isinstance(p, dict)
        ]

    criteria = spec.get("decisionTableSourceCriterias")
    if isinstance(criteria, list) and criteria:
        body["decisionTableSourceCriterias"] = [
            _criteria_to_metadata(c) for c in criteria if isinstance(c, dict)
        ]

    return body


def to_tooling(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Canonical spec → a Tooling ``DecisionTable`` POST/PATCH body.

    Shape: ``{"FullName": <api name>, "Metadata": {…}}`` — the
    Tooling create/update body. On a **PATCH** the caller sends only
    ``{"Metadata": {…}}`` (the id is in the URL); use :func:`tooling_metadata_only`
    for that. The ``decisionTableParameters`` array is a **full replace** on PATCH.
    """
    return {"FullName": spec.get("fullName"), "Metadata": to_metadata(spec)}


def tooling_metadata_only(
    spec: Dict[str, Any], *, live_status: Optional[str] = None
) -> Dict[str, Any]:
    """Return the complete Metadata body for a Tooling update.

    Updates retain the platform's current status rather than taking lifecycle
    state from the spec. Tooling requires status and replaces the complex value,
    so callers must supply ``live_status`` for real requests.
    """
    body = to_metadata(spec)
    body.pop("status", None)
    if live_status:
        body["status"] = live_status
    return {"Metadata": body}
