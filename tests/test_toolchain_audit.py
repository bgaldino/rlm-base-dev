"""Offline checks for scripts/ai/toolchain_audit.py and the audit doc it serves.

The audit's commands used to sit in markdown table cells beside Expect and Fix cells that
named `pyenv uninstall` and `pipx inject`. An agent took the wrong column and ran what it
held. These tests keep the shape that makes that impossible: every command lives in the
script, every table row names a check the script has, no table cell holds a runnable
command, and nothing the script runs changes the machine.
Stdlib only. Run with: python tests/test_toolchain_audit.py
"""
import contextlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts" / "ai"))
import toolchain_audit as ta  # noqa: E402

DOC = REPO / ".cursor" / "skills" / "toolchain" / "workstation-audit.md"

# Commands that change the machine. The script must run none of them, and no table cell
# in the doc may hold one as a code span (an agent could lift it out and run it).
MUTATING = re.compile(
    r"(?:^|[\s;&|(`])(?:"
    r"pyenv (?:install|uninstall|local|rehash)|pyenv global [^\s;|)]"
    r"|pipx (?:inject|reinstall|install|uninstall|upgrade|upgrade-shared|runpip|ensurepath)"
    r"|brew (?:upgrade|install|uninstall|reinstall|link|unlink|tab|tap|cleanup|update)"
    r"|pip3? install|-m pip install"
    r"|npm (?:install|i|update|uninstall|ci)\b|sf (?:update|plugins (?:install|update|uninstall))"
    r"|direnv (?:allow|deny|reload)|nvm (?:install|uninstall|alias|reinstall-packages)"
    r"|git (?:switch|checkout|stash|reset|clean|commit|push|config [^-\s]|config --(?:add|unset|global [^-]))"
    r"|rm |mv |update-toolchain\.sh"
    r"|cci (?:task|flow) run (?!validate_setup -o auto_fix false -o auto_fix_robot false)"
    r")"
)
CODE_SPAN = re.compile(r"`([^`]+)`")
# A code span that reads as a command line rather than a value or a name.
MULTI_STEP = re.compile(r"\$\(|;\s|\s\|\s|\\\||&&|\|\|")


def doc_tables():
    """(section, header, cells) for every table body row in the doc's numbered sections."""
    section = header = None
    rows = []
    for line in DOC.read_text().splitlines():
        m = re.match(r"^## (\d)\. ", line)
        if m:
            section = int(m.group(1))
        elif line.startswith("## "):
            section = None
        if not line.startswith("|"):
            header = None
            continue
        if not section or re.match(r"^\|[-|\s]+\|$", line):
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line)[1:-1]]
        if header is None:
            header = cells[0]
            continue
        rows.append((section, header, cells))
    return rows


class DocShape(unittest.TestCase):
    def test_every_check_has_one_row_in_its_section(self):
        ids = {}
        for section, header, cells in doc_tables():
            m = header == "Check" and re.match(r"^`([a-z0-9-]+)`", cells[0])
            if m:
                ids.setdefault(m.group(1), []).append(section)
        for check in ta.CHECKS:
            self.assertEqual(ids.get(check.id), [check.section],
                             f"{check.id}: needs one row in audit §{check.section}")
        self.assertEqual(set(ids) - {c.id for c in ta.CHECKS}, set(),
                         "rows naming checks the script doesn't have")

    def test_no_table_cell_holds_a_command(self):
        for section, _, cells in doc_tables():
            for cell in cells:
                for span in CODE_SPAN.findall(cell):
                    self.assertIsNone(MUTATING.search(span), f"§{section}: `{span}`")
                    self.assertIsNone(MULTI_STEP.search(span), f"§{section}: `{span}`")

    def test_no_mutating_command_anywhere_in_a_cell(self):
        # Plain prose in a cell can't be lifted as a command; a code span or a bare
        # command name next to arguments can. This catches both.
        for section, _, cells in doc_tables():
            for cell in cells[1:]:
                self.assertIsNone(MUTATING.search(cell.replace("`", " ")),
                                  f"§{section}: {cell[:80]}")

    def test_fenced_blocks_only_run_the_script(self):
        text = DOC.read_text()
        for block in re.findall(r"```[a-z]*\n(.*?)```", text, re.S):
            for line in block.strip().splitlines():
                self.assertTrue(line.startswith("python3 scripts/ai/toolchain_audit.py"),
                                f"fenced line outside the script: {line}")


