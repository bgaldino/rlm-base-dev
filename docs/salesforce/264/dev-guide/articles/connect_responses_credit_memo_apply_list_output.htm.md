---
page_id: connect_responses_credit_memo_apply_list_output.htm
title: Credit Memo Apply List
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_credit_memo_apply_list_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Credit Memo Apply List

Output representation of the list of applied credit memo results.

        
          

**JSON example**

          
: 
            

```
{
  "applyCreditResults" : [ {
    "appliedToId" : "3ttxx000000003FAAQ",
    "errors" : null,
    "id" : "4sFxx00000002ppEAA",
    "success" : true
  }, {
    "appliedToId" : "3ttxx0000000001AAA",
    "errors" : null,
    "id" : "4sFxx00000002pqEAA",
    "success" : true
  } ]
}
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `applyCredit​Results` | [Credit Memo Apply](./connect_responses_credit_memo_apply_output.htm.md)[] | Output list of the applied credit memo results. | Big, 62.0 | 62.0 |
