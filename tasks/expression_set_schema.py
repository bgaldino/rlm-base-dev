"""
Schema validation for BRE Expression Set definitions and overlays.

Dependency-free, pure-function validation used as a pre-flight by the
Expression Set Connect API tasks (``tasks/rlm_expression_set_connect.py``) and
exposed standalone via ``scripts/ai/validate_expression_set.py``. Catches
malformed payloads *before* they reach the org, where the Connect PATCH/POST
handler can swallow real errors into opaque gacks.

Two entry points:
  * ``validate_definition(defn)``  — a full ExpressionSet definition (the shape
    produced by ``export_expression_set`` and consumed by ``import``).
  * ``validate_overlay(overlay)``  — a declarative overlay
    (``addSteps``/``removeSteps``/``updateSteps``/``reorderSteps``/
    ``addVariables``/``removeVariables``) consumed by
    ``apply_expression_set_overlay``.

The enums and field sets below were captured from a live v67.0 export of
``RLM_Price_Distribution_Procedure`` plus POST/Tooling validation messages — see
``docs/references/expression-set-connect-api-reference.md`` for provenance.

No CumulusCI or org imports here on purpose: this module is unit-testable and
reusable from a plain ``python`` invocation.
"""
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


# ----------------------------------------------------------------------
# Verified schema constants (v67.0 / Release 262)
#
# Enums below are sourced from the generated Connect API OpenAPI spec (the
# closest published spec to v67.0) and cross-checked against live GET exports
# of RLM_DefaultPricingProcedure (92 steps) and RLM_Price_Distribution_Procedure
# (11 steps). The GET output step
# shape matches the INPUT ExpressionSetVersionStepRepresentation exactly
# (flat steps[] with parentStep-by-name; no id/uniqueIdentifier on steps).
# ----------------------------------------------------------------------

# ExpressionSetUsageTypeEnumRepresentation (Revenue Cloud subset documented in
# the expression-sets skill). Unknown values warn (forward-compat) rather than error.
USAGE_TYPES = {
    "DefaultPricing",          # PricingProcedure
    "PricingDiscovery",        # DiscoveryProcedure
    "DefaultRating",           # RatingProcedure
    "RatingDiscovery",         # RatingDiscoveryProcedure
    "ProductQualification",    # QualificationProcedure
    "Constraint",              # Constraint (CML-based, not step graph)
    "Bre",                     # Generic BRE
    "PricingDiscoveryAction",  # Discovery actions
}

# usageTypes under which AssignmentElement steps are permitted.
ASSIGNMENT_USAGE_TYPES = {"DefaultPricing", "PricingDiscovery"}

# ExpsSetStepTypeEnumRepresentation — complete (9 values, OAS-confirmed).
STEP_TYPES = {
    "AdvancedCondition",
    "AdvancedListFilter",
    "Branch",
    "BusinessKnowledgeModel",
    "Condition",
    "DefaultPath",
    "ListFilter",
    "ListGroup",
    "SubExpression",
}

# BusinessKnowledgeModelEnumRepresentation has ~130 values and grows per
# release, so actionType is validated as a WARNING (unknown → warn, not error).
# This is a representative subset of the ones relevant to pricing for log
# context only; it is intentionally NOT exhaustive.
KNOWN_ACTION_TYPES = {
    "AssignmentElement",
    "PricingSettings",
    "DiscountDistributionService",
    "BreakdownLineMapping",
    "ListPrice",
    "DerivedPricing",
    "PriceRevision",
    "Proration",
    "ManualDiscount",
    "VolumeDiscount",
    "VolumeTierDiscount",
    "AttributeDiscount",
    "BundleDiscount",
    "FormulaBasedPricing",
    "SubscriptionPricing",
    "GroupingAndAggregatePricing",
    "RoundingValues",
    "StopPricing",
    "MinimumPrice",
    "PriceGuidance",
    "PriceAdjustmentMatrix",
    "PricingPropagation",
    "CommercePricing",
    "GetOutputsFromDecisionMatrix",
    "GetOutputsFromDecisionTable",
}

# ExpsSetCustomElementParameterTypeEnumRepresentation — complete (5 values).
PARAM_TYPES = {"Formula", "Literal", "Lookup", "Parameter", "PickList"}

# ExpsSetVariableDataTypeEnumRepresentation — complete (14 values, OAS-confirmed).
VARIABLE_DATA_TYPES = {
    "ActionOutput",
    "Boolean",
    "Context",
    "ContextNode",
    "Currency",
    "Date",
    "DateTime",
    "DecisionMatrix",
    "DecisionTable",
    "Numeric",
    "Percent",
    "Sobject",
    "SubExpression",
    "Text",
}

