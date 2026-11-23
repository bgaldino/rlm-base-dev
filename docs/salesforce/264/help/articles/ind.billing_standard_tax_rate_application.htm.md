---
article_id: ind.billing_standard_tax_rate_application.htm
title: Understand How Revenue Cloud Determines and Applies Tax Rates
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_standard_tax_rate_application.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_standard_tax_rate.htm
fetched_at: 2026-11-23
---

# Understand How Revenue Cloud Determines and Applies Tax Rates

When you use the Revenue Standard Tax Engine, Revenue Cloud calculates taxes for transactions by matching the transaction record field values to the configured tax rates. These values include the shipping address, product code, legal entity, and currency ISO code. You can also match custom tax rate fields. Revenue Cloud uses the Revenue Standard Tax Entries decision table, or a cloned decision table that you associate with the tax engine, to perform this matching.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license

To match custom tax rate fields, see Extend Your Revenue Standard Tax Engine.

How Matching, Priority, and Application Basis Work
NOTE

Revenue Cloud matches tax rates to transactions by using the Geo Country and Geo State records and their currency ISO codes. If your Salesforce org has State and Country/Territory picklists enabled, Revenue Cloud can immediately evaluate addresses on transactions against tax rate criteria.

If Geo Country and Geo State records aren’t available or are incomplete, enabling state and country/territory picklists and creating Geo Country and Geo State records can help ensure consistent ISO code usage. This improves address matching accuracy when Revenue Cloud determines applicable tax rates, especially in scenarios where tax rules depend on country or state-level location data. See Enable State and Country/Territory Picklists, Create Geo Countries for the Manual Salesforce Tax Solution, and Create Geo States for the Manual Salesforce Tax Solution.

Revenue Cloud processes all matching tax rates in the priority order defined on the tax rate record and creates individual tax lines for each applicable tax rate. The priority number determines the order in which tax rates are applied, with lower numbers indicating a higher priority. When both country and state tax rates apply, the priority controls which rate is calculated first. If multiple tax rates share the same priority, the tax rate record created first takes precedence. If no priority is specified, the tax rate is applied last. Similarly, if multiple tax rates have no priority specified, Revenue Cloud uses them in chronological order, with the tax rate created first taking precedence.

Revenue Cloud generates tax lines based on the defined tax rates. The tax can be a percentage of the charge amount for gross calculation, a percentage of the charge amount plus previously calculated taxes for net calculation, or a flat tax amount as defined in your tax rate.

Multi-Currency and Single-Currency Considerations

Revenue Cloud handles tax calculation differently for single and multi-currency orgs.

Single-Currency Org: In a single-currency org, the Revenue Standard Tax Entries decision table is created without the Currency ISO Code field. Tax rate matching considers only the tax code, legal entity, country ISO code, state ISO code, and product code.
Multi-Currency Org: In a multi-currency org, the Revenue Standard Tax Entries decision table automatically includes the Currency ISO Code field. Tax rate matching considers tax code, legal entity, country ISO code, state ISO code, product code, and currency ISO code, ensuring accurate tax application for transactions created with different currencies.
NOTE If you can’t view the Currency ISO Code field for a multi-currency org, manually add this field from the tax rate page layout.
NOTE If your Salesforce org changes currency configuration after initially setting up the standard tax, you must refresh the Revenue Standard Tax Entries decision table to ensure correct tax matching. Revenue Cloud updates the decision table structure based on your Salesforce org configuration after every refresh. When switching to multi-currency, the Currency ISO Code field is added. When switching to single-currency, the Currency ISO Code field is removed.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_standard_tax_rate_application.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
