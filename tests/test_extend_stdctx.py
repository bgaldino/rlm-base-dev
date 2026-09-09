"""Unit tests for tasks/rlm_extend_stdctx.py — the context-definition recovery
window and failure-message split (todo 126 / #264-64).

`_recover_context_id` polls the org for a context definition by developerName
after the creating POST's connection drops. The bug: it gave up after a fixed
3 attempts / ~90s, while the POST it recovers from documents itself as taking
"5-10 minutes on some org types" — so the recovery window was sized for a fast
commit, not the slow one it exists to wait out. Fixed by polling on a total
time budget (_RECOVER_BUDGET_SECONDS) with capped exponential backoff instead
of a fixed attempt count.

No browser or CumulusCI runtime is needed: the task is built with `__new__`
(no `__init__`, no keychain/org), `_recover_context_id` only calls
`self.logger` / `self._build_url_and_headers` / `self._make_request`, and all
three are faked here. `sleep`/`monotonic` are passed in as fakes so the test
drives the elapsed-budget loop without waiting in real time.

Run:  <cci-venv-python> tests/test_extend_stdctx.py
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tasks.rlm_extend_stdctx import (  # noqa: E402
    ExtendStandardContext,
    _RECOVER_BUDGET_SECONDS,
    _RECOVER_MAX_INTERVAL,
    _MAX_RETRIES,
)


_passed = _total = 0


def check(label, cond):
    global _passed, _total
    _total += 1
    if cond:
        _passed += 1
        print(f"  [PASS] {label}")
    else:
        print(f"  [FAIL] {label}")


class _NullLogger:
    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


def _new_task():
    t = ExtendStandardContext.__new__(ExtendStandardContext)
    t.logger = _NullLogger()
    # _recover_context_id only needs a (url, headers) pair back; contents are
    # irrelevant to these tests since _make_request is faked below.
    t._build_url_and_headers = lambda endpoint: (f"https://example/{endpoint}", {})
    return t


class _FakeClock:
    """Drives monotonic()/sleep() without real time. Each sleep() call advances
    the clock by the requested duration and is recorded for assertion."""

    def __init__(self):
        self.now = 0.0
        self.sleeps = []

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


def test_recovers_after_more_than_the_old_attempt_cap():
    t = _new_task()
    clock = _FakeClock()
    calls = {"n": 0}

    def fake_make_request(method, url, headers=None, retryable=None, **kwargs):
        calls["n"] += 1
        # Miss for the first 6 probes (well past the old _MAX_RETRIES=3 cap),
        # then a hit.
        if calls["n"] < 7:
            return {"isSuccess": False}
        return {"isSuccess": True, "contextDefinitionId": "0ctXX0000000001"}

    t._make_request = fake_make_request
    result = t._recover_context_id(
        "Sales_Transaction_Context", sleep=clock.sleep, monotonic=clock.monotonic
    )
    check("recovers the id once a later probe hits", result == "0ctXX0000000001")
    check(
        "probed more times than the old fixed 3-attempt cap",
        calls["n"] > _MAX_RETRIES,
    )
    check("polled for less than the full budget (early hit)", clock.now < _RECOVER_BUDGET_SECONDS)


def test_exhausts_the_full_budget_when_never_visible():
    t = _new_task()
    clock = _FakeClock()

    def fake_make_request(method, url, headers=None, retryable=None, **kwargs):
        return {"isSuccess": False}

    t._make_request = fake_make_request
    result = t._recover_context_id(
        "Sales_Transaction_Context", sleep=clock.sleep, monotonic=clock.monotonic
    )
    check("returns None when the definition never becomes visible", result is None)
    check(
        "polls for materially longer than the old ~90s window",
        clock.now >= _RECOVER_BUDGET_SECONDS - 1,
    )
    check(
        "total simulated wait does not overshoot the budget by more than one interval",
        clock.now <= _RECOVER_BUDGET_SECONDS + _RECOVER_MAX_INTERVAL,
    )
    check(
        "no single backoff interval exceeds the configured cap",
        all(s <= _RECOVER_MAX_INTERVAL for s in clock.sleeps),
    )
    check(
        "backoff grows rather than staying flat "
        "(the final interval may be clipped shorter to fit the remaining budget)",
        max(clock.sleeps) > clock.sleeps[0],
    )


def test_probe_timeout_is_capped_to_the_remaining_budget():
    # A probe issued near the deadline must not itself be allowed to hang for
    # the full default (connect, read) timeout -- that could blow well past
    # _RECOVER_BUDGET_SECONDS on its own. Each probe's timeout should be
    # capped to what's left of the budget.
    t = _new_task()
    clock = _FakeClock()
    seen_timeouts = []

    def fake_make_request(method, url, headers=None, retryable=None, timeout=None, **kwargs):
        seen_timeouts.append(timeout)
        return {"isSuccess": False}

    t._make_request = fake_make_request
    t._recover_context_id(
        "Sales_Transaction_Context", sleep=clock.sleep, monotonic=clock.monotonic
    )
    check("every probe passed an explicit timeout", all(tm is not None for tm in seen_timeouts))
    check(
        "no probe's timeout exceeds the remaining budget at the time it was issued",
        all(connect <= _RECOVER_BUDGET_SECONDS and read <= _RECOVER_BUDGET_SECONDS
            for connect, read in seen_timeouts),
    )
    check(
        "the final probe's timeout is capped well below the default 600s read timeout",
        seen_timeouts[-1][1] < 600,
    )


def test_failure_messages_are_distinct_and_carry_the_right_guidance():
    t = _new_task()
    network_msg = t._recovery_failure_message("Sales_Transaction_Context", "network_drop")
    missing_id_msg = t._recovery_failure_message("Sales_Transaction_Context", "missing_id")
    dup_msg = t._recovery_failure_message("Sales_Transaction_Context", "duplicate_value")

    check("the three reasons produce distinct messages",
          len({network_msg, missing_id_msg, dup_msg}) == 3)
    check(
        "network_drop message tells the operator to re-run",
        "re-run" in network_msg.lower(),
    )
    check(
        "network_drop message explains the DUPLICATE_VALUE auto-recovery path",
        "duplicate_value" in network_msg.lower(),
    )
    check(
        "network_drop message claims the connection dropped",
        "connection drop" in network_msg.lower(),
    )
    check(
        "missing_id message does not falsely claim the connection dropped",
        "connection drop" not in missing_id_msg.lower(),
    )
    check(
        "missing_id message still tells the operator to re-run",
        "re-run" in missing_id_msg.lower(),
    )
    check(
        "duplicate_value message points at a visibility/permission problem",
        "visibility" in dup_msg.lower() or "permission" in dup_msg.lower(),
    )
    check(
        "duplicate_value message points at the Connect-API inspect path",
        "context-service" in dup_msg,
    )
    check(
        "duplicate_value message also names the same-Name/different-developerName "
        "collision case, not just visibility/permission",
        "developername" in dup_msg.lower() and "name" in dup_msg.lower(),
    )


def main():
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    print(f"Running {len(tests)} test groups...\n")
    for t in tests:
        t()
    print(f"\n{_passed}/{_total} checks passed.")
    return 0 if _passed == _total else 1


if __name__ == "__main__":
    sys.exit(main())
