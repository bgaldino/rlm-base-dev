---
article_id: ind.billing_credit_memos_apis_and_actions.htm
title: Manage Credit Memos by Using APIs or Flow Actions
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_credit_memos_apis_and_actions.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Manage Credit Memos by Using APIs or Flow Actions

Use APIs or Flow actions to create credit memos, apply credit memos to invoices, unapply already applied credits from invoices, and convert negative invoice lines into posted credit memos.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
GOAL	API
Create a standalone credit memo without applying it to an invoice	

Create a Standalone Credit Memo


Create a credit memo and apply it to an invoice	Create and Apply Credit Memo API
Apply a credit memo to an invoice	

Apply Credit Memo API

To automate the process of applying credits, build a custom flow and use the Apply Credit action. When the credit application level is Invoice, this action applies the balances of credit memos to settle the balances of posted invoices.


Apply a credit memo line to an invoice line	

Apply Credit Memo Line API

To automate the process of applying credits, build a custom flow and use the Apply Credit action. When the credit application level is Invoice Line, this action applies the balances of credit memo lines to settle the balances of posted invoice lines.


Unapply an applied credit memo from an invoice	

Unapply Credit Memo API

To automate the process of unapplying credits, build a custom flow and use the Unapply Credit action. When the credit application level is Invoice, this action unapplies credit memos from invoices and creates a related Credit Memo Invoice Application record of type Unapplied for the existing Credit Memo Invoice Application record of type Applied.


Unapply an applied credit memo line from an invoice line	

Unapply Credit Memo Line API

To automate the process of unapplying credits, build a custom flow and use the Unapply Credit action. When the credit application level is Invoice Line, this action unapplies credit memos lines from invoice lines and creates a related Credit Memo Line Invoice Line record of type Unapplied for the existing Credit Memo Line Invoice Line record of type Applied.


Convert a list of invoice lines with a negative amount into a posted credit memo	Convert Negative Invoice Lines into Credit Memos API
