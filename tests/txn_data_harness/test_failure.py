"""Tests for the scenario-failure classifier."""

from __future__ import annotations

import pytest

from scripts.txn_data_harness.auth import SfApiError
from scripts.txn_data_harness.failure import classify_exception, classify_signature
from scripts.txn_data_harness.lifecycle import LifecycleError


@pytest.mark.parametrize("text", [
    "request timed out after 180s",
    "HTTP 503: service unavailable",
    "UNABLE_TO_LOCK_ROW: unable to obtain exclusive access to this record",
    "REQUEST_LIMIT_EXCEEDED",
    "connection reset by peer",
])
def test_transient_messages(text: str) -> None:
    assert classify_signature(text) == "transient"


@pytest.mark.parametrize("text", [
    "[order] quote_id is required before order",
    "INVALID_FIELD: no such column 'Foo__c'",
    "REQUIRED_FIELD_MISSING: missing required field",
    "MALFORMED_QUERY: unexpected token",
])
def test_deterministic_messages(text: str) -> None:
    assert classify_signature(text) == "deterministic"


def test_unknown_message() -> None:
    assert classify_signature("something weird happened") == "unknown"
    assert classify_signature("") == "unknown"


def test_transient_wins_over_deterministic() -> None:
    # A row-lock error that also mentions a field is still retryable.
    assert classify_signature("UNABLE_TO_LOCK_ROW on field invalid_field") == "transient"


def test_classify_exception_uses_http_status() -> None:
    # A 500 with a generic body is transient even if the body lacks a keyword.
    exc = SfApiError(500, "internal error", "POST", "/x")
    assert classify_exception(exc) == "transient"


def test_classify_exception_falls_back_to_message() -> None:
    exc = LifecycleError("order", "quote_id is required before order")
    assert classify_exception(exc) == "deterministic"
