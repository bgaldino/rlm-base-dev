---
article_id: ind.product_configurator_invocable_action_api_call.htm
title: Use an API Call to Run the Run Config Rules Action
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_invocable_action_api_call.htm&type=5&release=264
release: 264
release_name: Winter '27
area: configurator
parent_article: ind.product_configurator_invocable_action_to_run_rules.htm
fetched_at: 2026-09-04
---

# Use an API Call to Run the Run Config Rules Action

Use an API call to run the Run Config Rules invocable action with the Hide/Disable, Message, or Recommend rule.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
USER PERMISSIONS NEEDED
To work with configuration rules:	Manage Configurator with Constraint Rules Engine
To use the Run Config Rules invocable action:	Product Configuration Rules User
To use the Revenue Management REST API:	Product Configurator API User

For information on the Run Config Rules invocable action, see Run Config Rules Action in the Revenue Management Developers Guide.

Use the Revenue Management REST API to send a POST request to this endpoint. /services/data/v65.0/actions/standard/runConfigRules

Use a JSON object for the request body with a top-level key named inputs that contains the method parameters, as in this example.

EXAMPLE
{
  "inputs": [
    {
      "transactionId": "order or quote"
    }
  ]
}
