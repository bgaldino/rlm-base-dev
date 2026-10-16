---
page_id: apex_class_commercetax_CustomTaxAttributesResponse.htm
title: CustomTaxAttributesResponse Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_CustomTaxAttributesResponse.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

    

# CustomTaxAttributesResponse Class

    
    
    
Sets additional data or custom attributes in the tax
            response.

        

## Namespace

            
            

[CommerceTax](./apex_namespace_commercetax.htm.md)

        

    

- 
**[CustomTaxAttributesResponse Constructors](./apex_class_commercetax_CustomTaxAttributesResponse.htm.md#apex_commercetax_CustomTaxAttributesResponse_constructors)**  

Learn more about the available constructors with the `CustomTaxAttributesResponse` class.

- 
**[CustomTaxAttributesResponse Methods](./apex_class_commercetax_CustomTaxAttributesResponse.htm.md#apex_commercetax_CustomTaxAttributesResponse_methods)**  

Learn more about the available methods with the `CustomTaxAttributesResponse` class.

  

## CustomTaxAttributesResponse Constructors

  
  
  
Learn more about the available constructors with the `CustomTaxAttributesResponse` class.

    
      

The `CustomTaxAttributesResponse` class includes
        these constructors.

    

    
  

- 
**[CustomTaxAttributesResponse()](./apex_class_commercetax_CustomTaxAttributesResponse.htm.md#apex_commercetax_CustomTaxAttributesResponse_ctor)**  

Constructor to set additional data or custom attributes in the tax       response.

  

### CustomTaxAttributesResponse()

  
  
  
Constructor to set additional data or custom attributes in the tax
      response.

    

#### Signature

      
      

`global CustomTaxAttributesResponse()`

    

  

  

## CustomTaxAttributesResponse Methods

  
  
  
Learn more about the available methods with the `CustomTaxAttributesResponse` class.

    
      

The `CustomTaxAttributesResponse` class includes
        these methods.

    

    
  

- 
**[setData(data)](./apex_class_commercetax_CustomTaxAttributesResponse.htm.md#apex_commercetax_CustomTaxAttributesResponse_setData)**  

Sets additional data or custom attributes in the tax     response.

  

### setData(data)

  
  
  
Sets additional data or custom attributes in the tax
    response.

    

#### Signature

      
      

`global void setData(Map<String, Object>
        data)`

      
    

    

#### Parameters

      
      
        
- 
**data**:

Type: Map<String, Object> Additional data or custom attributes to be included in the tax response.

      

    

    

#### Return Value

      
      

Type: void
