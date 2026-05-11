---
article_id: ind.billing_set_up_context_definition.htm
title: Select Context Definition and Mapping for Create Billing Schedules for Orders API
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_set_up_context_definition.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
parent_article: ind.billing_configure_context_definitions.htm
fetched_at: 2026-05-11
---

# Select Context Definition and Mapping for Create Billing Schedules for Orders API

The Create Billing Schedules for Orders API uses Context Service to hydrate the data of orders to create billing schedules. Before using this API, select a context definition and its mapping that you want the API to use.

REQUIRED EDITIONS
USER PERMISSIONS
NEEDED
To select a context definition and its mappings:	Billing Admin permission set
In Setup, find and select Billing Settings.
In the Context Service Mapping section, select the extended BillingContext context definition as the context definition.
Select OrderEntitiesMapping or a similar source mapping context map that you have added.
Make sure to select only a source context mapping that maps orders to billing transaction context nodes.
Optionally, add a custom intracontext mapping and select the mapping to map custom Order fields to the billing transaction nodes, or to override the existing mapping of standard fields.
You can pass preferred order details to billing schedules by configuring the custom mapping by using Context Service.
SEE ALSO
Turn On Context Service
Revenue Cloud Developer Guide: Create Billing Schedules for Orders API
Revenue Cloud Developer Guide: Create Standalone Billing Schedules API
