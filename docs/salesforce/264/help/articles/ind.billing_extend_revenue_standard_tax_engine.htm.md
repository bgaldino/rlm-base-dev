---
article_id: ind.billing_extend_revenue_standard_tax_engine.htm
title: Extend Your Revenue Standard Tax Engine
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_extend_revenue_standard_tax_engine.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_standard_tax_rate.htm
fetched_at: 2026-09-04
---

# Extend Your Revenue Standard Tax Engine

Apply tax rates based on custom attributes, such as product category, customer attributes, or exemption criteria, without writing Apex code. Use a custom metadata type to map billing transaction fields to a cloned Revenue Standard Tax Entries decision table, and persist matched values on invoice and credit memo tax lines.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Configure Custom Metadata Types
Create a custom metadata type that maps billing transaction fields to decision table columns for the Revenue Standard Tax Engine.
Clone the Decision Table
Clone the Revenue Standard Tax Entries decision table and add the custom columns that you use to match tax rates.
