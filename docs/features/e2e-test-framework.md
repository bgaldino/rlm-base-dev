# E2E Test Framework

End-to-end functional tests for Revenue Cloud (RLM) using Robot Framework + SeleniumLibrary. Validates the core sales workflow against a fully provisioned Salesforce org.

## Test Flow

**Quote-to-Order** (`quote_to_order.robot`) — full end-to-end flow:

```
Revenue Cloud App
  -> Reset Account (clear transactional data)
  -> Create Opportunity (QuickAction)
  -> Create Quote (QuickAction / Flow)
  -> Browse Catalogs -> Select Catalog -> Search Product -> Add -> Save Quote
  -> Create Order (Select Single Order -> Finish)
  -> Activate Order (confirm dialog)
  -> Verify Assets on Account (async poll)
  -> Screenshot Assets tab
```

The flow is also available as two modular tests that can be run independently:

**Setup Quote** (`setup_quote.robot`) — Part 1: Reset Account → Create Opportunity → Create Quote.
Can be run standalone to prepare a Quote for other tests.

**Order From Quote** (`order_from_quote.robot`) — Part 2: Add Products → Create Order → Activate Order → Verify Assets.
If no `QUOTE_ID` is provided, creates a fresh Quote automatically.

**Reset Account** (`reset_account.robot`) — Standalone utility to reset an Account before re-running tests.

## Repository Layout

```
robot/rlm-base/
  resources/
    E2ECommon.robot           # Shared keywords (navigation, shadow DOM, workflows)
    SalesforceAPI.py          # REST API keyword library (query, create, poll)
    ChromeOptionsHelper.py    # Headless Chrome options
    ChromeDebugHelper.py      # Headed Chrome with CDP (port 9222)
    WebDriverManager.py       # ChromeDriver path resolution
  variables/
    E2EVariables.robot        # Test data, timeouts, feature flags
  tests/e2e/
    quote_to_order.robot      # Full Quote-to-Order E2E test
    setup_quote.robot         # Part 1: Reset Account + Opportunity + Quote
    order_from_quote.robot    # Part 2: Add Products + Order + Activate + Verify
    reset_account.robot       # Account reset utility
  results/                    # Output (gitignored)
    e2e_<timestamp>/          # Timestamped run folder
      log.html, report.html, output.xml, *.png
tasks/
  rlm_robot_e2e.py            # CCI task wrapper (RunE2ETests)
```

## Prerequisites

### Environment

1. **CumulusCI** with Robot Framework dependencies installed:
   ```bash
   pipx inject cumulusci --force -r robot/requirements.txt
   ```
   Or run `cci task run validate_setup` which auto-installs them.

2. **Chrome browser** installed (headless or headed mode).

3. **A provisioned org** with `prepare_rlm_org` completed and `qb=true`:
   ```bash
   cci flow run prepare_rlm_org --org beta
   ```

### Required Org State

- QuantumBit product catalog loaded (`qb=true` in project config)
- Test Account exists (default: "Global Media" from sample data)
- Account must have the "Reset Account" QuickAction available
- Browse Catalogs must be enabled on the Quote page

### Test Data Defaults (overridable)

| Variable | Default | Override |
|----------|---------|----------|
| `TEST_ACCOUNT_NAME` | Global Media | `-v TEST_ACCOUNT_NAME:"My Account"` |
| `TEST_CATALOG_NAME` | QuantumBit Software | `-v TEST_CATALOG_NAME:"My Catalog"` |
| `TEST_PRODUCT_NAME` | QuantumBit Complete Solution | `-v TEST_PRODUCT_NAME:"My Product"` |
| `ASYNC_TIMEOUT` | 180s | `-v ASYNC_TIMEOUT:300s` |
| `ASYNC_POLL_INTERVAL` | 10s | `-v ASYNC_POLL_INTERVAL:5s` |

## Running Tests

