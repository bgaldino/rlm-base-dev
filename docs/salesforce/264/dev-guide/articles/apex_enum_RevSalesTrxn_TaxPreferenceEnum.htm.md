---
page_id: apex_enum_RevSalesTrxn_TaxPreferenceEnum.htm
title: TaxPreferenceEnum Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_RevSalesTrxn_TaxPreferenceEnum.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_RevSalesTrxn.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# TaxPreferenceEnum Enum

Specifies whether to execute or skip the tax calculation step for each sales
    transaction record. Available in API version 65.0 and later.

    

## Enum Values

      
      

The `RevSalesTrxn.TaxPreferenceEnum` enum includes this
        value.

      

          
          
          
            
              

              

            

          

          
            
              

              

            

          

        
| Value | Description |
| --- | --- |
| `Skip` | Specifies to skip tax calculation request for each sales transaction record. If this value isn't specified, then tax calculation request is performed by default. |
