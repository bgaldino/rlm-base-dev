---
page_id: cml_best_practice_attribute_name.htm
title: "Configurator API: Include the Attribute Developer Name When Creating or Updating Attributes"
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_best_practice_attribute_name.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_cml_best_practices.htm
fetched_at: 2026-09-29
---

# Configurator API: Include the Attribute Developer Name When Creating or Updating
    Attributes

When a constraint model is active, include the attribute developer name in Product
    Configurator API requests that create or update a product attribute.

    

When a constraint model is active, Product Configurator API requests that create or update
      a product attribute must include `AttributeName` in the
      payload. Set `AttributeName` to the attribute’s developer
      name. The constraint engine matches that value to the attribute name defined in the CML
      model, which is the CML variable name.

    

When you import a product attribute from Product Catalog Management (PCM) into CML, the
      variable name is the attribute’s developer name. For the engine to apply the value in the
      request, `AttributeName` must match that CML variable
      name. `AttributeKey` doesn’t replace `AttributeName`.

    

When the payload includes a matching `AttributeName`,
      the engine uses the submitted attribute value. When the payload omits `AttributeName`, the engine can’t match the input to a CML
      variable and applies the default attribute value defined in CML.

    

This `addedNodes` payload creates an order item
      attribute without `AttributeName`. The engine applies the
      CML default for that attribute instead of `"true"`.

    

```
{
    "path": [
        "801WI00001Q5fN0YAJ",
        "ref_Assoc1Line",
        "ref_Assoc1LineAttrAssoc"
    ],
    "addedObject": {
        "id": "ref_Assoc1LineAttrAssoc",
        "SalesTransactionItemAttrParent": "ref_Assoc1Line",
        "ParentReference": "ref_Assoc1Line",
        "AttributeKey": "0tjWI0000000I6cYAE",
        "AttributeValue": "true",
        "businessObjectType": "OrderItemAttribute"
    }
}
```

    

This payload includes `AttributeName` set to `Associate`, which matches the CML variable. The engine applies
        `"true"`.

    

```
{
    "path": [
        "801WI00001Q5fN0YAJ",
        "ref_Assoc1RV",
        "ref_Assoc1RVAssocAttr"
    ],
    "addedObject": {
        "id": "ref_Assoc1RVAssocAttr",
        "AttributeName": "Associate",
        "SalesTransactionItemAttrParent": "ref_Assoc1RV",
        "ParentReference": "ref_Assoc1RV",
        "AttributeKey": "0tjWI0000000I6cYAE",
        "AttributeValue": "true",
        "businessObjectType": "OrderItemAttribute"
    }
}
```

    

For a picklist attribute, include `AttributeName` with
      the same developer-name match, plus `AttributeValue` and
        `AttributePicklistValue`.

    

```
{
    "path": [
        "801WI00001Q5fN0YAJ",
        "ref_Assoc1RV",
        "ref_Assoc1RVLengthAttr"
    ],
    "addedObject": {
        "id": "ref_Assoc1RVLengthAttr",
        "AttributeName": "RV_Trailer",
        "SalesTransactionItemAttrParent": "ref_Assoc1RV",
        "ParentReference": "ref_Assoc1RV",
        "AttributeKey": "0tjWI0000000I6bYAE",
        "AttributeValue": "Upto 33 Ft and longer",
        "AttributePicklistValue": "0v6WI0000000DuxYAE",
        "businessObjectType": "OrderItemAttribute"
    }
}
```

    

Include `AttributeName` the same way in `updatedNodes` when you update an existing attribute. On a
      quote, use `businessObjectType` `QuoteLineItemAttribute` and the same `AttributeName` requirement.

    

For how the engine chooses a default when no matching payload value is present, see
        [defaultValue Annotation](./cml_annotation_example_defaultValue.htm.md).
