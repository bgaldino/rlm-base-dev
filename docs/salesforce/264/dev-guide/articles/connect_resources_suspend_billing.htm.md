---
page_id: connect_resources_suspend_billing.htm
title: Suspend Billing (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_suspend_billing.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Suspend Billing (POST)

Suspend billing for billing schedule groups or an account for a
      predefined period.

    
      
        
          

**Resource**

          
: 
            

```
/commerce/invoicing/actions/suspend-billing
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/commerce/invoicing/actions/suspend-billing
```

          

        
        
          

**Available version**

          
: 63.0

        
        
          

**HTTP methods**

          
: POST

        
        
          

**Request body for POST**

          
: 
            

**JSON example**

: 

```
{
    "referenceIds": 
    [
        {
            "referenceId": "001DU000001o2UwYAI",
            "suspendDate": "2024-11-27",
            "resumeDate": "2024-12-27"
        }
    ]
}
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `referenceIds` | [Suspend Billing Object Input](./connect_requests_suspend_billing_entity_input.htm.md)[] | Input representation of the account or billing schedule group IDs to suspend the billing operation for. | Required | 63.0 |

          

        
        
          

**Response body for POST**

          
: [Suspend Resume
              Billing](./connect_responses_suspend_resume_billing_output.htm.md)
