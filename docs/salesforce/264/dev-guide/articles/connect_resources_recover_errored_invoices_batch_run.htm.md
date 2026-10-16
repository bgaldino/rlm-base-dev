---
page_id: connect_resources_recover_errored_invoices_batch_run.htm
title: Invoice Run Recovery (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_recover_errored_invoices_batch_run.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Invoice Run Recovery (POST)

Recover records associated with a failed invoice run. Recovery is
      required only when billing schedules remain in the `Processing`, `Void In Progress`, or `Error` status.

    
      
        
          

**Special Access Rules**

          
: To use this API, you need the Invoice Scheduler API permission set.

        
        
          

**Resource**

          
: 
            

```
/commerce/invoicing/invoice-batch-runs/invoiceBatchRunId/actions/recover
```

          

          
: The invoiceBatchRunId parameter is the ID of the failed invoice
            batch run record whose details you want to retrieve.

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/commerce/invoicing/invoice-batch-runs/5IRxx0000004TwGGAU/actions/recover
```

          

        
        
          

**Available version**

          
: 62.0

        
        
          

**HTTP methods**

          
: POST

        
        
          

**Response body for POST**

          
: [Invoice Batch Run Recovery](./connect_responses_invoice_batch_run_recovery_output.htm.md)
