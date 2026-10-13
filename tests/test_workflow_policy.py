"""Workflow security policy, from the ESAG GitHub Actions Security Guide (offline, needs PyYAML).

Every workflow in .github/workflows must:

1. pin every action to a full commit SHA;
2. use only actions from an allowed owner (GitHub-authored, verified creators, or approved);
3. declare a top-level `permissions:` block, so a job that doesn't name its own starts with
   nothing rather than the repository default;
4. keep `${{ }}` expressions out of `run:` scripts. Values reach a script through `env:`, so
   neither untrusted input nor a secret is interpolated into the script text (script injection,
   or a secret written into the generated script file).

Repository settings enforce some of this server-side, but they can be switched off and don't
travel with the code to the SalesforceLabs mirror. This suite is the in-repo guard that still
fails a PR then.

It reads the *parsed* workflow, not its source text: YAML has more ways to spell a key than a
line pattern can track (`uses :`, `"uses":`, `- { uses: … }`, `"u\\u0073es":`, an explicit
`? uses`), and the parser resolves all of them. Every `uses` key anywhere in a workflow counts,
whether it's a step's action or a job's reusable workflow, and its value must be one of:

- `owner/repo[/path]@<40-hex SHA>`,
- a local `./path` (no remote ref to pin), or
- a `docker://image@sha256:<digest>`.

Anything else, including a non-string value, is unpinned.

Run: python tests/test_workflow_policy.py
"""
import os
import re
import sys

import yaml

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKFLOWS = os.path.join(REPO, ".github", "workflows")
FULL_SHA_USE = re.compile(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}")
DIGEST = re.compile(r"docker://[^@\s]+@sha256:[0-9a-f]{64}")
# Owners whose actions may be used. `actions` and `github` are GitHub-authored; `docker` is a
# Marketplace verified creator. `anthropics/claude-code-action` is in use pending approval
# (#ask-enterprise-security, per the guide); remove it here if that approval is refused.
ALLOWED_OWNERS = {"actions", "github", "docker", "anthropics"}
EXPRESSION = re.compile(r"\$\{\{")

_passed = _total = 0


def check(label, ok, detail=""):
    global _passed, _total
    _total += 1
    _passed += bool(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + ("" if ok else f"\n         {detail}"))


def pinned(value) -> bool:
    if not isinstance(value, str):
        return False
    return (value.startswith("./") or bool(FULL_SHA_USE.fullmatch(value))
            or bool(DIGEST.fullmatch(value)))


def uses_values(node, path="$"):
    """Every (path, value) of a `uses` key anywhere in a parsed document."""
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}"
            if key == "uses":
                yield here, value
            yield from uses_values(value, here)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            yield from uses_values(item, f"{path}[{i}]")


def owner(value: str) -> str:
    return value.split("/", 1)[0] if isinstance(value, str) and "/" in value else ""


def disallowed_in(doc):
    return [f"{where}: {value!r}" for where, value in uses_values(doc)
            if isinstance(value, str) and not value.startswith(("./", "docker://"))
            and owner(value) not in ALLOWED_OWNERS]


def run_scripts(doc):
    """Every (path, script) of a step's `run:` in a parsed workflow."""
    for job_name, job in ((doc or {}).get("jobs") or {}).items():
        for i, step in enumerate((job or {}).get("steps") or []):
            if isinstance(step, dict) and "run" in step:
                yield f"jobs.{job_name}.steps[{i}] ({step.get('name', '')})", str(step["run"])


def interpolating_in(doc):
    return [where for where, script in run_scripts(doc) if EXPRESSION.search(script)]


def unpinned_in(text: str):
    return [f"{where}: {value!r}" for where, value in uses_values(yaml.safe_load(text))
            if not pinned(value)]


