"""Workflow security policy, from the ESAG GitHub Actions Security Guide (offline, needs PyYAML).

Every workflow in .github/workflows must:

1. pin every action to a full commit SHA;
2. use only actions from an allowed owner (GitHub-authored, verified creators, or approved);
3. declare a top-level `permissions:` mapping (or `read-all`) with no write scope, so a job
   that doesn't name its own starts read-only or with nothing; `write-all`, an empty value and a
   top-level write all fail. A job's own block may name the write scopes it uses, but not
   `write-all` or an empty value;
4. keep `${{ }}` expressions out of scripts: `run:`, and the `script` of `actions/github-script`.
   Values reach a script through `env:`, so neither untrusted input nor a secret is interpolated
   into the script text (script injection, or a secret written into the generated script
   file). An expression in an action input (`with:`) may reference only allowlisted contexts
   (secrets, step outputs, runner/matrix/vars/env/needs/inputs, and `github` fields no outside
   contributor sets), because an input reaches an action as text it may run or follow, a prompt
   included, and the attacker-controlled fields can't be listed completely. `env.NAME` is
   resolved to its definition, and matrix values and job outputs are held to the same rule, so
   none of them launders an untrusted value; what can't be resolved fails closed. Every local action
   reachable from a workflow (`uses: ./path`, followed through other local actions), and any
   under `.github/actions/`, is held to the same rules; a `./` reference with nothing behind it
   fails.

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
ALLOWED_OWNERS = {"actions", "github", "docker", "anthropics"}  # compared case-insensitively
# `docker://` images skip the owner list, so each must be approved by name (none are in use).
ALLOWED_IMAGES: set = set()
EXPRESSION = re.compile(r"\$\{\{")
# An expression in an action input may reference only contexts known to be safe: an allowlist,
# because a list of the attacker-controlled fields (titles, bodies, branch names, commit
# messages, in dotted, indexed or bracketed form) never ends. Writers-only `inputs`, step
# outputs, secrets and runner/matrix/vars/env/needs values are allowed; of `github`, only fields
# no outside contributor sets.
def expressions(text: str):
    """The body of each `${{ … }}`, ending at the first `}}` outside a '…' string literal."""
    out, i = [], 0
    while True:
        start = text.find("${{", i)
        if start < 0:
            return out
        j, quoted = start + 3, False
        while j < len(text):
            if text[j] == "'":
                quoted = not quoted  # '' (an escaped quote) toggles twice
            elif not quoted and text.startswith("}}", j):
                break
            j += 1
        out.append(text[start + 3:j])
        i = j + 2
CONTEXT_REF = re.compile(r"(?<![\w.'\"])([A-Za-z_][\w-]*)((?:\.[\w-]+|\[[^\]]*\])*)")
SAFE_ROOTS = {"secrets", "steps", "runner", "env", "matrix", "vars", "needs", "inputs", "job",
              "strategy"}
SAFE_GITHUB = {"repository", "repository_owner", "repository_id", "run_id", "run_number",
               "run_attempt", "sha", "server_url", "api_url", "graphql_url", "workflow", "job",
               "event_name", "actor", "token", "action", "workspace",
               "event.pull_request.number", "event.number", "event.repository.default_branch",
               "event.repository.full_name", "event.repository.name"}
FUNCTIONS = {"format", "contains", "startsWith", "endsWith", "join", "toJSON", "fromJSON",
             "hashFiles", "success", "always", "cancelled", "failure", "true", "false", "null",
             "NaN", "Infinity"}

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
    return value.split("/", 1)[0].lower() if isinstance(value, str) and "/" in value else ""


def allowed(value) -> bool:
    if not isinstance(value, str):
        return False
    if value.startswith("./"):
        return True
    if value.startswith("docker://"):
        return value[len("docker://"):].split("@", 1)[0] in ALLOWED_IMAGES
    return owner(value) in ALLOWED_OWNERS


def disallowed_in(doc):
    return [f"{where}: {value!r}" for where, value in uses_values(doc) if not allowed(value)]


def permissions_problem(doc):
    """Why a workflow's top-level permissions aren't least-privilege, or None."""
    if not isinstance(doc, dict) or "permissions" not in doc:
        return "no top-level permissions block; add `permissions: {}` or the least it needs"
    value = doc["permissions"]
    if value == "read-all" or value == {}:
        return None
    if not isinstance(value, dict):
        return f"top-level permissions is {value!r}; use a mapping, `{{}}` or `read-all`"
    writes = sorted(k for k, v in value.items() if v != "read" and v != "none")
    return f"top-level write scopes {writes}; grant them in the job that needs them" if writes else None


def job_permissions_problems(doc):
    """Jobs whose own permissions aren't scoped. A job may grant the specific scopes it uses
    (`contents: write`), which is the point of keeping the top level empty; a blanket
    `write-all`, an empty value, or anything but a mapping or `read-all` fails."""
    out = []
    for job_name, job in ((doc or {}).get("jobs") or {}).items():
        if not isinstance(job, dict) or "permissions" not in job:
            continue  # inherits the top level, which permissions_problem() already holds
        value = job["permissions"]
        if value == "read-all" or isinstance(value, dict):
            bad = sorted(k for k, v in (value.items() if isinstance(value, dict) else [])
                         if v not in ("read", "write", "none"))
            if bad:
                out.append(f"jobs.{job_name}.permissions: unknown levels for {bad}")
            continue
        out.append(f"jobs.{job_name}.permissions is {value!r}; name the scopes the job uses")
    return out


def steps_of(doc):
    """(path, step) for every step: a workflow's jobs, or a composite action's runs.steps."""
    doc = doc or {}
    for job_name, job in (doc.get("jobs") or {}).items():
        for i, step in enumerate((job or {}).get("steps") or []):
            yield f"jobs.{job_name}.steps[{i}]", step
    for i, step in enumerate(((doc.get("runs") or {}).get("steps")) or []):
        yield f"runs.steps[{i}]", step


def run_scripts(doc):
    """Every (path, script) a step runs: `run:`, or the `script` of actions/github-script."""
    for where, step in steps_of(doc):
        if not isinstance(step, dict):
            continue
        label = f"{where} ({step.get('name', '')})"
        if "run" in step:
            yield label, str(step["run"])
        uses = step.get("uses")
        if isinstance(uses, str) and uses.lower().startswith("actions/github-script@"):
            yield label + " with.script", str((step.get("with") or {}).get("script", ""))


def _strings(node):
    """Every string anywhere in a parsed YAML value."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from _strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _strings(value)


