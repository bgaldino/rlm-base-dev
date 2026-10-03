#!/usr/bin/env python3
"""
Offline invariants for ValidateCML's per-model validation (``data_dirs``).

    python tests/test_rlm_cml_validate.py

No org and no CumulusCI install required.

Why this file exists
--------------------
``prepare_constraints`` imports four constraint models but validated only one,
and that one through the hand-kept ``scripts/cml/*.cml`` copies, each checked
against a single model's ESC rows. ``data_dirs`` validates each directory's own
``blobs/*.ffxblob`` (what ``import_cml`` uploads) against that directory's ESC
rows. The ESC CSVs key rows by ``ExpressionSet.ApiName``, which differs from the
display ``Name`` for two shipped models ("QuantumBit PCM", "QuantumBit Bundle"),
so the model name must come from ``ApiName`` or every association reads as
missing.
"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tasks.rlm_cml import ValidateCML  # noqa: E402

FAILURES = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}{(' -- ' + detail) if detail else ''}")
        FAILURES.append(label)


class _Log:
    def __init__(self):
        self.lines = []

    def info(self, msg):
        self.lines.append(msg)

    warning = error = info


def _task(**options):
    t = ValidateCML.__new__(ValidateCML)
    t.options = options
    t.logger = _Log()
    return t


def _model_dir(root, api_name, display_name, tags, blob=True):
    d = os.path.join(root, api_name)
    os.makedirs(os.path.join(d, "blobs"))
    with open(os.path.join(d, "ExpressionSet.csv"), "w") as f:
        f.write("ApiName,Name\n" f"{api_name},{display_name}\n")
    with open(os.path.join(d, "ExpressionSetConstraintObj.csv"), "w") as f:
        f.write("ExpressionSet.ApiName,ConstraintModelTag,ConstraintModelTagType\n")
        for tag in tags:
            f.write(f"{api_name},{tag},Type\n")
    if blob:
        with open(os.path.join(d, "blobs", f"ESDV_{api_name}_V1.ffxblob"), "w") as f:
            f.write("type Widget;\n")
    return d


with tempfile.TemporaryDirectory() as root:
    a = _model_dir(root, "ModelA", "Model A", ["Widget"])
    b = _model_dir(root, "ModelB", "ModelB", ["Widget"])

    print("data_dirs validates each directory's own blob against its own rows")
    targets = _task(data_dirs=f"{a},{b}")._collect_targets()
    check("one target per model blob", len(targets) == 2, repr(targets))
    check("each target is checked against its own directory only",
          [t[2] for t in targets] == [[a], [b]], repr(targets))
    check("targets are the .ffxblob files import_cml uploads",
          all(t[0].endswith(".ffxblob") for t in targets), repr(targets))

    print("The model name comes from ApiName, which keys the ESC rows")
    check("ApiName wins over a differing display Name",
          ValidateCML._infer_expression_set_name(targets[0][0], [a]) == "ModelA")
    t = _task(data_dirs=f"{a},{b}")
    t._run_task()
    missing = [line for line in t.logger.lines if "Missing" in line or "not found in CML" in line]
    check("a model whose Name differs from its ApiName reports no false missing associations",
          not missing, repr(missing))

    print("A data directory with no model blob is an error, not a silent skip")
    empty = _model_dir(root, "ModelC", "ModelC", [], blob=False)
    try:
        _task(data_dirs=empty)._collect_targets()
        raised = False
    except Exception as exc:  # TaskOptionsError, or Exception without CumulusCI
        raised = "No .ffxblob" in str(exc)
    check("missing blob raises naming the directory", raised)

    print("Without data_dirs the cml_dir behaviour is unchanged")
    cml_dir = os.path.join(root, "cml")
    os.makedirs(cml_dir)
    Path(cml_dir, "One.cml").write_text("type Widget;\n")
    Path(cml_dir, "notes.txt").write_text("ignored\n")
    legacy = _task(cml_dir=cml_dir, data_dir=a)._collect_targets()
    check("cml_dir .cml files are checked against data_dir",
          legacy == [(os.path.join(cml_dir, "One.cml"), "One.cml", [a])], repr(legacy))

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILING CHECK(S): " + "; ".join(FAILURES))
    sys.exit(1)
print("All checks passed.")
