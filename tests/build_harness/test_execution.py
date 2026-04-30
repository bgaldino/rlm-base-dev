"""Tests for scripts.build_harness.harness.execution.

Covers the pure helpers ``make_run_id``. The subprocess-heavy ``run_command``
and ``org_exists`` are integration-level and not covered here.
"""

from __future__ import annotations

import re

from scripts.build_harness.harness.execution import make_run_id


class TestMakeRunId:
    """``make_run_id`` must return a deterministic format used as directory names."""

    def test_starts_with_run_prefix(self) -> None:
        assert make_run_id().startswith("run-")

    def test_matches_iso_timestamp_pattern(self) -> None:
        rid = make_run_id()
        assert re.fullmatch(r"run-\d{8}T\d{6}Z", rid), f"unexpected format: {rid}"

    def test_consecutive_calls_are_equal_or_increasing(self) -> None:
        a = make_run_id()
        b = make_run_id()
        assert b >= a
