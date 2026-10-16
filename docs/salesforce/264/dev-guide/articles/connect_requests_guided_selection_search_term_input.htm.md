---
page_id: connect_requests_guided_selection_search_term_input.htm
title: Guided Selection Search Term Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_guided_selection_search_term_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Guided Selection Search Term Input

Input representation of the search terms of a guided selection.

**JSON example**

: 

```
  "searchTerms": [
    {
      "term": "IPhone",
      "tags": [
        "deviceType",
        "mobile"
      ]
    },
    {
      "term": "4GB",
      "tags": [
        "RAM"
      ]
    },
    {
      "term": "64GB",
      "tags": [
        "Storage"
      ]
    }
  ]
```

**Properties**

: 

                
                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                    

                  

                

                
                  
                    
                    

                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                    

                  

                

              
| Name |  | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- | --- |
| `tags` |  | String[] | Search term tags for the guided selection. | Optional | 62.0 |
| `term` |  | String | Search term for the guided selection. | Required | 62.0 |
