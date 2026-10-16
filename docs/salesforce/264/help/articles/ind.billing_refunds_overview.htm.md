---
article_id: ind.billing_refunds_overview.htm
title: Issue Refunds and Settle Balances
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_refunds_overview.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payments.htm
fetched_at: 2026-09-04
---

# Issue Refunds and Settle Balances

A refund returns an amount that a customer no longer owes, such as an overpayment or an available credit balance. Billing issues a refund either automatically, after you cancel or reduce a subscription, or on demand, when you want to settle a customer’s available credit balance by using a credit memo.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
Types of Refunds

Billing supports two types of refunds—referenced refunds and unreferenced (or non-referenced) refunds. They differ by whether the refund references an original payment, how and when the refund is issued, and which payment method receives the funds.

 	REFERENCED REFUND	UNREFERENCED REFUND
How the refund is issued	Automatically	Manually
When the refund is issued	When you cancel or reduce a subscription	When you settle an available credit balance back to the customer’s account.
Refund issued via	The original payment method used on the settled invoice.	A saved payment method resolved from the API request, the credit memo, or the billing account.
Applied to	The credit memo that the subscription change creates.	A credit memo or a credit memo line.
Requirements	The original payment is associated with a payment gateway.	The account has an available credit balance and uses a supported third-party payment gateway.
How Billing Processes Referenced Refunds

When you cancel or reduce a subscription, Billing calculates the refund amount and generates a credit memo to settle the resulting negative invoice. Billing then automatically issues the refund against the original payment method. Billing can initiate a referenced refund only when the original payment is associated with a payment gateway.

To issue referenced refunds, turn on Issue Refunds and Settle Balances on the Billing Settings page. For more information, see Initiate Automated Refunds on Negative and Canceled Invoices.

How Billing Processes Unreferenced Refunds

Customers build up credit balances from overpayments, adjustments, or canceled orders that have no payment to reference. An unreferenced refund returns an available credit balance against a credit memo instead of refunding back against the original payment. Accounts receivable and collections teams can issue an unreferenced refund against a credit memo or a credit memo line, and Billing automatically reduces the outstanding credit balance.

Billing pays the refund to a saved payment method through a supported third-party gateway. Teams also use unreferenced refunds to resolve billing disputes and overpayment claims by converting credit memo balances into refunds.

To learn how Billing applies and pays unreferenced refunds, see Refund Available Credit Balances to Customer Accounts. To issue an unreferenced refund, see Issue an Unreferenced Refund Against a Credit Memo.

Initiate Automated Refunds on Negative and Canceled Invoices
During subscription changes such as a quantity reduction or cancellation, Billing generates a negative invoice which then gets converted to a credit memo. This action triggers the automated refund process, where Billing automatically initiates the refund to the original payment method.
Refund Available Credit Balances to Customer Accounts
Refund a customer’s available credit balance against a credit memo or credit memo line without referencing an original payment.
