---
article_id: ind.billing_invoice_delete.htm
title: Delete Invoices
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_delete.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_invoice_generation.htm
fetched_at: 2026-09-04
---

# Delete Invoices

Delete invoices in Agentforce Revenue Management to correct billing errors, remove duplicate invoices, or clean up invoice drafts.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To delete invoices:	

Billing Admin permission set

OR

If you have only the Billing Operations User permission set, you can delete invoices with a status of Draft or Canceled

Before you delete an invoice with a status other than Draft or Canceled, clone the Billing Admin permission set and enable the Delete Invoice and Invoice Lines user permission.

WARNING Invoice deletion can cause data integrity issues.
From the App Launcher, find and select Invoices.
Open the Invoice record that you want to delete.
From the quick actions menu, click Delete.
Confirm the deletion.

After you delete an invoice, you can’t recover it. The invoice deletion also removes the related invoice lines and billing period items. If Billing can’t delete the invoice, an error message appears on the Invoice record.
