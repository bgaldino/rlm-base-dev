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
licenses, the managed Billing Collections and Recovery Specialist set and `RLM_CollectionsDashboard`,
nothing else: the set is self-sufficient beside the specialist set, so the dashboard works with
`billing_ui` on and `collections` off (`RLM_CollectionsUI`, which ships with `collections`, is for the
Collection Plan record page, not the dashboard). The specialist set reads accounts, currencies,
invoices, payment schedules, collection plans and plan items; `RLM_CollectionsDashboard` adds the
tab, the controller and, read-only, every read the controller makes that the specialist set lacks
(measured on 264, 2026-11-26, todo 435, as a Minimum Access user holding only those two sets): read
on Case and Payment; Case AccountId/Subject/Description/Reason; CollectionPlan
AccountId/Duedate/ClosedDate/DaysPastDue; CollectionPlanItem.InvoiceId; Task ActivityDate/WhatId
(the platform adds Event.WhatId with Task.WhatId, so the file lists it).

Debit memos stay unread, by owner decision: reading `DebitMemo` needs the Manage Debit Memos user
permission (measured on 264), a manage permission too broad for a read-only collections role, so
the set does not grant it.

The dashboard shows anything it could not read as not available, never as a zero or an empty
"none" (todo 435), and says why. Every unavailable section carries a reason: `refused` when the user
may not read it (a USER_MODE read throws "sObject type ... is not supported" or "No such column ...",
measured on 264), shown as "You don't have access to ...", or `failed` for any other error, shown as
"... could not be loaded. Refresh the page to try again.", so a fully granted user hitting a
transient failure is not sent to an administrator. A failed call (a wire or imperative error) is
always `failed`.

Every read a figure or list is built from is bounded (`boundedRows` in the controller; sums are read
as rows through `boundedSum`), so a large org gets a section that says it has too many records instead of a figure
from a cut-off read, or the per-transaction limit of 50,000 query rows, whose `LimitException` no
catch block can handle and which would fail the whole call (every card, or every worklist tab, at
once). Each read may take the lesser of `ROW_CAP` (10,000 rows) and what the call has left less
`ROW_HEADROOM` (1,000 rows); one row more makes its section unavailable as `tooMany`. The page says
"Too many records to total here." for a figure and "Too many records to list here." for a list, then
suggests the filters that narrow that section and are not already in use ("Choose an account or
currency to narrow it.", "Choose an account ...", "Choose a currency ..."), or, when every such filter
is in use, "Too many records to total here even for this account and currency." Which filters narrow a
section is what the controller reports its reads applied (`filtersByKey` on the cards, `filtersByTab`
on the worklist, `filters` on the promises, tasks, plans and progress): a filter is listed only where
the object read has the field, so a single-currency org, whose Invoice and Payment have no
`CurrencyIsoCode`, is never told to choose a currency. The Disputed tab reports the filters of the read
that had too many: its open cases follow the account only, its invoice rollup the currency too.
Progress follows the shown currency (it totals amounts), and the user's own plans follow no filter. A read whose allowance is
zero runs no query and is too many at once. The guarantee is per call, not per read: whatever the
data, a call stays under 49,250 query rows. A bounded read takes at most its allowance plus one row,
so the bounded reads of a call stop at 49,001 query rows, after which every later bounded read has
no allowance and is reported as too many without querying; the only fixed reads after them are the
payment count (one row) and the plan tasks (at most 201 rows). The short lists show a fixed number
of rows: the 200 most overdue critical follow-up invoices, the 10 largest High-Value balances, the
200 accounts with the newest open cases on the Disputed tab, the 200 latest-due plan tasks and the
user's 50 soonest-due plans. Each knows when there are more (its read goes one row past what it
shows; High-Value ranks every qualifying account; Disputed reads open cases until the account past
the listed ones turns up), and
then says "Showing the first N of more than N" with its order and the filters that narrow which rows
it lists (only the account, for Disputed), with "N+" as the count where the list shows one, instead
of reading as complete. The Critical list is read, ordered and shown by one key, the due date:
invoices of 2000 or more due over 30 days ago, earliest due first, with days overdue counted from the
due date. `Invoice.DaysInvoiceOverdue` is not used: on 264 (measured 2026-11-26) it is a
platform-calculated, nillable Integer that was null on every Posted invoice in the org checked (none
there was past due), so ordering on it would put a null-days invoice after others whatever its due
date. The reads with their own small `LIMIT` (those short lists, the account
options and the account search), the active currencies and the payment count (`COUNT(Id)`) are not
bounded further; the account names a tab looks up and the Disputed tab's case text
(`readDisputeReasons`) are checked against the same allowance before they run, and the High-Value tab
looks up names and plans for its ten listed accounts only.

