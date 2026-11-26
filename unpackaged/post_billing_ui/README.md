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
  into this directory (per `FLEXIPAGE_MAP`). One has since moved here:
  `flexipages/RLM_Collections_Dashboard` ships in this bundle with its tab, see
  **Collections Dashboard** below.

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

`rlmBillingScheduleGroupModal` calls `RLM_BillingScheduleGroupService`, which invokes
the standard `createBillingSchedulesFromTrxn` action. The payload carries the chosen
legal entity (`LegalEntityId__std`), the billing treatment of that entity for the chosen
Advance or Arrears timing, or for a one-time charge the entity's treatment in the
charge's currency (`BillingTreatmentId__std`; the timing tags themselves are rejected by
the action), a billing term when a caller gives one (`BillingTerm__std`; the modal has
no input for it) and a shipping city (`ShippingCity__std`: the account's `ShippingCity`,
else the `billingCity` the caller submitted, which create requires). The account sent
(`AccountId__std`) is the account page the modal opened on (`pageAccountId`) when it is
the billing account's own or is linked to it through `AccountBillingAccount`; with no
page account, the billing account's own account, else its oldest link (create refuses
when it has neither). `getAccountBillingInfo` returns the billing city of that same
account (the page account's when the billing account is reached through a link), so the
submitted city matches the account sent. Treatments considered are the oldest-first
active, non-milestone, billable ones of the legal entity in the charge's currency,
counting only their active items typed Advance or Arrears (a None-type item is ignored;
several items of one timing are fine). A recurring charge takes the first treatment
whose items all bill in the chosen timing; one with items in both timings is ambiguous
and skipped (when it is the only match the refusal says it has items in both timings and
must be split into one treatment per timing, naming it when readable). A one-time charge
(billing term unit OneTime) offers no timing and ignores one if sent, so ambiguity does
not apply: a treatment is still sent (measured: left to itself the platform picked a JPY
treatment of the legal entity for a EUR charge): the first Advance-only treatment, else
the first Arrears-only one, else (last, since what the platform bills for it on a
one-time charge is unmeasured) the first with both timings. The charge currency must be
an active `CurrencyType`, and the legal entity active and visible to the user (as the
picker offers them), or create refuses before the lookup. The treatment read filters on
the charge currency and is capped at 1000 items, oldest first; one row past the cap
shows the read was cut off, and the last treatment read is then dropped when the extra
row belongs to it (it may be cut short). When the page account differs from the billing
account's own, it must be readable (Account read in USER_MODE) and linked to the billing
account; if it is not found, not readable, not linked (link deleted, or a stale cached
`getAccountBillingInfo`) or its link read is refused, create refuses instead of falling
back to the owner (an account that is not linked says to open the billing screen from a
linked account; a read the user is not allowed says to contact an administrator; one not
found or not visible says so). If the treatment read runs past the cap and nothing fits,
the message says the lookup was cut off; a one-time charge also refuses a cut-off read
whose choice is not Advance-only, since an Advance-only treatment may lie past the cap.
It reads `BillingTreatment`, `BillingTreatmentItem`, `LegalEntity`, `CurrencyType` and
`Account.ShippingCity` in USER_MODE. `RLM_BillingUI` grants object read on
`BillingTreatment` and `LegalEntity` (the item follows its master, below) and field read
on the shipping city through the `Account.ShippingAddress` compound grant; the treatment
and item fields it reads (`Status`, `LegalEntityId`, `IsMilestoneBilling`,
`ExcludeFromBilling`, `CurrencyIsoCode`, `CreatedDate`, `BillingType`,
`BillingTreatmentId`) are not permissionable (measured on a 264 scratch org,
2026-11-26), so no `fieldPermissions` rows exist or are possible. The module needs a
multi-currency org: the service reads `CurrencyType` and
`BillingTreatment.CurrencyIsoCode`, which exist only there. `CurrencyType` needs no
grant (`RLM_BillingUIAccessTest` asserts it is readable on a multi-currency org). The
service refuses, with a message naming currency and legal entity (and the timing, in
lower case, for a recurring charge), a charge with no such treatment, including one
whose only treatments are in another currency, before calling the action; it never sends
a treatment of another currency. `BillingTreatmentItem` has no grant of its own: it is a
master-detail child, so its read follows `BillingTreatment` (a grant on it is dropped on
deploy, measured). Sharing cannot hide a treatment from the read: on 264
`BillingTreatment`'s organization-wide default is public (`BillingTreatmentItem` is
controlled by its parent, `LegalEntity` is private), so "no treatment" means none
exists. The modal's currency list is hardcoded (USD, EUR, GBP, CAD, AUD, JPY, CHF).

