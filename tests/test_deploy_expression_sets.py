#!/usr/bin/env python3
"""
Offline checks for tasks/rlm_deploy_expression_sets.py (the post-deploy version read-back).

    python tests/test_deploy_expression_sets.py

No org and no `sf` needed; runs with or without CumulusCI installed. The org's
ExpressionSetVersion rows are faked, and so is the deployed package (built here the
way the Deploy task's package is: source files minus what `.forceignore` excludes,
Draft flipped to Active). Why it exists (todo packs 172, 175): a deploy of the repo's
`_V1` succeeds and changes no price when the org executes another version of the
same definition, or when the deploy handler skips a version whose DeveloperName exists
under a different VersionNumber. The read-back turns both into a failed build — and
must expect only what was actually deployed.
"""
import base64
import importlib.util
import io
import logging
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_spec = importlib.util.spec_from_file_location(
    "_rlm_test_deploy_expression_sets", REPO / "tasks" / "rlm_deploy_expression_sets.py"
)
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)

failures = []


def check(label, condition, detail=""):
    print(f"  {'PASS' if condition else 'FAIL'}  {label}{'' if condition else ' — ' + str(detail)}")
    if not condition:
        failures.append(label)


SOURCE_DIR = REPO / "force-app" / "main" / "default" / "expressionSetDefinition"
SOURCE_SUFFIX = ".expressionSetDefinition-meta.xml"
PRICING = "RLM_DefaultPricingProcedure"
V1 = f"{PRICING}_V1"
NOW = datetime(2026, 11, 24, tzinfo=timezone.utc)
# ramp264's version chain (packs 172/175): three active; v40 ran. No Rank was read
# there, so these rows carry none (the resolver then falls back to VersionNumber).
RAMP264 = [
    {"ApiName": V1, "VersionNumber": 1, "IsActive": True},
    {"ApiName": f"{PRICING}_RLM_Rev_Mgmt_Def_and_Promo_Price_Proc_v20", "VersionNumber": 2,
     "IsActive": False},
    {"ApiName": f"{PRICING}_RLM_Rev_Mgmt_Def_and_Partner_Price_Proc_v30", "VersionNumber": 3,
     "IsActive": True},
    {"ApiName": f"{PRICING}_RLM_Rev_Mgmt_Def_Partner_Price_and_Ramp_v40", "VersionNumber": 4,
     "IsActive": True},
]


def forceignored_sources():
    """Expression set source files the repo's real .forceignore lists by exact path."""
    ignored = set()
    for line in (REPO / ".forceignore").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("force-app/main/default/expressionSetDefinition/") \
                and line.endswith(SOURCE_SUFFIX):
            ignored.add(line.rsplit("/", 1)[-1])
    return ignored


