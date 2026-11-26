#!/usr/bin/env python3
"""Offline tests for RecordActionHelper.py (``Click Highlights Panel Action``, pack 431).

A record page's actions ribbon renders late on a new browser's first visit and can
re-render, replacing its buttons. The helper must click only once the ribbon has kept the
same nodes for its settle window, re-check them in the same call that clicks, settle again
when they changed, open "Show more actions" only once, and fail naming what it saw.

Robot Framework is stubbed in ``sys.modules``; the driver is a fake that answers the
helper's two scripts from a scripted sequence of page states on a fake clock, so no
browser is started and nothing beyond the stdlib is needed.

Run:  python tests/test_record_action_helper.py
"""
import ast
import importlib.util
import json
import os
import sys
import types

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(_HERE, "..", "robot", "rlm-base", "resources", "RecordActionHelper.py")

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


class _FakeBuiltIn:
    driver = None

    def get_library_instance(self, name):
        return types.SimpleNamespace(driver=_FakeBuiltIn.driver)


def _install_stubs():
    robot = types.ModuleType("robot")
    api = types.ModuleType("robot.api")
    api.logger = types.SimpleNamespace(info=lambda *a, **k: None, warn=lambda *a, **k: None)
    deco = types.ModuleType("robot.api.deco")
    deco.keyword = lambda *a, **k: (a[0] if a and callable(a[0]) else (lambda f: f))
    libraries = types.ModuleType("robot.libraries")
    builtin = types.ModuleType("robot.libraries.BuiltIn")
    builtin.BuiltIn = _FakeBuiltIn
    utils = types.ModuleType("robot.utils")

    def timestr_to_secs(value):  # the subset of Robot's parser the helper needs
        text = str(value).strip()
        return float(text[:-1]) if text.endswith("s") else float(text)

    utils.timestr_to_secs = timestr_to_secs
    sys.modules.update({"robot": robot, "robot.api": api, "robot.api.deco": deco, "robot.utils": utils,
                        "robot.libraries": libraries, "robot.libraries.BuiltIn": builtin})


_install_stubs()
_spec = importlib.util.spec_from_file_location("RecordActionHelper", _SRC)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


class Clock:
    def __init__(self):
        self.t = 0.0

    def now(self):
        return self.t

    def sleep(self, s):
        self.t += s


def ribbon(*labels, more=False, gen=1):
    """A page state: visible ribbon buttons (node generation ``gen``) and no open menu."""
    names = list(labels) + (["Show more actions"] if more else [])
    return {"ribbon": names, "more": more,
            "ribbonSig": "|".join(f"{gen}.{i}:{n}" for i, n in enumerate(names)), "menu": [], "menuSig": ""}


def with_menu(state, *items, gen=1):
    s = dict(state)
    s["menu"] = list(items)
    s["menuSig"] = "|".join(f"m{gen}.{i}:{n}" for i, n in enumerate(items))
    return s


EMPTY = {"ribbon": [], "more": False, "ribbonSig": "", "menu": [], "menuSig": ""}


class FakeDriver:
    """``timeline`` is a list of (from_time, state) pairs: the page shows ``state`` from
    that fake time on. A state may be an Exception instance (the script raises).
    ``clicks`` maps a click kind to a list of results returned in order (default
    'clicked'); a click may also switch the page to a new timeline entry."""

    def __init__(self, clock, timeline, clicks=None, on_click=None):
        self.clock, self.timeline = clock, timeline
        self.clicks = {k: list(v) for k, v in (clicks or {}).items()}
        self.on_click = on_click or {}
        self.click_log = []

    def _current(self):
        """The entry with the latest start time not after now (ties: the later insertion)."""
        state, start = None, None
        for t, s in self.timeline:
            if self.clock.t >= t and (start is None or t >= start):
                state, start = s, t
        return state

    def execute_script(self, script, *args):
        if script is m._STATE_JS:
            state = self._current()
            if isinstance(state, Exception):
                raise state
            return json.dumps(state)
        assert script is m._CLICK_JS, "unexpected script"
        kind, label, expected = args
        self.click_log.append((round(self.clock.t, 2), kind, label, expected))
        results = self.clicks.get(kind)
        result = results.pop(0) if results else "clicked"
        if isinstance(result, Exception):
            raise result
        current = self._current()
        if result == "clicked" and kind == "more" and current and current["menu"]:
            closed = dict(current, menu=[], menuSig="")  # clicking it again closes the menu
            self.timeline.append((self.clock.t, closed))
        elif result == "clicked" and kind in self.on_click:
            self.timeline.append((self.clock.t, self.on_click[kind]))
        return result


