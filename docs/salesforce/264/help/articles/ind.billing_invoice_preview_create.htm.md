---
article_id: ind.billing_invoice_preview_create.htm
title: Generate Invoice Previews for Orders and Accounts
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_preview_create.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_preview_invoice.htm
fetched_at: 2026-09-04
---

# Generate Invoice Previews for Orders and Accounts

Preview invoices for the next two billing periods of orders and accounts. Generate and download PDF documents of the invoice previews.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER
PERMISSIONS NEEDED
To generate invoice previews:	

You must have one of these permission sets:

Billing Admin
Billing Operations User
Billing Customer Service

To generate invoice preview PDF documents:	DocGen User permission set

The Preview Invoices quick action is available by default on both the Order page layout and the Account page layout.

Open the Account or Order record that you want to generate an invoice preview for.
From the quick actions menu, click Preview Invoices.
Select a preview date.

The default preview date is the current date and the default number of billing periods is 2. The preview date is the target date for generating an invoice preview for the first billing period. If you select 2 as the number of billing periods, the target date for generating an invoice preview for the second billing period is calculated by adding the transaction's shortest billing frequency to the previous invoice preview's target date.

For example, if you select March 3, 2025 as the preview date and the number of billing periods as 2, and the shortest billing frequency is monthly, invoice previews are generated for March 3, 2025 and April 3, 2025.
Select up to two as the number of billing periods.
Click Preview.
To generate a PDF for the invoice preview, click Generate PDF.
The generated PDF appears in the Notes & Attachments related list.
Open the PDF that you want to download and click Download.
NOTE Preview Invoices quick action is available out-of-the-box for draft and activate orders, accounts, and billing schedule groups. To preview invoices for quotes, see Generate Invoice Previews with the Invoice Preview API.
