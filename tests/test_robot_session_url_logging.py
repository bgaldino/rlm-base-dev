#!/usr/bin/env python3
"""Robot results must never contain a Salesforce session URL.

``sf org open --url-only`` prints ``https://<host>/secur/frontdoor.jsp?sid=...&otp=...``, a live
login. The setup suites used to pass it through Robot variables, so ``Go To ${target}`` and the
keyword return value wrote it into output.xml and log.html. ``SessionUrlGuard.py`` now keeps it in
Python. These cases run the real ``SetupToggles.robot`` / ``E2ECommon.robot`` navigation keywords in
a real Robot process, against a fake ``sf`` on PATH that prints a sentinel frontdoor URL and a stub
SeleniumLibrary that records what the browser would have loaded, then scan every result file
(including log.html's compressed strings) for the sentinel and the frontdoor pattern. No org,
browser or network is used.

The stub reproduces the real leak sources (selenium's remote_connection DEBUG request/response
lines and SeleniumLibrary's "Opening url" INFO line). Mutation tests copy the robot tree, switch the
protection off in the copy and require the scanner to find the leak, so a green run cannot mean
"nothing was ever emitted".

Run:  python tests/test_robot_session_url_logging.py     (needs robotframework)
"""
import base64
import importlib.util
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


scanner = _load("check_robot_session_urls", REPO / "scripts" / "ai" / "check_robot_session_urls.py")
guard = _load("session_url_guard_under_test", REPO / "robot" / "rlm-base" / "resources" / "SessionUrlGuard.py")

SID = "00DSENTINELORGID0001!SENTINEL-SESSION-ID"
OTP = "SENTINELONETIMEPASSWORD"
FRONTDOOR = f"https://example.my.salesforce.com/secur/frontdoor.jsp?sid={SID}&otp={OTP}&retURL=%2Flightning%2Fsetup"

FAKE_SF = f"""#!/bin/sh
if [ "$FAKE_SF_FAIL" = "1" ]; then
  echo '{{"name":"Error","message":"sf failed near {FRONTDOOR}","exitCode":1,"status":1}}' >&2
  exit 1
fi
echo '{{"status":0,"result":{{"url":"{FRONTDOOR}"}}}}'
"""

