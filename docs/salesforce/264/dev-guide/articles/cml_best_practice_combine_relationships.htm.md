---
page_id: cml_best_practice_combine_relationships.htm
title: "Relationships: Combine Relationships to Reduce Performance Impact"
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_best_practice_combine_relationships.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_cml_best_practices.htm
fetched_at: 2026-09-29
---

# Relationships: Combine Relationships to Reduce Performance Impact

Creating multiple relationships on a type can impact performance. When possible, combine
    relationships to improve performance.

    

Creating multiple relationships on a type can impact performance. When possible, combine
      relationships to improve performance.

    

When possible, avoid this example, which includes separate relationships for Mouse and
      Keyboard, two accessories in a product bundle:

    

```
relation mouse : Mouse;
relation keyboard : Keyboard;
```

    

Follow this example, which uses one relationship for Accessories, which can include Mouse,
      Keyboard, and other accessories.

    

```
relation accessories : Accessories;
```
