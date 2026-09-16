---
page_id: connect_responses_unit_of_measure_status.htm
title: Unit of Measure Status
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_unit_of_measure_status.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Unit of Measure Status

Output representation of the status of the Unit of Measure API request.

      
        
          

**JSON example**

          
: 
            

```
  "status": {
    "errors": [],
    "httpStatusCode": "200",
    "message": " Successfully fetched UnitOfMeasure Info. "
  }
```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Unit Of Measure Error](./connect_responses_unit_of_measure_error_output.htm.md)[] | Errors encountered during the processing of the API request. | Small, 63.0 | 63.0 |
| `httpStatus​Code` | String | HTTP status code of the API request. | Small, 63.0 | 63.0 |
| `message` | String | Localized response message. | Small, 63.0 | 63.0 |
