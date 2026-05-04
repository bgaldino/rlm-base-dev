from __future__ import annotations

import datetime as dt
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
            process.terminate()

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
) -> Dict[str, Any]:
    started_at = now_utc()
    with log_path.open("a", encoding="utf-8") as log_handle:
        log_handle.write(f"\n[{started_at}] COMMAND: {' '.join(command)}\n")
        log_handle.flush()

        def _handle_line(line: str) -> None:
            log_handle.write(f"{line}\n")
            print(f"{print_prefix}{line}" if print_prefix else line)

        stream_result = run_command_stream(
            command,
            cwd=(cwd or root),
            on_line=_handle_line,
        )

    duration = float(stream_result["duration_seconds"])
    signature_line = str(stream_result["failure_signature"])
    exit_code = int(stream_result["exit_code"])

    return {
        "started_at": started_at,
        "finished_at": now_utc(),
        "duration_seconds": duration,
        "exit_code": exit_code,
        "failure_signature": signature_line,
        "failure_class": classify_signature(signature_line) if exit_code != 0 else "none",
        "tail": list(stream_result.get("tail", [])),
    }


def org_exists(root: Path, alias: str) -> bool:
    try:
        result = subprocess.run(
            ["cci", "org", "info", alias],
            cwd=str(root),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return False
    return result.returncode == 0
