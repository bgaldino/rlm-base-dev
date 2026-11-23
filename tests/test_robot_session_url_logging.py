#!/usr/bin/env python3
"""Robot results must never contain a Salesforce session URL (todo 418).

``sf org open --url-only`` prints ``https://<host>/secur/frontdoor.jsp?sid=...&otp=...``, a live
login. The setup suites used to pass it through Robot variables, so ``Go To ${target}`` and the
keyword return value wrote it into output.xml and log.html. ``SessionUrlGuard.py`` now keeps it in
Python. These cases run the real ``SetupToggles.robot`` / ``E2ECommon.robot`` navigation keywords in
a real Robot process, against a fake ``sf`` on PATH that prints a sentinel frontdoor URL and a stub
SeleniumLibrary that records what the browser would have loaded, then scan every result file
(including log.html's compressed strings) for the sentinel and the frontdoor pattern. No org,
browser or network is used.

Run:  python tests/test_robot_session_url_logging.py     (needs robotframework)
"""
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts" / "ai"))
import check_robot_session_urls as scanner  # noqa: E402

SID = "00DSENTINELORGID0001!SENTINEL-SESSION-ID"
OTP = "SENTINELONETIMEPASSWORD"
FRONTDOOR = f"https://example.my.salesforce.com/secur/frontdoor.jsp?sid={SID}&otp={OTP}&retURL=%2Flightning%2Fsetup"

FAKE_SF = f"""#!/bin/sh
if [ "$FAKE_SF_FAIL" = "1" ]; then echo "sf failed near {FRONTDOOR}" >&2; exit 1; fi
echo "Access org with the following URL: {FRONTDOOR}"
"""

# Stand-ins for the two libraries the resources import; the real ones need a browser.
STUB_SELENIUM_LIBRARY = '''
import os
class _Driver:
    def get(self, url):
        with open(os.environ["STUB_NAV_LOG"], "a") as f:
            f.write(url + "\\n")
        if os.environ.get("STUB_NAV_FAIL") == "1":
            raise RuntimeError("navigation to " + url + " failed")
class SeleniumLibrary:
    def __init__(self, *args, **kwargs):
        self.driver = _Driver()
    def go_to(self, url):
        self.driver.get(url)
    def get_title(self):
        return os.environ.get("STUB_TITLE", "Setup Home")
    def wait_until_page_contains_element(self, locator, timeout=None):
        pass
    def capture_page_screenshot(self, filename=None):
        pass
'''
STUB_SELENIUM = {"selenium/__init__.py": "", "selenium/webdriver.py": ""}

SUITE = """*** Settings ***
Resource    {resources}/SetupToggles.robot
Resource    {resources}/E2ECommon.robot

*** Variables ***
${{MANUAL_LOGIN_WAIT}}    0s
${{REVENUE_SETTINGS_URL}}    https://example.my.salesforce-setup.com/lightning/setup/RevenueSettings/home

*** Test Cases ***
Setup Page Through Org Alias
    Open Setup Page    /lightning/setup/Timeline/home

Revenue Settings Through Org Alias
    Open Revenue Settings Page

Explicit Plain Url
    Open Setup Page    url=https://example.my.salesforce-setup.com/lightning/setup/Timeline/home

Login Page Retry
    Open Setup Page    /lightning/setup/Timeline/home

E2E App And Record
    Navigate To App    Revenue Cloud
    Navigate To Record    Account    001000000000001AAA

Failing Navigation Is Redacted
    [Tags]    expect-fail
    Open Setup Page    /lightning/setup/Timeline/home
"""


class SessionUrlLoggingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        (root / "bin").mkdir()
        sf = root / "bin" / "sf"
        sf.write_text(FAKE_SF)
        sf.chmod(sf.stat().st_mode | stat.S_IEXEC)
        stubs = root / "stubs"
        (stubs / "selenium").mkdir(parents=True)
        (stubs / "SeleniumLibrary.py").write_text(STUB_SELENIUM_LIBRARY)
        for rel, body in STUB_SELENIUM.items():
            (stubs / rel).write_text(body)
        cls.root, cls.stubs = root, stubs
        suite = root / "suite.robot"
        suite.write_text(SUITE.format(resources=REPO / "robot" / "rlm-base" / "resources"))
        cls.suite = suite

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_robot(self, name, extra_env=None, loglevel="DEBUG", include=None, exclude=None):
        out = self.root / name
        env = dict(os.environ)
        env.update(
            PATH=f"{self.root / 'bin'}{os.pathsep}{env['PATH']}",
            STUB_NAV_LOG=str(self.root / f"{name}.nav"),
            **(extra_env or {}),
        )
        cmd = [sys.executable, "-m", "robot", "--pythonpath", str(self.stubs), "--outputdir", str(out),
               "--loglevel", loglevel, "--variable", "ORG_ALIAS:my-alias", "--variable", "LIGHTNING_RENDER_WAIT:0s", "--variable", f"EXECDIR:{REPO}"]
        for tag in include or []:
            cmd += ["--include", tag]
        for tag in exclude or []:
            cmd += ["--exclude", tag]
        proc = subprocess.run(cmd + [str(self.suite)], cwd=REPO, env=env, capture_output=True, text=True)
        return proc, out

    def assert_clean(self, proc, out):
        console = proc.stdout + proc.stderr
        self.assertNotIn(SID, console)
        self.assertNotIn(OTP, console)
        self.assertFalse(scanner.SESSION_URL_PATTERN.search(console), "session URL on the console")
        files = [p for p in out.rglob("*") if p.is_file()]
        self.assertTrue(any(p.name == "output.xml" for p in files))
        for path in files:
            if path.suffix in {".xml", ".html"}:
                text = path.read_text(encoding="utf-8", errors="replace")
                self.assertNotIn(SID, text, path.name)
                self.assertNotIn(OTP, text, path.name)
        self.assertEqual(scanner.scan_paths([out]), [])

    def test_passing_suite_leaves_no_session_url(self):
        proc, out = self.run_robot("pass", exclude=["expect-fail"], extra_env={"STUB_TITLE": "Log In"})
        self.assertEqual(proc.returncode, 0, proc.stdout[-2000:])
        self.assert_clean(proc, out)
        loaded = (self.root / "pass.nav").read_text().splitlines()
        # The browser really got the frontdoor URL (so the guard is not just skipping navigation).
        self.assertTrue(loaded and all(u == FRONTDOOR or "/lightning/setup/Timeline/home" in u for u in loaded), loaded)
        # 5 authenticated navigations plus re-navigations after each "Log In" title.
        self.assertGreaterEqual(len(loaded), 5)
        self.assertIn("https://example.my.salesforce-setup.com/lightning/setup/Timeline/home", loaded)

    def test_info_loglevel_also_clean(self):
        proc, out = self.run_robot("info", loglevel="INFO", exclude=["expect-fail"])
        self.assertEqual(proc.returncode, 0, proc.stdout[-2000:])
        self.assert_clean(proc, out)

    def test_failed_navigation_message_is_redacted(self):
        proc, out = self.run_robot("navfail", include=["expect-fail"], extra_env={"STUB_NAV_FAIL": "1"})
        self.assertEqual(proc.returncode, 1)
        self.assertIn("session-url-redacted", proc.stdout)
        self.assert_clean(proc, out)

    def test_failed_sf_message_is_redacted(self):
        proc, out = self.run_robot("sffail", include=["expect-fail"], extra_env={"FAKE_SF_FAIL": "1"})
        self.assertEqual(proc.returncode, 1)
        self.assertIn("sf org open failed", proc.stdout)
        self.assert_clean(proc, out)

    def test_log_level_restored_after_navigation(self):
        proc, out = self.run_robot("level", exclude=["expect-fail"], loglevel="INFO")
        self.assertEqual(proc.returncode, 0)
        xml = (out / "output.xml").read_text(encoding="utf-8")
        # Keywords after the navigation are still logged: the level was restored.
        self.assertIn("Wait Until Page Contains Element", xml)
        self.assertIn("Navigated to app: Revenue Cloud", xml)


class ScannerTest(unittest.TestCase):
    """The check must be able to fail, including on log.html's compressed strings."""

    def test_detects_session_patterns(self):
        with tempfile.TemporaryDirectory() as d:
            for name, body in {
                "a.xml": f"<msg>{FRONTDOOR}</msg>",
                "b.xml": "<msg>https://x.my.salesforce.com/home?foo=1&sid=ABCDEF123456</msg>",
                "c.xml": "<msg>https://x.my.salesforce.com/x?otp=ABCDEF123456</msg>",
            }.items():
                (Path(d) / name).write_text(body)
            self.assertEqual(sorted(p.name for p in scanner.scan_paths([d])), ["a.xml", "b.xml", "c.xml"])

    def test_clean_text_passes(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "ok.xml").write_text("<msg>Navigated to app: X; sid and otp are words; /lightning/page</msg>")
            self.assertEqual(scanner.scan_paths([d]), [])

    def test_detects_compressed_log_html_strings(self):
        import base64
        import json
        import zlib
        packed = base64.b64encode(zlib.compress(FRONTDOOR.encode())).decode()
        html = 'window.output["strings"] = window.output["strings"].concat(' + json.dumps(["*plain", packed]) + ");"
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "log.html").write_text(html)
            self.assertFalse(scanner.SESSION_URL_PATTERN.search(html))
            self.assertEqual([p.name for p in scanner.scan_paths([d])], ["log.html"])

    def test_main_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(scanner.main([d]), 0)
            (Path(d) / "output.xml").write_text(FRONTDOOR)
            self.assertEqual(scanner.main([d]), 1)
            self.assertEqual(scanner.main([os.path.join(d, "missing")]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
