"""RecordActionHelper — clicks a record page action once the actions ribbon has settled.

A Lightning record page renders its highlights-panel actions ribbon
(``runtime_platform_actions-actions-ribbon`` under ``records-highlights2`` /
``records-lwc-highlights-panel``; related-list headers use the same component for their
"New" buttons, so only a ribbon with a ``highlights`` ancestor counts) late, and can
re-render it: on a new
browser's first visit the ribbon appeared 12.3 s after navigation, 3.7 s on later
visits (measured 2026-11-26, Release 264), and a re-render replaces its buttons with
new nodes. The old keyword waited a fixed 10 s for a WebDriver XPath match and then
clicked in a separate lookup, so it either timed out before a cold ribbon existed or
clicked a node the re-render had just replaced (pack 431).

Here every look at the page is one in-page JavaScript call that walks shadow roots:

1. Settle: the visible ribbon's buttons are tagged with a per-node token; the ribbon
   counts as settled once the same tokens (same nodes, same labels) have held for
   ``SETTLE_S``. Any change restarts the window.
2. Click: a second call re-reads the ribbon, and clicks only if its token signature
   still equals the settled one, in the same JavaScript turn, so the node clicked is
   the node that was checked. A changed signature goes back to step 1.
3. The action is the visible ribbon button whose label is the action label; else the
   ribbon's "Show more actions" menu is opened and its item is clicked the same way.
   The previous keyword's last resort (any visible page button with that label or
   ``name``) is gone: every caller's action is in the ribbon or its menu (measured
   2026-11-26: Reset Account and New Contract in the menu; New Opportunity, New Quote,
   Create Order and Activate in the ribbon).
4. Anything short of a click (an action in neither list, a menu that did not open or
   settle, a page that moved on) is looked at again until the timeout, since a settled
   ribbon can still add actions or move them into the menu (an open menu is closed
   first). A click whose script raised is never repeated (it may have run).

No WebDriver element handle is created, so ChromeDriver's stale-element check never
applies.
"""

import json
import time

from robot.api import logger
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn
from robot.utils import timestr_to_secs

# Collects the visible ribbon controls and the visible menu items, tagging each node with
# a token that survives as long as the node does. Returns JSON text so a test fake can
# return the same shape.
_SNAPSHOT_FN = """
function rlmWalk(root, out, depth) {
    if (depth > 14) return out;
    var all = root.querySelectorAll('*');
    for (var i = 0; i < all.length; i++) {
        out.push(all[i]);
        if (all[i].shadowRoot) rlmWalk(all[i].shadowRoot, out, depth + 1);
    }
    return out;
}
function rlmVisible(el) { return el.isConnected && el.getClientRects().length > 0; }
function rlmInHighlights(el) {
    var n = el;
    for (var k = 0; k < 80 && n; k++) {
        if (n.tagName && /highlights/i.test(n.tagName)) return true;
        var p = n.parentNode;
        n = !p ? null : (p.nodeType === 11 && p.host ? p.host : p);
    }
    return false;
}
function rlmLabel(el) {
    var text = (el.textContent || '').replace(/\\s+/g, ' ').trim();
    return text || el.getAttribute('title') || el.getAttribute('aria-label') || '';
}
function rlmToken(el) {
    if (!el.__rlmActionToken) {
        window.__rlmActionSeq = (window.__rlmActionSeq || 0) + 1;
        el.__rlmActionToken = window.__rlmActionSeq;
    }
    return el.__rlmActionToken;
}
function rlmSnapshot() {
    var els = rlmWalk(document, [], 0);
    var ribbon = [], menu = [];
    for (var i = 0; i < els.length; i++) {
        var el = els[i];
        if (el.tagName === 'RUNTIME_PLATFORM_ACTIONS-ACTIONS-RIBBON' && rlmVisible(el) && rlmInHighlights(el)) {
            var inside = rlmWalk(el.shadowRoot || el, [], 0);
            if (el.shadowRoot) inside = inside.concat(Array.prototype.slice.call(el.querySelectorAll('*')));
            for (var j = 0; j < inside.length; j++) {
                var c = inside[j];
                if (!rlmVisible(c)) continue;
                if (c.getAttribute('role') === 'menuitem') {
                    menu.push({el: c, label: rlmLabel(c), token: rlmToken(c)});
                } else if (c.tagName === 'BUTTON' || c.tagName === 'A') {
                    ribbon.push({el: c, label: rlmLabel(c), token: rlmToken(c),
                                 more: /^show more actions$|^more actions$/i.test(rlmLabel(c))
                                       || /more actions/i.test(c.getAttribute('title') || '')});
                }
            }
        }
    }
    var sig = function (list) { return list.map(function (x) { return x.token + ':' + x.label; }).join('|'); };
    return {ribbon: ribbon, menu: menu, ribbonSig: sig(ribbon), menuSig: sig(menu)};
}
"""

