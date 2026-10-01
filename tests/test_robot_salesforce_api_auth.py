#!/usr/bin/env python3
"""Offline tests for SalesforceAPI.py's sf CLI authentication.

robot/rlm-base/resources/SalesforceAPI.py reads its Bearer token from
``sf org display --json``. sf 2.145+ redacts ``result.accessToken`` there, so
the library must notice the placeholder and fall back to
``sf org auth show-access-token --json`` -- and must never put the token in a
log record or an exception message. These cases pin that behaviour.

`requests` and Robot Framework are stubbed in ``sys.modules`` before the
library loads, and ``subprocess.run`` is replaced with a fake, so no org is
contacted and nothing beyond the stdlib is needed.

Run:  python tests/test_robot_salesforce_api_auth.py
"""
import importlib.util
import json
import logging
import os
import subprocess
import sys
import types

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(_HERE, "..", "robot", "rlm-base", "resources", "SalesforceAPI.py")

ALIAS = "rlm-base__beta"
INSTANCE = "https://example.my.salesforce.com"
# Sentinels, not real credentials: shaped like a token so the "00D" check
# accepts them, distinctive so a leak into any message is easy to spot.
TOKEN = "00DFAKEORGID0001!SENTINEL-TOKEN-DO-NOT-LEAK"
REDACTED = "[REDACTED] Use 'sf org auth show-access-token' to view."


class _FakeBuiltIn:
    alias = ALIAS

    def get_variable_value(self, name, default=None):
        return self.alias if name == "${ORG_ALIAS}" else default


def _install_stubs():
    robot = types.ModuleType("robot")
    api = types.ModuleType("robot.api")
    deco = types.ModuleType("robot.api.deco")
    deco.keyword = lambda *a, **k: (a[0] if a and callable(a[0]) else (lambda f: f))
    libraries = types.ModuleType("robot.libraries")
    builtin = types.ModuleType("robot.libraries.BuiltIn")
    builtin.BuiltIn = _FakeBuiltIn
    sys.modules.update({
        "robot": robot, "robot.api": api, "robot.api.deco": deco,
        "robot.libraries": libraries, "robot.libraries.BuiltIn": builtin,
        "requests": types.ModuleType("requests"),
    })


_install_stubs()
_spec = importlib.util.spec_from_file_location("SalesforceAPI", _SRC)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

_PASS = 0
_FAIL = 0


def check(label, condition, detail=""):
    global _PASS, _FAIL
    if condition:
        _PASS += 1
    else:
        _FAIL += 1
        print(f"  FAIL: {label}" + (f"  ({detail})" if detail else ""))


