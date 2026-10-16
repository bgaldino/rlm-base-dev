---
page_id: connect_resources_consumption_traceabilities.htm
title: Consumption Traceabilities (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_consumption_traceabilities.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Consumption Traceabilities (POST)

Get a comprehensive breakdown of overage charges and resource drawdown,
      enabling you to view information that's applicable to specific invoice lines.

This API provides an automated, clear, and traceable breakdown of all charges with
        details of specific rates, tiers, and discounts.

        
          

**Resource**

          
: 
            

```
/revenue/usage-management/consumption/actions/trace
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/revenue/usage-management/consumption/actions/trace
```

          

        
        
          

**Available version**

          
: 66.0

        
        
          

**HTTP methods**

          
: POST

        
        
          

**Request body for POST**

          
: 
            

**JSON example**

: 

```
{
  "liableSummaryIds": [
    "1HG000000000001"
  ]
}
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `liableSummaryIds` | String[] | List of liable summary IDs to trace the consumption. | Required | 66.0 |

          

        
        
          

**Response body for POST**

          
: [Consumption
              Traceabilities](./connect_responses_consumption_traceabilities_output.htm.md)
