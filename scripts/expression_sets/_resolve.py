#!/usr/bin/env python3
"""Read-only Expression Set resolution helpers (sf-CLI transport).

Turn an expression-set ``DeveloperName`` into the ids the Connect API and the
version-lifecycle SObjects need: the runtime ``ExpressionSet`` Id (prefix
``9QL``, what the Connect resource is keyed by), the tooling
``ExpressionSetDefinition`` Id (prefix ``9QA``, what procedure-plan references
point at), and the ``ExpressionSetVersion`` (the source of truth for a version's
Id / ApiName / IsActive).

These reuse the EXACT resolution SOQL and "prefer active version" ordering from
``ExpressionSetConnectBase`` in ``tasks/rlm_expression_set_connect.py`` so the
CLIs and the task resolve the same records. Pure reads on ``_client`` — no
transport state beyond the ``target_org`` / ``api_version`` args.
"""

from typing import Any, Dict, List, Optional

from . import _client
from ._guards import (
    VERSION_FIELDS,
    executing_version,
    rank_order_warning,
    target_version_warning,
)


class ResolveError(RuntimeError):
    """Raised when an expression set / version cannot be resolved in the org."""


def _query(soql: str, *, target_org: str, api_version: str) -> List[Dict[str, Any]]:
    return _client.soql_query(soql, target_org=target_org, api_version=api_version)


def resolve_definition_id(
    api_name: str, *, target_org: str, api_version: str = _client.DEFAULT_API_VERSION
) -> str:
    """Resolve the tooling ``ExpressionSetDefinition`` Id (prefix 9QA)."""
    safe = _client.soql_literal(api_name)
    records = _query(
        f"SELECT Id FROM ExpressionSetDefinition WHERE DeveloperName = '{safe}'",
        target_org=target_org, api_version=api_version,
    )
    if not records:
        raise ResolveError(f"ExpressionSetDefinition '{api_name}' not found in org.")
    return records[0]["Id"]


def resolve_expression_set_id(
    api_name: str, *, target_org: str, api_version: str = _client.DEFAULT_API_VERSION
) -> str:
    """Resolve the runtime ``ExpressionSet`` Id (prefix 9QL) the Connect API uses."""
    safe = _client.soql_literal(api_name)
    records = _query(
        "SELECT Id FROM ExpressionSet "
        f"WHERE ExpressionSetDefinition.DeveloperName = '{safe}'",
        target_org=target_org, api_version=api_version,
    )
    if not records:
        raise ResolveError(f"ExpressionSet for '{api_name}' not found in org.")
    return records[0]["Id"]


def resolve_definition_id_by_es_id(
    es_id: str, *, target_org: str, api_version: str = _client.DEFAULT_API_VERSION
) -> str:
    """Resolve the tooling ``ExpressionSetDefinition`` Id (9QA) from a runtime
    ``ExpressionSet`` Id (9QL).

    The 9QA is the **stable** key for the Tooling ``ExpressionSetDefinitionVersion``
    (see ``_tooling.resolve_esdv``): unlike the ESDV ``DeveloperName`` (rewritten in
    place by a Connect PATCH), ``ExpressionSet.ExpressionSetDefinitionId`` survives.
    Read-only callers that hold only the 9QL (``describe`` / ``trace`` invoked with
    ``--expression-set-id``) use this to pin a label read to the right definition.
    """
    safe = _client.soql_literal(es_id)
    records = _query(
        f"SELECT ExpressionSetDefinitionId FROM ExpressionSet WHERE Id = '{safe}'",
        target_org=target_org, api_version=api_version,
    )
    if not records or not records[0].get("ExpressionSetDefinitionId"):
        raise ResolveError(
            f"ExpressionSetDefinition Id not found for ExpressionSet {es_id}."
        )
    return records[0]["ExpressionSetDefinitionId"]


