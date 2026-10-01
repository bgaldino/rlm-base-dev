#!/usr/bin/env python3
"""Offline tests for scripts/sf_token.py (stdlib only; sf is stubbed)."""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import sf_token as m  # noqa: E402

ALIAS = "my-scratch"
TOKEN = "00DAB0000000001!AQEAQ.secret-token-value"
REDACTED = "[REDACTED] Use 'sf org auth show-access-token' to view."
INSTANCE = "https://example.my.salesforce.com/"

_PASS = 0
_FAIL = 0


def check(name, condition, detail=None):
    global _PASS, _FAIL
    if condition:
        _PASS += 1
        print(f"  [PASS] {name}")
    else:
        _FAIL += 1
        print(f"  [FAIL] {name}" + (f" -- {detail}" if detail is not None else ""))


def _completed(returncode=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(args=[], returncode=returncode,
                                       stdout=stdout, stderr=stderr)


def _display(token=TOKEN, instance=INSTANCE):
    result = {"instanceUrl": instance} if instance else {}
    if token is not None:
        result["accessToken"] = token
    return _completed(stdout=json.dumps({"status": 0, "result": result}))


def _show(token=TOKEN):
    return _completed(stdout=json.dumps({"status": 0, "result": {"accessToken": token}}))


def _run(responses, alias=ALIAS):
    """Call org_auth with subprocess.run answering from ``responses`` in order."""
    calls = []
    queue = list(responses)
    original = m.subprocess.run

    def fake_run(cmd, **kw):
        calls.append(cmd)
        response = queue.pop(0)
        if isinstance(response, BaseException):
            raise response
        return response

    m.subprocess.run = fake_run
    try:
        return m.org_auth(alias), calls, None
    except Exception as exc:  # noqa: BLE001 -- the test inspects whatever was raised
        return None, calls, exc
    finally:
        m.subprocess.run = original


def _no_leak(label, error):
    check(f"{label}: token not in the error", error is None or TOKEN not in str(error), error)


def test_real_token_from_display():
    print("test_real_token_from_display")
    result, calls, error = _run([_display()])
    check("returns instance URL without trailing slash and the token",
          result == (INSTANCE.rstrip("/"), TOKEN), result)
    check("one sf call, no fallback", len(calls) == 1, calls)
    check("calls sf org display with --json",
          calls and calls[0][:3] == ["sf", "org", "display"] and "--json" in calls[0], calls)


def test_redacted_or_missing_token_falls_back():
    print("test_redacted_or_missing_token_falls_back")
    for label, display in (("redacted", _display(token=REDACTED)),
                           ("missing", _display(token=None))):
        result, calls, error = _run([display, _show()])
        check(f"{label}: returns the fallback token", result == (INSTANCE.rstrip("/"), TOKEN),
              (result, error))
        check(f"{label}: second call is show-access-token",
              len(calls) == 2 and calls[1][:4] == ["sf", "org", "auth", "show-access-token"],
              calls)
        check(f"{label}: fallback targets the alias", len(calls) == 2 and ALIAS in calls[1], calls)


def test_failures_raise_named_and_without_token():
    print("test_failures_raise_named_and_without_token")
    cases = [
        ("display non-zero exit", [_completed(returncode=1, stderr="NoOrgFound")],
         ["org display", "rc=1", "NoOrgFound"], 1),
        ("missing instanceUrl", [_display(instance=None)], ["instanceUrl"], 1),
        ("fallback non-zero exit",
         [_display(token=REDACTED), _completed(returncode=1, stderr="auth expired")],
         ["show-access-token", "rc=1"], 2),
        ("fallback non-JSON", [_display(token=REDACTED), _completed(stdout=f"Token: {TOKEN}")],
         ["non-JSON"], 2),
        ("fallback still redacted", [_display(token=REDACTED), _show(token=REDACTED)],
         ["did not return a usable"], 2),
        ("fallback timeout",
         [_display(token=REDACTED), subprocess.TimeoutExpired(cmd="sf", timeout=60)],
         ["timed out after 60"], 2),
    ]
    for label, responses, fragments, n_calls in cases:
        result, calls, error = _run(responses)
        check(f"{label}: raises SfTokenError", isinstance(error, m.SfTokenError), error)
        check(f"{label}: names the alias", error is not None and ALIAS in str(error), error)
        for fragment in fragments:
            check(f"{label}: message has {fragment!r}",
                  error is not None and fragment in str(error), error)
        check(f"{label}: made {n_calls} sf call(s)", len(calls) == n_calls, calls)
        _no_leak(label, error)
    # The non-JSON stdout holds the token; its decode error must not be chained.
    _, _, error = _run([_display(token=REDACTED), _completed(stdout=f"Token: {TOKEN}")])
    check("non-JSON: decode error not chained",
          error is not None and error.__cause__ is None and error.__suppress_context__)


def test_requires_alias():
    print("test_requires_alias")
    result, calls, error = _run([], alias="")
    check("empty alias raises SfTokenError", isinstance(error, m.SfTokenError), error)
    check("empty alias makes no sf call", calls == [], calls)


def test_token_rule():
    print("test_token_rule")
    check("00D-prefixed token is real", m.looks_like_a_real_token(TOKEN))
    check("placeholder is not real", not m.looks_like_a_real_token(REDACTED))
    check("None is not real", not m.looks_like_a_real_token(None))


def main():
    for fn in (test_real_token_from_display, test_redacted_or_missing_token_falls_back,
               test_failures_raise_named_and_without_token, test_requires_alias,
               test_token_rule):
        fn()
    print(f"\n{_PASS} passed, {_FAIL} failed.")
    return 1 if _FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
