"""Unit tests for pure-logic helpers in scripts/ai/docgen/.

Tests functions that don't require org access — hierarchy analysis,
depth computation, pivot detection, array root extraction, SOQL escaping,
output parsing, and token extraction.
"""
import json
import sys
from pathlib import Path

import pytest

# Add docgen scripts to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts" / "ai" / "docgen"))

from _soql import soql_escape


# ─── soql_escape ────────────────────────────────────────────────────────────

class TestSoqlEscape:
    def test_plain_string(self):
        assert soql_escape("RLMQuoteProposalExtract") == "RLMQuoteProposalExtract"

    def test_single_quote(self):
        assert soql_escape("O'Brien") == "O\\'Brien"

    def test_multiple_quotes(self):
        assert soql_escape("it's a 'test'") == "it\\'s a \\'test\\'"

    def test_backslash(self):
        assert soql_escape("path\\name") == "path\\\\name"

    def test_combined(self):
        assert soql_escape("it's\\here") == "it\\'s\\\\here"

    def test_empty_string(self):
        assert soql_escape("") == ""

    def test_non_string(self):
        assert soql_escape(123) == "123"

    def test_salesforce_id(self):
        assert soql_escape("0jIO40000004VGZMA2") == "0jIO40000004VGZMA2"


# ─── docgen_inspect_hierarchy — pure functions ──────────────────────────────

from docgen_odt_inspect_hierarchy import (
    classify_items,
    build_hierarchy_tree,
    compute_depth,
    get_output_array_root,
    find_pivot_path,
    _deeper_oqs_are_many_to_one,
    validate_depth_uniformity,
)


class TestClassifyItems:
    def test_separates_queries_from_mappings(self):
        items = [
            {"InputObjectName": "Quote", "InputObjectQuerySequence": 1,
             "OutputFieldName": "Quote"},
            {"InputFieldName": "Quote:Name", "OutputFieldName": "QuoteName"},
        ]
        oqs, fms = classify_items(items)
        assert len(oqs) == 1
        assert len(fms) == 1
        assert oqs[0]["InputObjectName"] == "Quote"

    def test_item_without_sequence_is_mapping(self):
        items = [
            {"InputObjectName": "Quote", "OutputFieldName": "Quote"},
        ]
        oqs, fms = classify_items(items)
        assert len(oqs) == 0
        assert len(fms) == 1


class TestBuildHierarchyTree:
    def test_simple_tree(self):
        oqs = [
            {"OutputFieldName": "Root", "InputObjectName": "Quote"},
            {"OutputFieldName": "Root:Child", "InputObjectName": "QLI"},
        ]
        tree = build_hierarchy_tree(oqs)
        assert "Root" in tree
        assert "Child" in tree["Root"]
        assert tree["Root"]["__item__"]["InputObjectName"] == "Quote"
        assert tree["Root"]["Child"]["__item__"]["InputObjectName"] == "QLI"

    def test_deep_nesting(self):
        oqs = [
            {"OutputFieldName": "A:B:C", "InputObjectName": "Obj"},
        ]
        tree = build_hierarchy_tree(oqs)
        assert "A" in tree
        assert "B" in tree["A"]
        assert "C" in tree["A"]["B"]


class TestComputeDepth:
    def test_root_depth(self):
        oqs = [{"OutputFieldName": "Quote"}]
        assert compute_depth("Quote:Name", oqs) == 1

    def test_child_depth(self):
        oqs = [
            {"OutputFieldName": "Quote"},
            {"OutputFieldName": "Quote:QLI"},
        ]
        assert compute_depth("Quote:QLI:ProductName", oqs) == 2

    def test_grandchild_depth(self):
        oqs = [
            {"OutputFieldName": "Quote"},
            {"OutputFieldName": "Quote:QLI"},
            {"OutputFieldName": "Quote:QLI:Product"},
        ]
        assert compute_depth("Quote:QLI:Product:Name", oqs) == 3

    def test_no_match_returns_zero(self):
        oqs = [{"OutputFieldName": "Other"}]
        assert compute_depth("Quote:Name", oqs) == 0

    def test_partial_match_uses_deepest(self):
        oqs = [
            {"OutputFieldName": "Quote"},
            {"OutputFieldName": "Quote:QLI"},
        ]
        assert compute_depth("Quote:QLI:Product:Name", oqs) == 2


class TestGetOutputArrayRoot:
    def test_two_parts(self):
        assert get_output_array_root("Grant:ProductName") == "Grant"

    def test_three_parts(self):
        assert get_output_array_root("Line:CQL:ProductName") == "Line:CQL"

    def test_single_part(self):
        assert get_output_array_root("TopLevel") == "TopLevel"

    def test_four_parts(self):
        assert get_output_array_root("Line:CQL:CQL2:Name") == "Line:CQL:CQL2"


class TestFindPivotPath:
    def test_common_prefix(self):
        oqs = [
            {"OutputFieldName": "Quote"},
            {"OutputFieldName": "Quote:QLI"},
            {"OutputFieldName": "Quote:QLI:Product"},
        ]
        mappings = [
            {"input": "Quote:QLI:ProductName", "depth": 2},
            {"input": "Quote:QLI:Product:Name", "depth": 3},
        ]
        assert find_pivot_path(mappings, oqs) == "Quote:QLI"

    def test_no_common_prefix(self):
        oqs = [
            {"OutputFieldName": "A"},
            {"OutputFieldName": "B"},
        ]
        mappings = [
            {"input": "A:Field", "depth": 1},
            {"input": "B:Field", "depth": 1},
        ]
        assert find_pivot_path(mappings, oqs) is None

    def test_empty_mappings(self):
        assert find_pivot_path([], []) is None


