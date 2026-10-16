---
page_id: connect_resources_lock_doc_version.htm
title: Lock Document Version
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_lock_doc_version.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_clm_resources.htm
fetched_at: 2026-10-13
---

# Lock Document Version

Lock an active contract document version for
    modification.

    

## Resource

      
      

```
/connect/clm/contract-document-version/$CONTRACT_DOCUMENT_VERSION_ID/lock
```

    

    

## Available Version

      
      

56.0

    

    

## HTTP Methods

      
      

PATCH

    

    

## Example for PATCH

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v56.0/connect/clm/contract-document-version/${contractversionid}/lock
```

    

    

## Response Body for PATCH

      
      

[Generic Output Representation](./connect_responses_generic_output.htm.md)
