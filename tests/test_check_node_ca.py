"""Offline fixtures for scripts/ai/check_node_ca.py.

The case that matters is the one npm can't show: two shell blocks each assign their own
bundle, the later one wins, and Node loses the other's certificates while a registry with
a public certificate still answers. The zsh cases run only where zsh exists.
Stdlib only. Run with: python tests/test_check_node_ca.py
"""
import base64
import contextlib
import io
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts" / "ai"))
import check_node_ca as cnc  # noqa: E402


def pem(*payloads):
    """A PEM file body with one fake certificate per payload (only the DER bytes are hashed)."""
    out = []
    for p in payloads:
        b64 = base64.b64encode(p.encode()).decode()
        out.append("-----BEGIN CERTIFICATE-----\n" + b64 + "\n-----END CERTIFICATE-----\n")
    return "".join(out)


class Home(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.home)

    def write(self, rel, text):
        path = os.path.join(self.home, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)
        return path


class TraceParsing(unittest.TestCase):
    def test_assignments_from_xtrace(self):
        trace = "\n".join([
            "+/h/.zshenv:3> export NODE_EXTRA_CA_CERTS=/h/a.pem",
            "+/h/.zshrc:9> NODE_EXTRA_CA_CERTS=/h/b.pem",
            "+/h/.zshrc:10> typeset -gx NODE_EXTRA_CA_CERTS='/h/with space.pem'",
            "+/h/.zshrc:11> export NODE_EXTRA_CA_CERTS=/h/a.pem:/h/c.pem",
            "+/h/.zshrc:12> echo NODE_EXTRA_CA_CERTS=/h/not-an-assignment.pem",
            "+/h/.zshrc:13> export MY_NODE_EXTRA_CA_CERTS=/h/other.pem",
            "+/h/.zshrc:14> export TOKEN=secret",
            "+/h/.zshrc:15> export A=1 NODE_EXTRA_CA_CERTS=/h/d.pem",
            "+f:0> local NODE_EXTRA_CA_CERTS=/h/local.pem",
            "+/h/.zshrc:16> NODE_EXTRA_CA_CERTS=/h/prefix.pem +/h/.zshrc:16> true",
        ])
        self.assertEqual(cnc.assigned_from_trace(trace),
                         ["/h/a.pem", "/h/b.pem", "/h/with space.pem", "/h/c.pem", "/h/d.pem"])

    def test_a_shell_that_didnt_run_is_a_fail_not_na(self):
        self.assertEqual(cnc.evaluate("/h", [], {"-c": None, "-lic": None})[0], 1)
        self.assertEqual(cnc.evaluate("/h", [], {"-c": "", "-lic": None})[0], 1)


class Fingerprints(Home):
    def test_counts_unique_certificates(self):
        p = self.write("x.pem", pem("one", "two", "one"))
        self.assertEqual(len(cnc.fingerprints(p)), 2)

    def test_missing_file_is_empty(self):
        self.assertEqual(cnc.fingerprints(os.path.join(self.home, "nope.pem")), set())


class Evaluate(Home):
    def setUp(self):
        super().setUp()
        self.corp = self.write(".corp/bundle.pem", pem("c1", "c2", "shared"))
        self.tool = self.write(".tool/bundle.pem", pem("t1", "shared"))
        self.combined = self.write(".config/certs/combined.pem", pem("c1", "c2", "shared", "t1"))

    def test_later_block_wins_is_a_fail(self):
        status, lines = cnc.evaluate(self.home, [self.corp, self.tool], {"-c": self.tool, "-lic": self.tool})
        self.assertEqual(status, 1)
        self.assertTrue(any("2 of its 3 certs aren't in the exported file" in l for l in lines), lines)

    def test_combined_file_passes(self):
        status, lines = cnc.evaluate(self.home, [self.corp, self.tool, self.combined],
                                     {"-c": self.combined, "-lic": self.combined})
        self.assertEqual(status, 0, lines)

    def test_empty_in_noninteractive_shell_fails(self):
        status, lines = cnc.evaluate(self.home, [self.tool], {"-c": "", "-lic": self.tool})
        self.assertEqual(status, 1)
        self.assertIn("FAIL: zsh -c exports nothing", lines)

    def test_colon_list_fails_and_redacts_every_element(self):
        value = f"{self.corp}:{self.tool}"
        status, lines = cnc.evaluate(self.home, [self.corp, self.tool], {"-c": value, "-lic": value})
        self.assertEqual(status, 1)
        self.assertTrue(any("colon-separated" in l for l in lines))
        self.assertFalse(any(self.home in l for l in lines), lines)

    def test_exported_file_without_certificates_fails(self):
        empty = self.write("empty.pem", "not a certificate\n")
        status, lines = cnc.evaluate(self.home, [], {"-c": empty, "-lic": empty})
        self.assertEqual(status, 1)
        self.assertTrue(any("holds no PEM certificates" in l for l in lines))

    def test_shells_disagree_fails(self):
        status, lines = cnc.evaluate(self.home, [], {"-c": self.combined, "-lic": self.tool})
        self.assertEqual(status, 1)
        self.assertIn("FAIL: the two shells export different files", lines)

    def test_nothing_assigned_or_exported_is_na(self):
        self.assertEqual(cnc.evaluate(self.home, [], {"-c": "", "-lic": ""})[0], cnc.NA)

    def test_assigned_but_absent_bundle_is_only_noted(self):
        gone = os.path.join(self.home, "gone.pem")
        status, lines = cnc.evaluate(self.home, [gone, self.combined], {"-c": self.combined, "-lic": self.combined})
        self.assertEqual(status, 0)
        self.assertTrue(any(l.startswith("note:") for l in lines))

    def test_output_uses_tilde_not_home(self):
        _, lines = cnc.evaluate(self.home, [self.corp], {"-c": self.tool, "-lic": self.tool})
        self.assertFalse(any(self.home in l for l in lines), lines)


