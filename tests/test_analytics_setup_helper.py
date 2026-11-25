#!/usr/bin/env python3
"""Offline tests for AnalyticsSetupHelper.py (enable CRM Analytics on Getting Started).

On Release 264 orgs Lightning Setup is served from ``*.my.salesforce-setup.com`` and the
Getting Started content is not reachable by XPath: ``document.evaluate`` finds no button
there, and under Chrome/ChromeDriver 158 a WebDriver XPath lookup on Setup pages either
misses or raises ``StaleElementReferenceException``. ``WebDriverWait`` ignores only
``NoSuchElementException``, so the helper's old XPath wait aborted on the stale error before
its shadow-DOM JavaScript fallback ran, and ``enable_analytics.robot`` failed on every fresh
org. These cases pin the replacement: the helper finds and clicks the button with in-page
JavaScript only, polls for it, and reads the outcome from the page rather than an element
handle.

Selenium and Robot Framework are stubbed in ``sys.modules`` before the library loads, and
the driver is a fake that answers the helper's scripts, so no browser is started and
nothing beyond the stdlib is needed.

Run:  python tests/test_analytics_setup_helper.py
"""
import ast
import importlib.util
import os
import sys
import types

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(_HERE, "..", "robot", "rlm-base", "resources", "AnalyticsSetupHelper.py")

_PASS = 0
_FAIL = 0


def check(name, ok, detail=""):
    global _PASS, _FAIL
    if ok:
        _PASS += 1
        print(f"  PASS  {name}")
    else:
        _FAIL += 1
        print(f"  FAIL  {name}  {detail}")


# Same hierarchy as selenium.common.exceptions: both subclass WebDriverException.
class WebDriverException(Exception):
    pass


class StaleElementReferenceException(WebDriverException):
    pass


class TimeoutException(WebDriverException):
    pass


_LOG = []


class _FakeBuiltIn:
    driver = None

    def log(self, msg, level="INFO"):
        _LOG.append((level, msg))

    def get_library_instance(self, name):
        return types.SimpleNamespace(driver=_FakeBuiltIn.driver)


def _install_stubs():
    selenium = types.ModuleType("selenium")
    common = types.ModuleType("selenium.common")
    exceptions = types.ModuleType("selenium.common.exceptions")
    exceptions.StaleElementReferenceException = StaleElementReferenceException
    exceptions.WebDriverException = WebDriverException
    exceptions.TimeoutException = TimeoutException
    robot = types.ModuleType("robot")
    api = types.ModuleType("robot.api")
    deco = types.ModuleType("robot.api.deco")
    deco.keyword = lambda *a, **k: (a[0] if a and callable(a[0]) else (lambda f: f))
    libraries = types.ModuleType("robot.libraries")
    builtin = types.ModuleType("robot.libraries.BuiltIn")
    builtin.BuiltIn = _FakeBuiltIn
    sys.modules.update({
        "selenium": selenium, "selenium.common": common,
        "selenium.common.exceptions": exceptions,
        "robot": robot, "robot.api": api, "robot.api.deco": deco,
        "robot.libraries": libraries, "robot.libraries.BuiltIn": builtin,
    })


_install_stubs()
_spec = importlib.util.spec_from_file_location("AnalyticsSetupHelper", _SRC)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


class FakeDriver:
    """Answers the helper's two scripts from a scripted sequence of page states.

    ``states`` is consumed one entry per state read: "enable" (the Enable button is on the
    page), "launch" (CRM Analytics is on), "none" (neither yet), or an exception instance to
    raise. The last entry repeats. Clicking moves the page to ``after_click``.
    WebDriver element lookups always raise, the way they do on 264 Setup under Chrome 158,
    so any use of them fails the test.
    """

    def __init__(self, states, after_click="launch", click_result="clicked", click_lands=False):
        self.states = list(states)
        self.after_click = after_click
        self.click_result = click_result
        self.click_lands = click_lands  # with an exception click_result: did the click happen first
        self.clicks = 0
        self.click_times = []
        self.switched_default = 0
        self.switch_to = types.SimpleNamespace(default_content=self._default_content)

    def _default_content(self):
        self.switched_default += 1

    def _next_state(self):
        state = self.states[0] if len(self.states) == 1 else self.states.pop(0)
        if isinstance(state, Exception):
            raise state
        return state

    def execute_script(self, script, *args):
        if script is m._PAGE_STATE_JS:
            return self._next_state()
        if script is m._CLICK_ENABLE_JS:
            if isinstance(self.click_result, Exception):
                if self.click_lands:
                    self.clicks += 1
                    self.click_times.append(CLOCK.t)
                    self.states = [self.after_click]
                raise self.click_result
            if self.click_result == "clicked":
                self.clicks += 1
                self.click_times.append(CLOCK.t)
                self.states = [self.after_click]
            return self.click_result
        raise AssertionError("unexpected script")

    def find_element(self, *a, **k):
        raise StaleElementReferenceException("stale element not found in the current frame")

    find_elements = find_element