def run(timeline, label="Reset Account", clicks=None, on_click=None, timeout=None):
    clock = Clock()
    driver = FakeDriver(clock, timeline, clicks, on_click)
    _FakeBuiltIn.driver = driver
    helper = m.RecordActionHelper(clock=clock.now, sleep=clock.sleep)
    try:
        result = helper.click_record_action(label, timeout)
        error = None
    except AssertionError as exc:
        result, error = None, str(exc)
    return result, error, driver, clock


def test_late_ribbon_is_clicked_after_settle():
    r = ribbon("Edit", "Reset Account")
    result, error, d, _ = run([(0, EMPTY), (12.3, r)])
    check("late ribbon: clicked directly", result == "direct" and not error, f"{result} {error}")
    check("late ribbon: one click, with the settled signature",
          [c[1:] for c in d.click_log] == [("direct", "Reset Account", r["ribbonSig"])], d.click_log)
    check("late ribbon: not before the settle window",
          d.click_log and d.click_log[0][0] >= 12.3 + m.RecordActionHelper.SETTLE_S, d.click_log)


def test_rerender_restarts_settle_window():
    first, second = ribbon("Edit", "Reset Account", gen=1), ribbon("Edit", "Reset Account", gen=2)
    result, error, d, _ = run([(0, first), (1.0, second)])
    check("re-render: clicked", result == "direct", error)
    check("re-render: the click uses the new nodes' signature", d.click_log[0][3] == second["ribbonSig"], d.click_log)
    check("re-render: window restarted at the re-render",
          d.click_log[0][0] >= 1.0 + m.RecordActionHelper.SETTLE_S, d.click_log)


def test_changed_at_click_settles_again():
    r = ribbon("Edit", "Reset Account")
    result, error, d, _ = run([(0, r)], clicks={"direct": ["changed", "clicked"]})
    check("changed at click: settled again and clicked", result == "direct" and len(d.click_log) == 2,
          f"{result} {error} {d.click_log}")
    check("changed at click: second click waited a full window",
          d.click_log[1][0] - d.click_log[0][0] >= m.RecordActionHelper.SETTLE_S, d.click_log)


def test_overflow_menu_is_used_once():
    r = ribbon("Edit", "Delete", more=True)
    opened = with_menu(r, "Clone", "Create Order")
    result, error, d, _ = run([(0, r)], label="Create Order", on_click={"more": opened})
    check("overflow: clicked from the menu", result == "menu" and not error, f"{result} {error}")
    kinds = [c[1] for c in d.click_log]
    check("overflow: more once, then the menu item", kinds == ["more", "menu"], d.click_log)
    check("overflow: the menu item click uses the menu signature", d.click_log[-1][3] == opened["menuSig"], d.click_log)


def test_menu_changed_at_click_does_not_reopen_menu():
    r = ribbon("Edit", more=True)
    opened = with_menu(r, "Create Order")
    result, error, d, _ = run([(0, r)], label="Create Order", on_click={"more": opened},
                              clicks={"menu": ["changed", "clicked"]})
    kinds = [c[1] for c in d.click_log]
    check("menu changed: settled the menu again without clicking more", kinds == ["more", "menu", "menu"]
          and result == "menu", f"{kinds} {result} {error}")