The account filter lists the first 500 accounts by name (`ACCOUNT_OPTION_ROWS`). With more, it says
"Showing the first 500 accounts by name. Search for an account to find another." and offers a search:
the typed text (two characters or more, matched literally) finds accounts whose name contains it,
the first 50 by name (`searchAccounts`, USER_MODE), and says when there are more matches. The chosen
account stays in the list whatever a search finds. When the accounts cannot be read, the filter offers
only "All Accounts" (the dashboard still loads, unfiltered, with no error toast) and says why: "You
don't have access to accounts." or "Accounts could not be loaded. Refresh the page to try again.",
with no search; a refused search says "You don't have access to accounts." too. The account options,
the currency options and the default currency are loaded as separate calls, so a failed currency
list falls back to the default currency alone without touching the accounts, and the reverse.

Every invoice read counts the same receivable invoices: Posted, with a balance (`RECEIVABLE_INVOICE`,
`Status = 'Posted' AND Balance > 0`, the condition the cards have always used). The cards and their
aging, the Critical and High-Value tabs and the Disputed tab's rollup each build their WHERE clause
from it (`receivableInvoiceWhere`), so a Draft, Pending or Canceled invoice is in no figure or list,
and a figure on one part of the page cannot count invoices another leaves out. Before this, Critical
had no status filter, the Disputed rollup counted every status and High-Value excluded only Paid,
Closed and Canceled. Whether a Draft invoice carries a balance could not be observed: on the 264 org
checked (2026-11-26) Invoice is not createable through DML and the only invoices were Posted;
`everyInvoiceRead_countsOnlyPostedInvoicesWithABalance` therefore checks the SOQL each invoice read
executed, recorded where it runs (only while a test runs).

The page shows one currency at a time and converts nothing. On a multi-currency org the currency
filter offers the active currencies, with no "All Currencies", and starts on the user's default
currency (else the first one offered); every amount read is filtered to that currency: the cards and
their aging, the Critical and High-Value lists, the Disputed tab's invoice rollup, payment promises
and progress ("No collection plan data in USD." when it has none). The user's own plans are a list,
not a total: every plan is listed, each amount in its plan's own currency. The amounts are formatted in it, and the page says "Showing amounts in
EUR only. Choose another currency to see its amounts." A single-currency org keeps "All Currencies"
and reads and shows its amounts as they are, with no note. Measured on 264 (2026-11-26), on a
multi-currency org (USD corporate; AUD, CAD, CHF, EUR, GBP and JPY active), with test payments rolled
back: a `SUM()` over a currency field returns the corporate currency, even grouped by
`CurrencyIsoCode` (100 USD and 100 EUR summed to 214.11 USD, the EUR group alone to 114.11) and even
filtered to one currency (`SUM(Amount)` and `SUM(Balance)` of a 100 EUR payment `WHERE CurrencyIsoCode
= 'EUR'` both returned 114.11, not 100). So amounts are read as rows and added in Apex
(`boundedSum`), never as a `SUM()`, and no figure mixes currencies or shows one currency's amounts in
another. The Critical list's threshold is 2000 in the shown currency. Every section says which
currency its answer is in, and the page formats its amounts in that currency, showing none before the
answer arrives.

An account name the user may not read shows "Not available" on the worklist and plan rows, as an
unread plan or promise date does: when the Account read is refused or fails, and when the account is
missing from it because sharing hides it from the user (Account.Name is required, so a missing account
is a hidden one), as plain text with no link to the account, whose page the user could not open. A row
with no account at all shows "—". The Critical list's bill-to contact follows the same rule: its name,
read in USER_MODE for the listed rows in one batch, "Not available" as plain text when it is refused,
fails or the contact is hidden, "—" with no contact. A collection plan is labelled by its name, not its
record Id, on the worklist and in the plan tasks list (no column or tooltip shows a record Id). Measured on 264 (2026-11-26): the collections user reads `Contact.Name`, so
`RLM_CollectionsDashboard` grants nothing more for it.

Query-row costs measured on 264 (2026-11-26): a `SUM` aggregate costs a query row for every row it
adds up, with or without `GROUP BY`, while `COUNT()` and `COUNT(Id)` cost one. Sums are read as rows
and added in Apex (see the currency paragraph above), which costs the same rows. A SOQL for loop over a list (`for
(List<Case> chunk : ...)`) fetches 200-row chunks and is charged for what it fetched: one that stopped
after its first chunk of a 500-row result was charged 400 rows, not 500 (measured 2026-11-26); a loop
over single rows of `Database.query` or `Database.queryWithBinds` was charged all 500. The Disputed
tab's open-case read is such a list loop, limited to its allowance plus one row like any bounded read:
it stops at the first account past the 200 listed ones, so an org with more open cases than the row
cap still gets its list, and it is too many only when the allowance runs out before that account
turns up.

Heap, measured on the same org against the 6 MB synchronous limit, for these reads:

- **Invoice reads** (unpaid, high-value and disputed invoices): 10,001 rows with the five fields they
  select take about 1.34 MB.
- **The open-case read of the Disputed tab** selects three fields (`Id`, `CaseNumber`, `AccountId`; no
  text) and holds one 200-row chunk at a time plus the listed accounts' cases: 10,001 rows of those
  fields took about 1.0 MB, so a chunk is a small part of that.