def build_package(files):
    """A base64 MDAPI zip like Deploy._get_package_zip returns: package.xml plus one
    expressionSetDefinitions/<Name>.expressionSetDefinition per source file, with the
    activate task's Draft→Active transform applied."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("package.xml", "<Package/>")
        for f in files:
            name = f.name[: -len(SOURCE_SUFFIX)]
            text = f.read_text(encoding="utf-8").replace(
                "<status>Draft</status>", "<status>Active</status>")
            zf.writestr(f"expressionSetDefinitions/{name}.expressionSetDefinition", text)
    return base64.b64encode(buf.getvalue()).decode()


def expected(name=PRICING, api=V1, number=1, status="Active"):
    return {"definition": name, "apiName": api, "versionNumber": number, "status": status}


# ---------------------------------------------------------------------------
print("\n[1] the read-back expects exactly what the deploy sent")

ignored = forceignored_sources()
check("the repo's .forceignore excludes Salesforce_Pricing_Discovery_Procedure",
      f"Salesforce_Pricing_Discovery_Procedure{SOURCE_SUFFIX}" in ignored, ignored)
check("…and that file is in the deployed source path (so reading the path is wrong)",
      (SOURCE_DIR / f"Salesforce_Pricing_Discovery_Procedure{SOURCE_SUFFIX}").is_file())

sent = [f for f in sorted(SOURCE_DIR.glob(f"*{SOURCE_SUFFIX}")) if f.name not in ignored]
package = build_package(sent)
deployed = mod.deployed_versions(package)
names = {v["definition"] for v in deployed}
check("every packaged definition is read, and only those",
      names == {f.name[: -len(SOURCE_SUFFIX)] for f in sent}, sorted(names))
check("a .forceignore'd definition is not expected",
      "Salesforce_Pricing_Discovery_Procedure" not in names, sorted(names))
check("the pricing procedure is expected as deployed: _V1, VersionNumber 1, Active",
      [v for v in deployed if v["definition"] == PRICING] == [expected()],
      [v for v in deployed if v["definition"] == PRICING])
check("a version shipped Inactive stays Inactive in the package (not checked for executing)",
      [v["status"] for v in deployed if v["definition"] == "RLM_DefaultPricingDiscoveryProcedure"]
      == ["Inactive"])
check("no package (nothing deployed) → nothing expected", mod.deployed_versions(None) == [])

yml = (REPO / "cumulusci.yml").read_text(encoding="utf-8")
block = re.search(r"^  activate_and_deploy_expression_sets:\n(.*?)(?=^  \S)", yml, re.S | re.M)
body = block.group(1) if block else ""
check("activate_and_deploy_expression_sets runs this task class",
      "class_path: tasks.rlm_deploy_expression_sets.DeployExpressionSets" in body, body[:300])
check("its version_check is the safe default (fail)", "version_check: fail" in body)

# ---------------------------------------------------------------------------
print("\n[2] read-back findings")

fresh = {PRICING: [{"ApiName": V1, "VersionNumber": 1, "IsActive": True, "Rank": 1}]}
check("a fresh single-version org has no finding",
      mod.version_findings([expected()], fresh, NOW) == [])

chain = mod.version_findings([expected()], {PRICING: RAMP264}, NOW)
check("ramp264 chain (no Rank read): _V1 is active but v40 executes → finding",
      len(chain) == 1 and "does not execute" in chain[0]
      and "Partner_Price_and_Ramp_v40 (v4)" in chain[0], chain)
check("the chain finding points at editing or re-ranking the executing version",
      chain and "set_step_formula.py" in chain[0] and "re-rank" in chain[0], chain)
check("without an org, the finding prints no command",
      chain and "describe_expression_set.py" not in chain[0], chain)
with_org = mod.version_findings([expected()], {PRICING: RAMP264}, NOW, target_org="u@x.test")
check("with the org's username, the finding prints a complete read-only inspect command "
      "for the executing version",
      with_org and "python scripts/expression_sets/describe_expression_set.py "
      f"--target-org u@x.test --developer-name {PRICING} --version "
      f"{PRICING}_RLM_Rev_Mgmt_Def_Partner_Price_and_Ramp_v40 --labels" in with_org[0],
      with_org)

ranked = [dict(r, Rank=r["VersionNumber"]) for r in RAMP264]
ranked[0]["Rank"] = 10
check("Rank decides: the deployed _V1 with the highest Rank executes → no finding",
      mod.version_findings([expected()], {PRICING: ranked}, NOW) == [])
check("…and the Rank/VersionNumber disagreement is warned about",
      "highest VersionNumber" in (mod.rank_order_warning(ranked, NOW) or ""))

expired = [{"ApiName": V1, "VersionNumber": 1, "IsActive": True,
            "EndDateTime": "2020-01-01T00:00:00.000+0000"}]
check("an active version whose window has ended does not execute → finding",
      "date window does not cover now" in " ".join(
          mod.version_findings([expected()], {PRICING: expired}, NOW)))

noop = mod.version_findings(
    [expected()], {PRICING: [{"ApiName": V1, "VersionNumber": 2, "IsActive": True}]}, NOW)
check("same DeveloperName under another VersionNumber is a finding, stated factually",
      len(noop) == 1 and "is VersionNumber 2 in the org but 1 in the deployed package"
      in noop[0] and "silent" not in noop[0], noop)
missing = mod.version_findings([expected()], {PRICING: RAMP264[1:]}, NOW)
check("a deployed version absent from the org is a finding",
      len(missing) == 1 and "no ExpressionSetVersion named" in missing[0], missing)
inactive = mod.version_findings(
    [expected()], {PRICING: [{"ApiName": V1, "VersionNumber": 1, "IsActive": False}]}, NOW)
check("a version deployed Active that reads inactive is a finding",
      len(inactive) == 1 and "inactive" in inactive[0], inactive)
check("a version deployed Inactive is checked for existence and number only",
      mod.version_findings([expected(status="Inactive")], {PRICING: RAMP264}, NOW) == [])

# ---------------------------------------------------------------------------
print("\n[3] the task")


class _FakeSf:
    def __init__(self, sets, versions):
        self.sets, self.versions, self.queries = sets, versions, []

    def query_all(self, soql):
        self.queries.append(soql)
        if "FROM ExpressionSetVersion" in soql:
            return {"records": self.versions}
        return {"records": self.sets}


def make_task(mode, rows, package_b64):
    task = object.__new__(mod.DeployExpressionSets)
    task.logs = []

    class _Capture(logging.Handler):
        def emit(handler, record):
            task.logs.append((record.levelname, record.getMessage()))

    task.logger = logging.getLogger(f"test_deploy_es_{id(task)}")
    task.logger.addHandler(_Capture())
    task.logger.setLevel(logging.INFO)
    task.logger.propagate = False
    task.options = {"version_check": mode}
    task.org_config = type("Org", (), {"name": "tk-org", "username": "u@x.test"})()
    task.version_check = mode
    task._deployed_package = package_b64
    task._sf_client = _FakeSf(
        [{"Id": f"9QL{i}", "ExpressionSetDefinition": {"DeveloperName": d}}
         for i, d in enumerate(sorted(rows))],
        [dict(r, ExpressionSetId=f"9QL{i}")
         for i, d in enumerate(sorted(rows)) for r in rows[d]],
    )
    return task


def deployed_rows():
    return {v["definition"]: [{"ApiName": v["apiName"], "VersionNumber": v["versionNumber"],
                               "IsActive": v["status"] == "Active"}]
            for v in deployed}


ok = make_task("fail", deployed_rows(), package)
ok._check_versions()
check("a fresh build (the real deployed set, the ignored file absent from the org) passes",
      any(f"Version read-back: all {len(deployed)}" in m for _, m in ok.logs), ok.logs)
check("the read-back takes two queries, not one per definition",
      len(ok._sf_client.queries) == 2, ok._sf_client.queries)
check("the queries read Rank and the date window",
      "Rank" in ok._sf_client.queries[1] and "StartDateTime" in ok._sf_client.queries[1])

chain_rows = dict(deployed_rows(), **{PRICING: RAMP264})
failing = make_task("fail", chain_rows, package)
try:
    failing._check_versions()
    raised = None
except mod.CumulusCIFailure as exc:
    raised = exc
check("version_check fail raises on a chain", raised is not None, failing.logs)
check("the failure says the deploy is applied and not to re-run the step",
      raised is not None and "already been applied" in str(raised)
      and "do not re-run it" in str(raised), raised)
check("each finding is logged as an error",
      any(level == "ERROR" and "does not execute" in m for level, m in failing.logs),
      failing.logs)

warning = make_task("warn", chain_rows, package)
warning._check_versions()
check("version_check warn logs the finding as a warning and continues",
      any(level == "WARNING" and "does not execute" in m for level, m in warning.logs)
      and not any(level == "ERROR" for level, _ in warning.logs), warning.logs)

check("the failure names the remedies: run the steps after this one (a harness resume "
      "would re-run it), edit or re-rank the executing version, warn only for future builds",
      raised is not None and "run the prepare_rlm_org steps after this one" in str(raised)
      and "resume restarts at the failed step" in str(raised)
      and "re-rank the executing version" in str(raised)
      and "set_step_formula.py" in str(raised)
      and "the task option -o version_check warn" in str(raised)
      and "the flow option -o activate_and_deploy_expression_sets__version_check warn"
      in str(raised)
      and "On a new build" in str(raised), raised)
check("the failure prints no command that would re-run the step on this org",
      raised is not None and "cci task run" not in str(raised)
      and "cci flow run" not in str(raised) and "--org" not in str(raised), raised)


class _BrokenSf(_FakeSf):
    def query_all(self, soql):
        raise RuntimeError("INVALID_SESSION_ID: session expired")


for mode in ("warn", "fail"):
    broken = make_task(mode, deployed_rows(), package)
    broken._sf_client = _BrokenSf([], [])
    try:
        broken._check_versions()
        broken_raised = None
    except mod.CumulusCIFailure as exc:
        broken_raised = exc
    if mode == "warn":
        check("warn mode: a read-back that cannot query warns and does not fail the build",
              broken_raised is None
              and any(level == "WARNING" and "could not run" in m for level, m in broken.logs),
              (broken_raised, broken.logs))
    else:
        check("fail mode: a read-back that cannot query fails, naming the cause",
              broken_raised is not None and "unverified" in str(broken_raised)
              and any("INVALID_SESSION_ID" in m for _, m in broken.logs),
              (broken_raised, broken.logs))

# The build harness must never retry this step: a retry re-runs a deploy the
# platform refuses on a built org. It classifies a failed step by one line of its
# output (the last with an error keyword; "transient" and "unknown" are retried),
# so render each failure the way `cci` prints a task failure ("Error: <message>",
# wrapped, then its help line) and classify it as the harness does.
from scripts.build_harness.harness.failure import (  # noqa: E402
    classify_signature,
    infer_failure_signature,
)


def cci_output(message, width):
    import textwrap
    lines = ["[11/25/26 07:53:52] Beginning task: DeployExpressionSets"]
    for i, paragraph in enumerate(str(message).split("\n")):
        lines.extend(textwrap.wrap(("Error: " if i == 0 else "") + paragraph, width) or [""])
    lines.append("Run this command for more information about debugging errors: cci error --help")
    return lines


class _TransientSf(_FakeSf):
    def query_all(self, soql):
        raise RuntimeError("HTTPSConnectionPool: Read timed out. (read timeout=30); "
                           "503 Service Unavailable; connection reset")


read_failures = [("a finding", raised)]
for sf_class in (_BrokenSf, _TransientSf):
    task_ = make_task("fail", deployed_rows(), package)
    task_._sf_client = sf_class([], [])
    try:
        task_._check_versions()
    except mod.CumulusCIFailure as exc:
        read_failures.append((sf_class.__name__, exc))
check("every read-back failure ends with the fixed signature line",
      len(read_failures) == 3
      and all(str(e).splitlines()[-1] == mod.READBACK_FAILURE_SIGNATURE
              for _, e in read_failures), read_failures)
for name, exc in read_failures:
    for width in (60, 80, 120, 1000):
        signature = infer_failure_signature(cci_output(exc, width))
        check(f"harness classifies the read-back failure ({name}, width {width}) as "
              "deterministic, so it is not retried",
              signature == mod.READBACK_FAILURE_SIGNATURE
              and classify_signature(signature) == "deterministic", signature)

empty = make_task("fail", {}, None)
empty._check_versions()
check("nothing deployed → nothing to read back, no query",
      empty._sf_client.queries == [], empty._sf_client.queries)

check("version_check parses fail/warn, defaulting to fail",
      mod.version_check_mode(None) == "fail" and mod.version_check_mode(" WARN ") == "warn")
try:
    mod.version_check_mode("skip")
    bad = None
except mod.TaskOptionsError as exc:
    bad = exc
check("an invalid version_check is a TaskOptionsError naming the choices",
      bad is not None and "fail, warn" in str(bad), bad)


# _init_options / _run_task / _get_package_zip call super(): stand the Deploy base
# in with a stub (patched onto the real Deploy when CumulusCI is installed, or
# mixed in after DeployExpressionSets when it is not).
class _BaseStub:
    package = "UEsFBgAAAAAAAAAAAAAAAAAAAAAAAA=="  # an empty zip

    def _init_options(self, kwargs):
        self.options = dict(kwargs)

    def _get_package_zip(self, path):
        return _BaseStub.package

    def _run_task(self):
        self._get_package_zip("path")
        return "deployed"


def stubbed_task():
    base = mod.DeployExpressionSets.__mro__[1]
    if base is object:
        cls = type("_T", (mod.DeployExpressionSets, _BaseStub), {})
        return object.__new__(cls), lambda: None
    saved = {n: base.__dict__.get(n) for n in ("_init_options", "_get_package_zip", "_run_task")}
    for n in saved:
        setattr(base, n, _BaseStub.__dict__[n])

    def restore():
        for n, fn in saved.items():
            if fn is None:
                delattr(base, n)
            else:
                setattr(base, n, fn)
    return object.__new__(mod.DeployExpressionSets), restore


task, restore = stubbed_task()
try:
    try:
        task._init_options({"version_check": "nope"})
        init_error = None
    except mod.TaskOptionsError as exc:
        init_error = exc
    check("_init_options rejects an invalid version_check", init_error is not None, init_error)
    task._init_options({})
    check("_init_options defaults version_check to fail", task.version_check == "fail")

    task.logger = logging.getLogger("test_deploy_es_run")
    calls = []
    task._check_versions = lambda: calls.append("read-back")
    task.check_only = True
    check("check_only: the deploy runs and the read-back is skipped",
          task._run_task() == "deployed" and calls == [], calls)
    task.check_only = False
    check("a real deploy runs the read-back",
          task._run_task() == "deployed" and calls == ["read-back"], calls)
    check("_get_package_zip keeps the package it returns",
          task._deployed_package == _BaseStub.package)
    _BaseStub.package = {"ExpressionSetDefinition": ["X"]}  # a collision map, not a zip
    task._get_package_zip("path")
    check("a collision map (nothing deployed) is not kept as a package",
          task._deployed_package is None)
finally:
    restore()

check("the option is declared on the task",
      "version_check" in mod.DeployExpressionSets.task_options)

print()
if failures:
    print(f"{len(failures)} check(s) FAILED")
    sys.exit(1)
print("all checks passed")
