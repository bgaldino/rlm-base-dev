#!/usr/bin/env python3
"""
Offline invariants for tasks/rlm_apex_file.FileBasedAnonymousApexTask.

    python tests/test_rlm_apex_file.py

No org and no CumulusCI install required -- the task module degrades gracefully
when CumulusCI is absent, and every check here is pure string handling against
debug-log text captured verbatim from a real `sf apex run --json` response.

Why this file exists
--------------------
Two defects shipped in this task and neither was visible from its output:

1. It extended SFDXBaseTask -- documented as "call the sfdx cli with params and
   NO org" -- leaving `salesforce_task` False. cci builds the --org option from
   that flag, so `--org <alias>` was rejected outright and the task could only
   ever run against the default org, without logging which org that was.
2. It logged the script's output at debug level behind a 50-line cap. Since the
   head of an Apex debug log is the whole script echoed back as
   "Execute Anonymous:" lines, a 500-line validator burned the entire cap on
   source echo. A PASSING run therefore printed nothing at all, and the task
   communicated only by throwing.

Both are the kind of regression that reads as "working" -- the task still exits
0 -- so they need a test that asserts on the parsing, not on the exit code.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tasks.rlm_apex_file import (  # noqa: E402
    FileBasedAnonymousApexTask,
    LOG_EVENT_LINE,
    MAX_SCRIPT_OUTPUT_LINES,
)

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))


def extract(log_text):
    """Call the extractor unbound -- it touches no instance state."""
    return FileBasedAnonymousApexTask._extract_script_output(
        FileBasedAnonymousApexTask, log_text
    )


# Captured verbatim from `sf apex run --json` against a scratch org. Do not
# "tidy" these strings: the bare continuation lines and the &#124; entity are
# exactly what the platform emits, and they are the whole point of the test.
REAL_LOG = "\n".join(
    [
        "62.0 APEX_CODE,DEBUG;APEX_PROFILING,INFO;CALLOUT,INFO",
        "Execute Anonymous: System.debug('MARKER-START');",
        "Execute Anonymous: System.debug('multi\\nline\\noutput');",
        "16:03:23.39 (40382722)|USER_DEBUG|[1]|DEBUG|MARKER-START",
        "16:03:23.39 (40433892)|USER_DEBUG|[2]|DEBUG|multi",
        "line",
        "output",
        "16:03:23.39 (40448772)|USER_DEBUG|[3]|DEBUG|GATE-A BEFORE &#124; assets=1 arce=5",
        "16:03:23.40 (40534783)|CUMULATIVE_LIMIT_USAGE",
        "16:03:23.40 (40534783)|LIMIT_USAGE_FOR_NS|(default)|",
        "  Number of SOQL queries: 0 out of 100",
        "16:03:23.40 (40534999)|FATAL_ERROR|System.AssertException: boom",
    ]
)


def check_task_requires_an_org(_):
    """
    salesforce_task drives three separate behaviours in cci: whether --org is
    offered at all, whether __call__ guards on a missing org, and whether
    _log_begin records the org. All three were off.
    """
    check(
        "task_declares_salesforce_task",
        FileBasedAnonymousApexTask.salesforce_task is True,
        "must be True or cci silently drops --org and runs against the default org",
    )


def check_source_echo_is_dropped(_):
    out = extract(REAL_LOG)
    echoed = [line for line in out if "Execute Anonymous" in line]
    check(
        "source_echo_dropped",
        not echoed,
        "script source must not reach task output" if echoed else f"{len(out)} line(s) kept",
    )


def check_multiline_debug_survives(_):
    """
    The regression that a naive USER_DEBUG filter causes. A System.debug()
    containing newlines emits its first line prefixed and every following line
    BARE. Dropping those silently truncates exactly the multi-line failure
    reports these scripts exist to produce.
    """
    out = extract(REAL_LOG)
    contiguous = ["multi", "line", "output"]
    idx = out.index("multi") if "multi" in out else -1
    ok = idx >= 0 and out[idx : idx + 3] == contiguous
    check(
        "multiline_continuations_kept",
        ok,
        "bare continuation lines must survive, in order" if not ok else "multi/line/output intact",
    )


def check_platform_chatter_is_not_mistaken_for_output(_):
    """
    An indented bare line also follows LIMIT_USAGE_FOR_NS. It is NOT a debug
    continuation, and only closing the block on every non-USER_DEBUG event
    keeps it out.
    """
    out = extract(REAL_LOG)
    leaked = [line for line in out if "Number of SOQL queries" in line]
    check(
        "limit_usage_chatter_excluded",
        not leaked,
        "platform limit output leaked into script output" if leaked else "excluded",
    )


def check_pipes_in_messages_survive(_):
    """
    Messages routinely contain "|" (e.g. 'GATE-A BEFORE | assets=1'). Splitting
    without maxsplit would truncate them at the first pipe.
    """
    out = extract(REAL_LOG)
    ok = "GATE-A BEFORE | assets=1 arce=5" in out
    check(
        "pipe_bearing_message_intact",
        ok,
        "message truncated at an embedded pipe" if not ok else "intact and unescaped",
    )


def check_html_entities_are_decoded(_):
    out = extract(REAL_LOG)
    still_encoded = [line for line in out if "&#" in line]
    check(
        "html_entities_decoded",
        not still_encoded,
        f"raw entities left: {still_encoded}" if still_encoded else "decoded",
    )


def check_errors_are_surfaced(_):
    """A script that blew up must say so in the task output, not only in the raised exception."""
    out = extract(REAL_LOG)
    ok = any(line.startswith("FATAL_ERROR:") and "AssertException" in line for line in out)
    check("fatal_error_surfaced", ok, "FATAL_ERROR must appear in output" if not ok else "surfaced")


def check_event_regex_needs_the_timestamp(_):
    """
    Event detection must key on the timestamp+nanos prefix. Matching on "|"
    alone would classify any continuation line containing a pipe as an event
    and silently drop it.
    """
    check(
        "event_regex_requires_timestamp",
        LOG_EVENT_LINE.match("16:03:23.39 (40382722)|USER_DEBUG|[1]|DEBUG|x") is not None
        and LOG_EVENT_LINE.match("elapsed (ms) | 42") is None
        and LOG_EVENT_LINE.match("plain continuation") is None,
        "regex must accept real event lines and reject pipe-bearing prose",
    )


def check_empty_and_missing_logs_are_safe(_):
    ok = extract("") == []
    check("empty_log_safe", ok, "empty log must yield no output, not raise")


def check_overflow_is_reported_not_silent(_):
    """
    REVIEW.md: no silent caps. Verify the cap exists and that the extractor
    itself does not truncate -- the caller reports the overflow, so the count
    it reports has to be the true one.
    """
    big = "\n".join(
        f"16:03:23.39 (4038272{i})|USER_DEBUG|[{i}]|DEBUG|line {i}"
        for i in range(MAX_SCRIPT_OUTPUT_LINES + 25)
    )
    out = extract(big)
    check(
        "extractor_does_not_truncate",
        len(out) == MAX_SCRIPT_OUTPUT_LINES + 25,
        f"extractor returned {len(out)}; caller must be the one that caps and reports",
    )


def main():
    checks = (
        check_task_requires_an_org,
        check_source_echo_is_dropped,
        check_multiline_debug_survives,
        check_platform_chatter_is_not_mistaken_for_output,
        check_pipes_in_messages_survive,
        check_html_entities_are_decoded,
        check_errors_are_surfaced,
        check_event_regex_needs_the_timestamp,
        check_empty_and_missing_logs_are_safe,
        check_overflow_is_reported_not_silent,
    )
    for fn in checks:
        try:
            fn(None)
        except Exception as exc:  # a check that blows up is a failure, not a crash
            check(
                fn.__name__.replace("check_", ""),
                False,
                f"check raised {type(exc).__name__}: {exc}",
            )

    width = max(len(n) for n, _, _ in RESULTS)
    failed = 0
    print("rlm_apex_file task invariants\n" + "=" * (width + 60))
    for name, ok, detail in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'}  {name:<{width}}  {detail}")
        failed += 0 if ok else 1
    print("=" * (width + 60))
    print(f"{len(RESULTS) - failed}/{len(RESULTS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
