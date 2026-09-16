---
article_id: ind.billing_financial_accounting.htm
title: Manage Financial Accounting in Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_financial_accounting.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing.htm
fetched_at: 2026-09-04
---

# Manage Financial Accounting in Revenue Management

Streamline the financial accounting process for your organization with accounting periods for legal entities, chart of accounts, journal entries for your billing transactions, and by capturing transaction amounts in corporate currency.

Financial Accounting Data Model in Revenue Management
The Financial Accounting data model depicts the objects and their relationships to record and manage the financial accounting process for Invoice, Credit Memo, Payment, and Refund records. This process includes defining accounting periods, setting up a chart of accounts, and creating dual journal entries for your legal entities.
Legal Entities
A legal entity defines how your organization is structured. In Revenue Management, you can create multiple legal entities, which define the billing and tax information for an order product. If you have customers and business segments in different tax locations, use multiple legal entities to govern the use of tax treatments, billing treatments, finance periods, and finance books.
Manage Accounting Periods in Revenue Management
Accounting periods help your company organize and monitor financial performance by defining specific time frames for business reports. Ensure accurate financial reporting and streamlined record-keeping by associating billing transactions to legal entity accounting periods.
Manage Chart of Accounts and Transaction Journals in Revenue Management
Set up a chart of accounts for your legal entities by creating general ledger accounts. Assign appropriate general ledger accounts to transaction journals by setting up general ledger account assignment rules. Automatically generate dual transaction journals based on the configuration for the billing transaction type and criteria in the general ledger account assignment rule.
Foreign Exchange Realized Gains and Losses
Automatically create dual transaction journals for foreign exchange gains or losses when payments and credit memos are created and applied to invoices. The invoices can be fully or partially settled. Foreign exchange gains and losses transaction journals help with income statements during corporate accounting, which ensures accurate measurement of financial performance.
Legal Entity Accounting Periods Closure and Reopening
Close legal entity accounting periods and accounting periods after their duration ends to maintain data integrity. Reopen legal entity accounting periods to reconcile receivable transactions.
Capture Transaction Amounts in Multiple Currencies
Manage multi-currency billing transactions by viewing amounts in transactional currency, functional currency, and corporate currency.
