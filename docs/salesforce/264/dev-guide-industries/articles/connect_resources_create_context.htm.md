---
page_id: connect_resources_create_context.htm
title: Context Service (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_create_context.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: runtime_context_intance_management.htm
fetched_at: 2026-11-23
---

# Context Service (POST)

Create new context records by submitting metadata and associated JSON data. After
validating the data, the system generates a new context ID. Context objects created using this
API apply only to a single request. They cannot be used to pass data across multiple
requests.

## Resource

```
/connect/contexts
```

## Example

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/contexts
```

## Available Version

59.0

## Requires Chatter

No

## HTTP Methods

POST

## Request Body for POST

### JSON Example

```
{
  "metadata": {
    "contextDefinitionId": "11Oxx0000006VjNEAU",
    "mappingId": "11jxx0000004Q83AAE"
  },
  "data": "{\"Order\":[{\"id\":\"TestOrder123\",\"businessObjectType\":\"Order\",\"Name\":\"Test Order\",\"Status\":\"SHIPPED\",\"AccountName\":\"Kroger\",\"OrderItems\":[{\"id\":\"TestOrderItem1\",\"businessObjectType\":\"OrderItem\",\"ProductName\":\"Coke\"},{\"id\":\"TestOrderItem2\",\"businessObjectType\":\"OrderItem\",\"ProductName\":\"Pepsi\"}]}]}"
}
```

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `data` | String | Payload containing context-specific information. | Required | 59.0 |
| `metadata` | [Context MetaData Input](./connect_requests_context_meta_data_input.htm.md "Input representation of context metadata.") | Metadata information about context. | Required | 59.0 |

## Response Body for POST

[Context
Info](./connect_responses_context_info.htm.md "Output representation containing detailed information about a context.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_create_context.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
