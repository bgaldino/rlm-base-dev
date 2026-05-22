---
article_id: ind.pricing_pricing_operations_console_sections.htm
title: Understand Your Pricing Data
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_pricing_operations_console_sections.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Understand Your Pricing Data

The Agentforce Revenue Management Operations Console has four sections that show you how your pricing data is used.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
Console Sections
SECTION	DESCRIPTION
Price Waterfall Storage	Shows the amount of data consumed by the Price Waterfall.
Decision Tables	Shows the number of decision tables that Salesforce Pricing uses to run the pricing processes.
API Calls	Shows the number of API calls you’ve used out of your allotted limit.
Pricing API Executions	Shows the list of logs that are generated after a pricing API is run.
Pricing API Execution Log Details

When a pricing API is run, a log is generated with the following details:

LOG DETAIL	DESCRIPTION
Execution ID	The ID generated every time a pricing API runs.
Created Date	The date the API execution log was created.
Status	The status of the API response, whether it succeeded or failed.
API Endpoint	The unique API endpoint that is called during the execution.
Reference Key	The reference ID that a consuming functional area must pass in the API to search for specific logs in the Agentforce Revenue Management Operations Console.
Created By ID	The user who executed the API.
