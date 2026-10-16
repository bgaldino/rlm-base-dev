"""Regression: the CCI context task must not clobber sibling attribute mappings.

``PATCH context-mappings/{id}/context-node-mappings`` replaces a node mapping's
whole ``contextAttributeMappings`` list. Plans that share a node mapping (the
Approvals, PrmPricing and ConstraintEngineNodeStatus plans all map
SalesTransactionItem on QuoteEntitiesMapping) must re-emit each other's rows.
"""
import logging
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from tasks.rlm_context_service import ManageContextDefinition  # noqa: E402

NM_ID = "11bNM0000000001"


def _detail(rows):
    return {
        "contextDefinitionVersionList": [{
            "contextMappings": [{
                "contextMappingId": "11jMAP000000001",
                "name": "QuoteEntitiesMapping",
                "contextNodeMappings": [{
                    "contextNodeMappingId": NM_ID,
                    "contextNodeName": "SalesTransactionItem",
                    "attributeMappings": rows,
                }],
            }],
        }],
    }


def _row(mapping_id, attr_id, name, base_reference=None):
    row = {
        "contextAttributeMappingId": mapping_id,
        "contextAttributeId": attr_id,
        "contextAttributeName": name,
        "contextInputAttributeName": name,
        "dataType": "STRING",
        "sourceObject": "QuoteLineItem",
    }
    if base_reference:
        row["baseReference"] = base_reference
    return row


def _payload(attr_id, name):
    return {
        "contextMappings": [{
            "contextMappingId": "11jMAP000000001",
            "contextNodeMappings": [{
                "contextNodeMappingId": NM_ID,
                "attributeMappings": [{
                    "contextAttributeId": attr_id,
                    "contextInputAttributeName": name,
                }],
            }],
        }],
    }


class NodeMappingSiblingMergeTest(unittest.TestCase):
    def setUp(self):
        self.task = ManageContextDefinition.__new__(ManageContextDefinition)
        self.task.logger = logging.getLogger("test")
        self.patched = []
        self.task._patch_context_node_mappings = (
            lambda mapping_id, node_maps, dry_run: self.patched.append(node_maps)
        )

    def _sent_rows(self):
        self.assertEqual(len(self.patched), 1)
        return self.patched[0][0]["attributeMappings"]["contextAttributeMappings"]

    def test_patch_reemits_custom_siblings(self):
        detail = _detail([
            _row("11cPRM1", "11eAttr1", "PartnerDiscount__c"),
            _row("11cCENS", "11eAttr2", "ConstraintEngineNodeStatus__c"),
        ])
        self.task._apply_context_mapping_updates(
            "11OCTX", _payload("11eAttr3", "RLM_Approval__c"), False, detail=detail
        )
        names = {r.get("contextInputAttributeName") for r in self._sent_rows()}
        self.assertEqual(
            names,
            {"RLM_Approval__c", "PartnerDiscount__c", "ConstraintEngineNodeStatus__c"},
        )
        # Siblings are projected to the PATCH-accepted shape.
        for row in self._sent_rows():
            self.assertNotIn("dataType", row)
            self.assertNotIn("contextAttributeName", row)

    def test_reemitted_row_is_not_duplicated(self):
        detail = _detail([_row("11cAPR", "11eAttr3", "RLM_Approval__c")])
        payload = _payload("11eAttr3", "RLM_Approval__c")
        self.task._apply_context_mapping_updates("11OCTX", payload, False, detail=detail)
        self.assertEqual(len(self._sent_rows()), 1)

    def test_inherited_siblings_are_not_reemitted(self):
        detail = _detail([
            _row("11cSTD", "11eAttr9", "ListPrice",
                 base_reference="SalesTransactionContext__stdctx/x"),
        ])
        self.task._apply_context_mapping_updates(
            "11OCTX", _payload("11eAttr3", "RLM_Approval__c"), False, detail=detail
        )
        names = [r.get("contextInputAttributeName") for r in self._sent_rows()]
        self.assertEqual(names, ["RLM_Approval__c"])


if __name__ == "__main__":
    unittest.main()