# ExpsSetVariableTypeEnumRepresentation — variable `type` (5 values).
VARIABLE_TYPES = {"Constant", "Formula", "LocalListVariable", "LocalNode", "Variable"}

# ExpressionSetInterfaceSourceTypeEnumRepresentation (11 values).
INTERFACE_SOURCE_TYPES = {
    "Constraint",
    "DiscoveryProcedure",
    "EventOrchestration",
    "GpaCalculationProcedure",
    "IntelligentDecisionStudio",
    "ItServiceManagement",
    "PricingProcedure",
    "QualificationProcedure",
    "RatingDiscoveryProcedure",
    "RatingProcedure",
    "Sample",
}

# ExpsSetResourceInitializationTypeEnumRepresentation (2 values).
RESOURCE_INIT_TYPES = {"Default", "Off"}

# Fields the Connect *output* (GET) emits that are output-only. Their presence on
# an input payload is tolerated by PATCH (full-graph replace) but is worth a
# warning so authors do not hand-maintain them.
OUTPUT_ONLY_TOP_LEVEL = {"id", "error"}

# Required keys per nesting level.
REQUIRED_TOP_LEVEL = {"apiName", "name", "usageType", "versions"}
REQUIRED_VERSION = {"versionNumber", "rank", "steps"}
REQUIRED_STEP = {"name", "sequenceNumber", "stepType"}
REQUIRED_PARAM = {"name", "type"}
REQUIRED_VARIABLE = {"name", "dataType"}

# Overlay operation keys.
OVERLAY_OPS = {
    "addSteps",
    "removeSteps",
    "updateSteps",
    "reorderSteps",
    "addVariables",
    "removeVariables",
}

# HTML/XML entities the Connect GET serializer emits inside JSON string leaves
# (customElement.parameters[].value, advancedCondition.criteria[].value, formula
# text). Their presence in a payload about to be sent to Connect means it is raw
# GET output that must be HTML-unescaped first (see
# ExpressionSetConnectBase._normalize_html_entities) — otherwise the engine's
# value parser rejects the literal `&quot;`/`&#39;`. Warn so this is caught
# early rather than as an opaque server gack.
_HTML_ENTITY_RE = re.compile(r"&(?:quot|amp|lt|gt|apos|#\d+|#x[0-9a-fA-F]+);")

# Identifier tokenizer for Formula param values and externalDependencies entries.
_IDENTIFIER_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _contains_html_entities(value) -> bool:
    return isinstance(value, str) and bool(_HTML_ENTITY_RE.search(value))


class Severity(Enum):
    ERROR = "Error"
    WARNING = "Warning"


@dataclass
class Issue:
    severity: Severity
    location: str
    message: str


@dataclass
class ValidationResult:
    passed: bool = True
    issues: List[Issue] = field(default_factory=list)

    def error(self, location: str, message: str) -> None:
        self.issues.append(Issue(Severity.ERROR, location, message))
        self.passed = False

    def warn(self, location: str, message: str) -> None:
        self.issues.append(Issue(Severity.WARNING, location, message))

    @property
    def errors(self) -> List[Issue]:
        return [i for i in self.issues if i.severity is Severity.ERROR]

    @property
    def warnings(self) -> List[Issue]:
        return [i for i in self.issues if i.severity is Severity.WARNING]

    def merge(self, other: "ValidationResult") -> None:
        self.issues.extend(other.issues)
        if not other.passed:
            self.passed = False

    def format_report(self) -> str:
        if not self.issues:
            return "OK — no issues."
        lines = []
        for issue in self.issues:
            lines.append(f"[{issue.severity.value}] {issue.location}: {issue.message}")
        lines.append(
            f"\n{len(self.errors)} error(s), {len(self.warnings)} warning(s)."
        )
        return "\n".join(lines)


# ----------------------------------------------------------------------
# Shared step/param/variable checks (used by both definition and overlay)
# ----------------------------------------------------------------------


