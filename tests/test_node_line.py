"""Offline check: every place that names the Node major line agrees with `.nvmrc`.

`.nvmrc` is the single source for the Node major line. `.envrc` (a bare `nvm use`) and
`scripts/bash/update-toolchain.sh` read it; the Dockerfile's `NODE_MAJOR`, every
`actions/setup-node` step and `package.json`'s `engines.node` floor restate it, because
neither Docker nor Actions reads `.nvmrc` unless told to. Bumping the line is a deliberate
change to all of them at once (docs/guides/dev-environment-setup.md, "Bumping a major
line"), and this suite fails the gate until they agree. It also refuses a float back to
`lts/*`, which would jump a major the day the next one becomes LTS, with no test step. And it
covers the lines that tell a person which Node to install (the setup guides, the skills, the
`validate_setup` hint), so a bump can't leave the guides installing the old line.

Each rule is a function over text, with a positive control beside the real-file check, so a
parser that matches nothing can't pass by finding nothing to compare.
Stdlib only. Run with: python tests/test_node_line.py
"""
import json
import logging
import os
import re
import stat
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tasks.rlm_validate_setup import FAIL, PASS, WARN, ValidateSetup  # noqa: E402


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
            m = re.match(r"\s*node-version(-file)?:\s*[\"']?([^\"'#]+?)[\"']?\s*(?:#.*)?$", later)
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


# The phrasings the guides, skills and validate_setup hint use to name the line. Each instruction
# file must match at least one, so a reworded line drops out loudly instead of silently.
INSTRUCTION_FILES = (
    "docs/guides/local-installation.md",
    "docs/guides/dev-environment-setup.md",
    ".cursor/skills/troubleshooting/SKILL.md",
    ".cursor/skills/toolchain/SKILL.md",
    ".cursor/skills/toolchain/workstation-audit.md",
    ".cursor/skills/toolchain/verification-handoff.md",
    "tasks/rlm_validate_setup.py",
)
# Where a stale floor ("Node LTS >=22", "release **22 or later**", "an LTS ≥ 22") could survive a
# bump: every instruction file above plus the docs that describe the toolchain without an install
# line. Phrasings vary, so this rule isn't phrase-bound: any major written near "Node", "LTS",
# "engines" or an nvm command that is *lower* than .nvmrc's fails. A higher one is allowed, for
# forward-looking text such as "when Node 26 becomes LTS".
STALE_SCAN_FILES = INSTRUCTION_FILES + (
    ".cursor/skills/toolchain/managed-workstations.md",
    "README.md",
    "CONTRIBUTING.md",
    "docker/README.md",
)
NODE_MAJOR_NEAR = re.compile(
    r"(?:Node(?:\.js)?|LTS|engines(?:\.node)?|nvm (?:install|alias default|use))"
    r"[^|`\n]{0,40}?(?<![\d.])(\d{2})(?![\d])")
INSTRUCTION_PATTERNS = (
    r"nvm (?:install|alias default) (\d+)\b",
    r"\.nvmrc`? \(`?(\d+)`?",
    r"Node(?:\.js)? (\d+), the line pinned",
    r"Node (\d+) \(the line pinned in",
    r"Node's \((\d+)\) is `\.nvmrc`",
    r"Use \*\*Node (\d+)\*\*",
    r"\bv(\d+)\.x \((?:nvm; )?the line",
    r"Should show v(\d+)\.x",
)


def instructed_majors(text):
    """Every Node major an instruction names, in the phrasings above."""
    return [int(m) for pat in INSTRUCTION_PATTERNS for m in re.findall(pat, text)]