# arguments: none. Returns a JSON summary of what the page shows now.
_STATE_JS = "return (function () {" + _SNAPSHOT_FN + """
    var s = rlmSnapshot();
    return JSON.stringify({
        ribbon: s.ribbon.map(function (x) { return x.label; }),
        more: s.ribbon.some(function (x) { return x.more; }),
        ribbonSig: s.ribbonSig,
        menu: s.menu.map(function (x) { return x.label; }),
        menuSig: s.menuSig
    });
})();"""

# arguments: kind ('direct' | 'more' | 'menu'), label, expected signature.
# Clicks only if the signature of the list the click is taken from is unchanged.
# Returns 'clicked', 'changed' (the page moved on since the settle; settle again) or
# 'missing' (nothing with that label in that list).
_CLICK_JS = "return (function (kind, label, expected) {" + _SNAPSHOT_FN + """
    var s = rlmSnapshot();
    var list, sig;
    if (kind === 'menu') { list = s.menu; sig = s.menuSig; }
    else { list = s.ribbon; sig = s.ribbonSig; }
    if (sig !== expected) return 'changed';
    for (var i = 0; i < list.length; i++) {
        var x = list[i];
        var hit = kind === 'more' ? x.more : x.label === label;
        if (hit) { x.el.click(); return 'clicked'; }
    }
    return 'missing';
})(arguments[0], arguments[1], arguments[2]);"""


_NEVER_SETTLED = "the ribbon never settled"
# Selenium errors (by class name, so the module needs no selenium import) after which no
# later read can succeed.
_DEAD_SESSION_ERRORS = ("InvalidSessionIdException", "NoSuchWindowException")


