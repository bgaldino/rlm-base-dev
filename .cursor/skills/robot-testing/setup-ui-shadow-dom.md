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
5. **CRM Analytics** — As of **262**, the legacy `InsightsSetupSettings` Visualforce iframe page is **gone**. `enable_analytics_replication` (`AnalyticsSetupHelper.py` + `enable_analytics.robot`) now clicks **"Enable CRM Analytics"** on `/lightning/setup/InsightsSetupGettingStarted/home` in the **main Lightning DOM** — **no iframe switching**. The button itself is wrapped in `lightning-button`, so `AnalyticsSetupHelper.py` still uses the standard recursive `shadowRoot` traversal (see rule 1) to find it — that's normal LWC shadow piercing, not iframe gymnastics. Do not reintroduce frame-switch helpers when debugging this suite. Other Setup flows that historically used Visualforce iframes (Classic Setup pages still hosted in `<iframe>` shells) do still require frame switching; treat each on a case-by-case basis.
6. **Authentication** — Use `sf org open --url-only` with `self.org_config.username` in Python wrappers; wrap URL logging with `Set Log Level NONE` so session tokens never appear in `log.html`.
7. **Retries** — Setup pages can be slow or flaky; follow **existing** timeout/save-staleness patterns in `SetupToggles.robot` and related resources instead of ad-hoc long `Sleep`.
8. **Forced "Change Your Password" on frontdoor login** — Some scratch org definitions (notably the TSO/trialforce-derived templates such as `tfid-cdo-rlm`) flag the admin user to **reset password at next login**. When that happens, `sf org open --url-only` (frontdoor) redirects to the **"Change Your Password"** page instead of the requested Setup page, so every toggle lookup fails on the wrong page (symptom: identical screenshots, `'change your password ...' does not contain 'log in'`). Two layers guard against this: (a) the `set_scratch_org_password` CCI task runs as **`prepare_core` step 1** (`when: org_config.scratch`) and clears the flag via `System.setPassword`; (b) `_Handle Change Password If Needed` in `SetupToggles.robot` completes the reset in-browser as a safety net (password in `${SCRATCH_NEW_PASSWORD}`, kept in sync with `scripts/apex/setScratchOrgPassword.apex`). If you see this page in a new suite, ensure it routes through `Open Setup Page` / `_Wait For Login If Needed` so both guards apply.

## DO NOT

- **DO NOT** paste generic Stack Overflow Selenium for Lightning Setup — it will not cross shadow roots.
- **DO NOT** log org URLs at default log level during authentication.
- **DO NOT** add sleeps without checking whether an existing keyword already polls for readiness.

## Where to look in the repo

| Area | Location |
|------|----------|
| Shared toggle / checkbox keywords | `robot/rlm-base/resources/SetupToggles.robot` |
| Chrome / driver resolution | `robot/rlm-base/resources/WebDriverManager.py` |
| Analytics (Lightning Getting Started page, main DOM — VF iframe removed in 262+) | `robot/rlm-base/resources/AnalyticsSetupHelper.py`, `robot/rlm-base/tests/setup/enable_analytics.robot` |
| Variables (URLs, labels) | `robot/rlm-base/variables/SetupVariables.robot` |

After substantive changes, run `cci task run validate_setup` (no org) and exercise the relevant `configure_*` / `enable_*` task against a scratch org when possible.
