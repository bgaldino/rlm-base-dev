---
page_id: connect_requests_context_input.htm
title: Context Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Input

Input representation for defining a context.

**JSON example**

: 

```
{
  "metadata": {
    "contextDefinitionId": "11Oxx0000006VjNEAU",
    "mappingId": "11jxx0000004Q83AAE"
  },
  "data": "{\"Order\":[{\"id\":\"TestOrder123\",\"businessObjectType\":\"Order\",\"Name\":\"Test Order\",\"Status\":\"SHIPPED\",\"AccountName\":\"Kroger\",\"OrderItems\":[{\"id\":\"TestOrderItem1\",\"businessObjectType\":\"OrderItem\",\"ProductName\":\"Coke\"},{\"id\":\"TestOrderItem2\",\"businessObjectType\":\"OrderItem\",\"ProductName\":\"Pepsi\"}]}]}"
}
```

**Properties**

: 

                    

                    

                    

                    

                    

                  

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `data` | String | Payload containing context-specific information. | Required | 59.0 |
| `metadata` | [Context MetaData Input](./connect_requests_context_meta_data_input.htm.md) | Metadata information about context. | Required | 59.0 |
