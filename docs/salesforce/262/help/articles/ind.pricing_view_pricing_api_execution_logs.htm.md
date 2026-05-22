---
article_id: ind.pricing_view_pricing_api_execution_logs.htm
title: Investigate and Analyze Pricing API Execution Logs
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_view_pricing_api_execution_logs.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Investigate and Analyze Pricing API Execution Logs

Open price logs to resolve errors by using the log information in the Agentforce Revenue Management Operations Console app. All headless pricing and pricing API executions, including discovery and pricing procedures performed within an API call, are recorded as pricing logs. This includes successful and unsuccessful executions.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer editions of Agentforce Revenue Management where Salesforce Pricing is enabled
USER PERMISSIONS NEEDED
To view price logs:	Salesforce Pricing Design Time
From the App Launcher, find and select Revenue Cloud Operations Console.
From the list of pricing API executions, find and select the pricing log you want to check.
To check the success and failure status of the API, check the Details and the Debug Details tabs.
A successful API call shows a Success status along with relevant details, such as information about a pricing procedure executed through the API.
A failed call shows an Error status along with the reason for the failure and the troubleshooting steps.
To see the name, status, execution key, API type, and endpoint information about the API, select Details.
To see the details on each successful line item, the elements involved, and the success status, select Debug Details.
NOTE If you delete an execution log record, it's removed from the Pricing API Execution and Pricing Process Execution objects. However, the API execution details remain available in the Price Waterfall view of the pricing procedure.
SEE ALSO
PricingAPIExecution
PricingProcessExecution