# Stand-ins for the two libraries the resources import; the real ones need a browser.
STUB_SELENIUM_LIBRARY = '''
import logging
import os

from robot.api import logger


def _emit(kind):
    # Proof the stub emitted a leak source, whatever Robot then did with it.
    with open(os.environ["STUB_EMIT_LOG"], "a") as f:
        f.write(kind + "\\n")


class _Driver:
    @property
    def current_url(self):
        url = os.environ.get("STUB_CURRENT_URL", "https://example.my.salesforce.com/lightning/page")
        logging.getLogger("selenium.webdriver.remote.remote_connection").debug(
            "Remote response: status=200 | data={\\"value\\":\\"%s\\"} | headers={}", url)
        _emit("response")
        return url

    def get(self, url):
        with open(os.environ["STUB_NAV_LOG"], "a") as f:
            f.write(url + "\\n")
        logging.getLogger("selenium.webdriver.remote.remote_connection").debug(
            "POST http://127.0.0.1:1/session/abc/url {\\"url\\": \\"%s\\"}", url)
        _emit("request")
        if os.environ.get("STUB_NAV_FAIL") == "1":
            raise RuntimeError("navigation to " + url + " failed")


class SeleniumLibrary:
    def __init__(self, *args, **kwargs):
        self.driver = _Driver()
        self.password_changed = False

    def go_to(self, url):
        logger.info("Opening url '%s'" % url)  # what the real SeleniumLibrary logs
        _emit("opening")
        self.driver.get(url)

    def get_title(self):
        if os.environ.get("STUB_CHANGE_PW") == "1" and not self.password_changed:
            return "Change Your Password"
        return os.environ.get("STUB_TITLE", "Setup Home")

    def get_webelements(self, locator):
        return ["password-1", "password-2"] if os.environ.get("STUB_CHANGE_PW") == "1" else []

    def input_password(self, locator, password):
        pass

    def click_element(self, locator):
        self.password_changed = True

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

Change Password Flow
    [Tags]    changepw
    Open Setup Page    /lightning/setup/Timeline/home

Current Url Is Read Without Logging
    [Tags]    currenturl
    ${id}=    Get Record Id From Url
    Should Be Equal    ${id}    001000000000001AAA
    Current Url Should Be Record Page    Account
    Run Keyword And Expect Error    *not a Contact record page*    Current Url Should Be Record Page    Contact

Log Level Is Restored After A Failed Navigation
    [Tags]    level
    Set Log Level    WARN
    Run Keyword And Expect Error    *    Go To Authenticated Page    my-alias    /lightning/setup/Timeline/home
    ${level}=    Set Log Level    DEBUG
    Should Be Equal    ${level}    WARN
"""


def render_suite(resources):
    return SUITE.replace("{resources}", str(resources)).replace("{{", "{").replace("}}", "}")


CURRENT_URL = f"https://example.my.salesforce.com/lightning/r/Account/001000000000001AAA/view?sid={SID}&otp={OTP}"
NAV_TAGS = ["expect-fail", "changepw", "currenturl", "level"]


def _pack(text):
    return base64.b64encode(zlib.compress(text.encode())).decode()


class RobotRunMixin:
    @classmethod
    def build_workspace(cls):
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

    def make_tree(self, name, mutate=None):
        """Copy robot/rlm-base into the workspace (optionally mutating the guard) and write the suite."""
        tree = self.root / name
        shutil.copytree(REPO / "robot" / "rlm-base", tree / "robot" / "rlm-base",
                        ignore=shutil.ignore_patterns("results", "__pycache__"))
        if mutate:
            guard_py = tree / "robot" / "rlm-base" / "resources" / "SessionUrlGuard.py"
            source = guard_py.read_text()
            mutated = mutate(source)
            self.assertNotEqual(mutated, source, "the mutation did not change the guard")
            guard_py.write_text(mutated)
        suite = tree / "suite.robot"
        suite.write_text(render_suite(tree / "robot" / "rlm-base" / "resources"))
        return tree, suite

    def run_robot(self, name, tree=None, suite=None, extra_env=None, loglevel="DEBUG", include=None, exclude=None):
        if tree is None:
            tree, suite = REPO, self.suite
        out = self.root / f"out-{name}"
        nav, emit = self.root / f"{name}.nav", self.root / f"{name}.emit"
        env = dict(os.environ)
        env.update(
            PATH=f"{self.root / 'bin'}{os.pathsep}{env['PATH']}",
            STUB_NAV_LOG=str(nav),
            STUB_EMIT_LOG=str(emit),
            STUB_CURRENT_URL=CURRENT_URL,
            **(extra_env or {}),
        )
        cmd = [sys.executable, "-m", "robot", "--pythonpath", str(self.stubs), "--outputdir", str(out),
               "--loglevel", loglevel, "--variable", "ORG_ALIAS:my-alias", "--variable", "LIGHTNING_RENDER_WAIT:0s",
               "--variable", f"EXECDIR:{tree}"]
        for tag in include or []:
            cmd += ["--include", tag]
        for tag in exclude or []:
            cmd += ["--exclude", tag]
        proc = subprocess.run(cmd + [str(suite)], cwd=tree, env=env, capture_output=True, text=True)
        emitted = emit.read_text().splitlines() if emit.exists() else []
        return proc, out, emitted


class SessionUrlLoggingTest(RobotRunMixin, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build_workspace()
        suite = cls.root / "suite.robot"
        suite.write_text(render_suite(REPO / "robot" / "rlm-base" / "resources"))
        cls.suite = suite

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def assert_clean(self, proc, out, emitted):
        # The stub emitted leak sources, so a clean result is the protection, not silence.
        self.assertTrue(emitted, "stub emitted nothing: this test would pass vacuously")
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
        proc, out, emitted = self.run_robot("pass", exclude=NAV_TAGS, extra_env={"STUB_TITLE": "Log In"})
        self.assertEqual(proc.returncode, 0, proc.stdout[-2000:])
        self.assert_clean(proc, out, emitted)
        loaded = (self.root / "pass.nav").read_text().splitlines()
        # The browser really got the frontdoor URL (so the guard is not just skipping navigation).
        self.assertIn(FRONTDOOR, loaded)
        self.assertGreaterEqual(len(loaded), 5)
        self.assertIn("https://example.my.salesforce-setup.com/lightning/setup/Timeline/home", loaded)

    def test_info_loglevel_also_clean(self):
        proc, out, emitted = self.run_robot("info", loglevel="INFO", exclude=NAV_TAGS)
        self.assertEqual(proc.returncode, 0, proc.stdout[-2000:])
        self.assert_clean(proc, out, emitted)

    def test_failed_navigation_message_is_redacted(self):
        proc, out, emitted = self.run_robot("navfail", include=["expect-fail"], extra_env={"STUB_NAV_FAIL": "1"})
        self.assertEqual(proc.returncode, 1)
        self.assertIn("session-url-redacted", proc.stdout)
        self.assert_clean(proc, out, emitted)

    def test_failed_sf_message_is_redacted(self):
        proc, out, emitted = self.run_robot("sffail", include=["expect-fail"], extra_env={"FAKE_SF_FAIL": "1"})
        self.assertEqual(proc.returncode, 1)
        self.assertIn("sf org open failed", proc.stdout)
        self.assertFalse(emitted)  # sf failed before any navigation
        console = proc.stdout + proc.stderr
        self.assertNotIn(SID, console)
        self.assertEqual(scanner.scan_paths([out]), [])

    def test_change_password_flow_is_clean(self):
        proc, out, emitted = self.run_robot("changepw", include=["changepw"], extra_env={"STUB_CHANGE_PW": "1"})
        self.assertEqual(proc.returncode, 0, proc.stdout[-2000:])
        self.assert_clean(proc, out, emitted)
        # Initial navigation plus the re-navigation after the password was changed.
        self.assertEqual((self.root / "changepw.nav").read_text().splitlines(), [FRONTDOOR, FRONTDOOR])

    def test_current_url_is_never_logged(self):
        proc, out, emitted = self.run_robot("currenturl", include=["currenturl"])
        self.assertEqual(proc.returncode, 0, proc.stdout[-2000:])
        self.assertIn("response", emitted)
        self.assert_clean(proc, out, emitted)

    def test_log_level_restored_after_failed_navigation(self):
        proc, out, emitted = self.run_robot("level", include=["level"], extra_env={"STUB_NAV_FAIL": "1"})
        self.assertEqual(proc.returncode, 0, proc.stdout[-2000:])  # the test asserts the sentinel level came back
        self.assert_clean(proc, out, emitted)

    def test_log_level_restored_after_navigation(self):
        proc, out, _ = self.run_robot("restored", exclude=NAV_TAGS, loglevel="INFO")
        self.assertEqual(proc.returncode, 0)
        xml = (out / "output.xml").read_text(encoding="utf-8")
        # Keywords after the navigation are still logged: the level was restored.
        self.assertIn("Wait Until Page Contains Element", xml)
        self.assertIn("Navigated to app: Revenue Cloud", xml)


class MutationTest(RobotRunMixin, unittest.TestCase):
    """With the protection switched off the scanner MUST find the leak (the check can fail)."""

    @classmethod
    def setUpClass(cls):
        cls.build_workspace()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def assert_leaks(self, name, mutate, loglevel="DEBUG", include=None, exclude=None, env=None, rc=None):
        tree, suite = self.make_tree(name, mutate)
        proc, out, emitted = self.run_robot(name, tree, suite, loglevel=loglevel, include=include,
                                            exclude=exclude, extra_env=env)
        if rc is not None:
            self.assertEqual(proc.returncode, rc, proc.stdout[-2000:])
        self.assertTrue(emitted, "stub emitted nothing")
        hits = scanner.scan_paths([out])
        self.assertTrue(hits, "scanner missed a deliberate leak")
        # The finding is the sentinel session, not an unrelated match: it must be in the decoded text.
        seen = []
        for hit in hits:
            text = hit.read_text(encoding="utf-8", errors="replace")
            seen.append(text)
            if hit.suffix in {".html", ".htm", ".js"}:
                seen.extend(scanner._decoded_strings(text))
        self.assertTrue(any(SID in t or OTP in t for t in seen), "finding does not contain the sentinel session")

    def test_level_not_lowered_leaks_selenium_debug_request(self):
        def mutate(src):
            head, sep, tail = src.partition("    def _current_url")
            return head.replace('set_log_level("NONE")', 'set_log_level("DEBUG")') + sep + tail
        self.assert_leaks("mut-level", mutate, exclude=NAV_TAGS, rc=0)

    def test_go_to_instead_of_driver_get_leaks_opening_url_line(self):
        def mutate(src):
            return src.replace('set_log_level("NONE")', 'set_log_level("INFO")').replace(
                'get_library_instance("SeleniumLibrary").driver.get(url)',
                'get_library_instance("SeleniumLibrary").go_to(url)')
        self.assert_leaks("mut-opening", mutate, loglevel="INFO", exclude=NAV_TAGS, rc=0)

    def test_redaction_off_leaks_failure_message(self):
        self.assert_leaks(
            "mut-redact",
            lambda src: src.replace("redact_session_urls(exc, url)", "exc"),
            include=["expect-fail"], env={"STUB_NAV_FAIL": "1"}, rc=1)

    def test_current_url_read_with_logging_on_leaks(self):
        def mutate(src):
            head, sep, tail = src.partition("    def _current_url")
            return head + sep + tail.replace('set_log_level("NONE")', 'set_log_level("DEBUG")')
        self.assert_leaks("mut-current", mutate, include=["currenturl"], rc=0)


class RedactionTest(unittest.TestCase):
    def test_pattern_matches_plain_and_encoded_forms(self):
        for text in [
            "https://h/secur/frontdoor.jsp?x=1", "https://h/secur%2Ffrontdoor.jsp", "https://H/SECUR/FRONTDOOR.JSP",
            "https://h/p?sid=abc", "https://h/p?a=1&sid=abc", "x;otp=abc", "https%3A%2F%2Fh%2Fp%3Fsid%3Dabc",
            "p%3Fotp=abc", "a%26sid%3Dabc", "a%26OTP%3Dabc", "https://h/p?a=1&amp;sid=abc",
        ]:
            self.assertTrue(guard.SESSION_URL_PATTERN.search(text), text)
            self.assertTrue(scanner.SESSION_URL_PATTERN.search(text), text)

    def test_pattern_matches_bare_params_cookies_and_double_encoding(self):
        for text in [
            "sid=00D000000000000AA!AAAAAAAA; oid=00D000000000000",  # cookie string, starts with sid=
            "Cookie: foo=1; sid=abc", "'sid=abc'", "(otp=abc)", "a,sid=abc",
            "https%253A%252F%252Fh%252Fp%253Fsid%253Dabc", "a%2526otp%253Dabc", "h/secur%252Ffrontdoor.jsp",
        ]:
            self.assertTrue(guard.SESSION_URL_PATTERN.search(text), text)
            self.assertTrue(scanner.SESSION_URL_PATTERN.search(text), text)

    def test_pattern_matches_a_raw_session_id(self):
        # Shape inferred from Salesforce session ids: 00D + 12-15 org-id chars, '!', 20+ token chars.
        for sid in ["00D000000000000AAA!AAAAAAAAAAAAAAAAAAAAAAAA", "00D000000000000!AAAAAAAAAA.AAAAAAAAAA_AA"]:
            self.assertTrue(guard.SESSION_URL_PATTERN.search(f"value {sid} end"), sid)
            self.assertTrue(scanner.SESSION_URL_PATTERN.search(sid), sid)
            self.assertEqual(guard.redact_session_urls(f"bad {sid}"), guard.WITHHELD)
        for encoded in ["00D000000000000AAA%21AAAAAAAAAAAAAAAAAAAAAAAA", "00D000000000000%2521AAAAAAAAAAAAAAAAAAAAAAAA"]:
            self.assertTrue(guard.SESSION_URL_PATTERN.search(f"cookie {encoded}"), encoded)
            self.assertTrue(scanner.SESSION_URL_PATTERN.search(encoded), encoded)
            self.assertEqual(guard.redact_session_urls(f"bad {encoded}"), guard.WITHHELD)
        # Encoded context: the char before 00D is the last hex digit of an escape, not a boundary.
        for encoded in ["x%3D00D000000000000%21" + "A" * 24, "%22sessionId%22%3A%2200D000000000000%21" + "A" * 24,
                        "a%2C00D000000000000%2521" + "A" * 24]:
            self.assertTrue(guard.SESSION_URL_PATTERN.search(encoded), encoded)
            self.assertTrue(scanner.SESSION_URL_PATTERN.search(encoded), encoded)
            self.assertEqual(guard.redact_session_urls(f"bad {encoded}"), guard.WITHHELD)
        # No left anchor: any prefix (double-encoded, JS/JSON escapes, a word char) still matches.
        for encoded in ["%253D00D000000000000%2521" + "A" * 24, "%2522%253A%252200D000000000000%2521" + "A" * 24,
                        "\\x3d00D000000000000!" + "A" * 24, "x100D000000000000%21" + "A" * 24]:
            self.assertTrue(guard.SESSION_URL_PATTERN.search(encoded), encoded)
            self.assertTrue(scanner.SESSION_URL_PATTERN.search(encoded), encoded)
            self.assertEqual(guard.redact_session_urls(f"bad {encoded}"), guard.WITHHELD)
        self.assertFalse(guard.SESSION_URL_PATTERN.search("00D00000000000%21" + "A" * 24))  # id too short
        self.assertFalse(guard.SESSION_URL_PATTERN.search("00D000000000000%21" + "A" * 19))  # token too short
        self.assertFalse(guard.SESSION_URL_PATTERN.search("00D000000000000" + "A" * 24))  # no separator
        self.assertFalse(guard.SESSION_URL_PATTERN.search("00D000000000000%21short"))
        self.assertFalse(guard.SESSION_URL_PATTERN.search("00D000000000000!short"))
        self.assertFalse(guard.SESSION_URL_PATTERN.search("record 00D000000000000 is an org id"))

    def test_raw_values_with_plus_are_redacted(self):
        url = "https://h.my.salesforce.com/secur/frontdoor.jsp?sid=AAAA+BBBB+CCCC&otp=DDDD"
        out = guard.redact_session_urls("failed with value AAAA+BBBB+CCCC here", url)
        self.assertNotIn("AAAA+BBBB+CCCC", out)

    def test_bare_sid_message_is_withheld(self):
        self.assertEqual(guard.redact_session_urls("sid=00D000000000000AA!AAAAAAAA"), guard.WITHHELD)

    def test_pattern_leaves_ordinary_text(self):
        for text in ["sid and otp are words", "/lightning/setup/Timeline/home", "https://h/p?side=1&other=2",
                     "residual=1"]:
            self.assertFalse(guard.SESSION_URL_PATTERN.search(text), text)

    def test_guard_and_scanner_patterns_agree(self):
        self.assertEqual(guard.SESSION_URL_PATTERN.pattern, scanner.SESSION_URL_PATTERN.pattern)
        self.assertEqual(guard.SESSION_URL_PATTERN.flags, scanner.SESSION_URL_PATTERN.flags)

    def test_known_url_and_values_are_replaced(self):
        out = guard.redact_session_urls(f"failed: {FRONTDOOR} then", FRONTDOOR)
        self.assertEqual(out, f"failed: {guard.REDACTED} then")
        # A bare value (no URL around it) is replaced when the URL is known.
        out = guard.redact_session_urls(f"bad session {SID} and {OTP}", FRONTDOOR)
        self.assertNotIn(SID, out)
        self.assertNotIn(OTP, out)
        # Percent-encoded copy of the whole URL.
        from urllib.parse import quote
        out = guard.redact_session_urls(f"see {quote(FRONTDOOR, safe='')}", FRONTDOOR)
        self.assertNotIn("frontdoor", out.lower())

    def test_other_session_urls_are_replaced_without_a_known_url(self):
        out = guard.redact_session_urls("cannot load https://h.my.salesforce.com/p?sid=ZZZ999&a=1 now")
        self.assertEqual(out, f"cannot load {guard.REDACTED} now")

    def test_message_is_withheld_when_the_pattern_survives(self):
        # No scheme, so the URL redaction cannot see it; the pattern still matches.
        self.assertEqual(guard.redact_session_urls("at host/secur/frontdoor.jsp?sid=ZZZ999"), guard.WITHHELD)
        self.assertEqual(guard.redact_session_urls("odd ?otp=ZZZ999 fragment"), guard.WITHHELD)

    def fetch_with(self, stdout, stderr):
        class Result:
            returncode = 1

        Result.stdout, Result.stderr = stdout, stderr
        real_run, real_which = guard.subprocess.run, guard.shutil.which
        guard.subprocess.run, guard.shutil.which = (lambda *a, **k: Result()), (lambda name: "/bin/sf")
        try:
            with self.assertRaises(RuntimeError) as ctx:
                guard._fetch_url("x", "/p")
        finally:
            guard.subprocess.run, guard.shutil.which = real_run, real_which
        return str(ctx.exception)

    def test_sf_error_json_on_stderr_is_parsed(self):
        # The parsed message, not the raw stderr, is reported.
        msg = self.fetch_with("", '{"name":"Error","message":"no such org","exitCode":1}')
        self.assertEqual(msg, "sf org open failed (exit 1): no such org")
        self.assertNotIn('"exitCode"', msg)

    def test_sf_error_json_on_stdout_is_parsed(self):
        # Older sf wrote the error JSON to stdout.
        msg = self.fetch_with('{"name":"Error","message":"no such org","exitCode":1}', "")
        self.assertEqual(msg, "sf org open failed (exit 1): no such org")

    def test_ordinary_messages_pass_through(self):
        self.assertEqual(guard.redact_session_urls("timeout after 120s"), "timeout after 120s")


class ScannerTest(unittest.TestCase):
    """The check must be able to fail, including on log.html's compressed strings."""

    def scan(self, **files):
        with tempfile.TemporaryDirectory() as d:
            for name, body in files.items():
                (Path(d) / name.replace("__", ".")).write_text(body)
            return sorted(p.name for p in scanner.scan_paths([d]))

    @staticmethod
    def log_html(*chunks):
        return "<script>" + "".join(
            'window.output["strings"] = window.output["strings"].concat(' + c + ");\n" for c in chunks
        ) + "</script>"

    def test_detects_session_patterns(self):
        self.assertEqual(self.scan(
            a__xml=f"<msg>{FRONTDOOR}</msg>",
            b__xml="<msg>https://x.my.salesforce.com/home?foo=1&amp;sid=ABCDEF123456</msg>",
            c__xml="<msg>https://x.my.salesforce.com/x?otp=ABCDEF123456</msg>",
            d__xml="<msg>https%3A%2F%2Fx%2Fsecur%2Ffrontdoor.jsp</msg>".replace("%2Ffrontdoor", "%2Ffrontdoor"),
        ), ["a.xml", "b.xml", "c.xml", "d.xml"])

    def test_clean_text_passes(self):
        self.assertEqual(self.scan(ok__xml="<msg>Navigated to app: X; sid and otp are words; /lightning/page</msg>"), [])

    def test_detects_compressed_log_html_strings(self):
        html = self.log_html(json.dumps(["*plain", _pack(FRONTDOOR)]))
        self.assertFalse(scanner.SESSION_URL_PATTERN.search(html))
        self.assertEqual(self.scan(log__html=html), ["log.html"])

    def test_leak_in_a_later_chunk_and_encoded_in_compressed_string(self):
        html = self.log_html(
            json.dumps(["*clean", "*text with ); and ] inside"]),
            json.dumps([_pack("fine"), _pack("p%3Fsid%3Dabc")]),
        )
        self.assertEqual(self.scan(log__html=html), ["log.html"])

    def test_clean_multi_chunk_log_html_passes(self):
        html = self.log_html(json.dumps(["*a", _pack("b")]), json.dumps(["*c"]))
        self.assertEqual(self.scan(log__html=html), [])

    def test_robot_hex_escapes_are_decoded(self):
        chunk = '["*\\x3cp>hello\\x3c/p>", "' + _pack(FRONTDOOR) + '"]'
        self.assertEqual(self.scan(log__html=self.log_html(chunk)), ["log.html"])
        clean = '["*\\x3cp>hello\\x3c/p>"]'
        self.assertEqual(self.scan(log__html=self.log_html(clean)), [])

    def test_undecodable_chunk_is_a_finding(self):
        self.assertEqual(self.scan(log__html=self.log_html('["*ok", "unterminated')), ["log.html"])

    def test_split_log_js_files(self):
        leak = "window.strings1 = " + json.dumps(["*x", _pack(FRONTDOOR)]) + ";\n"
        clean = "window.strings2 = " + json.dumps(["*x", _pack("fine")]) + ";\n"
        broken = "window.strings3 = [\"*x\", ;\n"
        self.assertEqual(self.scan(**{"log-1__js": leak, "log-2__js": clean, "log-3__js": broken}),
                         ["log-1.js", "log-3.js"])

    def test_main_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(scanner.main([d]), 0)
            (Path(d) / "output.xml").write_text(FRONTDOOR)
            self.assertEqual(scanner.main([d]), 1)
            self.assertEqual(scanner.main([os.path.join(d, "missing")]), 2)


class RobotTreeSweepTest(unittest.TestCase):
    """Static guard: nothing in robot/ or tasks/ may read, log or navigate to a URL unguarded.

    Name based: it flags the keywords and calls below by text. It cannot see a URL reached through a
    keyword it does not know, so the live-run scan (check_robot_session_urls.py) stays the backstop.
    The forbidden keywords are those of the installed SeleniumLibrary that read
    ``driver.current_url`` (which selenium then logs at DEBUG), plus a few that do not themselves
    read it but sit in the same family and are barred by design (``Close Window`` and
    ``Get Window Handles`` only use ``driver.close()``/``driver.window_handles``): the location
    keywords, the window keywords, ``Log Source``, cookies, and every keyword that finds an element
    by an ``a``/``img``/``input`` tag (links, images, buttons, checkboxes, radio buttons, text
    fields). With an unprefixed locator the element finder reads the base URL, because those tags'
    key attributes include ``@href``/``@src``. Keywords that find by ``button``/``textarea``/``select``
    or no tag do not. A prefixed locator (``id:``, ``css:``, ``xpath:``) avoids the read, but this sweep
    is name based and cannot tell, so the keywords are barred outright; use ``Click Element`` with a
    prefixed locator instead.
    """

    FORBIDDEN = re.compile(
        r"\b(?:Get[ _]?Locations?|Location[ _]?Should[ _]?(?:Not[ _]?)?(?:Be|Contain)|Log[ _]?Location"
        r"|Wait[ _]?Until[ _]?Location[ _]?(?:Is|Is[ _]?Not|Contains|Does[ _]?Not[ _]?Contain)"
        r"|Get[ _]?Source|Log[ _]?Source|Get[ _]?Cookies?|Add[ _]?Cookie|Delete[ _]?(?:All[ _]?)?Cookies?"
        r"|Switch[ _]?Window|Close[ _]?Window|Get[ _]?Window[ _]?(?:Titles|Names|Identifiers|Handles)"
        r"|Click[ _]?(?:Link|Image|Button)|Mouse[ _]?Down[ _]?On[ _]?(?:Link|Image)"
        r"|Page[ _]?Should[ _]?(?:Not[ _]?)?Contain[ _]?(?:Link|Image|Button|Checkbox|Radio[ _]?Button|Textfield)"
        r"|(?:Select|Unselect)[ _]?Checkbox|Checkbox[ _]?Should[ _]?(?:Not[ _]?)?Be[ _]?Selected"
        r"|Textfield[ _]?(?:Should[ _]?Contain|Value[ _]?Should[ _]?Be)"
        r"|get_location|get_locations|current_url|page_source|window_handles)\b"
        r"|(?:window\.|document\.)location\b(?!\.pathname)"
        r"|\blocation\.(?:href|search|hash|origin|host|hostname|toString)\b"
        r"|\bdocument\.(?:URL|documentURI|baseURI|referrer)\b",
        re.IGNORECASE)
    ORG_OPEN = re.compile(r"org\s+open\b.*(?:--url-only|\s-r\b)|[\"']org[\"'],\s*[\"']open[\"']|\burl-only\b")
    # Python files: prose (docstrings) may name the command; only code that runs it counts.
    ORG_OPEN_PY = re.compile(
        r"[\"']org[\"'],\s*[\"']open[\"']|[\"']sf org open|(?:run|Popen|check_output|check_call|call|shlex\.split)\(.*org\s+open")
    DOC_LINE = re.compile(r"\s*(?:#|\.\.\.|\[Documentation\]|Documentation\b)")

    def files(self, *roots):
        found = []
        for root in roots:
            found += [p for p in sorted((REPO / root).rglob("*")) if p.suffix in {".robot", ".py"}
                      and "results" not in p.parts and p.name != "SessionUrlGuard.py"]
        return found

    def hits(self, pattern, files, skip_docs=False):
        found = []
        for path in files:
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if skip_docs and self.DOC_LINE.match(line):
                    continue
                if pattern.search(line):
                    found.append(f"{path.relative_to(REPO)}:{number}")
        return found

    def test_forbidden_pattern_flags_each_reader(self):
        for line in ["    ${u}=    Get Location", "    Get Locations", "    Location Should Be    x",
                     "    Wait Until Location Contains    x", "    Log Location", "    Get Cookies",
                     "    Switch Window    NEW", "    Get Window Titles", "    Log Source", "    Click Link    x",
                     "    Execute JavaScript    return window.location.href", "    Execute JavaScript    return location.search",
                     "    Execute JavaScript    return document.URL", "    Execute JavaScript    return window.location",
                     "    Click Button    Save", "    Page Should Not Contain Button    Save",
                     "    Page Should Contain Checkbox    x", "    Select Checkbox    x", "    Unselect Checkbox    x",
                     "    Checkbox Should Be Selected    x", "    Checkbox Should Not Be Selected    x",
                     "    Page Should Contain Radio Button    x", "    Page Should Contain Textfield    x",
                     "    Textfield Should Contain    x    y", "    Textfield Value Should Be    x    y"]:
            self.assertTrue(self.FORBIDDEN.search(line), line)
        # Python spellings and Robot's case/space/underscore-insensitive names.
        for line in ['        selib.click_button("Save")', "        selib.select_checkbox('x')",
                     "        self.selenium.checkbox_should_be_selected(loc)", "        s.page_should_contain_textfield(x)",
                     "        s.textfield_value_should_be(a, b)", "    Click_Button    Save", "    clickbutton    Save",
                     "    Page_Should_Not_Contain_Button    x", "        s.click_link(x)", "        s.get_location()"]:
            self.assertTrue(self.FORBIDDEN.search(line), line)
        self.assertFalse(self.FORBIDDEN.search("    ... window.location.pathname ..."))
        # Prefixed locators and tags that do not read the URL stay allowed.
        for line in ["    Click Element    link:Home", "    Click Element    id:save", "    Input Text    id:x    y",
                     "    Textarea Should Contain    x    y", "    Radio Button Should Be Set To    g    v"]:
            self.assertFalse(self.FORBIDDEN.search(line), line)

    def test_no_unguarded_url_or_source_reads(self):
        self.assertEqual(self.hits(self.FORBIDDEN, self.files("robot", "tasks")), [],
                         "use SessionUrlGuard keywords instead")

    def test_org_open_only_in_the_guard(self):
        robot_files = [f for f in self.files("robot") if f.suffix == ".robot"]
        py_files = [f for f in self.files("robot", "tasks") if f.suffix == ".py"]
        found = self.hits(self.ORG_OPEN, robot_files, skip_docs=True) + self.hits(self.ORG_OPEN_PY, py_files)
        self.assertEqual(found, [], "only SessionUrlGuard.py may call sf org open --url-only / -r")
        self.assertTrue(self.ORG_OPEN_PY.search('cmd = ["org", "open", "-r"]'))
        self.assertTrue(self.ORG_OPEN.search("Run Process    sf org open -o x -r"))

    def test_go_to_never_takes_a_session_variable(self):
        allowed = re.compile(r"^\s*Go To\s{2,}(about:blank|\$\{url\})\s*$")
        found = []
        for path in self.files("robot"):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if re.match(r"\s*Go To\s{2,}", line) and not allowed.match(line):
                    found.append(f"{path.relative_to(REPO)}:{number}")
        self.assertEqual(found, [])

    def test_no_committed_org_host_in_robot_tree(self):
        host = re.compile(r"https://[a-z0-9-]+\.(?:scratch\.)?my\.salesforce(?:-setup)?\.com", re.IGNORECASE)
        found = []
        for path in self.files("robot"):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if host.search(line) and "your-org" not in line and "example" not in line:
                    found.append(f"{path.relative_to(REPO)}:{number}")
        self.assertEqual(found, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
