---
page_id: cml_require_rule.htm
title: Require Rule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_require_rule.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_constraints.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Require Rule

The require rule requires certain components to be included in a relationship when
    specified conditions are met.

    

Required components can have attributes and quantity specified. The require rule can
        include an optional explanation message, for the rule failure explanation.

In certain
        scenarios, you can independently add a type at the header level. This means you can include
        a specific type even if it isn't explicitly defined as part of any of the relationships
        you've configured. This capability offers flexibility in managing and including
        necessary types that might not always fall under a specific relationship structure.

#### Note

If a require rule auto-adds a product that has one or more Product Selling
        Model Options (PSMOs), set one PSMO on the product to Default. The system uses the default
        PSMO to determine which pricebook entry to use for the auto-added product. For more
        information, see [Manage Product Selling
          Model](https://help.salesforce.com/s/articleView?id=ind.product_catalog_product_selling_model.htm&language=en_US) in Revenue Cloud in Salesforce Help.

The
        require rule has this
        syntax:

```
require(logic expression, relationship[type]{var=value,…,var=value}==integer value, "Explanation message");
```

In
        this example, the require rule specifies that if the number of engineers is more than 0,
        installation is required. The installation will be automatically added upon adding an
        engineer.

```
type GeneratorSet {
    relation engineers : engineer[0..99];
relation installation : install[0..5];
   require(engineers[engineer] > 0, installation[install], "Installation is required if engineers are present");
}
type engineer{}
type install{}

```
