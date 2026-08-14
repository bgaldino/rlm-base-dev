#!/usr/bin/env python3
"""
Offline invariants for the 264 context-tag tolerance in
tasks/rlm_manage_fulfillment_scope_cnfg.ManageFulfillmentScopeCnfg.

    python tests/test_fulfillment_scope_tolerance.py

No org and no CumulusCI install required: the task module degrades on ImportError
(the same property tests/test_rlm_apex_file.py relies on) and every check here is
pure classification against Tooling API error payloads captured verbatim from a
fresh 264 scratch org.

Why this file exists
--------------------
Release 264 ships the standard SalesTransactionItemGroup context attribute typed
`lookup`, while CustomFulfillmentScopeCnfg validation demands String. Both sides are
platform-shipped, so `prepare_dro` cannot complete on a fresh 264 org and the build
is unblocked by tolerating that one rejection.

A tolerance is a detector, and this branch has repeatedly shipped detectors that
could not fail (see the private plan's #264-23/#264-27/#264-31). The risk here is
specific: "skip the record when the org says no" would also swallow a misspelled tag,
turning a repo defect into a silent no-op. So the skip is gated twice -- on the error
message AND on the attribute's type read back from the org -- and the second gate is
UNREACHABLE from a live test, because the platform emits a different message for a
missing tag ("Enter a valid Item Context Tag.", no "String") and short-circuits the
first gate. Live testing therefore cannot prove the org-side gate works at all; only
these checks can, which is the whole reason they exist.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from tasks.rlm_manage_fulfillment_scope_cnfg import (  # noqa: E402
    ManageFulfillmentScopeCnfg,
    ToolingWriteError,
    _CONTEXT_TAG_FIELD,
)

try:
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:  # mirrors the task module's own guard
    TaskOptionsError = Exception

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))


# ---------------------------------------------------------------------------- #
# Error payloads, captured verbatim from the Tooling API on a fresh 264 org.
# Do not paraphrase these: the classifier keys on their wording, so a tidied-up
# copy would test the test rather than the platform.
# ---------------------------------------------------------------------------- #

# The 264 defect being tolerated: SalesTransactionItemGroup is typed `lookup`.
TYPE_MISMATCH = json.dumps(
    [{"message": "Enter a valid Item Context Tag with the data type set to String.",
      "errorCode": "INVALID_INPUT", "fields": []}]
)
# A tag that does not resolve at all -- note the message does NOT say "String".
MISSING_TAG = json.dumps(
    [{"message": "Enter a valid Item Context Tag.",
      "errorCode": "INVALID_INPUT", "fields": []}]
)
# An unrelated rejection (DeveloperName with a space).
NAME_INTEGRITY = json.dumps(
    [{"message": "Name: The Custom Fulfillment Scope Config API Name can only contain "
                 "underscores and alphanumeric characters.",
      "errorCode": "FIELD_INTEGRITY_EXCEPTION", "fields": ["DeveloperName"]}]
)

# The type-mismatch rejection accompanied by a SECOND, unrelated failure. The tolerance
# must NOT fire here: skipping the record would discard the name-integrity error too.
MIXED_ERRORS = json.dumps(
    [{"message": "Enter a valid Item Context Tag with the data type set to String.",
      "errorCode": "INVALID_INPUT", "fields": []},
     {"message": "Name: The Custom Fulfillment Scope Config API Name can only contain "
                 "underscores and alphanumeric characters.",
      "errorCode": "FIELD_INTEGRITY_EXCEPTION", "fields": ["DeveloperName"]}]
)
# An empty array: no evidence this is the known defect, so it must not be tolerated.
EMPTY_ERRORS = json.dumps([])

GROUP_RECORD = {"DeveloperName": "Group_Identifier",
                _CONTEXT_TAG_FIELD: "SalesTransactionItemGroup"}
# Same rejection, a DIFFERENT tag. The defect is specific to SalesTransactionItemGroup,
# so this must re-raise however the org types the attribute.
OTHER_TAG_RECORD = {"DeveloperName": "Other_Identifier",
                    _CONTEXT_TAG_FIELD: "SalesTransactionItem"}


class _StubLogger:
    def __init__(self):
        self.lines = []

    def _add(self, level):
        return lambda msg: self.lines.append((level, str(msg)))

    def __getattr__(self, name):
        if name in {"info", "debug", "warning", "error"}:
            return self._add(name)
        raise AttributeError(name)


class _StubTask:
    """Borrows the real classifier; stubs only the org round-trip.

    `data_type` is what the org reports for the tag: a string, or None for "no such
    tag". Every query is recorded so a check can assert the org was NOT consulted on
    the short-circuit paths -- a tolerance that queries on every failure would be a
    performance and log-noise regression even where it returns the right answer.
    """

    # staticmethod() is required, not decoration: accessing the attribute off the real
    # class yields a plain function, which would rebind as an instance method here and
    # be handed `self` as its first argument.
    _looks_like_context_tag_type_error = staticmethod(
        ManageFulfillmentScopeCnfg._looks_like_context_tag_type_error
    )
    _headers = ManageFulfillmentScopeCnfg._headers
    _context_tag_data_type = ManageFulfillmentScopeCnfg._context_tag_data_type
    _is_platform_context_tag_defect = (
        ManageFulfillmentScopeCnfg._is_platform_context_tag_defect
    )

    def __init__(self, data_type):
        self.logger = _StubLogger()
        self.data_type = data_type
        self.queries = []

    def _data_query(self, access_token, instance_url, api_version, soql):
        self.queries.append(soql)
        if self.data_type is None:
            return []
        return [{"ContextAttribute": {"DataType": self.data_type}}]


def tolerate(body, record=GROUP_RECORD, data_type="lookup"):
    task = _StubTask(data_type)
    verdict = task._is_platform_context_tag_defect(
        ToolingWriteError("Tooling create failed: 400", 400, body),
        record, "tok", "https://example.my.salesforce.com", "68.0",
    )
    return verdict, task


# ---------------------------------------------------------------------------- #
# The tolerance fires only for the real defect
# ---------------------------------------------------------------------------- #


def check_the_264_defect_is_tolerated(_):
    verdict, task = tolerate(TYPE_MISMATCH, data_type="lookup")
    logged = " ".join(msg for _, msg in task.logger.lines)
    check("tolerates_lookup_typed_tag", verdict is True,
          "the 264 lookup/String mismatch must be skipped or the build cannot proceed")
    check("tolerance_names_the_actual_type", "lookup" in logged and "String" in logged,
          f"the warning must state what the org reported. Got: {logged[:90]}")


def check_missing_tag_is_not_tolerated(_):
    """A typo'd tag must fail. This is the defect the tolerance could have masked."""
    verdict, _ = tolerate(MISSING_TAG, data_type=None)
    check("rejects_missing_tag_message", verdict is False,
          "the platform's missing-tag message must re-raise, not skip")


