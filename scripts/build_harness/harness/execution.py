from __future__ import annotations

import datetime as dt
import json
import re
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


def _gone_detail(org: Dict[str, Any], sf_alias: str) -> Optional[str]:
    """Why an `sf` org record is no longer usable, or None when it still is.

    Trusts only the status that `sf` itself reports (Expired or Deleted, or
    `isExpired`). `expirationDate` is deliberately not compared with today's date:
    ScratchOrgInfo.ExpirationDate carries no time zone, and a live org must never be
    declared gone on its last day (`missing` blocks resume).
    """
    status = str(org.get("status") or "")
    if status.lower() in _GONE_ORG_STATUSES:
        return f"Org `{sf_alias}` has status {status}."
    if org.get("isExpired") is True:
        return f"Org `{sf_alias}` is expired."
    return None


def _local_org_record(root: Path, sf_alias: str, timeout: float) -> Optional[Dict[str, Any]]:
    """Find the org in `sf org list --all --skip-connection-status --json`.

    Matches the alias, any entry of an `aliases` list, or the username. Not
    local-only: `--skip-connection-status` skips only the per-org connection check of
    non-scratch orgs. plugin-org's `processScratchOrgs` still queries ScratchOrgInfo on
    the dev hub for every scratch org (read from plugin-org 7.0.13 `orgListUtil.js`),
    and that query is what supplies `status`, `isExpired` and `expirationDate`. When
    the hub cannot be queried, scratch orgs are dropped from the list, so an absent org
    is not evidence that the org is gone. Needs no CumulusCI.

    Returns the org record, `{}` when the list was read and no entry matches, or
    None when the list could not be read.
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
            if not isinstance(org, dict):
                continue
            names = {org.get("alias"), org.get("username")}
            aliases = org.get("aliases")
            if isinstance(aliases, list):
                names.update(a for a in aliases if isinstance(a, str))
            if sf_alias in names:
                return org
    return {}


def probe_org(
    root: Path,
    sf_alias: str,
    *,
    timeout: float = ORG_PROBE_TIMEOUT_SECONDS,
) -> Dict[str, str]:
    """Check that a scratch org is still usable, without any CumulusCI call.

    Runs `sf org display --target-org <sf_alias> --json`. Unlike `cci org info`, it
    cannot reach CumulusCI's expired-org recreation (`check_org_expired`), and it took
    1-3 seconds where `cci org info` took 9-27 seconds on the same org. When display
    fails for any reason other than an unknown alias (an expired org can fail on its
    token refresh), `sf org list --all --skip-connection-status` is consulted. That list
    is not network-free (it reads each scratch org's status from the dev hub), so it can
    cost a second timeout. Only positive evidence gives `missing`: display reporting an
    unknown alias, or a list record that is Expired, Deleted or `isExpired`. An alias absent from the
    list, or an unreadable list, leaves the state `error` (unknown).

    Returns {"state": ..., "detail": ...} where state is one of:
      present - the org is authenticated and `sf` does not report it Expired, Deleted or `isExpired`
      missing - no authorization for the alias, or `sf` reports the org Expired, Deleted or `isExpired`
                (never decided from `expirationDate` and today's date)
      timeout - the probe did not finish in time; the org's state is unknown
      error   - the probe could not run or its output was unreadable; state unknown
    """
    if not root.is_dir():
        return {"state": "error", "detail": f"Working directory does not exist: {root}"}
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
    except (OSError, ValueError) as exc:  # ValueError includes UnicodeDecodeError
        return {"state": "error", "detail": f"`sf org display` could not run or be read: {exc!r}"}

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
        gone = _gone_detail(org, sf_alias)
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
            return {"state": "error", "detail": f"`{sf_alias}` is not in `sf org list` (the dev hub may be unreachable). {failure}"}
        gone = _gone_detail(local, sf_alias)
        if gone:
            return {"state": "missing", "detail": f"{gone} {failure}"}
    return {"state": "error", "detail": failure}


_CUSTOM_KEY_LINE = re.compile(r"^([A-Za-z_][\w.-]*):(?:\s+(.*))?$")


class PreflightFailure(str):
    """A preflight failure message that also carries its failure class."""

    failure_class: str

    def __new__(cls, message: str, failure_class: str) -> "PreflightFailure":
        obj = super().__new__(cls, message)
        obj.failure_class = failure_class
        return obj


def _parse_project_info_custom(output: str) -> Dict[str, str]:
    """Read the top-level `custom:` block of `cci project info` as name -> text.

    The output looks like YAML but is not (a value such as `Sandbox orgs: ` breaks a
    YAML parser), so read the block by indentation: one `name: value` line per flag
    directly under `custom:`; deeper lines (lists, mappings) are not flags.
    """
    flags: Dict[str, str] = {}
    in_block = False
    block_indent: Optional[int] = None
    for line in output.splitlines():
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent == 0:
            in_block = line.rstrip() == "custom:"
            block_indent = None
            continue
        if not in_block:
            continue
        if block_indent is None:
            block_indent = indent
        if indent != block_indent:
            continue
        # A multi-line string value continues on lines that are not `key: value` or
        # `key:`; ignore them rather than reading their text as a flag.
        match = _CUSTOM_KEY_LINE.match(line.strip())
        if match:
            flags[match.group(1)] = (match.group(2) or "").strip()
    return flags


_WORKTREE_HINT = (
    "CumulusCI's project root is the first folder upward from the working directory whose "
    ".git is a directory; start the build from the main checkout or a regular git clone, "
    "not a git worktree."
)


def verify_project_flags(
    project_root: Path,
    effective_flags: Dict[str, Any],
    *,
    timeout: float = 60,
) -> Optional[str]:
    """Check that CumulusCI, run from ``project_root``, loads the scenario's flags.

    Every ``when:`` check in a flow, including those of the nested flows' tasks, is
    evaluated against the ``project.custom`` that CumulusCI itself loaded. The
    harness writes the scenario's flags into the workspace's generated
    ``cumulusci.yml``, but CumulusCI takes as its project root the first folder
    upward from the working directory whose ``.git`` is a directory. When that is
    not the workspace (the build started from a git worktree, where ``.git`` is a
    file), CumulusCI loads another checkout's defaults and silently skips every
    task whose flag the scenario turned on. `cci project info` prints the
    ``project.custom`` CumulusCI loaded, read-only and without an org.

    Two checks, because each catches a different case:

    1. ``project_root/.git`` must be a directory. The workspace symlinks the checkout's
       ``.git`` entry, so this is false exactly when the build started from a git
       worktree. That case is not caught by the flag comparison when the scenario's
       overrides happen to equal the enclosing checkout's defaults, yet CumulusCI would
       still take that checkout's ``tasks/`` and ``robot/`` results.
    2. ``cci project info`` must print the scenario's boolean flags. This catches a
       project root that resolves to some other checkout with other defaults, however
       it came about.

    Returns None when both pass, otherwise a ``PreflightFailure`` (a ``str`` that also
    carries ``failure_class``): ``deterministic`` for what is wrong with the setup,
    ``transient`` for a timeout, ``unknown`` when ``cci`` could not run or report.
    """
    if not (project_root / ".git").is_dir():
        return PreflightFailure(
            f"{project_root} has no `.git` directory, so CumulusCI would not take it as the project root "
            "and would build with another checkout's tasks and flag defaults. " + _WORKTREE_HINT,
            "deterministic",
        )
    try:
        result = subprocess.run(
            ["cci", "project", "info"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return PreflightFailure(
            f"`cci project info` did not finish within {timeout:g}s in {project_root}; cannot confirm the scenario flags: {exc!r}",
            "transient",
        )
    except (FileNotFoundError, OSError) as exc:
        return PreflightFailure(
            f"Could not run `cci project info` in {project_root} to confirm the scenario flags: {exc!r}",
            "unknown",
        )
    if result.returncode != 0:
        return PreflightFailure(
            f"`cci project info` exited {result.returncode} in {project_root}; cannot confirm the scenario flags.",
            "unknown",
        )
    custom = _parse_project_info_custom(result.stdout or "")
    if not custom:
        return PreflightFailure("`cci project info` printed no `custom:` block; cannot confirm the scenario flags.", "deterministic")

    # `when:` expressions read boolean flags; the rest of project.custom (the
    # `rlm_*_api_names`, `ps_*` and `dt_*` lists) is data, which `cci project info`
    # prints as a bare key over indented items.
    checked = {name: wanted for name, wanted in effective_flags.items() if isinstance(wanted, bool)}
    if not checked:
        return PreflightFailure(
            "The scenario has no boolean flags to check against `cci project info`; cannot confirm them.", "deterministic"
        )
    mismatches = []
    for name, wanted in checked.items():
        if name not in custom:
            mismatches.append(f"{name}: scenario {wanted!r}, absent from CumulusCI's project.custom")
        elif custom[name] != str(wanted):
            mismatches.append(f"{name}: scenario {wanted!r}, CumulusCI loaded {custom[name]!r}")
    if not mismatches:
        return None
    return PreflightFailure(
        "CumulusCI did not load the scenario's flags from the generated workspace, so `when:` checks "
        "inside flows would skip tasks the scenario enables. Mismatches: "
        + "; ".join(mismatches)
        + ". "
        + _WORKTREE_HINT,
        "deterministic",
    )