def test_label_missing_from_menu_fails_naming_it():
    r = ribbon("Edit", more=True)
    result, error, d, _ = run([(0, r)], label="Activate", on_click={"more": with_menu(r, "Clone", "Delete")}, timeout=10)
    check("menu lacks label: fails at the deadline naming ribbon and menu",
          result is None and error and "['Clone', 'Delete']" in error and "Activate" in error, error)
    kinds = [c[1] for c in d.click_log]
    check("menu lacks label: the menu is closed again before the next look",
          kinds[:2] == ["more", "more"], kinds[:6])


def test_label_that_moves_into_the_menu_later_is_found():
    first = ribbon("Edit", more=True)
    later = ribbon("Edit", more=True, gen=2)
    menus = {"n": 0}

    class MovingDriver(FakeDriver):
        def execute_script(self, script, *args):
            if script is m._CLICK_JS and args[0] == "more" and not self._current()["menu"]:
                menus["n"] += 1
                items = ("Clone",) if menus["n"] == 1 else ("Clone", "Create Order")
                base = first if menus["n"] == 1 else later
                self.click_log.append((round(self.clock.t, 2), "more", args[1], args[2]))
                self.timeline.append((self.clock.t, with_menu(base, *items, gen=menus["n"])))
                return "clicked"
            return super().execute_script(script, *args)

    clock = Clock()
    d = MovingDriver(clock, [(0, first), (4.0, later)])
    _FakeBuiltIn.driver = d
    helper = m.RecordActionHelper(clock=clock.now, sleep=clock.sleep)
    result = helper.click_record_action("Create Order")
    check("action added to the menu after a first look: found on a later look", result == "menu",
          [c[1] for c in d.click_log])


def test_label_added_to_ribbon_after_settle_is_clicked():
    result, error, d, _ = run([(0, ribbon("Edit")), (5.0, ribbon("Edit", "Reset Account", gen=2))])
    check("action added to a settled ribbon later: clicked directly", result == "direct", f"{result} {error}")


def test_ribbon_rerender_after_more_click_retries():
    first, second = ribbon("Edit", more=True, gen=1), ribbon("Edit", more=True, gen=2)
    opened = with_menu(second, "New Contract", gen=2)
    clicks = {"n": 0}

    class RerenderDriver(FakeDriver):
        def execute_script(self, script, *args):
            if script is m._CLICK_JS and args[0] == "more" and not self._current()["menu"]:
                clicks["n"] += 1
                self.click_log.append((round(self.clock.t, 2), "more", args[1], args[2]))
                # First click: the ribbon re-renders and the menu never shows. Second: it opens.
                self.timeline.append((self.clock.t, second if clicks["n"] == 1 else opened))
                return "clicked"
            return super().execute_script(script, *args)

    clock = Clock()
    d = RerenderDriver(clock, [(0, first)])
    _FakeBuiltIn.driver = d
    helper = m.RecordActionHelper(clock=clock.now, sleep=clock.sleep)
    try:
        result, error = helper.click_record_action("New Contract"), None
    except AssertionError as exc:
        result, error = None, str(exc)
    check("ribbon re-rendered after the more click: looked again and clicked from the menu",
          result == "menu" and clicks["n"] == 2, f"{result} {error} {d.click_log}")


