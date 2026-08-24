---
page_id: connect_requests_context_aware_standalone_billing_schedule_metadata_input.htm
title: Standalone Billing Schedule Metadata Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_context_aware_standalone_billing_schedule_metadata_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Standalone Billing Schedule Metadata Input

Input representation of the metadata details to create a billing schedule. This
    representation includes the name of the context definition and context mapping along with the
    mapping details of the transaction, billing schedule, and billing schedule group.

          

**JSON example**

          
: 

```
{
  "transactionDetails": "{\"nodeName\": [{\"id\":\"001SG000004FvlGYAS\", \"businessSobjectType\": \"Account\", \"Quantity\":\"4\" , \"Name\": \"TestAccount\"}]}",
  "transactionContextDetails": {
    "contextDefinitionName": "StandaloneBillingContext",
    "intraContextCustomMappingName": "CustomContextMapping",
    "readContextMappingName": "OrderTransactionMapping",
    "saveContextMappingName": "BSGEntitiesMapping"
  }
}
```

This example shows a sample request to generate billing schedules from order
            items by specifying the BillingContext standard context definition as the context
            definition name.

```
{
  "transactionDetails": "{\"nodeName\": [{\"id\":\"001SG000004FvlGYAS\", \"businessSobjectType\": \"Account\", \"Quantity\":\"4\" , \"Name\": \"TestAccount\"}]}",
  "transactionContextDetails": {
    "contextDefinitionName": "BillingContext__stdctx",
    "readContextMappingName": "OrderEntitiesMapping",
    "saveContextMappingName": "BSGEntitiesMapping"
  }
}
```

        

**Properties**

: 

                  
                    

                    

                    

                    

                    

                  

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `context​Definition​Name` | String | Name of the context definition that’s used to hydrate the context to generate the billing schedule. To generate billing schedules from order items, specify the BillingContext standard context definition as the context definition name. Applicable from API version 66.0 and later. | Required | 64.0 |
| `intraContext​CustomMapping​Name` | String | Name of the cross-context custom mapping that's used to map Billing fields to Transaction fields. Use this mapping to populate the Billing fields with the values stored in custom transaction fields. | Optional | 65.0 |
| `readContext​Mapping​Name` | String | Name of the context mapping with the mapping for the transaction. | Required | 64.0 |
| `saveContext​Mapping​Name` | String | Name of the context mapping with the mapping for the billing schedule and billing schedule group. | Required | 64.0 |
