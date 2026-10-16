"""Offline check: every place that names the Node major line agrees with `.nvmrc`.

`.nvmrc` is the single source for the Node major line. `.envrc` (a bare `nvm use`) and
`scripts/bash/update-toolchain.sh` read it; the Dockerfile's `NODE_MAJOR`, every
`actions/setup-node` step and `package.json`'s `engines.node` floor restate it, because
neither Docker nor Actions reads `.nvmrc` unless told to. Bumping the line is a deliberate
change to all of them at once (docs/guides/dev-environment-setup.md, "Bumping a major
line"), and this suite fails the gate until they agree. It also refuses a float back to
`lts/*`, which would jump a major the day the next one becomes LTS, with no test step.

Each rule is a function over text, with a positive control beside the real-file check, so a
parser that matches nothing can't pass by finding nothing to compare.
Stdlib only. Run with: python tests/test_node_line.py
"""
import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def nvmrc_major(text):
    """The bare major in `.nvmrc`, or None when it holds anything else (`lts/*`, `24.1`, …)."""
    value = text.strip()
    return int(value) if re.fullmatch(r"\d+", value) else None


def dockerfile_major(text):
    """`ARG NODE_MAJOR=<n>`, or None when the Dockerfile doesn't declare it."""
    m = re.search(r"^ARG NODE_MAJOR=(\d+)\s*$", text, re.M)
    return int(m.group(1)) if m else None


def setup_node_lines(text):
    """(line number, 'version' | 'file', value) for each actions/setup-node step's Node input.

    Reads the lines after each `uses: actions/setup-node@` up to the next step (`- `). A step
    with neither input is reported as ('version', '') so it can't slip through unchecked.
    """
    lines = text.splitlines()
    found = []
    for i, line in enumerate(lines):
        if not re.search(r"uses:\s*actions/setup-node@", line):
            continue
        entry = (i + 1, "version", "")
        for later in lines[i + 1:]:
            if re.match(r"\s*- ", later):
                break
            m = re.match(r"\s*node-version(-file)?:\s*[\"']?([^\"'#\s]+)", later)
            if m:
                entry = (i + 1, "file" if m.group(1) else "version", m.group(2))
                break
        found.append(entry)
    return found


def engines_floor_major(package_json_text):
    """The major in `engines.node`'s `>=` floor, or None without one."""
    spec = (json.loads(package_json_text).get("engines") or {}).get("node", "")
    m = re.search(r">=\s*v?(\d+)", spec)
    return int(m.group(1)) if m else None


def floats_on_lts(text):
    """Non-comment lines naming an `lts/` alias (`lts/*`, `lts/krypton`, `--lts`)."""
    return [line.strip() for line in text.splitlines()
            if not line.lstrip().startswith("#") and re.search(r"lts/|--lts\b", line)]


def read(rel):
    return (REPO / rel).read_text(encoding="utf-8")


class Parsers(unittest.TestCase):
    """Positive controls: each rule sees what it is meant to, and refuses what it must."""

    def test_nvmrc(self):
        self.assertEqual(nvmrc_major("24\n"), 24)
        for bad in ("lts/*", "24.1", "v24", "", "node"):
            with self.subTest(bad=bad):
                self.assertIsNone(nvmrc_major(bad))

    def test_dockerfile(self):
        self.assertEqual(dockerfile_major("FROM x\n# note\nARG NODE_MAJOR=26\nRUN y\n"), 26)
        self.assertIsNone(dockerfile_major("FROM x\nARG NODE_VERSION=24\n"))

    def test_setup_node(self):
        wf = ("steps:\n"
              "  - uses: actions/setup-node@abc  # v5\n"
              "    with:\n"
              "      # pinned\n"
              "      node-version: \"24.16.0\"\n"
              "  - uses: actions/setup-node@abc\n"
              "    with:\n"
              "      node-version-file: .nvmrc\n"
              "  - uses: actions/setup-node@abc\n"
              "  - run: echo node-version: 99\n")
        self.assertEqual(setup_node_lines(wf), [
            (2, "version", "24.16.0"), (6, "file", ".nvmrc"), (9, "version", "")])

    def test_engines(self):
        self.assertEqual(engines_floor_major('{"engines": {"node": ">=24"}}'), 24)
        self.assertEqual(engines_floor_major('{"engines": {"node": ">= 24.0.0"}}'), 24)
        self.assertIsNone(engines_floor_major('{"engines": {"node": "^24"}}'))
        self.assertIsNone(engines_floor_major("{}"))

    def test_lts_float(self):
        self.assertEqual(floats_on_lts("# don't use lts/* here\nnvm use\n"), [])
        self.assertEqual(floats_on_lts("  nvm use --silent lts/\\* >/dev/null\n"),
                         ["nvm use --silent lts/\\* >/dev/null"])
        self.assertEqual(floats_on_lts('NODE_LINE="lts/*"\n'), ['NODE_LINE="lts/*"'])
        self.assertEqual(floats_on_lts("nvm install --lts\n"), ["nvm install --lts"])


class NodeLine(unittest.TestCase):
    """The real files agree with `.nvmrc`."""

    @classmethod
    def setUpClass(cls):
        cls.major = nvmrc_major(read(".nvmrc"))

    def test_nvmrc_is_a_bare_major(self):
        self.assertIsNotNone(self.major, ".nvmrc must hold a bare Node major such as 24")

    def test_dockerfile_matches(self):
        self.assertEqual(dockerfile_major(read("docker/Dockerfile")), self.major,
                         "docker/Dockerfile's ARG NODE_MAJOR must equal .nvmrc")

    def test_every_setup_node_step_matches(self):
        workflows = sorted((REPO / ".github" / "workflows").glob("*.y*ml"))
        steps = [(wf, step) for wf in workflows
                 for step in setup_node_lines(wf.read_text(encoding="utf-8"))]
        self.assertTrue(steps, "no actions/setup-node step found; this rule would check nothing")
        for wf, (line, kind, value) in steps:
            with self.subTest(workflow=wf.name, line=line):
                if kind == "file":
                    self.assertEqual(value, ".nvmrc", "node-version-file must be .nvmrc")
                else:
                    self.assertRegex(value, r"^\d+", "node-version must name a version")
                    self.assertEqual(int(value.split(".")[0]), self.major,
                                     f"node-version {value} isn't on the .nvmrc line")

    def test_engines_floor_matches(self):
        self.assertEqual(engines_floor_major(read("package.json")), self.major,
                         "package.json engines.node must be >=<.nvmrc major>")

    def test_nothing_floats_on_lts(self):
        for rel in (".envrc", "scripts/bash/update-toolchain.sh"):
            with self.subTest(file=rel):
                self.assertEqual(floats_on_lts(read(rel)), [],
                                 f"{rel} must take the Node line from .nvmrc, not lts/*")

    def test_update_script_reads_nvmrc(self):
        self.assertRegex(read("scripts/bash/update-toolchain.sh"), r'NODE_LINE="\$\(.*\.nvmrc',
                         "update-toolchain.sh must read NODE_LINE from .nvmrc")


if __name__ == "__main__":
    unittest.main()
