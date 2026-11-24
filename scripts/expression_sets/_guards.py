#!/usr/bin/env python3
"""Pure version guards shared by the toolkit CLIs and the CCI expression-set tasks.

Stdlib only, no I/O and no CumulusCI import: ``tasks/rlm_expression_set_connect.py``
imports this module, and ``tests/test_expression_set_schema.py`` must keep running
under base Python.

Two facts drive these guards (todo packs 172 and 175):

* **Which version runs.** An expression set can hold several versions, several of
  them active at once (``ramp264``: v1, v3 and v4 active). The runtime executes the
  highest-numbered ACTIVE one (:func:`executing_version`).
* **What a replace import can target.** A replace import is one full-graph Connect
  PATCH. It sends the payload's first version and rewrites that version's ``id`` to
  the org version the importer resolved (active first, then highest-numbered).
  When the payload's version is a different version from that target, the PATCH
  rebinds one version's content onto another existing version. On ``ramp264`` the
  payload carried ``RLM_DefaultPricingProcedure_V1`` while the importer targeted the
  executing ``..._Partner_Price_and_Ramp_v40``: the platform rejected the PATCH on a
  version-name collision with the real ``_V1``, after writing a formula into
  ``versions[0]``. A full-graph PATCH on a set with one active version and one
  inactive draft, aimed at the version it names, succeeded live on 264 (the overlay
  path, commit 68dccf7bd). :func:`import_target_refusal` refuses the first shape
  and allows the second.
"""

from typing import Any, Dict, List, Optional


def executing_version(versions: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """The version that runs: the highest-numbered ACTIVE ``ExpressionSetVersion``.

    Returns ``None`` when no version is active.
    """
    active = [v for v in versions if v.get("IsActive")]
    if not active:
        return None
    return max(active, key=lambda v: v.get("VersionNumber") or 0)


def version_rows(versions: List[Dict[str, Any]]) -> str:
    """``"ApiName (vN, active), ..."``, lowest number first, for messages."""
    return ", ".join(
        f"{v.get('ApiName')} (v{v.get('VersionNumber')}"
        f"{', active' if v.get('IsActive') else ''})"
        for v in sorted(versions, key=lambda r: r.get("VersionNumber") or 0)
    )


def _payload_version_api_name(payload: Dict[str, Any]) -> Optional[str]:
    versions = payload.get("versions")
    if isinstance(versions, list) and versions and isinstance(versions[0], dict):
        return versions[0].get("apiName")
    return None


def import_target_refusal(
    api_name: str,
    versions: List[Dict[str, Any]],
    target: Dict[str, Any],
    payload: Dict[str, Any],
) -> Optional[str]:
    """Why a replace import must not PATCH ``target``, or ``None`` to proceed.

    ``versions`` are the org's ``ExpressionSetVersion`` rows for the set, ``target``
    the one the importer resolved and will rewrite the payload's version id to, and
    ``payload`` the definition being imported. A set with one version is never
    refused here (the importers keep their existing single-version handling). On a
    set with several versions the import is refused when:

    1. more than one version is active, so which version the import should replace
       is ambiguous and the one that executes may not be the one the payload
       describes (the ``ramp264`` shape); or
    2. the payload's version ``apiName`` is missing or differs from ``target``'s
       ``ApiName``, so the PATCH would rebind the payload's version onto a different
       existing version (also the ``ramp264`` failure).

    A set with at most one active version, imported with a payload whose version is
    the target, proceeds. The caller refuses before any write.
    """
    if len(versions) <= 1:
        return None
    rows = version_rows(versions)
    running = executing_version(versions)
    alternatives = (
        "Nothing was written. To change a step formula, use "
        "scripts/expression_sets/set_step_formula.py, which edits one version (the "
        "executing one by default, or --version-api-name). To change an inactive "
        "draft, apply an overlay aimed at it (apply_expression_set_overlay --version, "
        "or the CCI task's -o version_api_name). To replace the whole "
        "graph, import it as a new expression set (change the top-level apiName and "
        "name and the version apiName)."
    )
    active = [v for v in versions if v.get("IsActive")]
    if len(active) > 1:
        return (
            f"Expression set '{api_name}' has {len(active)} active versions: {rows}. "
            f"Only {running.get('ApiName')} executes (the highest-numbered active "
            "version), and a whole-set import cannot tell which version it should "
            "replace: on a version chain like this the platform rejected the PATCH on "
            "a version-name collision after partially applying. " + alternatives
        )
    incoming = _payload_version_api_name(payload)
    if not incoming:
        return (
            f"Expression set '{api_name}' has {len(versions)} versions: {rows}, and the "
            "payload's version has no apiName, so the import cannot confirm it replaces "
            f"{target.get('ApiName')}. Set versions[0].apiName to the version to "
            "replace. " + alternatives
        )
    if incoming != target.get("ApiName"):
        return (
            f"Expression set '{api_name}' has {len(versions)} versions: {rows}. The "
            f"payload's version is {incoming}, but the import would replace "
            f"{target.get('ApiName')} (v{target.get('VersionNumber')}), rebinding one "
            "version's content onto a different existing version; the platform "
            "rejected that on a version-name collision after partially applying. "
            + alternatives
        )
    return None
