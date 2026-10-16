---
page_id: connect_resources_get_catalogs.htm
title: Catalog List (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_catalogs.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Catalog List (POST)

Retrieve, search, filter, or sort catalog
    records.

    
      
        
          

**Resource**

          
: 
            

```
/connect/pcm/catalogs
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/catalogs
```

          

        
        
          

**Available version**

          
: 60.0

        
        
          

**Requires Chatter**

          
: No

        
        
          

**HTTP methods**

          
          
          
: POST

#### Note

The POST method is used to retrieve the catalog records instead of the GET
              method as a request payload is sent to filter the
          records.

        
        
          

**Request body for POST**

          
: 
            

**JSON example**

          
: This example shows how to retrieve catalogs that contain `apple` in the catalog name.

: 

```
{
"pageSize": 100,
"offset": 0,
"language": "french",
"filter": {
"criteria": [
{
"property": "name",
"operator": "contains",
"value": "apple"
}
]
}
}
```

          
: This example shows how to retrieve catalogs with `ServiceProcess` as the catalog type.

          
: 
            

```
{
"pageSize": 100,
"offset": 0,
"sort": {
  "orders": [
   {
   "property": "name",
   "direction": "desc"
   }
  ]
 },
"filter": {
"criteria": [
{
"property": "catalogType",
"operator": "eq",
"value": "ServiceProcess"
}
]
}
}
```

          

**Properties**

: 

- 
- 
- 

                  
                    

                    

                    

                    

                    

                  

- 
- 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `correlation​Id` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Optional | 60.0 |
| `filter` | [Filter](./connect_requests_criteria.htm.md) | Criteria to filter the records. Filters are applicable to the fields of the ProductCatalog object. The supported operators are: `eq` `in` `contains` The supported properties are `name` and `catalogType`. | Optional | 60.0 |
| `language` | String | Custom language that you can specify to get translated data for the fields of an object that's enabled for translation. See [Translate Product and Product Category Data](https://help.salesforce.com/s/articleView?id=ind.product_catalog_translate_product2_and_productcategory_data.htm&language=en_US). | Optional | 64.0 |
| `offset` | Integer | Number of records to skip. The default value is 0. | Optional | 60.0 |
| `page​Size` | Integer | Number of records per page. Valid values are from 1 through 100. If unspecified, defaults to 100. | Optional | 60.0 |
| `sort` | [Sort](./connect_requests_order.htm.md) | Sort order of the catalog records. The supported operators are: `asc` `desc` | Optional | 60.0 |

          

        
        
          

**Response body for POST**

          
: [Catalogs Output](./connect_responses_catalogs_output.htm.md)
