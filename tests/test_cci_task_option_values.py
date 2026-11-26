#!/usr/bin/env python3
"""
Task options in cumulusci.yml are values, never option specs.

    ~/.local/pipx/venvs/cumulusci/bin/python tests/test_cci_task_option_values.py

Needs CumulusCI (and its PyYAML); no org.

Why this file exists
--------------------
The `options:` of a task in cumulusci.yml are default *values*. Two tasks carried
`{description, required}` dicts there, as if declaring the option (todo 492). cci
passed the dict to the task as the value: `assign_permission_set_groups_tolerant`
warned "Unknown option type <class 'dict'>" on every run and, without `api_names`,
failed with "can only join an iterable"; `recalculate_permission_set_groups`
without `api_names` failed with "api_names must be a list or comma-separated
string" instead of cci's required-option error. Option specs belong in the class's
`task_options`.
"""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Import before CumulusCI: cumulusci's project_config empties the repo's `tasks` package path.
from tasks.rlm_assign_permission_set_groups import AssignPermissionSetGroupsTolerant  # noqa: E402

from cumulusci.core.config import TaskConfig  # noqa: E402
from cumulusci.core.exceptions import TaskOptionsError  # noqa: E402

SPEC_KEYS = {"description", "required"}

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))


def spec_valued_options(config):
    """(where, option) for every task or flow-step option whose value looks like an option spec."""
    found = []
    for task, body in (config.get("tasks") or {}).items():
        for option, value in ((body or {}).get("options") or {}).items():
            if isinstance(value, dict) and SPEC_KEYS & set(value):
                found.append((f"tasks.{task}", option))
    for flow, body in (config.get("flows") or {}).items():
        for step, spec in ((body or {}).get("steps") or {}).items():
            for option, value in ((spec or {}).get("options") or {}).items():
                if isinstance(value, dict) and SPEC_KEYS & set(value):
                    found.append((f"flows.{flow}.steps.{step}", option))
    return found


def init_tolerant(options):
    task = object.__new__(AssignPermissionSetGroupsTolerant)
    task.task_config = TaskConfig({"options": options})
    task.project_config = None
    task._init_options({})
    return task


def test_no_spec_valued_options():
    config = yaml.safe_load((ROOT / "cumulusci.yml").read_text(encoding="utf-8"))
    found = spec_valued_options(config)
    check("cumulusci.yml has no option spec as an option value", not found,
          ", ".join(f"{where}: {option}" for where, option in found))


def test_detector_flags_a_spec():
    config = {"tasks": {"t": {"options": {"a": {"description": "x", "required": True}, "b": 3}}},
              "flows": {"f": {"steps": {1: {"task": "t", "options": {"c": {"required": False}}}}}}}
    check("detector flags a task option and a flow-step option",
          spec_valued_options(config) == [("tasks.t", "a"), ("flows.f.steps.1", "c")],
          repr(spec_valued_options(config)))


def test_tolerant_requires_api_names():
    try:
        init_tolerant({})
    except TaskOptionsError as e:
        check("assign_permission_set_groups_tolerant without api_names names the option", "api_names" in str(e), str(e))
    except Exception as e:  # noqa: BLE001
        check("assign_permission_set_groups_tolerant without api_names names the option", False,
              f"{type(e).__name__}: {e}")
    else:
        check("assign_permission_set_groups_tolerant without api_names names the option", False, "no error")


def test_tolerant_defaults_to_running_user():
    task = init_tolerant({"api_names": "A, B"})
    check("assign_permission_set_groups_tolerant parses api_names and leaves user_alias empty",
          task.options["api_names"] == ["A", "B"] and not task.options["user_alias"], repr(task.options))


def main():
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    failed = [r for r in RESULTS if not r[1]]
    for name, ok, detail in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail and not ok else ""))
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
