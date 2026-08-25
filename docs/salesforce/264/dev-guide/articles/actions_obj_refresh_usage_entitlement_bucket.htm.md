---
page_id: actions_obj_refresh_usage_entitlement_bucket.htm
title: Refresh Usage Entitlement Bucket Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_refresh_usage_entitlement_bucket.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_invocable_actions_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Refresh Usage Entitlement Bucket Action

Refresh entitlements by evaluating the usage entitlement bucket
			records and creating a new usage entitlement entry.

		
			

This action is available in API version 63.0 and later.

		

		

## Special Access Rules

			
			

The Refresh Usage Entitlement Bucket action is available in Enterprise, Developer,
				and Unlimited Editions where Usage Management is enabled. To use this action, you
				need the Usage Management Run Time User permission.

		

		

## Supported REST HTTP Methods

			
			
				
					

**URI**

					
: `/services/data/v68.0/actions/standard/refreshUsageEntitlementBucket`

				
				
					

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
| transactionUsageEntitlementId | **Type** string **Description** Required. ID of the transaction usage entitlement record that's associated with the usage entitlement buckets that you need to refresh. |

		

		

## Outputs

			
			

None.

		

		

## Example

			
			
				
					

**POST**

					
: 
						

This example shows a sample request for the Refresh Usage Entitlement
							Bucket action.

						

```
{
  "inputs": [
    {
      "transactionUsageEntitlementId": "3ttDU00000000iZYAQ"
    }
  ]
}
```

						

This example shows a sample response for the Refresh Usage Entitlement
							Bucket action.

						

```
{
  "actionName": "refreshUsageEntitlementBucket",
  "errors": null,
  "isSuccess": true
}
```

					

				
			

		

	

#### See Also

- [*Salesforce Help*: Permission Set Licenses, Personas, and User Permissions for
       Usage Management](https://help.salesforce.com/s/articleView?id=ind.um_usage_management_psls_and_personas.htm&language=en_US)
