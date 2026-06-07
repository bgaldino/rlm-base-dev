---
article_id: ind.billing_fgn_exch_unrealized_gains_losses_use_case.htm
title: "Example: Automatically Capture Unrealized Foreign Exchange Unrealized Gains or Losses"
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_fgn_exch_unrealized_gains_losses_use_case.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Example: Automatically Capture Unrealized Foreign Exchange Unrealized Gains or Losses

Explore an example to understand how to a set up general ledger accounts on the Salesforce org's default general ledger accounts and create dual transaction journals and reversal transaction journals to capture unrealized gains or losses amount of the invoices during legal entity accounting period closure.

Smartbytes Scenario: Initial Setup and Configuration

Smartbytes is a US based large enterprise company with multiple legal entities. Their Billing Admin turns on Create Transaction Journals for Transactions, Create Transaction Journals for Foreign Exchange Gains or Losses, enables advanced currency management, and edits dated conversion rates in their Salesforce org. Then, their Accounting Admin creates the general ledger accounts with type as Others for unrealized gains, unrealized losses, and account receivables, and sets the accounts as their Salesforce org's defaults.

Unrealized Gain General Ledger Account: 01-800-8000 Unrealized Gain
Unrealized Losses General Ledger Account: 01-800-8001 Unrealized Loss
Account Receivable General Ledger Account: 01-100-1001 Accounts Receivable
Foreign Exchange Unrealized Gain or Loss Calculation

Let's look at a specific transaction to see how foreign exchange unrealized gains or losses are calculated.

Invoice creation: On invoice date August 27, 2025, Smartbytes creates an invoice for their Indian customer with an invoice's balance of 10,000 INR.

The system automatically converts the balance to the corporate currency (USD) using the conversion rate on the invoice date.

Dated conversion rate on the invoice date: 1 USD = 87.66 INR
Corporate currency equivalent of the balance amount on August 27, 2025 = 114.07 USD

Legal entity accounting period closure: The INR-2025-2026-August1-August31 legal entity accounting period is closed on August 31, 2025.

Dated conversion rate on the end date of the legal entity accounting period: 1 USD = 88.17 INR
Corporate currency equivalent of the balance amount on August 31, 2025 = 113.417 USD

Foreign exchange unrealized gain or loss calculation: The foreign exchange unrealized gains or losses are calculated as the difference between the corporate currency equivalent of the balance amount on August 31, 2025, and the corporate currency equivalent of the balance amount on August 27, 2025. The loss recorded for this transaction is 0.66 USD.

Automatic Transaction Journal Creation

When the legal entity accounting period is closed, dual transaction journals are automatically created to record the foreign exchange unrealized loss of 0.66 USD and dual reversal transaction journals are also created to record the same for the start date of next legal entity accounting period.

A transaction journal is created for the 01-800-8001 Unrealized Loss account with the unrealized loss amount as the debit amount for INR-2025-2026-August1-August31 legal entity accounting period..
A transaction journal is created for the 01-100-1001 Accounts Receivable account with the unrealized loss amount as the credit amount for INR-2025-2026-August1-August31 legal entity accounting period.
A reversal transaction journal is created for the 01-800-8001 Unrealized Loss account with the unrealized loss amount as the credit amount for INR-2025-2026-September1-September30 legal entity accounting period.
A reversal transaction journal is created for the 01-100-1001 Accounts Receivable account with the unrealized loss amount as the debit amount for INR-2025-2026-September1-September30 legal entity accounting period.
