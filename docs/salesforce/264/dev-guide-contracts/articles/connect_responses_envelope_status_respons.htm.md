---
page_id: connect_responses_envelope_status_respons.htm
title: Envelope Status
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_envelope_status_respons.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# Envelope Status

Output representation of the envelope status record.

              

              

              

              

              

            

              

              

              

              

              

            

              

              

              

              

              

            

              

              

              

              

              

            

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `envelopeId` | String | The ID of the envelope for which the e-signature status is updated. | Small, 56.0 | 56.0 |
| `error` | String | Error code corresponding to the envelope ID. | Small, 56.0 | 56.0 |
| `errorMessage` | String | Error message corresponding to the envelope ID. | Small, 56.0 | 56.0 |
| `status` | String | Updated envelope status. | Small, 56.0 | 56.0 |
| `success` | Boolean | Indicates whether the envelope is successfully updated (`true`) or not (`false`). | Small, 56.0 | 56.0 |
