#!/usr/bin/env python3
"""
Offline invariants for the Chrome/ChromeDriver override handling shared by the
Robot helpers and tasks/rlm_validate_setup.ValidateSetup.

    python tests/test_validate_setup_chrome.py

No org, browser, or CumulusCI install required -- fake ``--version``
executables in a temp directory stand in for Chrome and ChromeDriver.

Why this file exists
--------------------
On some managed workstations stock Chrome crashes headless on Salesforce Setup
pages, and the workaround is CHROME_BINARY + CHROMEDRIVER_PATH pointing at a
matching Chrome for Testing pair. validate_setup has to report what Robot will
actually launch: an override that is set but broken must not pass silently, a
broken CHROMEDRIVER_PATH falls back (WebDriverManager.py ignores it), and a
browser/driver major-version mismatch -- the usual failure when only one of the
two is overridden -- must be flagged before a build gets as far as docgen: as a
FAIL when the browser is an override (certain), a WARN when it was guessed.
"""
import importlib.util
import logging
import os
import stat
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tasks.rlm_validate_setup import FAIL, PASS, WARN, ValidateSetup  # noqa: E402

# Loaded by path, like Robot does; named as a stdlib_offline_suites trigger in pr_gate.py.
_WDM_SRC = REPO_ROOT / "robot" / "rlm-base" / "resources" / "WebDriverManager.py"
_spec = importlib.util.spec_from_file_location("WebDriverManager", _WDM_SRC)
WebDriverManager = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(WebDriverManager)

RESULTS = []
ENV_VARS = ("CHROME_BINARY", "CHROME_BIN", "CHROMEDRIVER_PATH", "PATH")


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))


def _task(tmp):
    """A task isolated from host drivers: its system-driver location is a path
    under ``tmp`` that does not exist, so only PATH (set per check) is searched."""
    task = object.__new__(ValidateSetup)
    task.logger = logging.getLogger("validate_setup_test")
    task._system_chromedriver = str(Path(tmp) / "no-system-chromedriver")
    return task


def _fake_binary(directory, name, version_line):
    path = Path(directory) / name
    path.write_text(f"#!/bin/sh\necho '{version_line}'\n")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return str(path)


def _set_env(**values):
    for var in ENV_VARS:
        os.environ.pop(var, None)
    for var, value in values.items():
        os.environ[var] = value


def check_chrome_binary_override_wins(tmp):
    chrome = _fake_binary(tmp, "cft-chrome", "Google Chrome for Testing 154.0.8037.92")
    _set_env(CHROME_BINARY=chrome, CHROME_BIN="/nonexistent/chromium")
    result = _task(tmp)._check_chrome_chromium()
    check("chrome_binary_override_wins", result["status"] == PASS and "CHROME_BINARY" in result["detail"], result["detail"])


def check_chrome_bin_is_fallback(tmp):
    chrome = _fake_binary(tmp, "chromium", "Chromium 154.0.8037.98")
    _set_env(CHROME_BIN=chrome)
    result = _task(tmp)._check_chrome_chromium()
    check("chrome_bin_is_fallback", result["status"] == PASS and "CHROME_BIN" in result["detail"], result["detail"])


def check_broken_chrome_override_fails(tmp):
    _set_env(CHROME_BINARY=str(Path(tmp) / "missing-chrome"))
    result = _task(tmp)._check_chrome_chromium()
    check("broken_chrome_override_fails", result["status"] == FAIL, result["detail"])


def _expected_fallback_driver(tmp):
    """Put a fake chromedriver on PATH; return what WebDriverManager.py's default
    lookup should pick (its hardcoded /usr/bin/chromedriver still wins on hosts
    that have one, so the expectation is exact either way)."""
    fake = _fake_binary(tmp, "chromedriver", "ChromeDriver 154.0.8037.98 (abc)")
    if os.path.isfile("/usr/bin/chromedriver") and os.access("/usr/bin/chromedriver", os.X_OK):
        return "/usr/bin/chromedriver"
    return fake


def check_broken_driver_override_warns_with_fallback(tmp):
    fallback = _fake_binary(tmp, "chromedriver", "ChromeDriver 154.0.8037.98 (abc)")
    _set_env(CHROMEDRIVER_PATH=str(Path(tmp) / "missing-driver"), PATH=tmp)
    result = _task(tmp)._check_chromedriver()
    check(
        "broken_driver_override_warns_with_fallback",
        result["status"] == WARN and fallback in result["detail"],
        result["detail"],
    )


def check_broken_driver_override_without_fallback_fails(tmp):
    _set_env(CHROMEDRIVER_PATH=str(Path(tmp) / "missing-driver"), PATH=tmp)
    task = _task(tmp)
    task._webdriver_manager_available = lambda: False
    result = task._check_chromedriver()
    check("broken_driver_override_without_fallback_fails", result["status"] == FAIL, result["detail"])


def check_driver_override_passes(tmp):
    driver = _fake_binary(tmp, "chromedriver", "ChromeDriver 154.0.8037.92 (abc)")
    _set_env(CHROMEDRIVER_PATH=driver)
    result = _task(tmp)._check_chromedriver()
    check("driver_override_passes", result["status"] == PASS and driver in result["detail"], result["detail"])