def _validate_params(
    params: list, location: str, result: ValidationResult
) -> None:
    """Validate a customElement.parameters list.

    Catches duplicate parameter names within a single element — the defect in
    the original map_line_item.json (two ``sectionJsonString9`` entries), which
    silently drops a section mapping.
    """
    if not isinstance(params, list):
        result.error(location, "customElement.parameters must be a list.")
        return
    seen: Set[str] = set()
    for i, param in enumerate(params):
        ploc = f"{location}.parameters[{i}]"
        if not isinstance(param, dict):
            result.error(ploc, "parameter must be an object.")
            continue
        missing = REQUIRED_PARAM - param.keys()
        if missing:
            result.error(ploc, f"missing required key(s): {sorted(missing)}.")
        ptype = param.get("type")
        if ptype is not None and ptype not in PARAM_TYPES:
            result.error(
                ploc,
                f"invalid param type '{ptype}'. Valid: {sorted(PARAM_TYPES)}.",
            )
        name = param.get("name")
        if name is not None:
            if name in seen:
                result.error(
                    ploc,
                    f"duplicate parameter name '{name}' within the same "
                    "customElement (later value overwrites the earlier — likely "
                    "a copy/paste numbering bug).",
                )
            seen.add(name)
        if _contains_html_entities(param.get("value")):
            result.warn(
                ploc,
                "parameter value contains HTML entities (e.g. &quot;/&#39;) — "
                "this is raw Connect GET output. It must be HTML-unescaped before "
                "PATCH/POST or the engine's value parser rejects it (\"Syntax "
                "error. Found '&'\"). The import/overlay tasks do this "
                "automatically unless normalize_html_entities:false.",
            )


def _validate_step(
    step: dict,
    location: str,
    result: ValidationResult,
    usage_type: Optional[str] = None,
    require_sequence: bool = True,
) -> None:
    if not isinstance(step, dict):
        result.error(location, "step must be an object.")
        return
    # Overlay-added steps may omit sequenceNumber: the apply task derives it
    # from the step's `placement`. In a full definition it is required.
    required = REQUIRED_STEP if require_sequence else (REQUIRED_STEP - {"sequenceNumber"})
    missing = required - step.keys()
    if missing:
        result.error(location, f"missing required key(s): {sorted(missing)}.")

    step_type = step.get("stepType")
    if step_type is not None and step_type not in STEP_TYPES:
        result.error(
            location,
            f"invalid stepType '{step_type}'. Valid: {sorted(STEP_TYPES)}.",
        )

    action_type = step.get("actionType")
    if action_type is not None and action_type not in KNOWN_ACTION_TYPES:
        result.warn(
            location,
            f"actionType '{action_type}' is not in the pricing-relevant subset "
            "this validator tracks. The full BusinessKnowledgeModel enum has "
            "~130 values and grows per release, so this is informational only — "
            "not necessarily invalid.",
        )
    if action_type == "AssignmentElement" and usage_type is not None:
        if usage_type not in ASSIGNMENT_USAGE_TYPES:
            result.error(
                location,
                f"actionType 'AssignmentElement' is only available under "
                f"usageType {sorted(ASSIGNMENT_USAGE_TYPES)}, not '{usage_type}'.",
            )

    ce = step.get("customElement")
    if ce is not None:
        if not isinstance(ce, dict):
            result.error(f"{location}.customElement", "must be an object.")
        else:
            _validate_params(ce.get("parameters", []), f"{location}.customElement", result)

    # Warn on HTML entities in expression-bearing fields (raw GET output). These
    # complement the customElement.parameters[].value check above; the engine
    # rejects literal &quot;/&#39; unless they are unescaped before PATCH/POST.
    for fld in ("formula", "conditionExpression", "assignment", "subExpression"):
        if _contains_html_entities(step.get(fld)):
            result.warn(
                f"{location}.{fld}",
                "contains HTML entities (raw GET output); HTML-unescape before "
                "PATCH/POST (handled by the import/overlay tasks unless "
                "normalize_html_entities:false).",
            )
    adv = step.get("advancedCondition")
    if isinstance(adv, dict):
        for ci, crit in enumerate(adv.get("criteria", []) or []):
            if isinstance(crit, dict) and _contains_html_entities(crit.get("value")):
                result.warn(
                    f"{location}.advancedCondition.criteria[{ci}].value",
                    "contains HTML entities (raw GET output); HTML-unescape "
                    "before PATCH/POST (handled by the import/overlay tasks "
                    "unless normalize_html_entities:false).",
                )


