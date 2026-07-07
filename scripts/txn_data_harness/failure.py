"""Failure-signature classification for scenario-level retry decisions.

Adapted from ``scripts/build_harness/harness/failure.py``. The build harness
bucketed CCI subprocess output; here we bucket exception messages raised by the
lifecycle steps (``LifecycleError``) and the REST transport (``SfApiError``).

``classify_signature(text)`` returns ``"transient"`` / ``"deterministic"`` /
``"unknown"``. The runner retries only ``"transient"`` failures; everything else
fails fast so a config/code defect is surfaced to the operator immediately.

``classify_exception(exc)`` is the preferred entry point: it inspects an
``SfApiError``'s HTTP status directly (a 429/5xx is transient regardless of body
wording) before falling back to message-substring matching.
"""

from __future__ import annotations

from .auth import SfApiError

# Substrings (lowercased) that suggest a network-/availability-/contention-level
# blip worth one or two retries before giving up. Includes the generic transport
# markers plus Salesforce row-lock and limit codes that clear on retry.
TRANSIENT_PATTERNS: tuple[str, ...] = (
    "timed out",
    "timeout",
    "connection reset",
    "temporarily unavailable",
    "service unavailable",
    "server_unavailable",
    "network is unreachable",
    "503",
    "502",
    "504",
    "429",
    "unable_to_lock_row",
    "unable to obtain exclusive access",
    "request_limit_exceeded",
    "query_timeout",
)

# Substrings (lowercased) that suggest a config/code defect that will fail again
# on retry. Includes the harness's own precondition guards ("is required before")
# from steps.py plus common deterministic Salesforce API faults.
DETERMINISTIC_PATTERNS: tuple[str, ...] = (
    "is required before",
    "invalid_field",
    "invalid field",
    "malformed_query",
    "malformed query",
    "required_field_missing",
    "field_integrity_exception",
    "insufficient_access",
    "entity_is_deleted",
    "no such column",
    "not found",
    "does not exist",
)

# Salesforce HTTP statuses that are always worth a retry, independent of the
# response body wording.
_TRANSIENT_STATUS: frozenset[int] = frozenset({420, 429, 500, 502, 503, 504})


def classify_signature(text: str) -> str:
    """Bucket a failure message into transient / deterministic / unknown.

    Transient patterns are checked first so a contention error that also happens
    to mention a field name is still treated as retryable.
    """
    lowered = (text or "").lower()
    if any(token in lowered for token in TRANSIENT_PATTERNS):
        return "transient"
    if any(token in lowered for token in DETERMINISTIC_PATTERNS):
        return "deterministic"
    return "unknown"


def classify_exception(exc: BaseException) -> str:
    """Classify a raised exception, preferring HTTP status over message text.

    An ``SfApiError`` carries a ``.status``; a 429/5xx is transient regardless of
    body wording. Everything else defers to :func:`classify_signature` over the
    exception's string form.
    """
    if isinstance(exc, SfApiError) and exc.status in _TRANSIENT_STATUS:
        return "transient"
    return classify_signature(str(exc))
