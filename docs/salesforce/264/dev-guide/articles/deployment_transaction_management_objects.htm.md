---
page_id: deployment_transaction_management_objects.htm
title: Transaction Management Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_transaction_management_objects.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Management Deployment
parent_page: deployment_appendix_A.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Transaction Management Objects

This table provides the deployment sequence, object types, and API names for
    Transaction Management objects in Revenue Management.

    

        
        
        
        
        
        
          
            

            

            

            

            

          

        

        
          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

        

      
| Object Use Type | Object Name | Object API | Deployment Sequence | Lookup Fields (Foreign Keys) |
| --- | --- | --- | --- | --- |
| Metadata | App Usage Assignment | AppUsageAssignment | 1 | Order, Quote, Contract, Asset |
| Metadata | Sales Transaction Type | SalesTransactionType | 1 | PricingProcedure |
| Metadata | Quote Template Rich Text Data | QuoteTemplateRichTextData | 1 | None |
| Metadata | Transaction Processing Type | TransactionProcessingType | 1 | None |

  

#### See Also

- [*Revenue Cloud Developer Guide*: Transaction Management Standard
       Objects](./quote_and_order_capture_standard_objects.htm.md)

- [Explore the Revenue Cloud Data Model](https://help.salesforce.com/s/articleView?id=ind.data_model_overview.htm&language=en_US)