def test_lost_more_click_is_retried():
    r = ribbon("Edit", more=True)
    opened = with_menu(r, "Reset Account")
    clicks = {"n": 0}

    class LosesFirstClick(FakeDriver):
        def execute_script(self, script, *args):
            if script is m._CLICK_JS and args[0] == "more" and not self._current()["menu"]:
                clicks["n"] += 1
                self.click_log.append((round(self.clock.t, 2), "more", args[1], args[2]))
                if clicks["n"] > 1:  # the first click lands before the handler is wired
                    self.timeline.append((self.clock.t, opened))
                return "clicked"
            return super().execute_script(script, *args)

    clock = Clock()
    d = LosesFirstClick(clock, [(0, r)])
    _FakeBuiltIn.driver = d
    helper = m.RecordActionHelper(clock=clock.now, sleep=clock.sleep)
    try:
        result, error = helper.click_record_action("Reset Account"), None
    except AssertionError as exc:
        result, error = None, str(exc)
    check("lost 'Show more actions' click: retried within the deadline, then clicked from the menu",
          result == "menu" and clicks["n"] == 2, f"{result} {error} {d.click_log}")


def test_unknown_more_click_goes_on_to_the_menu():
    r = ribbon("Edit", more=True)
    opened = with_menu(r, "Reset Account")

    class RaisesAfterOpening(FakeDriver):
        def execute_script(self, script, *args):
            if script is m._CLICK_JS and args[0] == "more" and not self._current()["menu"]:
                self.click_log.append((round(self.clock.t, 2), "more", args[1], args[2]))
                self.timeline.append((self.clock.t, opened))
                raise RuntimeError("reply lost")
            return super().execute_script(script, *args)

    clock = Clock()
    d = RaisesAfterOpening(clock, [(0, r)])
    _FakeBuiltIn.driver = d
    result = m.RecordActionHelper(clock=clock.now, sleep=clock.sleep).click_record_action("Reset Account")
    check("'more' click with unknown outcome: menu read, not re-clicked",
          result == "menu" and [c[1] for c in d.click_log] == ["more", "menu"], d.click_log)


def test_dead_session_fails_at_once():
    class InvalidSessionIdException(Exception):
        pass

    clock = Clock()
    d = FakeDriver(clock, [(0, InvalidSessionIdException("gone"))])
    _FakeBuiltIn.driver = d
    try:
        m.RecordActionHelper(clock=clock.now, sleep=clock.sleep).click_record_action("Reset Account")
        raised = None
    except InvalidSessionIdException:
        raised = "dead"
    except AssertionError as exc:
        raised = str(exc)
    check("dead browser session: raised at once, not polled to the deadline",
          raised == "dead" and clock.t < 1, f"{raised} t={clock.t}")


def test_dead_session_at_click_is_raised():
    class NoSuchWindowException(Exception):
        pass

    r = ribbon("Create Order")
    try:
        result, error, d, _ = run([(0, r)], label="Create Order", clicks={"direct": [NoSuchWindowException("closed")]})
        raised = f"returned {result}"
    except NoSuchWindowException:
        raised = "dead"
    check("dead browser session at the click: raised, not reported as clicked", raised == "dead", raised)


def test_menu_that_never_opens_fails():
    r = ribbon("Edit", more=True)
    result, error, d, _ = run([(0, r)], label="Activate", timeout=40)
    check("menu never opens: fails naming it", result is None and error and "opened no menu" in error, error)


def test_ribbon_never_settles_fails_without_click():
    result, error, d, clock = run([(0, EMPTY)], timeout=5)
    check("no ribbon: fails without clicking", result is None and not d.click_log
          and "never settled" in (error or ""), f"{error} {d.click_log}")
    check("no ribbon: gives up at the timeout", clock.t <= 5 + m.RecordActionHelper.POLL_S + 1e-9, clock.t)


def test_ribbon_that_keeps_changing_never_settles():
    timeline = [(i * 0.5, ribbon("Edit", "Reset Account", gen=i)) for i in range(40)]
    result, error, d, _ = run(timeline, timeout=10)
    check("flapping ribbon: never clicked, fails", result is None and not d.click_log,
          f"{error} {d.click_log}")


def test_script_errors_count_as_not_ready():
    r = ribbon("Reset Account")
    result, error, d, _ = run([(0, RuntimeError("document unloaded")), (2.0, r)])
    check("script errors mid-navigation: retried, then clicked", result == "direct"
          and d.click_log[0][0] >= 2.0 + m.RecordActionHelper.SETTLE_S, f"{result} {error} {d.click_log}")


