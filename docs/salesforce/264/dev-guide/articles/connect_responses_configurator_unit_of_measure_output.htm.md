---
page_id: connect_responses_configurator_unit_of_measure_output.htm
title: Configurator Unit Of Measure
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_configurator_unit_of_measure_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Configurator Unit Of Measure

Output representation of the details of the unit of measure record.

      
        
          

**JSON Example**

          
: 
            

```
{
  "unitOfMeasure": {
    "id": "0hEXR00000000BJ2AY",
    "name": "Litres",
    "roundingMethod": "Down",
    "scale": 2,
    "unitCode": "Ltrs"
  }
}
```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `id` | String | ID of the unit of measure record. | Small, 63.0 | 63.0 |
| `name` | String | Name of the unit of measure record. | Small, 63.0 | 63.0 |
| `rounding​Method` | String | Rounding method associated with the unit of measure record. | Small, 63.0 | 63.0 |
| `scale` | Integer | Scale associated with the unit of measure record. | Small, 63.0 | 63.0 |
| `unitCode` | String | Unit code associated with the unit of measure record. | Small, 63.0 | 63.0 |
