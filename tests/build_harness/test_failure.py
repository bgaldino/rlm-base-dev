"""Tests for scripts.build_harness.harness.failure.

Locks in the contract of ``classify_signature`` and ``infer_failure_signature``.
The CLI scenario runner uses ``classify_signature`` to decide whether to retry
a failed CCI step; the TUI runner shows the result in the failure banner. Both
must agree on the bucket name spellings ("transient" / "deterministic" /
"unknown") because the strings flow into JSON manifests downstream consumers
parse.
"""

from __future__ import annotations

import pytest

from scripts.build_harness.harness.failure import (
    DETERMINISTIC_PATTERNS,
    TRANSIENT_PATTERNS,
    classify_signature,
    infer_failure_signature,
)


class TestClassifySignatureBuckets:
    """The bucket names are part of the on-disk manifest schema."""

    @pytest.mark.parametrize("text", ["", "no signal here", "succeeded"])
    def test_returns_unknown_when_no_pattern_matches(self, text: str) -> None:
        assert classify_signature(text) == "unknown"

    @pytest.mark.parametrize(
        "text",
        [
            "Connection timed out after 30s",
            "HTTP 503 Service Unavailable",
            "got 502 from upstream",
            "rate limited: 429",
            "connection reset by peer",
            "name or service not known: na123.salesforce.com",
        ],
    )
    def test_transient_patterns_classify_as_transient(self, text: str) -> None:
        assert classify_signature(text) == "transient"

    @pytest.mark.parametrize(
        "text",
        [
            "INVALID FIELD: Foo__c does not exist",
            "Traceback (most recent call last):",
            "AssertionError: expected 1 got 2",
            "validation error: bad config",
            "KeyError: 'missing'",
            "yaml.parser.ParserError: bad indent",
            "command not found: cci",
        ],
    )
    def test_deterministic_patterns_classify_as_deterministic(self, text: str) -> None:
        assert classify_signature(text) == "deterministic"

    def test_case_insensitive(self) -> None:
        assert classify_signature("TIMED OUT") == "transient"
        assert classify_signature("traceback") == "deterministic"
        assert classify_signature("TraceBack") == "deterministic"

    def test_transient_takes_priority_over_deterministic(self) -> None:
        # "timed out" comes first in TRANSIENT_PATTERNS; if a line happens to
        # contain both flavors of substring (rare but possible), the transient
        # check runs first. Pin this behavior so the retry policy is stable.
        text = "Traceback: connection timed out"
        assert "timed out" in TRANSIENT_PATTERNS
        assert "traceback" in DETERMINISTIC_PATTERNS
        assert classify_signature(text) == "transient"


class TestInferFailureSignature:
    def test_empty_input_returns_empty_string(self) -> None:
        assert infer_failure_signature([]) == ""

    def test_picks_last_error_line_walking_backwards(self) -> None:
        lines = [
            "Step 1: ok",
            "Step 2: error A",
            "Step 3: error B",
            "Done",
        ]
        # Walks in reverse; "Done" has no error keyword, "error B" matches first.
        assert infer_failure_signature(lines) == "Step 3: error B"

    def test_skips_cci_help_noise(self) -> None:
        # CCI prints these on every non-zero exit; they should never surface
        # as the failure signature even though they appear at the very end.
        lines = [
            "AssertionError: thing broke",
            "Run cci error --help for more details",
            "See debugging errors in the CCI docs",
        ]
        assert infer_failure_signature(lines) == "AssertionError: thing broke"

    def test_falls_back_to_last_line_when_no_error_keyword(self) -> None:
        lines = ["INFO: starting", "INFO: working", "INFO: done"]
        assert infer_failure_signature(lines) == "INFO: done"

    def test_strips_trailing_whitespace_on_returned_line(self) -> None:
        lines = ["  Traceback (most recent call last):  \n"]
        assert infer_failure_signature(lines) == "Traceback (most recent call last):"

    def test_recognizes_all_keyword_variants(self) -> None:
        for keyword in ["error", "exception", "failed", "traceback"]:
            lines = ["benign", f"Something {keyword} happened", "tail"]
            assert infer_failure_signature(lines) == f"Something {keyword} happened"

    def test_handles_iterables_not_just_lists(self) -> None:
        # Generators, deques, etc. are valid inputs (the CLI passes a deque
        # tail buffer). Confirm we materialize before reversing.
        gen = (line for line in ["info", "an error occurred", "tail"])
        assert infer_failure_signature(gen) == "an error occurred"

    def test_blank_lines_in_input_are_treated_as_no_keyword(self) -> None:
        lines = ["error: real failure", "", "   "]
        # Walks backward: "   " (no keyword) then "" (no keyword) then "error:..."
        assert infer_failure_signature(lines) == "error: real failure"
