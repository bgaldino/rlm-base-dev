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


def _fake_sf(monkeypatch, *, stdout="", returncode=0, stderr="", raises=None, list_payload=None):
    """Fake `subprocess.run`: `sf org display` gets the given outcome; `sf org list` gets list_payload."""
    calls = []

    class _Result:
        pass

    def _run(command, **kwargs):
        calls.append((command, kwargs))
        result = _Result()
        if command[:3] == ["sf", "org", "list"]:
            result.returncode, result.stderr = (0, "") if list_payload is not None else (1, "")
            result.stdout = json.dumps(list_payload) if list_payload is not None else ""
            return result
        if raises is not None:
            raise raises
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
    assert kwargs["timeout"] == ORG_PROBE_TIMEOUT_SECONDS


def test_probe_org_timeout_is_not_missing(tmp_path, monkeypatch) -> None:
    _fake_sf(monkeypatch, raises=subprocess.TimeoutExpired(cmd=["sf"], timeout=45))
    result = probe_org(tmp_path, "rlm-base__demo")
    assert result["state"] == "timeout"
    assert "45" in result["detail"]


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


_FAILED_DISPLAY = json.dumps({"status": 1, "name": "RefreshTokenError", "message": "expired access/refresh token"})


def _org_list(*orgs):
    return {"status": 0, "result": {"scratchOrgs": list(orgs), "nonScratchOrgs": []}}


def test_probe_org_display_failure_with_locally_expired_org_is_missing(tmp_path, monkeypatch) -> None:
    listing = _org_list({"alias": "rlm-base__demo", "isExpired": True, "status": "Deleted", "expirationDate": "2026-11-13"})
    calls = _fake_sf(monkeypatch, stdout=_FAILED_DISPLAY, returncode=1, list_payload=listing)
    result = probe_org(tmp_path, "rlm-base__demo", today=dt.date(2026, 11, 24))
    assert result["state"] == "missing"
    assert "RefreshTokenError" in result["detail"]
    commands = [c for c, _ in calls]
    assert ["sf", "org", "list", "--all", "--skip-connection-status", "--json"] in commands
    assert not any(c[0] == "cci" for c in commands)


def test_probe_org_real_expired_org_error_shape_is_missing(tmp_path, monkeypatch) -> None:
    # Measured 2026-11-24: `sf org display` on a deleted scratch org exits 2 with
    # DomainNotFoundError, not NamedOrgNotFoundError; `sf org list --all` marks it Deleted.
    display = json.dumps({"status": 2, "name": "DomainNotFoundError", "message": "The org cannot be found"})
    listing = _org_list({"alias": "rlm-base__demo", "isExpired": True, "status": "Deleted", "expirationDate": "2026-11-13"})
    _fake_sf(monkeypatch, stdout=display, returncode=2, list_payload=listing)
    assert probe_org(tmp_path, "rlm-base__demo", today=dt.date(2026, 11, 24))["state"] == "missing"


def test_probe_org_display_failure_with_past_expiration_in_list_is_missing(tmp_path, monkeypatch) -> None:
    listing = _org_list({"alias": "rlm-base__demo", "isExpired": False, "expirationDate": "2026-11-20"})
    _fake_sf(monkeypatch, stdout=_FAILED_DISPLAY, returncode=1, list_payload=listing)
    assert probe_org(tmp_path, "rlm-base__demo", today=dt.date(2026, 11, 24))["state"] == "missing"


def test_probe_org_display_failure_with_alias_absent_from_list_is_missing(tmp_path, monkeypatch) -> None:
    _fake_sf(monkeypatch, stdout=_FAILED_DISPLAY, returncode=1, list_payload=_org_list({"alias": "other"}))
    assert probe_org(tmp_path, "rlm-base__demo")["state"] == "missing"


def test_probe_org_display_failure_with_live_org_in_list_stays_error(tmp_path, monkeypatch) -> None:
    listing = _org_list({"alias": "rlm-base__demo", "isExpired": False, "expirationDate": "2026-11-30", "status": "Active"})
    _fake_sf(monkeypatch, stdout=_FAILED_DISPLAY, returncode=1, list_payload=listing)
    assert probe_org(tmp_path, "rlm-base__demo", today=dt.date(2026, 11, 24))["state"] == "error"


def test_probe_org_display_failure_with_unreadable_list_stays_error(tmp_path, monkeypatch) -> None:
    _fake_sf(monkeypatch, stdout=_FAILED_DISPLAY, returncode=1, list_payload=None)
    assert probe_org(tmp_path, "rlm-base__demo")["state"] == "error"


def test_probe_org_expiring_today_is_still_present(tmp_path, monkeypatch) -> None:
    payload = json.dumps({"status": 0, "result": {"status": "Active", "expirationDate": "2026-11-24"}})
    _fake_sf(monkeypatch, stdout=payload)
    assert probe_org(tmp_path, "rlm-base__demo", today=dt.date(2026, 11, 24))["state"] == "present"


def test_probe_org_default_today_is_utc(tmp_path, monkeypatch) -> None:
    utc_today = dt.datetime.now(dt.timezone.utc).date()
    payload = json.dumps({"status": 0, "result": {"status": "Active", "expirationDate": utc_today.isoformat()}})
    _fake_sf(monkeypatch, stdout=payload)
    assert probe_org(tmp_path, "rlm-base__demo")["state"] == "present"


@pytest.mark.parametrize("result", [None, [], "Active"])
def test_probe_org_non_dict_result_is_error(tmp_path, monkeypatch, result) -> None:
    _fake_sf(monkeypatch, stdout=json.dumps({"status": 0, "result": result}))
    assert probe_org(tmp_path, "rlm-base__demo")["state"] == "error"


def test_probe_timeout_is_well_below_two_minutes() -> None:
    assert 10 < ORG_PROBE_TIMEOUT_SECONDS <= 45
