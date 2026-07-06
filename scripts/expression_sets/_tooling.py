#!/usr/bin/env python3
"""Tooling-API access for the one thing Connect can't touch: BRE step **labels**.

Part of the self-contained ``scripts/expression_sets/`` toolkit (imports nothing
from ``tasks/``). Every OTHER read/write in this toolkit goes through the Connect
resource ``connect/business-rules/expression-set/{9QL}`` — but a step's readable
``label`` is **absent from the Connect representation entirely** (GET never
serializes it; POST/PATCH reject it with ``JSON_PARSER_ERROR: Unrecognized field
"label"``). A Connect full-graph PATCH therefore *rebuilds* every label from the
spaceless ``name`` on every write, so the only place labels can be read or written
is the Tooling sObject ``ExpressionSetDefinitionVersion.Metadata.steps[].label``.

This module is the seam for that (live-verified on 262 / v67.0):

  * **Pure** helpers (no org, unit-tested): read labels off a Tooling ``Metadata``
    blob (:func:`step_labels`), find steps that lack a readable label
    (:func:`label_drift`), humanize a spaceless name into a best-effort label
    (:func:`humanize_name`), and apply / derive a ``{name: label}`` map onto a
    ``Metadata`` blob (:func:`apply_labels` / :func:`derive_labels`). None mutate
    their input.
  * **I/O** helpers over a :class:`_client.Transport` (the same injectable seam the
    lifecycle engine takes, so a fake transport tests them without an org):
    resolve the Tooling version id (:func:`resolve_esdv`), GET its ``Metadata``
    (:func:`fetch_metadata`), and PATCH ``Metadata`` back (:func:`patch_metadata`,
    dropping the read-only ``urls`` key).

Object model: the Tooling ``ExpressionSetDefinitionVersion`` (prefix ``9QB``) is a
1:1 sibling of the runtime ``ExpressionSetVersion`` (prefix ``9QM``) — its
``DeveloperName`` equals the 9QM ``ApiName`` (e.g.
``RLM_DefaultPricingProcedure_V1``). That equality is the join key, so a relabel
targets the *exact* version the lifecycle engine deactivates.

**Active-version guard applies.** A Tooling ``Metadata`` PATCH on an *active*
version returns ``INVALID_ID_FIELD: LatestVersionSnapshotId not found`` and does
NOT persist. The write must run inside the deactivate → PATCH → reactivate
lifecycle (:class:`_lifecycle.LifecycleEngine`), exactly like a Connect mutation —
and, because a Connect mutation clobbers labels, a relabel must run **last**.
"""

import re
from copy import deepcopy
from typing import Any, Dict, List, Optional
from urllib.parse import quote

ESDV_SOBJECT = "ExpressionSetDefinitionVersion"

# The one read-only key inside a Tooling ``Metadata`` blob that a PATCH rejects:
# ``urls`` is server-emitted (per-record REST hrefs) and echoing it back on write
# fails. Everything else round-trips. Deny-list (not allow-list) so a future
# writable Metadata field survives the PATCH untouched.
_METADATA_READONLY_KEYS = frozenset({"urls"})


class ToolingError(RuntimeError):
    """Raised on a Tooling-API failure specific to label read/write."""


# ----------------------------------------------------------------------
# Pure helpers (no org; unit-tested)
# ----------------------------------------------------------------------


def step_labels(metadata: dict) -> Dict[str, Optional[str]]:
    """Return ``{step name: label}`` for every named step in a Tooling ``Metadata``.

    ``label`` may be ``None`` (a step with no label) — kept, not dropped, so a
    caller can distinguish "no label" from "step absent". Pure.
    """
    out: Dict[str, Optional[str]] = {}
    for step in metadata.get("steps") or []:
        if isinstance(step, dict) and step.get("name"):
            out[step["name"]] = step.get("label")
    return out


def label_drift(metadata: dict) -> List[str]:
    """Names of steps that lack a readable label (label missing or == name).

    ``label == name`` is the fingerprint of a Connect-created / Connect-clobbered
    step (Connect rebuilds the label from the spaceless name). These are exactly
    the steps a relabel should target. Pure.
    """
    return [
        name
        for name, label in step_labels(metadata).items()
        if not label or label == name
    ]


def humanize_name(name: str) -> str:
    """Best-effort readable label from a spaceless API name. **Lossy.**

    Splits underscores and camelCase boundaries and collapses whitespace:
    ``ApplyHeaderPriceOverride`` → ``Apply Header Price Override``. It CANNOT
    recover casing/punctuation the original label carried that despacing
    discarded — an all-lowercase run-on
    (``Applyamountbasedandpercentagebaseddiscounts``) comes back essentially
    unchanged. Callers must warn that ``--auto`` output is approximate and prefer
    an explicit ``{name: label}`` map when the true labels are known. Pure.
    """
    if not name:
        return name
    s = name.replace("_", " ")
    # camelCase / PascalCase boundary: lower|digit → Upper
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", s)
    # acronym boundary: UPPER → Upper+lower (e.g. "ESVName" → "ESV Name")
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def apply_labels(
    metadata: dict, name_to_label: Dict[str, str], *, logger=None
) -> tuple:
    """Apply a ``{name: label}`` map onto a copy of ``Metadata``.

    Returns ``(new_metadata, changed_names)`` — a NEW dict (input not mutated) and
    the sorted list of step names whose label actually changed. A map entry whose
    label already matches, or whose name matches no step, is a no-op. An empty /
    ``None`` label value is skipped (never blanks an existing label). Pure.
    """
    result = deepcopy(metadata)
    changed: List[str] = []
    for step in result.get("steps") or []:
        if not isinstance(step, dict):
            continue
        name = step.get("name")
        if name in name_to_label:
            new_label = name_to_label[name]
            if new_label and step.get("label") != new_label:
                step["label"] = new_label
                changed.append(name)
    if logger and changed:
        logger(f"Relabeled {len(changed)} step(s): {', '.join(sorted(changed))}")
    return result, sorted(changed)


