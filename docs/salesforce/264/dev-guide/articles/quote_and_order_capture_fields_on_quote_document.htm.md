---
page_id: quote_and_order_capture_fields_on_quote_document.htm
title: Transaction Management Fields on Quote Document
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/quote_and_order_capture_fields_on_quote_document.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_fields_on_standard_objects.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Transaction Management Fields on Quote Document

      Standard and custom fields extend the standard Quote Document object for use
         in Transaction Management to represent information about quote documents. This object
      is available in API version 61.0 and later.

      

## Special Access Rules

         
         

To view these fields, you must have the Revenue Cloud Advanced license. See [Quote Document](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_quotedocument.htm) for fields on the Salesforce
            platform object.

      

      

## Fields

         
         

               
               
               
                  
                     

                     

                  

               

               
                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 
- 
- 
- 
- 
- 
- 

: 

                  

               

            
| Field | Details |
| --- | --- |
| Document Template | **Type** String **Properties** Create, Filter, Group, Nillable, Sort **Description** The template ID used for generating the quote document. |
| Status | **Type** Picklist **Properties** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** The status of the quote document. Possible values are: `Completed` `Failed` `Generating` `In Progress` `None` `Queued` The default value is `None`. |
