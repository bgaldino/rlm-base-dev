#!/usr/bin/env python3
"""Pure payload-shaping for BRE Expression Set Connect mutations.

Part of the self-contained ``scripts/expression_sets/`` toolkit (imports nothing
from ``tasks/``). Transport-agnostic, dependency-free (no ``requests``, no
CumulusCI, no ``sf`` CLI): the exact verb-specific field rules and HTML-entity
normalization the Connect API demands. It mirrors the rules the CCI task
(``tasks/rlm_expression_set_connect.py``, reference-only) applies, so the CLIs
shape identical payloads — without sharing code with the task.

Everything here operates on plain dicts/lists (a parsed Connect GET payload) and
returns new structures — none of these functions mutate their input, so a caller
can shape a payload and still verify against the original.

The rules encoded here were verified live on 262 / v67.0; see
``docs/references/expression-set-connect-api-reference.md`` and the module
docstring of ``tasks/rlm_expression_set_connect.py`` for provenance:

  * **Top-level ``id``/``error`` are output-only** — the Connect GET emits them,
    the PATCH/POST parser rejects them. Always stripped.
  * **The version-level ``id`` is verb-dependent.** A PATCH (replace) KEEPS it
    (the server matches the version in place; stripping it makes the server
    treat the version as new and gack). A POST-create OMITS it (a create body
    carrying a source-org 9QM id makes the server reject or mis-bind the new
    version).
  * **A PATCH must carry the TARGET org's version id.** An export-from-source /
    import-into-target workflow carries the *source* org's id; rewrite it to the
    id resolved in the target org before the PATCH.
  * **The Connect GET serializer HTML-escapes JSON-in-string content**
    (``customElement.parameters[].value``, ``advancedCondition.criteria[].value``,
    formula text) as ``&quot;``/``&#39;``. JSON carries no entity layer, so the
    engine's value sub-parser rejects the literal entities on input. Every
    mutation HTML-unescapes the payload immediately before the Connect call.
"""

import html
from typing import Any, Dict


# Top-level output-only fields the Connect API rejects on PATCH/POST. Deny-list,
# not allow-list: the Input representation accepts almost every field the Output
# representation returns; only these output-only ones must be removed.
TOP_LEVEL_DENY = frozenset({"id", "error"})


def strip_readonly_fields(payload: dict, for_create: bool = False) -> dict:
    """Remove output-only fields the Connect API rejects on PATCH/POST.

    Keeps everything else, including top-level ``interfaceSourceType`` /
    ``resourceInitializationType`` / ``contextDefinitions``. The version-level
    ``id`` is kept for a PATCH (which needs it to match in place) and stripped
    when ``for_create`` is set (a POST-create must not carry a source-org id).

    The Connect endpoint names the definition with ``apiName`` and **rejects**
    the SObject field name ``developerName`` (``JSON_PARSER_ERROR: Unrecognized
    field "developerName"``). Since the import CLI accepts either as the input's
    name field, fold ``developerName`` into ``apiName`` (when ``apiName`` is
    absent) and drop it — on both verbs.

    Returns a new dict; does not mutate the input (so the caller's payload can
    be re-shaped for a different verb or verified against the original).
    """
    stripped = {k: v for k, v in payload.items() if k not in TOP_LEVEL_DENY}
    if "developerName" in stripped:
        dev_name = stripped.pop("developerName")
        stripped.setdefault("apiName", dev_name)
    if for_create:
        versions = stripped.get("versions")
        if isinstance(versions, list):
            stripped["versions"] = [
                {k: v for k, v in version.items() if k != "id"}
                if isinstance(version, dict)
                else version
                for version in versions
            ]
    return stripped


def rewrite_version_id(payload: dict, target_version_id: str) -> dict:
    """Rewrite ``versions[0].id`` to the target org's version id for a PATCH.

    An export-from-source / import-into-target workflow carries the source org's
    version id in the payload, while the Connect PATCH endpoint matches on the
    target version id. Without this rewrite the server rejects or mis-binds the
    version. Idempotent when the id already matches (same-org re-import).

    Mutates and returns ``payload`` (matching the CCI task's historical
    behavior — the task chains ``strip`` → ``rewrite`` → ``normalize`` on a
    payload it already owns). Only the first/active version is rewritten: the
    PATCH operates on a single version at a time.
    """
    versions = payload.get("versions")
    if not isinstance(versions, list) or not versions:
        return payload
    first = versions[0]
    if isinstance(first, dict):
        first["id"] = target_version_id
    return payload


def unescape_value(value: Any) -> Any:
    """Recursively HTML-unescape every string leaf in a JSON-like value.

    ``html.unescape()`` is the exact inverse of a single escape pass and a no-op
    on entity-free strings, so a full recursive walk over string leaves is safe
    and correct. Returns a new structure; does not mutate the input.
    """
    if isinstance(value, str):
        return html.unescape(value)
    if isinstance(value, list):
        return [unescape_value(v) for v in value]
    if isinstance(value, dict):
        return {k: unescape_value(v) for k, v in value.items()}
    return value  # int / float / bool / None pass through unchanged


def normalize_html_entities(payload: dict, enabled: bool = True) -> dict:
    """HTML-unescape all string leaves before a Connect PATCH/POST.

    ``enabled=False`` is a probe escape hatch to reproduce the un-normalized
    gack on demand — it returns the payload unchanged. Otherwise delegates to
    :func:`unescape_value` (a new structure; input not mutated).
    """
    if not enabled:
        return payload
    return unescape_value(payload)
