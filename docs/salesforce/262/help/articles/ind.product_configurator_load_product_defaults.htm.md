---
article_id: ind.product_configurator_load_product_defaults.htm
title: Load Product Defaults from PCM to a Constraint Model
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_load_product_defaults.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Load Product Defaults from PCM to a Constraint Model

Include product defaults defined in Product Catalog Management (PCM), such as attributes, attribute values, and custom and standard fields, when you import products to a Constraint Modeling Language (CML) constraint model.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
USER PERMISSIONS NEEDED
To import object data:	Product Configuration Constraints Designer permission set

To load referenced product field values into CML constraints, turn on Read access to the Product object for the Constraint Rules Engine Licenseless permission set.

In Setup, enter Permission Sets in Quick Find and select Permission Sets.
Select the Constraint Rules Engine Licenseless permission set.
NOTE If the Constraint Rules Engine Licenseless permission set for the Platform Integration User isn't available in your org, contact Salesforce Customer Support.
In the Apps section of the setup page for Constraint Rules Engine Licenseless permission set, select Object Settings.
For the Products object, turn on Read permission for Object Permissions and for the fields that you want to reference in the CML constraint.
To reference product field values in a constraint by using CML Editor, include the productField attribute annotation in the constraint to map a CML attribute to the corresponding product field.
NOTE When you use Visual Builder to import products from PCM, Constraint Rules Engine automatically includes field values.
