---
page_id: connect_responses_binding_object_resource_grant_and_policy_detail_output.htm
title: Binding Object Resource Grant And Policy Detail
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_binding_object_resource_grant_and_policy_detail_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Binding Object Resource Grant And Policy Detail

Output representation of the details of resource grants and binding policies.

        
          

**JSON example**

          
: This example includes the details of resource grants and binding policies for a
            specified binding object.

```
{
  "bindingObjectResourceGrantAndPolicyDetail": {
    "bindingObjectGrantDetail": [
      {
        "effectiveEndDate": "Sat Oct 04 23:59:59 GMT 2025",
        "effectiveStartDate": "Fri Sep 05 00:00:00 GMT 2025",
        "grantType": "Grant",
        "id": "1B0SB0000000Eiv0AE",
        "product": {
          "id": "01tSB000006XMtqYAG"
        },
        "quantity": 100,
        "record": {
          "id": "02iSB000000IoETYA0"
        },
        "unitOfMeasure": {
          "id": "0hESB0000003yfp2AA"
        },
        "usageRefreshPolicy": {
          "id": "1BYSB0000001lOH4AY",
          "negotiable": null
        },
        "usageRolloverPolicy": {
          "id": "1BVSB000000A1xJ4AS",
          "negotiable": null
        },
        "validityPeriodTerm": 1,
        "validityPeriodUnit": "Month"
      }
    ],
    "bindingObjectResourcePolicyDetail": {
      "drawdownOrder": "ExpiringFirst",
      "id": "1X2SB00000002WT0AY",
      "ratingFrequencyPolicy": {
        "id": "1HJSB0000000G3B4AU",
        "negotiable": null
      },
      "usageAggregationPolicy": {
        "id": "1cfSB0000001xHPYAY",
        "negotiable": null
      },
      "usageCommitmentPolicy": {
        "id": null,
        "negotiable": null
      },
      "usageOveragePolicy": {
        "id": "7UkSB00000002OP0AY",
        "negotiable": null
      }
    }
  }
}
```

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `bindingObject​Grant​Detail` | [Binding Object Grant Detail](./connect_responses_binding_object_grant_detail_output.htm.md)[] | Details of the negotiated resource grants for the specified binding object. | Big, 65.0 | 65.0 |
| `bindingObject​ResourcePolicy​Detail` | [Binding Object Resource Policy Detail](./connect_responses_binding_object_resource_policy_detail_output.htm.md) | Detail of the binding policies. | Big, 65.0 | 65.0 |
