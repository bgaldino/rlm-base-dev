"""Tests for scripts.build_harness.harness.execution."""

from __future__ import annotations

import datetime as dt
import json
import re
import subprocess
import sys
from threading import Event

import pytest

from scripts.build_harness.harness.execution import (
    ORG_PROBE_TIMEOUT_SECONDS,
    make_run_id,
    probe_org,
    run_command,
    run_command_stream,
    sf_alias_for,
)


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


def test_run_command_stream_emits_output(tmp_path) -> None:
    lines = []
    result = run_command_stream(
        [sys.executable, "-c", "print('hello-from-stream')"],
        cwd=tmp_path,
        on_line=lines.append,
    )
    assert result["exit_code"] == 0
    assert "hello-from-stream" in lines
    assert "hello-from-stream" in result["tail"]


def test_run_command_stream_honors_stop_event(tmp_path) -> None:
    stop_event = Event()
    seen = {"count": 0}

    def _on_line(line: str) -> None:
        if "tick-" in line:
            seen["count"] += 1
            if seen["count"] == 1:
                stop_event.set()

    result = run_command_stream(
        [
            sys.executable,
            "-c",
            (
                "import time\n"
                "for i in range(50):\n"
                "    print(f'tick-{i}', flush=True)\n"
                "    time.sleep(0.1)\n"
            ),
        ],
        cwd=tmp_path,
        stop_event=stop_event,
        on_line=_on_line,
    )
    assert seen["count"] >= 1
    assert result["exit_code"] != 0


def test_run_command_can_suppress_stdout(tmp_path, capsys) -> None:
    log_path = tmp_path / "scenario.log"
    run_command(
        tmp_path,
        [sys.executable, "-c", "print('hidden-line')"],
        log_path,
        emit_output=False,
    )
    captured = capsys.readouterr()
    assert "hidden-line" not in captured.out
    assert "hidden-line" in log_path.read_text(encoding="utf-8")


def _fake_sf(monkeypatch, *, stdout="", returncode=0, stderr="", raises=None):
    calls = []

    class _Result:
        pass

    def _run(command, **kwargs):
        calls.append((command, kwargs))
        if raises is not None:
            raise raises
        result = _Result()
        result.stdout, result.returncode, result.stderr = stdout, returncode, stderr
        return result

    monkeypatch.setattr("scripts.build_harness.harness.execution.subprocess.run", _run)
    return calls


def test_sf_alias_for_joins_project_and_alias() -> None:
    assert sf_alias_for("rlm-base", "demo") == "rlm-base__demo"


def test_probe_org_present_uses_sf_not_cci(tmp_path, monkeypatch) -> None:
    payload = json.dumps({"status": 0, "result": {"status": "Active", "expirationDate": "2026-11-30"}})
    calls = _fake_sf(monkeypatch, stdout=payload)
    result = probe_org(tmp_path, "rlm-base__demo", today=dt.date(2026, 11, 24))
    assert result["state"] == "present"
    command, kwargs = calls[0]
    assert command[:3] == ["sf", "org", "display"]
    assert "cci" not in command
    assert kwargs["timeout"] == ORG_PROBE_TIMEOUT_SECONDS > 30


def test_probe_org_timeout_is_not_missing(tmp_path, monkeypatch) -> None:
    _fake_sf(monkeypatch, raises=subprocess.TimeoutExpired(cmd=["sf"], timeout=120))
    result = probe_org(tmp_path, "rlm-base__demo")
    assert result["state"] == "timeout"
    assert "120" in result["detail"]


def test_probe_org_not_found_is_missing(tmp_path, monkeypatch) -> None:
    payload = json.dumps({"status": 2, "name": "NamedOrgNotFoundError", "message": "No authorization"})
    _fake_sf(monkeypatch, stdout=payload, returncode=2)
    assert probe_org(tmp_path, "rlm-base__demo")["state"] == "missing"


@pytest.mark.parametrize("status", ["Expired", "Deleted"])
def test_probe_org_expired_or_deleted_status_is_missing(tmp_path, monkeypatch, status) -> None:
    _fake_sf(monkeypatch, stdout=json.dumps({"status": 0, "result": {"status": status}}))
    assert probe_org(tmp_path, "rlm-base__demo")["state"] == "missing"


def test_probe_org_past_expiration_date_is_missing(tmp_path, monkeypatch) -> None:
    payload = json.dumps({"status": 0, "result": {"status": "Active", "expirationDate": "2026-11-20"}})
    _fake_sf(monkeypatch, stdout=payload)
    result = probe_org(tmp_path, "rlm-base__demo", today=dt.date(2026, 11, 24))
    assert result["state"] == "missing"


def test_probe_org_other_failure_is_error_not_missing(tmp_path, monkeypatch) -> None:
    payload = json.dumps({"status": 1, "name": "GenericTimeoutError", "message": "socket hang up"})
    _fake_sf(monkeypatch, stdout=payload, returncode=1)
    result = probe_org(tmp_path, "rlm-base__demo")
    assert result["state"] == "error"
    assert "GenericTimeoutError" in result["detail"]


def test_probe_org_unparseable_output_is_error(tmp_path, monkeypatch) -> None:
    _fake_sf(monkeypatch, stdout="not json", stderr="boom", returncode=1)
    assert probe_org(tmp_path, "rlm-base__demo")["state"] == "error"


def test_probe_org_missing_sf_binary_is_error(tmp_path, monkeypatch) -> None:
    _fake_sf(monkeypatch, raises=FileNotFoundError())
    assert probe_org(tmp_path, "rlm-base__demo")["state"] == "error"
