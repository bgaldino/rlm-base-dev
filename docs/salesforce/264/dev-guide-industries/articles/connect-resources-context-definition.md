---
page_id: connect-resources-context-definition
title: Context Definition (GET, POST)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-definition.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-context-definition-management
legacy_page_id: connect_resources_context_definition.htm
fetched_at: 2026-11-25
---

# Context Definition (GET, POST)

Create a context definition, clone an existing context definition, extend a standard definition (file based definition) or to persist entire context definition.

## Resource

```
/connect/context-definitions
```

## Example for GET

```
https://{yourInstance}.salesforce.com/services/data/v59.0/connect/context-definitions
```

{yourInstance} is the domain name of your Salesforce instance.

## Example for POST

```
https://{yourInstance}.salesforce.com/services/data/v59.0/connect/context-definitions
```

## Available Version

59.0

## Requires Chatter

No

## HTTP Methods

GET, POST

## Response Body for GET

[Context Definition List](./connect-responses-context-definition-list.md)

## Request Body for POST

### JSON Example

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

### Properties

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

## Response Body for POST

[Context Definition Information](./connect-responses-context-definition-info.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-definition.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