class TestDeeperOqsAreManyToOne:
    def test_fk_lookup_is_safe(self):
        oqs = [
            {"OutputFieldName": "Quote:QLI"},
            {"OutputFieldName": "Quote:QLI:Product"},
        ]
        mappings = [
            {"input": "Quote:QLI:Name", "depth": 2},
            {"input": "Quote:QLI:Product:Name", "depth": 3},
        ]
        oqs[1]["FilterValue"] = "Quote:QLI:Product2Id"
        assert _deeper_oqs_are_many_to_one("Quote:QLI", mappings, oqs) is True

    def test_child_of_is_dangerous(self):
        oqs = [
            {"OutputFieldName": "Quote:QLI"},
            {"OutputFieldName": "Quote:QLI:Grant"},
        ]
        mappings = [
            {"input": "Quote:QLI:Name", "depth": 2},
            {"input": "Quote:QLI:Grant:Qty", "depth": 3},
        ]
        oqs[1]["FilterValue"] = "Quote:QLI:Id"
        assert _deeper_oqs_are_many_to_one("Quote:QLI", mappings, oqs) is False

    def test_mixed_fk_and_child_of(self):
        oqs = [
            {"OutputFieldName": "Quote:QLI"},
            {"OutputFieldName": "Quote:QLI:Product"},
            {"OutputFieldName": "Quote:QLI:Grant"},
        ]
        mappings = [
            {"input": "Quote:QLI:Name", "depth": 2},
            {"input": "Quote:QLI:Product:Name", "depth": 3},
            {"input": "Quote:QLI:Grant:Qty", "depth": 3},
        ]
        oqs[1]["FilterValue"] = "Quote:QLI:Product2Id"
        oqs[2]["FilterValue"] = "Quote:QLI:Id"
        assert _deeper_oqs_are_many_to_one("Quote:QLI", mappings, oqs) is False

    def test_no_deeper_oqs_is_safe(self):
        oqs = [{"OutputFieldName": "Quote:QLI"}]
        mappings = [{"input": "Quote:QLI:Name", "depth": 2}]
        assert _deeper_oqs_are_many_to_one("Quote:QLI", mappings, oqs) is True


class TestValidateDepthUniformity:
    def test_uniform_depth_no_violations(self):
        oqs = [
            {"OutputFieldName": "Quote"},
            {"OutputFieldName": "Quote:QLI"},
        ]
        fms = [
            {"InputFieldName": "Quote:QLI:Name", "OutputFieldName": "Line:Name"},
            {"InputFieldName": "Quote:QLI:Qty", "OutputFieldName": "Line:Qty"},
        ]
        violations = validate_depth_uniformity(fms, oqs)
        assert violations == []

    def test_mixed_depth_with_child_of_high_severity(self):
        oqs = [
            {"OutputFieldName": "Quote"},
            {"OutputFieldName": "Quote:QLI"},
            {"OutputFieldName": "Quote:QLI:Grant"},
        ]
        oqs[2]["FilterValue"] = "Quote:QLI:Id"
        fms = [
            {"InputFieldName": "Quote:QLI:Name", "OutputFieldName": "Items:Name"},
            {"InputFieldName": "Quote:QLI:Grant:Qty", "OutputFieldName": "Items:GrantQty"},
        ]
        violations = validate_depth_uniformity(fms, oqs)
        assert len(violations) == 1
        assert violations[0]["severity"] == "high"
        assert violations[0]["array_root"] == "Items"

    def test_mixed_depth_with_fk_low_severity(self):
        oqs = [
            {"OutputFieldName": "Quote"},
            {"OutputFieldName": "Quote:QLI"},
            {"OutputFieldName": "Quote:QLI:Product"},
        ]
        oqs[2]["FilterValue"] = "Quote:QLI:Product2Id"
        fms = [
            {"InputFieldName": "Quote:QLI:Name", "OutputFieldName": "Items:Name"},
            {"InputFieldName": "Quote:QLI:Product:SKU", "OutputFieldName": "Items:SKU"},
        ]
        violations = validate_depth_uniformity(fms, oqs)
        assert len(violations) == 1
        assert violations[0]["severity"] == "low"


# ─── docgen_execute_odt — pure functions ────────────────────────────────────

from docgen_odt_execute import count_arrays, filter_fields


class TestCountArrays:
    def test_list_of_dicts(self):
        data = [{"Name": "A", "Items": [{"x": 1}, {"x": 2}]}]
        counts = count_arrays(data)
        assert counts["(root)"] == 1
        assert "Items" in counts

    def test_empty_list(self):
        counts = count_arrays([])
        assert counts == {"(root)": 0}

    def test_list_of_non_dicts(self):
        counts = count_arrays(["a", "b", "c"])
        assert counts == {"(root)": 3}

    def test_dict_input(self):
        data = {"Items": [1, 2, 3], "Name": "Test"}
        counts = count_arrays(data)
        assert counts == {"Items": 3}


class TestFilterFields:
    def test_filters_dict(self):
        data = {"a": 1, "b": 2, "c": 3}
        assert filter_fields(data, {"a", "c"}) == {"a": 1, "c": 3}

    def test_filters_list_of_dicts(self):
        data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        result = filter_fields(data, {"a"})
        assert result == [{"a": 1}, {"a": 3}]

    def test_non_dict_list_items_skipped(self):
        data = ["string", {"a": 1}]
        result = filter_fields(data, {"a"})
        assert result == [{"a": 1}]

    def test_scalar_passthrough(self):
        assert filter_fields(42, {"a"}) == 42
