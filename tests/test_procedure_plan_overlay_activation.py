#!/usr/bin/env python3
"""
Invariant: apply_procedure_plan_overlay leaves the plan version as active or inactive as it found it.

    python tests/test_procedure_plan_overlay_activation.py

Stdlib only: `requests` is replaced by a stub and the task's org calls are overridden, so no org,
no network and no CumulusCI install.

Why this file exists
--------------------
The quote procedure plan is built inactive by default (`procedureplans_active: false`, todo 314)
and cumulusci.yml runs the overlay with `activate_after_apply: false`. The finally block must then
reactivate only a version that was active before, on success or failure, including when the
deactivate PATCH landed but the wait for it timed out. It must never activate an inactive one.
"""
import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.modules.setdefault("requests", types.ModuleType("requests"))
sys.modules["cumulusci"] = None  # use the module's no-CumulusCI fallback (BaseSalesforceTask = object)
from tasks.rlm_apply_procedure_plan_overlay import ApplyProcedurePlanOverlay  # noqa: E402

FAILURES = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}{(' -- ' + detail) if detail else ''}")
        FAILURES.append(label)


class FakeLogger:
    def info(self, *args, **kwargs):
        pass

    warning = info


class FakeTask(ApplyProcedurePlanOverlay):
    def __init__(self, was_active, activate_after_apply, fail_apply=False, fail_wait=False,
                 fail_patch=False, fail_reactivate=False):
        self.options = {"developerName": "PLAN", "overlay_file": "overlay.json", "activate_after_apply": activate_after_apply}
        self.logger = FakeLogger()
        self.active = was_active
        self.fail_apply = fail_apply
        self.fail_wait = fail_wait
        self.fail_patch = fail_patch
        self.fail_reactivate = fail_reactivate

    def _load_overlay(self):
        return {}

    def _get_version(self, developer_name):
        return {"Id": "1Cv", "IsActive": self.active}

    def _set_version_active(self, version_id, active, dry_run):
        if active and self.fail_reactivate:
            raise RuntimeError("reactivate failed")
        self.active = active
        if self.fail_patch and not active:
            raise ConnectionError("reset after the PATCH landed")

    def _wait_for_active_state(self, version_id, active):
        if self.fail_wait and not active:
            raise TimeoutError("still active")

    def _apply_overlay(self, version_id, overlay, dry_run):
        if self.fail_apply:
            raise RuntimeError("apply failed")

    def _verify_overlay(self, version_id, overlay):
        pass


def run(**kwargs):
    task = FakeTask(**kwargs)
    try:
        task._run_task()
        return task.active, None
    except Exception as exc:
        return task.active, exc


def check_restore_matrix():
    for was_active in (True, False):
        for fail_apply in (False, True):
            end, exc = run(was_active=was_active, activate_after_apply=False, fail_apply=fail_apply)
            check(f"activate_after_apply false, was_active={was_active}, fail_apply={fail_apply}: "
                  f"ends {was_active}", end is was_active and (exc is not None) is fail_apply,
                  f"ended {end}, raised {exc!r}")


def check_wait_timeout_restores():
    end, exc = run(was_active=True, activate_after_apply=False, fail_wait=True)
    check("deactivate wait times out: the active version is still restored",
          end is True and exc is not None, f"ended {end}")


def check_raised_patch_restores():
    end, exc = run(was_active=True, activate_after_apply=False, fail_patch=True)
    check("deactivate PATCH raises after landing: the active version is still restored",
          end is True and isinstance(exc, ConnectionError), f"ended {end}, raised {exc!r}")


def check_failed_reactivation_is_reported():
    _, exc = run(was_active=True, activate_after_apply=False, fail_apply=True, fail_reactivate=True)
    check("apply and reactivation both fail: reported together, chained to the apply failure",
          exc is not None and "reactivation also failed" in str(exc)
          and isinstance(exc.__cause__, RuntimeError), repr(exc))


def check_activate_after_apply_true():
    end, _ = run(was_active=False, activate_after_apply=True)
    check("activate_after_apply true activates an inactive version", end is True)


def main():
    print("apply_procedure_plan_overlay activation restore")
    for fn in (check_restore_matrix, check_wait_timeout_restores, check_raised_patch_restores,
               check_failed_reactivation_is_reported, check_activate_after_apply_true):
        try:
            fn()
        except Exception as exc:  # a check that blows up is a failure, not a crash
            check(fn.__name__, False, f"check raised {type(exc).__name__}: {exc}")
    if FAILURES:
        print(f"\n{len(FAILURES)} failure(s)")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