class ScriptChecks(unittest.TestCase):
    def test_ids_unique_and_sections_known(self):
        ids = [c.id for c in ta.CHECKS]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual({c.section for c in ta.CHECKS}, set(ta.SECTIONS))

    def test_commands_are_read_only(self):
        for check in ta.CHECKS:
            cmd = ta.command(check)
            self.assertTrue(cmd, check.id)
            self.assertIsNone(MUTATING.search(cmd), f"{check.id}: {cmd[:80]}")

    def test_mutating_pattern_catches_the_incident(self):
        # The Expect cell that was run named these, with and without arguments.
        for text in ("pyenv uninstall", "pipx inject --force cumulusci -r x",
                     "brew upgrade", "rm -rf x", "pyenv global 3.13.1",
                     "cci task run validate_setup", "cci flow run prepare_rlm_org",
                     "direnv allow"):
            self.assertIsNotNone(MUTATING.search(text), text)
        for text in ("pyenv global; x", '"$(pyenv global)"', "pipx environment --value X",
                     "git config --get user.signingkey",
                     "cci task run validate_setup -o auto_fix false -o auto_fix_robot false"):
            self.assertIsNone(MUTATING.search(text), text)


def run_main(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        try:
            code = ta.main(list(argv))
        except SystemExit as exc:
            code = exc.code
    return code, out.getvalue()


class Selection(unittest.TestCase):
    def test_on_request_runs_only_when_named(self):
        args = type("A", (), {"all": True, "section": [], "check": []})
        self.assertNotIn("ca-direct-probe", [c.id for c in ta.select(args)])
        args.all, args.section = False, [6]
        self.assertNotIn("ca-direct-probe", [c.id for c in ta.select(args)])
        args.check = ["ca-direct-probe"]
        self.assertIn("ca-direct-probe", [c.id for c in ta.select(args)])

    def test_section_keeps_doc_order(self):
        args = type("A", (), {"all": False, "section": [2], "check": []})
        self.assertEqual([c.id for c in ta.select(args)],
                         [c.id for c in ta.CHECKS if c.section == 2])

    def test_list_and_show(self):
        code, out = run_main("--list")
        self.assertEqual(code, 0)
        for check in ta.CHECKS:
            self.assertIn(check.id, out)
        code, out = run_main("--show", "signing")
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), ta.command(next(c for c in ta.CHECKS if c.id == "signing")))

    def test_usage_errors(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(run_main()[0], 2)
            self.assertEqual(run_main("--show", "nope")[0], 2)
            # 1 means a check timed out or couldn't start, so a typo must not exit 1.
            self.assertEqual(run_main("--check", "nope")[0], 2)
            self.assertEqual(run_main("--check", "signing", "--shell", "no-such-shell-x")[0], 2)
            self.assertEqual(run_main("--check", "signing", "--timeout", "0")[0], 2)


GUIDE = REPO / "docs" / "guides" / "dev-environment-setup.md"


def zshenv_nvm_block():
    """The NVM block of the guide's ~/.zshenv template: from `# NVM —` to the pyenv block."""
    text = GUIDE.read_text()
    start = text.index("# NVM —")
    return text[start:text.index("# pyenv binary", start)]


@unittest.skipUnless(shutil.which("zsh") and shutil.which("direnv"), "needs zsh and direnv")
class NodeChecks(unittest.TestCase):
    """The §3 Node checks run against a scratch HOME: fake Node installs under its ~/.nvm, a
    fake nvm.sh, and a scratch repo whose .envrc is allowed in the scratch HOME's direnv."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = Path(tmp.name).resolve() / "home"
        self.repo = Path(tmp.name).resolve() / "repo"
        self.bin = Path(tmp.name).resolve() / "bin"
        for d in (self.repo, self.bin):
            d.mkdir(parents=True)
        for version in ("v24.0.0", "v26.0.0"):
            node = self.home / ".nvm" / "versions" / "node" / version / "bin" / "node"
            node.parent.mkdir(parents=True)
            node.write_text(f"#!/bin/sh\necho {version}\n")
            node.chmod(0o755)
        (self.repo / ".nvmrc").write_text("24\n")
        # .envrc's `nvm use` stands in as PATH_add of the pinned line's bin dir.
        (self.repo / ".envrc").write_text('PATH_add "$HOME/.nvm/versions/node/v24.0.0/bin"\n')
        self.env = {"HOME": str(self.home), "PATH": f"{self.bin}:/usr/bin:/bin"}
        os.symlink(shutil.which("direnv"), self.bin / "direnv")

    def fake_nvm(self, default):
        """nvm.sh in $NVM_DIR whose `default` alias names `default` and resolves to v26.0.0."""
        (self.home / ".nvm" / "nvm.sh").write_text(
            f'nvm_alias() {{ echo {default}; }}\n'
            'nvm() { [ "$1" = version ] && echo v26.0.0; }\n')

    def zshenv(self, nvm_block):
        (self.home / ".zshenv").write_text(
            f'export PATH="{self.bin}:/usr/bin:/bin:$PATH"\n{nvm_block}\n'
            'eval "$(direnv export zsh 2>/dev/null)"\n')
        subprocess.run(["direnv", "allow", str(self.repo)], env=self.env, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)

    def run_check(self, check_id):
        check = next(c for c in ta.CHECKS if c.id == check_id)
        return subprocess.run(["zsh", "-c", ta.command(check)], cwd=self.repo, env=self.env,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                              timeout=60).stdout

    def nested(self, out):
        lines = {line.split(":", 1)[0]: line for line in out.splitlines() if ": v" in line}
        repo = next(v for k, v in lines.items() if k.startswith("repo shell"))
        self.assertIn("(.envrc loaded)", repo)
        return repo.split(": ", 1)[1], lines["nested shell"].split(": ", 1)[1]

    def test_nested_shell_fails_on_a_newest_installed_prepend(self):
        # osaka's old line: the nested shell re-prepends the newest Node, and direnv, seeing
        # .envrc already loaded, doesn't put the pinned line back in front.
        self.zshenv('export PATH="$HOME/.nvm/versions/node/$(ls "$HOME/.nvm/versions/node" '
                    '| sort -V | tail -1)/bin:$PATH"')
        repo, nested = self.nested(self.run_check("node-nested-shell"))
        self.assertTrue(repo.startswith("v24.0.0 from ~/.nvm/versions/node/v24.0.0/bin/node;"), repo)
        self.assertTrue(nested.startswith("v26.0.0 from ~/.nvm/versions/node/v26.0.0/bin/node;"), nested)

    def test_nested_shell_passes_on_the_guide_template(self):
        # The template prepends `default` (here v26, the worst case) in a fresh shell, but not
        # in one that inherits a loaded .envrc, so the nested shell's Node dirs are unchanged.
        self.fake_nvm("node")
        self.fake_brew_nvm()
        self.zshenv(zshenv_nvm_block())
        repo, nested = self.nested(self.run_check("node-nested-shell"))
        self.assertTrue(repo.startswith("v24.0.0 from ~/.nvm/versions/node/v24.0.0/bin/node;"), repo)
        self.assertEqual(nested, repo)

    def fake_brew_nvm(self):
        brew = self.bin / "brew"
        brew.write_text(f"#!/bin/sh\n[ \"$*\" = '--prefix nvm' ] && echo '{self.home / '.nvm'}'\n")
        brew.chmod(0o755)

    def test_template_keeps_default_when_no_nvm_node_was_inherited(self):
        # $DIRENV_DIR alone doesn't keep anything: a shell that inherits it without any nvm
        # Node on PATH (a parent that replaced PATH) still gets `default`.
        self.fake_nvm("24")
        self.fake_brew_nvm()
        self.zshenv(zshenv_nvm_block())
        env = dict(self.env, DIRENV_DIR=f"-{self.repo}")
        out = subprocess.run(["zsh", "-c", "command -v node"], cwd="/tmp", env=env,
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                             timeout=60).stdout.strip()
        self.assertEqual(out, str(self.home / ".nvm/versions/node/v26.0.0/bin/node"))

    def node_ahead_of_nvm(self, bin_dir):
        """A `node` (v26) in `bin_dir`, which ~/.zshenv prepends before the NVM block."""
        bin_dir.mkdir(parents=True)
        (bin_dir / "node").write_text("#!/bin/sh\necho v26.0.0\n")
        (bin_dir / "node").chmod(0o755)
        return f'export PATH="{bin_dir}:$PATH"\n'

    def test_template_keeps_nvm_ahead_of_a_local_bin_node_shim(self):
        # The template prepends ~/.local/bin before the NVM block, and managed workstations
        # keep a tool's `node` shim there (DevBar's). A guard that only skipped the prepend let
        # that shim win in the nested shell (bgaldino-ltmf746, pack 285): the block must move
        # the inherited nvm Node back in front of it, without adding a second copy.
        self.fake_nvm("24")
        self.fake_brew_nvm()
        self.zshenv(self.node_ahead_of_nvm(self.home / ".local" / "bin") + zshenv_nvm_block())
        repo, nested = self.nested(self.run_check("node-nested-shell"))
        self.assertTrue(repo.startswith("v24.0.0 from ~/.nvm/versions/node/v24.0.0/bin/node;"), repo)
        self.assertEqual(nested, repo)

    def test_template_keeps_nvm_ahead_of_a_shim_with_the_installers_nvm(self):
        # scheck-ltmj0vv's shape: nvm from nvm's own installer ($NVM_DIR/nvm.sh, no Homebrew
        # nvm) and a ~/.local/bin node shim. The block must find that nvm.sh too, and the
        # reorder must not depend on it.
        self.fake_nvm("24")
        self.zshenv(self.node_ahead_of_nvm(self.home / ".local" / "bin") + zshenv_nvm_block())
        repo, nested = self.nested(self.run_check("node-nested-shell"))
        self.assertTrue(repo.startswith("v24.0.0 from ~/.nvm/versions/node/v24.0.0/bin/node;"), repo)
        self.assertEqual(nested, repo)

    def test_template_keeps_an_inherited_xdg_nvm_dir(self):
        # An nvm installed under $XDG_CONFIG_HOME: .envrc exports that NVM_DIR and puts its Node
        # first. The nested shell must keep the inherited NVM_DIR, so it recognises that Node,
        # rather than resetting NVM_DIR to ~/.nvm and putting Homebrew nvm's default first.
        xdg = self.home / ".config" / "nvm"
        node = xdg / "versions" / "node" / "v24.0.0" / "bin" / "node"
        node.parent.mkdir(parents=True)
        node.write_text("#!/bin/sh\necho v24.0.0-xdg\n")
        node.chmod(0o755)
        (self.repo / ".envrc").write_text(f'export NVM_DIR="{xdg}"\nPATH_add "{node.parent}"\n')
        self.fake_nvm("node")
        self.fake_brew_nvm()
        self.zshenv(self.node_ahead_of_nvm(self.home / ".local" / "bin") + zshenv_nvm_block())
        out = self.run_check("node-nested-shell")
        self.assertIn("nested shell: v24.0.0-xdg from ~/.config/nvm/versions/node/v24.0.0/bin/node;", out)

    def test_template_keeps_nvm_ahead_of_a_homebrew_node(self):
        # `brew shellenv` moves Homebrew's bin first in every shell; a Homebrew `node` there
        # must not win in the nested shell either.
        self.fake_nvm("24")
        self.fake_brew_nvm()
        self.zshenv(self.node_ahead_of_nvm(self.home / "homebrew" / "bin") + zshenv_nvm_block())
        repo, nested = self.nested(self.run_check("node-nested-shell"))
        self.assertEqual(nested, repo)

    def test_nested_shell_shows_a_node_ahead_of_nvm_without_the_template(self):
        # With no NVM block to put nvm's Node back, a `node` prepended before it wins in the
        # nested shell, and the check names its path.
        self.zshenv(self.node_ahead_of_nvm(self.home / ".local" / "bin"))
        repo, nested = self.nested(self.run_check("node-nested-shell"))
        self.assertTrue(repo.startswith("v24.0.0 from ~/.nvm/versions/node/v24.0.0/bin/node;"), repo)
        self.assertTrue(nested.startswith("v26.0.0 from ~/.local/bin/node;"), nested)

    def test_nested_shell_shows_a_duplicate_from_an_unconditional_default_prepend(self):
        # bgaldino-ltmf746's hand-written block: `default` prepended in every shell. Here it's
        # the pinned line, so Node is right, but the nested shell's list gains a second copy.
        self.zshenv('export PATH="$HOME/.nvm/versions/node/v24.0.0/bin:$PATH"')
        repo, nested = self.nested(self.run_check("node-nested-shell"))
        self.assertEqual(nested.split(";")[0], repo.split(";")[0])
        dirs = lambda out: out.split("on PATH:", 1)[1].split()
        self.assertEqual(len(dirs(nested)), len(dirs(repo)) + 1, (repo, nested))

    def test_template_block_is_idempotent(self):
        # Run twice in one shell (a nested shell of a nested shell), the block leaves the
        # inherited nvm Node dir in front, once, and the rest of PATH in order, empty entries
        # (the current directory) included.
        self.fake_nvm("24")
        self.fake_brew_nvm()
        block = self.home / "block.sh"
        block.write_text(zshenv_nvm_block())
        nvm24 = self.home / ".nvm/versions/node/v24.0.0/bin"
        nvm26 = self.home / ".nvm/versions/node/v26.0.0/bin"
        # A package's bin dir under an nvm version, ahead of the Node bin: not the one to keep.
        pkg = self.home / ".nvm/versions/node/v24.0.0/lib/node_modules/pkg/bin"
        pkg.mkdir(parents=True)
        env = dict(self.env, DIRENV_DIR=f"-{self.repo}",
                   PATH=f":/opt/x:{pkg}:{nvm24}::{self.bin}:/usr/bin:/bin:{nvm26}")
        for shell in ("zsh", "sh"):
            out = subprocess.run([shell, "-c", f'. "{block}"; . "{block}"; echo "$PATH"'],
                                 env=env, stdout=subprocess.PIPE, text=True, check=True,
                                 timeout=60).stdout.strip()
            self.assertEqual(out, f"{nvm24}::/opt/x:{pkg}::{self.bin}:/usr/bin:/bin:{nvm26}", shell)

    def test_nvm_default_shows_the_alias_and_what_it_resolves_to(self):
        self.zshenv("")
        self.assertIn("nvm not found", self.run_check("nvm-default"))
        self.fake_nvm("node")
        out = self.run_check("nvm-default")
        self.assertIn(".nvmrc: 24", out)
        self.assertIn("default -> node -> v26.0.0", out)


class Run(unittest.TestCase):
    def run_one(self, command, timeout=30, grace=ta.HELD_OUTPUT_GRACE):
        check = ta.Check(1, "probe", "Probe", command=command)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            ok = ta.run(check, ta.pick_shell(None), str(REPO), timeout, grace=grace)
        return ok, out.getvalue()

    @staticmethod
    def alive(pid):
        """Running, not just present. os.kill(pid, 0) succeeds for a killed child that
        isn't fully gone: a zombie (Z) under a PID 1 that doesn't reap (some containers),
        and, while the reaper releases it, a dead task (X). Counting X as running made
        wait_gone flake on Linux CI right after the kill."""
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        if os.path.isdir("/proc/self"):
            # procfs is the authority: a missing entry is a task released since kill().
            try:
                with open(f"/proc/{pid}/stat") as f:
                    return f.read().rsplit(")", 1)[1].split()[0] not in ("Z", "X")
            except (OSError, IndexError):
                return False
        # No procfs (macOS): ask ps.
        try:
            stat = subprocess.run(["ps", "-o", "stat=", "-p", str(pid)],
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                  text=True, timeout=10).stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            return True
        return bool(stat) and stat[0] not in "ZX"

    def wait_gone(self, pid):
        # A process that stopped running doesn't come back: decide on the sample that
        # saw it stop, not on a second one.
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if not self.alive(pid):
                return True
            time.sleep(0.05)
        return False

    def test_output_and_exit_status_are_evidence(self):
        ok, out = self.run_one('printf one; echo two >&2; echo "cwd=$(pwd)"; exit 3')
        self.assertTrue(ok)
        lines = out.splitlines()
        self.assertEqual(lines[0], "== §1 probe: Probe")
        self.assertIn("two", out)
        # The shell can report a logical path (macOS links /var to /private/var), so
        # compare resolved paths on both sides.
        cwd = next(line[len("cwd="):] for line in lines if line.startswith("cwd="))
        self.assertEqual(Path(cwd).resolve(), REPO.resolve())
        self.assertEqual(lines[-1], "[exit 3]")

    def test_timeout_is_reported(self):
        ok, out = self.run_one("echo started; sleep 5", timeout=1)
        self.assertFalse(ok)
        self.assertIn("started", out)
        self.assertIn("[timeout after 1s]", out)

    def test_timeout_stops_what_the_shell_started(self):
        # A grandchild (npm, cci, a fresh zsh) must not outlive a timed-out check.
        ok, out = self.run_one('sleep 30 & echo "child=$!"; wait', timeout=1)
        self.assertFalse(ok)
        pid = int(next(l for l in out.splitlines() if l.startswith("child="))[6:])
        self.assertTrue(self.wait_gone(pid), "the background sleep survived the timeout")

    def test_interrupt_stops_the_check_group(self):
        # The group runs in its own session, so Ctrl-C at the terminal never reaches it:
        # run() has to stop it before the KeyboardInterrupt leaves.
        with tempfile.TemporaryDirectory() as tmp:
            pidfile = os.path.join(tmp, "pid")
            real = ta.time.monotonic
            calls = []

            def interrupt_in_loop():
                calls.append(1)
                if len(calls) > 1 and os.path.exists(pidfile) and os.path.getsize(pidfile):
                    raise KeyboardInterrupt
                return real()

            ta.time.monotonic = interrupt_in_loop
            try:
                with self.assertRaises(KeyboardInterrupt):
                    self.run_one(f'sleep 30 & echo $! > "{pidfile}"; wait', timeout=60)
            finally:
                ta.time.monotonic = real
            with open(pidfile) as f:
                pid = int(f.read())
        self.assertTrue(self.wait_gone(pid), "the background sleep survived the interrupt")

    def test_output_held_after_the_shell_exits_is_stopped(self):
        # A background job from a startup file can hold the output open after the shell
        # exits; the check ends after the grace period, not at the timeout.
        start = time.monotonic()
        ok, out = self.run_one('sleep 30 & echo "child=$!"; exit 4', timeout=60, grace=1)
        self.assertTrue(ok)
        self.assertLess(time.monotonic() - start, 20)
        self.assertIn("[exit 4; stopped what it left holding its output", out)
        pid = int(next(l for l in out.splitlines() if l.startswith("child="))[6:])
        self.assertTrue(self.wait_gone(pid))


if __name__ == "__main__":
    unittest.main()
