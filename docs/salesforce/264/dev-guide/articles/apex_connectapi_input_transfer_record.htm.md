---
page_id: apex_connectapi_input_transfer_record.htm
title: ConnectApi.TransferRecordInputRepresentation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_transfer_record.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: transaction_management_apex_input_classes.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ConnectApi.TransferRecordInputRepresentation

Input representation of the details of the assets to be transferred.

This Apex class is used by the `transferRecords`
        apex-defined input variable. See [Initiate Transfer Action](./actions_obj_initiate_transfer.htm.md).

          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `assetId` | String | ID of the asset to transfer. | Required | 65.0 |
| `transferQuantity` | Double | Transfer quantity for the request. | Required | 65.0 |
