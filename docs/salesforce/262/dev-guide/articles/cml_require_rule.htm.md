---
page_id: cml_require_rule.htm
title: Require Rule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_require_rule.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_constraints.htm
fetched_at: 2026-06-09
---

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

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

When you assign a require rule to a virtual bundle (a bundle related to the
sales transaction, where the parent product has no associated price), set one Product
Selling Model Option on the required product to Default. For more information on Product
Selling Model Options, see Manage Product Selling Model in Revenue Cloud.

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
