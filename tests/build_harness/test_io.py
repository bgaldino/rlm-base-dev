"""Tests for scripts.build_harness.harness.io.

This module is the single source of truth for filesystem and serialization
helpers used by the harness CLI, the scenario runner, the provenance writer,
the report writer, and the TUI runner. The contract these tests pin down:

- ``now_utc`` always returns an ISO-8601 UTC string parsable by ``fromisoformat``.
- ``ensure_dir`` is idempotent and creates parents.
- ``write_json`` writes deterministic, human-diffable JSON (sorted keys,
  indent=2, trailing newline). ``load_json`` round-trips.
- ``load_jsonl`` returns ``[]`` for missing files (no exception) and skips
  blank lines.
- ``append_jsonl`` produces sorted-key one-object-per-line output suitable
  for ``load_jsonl`` to read back.
"""

from __future__ import annotations

import datetime as dt
import json

import pytest

from scripts.build_harness.harness.io import (
    append_jsonl,
    ensure_dir,
    load_json,
    load_jsonl,
    now_utc,
    write_json,
)


class TestNowUtc:
    def test_returns_iso8601_string(self) -> None:
        stamp = now_utc()
        assert isinstance(stamp, str)
        # Round-trip through fromisoformat: must be valid ISO-8601.
        parsed = dt.datetime.fromisoformat(stamp)
        assert parsed.tzinfo is not None, "now_utc must include timezone"

    def test_is_utc(self) -> None:
        parsed = dt.datetime.fromisoformat(now_utc())
        # offset must be exactly UTC (zero seconds).
        assert parsed.utcoffset() == dt.timedelta(0)


class TestEnsureDir:
    def test_creates_missing_directory(self, tmp_path) -> None:
        target = tmp_path / "new"
        ensure_dir(target)
        assert target.is_dir()

    def test_creates_nested_parents(self, tmp_path) -> None:
        target = tmp_path / "a" / "b" / "c"
        ensure_dir(target)
        assert target.is_dir()

    def test_idempotent_on_existing(self, tmp_path) -> None:
        target = tmp_path / "exists"
        target.mkdir()
        # Must not raise on second call.
        ensure_dir(target)
        ensure_dir(target)
        assert target.is_dir()


class TestWriteJsonLoadJson:
    def test_roundtrip_dict(self, tmp_path) -> None:
        path = tmp_path / "x.json"
        payload = {"b": 2, "a": 1, "nested": {"y": [1, 2, 3]}}
        write_json(path, payload)
        assert load_json(path) == payload

    def test_output_is_sorted_indented_with_trailing_newline(self, tmp_path) -> None:
        path = tmp_path / "x.json"
        write_json(path, {"b": 2, "a": 1})
        text = path.read_text(encoding="utf-8")
        # Sorted keys: a appears before b.
        assert text.index('"a"') < text.index('"b"')
        # Indent 2 means we have at least one '  "' opening.
        assert '\n  "a"' in text
        # Trailing newline keeps git diffs clean.
        assert text.endswith("\n")

    def test_load_json_missing_raises_filenotfound(self, tmp_path) -> None:
        with pytest.raises(FileNotFoundError):
            load_json(tmp_path / "does_not_exist.json")

    def test_write_json_preserves_unicode(self, tmp_path) -> None:
        path = tmp_path / "u.json"
        write_json(path, {"flag": "café"})
        # Python's json.dump escapes non-ASCII by default; the round-trip
        # value must still be the original unicode string.
        assert load_json(path) == {"flag": "café"}


class TestLoadJsonl:
    def test_returns_empty_for_missing_file(self, tmp_path) -> None:
        # Critical contract: callers (provenance, reporting) rely on this
        # to skip absent step_results.jsonl files without checking existence.
        assert load_jsonl(tmp_path / "missing.jsonl") == []

    def test_skips_blank_lines(self, tmp_path) -> None:
        path = tmp_path / "events.jsonl"
        path.write_text(
            '{"a": 1}\n'
            "\n"
            "   \n"
            '{"b": 2}\n',
            encoding="utf-8",
        )
        assert load_jsonl(path) == [{"a": 1}, {"b": 2}]

    def test_preserves_order(self, tmp_path) -> None:
        path = tmp_path / "events.jsonl"
        path.write_text(
            '{"step": 3}\n'
            '{"step": 1}\n'
            '{"step": 2}\n',
            encoding="utf-8",
        )
        rows = load_jsonl(path)
        assert [row["step"] for row in rows] == [3, 1, 2]


class TestAppendJsonl:
    def test_appends_one_object_per_line(self, tmp_path) -> None:
        path = tmp_path / "events.jsonl"
        append_jsonl(path, {"a": 1})
        append_jsonl(path, {"b": 2})
        lines = path.read_text(encoding="utf-8").splitlines()
        assert lines == ['{"a": 1}', '{"b": 2}']

    def test_sorted_keys_in_each_line(self, tmp_path) -> None:
        # Sorted keys are required so step_results.jsonl is diffable across
        # runs even when Python dict ordering varies.
        path = tmp_path / "events.jsonl"
        append_jsonl(path, {"z": 1, "a": 2, "m": 3})
        line = path.read_text(encoding="utf-8").rstrip("\n")
        # Reparse and check key order is alphabetical in the serialized form.
        keys_in_order = [k for k, _ in json.JSONDecoder(object_pairs_hook=list).decode(line)]
        assert keys_in_order == ["a", "m", "z"]

    def test_roundtrip_with_load_jsonl(self, tmp_path) -> None:
        path = tmp_path / "events.jsonl"
        rows = [{"id": 1, "label": "first"}, {"id": 2, "label": "second"}]
        for row in rows:
            append_jsonl(path, row)
        assert load_jsonl(path) == rows