**Dates (todo 435).** Start Date defaults to today in the user's Salesforce time zone
(`@salesforce/i18n/timeZone`, read through `Intl`), not the browser's and not UTC; the
billing day and month are taken from that same `YYYY-MM-DD` value, and End Date is
calendar math on it (`billingDates.js`), so no date passes through a local or UTC `Date`.
End Date is the end date the platform itself computes for a term-defined line from its start date
and term: the day before the start's day of the month that many months later, that day moved to the
last day of a month that lacks it, with no month-end special case. Measured on a 264 org
(2026-11-26, todo 435) by placing a quote with Place Sales Transaction, lines given a StartDate and
SubscriptionTerm and no EndDate, and reading back the EndDate:

| Start | Term | Platform End Date |
|-------|------|-------------------|
| 2027-02-28 | 1 Annual | 2028-02-27 (priced as 0.9973 of a year) |
| 2027-02-28 | 12 Months | 2028-02-27 |
| 2027-02-28 | 2 Annual | 2029-02-27 |
| 2027-02-28 | 1 / 3 / 6 Months | 2027-03-27 / 2027-05-27 / 2027-08-27 |
| 2028-02-29 | 1 Annual, 12 Months | 2029-02-27 |
| 2027-01-31 | 1 Annual, 12 Months | 2028-01-30 |
| 2027-01-31 | 1 Month | 2027-02-27 |
| 2027-03-31 | 1 Month | 2027-04-29 |
| 2026-04-30 | 1 Annual | 2027-04-29 |

The 2027-02-28 annual result is the Help's partial-period case
(`ind.pricing_annual_proration_examples_for_leap_years`), not its 28-Feb-2028 full period: the modal
follows what the platform computes. Quarterly and semi-annual units were not measured (no price book
entry on that org uses them) and are computed as 3 and 6 months. Billing periods are only
materialized by an invoice run, which was not run, so whether billing adds a stub for these ends is
not measured. The Jest suite `rlmBillingScheduleGroupModal.dates.test.js`
pins the browser zone through `tests/jest/browser-time-zone-environment.js`.

**Bill-to contact (todo 435).** The action takes the bill-to contact from the billing
account (`BillingAccount.BillToContactId`) and fails without one. `getAccountBillingInfo`
flags it (`billToContactMissing`), the modal blocks Create with a sentence saying to add
one, and create refuses the same case before calling the action. `getAccountBillingInfo` is
cacheable, so the modal shows the cached answer at once and asks the server once per opening
(`refreshApex`): a contact or Billing City added since clears the blocker without waiting for the
cache to expire. `RLM_BillingUI` grants
read on the field; the read also needs Contact read, which the set grants.

## Collections Dashboard

The `RLM_Collections_Dashboard` app page (`rlmCollectionsDashboard`), its tab and the
`RLM_CollectionsDashboard` permission set ship here, with the component and controller they
need, so they deploy with `billing_ui` whether or not `collections` is on. With `collections` on
as well, the UX assembler adds the tab to the Billing - Collections console
(`templates/applications/patches/billing_ui/standard__CollectionConsole.patch.xml`); on an
existing org, deploy this bundle before `assemble_and_deploy_ux`, or the console names a tab the
org does not have.

A collections user who does not hold `RLM_BillingUI` needs the Billing and Billing Advanced
licenses, the managed Billing Collections and Recovery Specialist set, `RLM_CollectionsUI` and
`RLM_CollectionsDashboard`. The specialist set reads accounts, currencies, invoices, payment
schedules and collection plans; `RLM_CollectionsDashboard` adds the tab, the controller and the
reads the dashboard makes that the specialist set lacks (measured on 264, todo 435): read on
Case and Payment, Case AccountId/Subject/Description/Reason, CollectionPlanItem.InvoiceId and
Task ActivityDate/WhatId (the platform adds Event.WhatId with Task.WhatId, so the file lists it).
Without them the controller swallows the refused reads and the cards, disputed worklist and
plan tasks come back empty, which reads as nothing owed.

Debit memos stay unread, by owner decision: reading `DebitMemo` needs the Manage Debit Memos user
permission (measured on 264), a manage permission too broad for a read-only collections role, so
the set does not grant it. The dashboard shows what such a user cannot read as not available
instead of a zero: the Debit Memos line of the total balance reads "—" with "You don't have
access to debit memos.", and the Total Balance says it excludes debit memos. The same rule covers
every figure the dashboard shows (todo 435): a refused invoice, payment, payment schedule or
collection plan read is returned as unavailable (null, or the cards' `unavailable` list, or the
progress `unavailable` flag), never as $0.00. `RLM_BillingUIAccessTest`
runs every controller read as this user, and `RLM_CollectionsDashboardControllerTest` loads the
dashboard as this user and as the same user without the set. The build assigns the set to the
running user only.

## Do not

- Do **not** add `classes/` to `.prettierignore` — it would exempt the 25 hand-authored
  files (including every test) from formatting enforcement.
- Do **not** treat a re-run of the generator as a maintenance step; its source is absent.
  Behavior is guarded offline by `tests/test_build_billing_ui_module.py`.
