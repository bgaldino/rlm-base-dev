---
page_id: actions_obj_create_billing_schedule_from_billing_transaction.htm
title: Create Billing Schedules From Billing Transaction Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_create_billing_schedule_from_billing_transaction.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_invocable_actions_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Create Billing Schedules From Billing Transaction Action

Create one or more billing schedules for a specified billing
			transaction ID.

		
			

This action calls the [Create Billing Schedules
					for Orders (POST) API](./connect_resources_create_billing_schedules.htm.md) to retrieve the billing transaction items
				associated with the billing transaction ID. The API generates the corresponding
				billing schedules for each of the billing transaction items for operations such as
				transaction modifications, renewals, cancellations, and new sales.

			

This action is available in API version 62.0 and later.

		

		

## Special Access Rules

			
			

The Create Billing Schedules From Billing Transaction action is available in Enterprise,
				Unlimited, and Developer Editions where Billing is enabled. To use this action, you
				need the Create Billing Schedules From Billing Transactions API permission set.

		

		

## Supported REST HTTP Methods

			
			
				
					

**URI**

					
: `/services/data/v68.0/actions/standard/createBillingSchedulesFromBillingTransaction`

				
				
					

**Formats**

					
: JSON, XML

				
				
					

**HTTP Methods**

					
: POST

				
				
					

**Authentication**

					
: `Authorization: Bearer
							token`

				
			

		

		

## Inputs

			
			

					
					
					
						
							

							

						

					

					
						
							

							

: 

: 

						

					

				
| Input | Details |
| --- | --- |
| billingTransactionId | **Type** string **Description** Required. ID of the billing transaction record to create one or more billing schedules for. |

		

		

## Outputs

			
			

					
					
					
						
							

							

						

					

					
						
							

							

: 

: 

						

						
							

							

: 

: 

						

					

				
| Output | Details |
| --- | --- |
| requestId | **Type** string **Description** Universally Unique Identifier (UUID) that’s used to track the status of the asynchronous action. |
| statusUrl | **Type** string **Description** URL that’s used to check the status of the API request. |

		

		

## Example

			
			
				
					

**POST**

					
: 
						

This example shows a sample request for the Create Billing Schedules From Billing
							Transaction action.

						

```
{
  "inputs": [
    {
      "billingTransactionId": "801xx000003JztvAAC"
    }
  ]
}
```

						

This example shows a sample response for the Create Billing Schedules
							From Billing Transaction action.

						

```
{
  "actionName": "createBillingSchedulesFromBillingTransaction",
  "errors": null,
  "isSuccess": true,
  "outputValues": {
    "requestId": "4sFDU00000000652AA",
    "statusUrl": "/services/data/v62.0/sobjects/AsyncOperationTracker/16Pxx0000004NhAEAU"
  },
  "sortOrder": -1,
  "version": 1
}
```

					

				
			

		

	

#### See Also

- [*Revenue Cloud Developer Guide*: Context-Aware Billing
                            Schedule API](./connect_resources_create_billing_schedules.htm.md)
