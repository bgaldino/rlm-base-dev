---
page_id: connect_resources_retrieve_place_sales_transaction_error.htm
title: Retrieve Sales Transaction API Errors (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_retrieve_place_sales_transaction_error.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_business_apis_rest_references.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Retrieve Sales Transaction API Errors (GET)

Retrieve any asynchronous error details associated with
      a sales transaction request.

    
      

This API returns detailed error status and a retryable payload from [Place Sales Transaction API](./connect_resources_place_sales_transaction.htm.md)
        that runs asynchronously. Also, view any blocking errors that prevent a subrequest from
        persisting. This request doesn’t return any non-blocking warnings, such as configuration or
        tax warnings.

      

You can view the list of `rollbackedReferenceIds`, which
        shows synthetic or reference IDs that roll back when the batch fails.

      
        
          

**Resource**

          
: 
            

```
connect/revenue/transaction-management/sales-transactions/actions/place/trackerId/errors
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/revenue/transaction-management/sales-transactions/actions/place/16PRM0000004DBq/errors
```

          

        
        
          

**Available version**

          
: 66.0

        
        
          

**HTTP methods**

          
: GET

        
        
          

**Request parameter for GET**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                

              
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `includeRetryable​Payload` | Boolean | Indicates whether to return a subset of the original Place Sales Transaction API payload errors (`true`) or not (`false`). The default value is `false`. | Optional | 66.0 |

          

        
        
          

**Response body for GET**

          
: [Sales Transaction
              Async Error](./connect_responses_place_sales_transaction_async_error_output.htm.md)
