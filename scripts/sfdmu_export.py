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
(SFDMU unshift semantics, subquery-aware `FROM`/`SELECT` parsing, etc.) land as
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

    Mirrors SFDMU's own `ScriptLoader._normalizeObjectSets` (v5.8.0), which is a
    MERGE, not a precedence pick: a non-empty top-level `objects` array is
    `unshift`ed as `objectSets[0]` — prepended as pass 1, ahead of any existing
    `objectSets` — unconditionally on `objects` being non-empty. It does NOT check
    whether `objectSets` is already populated. So a plan carrying BOTH a non-empty
    `objectSets` and a non-empty `objects` runs `objects` as an *additional*,
    prepended pass; the earlier "objectSets wins outright, objects never read"
    rule silently dropped every object declared only in that top-level `objects`
    (todo pack 168). Guarded on `objects` being a non-empty list, matching JS's
    `Array.isArray(objects) && objects.length > 0`; an empty/absent `objects`
    leaves `objectSets` untouched. Returns a new list — never mutates the input.
    """
    object_sets = export_data.get("objectSets")
    if not isinstance(object_sets, list):
        object_sets = []
    objects = export_data.get("objects")
    if isinstance(objects, list) and objects:
        return [{"objects": objects}, *object_sets]
    return list(object_sets)


def _strip_parenthesized(query: str) -> str:
    """Return `query` with every parenthesized group (and its contents) removed.

    A SOQL query may carry a SELECT-clause subquery — `SELECT Id, (SELECT Id FROM
    Contacts) FROM Account` — whose own `FROM Contacts` is the *first* `FROM` in the
    string. The plain `\\sFROM\\s+(\\w+)` / non-greedy `SELECT\\s+(.+?)\\s+FROM` regexes
    below both stop at that inner `FROM`, misidentifying the object as `Contacts` and
    truncating the field list. Removing the parenthesized groups first (depth-tracked,
    so nested subqueries collapse too) leaves the outer `SELECT … FROM Account`, which
    the same regexes then read correctly.

    SOQL single-quoted string literals are tracked (with `\\` escapes), so a parenthesis
    *inside* a quoted value — `… WHERE Name = '(' …` — is not counted as structural.
    Without that, a child subquery carrying such a literal (`SELECT Id, (SELECT Id FROM
    Contacts WHERE Name = '(') FROM Account`) would leave `depth` non-zero at the subquery's
    real closing paren, strip the outer `FROM Account`, and make both callers report the
    declaration unparseable. A removed top-level group is replaced with a single space so
    the tokens it sat between do not glue together.

    Baseline-neutral on every shipped plan: the only parentheses in tracked queries are
    in trailing `WHERE … IN ( … )` clauses, which sit *after* the outer `FROM` — the
    `SELECT … FROM` match already terminates before them, so stripping them changes
    nothing. It bites only on a genuine SELECT-clause subquery, which no plan uses today.
    """
    out, depth, in_str, escaped = [], 0, False, False
    for ch in query:
        if in_str:
            if depth == 0:
                out.append(ch)
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == "'":
                in_str = False
            continue
        if ch == "'":
            in_str = True
            if depth == 0:
                out.append(ch)
        elif ch == '(':
            depth += 1
        elif ch == ')':
            if depth > 0:
                depth -= 1
                if depth == 0:
                    out.append(' ')  # separator where a top-level group was removed
        elif depth == 0:
            out.append(ch)
    return ''.join(out)


def extract_object_name(query: str) -> str:
    """Extract the object API name from a SOQL query, or "" if not found.

    Non-string `query` returns "" rather than raising: `re.search` on a non-str
    raises `TypeError`, which would take a whole run down over one malformed
    declaration; "" makes the caller skip the declaration, which callers already
    handle (`if not obj_name`).

    Subquery-aware: parenthesized groups are stripped first so a SELECT-clause
    subquery's inner `FROM` cannot be mistaken for the outer object — see
    `_strip_parenthesized`. The name is returned in its original SOQL casing and
    callers key on it exactly, never case-folded: SFDMU reads each object's CSV at
    `path.join(rootPath, sObjectName)` with `sObjectName` this raw name and no case
    normalization (`Common.getCSVFilename`; `ScriptObject.name = parsed.sObject`), so
    `FROM Account` and `FROM account` are different files on case-sensitive Linux.
    Folding identity would credit a CSV SFDMU never reads and hide a missing-file
    error (todo pack 163 — the fold was tried and reverted for exactly this).
    """
    if not isinstance(query, str):
        return ""
    match = re.search(r'\sFROM\s+(\w+)', _strip_parenthesized(query), re.IGNORECASE)
    return match.group(1) if match else ""


def parse_select_fields(query: str) -> List[str]:
    """Field names from a SOQL SELECT clause (incl. relationship traversals like
    `Product.Name`), or [] if the query is non-string or has no parseable SELECT.

    Subquery-aware (see `_strip_parenthesized`): a SELECT-clause subquery is removed
    before the SELECT…FROM match, so the outer query's fields are read rather than the
    subquery's truncated ones. Empty tokens are dropped, so the comma a removed subquery
    leaves behind (`SELECT Id, (…) FROM X` -> `SELECT Id,  FROM X`) does not yield a
    spurious `""` field."""
    if not isinstance(query, str):
        return []
    match = re.search(r'SELECT\s+(.+?)\s+FROM', _strip_parenthesized(query),
                      re.IGNORECASE | re.DOTALL)
    if not match:
        return []
    fields_str = match.group(1)
    # Split by comma, strip whitespace, drop empties (e.g. a trailing comma left by a
    # stripped subquery).
    fields = [f.strip() for f in fields_str.split(',') if f.strip()]
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


# `object-set-` then a non-negative integer with NO leading zero and nothing else.
# `re.fullmatch` (anchored both ends) rejects `object-set-1-backup`; `0|[1-9]\d*`
# rejects `object-set-01`. Both are names SFDMU never reads — it builds the path it
# reads from the pass index (Script.js: OBJECT_SET_SUBDIRECTORY_PREFIX +
# String(objectSetIndex + 1)), always canonical — so a caller that matches loosely
# either credits a directory SFDMU ignores (the validator) or copies dead weight into
# source/ (the runtime sync in tasks/rlm_sfdmu.py). `object-set-0` is admitted here so
# callers can range-check it and report it through their own out-of-range path rather
# than as a name error (it's the likely 1-based-vs-0-based typo).
#
# `re.ASCII` is required: without it Python's `\d` matches Unicode decimal digits
# (and `int()` parses them), so `object-set-1١` would match and resolve to 11 — but
# SFDMU builds names from JS `String(index + 1)`, which is ASCII-only, so no such
# directory is ever a real pass. Restrict `\d` to `[0-9]` so a Unicode-digit name is
# rejected as non-canonical, matching what SFDMU can actually read.
_OBJECT_SET_DIR_RE = re.compile(r"object-set-(0|[1-9]\d*)", re.ASCII)


def object_set_dir_number(name) -> Optional[int]:
    """The 1-based pass number encoded in a canonical `object-set-N` directory name,
    returned AS WRITTEN (so `object-set-0` -> 0), or `None` if `name` is not canonical.

    One home for the object-set directory rule the SFDMU validator and the
    `tasks/rlm_sfdmu.py` runtime sync each used to spell differently (pack 161): the
    validator matched strictly here and the sync matched loosely with `startswith`, so
    a non-canonical directory was flagged by one and silently mis-copied by the other.
    A non-string `name` returns `None` rather than raising.
    """
    if not isinstance(name, str):
        return None
    match = _OBJECT_SET_DIR_RE.fullmatch(name)
    return int(match.group(1)) if match else None
