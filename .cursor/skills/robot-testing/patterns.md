# Robot Framework — Patterns & Reference

Detailed patterns for Robot Framework tests in this repository.

---

## Repository Structure

```
robot/rlm-base/
├── tests/
│   ├── e2e/                          # E2E functional tests
│   │   ├── quote_to_order.robot
│   │   ├── setup_quote.robot
│   │   ├── order_from_quote.robot
│   │   └── reset_account.robot
│   └── setup/                        # Org setup automation
│       ├── configure_revenue_settings.robot
│       ├── configure_core_pricing_setup.robot
│       ├── configure_product_discovery_settings.robot
│       ├── configure_billing_email_settings.robot
│       ├── enable_analytics.robot
│       ├── enable_document_builder.robot
│       ├── enable_constraints_settings.robot
│       └── reorder_app_launcher.robot
├── resources/
│   ├── E2ECommon.robot               # ~1250 lines — main E2E keywords
│   ├── SetupToggles.robot            # ~380 lines — setup toggle keywords
│   ├── SalesforceAPI.py              # REST API keywords (SOQL, DML)
│   ├── ChromeOptionsHelper.py        # Headless Chrome options
│   ├── ChromeDebugHelper.py          # Headed Chrome + CDP
│   ├── AnalyticsSetupHelper.py       # VF iframe checkbox automation
│   └── WebDriverManager.py           # ChromeDriver path resolution
├── variables/
│   ├── E2EVariables.robot            # Test data + feature flags
│   └── SetupVariables.robot          # Setup page URLs + toggle labels
└── results/                          # Test output (gitignored)
```

---

## CCI Task Wiring

### Setup tasks (run during `prepare_rlm_org`)

| CCI Task | Python Class | Suite |
|----------|-------------|-------|
| `configure_revenue_settings` | `ConfigureRevenueSettings` | `tests/setup/configure_revenue_settings.robot` |
| `configure_core_pricing_setup` | `ConfigureCorePricingSetup` | `tests/setup/configure_core_pricing_setup.robot` |
| `configure_product_discovery_settings` | `ConfigureProductDiscoverySettings` | `tests/setup/configure_product_discovery_settings.robot` |
| `configure_billing_email_settings` | `ConfigureBillingEmailSettings` | `tests/setup/configure_billing_email_settings.robot` |
| `enable_analytics_replication` | `EnableAnalyticsReplication` | `tests/setup/enable_analytics.robot` |
| `enable_document_builder_toggle` | `EnableDocumentBuilderToggle` | `tests/setup/enable_document_builder.robot` |
| `enable_constraints_settings` | `EnableConstraintsSettings` | `tests/setup/enable_constraints_settings.robot` |
| `reorder_app_launcher` | `ReorderAppLauncher` | `tests/setup/reorder_app_launcher.robot` |

### E2E tasks (run on demand)

| CCI Task | Suite | Mode |
|----------|-------|------|
| `robot_e2e` | `tests/e2e/quote_to_order.robot` | Headless |
| `robot_e2e_debug` | `tests/e2e/quote_to_order.robot` | Headed + CDP |
| `robot_setup_quote` | `tests/e2e/setup_quote.robot` | Headed |
| `robot_order_from_quote` | `tests/e2e/order_from_quote.robot` | Headed |
| `robot_reset_account` | `tests/e2e/reset_account.robot` | Headed |

---

## Python Wrapper Pattern

All Robot task wrappers follow this structure:

1. Resolve org username from `self.org_config.username`
2. Call `check_urllib3_for_robot()` from `tasks.robot_utils`
3. Build: `[sys.executable, "-m", "robot", "--variable", "ORG_ALIAS:{username}"]`
4. Pass task options as `--variable` args
5. E2E wrappers also pass feature flags from `project__custom`
6. Run via `subprocess.run(cmd, cwd=str(repo_root))`
7. Raise `RuntimeError` on non-zero exit

---

## Authentication

All tests authenticate via `sf org open --url-only`:

```robot
${result}=    Run Process    sf    org    open
...    --url-only    --path    ${page_path}
...    -o    ${ORG_ALIAS}
```

**Security:** `Set Log Level NONE` wraps all URL retrieval to prevent
session tokens from appearing in `log.html`.

---

## Shadow DOM Traversal

Salesforce Lightning uses LWC synthetic shadow DOM. Standard Selenium
locators and XPath cannot pierce shadow boundaries. The repo uses recursive
JavaScript traversal via two canonical helper functions shared as Robot
variables (prepend them to `Execute JavaScript` blocks that need them).

