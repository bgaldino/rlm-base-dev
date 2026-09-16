---
page_id: actions_obj_recover_billing_schedule.htm
title: Recover Billing Schedules Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_recover_billing_schedule.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_invocable_actions_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Recover Billing Schedules Action

Recover one or more billing schedules in the `Error` or `Processing` status.

		

This action uses the ID of the billing schedule record in the `Error` or `Processing` status to
				retrieve the latest generated invoice. This action also retrieves any other billing
				schedules in the `Error` or `Processing` status associated with that invoice.

This action is available in API version 62.0 and later.

		

## Special Access Rules

			
			

The Recover Billing Schedules action is available in Enterprise, Unlimited, and
				Developer Editions where Billing is enabled. To use this action, you need the Manage
				Errors Using Invoice Error Recovery API permission set.

		

		

## Supported REST HTTP Methods

			
			
				
					

**URI**

					
: `/services/data/v68.0/actions/standard/recoverBillingSchedules`

				
				
					

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
| billingScheduleId | **Type** string **Description** Required. ID of the billing schedule record in the `Error` or `Processing` status. |

		

		

## Outputs

			
			

					
					
					
						
							

							

						

					

					
						
							

							

: 

: 

						

					

				
| Output | Details |
| --- | --- |
| successBillingScheduleIds | **Type** string **Description** Comma-separated list of IDs associated with the parent billing schedule record in the `Error` or `Processing` status. |

		

		

## Example

			
			
				
					

**POST**

					
: 
						

This example shows a sample request for the Recover Billing Schedules
							action.

						

```
{
  "inputs": [
    {
      "billingScheduleId": "801xx000003JztvAAC"
    }
  ]
}
```

						

This example shows a sample response for the Recover Billing Schedules
							action.

						

```
{
  "actionName": "recoverBillingSchedules",
  "errors": null,
  "isSuccess": true,
  "outputValues": {
    "successBillingScheduleIds": ["4sFDU00000000652AA", 16Pxx0000004NhAEAU]
  },
  "sortOrder": -1,
  "version": 1
}
```
