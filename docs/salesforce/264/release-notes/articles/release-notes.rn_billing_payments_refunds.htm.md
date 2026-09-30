---
article_id: release-notes.rn_billing_payments_refunds.htm
title: Payments and Refunds
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_billing_payments_refunds.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_billing.htm
fetched_at: 2026-09-30
---

# Payments and Refunds

Pass Level 2 and Level 3 payment data via Stripe and Adyen. Support flexible customer payment options through saved digital wallets and regional payment methods. Add Billing Self-Service components on LWR Experience Cloud sites, refund available credit balances back to the account, and automatically reconcile payment advice records with bank statements.

Send Level 2 and Level 3 Payment Data Through a Native Payment Gateway
Pass Level 2 and Level 3 enhanced transaction data in your payment requests to Stripe and Adyen native payment gateways. The payment batch run automatically includes the enhanced metadata in the payment gateway logs.
Save Digital Wallets for Future Invoice Payments
When you add digital wallets to a payment method set, customers can save options like Apple Pay and Google Pay in the Self-Service Billing Portal. They can then reuse those payment methods for future invoices or set them as their default. Saved digital wallets appear in their saved payment methods.
Accept Regional Payment Methods in the Self-Service Billing Portal Through Native Gateways
Your customers can pay invoices by using regional payment methods from the Self-Service Billing Portal. Supported methods include Bancontact, Klarna, Affirm, Canadian Pre-Authorized Debit, and New Zealand BECS through Stripe and Adyen. These payment options expand coverage across different regions and payment preferences.
Add Billing Self-Service Components in LWR Experience Cloud Sites
Add billing capabilities to any Experience Cloud site built on Lightning Web Runtime (LWR) templates. The Posted Invoices, Invoice Line Viewer, Self-Service Payment Sheet, Self-Service Payment Confirmation, and Manage Saved Payment Methods components now appear in the Experience Cloud palette. Customers can view invoices, pay outstanding balances, save payment methods for future use, and manage saved payment methods from your branded site. Customize the page layout and component placement to match your site design. Add these components to existing LWR sites or build your own sites.
Refund Available Credit Balances to Customer Accounts
Your accounts receivable or collections team can now issue refunds for credit balances available on an account. Billing automatically reduces the outstanding credit balance when a refund is issued. Previously, you could only issue referenced refunds against payments, but with this enhancement, you can issue an available credit balance as a refund to a customer’s preferred payment method. You can issue refunds against credit memos or credit memo lines.
Reconcile Payment Advice and Bank Data with Lockbox Processing
Accelerate cash collection by automating payment reconciliation between payment advice records and bank statements. Billing uses Document AI to extract payment data from payment advice documents, checks, emails, or other payment advice records and automatically matches the payment data against available bank statements. Your accounts receivable team can then review all matched and unmatched transactions in the reconciled payment records.
