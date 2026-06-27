"""CCI task that runs Agentforce CLI Testing Center specs (`sf agent test`).

Agent behavior is not verifiable by metadata deploy alone — routing and action
invocation have to be exercised against a live, published+activated agent. This
task deploys each YAML test spec under ``tests_path`` as an
``AiEvaluationDefinition`` (``sf agent test create``) and runs it
(``sf agent test run``), then interprets the per-test-case assertion results.

Assertion policy (matches the test-spec skill guidance):
  * ``topic_assertion`` and ``actions_assertion`` are authoritative — any
    non-PASS fails the task.
  * ``output_validation`` is only ignored for the known-harmless case: a
    non-PASS whose error is the "missing expected input" skip AND the test case
    set no ``expectedOutcome``. When a spec *does* set ``expectedOutcome`` (the
    guardrail spec, many action cases), a non-PASS ``output_validation`` is a
    real failure.

Notes:
  * ``--target-org`` is passed explicitly on every CLI call (from
    ``org_config.username``) so the task never silently hits the user's default
    SF CLI org.
  * api-names are derived deterministically from each spec's filename and
    sanitized to the ``AiEvaluationDefinition`` naming rules.
  * ``sf agent test run --wait`` exits non-zero when test cases fail, so the run
    step does NOT use ``run_sf_json`` (which raises on non-zero) — it parses the
    JSON payload regardless of exit code and decides pass/fail from assertions.
"""
import json
import re
import subprocess
from pathlib import Path

try:
    from cumulusci.core.exceptions import CommandException, TaskOptionsError
    from cumulusci.tasks.salesforce import BaseSalesforceTask
except ImportError:  # pragma: no cover - allows bare import in unit context
    BaseSalesforceTask = object
    CommandException = Exception
    TaskOptionsError = Exception

from tasks.rlm_agents_common import run_sf_json

DEFAULT_TESTS_PATH = "unpackaged/post_agents/tests/quote"
DEFAULT_API_NAME_PREFIX = "RLM_Quote"
# Substring that marks the harmless "no expectedOutcome" output_validation skip.
HARMLESS_OUTPUT_SKIP = "missing expected input"
# AiEvaluationDefinition DeveloperName max length.
MAX_API_NAME_LEN = 40