def _completed(*, returncode=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(["sf"], returncode, stdout=stdout, stderr=stderr)


def _display(token=REDACTED, instance=INSTANCE + "/"):
    result = {"instanceUrl": instance, "username": "user@example.com"}
    if token is not None:
        result["accessToken"] = token
    return _completed(stdout=json.dumps({"status": 0, "result": result}))


def _show(token=TOKEN):
    return _completed(stdout=json.dumps({"status": 0, "result": {"accessToken": token}}))


class _Capture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


def _run(responses):
    """Authenticate a fresh library against scripted ``subprocess.run`` results.

    Each entry is a CompletedProcess or an exception to raise. Returns
    ``(lib, calls, error, log_messages)``.
    """
    calls = []
    queue = list(responses)

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        item = queue.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item

    capture = _Capture()
    m._logger.addHandler(capture)
    m._logger.setLevel(logging.DEBUG)
    original = m.subprocess.run
    m.subprocess.run = fake_run
    lib = m.SalesforceAPI()
    error = None
    try:
        lib._ensure_authenticated()
    except AssertionError as exc:
        error = exc
    finally:
        m.subprocess.run = original
        m._logger.removeHandler(capture)
    return lib, calls, error, capture.messages


def _no_leak(label, error, logs):
    text = " ".join(logs) + (str(error) if error else "")
    check(f"{label}: token absent from logs and error", TOKEN not in text)


def test_token_shape_check():
    print("test_token_shape_check")
    check("real token accepted", m._looks_like_a_real_token(TOKEN))
    check("redaction placeholder rejected", not m._looks_like_a_real_token(REDACTED))
    check("None rejected", not m._looks_like_a_real_token(None))
    check("empty rejected", not m._looks_like_a_real_token(""))
    check("non-string rejected", not m._looks_like_a_real_token(123))


def test_unredacted_display_token_used_without_fallback():
    print("test_unredacted_display_token_used_without_fallback")
    lib, calls, error, logs = _run([_display(token=TOKEN)])
    check("no error", error is None, error)
    check("only sf org display ran", calls == [["sf", "org", "display", "-o", ALIAS, "--json"]], calls)
    check("token from display used", lib._access_token == TOKEN)
    check("instance URL trailing slash stripped", lib._instance_url == INSTANCE, lib._instance_url)
    check("Bearer header carries token", lib._headers()["Authorization"] == f"Bearer {TOKEN}")
    _no_leak("unredacted", error, logs)


def test_redacted_display_token_falls_back():
    print("test_redacted_display_token_falls_back")
    lib, calls, error, logs = _run([_display(), _show()])
    check("no error", error is None, error)
    check("fallback argv", calls[1:] == [
        ["sf", "org", "auth", "show-access-token", "-o", ALIAS, "--json"]], calls)
    check("fallback token used", lib._access_token == TOKEN)
    check("placeholder never stored", lib._access_token != REDACTED)
    check("instance URL still from display", lib._instance_url == INSTANCE)
    check("fallback is logged", any("show-access-token" in msg for msg in logs), logs)
    _no_leak("redacted", error, logs)


def test_missing_display_token_falls_back():
    print("test_missing_display_token_falls_back")
    lib, calls, error, logs = _run([_display(token=None), _show()])
    check("no error", error is None, error)
    check("fallback ran", len(calls) == 2, calls)
    check("fallback token used", lib._access_token == TOKEN)


def test_missing_instance_url_fails_before_fallback():
    print("test_missing_instance_url_fails_before_fallback")
    lib, calls, error, logs = _run([_display(instance=None)])
    check("raises", error is not None)
    check("names instanceUrl", error is not None and "instanceUrl" in str(error), error)
    check("no fallback call", len(calls) == 1, calls)
    check("not authenticated", lib._access_token is None)


def test_display_failure_names_alias():
    print("test_display_failure_names_alias")
    lib, calls, error, logs = _run([_completed(returncode=1, stderr="NoOrgFound: no such org")])
    check("display failure raises", error is not None)
    check("display failure names the alias", error is not None and ALIAS in str(error), error)
    check("display failure makes no fallback call", len(calls) == 1, calls)
    _no_leak("display failure", error, logs)


def test_display_bad_output_raises_without_token():
    # PR #492 review round 3 (class from #493): sf org display's own output.
    print("test_display_bad_output_raises_without_token")
    cases = [
        ("display non-JSON with token", _completed(stdout=f"Access token: {TOKEN}"),
         ["non-JSON", ALIAS]),
        ("display top-level list", _completed(stdout="[]"), ["instanceUrl"]),
        ("display non-object result", _completed(stdout=json.dumps({"result": []})),
         ["unexpected JSON shape", ALIAS]),
    ]
    for label, response, expected in cases:
        lib, calls, error, logs = _run([response])
        check(f"{label}: raises AssertionError", isinstance(error, AssertionError), error)
        for fragment in expected:
            check(f"{label}: message has {fragment!r}", error is not None and fragment in str(error), error)
        check(f"{label}: no fallback call", len(calls) == 1, calls)
        _no_leak(label, error, logs)
    lib, calls, error, logs = _run([_completed(stdout=f"Access token: {TOKEN}")])
    check("display non-JSON: decode error not chained",
          error is not None and error.__cause__ is None and error.__suppress_context__)


def test_fallback_failures_raise_without_token():
    print("test_fallback_failures_raise_without_token")
    cases = [
        ("non-zero exit", _completed(returncode=1, stderr="NoOrgFound: no such org"),
         ["rc=1", ALIAS]),
        # PR #492 review: a failed run's stdout may hold the token, so neither
        # stream may reach the error.
        ("non-zero exit, token on stdout", _completed(returncode=1, stdout=f"partial {TOKEN}"),
         ["rc=1", ALIAS]),
        ("non-JSON stdout", _completed(stdout=f"Access token: {TOKEN}"), ["non-JSON", ALIAS]),
        ("still redacted", _show(token=REDACTED), ["did not return a usable", ALIAS]),
        ("no result", _completed(stdout=json.dumps({"status": 0})), ["did not return a usable", ALIAS]),
        ("non-object result", _completed(stdout=json.dumps({"result": "x"})),
         ["unexpected JSON shape", ALIAS]),
        ("timeout", subprocess.TimeoutExpired(cmd="sf", timeout=30), ["timed out after 30", ALIAS]),
    ]
    for label, response, expected in cases:
        lib, calls, error, logs = _run([_display(), response])
        check(f"{label}: raises AssertionError", error is not None)
        for fragment in expected:
            check(f"{label}: message has {fragment!r}", error is not None and fragment in str(error), error)
        check(f"{label}: no partial auth state", lib._access_token is None and lib._instance_url is None)
        _no_leak(label, error, logs)
    # The non-JSON case is the one whose stdout holds the token; the decode
    # error (whose `.doc` is that stdout) must not be chained onto ours.
    lib, calls, error, logs = _run([_display(), _completed(stdout=f"Access token: {TOKEN}")])
    check("non-JSON: decode error not chained",
          error is not None and error.__cause__ is None and error.__suppress_context__)


def test_already_authenticated_skips_sf():
    print("test_already_authenticated_skips_sf")
    calls = []
    original = m.subprocess.run
    m.subprocess.run = lambda cmd, **kw: calls.append(cmd)
    try:
        lib = m.SalesforceAPI()
        lib._access_token, lib._instance_url = TOKEN, INSTANCE
        lib._ensure_authenticated()
    finally:
        m.subprocess.run = original
    check("no sf call when already authenticated", calls == [], calls)


def main():
    for test in (
        test_token_shape_check,
        test_unredacted_display_token_used_without_fallback,
        test_redacted_display_token_falls_back,
        test_missing_display_token_falls_back,
        test_missing_instance_url_fails_before_fallback,
        test_display_failure_names_alias,
        test_display_bad_output_raises_without_token,
        test_fallback_failures_raise_without_token,
        test_already_authenticated_skips_sf,
    ):
        test()
    print(f"\n{_PASS} passed, {_FAIL} failed.")
    return 1 if _FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
