---
article_id: ind.billing_tax_summary_difference.htm
title: Tax Totals at the Line and Header Levels
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_tax_summary_difference.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_tax_additional_configuration.htm
fetched_at: 2026-09-04
---

# Tax Totals at the Line and Header Levels

Understand how Billing applies line-level and header-level tax amounts during balance calculation.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license

When Capture Taxes At Header is turned on:

For an Apex or partner tax engine, Billing stores the consolidated tax amount returned by your tax engine in the Total Taxes Captured at Header field on invoices and credit memos.
For the Revenue Standard Tax Engine, Billing calculates tax from the invoice total charge amount and shipping address, then stores the result at the invoice header.
Invoice balance calculations use the header tax amount instead of the sum of line-level taxes.
Billing retains line-level tax details as an aggregated total of all invoice lines for reporting or reconciliation when provided by the tax adaptor.
For credit memos created from invoices based on the header tax, the credit memo records the corresponding header tax amount. The Total Taxes Captured at Header field stores the tax amount returned for the credit memo calculation.

Billing applies line-level tax instead of header-level tax in these situations:

The header tax amount is null or missing.
The tax engine fails to return a header tax amount.
The invoice is created before header tax is enabled.
The Credit, Payment, and Refund Application Level is changed from Header Level to Line Level after invoice creation.
The users manually edit tax amounts while the invoice is in draft status.
A tax engine timeout occurs during header tax calculation.
A network connectivity issue interrupts tax service calls.
The currency conversion fails for the header tax amount.
Exchange rate calculation errors affect the header tax amount.
The header tax format in the API request is invalid.
An API version compatibility issue prevents header tax processing.