class FakeClock:
    """Stands in for the helper's ``time`` module: sleep() advances monotonic()."""

    def __init__(self):
        self.t = 0.0

    def monotonic(self):
        return self.t

    def sleep(self, seconds):
        self.t += seconds


CLOCK = FakeClock()


def _run(driver, **overrides):
    _LOG.clear()
    _FakeBuiltIn.driver = driver
    CLOCK.t = 0.0
    lib = m.AnalyticsSetupHelper()
    lib.POLL_S = 0.25
    for k, v in overrides.items():
        setattr(lib, k, v)
    original = m.time
    m.time = types.SimpleNamespace(monotonic=CLOCK.monotonic, sleep=CLOCK.sleep)
    try:
        return lib.enable_crm_analytics_via_getting_started_page()
    finally:
        m.time = original


def test_clicks_enable_button_without_webdriver_lookups():
    d = FakeDriver(["enable"])
    result = _run(d)
    check("Enable button present: clicked via JS", result == "clicked", result)
    check("exactly one click", d.clicks == 1, d.clicks)


def test_waits_for_button_to_render():
    d = FakeDriver(["none", "none", "enable"])
    result = _run(d)
    check("button rendered late: still clicked", result == "clicked" and d.clicks == 1, (result, d.clicks))


def test_stale_and_script_errors_are_retried():
    d = FakeDriver([StaleElementReferenceException("x"), WebDriverException("navigating"), "enable"])
    result = _run(d)
    check("transient driver errors during the setup-domain hop are retried", result == "clicked", result)


def test_already_enabled_returns_without_click():
    d = FakeDriver(["launch"])
    result = _run(d)
    check("Launch CRM Analytics present: already_enabled", result == "already_enabled", result)
    check("no click when already enabled", d.clicks == 0, d.clicks)


def test_page_never_renders_raises():
    d = FakeDriver(["none"])
    try:
        result = _run(d, BUTTON_WAIT_S=0.05)
    except AssertionError as exc:
        check("neither button nor enabled marker: fails loudly",
              "Getting Started" in str(exc) and "held" in str(exc), str(exc))
    else:
        check("neither button nor enabled marker: fails loudly", False, f"returned {result!r}")


def test_click_without_confirmation_fails():
    d = FakeDriver(["enable"], after_click="enable")
    try:
        result = _run(d, POST_CLICK_WAIT_S=0.05)
    except AssertionError as exc:
        check("click not confirmed by the page: fails", "did not confirm" in str(exc), str(exc))
    else:
        check("click not confirmed by the page: fails", False, f"returned {result!r}")


def test_button_vanishes_before_click_is_rechecked():
    d = FakeDriver(["enable"], click_result="not_found")
    d_states_after = ["launch"]

    def execute_script(script, *args, _orig=d.execute_script):
        if script is m._CLICK_ENABLE_JS:
            d.states = list(d_states_after)
            return "not_found"
        return _orig(script, *args)

    d.execute_script = execute_script
    result = _run(d)
    check("button gone at click time and page shows enabled: already_enabled",
          result == "already_enabled" and d.clicks == 0, (result, d.clicks))


def test_click_misses_but_button_stays_raises():
    d = FakeDriver(["enable"], click_result="not_found")
    try:
        result = _run(d)
    except AssertionError as exc:
        check("JS click finds nothing but Enable is still there: fails naming the re-render",
              "re-rendered at click time" in str(exc) and d.clicks == 0, str(exc))
    else:
        check("JS click finds nothing but Enable is still there: fails naming the re-render",
              False, f"returned {result!r}")


def test_driver_error_after_the_click_landed_is_confirmed_by_the_page():
    d = FakeDriver(["enable"], click_result=WebDriverException("session hiccup"), click_lands=True)
    result = _run(d)
    check("driver errors after the JS click ran, page shows Launch: clicked",
          result == "clicked" and d.clicks == 1, (result, d.clicks))


