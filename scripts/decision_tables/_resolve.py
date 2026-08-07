#!/usr/bin/env python3
"""Resolve Decision Table api-names to Tooling ids and load the definition graph.

All setup-object reads go through the **Tooling** surface (``_client.tooling_query``
/ ``tooling_sobject_request``) — the 5 Decision Table objects are Tooling-only.

Resolution model (live-verified 2026-07-09):

- ``DecisionTable.DeveloperName`` is the api name; ``Id`` (``0lD…``) is the key
  every child object foreign-keys to.
- A Tooling **GET of ``DecisionTable/{id}``** returns the ``Metadata``
  complexvalue with the parameters / dataset link / source criteria inlined —
  the cheapest full-definition read. The individual child objects
  (``DecisionTableParameter`` ``0lP``, ``DecisionTableDatasetLink`` ``0lX``,
  ``DecisionTblDatasetParameter`` ``0lZ``, ``DecisionTableSourceCriteria``
  ``0VT``) are queried separately when the caller needs record ids (e.g. a
  Phase-2 in-place child PATCH).

Functions take the bound :class:`_client.Transport` so they are unit-testable
against a fake transport, mirroring ``scripts/expression_sets/_resolve.py``.
"""

from typing import Any, Dict, List, Optional

from scripts.decision_tables import _client
from scripts.decision_tables._client import DecisionTableClientError, soql_literal


class ResolveError(RuntimeError):
    """A Decision Table (or child record) could not be resolved by the given key."""


# Columns pulled for the list / resolve views. Kept in sync with the
# live-verified DecisionTable Tooling describe field set.
_TABLE_COLUMNS = (
    "Id", "DeveloperName", "MasterLabel", "Status", "UsageType",
    "SourceObject", "LastSyncDate",
)
_PARAM_COLUMNS = (
    "Id", "DecisionTableId", "FieldName", "FieldPath", "Usage", "Operator",
    "Sequence", "DataType", "IsRequired", "IsGroupByField", "SortType", "DomainObject",
)
_DATASET_LINK_COLUMNS = (
    "Id", "DecisionTableId", "DeveloperName", "MasterLabel", "SetupName",
    "SourceObject", "IsDefault", "Description",
)
_DATASET_PARAM_COLUMNS = (
    "Id", "DecisionTableDatasetLinkId", "DecisionTableParameterId",
    "DatasetFieldName", "DatasetSourceObject",
)
_SOURCE_CRITERIA_COLUMNS = (
    "Id", "DecisionTableId", "SourceFieldName", "Operator", "Value",
    "ValueType", "SequenceNumber",
)


def _tooling(transport, query: str) -> List[Dict[str, Any]]:
    """Run a Tooling SOQL query through the bound transport."""
    return transport.tooling_query(query)


