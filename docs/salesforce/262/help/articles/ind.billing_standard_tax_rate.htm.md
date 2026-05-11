---
article_id: ind.billing_standard_tax_rate.htm
title: Revenue Standard Tax Engine
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_standard_tax_rate.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Revenue Standard Tax Engine

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Revenue Standard Tax Engine

Organizations often face challenges when managing taxes. Common issues include dependency on external tax vendors for simple scenarios, extra licensing and per-transaction costs, performance overhead from external API calls, and regulatory or data residency constraints. These challenges make tax management more complex and costly than necessary. The revenue standard tax engine addresses these issues by enabling internal tax calculation and storage for predictable tax structures. By handling simple tax scenarios internally, organizations can streamline their Agentforce Revenue Management processes.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license

You can use multiple tax engines at the same time. Configure some legal entities to use the revenue standard tax engine for simple tax rates, while others use external tax providers for complex jurisdictions.

NOTE Revenue standard tax engine is designed for simple calculations and may not be suitable for tax compliance needs. It calculates taxes at a line level and might include rounding at line level.
Configure Tax Rates
Use the Revenue Standard Tax Engine to calculate taxes natively in Agentforce Revenue Management. Define tax rates and use the built-in decision table to determine applicable taxes for products.
Understand How Agentforce Revenue Management Determines and Applies Tax Rates
When you use the Revenue Standard Tax Engine, Agentforce Revenue Management calculates taxes for transactions by matching the transaction record field values to the configured tax rates. These values include the shipping address, product code, legal entity, and currency ISO code. Revenue Cloud uses the built-in Revenue Standard Tax Entries decision table to perform this matching.
Revenue Standard Tax Engine Example
Explore an example that shows how the Standard Tax Engine applies multiple tax rates to an invoice based on location, currency, and product criteria.
