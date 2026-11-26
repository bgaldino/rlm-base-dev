# Setup UI — Shadow DOM and Lightning Web Security

Read this when editing **Robot setup tests** under `robot/rlm-base/tests/setup/` or shared resources that drive **Setup**, **App Builder–less** toggles, or **LWC controls** with no REST equivalent.

## Relationship to `patterns.md`

- **Code samples and keyword tables** — `.cursor/skills/robot-testing/patterns.md` (shadow helpers, combobox flow, CCI task wiring).
- **This file** — agent-facing **decisions and pitfalls** so you do not re-learn them from failed runs.

## Quick rules

1. **Shadow DOM** — Standard Selenium/XPath does not cross into LWC shadow roots. Use the repo’s **recursive `findEl` / `findAll` JavaScript** patterns from `patterns.md`, not generic `Click Element` on inner nodes.
2. **`composed: true` on events** — When dispatching events that must cross shadow boundaries, use `composed: true` (see `patterns.md` and existing setup suites).
3. **No `//` in Robot `Execute JavaScript` blocks** — Robot joins continuation lines; `//` comments break the script. Use `/* */`.
4. **LWC inputs** — Do not use `Input Text` on Lightning inputs; use the **native setter** pattern documented in `patterns.md`.
5. **CRM Analytics** — As of **262**, the legacy `InsightsSetupSettings` Visualforce iframe page is **gone**. `enable_analytics_replication` (`AnalyticsSetupHelper.py` + `enable_analytics.robot`) now clicks **"Enable CRM Analytics"** on `/lightning/setup/InsightsSetupGettingStarted/home` — **no iframe switching**. `AnalyticsSetupHelper.py` finds and clicks it with in-page JavaScript that walks shadow roots (see rule 1), polls the page until it shows **"Launch CRM Analytics"** (already on) or the Enable button has held for `ENABLE_SETTLE_S` (3 s), and confirms the click the same way. The settle matters: an org that already has CRM Analytics renders the Enable button for ~0.5-1 s while the page loads, then swaps in Launch (measured on every load, Chrome 157 and 158), so acting on the first Enable seen clicks a loading-state button. It uses **no WebDriver element lookups**: measured 2026-11-24 on a fresh 264 scratch org (Setup served from `*.my.salesforce-setup.com`) under ChromeDriver 158, the button is out of XPath's reach (`document.evaluate` finds none), WebDriver XPath lookups on Setup pages missed or raised `StaleElementReferenceException` (rule 11 has the cause), and `WebDriverWait` does not ignore that error, so the old XPath wait failed before its JavaScript fallback ran. `tests/test_analytics_setup_helper.py` pins this. Do not reintroduce frame-switch helpers when debugging this suite. Other Setup flows that historically used Visualforce iframes (Classic Setup pages still hosted in `<iframe>` shells) do still require frame switching; treat each on a case-by-case basis.
6. **Authentication** — Use `sf org open --url-only` with `self.org_config.username` in Python wrappers; navigate with `Go To Authenticated Page` / `Open Setup Page` (`SessionUrlGuard.py`) so the frontdoor URL never enters a Robot variable and session tokens never appear in `output.xml` or `log.html`.
7. **Retries** — Setup pages can be slow or flaky; follow **existing** timeout/save-staleness patterns in `SetupToggles.robot` and related resources instead of ad-hoc long `Sleep`.
8. **Forced "Change Your Password" on frontdoor login** — Some scratch org definitions (notably the TSO/trialforce-derived templates such as `tfid-cdo-rlm`) flag the admin user to **reset password at next login**. When that happens, `sf org open --url-only` (frontdoor) redirects to the **"Change Your Password"** page instead of the requested Setup page, so every toggle lookup fails on the wrong page (symptom: identical screenshots, `'change your password ...' does not contain 'log in'`). Two layers guard against this: (a) the `set_scratch_org_password` CCI task runs as **`prepare_core` step 2** (after `fix_scratch_org_identity`) (`when: org_config.scratch`) and clears the flag via `System.setPassword`; (b) `_Handle Change Password If Needed` in `SetupToggles.robot` completes the reset in-browser as a safety net (password in `${SCRATCH_NEW_PASSWORD}`, kept in sync with `scripts/apex/setScratchOrgPassword.apex`). If you see this page in a new suite, ensure it routes through `Open Setup Page` / `_Wait For Login If Needed` so both guards apply.

