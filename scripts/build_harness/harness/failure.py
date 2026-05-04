"""Failure-signature heuristics shared by the CLI runner and TUI runner.

Two helpers and two pattern lists:

- ``classify_signature(text)`` returns ``"transient"`` / ``"deterministic"`` /
  ``"unknown"`` based on substring matches against the pattern lists. Used by
  the scenario runner to decide whether to retry a failed CCI step.

- ``infer_failure_signature(lines)`` walks a buffered tail of stdout in reverse
  and returns the first line that looks like an error message (skipping the
  generic ``"cci error --help"`` / ``"debugging errors"`` noise that CCI prints
  on every non-zero exit). Falls back to the final line if no error-keyword
  line is found, and returns ``""`` for an empty input.

Keeping both implementations in one module guarantees the CLI and TUI agree on
what counts as a "transient" failure (worth retrying) and what counts as the
human-readable failure_signature shown in reports and the TUI banner.
"""

from __future__ import annotations

from typing import Iterable, List

# Substrings (lowercased) that strongly suggest a network-/availability-level
# blip worth one or two retries before giving up.
TRANSIENT_PATTERNS: tuple[str, ...] = (
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

# Substrings (lowercased) that strongly suggest a config/code defect that will
# fail again on retry. Treat these as terminal and surface to the operator.
DETERMINISTIC_PATTERNS: tuple[str, ...] = (
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
    "command not found",
    "file not found",
    "metadata not found",
    "no such file or directory",
)

# Lines we never want to surface as the failure signature. CCI prints these on
# every non-zero exit; they are pointers to its own help output, not the actual
# failure cause.
_SIGNATURE_NOISE: tuple[str, ...] = (
    "cci error --help",
    "debugging errors",
)

# Lowercase substrings that mark a line as "looks like an error message" while
# walking the tail of captured stdout.
_SIGNATURE_KEYWORDS: tuple[str, ...] = (
    "error",
    "exception",
    "failed",
    "traceback",
)


def classify_signature(text: str) -> str:
    """Bucket a failure signature into transient / deterministic / unknown."""
    lowered = text.lower()
    if any(token in lowered for token in TRANSIENT_PATTERNS):
        return "transient"
    if any(token in lowered for token in DETERMINISTIC_PATTERNS):
        return "deterministic"
    return "unknown"


def infer_failure_signature(lines: Iterable[str]) -> str:
    """Pick the most informative error line from a buffered command tail.

    Walks ``lines`` in reverse, skipping CCI's generic help noise, and returns
    the first line containing an error/exception/failed/traceback keyword. If
    no such line is found, falls back to the last non-noise line (or simply
    the last line). Returns ``""`` when ``lines`` is empty.
    """
    materialized: List[str] = list(lines)
    if not materialized:
        return ""
    for candidate in reversed(materialized):
        lowered = candidate.lower()
        if any(noise in lowered for noise in _SIGNATURE_NOISE):
            continue
        if any(token in lowered for token in _SIGNATURE_KEYWORDS):
            return candidate.strip()
    return materialized[-1].strip()
