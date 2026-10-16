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
import re
import sys
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
        self.assertTrue({c.section for c in ta.CHECKS} <= set(ta.SECTIONS))
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
        code, _ = run_main("--check", "nope")
        self.assertNotEqual(code, 0)


class Run(unittest.TestCase):
    def run_one(self, command, timeout=30):
        check = ta.Check(1, "probe", "Probe", command=command)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            ok = ta.run(check, ta.pick_shell(None), str(REPO), timeout)
        return ok, out.getvalue()

    def test_output_and_exit_status_are_evidence(self):
        ok, out = self.run_one('printf one; echo two >&2; pwd; exit 3')
        self.assertTrue(ok)
        lines = out.splitlines()
        self.assertEqual(lines[0], "== §1 probe: Probe")
        self.assertIn("two", out)
        self.assertIn(str(REPO), out)
        self.assertEqual(lines[-1], "[exit 3]")

    def test_timeout_is_reported(self):
        ok, out = self.run_one("echo started; sleep 5", timeout=1)
        self.assertFalse(ok)
        self.assertIn("[timeout after 1s]", out)


if __name__ == "__main__":
    unittest.main()