class TestAgents(BaseSalesforceTask):
    """Deploy and run every ``*.yaml`` agent test spec under ``tests_path``."""

    CLI_CREATE_TIMEOUT_SECONDS = 300
    CLI_RUN_TIMEOUT_SECONDS = 1200
    RUN_WAIT_MINUTES = 15

    task_options = {
        "tests_path": {
            "description": (
                "Path (relative to repo root) containing agent test spec YAML "
                f"files. Default: {DEFAULT_TESTS_PATH}"
            ),
            "required": False,
        },
        "api_name_prefix": {
            "description": (
                "Prefix for generated test api-names. Default: "
                f"{DEFAULT_API_NAME_PREFIX}"
            ),
            "required": False,
        },
    }

    def _run_task(self):
        tests_root = Path(self.options.get("tests_path") or DEFAULT_TESTS_PATH)
        prefix = self.options.get("api_name_prefix") or DEFAULT_API_NAME_PREFIX

        if not tests_root.is_dir():
            self.logger.info(f"No test directory at {tests_root}; nothing to run.")
            return

        specs = sorted(tests_root.glob("*.yaml"))
        if not specs:
            self.logger.info(f"No *.yaml specs found under {tests_root}; nothing to run.")
            return

        target = self.org_config.username
        api_names = self._build_api_names(specs, prefix)

        self.logger.info(
            f"Running {len(specs)} agent test spec(s) on {target}: "
            + ", ".join(p.name for p in specs)
        )

        failures = []
        for spec in specs:
            api_name = api_names[spec]
            self._create(spec, api_name, target)
            spec_failures = self._run_and_evaluate(spec, api_name, target)
            failures.extend(spec_failures)

        if failures:
            detail = "\n".join(f"  - {f}" for f in failures)
            raise CommandException(
                f"{len(failures)} agent test assertion(s) failed:\n{detail}"
            )

        self.logger.info("All agent test assertions passed.")

    # -- api-name derivation -------------------------------------------------

    def _build_api_names(self, specs, prefix):
        """Map each spec path to a deterministic, valid, unique api-name."""
        names = {}
        seen = {}
        for spec in specs:
            api_name = self._sanitize_api_name(prefix, spec.stem)
            if api_name in seen:
                raise TaskOptionsError(
                    f"Test specs '{seen[api_name].name}' and '{spec.name}' both map "
                    f"to api-name '{api_name}'. Rename one spec file to disambiguate."
                )
            seen[api_name] = spec
            names[spec] = api_name
        return names

    @staticmethod
    def _sanitize_api_name(prefix, stem):
        """Build a metadata-safe DeveloperName from prefix + file stem.

        Rules: alphanumeric + underscore only, must start with a letter, no
        consecutive or trailing underscores, length-capped.
        """
        raw = f"{prefix}_{stem}"
        # Non-alphanumeric runs collapse to a single underscore.
        cleaned = re.sub(r"[^0-9A-Za-z]+", "_", raw)
        cleaned = re.sub(r"_+", "_", cleaned).strip("_")
        if not cleaned:
            cleaned = "Agent_Test"
        if not cleaned[0].isalpha():
            cleaned = f"X_{cleaned}"
        if len(cleaned) > MAX_API_NAME_LEN:
            cleaned = cleaned[:MAX_API_NAME_LEN].rstrip("_")
        return cleaned

    # -- CLI steps -----------------------------------------------------------

    def _create(self, spec, api_name, target):
        self.logger.info(f"  → sf agent test create --api-name {api_name} ({spec.name})")
        cmd = [
            "sf", "agent", "test", "create",
            "--spec", str(spec),
            "--api-name", api_name,
            "--force-overwrite",
            "--target-org", target,
            "--json",
        ]
        run_sf_json(
            cmd,
            timeout=self.CLI_CREATE_TIMEOUT_SECONDS,
            label=f"sf agent test create ({api_name})",
        )

    def _run_and_evaluate(self, spec, api_name, target):
        """Run one spec and return a list of human-readable failure strings."""
        self.logger.info(f"  → sf agent test run --api-name {api_name}")
        cmd = [
            "sf", "agent", "test", "run",
            "--api-name", api_name,
            "--wait", str(self.RUN_WAIT_MINUTES),
            "--result-format", "json",
            "--json",
            "--target-org", target,
        ]
        # `test run --wait` exits non-zero on test-case failures, so we parse
        # the payload regardless of return code (unlike run_sf_json).
        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=self.CLI_RUN_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as exc:
            raise CommandException(
                f"sf agent test run ({api_name}) timed out after "
                f"{self.CLI_RUN_TIMEOUT_SECONDS}s."
            ) from exc
        except FileNotFoundError as exc:
            raise CommandException(
                "sf agent test run failed: the Salesforce CLI ('sf') was not "
                "found on PATH."
            ) from exc

        payload = {}
        if proc.stdout:
            try:
                payload = json.loads(proc.stdout)
            except json.JSONDecodeError:
                pass

        result = payload.get("result")
        if not isinstance(result, dict) or "testCases" not in result:
            message = (
                payload.get("message")
                or proc.stderr.strip()
                or proc.stdout.strip()
                or f"exit {proc.returncode}"
            )
            raise CommandException(
                f"sf agent test run ({api_name}) produced no parseable results: {message}"
            )

        return self._evaluate_results(spec.name, result)

    # -- assertion evaluation ------------------------------------------------

    def _evaluate_results(self, spec_name, result):
        failures = []
        test_cases = result.get("testCases") or []
        passed = 0

        for case in test_cases:
            num = case.get("testNumber", "?")
            utterance = (case.get("inputs") or {}).get("utterance", "")
            had_expected_outcome = self._had_expected_outcome(case)
            case_failures = []

            for assertion in case.get("testResults") or []:
                name = assertion.get("name")
                outcome = (assertion.get("result") or "").upper()
                if outcome == "PASS":
                    continue

                if name in ("topic_assertion", "actions_assertion"):
                    # `sf agent test create` always emits a topic/action
                    # expectation block even when the spec omits expectedTopic /
                    # expectedActions — it just has an empty expectedValue, which
                    # can never PASS. An assertion with no expected value is not
                    # a real assertion, so don't count it as a failure. (An
                    # actions_assertion that legitimately expects "no actions"
                    # carries expectedValue '[]', not '', so it is preserved.)
                    if self._has_no_expected_value(assertion):
                        continue
                    case_failures.append(self._format_failure(assertion))
                elif name == "output_validation":
                    if self._is_real_output_failure(assertion, had_expected_outcome):
                        case_failures.append(self._format_failure(assertion))
                # Other assertion types (metrics, custom) are advisory here.

            if case_failures:
                for cf in case_failures:
                    failures.append(f"[{spec_name}] case {num} (\"{utterance}\"): {cf}")
            else:
                passed += 1

        self.logger.info(
            f"    {spec_name}: {passed}/{len(test_cases)} test case(s) passed"
        )
        return failures

    @staticmethod
    def _had_expected_outcome(case):
        """True if the test case set an expectedOutcome.

        The result JSON does not echo the spec input, so infer from the
        output_validation assertion: when expectedOutcome is omitted, the
        framework reports the harmless "missing expected input" skip; when set,
        it carries a real expected/actual comparison.
        """
        for assertion in case.get("testResults") or []:
            if assertion.get("name") != "output_validation":
                continue
            err = (assertion.get("errorMessage") or "").lower()
            if HARMLESS_OUTPUT_SKIP in err:
                return False
            return True
        return False

    @staticmethod
    def _has_no_expected_value(assertion):
        """True if a topic/action assertion carries no expected value.

        The create command emits an empty expectation block for any dimension
        the spec left unset, which the runtime then reports as a non-PASS with a
        blank expectedValue. Treat that as "nothing asserted", not a failure.
        """
        expected = assertion.get("expectedValue")
        if expected is None:
            return True
        return str(expected).strip() == ""

    @staticmethod
    def _is_real_output_failure(assertion, had_expected_outcome):
        if not had_expected_outcome:
            return False
        err = (assertion.get("errorMessage") or "").lower()
        # Defensive: never count the harmless skip even if outcome inference drifts.
        if HARMLESS_OUTPUT_SKIP in err:
            return False
        return True

    @staticmethod
    def _format_failure(assertion):
        name = assertion.get("name")
        expected = assertion.get("expectedValue")
        actual = assertion.get("actualValue")
        err = assertion.get("errorMessage")
        parts = [f"{name} {assertion.get('result')}"]
        if expected not in (None, ""):
            parts.append(f"expected={expected!r}")
        if actual not in (None, ""):
            parts.append(f"actual={actual!r}")
        if err:
            parts.append(f"error={err}")
        return " ".join(parts)
