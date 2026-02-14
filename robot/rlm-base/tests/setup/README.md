# Setup toggles (Robot Framework)

Tests that enable toggles on Salesforce Lightning Setup pages that cannot be controlled via metadata (e.g. Document Builder for Doc Gen).

## Prerequisites

Install and verify prerequisites in the **main README** only: [Installation — Document Builder automation dependencies](../../../README.md#installation) (Robot Framework, SeleniumLibrary, Chrome/ChromeDriver, Salesforce CLI). Do not install or verify from this folder; the main README is the single source of truth.

## Run the Document Builder test

From the repo root. **Recommended:** pass an org alias so the test uses `sf org open --url-only` to get an authenticated URL; the Selenium browser then opens that URL and is logged in without manual steps.

```bash
# Recommended: use Salesforce CLI to get an authenticated URL (no manual login)
robot -v ORG_ALIAS:my-scratch robot/rlm-base/tests/setup/enable_document_builder.robot

# Fallback: use a static URL (browser may show login; you have MANUAL_LOGIN_WAIT to log in)
robot robot/rlm-base/tests/setup/enable_document_builder.robot

# Override URL for a different org (no sf login)
robot -v REVENUE_SETTINGS_URL:https://your-org.scratch.my.salesforce-setup.com/lightning/setup/RevenueSettings/home robot/rlm-base/tests/setup/enable_document_builder.robot
```

If you don't set `ORG_ALIAS` and the browser opens on a Salesforce login page, log in within the configured wait (default 90s); the test will then reload the Revenue Settings page and enable the Document Builder toggle.

## Variables

| Variable | Description |
|----------|-------------|
| `ORG_ALIAS` | **Recommended.** Org username or alias. When set, the test runs `sf org open -o <alias> --url-only -p /lightning/setup/RevenueSettings/home` and opens the returned URL in the browser so the session is authenticated. |
| `REVENUE_SETTINGS_URL` | Full URL to Revenue Settings when not using ORG_ALIAS (e.g. `.../lightning/setup/RevenueSettings/home`). |
| `MANUAL_LOGIN_WAIT` | If a login page is shown, wait this long (e.g. `90s`) for manual login before reloading. |
| `DOCUMENT_BUILDER_PREREQUISITE_LABEL` | If set, the test enables this toggle first so Document Builder becomes enabled. Default: empty (skip). |
| `DOCUMENT_BUILDER_TOGGLE_LABEL` | Label of the toggle on the page (default: "Document Builder"). |

### If a toggle is disabled

If the test fails with **"Toggle X is disabled on the page"**, Revenue Settings is showing that toggle as disabled (no click allowed). In that case:

1. Open **Setup → Revenue Settings** in the org and see which toggles are above Document Builder (or Revenue Management).
2. Enable any prerequisites manually (e.g. enable the first toggle if it is required before others).
3. Re-run the flow or task. The test will then click the Document Builder toggle (and verify it is on).

If your org does not allow enabling these toggles (e.g. missing feature or permissions), the test cannot enable them automatically.

## CumulusCI

The **Document Builder toggle** is run automatically as part of the **prepare_docgen** flow (step 2, before `deploy_post_docgen`). When you run:

```bash
cci flow run prepare_docgen --org my-scratch
```

the flow will: (1) create_docgen_library, (2) **enable_document_builder_toggle** (this Robot test with the flow's org), (3) deploy_post_docgen. The task passes the flow's org to the test via `ORG_ALIAS`, so the browser is authenticated via `sf org open --url-only`.

To run only the enable-Document-Builder task:

```bash
cci task run enable_document_builder_toggle --org my-scratch
```

To run all Robot setup tests manually:

```bash
cci task run robot --options "suites=robot/rlm-base/tests/setup"
```

## Generated output

Running the test (or the CCI task) produces log and report files in `robot/rlm-base/results/` (or `--outputdir`). On failure, a screenshot may be saved (e.g. `document_builder_toggle_verification_failed.png`). This directory is in `.gitignore`; do not commit its contents. To remove local run artifacts: `rm -f robot/rlm-base/results/*`.
