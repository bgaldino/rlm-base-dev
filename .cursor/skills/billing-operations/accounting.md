# Billing Operations — Legal Entities, Accounting Periods and the Ledger

Read this when setting up legal entities, accounting periods, ledger accounts or journal
rules, or closing a period. Parent: [SKILL.md](SKILL.md). A read of Help; not measured here.

Licensing varies by record type: legal entity accounting periods and corporate-currency
amounts cover invoices and credit memos with Advanced or Billing licenses and payments,
refunds and debit memos with the Billing license only; transaction journals need the
Billing license [Help: `ind.billing_setup_financial_accounting_features`]. Confirm first.

## Legal entities

A legal entity models how the organization is structured and governs billing treatments,
tax treatments, finance periods and finance books. Create each one Active; its currency
can't be edited after creation in a multi-currency org
[Help: `ind.billing_legal_entities_manage`, `ind.billing_create_legal_entities`].

Where the legal entity comes from [Help: `ind.billing_legal_entity_default`]:

- Billing schedule groups: the order item's legal entity, else the order's, else the org
  default legal entity.
- Billing transactions: filled automatically from their source; editing has
  considerations listed in the article.

Decision: one entity is enough when billing and tax treatments do not vary; add entities
when tax locations, currencies or ledgers differ, since treatment selection of Legal Entity
is per entity ([billing-setup](../billing-setup/SKILL.md) → treatments, [tax.md](tax.md))
[inferred from Help]. Email preferences resolve billing account first, then legal entity
[Help: `ind.billing_invoice_pdf_document_delivery_through_email`].

## Accounting periods

- Create **accounting periods** with start and end dates and a financial year, avoiding
  overlaps and gaps.
- Create a **legal entity accounting period** per entity per period; its status can only be
  Open at creation. Transactions are assigned to the entity's period
  [Help: `ind.billing_accounting_periods_explain`,
  `ind.billing_legal_entity_accounting_periods_create`].
- Permission sets: Accounts Receivables Admin to create; Accounts Receivables Admin and
  Data Pipelines Base User to close or reopen
  [Help: `ind.billing_legal_entity_accounting_periods_create`,
  `ind.billing_legal_entity_accounting_periods_close`,
  `ind.billing_legal_entity_accounting_period_reopen`].

### Close and reopen

Before closing: enable Data Pipelines, turn on Create Transaction Journals for
Transactions and for Foreign Exchange Gains or Losses (with their ledger accounts), select
the default Data Processing Engine definition for closing, and for multiple currencies
set dated exchange rates (run data sync after deleting one)
[Help: `ind.billing_legal_entity_accounting_periods_close`]. Closing runs up to three Data
Processing Engine definitions, depending on the org's licenses; closing copies closing
balances as the next period's opening balances
[Help: `ind.billing_legal_entity_accounting_period_closure_importance`].
Reopen to reconcile; it also removes unrealized foreign exchange journals where that
license applies [Help: `ind.billing_legal_entity_accounting_period_reopen`]. General
ledger accounts created before Winter '26 have no Type; set it by hand or opening and
closing balances cannot be computed [Help: `ind.billing_general_ledger_accounts_create`].

## Chart of accounts, rules and journals

1. **General ledger accounts**: accounting name, unique code, the financial statement they
   feed (such as Income Statement or Balance Sheet)
   [Help: `ind.billing_general_ledger_accounts_create`].
2. **Assignment rules**: one per legal entity and transaction type, with a priority when
   several exist; equal priorities all apply. Each rule's entries name credit and debit
   accounts and criteria [Help: `ind.billing_general_ledger_account_assignment_rules_create`,
   `ind.billing_general_ledger_account_assignment_rules_criteria`].
3. **Settings**: turn on Create Transaction Journals for Transactions
   [Help: `ind.billing_setup_financial_accounting_features`].
4. **Journals** are created as dual entries (a debit and a credit) when [Help:
   `ind.billing_general_ledger_results`]:
   - an invoice, credit memo or their lines and taxes change to Posted, Voided or Canceled;
   - a credit memo is applied to an invoice;
   - a payment or refund becomes Processed, and when payment lines for invoices or refund
     line payments are created;
   - debit memo lines are created.

Journals are meant to be integrated with the customer's accounting system for financial
statements [Help: `ind.billing_general_ledger_results`]. Ask whether Salesforce is the
ledger of record or only a sub-ledger feed [inferred from Help].

Period summaries per ledger account and period are created during closure by data
processing definitions, or by hand while the period is Open
[Help: `ind.billing_general_ledger_accounting_period_summary_create`]. Foreign exchange
realized and unrealized gain or loss journals have their own use cases
[Help: `ind.billing_fgn_exch_realized_gains_losses_use_case`,
`ind.billing_fgn_exch_unrealized_gains_losses_use_case`], and amounts can be stored in
transactional, functional and corporate currency
[Help: `ind.billing_transaction_amounts_corporate_currency`].

## Revenue recognition

The 264 Help snapshot's Billing area describes financial accounting (periods, ledger accounts,
journals) and no revenue recognition schedules or deferred-revenue waterfall. Do not promise
recognition from this product; ask where the customer's recognition system of record lives.
This is an inference from reading the Billing article list, not from a product statement
[inferred from Help].

## What the repo ships

`qb-billing` loads the ledger accounts and assignment rules, plus accounting periods and
legal entity accounting periods; it reads the legal entities that `qb-tax` creates.
`deploy_billing_id_settings` sets the org defaults. `qb-accounting` is reference data
with the same ledger accounts and rules plus an empty journal entry rules file and 11
billing batch filter criteria rows; no CCI task loads it
[Repo: `datasets/sfdmu/qb/en-US/qb-billing/README.md`,
`datasets/sfdmu/qb/en-US/qb-tax/README.md`,
`datasets/sfdmu/qb/en-US/qb-accounting/README.md`, `docs/references/repository-layout.md`,
`billing-setup/shipped-billing.md`]. That journals appear correctly on a posted invoice
for the repo's rules: not measured.

## Read-backs

```sql
SELECT Id, Name, Status FROM LegalEntity
SELECT Id, LegalEntityId, AccountingPeriodId, Status FROM LegalEntyAccountingPeriod
SELECT Id, Name, AccountingCode FROM GeneralLedgerAccount
SELECT Id, Name, LegalEntityId FROM GeneralLedgerAcctAsgntRule
SELECT Id, ActivityDate FROM TransactionJournal
SELECT Id, LegalEntityAccountingPeriodId FROM GeneralLdgrAcctPrdSummary
```

Check: every legal entity used by a treatment has an Open period covering the invoice date;
each transaction type per entity has an assignment rule; a posted invoice produces a
balanced pair of journals; a closed period's closing balances become the next period's
opening balances [Help: `ind.billing_legal_entity_accounting_period_closure_importance`]
(behavior of postings into a closed period: not measured).
