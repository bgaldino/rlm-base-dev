"""Tests for retention parsing and manifest pruning."""

from __future__ import annotations

import datetime as dt
import os

import pytest

from scripts.txn_data_harness.manifests import (
    parse_retention,
    prune_old_runs,
    write_manifest,
)
from scripts.txn_data_harness.models import Manifest


@pytest.mark.parametrize("text,expected", [
    ("30m", dt.timedelta(minutes=30)),
    ("24h", dt.timedelta(hours=24)),
    ("7d", dt.timedelta(days=7)),
    ("2w", dt.timedelta(weeks=2)),
    (" 45s ", dt.timedelta(seconds=45)),
])
def test_parse_retention_valid(text: str, expected: dt.timedelta) -> None:
    assert parse_retention(text) == expected


@pytest.mark.parametrize("text", ["", "0d", "-3d", "7x", "abc", "7"])
def test_parse_retention_invalid(text: str) -> None:
    with pytest.raises(ValueError):
        parse_retention(text)


def _out_dir(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    return out


def test_prune_refuses_unexpected_directory(tmp_path) -> None:
    bad = tmp_path / "datasets"
    bad.mkdir()
    with pytest.raises(ValueError, match="Refusing to prune"):
        prune_old_runs(dt.timedelta(days=1), manifest_dir=bad, dry_run=False)


def test_prune_dry_run_reports_but_keeps_files(tmp_path) -> None:
    out = _out_dir(tmp_path)
    old = write_manifest(Manifest(run_id="OLD"), manifest_dir=out)
    os.utime(old, (1, 1))  # epoch -> definitely older than any retention

    removed = prune_old_runs(
        dt.timedelta(seconds=1), manifest_dir=out, dry_run=True, safe_root=out
    )

    assert removed == [old]
    assert old.exists()  # dry run does not delete


def test_prune_deletes_only_files_past_cutoff(tmp_path) -> None:
    out = _out_dir(tmp_path)
    old = write_manifest(Manifest(run_id="OLD"), manifest_dir=out)
    new = write_manifest(Manifest(run_id="NEW"), manifest_dir=out)
    now = dt.datetime.now(dt.timezone.utc)
    os.utime(old, (1, 1))
    os.utime(new, (now.timestamp(), now.timestamp()))

    removed = prune_old_runs(
        dt.timedelta(hours=1), manifest_dir=out, dry_run=False, now=now, safe_root=out
    )

    assert removed == [old]
    assert not old.exists()
    assert new.exists()


def test_prune_rejects_zero_retention(tmp_path) -> None:
    with pytest.raises(ValueError):
        prune_old_runs(dt.timedelta(0), manifest_dir=_out_dir(tmp_path))
