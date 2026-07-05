"""Expression Set tooling (standalone, CumulusCI-free; ``sf``-CLI transport).

A self-contained, full-lifecycle toolkit for BRE Expression Sets (pricing /
discovery / rating / qualification procedures and constraint rules). It covers
the whole lifecycle — inspect, export, trace, diff, and the guarded
create/replace/overlay/activate/delete mutators — on the ``sf`` CLI transport,
so **no access token is ever handled or passed** (``--target-org`` is the *SF
CLI* alias, e.g. ``rlm-base__july4_ctxPilot``, never the CCI alias).

INDEPENDENT of the CCI tasks. This package imports **nothing** from ``tasks/``
and nothing under ``tasks/`` imports from it. The CCI task
``tasks/rlm_expression_set_connect.py`` (and ``tasks/expression_set_schema.py``)
is **reference-only**: this toolkit mirrors its live-verified Connect/lifecycle
rules but runs as its own program. The validator is therefore *vendored* here as
``_schema.py`` rather than imported (the task imports the canonical copy, and a
CLI must not share an import with a CCI task).

Shared internals live at the package root as ``_*`` modules:

- ``_client``    — the ``sf``-CLI transport (``Transport`` seam + request/SOQL fns)
- ``_resolve``   — api-name → ExpressionSet / ExpressionSetDefinition / version ids
- ``_schema``    — vendored validator + enums (mirror of the task's copy)
- ``_payload``   — verb-specific field rules + HTML-entity normalization (pure)
- ``_overlay``   — declarative step/variable merge (pure)
- ``_graph``     — producer/consumer dependency graph + 3-scope classifier (pure)
- ``_lifecycle`` — the deactivate → mutate → reactivate engine + procedure-plan cascade

Entry scripts import them as ``from scripts.expression_sets._x import ...`` after
adding the repo root to ``sys.path`` (so a direct ``python scripts/...`` run
resolves the package). This is **not** wired into ``cumulusci.yml`` or any flow.
"""
