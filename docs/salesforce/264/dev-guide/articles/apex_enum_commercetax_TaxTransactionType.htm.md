---
page_id: apex_enum_commercetax_TaxTransactionType.htm
title: TaxTransactionType Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_commercetax_TaxTransactionType.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# TaxTransactionType Enum

Shows whether the tax transaction is for a credit or debit
      transaction.

    

## Usage

      
      

Used by the [CalculateTaxResponse](./apex_class_commercetax_CalculateTaxResponse.htm.md#apex_class_commercetax_CalculateTaxResponse) and [CalculateTaxRequest](./apex_class_commercetax_CalculateTaxRequest.htm.md#apex_class_commercetax_CalculateTaxRequest) class
        methods.

    

    

## Enum Values

      
      

The `commercetax.TaxTransactionType` enum includes
        these values.

      

          
          
          
            
              

              

            

          

          
            
              

              

            

            
              

              

            

            
              

              

            

          

        
| Value | Description |
| --- | --- |
| `Credit` | Represents a credit transaction. |
| `Debit` | Represents a debit transaction. |
| `Void` | Specifies that the tax engine has voided the document that's mentioned in the `referenceDocumentCode` property value. |
