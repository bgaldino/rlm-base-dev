---
article_id: ind.pricing_understand_and_resolve_api_execution_messages.htm
title: Resolve API Execution Errors
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_understand_and_resolve_api_execution_messages.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Resolve API Execution Errors

Use the Debug Details tab to troubleshoot errors in the executed API.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer editions of Agentforce Revenue Management where Salesforce Pricing is enabled
USER PERMISSIONS NEEDED
To view price logs:	Salesforce Pricing Design Time

Here are some of the most common issues when your pricing API call fails.

If the failed pricing API was used to calculate a product's price, find the error details under the Debug Details tab.
Under Debug Details, click Pricing Procedure.
To find the reasons for success or failure of a line item, expand the line item.
To resolve the error for a failed line item, follow the troubleshooting steps under the respective line item.
In a typical pricing API call, pricing is calculated for multiple line items. Sometimes, one line item fails, but the others succeed. For example, if you use a Manual Discount element and enter an incorrect value for the Adjustment Type variable, the API call for that specific line item fails, while the other line items succeed.
If the failed API was used to calculate a product's derived price, check whether the error occurred in the discovery procedure, pricing procedure, or both.
To identify and resolve the issue, under Debug Details, click Discovery Procedure and check the error message.
The Discovery Procedure tab shows the details in JSON format.
To check the issues based on source and derived products, and their execution information under Debug Details, click Pricing Procedure and follow the troubleshooting steps.
When a pricing procedure is executed, you may see an error status even if the error log is empty. This happens because a line item has not been executed for pricing.
SEE ALSO
Derived Price
Discovery Procedures for Pricing
