---
page_id: connect_requests_context_input.htm
title: Context Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-11-23
---

# Context Input

Input representation for defining a context.

## JSON Example

```
{
  "metadata": {
    "contextDefinitionId": "11Oxx0000006VjNEAU",
    "mappingId": "11jxx0000004Q83AAE"
  },
  "data": "{\"Order\":[{\"id\":\"TestOrder123\",\"businessObjectType\":\"Order\",\"Name\":\"Test Order\",\"Status\":\"SHIPPED\",\"AccountName\":\"Kroger\",\"OrderItems\":[{\"id\":\"TestOrderItem1\",\"businessObjectType\":\"OrderItem\",\"ProductName\":\"Coke\"},{\"id\":\"TestOrderItem2\",\"businessObjectType\":\"OrderItem\",\"ProductName\":\"Pepsi\"}]}]}"
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `data` | String | Payload containing context-specific information. | Required | 59.0 |
| `metadata` | [Context MetaData Input](./connect_requests_context_meta_data_input.htm.md "Input representation of context metadata.") | Metadata information about context. | Required | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
