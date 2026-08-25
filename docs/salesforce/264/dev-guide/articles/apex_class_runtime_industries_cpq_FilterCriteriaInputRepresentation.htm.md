---
page_id: apex_class_runtime_industries_cpq_FilterCriteriaInputRepresentation.htm
title: FilterCriteriaInputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_FilterCriteriaInputRepresentation.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# FilterCriteriaInputRepresentation Class

Contains properties to store criteria details to filter records based on supported
    properties.

## Namespace

[runtime_industries_cpq](./apex_namespace_runtime_industries_cpq.htm.md)

- 
**[FilterCriteriaInputRepresentation Properties](./apex_class_runtime_industries_cpq_FilterCriteriaInputRepresentation.htm.md#apex_runtime_industries_cpq_FilterCriteriaInputRepresentation_properties)**  

Learn more about the properties available with the FilterCriteriaInputRepresentation     class.

  

## FilterCriteriaInputRepresentation Properties

  
  
  
Learn more about the properties available with the FilterCriteriaInputRepresentation
    class.

    
      

The `FilterCriteriaInputRepresentation` class includes
        these properties.

    

    
  

- 
**[attributeType](./apex_class_runtime_industries_cpq_FilterCriteriaInputRepresentation.htm.md#apex_runtime_industries_cpq_FilterCriteriaInputRepresentation_attributeType)**  

Get details of the search attribute type of the facet for a faceted search.

- 
**[operator](./apex_class_runtime_industries_cpq_FilterCriteriaInputRepresentation.htm.md#apex_runtime_industries_cpq_FilterCriteriaInputRepresentation_operator)**  

Get the operator that's used for the filter criteria.

- 
**[property](./apex_class_runtime_industries_cpq_FilterCriteriaInputRepresentation.htm.md#apex_runtime_industries_cpq_FilterCriteriaInputRepresentation_property)**  

Get the property name to use in the filter, which must be the same as the object field.     The supported property is name.

- 
**[value](./apex_class_runtime_industries_cpq_FilterCriteriaInputRepresentation.htm.md#apex_runtime_industries_cpq_FilterCriteriaInputRepresentation_value)**  

Get the value for the filter criteria.

### attributeType

Get details of the search attribute type of the facet for a faceted search.

#### Signature

`public String attributeType {get; set;}`

#### Property Value

Type: String

    

#### Usage

      
      

Valid values are:

      
                        
- `ProductStandard`

                        
- `ProductCustom`

                        
- `ProductDynamicAttribute`

                        
- `ProductAttributeStandard`

                        
- `ProductAttributeCustom`

                      

    

### operator

Get the operator that's used for the filter criteria.

#### Signature

`public String operator {get; set;}`

#### Property Value

Type: String

    

#### Usage

      
      

The supported operators are:

      
                        
- `eq`

                        
- `in`

                        
- `contains`

                        
- 
`gt`—Specifies a greater than
                          criteria. Available from API version 63.0 and later for Number, Date, and
                          Datetime data types only.

                        
- 
`lt`—Specifies a less than
                          criteria. Available from API version 63.0 and later for Number, Date, and
                          Datetime data types only.

                        
- 
`gte`—Specifies a greater than
                          or equal to criteria. Available from API version 63.0 and later for
                          Number, Date, and Datetime data types only.

                        
- 
`lte`—Specifies a less than or
                          equal to criteria. Available from API version 63.0 and later for Number,
                          Date, and Datetime data types only.

                      

    

### property

Get the property name to use in the filter, which must be the same as the object field.
    The supported property is name.

#### Signature

`public String property {get; set;}`

#### Property Value

Type: String

### value

Get the value for the filter criteria.

#### Signature

`public String value {get; set;}`

#### Property Value

Type: String
