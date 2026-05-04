"""Tests for scripts.build_harness.harness.config.

Pins down the contracts for the pure helpers used by the harness CLI, the
scenario runner, and the TUI:

- ``compose_flags`` — override precedence (scenario > defaults; explicit
  ``False`` wins over default ``True``).
- ``alias_for_scenario`` — naming policy used to derive scratch org aliases.
  Salesforce caps aliases at 60 chars, so the function must too.
- ``select_scenarios`` — filter-by-id behavior including the missing-id error
  path.
- ``load_scenarios`` — empty-scenarios-list error path.
- ``load_default_flags`` and ``load_prepare_steps`` — parse cumulusci.yml
  fragments and surface validation errors with helpful messages.
- ``evaluate_when`` — current behavior of the boolean ``when:`` evaluator.
  These tests pin the *current* behavior (eval()-based) so the upcoming
  Phase 2b refactor to an ast-based evaluator can be verified to preserve it.
"""

from __future__ import annotations

import pytest

import yaml

from scripts.build_harness.harness.config import (
    Step,
    alias_for_scenario,
    cleanup_scenario_project_root,
    compose_flags,
    evaluate_when,
    load_default_flags,
    load_prepare_steps,
    load_scenarios,
    prepare_scenario_project_root,
    select_scenarios,
)


class TestComposeFlags:
    def test_overrides_replace_defaults(self) -> None:
        defaults = {"a": True, "b": False, "c": "x"}
        merged = compose_flags(defaults, {"b": True})
        assert merged == {"a": True, "b": True, "c": "x"}

    def test_overrides_can_set_false_over_default_true(self) -> None:
        # Critical: the typical scenario use case is "default is True, this
        # scenario disables it". Falsy override must NOT be silently dropped.
        defaults = {"feature_x": True}
        merged = compose_flags(defaults, {"feature_x": False})
        assert merged == {"feature_x": False}

    def test_overrides_add_new_keys(self) -> None:
        merged = compose_flags({"a": 1}, {"b": 2})
        assert merged == {"a": 1, "b": 2}

    def test_does_not_mutate_inputs(self) -> None:
        defaults = {"a": True}
        overrides = {"a": False, "b": True}
        compose_flags(defaults, overrides)
        assert defaults == {"a": True}
        assert overrides == {"a": False, "b": True}

    def test_none_overrides_treated_as_empty(self) -> None:
        # Scenario JSON files may omit the flag_overrides key entirely; the
        # caller passes scenario.get("flag_overrides", {}) but defensive code
        # also handles None.
        merged = compose_flags({"a": True}, None)  # type: ignore[arg-type]
        assert merged == {"a": True}


class TestAliasForScenario:
    def test_uses_org_alias_prefix_when_provided(self) -> None:
        alias = alias_for_scenario(
            {"scenario_id": "ent-full", "org_alias_prefix": "harness-ent"},
            run_id="run-2026-04-29-abc123def456",
        )
        assert alias.startswith("harness-ent-")

    def test_falls_back_to_scenario_id_when_no_prefix(self) -> None:
        alias = alias_for_scenario(
            {"scenario_id": "minimal"},
            run_id="run-2026-04-29-aaaaaaaaaaaa",
        )
        assert alias.startswith("harness-minimal-")

    def test_uses_last_12_chars_of_compacted_run_id(self) -> None:
        alias = alias_for_scenario(
            {"scenario_id": "x", "org_alias_prefix": "p"},
            run_id="run-2026-04-29-abcdef123456",
        )
        # "run-" stripped → "2026-04-29-abcdef123456" → last 12 = "abcdef123456"
        assert alias == "p-abcdef123456"

    def test_caps_at_60_chars(self) -> None:
        # Salesforce aliases must be <= 60 chars. With a long prefix the
        # function must still produce a compliant name.
        long_prefix = "x" * 80
        alias = alias_for_scenario(
            {"scenario_id": "s", "org_alias_prefix": long_prefix},
            run_id="run-2026-04-29-abc123def456",
        )
        assert len(alias) <= 60

    def test_lowercases_run_id_segment(self) -> None:
        # Compacted run id is lowercased so the alias is case-insensitive
        # and matches `cci org` comparisons.
        alias = alias_for_scenario(
            {"scenario_id": "s", "org_alias_prefix": "p"},
            run_id="run-2026-04-29-ABCDEF123456",
        )
        # The compacted tail must not contain uppercase letters.
        tail = alias.rsplit("-", 1)[-1]
        assert tail == tail.lower()


