#!/usr/bin/env python3
"""
Offline invariants for tasks/rlm_enable_change_data_capture.EnableChangeDataCapture.

    python tests/test_rlm_enable_change_data_capture.py

No org and no CumulusCI install required: the task module degrades gracefully when
CumulusCI is absent, and `requests` is replaced with a fake that records calls.

Why this file exists
--------------------
CDC selections count against a five-entity allocation on orgs without the CDC add-on.
Deploying Quote and Order unconditionally would fail the build on a persistent org that
already uses its allocation (Codex review on PR #545). The task must:
- add only what's missing,
- warn and continue when the platform rejects a selection,
- fail only when raise_on_failure is set.
Each of those reads as "working" from the exit code alone, so these checks assert on the
calls made and the outcome.
"""
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tasks.rlm_enable_change_data_capture import (  # noqa: E402
    CHANNEL,
    EnableChangeDataCapture,
    change_event_name,
)

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))


class FakeResponse:
    def __init__(self, status, payload=None, text=""):
        self.status_code = status
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeRequestException(Exception):
    pass


class FakeRequests:
    """Answers the selection query, then each create with the next queued status.

    A status of "raise" makes that call raise FakeRequestException, standing in for a
    network error.
    """

    def __init__(self, selected, create_statuses, query_status=200):
        self.selected = selected
        self.create_statuses = list(create_statuses)
        self.query_status = query_status
        self.posts = []

    def get(self, url, headers=None, params=None, timeout=None):
        if self.query_status == "raise":
            raise FakeRequestException("connection reset")
        rows = [{"EventChannel": ch, "SelectedEntity": e} for ch, e in self.selected]
        resp = FakeResponse(self.query_status, {"records": rows})
        if self.query_status >= 400:
            def raise_http():
                raise FakeRequestException(f"HTTP {self.query_status}")
            resp.raise_for_status = raise_http
        return resp

    def post(self, url, headers=None, json=None, timeout=None):
        self.posts.append(json)
        status = self.create_statuses.pop(0) if self.create_statuses else 201
        if status == "raise":
            raise FakeRequestException("read timed out")
        text = "" if status in (200, 201) else '[{"errorCode":"LIMIT_EXCEEDED"}]'
        return FakeResponse(status, text=text)


class Log:
    def __init__(self):
        self.infos, self.warnings = [], []

    def info(self, msg):
        self.infos.append(msg)

    def warning(self, msg):
        self.warnings.append(msg)


def make_task(fake, entities=None, raise_on_failure=False):
    sys.modules["requests"] = types.SimpleNamespace(
        get=fake.get, post=fake.post, RequestException=FakeRequestException)
    task = EnableChangeDataCapture.__new__(EnableChangeDataCapture)
    task.entities = entities or ["Quote", "Order"]
    task.allocation = 5
    task.raise_on_failure = raise_on_failure
    task.logger = Log()
    task.org_config = types.SimpleNamespace(instance_url="https://x", access_token="t")
    task.project_config = types.SimpleNamespace(project__package__api_version="68.0")
    return task


def check_change_event_names(_):
    check("standard object", change_event_name("Quote") == "QuoteChangeEvent")
    check("custom object", change_event_name("Foo__c") == "Foo__ChangeEvent")


def check_fresh_org_selects_both(_):
    fake = FakeRequests([], [201, 201])
    make_task(fake)._run_task()
    events = [p["Metadata"]["selectedEntity"] for p in fake.posts]
    check("fresh org creates Quote and Order", events == ["QuoteChangeEvent", "OrderChangeEvent"], str(events))
    check("members go on the ChangeEvents channel",
          all(p["Metadata"]["eventChannel"] == CHANNEL and p["FullName"].startswith(CHANNEL + "_") for p in fake.posts))


def check_rerun_adds_nothing(_):
    fake = FakeRequests([(CHANNEL, "QuoteChangeEvent"), (CHANNEL, "OrderChangeEvent")], [])
    task = make_task(fake)
    task._run_task()
    check("rerun makes no create call", fake.posts == [], str(fake.posts))
    check("rerun says nothing to add", any("Nothing to add" in m for m in task.logger.infos))


