---
page_id: connect_responses_pricing_simulation_input_variables_with_data_output.htm
title: Pricing Simulation Input Variables With Data
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_pricing_simulation_input_variables_with_data_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Pricing Simulation Input Variables With Data

Output representation of the pricing simulation variables with data.

        
          

**JSON example**

          
: 
            

```
{
  "error": "",
  "simulationInputJsonWithData": "{\"SalesTransaction\": [{\"PriceBooks\": \"01sxx0000005ptpAAA\",\"SalesTransactionItem\": [{\"LineItemQuantity\": 4,\"ProductSellingModel\": null,\"Product\": \"01txx0000006i2SAAQ\",\"LineItem\": \"0QLxx0000004C92GAE\"},{\"LineItemQuantity\": 3,\"ProductSellingModel\": null,\"Product\": \"01txx0000006i2TAAQ\",\"LineItem\": \"0QLxx0000004C93GAE\"}]}]}",
  "success": true
}
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | String | Returns the cause of error, if any. For a successful request, this API returns an empty string. | Small, 64.0 | 64.0 |
| `simulationInput​JsonWith​Data` | String | Resultant simulation input variables with quote or order data such as ID, which was specified in the query parameters. | Small, 64.0 | 64.0 |
| `success` | Boolean | Indicates whether the request was successful (`true`) or not (`false`). | Small, 64.0 | 64.0 |
