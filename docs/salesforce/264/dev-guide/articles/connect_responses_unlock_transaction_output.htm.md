---
page_id: connect_responses_unlock_transaction_output.htm
title: Unlock Transaction
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_unlock_transaction_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-09-29
---

# Unlock Transaction

Output representation of the request to unlock a sales transaction.

    

## JSON Example

      
      

This example shows a sample response when the unlock operation is successful.

      

```
{
  "isSuccess": true,
  "errorResponse": []
}
```

      

This example shows a sample response when the transaction is already in a terminal status and can’t be unlocked.

      

```
{
  "isSuccess": false,
  "errorResponse": [
    {
      "errorCode": "INVALID_STATUS",
      "message": "Can't update the status because the transaction is already completed with pricing."
    }
  ]
}
```

    

    
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `isSuccess` | Boolean | Indicates whether the unlock operation was successful (`true`) or not (`false`). | Small, 68.0 | 68.0 |
| `error​Response` | [Sales Transaction Error Response](./connect_responses_place_sales_transaction_error_response.htm.md)[] | List of errors if the operation failed. | Small, 68.0 | 68.0 |
