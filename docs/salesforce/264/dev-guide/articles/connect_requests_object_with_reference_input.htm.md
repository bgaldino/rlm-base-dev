---
page_id: connect_requests_object_with_reference_input.htm
title: Object with Reference Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_object_with_reference_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Object with Reference Input

Input representation of a list of records to be inserted or updated. To update a
    record, specify the record ID.

    

This is a sample request to create a sales transaction for an order line item.

        
          

**JSON example**

          
: 
            

```
{
  "referenceId": "refOrderItem0",
  "record": {
    "attributes": {
      "type": "OrderItem",
      "method": "POST"
    },
    "OrderId": "@{refOrder.id}",
    "OrderActionId": "@{refOrderAction.id}",
    "PricebookEntryId": "01uRM000000igZG",
    "Quantity": 2
  }
}
```

          

        
      

This is a sample request to update an order line item.

        
          

**JSON example**

          
: 
            

```
{
  "referenceId": "refOrderItem0",
  "record": {
    "attributes": {
      "type": "OrderItem",
      "method": "PATCH",
      "id": "402xx000003KY5vJGH"
    },
    "OrderId": "@{refOrder.id}",
    "OrderActionId": "@{refOrderAction.id}",
    "PricebookEntryId": "01uRM000000igZG",
    "Quantity": 2,
    "UnitPrice": 800
  }
}
```

          

        
      

        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `referenceId` | String | Reference ID that maps to the response and can be used as a reference in later subrecords. This property value starts with a letter or number only and can contain letters, numbers, and underscores. It's also case-sensitive when used for referencing. | Required | 60.0 |
| `records` | [Object Input Map](./connect_requests_object_input_representation_map.htm.md) | Details of a record to be ingested. | Required | 60.0 |
