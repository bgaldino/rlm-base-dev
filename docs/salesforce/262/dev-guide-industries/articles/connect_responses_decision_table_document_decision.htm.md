---
page_id: connect_responses_decision_table_document_decision.htm
title: Decision Table Document Decision Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_table_document_decision.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: dfdt_apis_responses.htm
fetched_at: 2026-06-25
---

# Decision Table Document Decision Output

Decision Table output.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=industries_reference)

#### Important

Where possible, we changed noninclusive terms
to align with our company value of Equality. We maintained certain terms to avoid any effect
on customer implementations.

| Attribute Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `defaultMaximum​FileSizeAllowed` | Integer | Default maximum file size if `maximumFile​SizeAllowed` is null for a Document Type. | Small, 59.0 | 59.0 |
| `defaultMaximum​FileUploads​Allowed` | Integer | Default maximum file uploads if `maximumFile​UploadsAllowed` is null for a Document Type. | Small, 59.0 | 59.0 |
| `document​CategoryId` | String | ID of the Document Category. | Small, 59.0 | 59.0 |
| `document​CategoryLabel` | String | Master label of the Document Category. | Small, 59.0 | 59.0 |
| `documentTypes` | [Document Types Output](./connect_responses_document_types.htm.md "Output representation of the Document Type.")[] | List of document types and their properties. | Big, 59.0 | 59.0 |
| `helpText` | String | Help text for files in this Document Category. | Small, 59.0 | 59.0 |
| `isRequired` | Boolean | Indicates whether uploading a file in this Document Category is required. If `isRequired` isn't set, the `isUploadRequired` value is used. If neither `isRequired` nor `isUploadRequired` is set, the default is `false`. | Small, 59.0 | 59.0 |
