---
page_id: connect_resources_post_draft_credit_memo.htm
title: Post a Draft Memo (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_post_draft_credit_memo.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Post a Draft Memo (POST)

Post a draft credit memo to a credit memo record for review and
      approval.

    
      
        
          

**Resource**

          
: 
            

```
/commerce/invoicing/credit/collection/actions/post
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v65.0/commerce/invoicing/credit/collection/actions/post
```

          

        
        
          

**Available version**

          
: 65.0

        
        
          

**HTTP methods**

          
: POST

        
        
          

**Request body for POST**

          
: 
            

**JSON example**

: 

```
{
"creditMemoIds": ["50gDU00000001MnYAI"]
}
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `correlationId` | String | Splunk correlation ID to use to track messages that are related to the request and logged in Splunk by the different services involved in the request. If not specified, the service creates a random Universally Unique Identifier (UUID). | Optional | 65.0 |
| `creditMemoIds` | String[] | ID of the credit memo record in `Draft` status to be posted. You can post one draft credit memo per API request. | Required | 65.0 |

          

        
        
          

**Response body for POST**

          
: [Credit Memo
              Post](./connect_responses_credit_memo_post_output.htm.md)
