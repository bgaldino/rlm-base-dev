---
article_id: ind.billing_standard_tax_rate_application.htm
title: Understand How Agentforce Revenue Management Determines and Applies Tax Rates
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_standard_tax_rate_application.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Understand How Agentforce Revenue Management Determines and Applies Tax Rates

When you use the Revenue Standard Tax Engine, Agentforce Revenue Management calculates taxes for transactions by matching the transaction record field values to the configured tax rates. These values include the shipping address, product code, legal entity, and currency ISO code. Revenue Cloud uses the built-in Revenue Standard Tax Entries decision table to perform this matching.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
NOTE

Agentforce Revenue Management matches tax rates to transactions by using the Geo Country and Geo State records and their currency ISO codes. If your Salesforce org has State and Country/Terrirotry picklists enabled, Agentforce Revenue Management can immediately evaluate addresses on transactions against tax rate criteria.

If Geo Country and Geo State records aren’t available or are incomplete, enabling state and country/territory picklists and creating Geo Country and Geo State records can help ensure consistent ISO code usage. This improves address matching accuracy when Revenue Cloud determines applicable tax rates, especially in scenarios where tax rules depend on country or state-level location data. See Enable State and Country/Territory Picklists, Create Geo Countries for the Manual Salesforce Tax Solution, and Create Geo States for the Manual Salesforce Tax Solution.

Agentforce Revenue Management processes all matching tax rates in the priority order defined in the tax rate and creates individual tax lines for each applicable tax rate. The priority number determines the order in which tax rates are applied, with lower numbers indicating a higher priority. When both country and state tax rates apply, the priority controls which rate is calculated first. If multiple tax rates share the same priority, the tax rate record created first takes precedence. If no priority is specified, the tax rate is applied last. Similarly, if multiple tax rates have no priority specified, Agentforce Revenue Management uses them in chronological order, with the tax rate created first taking precedence.

Agentforce Revenue Management generates tax lines based on the defined tax rates. The tax can be a percentage of the charge amount for gross calculation, a percentage of the charge amount plus previously calculated taxes for net calculation, or a flat tax amount as defined in your tax rate.

Multi-Currency and Single-Currency Considerations

Agentforce Revenue Management handles tax calculation differently for single and multi-currency orgs.

Single-Currency Org: In a single-currency org, the Revenue Standard Tax Entries decision table is created without the Currency ISO Code field. Tax rate matching considers only the tax code, legal entity, country ISO code, and state ISO code.
Multi-Currency Org: In a multi-currency org, the Revenue Standard Tax Entries decision table automatically includes the Currency ISO Code field. Tax rate matching considers tax code, legal entity, country ISO code, state ISO code, and currency ISO code, ensuring accurate tax application for transactions created with different currencies.
NOTE If you are unable to view the Currency ISO Code field for a multi-currency org, manually add this field from the tax rate page layout.
NOTE If your Salesforce org changes currency configuration after initially setting up the standard tax, you must refresh the Revenue Standard Tax Entries decision table to ensure correct tax matching. Agentforce Revenue Management will update the decision table structure based on your Salesforce org configuration after every refresh. When switching to multi-currency, the Currency ISO Code field is added. When switching to single-currency, the Currency ISO Code field is removed.