```bash
# Full Quote-to-Order flow (headless)
cci task run robot_e2e --org beta

# Full flow — headed with CDP debugging (connect via chrome://inspect)
cci task run robot_e2e_debug --org beta

# Full flow — headed with pause points for DOM inspection
cci task run robot_e2e_debug -o pause_for_recording true --org beta

# Part 1 only: Reset Account + Create Opportunity + Create Quote
cci task run robot_setup_quote --org beta

# Part 2 only: Add Products + Create Order + Activate + Verify Assets
cci task run robot_order_from_quote --org beta

# Reset Account only
cci task run robot_reset_account --org beta

# Override test data
cci task run robot_e2e --org beta -v TEST_ACCOUNT_NAME:"Acme Corp"
```

### CCI Task Reference

| Task | Suite | Browser | Description |
|------|-------|---------|-------------|
| `robot_e2e` | `quote_to_order.robot` | Headless | Full Quote-to-Order flow |
| `robot_e2e_debug` | `quote_to_order.robot` | Headed + CDP (port 9222) | Same flow, visible browser for debugging |
| `robot_setup_quote` | `setup_quote.robot` | Headed | Part 1: Reset Account + Opportunity + Quote |
| `robot_order_from_quote` | `order_from_quote.robot` | Headed | Part 2: Add Products + Order + Activate + Verify |
| `robot_reset_account` | `reset_account.robot` | Headed | Reset Account only |

### Output

Results are written to `robot/rlm-base/results/e2e_<YYYYMMDD_HHMMSS>/`:
- `log.html` — detailed step-by-step log with screenshots
- `report.html` — pass/fail summary
- `output.xml` — machine-readable results
- `e2e_*.png` — screenshots captured at each step

## Architecture Decisions

### Shadow DOM Traversal (the core challenge)

Salesforce Lightning Web Components (LWC) use shadow DOM extensively. Standard Selenium XPath selectors (`//button[text()='Save']`) cannot cross shadow DOM boundaries. This affects:

- Flow navigation bars (`flowruntime-navigation-bar` > `lightning-button` > shadow > `button`)
- Action ribbon buttons (`runtime_platform_actions-actions-ribbon` > `lightning-button` > shadow > `button`)
- Modals (`lightning-modal` > `lightning-modal-footer` > shadow > `slot` > `lightning-button` > shadow > `button`)
- Toast notifications (`lightning-notification-toast` > shadow > `button`)
- Browse Catalogs components (`runtime_industries_cpq-product-row` > shadow > `button`)

**Solution**: Recursive JavaScript traversal via `Execute JavaScript`. Every keyword that interacts with LWC components uses a `findAllButtons(root)` or `deepQueryAll(root, selector)` pattern:

```javascript
function findAllButtons(root) {
    var btns = [];
    var all = root.querySelectorAll('*');
    for (var i = 0; i < all.length; i++) {
        if (all[i].tagName === 'BUTTON') btns.push(all[i]);
        if (all[i].shadowRoot) btns = btns.concat(findAllButtons(all[i].shadowRoot));
    }
    return btns;
}
```

For slotted content (e.g., `lightning-modal-footer`), the `deepQueryAll` variant also traverses `slot.assignedElements()`.

**Why not UTAM?** Salesforce's UI Test Automation Model was evaluated and rejected:
- No CumulusCI integration (Robot Framework is CCI-native)
- No pre-built page objects for the components we need (flow modals, CPQ catalogs)
- JavaScript-only toolchain in a Python-centric project
- Enormous migration cost vs. fixing specific shadow DOM issues with JS helpers

### Keyword Architecture: XPath First, JS Fallback

Most keywords follow a three-tier strategy:

1. **XPath** — fast, works for light DOM and synthetic shadow
2. **Scoped JS** — searches within a specific component's shadow root
3. **Broad JS** — `findAllButtons(document)` as a last resort

This makes tests resilient across LWC rendering modes (synthetic vs. native shadow).

