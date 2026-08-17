"""Unit tests for tasks/rlm_agents_common.py — agent discovery and the sf-CLI contract.

`run_sf_json` is the single success contract for all five Agentforce tasks
(`publish_agents`, `activate_agents`, `deactivate_agents`, `test_agents`), so a
gap in how it reports failure is a gap in all of them. #264-59 is what that cost:
`activate_agents` failed in CI and the entire reported reason was

    sf agent activate (RLM_Billing_Employee_Assistance) failed: ›   Warning:
    @salesforce/cli update available from 2.127.2 to 2.147.7.

— the CLI's own update notice, which the old fallback chain picked up because it
took the *first* non-empty source and stderr held nothing else. The cause was
invisible and the org was already torn down, so it could not be recovered after
the fact. These tests pin the reporting contract instead: every source is
included, the update notice never stands in for a cause, and the exit code is
always present so a silent non-zero still says something.

No org, no network, no CLI — `subprocess.run` is stubbed.

Run:  <cci-venv-python> tests/test_agents_common.py
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tasks import rlm_agents_common as common  # noqa: E402

# CommandException comes from the module under test so the assertion names the
# class the code will raise. See tests/test_snapshot_dev_guide.py for why a
# narrower import from CumulusCI silently disagrees with the module's fallback.
CommandException = common.CommandException


_passed = _total = 0


def check(label, cond, detail=""):
    global _passed, _total
    _total += 1
    if cond:
        _passed += 1
        print(f"  [PASS] {label}")
    else:
        print(f"  [FAIL] {label}  {detail}")


class _Result:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _stub_run(result=None, raises=None):
    """Replace subprocess.run inside the module under test."""
    calls = []

    def fake(cmd, **kwargs):
        calls.append((cmd, kwargs))
        if raises is not None:
            raise raises
        return result

    common.subprocess.run = fake
    return calls


# Captured once, at import, before any stub can be installed. `common.subprocess`
# is the shared module object, so stubbing sets `subprocess.run` globally -- and
# restoring from `subprocess.run` would therefore reinstall the stub, leaking it
# into every later check and making in-process subprocess use order-dependent.
_REAL_RUN = subprocess.run


def _restore():
    common.subprocess.run = _REAL_RUN


def _failure_message(returncode=1, stdout="", stderr=""):
    _stub_run(_Result(returncode, stdout, stderr))
    try:
        common.run_sf_json(["sf", "agent", "activate"], timeout=5, label="sf agent activate (X)")
    except CommandException as exc:
        return str(exc)
    finally:
        _restore()
    return ""


UPDATE_NOTICE = "›   Warning: @salesforce/cli update available from 2.127.2 to 2.147.7.\n"


def check_the_update_notice_never_stands_in_for_a_cause(_):
    """The exact #264-59 shape: non-zero exit, no JSON, stderr holds only the notice."""
    msg = _failure_message(returncode=1, stdout="", stderr=UPDATE_NOTICE)
    check("notice_is_not_reported_as_the_cause", "update available" not in msg,
          f"the CLI's own update notice is being reported as the failure: {msg!r}")
    check("exit_code_survives_an_otherwise_empty_failure", "exit 1" in msg,
          f"a failure with nothing but the notice must still say something: {msg!r}")


def check_a_real_stderr_message_is_kept_even_alongside_the_notice(_):
    msg = _failure_message(
        returncode=1,
        stderr=UPDATE_NOTICE + "Error: No authorization information found for test@example.com.",
    )
    check("real_stderr_is_reported", "No authorization information found" in msg, msg)
    check("notice_is_filtered_from_a_mixed_stream", "update available" not in msg, msg)


def check_envelope_name_and_message_are_both_reported(_):
    msg = _failure_message(
        returncode=1,
        stdout='{"status":1,"name":"AgentNotFoundError","message":"No agent named X."}',
    )
    check("envelope_name_is_reported", "AgentNotFoundError" in msg, msg)
    check("envelope_message_is_reported", "No agent named X." in msg, msg)
    # A parsed envelope is already summarized by name+message; dumping the raw
    # JSON as well would bury it.
    check("parsed_envelope_is_not_also_dumped_raw", '{"status"' not in msg, msg)


def check_a_nonzero_status_with_exit_zero_still_fails(_):
    """The CLI's documented contract: exit 0 but status != 0 is a failure."""
    msg = _failure_message(returncode=0, stdout='{"status":68,"message":"Deploy failed."}')
    check("status_not_zero_is_a_failure", "Deploy failed." in msg, msg)
    check("exit_zero_is_still_reported", "exit 0" in msg, msg)


def check_unparseable_output_is_quoted_rather_than_swallowed(_):
    msg = _failure_message(returncode=1, stdout="Usage: sf agent activate ...")
    check("unparseable_stdout_is_quoted", "Usage: sf agent activate" in msg, msg)


def check_an_envelope_with_no_message_still_explains_itself(_):
    """A `{"status":1}` envelope with no message must not produce an empty reason."""
    msg = _failure_message(returncode=1, stdout='{"status":1}')
    check("empty_envelope_still_has_a_reason", msg.strip().endswith("exit 1"), msg)
    check("empty_envelope_reason_is_not_blank", msg.strip() != "exit 1", msg)
    check("empty_envelope_shows_what_it_got", '{"status":1}' in msg, msg)


