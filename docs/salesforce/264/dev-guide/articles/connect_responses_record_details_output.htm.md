---
page_id: connect_responses_record_details_output.htm
title: Record Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_record_details_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Record Details

Output representation of the record details including ID and name.

      
        
          

**JSON example**

          
: This example shows the record details with ID and name.

```
{
  "records": [
    {
      "id": "a0bxx0000004CqZAAU",
      "name": "PUR-001"
    }
  ]
}
```

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `id` | String | Unique identifier of the object. | Big, 66.0 | 66.0 |
| `name` | String | Display name of the object. | Big, 66.0 | 66.0 |
