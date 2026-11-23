---
article_id: ind.billing_payment_reconciliation_setup_batch_transform.htm
title: Create a Custom Batch Data Transform
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payment_reconciliation_setup_batch_transform.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payment_reconciliation_setup.htm
fetched_at: 2026-11-23
---

# Create a Custom Batch Data Transform

After Document AI parses your payment advice and payment proof files, convert the numeric and text fields that represent currency and date values into the currency and date data types that payment reconciliation requires.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To create a custom batch data transform:	

Data Cloud Architect permission set

Create a custom batch data transform to convert the text and number fields parsed by Document AI into date and currency fields. Make sure that your data transform is able to resolve the currency ISO code from the payment details.
For each output DLO, complete these steps.
Add a transform node to convert all the fields in the DLO to the required data type. Optionally, add custom transformation logic or formula nodes.
Select the three DLOs and add them to the default data space. Select the Add without filters checkbox.
Map the output DLOs to the PaymentAdvice_std__dlm, PaymentAdviceLineInvoice_std__dlm, and PaymentProof_std__dlm data model objects.
Save, build, and run the batch data transform. You can run the data transform manually or schedule it.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_payment_reconciliation_setup_batch_transform.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
