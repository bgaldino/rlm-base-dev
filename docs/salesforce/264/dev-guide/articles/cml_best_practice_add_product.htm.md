---
page_id: cml_best_practice_add_product.htm
title: "Automatically Add a Product: Define as a Separate Constraint"
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_best_practice_add_product.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_cml_best_practices.htm
fetched_at: 2026-09-29
---

# Automatically Add a Product: Define as a Separate Constraint

To automatically add a product and also set attributes on the product, define these
    procedures as separate constraints.

    

If you need to automatically add a product, and also set attributes on the product, define
      these procedures as separate constraints, as in this example.

    

```
constraint(laptop[Laptop] > 0, warranty[Warranty] > 0);
constraint(warranty[Warranty] > 0, warranty[Warranty].type == “Premium”);
```

    

Avoid this example, which automatically adds a product and sets attributes on the product,
      in the same constraint.

    

```
constraint(laptop[Laptop] > 0, warranty[Warranty] > 0 && warranty[Warranty].type == "Premium");
```
