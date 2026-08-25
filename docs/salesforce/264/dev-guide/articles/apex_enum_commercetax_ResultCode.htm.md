---
page_id: apex_enum_commercetax_ResultCode.htm
title: ResultCode Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_commercetax_ResultCode.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ResultCode Enum

Code that represents the results of a tax request made to the tax
      engine.

    

## Usage

      
      

Used by the [ErrorResponse](./apex_class_commercetax_ErrorResponse.htm.md#apex_class_commercetax_ErrorResponse)
        class method.

    

    

## Enum Values

      
      

The `commercetax.ResultCode` enum includes these
        values.

      

          
          
          
            
              

              

            

          

          
            
              

              

            

            
              

              

            

          

        
| Value | Description |
| --- | --- |
| `TaxEngineError` | Represents an error that occurred during the tax request process. |
| `ReferenceDocumentCodeMissing` | Specifies if the document mentioned as a `referenceDocumentCode` value isn't available in the tax engine. |
