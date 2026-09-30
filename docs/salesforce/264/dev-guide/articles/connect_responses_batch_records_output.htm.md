---
page_id: connect_responses_batch_records_output.htm
title: Batch Records
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_batch_records_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-09-29
---

# Batch Records

Output representation of a single batch and the records that it contains.

    

## JSON Example

      
      

This example response shows a single batch and the records that it contains.

      

```
{
  "batchIndex": 0,
  "batchRecords": {
    "records": {
      "Quote": [
        {
          "data": {
            "Id": "0Q0d2700000AbCdEAAV",
            "Name": "Q-00001",
            "Status": "Draft",
            "GrandTotalAmount": 1500.00,
            "hasDeletedLines": true
          }
        }
      ],
      "QuoteLineItem": [
        {
          "data": {
            "Id": "0QLd2700000XyZaBAAX",
            "Quantity": 2,
            "Product2Id": "01td2700000PqRsTAAV"
          }
        },
        {
          "data": {
            "Id": "0QLd2700000XyZaCAAX",
            "Quantity": 5,
            "Product2Id": "01td2700000PqRsUAAV"
          }
        }
      ]
    }
  }
}
```

    

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `batchIndex` | Integer | Zero-based index of the batch. | Small, 68.0 | 68.0 |
| `batchRecords` | [Read Sales Transaction Records](./connect_responses_read_sales_transaction_records_output.htm.md) | Records that the batch contains. | Small, 68.0 | 68.0 |
