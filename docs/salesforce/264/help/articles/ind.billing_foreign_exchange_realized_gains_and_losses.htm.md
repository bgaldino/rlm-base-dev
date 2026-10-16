---
article_id: ind.billing_foreign_exchange_realized_gains_and_losses.htm
title: Foreign Exchange Realized Gains and Losses
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_foreign_exchange_realized_gains_and_losses.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_financial_accounting.htm
fetched_at: 2026-09-04
---

# Foreign Exchange Realized Gains and Losses

Automatically create dual transaction journals for foreign exchange gains or losses when payments and credit memos are created and applied to invoices. The invoices can be fully or partially settled. Foreign exchange gains and losses transaction journals help with income statements during corporate accounting, which ensures accurate measurement of financial performance.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.

To enable Foreign Exchange Gain or Loss calculations, your Billing admin must turn on the Create Transaction Journals for Transactions and Create Transaction Journals for Foreign Exchange Gains or Losses features, and select the realized gain, realized loss, and account receivable general ledger accounts. See Set Up Financial Accounting Features.

WARNING If you've already created transaction journals that record realized foreign exchange gains or losses, don't modify the corporate currency or the dated conversion rates. Changing these impacts the accuracy of existing transaction journals.

The foreign exchange realized gains and losses are calculated based on the difference between the corporate currency conversion rates on the invoice date and the payment's effective date. This difference amount is populated as the debit or credit amounts of the transaction journals. All the amount values for the foreign exchange realized gains and losses transaction journals are in corporate currency.

In case of partial invoice settlement, unrealized gain and loss calculations are calculated during the legal entity accounting period closure. Unrealized and reversal transaction journals are created for the remaining invoice balance. See Legal Entity Accounting Period Closure Procedure

Example: Automatically Capture Foreign Exchange Realized Gains or Losses
Explore an example to understand how general ledger accounts are set up and how dual transaction journals are created when Payments or Credit Memo records are created and applied to the invoices.
