---
article_id: ind.billing_setup_apply_credits_to_posted_invoices.htm
title: Automatic Application of Credits to Settle Invoice Balances
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_setup_apply_credits_to_posted_invoices.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Automatic Application of Credits to Settle Invoice Balances

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Automatic Application of Credits to Settle Invoice Balances

Eliminate the need to manually apply credit memos by automatically applying available credit memo balances to settle the balances of posted invoices.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Process Overview

When your Billing admin enables the Apply Credits to Posted Invoices feature, the system automatically applies the balances of credit memo to settle the balances of posted invoices based on the credit application level.

The automatic credit application process runs immediately after invoices are posted by using one of these methods:

After a scheduled invoice run completes.
Using Post Draft Invoices in Batch API.
After running the Post Draft Invoice Batch Run action.
Visualizing the Process

This flowchart shows the step where credit application happens in the business process flow.
