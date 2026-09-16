---
page_id: apex_enum_commercetax_CalculateTaxType.htm
title: CalculateTaxType Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_commercetax_CalculateTaxType.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# CalculateTaxType Enum

Shows whether a tax calculation request is for estimated or actual
      tax.

    

## Usage

      
      

Used by the [CalculateTaxRequest](./apex_class_commercetax_CalculateTaxRequest.htm.md#apex_class_commercetax_CalculateTaxRequest) and [CalculateTaxResponse](./apex_class_commercetax_CalculateTaxResponse.htm.md#apex_class_commercetax_CalculateTaxResponse) class methods.

    

    

## Enum Values

      
      

The `commercetax.CalculateTaxType` enum includes these
        values.

      

          
          
          
            
              

              

            

          

          
            
              

              

            

            
              

              

            

          

        
| Value | Description |
| --- | --- |
| `Actual` | Specifies that the tax calculation service should calculate the finalized (actual) tax for the requested line items. |
| `Estimated` | Specifies that the tax calculation service should estimate the tax for the requested line items. |
