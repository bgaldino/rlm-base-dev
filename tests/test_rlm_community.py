#!/usr/bin/env python3
"""
Offline invariants for the org-aware tasks in tasks/rlm_community.py.

    python tests/test_rlm_community.py

Reads only class attributes and module source text, so no org is needed. The
module imports `requests` at import time, so this suite lives in pr_gate's
REQUESTS_SUITES (deps=["requests"]), not the stdlib list.

Why this file exists
--------------------
`PatchNetworkEmailForDeploy` and `PatchPaymentsSiteForDeploy` read the target org
through `self.org_config` (REST query / username) but shipped as bare `BaseTask`.
With `salesforce_task` left False, cci builds no `--org` option, so a standalone
`cci task run patch_network_email_for_deploy --org <alias>` is REJECTED and the
task can only ever run against the default org — silently unsafe when the whole
point is patching a specific community's Network email. This was observed live:
`--org` was rejected until the flag was set. These tasks now run in flows for two
communities (PRM `rlm`, Billing Portal), so the org must be explicit.

The two Revert tasks are pure file I/O — they touch no `org_config` — so they
correctly stay orgless; forcing `salesforce_task` on them would impose a bogus
org requirement. That distinction is asserted here so a "fix everything to True"
regression is caught too.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tasks.rlm_community import (  # noqa: E402
    PatchNetworkEmailForDeploy,
    PatchPaymentsSiteForDeploy,
    RevertNetworkEmailAfterDeploy,
    RevertPaymentsSiteAfterDeploy,
)

MODULE_SRC = (REPO_ROOT / "tasks" / "rlm_community.py").read_text(encoding="utf-8")

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))


def _sf_flag(cls):
    # BaseTask defaults salesforce_task = False; under the module's import guard
    # BaseTask degrades to `object`, which has no such attribute. getattr with a
    # False default reads "does this class opt into an org" under either interpreter.
    return getattr(cls, "salesforce_task", False) is True


def check_org_reading_patch_tasks_declare_salesforce_task(_):
    check(
        "patch_network_declares_salesforce_task",
        _sf_flag(PatchNetworkEmailForDeploy),
        "must be True or cci drops --org and the task can only hit the default org",
    )
    check(
        "patch_payments_declares_salesforce_task",
        _sf_flag(PatchPaymentsSiteForDeploy),
        "must be True or cci drops --org and the task can only hit the default org",
    )


def check_file_only_revert_tasks_stay_orgless(_):
    # Reverts do only file I/O; declaring salesforce_task would force a bogus org
    # requirement on a task that never reads the org.
    check(
        "revert_network_is_orgless",
        not _sf_flag(RevertNetworkEmailAfterDeploy),
        "revert does file I/O only and must not require an org",
    )
    check(
        "revert_payments_is_orgless",
        not _sf_flag(RevertPaymentsSiteAfterDeploy),
        "revert does file I/O only and must not require an org",
    )


def _notfound_raise_literals():
    """The string literals of the *specific* `Network not found` raise, and nothing else.

    An earlier version of this check joined every quoted string in the whole module, so the
    creator names living in the module/class docstrings satisfied it — reverting the actual
    raise to PRM-only guidance would still have passed. Scope strictly to the raise that
    carries "not found in org" so the assertion fails exactly when that message is wrong.
    """
    raises = re.findall(
        r'raise TaskOptionsError\(\s*((?:f?"[^"]*"\s*)+)\)', MODULE_SRC, re.DOTALL
    )
    notfound = [r for r in raises if "not found in org" in r]
    if not notfound:
        return None
    return " ".join(re.findall(r'f?"([^"]*)"', notfound[0]))


def check_missing_network_error_is_network_agnostic(_):
    # Finding: the not-found guidance used to name only create_partner_central, so a
    # failed Billing Portal setup pointed operators at an unrelated PRM prerequisite.
    # The message must reference the selected community's creation step, not a single
    # hard-coded PRM one. Assert against ONLY the not-found raise's own literals so a
    # revert of that message — even with the creator names still present in docstrings —
    # fails this check.
    frag = _notfound_raise_literals()
    check(
        "found_the_network_not_found_raise",
        frag is not None,
        "could not locate the `Network ... not found in org` raise in the module",
    )
    ok = frag is not None and "create_partner_central" in frag and "create_billing_portal" in frag
    check(
        "missing_network_error_names_the_owning_community_step",
        ok,
        "the not-found raise itself must name both community create steps, not only the PRM one",
    )


def main():
    checks = (
        check_org_reading_patch_tasks_declare_salesforce_task,
        check_file_only_revert_tasks_stay_orgless,
        check_missing_network_error_is_network_agnostic,
    )
    for fn in checks:
        try:
            fn(None)
        except Exception as exc:  # a check that blows up is a failure, not a crash
            check(fn.__name__.replace("check_", ""), False, f"check raised {type(exc).__name__}: {exc}")

    width = max(len(n) for n, _, _ in RESULTS)
    failed = 0
    print("rlm_community task invariants\n" + "=" * (width + 60))
    for name, ok, detail in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'}  {name:<{width}}  {detail}")
        failed += 0 if ok else 1
    print("=" * (width + 60))
    print(f"{len(RESULTS) - failed}/{len(RESULTS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
