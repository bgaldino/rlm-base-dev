---
page_id: connect_responses_external_document_review_c_c.htm
title: External Document Review CC
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_external_document_review_c_c.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# External Document Review CC

Output representation for external document version review.

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `content​VersionId` | String | Record ID of content version associated with an external document. | Small, 61.0 | 61.0 |
| `contract​Document​VersionId` | String | Record ID of the contract document version. | Small, 61.0 | 61.0 |
| `external​DocumentId` | String | Record ID of the external document. | Small, 61.0 | 61.0 |
| `isReview​Completed​ByCurrentUser` | Boolean | Indicates whether the current user has completed the review for the document (`true`) or not (`false`). | Small, 61.0 | 61.0 |
| `url` | String | URL of the external document. | Big, 61.0 | 61.0 |

    

    

## Sample Response

      
      

```
{
  "contentVersionId": "11RSB0000008rQX2AY",
  "externalDocumentId": "11nSB000001as69YAA",
  "contractDocumentVersionId": "a3k5g000000QyRSAA0",
  "url": "https://www.salesforce.com",
  "isReviewCompletedByCurrentUser": "true"
}
```
