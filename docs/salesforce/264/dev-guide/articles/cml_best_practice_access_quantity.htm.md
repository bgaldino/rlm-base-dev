---
page_id: cml_best_practice_access_quantity.htm
title: "Access Quantity in CML: Cardinality and Attribute Constraints"
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_best_practice_access_quantity.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_cml_best_practices.htm
fetched_at: 2026-09-29
---

# Access Quantity in CML: Cardinality and Attribute Constraints

There are two ways to access quantity in CML. Use cardinality constraints and attribute
    constraints correctly for best performance.

    

There are two ways to access quantity in CML:

    

A cardinality constraint creates or validates the presence of components. The constraint
      engine adds or removes instances to satisfy the conditions of the constraint.

    

An attribute constraint, such as lineItemQuantity or ItemEndQuantity, only reads or
      validates. The constraint engine validates the expression, but doesn't configure to satisfy
      the conditions of the constraint

    

For best performance, follow these guidelines:

    
      
- Use a cardinality constraint whenever possible. Use `lineItemQuantity` or `ItemEndQuantity` only
        when a cardinality constraint can't meet the business need.

      
- Treat `lineItemQuantity` and `ItemEndQuantity` as read-only. Use only in calculation or
        evaluation rules.

      
- Keep scope in mind. When a product can have multiple instances, read `lineItemQuantity` or `ItemEndQuantity` per instance. Avoid reading the attribute at a parent or
        aggregate scope where it can be unbound or ambiguous.

      
- Don't use `lineItemQuantity` or `ItemEndQuantity` to create components. Drive component
        creation by cardinality, not by attribute references.

    

    

Use constraint patterns similar to these examples. Do this.

    

```
constraint(mouse[Mouse] == warranty[Warranty])
```

    

Avoid this.

    

```
constraint(mouse[Mouse].lineItemQuantity == warranty[Warranty].lineItemQuantity)
```

    

Do this.

    

```
constraint(mouse[Mouse] == 3)
```

    

Avoid this.

    

```
constraint(mouse[Mouse].lineItemQuantity == 3)
```
