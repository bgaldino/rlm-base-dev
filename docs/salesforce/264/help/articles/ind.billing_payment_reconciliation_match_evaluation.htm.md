---
article_id: ind.billing_payment_reconciliation_match_evaluation.htm
title: Understand How Payment Reconciliation Evaluates a Match
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payment_reconciliation_match_evaluation.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payment_reconciliation.htm
fetched_at: 2026-09-04
---

# Understand How Payment Reconciliation Evaluates a Match

Payment reconciliation first checks whether the currency ISO code matches between the payment advice and payment proof documents. If yes, then it compares each payment against three criteria and records how closely the values align, so your accounts receivable team can review the results.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.

When the payment advice and payment proof use the same currency ISO code, then payment reconciliation evaluates these criteria.

Account—Reconciliation resolves the payer named on the payment advice and payment proof to an account and records a match score. A high-confidence score resolves the account automatically.
Amount—Reconciliation compares the amount on the payment advice with the amount confirmed on the payment proof, and each applied amount with its open invoice. It records the difference as an amount variance percentage. Payment reconciliation treats an amount variance within 2% as a match.
Date—Reconciliation compares the payment date on the advice with the date the bank confirmed the payment, and records the difference as a date variance in days. Payment reconciliation treats a date variance within 5 days as a match.

The matching is performed by using two data transforms:

PaymentAdviceInvoiceReconciliation—An advice-to-invoice data transform that matches a payment advice to your open invoices with balance greater than 0, confirming what the payment pays for, including any deductions.
PaymentAdvicePaymentProofReconciliation—An advice-to-proof data transform that matches a payment advice to the bank’s payment proof, confirming that the funds are settled.

Every reconciliation record is created with a Pending status that can then be reviewed by your accounts receivable team.

NOTE You can implement custom logic to create and apply payments after the match is confirmed.
Example 1: Payment Reconciliation with a 3-day Variance in Date

Acme Corp sends a payment advice for a $10,000 ACH payment dated March 15, 2026, that pays two invoices. Acme’s payment settles into your bank account, and your bank statement books the deposit on March 18, 2026, three days later. Payment reconciliation checks the currency ISO code in the payment advice and payment proof documents, and if there’s a match, it compares the two documents and your open invoices, and records the results.

PARAMETER	PAYMENT ADVICE	PAYMENT PROOF	RESULT
Account	Payer “Acme Corp”	Resolves to the Acme Corp account	High-confidence account match
Amount	$10,000	$10,000 confirmed	0% amount variance
Date	March 15, 2026	Booked March 18, 2026	3-day date variance
Invoice INV-1001	$6,000 applied	$6,000 invoice	Complete match, no deduction
Invoice INV-1002	$4,000 applied	$4,200 invoice	$200 short payment, deduction code EARLYPAY

Payment reconciliation writes these results to two kinds of records–Payment Advice Reconciliation and Payment Advice Invoice Reconciliation–that your accounts receivable team reviews.

The Payment Advice Reconciliation record is the header record for the advice-to-proof match.

FIELD	VALUE
Payer Name	Acme Corp
Account	Acme Corp (resolved)
Payment Advice Account Score	1, high confidence
Amount Variance %	0%
Date Variance (Days)	3
Review Status	Pending

A Payment Advice Invoice Reconciliation record is created for each invoice, for the advice-to-invoice match.

INVOICE	APPLIED AMOUNT	INVOICE AMOUNT	DEDUCTION AMOUNT	REVIEW STATUS
INV-1001	$6,000	$6,000	None	Pending
INV-1002	$4,000	$4,200	$200, EARLYPAY	Pending

The account and amount align, and the Payment Advice Reconciliation record shows a 3-day date variance between when Acme intended to pay and when the bank confirmed the deposit. Considering this as a normal settlement gap, your reviewer accepts the advice-to-proof match. On the Payment Advice Invoice Reconciliation records, INV-1001 is a complete match. INV-1002 is a $200 short payment against a $4,200 invoice, so the reviewer confirms the early-payment discount.

Example 2: Payment Reconciliation with a 2% Variance in Amount

Globex Corp sends a payment advice for a $10,000 wire payment dated April 6, 2026, that pays two invoices. The wire settles into your bank account the same day, but your bank statement confirms a deposit of $9,820, that’s $180 less, because an intermediary bank deducted a wire fee. Payment reconciliation checks the currency ISO code in the payment advice and payment proof documents, and if there’s a match, it compares the two documents and your open invoices, and records the results.

PARAMETER	PAYMENT ADVICE	PAYMENT PROOF	RESULT
Account	Payer “Globex Corp”	Resolves to the Globex Corp account	High-confidence account match
Amount	$10,000	$9,820 confirmed	1.8% amount variance (within 2%)
Date	April 6,2026	Booked April 6, 2026	0-day date variance
Invoice INV-2001	$6,000 applied	$6,000 invoice	Complete match
Invoice INV-2002	$4,000 applied	$4000 invoice	Complete match

Payment reconciliation writes these results to two kinds of records–Payment Advice Reconciliation and Payment Advice Invoice Reconciliation–that your accounts receivable team reviews.

The Payment Advice Reconciliation record is the header record for the advice-to-proof match.

FIELD	VALUE
Payer Name	Globex Corp
Account	Globex Corp (resolved)
Payment Advice Account Score	1, high confidence
Amount Variance %	1.8%
Date Variance (Days)	0
Review Status	Pending

A Payment Advice Invoice Reconciliation record is created for each invoice, for the advice-to-invoice match.

INVOICE	APPLIED AMOUNT	INVOICE AMOUNT	DEDUCTION AMOUNT	REVIEW STATUS
INV-2001	$6,000	$6,000	0	Pending
INV-2002	$4,000	$4,000	0	Pending

The account, currency ISO code, and dates all align. The advice-to-proof amount varies by 1.8%, within the 2% threshold, because the bank deducted a wire fee before the funds landed, so reconciliation treats it as a match and your reviewer accepts the advice-to-proof match. On the Payment Advice Invoice Reconciliation records, both INV-2001 and INV-2002 are considered as complete matches, because Globex applied the full invoice amounts even though the bank’s net deposit was lower.