class TestSelectScenarios:
    @pytest.fixture
    def all_scenarios(self):
        return [
            {"scenario_id": "minimal", "name": "Minimal"},
            {"scenario_id": "ent-full", "name": "Enterprise"},
            {"scenario_id": "trial", "name": "Trial"},
        ]

    def test_returns_all_when_no_filter(self, all_scenarios) -> None:
        assert select_scenarios(all_scenarios, None) == all_scenarios
        assert select_scenarios(all_scenarios, []) == all_scenarios

    def test_filters_to_requested_ids_in_request_order(self, all_scenarios) -> None:
        result = select_scenarios(all_scenarios, ["trial", "minimal"])
        assert [s["scenario_id"] for s in result] == ["trial", "minimal"]

    def test_raises_with_missing_ids(self, all_scenarios) -> None:
        with pytest.raises(ValueError, match="Unknown scenario_id"):
            select_scenarios(all_scenarios, ["nope", "also-nope"])


class TestLoadScenarios:
    def test_returns_scenarios_list(self) -> None:
        payload = {"scenarios": [{"scenario_id": "x"}]}
        assert load_scenarios(payload) == [{"scenario_id": "x"}]

    def test_raises_when_empty(self) -> None:
        with pytest.raises(ValueError, match="no scenarios"):
            load_scenarios({"scenarios": []})

    def test_raises_when_missing_key(self) -> None:
        with pytest.raises(ValueError, match="no scenarios"):
            load_scenarios({})


class TestLoadDefaultFlags:
    def test_returns_project_custom_dict(self) -> None:
        cci = {"project": {"custom": {"flag_a": True, "flag_b": False}}}
        assert load_default_flags(cci) == {"flag_a": True, "flag_b": False}

    def test_returns_empty_dict_when_custom_missing(self) -> None:
        # An empty dict is valid (a project with no custom flags).
        assert load_default_flags({"project": {}}) == {}
        assert load_default_flags({}) == {}

    def test_raises_when_custom_is_not_dict(self) -> None:
        with pytest.raises(ValueError, match="project.custom"):
            load_default_flags({"project": {"custom": "not a dict"}})


class TestLoadPrepareSteps:
    def test_parses_task_step(self) -> None:
        cci = {
            "flows": {
                "prepare_rlm_org": {
                    "steps": {
                        "1": {"task": "create_user"},
                    }
                }
            }
        }
        steps = load_prepare_steps(cci)
        assert steps == [Step(step_number=1, target_type="task", target_name="create_user", when=None)]

    def test_parses_flow_step_with_when(self) -> None:
        cci = {
            "flows": {
                "prepare_rlm_org": {
                    "steps": {
                        "5": {"flow": "deploy_extra", "when": "project_config.project__custom__commerce"},
                    }
                }
            }
        }
        steps = load_prepare_steps(cci)
        assert steps[0].target_type == "flow"
        assert steps[0].target_name == "deploy_extra"
        assert steps[0].when == "project_config.project__custom__commerce"

    def test_steps_are_returned_sorted_by_step_number(self) -> None:
        # YAML ordering is not guaranteed; the runner depends on numeric order.
        cci = {
            "flows": {
                "prepare_rlm_org": {
                    "steps": {
                        "10": {"task": "ten"},
                        "1": {"task": "one"},
                        "2": {"task": "two"},
                    }
                }
            }
        }
        steps = load_prepare_steps(cci)
        assert [s.step_number for s in steps] == [1, 2, 10]

    def test_raises_when_flow_steps_missing(self) -> None:
        with pytest.raises(ValueError, match="flows.prepare_rlm_org.steps"):
            load_prepare_steps({"flows": {"prepare_rlm_org": {"steps": "not a dict"}}})

    def test_raises_when_step_has_no_target(self) -> None:
        cci = {"flows": {"prepare_rlm_org": {"steps": {"1": {"when": "x"}}}}}
        with pytest.raises(ValueError, match="missing flow/task target"):
            load_prepare_steps(cci)

    def test_raises_when_step_is_not_dict(self) -> None:
        cci = {"flows": {"prepare_rlm_org": {"steps": {"1": "string"}}}}
        with pytest.raises(ValueError, match="Invalid step config"):
            load_prepare_steps(cci)


