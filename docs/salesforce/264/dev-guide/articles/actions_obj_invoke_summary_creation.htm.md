---
page_id: actions_obj_invoke_summary_creation.htm
title: Invoke Summary Creation Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_invoke_summary_creation.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_invocable_actions_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Invoke Summary Creation Action

Invoke the service that creates various summaries, such as usage,
			ratable, and liable summaries where the usage amount is zero. The service also checks
			and updates the billing period of the usage entitlement account if the billing period is
			expired.

		
			

This action is available in API version 63.0 and later.

		

		

## Special Access Rules

			
			

The Invoke Summary Creation action is available in Enterprise, Developer,
				and Unlimited Editions where Usage Management is enabled. To use this action, you
				need the Usage Management Run Time User permission.

		

		

## Supported REST HTTP Methods

			
			
				
					

**URI**

					
: `/services/data/v68.0/actions/standard/invokeSummaryCreationService`

				
				
					

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
| usageEntitlementAccountId | **Type** string **Description** Required. ID of the usage entitlement account record that’s used to create summaries. |

		

		

## Outputs

			
			

None.

		

		

## Example

			
			
				
					

**POST**

					
: 
						

This example shows a sample request for the Invoke Summary Creation
							action.

						

```
{
  "inputs": [
    {
      "usageEntitlementAccountId": "3ttDU00000000iZYAQ"
    }
  ]
}
```

						

This example shows a sample response for the Invoke Summary Creation
							action.

						

```
{
  "actionName": "invokeSummaryCreationService",
  "errors": null,
  "isSuccess": true
}
```

					

				
			

		

	

#### See Also

- [*Salesforce Help*: Permission Set Licenses, Personas, and User Permissions for
       Usage Management](https://help.salesforce.com/s/articleView?id=ind.um_usage_management_psls_and_personas.htm&language=en_US)
