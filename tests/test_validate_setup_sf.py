#!/usr/bin/env python3
"""validate_setup's sf CLI check: it names the sf that runs, and WARNs on a shadowed second one.

Fake `sf` executables on a temporary PATH; no real sf, no org. Stdlib only.

Run with: python tests/test_validate_setup_sf.py
"""
import logging
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tasks.rlm_validate_setup import FAIL, PASS, WARN, ValidateSetup  # noqa: E402


class ValidateSetupSf(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        saved = os.environ.get("PATH", "")
        self.addCleanup(os.environ.__setitem__, "PATH", saved)
        self.task = object.__new__(ValidateSetup)
        self.task.logger = logging.getLogger("validate_setup_sf_test")

    def fake_sf(self, subdir, version):
        """An executable `sf` under tmp/<subdir> that prints a CLI version line."""
        d = Path(self.tmp.name) / subdir
        d.mkdir(parents=True, exist_ok=True)
        sf = d / "sf"
        sf.write_text(f"#!/bin/sh\necho '@salesforce/cli/{version} darwin-arm64 node-v24.22.0'\n")
        sf.chmod(sf.stat().st_mode | stat.S_IXUSR)
        return d

    def on_path(self, *dirs):
        # Only the fake dirs: the Docker image (and a distro npm) puts a real sf in /usr/bin, which
        # would count as a second install. The fakes need nothing else: `#!/bin/sh` is absolute
        # and `echo` is a builtin.
        os.environ["PATH"] = os.pathsep.join(str(d) for d in dirs)

    def test_one_install_passes_and_names_its_path(self):
        first = self.fake_sf("a/node_modules/@salesforce/cli/bin", "2.154.4")
        self.on_path(first)
        result = self.task._check_sf_cli()
        self.assertEqual(result["status"], PASS, result)
        self.assertIn(str(first / "sf"), result["detail"])
        self.assertIn("(npm)", result["detail"])

    def test_a_second_install_later_on_path_warns_and_names_both(self):
        first = self.fake_sf("npm/node_modules/@salesforce/cli/bin", "2.154.4")
        second = self.fake_sf("standalone/sf/bin", "2.150.6")
        self.on_path(first, second)
        result = self.task._check_sf_cli()
        self.assertEqual(result["status"], WARN, result)
        self.assertIn(str(first / "sf"), result["detail"])
        self.assertIn(str(second / "sf"), result["detail"])
        self.assertIn("2.150.6", result["detail"], "the shadowed copy's own version is reported")
        self.assertIn("standalone installer", result["detail"])

    def test_the_same_install_reached_twice_is_not_a_second_install(self):
        real = self.fake_sf("real", "2.154.4")
        link_dir = Path(self.tmp.name) / "linked"
        link_dir.mkdir()
        (link_dir / "sf").symlink_to(real / "sf")
        self.on_path(link_dir, real)
        self.assertEqual(self.task._check_sf_cli()["status"], PASS)

    def test_an_old_major_still_fails(self):
        self.on_path(self.fake_sf("old", "1.99.0"))
        self.assertEqual(self.task._check_sf_cli()["status"], FAIL)

    def test_install_methods(self):
        m = ValidateSetup._sf_install_method
        self.assertEqual(m("/x/lib/node_modules/@salesforce/cli/bin/run.js"), "npm")
        self.assertEqual(m("/opt/homebrew/Cellar/sf/2.1/bin/sf"), "Homebrew")
        self.assertEqual(m("/home/u/.local/share/sf/client/2.1/bin/sf"), "standalone installer")
        self.assertEqual(m("/usr/local/bin/something"), "")


if __name__ == "__main__":
    unittest.main()
