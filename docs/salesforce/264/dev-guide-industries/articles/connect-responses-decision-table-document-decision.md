---
page_id: connect-responses-decision-table-document-decision
title: Decision Table Document Decision Output
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-decision-table-document-decision.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Discovery Framework
parent_page: dfdt-apis-responses
legacy_page_id: connect_responses_decision_table_document_decision.htm
fetched_at: 2026-11-25
---

# Decision Table Document Decision Output

Decision Table output.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

| Attribute Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `defaultMaximum​FileSizeAllowed` | Integer | Default maximum file size if `maximumFile​SizeAllowed` is null for a Document Type. | Small, 59.0 | 59.0 |
| `defaultMaximum​FileUploads​Allowed` | Integer | Default maximum file uploads if `maximumFile​UploadsAllowed` is null for a Document Type. | Small, 59.0 | 59.0 |
| `document​CategoryId` | String | ID of the Document Category. | Small, 59.0 | 59.0 |
| `document​CategoryLabel` | String | Master label of the Document Category. | Small, 59.0 | 59.0 |
| `documentTypes` | [Document Types Output](./connect-responses-document-types.md)[] | List of document types and their properties. | Big, 59.0 | 59.0 |
| `helpText` | String | Help text for files in this Document Category. | Small, 59.0 | 59.0 |
| `isRequired` | Boolean | Indicates whether uploading a file in this Document Category is required. If `isRequired` isn’t set, the `isUploadRequired` value is used. If neither `isRequired` nor `isUploadRequired` is set, the default is `false`. | Small, 59.0 | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-decision-table-document-decision.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
