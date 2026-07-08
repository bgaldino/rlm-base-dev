#!/usr/bin/env python3
"""Pure overlay-transformation logic for BRE Expression Sets.

Part of the self-contained ``scripts/expression_sets/`` toolkit (imports nothing
from ``tasks/``). Transport-agnostic, dependency-free: the declarative
step/variable merge that turns an overlay (``addSteps`` / ``removeSteps`` /
``updateSteps`` / ``reorderSteps`` / ``addVariables`` / ``removeVariables``) into
a modified definition. It mirrors the merge rules the CCI task
(``tasks/rlm_expression_set_connect.py``, reference-only) applies, so the
``apply_expression_set_overlay`` CLI produces the same result the task would —
without sharing code with it.

The single load-bearing rule these functions encode: a step's execution order
is its ``sequenceNumber`` (scoped per parent — children restart at 1), NEVER the
array order. The Connect GET serializes top-level steps alphabetically by name;
placement math must operate on ``sequenceNumber`` alone.

Errors: pure functions raise the class passed as ``error_cls`` (default
:class:`OverlayError`); the CLIs pass their own transport-free error class.

Logging: functions take a ``logger`` (a ``logging.Logger``-style object with
``.info``/``.warning``); the default module logger stays silent unless the host
configures handlers.
"""

import logging
from copy import deepcopy
from typing import List, Optional

_LOGGER = logging.getLogger("expression_sets.overlay")
_LOGGER.addHandler(logging.NullHandler())


class OverlayError(Exception):
    """Raised on a structurally invalid overlay/definition merge.

    The default error class for these pure functions; the CLIs pass their own
    ``error_cls`` (a transport-free toolkit error) so failures surface with the
    package's error type.
    """


# Overlay-only metadata that must NOT be forwarded to the Connect payload.
# ``placement`` directs :func:`add_steps` to compute sequenceNumber and never
# goes to the API. ``label`` is the readable step label — Connect has NO label
# field and rejects it (``JSON_PARSER_ERROR: Unrecognized field "label"``), so an
# overlay carries it here purely for the post-PATCH Tooling relabel to consume
# (see :func:`overlay_labels`), and it is stripped before the Connect send. Add
# new overlay-local keys here as the schema evolves.
OVERLAY_ONLY_STEP_KEYS = frozenset({"placement", "label"})

# Sensible defaults filled in for the small set of required-by-engine flags when
# an overlay omits them (the validator gates the rest of the step shape).
_STEP_DEFAULTS = {
    "description": "",
    "sequenceNumber": 1,
    "stepType": "BusinessKnowledgeModel",
    "resultIncluded": False,
    "shouldExposeExecPathMsgOnly": True,
    "shouldExposeConditionDetails": False,
    "shouldShowExplExternally": False,
}


def _log(logger, level, *args):
    (logger or _LOGGER).__getattribute__(level)(*args)


def overlay_labels(overlay: dict) -> dict:
    """Harvest the ``{step name: label}`` map an overlay carries, if any.

    An overlay can ship readable labels for the steps it adds/updates two ways
    (a per-step ``label`` wins over the top-level map on a name collision):

      * a top-level ``"labels": {"StepName": "Readable Label"}`` block (canonical,
        same shape as ``relabel_expression_set.py --labels-file``), and/or
      * a ``"label"`` field on an individual ``addSteps`` entry (self-describing —
        travels with a sliced step; stripped from the Connect send by
        :data:`OVERLAY_ONLY_STEP_KEYS`).

    Connect has no label field, so these never reach the Connect PATCH; the
    mutator feeds this map to the post-PATCH Tooling relabel so a newly-added step
    lands with its readable label. Only string labels are kept. Pure.
    """
    out: dict = {}
    top = overlay.get("labels")
    if isinstance(top, dict):
        out.update({k: v for k, v in top.items() if isinstance(v, str)})
    for step in overlay.get("addSteps", []) or []:
        if isinstance(step, dict) and isinstance(step.get("label"), str) and step.get("name"):
            out[step["name"]] = step["label"]
    return out


# ----------------------------------------------------------------------
# Version / step selection
# ----------------------------------------------------------------------


def find_version(
    versions: list, version_api_name: Optional[str], *, error_cls=OverlayError
) -> dict:
    """Return the target version block (by apiName, else the first version)."""
    if version_api_name:
        for v in versions:
            if v.get("apiName") == version_api_name:
                return v
        raise error_cls(f"Version '{version_api_name}' not found in definition.")
    return versions[0]


