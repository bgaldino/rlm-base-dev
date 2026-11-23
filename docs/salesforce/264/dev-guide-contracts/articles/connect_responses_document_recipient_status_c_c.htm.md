---
page_id: connect_responses_document_recipient_status_c_c.htm
title: Document Recipient Status
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_document_recipient_status_c_c.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-11-23
---

# Document Recipient Status

Output representation of recipient status and sequence information for the
signers.

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contract​Document​VersionId` | String | Record ID of the contract document version. | Small, 61.0 | 61.0 |
| `hasCurrent​UserSigned` | Boolean | Indicates whether the current user has signed the document (`true`) or not (`false`). The default value is `false`. | Small, 61.0 | 61.0 |
| `isCurrent​UserRecipient` | Boolean | Indicates whether the current user is also a signer (`true`) or not (`false`). The default value is `false`. | Small, 61.0 | 61.0 |
| `preceding​SignersExists` | Boolean | Indicates whether the document is signed by preceding signers (`true`) or not (`false`). The default value is `false`. | Small, 61.0 | 61.0 |
| `preceding​SignersSigned` | Boolean | Indicates whether all preceding signers have completed their signatures (`true`) or not (`false`). The default value is `false`. | Small, 61.0 | 61.0 |
| `recipient​Sequence` | Integer | Sequence number of the current user. | Small, 61.0 | 61.0 |
| `recipients` | [Recipients Response[]](./connect_responses_recipient_output.htm.md "Output representation of a recipient’s personal and status information in a contract document’s signing process.") | List of all the signers involved in the contract document. | Big, 61.0 | 61.0 |

## Sample Response

```
{
  "isCurrentUserRecipient": "true",
  "hasCurrentUserSigned": "true",
  "recipientSequence": "4",
  "preceddingSignersExists": "true",
  "preceedingSignersSigned": "true",
  "Recipients": [
    {
      "Name": "Rishyv Misrep",
      "email": "rishyv@salesforce.com",
      "status": "Signed",
      "finalStatusDateTime": ""
    }
  ]
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_document_recipient_status_c_c.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
