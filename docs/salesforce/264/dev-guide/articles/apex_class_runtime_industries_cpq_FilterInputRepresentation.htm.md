---
page_id: apex_class_runtime_industries_cpq_FilterInputRepresentation.htm
title: FilterInputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_FilterInputRepresentation.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# FilterInputRepresentation Class

Contains the filter property to filters records based on supported criteria.

## Namespace

[runtime_industries_cpq](./apex_namespace_runtime_industries_cpq.htm.md)

- 
**[FilterInputRepresentation Properties](./apex_class_runtime_industries_cpq_FilterInputRepresentation.htm.md#apex_runtime_industries_cpq_FilterInputRepresentation_properties)**  

Learn more about the available properties with the FilterInputRepresentation     class.

  

## FilterInputRepresentation Properties

  
  
  
Learn more about the available properties with the FilterInputRepresentation
    class.

    
      

The `FilterInputRepresentation` class includes these
        properties.

    

    
  

- 
**[filter](./apex_class_runtime_industries_cpq_FilterInputRepresentation.htm.md#apex_runtime_industries_cpq_FilterInputRepresentation_filter)**  

Filters records based on supported criteria. The supported property is name.

### filter

Filters records based on supported criteria. The supported property is name.

#### Signature

`public runtime_industries_cpq.Filter filter {get; set;}`

#### Property Value

Type: [runtime_industries_cpq.Filter](./apex_class_runtime_industries_cpq_Filter.htm.md#apex_class_runtime_industries_cpq_Filter)

    

#### Usage

      
      

The supported operators are:

      
                        
- `eq`

                        
- `in`

                        
- 
`contains`—This value isn't
                          applicable if the **Use Indexed Data For Product Listing and
                            Search** toggle from the Product Discovery Settings page from
                          Setup is enabled.

                      

      

If multiple criteria are specified, then the resultant criteria are combined by using the
          `and` operator.
