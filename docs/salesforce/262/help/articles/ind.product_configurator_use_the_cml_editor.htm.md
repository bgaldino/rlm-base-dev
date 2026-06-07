---
article_id: ind.product_configurator_use_the_cml_editor.htm
title: Use Code to Define Constraints and Rules in the CML Editor
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_use_the_cml_editor.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Use Code to Define Constraints and Rules in the CML Editor

In the Constraint Builder, use Constraint Modeling Language (CML) code to define constraints and rules for a constraint model.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
USER PERMISSIONS NEEDED
To create a constraint model:	Product Configuration Constraints Designer permission set

Complete the steps for Constraint Rules Engine setup before you work with constraint models. See Set Up Configurator With Constraint Rules Engine.

In the CML Editor, you add types for a constraint model to define constraints and rules. A type corresponds mainly to a product, product bundles, or product classification. There are also special types that work differently from the main types —  imported types from linked constraint models, and types corresponding to product component groups imported from Product Catalog Management (PCM). The CML Editor uses constraint modeling language (CML) to define constraint models. For more information on CML, see the Constraint Modeling Language (CML) User Guide.

You can import data from Salesforce objects to include in CML code. See Import Data from Salesforce Objects to Use in Constraint Models.

Create a constraint model.
In the Constraint Models app, select the constraint model you want to modify.
On the Details page, select the version name of the constraint model.
In the Constraint Builder header in the upper left corner, select CML Editor.
To create a new constraint model, select New Type.
Give the type a name that refers to the product, product bundle, or product classification it modifies, such as Laptop. To make the new type a child of an existing type, select a parent type.
Select Create.
In the left pane, select the type name.
To define variables, relationships, or associations for the selected type, go to the tabs for Variables, Relationships, or Associations, and follow the prompts to enter and save the required information.
To edit existing variables, relationships, or associations in the respective tabs, from the quick-action menu, click Edit, and then make the needed changes.
To write or edit CML code directly and define your constraints and rules, work in the CML Editor code window.
Save your changes.
To make the constraint model available for use, select Activate.

After you save a constraint model, you can switch back and forth between the CML Editor and the Visual Builder. Use the Visual Builder to add or edit constraints and rules with point-and-click tools.

NOTE Some constraints and rules that you create in the CML Editor can't be edited in the Visual Builder because they're not part of the Visual Builder tools. If you try to edit one of those constraints or rules in the Visual Builder, a message prompts you to return to the CML Editor.
