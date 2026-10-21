---
page_id: connect_resources_esign_envelope_status.htm
title: E-signature Envelope Status
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_esign_envelope_status.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_docgen_resources.htm
fetched_at: 2026-10-13
---

# E-signature Envelope Status

Update e-signature envelope status.

    

## Resource

      
      

```
/connect/e-sign/signature-requests/$SOURCE_OBJECT_ID/envelopes/status
```

    

    

## Available Version

      
      

56.0

    

    

## HTTP Methods

      
      

PATCH

    

    

## Example

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v56.0/connect/e-sign/signature-requests/{sourceObjectId}/envelopes/status
```

    

    

## Response Body for PATCH

      
      

[Envelope Status List Response](./connect_responses_envelope_status_list_respons.htm.md)
