---
article_id: ind.billing_invoice_preview_example.htm
title: "Example: Preview Invoices for an Order"
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_preview_example.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_invoice_previews.htm
fetched_at: 2026-09-04
---

# Example: Preview Invoices for an Order

This example shows how Billing generates preview invoices when an order includes products with different billing frequencies.

Acme Software Innovations places an order with these products for its customer, Growth Digital Marketing Pro.

Cloud Storage Pro, annual subscription, billed yearly at $1,200
Support Package, annual subscription, billed yearly at $600
User Licenses, monthly subscription, billed monthly at $150
API Access, monthly subscription, billed monthly at $50

The Acme Software Innovations Billing team wants to preview billing charges and share a proforma invoice before generating the actual invoices. The Billing team opens the order record for Growth Digital Marketing Pro and clicks Preview Invoices. They select March 1, 2025 as the preview date and 2 as the number of billing periods.

Billing generates two invoice previews.

The first invoice preview includes these products due for billing on March 1, 2025.

Cloud Storage Pro billed at $1,200
Support Package billed at $600
User Licenses billed at $150
API Access billed at $50

Billing calculates the second preview date by adding the shortest billing frequency, which is 1 month to the first preview date. The second invoice preview includes these monthly products due for billing on April 1, 2025.

User Licenses billed at $150
API Access billed at $50
NOTE The annual products were billed in the first invoice preview and their next billing is on March 1, 2026. Therefore, the second invoice preview has only monthly subscription products.

The Acme Software Innovations Billing team generates a PDF for each invoice preview, downloads them, and emails them to Growth Digital Marketing Pro for reconfirmation.
