#!/usr/bin/env python3
"""Neutral, read-only Context Definition / mapping resolution helpers.

Shared resolution logic that both the design-time apply path and the runtime
instance path need: turn a ``developerName`` into a ``contextDefinitionId``,
fetch a definition's detail, and pick a **context mapping** (default or by name)
off its active version. These are pure reads built directly on ``_client``
(GET + the shared normalizers) — **no** ``Transport`` and **no** dependency on
``_apply`` orchestration internals, so ``_runtime`` can consume them without
pulling in the whole apply sequencer.

Auth is delegated entirely to the ``sf`` CLI (see ``_client``) — no access token
is ever handled. ``target_org`` is the **SF CLI** alias (e.g. ``rlm-base__beta``),
never the CCI alias.

Mapping ids matter for the runtime lifecycle: create needs a *source* mapping
(hydration) and persist needs a *target* mapping (persistence); both are
``ContextMapping`` ids (prefix ``11j``) selected here by ``isDefault`` or by name.
"""

from typing import Any, Dict, List, Optional, Tuple

from . import _client
from . import _endpoints as ep


def resolve_definition_id(
    developer_name: str, *, target_org: str, api_version: str = _client.DEFAULT_API_VERSION
) -> Optional[str]:
    """Resolve a ``contextDefinitionId`` from a ``developerName`` (read-only).

    Lists definitions with ``includeInactive=true`` (so an inactive definition
    still resolves) and matches on ``developerName`` via the shared normalizer /
    name reader — the same path ``describe_context._resolve_id`` and
    ``ContextApplier.resolve_definition_id`` use, so all three see the same set.
    Returns ``None`` when no definition matches.
    """
    response = _client.connect_get(
        f"{ep.DEFINITION_COLLECTION}?includeInactive=true", target_org, api_version
    )
    for item in _client.normalize_definition_list(response):
        if _client.definition_developer_name(item) == developer_name:
            return item.get("contextDefinitionId") or item.get("id")
    return None


def fetch_detail(
    context_definition_id: str,
    *,
    target_org: str,
    api_version: str = _client.DEFAULT_API_VERSION,
) -> Dict[str, Any]:
    """GET one definition's full detail (version → nodes → mappings → hydration).

    Tolerates the list-wrapper the item endpoint occasionally returns.
    """
    resp = _client.connect_get(
        ep.DEFINITION_ITEM.format(context_definition_id=context_definition_id),
        target_org,
        api_version,
    )
    if isinstance(resp, list):
        return resp[0] if len(resp) == 1 and isinstance(resp[0], dict) else {}
    return resp if isinstance(resp, dict) else {}


def iter_context_mappings(detail: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return the contextMapping dicts on the **active** version of a detail.

    Uses ``_client.active_version`` (prefers the ``isActive`` version, not just
    the first) so a resolved mapping id belongs to the version that will actually
    hydrate at runtime.
    """
    version = _client.active_version(detail)
    mappings = version.get("contextMappings") if isinstance(version, dict) else None
    return [m for m in (mappings or []) if isinstance(m, dict)]


def _mapping_id(mapping: Dict[str, Any]) -> Optional[str]:
    return mapping.get("contextMappingId") or mapping.get("id")


def default_mapping_id(detail: Dict[str, Any]) -> Optional[str]:
    """Return the id of the ``isDefault`` context mapping, or ``None``."""
    for mapping in iter_context_mappings(detail):
        if mapping.get("isDefault") in (True, "true"):
            return _mapping_id(mapping)
    return None


def mapping_id_by_name(detail: Dict[str, Any], name: str) -> Optional[str]:
    """Return the id of the context mapping named ``name``, or ``None``."""
    for mapping in iter_context_mappings(detail):
        if mapping.get("name") == name:
            return _mapping_id(mapping)
    return None


def mapping_names(detail: Dict[str, Any]) -> List[str]:
    """Return every context mapping name on the active version (for error text)."""
    return [m.get("name") for m in iter_context_mappings(detail) if m.get("name")]


def resolve_mapping(
    detail: Dict[str, Any], mapping_name: Optional[str] = None
) -> Tuple[str, str]:
    """Resolve ``(contextDefinitionId, contextMappingId)`` from a fetched detail.

    With ``mapping_name`` omitted, selects the definition's **default** mapping;
    with a name, selects that mapping. Raises ``ValueError`` when the detail has
    no definition id, no default mapping, or an unknown mapping name — the caller
    turns that into an exit-2 config error.
    """
    context_definition_id = detail.get("contextDefinitionId") or detail.get("id")
    if not context_definition_id:
        raise ValueError("Definition detail is missing a contextDefinitionId.")

    if mapping_name:
        mapping_id = mapping_id_by_name(detail, mapping_name)
        if not mapping_id:
            available = ", ".join(sorted(mapping_names(detail))) or "(none)"
            raise ValueError(
                f"No context mapping named '{mapping_name}' on the active version. "
                f"Available mappings: {available}."
            )
        return context_definition_id, mapping_id

    mapping_id = default_mapping_id(detail)
    if not mapping_id:
        available = ", ".join(sorted(mapping_names(detail))) or "(none)"
        raise ValueError(
            "No default context mapping on the active version; pass an explicit "
            f"mapping name. Available mappings: {available}."
        )
    return context_definition_id, mapping_id