### Shared helpers (Robot variables)

Define in `*** Variables ***` and prepend to JS blocks that need them:

```robot
# Find single element — depth-limited to 6 shadow levels
${_JS_FIND_EL}    function findEl(root, sel, d) { if (d > 6) return null; var el = root.querySelector(sel); if (el) return el; var all = root.querySelectorAll('*'); for (var i=0;i<all.length;i++){if(all[i].shadowRoot){var f=findEl(all[i].shadowRoot,sel,d+1);if(f)return f;}} return null; }

# Find all elements matching selector (used for options, pills, etc.)
# Define inline in JS block as a named function expression — see examples below
```

### findEl usage in Execute JavaScript

```robot
${result}=    Execute JavaScript
...    ${_JS_FIND_EL}
...    return (function(targetValue) {
...        var el = findEl(document, 'lightning-combobox[data-id="myField"]', 0);
...        if (!el) return 'not_found';
...        ...
...    })(arguments[0])
...    ARGUMENTS    ${my_var}
```

### findAll (inline variant for collecting multiple elements)

```javascript
function findAll(root, sel, d, acc) {
    if (d > 6) return;
    root.querySelectorAll(sel).forEach(function(el){acc.push(el);});
    root.querySelectorAll('*').forEach(function(el){if(el.shadowRoot)findAll(el.shadowRoot,sel,d+1,acc);});
}
var items = []; findAll(document, '[role="option"]', 0, items);
```

### Lightning combobox interaction pattern

Salesforce comboboxes have a 3-level shadow structure:
`lightning-combobox` → shadowRoot → `lightning-base-combobox` → shadowRoot → `button[role="combobox"]`

Options are `lightning-base-combobox-item[role="option"]` with text in their own shadow roots.

```robot
# Step 1: open the dropdown
${open_result}=    Execute JavaScript
...    ${_JS_FIND_EL}
...    return (function() {
...        var lc = findEl(document, 'lightning-combobox[data-id="myField"]', 0);
...        if (!lc) return 'combobox_not_found';
...        var lbc = lc.shadowRoot && lc.shadowRoot.querySelector('lightning-base-combobox');
...        if (!lbc) return 'page_not_ready';
...        var btn = lbc.shadowRoot && lbc.shadowRoot.querySelector('button[role="combobox"]');
...        if (!btn) return 'page_not_ready';
...        btn.click(); return 'opened';
...    })()

# Step 2: click the matching option
${select_result}=    Execute JavaScript
...    return (function(targetValue) {
...        function findAll(root, sel, d, acc) {
...            if (d > 6) return;
...            root.querySelectorAll(sel).forEach(function(el){acc.push(el);});
...            root.querySelectorAll('*').forEach(function(el){if(el.shadowRoot)findAll(el.shadowRoot,sel,d+1,acc);});
...        }
...        var opts = []; findAll(document, '[role="option"]', 0, opts);
...        for (var i=0; i<opts.length; i++) {
...            var text = opts[i].shadowRoot ? opts[i].shadowRoot.textContent.trim() : opts[i].textContent.trim();
...            if (text === targetValue) { opts[i].click(); return 'clicked'; }
...        }
...        return 'not_found';
...    })(arguments[0])
...    ARGUMENTS    ${target_value}
```

### Toggle interaction (SetupToggles.robot)

Lightning toggles nest two shadow levels:
`lightning-input` → shadowRoot → `lightning-primitive-input-toggle` → shadowRoot → `input[role="switch"]`

Plain checkboxes (`input[type="checkbox"]` in light DOM) also exist — check `lightning-input` first
at each DOM depth; only fall back to plain inputs when no `lightning-input` is found at that depth.
Always click the wrapping `<label>` (not the raw `<input>`) to trigger LWC save handlers:

```javascript
(pi.closest('label') || pi).click();
```

### Render timing — Wait Until Keyword Succeeds

Some setup pages (e.g. CorePricingSetup) render LWC components slowly. Return a
`'page_not_ready'` sentinel from JS when the expected element is absent, then use
`Wait Until Keyword Succeeds` to retry:

```robot
${result}=    Wait Until Keyword Succeeds    20s    3s    _My Helper Keyword    ${arg}
...

_My Helper Keyword
    [Arguments]    ${arg}
    ${result}=    Execute JavaScript    ...
    Should Not Be Equal    ${result}    page_not_ready
    ...    msg=Page LWC components not yet rendered; retrying...
    RETURN    ${result}
```

