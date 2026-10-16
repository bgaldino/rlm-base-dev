---
page_id: connect_requests_context_tag_input.htm
title: Context Tag Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_tag_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Tag Input 

Input representation of the context tag.

        
          

**JSON example**

          
: 
            

```
{
    "contextTags": [
        {
            "name": "Attribute_Tag",
            "contextAttributeId": "11nxx000001hOozAAE"
        },
        {
            "name": "Node_Tag",
            "contextNodeId": "11oxx000001G9D2AAK"
        }
    ]
}
```

          

        

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextAttributeId` | String | ID of the (parent) context attribute. | Required | 59.0 |
| `contextNodeId` | String | ID of the (parent) context node. | Required | 59.0 |
| `contextTagId` | String | ID of this Context tag. Required only for update. | Optional | 59.0 |
| `name` | String | Name of the context tag. | Required | 59.0 |