def check_a_cause_hidden_below_name_and_message_is_still_reported(_):
    """The regression this function exists to prevent, one level deeper.

    `sf` can return a parsed envelope whose cause sits somewhere other than
    `name`/`message` -- nested under `result`, typically. Suppressing stdout
    because *a* payload parsed, rather than because the payload actually said
    something, degraded the whole report to `exit 1` once the update notice was
    stripped from stderr: the same silence, arrived at by a different route.
    """
    nested = ('{"status":1,"result":{"failures":[{"error":"AGENT_NOT_ACTIVATABLE",'
              '"detail":"no active version"}]}}')
    msg = _failure_message(returncode=1, stdout=nested, stderr=UPDATE_NOTICE)
    check("hidden_cause_is_surfaced", "AGENT_NOT_ACTIVATABLE" in msg, msg)
    check("hidden_cause_detail_is_surfaced", "no active version" in msg, msg)
    check("hidden_cause_is_not_just_the_exit_code", msg.strip() != "exit 1", msg)
    check("hidden_cause_does_not_reintroduce_the_notice", "update available" not in msg, msg)

    # A real message must still suppress the dump, or every error grows a JSON tail.
    plain = _failure_message(returncode=1, stdout='{"status":1,"message":"real cause"}')
    check("a_real_message_does_not_also_dump_the_envelope", "status" not in plain, plain)

    # Large payloads are truncated rather than made unreadable.
    big = '{"status":1,"result":{"blob":"' + "x" * 2000 + '"}}'
    msg = _failure_message(returncode=1, stdout=big)
    check("an_oversized_payload_is_truncated",
          len(msg) < 900 and "(truncated)" in msg, str(len(msg)))


def check_the_stub_is_actually_restored(_):
    """Guards the harness, not the code -- a leaked stub invalidates every check.

    `common.subprocess` is the shared module object, so installing a stub sets
    `subprocess.run` globally; restoring *from* `subprocess.run` reinstalled the
    stub instead of the real function and leaked it into everything after.
    """
    _stub_run(_Result(0, "{}"))
    check("stub_is_installed", common.subprocess.run is not _REAL_RUN, "stub did not take")
    _restore()
    check("stub_is_removed", common.subprocess.run is _REAL_RUN, "stub leaked past _restore")
    check("module_level_run_is_the_real_one", subprocess.run is _REAL_RUN,
          "the shared subprocess module is still stubbed")
    # And it genuinely runs a process again.
    done = subprocess.run([sys.executable, "-c", "print('ok')"], capture_output=True, text=True)
    check("real_subprocess_works_after_restore", done.stdout.strip() == "ok", done.stdout)


def check_success_returns_the_parsed_envelope(_):
    _stub_run(_Result(0, '{"status":0,"result":{"id":"0Xx"}}'))
    try:
        payload = common.run_sf_json(["sf", "agent", "activate"], timeout=5, label="x")
        check("success_returns_payload", payload.get("result", {}).get("id") == "0Xx", str(payload))
    finally:
        _restore()


def check_a_missing_cli_is_named(_):
    _stub_run(raises=FileNotFoundError("sf"))
    try:
        common.run_sf_json(["sf", "agent", "activate"], timeout=5, label="sf agent activate (X)")
        check("missing_cli_raises", False, "expected CommandException")
    except CommandException as exc:
        check("missing_cli_raises", True)
        check("missing_cli_names_the_binary", "'sf') was not found" in str(exc), str(exc))
    finally:
        _restore()


def check_a_timeout_is_named(_):
    _stub_run(raises=subprocess.TimeoutExpired(cmd=["sf"], timeout=5))
    try:
        common.run_sf_json(["sf"], timeout=5, label="sf agent activate (X)")
        check("timeout_raises", False, "expected CommandException")
    except CommandException as exc:
        check("timeout_raises", True)
        check("timeout_reports_the_limit", "timed out after 5s" in str(exc), str(exc))
    finally:
        _restore()


def check_bundle_discovery(_):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "aiAuthoringBundles"
        check("missing_dir_is_empty_not_an_error", common.discover_agent_bundles(root) == [])
        (root / "RLM_Quoting_Assistant").mkdir(parents=True)
        (root / "RLM_Billing_Employee_Assistance").mkdir()
        (root / "notes.txt").write_text("ignored")
        found = common.discover_agent_bundles(root)
        check("only_directories_are_agents", found ==
              ["RLM_Billing_Employee_Assistance", "RLM_Quoting_Assistant"], str(found))
        check("discovery_is_sorted_so_publish_and_activate_agree", found == sorted(found), str(found))


def main():
    print("tasks/rlm_agents_common.py — sf CLI contract and agent discovery")
    print("=" * 100)
    for fn in (
        check_the_update_notice_never_stands_in_for_a_cause,
        check_a_cause_hidden_below_name_and_message_is_still_reported,
        check_the_stub_is_actually_restored,
        check_a_real_stderr_message_is_kept_even_alongside_the_notice,
        check_envelope_name_and_message_are_both_reported,
        check_a_nonzero_status_with_exit_zero_still_fails,
        check_unparseable_output_is_quoted_rather_than_swallowed,
        check_an_envelope_with_no_message_still_explains_itself,
        check_success_returns_the_parsed_envelope,
        check_a_missing_cli_is_named,
        check_a_timeout_is_named,
        check_bundle_discovery,
    ):
        fn(None)
    print("=" * 100)
    print(f"{_passed}/{_total} checks passed")
    return 0 if _passed == _total else 1


if __name__ == "__main__":
    sys.exit(main())