def _validate_variable(var: dict, location: str, result: ValidationResult) -> None:
    if not isinstance(var, dict):
        result.error(location, "variable must be an object.")
        return
    missing = REQUIRED_VARIABLE - var.keys()
    if missing:
        result.error(location, f"missing required key(s): {sorted(missing)}.")
    data_type = var.get("dataType")
    if data_type is not None and data_type not in VARIABLE_DATA_TYPES:
        result.error(
            location,
            f"invalid variable dataType '{data_type}'. Valid: "
            f"{sorted(VARIABLE_DATA_TYPES)} (NOT Number/Decimal/Double).",
        )
    var_type = var.get("type")
    if var_type is not None and var_type not in VARIABLE_TYPES:
        result.error(
            location,
            f"invalid variable type '{var_type}'. Valid: {sorted(VARIABLE_TYPES)}.",
        )


def _validate_sequence_numbers(
    steps: list, location: str, result: ValidationResult
) -> None:
    """Check top-level step sequenceNumbers are present, unique, contiguous.

    sequenceNumber is scoped PER PARENT: child steps (with a non-null
    parentStep) restart at 1 under each parent. We validate the top-level scope
    (parentStep is None) and each parent's child scope independently.
    """
    by_scope: Dict[Optional[str], List[int]] = {}
    for step in steps:
        if not isinstance(step, dict):
            continue
        scope = step.get("parentStep")
        seq = step.get("sequenceNumber")
        by_scope.setdefault(scope, [])
        if isinstance(seq, int):
            by_scope[scope].append(seq)

    for scope, seqs in by_scope.items():
        scope_label = "top-level" if scope is None else f"children of '{scope}'"
        dupes = {s for s in seqs if seqs.count(s) > 1}
        if dupes:
            result.error(
                location,
                f"duplicate sequenceNumber(s) {sorted(dupes)} among {scope_label} "
                "steps (sequenceNumber must be unique within a parent scope).",
            )
        if seqs:
            expected = set(range(1, len(seqs) + 1))
            actual = set(seqs)
            if actual != expected:
                missing = sorted(expected - actual)
                extra = sorted(actual - expected)
                result.warn(
                    location,
                    f"{scope_label} sequenceNumbers are not contiguous 1..N "
                    f"(missing {missing}, unexpected {extra}). The engine "
                    "tolerates gaps but renumbering keeps exports stable.",
                )


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------


def detect_kind(data) -> str:
    """Return 'overlay' or 'definition' for an arbitrary parsed JSON payload.

    A dict carrying any OVERLAY_OPS key is an overlay; one with a ``versions``
    array is a definition; anything else defaults to overlay (the more common
    author-facing shape).
    """
    if isinstance(data, dict) and data.keys() & OVERLAY_OPS:
        return "overlay"
    if isinstance(data, dict) and "versions" in data:
        return "definition"
    return "overlay"


