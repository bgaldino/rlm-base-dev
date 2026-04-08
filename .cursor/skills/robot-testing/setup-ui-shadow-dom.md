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
5. **VF / Classic iframe** — Some flows (e.g. CRM Analytics) use **Visualforce iframes**, not shadow DOM. Use **frame switch** helpers (see `AnalyticsSetupHelper.py`, `enable_analytics.robot`) — do not apply shadow traversal to iframe content.
6. **Authentication** — Use `sf org open --url-only` with `self.org_config.username` in Python wrappers; wrap URL logging with `Set Log Level NONE` so session tokens never appear in `log.html`.
7. **Retries** — Setup pages can be slow or flaky; follow **existing** timeout/save-staleness patterns in `SetupToggles.robot` and related resources instead of ad-hoc long `Sleep`.

## DO NOT

- **DO NOT** paste generic Stack Overflow Selenium for Lightning Setup — it will not cross shadow roots.
- **DO NOT** log org URLs at default log level during authentication.
- **DO NOT** add sleeps without checking whether an existing keyword already polls for readiness.

## Where to look in the repo

| Area | Location |
|------|----------|
| Shared toggle / checkbox keywords | `robot/rlm-base/resources/SetupToggles.robot` |
| Chrome / driver resolution | `robot/rlm-base/resources/WebDriverManager.py` |
| Analytics (VF iframe) | `robot/rlm-base/resources/AnalyticsSetupHelper.py`, `tests/setup/enable_analytics.robot` |
| Variables (URLs, labels) | `robot/rlm-base/variables/SetupVariables.robot` |

After substantive changes, run `cci task run validate_setup` (no org) and exercise the relevant `configure_*` / `enable_*` task against a scratch org when possible.
