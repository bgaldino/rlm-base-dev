---
page_id: apex_connectapi_input_transfer_record.htm
title: ConnectApi.TransferRecordInputRepresentation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_transfer_record.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: transaction_management_apex_input_classes.htm
fetched_at: 2026-06-09
---

# ConnectApi.TransferRecordInputRepresentation

Input representation of the details of the assets to be transferred.

This Apex class is used by the `transferRecords`
apex-defined input variable. See [Initiate Transfer Action](./actions_obj_initiate_transfer.htm.md "Transfer an asset or multiple assets from one account to another.").

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `assetId` | String | ID of the asset to transfer. | Required | 65.0 |
| `transferQuantity` | Double | Transfer quantity for the request. | Required | 65.0 |