def check_unrelated_rejection_is_not_tolerated(_):
    verdict, task = tolerate(NAME_INTEGRITY, data_type="lookup")
    check("rejects_unrelated_error_code", verdict is False,
          "a non-context-tag rejection must re-raise even on an affected org")
    check("unrelated_error_does_not_query_the_org", task.queries == [],
          f"classification must short-circuit before the round-trip; got {task.queries}")


def check_a_second_unrelated_error_defeats_the_tolerance(_):
    """
    The classifier is all-not-any. A response carrying the tolerated type mismatch AND an
    unrelated failure must re-raise: skipping the record to excuse the first error would
    silently discard the second, which is a genuine repo defect.
    """
    verdict, task = tolerate(MIXED_ERRORS, data_type="lookup")
    check("rejects_mixed_error_response", verdict is False,
          "a response with a second, unrelated error must re-raise, not be skipped")
    check("mixed_response_does_not_query_the_org", task.queries == [],
          f"classification must short-circuit before the round-trip; got {task.queries}")


def check_empty_error_array_is_not_tolerated(_):
    verdict, _ = tolerate(EMPTY_ERRORS, data_type="lookup")
    check("rejects_empty_error_array", verdict is False,
          "an empty array is not evidence of the known defect and must re-raise")


def check_a_different_tag_is_not_tolerated(_):
    """
    The tolerance is pinned to SalesTransactionItemGroup. Another tag hitting the same
    rejection is a repo data error -- it names an attribute that is legitimately not
    String -- and must fail the build rather than be skipped.
    """
    verdict, task = tolerate(TYPE_MISMATCH, record=OTHER_TAG_RECORD, data_type="lookup")
    check("rejects_a_different_tag", verdict is False,
          "only SalesTransactionItemGroup is tolerated; another tag must re-raise")
    check("different_tag_does_not_query_the_org", task.queries == [],
          f"the tag gate must short-circuit before the round-trip; got {task.queries}")