- **Case text** (subject, description, reason): a description can be 32,000 characters. 200 cases at
  that length take 6.4 MB as one list, over the limit, and a one-row SOQL for loop peaks at the same
  6.46 MB because it fetches 200 rows at a time. So the open-case read carries no text: each account's
  newest open case is picked from ids, and only those cases' text is read, 50 per query
  (`DESCRIPTION_BATCH`), keeping a 200-character excerpt. Read that way, 200 cases at the maximum
  length peaked at 1.65 MB, and the excerpts kept took 48 KB.
- **The Disputed tab** lists the 200 accounts with the newest open cases (`DISPUTED_ROWS`) and says
  when there are more, so its case text never passes that measured 200.
- **The High-Value roll-up** at the read cap (10,000 invoice rows on 10,000 accounts, every account
  qualifying), its structures rebuilt in anonymous Apex from synthetic rows: the rows took 1.12 MB, the
  rows with its two 10,000-entry per-account maps 1.68 MB (the peak), the maps alone 0.56 MB once the
  rows are released, and 0.78 MB after the top-10 pick, in 862 ms of CPU including building the rows.
  The roll-up drops the rows once it has the sums and picks the ten largest in one pass, building a row
  for those ten only; `addHighValueDelinquents_atTheReadCap_listsTheTenLargest` runs the real method at
  that size within the test's limits.

Each invoice and case read is released before the next large read in its tab: on the Disputed tab, only
the 200 listed accounts' cases are kept from the open-case read (each chunk is dropped as the loop
moves on) through the case text, name and invoice reads. The payment schedule
and schedule item reads were not measured; they select two and three short fields.

Figures: an unread invoice, debit memo or payment amount comes back null and listed in the cards'
`unavailable` with its `unavailableReason` (unread payment schedule amounts make
`PaymentPromiseSummary.unavailable` true instead, with its reason); the Debit Memos line of the
total balance reads "—" and the Total Balance is a partial total that says it excludes debit memos
and why (likewise for unapplied credits and payments). Unpaid invoices are its main component: when
they could not be read there is no total at all, and the Total Balance shows "—" with the invoices'
reason. The unapplied payment count is its own key: if only the count
could not be read, only the count shows "—" and the balance stays in the total. Payment promises,
plan tasks and the user's plans come back as wrappers with an explicit `unavailable` flag and reason;
progress carries the same flag; a worklist tab that could not be read is listed in
`WorklistData.unavailable` and says so instead of "No items in this view". A failure anywhere in
building a tab, not only in its first read, marks that tab unavailable and drops any rows it had
added; the other tabs are still built. Inside a tab that was
read, a row whose collection plan (or, on the Disputed tab, promise-to-pay date) could not be looked
up shows "Not available" rather than "—", and offers no Create Collection Plan, since a plan may
exist. A plan that was read and is absent shows "—" with Create; a USER_MODE read cannot tell a plan that
does not exist from one sharing hides from the user, so a hidden plan also reads as absent there.

The page gives every section (each card, the total, payment promises, progress, plan tasks, my plans
and each worklist tab) one state, derived in one place (`sections` in `rlmCollectionsDashboard.js`):
loading until that section's answer for the current filters arrives, then ready or unavailable with
its reason. Figures, counts, rows and "none" messages render from `ready` only, so nothing shows
$0.00 or "No items" before the data arrives, and an account or currency change puts the sections
that read it back to loading. The worklist is read through its wire alone (no second, imperative
call that could land out of order). There is no page-wide error state: a failed card read leaves
the other sections showing what they read. Each worklist tab shows exactly what its own reads
return: its rows, or "No items in this view" when it was read and has none, or unavailable with its
reason. Date-only values (task due dates, promise-to-pay
dates) are calendar dates and display as such in every time zone. The
payment reads filter on `CurrencyIsoCode` only where Payment has it (a multi-currency org), and a
"No such column" error counts as a refusal only for a field the org has; an absent field is a failure.
`RLM_BillingUIAccessTest` runs every controller read as this user, and
`RLM_CollectionsDashboardControllerTest` loads the dashboard as this user and as the same user
without the set. The build assigns the set to the running user only.

### Known limitations

Left as they are on purpose (todo 435: a review finding gets code only when it is a regression, or a
wrong figure or a misleading or empty-looking state on the normal path):

- No total across currencies. A multi-currency org shows one currency at a time; to see another
  currency's receivables, choose it.
- A collection plan that sharing hides from the user reads as no plan ("—", with Create), since a
  USER_MODE read cannot tell a hidden plan from a missing one.
- The account filter lists the first 500 accounts by name; others are found by the search, which
  returns the first 50 matches.
- Lists stop at their row counts (the worklist tabs, plan tasks, my plans) and say "Showing the first
  N ..." rather than paging.
- A figure past the row bound (10,000 rows, or what the call has left) is shown as too many records
  rather than a partial total.

## Do not

- Do **not** add `classes/` to `.prettierignore` — it would exempt the 25 hand-authored
  files (including every test) from formatting enforcement.
- Do **not** treat a re-run of the generator as a maintenance step; its source is absent.
  Behavior is guarded offline by `tests/test_build_billing_ui_module.py`.