def _layer(node):
    """An `env:` block as a lookup layer: a mapping, or None when absent."""
    return node if isinstance(node, dict) or node is None else str(node)


def unsafe_references(value, env=()):
    """Context references in `${{ }}` expressions that aren't on the allowlist.

    `env` is the env blocks visible to the expression, outermost first (workflow, job, step).
    `env.NAME` resolves to the innermost definition, which is held to the same rule against the
    blocks outside it, as GitHub evaluates it; so an env variable can't launder an untrusted
    value. What the check can't resolve fails closed: indexing into `env`, an `env:` that is
    itself an expression, and any `[...]` index that isn't a literal, a number or `*` (it would
    pick which secret or output reaches the input). A name no block defines passes: a script can
    set it through $GITHUB_ENV, which is beyond what a static check can follow."""
    out = []
    for expression in expressions(str(value)):
        code = re.sub(r"'(?:[^']|'')*'", "''", expression)  # string literals aren't references
        for root, rest in CONTEXT_REF.findall(code):
            if root in FUNCTIONS or root.isdigit():
                continue
            if any(index not in ("''", "*") and not index.isdigit()
                   for index in re.findall(r"\[([^\]]*)\]", rest)):
                out.append(root + rest)
            elif root == "github":
                field = rest[1:] if rest.startswith(".") else rest
                if field not in SAFE_GITHUB:
                    out.append(f"github{rest}")
            elif root == "env" and env:
                name = rest[1:].split(".", 1)[0] if rest.startswith(".") else None
                for k in range(len(env) - 1, -1, -1):
                    layer = env[k]
                    if name is None or isinstance(layer, str):
                        out.append(f"env{rest} (unresolvable)")
                        break
                    if layer and name in layer:
                        out += [f"env.{name} -> {r}" for r in unsafe_references(layer[name], env[:k])]
                        break
            elif root not in SAFE_ROOTS:
                out.append(root + rest)
    return out


