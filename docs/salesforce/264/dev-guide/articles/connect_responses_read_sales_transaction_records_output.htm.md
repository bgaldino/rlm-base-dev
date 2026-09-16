---
page_id: connect_responses_read_sales_transaction_records_output.htm
title: Read Sales Transaction Records
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_read_sales_transaction_records_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Read Sales Transaction Records

Output representation of the details of a map of keys and associated values. The keys are
    record type names, such as a Quote or QuoteLineItem, and values are lists of records of that
    type.

        
          

**JSON example**

          
: 
            

```
{
  "response": {
    "records": {
      "Quote": [
        {
          "data": {
            "Id": "0Q05g000000AJK954",
            "Name": "Sample Quote",
            "Status": "Draft",
            "TotalPrice": 1500
          }
        }
      ],
      "QuoteLineItem": [
        {
          "data": {
            "Id": "0QL5g000000DEF456",
            "Product2Id": "01t5g000000GUE752",
            "Quantity": 2,
            "UnitPrice": 750,
            "TotalPrice": 1500
          }
        }
      ]
    }
  },
  "isSuccess": true,
  "errorResponse": []
}
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `records` | Map<String, [Sales Transaction Record](./connect_responses_sales_transaction_record_output.htm.md)>> | Map of record type names to the list of records. | Small, 65.0 | 65.0 |
