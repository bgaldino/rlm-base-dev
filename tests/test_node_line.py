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

`.envrc` must find nvm where update-toolchain.sh does (Homebrew's, then nvm's own installer's
in `$NVM_DIR` or `$XDG_CONFIG_HOME/nvm`), or a workstation with the installer's nvm never gets
the pin, and the guide's `.envrc` template must carry the same code. The block also runs here
against fake nvm installs, to show which one it picks and what it says when there is none.

Each rule is a function over text, with a positive control beside the real-file check, so a
parser that matches nothing can't pass by finding nothing to compare.
Stdlib only. Run with: python tests/test_node_line.py
"""
import json
import logging
import os
import re
import shutil
import stat
import subprocess
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


NVM_SH_TEST = re.compile(r'\[ -s "([^"]*/nvm\.sh)" \]')


def nvm_sh_candidates(text):
    """The nvm.sh paths a script tests with `[ -s … ]`, in order; a leading `_` on a variable
    name is dropped, so .envrc's `$_NVM_PREFIX` compares equal to the update script's `$NVM_PREFIX`."""
    return [p.replace("$_", "$") for p in NVM_SH_TEST.findall(text)]


def section(text, start, end):
    """The lines from the one containing `start` up to (not including) the one containing `end`."""
    lines = text.splitlines()
    first = next((i for i, line in enumerate(lines) if start in line), None)
    if first is None:
        raise ValueError(f"no line contains the start marker {start!r}")
    last = next((i for i, line in enumerate(lines[first:], first) if end in line), None)
    if last is None:
        raise ValueError(f"no line after {start!r} contains the end marker {end!r}")
    return "\n".join(lines[first:last]) + "\n"


def code_lines(text):
    """Non-blank, non-comment lines, stripped: the code two copies of a block must share."""
    return [line.strip() for line in text.splitlines()
            if line.strip() and not line.lstrip().startswith("#")]


def envrc_node_block():
    return section(read(".envrc"), "# ── Node via nvm", "# ── Per-workstation")


def guide_node_block():
    return section(read("docs/guides/dev-environment-setup.md"), "# Node via nvm", "# Per-workstation")


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

    def test_nvm_sh_candidates(self):
        script = ('NVM_PREFIX="$(brew --prefix nvm)"\n'
                  'if [ -n "$_NVM_PREFIX" ] && [ -s "$_NVM_PREFIX/nvm.sh" ]; then x\n'
                  'elif [ -s "$NVM_DIR/nvm.sh" ]; then y\n'
                  'elif [ -n "${XDG_CONFIG_HOME:-}" ] && [ -s "$XDG_CONFIG_HOME/nvm/nvm.sh" ]; then z\n'
                  '[ -s "$NVM_PREFIX/etc/bash_completion.d/nvm" ]\n')
        self.assertEqual(nvm_sh_candidates(script), [
            "$NVM_PREFIX/nvm.sh", "$NVM_DIR/nvm.sh", "$XDG_CONFIG_HOME/nvm/nvm.sh"])
        self.assertEqual(nvm_sh_candidates('[ -s "$(brew --prefix nvm)/etc/x" ]\n'), [])

    def test_section_and_code_lines(self):
        text = "a\n# ── Node\n  # note\n\n  x=1\n# ── Next\nb\n"
        block = section(text, "# ── Node", "# ── Next")
        self.assertEqual(block, "# ── Node\n  # note\n\n  x=1\n")
        self.assertEqual(code_lines(block), ["x=1"])
        with self.assertRaisesRegex(ValueError, "start marker"):
            section(text, "# ── Gone", "# ── Next")
        with self.assertRaisesRegex(ValueError, "end marker"):
            section(text, "# ── Node", "# ── Gone")

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
        for name, text in ((".envrc", read(".envrc")), ("the guide's .envrc", guide_node_block())):
            with self.subTest(file=name):
                self.assertNotRegex(text, r"nvm use[^\n]*\bdefault\b",
                                    f"{name} must not fall back to nvm's default alias")

    def test_envrc_finds_nvm_like_the_update_script(self):
        # Homebrew's nvm alone would leave a workstation with nvm's own installer outside the pin.
        envrc = nvm_sh_candidates(envrc_node_block())
        self.assertEqual(envrc, nvm_sh_candidates(read("scripts/bash/update-toolchain.sh")),
                         ".envrc must test for nvm.sh where update-toolchain.sh does, in its order")
        self.assertIn("$NVM_PREFIX/nvm.sh", envrc, ".envrc must look for Homebrew's nvm")
        self.assertIn("$NVM_DIR/nvm.sh", envrc, ".envrc must look for nvm's own installer's nvm")

    def test_guide_template_mirrors_envrc(self):
        self.assertEqual(code_lines(guide_node_block()), code_lines(envrc_node_block()),
                         "dev-environment-setup.md's .envrc template must carry .envrc's Node code")

    def test_nothing_floats_on_lts(self):
        for rel in (".envrc", "scripts/bash/update-toolchain.sh"):
            with self.subTest(file=rel):
                self.assertEqual(floats_on_lts(read(rel)), [],
                                 f"{rel} must take the Node line from .nvmrc, not lts/*")

    def test_update_script_reads_nvmrc(self):
        self.assertRegex(read("scripts/bash/update-toolchain.sh"), r'NODE_LINE="\$\(.*\.nvmrc',
                         "update-toolchain.sh must read NODE_LINE from .nvmrc")


FAKE_NVM_SH = """\
echo "sourced ${BASH_SOURCE[0]} ${1:-}" >> "$NVM_LOG"
nvm() { echo "nvm $*" >> "$NVM_LOG"; [ -n "${FAKE_NODE_INSTALLED:-}" ]; }
"""


@unittest.skipUnless(shutil.which("bash"), "needs bash, which direnv runs .envrc under")
class EnvrcNodeBlock(unittest.TestCase):
    """.envrc's Node block run under bash against fake nvm installs: which nvm.sh it sources
    (each fake logs its own path), the NVM_DIR it leaves, what it tells nvm, and what it prints."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.log = self.root / "nvm.log"
        (self.root / "repo").mkdir()
        (self.root / "repo" / ".nvmrc").write_text("24\n")
        (self.root / "bin").mkdir()

    def fake_nvm(self, rel):
        path = self.root / rel
        path.mkdir(parents=True, exist_ok=True)
        (path / "nvm.sh").write_text(FAKE_NVM_SH)
        return str(path)

    def fake_brew(self, prefix):
        brew = self.root / "bin" / "brew"
        brew.write_text(f"#!/bin/sh\n[ \"$*\" = '--prefix nvm' ] && echo '{prefix}'\n")
        brew.chmod(brew.stat().st_mode | stat.S_IXUSR)

    def run_block(self, installed=True, **env):
        script = self.root / "block.sh"
        script.write_text(envrc_node_block() + 'echo "NVM_DIR=$NVM_DIR"\n')
        full_env = {"PATH": f"{self.root / 'bin'}:/usr/bin:/bin", "HOME": str(self.root / "home"),
                    "NVM_LOG": str(self.log), **env}
        if installed:
            full_env["FAKE_NODE_INSTALLED"] = "1"
        result = subprocess.run(["bash", str(script)], cwd=self.root / "repo", env=full_env,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        log = self.log.read_text().splitlines() if self.log.exists() else []
        return result.stdout.strip(), result.stderr, log

    def test_installer_nvm_in_nvm_dir(self):
        nvm_dir = self.fake_nvm("custom-nvm")
        out, err, log = self.run_block(NVM_DIR=nvm_dir)
        self.assertEqual(log, [f"sourced {nvm_dir}/nvm.sh --no-use", "nvm use --silent"])
        self.assertEqual(out, f"NVM_DIR={nvm_dir}")
        self.assertEqual(err, "")

    def test_installer_nvm_in_default_dir(self):
        nvm_dir = self.fake_nvm("home/.nvm")
        out, err, log = self.run_block()
        self.assertEqual(log, [f"sourced {nvm_dir}/nvm.sh --no-use", "nvm use --silent"])
        self.assertEqual(out, f"NVM_DIR={nvm_dir}")

    def test_installer_nvm_under_xdg_config_home(self):
        nvm_dir = self.fake_nvm("config/nvm")
        out, err, log = self.run_block(XDG_CONFIG_HOME=str(self.root / "config"))
        self.assertEqual(log, [f"sourced {nvm_dir}/nvm.sh --no-use", "nvm use --silent"])
        self.assertEqual(out, f"NVM_DIR={nvm_dir}")

    def test_order_is_brew_then_nvm_dir_then_xdg(self):
        nvm_dir = self.fake_nvm("home/.nvm")
        self.fake_nvm("config/nvm")
        _, _, log = self.run_block(XDG_CONFIG_HOME=str(self.root / "config"))
        self.assertEqual(log[:1], [f"sourced {nvm_dir}/nvm.sh --no-use"])
        self.log.unlink()
        brew_nvm = self.fake_nvm("brew/opt/nvm")
        self.fake_brew(brew_nvm)
        out, _, log = self.run_block(XDG_CONFIG_HOME=str(self.root / "config"))
        # Homebrew's nvm.sh wins, but nvm still keeps its versions in $NVM_DIR.
        self.assertEqual(log, [f"sourced {brew_nvm}/nvm.sh --no-use", "nvm use --silent"])
        self.assertEqual(out, f"NVM_DIR={nvm_dir}")

    def test_uninstalled_line_warns_without_falling_back(self):
        self.fake_nvm("home/.nvm")
        _, err, log = self.run_block(installed=False)
        self.assertEqual(log[1:], ["nvm use --silent"])
        self.assertIn("Node 24 (from .nvmrc) isn't installed", err)

    def test_no_nvm_names_the_guide(self):
        out, err, log = self.run_block()
        self.assertEqual(log, [])
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertIn("nvm not found", err)
        self.assertIn("docs/guides/local-installation.md, Step 3", err)


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
