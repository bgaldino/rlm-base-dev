---
page_id: apex_enum_commercetax_TaxTransactionStatus.htm
title: TaxTransactionStatus Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_commercetax_TaxTransactionStatus.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# TaxTransactionStatus Enum

Shows whether the tax transaction has been committed or
      uncommitted.

    

## Usage

      
      

Used by the [CalculateTaxResponse](./apex_class_commercetax_CalculateTaxResponse.htm.md#apex_class_commercetax_CalculateTaxResponse) class method.

    

    

## Enum Values

      
      

The `commercetax.TaxTransactionStatus` enum includes
        these values.

      

          
          
          
            
              

              

            

          

          
            
              

              

            

            
              

              

            

          

        
| Value | Description |
| --- | --- |
| `Committed` | Tax has been calculated and committed. |
| `Uncommitted` | Tax has been calculated but hasn't been committed. |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_commercetax_TaxTransactionStatus.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
