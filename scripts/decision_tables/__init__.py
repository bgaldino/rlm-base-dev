"""Decision Table tooling (standalone, CumulusCI-free; ``sf``-CLI transport).

A self-contained toolkit for Salesforce Revenue Cloud **BRE Decision Tables** —
the *definition* (columns + source binding + hit policy) and its *data/refresh*
lifecycle. Phase 1 ships the **read-only inspectors** (list / describe / diff /
trace / dump); Phase 2 adds the guarded lifecycle **mutators**
(create/update/activate/deactivate/refresh/delete), preview-by-default and
``--confirm`` to write.

Auth is delegated to the ``sf`` CLI (``sf api request rest --target-org …``), so
**no access token is ever handled or passed**. ``--target-org`` is always the
*SF CLI* alias (e.g. ``rlm-base__beta``), **never** the CCI alias. Pinned to
Release 262 / API v67.0.

INDEPENDENT of the CCI tasks. This package imports **nothing** from ``tasks/``
and nothing under ``tasks/`` imports from it. The CCI tasks
(``tasks/rlm_manage_decision_tables.py``, ``tasks/rlm_refresh_decision_table.py``)
remain the **org-build path**; this toolkit adds ad-hoc inspection and (Phase 2)
lifecycle control that mirror the same live-verified platform rules but run as
their own program.

Transport note — the 5 Decision Table setup objects (``DecisionTable``,
``DecisionTableParameter``, ``DecisionTableDatasetLink``,
``DecisionTblDatasetParameter``, ``DecisionTableSourceCriteria``) are **Tooling
API** objects, not on the normal REST ``/sobjects`` surface. ``_client`` exposes
distinct Tooling helpers (``tooling_query`` / ``tooling_sobject_request``)
alongside the Connect (``connect_request``/``connect_get``) and normal-REST
(``sobjects_request``/``soql_query``) helpers. Reads that hit
``PricingRecipeTableMapping`` and source-object row dumps use normal REST.

Shared internals live at the package root as ``_*`` modules:

- ``_client``    — the ``sf``-CLI transport (``Transport`` seam + Tooling/Connect/REST fns)
- ``_resolve``   — DeveloperName → ``DecisionTable`` id + child resolution via Tooling
- ``_schema``    — enum/field catalogs + canonical-spec validation (pure)

Entry scripts import them as ``from scripts.decision_tables._x import ...`` after
adding the repo root to ``sys.path``. This is **not** wired into ``cumulusci.yml``
or any flow.

Full guidance lives in the **decision-tables skill**
(``.cursor/skills/decision-tables/SKILL.md`` + ``authoring-and-data-model.md``,
``lifecycle-and-refresh.md``) with the object/ID/enum/error reference in
``docs/references/decision-table-api-reference.md``.
"""
