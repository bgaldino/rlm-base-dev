---
page_id: actions_obj_create_collection_plan.htm
title: Create Collection Plan Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_create_collection_plan.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_invocable_actions_parent.htm
fetched_at: 2026-09-29
---

# Create Collection Plan Action

Create one or more collection plans, each with its optional nested
			collection plan items.

		
			

Create multiple collection plans in a single request, each with optional nested collection
				plan items. If an item fails to create, its parent collection plan is rolled
				back.

			

This action is available in API version 68.0 and later.

		

		

## Special Access Rules

			
			

The Create Collection Plan action is available in Enterprise, Developer, and Unlimited
				Editions where Billing is enabled.

		

		

## Supported REST HTTP Methods

			
			
				
					

**URI**

					
: `/services/data/v68.0/actions/standard/createCollectionPlan`

				
				
					

**Formats**

					
: JSON, XML

				
				
					

**HTTP Methods**

					
: POST

				
				
					

**Authentication**

					
: `Authorization: Bearer
							token`

				
			

		

		

## Inputs

			
			

					
					
					
						
							

							

							

						

					

					
						
							

							

							

						

					

				
| Input | Type | Description |
| --- | --- | --- |
| compositeCollection​PlanInput | `CompositeCollectionPlanInput` | Required. Composite input that contains a `collectionPlans` list of collection plans to create. Each collection plan can include a nested list of collection plan items.**collectionPlans** — list of Collection Plan objects: **collectionPlanItems** — Collection Plan Item objects: |

		

		

## Outputs

			
			

					
					
					
						
							

							

							

						

					

					
						
							

							

							

						

					

				
| Output | Type | Description |
| --- | --- | --- |
| compositeCollection​PlanResult | `CompositeCollectionPlanResult` | Composite result that contains a `results` list, with one result for each collection plan in the request.**results** — Collection Plan Result objects: |

		

		

## Example

			
			
				
					

**POST**

					
: 
						

This example shows a sample request for the Create Collection Plan action.

						

```
{
  "inputs": [
    {
      "compositeCollectionPlanInput": {
        "collectionPlans": [
          {
            "accountId": "001xx000003DGXYA2",
            "contactId": "003xx000004TXYZA1",
            "initialDueAmount": 7500.00,
            "collectionPlanSegment": "High Risk",
            "dueDate": "2026-06-15",
            "collectionPlanReasonId": "0cR000000000001",
            "usageType": "Billing",
            "overdueRiskIndicator": "High",
            "collectionPlanItems": [
              { "invoiceId": "inv000000000001" },
              { "invoiceId": "inv000000000002" }
            ]
          }
        ]
      }
    }
  ]
}
```

						

This example shows a sample response for the Create Collection Plan action.

						

```
[
  {
    "actionName": "createCollectionPlan",
    "errors": null,
    "invocationId": null,
    "isSuccess": true,
    "outputValues": {
      "compositeCollectionPlanResult": {
        "results": [
          {
            "collectionPlanId": "1Eu000000000001AAA",
            "collectionPlanItemIds": [
              "1Ev000000000001AAA",
              "1Ev000000000002AAA"
            ],
            "isSuccess": true,
            "errors": null
          }
        ]
      }
    },
    "sortOrder": -1,
    "version": 1
  }
]
```