def test_driver_error_with_no_click_fails_naming_the_error():
    d = FakeDriver(["enable"], click_result=WebDriverException("session hiccup"), click_lands=False)
    try:
        result = _run(d, POST_CLICK_WAIT_S=1)
    except AssertionError as exc:
        check("driver errors and the page never confirms: fails naming the driver error",
              "driver raised WebDriverException" in str(exc), str(exc))
    else:
        check("driver errors and the page never confirms: fails naming the driver error",
              False, f"returned {result!r}")


def test_transient_enable_on_enabled_org_is_not_clicked():
    # Measured on 264 (both Chrome 157 and 158): an org with CRM Analytics already on renders
    # "Enable CRM Analytics" for ~0.5-1 s while loading, then "Launch CRM Analytics".
    d = FakeDriver(["none", "enable", "enable", "enable", "launch"])
    result = _run(d)
    check("Enable shown briefly, then Launch: already_enabled", result == "already_enabled", result)
    check("no click on the loading-state Enable button", d.clicks == 0, d.clicks)


def test_enable_must_hold_for_the_settle_window():
    d = FakeDriver(["none", "enable"])
    lib_settle = m.AnalyticsSetupHelper.ENABLE_SETTLE_S
    result = _run(d)
    check("Enable that stays: clicked", result == "clicked" and d.clicks == 1, (result, d.clicks))
    first_enable = 0.25  # second read, one poll after the first
    check("click waits for the settle window after Enable first appears",
          d.click_times and d.click_times[0] >= first_enable + lib_settle, d.click_times)
    check("settle window outlasts the measured ~1 s transient", lib_settle >= 2.5, lib_settle)


def test_rerender_restarts_the_settle_window():
    d = FakeDriver(["enable", "enable", "none", "enable"])
    lib_settle = m.AnalyticsSetupHelper.ENABLE_SETTLE_S
    result = _run(d)
    check("Enable interrupted by a re-render: still clicked once it holds",
          result == "clicked" and d.clicks == 1, (result, d.clicks))
    restart = 0.75  # the read after the "none"
    check("settle window restarts after the re-render",
          d.click_times and d.click_times[0] >= restart + lib_settle, d.click_times)


def test_enable_appearing_near_the_deadline_still_settles():
    d = FakeDriver(["none"] * 4 + ["enable"])
    result = _run(d, BUTTON_WAIT_S=1)
    check("Enable first seen at the wait deadline: clicked after settling",
          result == "clicked" and d.clicks == 1, (result, d.clicks))
    first_enable = 1.0  # fifth read, at the deadline
    check("the deadline does not cut the settle short",
          d.click_times and d.click_times[0] >= first_enable + m.AnalyticsSetupHelper.ENABLE_SETTLE_S,
          d.click_times)


def test_never_uses_webdriver_element_lookups():
    # Code only: the module docstring names these APIs to explain why they are avoided.
    tree = ast.parse(open(_SRC, encoding="utf-8").read())
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.ImportFrom):
            names.add(node.module or "")
            names.update(a.name for a in node.names)
    for banned in ("WebDriverWait", "find_element", "find_elements", "By", "staleness_of",
                   "selenium.webdriver.support.ui", "selenium.webdriver.common.by"):
        check(f"helper code does not use {banned}", banned not in names)


def main():
    for test in (
        test_clicks_enable_button_without_webdriver_lookups,
        test_waits_for_button_to_render,
        test_stale_and_script_errors_are_retried,
        test_already_enabled_returns_without_click,
        test_page_never_renders_raises,
        test_click_without_confirmation_fails,
        test_button_vanishes_before_click_is_rechecked,
        test_click_misses_but_button_stays_raises,
        test_driver_error_after_the_click_landed_is_confirmed_by_the_page,
        test_driver_error_with_no_click_fails_naming_the_error,
        test_transient_enable_on_enabled_org_is_not_clicked,
        test_enable_must_hold_for_the_settle_window,
        test_rerender_restarts_the_settle_window,
        test_enable_appearing_near_the_deadline_still_settles,
        test_never_uses_webdriver_element_lookups,
    ):
        test()
    print(f"\n{_PASS} passed, {_FAIL} failed.")
    return 1 if _FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