def check_a_different_resolvable_type_is_not_tolerated(_):
    """
    The org-side gate is pinned to `lookup`, the type the defect produces. The right tag
    typed something else non-String is a different problem and must re-raise.
    """
    for other_type in ("Reference", "Number", "Boolean"):
        verdict, _ = tolerate(TYPE_MISMATCH, data_type=other_type)
        check(f"rejects_{other_type.lower()}_typed_tag", verdict is False,
              f"only the 'lookup' type is tolerated; '{other_type}' must re-raise")


# ---------------------------------------------------------------------------- #
# The org-side gate -- unreachable from a live test, so only asserted here
# ---------------------------------------------------------------------------- #


def check_org_gate_rejects_a_tag_that_does_not_resolve(_):
    """
    The dangerous case: the type-mismatch MESSAGE with a tag the org cannot resolve.
    The platform does not currently emit this pair, which is exactly why it needs a
    check -- if a future release reworded the missing-tag error to mention String,
    message-matching alone would start silently skipping typos.
    """
    verdict, task = tolerate(TYPE_MISMATCH, data_type=None)
    errors = [msg for level, msg in task.logger.lines if level == "error"]
    check("org_gate_rejects_unresolvable_tag", verdict is False,
          "a tag absent from the org must re-raise even with the String message")
    check("org_gate_was_actually_consulted", len(task.queries) == 1,
          f"expected exactly one describe query, got {len(task.queries)}")
    check("unresolvable_tag_is_logged_as_an_error",
          any("does not resolve" in m for m in errors),
          "the operator must be told the tag is bad, not just that nothing happened")


def check_org_gate_rejects_an_already_string_tag(_):
    """
    Once the platform types the attribute String, this branch is what stops the
    tolerance from lingering as a blanket skip: the create should succeed, and if it
    somehow still fails the failure is about something else.
    """
    verdict, task = tolerate(TYPE_MISMATCH, data_type="string")
    check("org_gate_rejects_string_typed_tag", verdict is False,
          "a String-typed tag means the rejection is unrelated -- must re-raise")
    check("string_typed_rejection_is_logged_as_an_error",
          any(level == "error" for level, _ in task.logger.lines),
          "must log why it declined to skip")


def check_case_is_not_load_bearing(_):
    """The org returns `string` lowercase here, but casing is not a contract."""
    verdict, _ = tolerate(TYPE_MISMATCH, data_type="String")
    check("string_comparison_is_case_insensitive", verdict is False,
          "'String' and 'string' must both count as String-typed")


def check_record_without_a_tag_is_not_tolerated(_):
    verdict, task = tolerate(TYPE_MISMATCH, record={"DeveloperName": "No_Tag"})
    check("rejects_record_with_no_tag", verdict is False,
          "nothing to verify means nothing to excuse")
    check("no_tag_does_not_query_the_org", task.queries == [],
          "must not query for an empty tag")


def check_unparseable_body_is_safe(_):
    for body in ("<html>502 Bad Gateway</html>", "", "null"):
        verdict, _ = tolerate(body)
        check(f"unparseable_body_rejected[{body[:18] or 'empty'}]", verdict is False,
              "a non-JSON error body must re-raise, not crash or skip")


# ---------------------------------------------------------------------------- #
# Query shape and exception contract
# ---------------------------------------------------------------------------- #


def check_query_targets_title_not_name(_):
    """ContextTag has no Name field, so a Name-based filter would throw MALFORMED_QUERY."""
    _, task = tolerate(TYPE_MISMATCH, data_type="lookup")
    soql = task.queries[0]
    check("query_filters_on_title",
          "Title =" in soql and "Name =" not in soql,
          f"must filter ContextTag on Title. Got: {soql}")
    check("query_reads_the_attribute_type",
          "ContextAttribute.DataType" in soql and "FROM ContextTag" in soql,
          f"must traverse to the attribute's DataType. Got: {soql}")


def check_quotes_in_a_tag_are_escaped(_):
    """A tag value reaches SOQL as a literal, so an apostrophe must not break out.

    Exercises _context_tag_data_type directly rather than through the tolerance. Now that
    the tolerance is pinned to SalesTransactionItemGroup, no quoted tag can reach the
    query by that route -- the tag gate short-circuits first. The escaping is kept and
    tested here anyway: it guards the query builder itself, which is one refactor away
    from being reachable with an arbitrary tag again.
    """
    task = _StubTask("lookup")
    task._context_tag_data_type(
        "tok", "https://example.my.salesforce.com", "68.0", "O'Brien"
    )
    soql = task.queries[0]
    check("tag_literal_is_escaped", r"O\'Brien" in soql,
          f"an embedded quote must be escaped. Got: {soql}")