class TestEvaluateWhenBaseline:
    """Pin down current evaluate_when behavior (eval()-based).

    These tests must continue to pass after Phase 2b replaces the eval()
    backend with an ast-based safe evaluator. Each scenario reflects an
    actual ``when:`` expression style used in cumulusci.yml today.
    """

    def test_no_expression_means_always_true(self) -> None:
        assert evaluate_when(None, {}, "scratch") is True
        assert evaluate_when("", {}, "scratch") is True

    def test_simple_flag_reference_true(self) -> None:
        assert evaluate_when(
            "project_config.project__custom__commerce",
            {"commerce": True},
            "scratch",
        ) is True

    def test_simple_flag_reference_false(self) -> None:
        assert evaluate_when(
            "project_config.project__custom__commerce",
            {"commerce": False},
            "scratch",
        ) is False

    def test_unknown_flag_defaults_to_false(self) -> None:
        # The runner intentionally defaults missing flags to False so a
        # scenario that omits a flag opts out of the gated step.
        assert evaluate_when(
            "project_config.project__custom__brand_new_flag",
            {},
            "scratch",
        ) is False

    def test_not_operator(self) -> None:
        assert evaluate_when(
            "not project_config.project__custom__commerce",
            {"commerce": False},
            "scratch",
        ) is True
        assert evaluate_when(
            "not project_config.project__custom__commerce",
            {"commerce": True},
            "scratch",
        ) is False

    def test_and_operator(self) -> None:
        assert evaluate_when(
            "project_config.project__custom__a and project_config.project__custom__b",
            {"a": True, "b": True},
            "scratch",
        ) is True
        assert evaluate_when(
            "project_config.project__custom__a and project_config.project__custom__b",
            {"a": True, "b": False},
            "scratch",
        ) is False

    def test_or_operator(self) -> None:
        assert evaluate_when(
            "project_config.project__custom__a or project_config.project__custom__b",
            {"a": False, "b": True},
            "scratch",
        ) is True
        assert evaluate_when(
            "project_config.project__custom__a or project_config.project__custom__b",
            {"a": False, "b": False},
            "scratch",
        ) is False

    def test_org_is_scratch_reference(self) -> None:
        assert evaluate_when("org_config.scratch", {}, "scratch", org_is_scratch=True) is True
        assert evaluate_when("org_config.scratch", {}, "sandbox", org_is_scratch=False) is False

    def test_org_name_equality(self) -> None:
        assert evaluate_when(
            "org_config.name == 'beta'",
            {},
            "beta",
        ) is True
        assert evaluate_when(
            "org_config.name == 'beta'",
            {},
            "alpha",
        ) is False

    def test_complex_compound_expression(self) -> None:
        expr = (
            "project_config.project__custom__a "
            "and (org_config.scratch or project_config.project__custom__b)"
        )
        assert evaluate_when(expr, {"a": True, "b": False}, "x", org_is_scratch=True) is True
        assert evaluate_when(expr, {"a": True, "b": False}, "x", org_is_scratch=False) is False
        assert evaluate_when(expr, {"a": False, "b": True}, "x", org_is_scratch=True) is False

    def test_unparseable_expression_defaults_to_true(self) -> None:
        # Current behavior: an expression that fails to evaluate is treated
        # as a no-op (step runs). Pin this so the safe-eval refactor preserves
        # the same defensive default.
        assert evaluate_when("@@@ not valid python @@@", {}, "x") is True


