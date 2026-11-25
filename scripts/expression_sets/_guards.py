#!/usr/bin/env python3
"""Pure version guards shared by the toolkit CLIs and the CCI expression-set tasks.

Stdlib only, no I/O and no CumulusCI import: ``tasks/rlm_expression_set_connect.py``
imports this module, so it must import nothing the toolkit's plain Python lacks.

Two facts drive these guards (todo packs 172 and 175):

* **Which version runs.** An expression set can hold several versions, several of
  them active at once (``ramp264``: v1, v3 and v4 active; v4 ran). The 264 object
  reference for ``ExpressionSetVersion.Rank`` says that when more than one enabled
  version matches and their start/end windows overlap, the version with the
  **highest Rank** is chosen. The rest of :func:`executing_version`'s rule was
  measured live (264, 2026-11-24/25, direct Connect invocations of disposable sets,
  3 of 3 calls each): a numeric Rank beats a null one; among null Ranks the
  **earliest created** version runs (not the lower or higher VersionNumber); equal
  numeric Ranks cannot be set up (a deploy is refused with "Assign a unique rank to
  expression set version …", and activating a version through the sObject API
  needs a Rank: "Enter a valid rank to enable …"), so null Ranks only come from a
  Metadata API deploy.
* **What a replace import can target.** A replace import is one full-graph Connect
  PATCH. It sends the payload's versions and rewrites the first one's ``id`` to the
  version the importer targets (the executing version by :func:`executing_version`,
  else the active, then the highest-numbered one). Measured on 264 on two-version
  sets: payloads carrying both versions failed (2026-11-24: with both named alike,
  on the version-name collision; with the target first and the other version
  renamed in the payload, on a duplicate CalculationProcedureId). A one-version
  payload for the target failed on the version-name collision when another
  version's ``Name`` equalled its label, and succeeded when none did (2026-11-24,
  where the other version's ``Name`` had been changed by an sObject update; and
  2026-11-25, on versions deployed with their own labels, CLI and CCI, the other
  version left untouched). :func:`import_target_refusal` allows only that last
  shape; a two-version payload on versions with their own labels is refused here
  too, and how the platform would answer it is not measured.
* **What an overlay can send.** An overlay PATCH sends every version its GET
  returned, ids kept. Measured on 264 (2026-11-25): it succeeded when every version
  carried its own name and failed on the version-name collision when two carried
  the same one; :func:`version_name_collision_refusal` refuses the latter.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# The ExpressionSetVersion fields executing_version and import_target_refusal read.
# Every caller that resolves the executing version selects these.
VERSION_FIELDS = ("Id, ApiName, Name, VersionNumber, IsActive, Rank, StartDateTime, "
                  "EndDateTime, CreatedDate")

MEASURED = "measured on Release 264, 2026-11-24"


def _parse_datetime(value: Any) -> Optional[datetime]:
    """A Salesforce dateTime (``2020-01-01T08:00:00.000+0000`` or ``…Z``); None when
    empty. Raises ValueError on any other value: guessing a window would pick a
    version silently, so an unreadable date stops the caller instead."""
    if value is None or value == "":
        return None
    if isinstance(value, str):
        text = value.strip().replace("Z", "+0000")
        for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue
    raise ValueError(f"Unrecognized ExpressionSetVersion dateTime {value!r}.")


def in_window(version: Dict[str, Any], now: Optional[datetime] = None) -> bool:
    """Whether ``now`` lies in the version's StartDateTime/EndDateTime window.

    A missing (or unread) bound is open. The object reference says EndDateTime is
    when the version becomes inactive, so ``now == EndDateTime`` is outside. The
    platform matches against the call's effective date; the tooling uses now.
    """
    now = now or datetime.now(timezone.utc)
    start = _parse_datetime(version.get("StartDateTime"))
    end = _parse_datetime(version.get("EndDateTime"))
    return (start is None or start <= now) and (end is None or now < end)


def _has_rank(version: Dict[str, Any]) -> bool:
    return isinstance(version.get("Rank"), (int, float))


_LATEST = datetime.max.replace(tzinfo=timezone.utc)


def _creation_key(version: Dict[str, Any]):
    """Earliest created first: CreatedDate, then Id (Salesforce Ids grow with
    creation), then VersionNumber when neither was read."""
    return (_parse_datetime(version.get("CreatedDate")) or _LATEST,
            version.get("Id") or "", version.get("VersionNumber") or 0)


def running_candidates(versions: List[Dict[str, Any]],
                       now: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """The active versions whose date window covers ``now``."""
    return [v for v in versions if v.get("IsActive") and in_window(v, now)]


def _top_tier(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """The candidates that share the winning Rank: the highest numeric Rank, or every
    null-Rank candidate when none has a number."""
    ranked = [v for v in candidates if _has_rank(v)]
    if not ranked:
        return list(candidates)
    top = max(v["Rank"] for v in ranked)
    return [v for v in ranked if v["Rank"] == top]


def executing_version(versions: List[Dict[str, Any]],
                      now: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
    """The version that runs, among active versions whose window covers ``now``.

    The highest numeric ``Rank`` wins (264 object reference; measured: a Rank of 2
    beats 1 whatever the VersionNumbers, and any number beats a null Rank). Among
    versions with no Rank, the earliest created runs (measured, 264, 2026-11-25:
    VersionNumber 2 created before VersionNumber 1 ran, 3 of 3). Equal numeric
    Ranks are refused by the platform, so how it would choose between them is not
    measured; the same earliest-created rule is applied. Rows read without a
    ``Rank`` field at all (not :data:`VERSION_FIELDS`) fall back to the
    highest-numbered active version. Returns ``None`` when no active version
    covers ``now``.
    """
    candidates = running_candidates(versions, now)
    if not candidates:
        return None
    if not any("Rank" in v for v in candidates):
        return max(candidates, key=lambda v: v.get("VersionNumber") or 0)
    tier = _top_tier(candidates)
    return tier[0] if len(tier) == 1 else min(tier, key=_creation_key)


def rank_order_warning(versions: List[Dict[str, Any]],
                       now: Optional[datetime] = None) -> Optional[str]:
    """A note when several versions could run and the choice is easy to misread:
    Rank and VersionNumber point at different versions, the winner was chosen by
    creation order among null Ranks, or numeric Ranks are equal (a state the
    platform refuses to create); ``None`` otherwise."""
    candidates = running_candidates(versions, now)
    if len(candidates) < 2 or not any("Rank" in v for v in candidates):
        return None
    chosen = executing_version(versions, now)
    by_number = max(candidates, key=lambda v: v.get("VersionNumber") or 0)
    tier = _top_tier(candidates)
    ranks = ", ".join(f"{v.get('ApiName')}={v.get('Rank')}" for v in candidates)
    notes = []
    if len(tier) > 1 and not any(_has_rank(v) for v in tier):
        notes.append(
            f"none of the top candidates has a Rank, so {chosen.get('ApiName')}, the "
            f"earliest created, runs ({MEASURED})"
        )
    elif len(tier) > 1:
        notes.append(
            f"{len(tier)} versions share the top Rank, which the platform refuses to "
            f"create; {chosen.get('ApiName')} (earliest created) is assumed to run, "
            "which is not measured"
        )
    if chosen is not by_number:
        notes.append(
            f"{chosen.get('ApiName')} runs, not {by_number.get('ApiName')}, which has "
            "the highest VersionNumber"
        )
    if not notes:
        return None
    return f"Among the active versions ({ranks}): " + "; ".join(notes) + "."


def target_version_warning(es_id: str, active: List[Dict[str, Any]],
                           running: Optional[Dict[str, Any]],
                           chosen: Dict[str, Any]) -> Optional[str]:
    """What to say about a mutator's default target when it is not obvious, or None.

    One wording for the toolkit and the CCI task: several active versions with one
    running, or active versions none of whose date windows covers now (the target is
    then the active, highest-numbered version, which is not running;
    ``set_step_formula.py`` refuses that case and asks for a version name).
    """
    if active and running is None:
        return (
            f"ExpressionSet {es_id} has {len(active)} active version(s) but none has a "
            f"date window covering now, so none is running; operating on "
            f"{chosen.get('ApiName')} (active, highest-numbered), which is not the "
            "executing version."
        )
    if len(active) > 1:
        return (
            f"ExpressionSet {es_id} has {len(active)} active versions; operating on "
            f"{chosen.get('ApiName')}, the executing one (highest Rank among active "
            "versions in their date window; earliest created among null Ranks)."
        )
    return None


_NO_RANK_CAUSE = (
    ": the platform refuses to activate a version through the API without a Rank "
    "(\"Enter a valid rank to enable …\", measured on Release 264, 2026-11-25). "
    "Nothing was written."
)
# The run-without-activation remedy, in each surface's own option name.
NO_ACTIVATION_CLI = "run with --no-activate, which leaves the version inactive"
NO_ACTIVATION_CCI_APPLY = ("run with -o activate_after_apply false, which leaves the "
                           "version inactive")
NO_ACTIVATION_CCI_IMPORT = ("run with -o activate_after_import false, which leaves the "
                            "version inactive")


def _activate_cmd(esv: Dict[str, Any], flag: str) -> str:
    return ("python scripts/expression_sets/activate_expression_set.py --target-org "
            "<alias> --expression-set <name> --version "
            f"{esv.get('ApiName') or '<ApiName>'} {flag} --confirm")


def _rank_remedy(esv: Dict[str, Any], alternative: Optional[str]) -> str:
    # Measured on Release 264 (2026-11-25): an sObject update of Rank works on an
    # inactive version; on an active one it is refused ("An enabled Expression Set
    # Version cannot be updated/deleted."), as is a Metadata API redeploy, so an
    # active version is deactivated, ranked and activated again.
    update = ("sf data update record --target-org <alias> --sobject ExpressionSetVersion "
              f"--record-id {esv.get('Id')} --values \"Rank=<n>\"")
    if esv.get("IsActive"):
        how = (" Give it a Rank first. No update of an active version is accepted "
               "(\"An enabled Expression Set Version cannot be updated/deleted.\", "
               "measured), so: deactivate it (" + _activate_cmd(esv, "--deactivate")
               + "; it does not run while off), set a Rank that keeps the intended "
               f"version executing ({update}), and activate it again ("
               + _activate_cmd(esv, "--activate") + "); each step was measured")
    else:
        how = (" Give it a Rank first, one that keeps the intended version executing "
               f"({update}; measured on an inactive version)")
    return how + (f"; or {alternative}." if alternative else ".")


def null_rank_reactivation_refusal(
    esv: Dict[str, Any], activate_after: bool, alternative: Optional[str] = None
) -> Optional[str]:
    """Why a run that would activate ``esv`` must not start, or None.

    ``alternative`` is the other remedy offered besides giving the version a Rank,
    in the caller's own option name (``NO_ACTIVATION_*``); None when the caller has
    no way to run without activation or its only purpose is to activate.

    Activating a version through the API needs a Rank: the platform refused it on
    264 with "Enter a valid rank to enable …" (measured 2026-11-25). A run that
    would end by activating a version whose Rank is null (possible only after a
    Metadata API deploy) fails at that point, after its change was written: an
    active version is left off; an inactive one is changed but not activated.
    Refused before any write whenever the run would activate (``activate_after``).
    A row read without a ``Rank`` field is not judged.
    """
    if not (activate_after and "Rank" in esv and esv.get("Rank") is None):
        return None
    name = esv.get("ApiName") or esv.get("Id")
    if esv.get("IsActive"):
        what = (f"ExpressionSetVersion {name} is active with no Rank, so this run would "
                "deactivate it and could not turn it back on")
    else:
        what = (f"ExpressionSetVersion {name} has no Rank, so this run would write its "
                "change and then fail to activate it")
    return what + _NO_RANK_CAUSE + _rank_remedy(esv, alternative)


def null_rank_delete_refusal(esv: Dict[str, Any]) -> Optional[str]:
    """Why a whole-set delete must not start on ``esv``, or None.

    A failed DELETE is rolled back by reactivating the version it deactivated, which
    the platform refuses without a Rank (see ``null_rank_reactivation_refusal``).
    """
    if not (esv.get("IsActive") and "Rank" in esv and esv.get("Rank") is None):
        return None
    name = esv.get("ApiName") or esv.get("Id")
    return (
        f"Delete refused: ExpressionSetVersion {name} is active with no Rank, so if the "
        "DELETE failed its rollback could not turn the version back on" + _NO_RANK_CAUSE
        + _rank_remedy(esv, "deactivate it first (" + _activate_cmd(esv, "--deactivate")
                       + ") and then delete the set")
    )


def version_rows(versions: List[Dict[str, Any]]) -> str:
    """``"ApiName (vN, rank R, active), ..."``, lowest number first, for messages."""
    return ", ".join(
        f"{v.get('ApiName')} (v{v.get('VersionNumber')}"
        f"{', rank ' + str(v.get('Rank')) if v.get('Rank') is not None else ''}"
        f"{', active' if v.get('IsActive') else ''})"
        for v in sorted(versions, key=lambda r: r.get("VersionNumber") or 0)
    )


def import_target_refusal(
    api_name: str,
    versions: List[Dict[str, Any]],
    target: Dict[str, Any],
    payload: Dict[str, Any],
) -> Optional[str]:
    """Why a replace import must not PATCH ``target``, or ``None`` to proceed.

    ``versions`` are the org's ``ExpressionSetVersion`` rows for the set (with
    ``Name``, the version label), ``target`` the version the importer resolved and
    will rewrite the payload's version id to, and ``payload`` the definition being
    imported. A set with one version is never refused here (the importers keep
    their single-version handling). On a set with several versions the import
    proceeds only when all three hold, the one shape that succeeded live
    (:data:`MEASURED`):

    1. the payload carries exactly one version;
    2. that version's ``apiName`` is the target's ``ApiName``;
    3. no other existing version shares its label (``name``; the target's ``Name``
       when the payload has none), compared ignoring case and spacing (the
       platform's comparison is not measured, so this errs towards refusing); with
       no label to compare at all, the import is refused.

    Anything else is refused, naming the condition that failed. The caller refuses
    before any write.
    """
    if len(versions) <= 1:
        return None
    rows = version_rows(versions)
    alternatives = (
        "Nothing was written. To change a step formula, use "
        "scripts/expression_sets/set_step_formula.py, which edits one version (the "
        "executing one by default, or --version-api-name). To replace the whole "
        "graph, import it as a new expression set (change the top-level apiName and "
        "name and the version apiName)."
    )
    prefix = f"Expression set '{api_name}' has {len(versions)} versions: {rows}. "
    payload_versions = payload.get("versions")
    payload_versions = payload_versions if isinstance(payload_versions, list) else []
    if len(payload_versions) != 1:
        return (
            prefix + f"The payload carries {len(payload_versions)} versions; the "
            "importer rewrites the first payload version's id to the target, so on a "
            "multi-version set only a one-version payload for the targeted version "
            f"imports (two-version import payloads failed, {MEASURED}; on versions "
            "with their own labels this guard refuses them, and the platform's response "
            "is not measured). An overlay "
            "(apply_expression_set_overlay.py) sends every version under its own id, "
            "which succeeded when each version carried its own label (measured on "
            "Release 264, 2026-11-25). " + alternatives
        )
    incoming = payload_versions[0] if isinstance(payload_versions[0], dict) else {}
    incoming_api = incoming.get("apiName")
    if incoming_api != target.get("ApiName"):
        return (
            prefix + f"The payload's version is {incoming_api or '(no apiName)'}, but "
            f"the import would replace {target.get('ApiName')} "
            f"(v{target.get('VersionNumber')}), rebinding one version's content onto "
            "a different existing version (rejected on a version-name collision after "
            "partially applying, ramp264). " + alternatives
        )
    label = incoming.get("name") or target.get("Name")
    if not label:
        return (
            prefix + "Neither the payload's version nor the org row carries a label "
            "(name / Name), so the import cannot confirm that no other version shares "
            f"it ({MEASURED}: a shared label is rejected). Set versions[0].name. "
            + alternatives
        )

    sharing = [v.get("ApiName") for v in versions
               if v.get("ApiName") != target.get("ApiName")
               and _norm_label(v.get("Name")) == _norm_label(label)]
    if sharing:
        return (
            prefix + f"Other version(s) {', '.join(sharing)} share the label "
            f"'{label}', so the PATCH is rejected on a version-name collision even for "
            f"a one-version payload aimed at the target ({MEASURED}). " + alternatives
        )
    return None


def _norm_label(text: Any) -> str:
    # Whether the platform's name check ignores case or spacing is not measured;
    # comparing loosely refuses more, never less.
    return " ".join(str(text or "").split()).casefold()


def other_active_versions_refusal(
    api_name: str,
    versions: List[Dict[str, Any]],
    target: Dict[str, Any],
) -> Optional[str]:
    """Why an overlay PATCH, which sends every version, must not run, or ``None``.

    The lifecycle deactivates only ``target`` (the version it cycles) before the
    full-graph PATCH, so any other active version would be sent while active.
    Whether the platform accepts that is not measured, and a PATCH that fails part
    way leaves ``target`` and its procedure plans off. So the overlay is refused,
    before any write, while any version other than ``target`` is active.
    ``versions`` are the org's ``ExpressionSetVersion`` rows.
    """
    others = [v for v in versions
              if v.get("IsActive") and v.get("ApiName") != target.get("ApiName")]
    if not others:
        return None
    # --no-cascade: a deactivation cascade turns off every procedure plan that
    # references the set, and the executing version stays active, so its plans
    # must stay on.
    deactivate = "; ".join(
        _activate_cmd(v, "--deactivate --no-cascade").replace("<name>", api_name)
        for v in others)
    return (
        f"Expression set '{api_name}' has {len(versions)} versions: "
        f"{version_rows(versions)}. The overlay PATCH sends every version, but the "
        f"run deactivates only {target.get('ApiName')}, so it would rewrite "
        f"{', '.join(v.get('ApiName') for v in others)} while active (not measured; a "
        f"PATCH that failed part way would leave {target.get('ApiName')} and its "
        "procedure plans off). Nothing was written. Deactivate the other active "
        f"version(s) first ({deactivate}; a version that does not run changes no "
        "price), or change one step formula with "
        "scripts/expression_sets/set_step_formula.py, which edits only that version."
    )


def version_name_collision_refusal(
    api_name: str,
    versions: List[Dict[str, Any]],
    payload: Dict[str, Any],
) -> Optional[str]:
    """Why a full-graph PATCH that sends every version must not run, or ``None``.

    The overlay sends every version its GET returned. Measured on Release 264
    (2026-11-25, a two-version set, active and draft): the PATCH succeeded when
    each version carried its own name; it was rejected ("An expression set version
    with the name … exists in this expression set") when two versions carried the
    same name, both when the org rows' ``Name`` was shared and when it had been made
    distinct by an sObject update, which does not change the name the Connect GET
    returns. A one-version payload whose name another version's ``Name`` held was
    rejected the same way. So, on a set with several versions, the PATCH is refused
    when a payload version has no name, shares its name with another payload
    version, or carries the ``Name`` of a different org version (compared ignoring
    case and spacing). ``versions`` are the org's ``ExpressionSetVersion`` rows.
    The caller refuses before any write.
    """
    sent = [v for v in (payload.get("versions") or []) if isinstance(v, dict)]
    if len(versions) <= 1 and len(sent) <= 1:
        return None
    problems: List[str] = []
    seen: Dict[str, str] = {}
    for version in sent:
        api, label = version.get("apiName"), version.get("name")
        key = _norm_label(label)
        if not key:
            problems.append(f"{api} has no name in the payload")
            continue
        if key in seen:
            problems.append(f"{seen[key]} and {api} both carry the name '{label}'")
        else:
            seen[key] = api
        holders = [r.get("ApiName") for r in versions
                   if r.get("ApiName") != api and _norm_label(r.get("Name")) == key]
        if holders:
            problems.append(f"{api} carries the name '{label}', which "
                            f"{', '.join(holders)} holds")
    if not problems:
        return None
    return (
        f"Expression set '{api_name}' has {len(versions)} versions: "
        f"{version_rows(versions)}. The PATCH sends every version, and the platform "
        "rejects it when a version's name is not unique in the set (\"An expression "
        "set version with the name … exists in this expression set\", measured on "
        f"Release 264, 2026-11-25): {'; '.join(problems)}. Nothing was written. "
        "Versions deployed with their own <label> got distinct names (measured), but "
        "an sObject update of ExpressionSetVersion.Name did not change the name the "
        "GET returns (measured) and a deploy over an active version is refused, so on "
        "an existing set change one version's step formula with "
        "scripts/expression_sets/set_step_formula.py, which edits only that version."
    )
