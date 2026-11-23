---
page_id: connect_requests_context_definitions_input.htm
title: Context Definition Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_definitions_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-11-23
---

# Context Definition Input

Input representation of the context definition.

## JSON Example

```
{
   "name":"Example Definition",
   "description":"Example Description",
   "developerName":"John Doe",
   "startDate":"2023-06-02T00:00:00.000Z",
   "endDate":"2025-06-20T00:00:00.000Z",
   "isActive":false,
   "payload":"{\"contextDefinition\":{\"name\":\"ExampleDefinition\",\"description\":\"Example Description\",\"developerName\":\"ExampleDefinition\",\"contextDefinitionVersionList\":[{\"contextDefinitionVersion\":{\"isActive\":\"TRUE\",\"startDate\":\"2023-06-02T00:00:00.000Z\",\"endDate\":\"2025-06-20T00:00:00.000Z\",\"contextNodes\":[{\"name\":\"Claim\",\"isTransposable\":\"TRUE\",\"contextNodeId\":\"$param_claimId\",\"attributes\":[{\"dataType\":\"STRING\",\"type\":\"INPUT\",\"isFinal\":\"TRUE\",\"isKey\":\"false\",\"isValue\":\"true\",\"contextAttributeId\":\"$param_claimaccountId\",\"name\":\"Account\",\"contextTagList\":[{\"name\":\"ClaimAccount\"}]}],\"nodeChildren\":[{\"name\":\"ClaimItem\",\"isTransposable\":\"TRUE\",\"contextNodeId\":\"$param_claimItemId\",\"attributes\":[{\"dataType\":\"STRING\",\"type\":\"INPUT\",\"isFinal\":\"TRUE\",\"isKey\":\"FALSE\",\"isValue\":\"FALSE\",\"contextAttributeId\":\"$param_assetId\",\"name\":\"Asset\",\"contextTagList\":[{\"name\":\"ClaimItemAsset\"}]}],\"contextTagList\":[{\"contextNodeId\":\"$param_claimItemId\",\"name\":\"ClaimItem\"}]}],\"contextTagList\":[{\"contextNodeId\":\"$param_claimId\",\"name\":\"Claim\"}]}],\"contextMapping\":[{\"name\":\"Claim Order Mapping\",\"isDefault\":\"TRUE\",\"contextNodeMappings\":[{\"contextNodeId\":\"$param_claimId\",\"sObjectName\":\"Claim\",\"contextAttributeMappings\":[{\"contextAttributeId\":\"$param_claimaccountId\",\"hydrationSource\":\"SObject\",\"contextSObjectHydrationInfoList\":[{\"sObjectDomain\":\"Claim\",\"queryAttribute\":\"Account\",\"parentContextSObjectHydrationInfoList\":[{\"sObjectDomain\":\"Account\",\"queryAttribute\":\"Name\"}]}]}]},{\"contextNodeId\":\"$param_claimItemId\",\"sObjectName\":\"ClaimItem\",\"contextAttributeMappings\":[{\"contextAttributeId\":\"$param_assetId\",\"hydrationSource\":\"SObject\",\"contextSObjectHydrationInfoList\":[{\"sObjectDomain\":\"ClaimItem\",\"queryAttribute\":\"Asset\",\"parentContextSObjectHydrationInfoList\":[{\"sObjectDomain\":\"Asset\",\"queryAttribute\":\"Name\"}]}]}]}]}]}}]}}",
   "sourceDefinitionId":"11Oxx0000007MnhEAE",
   "contextTtl":30
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextTtl` | Integer | Time to live (TTL) of context. | Optional | 59.0 |
| `description` | String | Short description of context definition. | Optional | 59.0 |
| `developerName` | String | Developer name. | Required | 59.0 |
| `endDate` | String | End date till context definition is valid. | Optional | 59.0 |
| `isActive` | Boolean | Specifies whether context is active (`true`) or not (`false`). | Optional | 59.0 |
| `name` | String | Name of the context definition. | Required | 59.0 |
| `payload` | String | JSON payload containing all the definitions and mappings. | Optional | 59.0 |
| `sourceDefinitionId` | String | Source context definition ID. | Optional | 59.0 |
| `startDate` | String | Start date from when context definition is valid. | Required | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_definitions_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
