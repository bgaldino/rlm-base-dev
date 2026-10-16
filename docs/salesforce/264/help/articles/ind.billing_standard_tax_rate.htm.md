---
article_id: ind.billing_standard_tax_rate.htm
title: Revenue Standard Tax Engine
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_standard_tax_rate.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_tax_configuration.htm
fetched_at: 2026-09-04
---

# Revenue Standard Tax Engine

Organizations often face challenges when managing taxes. Common issues include dependency on external tax vendors for simple scenarios, extra licensing and per-transaction costs, performance overhead from external API calls, and regulatory or data residency constraints. These challenges make tax management more complex and costly than necessary. The revenue standard tax engine addresses these issues by enabling internal tax calculation and storage for predictable tax structures. By handling simple tax scenarios internally, organizations can streamline their Revenue Management processes.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license

You can use multiple tax engines at the same time. Configure some legal entities to use the revenue standard tax engine for simple tax rates, while others use external tax providers for complex jurisdictions.

NOTE Revenue standard tax engine is designed for simple calculations and may not be suitable for tax compliance needs. It calculates taxes at a line level and might include rounding at line level.
Configure Tax Rates
Use the Revenue Standard Tax Engine to calculate taxes natively in Revenue Management. Define tax rates and use the built-in decision table to determine applicable taxes for products.
Understand How Revenue Management Determines and Applies Tax Rates
When you use the Revenue Standard Tax Engine, Revenue Management calculates taxes for transactions by matching the transaction record field values to the configured tax rates. These values include the shipping address, product code, legal entity, and currency ISO code. You can also match custom tax rate fields. Revenue Management uses the Revenue Standard Tax Entries decision table, or a cloned decision table that you associate with the tax engine, to perform this matching.
Revenue Standard Tax Engine Example
Explore an example that shows how the Standard Tax Engine applies multiple tax rates to an invoice based on location, currency, and product criteria.
Extend Your Revenue Standard Tax Engine
Apply tax rates based on custom attributes, such as product category, customer attributes, or exemption criteria, without writing Apex code. Use a custom metadata type to map billing transaction fields to a cloned Revenue Standard Tax Entries decision table, and persist matched values on invoice and credit memo tax lines.
Create a Tax Engine
Create a tax engine record that Billing uses to calculate tax. Set the type to Revenue Standard Tax Engine. When you extend the Revenue Standard Tax Engine, associate a custom metadata type and a decision table.
