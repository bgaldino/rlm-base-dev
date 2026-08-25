---
page_id: connect_resources_create_billing_schedules_from_any_transaction.htm
title: Create Standalone Billing Schedules (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_create_billing_schedules_from_any_transaction.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Create Standalone Billing Schedules (POST)

Generate billing schedules from any internal or external transaction
      by using context service.

    
      

You can create a billing schedule from any sObject such as WorkOrder, Cart, Order,
        Opportunity, and insurance policy. Or, you can also generate billing schedules from order
        items.

    

    

The Create Standalone Billing Schedules (POST) API uses the StandaloneBillingContext context
                definition to hydrate the context of the transaction. The context definition
                includes these mappings.

        
- The TransactionMapping maps the fields of the transaction to the attributes of the
                    Transaction node.

        
- The BSGEntitiesMapping maps the attributes of the Billing Schedule node, the Billing
          Schedule Group node, and Billing Schedule Group Relationship node to the fields of the
          corresponding Salesforce objects.

      

For the StandaloneBillingContext context definition to hydrate all the required data, transaction
                data for the mandatory context tags are required. Here are the topics that mention
                the mandatory and optional tags, sample transaction details, and sample payloads for
                various types of transactions.

        
- [One-Time New Sale Transaction](./connect_requests_billing_schedule_input_for_one_time_new_sale.htm.md)

        
- [Term-Defined New Sale
          Transaction](./connect_requests_billing_schedule_input_for_termed_new_sale.htm.md)

        
- [Evergreen New Sale Transaction](./connect_requests_billing_schedule_input_for_evergreen_new_sale.htm.md)

        
- [New Sale Transaction With
                        Bundled Products](./connect_requests_billing_schedule_input_for_bundled_products_new_sale.htm.md)

                
- [New Sale Transaction With
                        Ramped Products](./connect_requests_billing_schedule_input_for_ramps_new_sale.htm.md)

        
- [New Sale Transaction With Usage
                        Products](./connect_requests_billing_schedule_input_for_usage_new_sale.htm.md)

                
- [Amended Transaction](./connect_requests_billing_schedule_input_for_amendment.htm.md)

                
- [Renewal Transaction](./connect_requests_billing_schedule_input_for_renewal.htm.md)

                
- [Early Renewal
                        Transaction](./connect_requests_billing_schedule_input_for_early_renewal.htm.md)

                
- [Canceled
                    Transaction](./connect_requests_billing_schedule_input_for_cancellation.htm.md)

      

    

        
          

**Special Access Rules**

          
: This API is available with the Revenue Cloud Billing license.

        
      

        
          

**Resource**

          
: 
            

```
/commerce/invoicing/standalone/billing-schedules/actions/create
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/commerce/invoicing/standalone/billing-schedules/actions/create
```

          

        
        
          

**Available version**

          
: 64.0

        
        
          

**HTTP methods**

          
: POST

        
        
          

**Request body for POST**

          
: 
            

**JSON example**

: 

```
{
  "transactionDetails": "{\"nodeName\": [{\"id\":\"801Az00000aynKZIAY\", \"businessSobjectType\": \"Order\"}]}",
  "transactionContextDetails": {
    "contextDefinitionName": "StandaloneBillingContext",
    "intraContextCustomMappingName": "CustomContextMapping",
    "readContextMappingName": "OrderTransactionMapping",
    "saveContextMappingName": "BSGEntitiesMapping"
  }
}
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `transaction​ContextDetails` | [Standalone Billing Schedule Metadata Input](./connect_requests_context_aware_standalone_billing_schedule_metadata_input.htm.md)[] | Details of the context definition and its mappings that are used to hydrate the transaction data and save it in the appropriate Billing fields. | Required | 64.0 |
| `transaction​Details` | String | Input JSON data that includes the ID of the transaction record for which the billing schedule must be created and other additional transaction details. The API request supports a single mapping ID. You can send separate requests for line items and line details by using their respective mapping IDs. However, this approach can result in duplicate billing schedules for the same line items and line details. | Required | 64.0 |

          

        
      

    
      
        
          

**Response body for POST**

          
: [Context-Aware Billing
              Schedule](./connect_responses_context_aware_billing_schedule_output.htm.md)

        
      

    

  

#### See Also

- [Salesforce Help: Context Service](https://help.salesforce.com/s/articleView?id=ind.context_service_context_definitions.htm&language=en_US)

- [Industries Common Resources Developer Guide: Context Service](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/context_service_overview.htm)

- [BillingScheduleGroup](./sforce_api_objects_billingschedulegroup.htm.md)
