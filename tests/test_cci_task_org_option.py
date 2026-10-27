#!/usr/bin/env python3
"""
Every task class under tasks/ that reads the org must accept --org.

    ~/.local/pipx/venvs/cumulusci/bin/python tests/test_cci_task_org_option.py

Needs CumulusCI (it imports each task class the way cci does, plus any
unregistered BaseTask subclass in tasks/); no org.

Why this file exists
--------------------
cci offers `--org` only when the task class sets `salesforce_task`
(`cumulusci/cli/task.py`). Plain `BaseTask` and `SFDXBaseTask` leave it False,
so a task built on them that reads `self.org_config` still runs -- against the
default org -- but rejects `--org <alias>` with "No such option". Twenty-four
classes shipped that way (todo 244), which forced "switch the default org, run,
switch it back" workarounds. This asserts the flag for every class that touches
`org_config`, and that no class also declares an `org` task option (cci would
then register `--org` twice).
"""
import inspect
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# self.sf / tooling / bulk exist only on org-bound bases, so they count as org use too.
ORG_USE = re.compile(
    r"self\.org_config\b|getattr\(\s*self\s*,\s*[\"']org_config[\"']|self\.(?:sf|tooling|bulk)\b"
)

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))


def reads_org(cls):
    """True when a repo-defined class in the MRO uses self.org_config, sf, tooling or bulk."""
    for klass in cls.__mro__:
        if not klass.__module__.startswith("tasks."):
            continue
        try:
            source = inspect.getsource(klass)
        except (OSError, TypeError):
            continue
        if ORG_USE.search(source):
            return True
    return False


def unregistered_classes(registered, base):
    """BaseTask subclasses defined under tasks/ that no cumulusci.yml task names."""
    import importlib

    found = {}
    for path in sorted((ROOT / "tasks").glob("*.py")):
        module_name = f"tasks.{path.stem}"
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:
            check(module_name, False, f"cannot import: {type(exc).__name__}: {exc}")
            continue
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ == module_name and issubclass(cls, base) and cls not in registered:
                found[f"{module_name}.{cls.__name__}"] = cls
    return found


def main():
    try:
        from cumulusci.cli.runtime import CliRuntime
        from cumulusci.core.tasks import BaseTask
        from cumulusci.core.config import TaskConfig
        from cumulusci.core.utils import import_global
    except ImportError as exc:
        print(f"FAIL  CumulusCI is required: {exc}")
        return 1
    import yaml

    os.chdir(ROOT)
    runtime = CliRuntime(load_keychain=False)
    project = runtime.project_config
    local = yaml.safe_load((ROOT / "cumulusci.yml").read_text(encoding="utf-8"))["tasks"]

    classes = {}
    for name in sorted(local):
        class_path = project.get_task(name).class_path
        try:
            classes[name] = (class_path, import_global(class_path))
        except Exception as exc:  # an unimportable task is a failure, not a skip
            check(name, False, f"cannot import {class_path}: {type(exc).__name__}: {exc}")
    # Unregistered classes too, so one gains --org before anyone wires it up.
    registered = {cls for _, cls in classes.values()}
    for class_path, cls in unregistered_classes(registered, BaseTask).items():
        classes[class_path] = (class_path, cls)

    org_tasks = 0
    for name, (class_path, cls) in classes.items():
        if "org" in (cls.task_options or {}) and cls.salesforce_task:
            check(name, False, f"{class_path} declares an 'org' option and sets salesforce_task")
        if reads_org(cls):
            org_tasks += 1
            if not cls.salesforce_task:
                check(name, False, f"{class_path} reads org_config but salesforce_task is False")
    check("org-reading tasks found", org_tasks > 0, f"{org_tasks} tasks")

    # A dry run (deploy: false) needs no org, so the instance drops the requirement.
    from tasks.rlm_ux_assembly import AssembleAndDeployUX

    for deploy, expected in (("false", False), ("true", True)):
        task = AssembleAndDeployUX(project, TaskConfig({"options": {"deploy": deploy}}))
        check(f"assemble_and_deploy_ux deploy={deploy}", task.salesforce_task is expected,
              f"salesforce_task={task.salesforce_task}")

    # Without an org, the best-effort repair warns and exits 0 instead of failing in __call__.
    from tasks.rlm_fix_scratch_identity import FixScratchOrgIdentity

    for raise_on_failure, expected in ((False, False), (True, True)):
        task = FixScratchOrgIdentity(
            project, TaskConfig({"options": {"raise_on_failure": raise_on_failure}})
        )
        check(f"fix_scratch_org_identity no org, raise_on_failure={raise_on_failure}",
              task.salesforce_task is expected, f"salesforce_task={task.salesforce_task}")

    failed = [r for r in RESULTS if not r[1]]
    for name, ok, detail in RESULTS:
        if not ok or name.startswith(("org-reading", "assemble", "fix_scratch")):
            print(f"  {'PASS' if ok else 'FAIL'}  {name}  {detail}")
    print(f"{len(classes)} tasks and unregistered classes checked; {len(failed)} failure(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
