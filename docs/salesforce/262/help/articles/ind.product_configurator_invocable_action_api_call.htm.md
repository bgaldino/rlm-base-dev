---
article_id: ind.product_configurator_invocable_action_api_call.htm
title: Use an API Call to Run the Run Config Rules Action
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_invocable_action_api_call.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Use an API Call to Run the Run Config Rules Action

Use an API call to run the Run Config Rules invocable action with the Hide/Disable, Message, or Recommend rule.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
USER PERMISSIONS NEEDED
To work with configuration rules:	Manage Configurator with Constraint Rules Engine
To use the Run Config Rules invocable action:	Product Configuration Rules User
To use the Agentforce Revenue Management REST API:	Product Configurator API User

For information on the Run Config Rules invocable action, see Run Config Rules Action in the Agentforce Revenue Management Developers Guide.

Use the Agentforce Revenue Management REST API to send a POST request to this endpoint. /services/data/v65.0/actions/standard/runConfigRules

Use a JSON object for the request body with a top-level key named inputs that contains the method parameters, as in this example.

EXAMPLE
{
  "inputs": [
    {
      "transactionId": "order or quote"
    }
  ]
}