def list_decision_tables(
    transport,
    *,
    status: Optional[str] = None,
    usage_type: Optional[str] = None,
    developer_name: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Return ``DecisionTable`` rows (Tooling), optionally filtered.

    ``developer_name`` may be a single name or a comma-separated list. Ordering
    is DeveloperName ascending for a stable, groupable view.
    """
    where: List[str] = []
    if status:
        where.append(f"Status = '{soql_literal(status)}'")
    if usage_type:
        where.append(f"UsageType = '{soql_literal(usage_type)}'")
    if developer_name:
        names = [n.strip() for n in developer_name.split(",") if n.strip()]
        if names:
            quoted = ", ".join(f"'{soql_literal(n)}'" for n in names)
            where.append(f"DeveloperName IN ({quoted})")
    soql = f"SELECT {', '.join(_TABLE_COLUMNS)} FROM DecisionTable"
    if where:
        soql += " WHERE " + " AND ".join(where)
    soql += " ORDER BY DeveloperName ASC"
    if limit:
        soql += f" LIMIT {int(limit)}"
    return _tooling(transport, soql)


def resolve_decision_table(transport, developer_name: str) -> Dict[str, Any]:
    """DeveloperName → the ``DecisionTable`` summary row (Tooling). Raises if absent."""
    rows = _tooling(
        transport,
        f"SELECT {', '.join(_TABLE_COLUMNS)} FROM DecisionTable "
        f"WHERE DeveloperName = '{soql_literal(developer_name)}'",
    )
    if not rows:
        raise ResolveError(
            f"No DecisionTable found with DeveloperName '{developer_name}'. "
            f"List tables with list_decision_tables.py (names are case-sensitive)."
        )
    return rows[0]


def get_decision_table_metadata(transport, record_id: str) -> Dict[str, Any]:
    """Tooling GET of ``DecisionTable/{id}`` → the record incl. the ``Metadata``
    complexvalue (parameters / dataset link / source criteria inlined)."""
    resp = transport.tooling_sobject("GET", "DecisionTable", record_id)
    if not isinstance(resp, dict):
        raise ResolveError(f"Unexpected Tooling GET response for DecisionTable/{record_id}.")
    return resp


def list_parameters(transport, decision_table_id: str) -> List[Dict[str, Any]]:
    """The columns (``DecisionTableParameter`` ``0lP``) for a table, in sequence."""
    return _tooling(
        transport,
        f"SELECT {', '.join(_PARAM_COLUMNS)} FROM DecisionTableParameter "
        f"WHERE DecisionTableId = '{soql_literal(decision_table_id)}' "
        f"ORDER BY Usage, Sequence NULLS LAST",
    )


def list_dataset_links(transport, decision_table_id: str) -> List[Dict[str, Any]]:
    """Dataset links (``DecisionTableDatasetLink`` ``0lX``) for a MultipleSobjects table."""
    return _tooling(
        transport,
        f"SELECT {', '.join(_DATASET_LINK_COLUMNS)} FROM DecisionTableDatasetLink "
        f"WHERE DecisionTableId = '{soql_literal(decision_table_id)}'",
    )


def list_dataset_parameters(transport, dataset_link_ids: List[str]) -> List[Dict[str, Any]]:
    """Join layer (``DecisionTblDatasetParameter`` ``0lZ``) for the given links.

    Often empty — the join layer is only populated for certain multi-object
    configs (observed 0 rows on the probed orgs).
    """
    ids = [i for i in dataset_link_ids if i]
    if not ids:
        return []
    quoted = ", ".join(f"'{soql_literal(i)}'" for i in ids)
    return _tooling(
        transport,
        f"SELECT {', '.join(_DATASET_PARAM_COLUMNS)} FROM DecisionTblDatasetParameter "
        f"WHERE DecisionTableDatasetLinkId IN ({quoted})",
    )


def list_source_criteria(transport, decision_table_id: str) -> List[Dict[str, Any]]:
    """Row-filter criteria (``DecisionTableSourceCriteria`` ``0VT``, v59.0+) for a table."""
    return _tooling(
        transport,
        f"SELECT {', '.join(_SOURCE_CRITERIA_COLUMNS)} FROM DecisionTableSourceCriteria "
        f"WHERE DecisionTableId = '{soql_literal(decision_table_id)}' "
        f"ORDER BY SequenceNumber NULLS LAST",
    )


def load_definition(transport, developer_name: str, *, with_metadata: bool = True) -> Dict[str, Any]:
    """Assemble a full definition view for one table across the 5 setup objects.

    Returns a dict::

        {
          "table": {…summary row…},
          "metadata": {…Metadata complexvalue…} | None,
          "parameters": [ … ],
          "datasetLinks": [ … ],
          "datasetParameters": [ … ],
          "sourceCriteria": [ … ],
        }

    ``with_metadata=False`` skips the per-record Tooling GET (the columns/criteria
    child queries alone are enough for a structural diff and are cheaper).
    """
    table = resolve_decision_table(transport, developer_name)
    dt_id = table["Id"]
    dataset_links = list_dataset_links(transport, dt_id)
    metadata = None
    if with_metadata:
        record = get_decision_table_metadata(transport, dt_id)
        metadata = record.get("Metadata")
    return {
        "table": table,
        "metadata": metadata,
        "parameters": list_parameters(transport, dt_id),
        "datasetLinks": dataset_links,
        "datasetParameters": list_dataset_parameters(
            transport, [d.get("Id") for d in dataset_links]
        ),
        "sourceCriteria": list_source_criteria(transport, dt_id),
    }


def get_connect_definition(transport, record_id: str) -> Dict[str, Any]:
    """Connect Decision Table Definitions GET by-id → the ``decisionTable`` object.

    The by-id GET envelope is ``{"code":"200","decisionTable":{…}}``; this unwraps
    it. Connect uses a **different field vocabulary** (``sourceType``,
    ``decisionResultPolicy``, ``parameters``, title-case ``usage``) — see the
    reference doc's field-name divergence table. The collection endpoint is
    POST-only (no list-GET), so callers resolve the id via Tooling first.
    """
    resp = transport.connect_get(f"{_client.DEFINITIONS_PATH}/{record_id}")
    if isinstance(resp, dict) and isinstance(resp.get("decisionTable"), dict):
        return resp["decisionTable"]
    if isinstance(resp, dict):
        return resp
    raise ResolveError(
        f"Unexpected Connect Definitions GET response for id '{record_id}'."
    )