def untrusted_inputs_in(doc):
    """Values that reach an action or a job from a context not known to be safe: a step's
    `with:`, a reusable-workflow job's `with:`, and a job's `strategy` (matrix values) and
    `outputs` (read downstream as `needs.<job>.outputs`). A step output written by a script
    is trusted: what a script prints is beyond what a static check can follow."""
    doc = doc if isinstance(doc, dict) else {}
    top = [_layer(doc.get("env"))]
    out = []

    def scan(where, block, env):
        if isinstance(block, str):
            block = {"": block}
        for key, value in block.items() if isinstance(block, dict) else []:
            bad = [r for text in _strings(value) for r in unsafe_references(text, env)]
            if bad:
                out.append(f"{where}.{key}: {bad}" if key != "" else f"{where}: {bad}")

    if isinstance(doc.get("env"), str):
        scan("env", doc["env"], ())
    for job_name, job in (doc.get("jobs") or {}).items():
        if not isinstance(job, dict):
            continue
        where = f"jobs.{job_name}"
        if isinstance(job.get("env"), str):
            scan(f"{where}.env", job["env"], top)
        job_env = top + [_layer(job.get("env"))]
        scan(f"{where}.with", job.get("with"), top)  # a reusable-workflow call
        scan(f"{where}.strategy", job.get("strategy"), ())
        scan(f"{where}.outputs", job.get("outputs"), job_env)
        for i, step in enumerate(job.get("steps") or []):
            if isinstance(step, dict):
                if isinstance(step.get("env"), str):
                    scan(f"{where}.steps[{i}].env", step["env"], job_env)
                scan(f"{where}.steps[{i}].with", step.get("with"), job_env + [_layer(step.get("env"))])
    runs = doc.get("runs") if isinstance(doc.get("runs"), dict) else {}
    for i, step in enumerate(runs.get("steps") or []):
        if isinstance(step, dict):
            if isinstance(step.get("env"), str):
                scan(f"runs.steps[{i}].env", step["env"], ())
            scan(f"runs.steps[{i}].with", step.get("with"), [_layer(step.get("env"))])
    return out


def interpolating_in(doc):
    return [where for where, script in run_scripts(doc) if EXPRESSION.search(script)]


def unpinned_in(text: str):
    return [f"{where}: {value!r}" for where, value in uses_values(yaml.safe_load(text))
            if not pinned(value)]


print("\nEvery workflow (and local composite action) meets the policy")
ACTIONS = os.path.join(REPO, ".github", "actions")
names = sorted(n for n in os.listdir(WORKFLOWS) if n.endswith((".yml", ".yaml")))
check("there are workflows to check", bool(names), WORKFLOWS)
local_actions = []
for root, _, files in os.walk(ACTIONS) if os.path.isdir(ACTIONS) else []:
    local_actions += [os.path.relpath(os.path.join(root, f), WORKFLOWS) for f in files
                      if f in ("action.yml", "action.yaml")]