def check_partial_adds_only_missing(_):
    fake = FakeRequests([(CHANNEL, "QuoteChangeEvent")], [201])
    make_task(fake)._run_task()
    events = [p["Metadata"]["selectedEntity"] for p in fake.posts]
    check("only the missing entity is created", events == ["OrderChangeEvent"], str(events))


def check_full_allocation_warns_not_fails(_):
    full = [(CHANNEL, f"E{i}ChangeEvent") for i in range(5)]
    fake = FakeRequests(full, [400, 400])
    task = make_task(fake)
    raised = False
    try:
        task._run_task()
    except Exception:
        raised = True
    check("full allocation does not raise by default", not raised)
    check("full allocation pre-check warns", any("may exceed" in m for m in task.logger.warnings))
    check("rejected selection is reported", any("LIMIT_EXCEEDED" in m for m in task.logger.warnings))


def check_raise_on_failure(_):
    full = [(CHANNEL, f"E{i}ChangeEvent") for i in range(5)]
    fake = FakeRequests(full, [400, 400])
    task = make_task(fake, raise_on_failure=True)
    raised = False
    try:
        task._run_task()
    except Exception as exc:
        raised = "LIMIT_EXCEEDED" in str(exc)
    check("raise_on_failure raises with the platform error", raised)


def check_query_failure_is_soft(_):
    for status in (500, "raise"):
        fake = FakeRequests([], [], query_status=status)
        task = make_task(fake)
        raised = False
        try:
            task._run_task()
        except Exception:
            raised = True
        check(f"query failure ({status}) warns, no raise", not raised and task.logger.warnings and fake.posts == [])
        fake = FakeRequests([], [], query_status=status)
        try:
            make_task(fake, raise_on_failure=True)._run_task()
            check(f"query failure ({status}) raises with raise_on_failure", False)
        except Exception as exc:
            check(f"query failure ({status}) raises with raise_on_failure",
                  "Could not read" in str(exc), str(exc)[:80])


def check_create_exception_is_soft(_):
    fake = FakeRequests([], ["raise", 201])
    task = make_task(fake)
    task._run_task()
    check("create exception warns and the next entity is still tried",
          len(fake.posts) == 2 and any("read timed out" in m for m in task.logger.warnings))


def check_custom_channel_members_not_counted(_):
    custom = [("RLM_Custom__chn", f"Evt{i}__e") for i in range(5)]
    fake = FakeRequests(custom, [201, 201])
    task = make_task(fake)
    task._run_task()
    check("custom-channel platform events don't trigger the allocation warning",
          not any("may exceed" in m for m in task.logger.warnings))


def check_option_parsing(_):
    task = EnableChangeDataCapture.__new__(EnableChangeDataCapture)
    task.options = {"entities": "Quote, Order,Case", "allocation": "7", "raise_on_failure": "True"}
    task._parse_options()
    check("entities from a comma string", task.entities == ["Quote", "Order", "Case"], str(task.entities))
    check("allocation parsed as int", task.allocation == 7)
    check("raise_on_failure parsed from 'True'", task.raise_on_failure is True)


def main():
    checks = (
        check_change_event_names,
        check_fresh_org_selects_both,
        check_rerun_adds_nothing,
        check_partial_adds_only_missing,
        check_full_allocation_warns_not_fails,
        check_raise_on_failure,
        check_query_failure_is_soft,
        check_create_exception_is_soft,
        check_custom_channel_members_not_counted,
        check_option_parsing,
    )
    for fn in checks:
        try:
            fn(None)
        except Exception as exc:  # a check that blows up is a failure, not a crash
            check(fn.__name__.replace("check_", ""), False, f"check raised {type(exc).__name__}: {exc}")

    width = max(len(n) for n, _, _ in RESULTS)
    failed = 0
    print("rlm_enable_change_data_capture task invariants\n" + "=" * (width + 60))
    for name, ok, detail in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'}  {name:<{width}}  {detail}")
        failed += 0 if ok else 1
    print("=" * (width + 60))
    print(f"{len(RESULTS) - failed}/{len(RESULTS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
