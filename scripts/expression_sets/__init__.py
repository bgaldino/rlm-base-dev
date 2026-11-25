"""Expression Set tooling (standalone, CumulusCI-free; ``sf``-CLI transport).

A self-contained, full-lifecycle toolkit for BRE Expression Sets (pricing /
discovery / rating / qualification procedures and constraint rules). It covers
the whole lifecycle — inspect, export, trace, diff, and the guarded
create/replace/overlay/activate/delete mutators — on the ``sf`` CLI transport,
so **no access token is ever handled or passed** (``--target-org`` is the *SF
CLI* alias, e.g. ``rlm-base__beta``, never the CCI alias).

Runs without CumulusCI. This package imports **nothing** from ``tasks/``; the
toolkit is its own program over the ``sf`` CLI. The deactivate → mutate → recover
state machine (``_engine``) and the version guards (``_guards``) are shared: the CCI
task ``tasks/rlm_expression_set_connect.py`` imports both (they are stdlib-only),
so the two surfaces run the same lifecycle code. Everything else is separate; the
validator is *vendored* here as ``_schema.py`` (a mirror of
``tasks/expression_set_schema.py``) rather than imported.

Shared internals live at the package root as ``_*`` modules:

- ``_client``    — the ``sf``-CLI transport (``Transport`` seam + request/SOQL fns)
- ``_resolve``   — api-name → ExpressionSet / ExpressionSetDefinition / version ids
- ``_guards``    — pure version guards (executing version, multi-version import rule)
- ``_schema``    — vendored validator + enums (mirror of the task's copy)
- ``_payload``   — verb-specific field rules + HTML-entity normalization (pure)
- ``_overlay``   — declarative step/variable merge (pure)
- ``_graph``     — producer/consumer dependency graph + 3-scope classifier (pure)
- ``_engine``    — the shared deactivate → mutate → recover state machine (``LifecycleCore``)
- ``_lifecycle`` — the toolkit's adapter over it (``LifecycleEngine``, ``Transport`` seam)

Entry scripts import them as ``from scripts.expression_sets._x import ...`` after
adding the repo root to ``sys.path`` (so a direct ``python scripts/...`` run
resolves the package). This is **not** wired into ``cumulusci.yml`` or any flow.
"""