Return `'page_not_ready'` from JS for: element absent, inner shadow not yet rendered (`lbc_not_found`,
`btn_not_found`), or no pills/content found at all.

---

## LWC Reactivity — Native Setter

Standard `input_text` doesn't trigger LWC change detection. Use:

```javascript
var nativeSetter = Object.getOwnPropertyDescriptor(
    HTMLInputElement.prototype, 'value'
).set;
nativeSetter.call(input, '${search_text}');
input.dispatchEvent(new Event('input', {bubbles: true, composed: true}));
input.dispatchEvent(new Event('change', {bubbles: true, composed: true}));
```

`composed: true` is essential for crossing shadow DOM boundaries.

---

## Multi-Tier Fallback Pattern

Most interaction keywords try strategies in order:
1. Standard Selenium XPath (fast, works outside shadow DOM)
2. Scoped XPath (within parent `<li>`, `<section>`, `@role='row'`)
3. Shadow DOM JavaScript (recursive traversal)
4. JS click (`arguments[0].click()`) when Selenium click is intercepted

---

## E2E Keyword Groups (E2ECommon.robot)

| Group | Key Keywords |
|-------|-------------|
| Browser | `Open Browser For E2E`, `Close Browser For E2E` |
| Navigation | `Navigate To App`, `Navigate To Record`, `Get Authenticated Url` |
| Modals | `Wait For Modal`, `Fill Modal Field`, `Select Modal Picklist Value`, `Save Modal` |
| Flows | `Advance Through Flow Screens` |
| Browse Catalogs | `Click Browse Catalogs`, `Select Catalog By Name`, `Search Product In Catalog`, `Add Product By Name` |
| Composite | `Reset Test Account`, `Create Opportunity From Account`, `Create Quote From Opportunity`, `Create Order From Quote`, `Activate Order` |
| Async | `Wait For Field Value Via API`, `Wait For Related Record Via API` |
| Utilities | `Capture Step Screenshot`, `Dismiss Toast If Present`, `Pause For Recording If Enabled` |

---

## Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `${TEST_CATALOG_NAME}` | `QuantumBit Software` | Catalog for Browse Catalogs |
| `${TEST_PRODUCT_NAME}` | `QuantumBit Complete Solution` | Product to add |
| `${ASYNC_TIMEOUT}` | `180s` | Max wait for async ops |
| `${ASYNC_POLL_INTERVAL}` | `10s` | Poll interval |
| `${HEADED}` | `false` | Browser mode |
| `${PAUSE_FOR_RECORDING}` | `false` | Debug pauses |

---

## Naming Conventions

| Convention | Example |
|-----------|---------|
| Suite variables | `${UPPER_SNAKE_CASE}` |
| Local variables | `${lower_snake}` |
| Internal keywords | Prefix with `_` |
| Python libraries | `WITH NAME` alias |
| Screenshots | `e2e_{counter}_{step_name}.png` |
| Tags | `e2e`, `requires_qb`, `maintenance` |

---

## Writing New Tests

### New setup automation test

1. Create `robot/rlm-base/tests/setup/<name>.robot`
2. Import `../../resources/SetupToggles.robot`
3. Suite Setup: `Open Browser For Setup` / Teardown: `Close Browser After Setup`
4. Use `Enable Toggle By Label` for simple toggles
5. Create Python wrapper in `tasks/`, register in `cumulusci.yml`
6. Wire into the appropriate `prepare_*` flow with `when:` condition

### New E2E test

1. Create `robot/rlm-base/tests/e2e/<name>.robot`
2. Import `../../resources/E2ECommon.robot` and `../../variables/E2EVariables.robot`
3. Gate with `Skip If` on the relevant feature flag
4. Use composite keywords from E2ECommon
5. Add `Capture Step Screenshot` at each major step
6. Register using `RunE2ETests` in `cumulusci.yml`

---

## Salesforce Interaction Layers

| Layer | Used By | How |
|-------|---------|-----|
| Lightning Record Pages | E2E tests | SeleniumLibrary + shadow DOM JS |
| Lightning Setup Pages | Setup tests | SeleniumLibrary + XPath + shadow DOM JS |
| Visualforce Iframes | `enable_analytics` | `switch_to.frame()` + standard WebDriver |
| Aura Framework API | `reorder_app_launcher` | Synchronous XHR to `/aura` |
| Salesforce REST API | E2E verification | `SalesforceAPI.py` via `sf org display` |
| SF CLI (`sf`) | Auth + navigation | `Run Process sf org open/display` |
