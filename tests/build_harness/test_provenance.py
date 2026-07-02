"""Tests for scripts.build_harness.harness.provenance.

Pin down the parser behavior for ``Stamped org: ...`` lines emitted by the
Apex stamp_git_commit script. The previous implementation used a strict
positional regex; this version is order-independent and tolerates new
fields. Tests cover both the legacy-format lines (regression) and the
new flexibility (extra fields, reordered fields, missing optional fields).
"""

from __future__ import annotations

from scripts.build_harness.harness.provenance import (
    parse_stamp_from_lines,
    parse_stamp_line,
)


class TestParseStampLineHappyPath:
    """The canonical line shape emitted today."""

    def test_full_legacy_format(self) -> None:
        line = (
            "Stamped org: commit=abc1234, branch=feature/foo, "
            "timestamp=2026-04-29T12:00:00Z, flow=prepare_rlm_org, org=beta"
        )
        parsed = parse_stamp_line(line)
        assert parsed == {
            "commit_hash_short": "abc1234",
            "branch": "feature/foo",
            "build_timestamp": "2026-04-29T12:00:00Z",
            "flow_name": "prepare_rlm_org",
            "org_definition": "beta",
            "dirty_tree": False,
        }

    def test_dirty_marker_extracted_from_commit_value(self) -> None:
        line = (
            "Stamped org: commit=abc1234 (dirty), branch=main, "
            "timestamp=2026-04-29T12:00:00Z, flow=prepare_rlm_org, org=beta"
        )
        parsed = parse_stamp_line(line)
        assert parsed["commit_hash_short"] == "abc1234"
        assert parsed["dirty_tree"] is True

    def test_handles_leading_whitespace_and_log_prefix(self) -> None:
        # Console output sometimes prepends timestamps or log levels; the
        # parser only requires the key part to start with the prefix after
        # ``.strip()``.
        line = "  Stamped org: commit=def5678, branch=x, timestamp=t, flow=f, org=o  "
        parsed = parse_stamp_line(line)
        assert parsed is not None
        assert parsed["commit_hash_short"] == "def5678"


class TestParseStampLineFlexibility:
    """The order-independent parser should tolerate format evolution."""

    def test_field_order_does_not_matter(self) -> None:
        line = (
            "Stamped org: org=beta, flow=prepare_rlm_org, "
            "timestamp=2026-04-29T12:00:00Z, branch=main, commit=abc1234"
        )
        parsed = parse_stamp_line(line)
        assert parsed["commit_hash_short"] == "abc1234"
        assert parsed["org_definition"] == "beta"

    def test_unknown_fields_preserved_in_extra(self) -> None:
        # If the Apex script adds a new field tomorrow we want it to show up
        # in build_provenance.json under ``extra`` rather than silently
        # dropping the entire stamp line.
        line = (
            "Stamped org: commit=abc1234, branch=main, "
            "timestamp=2026-04-29T12:00:00Z, flow=prepare_rlm_org, "
            "org=beta, build_user=alice, ci_run_id=12345"
        )
        parsed = parse_stamp_line(line)
        assert parsed is not None
        assert parsed["extra"] == {"build_user": "alice", "ci_run_id": "12345"}

    def test_extra_keys_with_digits_and_camelcase_preserved(self) -> None:
        # Keys containing digits or uppercase (e.g. camelCase) must still be
        # captured into ``extra`` with their original casing, not dropped.
        line = (
            "Stamped org: commit=abc1234, branch=main, ciRunId=987, "
            "ci_run_id2=xyz, attempt3=second"
        )
        parsed = parse_stamp_line(line)
        assert parsed is not None
        assert parsed["commit_hash_short"] == "abc1234"
        assert parsed["extra"] == {"ciRunId": "987", "ci_run_id2": "xyz", "attempt3": "second"}

    def test_missing_optional_fields_default_to_empty(self) -> None:
        # The strict regex would have returned None here; we now keep the
        # commit value (the most useful piece) and report empty strings for
        # the rest. Downstream consumers can still detect "stamped but
        # incomplete" by checking for empty strings.
        line = "Stamped org: commit=abc1234, branch=main"
        parsed = parse_stamp_line(line)
        assert parsed is not None
        assert parsed["commit_hash_short"] == "abc1234"
        assert parsed["branch"] == "main"
        assert parsed["build_timestamp"] == ""
        assert parsed["flow_name"] == ""
        assert parsed["org_definition"] == ""

    def test_no_extra_field_when_no_unknown_keys(self) -> None:
        # Don't pollute provenance.json with empty ``extra`` dicts on the
        # common case.
        line = (
            "Stamped org: commit=abc1234, branch=main, "
            "timestamp=t, flow=f, org=o"
        )
        parsed = parse_stamp_line(line)
        assert "extra" not in parsed


class TestParseStampLineRejection:
    def test_returns_none_for_unrelated_line(self) -> None:
        assert parse_stamp_line("hello world") is None
        assert parse_stamp_line("INFO: doing things") is None

    def test_returns_none_when_commit_missing(self) -> None:
        # A stamp line without a commit value is not useful as provenance.
        assert parse_stamp_line("Stamped org: branch=main, flow=f") is None

    def test_returns_none_for_empty_string(self) -> None:
        assert parse_stamp_line("") is None
        assert parse_stamp_line("   ") is None


class TestParseStampFromLines:
    """The aggregator that walks a buffered tail in reverse."""

    def test_returns_stamped_status_with_values(self) -> None:
        lines = [
            "INFO: starting",
            "Stamped org: commit=abc1234, branch=main, timestamp=t, flow=f, org=o",
            "INFO: continuing",
        ]
        result = parse_stamp_from_lines(lines)
        assert result["status"] == "stamped"
        assert result["values"]["commit_hash_short"] == "abc1234"

    def test_returns_last_stamp_when_multiple_present(self) -> None:
        # Walks in reverse; the most recent stamp wins.
        lines = [
            "Stamped org: commit=oldoldold, branch=main, timestamp=t, flow=f, org=o",
            "INFO: re-stamping",
            "Stamped org: commit=newnewnew, branch=main, timestamp=t, flow=f, org=o",
        ]
        result = parse_stamp_from_lines(lines)
        assert result["status"] == "stamped"
        assert result["values"]["commit_hash_short"] == "newnewnew"

    def test_recognizes_non_fatal_failure(self) -> None:
        lines = [
            "INFO: attempting stamp",
            "Failed to stamp org (non-fatal): permission denied",
        ]
        result = parse_stamp_from_lines(lines)
        assert result["status"] == "non_fatal_failure"
        assert "permission denied" in result["details"]

    def test_returns_unknown_when_no_stamp_or_failure_marker(self) -> None:
        result = parse_stamp_from_lines(["INFO: unrelated", "INFO: more"])
        assert result["status"] == "unknown"
        assert "stamp output not found" in result["details"]

    def test_empty_input_returns_unknown(self) -> None:
        assert parse_stamp_from_lines([])["status"] == "unknown"
