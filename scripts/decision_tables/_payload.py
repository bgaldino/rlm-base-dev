#!/usr/bin/env python3
"""Pure canonical-spec → Metadata/Tooling payload translators for Decision Tables.

Part of the self-contained ``scripts/decision_tables/`` toolkit (imports only
``_schema`` from the package; nothing from ``tasks/``). Transport-agnostic and
dependency-free (stdlib only — no ``requests``, no CumulusCI, no ``sf`` CLI):
just the field-shaping the two supported authoring paths demand. This is the
Decision Table analogue of ``scripts/expression_sets/_payload.py``.

One author-facing *canonical spec* (validated by ``_schema.validate_spec``) is
translated onto the source-controlled Metadata and REST Tooling paths:

  * :func:`to_metadata` — the ``Metadata`` body shared by the Metadata API and
    the Tooling ``Metadata`` complexvalue (field names ``dataSourceType`` /
    ``filterResultBy`` / ``decisionTableParameters``, ``usage`` UPPER-case).
  * :func:`to_metadata_xml` — serializes that body to a ``.decisionTable-meta.xml``
    for a ``sf project deploy`` (elements emitted **alphabetically**, matching the
    MDAPI serializer and the shipped ``unpackaged/pre/5_decisiontables/*.xml``).
  * :func:`to_tooling` — wraps the metadata body as ``{"FullName", "Metadata"}``
    for a Tooling ``DecisionTable`` POST/PATCH.
Every function operates on plain dicts/lists and returns **new** structures —
none mutate their input, so a caller can translate the same spec for multiple
paths or verify against the original.

Provenance — all shapes live-verified on 262 / v67.0 against scratch orgs (the
create/update/GET-back captures behind each rule); see
``docs/references/decision-table-api-reference.md`` for the field-by-field detail.
"""

from typing import Any, Dict, List, Optional
from xml.sax.saxutils import escape as _xml_escape

# The MDAPI DecisionTable root namespace (matches the shipped source XML).
METADATA_NAMESPACE = "http://soap.sforce.com/2006/04/metadata"

# ``usage`` values that carry an operator + sequence (INPUT columns only). Any
# other usage (OUTPUT / ROWCRITERIA) drops those on both paths.
_INPUT_USAGES = {"INPUT"}

# Booleans the MDAPI serializer always emits (shipped XML carries all four even
# at their defaults). Filled with ``False`` in the metadata body for a stable,
# diff-clean XML + Tooling shape.
_METADATA_DEFAULT_BOOLS = {
    "doesConsiderNullValue": False,
    "hasIncrementalSyncFailed": False,
    "isIncrementalSyncEnabled": False,
    "isVersioned": False,
}