def resolve_version_by_es_id(
    es_id: str, *, target_org: str, api_version: str = _client.DEFAULT_API_VERSION,
    logger=None,
) -> Dict[str, Any]:
    """Resolve the ``ExpressionSetVersion`` from the ExpressionSet Id.

    Prefers the version actually executing (``_guards.executing_version``: the
    highest Rank among active versions whose date window covers now) over a merely
    higher-numbered draft — mutating the wrong version would target a record that
    isn't live. Absent an executing version, the active (then highest-numbered)
    version comes first.
    """
    log = logger or _client.eprint
    safe = _client.soql_literal(es_id)
    records = _query(
        f"SELECT {VERSION_FIELDS} "
        f"FROM ExpressionSetVersion WHERE ExpressionSetId = '{safe}' "
        "ORDER BY IsActive DESC, VersionNumber DESC",
        target_org=target_org, api_version=api_version,
    )
    if not records:
        raise ResolveError(f"No ExpressionSetVersion found for ExpressionSet {es_id}.")
    try:
        running = executing_version(records)
        note = rank_order_warning(records)
    except ValueError as exc:  # an unreadable StartDateTime/EndDateTime
        raise ResolveError(str(exc)) from exc
    chosen = running or records[0]
    active = [r for r in records if r.get("IsActive")]
    message = target_version_warning(es_id, active, running, chosen)
    if message:
        log(f"WARNING: {message}")
        if note:
            log(f"WARNING: {note}")
    return chosen


def resolve_target_row(
    es_id: str, version_api_name: Optional[str] = None, *, target_org: str,
    api_version: str = _client.DEFAULT_API_VERSION, logger=None,
) -> Dict[str, Any]:
    """The ``ExpressionSetVersion`` row a read tool works on: the one named by
    ``version_api_name``, else the executing one (:func:`resolve_version_by_es_id`),
    never the Connect GET's first. Pair it with ``_guards.select_version`` to find
    the GET's block by VersionNumber. A name with no sObject row is returned as
    ``{"ApiName": name}`` so a GET-only (stale clone) name still matches by name."""
    if not version_api_name:
        return resolve_version_by_es_id(es_id, target_org=target_org,
                                        api_version=api_version, logger=logger)
    rows = [r for r in list_versions(es_id, target_org=target_org,
                                     api_version=api_version)
            if r.get("ApiName") == version_api_name]
    return rows[0] if rows else {"ApiName": version_api_name}


def list_expression_sets(
    *, target_org: str, api_version: str = _client.DEFAULT_API_VERSION,
    developer_name: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return one row per ExpressionSet: DeveloperName, interfaceSourceType,
    usageType, active-version info.

    ``interfaceSourceType`` / ``usageType`` live on the runtime ``ExpressionSet``
    (NOT the tooling ``ExpressionSetDefinition``) — this is the query that
    surfaces the Revenue Cloud type taxonomy. Optional ``developer_name`` filters
    to one set.
    """
    where = ""
    if developer_name:
        where = (
            "WHERE ExpressionSetDefinition.DeveloperName = "
            f"'{_client.soql_literal(developer_name)}'"
        )
    rows = _query(
        "SELECT Id, ExpressionSetDefinition.DeveloperName, InterfaceSourceType, "
        "UsageType, UsageSubtype FROM ExpressionSet "
        f"{where} ORDER BY ExpressionSetDefinition.DeveloperName",
        target_org=target_org, api_version=api_version,
    )
    result = []
    for r in rows:
        esd = r.get("ExpressionSetDefinition") or {}
        result.append({
            "id": r.get("Id"),
            "developerName": esd.get("DeveloperName"),
            "interfaceSourceType": r.get("InterfaceSourceType"),
            "usageType": r.get("UsageType"),
            "usageSubtype": r.get("UsageSubtype"),
        })
    return result


def list_versions(
    es_id: str, *, target_org: str, api_version: str = _client.DEFAULT_API_VERSION
) -> List[Dict[str, Any]]:
    """All ExpressionSetVersion rows for an ExpressionSet (active first), with the
    fields ``_guards.executing_version`` needs (Rank and the date window)."""
    safe = _client.soql_literal(es_id)
    return _query(
        f"SELECT {VERSION_FIELDS} FROM ExpressionSetVersion "
        f"WHERE ExpressionSetId = '{safe}' ORDER BY IsActive DESC, VersionNumber DESC",
        target_org=target_org, api_version=api_version,
    )
