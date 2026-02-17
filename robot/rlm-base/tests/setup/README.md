# Setup Automation (Robot Framework)

Robot Framework tests that configure Salesforce Revenue Settings page options that cannot be set via Metadata API. These include toggles, picklist selections, and text inputs on the Revenue Settings Lightning Setup page.

## Test Suites

| Suite | CCI Task | Description |
|-------|----------|-------------|
| `enable_document_builder.robot` | `enable_document_builder_toggle` | Enable Document Builder toggle (for Doc Gen) |
| `enable_constraints_settings.robot` | `enable_constraints_settings` | Set Default Transaction Type, Asset Context picklist, and enable Constraints Engine toggle |
| `configure_revenue_settings.robot` | `configure_revenue_settings` | Set Pricing Procedure, Usage Rating Procedure, enable Instant Pricing toggle, set Create Orders Flow |

## Prerequisites

Install and verify prerequisites in the **main README** only: [Installation — Document Builder automation dependencies](../../../README.md#installation) (Robot Framework, SeleniumLibrary, Chrome/ChromeDriver, Salesforce CLI). Do not install or verify from this folder; the main README is the single source of truth.

## Running Tests

From the repo root. **Recommended:** pass an org alias so the test uses `sf org open --url-only` to get an authenticated URL; the Selenium browser then opens that URL and is logged in without manual steps.

### Via CCI (recommended)

```bash
# Run individually
cci task run enable_document_builder_toggle --org my-scratch
cci task run enable_constraints_settings --org my-scratch
cci task run configure_revenue_settings --org my-scratch

# As part of the full org build
cci flow run prepare_rlm_org --org my-scratch
```

### Via Robot Framework directly

```bash
# Document Builder
robot -v ORG_ALIAS:my-scratch robot/rlm-base/tests/setup/enable_document_builder.robot

# Constraints prerequisites
robot -v ORG_ALIAS:my-scratch robot/rlm-base/tests/setup/enable_constraints_settings.robot

# Revenue Settings (Pricing, Usage Rating, Instant Pricing, Create Orders Flow)
robot -v ORG_ALIAS:my-scratch robot/rlm-base/tests/setup/configure_revenue_settings.robot
```

If you don't set `ORG_ALIAS` and the browser opens on a Salesforce login page, log in within the configured wait (default 90s); the test will then reload the Revenue Settings page.

## Variables

### Common Variables (all suites)

| Variable | Description |
|----------|-------------|
| `ORG_ALIAS` | **Recommended.** Org username or alias for authenticated browser session via `sf org open --url-only`. |
| `REVENUE_SETTINGS_URL` | Full URL to Revenue Settings when not using ORG_ALIAS. |
| `MANUAL_LOGIN_WAIT` | Wait time for manual login if no org alias (default: `90s`). |

### enable_document_builder.robot

| Variable | Description |
|----------|-------------|
| `DOCUMENT_BUILDER_PREREQUISITE_LABEL` | Toggle to enable first (prerequisite). Default: empty (skip). |
| `DOCUMENT_BUILDER_TOGGLE_LABEL` | Label of the Document Builder toggle (default: "Document Builder"). |

### enable_constraints_settings.robot

| Variable | Description |
|----------|-------------|
| `DEFAULT_TRANSACTION_TYPE_VALUE` | Value for Default Transaction Type dropdown (default: "Advanced Configurator"). |
| `ASSET_CONTEXT` | Value for Asset Context picklist (default: "RLM_AssetContext"). |

### configure_revenue_settings.robot

| Variable | Description |
|----------|-------------|
| `PRICING_PROCEDURE` | Default pricing procedure name (default: "RLM Revenue Management Default Pricing Procedure"). |
| `USAGE_RATING_PROCEDURE` | Default usage rating procedure name (default: "RLM Default Rating Discovery Procedure"). |
| `CREATE_ORDERS_FLOW` | API name of the Create Orders from Quotes flow (default: "RC_CreateOrdersFromQuote"). |

## Implementation Notes

### Shadow DOM Toggles

The Constraints Engine and Instant Pricing toggles are inside Lightning Web Component Shadow DOM boundaries, making them inaccessible to standard Selenium locators. Both toggles use JavaScript shadow DOM traversal (`findInShadows`) to locate the underlying `<input>` element and read its `checked` property directly for reliable state detection. This avoids false positives from ambient "Enabled"/"Disabled" text elsewhere on the page.

### Native `<select>` vs Lightning Combobox

The Asset Context field renders as a native HTML `<select>` element, while Pricing Procedure and Usage Rating render as Lightning comboboxes (pill/chip when set, dropdown when empty). The automation detects and handles both patterns:

- **Native `<select>`**: Uses `Select From List By Label` (SeleniumLibrary)
- **Lightning combobox**: Detects pills, hovers to reveal the clear button, clears if wrong value, then clicks dropdown options

### Idempotency

All tests detect current state before making changes:
- Toggles: Read `checked` property via JavaScript; skip click if already enabled
- Picklists: Check if correct value is already shown in pill; skip if matched
- Text inputs: Compare current value; skip if already correct

### Section Scoping

Picklist pill detection and clearing is scoped to the nearest ancestor container for each section, preventing interactions from bleeding into adjacent sections on the page.

## CumulusCI Flow Integration

| Task | Flow | Step |
|------|------|------|
| `enable_document_builder_toggle` | `prepare_docgen` | Step 2 |
| `enable_constraints_settings` | `prepare_constraints` | Step 5 (when `constraints_data` is true) |
| `configure_revenue_settings` | `prepare_rlm_org` | Step 27 |

## Generated Output

Running any test produces log and report files in `robot/rlm-base/results/` (or `--outputdir`). On failure, screenshots are saved automatically. This directory is in `.gitignore`; do not commit its contents. To remove local run artifacts: `rm -f robot/rlm-base/results/*`.
