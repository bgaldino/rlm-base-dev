# post_billing_ui — generated vs hand-authored

Most of this module was **bootstrapped once** by `scripts/build_billing_ui_module.py`,
which copied an extracted LWC bundle (`extracted/maaron-billinglwc/`, gitignored and
absent from a fresh clone) and applied `RLM_`/`rlm` namespace prefixes. It is a one-shot
bootstrap, **not** a round-trip generator: the source tree is not committed, so the
script cannot be re-run here, and only some of the files below are its output. The rest
are hand-authored and the script does not know about them — editing them and re-running
the generator (were the source present) would not touch them.

This split is easy to get wrong — a reviewer once read the whole `classes/` directory as
generated (it is mostly not), which is what todo pack 084 recorded and this file resolves.

## Generator-owned (`scripts/build_billing_ui_module.py`)

- **Apex controllers (11)** — one per `APEX_MAP` entry, each with its `.cls` and
  `.cls-meta.xml`:
  `RLM_BSGTimelineController`, `RLM_BillingCaseMetricsController`,
  `RLM_BillingScheduleGroupController`, `RLM_CollectionsDashboardController`,
  `RLM_DisputeDetailsController`, `RLM_InvoiceAgingController`,
  `RLM_InvoiceProductSummaryController`, `RLM_InvoiceTaxSummaryController`,
  `RLM_PaymentsDataController`, `RLM_SplitInvoicesController`,
  `RLM_TxnJournalRelatedListController`.
- **LWC components (17)** under `lwc/` — one per `LWC_MAP` entry (`rlm…`).
- **Static resources (2)** under `staticresources/` — `InvoiceCardLogo.*`.
- **Flexipages (8)** — written to `templates/flexipages/standalone/billing_ui/`, not
  into this directory (per `FLEXIPAGE_MAP`).

`RLM_TxnJournalRelatedListController` is generator-owned but was for a time out of the
generator's reach: `APEX_MAP` targeted an `RLM_TransactionJournal…` name 43 characters
long, over Salesforce's 40-char Apex-class cap, so the class was hand-shortened to the
35-char name above and the map left stale. Pack 084 fixed the map entry (and added a guard
that fails the build on any >40 value), so the map and the shipped class now agree.

## Hand-authored (the generator does NOT own these — 23 `.cls`)

- **Every `*Test` class** — the generator produces no tests.
- **Controllers with no `APEX_MAP` entry:** `RLM_BSGContextController`,
  `RLM_BillingScheduleGroupService`, `RLM_CollectionsConsoleController`,
  `RLM_InvoiceBatchRunMonitorController`, `RLM_InvoiceSummaryController`,
  `RLM_OnAccountBillingController`.

## Do not

- Do **not** add `classes/` to `.prettierignore` — it would exempt the 23 hand-authored
  files (including every test) from formatting enforcement.
- Do **not** treat a re-run of the generator as a maintenance step; its source is absent.
  Behavior is guarded offline by `tests/test_build_billing_ui_module.py`.
