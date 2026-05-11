---
article_id: ind.billing_configure_context_definitions.htm
title: Configure Context Definitions for Billing
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_configure_context_definitions.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
parent_article: ind.billing_setup.htm
fetched_at: 2026-05-11
---

# Configure Context Definitions for Billing

Context definitions in Billing act as a central data-mapping layer that helps information flow seamlessly from orders or external transactions into billing schedules. They transform data from Salesforce objects into a standardized format that enable the Billing APIs to read the details required to create accurate billing records. By configuring these context definitions, businesses can automate the transfer of custom field data.

Standard Context Definitions for Billing
After you turn on Context Service, you can access the standard context definitions that are available with Billing.
Select Context Definition and Mapping for Create Billing Schedules for Orders API
The Create Billing Schedules for Orders API uses Context Service to hydrate the data of orders to create billing schedules. Before using this API, select a context definition and its mapping that you want the API to use.
Capture Preferred Transaction Details by Using Custom Fields
To meet specific business requirements, populate custom field data from orders or external transactions to corresponding billing schedule, billing schedule group, and billing schedule group relationship records. Use Context Service to define how data must be transferred by configuring a custom intracontext mapping. Then, use the Create Billing Schedules for Orders API or the Create Standalone Billing Schedules API to generate billing schedules and billing schedule groups. You can also use custom fields to override the standard fields in billing nodes by using the custom intracontext mapping.
