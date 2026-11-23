---
name: robot-testing
description: >-
  Write, modify, and debug Robot Framework org-setup automation and end-to-end tests for
  Salesforce. Use for browser locators, LWC or shadow-DOM interactions, JavaScript
  keywords, Python task wrappers, and required live-org behavioral verification.
---

# Robot Framework Testing

Use this skill when writing, modifying, or debugging Robot Framework tests.

## Quick Rules

1. `tests/setup/` = **org configuration automation** (not tests). `tests/e2e/` = **functional tests**.
2. Setup tests run mid-flow to toggle settings with no API equivalent. E2E tests run after provisioning.
3. No `//` comments in JavaScript blocks — Robot joins continuation lines, breaking everything after `//`.
4. Use `composed: true` on dispatched events to cross shadow DOM boundaries.
5. Use `self.org_config.username` in Python wrappers for `sf org open -o`.
6. Gate E2E tests with `Skip If "${QB}" == "false"` on the relevant feature flag.
7. For Setup UI + shadow DOM vs iframe: read `setup-ui-shadow-dom.md` before adding new keywords (LWS, `composed`, VF frames).
8. **Live-org verification is mandatory** for any behavioral change to a `.robot` suite or its Python wrapper — `robot --dryrun` is syntax-only and does **not** prove UI/shadow-DOM logic works. See **DO NOT** and **Verification — dryrun is not enough** below.

## DO NOT

- **DO NOT** use `//` comments in Robot JavaScript — use `/* */` instead
- **DO NOT** use standard `input_text` for LWC inputs — use native setter pattern
- **DO NOT** put an authenticated (`sf org open --url-only`) URL in a Robot variable, keyword argument, return value or `Go To` — it carries a live session that lands in `output.xml`/`log.html`. Navigate with `Go To Authenticated Page` (`SessionUrlGuard.py`); see **Session URLs** below
- **DO NOT** commit a behavioral robot change (keywords, locators, `Execute JavaScript`/DOM logic, click targets, wait/assert flow) **or** its Python task wrapper as verified — or merge it — on `robot --dryrun` alone. Run the affected suite against a live scratch org first. Dryrun never launches a browser. Exempt: comment/`[Documentation]`-only edits, and resource files with no behavioral change.

## Session URLs — never in Robot results

`sf org open --url-only` prints a frontdoor URL (`secur/frontdoor.jsp?sid=...&otp=...`) that is a live login. Robot writes keyword arguments, return values, library log lines and **failure messages** into `output.xml`/`log.html`, and those files persist under `robot/rlm-base/results/`, `.harness/runs/*/robot_results/` and `.harness/tui-runs/*/robot_results/` (and may be uploaded as artifacts).