class RecordActionHelper:
    """Keyword library: click a record page highlights-panel action once the ribbon settles."""

    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    # Longest wait for a settled ribbon after the page was opened. A cold first visit
    # rendered it at 12.3 s; this leaves room for a slow org.
    READY_TIMEOUT_S = 60
    # How long the ribbon (or the opened menu) must keep the same nodes and labels.
    SETTLE_S = 1.5
    MENU_TIMEOUT_S = 15
    POLL_S = 0.25

    def __init__(self, clock=time.monotonic, sleep=time.sleep):
        self._clock = clock
        self._sleep = sleep

    def _driver(self):
        return BuiltIn().get_library_instance("SeleniumLibrary").driver

    def _state(self, driver):
        try:
            return json.loads(driver.execute_script(_STATE_JS))
        except Exception as exc:  # noqa: BLE001 - mid-navigation script errors: read again
            if type(exc).__name__ in _DEAD_SESSION_ERRORS:
                raise  # the browser is gone: polling until the deadline cannot help
            return {"error": type(exc).__name__}

    def _wait_settled(self, driver, key, timeout, ready):
        """Poll until state[key] (a signature) has held for SETTLE_S with ``ready(state)`` true.

        Returns the settled state, or None at the deadline (with the last state seen in
        ``self.last_state``)."""
        deadline = self._clock() + timeout
        held_sig, held_since = None, None
        while True:
            state = self._state(driver)
            self.last_state = state
            now = self._clock()
            if "error" not in state and ready(state):
                sig = state[key]
                if sig != held_sig:
                    held_sig, held_since = sig, now
                elif now - held_since >= self.SETTLE_S:
                    return state
            else:
                held_sig, held_since = None, None
            if now >= deadline:
                return None
            self._sleep(self.POLL_S)

    def _click(self, driver, kind, label, expected):
        """Runs the click script. Returns 'clicked', 'changed', 'missing' or 'unknown'.

        'unknown' means the script raised: the click may already have run (an alert, or
        a navigation that dropped the reply), so the caller must not click again."""
        try:
            return driver.execute_script(_CLICK_JS, kind, label, expected)
        except Exception as exc:  # noqa: BLE001 - the outcome is unknown, never retried blindly
            if type(exc).__name__ in _DEAD_SESSION_ERRORS:
                raise  # the browser is gone, so the click never ran
            logger.warn(f'Click on "{label}" ({kind}) raised {type(exc).__name__}; its outcome is unknown.')
            return "unknown"

    @keyword("Click Record Action")
    def click_record_action(self, label, timeout=None):
        """Clicks the record page action ``label`` once the actions ribbon has settled.

        Looks in the ribbon, then in its "Show more actions" menu. Returns ``direct`` or
        ``menu``. An action missing from a settled ribbon and menu is looked for again (the
        ribbon can still add actions or move them into the menu) until ``timeout`` (a Robot
        time string or seconds, default 60 s); then the keyword fails naming what the
        ribbon and menu showed. A click whose script
        raised is not repeated: it is reported as done, with a warning, and the caller's
        next wait shows whether it took effect.
        """
        label = str(label)
        timeout = self.READY_TIMEOUT_S if timeout in (None, "") else timestr_to_secs(timeout)
        driver = self._driver()
        deadline = self._clock() + timeout
        self.last_state, last_reason = None, _NEVER_SETTLED
        while self._clock() < deadline:
            state = self._wait_settled(driver, "ribbonSig", deadline - self._clock(), lambda s: bool(s["ribbon"]))
            if state is None:
                break
            if label in state["ribbon"]:
                result = self._click(driver, "direct", label, state["ribbonSig"])
                if result in ("clicked", "unknown"):
                    logger.info(f'Clicked record action "{label}" in the actions ribbon ({result}).')
                    return "direct"
                last_reason = "the ribbon changed between settle and click"
                continue
            if not state["more"]:
                last_reason = f'not in ribbon {state["ribbon"]}, which has no "Show more actions" menu'
                self._sleep(self.POLL_S)
                continue
            found = self._from_menu(driver, label, state, deadline)
            if found == "menu":
                return "menu"
            if found == "menu_changed":
                last_reason = "the menu changed between settle and click"
            elif found == "ribbon_changed":
                last_reason = 'the ribbon changed before "Show more actions" was clicked'
            elif found == "no_menu":
                last_reason = f'"Show more actions" opened no menu that settled within {self.MENU_TIMEOUT_S}s'
            elif isinstance(found, list):
                last_reason = f'not in ribbon {state["ribbon"]} or "Show more actions" menu {found}'
            elif last_reason == _NEVER_SETTLED:
                last_reason = "the timeout came while the menu was settling"
            # Otherwise "deadline" cut the menu wait short: keep the reason from the last full look.
        raise AssertionError(
            f'Action "{label}" not clicked within {timeout:g}s: {last_reason} '
            f"(last seen: {self._describe(self.last_state)})."
        )

    def _from_menu(self, driver, label, state, deadline):
        """Opens "Show more actions" (unless it is already open), settles the menu and
        clicks ``label`` in it. Returns 'menu' (clicked), 'ribbon_changed' (the ribbon moved
        on before the click), 'menu_changed' (the menu kept changing between settle and
        click), 'no_menu' (none settled within MENU_TIMEOUT_S), 'deadline' (the overall
        timeout came first), or the settled menu's labels when ``label`` is not among them
        (the menu is closed again so the next look starts from the ribbon)."""
        if not state["menu"]:
            opened = self._click(driver, "more", label, state["ribbonSig"])
            if opened not in ("clicked", "unknown"):
                return "ribbon_changed"
        menu_deadline = min(deadline, self._clock() + self.MENU_TIMEOUT_S)
        while self._clock() < menu_deadline:
            menu = self._wait_settled(driver, "menuSig", menu_deadline - self._clock(), lambda s: bool(s["menu"]))
            if menu is None:
                return "deadline" if menu_deadline == deadline else "no_menu"
            if label not in menu["menu"]:
                self._click(driver, "more", label, menu["ribbonSig"])
                return menu["menu"]
            result = self._click(driver, "menu", label, menu["menuSig"])
            if result in ("clicked", "unknown"):
                logger.info(f'Clicked record action "{label}" in the "Show more actions" menu ({result}).')
                return "menu"
        return "deadline" if menu_deadline == deadline else "menu_changed"

    @staticmethod
    def _describe(state):
        if not state:
            return "nothing"
        if "error" in state:
            return f"script error {state['error']}"
        return f"ribbon {state.get('ribbon')}, menu {state.get('menu')}"