# Top-level scalar fields carried into the metadata body when present in the spec
# (fullName is NOT here — it is the file name / top-level ``FullName``, never a
# child element). Order is irrelevant: :func:`to_metadata_xml` sorts alphabetically.
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

    INPUT columns keep ``operator`` + ``sequence``; OUTPUT/ROWCRITERIA drop them
    (matching the shipped XML, where OUTPUT columns carry neither). ``fieldPath``
    defaults to ``fieldName`` (the shipped tables set them equal for direct
    fields). Booleans ``isGroupByField`` / ``isRequired`` default to ``False``.
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

    This body is shared by both metadata-authoring paths: :func:`to_metadata_xml`
    serializes it to a ``.decisionTable-meta.xml`` and :func:`to_tooling` wraps it
    under ``{"FullName", "Metadata"}``. Field names and casing are the
    Metadata/Tooling vocabulary (``dataSourceType`` / ``filterResultBy`` /
    ``decisionTableParameters``; ``usage`` UPPER). ``fullName`` is intentionally
    NOT included (it is the file name / top-level ``FullName``). A missing
    ``conditionCriteria`` is synthesized from the INPUT sequences.

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

    Shape: ``{"FullName": <api name>, "Metadata": {…}}`` — the live-verified
    Tooling create/update body. On a **PATCH** the caller sends only
    ``{"Metadata": {…}}`` (the id is in the URL); use :func:`tooling_metadata_only`
    for that. The ``decisionTableParameters`` array is a **full replace** on PATCH.
    """
    return {"FullName": spec.get("fullName"), "Metadata": to_metadata(spec)}


def tooling_metadata_only(
    spec: Dict[str, Any], *, live_status: Optional[str] = None
) -> Dict[str, Any]:
    """Canonical spec → ``{"Metadata": {…}}`` for a Tooling PATCH (id is in the URL).

    The spec's own ``status`` is always **dropped** — it must never drive the
    table's lifecycle on an *update*. An author reusing a create spec or a describe
    round-trip very plausibly carries ``Active``; letting it ride along in the
    definition-edit PATCH would fight the deactivate-first guard and re-activate
    the table mid-sequence, before the guarded reactivate.

    A Tooling ``Metadata`` PATCH nonetheless **requires** ``status`` — a status-free
    body is rejected with ``FIELD_INTEGRITY_EXCEPTION: Required field is missing:
    status`` (live-confirmed 262 / v67.0 against a Draft scratch table). So the
    caller passes the table's **current live** ``status`` (read at PATCH time, e.g.
    via :meth:`_lifecycle.LifecycleEngine.get_status`) as ``live_status`` and it is
    stamped onto the body. In the deactivate-first sequence the engine has already
    flipped the live status to ``Inactive``, so the definition edit *re-asserts the
    status the table already has* and stays lifecycle-neutral — never the spec's.
    The lifecycle engine (:class:`_lifecycle.LifecycleEngine`) remains the **sole**
    owner of the Active↔Inactive transitions (its own full-``Metadata`` PATCHes).

    ``live_status`` is optional only so this pure translator stays callable without a
    transport in tests; a real PATCH must pass it (the platform rejects the body
    otherwise). The Tooling ``Metadata`` complexvalue is replaced **wholesale** (see
    :meth:`_lifecycle.LifecycleEngine._current_metadata` — a sparse body wipes the
    omitted fields), so the body carries the full definition. Create uses
    :func:`to_tooling`, not this: it honors the spec's requested ``status`` directly
    (the platform is the authority — an accepted write is faithful, a bad status is
    rejected with a clear error), so this update-only status-stripping does not apply
    there.
    """
    body = to_metadata(spec)
    body.pop("status", None)
    if live_status:
        body["status"] = live_status
    return {"Metadata": body}


# --------------------------------------------------------------------------- #
# Metadata API XML serialization
# --------------------------------------------------------------------------- #

def _xml_scalar(value: Any) -> str:
    """Render a scalar as XML element text (bools lower-cased, everything escaped)."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return _xml_escape(str(value))


def _render_element(name: str, value: Any, indent: str) -> List[str]:
    """Render one top-level element (scalar, or repeated blocks for a list value).

    A list value (``decisionTableParameters`` / ``decisionTableSourceCriterias``)
    emits one ``<name>…</name>`` block per entry, each with its own children
    sorted alphabetically (matching the MDAPI serializer). ``None``/empty scalars
    are skipped by the caller, so this only sees real values.
    """
    lines: List[str] = []
    if isinstance(value, list):
        for entry in value:
            lines.append(f"{indent}<{name}>")
            if isinstance(entry, dict):
                for child in sorted(entry.keys()):
                    child_val = entry[child]
                    if child_val is None or child_val == "":
                        continue
                    lines.append(
                        f"{indent}    <{child}>{_xml_scalar(child_val)}</{child}>"
                    )
            lines.append(f"{indent}</{name}>")
    else:
        lines.append(f"{indent}<{name}>{_xml_scalar(value)}</{name}>")
    return lines


def to_metadata_xml(spec: Dict[str, Any]) -> str:
    """Canonical spec → a ``.decisionTable-meta.xml`` string (Metadata API source).

    Elements are emitted **alphabetically** to match the platform's MDAPI
    serializer and the shipped ``unpackaged/pre/5_decisiontables/*.xml`` (so a
    round-trip / drift diff stays clean). The result is written to an SFDX package
    and deployed with ``sf project deploy start``; the *file name* carries the api
    name (``<fullName>.decisionTable-meta.xml``), so ``fullName`` is not an
    element here — see :func:`meta_file_name`.
    """
    body = to_metadata(spec)
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             f'<DecisionTable xmlns="{METADATA_NAMESPACE}">']
    for name in sorted(body.keys()):
        value = body[name]
        if value is None or value == "":
            continue
        lines.extend(_render_element(name, value, "    "))
    lines.append("</DecisionTable>")
    return "\n".join(lines) + "\n"


def meta_file_name(spec: Dict[str, Any]) -> str:
    """The source-format file name for a spec: ``<fullName>.decisionTable-meta.xml``."""
    return f"{spec.get('fullName')}.decisionTable-meta.xml"
