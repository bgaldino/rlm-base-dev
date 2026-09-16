---
page_id: connect_responses_unit_of_measure_error_output.htm
title: Unit of Measure Error
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_unit_of_measure_error_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Unit of Measure Error

Output representation of the details of errors encountered during the processing of the
    Unit of Measure API request.

      
        
          

**JSON example**

          
: 
            

```
  "errorCodeToErrorMap": {
    "UNIT_OF_MEASURE_INFO_INVALID_UOM_IDS": {
      "errorCode": "UOM_INFO_API_003",
      "messageDetail": "Invalid uomId is passed. Please specify a valid uomId.",
      "messageTitle": "Invalid uomId is passed.",
      "recordIds": [
        "sample"
      ],
      "source": "Unit_Of_Measure_Info_Api"
    }
  }
```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Localized error code. | Small, 63.0 | 63.0 |
| `messageDetail` | String | Localized details of the error message. | Small, 63.0 | 63.0 |
| `messageTitle` | String | Localized title of the error message. | Small, 63.0 | 63.0 |
| `recordIds` | String[] | List of erroneous record IDs. | Small, 63.0 | 63.0 |
| `source` | String | Localized source of the error. | Small, 63.0 | 63.0 |
