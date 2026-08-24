---
page_id: actions_obj_create_order_from_quote.htm
title: Create Order From Quote Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_create_order_from_quote.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_invocable_actions_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Create Order From Quote Action

Create a draft order from a quote record.

		
			

This action is available in API version 60.0 and later.

			

#### Note

 This API has been deprecated as of API version 65.0. In API version 65.0 and
				later, use the [Create
					Orders From Quote Action](./actions_obj_create_orders_from_quote.htm.md).

		

		

## Special Access Rules

			
			

The Create Order From Quote action is available in Enterprise, Unlimited, and Developer
				Editions of Revenue Management.

		

		

## Supported REST HTTP Methods

			
			
				
					

**URI**

					
: `/services/data/v68.0/actions/standard/createOrderFromQuote`

				
				
					

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
| quoteRecordId | **Type** id **Description** Required. ID of the quote record. |

		

		

## Outputs

			
			

					
					
					
						
							

							

						

					

					
						
							

							

: 

: 

						

						
							

							

: 

: 

						

						
							

							

: 

: 

						

					

				
| Output | Details |
| --- | --- |
| orderId | **Type** string **Description** ID of the created draft order. |
| orderNumber | **Type** string **Description** Unique order number of the created draft order. |
| requestId | **Type** string **Description** ID of the request. |

		

		

## Example

			
			
				
					

**POST**

					
: 
						

This sample request is for the Create Order From Quote action.

						

```
{
    "inputs": [
        {
        "quoteRecordId": "0Q0D200000000DhKAI"
        }
    ]
}
```

						

This sample response is for the Create Order From Quote action.

						

```
[
  {
    "actionName": "createOrderFromQuote",
    "errors": null,
    "invocationId": null,
    "isSuccess": true,
    "outcome": null,
    "outputValues": {
      "orderNumber": "00000122",
      "orderId": "801oB000000DCrNQAW"
    },
    "sortOrder": -1,
    "version": 1
  }
]
```
