---
article_id: ind.product_configurator_use_the_visual_builder.htm
title: Define Constraints and Rules with the Visual Builder
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_use_the_visual_builder.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Define Constraints and Rules with the Visual Builder

In the Constraint Builder, use point-and-click tools in the Visual Builder to define the constraints and rules for a constraint model. Add constraints and rules to easily configure products or product bundles.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
USER PERMISSIONS NEEDED
To create a constraint model:	Product Configuration Constraints Designer permission set

Complete the steps for Constraint Rules Engine setup before you work with constraint models. See Set Up Configurator With Constraint Rules Engine.

When you import a bundle with the Visual Builder, product classes are imported, but the class attributes aren't imported. You can add attributes manually in the CML Editor. For more information on working in the CML Editor, see Use Code to Define Constraints and Rules in the CML Editor.

Create a constraint model.
In the Constraint Models app, select the constraint model you want to modify.
On the Details page, select the version name of the constraint model.
To add a new item, click Add Item, select Product, and then click Next.
Select the item or items that you want to add to the constraint model, and then save your changes.
When you add a bundle, its product component groups and their cardinality are automatically imported from Product Catalog Management (PCM). The entire bundle structure is visible in the left panel, with child products and product classifications grouped into the respective product component groups. However, you can’t define constraints or rules at the group level.
Under Products, select the item that you want to add a constraint or rule to.
In the Visual Builder window, click .
Select a constraint or rule type.
To define the constraint or rule for the selected item, add one or more expressions.
To create more advanced conditions, you can also group multiple expressions. To do this, define a grouping logic. Use expression numbers within parentheses ‘()’ to form groups, and connect them with 'and', 'or', or 'xor' operators.
For example, (1 and 2) or (3 and 4).
If you don’t define a specific grouping logic, all expressions are by default combined using an ‘and’ operator.
Add more constraints or rules as needed, and add expressions to them.
Save the constraint model.
To make the constraint model available for use, select Activate.

After you save a constraint model, you can switch back and forth between the Visual Builder and the CML Editor. Use the CML Editor to view and edit code for the constraint model. For more information on CML, see the Constraint Modeling Language (CML) User Guide.

NOTE Some constraints and rules you create in the CML Editor can't be changed in the Visual Builder because they aren't part of the Visual Builder tools. These are labeled in the Visual Builder as not editable.
