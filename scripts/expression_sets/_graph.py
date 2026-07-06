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

# Mermaid node kinds — a finer *display* taxonomy layered over the three
# dependency SCOPES. scope() stays the load-bearing capture-logic axis (the
# validator depends on its version/custom/standard trichotomy); node_kind()
# refines it purely for the diagram, splitting version→(constant, variable) by
# the variable's declared ``type`` and standard→(std, context) by the ``__std``
# suffix. Every kind carries the same color as its parent scope (green=version,
# red=custom, blue=standard) PLUS a distinct node SHAPE, so the diagram stays
# legible in monochrome and a reader can tell a step from a constant from a
# context tag at a glance. Grounded only in what the Connect GET itself reveals:
#
#   kind      what it is                                     scope     shape       delims
#   step      a procedure step                               —         rectangle   [ ]
#   constant  a version variable, type=Constant              version   hexagon     {{ }}
#   variable  a version variable, non-Constant type          version   rounded     ( )
#   custom    a __c / __r custom field or relationship        custom    cylinder    [( )]
#   std       a __std standard-context field                 standard  subroutine  [[ ]]
#   context   a bare context-supplied name (a tag/attribute  standard  stadium     ([ ])
#             the bound ContextDefinition provides — the ES
#             GET can't say tag-vs-attribute, so we don't)
#
# Each entry: (open-delim, close-delim, classDef-style). Order is stable so the
# emitted classDef block is deterministic.
_MERMAID_KINDS = {
    "step":     ("[",  "]",  "fill:#ffffff,stroke:#555555,color:#111111"),
    "constant": ("{{", "}}", "fill:#e7f5e7,stroke:#2e7d32,color:#1b5e20"),
    "variable": ("(",  ")",  "fill:#d5ead5,stroke:#2e7d32,color:#1b5e20"),
    "custom":   ("[(", ")]", "fill:#fdecea,stroke:#c62828,color:#b71c1c"),
    "std":      ("[[", "]]", "fill:#e8eef7,stroke:#1565c0,color:#0d47a1"),
    "context":  ("([", "])", "fill:#eef3fb,stroke:#1565c0,color:#0d47a1"),
}


def _mermaid_classdefs(kinds: Optional[List[str]] = None) -> List[str]:
    """The ``classDef`` lines for the given node kinds (default: all), stable order.

    Pass a subset (e.g. ``["step"]`` for the flow view, which has only step nodes)
    so the emitted legend matches the kinds actually present in the diagram.
    """
    wanted = kinds if kinds is not None else list(_MERMAID_KINDS)
    return [
        f"classDef {kind} {_MERMAID_KINDS[kind][2]};"
        for kind in _MERMAID_KINDS
        if kind in wanted
    ]


def _mermaid_node(nid: str, label: str, kind: str) -> str:
    """A Mermaid node-declaration line: id + kind-specific shape wrapping a quoted label."""
    open_d, close_d, _style = _MERMAID_KINDS.get(kind, _MERMAID_KINDS["context"])
    return f'  {nid}{open_d}"{_mermaid_escape(label)}"{close_d}'


def _mermaid_escape(label: str) -> str:
    """Make a human label safe inside a Mermaid ``["…"]`` quoted node.

    Only the double-quote needs escaping inside a quoted label (Mermaid reads the
    ``#quot;`` entity); ``<br/>`` and other markup are intentionally passed
    through so multi-line labels render.
    """
    return str(label).replace('"', "#quot;")


