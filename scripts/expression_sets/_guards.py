#!/usr/bin/env python3
"""Pure version guards shared by the toolkit CLIs and the CCI expression-set tasks.

Stdlib only, no I/O and no CumulusCI import: ``tasks/rlm_expression_set_connect.py``
imports this module, and ``tests/test_expression_set_schema.py`` must keep running
under base Python.

Two facts drive these guards (todo packs 172 and 175):

* **Which version runs.** An expression set can hold several versions, several of
  them active at once (``ramp264``: v1, v3 and v4 active; v4 ran). The 264 object
  reference for ``ExpressionSetVersion.Rank`` says that when more than one enabled
  version matches and their start/end windows overlap, the version with the
  **highest Rank** is chosen. :func:`executing_version` applies that rule; its
  tie-break and null-Rank handling are not documented (see the function).
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

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# The ExpressionSetVersion fields executing_version reads. Every caller that resolves
# the executing version selects these.
VERSION_FIELDS = "Id, ApiName, VersionNumber, IsActive, Rank, StartDateTime, EndDateTime"


def _parse_datetime(value: Any) -> Optional[datetime]:
    """A Salesforce dateTime (``2020-01-01T08:00:00.000+0000`` or ``…Z``), or None."""
    if not value or not isinstance(value, str):
        return None
    text = value.strip().replace("Z", "+0000")
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def in_window(version: Dict[str, Any], now: Optional[datetime] = None) -> bool:
    """Whether ``now`` lies in the version's StartDateTime/EndDateTime window.

    A missing (or unread) bound is open. Whether the platform treats the end as
    inclusive is not documented; this treats ``now == EndDateTime`` as inside.
    """
    now = now or datetime.now(timezone.utc)
    start = _parse_datetime(version.get("StartDateTime"))
    end = _parse_datetime(version.get("EndDateTime"))
    return (start is None or start <= now) and (end is None or now <= end)


def _rank_key(version: Dict[str, Any]):
    # UNVERIFIED until the live check: the docs say the highest Rank wins among
    # enabled versions whose windows overlap, but say nothing about a null Rank or
    # equal Ranks. Here a null Rank sorts below every numeric Rank, and equal Ranks
    # fall back to the higher VersionNumber.
    rank = version.get("Rank")
    has_rank = isinstance(rank, (int, float))
    return (1 if has_rank else 0, rank if has_rank else 0, version.get("VersionNumber") or 0)


def running_candidates(versions: List[Dict[str, Any]],
                       now: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """The active versions whose date window covers ``now``."""
    return [v for v in versions if v.get("IsActive") and in_window(v, now)]


def executing_version(versions: List[Dict[str, Any]],
                      now: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
    """The version that runs: among active versions whose window covers ``now``,
    the highest ``Rank`` (264 object reference, ``ExpressionSetVersion.Rank``).

    The tie-break (higher ``VersionNumber``) and the null-Rank order (below any
    number) are NOT documented and are unverified until a live check. Rows read
    without ``Rank``/``StartDateTime``/``EndDateTime`` (see :data:`VERSION_FIELDS`)
    fall back to the highest-numbered active version. Returns ``None`` when no
    active version covers ``now``.
    """
    candidates = running_candidates(versions, now)
    if not candidates:
        return None
    return max(candidates, key=_rank_key)


def rank_order_warning(versions: List[Dict[str, Any]],
                       now: Optional[datetime] = None) -> Optional[str]:
    """A warning when Rank and VersionNumber disagree about which version runs, or
    when the choice rests on the undocumented tie-break; ``None`` otherwise."""
    candidates = running_candidates(versions, now)
    if len(candidates) < 2:
        return None
    by_rank = max(candidates, key=_rank_key)
    by_number = max(candidates, key=lambda v: v.get("VersionNumber") or 0)
    ranks = [v.get("Rank") for v in candidates]
    top = _rank_key(by_rank)[:2]
    tied = sum(1 for v in candidates if _rank_key(v)[:2] == top) > 1
    if by_rank is not by_number:
        return (
            f"Rank and VersionNumber disagree among the {len(candidates)} active "
            f"versions: {by_rank.get('ApiName')} has the highest Rank "
            f"({by_rank.get('Rank')}) and is taken as the executing version, while "
            f"{by_number.get('ApiName')} has the highest VersionNumber. Confirm which "
            "one runs with a constant-control formula before relying on either."
        )
    if tied or any(r is None for r in ranks):
        return (
            f"{len(candidates)} active versions share the top Rank or have no Rank "
            f"({', '.join(str(r) for r in ranks)}); {by_rank.get('ApiName')} is taken "
            "as the executing version by the higher VersionNumber, a tie-break the "
            "platform does not document. Confirm with a constant-control formula."
        )
    return None


def version_rows(versions: List[Dict[str, Any]]) -> str:
    """``"ApiName (vN, rank R, active), ..."``, lowest number first, for messages."""
    return ", ".join(
        f"{v.get('ApiName')} (v{v.get('VersionNumber')}"
        f"{', rank ' + str(v.get('Rank')) if v.get('Rank') is not None else ''}"
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
        runs = (
            f"Only {running.get('ApiName')} executes (the highest Rank among the "
            "active versions whose date window covers now)"
            if running else "None of them has a date window covering now"
        )
        return (
            f"Expression set '{api_name}' has {len(active)} active versions: {rows}. "
            f"{runs}, and a whole-set import cannot tell which version it should "
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