print("\nEvery action in every workflow is pinned to a full commit SHA")
names = sorted(n for n in os.listdir(WORKFLOWS) if n.endswith((".yml", ".yaml")))
check("there are workflows to check", bool(names), WORKFLOWS)
for name in names:
    with open(os.path.join(WORKFLOWS, name), encoding="utf-8") as fh:
        text = fh.read()
    try:
        bad = unpinned_in(text)
    except yaml.YAMLError as exc:
        check(f"{name} parses", False, exc)
        continue
    doc = yaml.safe_load(text)
    found = list(uses_values(doc))
    check(f"{name}: {len(found)} `uses`, all pinned", not bad, bad)
    check(f"{name}: every action from an allowed owner", not disallowed_in(doc), disallowed_in(doc))
    check(f"{name}: a top-level permissions block", isinstance(doc, dict) and "permissions" in doc,
          "add `permissions: {}` (or the least the workflow needs) at the top level")
    check(f"{name}: no ${{{{ }}}} interpolated into a run script", not interpolating_in(doc),
          interpolating_in(doc))

print("\nThe rule reads the parsed key, however YAML spells it")
SHA = "c" * 40
for label, doc, ok in (
        ("a release tag", "steps:\n  - uses: actions/checkout@v6\n", False),
        ("a branch", "steps:\n  - uses: docker/login-action@master\n", False),
        ("a short SHA", "steps:\n  - uses: actions/checkout@abc1234\n", False),
        ("a space before the colon", "steps:\n  - uses : actions/checkout@v6\n", False),
        ("a quoted key", 'steps:\n  - "uses": actions/checkout@v6\n', False),
        ("a unicode-escaped key", 'steps:\n  - "u\\u0073es": actions/checkout@v6\n', False),
        ("an explicit key", "steps:\n  - ? uses\n    : actions/checkout@v6\n", False),
        ("a flow mapping", "steps: [{name: x, uses: actions/checkout@v6}]\n", False),
        ("a block scalar", "steps:\n  - uses: >-\n      actions/checkout@v6\n", False),
        ("a non-string value", "steps:\n  - uses: [actions/checkout]\n", False),
        ("a job's reusable workflow by tag", "jobs:\n  x:\n    uses: o/r/.github/workflows/w.yml@v1\n",
         False),
        ("a full SHA", f"steps:\n  - uses: actions/cache@{SHA}  # v5.1.0\n", True),
        ("a full SHA in a flow mapping", f"steps: [{{uses: actions/cache@{SHA}}}]\n", True),
        ("a reusable workflow by SHA", f"jobs:\n  x:\n    uses: o/r/.github/workflows/w.yml@{SHA}\n",
         True),
        ("a local action", "steps:\n  - uses: ./.github/actions/setup\n", True),
        ("a docker image by digest", "steps:\n  - uses: docker://alpine@sha256:" + "a" * 64 + "\n",
         True),
        ("a docker image by tag", "steps:\n  - uses: docker://alpine:3.20\n", False)):
    found = list(uses_values(yaml.safe_load(doc)))
    check(f"that rule {'accepts' if ok else 'rejects'} {label}",
          bool(found) and (not unpinned_in(doc)) is ok, doc.strip())

print("\nThe other rules reject what they exist to reject")
check("an action from a personal account is disallowed",
      bool(disallowed_in({"steps": [{"uses": f"peter-evans/create-pull-request@{SHA}"}]})))
check("a GitHub-authored action is allowed",
      not disallowed_in({"steps": [{"uses": f"actions/checkout@{SHA}"}]}))
check("an expression in a run script is caught",
      bool(interpolating_in({"jobs": {"j": {"steps": [{"run": 'echo "${{ github.event.issue.title }}"'}]}}})))
check("the same value through env is not",
      not interpolating_in({"jobs": {"j": {"steps": [{"env": {"T": "${{ github.event.issue.title }}"},
                                                      "run": 'echo "$T"'}]}}}))

print(f"\n{_passed}/{_total} checks passed")
sys.exit(0 if _passed == _total else 1)
