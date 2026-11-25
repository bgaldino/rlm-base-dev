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

## Hand-authored (the generator does NOT own these — 25 `.cls`)

- **Every `*Test` class** — the generator produces no tests. `RLM_BillingUIAccessTest`
  covers no single controller: it proves that each billing role, given `RLM_BillingUI`,
  can run the controllers' USER_MODE reads.
- **`RLM_BillingUITestUsers`** — the test-only factory those access tests share: a
  Minimum Access user with only the licenses and permission sets a test names.
- **Controllers with no `APEX_MAP` entry:** `RLM_BSGContextController`,
  `RLM_BillingScheduleGroupService`, `RLM_CollectionsConsoleController`,
  `RLM_InvoiceBatchRunMonitorController`, `RLM_InvoiceSummaryController`,
  `RLM_OnAccountBillingController`.

## Create Billing Schedule Group modal

`rlmBillingScheduleGroupModal` calls `RLM_BillingScheduleGroupService`, which invokes the
standard `createBillingSchedulesFromTrxn` action. The payload carries the chosen legal entity
(`LegalEntityId__std`), the billing treatment of that entity for the chosen Advance or Arrears
timing, or for a one-time charge the entity's treatment in the charge's currency
(`BillingTreatmentId__std`; the timing tags themselves are rejected by the action), a
billing term when a caller gives one (`BillingTerm__std`; the modal has no input for it) and a
shipping city (`ShippingCity__std`: the account's `ShippingCity`, else the `billingCity` the
caller submitted, which create requires). The account sent (`AccountId__std`) is the account page
the modal opened on (`pageAccountId`) when it is the billing account's own or is linked to it through
`AccountBillingAccount`; otherwise the billing account's own account (if it has none, create refuses), else its oldest link.
`getAccountBillingInfo` returns the billing city of that same account (the page account's when the
billing account is reached through a link), so the submitted city matches the account sent. Treatments considered are the oldest-first active,
non-milestone, billable ones of the legal entity in the charge's currency, counting only their active
items typed Advance or Arrears (a None-type item is ignored; several items of one timing are fine).
A recurring charge takes the first treatment whose items all bill in the chosen timing; one with
items in both timings is ambiguous and skipped (when it is the only match the refusal says it has
items in both timings and must be split into one treatment per timing, naming it when readable). A one-time charge (billing term unit OneTime) offers no timing and
ignores one if sent, so ambiguity does not apply: it takes the first Advance-only treatment, else the first Arrears-only one, else (last, since
what the platform bills for it on a one-time charge is unmeasured) the first with both timings
(measured: left to itself the platform picks a treatment of the legal entity whatever the currency,
so one is sent). The charge currency must be an active `CurrencyType`, or create refuses before the
lookup. The treatment read filters on the charge currency and is capped at 1000 items, oldest first; when the cap is hit the last treatment read is dropped (it may be cut short). The page account must be readable (Account read in USER_MODE); if it differs from the billing account's own and its link read is refused or unreadable, create refuses. It reads `BillingTreatment`, `BillingTreatmentItem`, `LegalEntity`, `CurrencyType` and
`Account.ShippingCity` in USER_MODE. `RLM_BillingUI` grants object read on `BillingTreatment` and
`LegalEntity` (the item follows its master, below) and field read on the shipping city through the
`Account.ShippingAddress` compound grant; the treatment and item fields it reads (`Status`,
`LegalEntityId`, `IsMilestoneBilling`, `ExcludeFromBilling`, `CurrencyIsoCode`, `CreatedDate`,
`BillingType`, `BillingTreatmentId`) are not permissionable (measured on a 264 scratch org,
2026-11-26), so no `fieldPermissions` rows exist or are possible. The service refuses, with a
message naming currency and legal entity (and the timing, in lower case, for a recurring charge), a
charge with no such treatment, including one whose only treatments are in another currency, before calling the
action; it never sends a treatment of another currency. `BillingTreatmentItem` has no grant of
its own: it is a master-detail child, so its read follows `BillingTreatment` (a grant on it is
dropped on deploy, measured). Sharing cannot hide a treatment from the read: on 264 `BillingTreatment`'s
organization-wide default is public (`BillingTreatmentItem` is controlled by its parent, `LegalEntity`
is private), so "no treatment" means none exists. The modal's currency list is hardcoded (USD, EUR, GBP, CAD, AUD, JPY, CHF).

## Do not

- Do **not** add `classes/` to `.prettierignore` — it would exempt the 25 hand-authored
  files (including every test) from formatting enforcement.
- Do **not** treat a re-run of the generator as a maintenance step; its source is absent.
  Behavior is guarded offline by `tests/test_build_billing_ui_module.py`.