def find_step_sequence(steps: list, name: str, *, error_cls=OverlayError) -> int:
    """Return a top-level step's sequenceNumber (raises if absent)."""
    for s in steps:
        if s.get("name") == name and s.get("parentStep") is None:
            return s.get("sequenceNumber", 0)
    raise error_cls(f"Placement target step '{name}' not found in definition.")


def renumber_top_level_steps(steps: list) -> list:
    """Renumber top-level steps 1..N by their current sequenceNumber order.

    Children (parentStep set) are left untouched — they are scoped per parent.
    """
    top_level = [s for s in steps if s.get("parentStep") is None]
    top_level.sort(key=lambda s: s.get("sequenceNumber", 0))
    for i, s in enumerate(top_level, start=1):
        s["sequenceNumber"] = i
    return steps


def build_step(step_def: dict, *, error_cls=OverlayError) -> dict:
    """Build a Connect step payload from an overlay ``addSteps`` entry.

    Passes through every field the overlay author wrote (minus overlay-only
    metadata like ``placement``) so a future step field survives apply, then
    fills the small set of required-by-engine defaults the overlay omits.
    """
    step = {k: v for k, v in step_def.items() if k not in OVERLAY_ONLY_STEP_KEYS}
    if "name" not in step:
        # The validator requires name; defensive — never reached after validation.
        raise error_cls("addSteps entry is missing 'name'.")
    for key, value in _STEP_DEFAULTS.items():
        step.setdefault(key, value)
    return step


# ----------------------------------------------------------------------
# Step operations
# ----------------------------------------------------------------------


def remove_steps(steps: list, to_remove: list, *, logger=None) -> list:
    names_to_remove = {s["name"] for s in to_remove}
    present = {s.get("name") for s in steps}
    steps = [s for s in steps if s.get("name") not in names_to_remove]
    # Log per name against that name's actual presence — not a batch-wide count,
    # which would mislabel every name once any one was removed.
    for name in names_to_remove:
        if name in present:
            _log(logger, "info", "Removed step '%s'.", name)
        else:
            _log(logger, "warning", "Step '%s' not found for removal.", name)
    return renumber_top_level_steps(steps)


def add_steps(steps: list, to_add: list, *, logger=None, error_cls=OverlayError) -> list:
    for step_def in to_add:
        existing = next(
            (s for s in steps if s.get("name") == step_def["name"]), None
        )
        if existing:
            _log(logger, "info", "Step '%s' already exists, skipping add.", step_def["name"])
            continue

        # Read placement WITHOUT mutating the caller's overlay dict: the
        # verification pass reads placement back off the same overlay, so
        # popping it here would silently disable the placement check.
        placement = step_def.get("placement")
        new_step = build_step(step_def, error_cls=error_cls)

        # Child steps (parentStep set) are ordered by their own sequenceNumber
        # scoped WITHIN the parent (children restart at 1). They take no
        # top-level placement and must not trigger the top-level renumber/bump
        # logic below, which would overwrite their per-parent sequenceNumber.
        if step_def.get("parentStep"):
            steps.append(new_step)
            _log(
                logger, "info",
                "Added child step '%s' (parent '%s') at sequence %s.",
                new_step["name"], step_def["parentStep"], new_step["sequenceNumber"],
            )
            continue

        if placement and placement.get("afterStep"):
            target_name = placement["afterStep"]
            target_seq = find_step_sequence(steps, target_name, error_cls=error_cls)
            new_step["sequenceNumber"] = target_seq + 1
            for s in steps:
                if (
                    s.get("parentStep") is None
                    and s.get("sequenceNumber", 0) > target_seq
                ):
                    s["sequenceNumber"] = s["sequenceNumber"] + 1
        elif placement and placement.get("beforeStep"):
            target_name = placement["beforeStep"]
            target_seq = find_step_sequence(steps, target_name, error_cls=error_cls)
            new_step["sequenceNumber"] = target_seq
            for s in steps:
                if (
                    s.get("parentStep") is None
                    and s.get("sequenceNumber", 0) >= target_seq
                ):
                    s["sequenceNumber"] = s["sequenceNumber"] + 1
        elif placement and placement.get("sequenceNumber") is not None:
            seq = placement["sequenceNumber"]
            new_step["sequenceNumber"] = seq
            for s in steps:
                if (
                    s.get("parentStep") is None
                    and s.get("sequenceNumber", 0) >= seq
                ):
                    s["sequenceNumber"] = s["sequenceNumber"] + 1
        else:
            max_seq = max(
                (
                    s.get("sequenceNumber", 0)
                    for s in steps
                    if s.get("parentStep") is None
                ),
                default=0,
            )
            new_step["sequenceNumber"] = max_seq + 1

        steps.append(new_step)
        _log(
            logger, "info",
            "Added step '%s' at sequence %s.", new_step["name"], new_step["sequenceNumber"],
        )
    return steps


