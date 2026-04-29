from __future__ import annotations

import datetime as dt
import subprocess
import time
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

TRANSIENT_PATTERNS = (
    "timed out",
    "timeout",
    "connection reset",
    "temporarily unavailable",
    "503",
    "502",
    "429",
    "service unavailable",
    "network is unreachable",
    "name or service not known",
)

DETERMINISTIC_PATTERNS = (
    "invalid field",
    "no such column",
    "malformed",
    "yaml",
    "traceback",
    "assertionerror",
    "keyerror",
    "validation error",
    "does not exist",
    "unknown option",
    "not found",
)


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def make_run_id() -> str:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"run-{stamp}"


def classify_signature(text: str) -> str:
    lowered = text.lower()
    if any(token in lowered for token in TRANSIENT_PATTERNS):
        return "transient"
    if any(token in lowered for token in DETERMINISTIC_PATTERNS):
        return "deterministic"
    return "unknown"


def run_command(
    root: Path,
    command: Sequence[str],
    log_path: Path,
    print_prefix: str = "",
    cwd: Optional[Path] = None,
) -> Dict[str, Any]:
    start = time.monotonic()
    started_at = now_utc()
    tail = deque(maxlen=250)

    with log_path.open("a", encoding="utf-8") as log_handle:
        log_handle.write(f"\n[{started_at}] COMMAND: {' '.join(command)}\n")
        log_handle.flush()

        process = subprocess.Popen(
            list(command),
            cwd=str(cwd or root),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            tail.append(line.rstrip("\n"))
            log_handle.write(line)
            print(f"{print_prefix}{line}" if print_prefix else line, end="")
        process.wait()

    duration = round(time.monotonic() - start, 3)
    lines = list(tail)
    signature_line = ""
    for candidate in reversed(lines):
        low = candidate.lower()
        if "cci error --help" in low or "debugging errors" in low:
            continue
        if any(token in low for token in ("error", "exception", "failed", "traceback")):
            signature_line = candidate.strip()
            break
    if not signature_line and lines:
        signature_line = lines[-1].strip()

    return {
        "started_at": started_at,
        "finished_at": now_utc(),
        "duration_seconds": duration,
        "exit_code": int(process.returncode),
        "failure_signature": signature_line,
        "failure_class": classify_signature(signature_line) if process.returncode != 0 else "none",
        "tail": lines[-20:],
    }


def org_exists(root: Path, alias: str) -> bool:
    result = subprocess.run(
        ["cci", "org", "info", alias],
        cwd=str(root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0
