---
page_id: actions_obj_post_draft_invoice_batch_run.htm
title: Post Draft Invoice Batch Run Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_post_draft_invoice_batch_run.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_invocable_actions_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Post Draft Invoice Batch Run Action

Update the status of a batch of invoices from `Draft` to `Posted`
			for a credit memo application.

		
			

This action uses the ID of the invoice batch run record to find draft invoices from the batch
				and to post the draft invoices to an invoice record. This action is available in API
				version 62.0 and later.

		

		

## Special Access Rules

			
			

The Post Draft Invoice Batch Run action is available in Enterprise, Unlimited, and Developer
				Editions where Billing is enabled. To use this action, you need the Billing
				Operations User permission set.

		

		

## Supported REST HTTP Methods

			
			
				
					

**URI**

					
: `/services/data/v68.0/actions/standard/postDraftInvoiceBatchRun`

				
				
					

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
| invoiceBatchRunId | **Type** string **Description** Required. ID of the invoice batch run record that created the draft invoices. |

		

		

## Outputs

			
			

					
					
					
						
							

							

						

					

					
						
							

							

: 

: 

						

					

				
| Output | Details |
| --- | --- |
| invBatchDraftToPostedRunId | **Type** string **Description** ID of the record that’s created to track the batch process of posting draft invoices. These draft invoices are associated with the parent invoice batch run record. |

		

		

## Example

			
			
				
					

**POST**

					
: 
						

This example shows a sample request for the Post Draft Invoice Batch Run
							action.

						

```
{
  "inputs": [
    {
      "invoiceBatchRunId": "5IRSG000001Az014AC"
    }
  ]
}
```

						

This example shows a sample response for the Post Draft Invoice Batch Run
							action.

						

```
{
  "actionName": "postDraftInvoiceBatchRun",
  "errors": null,
  "isSuccess": true,
  "outputValues": {
    "invBatchDraftToPostedRunId": "4sFDU00000000652AA"
  }
}
```
