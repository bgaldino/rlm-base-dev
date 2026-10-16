---
page_id: connect_resources_customer_community_user.htm
title: Customer Community Resources
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_customer_community_user.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_resources.htm
fetched_at: 2026-10-13
---

# Customer Community Resources

Manage document control for Customer Community (CC) users by using
      Salesforce's
      Contract Lifecycle Management (CLM). Using CLM, CC users can securely access the most recent
      contract document versions. Use the Contract Document Version resource to streamline document
      sharing for external reviews and digital signing, ensuring access is granted only for the
      latest and relevant contract versions in compliance with the user's account and contract
      status.

      
         

Available
            resources are:

         

               
               
               
                  
                     

                     

                  

               

               
                  
                     

                     

                  

                  
                     

                     

                  

               

            
| Resource | Description |
| --- | --- |
| [`/connect/clm/cc/contract/${contractId}/contract-document-version` (GET)](./connect_resources_cc_user_contract_doc_version.htm.md) | Get latest details of a contract document version based on a contract ID. |
| [`/connect/clm/cc/documentRecipient?contractDocumentVersion=${contractDocumentVersionId}` (GET)](./connect_resources_document_recipient.htm.md) | Fetch recipient status for contract document versions to monitor e-signature progress and identify decline reasons. |

      

   

- 
**[Contract Document Version for Customer Community User (GET)](./connect_resources_cc_user_contract_doc_version.htm.md)**  

Get latest details of a contract document version based on a       contract ID.

- 
**[Document Recipient (GET)](./connect_resources_document_recipient.htm.md)**  

Fetch recipient status for contract document       versions to monitor e-signature progress and identify decline reasons.
