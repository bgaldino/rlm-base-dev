"""Context Service tooling (standalone, CumulusCI-free; ``sf``-CLI transport).

Two families of entry-point scripts, split by what they operate on:

- ``definition/`` — **design-time** Context *Definition* metadata (nodes,
  attributes, tags, mappings): apply / diff / patch / export / mutate / delete /
  describe / list / trace / validate. Live-proven; use for one-off exploration
  and updates. (Org *build* still goes through the CCI task
  ``manage_context_definition`` — see ``tasks/rlm_context_service.py``.)
- ``instance/`` — **runtime** context *instances* (hydrate → query → persist →
  delete). Verify-live; caveats apply (``ContextServicePilot`` perm, which path
  to use, which fields are updatable). See ``runtime-and-persistence.md``.

Shared internals live at the package root as ``_*`` modules (``_client`` holds
the ``sf``-CLI transport, ``_payload``/``_model`` the pure payload libraries,
``_apply``/``_mutate``/``_delete`` the design-time orchestrators, ``_runtime``
the instance lifecycle). Entry scripts import them as
``from scripts.context_service._x import ...``.
"""
