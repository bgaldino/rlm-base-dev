---
page_id: connect_responses_qualification_context_output.htm
title: Qualification Context
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_qualification_context_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Qualification Context

Output representation of the details about the product qualification.

      
        
          

**JSON example**

          
: 
            

```
{
  "qualificationContext": {
    "isQualified": true
  }
}
```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `isQualified` | Boolean | Indicates whether the product is qualified (`true`) or not (`false`). | Small, 67.0 | 67.0 |
| `reason` | String | Specifies the reason for product qualification or disqualification. | Small, 67.0 | 67.0 |
