---
page_id: connect_requests_filter_criteria_input.htm
title: Filter Criteria Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_filter_criteria_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Filter Criteria Input

Input representation of the criteria to filter records based on supported
    properties.

**JSON example**

: 

```

"criteria":
 [{
   "attributeType": "ProductStandard",
   "property": "name",
   "operator": "eq",
   "value": "iPhone"
 }]
```

**Properties**

: 

                  
                    

                    

                    

- 
- 
- 
- 
- 

                    

                    

                  

- 
- 
- 
- 
- 
- 
- 

                    

                    

                    

                    

                    

                  

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `attributeType` | String | Search attribute type of the facet for a faceted search. Valid values are: `ProductStandard` `ProductCustom` `ProductDynamicAttribute` `ProductAttributeStandard` `ProductAttributeCustom` | Optional | 63.0 |
| `operator` | String | Operator used for the filter criteria. The supported operators are: `eq` `in` `contains` `gt`—Specifies a greater than criteria. Available from API version 63.0 and later for Number, Date, and Datetime data types only. `lt`—Specifies a less than criteria. Available from API version 63.0 and later for Number, Date, and Datetime data types only. `gte`—Specifies a greater than or equal to criteria. Available from API version 63.0 and later for Number, Date, and Datetime data types only. `lte`—Specifies a less than or equal to criteria. Available from API version 63.0 and later for Number, Date, and Datetime data types only. | Required | 60.0 |
| `property` | String | Property name to use in the filter, which must be the same as the object field. The supported property is `name`. | Required | 60.0 |
| `value` | Object | Value for the filter criteria. | Required | 60.0 |
