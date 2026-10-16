---
page_id: connect_responses_rules_application_error_output.htm
title: Rules Application Error
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_rules_application_error_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Rules Application Error

Output representation of the error details for rules application failure.

      
        
          

**JSON example**

          
: This example shows the rules application error.

```
{
  "errors": [
    {
      "errorCode": "INVALID_ACCOUNT",
      "message": "The specified account does not exist or is not accessible."
    }
  ]
}
```

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Code that indicates the type of error. | Big, 66.0 | 66.0 |
| `message` | String | Message that states the reason for error, if any. | Big, 66.0 | 66.0 |
