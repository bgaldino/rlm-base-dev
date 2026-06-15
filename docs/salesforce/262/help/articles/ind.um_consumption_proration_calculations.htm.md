---
article_id: ind.um_consumption_proration_calculations.htm
title: Consumption Proration Calculations
source_url: https://help.salesforce.com/s/articleView?id=ind.um_consumption_proration_calculations.htm&type=5&release=262
release: 262
release_name: Summer '26
area: usage
fetched_at: 2026-05-11
---

# Consumption Proration Calculations

Proration is used to ensure that customers are only billed or granted resources for the fraction of a billing period that a product was active. Consumption Management uses a proration engine that performs the calculation and provides accurate billing.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license

Consumption is prorated when either grants are added or rates are updated between the billing cycles.

EXAMPLE

Mid-Cycle Grant Amendments

SCENARIO	PRORATION CALCULATION	RESULT
A customer purchases an anchor plan starting July 20 that grants them 4,000 text messages per month. The initial child bucket is created with a validity of July 20 to August 19, containing 4,000 texts. On August 3, the customer decided to amend the quote to purchase an additional quantity of the product.	Instead of granting the complete 4,000 texts for the new purchase, the proration engine cuts the original transaction's validity and creates a child bucket effective from August 3 to August 20. The new bucket is only active for 16 days of the billing cycle and therefore, the system's proration engine calculates a prorated balance of 2,193 text messages.	When the customer consumes texts between August 3 and August 20, Consumption Management draws down from a pooled total balance that includes the prorated 2,193 messages.

Mid-Cycle Rate Amendments

SCENARIO	PRORATION CALCULATION	RESULT
A customer is consuming an active plan that’s valid from Jan 1 to Jan 31. In the middle of a customer’s billing period, a sales rep overrides and amends the negotiated rate of a resource from $10 to $9.	The proration engine splits the consumption for the different rate durations. Consumed units logged before Jan 15 are aggregated and rated at the $10 rate, while usage logged after the amendment date is aggregated separately and rated at the new $9 rate.	Consumption Management generates two separate Liability Summary rows for the split periods, ensuring the total invoice accurately reflects the prorated mid-cycle rate change.