# And every local action reachable from a workflow, wherever it lives (`uses: ./tools/setup`),
# following local actions that use other local actions. A `./` reference with no action.yml
# behind it is a failure, not a skip.
missing_local = []
queue = list(names) + list(local_actions)
seen = set()
while queue:
    name = queue.pop()
    if name in seen:
        continue
    seen.add(name)
    with open(os.path.join(WORKFLOWS, name), encoding="utf-8") as fh:
        refs = [r for _, r in uses_values(yaml.safe_load(fh.read()))
                if isinstance(r, str) and r.startswith("./")]
    for ref in refs:
        target = os.path.normpath(os.path.join(REPO, ref[2:]))
        if target.endswith((".yml", ".yaml")):  # a local reusable workflow, scanned as one
            continue
        found = [os.path.relpath(os.path.join(target, f), WORKFLOWS)
                 for f in ("action.yml", "action.yaml") if os.path.isfile(os.path.join(target, f))]
        if not found:
            missing_local.append(f"{name}: {ref}")
        for rel in found:
            if rel not in local_actions:
                local_actions.append(rel)
                queue.append(rel)
check("every local `./` action a workflow uses exists", not missing_local, missing_local)
for name in names + sorted(local_actions):
    composite = name in local_actions
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
    if not composite:  # a composite action has no token of its own
        check(f"{name}: least-privilege top-level permissions", permissions_problem(doc) is None,
              permissions_problem(doc))
        check(f"{name}: every job's own permissions are scoped", not job_permissions_problems(doc),
              job_permissions_problems(doc))
    check(f"{name}: no ${{{{ }}}} interpolated into a run script", not interpolating_in(doc),
          interpolating_in(doc))
    check(f"{name}: no attacker-controlled event value in an action input",
          not untrusted_inputs_in(doc), untrusted_inputs_in(doc))

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
check("an expression in a github-script script is caught",
      bool(interpolating_in({"jobs": {"j": {"steps": [{"uses": f"actions/github-script@{SHA}",
                                                       "with": {"script": "core.info('${{ github.event.issue.title }}')"}}]}}})))
check("an expression in a composite action's step is caught",
      bool(interpolating_in({"runs": {"using": "composite",
                                      "steps": [{"run": "echo ${{ inputs.x }}", "shell": "bash"}]}})))
for label, perms, ok in (("`{}`", {}, True), ("`read-all`", "read-all", True),
                         ("read scopes", {"contents": "read", "pull-requests": "read"}, True),
                         ("`write-all`", "write-all", False), ("an empty value", None, False),
                         ("a top-level write scope", {"contents": "write"}, False)):
    check(f"top-level permissions {label} {'pass' if ok else 'fail'}",
          (permissions_problem({"permissions": perms}) is None) is ok, perms)
for label, perms, ok in (("named write scopes", {"contents": "write", "issues": "write"}, True),
                         ("`read-all`", "read-all", True), ("`write-all`", "write-all", False),
                         ("an empty value", None, False), ("an unknown level", {"contents": "admin"}, False)):
    check(f"job-level permissions {label} {'pass' if ok else 'fail'}",
          (not job_permissions_problems({"jobs": {"j": {"permissions": perms}}})) is ok, perms)
check("a job without its own permissions inherits the top level and passes",
      not job_permissions_problems({"jobs": {"j": {"steps": []}}}))
check("an owner's case doesn't matter", not disallowed_in({"steps": [{"uses": f"Actions/checkout@{SHA}"}]}))
check("an unapproved docker:// image is disallowed",
      bool(disallowed_in({"steps": [{"uses": "docker://alpine@sha256:" + "a" * 64}]})))
