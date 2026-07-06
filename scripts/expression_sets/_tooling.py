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
  * **Label preservation** around a clobbering Connect mutation: snapshot the
    readable labels a PATCH is about to reset (:func:`capture_labels`) and re-apply
    them afterwards
    (:func:`restore_labels_after_clobber`) — a deliberate SECOND deactivate →
    Tooling PATCH → reactivate cycle that reuses the shared relabel core
    (:func:`relabel_version`, also the engine behind ``relabel_expression_set.py``),
    rather than smuggling a label into the Connect body (Connect has no label
    field). Seed a name→label map from a shipped ``.expressionSetDefinition-meta.xml``
    with :func:`labels_from_metadata_xml`.

Object model: the Tooling ``ExpressionSetDefinitionVersion`` (prefix ``9QB``) is a
1:1 sibling of the runtime ``ExpressionSetVersion`` (prefix ``9QM``). Do **not**
join them by ``9QB.DeveloperName == 9QM.ApiName`` after a Connect full-graph
PATCH: that ``DeveloperName`` has been observed changing in place. Use the stable
``ExpressionSetDefinitionId`` (9QA) plus ``VersionNumber`` whenever the caller can
supply it, so a relabel targets the *exact* version the lifecycle engine
deactivates.

**Active-version guard applies.** A Tooling ``Metadata`` PATCH on an *active*
version returns ``INVALID_ID_FIELD: LatestVersionSnapshotId not found`` and does
NOT persist. The write must run inside the deactivate → PATCH → reactivate
lifecycle (:class:`_lifecycle.LifecycleEngine`), exactly like a Connect mutation —
and, because a Connect mutation clobbers labels, a relabel must run **last**.
"""

import re
import xml.etree.ElementTree as ET
from copy import deepcopy
from typing import Any, Dict, List, Optional
from urllib.parse import quote

from ._client import ExpressionSetClientError, soql_literal

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


def readable_labels(metadata: dict) -> List[str]:
    """Names of steps that DO have a readable label (label present and != name).

    The complement of :func:`label_drift` — the steps a Connect full-graph PATCH
    would reset to their spaceless name. Used to size the pre-PATCH clobber
    warning ("N labels will be reset"). Pure.
    """
    return [
        name
        for name, label in step_labels(metadata).items()
        if label and label != name
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


# Namespace on every Salesforce Metadata-API XML root.
_MD_NS = "{http://soap.sforce.com/2006/04/metadata}"


def labels_from_metadata_xml(xml_text: str) -> Dict[str, str]:
    """Parse ``{step name: label}`` from a ``.expressionSetDefinition-meta.xml``.

    The source-controlled Metadata XML is the authoritative name→label registry
    for a *shipped* procedure: every ``<steps>`` element carries its own direct
    ``<name>`` and ``<label>`` children (distinct from the nested
    ``<parameters><name>`` / ``<variables><name>`` tags, which we ignore by
    reading only the step element's *direct* children). Only steps that have BOTH
    a name and a non-empty label are returned. Pure — no org, no I/O beyond the
    passed-in string. Raises :class:`ToolingError` on unparseable XML.

    Note this seeds labels by *name*: it can restore a step whose name is
    unchanged from the repo, but a step the operator renamed on the target org
    won't match (use a live capture for those — see :func:`capture_labels`).
    """
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise ToolingError(f"Could not parse expressionSetDefinition XML: {exc}")
    out: Dict[str, str] = {}
    # <steps> can appear under the root or nested in <versions>; findall over the
    # whole tree catches both. Namespaced tag names use the metadata NS.
    for steps_el in root.iter(f"{_MD_NS}steps"):
        name = steps_el.findtext(f"{_MD_NS}name")
        label = steps_el.findtext(f"{_MD_NS}label")
        if name and label:
            out[name] = label
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


def resolve_esdv(
    transport,
    *,
    es_def_id: Optional[str] = None,
    version_number: Optional[int] = None,
    version_api_name: Optional[str] = None,
    developer_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Resolve the Tooling ``ExpressionSetDefinitionVersion`` (9QB) record.

    Resolution priority (most stable identifier first):

      1. ``es_def_id`` — the parent ``ExpressionSetDefinition`` Id (9QA), optionally
         pinned to an exact ``version_number``. **This is the stable key** and the
         one every mutating/restore caller should use. Absent ``version_number``,
         takes the highest ``VersionNumber``.
      2. ``version_api_name`` — the runtime ``ExpressionSetVersion.ApiName``. This
         *usually* equals the 9QB ``DeveloperName``, but **that equality is NOT
         stable across a Connect full-graph PATCH**: a Connect PATCH rewrites the
         ESDV ``DeveloperName`` in place (live-verified 262/v67.0 — the same 9QB Id
         came back under an unrelated ``DeveloperName`` after an overlay apply), so
         a lookup by ``DeveloperName`` right after a Connect mutation can miss.
         Prefer ``es_def_id`` in any post-PATCH (restore/relabel) path.
      3. ``developer_name`` — the ``ExpressionSetDefinition`` DeveloperName (highest
         ``VersionNumber``). Convenience for read-only callers.

    Returns the record dict (``Id``, ``DeveloperName``, ``VersionNumber``). Raises
    :class:`ToolingError` if none match or no identifier is given.
    """
    if es_def_id:
        where = f"ExpressionSetDefinitionId = '{soql_literal(es_def_id)}'"
        if version_number is not None:
            where += f" AND VersionNumber = {int(version_number)}"
    elif version_api_name:
        where = f"DeveloperName = '{soql_literal(version_api_name)}'"
    elif developer_name:
        where = (
            "ExpressionSetDefinition.DeveloperName = "
            f"'{soql_literal(developer_name)}'"
        )
    else:
        raise ToolingError(
            "resolve_esdv requires es_def_id, version_api_name, or developer_name."
        )
    records = _tooling_query(
        transport,
        f"SELECT Id, DeveloperName, VersionNumber FROM {ESDV_SOBJECT} "
        f"WHERE {where} ORDER BY VersionNumber DESC",
    )
    if not records:
        target = es_def_id or version_api_name or developer_name
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


def capture_labels(
    transport,
    version_api_name: Optional[str],
    logger=None,
    *,
    es_def_id: Optional[str] = None,
    version_number: Optional[int] = None,
) -> Dict[str, str]:
    """Snapshot the target version's readable ``{name: label}`` map (best-effort).

    Reads the current Tooling ``Metadata`` for the version and returns the labels
    for steps that HAVE a readable label (label present and != name) — the exact set
    a Connect full-graph PATCH is about to clobber. Taken BEFORE the clobbering PATCH
    so the labels can be re-applied afterwards to whatever steps survive under the
    same name (renamed / newly-added steps simply won't match on restore, which is
    correct — the snapshot only knows the pre-PATCH names).

    Resolves the Tooling version by the **stable** ``es_def_id`` (9QA) +
    ``version_number`` when the caller can supply them (a mutator always can), since
    the ESDV ``DeveloperName`` is unstable across a Connect PATCH; falls back to
    ``version_api_name`` for callers that only hold the runtime ApiName.

    **Best-effort and non-fatal by contract:** any failure (no version, Tooling
    read error, missing Metadata) is swallowed with an optional soft note and
    returns ``{}`` — capturing labels must never break a mutation. Pure-ish: one
    Tooling read, no writes.
    """
    if not (version_api_name or es_def_id):
        return {}
    try:
        esdv = resolve_esdv(
            transport, es_def_id=es_def_id, version_number=version_number,
            version_api_name=version_api_name,
        )
        metadata = fetch_metadata(transport, esdv["Id"])
    except (ToolingError, ExpressionSetClientError) as exc:
        if logger:
            logger(f"Note: could not capture step labels before the PATCH ({exc}).")
        return {}
    labels = step_labels(metadata)
    return {n: l for n, l in labels.items() if l and l != n}


def relabel_version(
    engine,
    *,
    es_def_id: str,
    esv: dict,
    name_to_label: Dict[str, str],
    activate_after: bool = True,
    cascade: bool = True,
    verify: bool = True,
) -> Dict[str, Any]:
    """Write step labels to a version's Tooling ``Metadata``, through the lifecycle.

    The shared relabel core used by BOTH ``relabel_expression_set.py`` (the
    standalone CLI) and the auto-restore step of the Connect mutators. Resolves the
    Tooling ``ExpressionSetDefinitionVersion`` via the **stable** ``es_def_id`` (9QA)
    + the version's ``VersionNumber`` — NOT the ESDV ``DeveloperName``, which a
    Connect full-graph PATCH rewrites in place (so the auto-restore path, which runs
    right after a Connect PATCH, would otherwise miss the record). Computes which
    labels actually change (skips no-ops / blanks / names absent from the version),
    and — only if something changes — runs the deactivate → Tooling PATCH →
    reactivate lifecycle via ``engine.run_mutation`` (the same active-version guard
    a Connect mutation obeys: a PATCH on an active version returns
    ``INVALID_ID_FIELD: LatestVersionSnapshotId not found``).

    ``engine`` is a ``_lifecycle.LifecycleEngine`` (duck-typed: uses ``.t``,
    ``.log``, ``.dry_run``, ``.run_mutation``). Returns ``{"esdvId", "changed",
    "planned"}``; ``changed``/``planned`` are the sorted step names whose label was
    (or, in dry-run, would be) written. A name in ``name_to_label`` that matches no
    step is a silent no-op — safe for auto-restore, where a captured/overlay label
    may reference a step the Connect mutation removed.
    """
    transport = engine.t
    # Resolve by the stable (es_def_id, VersionNumber) pair. Fall back to the
    # version ApiName only if the caller couldn't supply a VersionNumber (older
    # callers) — resolve_esdv still accepts version_api_name for that case.
    esdv = resolve_esdv(
        transport, es_def_id=es_def_id, version_number=esv.get("VersionNumber"),
        version_api_name=esv.get("ApiName"),
    )
    esdv_id = esdv["Id"]
    current = step_labels(fetch_metadata(transport, esdv_id))
    planned = {
        n: l for n, l in name_to_label.items()
        if l and n in current and current.get(n) != l
    }
    if not planned:
        return {"esdvId": esdv_id, "changed": [], "planned": []}

    def mutate():
        # Re-read post-deactivation so the PATCH reflects current stored Metadata;
        # re-apply as a guard against drift between pre-flight and the write window.
        metadata = fetch_metadata(transport, esdv_id)
        new_md, changed = apply_labels(metadata, planned, logger=engine.log)
        if not changed:
            engine.log("No label changes to write after re-read; skipping PATCH.")
            return
        patch_metadata(transport, esdv_id, new_md)
        engine.log(
            f"PATCHed Tooling Metadata for {esdv_id} ({len(changed)} label(s))."
        )
        if verify and not engine.dry_run:
            labels = step_labels(fetch_metadata(transport, esdv_id))
            missing = {n: l for n, l in planned.items() if labels.get(n) != l}
            if missing:
                raise ToolingError(
                    f"Relabel verification failed: {len(missing)} label(s) did not "
                    f"persist: {sorted(missing)}."
                )

    engine.run_mutation(
        es_def_id=es_def_id, esv=esv, mutate=mutate,
        activate_after=activate_after, cascade=cascade, verb="Relabel",
        # A relabel is a label-only Tooling Metadata PATCH — it never touches the
        # definition graph, so a failure leaves the stored Metadata byte-identical
        # (only the cosmetic labels are stale). Reactivate even on failure so a
        # cosmetic relabel error can't take a live procedure offline.
        reactivate_on_failure=True,
    )
    return {"esdvId": esdv_id, "changed": sorted(planned), "planned": sorted(planned)}


def restore_labels_after_clobber(
    engine,
    *,
    es_id: str,
    es_def_id: str,
    version_api_name: Optional[str],
    name_to_label: Dict[str, str],
    cascade: bool = True,
    logger=None,
) -> Dict[str, Any]:
    """Re-apply captured/overlay labels after a Connect mutation clobbered them.

    The auto-restore half of label preservation: run AFTER a Connect
    import/overlay has completed and reactivated the version. Re-resolves the
    version's CURRENT state (the Connect PATCH may have reactivated it, so the
    ``esv`` the caller held is stale), then runs the shared :func:`relabel_version`
    to restore labels for every step that still exists under the same name — a
    second deactivate → Tooling PATCH → reactivate cycle.

    **Non-fatal by contract:** the Connect mutation already succeeded, so a restore
    failure must not raise or roll back the applied mutation. It is caught, logged,
    and reported in the result as ``ok: False``/``error`` so the caller can surface
    it at the CLI boundary and the operator can re-run ``relabel_expression_set.py``
    manually. Skips silently when there is nothing to restore. Returns
    ``{"ok", "changed", "error"}``.
    """
    log = logger or engine.log
    if not name_to_label or not version_api_name:
        return {"ok": True, "changed": [], "error": None}
    try:
        rows = engine.t.soql(
            "SELECT Id, ApiName, IsActive, VersionNumber FROM ExpressionSetVersion "
            f"WHERE ExpressionSetId = '{soql_literal(es_id)}' "
            f"AND ApiName = '{soql_literal(version_api_name)}'"
        )
        if not rows:
            log(f"Note: could not restore labels — version '{version_api_name}' "
                f"not found after the mutation.")
            return {"ok": False, "changed": [], "error": "version not found"}
        result = relabel_version(
            engine, es_def_id=es_def_id, esv=rows[0],
            name_to_label=name_to_label, activate_after=True, cascade=cascade,
        )
        if result["changed"]:
            log(f"Restored {len(result['changed'])} step label(s) clobbered by the "
                f"Connect PATCH: {', '.join(result['changed'])}.")
        else:
            log("No step labels needed restoring after the Connect PATCH.")
        return {"ok": True, "changed": result["changed"], "error": None}
    except Exception as exc:  # noqa: BLE001 — restore must never fail the mutation
        log(f"⚠ Connect mutation succeeded but label RESTORE failed ({exc}). The "
            f"procedure stays LIVE (a relabel is non-corrupting, so the version was "
            f"reactivated) — only the readable labels are stale (spaceless names). "
            f"Re-run relabel_expression_set.py --expression-set <name> to restore them.")
        return {"ok": False, "changed": [], "error": str(exc)}