def check_version_mismatch_with_browser_override_fails(tmp):
    chrome = _fake_binary(tmp, "chrome-155", "Google Chrome 155.0.1.2")
    driver = _fake_binary(tmp, "driver-154", "ChromeDriver 154.0.8037.92 (abc)")
    _set_env(CHROME_BINARY=chrome, CHROMEDRIVER_PATH=driver)
    result = _task(tmp)._check_chrome_driver_versions()
    check(
        "version_mismatch_with_browser_override_fails",
        result is not None and result["status"] == FAIL,
        result and result["detail"],
    )


def check_version_mismatch_with_guessed_browser_warns(tmp):
    chrome = _fake_binary(tmp, "chrome-155", "Google Chrome 155.0.1.2")
    driver = _fake_binary(tmp, "driver-154", "ChromeDriver 154.0.8037.92 (abc)")
    _set_env(CHROMEDRIVER_PATH=driver)
    task = _task(tmp)
    task._resolve_chrome_binary = lambda: chrome  # stands in for the candidate-path search
    result = task._check_chrome_driver_versions()
    check(
        "version_mismatch_with_guessed_browser_warns",
        result is not None and result["status"] == WARN,
        result and result["detail"],
    )


def check_browser_override_with_webdriver_manager_driver_warns(tmp):
    chrome = _fake_binary(tmp, "cft-chrome", "Google Chrome for Testing 154.0.8037.92")
    _set_env(CHROME_BINARY=chrome, PATH=tmp)  # no driver override, none on PATH
    result = _task(tmp)._check_chrome_driver_versions()
    check(
        "browser_override_with_webdriver_manager_driver_warns",
        result is not None and result["status"] == WARN and "CHROMEDRIVER_PATH" in result["detail"],
        result and result["detail"],
    )


def check_stock_browser_with_webdriver_manager_driver_skips(tmp):
    _set_env(PATH=tmp)
    task = _task(tmp)
    task._resolve_chrome_binary = lambda: _fake_binary(tmp, "chrome", "Google Chrome 154.0.8037.98")
    result = task._check_chrome_driver_versions()
    check("stock_browser_with_webdriver_manager_driver_skips", result is None, f"got {result!r}")


def check_version_match_passes(tmp):
    chrome = _fake_binary(tmp, "chrome-154", "Google Chrome for Testing 154.0.8037.92")
    driver = _fake_binary(tmp, "driver-154b", "ChromeDriver 154.0.8037.92 (abc)")
    _set_env(CHROME_BINARY=chrome, CHROMEDRIVER_PATH=driver)
    result = _task(tmp)._check_chrome_driver_versions()
    check("version_match_passes", result is not None and result["status"] == PASS, result and result["detail"])


def check_webdriver_manager_honours_override(tmp):
    driver = _fake_binary(tmp, "chromedriver-override", "ChromeDriver 154.0.8037.92 (abc)")
    _set_env(CHROMEDRIVER_PATH=driver)
    got = WebDriverManager.get_chrome_driver_path()
    check("webdriver_manager_honours_override", got == driver, f"got {got!r}")


def check_webdriver_manager_ignores_broken_override(tmp):
    fallback = _expected_fallback_driver(tmp)
    _set_env(CHROMEDRIVER_PATH=str(Path(tmp) / "missing-driver"), PATH=tmp)
    got = WebDriverManager.get_chrome_driver_path()
    check("webdriver_manager_ignores_broken_override", got == fallback, f"got {got!r}, want {fallback!r}")


def main():
    saved = {var: os.environ.get(var) for var in ENV_VARS}
    checks = (
        check_chrome_binary_override_wins,
        check_chrome_bin_is_fallback,
        check_broken_chrome_override_fails,
        check_broken_driver_override_warns_with_fallback,
        check_broken_driver_override_without_fallback_fails,
        check_driver_override_passes,
        check_version_mismatch_with_browser_override_fails,
        check_version_mismatch_with_guessed_browser_warns,
        check_browser_override_with_webdriver_manager_driver_warns,
        check_stock_browser_with_webdriver_manager_driver_skips,
        check_version_match_passes,
        check_webdriver_manager_honours_override,
        check_webdriver_manager_ignores_broken_override,
    )
    try:
        for fn in checks:
            with tempfile.TemporaryDirectory() as tmp:
                try:
                    fn(tmp)
                except Exception as exc:  # a check that blows up is a failure, not a crash
                    check(fn.__name__.replace("check_", ""), False, f"check raised {type(exc).__name__}: {exc}")
    finally:
        for var, value in saved.items():
            if value is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = value

    width = max(len(n) for n, _, _ in RESULTS)
    failed = 0
    print("validate_setup Chrome override invariants\n" + "=" * (width + 60))
    for name, ok, detail in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'}  {name:<{width}}  {detail}")
        failed += 0 if ok else 1
    print("=" * (width + 60))
    print(f"{len(RESULTS) - failed}/{len(RESULTS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
