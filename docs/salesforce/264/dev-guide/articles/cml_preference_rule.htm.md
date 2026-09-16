---
page_id: cml_preference_rule.htm
title: Preference Rule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_preference_rule.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_constraints.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Preference Rule

The preference rule encourages the constraint solver to satisfy the condition, but
    doesn't enforce it if the condition can't be met.

    

The system tries to satisfy the condition in a preference rule, but if for some
        reason it can't, the system delivers a failure message to the user with `Info` severity.

      

#### Note

If a preference rule auto-adds a product that has one or more Product
        Selling Model Options (PSMOs), set one PSMO on the product to Default. The system uses the
        default PSMO to determine which pricebook entry to use for the auto-added product. For more
        information, see [Manage Product Selling
          Model](https://help.salesforce.com/s/articleView?id=ind.product_catalog_product_selling_model.htm&language=en_US) in Revenue Cloud in Salesforce Help.

The preference rule has this
        syntax.

```
preference(logic expression, string literal | string variable, argument, .., argument);
preference(logic expression, string literal | string variable);
preference(logic expression);

```

      

A preference rule can include an optional explanation message for failure. The message is of
          `Info` severity, meaning it does not block the user
        from continuing with the action.

In this example, the preference rule encourages the user
        to mention the `dBMax` value as `90` and the `requiredKW`
        value as `500`.

```
type GeneratorSet {
   int requiredKW = [101..10000];
   int dBMax = [0..140];
   preference(dBMax == 90, "90 preferred for dbMax");
   preference(requiredKW == 500,"50 preferred for requiredKW");
}
```
