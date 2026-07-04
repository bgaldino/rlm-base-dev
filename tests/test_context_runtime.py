#!/usr/bin/env python3
"""Unit tests for the runtime Context Service modules (_runtime, _resolve).

Self-contained — no pytest (matches this repo's lightweight test convention; see
tests/test_context_payload.py). Run from the repo root with base Python:

    python tests/test_context_runtime.py

Exits 0 when all checks pass, 1 otherwise.

Coverage: the pure body-builders and query-result shaping in ``_runtime`` (no
network), the ``_resolve`` mapping selection, the hydration skeleton, and the
``RuntimeSession`` dry-run contract — the last exercised through a
``FakeTransport`` that records every call as ``(method, path, body, dry_run)`` and
returns canned responses, so no org is touched.
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts", "context_service"))

import _runtime  # noqa: E402
import _resolve  # noqa: E402
import list_context_interfaces as lci  # noqa: E402

RESULTS = []


def check(name, condition):
    RESULTS.append((name, bool(condition)))
    print(f"  [{'PASS' if condition else 'FAIL'}] {name}")


# --------------------------------------------------------------------------- #
# FakeTransport — records calls, mirrors _apply.Transport.request signature
# --------------------------------------------------------------------------- #

class FakeTransport:
    """Mirror of _apply.Transport for offline tests.

    ``dry_run`` is the bound session flag; ``request`` honors a per-call override
    (``dry_run=None`` inherits, matching the real transport). Records every call;
    ``responses`` maps a path substring → canned return value.
    """

    def __init__(self, dry_run=False, responses=None):
        self.dry_run = dry_run
        self.logger = lambda *a, **k: None
        self.calls = []
        self.responses = responses or {}

    def request(self, method, path, body=None, *, dry_run=None):
        effective = self.dry_run if dry_run is None else dry_run
        self.calls.append((method, path, body, effective))
        if effective and method not in ("GET", "HEAD"):
            return {}  # transport-layer mutation skip
        for needle, resp in self.responses.items():
            if needle in path:
                return resp
        return {}

    def sobject(self, method, sobject, record_id=None, body=None, *, dry_run=None):
        effective = self.dry_run if dry_run is None else dry_run
        self.calls.append((method, f"sobjects/{sobject}", body, effective))
        return {}

    def soql(self, query):
        return []


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #

def _detail_with_mappings():
    """A minimal definition detail: one active version, two mappings + nodes."""
    return {
        "contextDefinitionId": "11O000000000001",
        "isActive": True,
        "contextDefinitionVersionList": [
            {
                "isActive": True,
                "contextNodes": [
                    {
                        "name": "Order",
                        "contextNodeId": "11o1",
                        "attributes": [
                            {"name": "Name", "dataType": "STRING"},
                            {"name": "TotalAmount", "dataType": "CURRENCY"},
                            {"name": "IsActive", "dataType": "BOOLEAN"},
                        ],
                        "childNodes": [
                            {
                                "name": "OrderItem",
                                "contextNodeId": "11o2",
                                "attributes": [
                                    {"name": "Quantity", "dataType": "NUMBER"},
                                ],
                                "childNodes": [],
                            }
                        ],
                    }
                ],
                "contextMappings": [
                    {
                        "name": "SalesMapping",
                        "contextMappingId": "11j0001",
                        "isDefault": True,
                        # Node → SObject binding: the node name ("Order") differs
                        # from the mapped SObject ("SalesOrder"); hydration keys on
                        # the SObject name, so the skeleton must emit it.
                        "contextNodeMappings": [
                            {"contextNodeName": "Order", "sObjectName": "SalesOrder"},
                            {"contextNodeName": "OrderItem", "sObjectName": "SalesOrderItem"},
                        ],
                    },
                    {"name": "QuoteMapping", "contextMappingId": "11j0002", "isDefault": False},
                ],
            }
        ],
    }


# --------------------------------------------------------------------------- #
# _resolve — mapping selection
# --------------------------------------------------------------------------- #

def test_resolve_mapping_default():
    detail = _detail_with_mappings()
    def_id, mapping_id = _resolve.resolve_mapping(detail)
    check("default mapping resolves to the isDefault id",
          def_id == "11O000000000001" and mapping_id == "11j0001")


def test_resolve_mapping_by_name():
    detail = _detail_with_mappings()
    _def_id, mapping_id = _resolve.resolve_mapping(detail, "QuoteMapping")
    check("named mapping resolves to the right id", mapping_id == "11j0002")


def test_resolve_mapping_unknown_name_raises():
    detail = _detail_with_mappings()
    try:
        _resolve.resolve_mapping(detail, "NoSuchMapping")
        check("unknown mapping name raises ValueError", False)
    except ValueError as exc:
        check("unknown mapping name raises ValueError", True)
        check("error lists the available mappings",
              "SalesMapping" in str(exc) and "QuoteMapping" in str(exc))


def test_resolve_mapping_no_default_raises():
    detail = _detail_with_mappings()
    for m in detail["contextDefinitionVersionList"][0]["contextMappings"]:
        m["isDefault"] = False
    try:
        _resolve.resolve_mapping(detail)
        check("missing default mapping raises ValueError", False)
    except ValueError:
        check("missing default mapping raises ValueError", True)


# --------------------------------------------------------------------------- #
# _runtime — pure body-builders
# --------------------------------------------------------------------------- #

def test_create_metadata_omits_tagged_data_when_unset():
    md = _runtime.build_create_metadata("11O1", "11j1")
    check("create metadata carries def + mapping ids",
          md == {"contextDefinitionId": "11O1", "mappingId": "11j1"})
    check("taggedData omitted when unset", "taggedData" not in md)


def test_create_metadata_includes_tagged_data_when_set():
    md = _runtime.build_create_metadata("11O1", "11j1", tagged_data=True)
    check("taggedData included when set", md.get("taggedData") is True)


def test_stringify_data_produces_json_string():
    s = _runtime.stringify_data({"Order": [{"id": "1", "businessObjectType": "Order"}]})
    check("stringify_data returns a str", isinstance(s, str))
    import json as _json
    check("stringify_data round-trips", _json.loads(s)["Order"][0]["id"] == "1")


def test_stringify_data_passes_through_existing_string():
    check("stringify_data trusts a pre-stringified str",
          _runtime.stringify_data('{"a":1}') == '{"a":1}')


def test_create_body_shape():
    body = _runtime.build_create_body("11O1", "11j1", {"Order": []})
    check("create body has metadata + data keys",
          set(body.keys()) == {"metadata", "data"})
    check("create body data is a stringified JSON string",
          isinstance(body["data"], str) and body["data"].startswith("{"))


def test_update_attributes_body_shape():
    body = _runtime.build_update_attributes_body(
        "CID", [{"dataPath": ["Order"], "attributes": [
            {"attributeName": "RampMode__c", "attributeValue": "RAMP"}]}]
    )
    inp = body["updateContextAttributesInput"]
    check("update-attrs body has the envelope + contextId",
          inp["contextId"] == "CID")
    entry = inp["nodePathAndAttributes"][0]
    check("update-attrs nodePath.dataPath preserved",
          entry["nodePath"]["dataPath"] == ["Order"])
    check("update-attrs attribute name/value shape",
          entry["attributes"][0] == {"attributeName": "RampMode__c", "attributeValue": "RAMP"})


def test_write_tags_body_shape():
    body = _runtime.build_write_tags_body(
        "CID", [{"dataPath": [], "tagValues": [
            {"tagName": "PriceTag", "tagValue": "9.99"}]}]
    )
    check("write-tags body carries contextId", body["contextId"] == "CID")
    entry = body["nodePathAndTagValues"][0]
    check("write-tags root dataPath is empty list", entry["nodePath"]["dataPath"] == [])
    check("write-tags tagName/tagValue shape",
          entry["tagValues"][0] == {"tagName": "PriceTag", "tagValue": "9.99"})


def test_persist_body_shape():
    body = _runtime.build_persist_body("CID", "11j0002")
    check("persist body envelope shape",
          body == {"contextPersistInput": {"contextId": "CID", "targetMappingId": "11j0002"}})


def test_query_record_body_omits_empty_optionals():
    body = _runtime.build_query_record_body("CID")
    check("query-record body carries only contextId when no optionals",
          body == {"contextId": "CID"})
    body2 = _runtime.build_query_record_body("CID", attributes=["A"], query_path=["Order"])
    check("query-record includes non-empty optionals",
          body2["attributes"] == ["A"] and body2["queryPath"] == ["Order"])


def test_query_tags_body_shape():
    check("query-tags body shape",
          _runtime.build_query_tags_body("CID", ["T1", "T2"])
          == {"contextId": "CID", "tags": ["T1", "T2"]})


# --------------------------------------------------------------------------- #
# _runtime — query-result shaping
# --------------------------------------------------------------------------- #

def test_flatten_query_records_depth():
    result = {
        "queryRecords": [
            {"businessObjectType": "Order", "id": "o1", "childQueryRecords": [
                {"businessObjectType": "OrderItem", "id": "i1", "childQueryRecords": []},
                {"businessObjectType": "OrderItem", "id": "i2"},
            ]},
        ]
    }
    rows = _runtime.flatten_query_records(result)
    check("flatten yields all records", len(rows) == 3)
    check("root row has depth 0", rows[0]["depth"] == 0 and rows[0]["id"] == "o1")
    check("child rows have depth 1", rows[1]["depth"] == 1 and rows[2]["depth"] == 1)
    check("flatten strips childQueryRecords from rows",
          all("childQueryRecords" not in r for r in rows))


def test_decode_compound_fields_parses_stringified():
    record = {"attributesAndValues": {
        "ShippingAddress": '{"city":"SF","state":"CA"}',
        "Name": "Acme",
    }}
    decoded = _runtime.decode_compound_fields(record)
    check("stringified compound value is parsed to a dict",
          decoded["attributesAndValues"]["ShippingAddress"] == {"city": "SF", "state": "CA"})
    check("scalar value is left untouched",
          decoded["attributesAndValues"]["Name"] == "Acme")


def test_decode_compound_fields_leaves_unparseable_raw():
    record = {"attributesAndValues": {"Weird": "{not json"}}
    decoded = _runtime.decode_compound_fields(record)
    check("unparseable pseudo-JSON is left raw",
          decoded["attributesAndValues"]["Weird"] == "{not json")


# --------------------------------------------------------------------------- #
# _runtime — hydration skeleton
# --------------------------------------------------------------------------- #

def test_hydration_skeleton_full_tree():
    skeleton = _runtime.build_hydration_skeleton(_detail_with_mappings())
    check("skeleton keyed by top node name", list(skeleton.keys()) == ["Order"])
    rec = skeleton["Order"][0]
    check("record carries businessObjectType", rec["businessObjectType"] == "Order")
    check("record carries an id placeholder", rec["id"] == "")
    check("string attr placeholder is empty string", rec["Name"] == "")
    check("currency attr placeholder is 0", rec["TotalAmount"] == 0)
    check("boolean attr placeholder is False", rec["IsActive"] is False)
    check("child node is a nested array", isinstance(rec["OrderItem"], list))
    child = rec["OrderItem"][0]
    check("child record carries its businessObjectType + attrs",
          child["businessObjectType"] == "OrderItem" and child["Quantity"] == 0)


def test_hydration_skeleton_node_filter():
    skeleton = _runtime.build_hydration_skeleton(
        _detail_with_mappings(), node_filter=["OrderItem"]
    )
    check("node filter surfaces the requested subtree as top-level",
          list(skeleton.keys()) == ["OrderItem"])
    check("filtered record has the child's attrs",
          skeleton["OrderItem"][0]["Quantity"] == 0)


def test_node_sobject_lookup_from_mapping():
    detail = _detail_with_mappings()
    mapping = detail["contextDefinitionVersionList"][0]["contextMappings"][0]
    lookup = _runtime.node_sobject_lookup(mapping)
    check("node→SObject lookup maps node name to mapped SObject",
          lookup == {"Order": "SalesOrder", "OrderItem": "SalesOrderItem"})
    check("node_sobject_lookup tolerates None mapping",
          _runtime.node_sobject_lookup(None) == {})
    check("node_sobject_lookup tolerates a mapping with no node mappings",
          _runtime.node_sobject_lookup({"name": "X"}) == {})


def test_hydration_skeleton_uses_mapped_sobject_name():
    # THE live-verified fix: businessObjectType must be the mapped SObject name
    # (e.g. Quote/SalesOrder), NOT the context node name — a node-name
    # businessObjectType hydrates zero records.
    detail = _detail_with_mappings()
    mapping = detail["contextDefinitionVersionList"][0]["contextMappings"][0]
    skeleton = _runtime.build_hydration_skeleton(detail, mapping=mapping)
    rec = skeleton["Order"][0]
    check("array key stays the node name", list(skeleton.keys()) == ["Order"])
    check("businessObjectType is the mapped SObject, not the node name",
          rec["businessObjectType"] == "SalesOrder")
    child = rec["OrderItem"][0]
    check("child businessObjectType is the child's mapped SObject",
          child["businessObjectType"] == "SalesOrderItem")
    check("child array key stays the child node name", "OrderItem" in rec)


def test_hydration_skeleton_falls_back_to_node_name_without_mapping():
    # No mapping (or a node absent from the mapping) → node name, documented as
    # non-hydrating; build_hydration_data.py always resolves a mapping.
    detail = _detail_with_mappings()
    skeleton = _runtime.build_hydration_skeleton(detail)  # no mapping
    check("no-mapping skeleton falls back to node name for businessObjectType",
          skeleton["Order"][0]["businessObjectType"] == "Order")


# --------------------------------------------------------------------------- #
# _runtime — build_from_record_skeleton (id-only, --from-record)
# --------------------------------------------------------------------------- #

def test_from_record_skeleton_is_id_only_with_mapped_sobject():
    # id-only payload: just id + mapped businessObjectType, no placeholders, no
    # child arrays — the runtime hydrates children server-side (live-verified).
    detail = _detail_with_mappings()
    mapping = detail["contextDefinitionVersionList"][0]["contextMappings"][0]
    skeleton, err = _runtime.build_from_record_skeleton(
        detail, root_id="0Q0xxx", mapping=mapping
    )
    check("from-record returns no error for a single-top-node def", err is None)
    check("from-record keyed by the node name", list(skeleton.keys()) == ["Order"])
    rec = skeleton["Order"][0]
    check("from-record record has exactly id + businessObjectType",
          set(rec.keys()) == {"id", "businessObjectType"})
    check("from-record id is the supplied root id", rec["id"] == "0Q0xxx")
    check("from-record businessObjectType is the mapped SObject name",
          rec["businessObjectType"] == "SalesOrder")
    check("from-record emits no child array", "OrderItem" not in rec)


def test_from_record_skeleton_falls_back_to_node_name_without_mapping():
    detail = _detail_with_mappings()
    skeleton, err = _runtime.build_from_record_skeleton(detail, root_id="0Q0xxx")
    check("from-record without mapping still builds", err is None)
    check("from-record businessObjectType falls back to node name",
          skeleton["Order"][0]["businessObjectType"] == "Order")


def test_from_record_skeleton_single_node_needs_no_node_name():
    detail = _detail_with_mappings()  # one top-level node
    skeleton, err = _runtime.build_from_record_skeleton(detail, root_id="X")
    check("single top node auto-selected without --node", err is None and skeleton)


def test_from_record_skeleton_multi_node_requires_node_name():
    detail = _detail_with_mappings()
    # add a second top-level node so selection is ambiguous
    version = detail["contextDefinitionVersionList"][0]
    version["contextNodes"].append({"name": "Asset", "attributes": [], "childNodes": []})
    skeleton, err = _runtime.build_from_record_skeleton(detail, root_id="X")
    check("ambiguous top nodes → error, no skeleton", skeleton is None and err)
    check("ambiguity error names --node and lists the nodes",
          "--node" in err and "Order" in err and "Asset" in err)
    # naming the node resolves it
    picked, err2 = _runtime.build_from_record_skeleton(
        detail, root_id="X", node_name="Asset"
    )
    check("naming the node resolves the ambiguity",
          err2 is None and list(picked.keys()) == ["Asset"])


def test_from_record_skeleton_unknown_node_name_errors():
    detail = _detail_with_mappings()
    skeleton, err = _runtime.build_from_record_skeleton(
        detail, root_id="X", node_name="Nope"
    )
    check("unknown --node → error, no skeleton", skeleton is None and err)
    check("unknown-node error lists the available top nodes", "Order" in err)


# --------------------------------------------------------------------------- #
# _runtime — RuntimeContextClient / dry-run contract
# --------------------------------------------------------------------------- #

def test_query_record_forces_execution_and_encodes_children():
    t = FakeTransport(dry_run=True, responses={"query-record": {"isSuccess": True}})
    client = _runtime.RuntimeContextClient(t)
    result = client.query_record(context_id="CID", children=False)
    check("query-record returns the canned response under dry-run",
          result == {"isSuccess": True})
    method, path, body, dry = t.calls[-1]
    check("query-record is POSTed", method == "POST")
    check("query-record forces dry_run=False (read always executes)", dry is False)
    check("query-record encodes children=false in the path", "children=false" in path)
    check("query-record body carries the contextId", body["contextId"] == "CID")


def test_query_tags_leaner_path():
    t = FakeTransport(dry_run=False)
    client = _runtime.RuntimeContextClient(t)
    client.query_tags(context_id="CID", tags=["T1"], leaner=True)
    _method, path, _body, dry = t.calls[-1]
    check("leaner tag read hits query-tags-leaner", path.endswith("query-tags-leaner"))
    check("tag read forces dry_run=False", dry is False)


def test_clear_runtime_schema_url_encodes_params():
    t = FakeTransport(dry_run=False)
    client = _runtime.RuntimeContextClient(t)
    client.clear_runtime_schema(
        context_definition_name="RLM Sales & Ctx", mapping_names=["A B", "C"]
    )
    method, path, _body, _dry = t.calls[-1]
    check("clear-schema is a DELETE", method == "DELETE")
    check("clear-schema URL-encodes the definition name (space+&)",
          "RLM%20Sales%20%26%20Ctx" in path)
    check("clear-schema joins + encodes mapping names",
          "contextMappingNames=A%20B%2CC" in path)


def test_get_interface_url_encodes_name():
    t = FakeTransport(dry_run=False)
    client = _runtime.RuntimeContextClient(t)
    client.get_definition_interface("My Interface")
    _method, path, _body, dry = t.calls[-1]
    check("interface GET encodes the name", "My%20Interface" in path)
    check("interface GET forces dry_run=False", dry is False)


def test_session_dry_run_issues_no_mutations():
    t = FakeTransport(dry_run=True)
    client = _runtime.RuntimeContextClient(t)
    session = _runtime.RuntimeSession(client)
    summary = session.run(
        create_spec={"context_definition_id": "11O1", "mapping_id": "11j1",
                     "data": {"Order": []}},
        attribute_updates=[{"dataPath": [], "attributes": [
            {"attributeName": "A", "attributeValue": "1"}]}],
        do_query=True,
        persist_target_mapping_id="11j2",
    )
    # Only the create POST should have been attempted (and skipped by the
    # transport); everything downstream is skipped because no contextId exists.
    check("dry-run session reports created=False", summary["created"] is False)
    check("dry-run session has no contextId", summary["context_id"] is None)
    check("dry-run session did not delete", summary["deleted"] is False)
    non_get = [c for c in t.calls if c[0] not in ("GET", "HEAD")]
    check("dry-run issued only the (skipped) create POST, no persist/query/delete",
          len(non_get) == 1 and non_get[0][1] == _runtime.ep.CONTEXTS_COLLECTION)


def test_session_reuse_existing_id_queries_but_does_not_delete():
    t = FakeTransport(dry_run=False, responses={"query-record": {"isSuccess": True}})
    client = _runtime.RuntimeContextClient(t)
    session = _runtime.RuntimeSession(client)
    summary = session.run(existing_context_id="REUSED", do_query=True)
    check("reused session keeps the supplied contextId", summary["context_id"] == "REUSED")
    check("reused session did not create", summary["created"] is False)
    check("reused session did not auto-delete the instance", summary["deleted"] is False)
    check("reused session ran the query", summary.get("query") == {"isSuccess": True})
    deletes = [c for c in t.calls if c[0] == "DELETE"]
    check("reused session issued no DELETE", not deletes)


def test_session_create_then_delete_live_path():
    t = FakeTransport(
        dry_run=False,
        responses={"connect/contexts": {"contextId": "NEW", "isSuccess": True}},
    )
    client = _runtime.RuntimeContextClient(t)
    session = _runtime.RuntimeSession(client)
    summary = session.run(
        create_spec={"context_definition_id": "11O1", "mapping_id": "11j1",
                     "data": {"Order": []}},
    )
    check("live session captures the created contextId", summary["context_id"] == "NEW")
    check("live session reports created=True", summary["created"] is True)
    check("live session auto-deleted the instance", summary["deleted"] is True)
    deletes = [c for c in t.calls if c[0] == "DELETE"]
    check("live session issued exactly one DELETE", len(deletes) == 1)


# --------------------------------------------------------------------------- #
# list_context_interfaces — response normalization (_rows, _count_interface_tags)
# --------------------------------------------------------------------------- #

def test_lci_rows_from_metadata_list_shape():
    # The live v67.0 list shape: a wrapper keyed contextDefinitionInterfaceMetadataList.
    response = {
        "contextDefinitionInterfaceMetadataList": [
            {"interfaceName": "DemoContextInterface", "version": 63.1},
            {"interfaceName": "StandaloneBillingContextInterface", "version": 64.6},
        ]
    }
    rows = lci._rows(response)
    check("list-shape rows are unwrapped from the metadata-list key", len(rows) == 2)
    check("list-shape rows carry interfaceName",
          rows[0]["interfaceName"] == "DemoContextInterface")


def test_lci_rows_from_singular_by_name_shape():
    # The by-name GET nests the row under the singular key + a node-tag tree.
    response = {
        "contextDefinitionInterfaceMetadata": {
            "developerName": "DemoContextInterface", "version": 63.1
        },
        "contextDefinitionInterfaceNodeTagList": [],
    }
    rows = lci._rows(response)
    check("by-name row is unwrapped from the singular key", len(rows) == 1)
    check("by-name row carries developerName",
          rows[0]["developerName"] == "DemoContextInterface")


def test_lci_rows_bare_list_and_unknown_envelope():
    check("a bare list passes through", len(lci._rows([{"name": "X"}, {"name": "Y"}])) == 2)
    check("an unrecognized envelope without a name yields no bogus row",
          lci._rows({"someWrapper": {"nested": 1}}) == [])
    check("a bare interface row (has a name) is wrapped",
          len(lci._rows({"interfaceName": "Solo"})) == 1)


def test_lci_count_interface_tags_recurses():
    response = {
        "contextDefinitionInterfaceNodeTagList": [
            {
                "name": "Root",
                "attributeTags": [{"name": "a1"}, {"name": "a2"}],
                "childNodeTags": [
                    {"name": "Child", "attributeTags": [{"name": "a3"}]},
                ],
            },
        ]
    }
    counts = lci._count_interface_tags(response)
    check("interface node-tag count includes nested nodes", counts == (2, 3))
    check("no node-tag list → None (e.g. the list endpoint)",
          lci._count_interface_tags({"contextDefinitionInterfaceMetadataList": []}) is None)


# --------------------------------------------------------------------------- #

def main():
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    print(f"Running {len(tests)} runtime test groups...\n")
    for t in tests:
        t()
    print()
    passed = sum(1 for _, ok in RESULTS if ok)
    total = len(RESULTS)
    print(f"{passed}/{total} checks passed.")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
