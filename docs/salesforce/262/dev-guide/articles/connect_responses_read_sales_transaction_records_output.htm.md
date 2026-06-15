---
page_id: connect_responses_read_sales_transaction_records_output.htm
title: Read Sales Transaction Records
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_read_sales_transaction_records_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-06-09
---

# Read Sales Transaction Records

Output representation of the details of a map of keys and associated values. The keys are
record type names, such as a Quote or QuoteLineItem, and values are lists of records of that
type.

JSON example
:   ```
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
| `records` | Map<String, [Sales Transaction Record](./connect_responses_sales_transaction_record_output.htm.md "Generic output representation for any sales transaction record type.")>> | Map of record type names to the list of records. | Small, 65.0 | 65.0 |
