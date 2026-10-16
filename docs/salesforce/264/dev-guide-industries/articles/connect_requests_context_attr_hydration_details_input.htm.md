---
page_id: connect_requests_context_attr_hydration_details_input.htm
title: Context Attribute Hydration Details Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_attr_hydration_details_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Attribute Hydration Details Input

Input representation of context attribute hydration detail.

**Properties**

: 

                    

                    

                    

                    

                    

                  

                    

                    

                    

                    

                    

                  

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `childDetails` | Context Attribute Hydration Details Input[] | Child of hydration details. | Required | 59.0 |
| `contextAttrHydrationDetailId` | String | ID of the hydration detail record. This field is required for the update request. | Optional | 59.0 |
| `parentAttributeMappingId` | String | ID of the parent context attribute mapping record. | Required | 59.0 |
| `parentDetailId` | String | ID of the parent context attribute hydration detail record. | Required | 59.0 |
| `queryAttribute` | String | Query attribute. | Optional | 59.0 |
| `sObjectDomain` | String | SObject domain. | Optional | 59.0 |