def check_exception_stays_compatible(_):
    """
    ToolingWriteError must remain a TaskOptionsError: any caller that does not catch
    it -- `_update_record`, and every other path -- has to behave exactly as before.
    """
    check("tooling_error_subclasses_task_options_error",
          issubclass(ToolingWriteError, TaskOptionsError),
          "narrowing the raised type must not change uncaught behaviour")
    exc = ToolingWriteError("Tooling create failed: 400 — body", 400, "body")
    check("tooling_error_carries_the_body",
          exc.body == "body" and exc.status_code == 400
          and "Tooling create failed: 400" in str(exc),
          "the body is what classification reads; the message is what operators read")


def check_create_raises_the_classifiable_error(_):
    """
    Locks the type at the raise site. If `_create_record` reverted to a bare
    TaskOptionsError the except clause would stop matching and the tolerance would
    quietly stop working -- and the giveaway would be a build failure, not a test one.
    Patches sys.modules so the function's own `import requests` resolves to the stub.
    """
    import types

    class _Resp:
        ok = False
        status_code = 400
        text = TYPE_MISMATCH

    stub = types.ModuleType("requests")
    stub.post = lambda *a, **k: _Resp()
    saved = sys.modules.get("requests")
    sys.modules["requests"] = stub
    raised = None
    try:
        ManageFulfillmentScopeCnfg._create_record(
            _StubTask("lookup"), "tok", "https://example.my.salesforce.com", "68.0", {}
        )
    except Exception as exc:
        raised = exc
    finally:
        if saved is None:
            del sys.modules["requests"]
        else:
            sys.modules["requests"] = saved

    check("create_raises_tooling_write_error",
          isinstance(raised, ToolingWriteError),
          f"expected ToolingWriteError, got {type(raised).__name__}")
    check("create_preserves_the_response_body",
          isinstance(raised, ToolingWriteError) and raised.body == TYPE_MISMATCH,
          "the raise site must pass the body through for classification")


# ---------------------------------------------------------------------------- #
# Wiring: the tolerance must be off by default and on only where it is needed
# ---------------------------------------------------------------------------- #


def check_cumulusci_wiring(_):
    import yaml

    cci = yaml.safe_load((REPO / "cumulusci.yml").read_text())
    task_default = (
        cci["tasks"]["manage_fulfillment_scope_cnfg"]["options"]
        .get("on_invalid_context_tag")
    )
    check("task_default_is_fail", task_default == "fail",
          f"the safe default must survive; got {task_default!r}")

    # Both call sites upsert the SAME file into the SAME object, so they must agree --
    # a manual run that behaves differently from the build is a trap for whoever is
    # debugging the build.
    for flow in ("upsert_fulfillment_scope_cnfg", "prepare_dro"):
        steps = cci["flows"][flow]["steps"]
        wired = [
            s.get("options", {}).get("on_invalid_context_tag")
            for s in steps.values()
            if s.get("task") == "manage_fulfillment_scope_cnfg"
        ]
        check(f"{flow}_sets_skip", wired == ["skip"],
              f"expected exactly one step with skip; got {wired}")


def main():
    checks = (
        check_the_264_defect_is_tolerated,
        check_missing_tag_is_not_tolerated,
        check_unrelated_rejection_is_not_tolerated,
        check_a_second_unrelated_error_defeats_the_tolerance,
        check_empty_error_array_is_not_tolerated,
        check_a_different_tag_is_not_tolerated,
        check_a_different_resolvable_type_is_not_tolerated,
        check_org_gate_rejects_a_tag_that_does_not_resolve,
        check_org_gate_rejects_an_already_string_tag,
        check_case_is_not_load_bearing,
        check_record_without_a_tag_is_not_tolerated,
        check_unparseable_body_is_safe,
        check_query_targets_title_not_name,
        check_quotes_in_a_tag_are_escaped,
        check_exception_stays_compatible,
        check_create_raises_the_classifiable_error,
        check_cumulusci_wiring,
    )
    for fn in checks:
        try:
            fn(None)
        except Exception as exc:  # a check that blows up is a failure, not a crash
            check(fn.__name__.replace("check_", ""), False,
                  f"check raised {type(exc).__name__}: {exc}")

    width = max(len(n) for n, _, _ in RESULTS)
    failed = 0
    print("CustomFulfillmentScopeCnfg context-tag tolerance\n" + "=" * (width + 60))
    for name, ok, detail in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'}  {name:<{width}}  {detail}")
        failed += 0 if ok else 1
    print("=" * (width + 60))
    print(f"{len(RESULTS) - failed}/{len(RESULTS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