def _step_display(name: str, label: Optional[str]) -> str:
    """Node title for a step: readable ``label`` over the API ``name`` when they differ.

    With no label, or a label equal to the (spaceless) name — the fingerprint of a
    Connect-created / Connect-clobbered step, where the label carries no more
    information than the name — just show the name. Otherwise show the label on top
    with the API name small underneath, so the diagram stays traceable back to the
    definition. Mirrors ``describe --labels`` drift handling.
    """
    if label and label != name:
        return f"{label}<br/><small>{name}</small>"
    return name


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
        # name → the variable's declared ``type`` (e.g. "Constant"), for
        # node_kind()'s constant-vs-variable split. Untyped vars fall back to
        # the generic "variable" kind.
        self.variable_types: Dict[str, Optional[str]] = {
            v.get("name"): v.get("type")
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

    def node_kind(self, name: str) -> str:
        """Refine ``scope()`` into a display node-kind (a key of ``_MERMAID_KINDS``).

        A finer split than the three scopes, using only signals present in the
        Connect GET:
          * version  → ``constant`` if the variable's ``type`` is ``Constant``,
            else ``variable``.
          * custom   → ``custom`` (a ``__c`` / ``__r`` field or relationship).
          * standard → ``std`` if the name ends ``__std`` (a standard-context
            field), else ``context`` (a bare context-supplied tag/attribute — the
            GET does not distinguish tag from attribute, so neither do we).
        Never returns ``step`` — step nodes are labeled by the renderer, not by a
        referenced-name lookup.
        """
        sc = self.scope(name)
        if sc == SCOPE_VERSION:
            return "constant" if self.variable_types.get(name) == "Constant" else "variable"
        if sc == SCOPE_CUSTOM:
            return "custom"
        return "std" if isinstance(name, str) and name.endswith("__std") else "context"

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

    def _step_tree(self) -> "tuple[Dict[str, List[dict]], List[dict]]":
        """The parent→children map and top-level list, each sorted by sequenceNumber.

        The shared spine of both the flat ``ordered_steps()`` view and the nested
        ``to_mermaid_flow()`` render, so execution order is defined in exactly one
        place. ``children[parent_name]`` is that parent's children in per-parent
        sequenceNumber order; ``top`` is the ``parentStep is None`` steps in
        sequenceNumber order.
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
        return children, top

    def ordered_steps(self) -> List[dict]:
        """Steps in execution order as a FLAT list: top-level by sequenceNumber,
        each parent's children nested right after it.

        Matches ``describe_expression_set._order_steps``. Steps whose named parent
        is absent are appended last so nothing is dropped. (The nested-container
        form of this same order is what ``to_mermaid_flow`` draws.)
        """
        children, top = self._step_tree()
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

    def to_mermaid_flow(
        self, *, title: Optional[str] = None,
        labels: Optional[Dict[str, Optional[str]]] = None,
    ) -> str:
        """Execution-flow diagram: top-down, children NESTED inside their ListGroup.

        A top-down (``flowchart TD``) run-order view. Top-level steps are chained
        by solid arrows in ``sequenceNumber`` order. A step that has children (a
        ``ListGroup``) is drawn as a Mermaid ``subgraph`` **containing** its
        children — chained inside, in their own per-parent ``sequenceNumber``
        order — so the diagram shows containment, not just a relationship edge. The
        group's box participates in the top-level chain in the group's own sequence
        slot. Nesting is recursive: a ListGroup inside a ListGroup becomes a nested
        subgraph.

        Pass ``labels`` (``{step-name: label}`` from the Tooling API — see
        ``_tooling.step_labels``) to title each node/group with its readable label
        over the small API name. Pure — no org access; deterministic output.
        """
        labels = labels or {}
        step_ids = _MermaidIds("s_")
        group_ids = _MermaidIds("sg_")

        # Parent→children tree + top-level list, both in sequenceNumber order —
        # the same spine ordered_steps() flattens.
        children, top = self._step_tree()

        lines: List[str] = ["flowchart TD"]
        if title:
            lines.append(f'  %% {title}')

        seen: Set[str] = set()
        group_ids_emitted: List[str] = []

        def _label(step: dict, *, with_type: bool) -> str:
            name = step.get("name") or "(unnamed)"
            label = _step_display(name, labels.get(name))
            if with_type:
                stype = step.get("stepType") or step.get("actionType") or ""
                if stype:
                    label = f"{label}<br/><i>{stype}</i>"
            return label

        def emit(step: dict, indent: str) -> str:
            """Emit a step (recursively) and return the id to chain it by.

            A childless step → a ``step`` node (its own id). A step with children →
            a ``subgraph`` box containing the children chained in sequence order
            (the subgraph's id). Either id is what the parent chain arrows into.
            """
            name = step.get("name") or "(unnamed)"
            seen.add(name)
            kids = children.get(name)
            if kids:
                gid = group_ids.get(name)
                group_ids_emitted.append(gid)
                # Subgraph title carries the group label (its ListGroup nature is
                # already conveyed by the box), children stack top-to-bottom.
                lines.append(f'{indent}subgraph {gid}["{_mermaid_escape(_label(step, with_type=False))}"]')
                lines.append(f'{indent}  direction TB')
                prev: Optional[str] = None
                for kid in kids:
                    cid = emit(kid, indent + "  ")
                    if prev is not None:
                        lines.append(f'{indent}  {prev} --> {cid}')
                    prev = cid
                lines.append(f'{indent}end')
                return gid
            nid = step_ids.get(name)
            lines.append(f'{indent}{_mermaid_node(nid, _label(step, with_type=True), "step")}')
            lines.append(f'{indent}class {nid} step;')
            return nid

        prev_top: Optional[str] = None  # last top-level chain id, for run-order chain
        for s in top:
            cid = emit(s, "  ")
            if prev_top is not None:
                lines.append(f'  {prev_top} --> {cid}')
            prev_top = cid
        # Any step whose named parent never appeared — surface as top-level, don't drop.
        for s in self.steps:
            if s.get("name") not in seen:
                cid = emit(s, "  ")
                if prev_top is not None:
                    lines.append(f'  {prev_top} --> {cid}')
                prev_top = cid

        if not self.steps:
            lines.append("  empty[/no steps in this version/]")
        # Flow has only step nodes — emit just that classDef so the legend matches.
        lines.extend("  " + d for d in _mermaid_classdefs(["step"]))
        # Tint the ListGroup subgraph boxes so containment reads at a glance
        # (a `style` line, not a classDef — keeps the legend to the step kind).
        for gid in group_ids_emitted:
            lines.append(f"  style {gid} fill:#f4f0fb,stroke:#7e57c2,color:#3d2b6b;")
        return "\n".join(lines) + "\n"

    def to_mermaid_deps(
        self, *, only_steps: Optional[Set[str]] = None, title: Optional[str] = None,
        labels: Optional[Dict[str, Optional[str]]] = None,
    ) -> str:
        """Data-dependency diagram: producer → name → consumer, kind-shaped & colored.

        Steps are rectangles; every referenced name is drawn with a shape + color
        keyed to its ``node_kind`` — so the diagram distinguishes not just the
        three scopes but the kinds within them: version **constants** (hexagon,
        green) vs other version **variables** (rounded, green); **custom** fields
        (cylinder, red); standard **std** ``__std`` fields (subroutine, blue) vs
        bare **context** tags/attributes (stadium, blue). Edges carry the role
        symbol (``>`` producer→name, ``<`` / ``?`` / ``~`` name→consumer). Pass
        ``labels`` (``{step-name: label}``) to title step nodes with their readable
        Tooling label. Pass ``only_steps`` to scope the diagram to those steps plus
        the names they touch and the immediate neighbor steps on the other side of
        each name (the one-step neighborhood — what ``trace --step`` shows, drawn).
        Pure.
        """
        labels = labels or {}
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
            label = _step_display(name, labels.get(name))
            if focus:
                label = f"{label}<br/><b>◆ focus</b>"
            lines.append(_mermaid_node(nid, label, "step"))

        def _var_node(name: str):
            key = f"__var__{name}"
            if key in rendered:
                return
            rendered.add(key)
            var_names.append(name)
            vid = var_ids.get(name)
            lines.append(_mermaid_node(vid, name, self.node_kind(name)))

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

        # Class assignments: steps → step; names → their finer node_kind.
        present: Set[str] = {"step"} if step_names else set()
        for name in step_names:
            lines.append(f"  class {step_ids.get(name)} step;")
        for name in var_names:
            kind = self.node_kind(name)
            present.add(kind)
            lines.append(f"  class {var_ids.get(name)} {kind};")
        # Emit only the classDefs for kinds actually drawn, so the legend matches.
        lines.extend("  " + d for d in _mermaid_classdefs(sorted(present)))
        return "\n".join(lines) + "\n"
