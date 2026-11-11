---
page_id: connect_resources_clm_resources.htm
title: CLM Resources
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_clm_resources.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_resources.htm
fetched_at: 2026-10-13
---

# CLM Resources

Manage Salesforce Contracts CLM resources. Check in and check out a contract document.
      Get and delete content document details. Execute actions for a contract based on the status.
      Update and create contracts. Get and create contract document versions. Get the status of
      document generation process. Get the list of configured templates for a usage type. Get a list
      of actions possible for a particular contract. Lock and unlock an active contract document
      version. Change a template in a contract document version. 

      
         

Available resources are:

         

               
               
               
                  
                     

                     

                  

               

               
                  
                     

                     

                  

                  
                     

                     

                  

                  
                     

                     

                  

                  
                     

                     

                  

                  
                     

                     

                  

                  
                     

                     

                  

                  
                     

                     

                  

                  
                     

                     

                  

                  
                     

                     

                  

                  
                     

                     

                  

                  
                     

                     

                  

                  
                     

                     

                  

               

            
| Resource | Description |
| --- | --- |
| [`/connect/clm/contract-document-version/$CONTRACT_DOCUMENT_VERSION_ID/​checkIn`](./connect_resources_checkin_doc_version.htm.md) | Check in a contract document version using contract document version ID. |
| [`/connect/clm/contract-document-version/$CONTRACT_DOCUMENT_VERSION_ID/​checkout`](./connect_resources_checkout_doc_version.htm.md) | Check out a contract document version for modification. |
| [`/connect/clm/contract-document-version/$CONTRACT_DOCUMENT_VERSION_ID/​content-documents`](./connect_resources_content_document_details.htm.md) | Get content document details associated with a contract document version. |
| [`/connect/clm/contract/$CONTRACT_ID`](./connect_resources_contract_actions.htm.md) | Execute possible actions for a contract based on the status. Actions can trigger work flows and change the status for a contract. |
| [`/connect/clm/contract`](./connect_resources_contracts.htm.md) | Update and create contracts using the object ID. |
| [`/connect/clm/contract/$CONTRACT_ID/​contract-document-version`](./connect_resources_details_doc_version.htm.md) | Get and create contract document versions. |
| [`/connect/clm/document-generation-process/status`](./connect_resources_doc_generation_process.htm.md) | Get the status of document generation process for a given contract document version ID. |
| [`/connect/clm/document-template`](./connect_resources_doc_template.htm.md) | Get the list of configured templates for a usage type. |
| [`/connect/clm/contract/$CONTRACT_ID/contract-actions`](./connect_resources_list_of_contract_actions.htm.md) | Get the list of actions possible for a particular contract. |
| [`/connect/clm/contract-document-version/$CONTRACT_DOCUMENT_VERSION_ID/​lock`](./connect_resources_lock_doc_version.htm.md) | Lock an active contract document version for modification. |
| [`/connect/clm/contract-document-version/$CONTRACT_DOCUMENT_VERSION_ID/​unlock`](./connect_resources_unlock_doc_version.htm.md) | Unlock latest contract document version. |
| [`/connect/clm/contract-document-version/$CONTRACT_DOCUMENT_VERSION_ID`](./connect_resources_template_doc_version.htm.md) | Change the template in a contract document version. |

      

   

- 
**[Check In Contract Document Version](./connect_resources_checkin_doc_version.htm.md)**  

Check in a contract document version using contract document version       ID.

- 
**[Check Out Contract Document Version](./connect_resources_checkout_doc_version.htm.md)**  

Check out a contract document version for modification.

- 
**[Content Document Details (GET, DELETE, PATCH)](./connect_resources_content_document_details.htm.md)**  

Get content document details associated with a contract document       version.     Delete content document details associated with a contract document       version.     Update the content document details associated with a contract document       version.

- 
**[Contracts (PATCH, POST)](./connect_resources_contracts.htm.md)**  

Update and create contracts using the object ID.

- 
**[Contract Actions](./connect_resources_contract_actions.htm.md)**  

Execute possible actions for a contract based on the status. Actions can trigger work flows and change the status for a contract.

- 
**[Contract Document Risk Analysis](./connect_resources_contract_risk_analysis.htm.md)**  

Start an asynchronous risk analysis for a contract document version,     or get the status and results of the most recent risk analysis run.

- 
**[Contract Document Version Template](./connect_resources_template_doc_version.htm.md)**  

Change the template in a contract document version.

- 
**[Details of Contract Document Versions](./connect_resources_details_doc_version.htm.md)**  

Get and create contract document versions.

- 
**[Document Generation Process](./connect_resources_doc_generation_process.htm.md)**  

Get the status of document generation process for a given contract       document version ID. 

- 
**[Document Template](./connect_resources_doc_template.htm.md)**  

Get the list of configured templates for a usage     type.

- 
**[List of Contract Actions](./connect_resources_list_of_contract_actions.htm.md)**  

 Get the list of actions possible for a particular     contract.

- 
**[Lock Document Version](./connect_resources_lock_doc_version.htm.md)**  

Lock an active contract document version for     modification.

- 
**[Unlock Document Version](./connect_resources_unlock_doc_version.htm.md)**  

Unlock latest contract document version.
