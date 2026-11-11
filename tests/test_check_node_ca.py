"""Offline fixtures for scripts/ai/check_node_ca.py.

The case that matters is the one npm can't show: two shell blocks each assign their own
bundle, the later one wins, and Node loses the other's certificates while a registry with
a public certificate still answers. The zsh cases run only where zsh exists.
Stdlib only. Run with: python tests/test_check_node_ca.py
"""
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


# Six self-signed test certificates (CN "check-node-ca test 1..6"). OpenSSL loads them
# without checking expiry or chain, so they don't go stale; no private key is kept.
CERTS = [
    """-----BEGIN CERTIFICATE-----
MIIBdTCCARqgAwIBAgIUQ0445JMrMM9Nb2l/qwBuTqDnPMgwCgYIKoZIzj0EAwIw
HzEdMBsGA1UEAwwUY2hlY2stbm9kZS1jYSB0ZXN0IDEwIBcNMjYxMDE1MTkwNTE4
WhgPMjEyNjA5MjExOTA1MThaMB8xHTAbBgNVBAMMFGNoZWNrLW5vZGUtY2EgdGVz
dCAxMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEaYm89yEiQ4cbMfZlj3oWHo7D
P/DjvR8YtV3MqzCE1Y+/XQnLo96uOYtWAyX8I9mQX4eAn478XTjFXw9BA+BoYaMy
MDAwHQYDVR0OBBYEFKgq87KY5xJT023tI19hwm1r5ZDvMA8GA1UdEwEB/wQFMAMB
Af8wCgYIKoZIzj0EAwIDSQAwRgIhALxn4GUe9OoqV3MyRDsZEwwmBzQbcunFIR2G
sGMBsNcsAiEAws5tByZ4chE8AE0dLBTT0LNYv5Wcz7vSk/uN2AsSBmc=
-----END CERTIFICATE-----\n""",
    """-----BEGIN CERTIFICATE-----
MIIBczCCARqgAwIBAgIUQDT6xQiYrWWtYC0nNcnwzWv4Zd4wCgYIKoZIzj0EAwIw
HzEdMBsGA1UEAwwUY2hlY2stbm9kZS1jYSB0ZXN0IDIwIBcNMjYxMDE1MTkwNTE4
WhgPMjEyNjA5MjExOTA1MThaMB8xHTAbBgNVBAMMFGNoZWNrLW5vZGUtY2EgdGVz
dCAyMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE0Y7w/qiSEeeij8RERtjOqAWz
f1xAeWc12f4IMRmYVUC5jq5a+aXu+byeVV1umxevmKUxOlY7rgsGdystz9x/UKMy
MDAwHQYDVR0OBBYEFMLHhR2ClTqjHvT04MClgzwq/Ru7MA8GA1UdEwEB/wQFMAMB
Af8wCgYIKoZIzj0EAwIDRwAwRAIgAcwVBYvITY/ow1QBQpzNYRJyyIg8k/Ic/yX8
taDiNd4CIGK4QTk7w/1JDCy5NdMCxN5gIKDwyzbmj5ubAP4W1KGy
-----END CERTIFICATE-----\n""",
    """-----BEGIN CERTIFICATE-----
MIIBczCCARqgAwIBAgIUdOnfeECk06XAMHE911+XQKg08BMwCgYIKoZIzj0EAwIw
HzEdMBsGA1UEAwwUY2hlY2stbm9kZS1jYSB0ZXN0IDMwIBcNMjYxMDE1MTkwNTE4
WhgPMjEyNjA5MjExOTA1MThaMB8xHTAbBgNVBAMMFGNoZWNrLW5vZGUtY2EgdGVz
dCAzMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEUXKpEMGo7psEmvN5hP0RmM86
ZKTDT5Dl1hj7HCnaDZuOjgQeQcnlsPHQ9VpfbSfs2Ux8WGlISvi8qJESL+5JvKMy
MDAwHQYDVR0OBBYEFJWSurOiyRl0hMIjNdgmYhOqgMggMA8GA1UdEwEB/wQFMAMB
Af8wCgYIKoZIzj0EAwIDRwAwRAIgBuU1Y9ilHCniyW4DqQR511i5zseqUm/kys/v
ehzUfGMCICl3nn6EAg08Y60RGssUl9HNgSGW1WZ8r9c/rfiSu/2a
-----END CERTIFICATE-----\n""",
    """-----BEGIN CERTIFICATE-----
MIIBdDCCARqgAwIBAgIUJ6P4vD0IM4E+nRMtIdm1Qve0YvowCgYIKoZIzj0EAwIw
HzEdMBsGA1UEAwwUY2hlY2stbm9kZS1jYSB0ZXN0IDQwIBcNMjYxMDE1MTkwNTE4
WhgPMjEyNjA5MjExOTA1MThaMB8xHTAbBgNVBAMMFGNoZWNrLW5vZGUtY2EgdGVz
dCA0MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEYY6VfEYKjk28E31br1YINLY+
7YxYsrlSHVD7PXxX+YDXXbV6G3jL14Cv7aQoS7Y3PR8glLovPGD+Lwlnhpz3raMy
MDAwHQYDVR0OBBYEFLwO1cYmOfzc3RIfC4we6M9O+IUHMA8GA1UdEwEB/wQFMAMB
Af8wCgYIKoZIzj0EAwIDSAAwRQIhAM50E45/KZo2FwKgOi9OJdsvnYoXwu8AsFsN
Ml/23+P1AiAR9Qu2YUB14w7zAjMWRo7CiZ+o5n/WF86J+KTGrE0yPg==
-----END CERTIFICATE-----\n""",
    """-----BEGIN CERTIFICATE-----
MIIBdTCCARqgAwIBAgIUa0EU9KedUIDfKcFanHFnuzbe9IswCgYIKoZIzj0EAwIw
HzEdMBsGA1UEAwwUY2hlY2stbm9kZS1jYSB0ZXN0IDUwIBcNMjYxMDE1MTkwNTE4
WhgPMjEyNjA5MjExOTA1MThaMB8xHTAbBgNVBAMMFGNoZWNrLW5vZGUtY2EgdGVz
dCA1MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEoBz6TQybics2wV/DPTF+kHnC
/tHSCWb68pY22lI4+2lPlgFhuQDjwImKaFs5ugY88G398iVHMeXaHvPuWtq/W6My
MDAwHQYDVR0OBBYEFI9GtvhMBocTmL6PPhhB8tCKDGEZMA8GA1UdEwEB/wQFMAMB
Af8wCgYIKoZIzj0EAwIDSQAwRgIhANnpNjDeyrZpYXaq8ezlSxUINB5oDeo/sr1N
COKHGpQkAiEA2pe91+ld6vk4xPU71PZhaBUUY++G7vMgadcCw/FzsEU=
-----END CERTIFICATE-----\n""",
    """-----BEGIN CERTIFICATE-----
MIIBczCCARqgAwIBAgIUSIE7hx5r3t9xraGVdLzRz1BGviUwCgYIKoZIzj0EAwIw
HzEdMBsGA1UEAwwUY2hlY2stbm9kZS1jYSB0ZXN0IDYwIBcNMjYxMDE1MTkwNTE4
WhgPMjEyNjA5MjExOTA1MThaMB8xHTAbBgNVBAMMFGNoZWNrLW5vZGUtY2EgdGVz
dCA2MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEB6fm7DM6tzMoJmkgix73C/ee
bjwVw+RyV0TTwF5lLiM84opmI0lShw0jaqGqgj4MCn6kgV+vxKwJn4ZkbJZtYKMy
MDAwHQYDVR0OBBYEFIXcWp2EPiex/Nr89kY8+v4gUU4WMA8GA1UdEwEB/wQFMAMB
Af8wCgYIKoZIzj0EAwIDRwAwRAIgcsqFSoPSCOUmADCMK0AnyYyuSscQDwosEKFe
TyUIVgICIDFv/nr/dW74OGXbNtyJVUu5Lj76E4SZLHEYjr26u7zS
-----END CERTIFICATE-----\n""",
]
NAMES = {}


def pem(*names):
    """A PEM file body with one real certificate per name; the same name gives the same cert."""
    for n in names:
        if n not in NAMES:
            NAMES[n] = CERTS[len(NAMES)]
    return "".join(NAMES[n] for n in names)


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

    def test_exported_file_openssl_rejects_fails(self):
        joined = self.write("joined.pem", pem("c1", "c2", "shared").rstrip("\n") + pem("t1"))
        status, lines = cnc.evaluate(self.home, [self.corp, self.tool], {"-c": joined, "-lic": joined})
        self.assertEqual(status, 1)
        self.assertTrue(any("OpenSSL can't fully parse" in l and l.startswith("FAIL") for l in lines), lines)
        self.assertIn("note: bundle coverage not checked: no shell exports a file Node can load whole", lines)

    def test_assigned_bundle_openssl_rejects_is_noted(self):
        joined = self.write("joined.pem", pem("c1").rstrip("\n") + pem("t1"))
        status, lines = cnc.evaluate(self.home, [joined, self.combined], {"-c": self.combined, "-lic": self.combined})
        self.assertEqual(status, 0, lines)
        self.assertTrue(any(l.startswith("note:") and "OpenSSL" in l for l in lines), lines)

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