def validate_definition(defn: dict) -> ValidationResult:
    """Validate a full ExpressionSet definition (export/import shape)."""
    result = ValidationResult()
    if not isinstance(defn, dict):
        result.error("(root)", "definition must be a JSON object.")
        return result

    missing = REQUIRED_TOP_LEVEL - defn.keys()
    if missing:
        result.error("(root)", f"missing required key(s): {sorted(missing)}.")

    usage_type = defn.get("usageType")
    if usage_type is not None and usage_type not in USAGE_TYPES:
        result.warn(
            "(root)",
            f"unrecognized usageType '{usage_type}' (known: {sorted(USAGE_TYPES)}).",
        )

    interface_source = defn.get("interfaceSourceType")
    if interface_source is not None and interface_source not in INTERFACE_SOURCE_TYPES:
        result.error(
            "(root)",
            f"invalid interfaceSourceType '{interface_source}'. Valid: "
            f"{sorted(INTERFACE_SOURCE_TYPES)}.",
        )

    resource_init = defn.get("resourceInitializationType")
    if resource_init is not None and resource_init not in RESOURCE_INIT_TYPES:
        result.error(
            "(root)",
            f"invalid resourceInitializationType '{resource_init}'. Valid: "
            f"{sorted(RESOURCE_INIT_TYPES)}.",
        )

    # Output-only fields (emitted by the Connect GET) are tolerated by a PATCH
    # full-graph replace but should not be hand-maintained on an input payload —
    # warn so authors don't carry them by hand (mirrors the version-level 'id'
    # warning below).
    present_output_only = OUTPUT_ONLY_TOP_LEVEL & defn.keys()
    if present_output_only:
        result.warn(
            "(root)",
            f"output-only field(s) {sorted(present_output_only)} present — these are "
            "emitted by the Connect GET output and don't need to be hand-maintained on "
            "an input payload (tolerated by a PATCH full-graph replace; the import task "
            "doesn't require them).",
        )

    versions = defn.get("versions")
    if not isinstance(versions, list) or not versions:
        result.error("(root).versions", "must be a non-empty list.")
        return result

    for vi, version in enumerate(versions):
        vloc = f"versions[{vi}]"
        if not isinstance(version, dict):
            result.error(vloc, "version must be an object.")
            continue
        vmissing = REQUIRED_VERSION - version.keys()
        if vmissing:
            result.error(vloc, f"missing required key(s): {sorted(vmissing)}.")

        # The version-level `id` is output-only on a POST-create (a source-org
        # 9QM the server rejects/mis-binds) but required for a PATCH-replace
        # (matches the version in place). The import task strips it on create;
        # warn so a hand-authored create payload is not surprised by it.
        if version.get("id"):
            result.warn(
                vloc,
                "version carries an 'id' — required for a Connect PATCH-replace "
                "but must be omitted on a POST-create (the import task strips it "
                "automatically when creating a new expression set).",
            )

        steps = version.get("steps", [])
        if not isinstance(steps, list):
            result.error(f"{vloc}.steps", "must be a list.")
            steps = []

        step_names = {
            s.get("name") for s in steps if isinstance(s, dict) and s.get("name")
        }
        for si, step in enumerate(steps):
            _validate_step(step, f"{vloc}.steps[{si}]", result, usage_type)
            # parentStep must resolve to a real step.
            if isinstance(step, dict):
                parent = step.get("parentStep")
                if parent is not None and parent not in step_names:
                    result.error(
                        f"{vloc}.steps[{si}]",
                        f"parentStep '{parent}' does not match any step name.",
                    )

        _validate_sequence_numbers(steps, f"{vloc}.steps", result)

        # Pricing procedures must start with a PricingSettings step.
        if usage_type in ASSIGNMENT_USAGE_TYPES:
            top_level = sorted(
                (s for s in steps if isinstance(s, dict) and s.get("parentStep") is None),
                key=lambda s: s.get("sequenceNumber", 0),
            )
            if top_level and top_level[0].get("actionType") != "PricingSettings":
                result.error(
                    f"{vloc}.steps",
                    "a pricing procedure must start with a PricingSettings step "
                    f"(first step is '{top_level[0].get('name')}' with actionType "
                    f"'{top_level[0].get('actionType')}').",
                )

        variables = version.get("variables", [])
        if not isinstance(variables, list):
            result.error(f"{vloc}.variables", "must be a list.")
        else:
            seen_var_names: Set[str] = set()
            for vri, var in enumerate(variables):
                _validate_variable(var, f"{vloc}.variables[{vri}]", result)
                if isinstance(var, dict):
                    name = var.get("name")
                    if name and name in seen_var_names:
                        result.error(
                            f"{vloc}.variables[{vri}]",
                            f"duplicate variable name '{name}'.",
                        )
                    if name:
                        seen_var_names.add(name)

    return result


