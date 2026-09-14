#!/usr/bin/env python3
"""Shared, dependency-free SFDMU ``export.json`` parsing primitives.

One home for the handful of rules that decode an SFDMU plan the way SFDMU itself
does — how a plan's passes are laid out, how an object's API name is read off its
SOQL query, which fields a SELECT lists, and how the `operation`/`excluded`
declarations resolve. At least five files each grew their own copy of these
(the validator, the two plan-README scripts, `tasks/rlm_sfdmu.py`, and
`diff_schemas.py`), and they drifted apart in ways three separate todo packs
document as bugs. This module is where the one true copy lives so a fix lands
once (see todo pack 191 and the follow-ons it blocks).

**Dependency-free by contract.** No `cumulusci`, no import of the validator's
`ValidationResult` or any other reporting machinery — a CCI task
(`tasks/rlm_sfdmu.py`) and a plain script (`diff_schemas.py`) must both be able
to import this without dragging in the validator's world. These functions return
plain data; a caller that wants to *report* on what they return does that with
its own machinery.

The canonical implementations were extracted verbatim from
`validate_sfdmu_v5_datasets.py` (the most complete/guarded copy); their long-form
rationale lives in that file's git history and in the referenced packs. Behavior
is intentionally identical to that pre-extraction copy — the behavioral fixes
(SFDMU unshift semantics, case-insensitive object identity, etc.) land as
follow-on commits ON this module, each with its own before/after test, so a
regression stays attributable.
"""

import re
from typing import List, Optional

# The TypeScript numeric enum SFDMU loads `operation` against, index-ordered.
# Index 8 (`unknown`) is the enum's own fallback: a value that resolves to a
# committed enum member but not a real, actionable operation. Mirrors
# `ScriptLoader`'s `OPERATION` enum (v5.8.0).
SFDMU_OPERATION_BY_INDEX = ("insert", "update", "upsert", "readonly", "delete",
                            "deletesource", "deletehierarchy", "harddelete", "unknown")


def normalize_object_sets(export_data: dict) -> List[dict]:
    """The plan's passes, with a flat `objects` plan presented as a single pass.

    A plan may declare its objects either under `objectSets` (multi-pass) or as a
    flat top-level `objects` list. Callers that need "the passes" must agree on
    this normalization — historically they disagreed, which is a silent wrong
    answer rather than an error, so it lives in one place.
    """
    object_sets = export_data.get("objectSets") or []
    if not object_sets and "objects" in export_data:
        return [{"objects": export_data["objects"]}]
    return object_sets


def extract_object_name(query: str) -> str:
    """Extract the object API name from a SOQL query, or "" if not found.

    Non-string `query` returns "" rather than raising: `re.search` on a non-str
    raises `TypeError`, which would take a whole run down over one malformed
    declaration; "" makes the caller skip the declaration, which callers already
    handle (`if not obj_name`).
    """
    if not isinstance(query, str):
        return ""
    match = re.search(r'\sFROM\s+(\w+)', query, re.IGNORECASE)
    return match.group(1) if match else ""


def parse_select_fields(query: str) -> List[str]:
    """Field names from a SOQL SELECT clause (incl. relationship traversals like
    `Product.Name`), or [] if the query is non-string or has no parseable SELECT."""
    if not isinstance(query, str):
        return []
    match = re.search(r'SELECT\s+(.+?)\s+FROM', query, re.IGNORECASE | re.DOTALL)
    if not match:
        return []
    fields_str = match.group(1)
    # Split by comma, strip whitespace
    fields = [f.strip() for f in fields_str.split(',')]
    return fields


def is_js_truthy(value) -> bool:
    """Python truthiness corrected to match SFDMU's JS truthiness for a JSON value.

    Diverges from Python for containers: `[]`/`{}` are falsy in Python but truthy
    in JS, so `"excluded": []`/`{}` is dropped by SFDMU (JS reads `object.excluded`
    as truthy) while a plain `if cfg.get("excluded")` would read it as live — a
    false read. Every boolean-like field SFDMU reads with plain JS truthiness
    (`deleteOldData`, top-level `useSeparatedCSVFiles`, `excluded`) goes through
    this same helper for the identical reason.
    """
    if isinstance(value, (list, dict)):
        return True
    return bool(value)


def resolve_operation(value) -> Optional[str]:
    """The canonical lowercase enum name SFDMU would resolve `value` to, or `None`
    if SFDMU cannot resolve it. Mirrors `ScriptLoader._resolveOperation` (v5.8.0).

    `None` does NOT mean a safe default — SFDMU leaves the raw, unresolved value
    in place on the object instead, and still writes it from source.

    Order matters: `bool` is checked before `int` because `isinstance(True, int)`
    is `True` in Python, but JS `typeof true === 'boolean'` fails the loader's
    `typeof operation === 'number'` check — a Boolean is always dropped, never read
    as 0/1. An integral `float` (`2.0`, which `json.load` produces for that literal)
    is accepted alongside `int`: JS has one numeric type, so `OPERATION[2.0]` is the
    same lookup as `OPERATION[2]`. `2.5`/`nan`/`inf` fail `is_integer()` and fall
    through. The string branch matches `SFDMU_OPERATION_BY_INDEX`, so the literal
    `"Unknown"` resolves to `"unknown"` (index 8), the same committed value a numeric
    `8` resolves to — distinct from a value that fails resolution outright (`None`).
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, int) or (isinstance(value, float) and value.is_integer()):
        idx = int(value)
        return (SFDMU_OPERATION_BY_INDEX[idx]
                if 0 <= idx < len(SFDMU_OPERATION_BY_INDEX) else None)
    if isinstance(value, str):
        normalized = value.strip().lower()
        return normalized if normalized in SFDMU_OPERATION_BY_INDEX else None
    return None
