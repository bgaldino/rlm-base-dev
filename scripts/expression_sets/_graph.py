#!/usr/bin/env python3
"""Producer/consumer dependency graph for a BRE Expression Set version.

Pure, transport-free. Turns a Connect GET (``versions[].steps[]`` +
``version.variables[]``) into a variable-dependency graph — who *produces* each
name, who *consumes* it — and classifies every referenced name into the three
dependency scopes the expression-sets skill's "capture dependencies" problem
turns on:

  * **version**  — declared in the version's ``variables[]`` (a ``Constant_*`` /
    ``Local*`` / ``Variable``). To move a step to another org, ship these in the
    overlay's ``addVariables``.
  * **custom**   — a ``__c`` / ``__r`` custom field or custom context node. The
    overlay CANNOT create these; the target org must already define them, mapped
    into the bound ContextDefinition. Declare them in ``externalDependencies``.
  * **standard** — context-supplied (a ``__std`` field, a bare context field/tag
    the bound ContextDefinition provides). Declare nothing.

Reference harvesting and custom-ref detection are imported from the package's
vendored validator ``._schema`` (``_step_variable_refs``, ``_is_custom_ref``,
``_IDENTIFIER_RE``) so trace's "satisfied"/scope logic stays aligned with the
overlay validator and the two can never diverge. In-package import only — the
toolkit is self-contained and imports nothing from ``tasks/``.

Role symbols (step-relative, used by the trace CLI):
    >  produces (output Parameter)
    <  consumes (input Parameter)
    ?  consumes as a filter criterion (advancedCondition.criteria[].sourceFieldName)
    ~  consumes inside a Formula (best-effort token match — may over-report
       function names / dotted paths)

Formula edges are BEST-EFFORT: a Formula param value is tokenized, so function
names and dotted path segments can appear as phantom consumers. The trace CLI
labels them ``~`` and its caveat text says so.
"""

from typing import Any, Dict, List, Optional, Set

# Reuse the package's own validator harvesters/detectors so scope logic never
# drifts from the overlay cross-check. In-package import (the toolkit is
# self-contained — it does NOT import from tasks/).
from ._schema import (
    _IDENTIFIER_RE,
    _is_custom_ref,
    _step_variable_refs,
)

# Scope names.
SCOPE_VERSION = "version"
SCOPE_CUSTOM = "custom"
SCOPE_STANDARD = "standard"


class Edge:
    """One (step, name, role) reference. ``role`` is a symbol from the module docstring."""

    __slots__ = ("step", "name", "role")

    def __init__(self, step: str, name: str, role: str):
        self.step = step
        self.name = name
        self.role = role

    def __repr__(self):
        return f"Edge({self.step!r} {self.role} {self.name!r})"


def _version(definition: dict, version_api_name: Optional[str]) -> dict:
    versions = definition.get("versions", []) if isinstance(definition, dict) else []
    if not versions:
        return {}
    if version_api_name:
        for v in versions:
            if v.get("apiName") == version_api_name:
                return v
    return versions[0]


def _formula_tokens(step: dict) -> Set[str]:
    """Identifier tokens from Formula-type params (best-effort consume edges)."""
    tokens: Set[str] = set()
    ce = step.get("customElement") or {}
    for p in ce.get("parameters", []) or []:
        if isinstance(p, dict) and p.get("type") == "Formula":
            tokens.update(_IDENTIFIER_RE.findall(str(p.get("value", ""))))
    return tokens


def _filter_refs(step: dict) -> Set[str]:
    """Names consumed as advancedCondition filter criteria."""
    refs: Set[str] = set()
    ac = step.get("advancedCondition") or {}
    for c in ac.get("criteria", []) or []:
        if isinstance(c, dict) and c.get("sourceFieldName"):
            refs.add(c["sourceFieldName"])
    return refs


