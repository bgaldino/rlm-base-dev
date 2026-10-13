"""Every action in every workflow is pinned to a full commit SHA (offline, needs PyYAML).

The ESAG GitHub Actions Security Guide requires SHA pins, and the repository setting that
enforces them server-side ("require full-length commit SHA") can be switched off, and doesn't
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

Run: python tests/test_workflow_pins.py
"""
import os
import re
import sys

import yaml

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKFLOWS = os.path.join(REPO, ".github", "workflows")
FULL_SHA_USE = re.compile(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}")
DIGEST = re.compile(r"docker://[^@\s]+@sha256:[0-9a-f]{64}")

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
    found = list(uses_values(yaml.safe_load(text)))
    check(f"{name}: {len(found)} `uses`, all pinned", not bad, bad)

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

print(f"\n{_passed}/{_total} checks passed")
sys.exit(0 if _passed == _total else 1)