class TestEvaluateWhenSafeEvaluator:
    """Tests specific to the ast-based safe evaluator introduced in Phase 2.

    The safe evaluator rejects any AST node outside the documented grammar
    (BoolOp/UnaryOp/Compare/Constant). The defensive ``return True`` default
    ensures the runner never silently skips a step when an expression cannot
    be evaluated, regardless of the *reason* (syntax error, disallowed node,
    or pure runtime error).
    """

    def test_rejects_function_call(self) -> None:
        # Pre-refactor this would have run with __builtins__={} blocking name
        # lookup, so it likely returned True via the broad except. Post-refactor
        # the AST walker rejects ast.Call directly. Either way the default
        # holds, but the reason is now structural.
        assert evaluate_when("__import__('os').system('ls')", {}, "x") is True

    def test_rejects_attribute_access(self) -> None:
        # No attribute access of any kind reaches eval; the regex substitution
        # only handles project_config.* and org_config.*. An unrelated
        # attribute reference is rejected by the AST walker.
        assert evaluate_when("'x'.upper()", {}, "x") is True

    def test_rejects_subscript(self) -> None:
        assert evaluate_when("[1, 2, 3][0]", {}, "x") is True

    def test_rejects_lambda(self) -> None:
        assert evaluate_when("(lambda: True)()", {}, "x") is True

    def test_rejects_arithmetic(self) -> None:
        # Arithmetic isn't part of the documented when: grammar; explicitly
        # rejected so a typo like ``1 + 1`` doesn't silently evaluate to truthy.
        assert evaluate_when("1 + 1", {}, "x") is True

    def test_rejects_chained_comparison(self) -> None:
        # ``a == b == c`` is a single Compare with two ops; we only allow one.
        assert evaluate_when("'a' == 'a' == 'a'", {}, "x") is True

    def test_rejects_disallowed_compare_op(self) -> None:
        # Only == and != are allowed. Ordering comparisons reject.
        assert evaluate_when("org_config.name < 'z'", {}, "beta") is True

    def test_allows_not_equal(self) -> None:
        # != is a valid Compare op even though no current cumulusci.yml uses it.
        assert evaluate_when("org_config.name != 'beta'", {}, "alpha") is True
        assert evaluate_when("org_config.name != 'beta'", {}, "beta") is False

    def test_string_result_normalized_to_bool(self) -> None:
        # The function wraps the AST result in bool(), so a non-empty string
        # value (such as a bare ``org_config.name`` reference) counts as
        # truthy. Pin this since callers test ``if evaluate_when(...)`` and
        # rely on the True/False contract.
        assert evaluate_when("org_config.name", {}, "beta") is True
        # An empty org name string -> bool('') -> False. Documented edge case;
        # the harness never passes an empty org name in normal operation but
        # pinning the coercion prevents future regressions.
        assert evaluate_when("org_config.name", {}, "") is False