def _system_zsh_sets_var():
    for name in ("zshenv", "zprofile", "zshrc", "zlogin"):
        try:
            with open(os.path.join("/etc", name), errors="replace") as f:
                if "NODE_EXTRA_CA_CERTS" in f.read():
                    return True
        except OSError:
            pass
    return False


@unittest.skipUnless(shutil.which("zsh"), "zsh not installed")
@unittest.skipIf(_system_zsh_sets_var(), "this host's /etc/zsh* sets NODE_EXTRA_CA_CERTS")
class RealShells(Home):
    """End to end through fresh zsh shells, the way the audit runs it."""

    def run_main(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return cnc.main(["--home", self.home])

    def setUp(self):
        super().setUp()
        self.write(".corp/bundle.pem", pem("c1", "c2"))
        self.write(".tool/bundle.pem", pem("t1"))
        self.write(".zshrc",
                   "# corp-managed-start\nexport NODE_EXTRA_CA_CERTS=\"$HOME/.corp/bundle.pem\"\n# corp-managed-end\n"
                   "# >>> tool >>>\nexport NODE_EXTRA_CA_CERTS=\"$HOME/.tool/bundle.pem\"\n# <<< tool <<<\n")

    def test_two_blocks_fail(self):
        self.assertEqual(self.run_main(), 1)

    def test_losing_bundle_assigned_through_a_variable_fails(self):
        self.write(".zshrc",
                   'corp="$HOME/.corp/bundle.pem"\nexport NODE_EXTRA_CA_CERTS="$corp"\n'
                   'export NODE_EXTRA_CA_CERTS="$HOME/.tool/bundle.pem"\n')
        self.assertEqual(self.run_main(), 1)

    def test_assignment_in_a_sourced_file_is_seen(self):
        self.write(".corp.zsh", 'export NODE_EXTRA_CA_CERTS="$HOME/.corp/bundle.pem"\n')
        self.write(".zshrc", 'source "$HOME/.corp.zsh"\nexport NODE_EXTRA_CA_CERTS="$HOME/.tool/bundle.pem"\n')
        self.assertEqual(self.run_main(), 1)

    def test_zdotdir_files_are_seen(self):
        self.write(".zshenv", 'ZDOTDIR="$HOME/.config/zsh"\n')
        os.remove(os.path.join(self.home, ".zshrc"))
        self.write(".config/zsh/.zshrc",
                   'export NODE_EXTRA_CA_CERTS="$HOME/.corp/bundle.pem"\n'
                   'export NODE_EXTRA_CA_CERTS="$HOME/.tool/bundle.pem"\n')
        self.assertEqual(self.run_main(), 1)

    def test_unexported_assignment_is_not_an_export(self):
        self.write(".zshrc", "")
        self.write(".zshenv", 'NODE_EXTRA_CA_CERTS="$HOME/.corp/bundle.pem"\n')
        self.assertEqual(self.run_main(), 1)

    def test_combined_export_from_zshenv_passes(self):
        self.write(".config/certs/all.pem", pem("c1", "c2", "t1"))
        self.write(".zshenv", 'export NODE_EXTRA_CA_CERTS="$HOME/.config/certs/all.pem"\n')
        with open(os.path.join(self.home, ".zshrc"), "a") as f:
            f.write('export NODE_EXTRA_CA_CERTS="$HOME/.config/certs/all.pem"\n')
        self.assertEqual(self.run_main(), 0)


if __name__ == "__main__":
    unittest.main()