def derive_labels(metadata: dict, *, only_drift: bool = True) -> Dict[str, str]:
    """Build a ``{name: humanized-label}`` map via :func:`humanize_name`.

    With ``only_drift`` (default) only steps that currently lack a readable label
    (``label`` missing or == name) are included, so a derive-then-apply pass
    touches only the run-on names and leaves good labels alone. Set it False to
    re-derive every step. Best-effort / lossy — see :func:`humanize_name`. Pure.
    """
    out: Dict[str, str] = {}
    for name, label in step_labels(metadata).items():
        if only_drift and label and label != name:
            continue
        out[name] = humanize_name(name)
    return out


def strip_metadata_readonly(metadata: dict) -> dict:
    """Drop the read-only keys a Tooling ``Metadata`` PATCH rejects (``urls``).

    Returns a NEW dict; input not mutated. Currently only ``urls`` — a deny-list
    so any future writable field survives untouched.
    """
    return {k: v for k, v in metadata.items() if k not in _METADATA_READONLY_KEYS}


# ----------------------------------------------------------------------
# I/O helpers (over a _client.Transport; testable with a fake transport)
# ----------------------------------------------------------------------


def _tooling_query(transport, soql: str) -> List[Dict[str, Any]]:
    """Run a Tooling SOQL query and return its ``records`` (reads always execute).

    Uses the Tooling query endpoint (``tooling/query``) — ``ExpressionSetDefinition
    Version`` is a Tooling entity, and its ``Metadata`` field is only reachable
    through the Tooling sObject API, so we resolve it there too for consistency.
    """
    resp = transport.connect("GET", f"tooling/query?q={quote(soql)}")
    if isinstance(resp, dict):
        return [r for r in resp.get("records", []) if isinstance(r, dict)]
    return []


def _soql_literal(value: Any) -> str:
    return str(value).replace("\\", "\\\\").replace("'", "\\'")


def resolve_esdv(
    transport,
    *,
    version_api_name: Optional[str] = None,
    developer_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Resolve the Tooling ``ExpressionSetDefinitionVersion`` (9QB) record.

    Prefer ``version_api_name`` (the runtime ``ExpressionSetVersion.ApiName``,
    which equals the 9QB ``DeveloperName``) — it pins the label write to the exact
    version the lifecycle engine deactivates. Falls back to ``developer_name`` (the
    ``ExpressionSetDefinition`` DeveloperName), taking the highest ``VersionNumber``.

    Returns the record dict (``Id``, ``DeveloperName``, ``VersionNumber``). Raises
    :class:`ToolingError` if none match or neither identifier is given.
    """
    if version_api_name:
        where = f"DeveloperName = '{_soql_literal(version_api_name)}'"
    elif developer_name:
        where = (
            "ExpressionSetDefinition.DeveloperName = "
            f"'{_soql_literal(developer_name)}'"
        )
    else:
        raise ToolingError(
            "resolve_esdv requires version_api_name or developer_name."
        )
    records = _tooling_query(
        transport,
        f"SELECT Id, DeveloperName, VersionNumber FROM {ESDV_SOBJECT} "
        f"WHERE {where} ORDER BY VersionNumber DESC",
    )
    if not records:
        target = version_api_name or developer_name
        raise ToolingError(
            f"No {ESDV_SOBJECT} found for '{target}'. Confirm the expression set "
            f"and version exist in the org."
        )
    return records[0]


def fetch_metadata(transport, esdv_id: str) -> Dict[str, Any]:
    """GET a Tooling ``ExpressionSetDefinitionVersion.Metadata`` blob (read).

    Returns the ``Metadata`` sub-dict (steps carry ``label``). Reads always
    execute, even under a dry-run transport. Raises :class:`ToolingError` if the
    record has no ``Metadata``.
    """
    resp = transport.connect(
        "GET", f"tooling/sobjects/{ESDV_SOBJECT}/{esdv_id}"
    )
    metadata = (resp or {}).get("Metadata") if isinstance(resp, dict) else None
    if not isinstance(metadata, dict):
        raise ToolingError(
            f"{ESDV_SOBJECT} {esdv_id} returned no Metadata "
            f"(cannot read/write labels)."
        )
    return metadata


def patch_metadata(transport, esdv_id: str, metadata: dict) -> Any:
    """PATCH a Tooling ``Metadata`` blob (write). Skipped+logged under dry-run.

    Strips the read-only ``urls`` key first and wraps the blob in the sObject
    ``{"Metadata": …}`` envelope. **Caller must have deactivated the version** —
    a PATCH on an active version returns ``INVALID_ID_FIELD:
    LatestVersionSnapshotId not found`` and does not persist. Route this through
    :meth:`_lifecycle.LifecycleEngine.run_mutation` so the guard is enforced.
    """
    body = {"Metadata": strip_metadata_readonly(metadata)}
    return transport.connect(
        "PATCH", f"tooling/sobjects/{ESDV_SOBJECT}/{esdv_id}", body
    )