for label, value, ok in (("a PR number", "${{ github.event.pull_request.number }}", True),
                        ("the repository", "${{ github.repository }}", True),
                        ("a step output", "${{ steps.meta.outputs.tag }}", True),
                        ("a secret", "${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}", True),
                        ("runner.os", "${{ runner.os }}", True),
                        ("a format() of safe values", "${{ format('{0}-{1}', github.repository, runner.os) }}", True),
                        ("a comment body", "review ${{ github.event.comment.body }}", False),
                        ("an issue title", "${{ github.event.issue.title }}", False),
                        ("a PR head ref", "${{ github.event.pull_request.head.ref }}", False),
                        ("github.head_ref", "${{ github.head_ref }}", False),
                        ("a commit message", "${{ github.event.head_commit.message }}", False),
                        ("an indexed commit message", "${{ github.event.commits[0].message }}", False),
                        ("a wildcard commit author", "${{ github.event.commits[*].author.email }}", False),
                        ("an indexed page name", "${{ github.event.pages[0].page_name }}", False),
                        ("head_ref inside format()", "${{ format('{0}', github.head_ref) }}", False),
                        ("bracket access", "${{ github['head_ref'] }}", False),
                        ("github.ref_name", "${{ github.ref_name }}", False),
                        ("an unlisted event field", "${{ github.event.pull_request.head.repo.default_branch }}", False),
                        ("a literal NaN", "${{ NaN }}", True),
                        ("}} inside a string literal", "${{ format('}}{0}', github.head_ref) }}", False)):
    found = untrusted_inputs_in({"jobs": {"j": {"steps": [{"uses": f"actions/x@{SHA}",
                                                           "with": {"prompt": value}}]}}})
    check(f"an action input with {label} is {'allowed' if ok else 'refused'}", (not found) is ok, value)
check("an untrusted value laundered through env into an action input is caught",
      bool(untrusted_inputs_in({"env": {"T": "${{ github.event.issue.title }}"},
                                "jobs": {"j": {"steps": [{"uses": f"actions/x@{SHA}",
                                                          "with": {"prompt": "${{ env.T }}"}}]}}})))
check("a safe value through env into an action input is allowed",
      not untrusted_inputs_in({"jobs": {"j": {"env": {"R": "${{ github.repository }}"},
                                              "steps": [{"uses": f"actions/x@{SHA}",
                                                         "with": {"repo": "${{ env.R }}"}}]}}}))
check("a reusable-workflow job's with: is checked",
      bool(untrusted_inputs_in({"jobs": {"j": {"uses": "./.github/workflows/x.yml",
                                               "with": {"t": "${{ github.event.issue.title }}"}}}})))
def flagged(doc):
    return bool(untrusted_inputs_in(doc))


def job(**fields):
    return {"jobs": {"j": fields}}


def step(**fields):
    return [dict({"uses": f"actions/x@{SHA}"}, **fields)]


TITLE = "${{ github.event.issue.title }}"
check("a step env re-reading a job env of the same name is resolved through the job's",
      flagged(job(env={"X": TITLE}, steps=step(env={"X": "${{ env.X }}"}, **{"with": {"p": "${{ env.X }}"}}))))
check("env indexed with ['X'] fails closed",
      flagged(job(env={"T": TITLE}, steps=step(**{"with": {"p": "${{ env['T'] }}"}}))))
check("a context reference inside [...] fails closed",
      flagged(job(steps=step(**{"with": {"p": "${{ secrets[github.head_ref] }}"}}))))
check("a literal index is allowed",
      not flagged(job(steps=step(**{"with": {"p": "${{ steps.a.outputs['x'] }}"}}))))
check("an env: written as an expression fails closed",
      flagged(job(env="${{ fromJSON(github.event.issue.body) }}",
                  steps=step(**{"with": {"p": "${{ env.T }}"}}))))
check("an untrusted matrix value is caught",
      flagged(job(strategy={"matrix": {"t": [TITLE]}}, steps=step(**{"with": {"p": "${{ matrix.t }}"}}))))
check("an untrusted job output is caught",
      flagged(job(outputs={"t": TITLE}, steps=[])))
check("a job output from a step output is allowed",
      not flagged(job(outputs={"t": "${{ steps.a.outputs.t }}"}, steps=[])))
check("the same value through env is not",
      not interpolating_in({"jobs": {"j": {"steps": [{"env": {"T": "${{ github.event.issue.title }}"},
                                                      "run": 'echo "$T"'}]}}}))

print(f"\n{_passed}/{_total} checks passed")
sys.exit(0 if _passed == _total else 1)
