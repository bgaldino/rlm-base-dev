---
article_id: ind.product_configurator_create_a_constraint_model.htm
title: Create a Constraint Model
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_create_a_constraint_model.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Create a Constraint Model

To create a constraint model, in the Constraint Models app, name the constraint model and specify a context definition.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
USER PERMISSIONS NEEDED
To create a constraint model:	Product Configuration Constraints Designer permission set

Complete the steps for Constraint Rules Engine setup before you create a constraint model. See Set Up Configurator With Constraint Rules Engine.

From the App Launcher, find and select Constraint Models.
Click New Constraint Model.
Enter a name and API name for the constraint model.
Select the active sales transaction context definition that the cfgStatus node is mapped to.
Save the constraint model.
NOTE Deleting or restoring constraint models isn't currently supported.
Define Constraints and Rules with the Visual Builder
In the Constraint Builder, use point-and-click tools in the Visual Builder to define the constraints and rules for a constraint model. Add constraints and rules to easily configure products or product bundles.
Constraint and Rule Types in the Visual Builder
The Visual Builder provides point-and-click tools for you to easily define constraints and rules for a constraint model. Use the basic logic constraint, the conditional logic constraint, the message rule, the require rule, the exclude rule, the hide/disable rule, and the preference rule to author complex configurations for products and product bundles in your catalog.
Use Code to Define Constraints and Rules in the CML Editor
In the Constraint Builder, use Constraint Modeling Language (CML) code to define constraints and rules for a constraint model.
Variables, Relationships, and Associations in Constraint Models
To define how a constraint model configures products, create variables, relationships, and associations for the constraint model.
Set Up Custom Labels for Run-Time Message Translation
Enable translations for run-time messages defined in your constraint model by creating unique, translatable custom labels for the messages. The labels you set up replace the original static message text in the CML to facilitate translation. During run time, the messages appear in different languages, based on the sales reps’ locale and the translation settings of their Salesforce org. With this support, sales reps can see important configuration information in their local languages, which accelerates troubleshooting and improves usability.
Import Data from Salesforce Objects to Use in Constraint Models
Import data from a standard or custom Salesforce object to use in a table constraint in a constraint model. The imported data populates the columns and rows in the table constraint in CML, and saves you the step of manually entering the data.
Load Product Defaults from PCM to a Constraint Model
Include product defaults defined in Product Catalog Management (PCM), such as attributes, attribute values, and custom and standard fields, when you import products to a Constraint Modeling Language (CML) constraint model.