def test_no_menu_and_label_missing_fails_naming_the_ribbon():
    result, error, d, _ = run([(0, ribbon("Edit"))], label="Activate", timeout=5)
    check("no menu, label missing: fails at the deadline naming the ribbon, no click",
          result is None and "['Edit']" in (error or "") and not d.click_log, error)


def test_deadline_during_menu_settle_keeps_last_full_look():
    r = ribbon("Edit", more=True)
    # Ribbon settles at 1.5 s, menu at 3.0 (closed again), ribbon at 4.5; the second menu
    # settle (4.5-6.0) is cut by the 5.5 s deadline, so the reason is the first full look.
    result, error, d, _ = run([(0, r)], label="Activate", on_click={"more": with_menu(r, "Clone")}, timeout=5.5)
    check("timeout during a menu settle: keeps the last full look's reason",
          result is None and "\"Show more actions\" menu ['Clone']" in (error or "")
          and "opened no menu" not in (error or ""), error)


def test_endless_changes_at_click_fail_at_deadline():
    r = ribbon("Reset Account")
    result, error, d, _ = run([(0, r)], clicks={"direct": ["changed"] * 50}, timeout=10)
    check("always changed at click: fails at the deadline saying so",
          result is None and "changed between settle and click" in (error or ""), error)


def test_click_with_unknown_outcome_is_not_repeated():
    r = ribbon("Create Order")
    result, error, d, _ = run([(0, r)], label="Create Order", clicks={"direct": [RuntimeError("alert open")]})
    check("click script raised: reported as done, not clicked again",
          result == "direct" and len(d.click_log) == 1, f"{result} {error} {d.click_log}")


def test_robot_time_string_timeout():
    result, error, d, clock = run([(0, EMPTY)], timeout="3s")
    check("timeout accepts a Robot time string", result is None and clock.t <= 3 + m.RecordActionHelper.POLL_S + 1e-9,
          f"{error} {clock.t}")


def test_never_uses_webdriver_element_lookups():
    tree = ast.parse(open(_SRC, encoding="utf-8").read())
    names = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    names |= {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    for banned in ("find_element", "find_elements", "WebDriverWait", "By"):
        check(f"helper code does not use {banned}", banned not in names)
    check("click script re-checks the signature before clicking",
          "if (sig !== expected) return 'changed';" in m._CLICK_JS)


def main():
    for test in (
        test_late_ribbon_is_clicked_after_settle,
        test_rerender_restarts_settle_window,
        test_changed_at_click_settles_again,
        test_overflow_menu_is_used_once,
        test_menu_changed_at_click_does_not_reopen_menu,
        test_label_missing_from_menu_fails_naming_it,
        test_label_that_moves_into_the_menu_later_is_found,
        test_label_added_to_ribbon_after_settle_is_clicked,
        test_ribbon_rerender_after_more_click_retries,
        test_lost_more_click_is_retried,
        test_unknown_more_click_goes_on_to_the_menu,
        test_dead_session_fails_at_once,
        test_dead_session_at_click_is_raised,
        test_menu_that_never_opens_fails,
        test_ribbon_never_settles_fails_without_click,
        test_ribbon_that_keeps_changing_never_settles,
        test_script_errors_count_as_not_ready,
        test_no_menu_and_label_missing_fails_naming_the_ribbon,
        test_deadline_during_menu_settle_keeps_last_full_look,
        test_endless_changes_at_click_fail_at_deadline,
        test_click_with_unknown_outcome_is_not_repeated,
        test_robot_time_string_timeout,
        test_never_uses_webdriver_element_lookups,
    ):
        test()
    print(f"\n{_PASS} passed, {_FAIL} failed.")
    return 1 if _FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