### Composite Workflow Keywords

Test steps are composed from high-level keywords in E2ECommon.robot:

| Keyword | Description |
|---------|-------------|
| `Reset Test Account` | Navigate to Account, run Reset Account flow |
| `Create Opportunity From Account` | QuickAction + API lookup, returns Id |
| `Create Quote From Opportunity` | QuickAction flow + API lookup, returns Id |
| `Add Products Via Browse Catalogs` | Full catalog workflow (Price Book modal, catalog select, search, add, save) |
| `Create Order From Quote` | Create Order flow with single order selection, returns Id |
| `Activate Order` | Click Activate, confirm dialog, poll for status |
| `Confirm Modal Action` | Generic Aura modal footer button click with retry |

These keep the test file readable while encapsulating shadow DOM complexity in the resource file.

### Async Polling

Salesforce platform operations (Order activation, Asset creation) are asynchronous. The framework uses `Wait Until Keyword Succeeds` with configurable timeouts:

- **Record creation** — `Wait For Related Record Via API` polls a SOQL query until a record appears
- **Field value** — `Wait For Field Value Via API` polls until a field matches the expected value
- **Asset verification** — `Verify Assets Exist On Account` polls until asset count > 0

Default: 180s timeout, 10s poll interval.

### Price Book Modal Race Condition

After clicking Browse Catalogs, a "Choose Price Book" modal may appear. Its render timing is unpredictable — it can appear before or after the catalog datatable. The fix:

- `_Dismiss Price Book Modal If Present` is called inside the `_Dismiss Or Select Catalog` retry loop
- If the modal appears late, it's dismissed on the next retry iteration
- Uses `deepQueryAll` with slot traversal because the modal's Save button is inside nested shadow DOM + slotted content

### LWC Input Handling

Setting values on LWC input components requires the native HTMLInputElement setter to trigger reactivity:

```javascript
var nativeSetter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
nativeSetter.call(input, value);
input.dispatchEvent(new Event('input', {bubbles: true, composed: true}));
```

For pressing Enter, Selenium's `Press Keys RETURN` is used instead of JS `KeyboardEvent` dispatch, which LWC components often ignore.

## Extending the Framework

### Adding a New Test

1. Create `robot/rlm-base/tests/e2e/my_test.robot`
2. Import shared resources:
   ```robot
   Resource    ../../resources/E2ECommon.robot
   Resource    ../../variables/E2EVariables.robot
   ```
3. Use `Lookup Test Account` in suite setup
4. Compose test steps from existing keywords

### Adding a New Workflow Keyword

Add to the `# -- Composite Workflow Keywords` section of `E2ECommon.robot`:

```robot
My New Workflow
    [Documentation]    Description of what this does.
    [Arguments]    ${record_id}
    Navigate To Record    MyObject    ${record_id}
    Click Highlights Panel Action    My Action
    Advance Through Flow Screens
    Dismiss Toast If Present
```

### Interacting with New LWC Components

If a component uses shadow DOM, follow this pattern:

```robot
_My Internal Keyword
    ${result}=    Execute JavaScript
    ...    return (function(){
    ...        function findAll(root, tag) {
    ...            var found = [];
    ...            var all = root.querySelectorAll('*');
    ...            for (var i = 0; i < all.length; i++) {
    ...                if (all[i].tagName === tag) found.push(all[i]);
    ...                if (all[i].shadowRoot) found = found.concat(findAll(all[i].shadowRoot, tag));
    ...            }
    ...            return found;
    ...        }
    ...        // Your component-specific logic here
    ...        return 'result';
    ...    })()
```

Key rules:
- Always use `Wait Until Keyword Succeeds` for retryable operations
- Set `composed: true` on events that need to cross shadow boundaries
- Check `offsetParent !== null` to filter hidden elements
- For slotted content, use `slot.assignedElements({flatten: true})`
- Prefix internal keywords with `_` (Robot Framework convention for private keywords)