def validate_overlay(overlay: dict) -> ValidationResult:
    """Validate a declarative overlay payload."""
    result = ValidationResult()
    if not isinstance(overlay, dict):
        result.error("(root)", "overlay must be a JSON object.")
        return result

    present_ops = overlay.keys() & OVERLAY_OPS
    if not present_ops:
        result.warn(
            "(root)",
            f"overlay has no operation keys ({sorted(OVERLAY_OPS)}) — it is a no-op.",
        )

    # Determine usageType context if the overlay declares it (optional).
    usage_type = overlay.get("usageType")

    add_steps = overlay.get("addSteps", [])
    if not isinstance(add_steps, list):
        result.error("addSteps", "must be a list.")
        add_steps = []

    added_names: Set[str] = set()
    for i, step in enumerate(add_steps):
        loc = f"addSteps[{i}]"
        _validate_step(step, loc, result, usage_type, require_sequence=False)
        if isinstance(step, dict):
            name = step.get("name")
            if name in added_names:
                result.error(loc, f"duplicate added step name '{name}'.")
            added_names.add(name)
            placement = step.get("placement")
            if placement is not None and not isinstance(placement, dict):
                result.error(f"{loc}.placement", "must be an object.")
            elif isinstance(placement, dict):
                keys = placement.keys() & {"afterStep", "beforeStep", "sequenceNumber"}
                if len(keys) > 1:
                    result.error(
                        f"{loc}.placement",
                        f"specify only one of afterStep/beforeStep/sequenceNumber "
                        f"(found {sorted(keys)}).",
                    )

    for op in ("removeSteps", "updateSteps", "reorderSteps"):
        items = overlay.get(op, [])
        if not isinstance(items, list):
            result.error(op, "must be a list.")
            continue
        for i, item in enumerate(items):
            if not isinstance(item, dict) or not item.get("name"):
                result.error(f"{op}[{i}]", "must be an object with a 'name'.")
            if op == "reorderSteps" and isinstance(item, dict):
                if not isinstance(item.get("sequenceNumber"), int):
                    result.error(
                        f"{op}[{i}]",
                        "reorderSteps entry requires an integer sequenceNumber.",
                    )

    add_vars = overlay.get("addVariables", [])
    if not isinstance(add_vars, list):
        result.error("addVariables", "must be a list.")
    else:
        added_var_names: Set[str] = set()
        for i, var in enumerate(add_vars):
            _validate_variable(var, f"addVariables[{i}]", result)
            if isinstance(var, dict):
                name = var.get("name")
                if name and name in added_var_names:
                    result.error(
                        f"addVariables[{i}]",
                        f"duplicate added variable name '{name}'.",
                    )
                if name:
                    added_var_names.add(name)

    remove_vars = overlay.get("removeVariables", [])
    if not isinstance(remove_vars, list):
        result.error("removeVariables", "must be a list.")
    else:
        for i, entry in enumerate(remove_vars):
            if isinstance(entry, str):
                if not entry:
                    result.error(
                        f"removeVariables[{i}]", "variable name must be non-empty."
                    )
            elif isinstance(entry, dict):
                if not entry.get("name"):
                    result.error(
                        f"removeVariables[{i}]",
                        "object entry requires a non-empty 'name'.",
                    )
            else:
                result.error(
                    f"removeVariables[{i}]",
                    "must be a string name or an object with a 'name'.",
                )

    _validate_external_dependencies(overlay.get("externalDependencies"), result)
    _warn_undeclared_external_dependencies(overlay, result)

    return result


# Suffixes that mark a reference as a CUSTOM, org-specific external dependency
# the overlay cannot ship in addVariables (custom fields / relationships). These
# may not exist in a target org and — for fields a step consumes — must be mapped
# into the bound ContextDefinition before the overlay applies, so they belong in
# the overlay's `externalDependencies` block.
#
# NOTE: `__std` and no-suffix names are STANDARD fields shipped with the standard
# context definitions (they are NOT custom) — they are established context, not an
# external dependency the overlay must declare.
_CUSTOM_REF_SUFFIXES = ("__c", "__r")


def _is_custom_ref(name: str) -> bool:
    return isinstance(name, str) and name.endswith(_CUSTOM_REF_SUFFIXES)


def _validate_external_dependencies(deps, result: "ValidationResult") -> None:
    """Validate the optional ``externalDependencies`` block shape.

    Schema (all optional, all lists of strings except ``note``)::

        "externalDependencies": {
          "customFields":  ["SalesTransaction_Hospitals__c (mapped into <ctx>)", ...],
          "contextNodes":  ["<custom ContextDefinition node>", ...],
          "contextFields": ["ItemProductCode", ...],
          "note": "free text"
        }

    The name is deliberate: these are dependencies **external** to the overlay —
    things it does NOT create, in contrast to ``addVariables`` (which it does).
    They are what the target org must already have for the overlay to apply:
    custom fields/relationships, custom ContextDefinition nodes, and the context
    mappings that expose them. The block is declarative metadata: the apply task
    ignores it; the validator checks its shape and uses it to suppress the
    undeclared-dependency warning below.
    """
    if deps is None:
        return
    if not isinstance(deps, dict):
        result.error("externalDependencies", "must be an object.")
        return
    allowed = {"customFields", "contextNodes", "contextFields", "note"}
    extra = set(deps) - allowed
    if extra:
        result.warn(
            "externalDependencies",
            f"unknown key(s) {sorted(extra)}; recognized keys are {sorted(allowed)}.",
        )
    for key in ("customFields", "contextNodes", "contextFields"):
        val = deps.get(key)
        if val is None:
            continue
        if not isinstance(val, list) or not all(isinstance(x, str) for x in val):
            result.error(f"externalDependencies.{key}", "must be a list of strings.")
    if "note" in deps and not isinstance(deps["note"], str):
        result.error("externalDependencies.note", "must be a string.")


