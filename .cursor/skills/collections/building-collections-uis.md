# Collections — Building Apex and LWC That Read Collections Data

Read this when writing Apex or LWC over plans, invoices, cases or payments. Parent:
[SKILL.md](SKILL.md). Working examples: `RLM_CollectionsDashboardController`,
`RLM_OnAccountBillingController`, `RLM_InvoiceSummaryController`,
`RLM_BillingCaseMetricsController` [Repo: unpackaged/post_billing_ui/classes/]. Security hygiene: `apex-security-hardening`.

## Refusal signatures

- Dynamic `Database.query` in USER_MODE on a refused object throws `QueryException: sObject type
  '<X>' is not supported`; on a refused field, `No such column '<f>'`. Checked as Login As personas. [Measured: 2026-11-25 to 2026-11-26, 264, fresh scratch build]
- An inline `[... WITH USER_MODE]` query **with a bind** on a refused object threw
  `QueryException: Variable does not exist: tmpVar1`: the text is misleading and means refused. [Measured: 2026-11-26, 264, ent-sb0 scratch build]
- An inline `COUNT()` on a refused object raised `SecurityException`. [Measured: 2026-11-26, 264, ent-sb0 scratch build]
- Which type each inline shape raises is not fully mapped, so catch `Exception` around a required
  read. [Open: which exception class does each inline query shape raise on a refused object? As a Login As persona, run each shape and log the class]
- **"No such column" has two causes.** A single-currency org has no `CurrencyIsoCode` on Invoice or
  Payment, and querying it throws the same text [Open: is CurrencyIsoCode absent from Invoice and Payment on a single-currency org? Describe both on a single-currency 264 scratch org]. Check describe before calling it a refusal, filter
  on currency only where the object has the field, and never offer a currency filter that cannot
  apply.

## Unavailable, never zero

- A refused or failed optional part shows "Unavailable", and any total that includes it is
  unavailable too.
- A required read fails with one fixed sentence; the raw text goes to the debug log only.
- A feature absent per describe, or an object with no matching rows, is a real 0.
- Three states: **refused** ("You don't have access to ..." sends the user to an admin), **failed**
  ("... could not be loaded. Refresh the page to try again." must not send a fully granted user to an
  admin) and **too many** (below). A wire or imperative error is always failed.
- Promise-to-pay reads go through the CollectionPlan chain; a refused read gives a visible segment
  note ("Promises to pay could not be read and are not shown."), never a zero. Same for debit memos
  and disputes. [Repo: unpackaged/post_billing_ui/lwc/rlmInvoiceSummaryBar/__tests__/rlmInvoiceSummaryBar.test.js]
- A collections-first status pill (In Collections, Written Off, Delinquent, In Dispute, Partially
  Paid, Overdue) cannot know any status when the plan read is refused, so it reads "Status
  Unavailable". [Repo: unpackaged/post_billing_ui/lwc/rlmAccountBalanceCard/rlmAccountBalanceCard.js]
  [Repo: unpackaged/post_billing_ui/lwc/rlmOnAccountBilling/rlmOnAccountBilling.js]
- Hidden by sharing is not absent: a USER_MODE read omits hidden rows, so "id missing from the
  result" means "not visible"; the repo's `RLM_AccountNames.Result.unavailable(id)` is the test for
  "hidden or refused, not absent" [Repo: unpackaged/post_billing_ui/classes/RLM_AccountNames.cls].

## Governor limits

- **SUM costs one query row per row summed**, with or without GROUP BY; `COUNT()` and `COUNT(Id)` cost
  one. Count first, then sum only within the bound. [Measured: 2026-11-25 to 2026-11-26, 264, fresh scratch build]
- **The 50,000 query-row `LimitException` cannot be caught** and fails every card at once. Bound
  every read to min(10,000, rows left less 1,000), plus one row to detect overflow; a call then stays
  under 49,250 rows whatever the data [Repo: unpackaged/post_billing_ui/README.md]. Overflow shows "Too many records to total/list here." with
  narrowing advice built only from the filters the reads actually applied.
- **List-form SOQL for loops are charged for chunks fetched ahead**: breaking after the first chunk of
  a 500-row result was charged 400 rows. A single-row loop over `Database.query` is charged every row;
  `queryWithBinds` cannot drive a list-form loop (compile error). [Measured: 2026-11-26, 264, fresh scratch build]
- **Heap (6 MB synchronous)**: 10,001 Invoice rows with 5 fields about 1.34 MB; 10,001 Case rows with
  Id, CaseNumber and AccountId about 1.0 MB. **Case text is the trap**: `Case.Description` can be
  32,000 characters, 200 cases take 6.4 MB as a list and a for loop peaks at 6.46 MB. Read ids first,
  pick each account's newest open case, then read only those texts 50 per query keeping a
  200-character excerpt (1.65 MB peak). A top-ten balance roll-up over 10,000 invoices and 10,000
  accounts peaked at 1.68 MB with two maps and 0.78 MB after releasing rows (862 ms CPU). [Measured: 2026-11-25 to 2026-11-26, 264, fresh scratch build]
- **Short lists say they are partial**: read one row past what is shown, then "Showing the first N of
  more than N". The account picker replaced a silent 500-account cut with a notice and a USER_MODE
  name search (first 50 matches, two-character minimum, wildcards escaped; "1_7" matched nothing
  literally). [Measured: 2026-11-26, 264, fresh scratch build, 505 accounts, live Chrome]

## Currency

- In a multi-currency org **SUM returns the corporate-converted amount even when filtered or grouped
  to one currency**: 100 USD plus 100 EUR returned 214.11, and the EUR group 114.11 [Measured: 2026-11-26, 264, fresh scratch build].
  `convertCurrency(Balance)` works in row reads, `SUM(convertCurrency(Balance))` is accepted, and
  `convertCurrency(SUM(...))` is rejected.
- Read amounts as rows with `CurrencyIsoCode` and sum in Apex per currency; the dashboard shows one
  currency at a time. If you must convert, use the dated rate for the day if the currency has one,
  else the standard rate; never guess 1 [Repo: unpackaged/post_billing_ui/classes/RLM_OnAccountBillingController.cls]. A
  SYSTEM_MODE `COUNT()` that returns only a boolean (do dated rates exist) separates "refused" from
  "none". `DatedConversionRate` held 0 rows with ACM off [Measured: 2026-11-26, 264, fresh scratch build].
- `CollectionPlan.TotalInvoiceBalance` is not createable or updateable, so tests cannot seed plan
  amounts [Measured: 2026-11-27, 264, fresh scratch build, API 68.0].

## Dates and labels

- Date-only values (promise dates, task due dates, invoice dates) must render as calendar dates;
  converting through the browser time zone shifts them by a day, and bucketing by local month shifts
  a period table. [Open: render a promise date in a browser outside UTC on a live 264 org and compare it to the stored date]
- Label columns with names, never record Ids. A `lightning-datatable` `url` column with value `'#'`
  renders as `https://#`, a broken link. [Measured: 2026-11-27, 264, ent-sb0 scratch build, live UI]
- Sort the Critical list by `DueDate`, not `DaysInvoiceOverdue`.

## Testing

`Invoice` cannot be inserted by DML and `Balance` is not updateable, so Apex tests assert query shape
or run on an org with billing runs. Persona tests: assign the sets to a Minimum Access user and use
`System.runAs` plus `UserRecordAccess`; Login As for the UI.