def update_steps(steps: list, to_update: list, *, logger=None, error_cls=OverlayError) -> list:
    for update_def in to_update:
        name = update_def["name"]
        target = next((s for s in steps if s.get("name") == name), None)
        if not target:
            # Raise rather than warn-and-continue: a missing target means the
            # edit silently does nothing, yet the PATCH still succeeds and is
            # reported as success. Fail loudly so a typo'd name is caught.
            raise error_cls(f"updateSteps target '{name}' not found in the definition.")
        for key, value in update_def.items():
            if key == "name":
                continue
            target[key] = value
        _log(logger, "info", "Updated step '%s'.", name)
    return steps


def reorder_steps(steps: list, reorder_defs: list, *, logger=None, error_cls=OverlayError) -> list:
    for reorder in reorder_defs:
        name = reorder["name"]
        target = next((s for s in steps if s.get("name") == name), None)
        if not target:
            raise error_cls(f"reorderSteps target '{name}' not found in the definition.")
        target["sequenceNumber"] = reorder["sequenceNumber"]
        _log(logger, "info", "Reordered step '%s' to sequence %s.", name, reorder["sequenceNumber"])
    return steps


# ----------------------------------------------------------------------
# Variable operations
# ----------------------------------------------------------------------


def add_variables(variables: list, to_add: list, *, logger=None) -> list:
    existing_names = {v.get("name") for v in variables}
    for var_def in to_add:
        name = var_def["name"]
        if name in existing_names:
            # Covers both names already on the live definition AND names we've
            # just appended from an earlier addVariables entry — so an overlay
            # with two entries for the same name skips the second instead of
            # appending a duplicate the Connect API would reject after the
            # version was already deactivated.
            _log(logger, "info", "Variable '%s' already exists, skipping.", name)
            continue
        variables.append(var_def)
        existing_names.add(name)
        _log(logger, "info", "Added variable '%s'.", name)
    return variables


def remove_variables(variables: list, to_remove: list, *, logger=None) -> list:
    # Accept either bare strings or {"name": "..."} entries — variables have no
    # other field to address, so a list of names is the natural shape.
    names = set()
    for entry in to_remove:
        if isinstance(entry, str):
            names.add(entry)
        elif isinstance(entry, dict) and entry.get("name"):
            names.add(entry["name"])
    original_count = len(variables)
    variables = [v for v in variables if v.get("name") not in names]
    removed = original_count - len(variables)
    if removed:
        _log(logger, "info", "Removed %d variable(s).", removed)
    return variables


# ----------------------------------------------------------------------
# Top-level overlay application
# ----------------------------------------------------------------------


def apply_overlay(
    definition: dict,
    overlay: dict,
    *,
    version_api_name: Optional[str] = None,
    logger=None,
    error_cls=OverlayError,
) -> dict:
    """Apply overlay transformations to a definition. Returns a modified copy.

    ``version_api_name`` selects the version to mutate (default: the first). The
    order of operations mirrors the CCI task exactly: removeSteps → addSteps →
    updateSteps → reorderSteps, then removeVariables → addVariables.
    """
    result = deepcopy(definition)
    versions = result.get("versions", [])
    if not versions:
        raise error_cls("Expression set has no versions to modify.")

    version = find_version(versions, version_api_name, error_cls=error_cls)
    steps = version.get("steps", [])
    variables = version.get("variables", [])

    if overlay.get("removeSteps"):
        steps = remove_steps(steps, overlay["removeSteps"], logger=logger)
    if overlay.get("addSteps"):
        steps = add_steps(steps, overlay["addSteps"], logger=logger, error_cls=error_cls)
    if overlay.get("updateSteps"):
        steps = update_steps(steps, overlay["updateSteps"], logger=logger, error_cls=error_cls)
    if overlay.get("reorderSteps"):
        steps = reorder_steps(steps, overlay["reorderSteps"], logger=logger, error_cls=error_cls)

    if overlay.get("removeVariables"):
        variables = remove_variables(variables, overlay["removeVariables"], logger=logger)
    if overlay.get("addVariables"):
        variables = add_variables(variables, overlay["addVariables"], logger=logger)

    version["steps"] = steps
    version["variables"] = variables
    return result
