---
page_id: connect_responses_decision_table_document_decision.htm
title: Decision Table Document Decision Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_table_document_decision.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Discovery Framework
parent_page: dfdt_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Table Document Decision Output

Decision Table output.

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
| `documentTypes` | [Document Types Output](./connect_responses_document_types.htm.md)[] | List of document types and their properties. | Big, 59.0 | 59.0 |
| `helpText` | String | Help text for files in this Document Category. | Small, 59.0 | 59.0 |
| `isRequired` | Boolean | Indicates whether uploading a file in this Document Category is required. If `isRequired` isn't set, the `isUploadRequired` value is used. If neither `isRequired` nor `isUploadRequired` is set, the default is `false`. | Small, 59.0 | 59.0 |
