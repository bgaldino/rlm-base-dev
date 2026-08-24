---
page_id: connect_requests_sequence_policy_input.htm
title: Sequence Policy Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_sequence_policy_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Sequence Policy Input

Input representation of the configured rules and properties to generate unique,
    sequential numbers for objects.

**JSON example**

: This example shows a sample request to create a sequence
            policy.

```
{
  "name": "Sample Sequence Policy",
  "description": "This is a sample sequence policy.",
  "effectiveFromDateTime": "2025-08-10",
  "expirationDateTime": "2025-09-20",
  "isActive": true,
  "sequenceMode": "Basic",
  "targetObject": "Invoice",
  "dateStampFormat": "Yyyy",
  "sequenceStartNumber": 1,
  "incrementNumber": 1,
  "maximumSequenceNumber": 1000,
  "minimumSequenceNumberWidth": 2,
  "filterCriteria": "Custom",
  "selectionLogic": "selectionLogic",
  "sequencePattern": "INV-{SequenceValue}-abc",
  "selectionCondition": [
    {
      "filterField": "AppType",
      "operator": "Equals",
      "filterValue": "RLM",
      "conditionNumber": 1
    },
    {
      "filterField": "Status",
      "operator": "Equals",
      "filterValue": "Posted",
      "conditionNumber": 2
    },
    {
      "filterField": "LegalEntity",
      "operator": "Equals",
      "filterValue": "US",
      "conditionNumber": 3
    }
  ]
}
```

**Properties**

: 

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

- 
- 

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

- 
- 

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `dateStamp​Format` | String | Format of the stamp date that's appended to the sequence number. You can't edit this property by using the Update Sequence Policy API. | Required | 65.0 |
| `description` | String | Additional details about the sequence policy. | Optional | 65.0 |
| `effectiveFrom​DateTime` | String | Date and time when the policy becomes effective. The default value is the current date. | Required | 65.0 |
| `expiration​DateTime` | String | Date and time when the policy expires. | Optional | 65.0 |
| `filter​Criteria` | String | Criteria to filter the target objects. | Required | 65.0 |
| `increment​Number` | Integer | Value by which the sequence number increases until it reaches the maximum number. This value must be greater than or equal to `1`. The default value is `1`. You can't edit this property by using the Update Sequence Policy API. | Required | 65.0 |
| `isActive` | Boolean | Indicates whether the policy is active (`true`) or not (`false`). The default value is `false`. | Required | 65.0 |
| `maximumSequence​Number` | Integer | Maximum number the sequence number can reach. | Optional | 65.0 |
| `minimumSequence​NumberWidth` | Integer | Minimum number of digits a sequence number must have. You can't edit this property by using the Update Sequence Policy API. | Optional | 65.0 |
| `name` | String | Name of the sequence policy. | Required | 65.0 |
| `selection​Condition` | [Selection Condition Input](./connect_requests_selection_condition_input.htm.md)[] | Criteria to determine which sequence policy is applied to a record. This property includes conditions based on any standard or custom fields of the record. | Optional | 65.0 |
| `selection​Logic` | String | Logic that determines the objects that the sequence policy applies to. | Optional | 65.0 |
| `sequence​Mode` | String | Specifies how sequence numbers are generated. Valid values are: `Basic`—Assigns sequential numbers without gap reconciliation. `Gapless`—Assigns sequential numbers with gap reconciliation. The usage of this value ensures that the posted invoices or credit memos don't have any numbering gaps for audits and compliance. You can't edit this property by using the Update Sequence Policy API. | Required | 65.0 |
| `sequence​Pattern` | String | Pattern structure that’s followed for the sequence. | Required | 65.0 |
| `sequenceStart​Number` | Integer | Starting value of the sequence number, which must be greater than or equal to `0`. The default value is `1`. You can't edit this property by using the Update Sequence Policy API. | Required | 65.0 |
| `target​Object` | String | Object that the policy is applied to. Valid values are: `Invoice` `CreditMemo`—Available in API version 66.0 and later. You can't edit this property by using the Update Sequence Policy API. | Required | 65.0 |
| `timeZone` | String | Time zone that’s applicable for the sequence policy. | Optional | 65.0 |
