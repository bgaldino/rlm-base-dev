---
article_id: ind.pricing_execute_pricing_elements_in_parallel.htm
title: Set Up Parallel Pricing Element Execution
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_execute_pricing_elements_in_parallel.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Set Up Parallel Pricing Element Execution

Run multiple pricing procedures concurrently or use parallel processing within a single pricing procedure to ensure faster and more efficient pricing, especially in complex scenarios.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS NEEDED
To run pricing elements in parallel:	Salesforce Pricing Design Time

When enabled, all active pricing procedures invoked from Headless or Pricing APIs will undergo parallel execution, meaning independent elements will be processed simultaneously.

NOTE The Map Line Item element doesn't support parallel execution. To use the Map Line Item element in your pricing procedure, disable parallel execution.
From Setup, in the Quick Find box, enter Salesforce Pricing, and then select Salesforce Pricing Setup.
Turn on Parallel Execution.
When Parallel Execution is turned on:
The sequence tag value in the waterfall changes, but the order of the execution remains the same.
The elements run in parallel when there are no dependencies, such as when the output of one element is not the input of another.
The list filters run sequentially, but the elements within the list filters run in parallel.
