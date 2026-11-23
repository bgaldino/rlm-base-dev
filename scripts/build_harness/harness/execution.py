from __future__ import annotations

import datetime as dt
import json
import subprocess
import time
from collections import deque
from pathlib import Path
from queue import Empty, Queue
from threading import Event, Thread
from typing import Any, Callable, Dict, Optional, Sequence

from scripts.build_harness.harness.failure import classify_signature, infer_failure_signature
from scripts.build_harness.harness.io import now_utc


def make_run_id() -> str:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"run-{stamp}"


def run_command_stream(
    command: Sequence[str],
    *,
    cwd: Path,
    stop_event: Optional[Event] = None,
    on_line: Optional[Callable[[str], None]] = None,
    on_detached: Optional[Callable[[], None]] = None,
) -> Dict[str, Any]:
    """Run a command, streaming output lines to callbacks while collecting tail."""
    started = time.monotonic()
    tail = deque(maxlen=250)
    command_list = list(command)

    try:
        process = subprocess.Popen(
            command_list,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except FileNotFoundError:
        signature = f"Command not found: {command_list[0]}"
        if on_line is not None:
            on_line(signature)
        return {
            "duration_seconds": 0.0,
            "exit_code": 127,
            "failure_signature": signature,
            "tail": [],
        }

    assert process.stdout is not None
    line_queue: "Queue[str]" = Queue()
    reader_done = Event()
    force_detached = False
    last_output_at = time.monotonic()

    def _read_stdout() -> None:
        try:
            for raw_line in process.stdout:
                line_queue.put(raw_line.rstrip("\n"))
        finally:
            reader_done.set()

    reader = Thread(target=_read_stdout, daemon=True)
    reader.start()

    # Grace period to wait after SIGTERM before escalating to SIGKILL, so a
    # subprocess that ignores (or is slow to honor) SIGTERM cannot wedge the loop.
    terminate_grace_seconds = 10.0
    terminate_requested_at: Optional[float] = None
    killed = False

    while True:
        drained_any = False
        try:
            while True:
                line = line_queue.get_nowait()
                drained_any = True
                last_output_at = time.monotonic()
                tail.append(line)
                if on_line is not None:
                    on_line(line)
        except Empty:
            pass

        if stop_event is not None and stop_event.is_set() and process.poll() is None:
            now = time.monotonic()
            if terminate_requested_at is None:
                process.terminate()
                terminate_requested_at = now
            elif not killed and now - terminate_requested_at > terminate_grace_seconds:
                process.kill()
                killed = True

        if process.poll() is not None:
            if reader_done.is_set():
                break
            if not drained_any and time.monotonic() - last_output_at > 1.0:
                force_detached = True
                if on_detached is not None:
                    on_detached()
                try:
                    process.stdout.close()
                except (OSError, ValueError):
                    pass
                break
        time.sleep(0.05)

    try:
        process.wait(timeout=30)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()

    try:
        while True:
            line = line_queue.get_nowait()
            tail.append(line)
            if on_line is not None:
                on_line(line)
    except Empty:
        pass

    duration = round(time.monotonic() - started, 3)
    signature = infer_failure_signature(list(tail))
    if force_detached and int(process.returncode or 0) == 0 and not signature:
        signature = "process exited with stdout detached"
    return {
        "duration_seconds": duration,
        "exit_code": int(process.returncode),
        "failure_signature": signature,
        "tail": list(tail)[-20:],
    }


def run_command(
    root: Path,
    command: Sequence[str],
    log_path: Path,
    print_prefix: str = "",
    cwd: Optional[Path] = None,
    emit_output: bool = True,
) -> Dict[str, Any]:
    started_at = now_utc()
    with log_path.open("a", encoding="utf-8") as log_handle:
        log_handle.write(f"\n[{started_at}] COMMAND: {' '.join(command)}\n")
        log_handle.flush()

        def _handle_line(line: str) -> None:
            log_handle.write(f"{line}\n")
            if emit_output:
                print(f"{print_prefix}{line}" if print_prefix else line)

        stream_result = run_command_stream(
            command,
            cwd=(cwd or root),
            on_line=_handle_line,
        )

    duration = float(stream_result["duration_seconds"])
    exit_code = int(stream_result["exit_code"])
    signature_line = str(stream_result["failure_signature"]) if exit_code != 0 else ""

    return {
        "started_at": started_at,
        "finished_at": now_utc(),
        "duration_seconds": duration,
        "exit_code": exit_code,
        "failure_signature": signature_line,
        "failure_class": classify_signature(signature_line) if exit_code != 0 else "none",
        "tail": list(stream_result.get("tail", [])),
    }


ORG_PROBE_TIMEOUT_SECONDS = 45

_GONE_ORG_STATUSES = {"expired", "deleted"}


def sf_alias_for(project_name: str, alias: str) -> str:
    """The Salesforce CLI alias CumulusCI gives a scratch org (`<project>__<alias>`)."""
    return f"{project_name}__{alias}"


def _utc_today() -> dt.date:
    return dt.datetime.now(dt.timezone.utc).date()


def _expired_detail(org: Dict[str, Any], sf_alias: str, today: dt.date) -> Optional[str]:
    """Why an `sf` org record is no longer usable, or None when it still is.

    An org that expires today is still usable; Salesforce removes it after that date.
    """
    status = str(org.get("status") or "")
    if status.lower() in _GONE_ORG_STATUSES:
        return f"Org `{sf_alias}` has status {status}."
    if org.get("isExpired") is True:
        return f"Org `{sf_alias}` is expired."
    expiration = org.get("expirationDate")
    if expiration:
        try:
            expires = dt.date.fromisoformat(str(expiration)[:10])
        except ValueError:
            return None
        if expires < today:
            return f"Org `{sf_alias}` expired on {expiration}."
    return None


def _local_org_record(root: Path, sf_alias: str, timeout: float) -> Optional[Dict[str, Any]]:
    """Find the alias in `sf org list --all --skip-connection-status --json`.

    Reads local auth files only (no network, no CumulusCI), and `--all` keeps
    expired and deleted orgs in the list. Returns the org record, `{}` when the
    list was read and the alias is not in it, or None when the list could not be read.
    """
    try:
        result = subprocess.run(
            ["sf", "org", "list", "--all", "--skip-connection-status", "--json"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        payload = json.loads(result.stdout or "")
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError, ValueError):
        return None
    org_result = payload.get("result") if isinstance(payload, dict) else None
    if result.returncode != 0 or not isinstance(org_result, dict):
        return None
    for group in org_result.values():
        if not isinstance(group, list):
            continue
        for org in group:
            if isinstance(org, dict) and org.get("alias") == sf_alias:
                return org
    return {}


def probe_org(
    root: Path,
    sf_alias: str,
    *,
    timeout: float = ORG_PROBE_TIMEOUT_SECONDS,
    today: Optional[dt.date] = None,
) -> Dict[str, str]:
    """Check that a scratch org is still usable, without any CumulusCI call.

    Runs `sf org display --target-org <sf_alias> --json`. Unlike `cci org info`, it
    cannot reach CumulusCI's expired-org recreation (`check_org_expired`), and it took
    1-3 seconds where `cci org info` took 9-27 seconds on the same org. When display
    fails for any reason other than an unknown alias (an expired org can fail on its
    token refresh), the local org list decides: an expired, deleted or absent org is
    `missing`; only an unreadable list leaves the state unknown.

    Returns {"state": ..., "detail": ...} where state is one of:
      present - the org is authenticated and not expired
      missing - no authorization for the alias, or the org is expired or deleted
      timeout - the probe did not finish in time; the org's state is unknown
      error   - the probe could not run or its output was unreadable; state unknown
    """
    today = today or _utc_today()
    try:
        result = subprocess.run(
            ["sf", "org", "display", "--target-org", sf_alias, "--json"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"state": "timeout", "detail": f"`sf org display` for `{sf_alias}` did not finish within {timeout:g}s."}
    except FileNotFoundError:
        return {"state": "error", "detail": "Command not found: sf"}

    try:
        payload = json.loads(result.stdout or "")
    except ValueError:
        payload = None
    if not isinstance(payload, dict):
        tail = (result.stderr or result.stdout or "").strip().splitlines()[-1:] or [""]
        failure = f"`sf org display` exited {result.returncode} without JSON output. {tail[0]}".strip()
    elif result.returncode == 0:
        org = payload.get("result")
        if not isinstance(org, dict):
            return {"state": "error", "detail": "`sf org display` returned no org record."}
        gone = _expired_detail(org, sf_alias, today)
        if gone:
            return {"state": "missing", "detail": gone}
        return {"state": "present", "detail": ""}
    elif payload.get("name") == "NamedOrgNotFoundError":
        return {"state": "missing", "detail": f"No authorization found for `{sf_alias}`."}
    else:
        message = str(payload.get("message") or "").strip().replace("\n", " ")
        failure = f"`sf org display` failed: {payload.get('name') or result.returncode}: {message}"

    local = _local_org_record(root, sf_alias, timeout)
    if local is not None:
        if not local:
            return {"state": "missing", "detail": f"No local authorization found for `{sf_alias}`. {failure}"}
        gone = _expired_detail(local, sf_alias, today)
        if gone:
            return {"state": "missing", "detail": f"{gone} {failure}"}
    return {"state": "error", "detail": failure}
