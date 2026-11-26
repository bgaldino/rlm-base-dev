#!/usr/bin/env python3
"""
Offline checks for tasks/rlm_external_credentials.py and the deploy_quantumbit wiring.

    python tests/test_external_credentials.py

No org required, and no CumulusCI install: the module degrades on ImportError.

Why this exists (todo 481): the public repo committed a real AWS account id as the
SalesforceContractsExtCredentials AwsAccountId. The file now holds a placeholder and
deploy_quantumbit sets the value in the deploy zip from the aws_account_id option or
RLM_AWS_ACCOUNT_ID, or drops the parameter when neither is set. These checks pin that no
12-digit parameterValue is committed, that both deploy shapes come out well-formed, that
a real id pasted or retrieved back into the file fails the deploy, and that the repo file
is never written.
"""
import importlib.util
import io
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import yaml

_spec = importlib.util.spec_from_file_location(
    "_rlm_test_external_credentials", REPO / "tasks" / "rlm_external_credentials.py"
)
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)

CREDENTIAL = REPO / "unpackaged/post_quantumbit/externalCredentials/SalesforceContractsExtCredentials.externalCredential-meta.xml"
NS = "{http://soap.sforce.com/2006/04/metadata}"
CTX = SimpleNamespace(logger=SimpleNamespace(info=lambda *_: None))
FAKE = "000000000000"  # obviously fake; never a real account

failures = []


def check(label, condition, detail=""):
    print(f"  {'PASS' if condition else 'FAIL'}  {label}{'' if condition else ' — ' + str(detail)}")
    if not condition:
        failures.append(label)


def raises(fn):
    try:
        fn()
    except Exception as e:  # noqa: BLE001 - the module's stand-ins are RuntimeError/ValueError
        return str(e)
    return None


def params(xml_text):
    root = ET.fromstring(xml_text)
    return {p.find(NS + "parameterName").text: (p.find(NS + "parameterValue").text if p.find(NS + "parameterValue") is not None else None)
            for p in root.findall(NS + "externalCredentialParameters")}


