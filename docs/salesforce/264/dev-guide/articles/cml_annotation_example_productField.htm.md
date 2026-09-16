---
page_id: cml_annotation_example_productField.htm
title: productField Annotation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_annotation_example_productField.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_annotation_examples.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# productField Annotation

productField is a CML annotation that defines the Product2 field on a variable.
  productField loads the value from Product Catalog Management (PCM) during constraint model
  activation.

  
   

     
     
     
      
       

       

      

     

     
      
       

       

      

      
       

       

      

      
       

       

      

     

    
| Annotation | `productfield` |
| --- | --- |
| Applicable to | Variable |
| Value Type/Values | Literal (case sensitive) |
| Description | Used to load the value from the corresponding Product2 field defined in Product Catalog Management(PCM). Defined under either a type or supertype. If defined under a supertype, the types, which inherit from the supertype, load the Product2 field value for the corresponding product. Supports a maximum of 50 Product2 fields. Loads product field values for a maximum of 20,000 products. Read-only. Doesn't support a null value. |

  

  

## Example 1

In this example, `RatedPowerOutput__c` is a custom field defined on the Product2 object. The constraint
    rules engine loads the value of `RatedPowerOutput__c` for the
    GeneratorSet product during constraint model
    activation.

```
type GeneratorSet {
    @(productField = "RatedPowerOutput__c")
    int ratedPowerOutput;
}
```

  

## Example 2

In this example, the product field variable `productName` is defined under a supertype `EquipmentItem`. Any type that inherits the supertype loads the
    value of `Name` for the corresponding product during
    constraint model
    activation.

```
type EquipmentItem {
    @(productField = "Name")
    string productName;
}

type GeneratorSet : EquipmentItem;
type GeneralModel : EquipmentItem;
```

  

## Example 3

In this example, the product field variable `productCode` is defined under the parent type `GeneratorSet`. `GeneralModel`
    is a child of `GeneratorSet`, and it can access the `productCode` variable from its parent by using the `parent()`
    function.

```
type GeneratorSet {
    @(productField = "ProductCode")
    string productCode;

    relation generalModels : GeneralModel[1..999999];
}

type GeneralModel {
    string parentProductCode = parent(productCode);
}
```