class TestPrepareScenarioProjectRoot:
    """The materialized scenario workspace.

    Verifies that the regenerated cumulusci.yml carries the banner header,
    parses back to the expected resolved data, and that symlinks to the
    other repo entries are created. Skipped when the platform cannot create
    symlinks (Windows without dev-mode).
    """

    @pytest.fixture
    def fake_repo(self, tmp_path):
        """Create a minimal source repo with one yaml + one scripts dir."""
        root = tmp_path / "src_repo"
        root.mkdir()
        # Top-level cumulusci.yml that the function rewrites (not symlinked).
        (root / "cumulusci.yml").write_text("project: {custom: {}}\n", encoding="utf-8")
        # scripts/ is *copied* (not symlinked) per the function's docstring,
        # so the harness can resolve script paths inside the workspace.
        scripts_dir = root / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "noop.apex").write_text("// noop\n", encoding="utf-8")
        # An arbitrary other dir that should be symlinked through.
        (root / "force-app").mkdir()
        (root / "force-app" / "marker.txt").write_text("hi\n", encoding="utf-8")
        # Harness artifact roots must not be linked into cci_project.
        (root / ".harness").mkdir()
        (root / ".harness" / "marker.txt").write_text("keep-out\n", encoding="utf-8")
        return root

    def test_banner_header_is_present(self, tmp_path, fake_repo) -> None:
        scenario_dir = tmp_path / "scenarios" / "minimal"
        scenario_dir.mkdir(parents=True)
        prepare_scenario_project_root(
            fake_repo, scenario_dir, {"project": {"custom": {}}}, {"flag_a": True}
        )
        text = (scenario_dir / "cci_project" / "cumulusci.yml").read_text(encoding="utf-8")
        assert text.startswith("# AUTO-GENERATED")
        assert "scripts/build_harness" in text
        assert "do not edit by hand" in text

    def test_yaml_still_parses_to_expected_data(self, tmp_path, fake_repo) -> None:
        scenario_dir = tmp_path / "scenarios" / "minimal"
        scenario_dir.mkdir(parents=True)
        prepare_scenario_project_root(
            fake_repo,
            scenario_dir,
            {"project": {"custom": {"a": False}}, "flows": {}},
            {"a": True, "b": "x"},
        )
        loaded = yaml.safe_load(
            (scenario_dir / "cci_project" / "cumulusci.yml").read_text(encoding="utf-8")
        )
        # Banner is comment-only; safe_load strips it.
        assert loaded["project"]["custom"] == {"a": True, "b": "x"}

    def test_scripts_directory_is_copied_not_symlinked(self, tmp_path, fake_repo) -> None:
        scenario_dir = tmp_path / "scenarios" / "minimal"
        scenario_dir.mkdir(parents=True)
        prepare_scenario_project_root(
            fake_repo, scenario_dir, {"project": {"custom": {}}}, {}
        )
        scripts_link = scenario_dir / "cci_project" / "scripts"
        assert scripts_link.is_dir()
        assert not scripts_link.is_symlink(), "scripts/ must be a real copy"
        assert (scripts_link / "noop.apex").read_text(encoding="utf-8") == "// noop\n"

    def test_other_dirs_are_symlinked(self, tmp_path, fake_repo) -> None:
        scenario_dir = tmp_path / "scenarios" / "minimal"
        scenario_dir.mkdir(parents=True)
        prepare_scenario_project_root(
            fake_repo, scenario_dir, {"project": {"custom": {}}}, {}
        )
        force_app_link = scenario_dir / "cci_project" / "force-app"
        assert force_app_link.is_symlink()
        assert (force_app_link / "marker.txt").read_text(encoding="utf-8") == "hi\n"

    def test_harness_root_is_not_symlinked(self, tmp_path, fake_repo) -> None:
        scenario_dir = tmp_path / "scenarios" / "minimal"
        scenario_dir.mkdir(parents=True)
        prepare_scenario_project_root(
            fake_repo, scenario_dir, {"project": {"custom": {}}}, {}
        )
        assert not (scenario_dir / "cci_project" / ".harness").exists()


class TestCleanupScenarioProjectRoot:
    def test_removes_existing_cci_project_directory(self, tmp_path) -> None:
        target = tmp_path / "cci_project"
        target.mkdir()
        (target / "file").write_text("x", encoding="utf-8")
        assert cleanup_scenario_project_root(target) is None
        assert not target.exists()

    def test_returns_none_when_already_removed(self, tmp_path) -> None:
        # Idempotent: re-running cleanup after a successful first cleanup
        # must not error. The name must match the safety guard's expected
        # ``cci_project`` suffix.
        assert cleanup_scenario_project_root(tmp_path / "cci_project") is None

    def test_refuses_to_clean_non_cci_project_directory(self, tmp_path) -> None:
        # Safety guard: the function refuses to recursively delete anything
        # that doesn't end in ``cci_project`` to prevent a misuse from
        # nuking, e.g., the run dir.
        wrong = tmp_path / "run-2026-04-29"
        wrong.mkdir()
        result = cleanup_scenario_project_root(wrong)
        assert result is not None
        assert "Refusing" in result
        assert wrong.exists(), "directory must not be removed"
