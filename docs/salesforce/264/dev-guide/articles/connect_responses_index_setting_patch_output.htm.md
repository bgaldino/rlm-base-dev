---
page_id: connect_responses_index_setting_patch_output.htm
title: Index Setting Update
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_index_setting_patch_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Index Setting Update

Output representation of the details of the updated index setting.

    
      
        
          

**JSON example**

          
: 
            

```
{
   "setting" : {
        "supportedLanguages" : ["en_US","ja","es","nl_NL"],
        "id": "1JySG0000000GUb0AM",
        "defaultLanguage" : "en_US"
   },
   "errors" : [],
   "statusCode" : "200"
}
```

          

        
      

    

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Error Output](./connect_responses_epc_error_output.htm.md)[] | List of errors, if any. | Small, 63.0 | 63.0 |
| `setting` | [Setting](./connect_responses_setting_output.htm.md)[] | Setting that’s used in indexing and maintained for an org. | Small, 63.0 | 63.0 |
| `statusCode` | String | Code that indicates the status of the API request. | Small, 63.0 | 63.0 |
