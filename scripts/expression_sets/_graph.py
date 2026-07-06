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

import re
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

# Mermaid scope styling — one classDef per dependency scope, so a rendered
# dependency diagram is color-legible without a legend: green=version variable
# (ship in addVariables), red=custom (externalDependencies / target must define),
# blue=standard context (declare nothing). Kept here next to the SCOPE_* names so
# the two never drift.
_MERMAID_CLASSDEFS = [
    "classDef version fill:#e7f5e7,stroke:#2e7d32,color:#1b5e20;",
    "classDef custom fill:#fdecea,stroke:#c62828,color:#b71c1c;",
    "classDef standard fill:#e8eef7,stroke:#1565c0,color:#0d47a1;",
    "classDef step fill:#ffffff,stroke:#555555,color:#111111;",
]


def _mermaid_escape(label: str) -> str:
    """Make a human label safe inside a Mermaid ``["…"]`` quoted node.

    Only the double-quote needs escaping inside a quoted label (Mermaid reads the
    ``#quot;`` entity); ``<br/>`` and other markup are intentionally passed
    through so multi-line labels render.
    """
    return str(label).replace('"', "#quot;")


class _MermaidIds:
    """Allocate stable, collision-free Mermaid node ids from arbitrary names.

    Mermaid node ids must be identifier-ish; step/variable names carry spaces and
    punctuation. Sanitize to ``[A-Za-z0-9_]``, prefix per namespace (``s_`` steps,
    ``v_`` variables) so a step and a like-named variable never collide, and
    append a counter on the rare post-sanitization clash. Insertion-order
    deterministic — same definition renders byte-identical output every run.
    """

    def __init__(self, prefix: str):
        self.prefix = prefix
        self._by_name: Dict[str, str] = {}
        self._used: Set[str] = set()

    def get(self, name: str) -> str:
        if name in self._by_name:
            return self._by_name[name]
        raw = re.sub(r"[^0-9A-Za-z]", "_", str(name)) or "x"
        base = f"{self.prefix}{raw}"
        candidate, i = base, 2
        while candidate in self._used:
            candidate = f"{base}_{i}"
            i += 1
        self._used.add(candidate)
        self._by_name[name] = candidate
        return candidate


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

    # -- ordering ------------------------------------------------------

    def ordered_steps(self) -> List[dict]:
        """Steps in execution order: top-level by sequenceNumber, children nested.

        Matches ``describe_expression_set._order_steps`` — top-level steps
        (``parentStep is None``) sorted by sequenceNumber, each parent's children
        following it in their own per-parent sequenceNumber order. Steps whose
        named parent is absent are appended last so nothing is dropped.
        """
        children: Dict[str, List[dict]] = {}
        top: List[dict] = []
        for s in self.steps:
            parent = s.get("parentStep")
            if parent:
                children.setdefault(parent, []).append(s)
            else:
                top.append(s)
        top.sort(key=lambda s: s.get("sequenceNumber", 0))
        for kids in children.values():
            kids.sort(key=lambda s: s.get("sequenceNumber", 0))

        ordered: List[dict] = []
        seen: Set[str] = set()

        def emit(step: dict):
            name = step.get("name")
            if name in seen:
                return
            seen.add(name)
            ordered.append(step)
            for kid in children.get(name, []):
                emit(kid)

        for s in top:
            emit(s)
        # Any child whose parent name never appeared as a step — don't drop it.
        for s in self.steps:
            if s.get("name") not in seen:
                ordered.append(s)
                seen.add(s.get("name"))
        return ordered

    # -- Mermaid rendering ---------------------------------------------

    def to_mermaid_flow(self, *, title: Optional[str] = None) -> str:
        """Execution-flow diagram: steps in sequenceNumber order, children nested.

        A top-down ``flowchart`` where consecutive top-level steps are chained by
        a solid arrow (the run order) and each child hangs off its parent by a
        dashed ``-. child .->`` edge. Pure — no org access; deterministic output.
        """
        ids = _MermaidIds("s_")
        lines: List[str] = ["flowchart TD"]
        if title:
            lines.append(f'  %% {title}')

        ordered = self.ordered_steps()
        prev_top: Optional[str] = None  # last top-level node id, for run-order chain
        for step in ordered:
            name = step.get("name") or "(unnamed)"
            nid = ids.get(name)
            stype = step.get("stepType") or step.get("actionType") or ""
            label = name if not stype else f"{name}<br/><i>{stype}</i>"
            lines.append(f'  {nid}["{_mermaid_escape(label)}"]')
            parent = step.get("parentStep")
            if parent:
                lines.append(f'  {ids.get(parent)} -. child .-> {nid}')
            else:
                if prev_top is not None:
                    lines.append(f'  {prev_top} --> {nid}')
                prev_top = nid
            lines.append(f"  class {nid} step;")

        if len(ordered) == 0:
            lines.append("  empty[/no steps in this version/]")
        lines.extend("  " + d for d in _MERMAID_CLASSDEFS)
        return "\n".join(lines) + "\n"

    def to_mermaid_deps(
        self, *, only_steps: Optional[Set[str]] = None, title: Optional[str] = None
    ) -> str:
        """Data-dependency diagram: producer → variable → consumer, scope-colored.

        Steps are boxes; every referenced name is a rounded node classed by scope
        (version / custom / standard). Edges carry the role symbol as their label
        (``>`` producer→var, ``<`` / ``?`` / ``~`` var→consumer). Pass
        ``only_steps`` to scope the diagram to those steps plus the variables they
        touch and the immediate neighbor steps on the other side of each variable
        (the one-step neighborhood — what ``trace --step`` shows, drawn). Pure.
        """
        step_ids = _MermaidIds("s_")
        var_ids = _MermaidIds("v_")
        lines: List[str] = ["flowchart LR"]
        if title:
            lines.append(f'  %% {title}')

        # Which edges to draw. With only_steps, keep every edge touching a focus
        # step, then pull in each connected variable's OTHER edges so the neighbor
        # steps (producers/consumers on the far side of the variable) show too.
        edges = self.edges
        if only_steps:
            focus_vars = {e.name for e in edges if e.step in only_steps}
            edges = [
                e for e in edges
                if e.step in only_steps or e.name in focus_vars
            ]

        step_names: List[str] = []
        var_names: List[str] = []
        rendered: Set[str] = set()

        def _step_node(name: str):
            if name in rendered:
                return
            rendered.add(name)
            step_names.append(name)
            nid = step_ids.get(name)
            focus = only_steps and name in only_steps
            label = f"{name}" + ("<br/><b>◆ focus</b>" if focus else "")
            lines.append(f'  {nid}["{_mermaid_escape(label)}"]')

        def _var_node(name: str):
            key = f"__var__{name}"
            if key in rendered:
                return
            rendered.add(key)
            var_names.append(name)
            vid = var_ids.get(name)
            lines.append(f'  {vid}("{_mermaid_escape(name)}")')

        for e in edges:
            _step_node(e.step)
            _var_node(e.name)
            sid = step_ids.get(e.step)
            vid = var_ids.get(e.name)
            if e.role == ">":  # step produces variable
                lines.append(f'  {sid} -->|"{e.role}"| {vid}')
            else:  # variable consumed by step (<, ?, ~)
                style = "-.->" if e.role in ("?", "~") else "-->"
                lines.append(f'  {vid} {style}|"{e.role}"| {sid}')

        if not edges:
            lines.append("  empty[/no variable references/]")

        # Class assignments: steps → step; variables → their scope.
        for name in step_names:
            lines.append(f"  class {step_ids.get(name)} step;")
        for name in var_names:
            lines.append(f"  class {var_ids.get(name)} {self.scope(name)};")
        lines.extend("  " + d for d in _MERMAID_CLASSDEFS)
        return "\n".join(lines) + "\n"
