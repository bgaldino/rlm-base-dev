---
article_id: release-notes.rn_salesforce_pricing_new_changed_connect_rest_apis.htm
title: New and Changed Connect REST APIs in Salesforce Pricing
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_salesforce_pricing_new_changed_connect_rest_apis.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_salesforce_pricing.htm
fetched_at: 2026-09-30
---

# New and Changed Connect REST APIs in Salesforce Pricing

Clone a pricing recipe along with its pricing recipe table mapping records, and optionally assign a different pricing usage subtype to the cloned pricing recipe. Streamline pricing recipe setup by retrieving valid pricing element types for a specific pricing usage subtype in a single API request, which reduces invalid configurations by returning only the elements supported by the selected context. Improve design-time governance and support multi-cloud operations by restricting context definitions and pricing procedures to vertical-specific options.

New Connect REST API Resources
Clone a pricing recipe with its pricing recipe table mapping records

Make a POST request to the new /connect/core-pricing/revenue/pricing-recipe/clone resource.

New request body: Pricing Recipe Clone Input

New response body: Pricing Recipe Clone

Get valid pricing elements for a pricing usage subtype

Make a GET request to the new /connect/core-pricing/revenue/pricing-recipe/valid-elements resource.

New response body: Pricing Valid Elements

Changed Connect REST API Request Bodies
Procedure Plan Definitions

This request body has this new property.

subType—Specifies the vertical or cloud-specific subclassification for the procedure plan definition.
Procedure Plan Evaluation By Object

This request body has this new property.

subType—Specifies the vertical or cloud-specific subclassification for the procedure plan definition.
SEE ALSO
Revenue Cloud Developer Guide: Salesforce Pricing Business APIs