### Adding a New CCI Task

In `cumulusci.yml`:

```yaml
robot_my_test:
  group: E2E Testing
  description: >
    Description of what this test validates.
  class_path: tasks.rlm_robot_e2e.RunE2ETests
  options:
    suite: robot/rlm-base/tests/e2e/my_test.robot
    outputdir: robot/rlm-base/results
    headed: true
```

### Debugging Tips

- **CDP debugging** — headed mode opens Chrome with remote debugging on port 9222. Connect via `chrome://inspect` or paste the CDP WebSocket URL from the test log.
- **Pause points** — use `Pause For Recording If Enabled` at any step; requires `-o pause_for_recording true`. When a pause is hit, the terminal shows a banner with the message and CDP URL. Press Enter to resume:
  ```
  ============================================================
    PAUSED: About to Browse Catalogs and add products.
    CDP: ws://127.0.0.1:9222/devtools/browser/abc123
  ============================================================
    Press Enter to resume...
    RESUMED
  ============================================================
  ```
  Pause points are placed before each major step (Reset, Create Opportunity, Create Quote, Browse Catalogs, Create Order, Activate Order) and after final verification. They have no effect in headless mode (`PAUSE_FOR_RECORDING` defaults to `false`).
- **Screenshots** — every step captures a screenshot; check `results/e2e_<timestamp>/log.html`.
- **Shadow DOM inspection** — in Chrome DevTools, enable "Show user agent shadow DOM" in Settings to see shadow roots in the Elements panel.
- **Test isolation** — run `cci task run robot_reset_account --org beta` to clear transactional data before re-running.

## Keyword Reference (E2ECommon.robot)

### Navigation
| Keyword | Arguments | Description |
|---------|-----------|-------------|
| `Navigate To App` | app_name | Opens a Lightning app by display name |
| `Navigate To Account` | account_id | Opens Account record page |
| `Navigate To Opportunity` | opportunity_id | Opens Opportunity record page |
| `Navigate To Quote` | quote_id | Opens Quote record page |
| `Navigate To Order` | order_id | Opens Order record page |
| `Click Record Page Tab` | tab_label | Clicks a tab on a record page |

### Actions
| Keyword | Arguments | Description |
|---------|-----------|-------------|
| `Click Highlights Panel Action` | action_label | Clicks a button/menu item in the highlights panel |
| `Save Modal` | button_label=Save | Clicks a button in a modal (shadow DOM aware) |
| `Advance Through Flow Screens` | | Iterates through flow screens clicking Next/Finish/Done |
| `Confirm Modal Action` | button_label=Activate | Clicks a confirmation button in a modal footer |

### Browse Catalogs
| Keyword | Arguments | Description |
|---------|-----------|-------------|
| `Click Browse Catalogs` | | Clicks Browse Catalogs, handles Price Book modal |
| `Select Catalog By Name` | catalog_name | Selects catalog radio + clicks Next |
| `Search Product In Catalog` | product_name | Types product name + presses Enter |
| `Add Product By Name` | product_name | Clicks Add on the matching product row |
| `Click Save Quote In Catalog` | | Clicks Save Quote (waits for enabled state) |

### Async / API
| Keyword | Arguments | Description |
|---------|-----------|-------------|
| `Wait For Field Value Via API` | sobject, record_id, field_name, expected_value | Polls until field matches |
| `Wait For Related Record Via API` | soql | Polls until SOQL returns a record, returns Id |
| `Lookup Test Account` | | Queries Account by TEST_ACCOUNT_NAME, sets ACCOUNT_ID |

### Utilities
| Keyword | Arguments | Description |
|---------|-----------|-------------|
| `Dismiss Toast If Present` | | Closes any visible toast messages |
| `Capture Step Screenshot` | step_name | Captures a numbered screenshot |
| `Pause For Recording If Enabled` | message | Pauses for DOM inspection (when enabled) |