- The URL stays inside Python: `Go To Authenticated Page    ${ORG_ALIAS}    <setup path>` (`robot/rlm-base/resources/SessionUrlGuard.py`) fetches it, reads it from `sf org open --url-only --json` (`result.url`, 120 s timeout), calls `driver.get` once with the log level at `NONE` (restored in `finally`), and re-raises failures with the known URL, its `sid`/`otp` values and any other session URL redacted (the whole message is withheld if the pattern still matches; the pattern covers URL-encoded forms). `Open Setup Page`, `Open Revenue Settings Page`, `Navigate To App` and `Navigate To Record` all use it. The log shows the org alias and setup path only.
- Re-navigate by path (`_Open Target Page`), never by passing the URL around. Never add a keyword that reads the page URL: `Get Location(s)`, `Location Should ...`, `Wait Until Location ...`, `Log Location`, `Get Source`/`Log Source`, `Get/Add/Delete Cookie(s)`, `Switch/Close Window`, `Get Window Titles/Names/Identifiers/Handles`, and every keyword that finds an element by an `a`/`img`/`input` tag: `Click Link`/`Click Image`/`Click Button`, `Mouse Down On Link/Image`, `Page Should (Not) Contain Link/Image/Button/Checkbox/Radio Button/Textfield`, `Select/Unselect Checkbox`, `Checkbox Should (Not) Be Selected`, `Textfield Should Contain`, `Textfield Value Should Be` (with an unprefixed locator SeleniumLibrary's element finder reads `driver.current_url` for those tags, and selenium logs it at DEBUG; use `Click Element` or similar with an `id:`/`css:`/`xpath:` locator instead), or JS `location.href/search/hash`, `document.URL`: the page URL can still be a frontdoor URL mid-login. Read it through `Get Record Id From Current Url` / `Current Url Should Be Record Page`, which read with logging off and report the path only. `tests/test_robot_session_url_logging.py` fails on any of those (its `FORBIDDEN` regex, over `robot/` and `tasks/`; `window.location.pathname` is allowed), on `Go To` with a variable other than the explicit `${url}`, on `sf org open` with `--url-only` or `-r` outside the guard, and on a committed org host. The list covers the installed SeleniumLibrary's keywords that read the URL; it is name based, so the scanner on live results remains the backstop.
- Why not just `Set Log Level NONE` in the suite: a failed `Go To` puts the URL in the failure text at any level, the level stays `NONE` if the keyword fails before restoring it, and a URL passed to a helper keyword is logged as that keyword's argument. (Measured with Robot 7.5.)
- `REVENUE_SETTINGS_URL` has no default (no committed org host): pass it only for a run without `ORG_ALIAS`. An explicit `url=` argument or `REVENUE_SETTINGS_URL` is logged as given: it must be a plain page URL, never a frontdoor/`sid=`/`otp=` one.
- Check: `python tests/test_robot_session_url_logging.py` (runs the real navigation keywords against a fake `sf`, no org; gated by `pr_gate.py`) and `python scripts/ai/check_robot_session_urls.py [results dir ...]`, which decodes `log.html`'s embedded string tables (each `.concat` chunk with `raw_decode`; an undecodable chunk is a finding) and split-log `.js` files. The test also runs mutation cases (protection switched off in a copy of the tree) that the scanner must flag, so a green run cannot be a silent one. Run the scanner on the results of every live run you cite as verification. Failure screenshots are viewport captures and show no URL bar.

## Verification — dryrun is not enough

`robot --dryrun` resolves keyword names, argument counts, and syntax. It does
**not** launch a browser, load a Salesforce page, or execute `Execute JavaScript`
blocks. A wrong DOM/shadow-root assumption passes dryrun and then fails mid-build
during `prepare_rlm_org` — after a full scratch-org spin-up, the most expensive
place to discover it.

**Before committing a behavioral robot change** (new/changed keyword, locator,
JS, click target, wait/assert flow) or a change to the Python task that runs a
suite, run it against a live scratch org:

```bash
# via the CCI task wrapper (preferred — mirrors how prepare_rlm_org runs it).
# Check `cci task run <task> --help` for task-specific options:
cci task run <robot_task> --org <cci_alias>            # CCI alias, e.g. beta
# or directly against a suite — ORG_ALIAS is passed to `sf org open -o`, so it
# takes the SF CLI alias (or username), NOT the CCI alias
robot -v ORG_ALIAS:<sf_alias> robot/rlm-base/tests/setup/<suite>.robot   # e.g. rlm-base__beta
```

The two commands take **different** alias forms (see AGENTS.md → *Org Identity:
CCI vs SF CLI*): `--org` takes the CCI alias (`beta`); the direct
`robot` run's `ORG_ALIAS` feeds `sf org open`, so it needs the SF CLI alias
(`rlm-base__beta`) or the org username.

Confirm the suite actually passes (toggle flips, pill/value reads back, element
is found) — not just that it parses. **Exempt:** comment/`[Documentation]`-only
edits and resource files with no behavioral change. When you cannot run a live
org, state that explicitly and mark the change **unverified** (PR label
`blocked: needs-live-verification`) — never present a dryrun as verification.

---

## Two Purposes: Setup vs E2E

| Aspect | Setup Tests | E2E Tests |
|--------|------------|-----------|
| Location | `tests/setup/` | `tests/e2e/` |
| Purpose | Configure org settings (no API equivalent) | Validate business workflows |
| When they run | Mid-flow in `prepare_rlm_org` | On demand after provisioning |
| Idempotent? | Yes — detects state before toggling | Yes — resets account first |
| Headed? | Headless by default | Headless default, headed for debug |
| Asserts logic? | No — only asserts control was set | Yes — verifies records/assets |

### Setup tests — what they configure

| Robot File | What | Why Robot? |
|-----------|------|-----------|
| `configure_revenue_settings` | Pricing Procedure, Usage Rating, Instant Pricing, flows | Shadow DOM controls, no API |
| `configure_core_pricing_setup` | Default Pricing Procedure on CorePricingSetup page | Shadow DOM combobox, no API |
| `configure_product_discovery_settings` | Default Catalog on Product Discovery Settings page | Shadow DOM combobox, no API |
| `enable_analytics` | CRM Analytics + Data Sync toggle | Light DOM button on `InsightsSetupGettingStarted/home` (VF iframe removed in 262+), no API |
| `enable_document_builder` | Document Builder toggle | Shadow DOM, no API |
| `enable_constraints_settings` | Transaction Type, Asset Context, Constraints Engine | Shadow DOM, no API |
| `reorder_app_launcher` | App Launcher ordering | SortOrder is platform read-only |

### E2E tests — what they validate

| Robot File | Flow | Prerequisite |
|-----------|------|-------------|
| `quote_to_order` | Full Reset→Opp→Quote→Products→**Configure bundle**→Order→Assets→**Renewal Opp** | `prepare_rlm_org` with `qb=true` |
| `setup_quote` | Part 1: Reset→Opp→Quote | Same |
| `order_from_quote` | Part 2: Products→Order→Assets | A Quote must exist |
| `reset_account` | Reset Account via QuickAction | An account must exist |

---

## CCI Task Wiring

For detailed CCI task tables, Python wrapper patterns, shadow DOM
traversal code, LWC reactivity patterns, keyword references, and
test authoring guides, read `.cursor/skills/robot-testing/patterns.md`.

For **agent-oriented** setup-UI pitfalls (shadow vs iframe, logging, when
not to copy generic Selenium), read
`.cursor/skills/robot-testing/setup-ui-shadow-dom.md`.

### Running tests

⚠ The `robot_e2e` tasks' **feature flags come from `cumulusci.yml` defaults, not from the org** — a TSO org
still gets `TSO:false`. Only `QB` is consumed by the suites today.

```bash
cci task run robot_e2e --org beta                                    # headless
cci task run robot_e2e_debug --org beta                              # headed + CDP port 9222
cci task run robot_e2e_debug --org beta -o pause_for_recording true  # with pauses
```

**Browser/driver overrides.** Headless and headed runs both honour `CHROME_BINARY` (falls back
to `CHROME_BIN`) for the browser and `CHROMEDRIVER_PATH` for the driver. Both are unset by
default. Set them as a matching pair, e.g. Chrome for Testing on managed workstations where
stock Chrome's renderer crashes on Setup pages; see
`docs/guides/local-installation.md` → Chrome for Testing. `validate_setup` reports both and
flags a major-version mismatch (FAIL when the browser is overridden, WARN otherwise), plus a
browser override with no driver set (WARN: webdriver-manager sizes its driver for stock Chrome),
and an override that exists but does not run cleanly, e.g. a wrong-architecture build or a
nonzero `--version` exit (FAIL).

---

## Related Skills

- **CCI Orchestration** — `.cursor/skills/cci-orchestration/SKILL.md`
- **Troubleshooting** — `.cursor/skills/troubleshooting/SKILL.md`
- **Repo Integration** — `.cursor/skills/repo-integration/SKILL.md`
