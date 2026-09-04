---
article_id: ind.billing_void_taxes.htm
title: Tax Implications of Invoice Voids
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_void_taxes.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_invoices_void.htm
fetched_at: 2026-09-04
---

# Tax Implications of Invoice Voids

Learn how voiding an invoice cancels its associated taxes and affects the status of related credit memos.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license

When you void a posted invoice, the Tax Calculation API calls out a tax engine to void or adjust the tax. The status of the related credit memo depends on the tax engine’s response, which varies based on the invoice’s line types. This table shows invoice line types along with tax engine responses and corresponding credit memo statuses.

INVOICE LINE TYPE	TAX ENGINE RESPONSE	CREDIT MEMO STATUS
All positive invoice lines	Void	Voided
All positive invoice lines	Credit	Posted
All negative invoice lines	Void	Voided
All negative invoice lines	Debit	Posted

When you void an invoice that contains both positive and negative invoice lines, Tax Calculation API makes two tax call-outs to the tax engine. This table shows the tax engine response for positive and negative invoice lines and the corresponding credit memo status.

TAX ENGINE RESPONSE FOR POSITIVE INVOICE LINES	TAX ENGINE RESPONSE FOR NEGATIVE INVOICE LINES	CREDIT MEMO STATUS
Void	Void	Voided
Credit	Void	Voided
Void	Debit	Voided
Credit	Debit	Posted