9. **Headless window size** — `Open Browser For Setup` ends with `Maximize Browser Window`, which in `--headless=new` Chrome shrinks the window from the `--window-size=1920,1080` option to the 800x600 default screen (viewport 800x457). Controls near a Setup page's right edge, such as a pill's remove button, then straddle the viewport and Selenium clicks on them fail with `ElementClickInterceptedException`. A suite that needs the full width calls `Set Window Size    1920    1080` after Suite Setup (as `configure_revenue_settings` does), or clicks with JavaScript.
10. **Match names exactly** — compare a pill or option to its target with equality (`normalize-space(.)='…'`), not `contains()`: a clone named `<name> Clone` otherwise passes for `<name>`.
11. **ChromeDriver 158+ and synthetic shadow** — Lightning loads LWC synthetic shadow, which replaces `window.ShadowRoot`; ChromeDriver 158+ checks reachability against a copy saved before that, so every element in a synthetic shadow tree reads as detached. A WebDriver XPath lookup whose matches include one, or a script that returns one, raises `StaleElementReferenceException`; CSS lookups never return those elements (LWC patches `querySelectorAll`). The browser-open keywords call `Allow Synthetic Shadow Element References` (`ChromeOptionsHelper.py`) to undo this; a new one must too. Measured 2026-11-26: stock Chrome 158 + driver 158 and Chrome for Testing 159 + driver 159 fail, Chrome 158 + driver 157 passes, and both 158 and 159 pass with the fix.
12. **Wait for the final Setup document** — In a new browser, a frontdoor login reaches a Setup page through my.salesforce.com and a complete, Aura-ready lightning.force.com page, then reloads it on `*.my.salesforce-setup.com` about 3.5 s later (first visit 9-14 s to a rendered control, later visits about 4 s). Anything clicked before the reload is lost, and a retry window that starts there can run out. `Open Setup Page` waits (`${SETUP_PAGE_SETTLE_TIMEOUT}`, 60 s) until the page is complete, Aura is ready and, for `/lightning/setup/` paths, it is on the Setup domain (`Current Page Is On Setup Domain`, `SessionUrlGuard.py`: the URL is read with logging off; page JS must not read `location.host`). Navigate through it rather than `_Open Target Page`.
13. **Record page actions** — The highlights-panel actions ribbon renders late (12.3 s on a new browser's first visit, 3.7 s later) and re-renders by replacing its buttons; related-list headers use the same `runtime_platform_actions-actions-ribbon` component for their "New" buttons. `Click Highlights Panel Action` (`E2ECommon.robot`) calls `Click Record Action` (`RecordActionHelper.py`), which scopes to the ribbon with a `highlights` ancestor, waits until its buttons keep the same nodes for 1.5 s, and clicks in the same JavaScript call that re-checks them (then the "Show more actions" menu; every current caller's action is in one of the two, so there is no page-wide fallback). An action not there yet is looked for again until the 60 s timeout, and a click whose script raised is never repeated. Do not reintroduce an XPath wait followed by a separate click.

## DO NOT

- **DO NOT** paste generic Stack Overflow Selenium for Lightning Setup — it will not cross shadow roots.
- **DO NOT** log org URLs at default log level during authentication.
- **DO NOT** add sleeps without checking whether an existing keyword already polls for readiness.

## Where to look in the repo

| Area | Location |
|------|----------|
| Shared toggle / checkbox keywords | `robot/rlm-base/resources/SetupToggles.robot` |
| Chrome / driver resolution | `robot/rlm-base/resources/WebDriverManager.py` |
| Analytics (Lightning Getting Started page, in-page JS shadow walk — VF iframe removed in 262+) | `robot/rlm-base/resources/AnalyticsSetupHelper.py`, `robot/rlm-base/tests/setup/enable_analytics.robot` |
| ChromeDriver 158+ synthetic shadow fix | `robot/rlm-base/resources/ChromeOptionsHelper.py` (`Allow Synthetic Shadow Element References`) |
| Record page actions (E2E) | `robot/rlm-base/resources/RecordActionHelper.py`, `Click Highlights Panel Action` in `E2ECommon.robot` |
| Variables (URLs, labels) | `robot/rlm-base/variables/SetupVariables.robot` |

After substantive changes, run `cci task run validate_setup` (no org) and exercise the relevant `configure_*` / `enable_*` task against a scratch org when possible.