def _declared_external_dependency_tokens(overlay: dict) -> Set[str]:
    """Identifier tokens named anywhere in the overlay's externalDependencies block.

    A declaration entry is free text (e.g. ``"Foo__c (mapped into Bar)"``); we
    extract the identifier-like tokens so a reference counts as declared if its
    name appears in any entry.
    """
    deps = overlay.get("externalDependencies")
    if not isinstance(deps, dict):
        return set()
    tokens: Set[str] = set()
    for key in ("customFields", "contextNodes", "contextFields"):
        for entry in deps.get(key, []) or []:
            if isinstance(entry, str):
                tokens.update(_IDENTIFIER_RE.findall(entry))
    return tokens


def _warn_undeclared_external_dependencies(
    overlay: dict, result: "ValidationResult"
) -> None:
    """Warn when addSteps reference a custom field/node not in `externalDependencies`.

    A custom reference (``__c``/``__r``/custom context node) that an added step
    CONSUMES cannot be shipped by the overlay (it is not a version variable) —
    the target org must already define it, mapped into the bound
    ContextDefinition. If it is not produced by an added step and not named in
    the overlay's `externalDependencies`, warn so the author documents it. This
    turns a silent apply-time-only failure (the field is missing in the target)
    into an authoring-time prompt.

    Standard fields (``__std`` / no suffix) are shipped with the standard context
    definitions, so they are NOT flagged — only genuinely custom references are.
    """
    add_steps = overlay.get("addSteps", []) or []
    if not isinstance(add_steps, list):
        return
    produced: Set[str] = set()
    for st in add_steps:
        _, p = _step_all_refs(st)
        produced |= p
    declared = _declared_external_dependency_tokens(overlay)
    add_var_names = {
        v.get("name")
        for v in overlay.get("addVariables", []) or []
        if isinstance(v, dict)
    }
    flagged: Set[str] = set()
    for st in add_steps:
        consumed, _ = _step_all_refs(st)
        for name in consumed:
            if not _is_custom_ref(name):
                continue
            if name in produced or name in declared or name in add_var_names:
                continue
            flagged.add(name)
    if flagged:
        result.warn(
            "externalDependencies",
            f"addSteps consume custom reference(s) {sorted(flagged)} that the "
            f"overlay cannot create (not version variables). The target org must "
            f"already define them — custom fields must be mapped into the bound "
            f"ContextDefinition. Declare them in an `externalDependencies` block "
            f"(customFields/contextNodes) to document the requirement and "
            f"silence this warning.",
        )


def validate_overlay_against_definition(
    overlay: dict, definition: dict, version_api_name: Optional[str] = None
) -> ValidationResult:
    """Cross-check overlay placement/reorder targets against a live definition.

    Verifies that every placement.afterStep/beforeStep and reorderSteps/
    updateSteps/removeSteps target names actually exist in the target version,
    so a typo'd target fails locally instead of mid-PATCH.
    """
    result = validate_overlay(overlay)
    versions = definition.get("versions", []) if isinstance(definition, dict) else []
    version = None
    if version_api_name:
        version = next(
            (v for v in versions if v.get("apiName") == version_api_name), None
        )
    elif versions:
        version = versions[0]
    if not version:
        result.error("(definition)", "could not resolve target version for overlay.")
        return result

    existing = {
        s.get("name")
        for s in version.get("steps", [])
        if isinstance(s, dict) and s.get("name")
    }
    # A placement target is valid if it pre-exists in the version OR is an
    # earlier addSteps entry in THIS overlay: _add_steps processes addSteps in
    # array order and appends as it goes, so a later step can legitimately be
    # placed afterStep/beforeStep a sibling added earlier in the same overlay
    # (e.g. chaining ListGroup blocks one after another). Checking only against
    # the pre-existing steps would reject every chained-placement overlay.
    added_so_far: Set[str] = set()
    for i, step in enumerate(overlay.get("addSteps", []) or []):
        placement = step.get("placement") if isinstance(step, dict) else None
        if isinstance(placement, dict):
            for key in ("afterStep", "beforeStep"):
                target = placement.get(key)
                if target and target not in existing and target not in added_so_far:
                    result.error(
                        f"addSteps[{i}].placement.{key}",
                        f"target step '{target}' not found in version "
                        f"'{version.get('apiName')}' or in an earlier addSteps "
                        f"entry.",
                    )
        if isinstance(step, dict) and step.get("name"):
            added_so_far.add(step["name"])
    for op in ("removeSteps", "updateSteps", "reorderSteps"):
        for i, item in enumerate(overlay.get(op, []) or []):
            name = item.get("name") if isinstance(item, dict) else None
            if name and name not in existing:
                result.error(
                    f"{op}[{i}]",
                    f"step '{name}' not found in version "
                    f"'{version.get('apiName')}'.",
                )

    _warn_unresolved_step_variable_refs(overlay, version, result)
    return result