def package(files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, text in files.items():
            z.writestr(name, text)
    return zipfile.ZipFile(buf)


print("committed metadata")
source = CREDENTIAL.read_bytes()
text = source.decode("utf-8")
committed = params(text)
check("the committed AwsAccountId is the placeholder", committed.get("AwsAccountId") == mod.PLACEHOLDER, committed.get("AwsAccountId"))
check("the placeholder is not an account id", not re.fullmatch(r"[0-9]{12}", mod.PLACEHOLDER))
pattern = re.compile(r"<parameterValue>[0-9]{12}</parameterValue>")
found = [str(p.relative_to(REPO)) for root in ("unpackaged", "force-app", "templates") for p in (REPO / root).rglob("*")
         if p.is_file() and p.suffix == ".xml" and pattern.search(p.read_text(errors="replace"))]
check("no 12-digit parameterValue is committed under unpackaged, force-app or templates", not found, found)

print("resolve_account_id")
check("the option wins over the environment", mod.resolve_account_id("111111111111", {mod.ENV_VAR: FAKE})[0] == "111111111111")
check("the environment is used when the option is unset",
      mod.resolve_account_id(None, {mod.ENV_VAR: FAKE}) == (FAKE, mod.ENV_VAR))
check("an empty option falls back to the environment", mod.resolve_account_id("  ", {mod.ENV_VAR: FAKE})[0] == FAKE)
check("neither set resolves to nothing", mod.resolve_account_id(None, {}) == (None, None)
      and mod.resolve_account_id("", {mod.ENV_VAR: ""}) == (None, None))
check("surrounding whitespace is dropped", mod.resolve_account_id(f" {FAKE}\n", {})[0] == FAKE)
check("a value that isn't 12 digits fails", raises(lambda: mod.resolve_account_id("12345", {})) is not None
      and raises(lambda: mod.resolve_account_id(None, {mod.ENV_VAR: "abcdefghijkl"})) is not None
      and raises(lambda: mod.resolve_account_id("1234567890123", {})) is not None)
check("an unquoted YAML number that lost its leading zero fails", raises(lambda: mod.resolve_account_id(12345678901, {})) is not None)
check("a YAML boolean fails rather than being ignored", raises(lambda: mod.resolve_account_id(True, {mod.ENV_VAR: FAKE})) is not None)
check("the error never echoes the value", "12345" not in (raises(lambda: mod.resolve_account_id("12345", {})) or "12345"))

print("apply_account_id")
name = "externalCredentials/X.externalCredential"
with_value = mod.apply_account_id(text, FAKE, name)
p = params(with_value)
check("a value replaces the placeholder", p.get("AwsAccountId") == FAKE and mod.PLACEHOLDER not in with_value, p)
check("a value leaves every other parameter as committed",
      {k: v for k, v in p.items() if k != "AwsAccountId"} == {k: v for k, v in committed.items() if k != "AwsAccountId"})
without = mod.apply_account_id(text, None, name)
p = params(without)
check("no value drops the AwsAccountId parameter", "AwsAccountId" not in p and mod.PLACEHOLDER not in without, p)
check("no value keeps the other parameters, the principal included",
      p == {k: v for k, v in committed.items() if k != "AwsAccountId"}, p)
check("dropping it leaves no blank line behind", "\n\n" not in without)
real = text.replace(mod.PLACEHOLDER, "222222222222")
check("a real id in the repo file fails instead of deploying",
      "must hold the placeholder" in (raises(lambda: mod.apply_account_id(real, FAKE, name)) or "")
      and "must hold the placeholder" in (raises(lambda: mod.apply_account_id(real, None, name)) or ""))
gone = mod.apply_account_id(text, None, name)
check("a file without the parameter fails", "found 0" in (raises(lambda: mod.apply_account_id(gone, FAKE, name)) or ""))
block = mod.account_block(text, name).group(0)
twice = text.replace(block, block + block)
check("a file with two AwsAccountId parameters fails", "found 2" in (raises(lambda: mod.apply_account_id(twice, FAKE, name)) or ""))

print("transform")
path = mod.package_path(mod.DEFAULT_CREDENTIAL)
check("the package path is the converted file name", path == "externalCredentials/" + CREDENTIAL.name.replace("-meta.xml", ""), path)
files = {path: text, "package.xml": "<Package/>"}
out = mod.AwsAccountIdTransform(mod.DEFAULT_CREDENTIAL, FAKE).process(package(files), CTX)
check("the transform sets the value in the zip", params(out.read(path).decode()).get("AwsAccountId") == FAKE)
check("the transform leaves other files alone", out.read("package.xml").decode() == "<Package/>")
out = mod.AwsAccountIdTransform(mod.DEFAULT_CREDENTIAL, None).process(package(files), CTX)
check("with no value the zip carries no AwsAccountId", "AwsAccountId" not in params(out.read(path).decode()))
check("fails when the credential isn't in the package",
      "not in the deploy package" in (raises(lambda: mod.AwsAccountIdTransform("Other", FAKE).process(package(files), CTX)) or ""))
check("the repo file is never written", CREDENTIAL.read_bytes() == source)

print("task")


class _StubBase:
    transforms = []

    def _init_options(self, kwargs):
        self.options = dict(kwargs)

    def _run_task(self):
        return "deployed"


_BASE = mod.DeployWithAwsAccountId.__mro__[1]
if _BASE is object:
    _Probe, _saved = type("_Probe", (mod.DeployWithAwsAccountId, _StubBase), {}), None
else:
    _Probe, _saved = mod.DeployWithAwsAccountId, (_BASE.__dict__.get("_init_options"), _BASE.__dict__.get("_run_task"))
    _BASE._init_options, _BASE._run_task = _StubBase._init_options, _StubBase._run_task


class Log:
    def __init__(self):
        self.lines = []

    def info(self, m):
        self.lines.append(m)

    warning = info


def run(options, env):
    t = object.__new__(_Probe)
    t.logger = Log()
    saved_env = mod.os.environ.get(mod.ENV_VAR)
    mod.os.environ.pop(mod.ENV_VAR, None)
    if env is not None:
        mod.os.environ[mod.ENV_VAR] = env
    try:
        t._init_options(options)
        result = t._run_task()
    finally:
        mod.os.environ.pop(mod.ENV_VAR, None)
        if saved_env is not None:
            mod.os.environ[mod.ENV_VAR] = saved_env
    return t, result


try:
    shared = _Probe.transforms
    before = list(shared)
    t, result = run({"path": "unpackaged/post_quantumbit"}, None)
    added = [x for x in t.transforms if isinstance(x, mod.AwsAccountIdTransform)]
    check("with nothing configured the task deploys and drops the parameter",
          result == "deployed" and len(added) == 1 and added[0].account_id is None, (result, added))
    check("the class-level transforms list is not mutated", list(shared) == before and t.transforms is not shared)
    check("the log says the parameter is left out", any("without its AwsAccountId" in line for line in t.logger.lines), t.logger.lines)
    t, result = run({"path": "p"}, FAKE)
    added = [x for x in t.transforms if isinstance(x, mod.AwsAccountIdTransform)]
    check("the environment variable reaches the transform", added[0].account_id == FAKE)
    check("the value is never logged", not any(FAKE in line for line in t.logger.lines), t.logger.lines)
    t, result = run({"path": "p", "aws_account_id": "111111111111"}, FAKE)
    check("the option reaches the transform ahead of the environment",
          [x for x in t.transforms if isinstance(x, mod.AwsAccountIdTransform)][0].account_id == "111111111111")
    t, _ = run({"path": "p", "external_credential": "Other"}, None)
    check("external_credential picks the file", [x for x in t.transforms if isinstance(x, mod.AwsAccountIdTransform)][0].path
          == "externalCredentials/Other.externalCredential")
    check("a bad value fails before anything deploys", raises(lambda: run({"path": "p", "aws_account_id": "x"}, None)) is not None)
finally:
    if _saved is not None:
        for attr, value in zip(("_init_options", "_run_task"), _saved):
            if value is None:
                delattr(_BASE, attr)
            else:
                setattr(_BASE, attr, value)

print("wiring")
cfg = yaml.safe_load((REPO / "cumulusci.yml").read_text())
task = cfg["tasks"]["deploy_quantumbit"]
check("deploy_quantumbit uses DeployWithAwsAccountId",
      task["class_path"] == "tasks.rlm_external_credentials.DeployWithAwsAccountId", task["class_path"])
check("deploy_quantumbit deploys post_quantumbit", task["options"]["path"] == "unpackaged/post_quantumbit")
check("no account id is committed in cumulusci.yml", "aws_account_id" not in task.get("options", {}))
others = [n for n, t in cfg["tasks"].items() if n != "deploy_quantumbit"
          and str((t.get("options") or {}).get("path", "")).rstrip("/") == "unpackaged/post_quantumbit"]
check("no other task deploys post_quantumbit around the substitution", not others, others)
steps = [s.get("options", {}) for f in cfg["flows"].values() for s in (f.get("steps") or {}).values()
         if s.get("task") == "deploy_quantumbit"]
check("no flow step commits an account id", not any("aws_account_id" in o for o in steps), steps)

print()
if failures:
    print(f"{len(failures)} failed: {', '.join(failures)}")
    sys.exit(1)
print("All checks passed.")