def lower_majors(text, major):
    """Majors below `major` written near a Node word: a stale floor left behind by a bump."""
    return [int(n) for n in NODE_MAJOR_NEAR.findall(text) if int(n) < major]


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
              "  - run: echo node-version: 99\n"
              "  - uses: actions/setup-node@abc\n"
              "    with:\n"
              "      node-version: ${{ matrix.node }}  # from the matrix\n")
        self.assertEqual(setup_node_lines(wf), [
            (2, "version", "24.16.0"), (6, "file", ".nvmrc"), (9, "version", ""),
            (11, "version", "${{ matrix.node }}")])

    def test_engines(self):
        self.assertEqual(engines_floor_major('{"engines": {"node": ">=24"}}'), 24)
        self.assertEqual(engines_floor_major('{"engines": {"node": ">= 24.0.0"}}'), 24)
        self.assertIsNone(engines_floor_major('{"engines": {"node": "^24"}}'))
        self.assertIsNone(engines_floor_major("{}"))

    def test_instructions(self):
        text = ("nvm install 26\nnvm alias default 26\n| `.nvmrc` (`26`) |\n"
                "Node.js 26, the line pinned\nNode's (26) is `.nvmrc`\nUse **Node 26**\n"
                "→ v26.x (the line pinned\n# Should show v26.x\n")
        self.assertEqual(instructed_majors(text), [26] * 8)
        self.assertEqual(instructed_majors("Node 24 → 26 is a deliberate change\n"), [])

    def test_lower_majors(self):
        for text in ("# Check CLI >=2 and Node LTS >=22\n", "use an LTS Node.js release **22 or later**\n",
                     "| Node from nvm | `node -v` | an LTS ≥ 22 |\n", "v<LTS ≥ 22>.x (nvm)\n",
                     "engines.node: >=22\n", "nvm install 22\n"):
            with self.subTest(text=text):
                self.assertEqual(lower_majors(text, 24), [22])
        for text in ("Node 24 → 26 is deliberate\n", "when Node 26 becomes LTS\n",
                     "Node, but only from an older 3.13 patch\n", "Node 24.16.0 is pinned\n"):
            with self.subTest(text=text):
                self.assertEqual(lower_majors(text, 24), [])

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
                elif value.startswith("${{"):
                    self.fail(f"node-version {value} is an expression this check can't resolve: "
                              "use node-version-file: .nvmrc, or a literal version on its line")
                else:
                    self.assertRegex(value, r"^\d+", "node-version must name a version")
                    self.assertEqual(int(value.split(".")[0]), self.major,
                                     f"node-version {value} isn't on the .nvmrc line")

    def test_engines_floor_matches(self):
        self.assertEqual(engines_floor_major(read("package.json")), self.major,
                         "package.json engines.node must be >=<.nvmrc major>")

    def test_instructions_match(self):
        for rel in INSTRUCTION_FILES:
            with self.subTest(file=rel):
                majors = instructed_majors(read(rel))
                self.assertTrue(majors, f"{rel} no longer names the Node line in a known phrasing")
                self.assertEqual(set(majors), {self.major},
                                 f"{rel} tells people to install a Node line other than .nvmrc's")

    def test_no_stale_lower_major(self):
        for rel in STALE_SCAN_FILES:
            with self.subTest(file=rel):
                self.assertEqual(lower_majors(read(rel), self.major), [],
                                 f"{rel} still names a Node line below .nvmrc's")

    def test_envrc_has_no_default_fallback(self):
        # Falling back to nvm's `default` would silently select an older line when .nvmrc's
        # isn't installed; .envrc warns instead (and validate_setup fails a lower major).
        self.assertNotRegex(read(".envrc"), r"nvm use[^\n]*\bdefault\b",
                            ".envrc must not fall back to nvm's default alias")

    def test_nothing_floats_on_lts(self):
        for rel in (".envrc", "scripts/bash/update-toolchain.sh"):
            with self.subTest(file=rel):
                self.assertEqual(floats_on_lts(read(rel)), [],
                                 f"{rel} must take the Node line from .nvmrc, not lts/*")

    def test_update_script_reads_nvmrc(self):
        self.assertRegex(read("scripts/bash/update-toolchain.sh"), r'NODE_LINE="\$\(.*\.nvmrc',
                         "update-toolchain.sh must read NODE_LINE from .nvmrc")


class ValidateSetupNode(unittest.TestCase):
    """validate_setup's Node check enforces the .nvmrc line: lower FAILs, higher WARNs."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.saved_path = os.environ.get("PATH", "")
        self.addCleanup(os.environ.__setitem__, "PATH", self.saved_path)
        self.task = object.__new__(ValidateSetup)
        self.task.logger = logging.getLogger("validate_setup_node_test")
        self.task._pinned_node_major = lambda: 24

    def run_with_node(self, version_line):
        node = Path(self.tmp.name) / "node"
        node.write_text(f"#!/bin/sh\necho '{version_line}'\n")
        node.chmod(node.stat().st_mode | stat.S_IXUSR)
        os.environ["PATH"] = f"{self.tmp.name}{os.pathsep}/usr/bin:/bin"
        return self.task._check_node()

    def test_pinned_major_passes(self):
        self.assertEqual(self.run_with_node("v24.22.0")["status"], PASS)

    def test_lower_major_fails_with_the_fix(self):
        result = self.run_with_node("v22.20.0")
        self.assertEqual(result["status"], FAIL)
        self.assertIn("nvm install 24", result["detail"])

    def test_higher_major_warns(self):
        self.assertEqual(self.run_with_node("v26.12.0")["status"], WARN)

    def test_unreadable_version_or_no_pin_passes(self):
        self.assertEqual(self.run_with_node("weird")["status"], PASS)
        self.task._pinned_node_major = lambda: None
        self.assertEqual(self.run_with_node("v18.0.0")["status"], PASS)

    def test_missing_node_warns(self):
        os.environ["PATH"] = self.tmp.name
        self.assertEqual(self.task._check_node()["status"], WARN)

    def test_pinned_major_reads_the_real_nvmrc(self):
        self.assertEqual(object.__new__(ValidateSetup)._pinned_node_major(), nvmrc_major(read(".nvmrc")))


if __name__ == "__main__":
    unittest.main()