class ExpressionSetGraph:
    """Producer/consumer graph over one version's steps.

    Build from a Connect GET payload; then query producers / consumers / scope
    for any referenced name, or scan for orphans.
    """

    def __init__(self, definition: dict, version_api_name: Optional[str] = None):
        self.definition = definition
        version = _version(definition, version_api_name)
        self.version_api_name = version.get("apiName")
        self.steps: List[dict] = [
            s for s in version.get("steps", []) or [] if isinstance(s, dict)
        ]
        self.variable_names: Set[str] = {
            v.get("name")
            for v in version.get("variables", []) or []
            if isinstance(v, dict) and v.get("name")
        }

        self.edges: List[Edge] = []
        self.producers: Dict[str, List[str]] = {}
        self.consumers: Dict[str, List[str]] = {}
        self._build()

    # -- construction --------------------------------------------------

    def _add(self, bucket: Dict[str, List[str]], name: str, step: str):
        bucket.setdefault(name, [])
        if step not in bucket[name]:
            bucket[name].append(step)

    def _build(self):
        for step in self.steps:
            step_name = step.get("name") or "(unnamed)"
            consumed, produced = _step_variable_refs(step)
            filter_consumed = _filter_refs(step)
            # _step_variable_refs already folds filter criteria into `consumed`;
            # separate the pure Parameter-input consumes from filter consumes so
            # the role symbol is accurate.
            param_consumed = consumed - filter_consumed
            formula_consumed = _formula_tokens(step)

            for name in produced:
                self.edges.append(Edge(step_name, name, ">"))
                self._add(self.producers, name, step_name)
            for name in param_consumed:
                self.edges.append(Edge(step_name, name, "<"))
                self._add(self.consumers, name, step_name)
            for name in filter_consumed:
                self.edges.append(Edge(step_name, name, "?"))
                self._add(self.consumers, name, step_name)
            # Formula tokens are best-effort; only record ones not already a
            # discrete Parameter reference on this step, to reduce noise.
            for name in formula_consumed - consumed - produced:
                self.edges.append(Edge(step_name, name, "~"))
                self._add(self.consumers, name, step_name)

    # -- queries -------------------------------------------------------

    @property
    def referenced_names(self) -> Set[str]:
        return set(self.producers) | set(self.consumers)

    def scope(self, name: str) -> str:
        """Classify a referenced name into version / custom / standard scope."""
        if name in self.variable_names:
            return SCOPE_VERSION
        if _is_custom_ref(name):
            return SCOPE_CUSTOM
        return SCOPE_STANDARD

    def produced_by(self, name: str) -> List[str]:
        return list(self.producers.get(name, []))

    def consumed_by(self, name: str) -> List[str]:
        return list(self.consumers.get(name, []))

    def step_edges(self, step_name: str) -> List[Edge]:
        """All reference edges (in/out/filter/formula) for one step."""
        return [e for e in self.edges if e.step == step_name]

    def step_closure(self, step_name: str) -> Dict[str, Any]:
        """A step's full dependency closure with scopes.

        Returns ``{consumes: [{name, role, scope, producers}], produces: [names]}``
        — exactly what ``export_expression_set_overlay`` needs to pre-classify the three scopes.
        """
        edges = self.step_edges(step_name)
        consumes = []
        produces = []
        for e in edges:
            if e.role == ">":
                produces.append(e.name)
            else:
                consumes.append({
                    "name": e.name,
                    "role": e.role,
                    "scope": self.scope(e.name),
                    "producers": self.produced_by(e.name),
                })
        return {"step": step_name, "consumes": consumes, "produces": sorted(set(produces))}

    def orphans(self) -> Dict[str, List[str]]:
        """Detect the three orphan classes.

        * ``consumed_no_producer`` — consumed by a step but produced by none AND
          not a version variable AND not standard-context-satisfiable → removal
          danger / undeclared dependency. Custom refs land here too (they have
          no in-graph producer).
        * ``produced_unused``      — produced but consumed by no step → dead output.
        * ``undeclared_custom``    — the custom-scoped subset of the above
          consumed-with-no-producer set (the ``externalDependencies`` gap).

        A name consumed with no producer is only flagged when it is NOT a version
        variable (version variables are satisfied by declaration, even without a
        producer step — e.g. a Constant).
        """
        consumed_no_producer = []
        undeclared_custom = []
        for name in sorted(self.consumers):
            if self.producers.get(name):
                continue
            if name in self.variable_names:
                continue  # declared version variable — satisfied
            consumed_no_producer.append(name)
            if _is_custom_ref(name):
                undeclared_custom.append(name)
        produced_unused = sorted(
            name for name in self.producers if not self.consumers.get(name)
        )
        return {
            "consumed_no_producer": consumed_no_producer,
            "produced_unused": produced_unused,
            "undeclared_custom": undeclared_custom,
        }
