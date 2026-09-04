---
article_id: ind.billing_payment_reconciliation_run.htm
title: Reconcile Payment Advice and Payment Proof with Bank Data
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payment_reconciliation_run.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payment_reconciliation.htm
fetched_at: 2026-09-04
---

# Reconcile Payment Advice and Payment Proof with Bank Data

Payment reconciliation connects the data you prepared in Data 360 with your billing records. After you share your payment advice and payment proof documents through the connector of your choice, Data 360 ingests them, Document AI extracts the data, and your batch data transforms convert it into the fields that Billing needs. When you run the reconciliation transforms, Billing pulls in this data, matches each payment advice against the bank’s payment proof and your open invoices, and creates reconciliation records. Your accounts receivable team then reviews the matched and unmatched records.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To reconcile payment advice and payment proof with bank data by using batch data transforms:	

Billing Admin permission set

AND

Data Cloud Architect permission set

Complete the setup steps for payment reconciliation, including deploying the payment reconciliation data kit.

Confirm that your latest payment advice and payment proof documents are ingested and processed into the PaymentAdvice, PaymentAdviceLineInvoice, and PaymentProof data model objects. To verify, view these data model objects in the Query Editor in Data 360.
In the Data Transforms tab in Data 360, run these payment reconciliation batch data transforms.
PaymentAdvicePaymentProofReconciliation
PaymentAdviceInvoiceReconciliation

You can also run them by using REST API.

POST /services/data/v68.0/ssot/data-transforms/PaymentAdvicePaymentProofReconciliation/actions/run
POST /services/data/v68.0/ssot/data-transforms/PaymentAdviceInvoiceReconciliation/actions/run
Billing matches the payment with payment proofs and invoices, and creates payment advice reconciliation records for you to review.
Open the payment advice reconciliation and payment advice invoice reconciliation records to review the matched and unmatched results.
Each record shows how closely the payment advice, payment proof, and invoice match, including the difference in amount and in payment date.
NOTE You can define and implement custom logic to accept, reject, and resolve the matched records, and then apply the payment to the appropriate invoice.