def _step_variable_refs(step: dict) -> "tuple[Set[str], Set[str]]":
    """Return (consumed, produced) variable names a step references.

    A reference is a ``customElement.parameters[]`` entry with ``type: Parameter``
    (the variable name is its ``value``) or an
    ``advancedCondition.criteria[].sourceFieldName``. ``input`` params (and filter
    criteria) are consumed; ``output`` params are produced.
    """
    consumed: Set[str] = set()
    produced: Set[str] = set()
    if not isinstance(step, dict):
        return consumed, produced
    ce = step.get("customElement") or {}
    for p in ce.get("parameters", []) or []:
        if not isinstance(p, dict) or p.get("type") != "Parameter":
            continue
        val = p.get("value")
        if not val:
            continue
        if p.get("input"):
            consumed.add(val)
        if p.get("output"):
            produced.add(val)
    ac = step.get("advancedCondition") or {}
    for c in ac.get("criteria", []) or []:
        if isinstance(c, dict) and c.get("sourceFieldName"):
            consumed.add(c["sourceFieldName"])
    return consumed, produced


def _step_all_refs(step: dict) -> "tuple[Set[str], Set[str]]":
    """Like ``_step_variable_refs`` but also harvests identifier tokens from
    ``Formula``-type params.

    A FormulaBasedPricing step references fields inside an expression string
    (e.g. ``"SalesTransaction_Hospitals__c - ItemStartQuantity"``), not as
    discrete Parameter params. For external-dependency detection a formula's tokens are
    treated as consumed; its ``output`` param is produced. Returns
    (consumed, produced).
    """
    consumed, produced = _step_variable_refs(step)
    if not isinstance(step, dict):
        return consumed, produced
    ce = step.get("customElement") or {}
    for p in ce.get("parameters", []) or []:
        if not isinstance(p, dict) or p.get("type") != "Formula":
            continue
        # Formula params are inputs; tokenize identifier-like names.
        consumed.update(_IDENTIFIER_RE.findall(str(p.get("value", ""))))
    return consumed, produced


def _warn_unresolved_step_variable_refs(
    overlay: dict, version: dict, result: "ValidationResult"
) -> None:
    """Warn when an addSteps step consumes a variable nothing in the target can
    supply.

    An added step's consumed variable is *satisfied* when the name is:
      * shipped in the overlay's ``addVariables``,
      * a version-level variable already declared in the target, or
      * produced (output) by one of the overlay's own added steps, or
      * already referenced by an existing target step (proving the bound
        ``ContextDefinition`` supplies it — `__std` fields / context tags).

    Anything else has no producer in that target: applying the overlay there
    references an undefined variable. This is a **warning** (not an error)
    because the cross-check cannot prove a context binding won't supply a name
    it has simply never been asked for — but in practice an unresolved name is
    the missing-version-variable class (e.g. a `Constant_*` the source org had
    but the target lacks), so it is worth surfacing before a non-atomic PATCH.
    """
    add_steps = overlay.get("addSteps", []) or []
    if not isinstance(add_steps, list):
        return

    target_vars = {
        v.get("name")
        for v in version.get("variables", []) or []
        if isinstance(v, dict) and v.get("name")
    }
    target_refs: Set[str] = set()
    for s in version.get("steps", []) or []:
        c, p = _step_variable_refs(s)
        target_refs |= c | p

    add_var_names = {
        v.get("name")
        for v in overlay.get("addVariables", []) or []
        if isinstance(v, dict) and v.get("name")
    }
    overlay_produced: Set[str] = set()
    for st in add_steps:
        _, p = _step_variable_refs(st)
        overlay_produced |= p

    satisfied = target_vars | target_refs | add_var_names | overlay_produced
    for i, st in enumerate(add_steps):
        consumed, _ = _step_variable_refs(st)
        unresolved = sorted(n for n in consumed if n not in satisfied)
        if unresolved:
            result.warn(
                f"addSteps[{i}]",
                f"step '{st.get('name')}' references variable(s) {unresolved} "
                f"that are not in the overlay's addVariables, not declared in "
                f"target version '{version.get('apiName')}', not produced by an "
                f"added step, and not used by any existing step. If these are "
                f"version-level variables (e.g. a Constant_*), ship them in "
                f"addVariables; if they are context-resolved (__std fields / "
                f"context tags), confirm the target binds the right "
                f"ContextDefinition.",
            )
